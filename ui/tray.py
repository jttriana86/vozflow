"""
VozFlow - System Tray
Icono en la bandeja del sistema con menú de opciones.
"""
from pathlib import Path

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import pyqtSignal, QObject, Qt

from config import COLOR_IDLE, COLOR_RECORDING

# Ruta al logo
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


class TrayIcon(QObject):
    """Icono de bandeja del sistema con menú contextual."""

    # Señales
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    toggle_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Crear icono (usar logo si existe)
        self._tray = QSystemTrayIcon()
        if LOGO_PATH.exists():
            self._tray.setIcon(self._create_icon_from_logo())
        else:
            self._tray.setIcon(self._create_icon(COLOR_IDLE))
        self._tray.setToolTip("VozFlow - Ctrl+Alt para dictar")

        # Crear menú
        self._menu = QMenu()
        self._setup_menu()
        self._tray.setContextMenu(self._menu)

        # Click en el icono
        self._tray.activated.connect(self._on_activated)

    def _setup_menu(self) -> None:
        """Configura el menú contextual."""
        # Estado
        self._status_action = QAction("Listo para dictar")
        self._status_action.setEnabled(False)
        self._menu.addAction(self._status_action)

        self._menu.addSeparator()

        # Hotkeys info
        hotkey_action = QAction("Ctrl+Alt: Mantener para grabar")
        hotkey_action.setEnabled(False)
        self._menu.addAction(hotkey_action)

        self._menu.addSeparator()

        # Configuración
        settings_action = QAction("Configuración...")
        settings_action.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(settings_action)

        self._menu.addSeparator()

        # Salir - más visible
        quit_action = QAction("❌ Cerrar VozFlow")
        quit_action.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(quit_action)

    def _create_icon(self, color: str) -> QIcon:
        """Crea un icono circular del color especificado."""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparente

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Círculo principal
        painter.setBrush(QColor(color))
        painter.setPen(QColor(color))
        margin = 4
        painter.drawEllipse(margin, margin, size - margin * 2, size - margin * 2)

        # Icono de micrófono simplificado (líneas)
        painter.setPen(QColor("white"))
        painter.setBrush(QColor("white"))

        # Cuerpo del mic
        mic_x = size // 2 - 6
        mic_y = size // 2 - 10
        painter.drawRoundedRect(mic_x, mic_y, 12, 16, 4, 4)

        # Base del mic
        painter.drawRect(size // 2 - 1, mic_y + 18, 2, 6)
        painter.drawRect(size // 2 - 6, mic_y + 24, 12, 2)

        painter.end()

        return QIcon(pixmap)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Maneja clicks en el icono."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Click izquierdo
            self.toggle_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Doble click
            self.settings_requested.emit()

    def show(self) -> None:
        """Muestra el icono en la bandeja."""
        self._tray.show()

    def hide(self) -> None:
        """Oculta el icono."""
        self._tray.hide()

    def _create_icon_from_logo(self, overlay_color: str | None = None) -> QIcon:
        """Crea icono desde el logo con overlay opcional de color."""
        pixmap = QPixmap(str(LOGO_PATH))
        # Escalar a tamaño de icono
        pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)

        if overlay_color:
            # Agregar indicador de estado (punto de color)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(overlay_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(44, 44, 18, 18)  # Punto en esquina inferior derecha
            painter.end()

        return QIcon(pixmap)

    def set_recording(self, is_recording: bool) -> None:
        """Actualiza el icono según estado de grabación."""
        if is_recording:
            if LOGO_PATH.exists():
                self._tray.setIcon(self._create_icon_from_logo(COLOR_RECORDING))
            else:
                self._tray.setIcon(self._create_icon(COLOR_RECORDING))
            self._tray.setToolTip("VozFlow - Grabando...")
            self._status_action.setText("Grabando...")
        else:
            if LOGO_PATH.exists():
                self._tray.setIcon(self._create_icon_from_logo())
            else:
                self._tray.setIcon(self._create_icon(COLOR_IDLE))
            self._tray.setToolTip("VozFlow - Ctrl+Alt para dictar")
            self._status_action.setText("Listo para dictar")

    def show_message(self, title: str, message: str,
                     icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                     duration: int = 3000) -> None:
        """Muestra una notificación."""
        self._tray.showMessage(title, message, icon, duration)
