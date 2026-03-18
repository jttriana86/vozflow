"""
VozFlow - Diálogo de Configuración
Primera ejecución y ajustes.
"""
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QGroupBox,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from core.audio import AudioRecorder
from core.transcriber import Transcriber

# Ruta al logo
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


def get_startup_folder() -> Path:
    """Retorna la carpeta de inicio de Windows."""
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"


def is_startup_enabled() -> bool:
    """Verifica si VozFlow está configurado para iniciar con Windows."""
    shortcut = get_startup_folder() / "VozFlow.lnk"
    return shortcut.exists()


def enable_startup() -> bool:
    """Agrega VozFlow al inicio de Windows."""
    try:
        startup_folder = get_startup_folder()
        shortcut_path = startup_folder / "VozFlow.lnk"

        # Encontrar el script principal
        if getattr(sys, 'frozen', False):
            # Si es ejecutable compilado
            target = Path(sys.executable)
            working_dir = target.parent
        else:
            # Si es script de Python
            script_dir = Path(__file__).parent.parent
            target = script_dir / "vozflow.bat"
            if not target.exists():
                target = script_dir / "main.py"
            working_dir = script_dir

        # Crear acceso directo usando PowerShell
        ps_command = f'''
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target}"
        $Shortcut.WorkingDirectory = "{working_dir}"
        $Shortcut.Description = "VozFlow - Speech to Text"
        $Shortcut.Save()
        '''
        os.system(f'powershell -Command "{ps_command}"')
        return True
    except Exception:
        return False


def disable_startup() -> bool:
    """Quita VozFlow del inicio de Windows."""
    try:
        shortcut = get_startup_folder() / "VozFlow.lnk"
        if shortcut.exists():
            shortcut.unlink()
        return True
    except Exception:
        return False


class FirstRunDialog(QDialog):
    """Diálogo de configuración inicial."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("VozFlow - Configuración")
        self.setFixedSize(450, 380)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )

        self._api_key = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Logo
        if LOGO_PATH.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(LOGO_PATH))
            pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        # Título
        title = QLabel("Bienvenido a VozFlow")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Dictado por voz para Windows")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Grupo API Key
        api_group = QGroupBox("API Key de Groq")
        api_layout = QVBoxLayout(api_group)

        api_info = QLabel(
            "Necesitas una API key gratuita de Groq.\n"
            "Obtén la tuya en: console.groq.com/keys"
        )
        api_info.setWordWrap(True)
        api_layout.addWidget(api_info)

        self._api_input = QLineEdit()
        self._api_input.setPlaceholderText("gsk_...")
        self._api_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self._api_input)

        layout.addWidget(api_group)

        # Grupo Micrófono
        mic_group = QGroupBox("Micrófono")
        mic_layout = QVBoxLayout(mic_group)

        self._mic_combo = QComboBox()
        self._load_microphones()
        mic_layout.addWidget(self._mic_combo)

        layout.addWidget(mic_group)

        # Botones
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar y Comenzar")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _load_microphones(self) -> None:
        """Carga los micrófonos disponibles."""
        devices = AudioRecorder.list_devices()
        for dev in devices:
            self._mic_combo.addItem(dev["name"], dev["index"])

    def _save(self) -> None:
        """Guarda la configuración."""
        api_key = self._api_input.text().strip()

        # Validar API key
        if not api_key:
            QMessageBox.warning(self, "Error", "Ingresa tu API key de Groq")
            return

        if not Transcriber.validate_api_key(api_key):
            QMessageBox.warning(
                self, "Error",
                "La API key no parece válida.\n"
                "Debe comenzar con 'gsk_'"
            )
            return

        # Guardar
        transcriber = Transcriber()
        transcriber.save_api_key(api_key)

        # Guardar micrófono seleccionado
        mic_index = self._mic_combo.currentData()
        if mic_index is not None:
            AudioRecorder.set_device(mic_index)

        self._api_key = api_key
        self.accept()

    @property
    def api_key(self) -> str:
        return self._api_key


class SettingsDialog(QDialog):
    """Diálogo de configuración general."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("VozFlow - Configuración")
        self.setFixedSize(400, 420)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Grupo API
        api_group = QGroupBox("API Key de Groq")
        api_layout = QVBoxLayout(api_group)

        self._api_input = QLineEdit()
        self._api_input.setPlaceholderText("gsk_...")
        self._api_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Cargar key existente
        transcriber = Transcriber()
        if transcriber.is_configured:
            self._api_input.setText("••••••••••••••••")

        api_layout.addWidget(self._api_input)
        layout.addWidget(api_group)

        # Grupo Micrófono
        mic_group = QGroupBox("Micrófono")
        mic_layout = QVBoxLayout(mic_group)

        self._mic_combo = QComboBox()
        self._load_microphones()
        mic_layout.addWidget(self._mic_combo)

        layout.addWidget(mic_group)

        # Grupo Idioma
        lang_group = QGroupBox("Idioma de transcripción")
        lang_layout = QVBoxLayout(lang_group)

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Español", "es")
        self._lang_combo.addItem("English", "en")
        self._lang_combo.addItem("Português", "pt")
        self._lang_combo.addItem("Français", "fr")
        self._lang_combo.addItem("Deutsch", "de")
        self._lang_combo.addItem("Auto-detectar", None)
        lang_layout.addWidget(self._lang_combo)

        layout.addWidget(lang_group)

        # Grupo Inicio automático
        startup_group = QGroupBox("Inicio automático")
        startup_layout = QVBoxLayout(startup_group)

        self._startup_check = QCheckBox("Iniciar VozFlow con Windows")
        self._startup_check.setChecked(is_startup_enabled())
        startup_layout.addWidget(self._startup_check)

        layout.addWidget(startup_group)

        # Info de hotkeys
        info_group = QGroupBox("Atajos de teclado")
        info_layout = QVBoxLayout(info_group)

        info_label = QLabel(
            "• Ctrl + Alt: Mantener para grabar\n"
            "• Ctrl x2 (doble tap): Modo manos libres\n"
            "• En modo manos libres, Ctrl simple para detener"
        )
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)

        # Botones
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _load_microphones(self) -> None:
        devices = AudioRecorder.list_devices()
        for dev in devices:
            self._mic_combo.addItem(dev["name"], dev["index"])

    def _save(self) -> None:
        # Guardar API key si cambió
        api_key = self._api_input.text().strip()
        if api_key and not api_key.startswith("•"):
            if Transcriber.validate_api_key(api_key):
                transcriber = Transcriber()
                transcriber.save_api_key(api_key)

        # Guardar micrófono
        mic_index = self._mic_combo.currentData()
        if mic_index is not None:
            AudioRecorder.set_device(mic_index)

        # Configurar inicio automático
        if self._startup_check.isChecked():
            enable_startup()
        else:
            disable_startup()

        self.accept()
