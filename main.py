"""
VozFlow - Speech to Text para Windows
Punto de entrada principal.

Uso:
    python main.py

Hotkeys:
    - Ctrl+Alt (mantener): Grabar mientras se mantiene presionado
    - Ctrl x2 (doble tap): Modo manos libres (toggle)
"""
import sys
import signal

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app import VozFlowApp
from ui.tray import TrayIcon
from ui.settings import FirstRunDialog, SettingsDialog
from core.transcriber import Transcriber

from config import APP_NAME


def main():
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)  # No cerrar al cerrar ventanas

    # Permitir Ctrl+C para salir
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Verificar si es primera ejecución
    transcriber = Transcriber()
    if not transcriber.is_configured:
        dialog = FirstRunDialog()
        if dialog.exec() != FirstRunDialog.DialogCode.Accepted:
            # Usuario canceló
            sys.exit(0)

    # Crear componentes
    vozflow = VozFlowApp()
    tray = TrayIcon()

    # Conectar señales del tray
    def show_settings():
        dialog = SettingsDialog()
        dialog.exec()

    def quit_app():
        vozflow.stop()
        tray.hide()
        app.quit()

    tray.settings_requested.connect(show_settings)
    tray.quit_requested.connect(quit_app)

    # Actualizar icono del tray según estado
    # (esto requiere conectar señales adicionales en una versión más completa)

    # Iniciar
    vozflow.start()
    tray.show()

    # Notificación inicial
    tray.show_message(
        "VozFlow activo",
        "Ctrl+Alt para dictar\nCtrl x2 para modo manos libres",
        duration=3000
    )

    # Event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
