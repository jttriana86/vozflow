"""
VozFlow - Controlador Principal
Orquesta todos los componentes.
"""
import time
import threading
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from core.audio import AudioRecorder
from core.hotkey import HotkeyListener
from core.transcriber import Transcriber
from core.clipboard import ClipboardManager
from ui.pill import PillWindow

from config import MIN_RECORDING_TIME


class TranscriptionWorker(QThread):
    """Worker thread para transcripción (no bloquear UI)."""

    finished = pyqtSignal(str)  # Texto transcrito
    error = pyqtSignal(str)     # Mensaje de error

    def __init__(self, audio_data: bytes, transcriber: Transcriber):
        super().__init__()
        self._audio_data = audio_data
        self._transcriber = transcriber

    def run(self):
        try:
            text = self._transcriber.transcribe(self._audio_data)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class VozFlowApp(QObject):
    """
    Controlador principal de VozFlow.

    Conecta:
    - HotkeyListener (entrada)
    - AudioRecorder (grabación)
    - Transcriber (API)
    - ClipboardManager (salida)
    - PillWindow (feedback visual)
    """

    def __init__(self):
        super().__init__()

        # Componentes
        self._hotkey = HotkeyListener()
        self._recorder = AudioRecorder(on_level=self._on_audio_level)
        self._transcriber = Transcriber()
        self._clipboard = ClipboardManager()
        self._pill = PillWindow()

        # Estado
        self._recording_start_time = 0.0
        self._worker: Optional[TranscriptionWorker] = None

        # Conectar señales
        self._hotkey.pressed.connect(self._start_recording)
        self._hotkey.released.connect(self._stop_recording)

    def start(self) -> None:
        """Inicia la aplicación."""
        self._hotkey.start()

    def stop(self) -> None:
        """Detiene la aplicación."""
        self._hotkey.stop()
        if self._recorder.is_recording:
            self._recorder.stop()
        self._pill.hide()

    def _start_recording(self) -> None:
        """Inicia la grabación de audio."""
        # Guardar contexto (ventana activa)
        self._clipboard.save_context()

        # Iniciar grabación
        self._recorder.start()
        self._recording_start_time = time.time()

        # Mostrar indicador
        self._pill.show_recording()

    def _stop_recording(self) -> None:
        """Detiene la grabación y procesa."""
        # Verificar tiempo mínimo
        elapsed = time.time() - self._recording_start_time
        if elapsed < MIN_RECORDING_TIME:
            self._recorder.stop()
            self._pill.hide_pill()
            return

        # Obtener audio
        audio_data = self._recorder.stop()

        if not audio_data:
            self._pill.hide_pill()
            return

        # Mostrar procesando
        self._pill.show_processing()

        # Transcribir en thread separado
        self._worker = TranscriptionWorker(audio_data, self._transcriber)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_transcription_error)
        self._worker.start()

    def _on_transcription_done(self, text: str) -> None:
        """Callback cuando la transcripción termina."""
        if text:
            # Pegar el texto
            success = self._clipboard.paste_text(text)

            if success:
                self._pill.show_success()
            else:
                self._pill.show_error("Paste!")
        else:
            self._pill.hide_pill()

        self._worker = None

    def _on_transcription_error(self, error: str) -> None:
        """Callback en caso de error."""
        print(f"Error de transcripción: {error}")
        self._pill.show_error("Error")
        self._worker = None

    def _on_audio_level(self, level: float) -> None:
        """Callback para nivel de audio."""
        self._pill.set_audio_level(level)

    @property
    def is_configured(self) -> bool:
        """Verifica si la app está configurada."""
        return self._transcriber.is_configured
