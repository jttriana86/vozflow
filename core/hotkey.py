"""
VozFlow - Detector de Hotkeys
Escucha combinaciones de teclas a nivel global en Windows.
"""
import time
import threading
from typing import Optional
from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from config import HOTKEY_HOLD, DOUBLE_TAP_KEY, DOUBLE_TAP_INTERVAL


class HotkeyListener(QObject):
    """
    Escucha hotkeys globales.

    Modos:
    - Hold: Mantener Ctrl+Alt para grabar
    - Hands-free: Doble tap en Ctrl para toggle (DESACTIVADO por ahora)
    """

    # Señales Qt
    pressed = pyqtSignal()   # Iniciar grabación
    released = pyqtSignal()  # Detener grabación

    def __init__(self):
        super().__init__()

        # Estado de teclas
        self._keys_held: set[str] = set()
        self._recording = False
        self._hands_free_mode = False

        # Para detección de doble tap (desactivado por defecto)
        self._enable_double_tap = False  # Desactivado - causa problemas
        self._last_release_time = 0.0
        self._waiting_for_double_tap = False

        # Listener de pynput
        self._listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Inicia el listener global de teclas."""
        if self._listener is not None:
            return

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def stop(self) -> None:
        """Detiene el listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None

        # Reset estado
        self._recording = False
        self._hands_free_mode = False
        self._keys_held.clear()

    def _normalize_key(self, key) -> Optional[str]:
        """Normaliza una tecla a string."""
        try:
            # Teclas especiales
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return "ctrl"
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return "alt"
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                return "shift"
            elif hasattr(key, "char") and key.char:
                return key.char.lower()
            elif hasattr(key, "name"):
                return key.name.lower()
        except AttributeError:
            pass
        return None

    def _on_press(self, key) -> None:
        """Callback cuando se presiona una tecla."""
        normalized = self._normalize_key(key)
        if not normalized:
            return

        with self._lock:
            # Evitar repetición de tecla mantenida
            if normalized in self._keys_held:
                return

            self._keys_held.add(normalized)

            # En modo hands-free, cualquier Ctrl detiene la grabación
            if self._hands_free_mode and normalized == "ctrl":
                self._hands_free_mode = False
                self._recording = False
                self.released.emit()
                return

            # Modo hold: verificar si todas las teclas del hotkey están presionadas
            if not self._hands_free_mode and HOTKEY_HOLD.issubset(self._keys_held):
                if not self._recording:
                    self._recording = True
                    self.pressed.emit()

    def _on_release(self, key) -> None:
        """Callback cuando se suelta una tecla."""
        normalized = self._normalize_key(key)
        if not normalized:
            return

        with self._lock:
            self._keys_held.discard(normalized)

            # Detectar doble tap en Ctrl (solo si está habilitado)
            if self._enable_double_tap and normalized == DOUBLE_TAP_KEY:
                now = time.time()
                if now - self._last_release_time < DOUBLE_TAP_INTERVAL:
                    # Doble tap detectado
                    if not self._hands_free_mode and not self._recording:
                        self._hands_free_mode = True
                        self._recording = True
                        self.pressed.emit()
                self._last_release_time = now

            # Modo hold: detener si se suelta alguna tecla del hotkey
            if not self._hands_free_mode and self._recording:
                if normalized in HOTKEY_HOLD:
                    self._recording = False
                    self.released.emit()

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def is_hands_free(self) -> bool:
        return self._hands_free_mode

    def cancel_recording(self) -> None:
        """Cancela cualquier grabación en curso."""
        with self._lock:
            if self._recording:
                self._recording = False
                self._hands_free_mode = False
                self.released.emit()
