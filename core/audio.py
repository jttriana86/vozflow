"""
VozFlow - Captura de Audio
Graba audio del micrófono y lo prepara para transcripción.
"""
import io
import wave
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, Callable

from config import SAMPLE_RATE, CHANNELS, DTYPE, CHUNK_SIZE, AUDIO_GAIN


class AudioRecorder:
    """Grabador de audio con visualización de nivel."""

    def __init__(self, on_level: Optional[Callable[[float], None]] = None):
        """
        Args:
            on_level: Callback para nivel de audio (0.0 - 1.0)
        """
        self._on_level = on_level
        self._frames: list[np.ndarray] = []
        self._recording = False
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Inicia la grabación."""
        with self._lock:
            if self._recording:
                return

            self._frames = []
            self._recording = True

            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=CHUNK_SIZE,
                callback=self._audio_callback
            )
            self._stream.start()

    def stop(self) -> bytes:
        """
        Detiene la grabación y retorna el audio en formato WAV.

        Returns:
            Bytes del archivo WAV
        """
        with self._lock:
            if not self._recording:
                return b""

            self._recording = False

            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            if not self._frames:
                return b""

            # Concatenar frames
            audio_data = np.concatenate(self._frames)

            # Aplicar ganancia
            audio_data = np.clip(audio_data * AUDIO_GAIN, -32768, 32767).astype(np.int16)

            # Convertir a WAV
            return self._to_wav(audio_data)

    def _audio_callback(self, indata: np.ndarray, frames: int,
                        time_info: dict, status: sd.CallbackFlags) -> None:
        """Callback de sounddevice para cada chunk de audio."""
        if not self._recording:
            return

        # Guardar frame
        self._frames.append(indata.copy())

        # Calcular nivel RMS para visualización
        if self._on_level:
            rms = np.sqrt(np.mean(indata.astype(np.float32) ** 2))
            # Normalizar a 0-1 (ajustar divisor según sensibilidad deseada)
            level = min(1.0, rms / 3000)
            self._on_level(level)

    def _to_wav(self, audio_data: np.ndarray) -> bytes:
        """Convierte numpy array a bytes WAV."""
        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit = 2 bytes
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())

        buffer.seek(0)
        return buffer.read()

    @property
    def is_recording(self) -> bool:
        return self._recording

    @staticmethod
    def list_devices() -> list[dict]:
        """Lista dispositivos de audio disponibles."""
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "sample_rate": dev["default_samplerate"]
                })
        return devices

    @staticmethod
    def set_device(device_index: int) -> None:
        """Establece el dispositivo de entrada por defecto."""
        sd.default.device[0] = device_index
