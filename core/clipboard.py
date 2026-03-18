"""
VozFlow - Clipboard y Pegado Automático
Maneja el portapapeles y simula Ctrl+V en Windows.
"""
import time
import threading
from typing import Optional

import pyperclip
import pyautogui
import pygetwindow as gw

from config import PASTE_DELAY


class ClipboardManager:
    """Gestiona el portapapeles y pegado automático en Windows."""

    def __init__(self):
        self._saved_window: Optional[str] = None
        self._original_clipboard: Optional[str] = None
        self._lock = threading.Lock()

        # Configurar pyautogui para ser más rápido
        pyautogui.PAUSE = 0.02
        pyautogui.FAILSAFE = False

    def save_context(self) -> None:
        """
        Guarda el contexto actual (ventana activa y portapapeles).
        Llamar ANTES de iniciar la grabación.
        """
        with self._lock:
            # Guardar ventana activa
            try:
                active = gw.getActiveWindow()
                if active:
                    self._saved_window = active.title
            except Exception:
                self._saved_window = None

            # Guardar contenido actual del portapapeles
            try:
                self._original_clipboard = pyperclip.paste()
            except Exception:
                self._original_clipboard = None

    def paste_text(self, text: str, restore_clipboard: bool = True) -> bool:
        """
        Pega texto en la ventana guardada.

        Args:
            text: Texto a pegar
            restore_clipboard: Si restaurar el portapapeles original después

        Returns:
            True si el pegado fue exitoso
        """
        if not text:
            return False

        with self._lock:
            try:
                # Restaurar foco a la ventana original
                self._restore_window()

                # Pequeña pausa para que la ventana esté activa
                time.sleep(PASTE_DELAY)

                # Copiar texto al portapapeles
                pyperclip.copy(text)

                # Simular Ctrl+V
                pyautogui.hotkey("ctrl", "v")

                # Pequeña pausa para que el pegado se complete
                time.sleep(0.05)

                # Restaurar portapapeles original si se solicitó
                if restore_clipboard and self._original_clipboard is not None:
                    time.sleep(0.1)
                    pyperclip.copy(self._original_clipboard)

                return True

            except Exception as e:
                print(f"Error al pegar: {e}")
                return False

    def _restore_window(self) -> None:
        """Restaura el foco a la ventana guardada."""
        if not self._saved_window:
            return

        try:
            # Buscar ventana por título
            windows = gw.getWindowsWithTitle(self._saved_window)
            if windows:
                win = windows[0]
                # Activar ventana
                if win.isMinimized:
                    win.restore()
                win.activate()
        except Exception:
            # Si falla, simplemente continuar
            pass

    def type_text(self, text: str) -> bool:
        """
        Escribe texto carácter por carácter (alternativa a pegar).
        Más lento pero más compatible.

        Args:
            text: Texto a escribir

        Returns:
            True si fue exitoso
        """
        if not text:
            return False

        try:
            self._restore_window()
            time.sleep(PASTE_DELAY)

            # Escribir con pyautogui
            pyautogui.write(text, interval=0.01)
            return True

        except Exception as e:
            print(f"Error al escribir: {e}")
            return False

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Copia texto al portapapeles sin pegar."""
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    @staticmethod
    def get_clipboard() -> str:
        """Obtiene el contenido actual del portapapeles."""
        try:
            return pyperclip.paste()
        except Exception:
            return ""
