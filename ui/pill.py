"""
VozFlow - Indicador Visual (Pill)
Ventana flotante que muestra el estado de grabación.
"""
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QFont, QPixmap

from config import (
    PILL_WIDTH, PILL_HEIGHT, PILL_OPACITY, PILL_CORNER_RADIUS,
    COLOR_IDLE, COLOR_RECORDING, COLOR_PROCESSING, COLOR_SUCCESS
)

# Ruta al logo
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

# Tamaño ajustado para incluir logo
PILL_WIDTH_WITH_LOGO = 150


class PillWindow(QWidget):
    """
    Ventana flotante tipo píldora que indica el estado.

    Estados:
    - idle: Oculta o gris
    - recording: Roja con animación de pulso
    - processing: Azul con texto "..."
    - success: Verde breve antes de ocultarse
    """

    def __init__(self):
        super().__init__()

        # Cargar logo si existe
        self._logo_pixmap = None
        if LOGO_PATH.exists():
            self._logo_pixmap = QPixmap(str(LOGO_PATH))
            self._logo_pixmap = self._logo_pixmap.scaled(
                28, 28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        # Configurar ventana
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # No aparece en taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ajustar tamaño si hay logo
        width = PILL_WIDTH_WITH_LOGO if self._logo_pixmap else PILL_WIDTH
        self.setFixedSize(width, PILL_HEIGHT)

        # Estado
        self._state = "idle"
        self._level = 0.0  # Nivel de audio 0-1
        self._pulse_opacity = 1.0

        # Color actual (para animaciones)
        self._current_color = QColor(COLOR_IDLE)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label de texto
        self._label = QLabel("")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._label.setStyleSheet("color: white;")
        layout.addWidget(self._label)

        # Timer para animación de pulso
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_growing = True

        # Posicionar en esquina superior derecha
        self._position_window()

    def _position_window(self) -> None:
        """Posiciona la ventana en la esquina superior derecha."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 20
            y = geometry.top() + 20
            self.move(x, y)

    def show_recording(self) -> None:
        """Muestra estado de grabación."""
        self._state = "recording"
        self._current_color = QColor(COLOR_RECORDING)
        self._label.setText("  REC" if self._logo_pixmap else "REC")
        self._pulse_timer.start(50)
        self.show()
        self.update()

    def show_processing(self) -> None:
        """Muestra estado de procesamiento."""
        self._state = "processing"
        self._current_color = QColor(COLOR_PROCESSING)
        self._label.setText("  ..." if self._logo_pixmap else "...")
        self._pulse_timer.stop()
        self._pulse_opacity = 1.0
        self.update()

    def show_success(self, auto_hide: bool = True) -> None:
        """Muestra éxito brevemente."""
        self._state = "success"
        self._current_color = QColor(COLOR_SUCCESS)
        self._label.setText("  OK" if self._logo_pixmap else "OK")
        self._pulse_timer.stop()
        self._pulse_opacity = 1.0
        self.update()

        if auto_hide:
            QTimer.singleShot(800, self.hide_pill)

    def show_error(self, message: str = "Error") -> None:
        """Muestra error brevemente."""
        self._state = "error"
        self._current_color = QColor("#E53935")
        text = message[:8]  # Truncar
        self._label.setText(f"  {text}" if self._logo_pixmap else text)
        self._pulse_timer.stop()
        self.update()

        QTimer.singleShot(2000, self.hide_pill)

    def hide_pill(self) -> None:
        """Oculta la píldora."""
        self._state = "idle"
        self._pulse_timer.stop()
        self.hide()

    def set_audio_level(self, level: float) -> None:
        """
        Actualiza el nivel de audio para visualización.

        Args:
            level: Nivel de 0.0 a 1.0
        """
        self._level = max(0.0, min(1.0, level))
        if self._state == "recording":
            self.update()

    def _update_pulse(self) -> None:
        """Actualiza la animación de pulso."""
        if self._pulse_growing:
            self._pulse_opacity += 0.05
            if self._pulse_opacity >= 1.0:
                self._pulse_opacity = 1.0
                self._pulse_growing = False
        else:
            self._pulse_opacity -= 0.05
            if self._pulse_opacity <= 0.6:
                self._pulse_opacity = 0.6
                self._pulse_growing = True

        self.update()

    def paintEvent(self, event) -> None:
        """Dibuja la píldora."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Color con opacidad de pulso
        color = QColor(self._current_color)
        if self._state == "recording":
            color.setAlphaF(self._pulse_opacity * PILL_OPACITY)
        else:
            color.setAlphaF(PILL_OPACITY)

        # Dibujar fondo redondeado
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            self.rect(),
            PILL_CORNER_RADIUS,
            PILL_CORNER_RADIUS
        )

        # Dibujar logo si existe
        if self._logo_pixmap:
            logo_x = 8
            logo_y = (PILL_HEIGHT - self._logo_pixmap.height()) // 2
            painter.drawPixmap(logo_x, logo_y, self._logo_pixmap)

        # Barra de nivel de audio (solo en recording)
        if self._state == "recording" and self._level > 0:
            bar_start = 45 if self._logo_pixmap else 10
            bar_width = int((self.width() - bar_start - 10) * self._level)
            level_color = QColor(255, 255, 255, 80)
            painter.setBrush(QBrush(level_color))
            painter.drawRoundedRect(
                bar_start, PILL_HEIGHT - 8,
                bar_width, 4,
                2, 2
            )
