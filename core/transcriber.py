"""
VozFlow - Transcriptor de Audio
Envía audio a Groq Whisper API y obtiene texto.
"""
import os
from typing import Optional
from groq import Groq

from config import GROQ_MODEL, GROQ_LANGUAGE, APP_DIR


class Transcriber:
    """Cliente de Groq Whisper para transcripción."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Clave API de Groq. Si no se proporciona, busca en .env o archivo guardado.
        """
        self._api_key = api_key or self._load_api_key()
        self._client: Optional[Groq] = None

        if self._api_key:
            self._client = Groq(api_key=self._api_key)

    def _load_api_key(self) -> Optional[str]:
        """Carga la API key desde variables de entorno o archivo."""
        # Primero intentar variable de entorno
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key

        # Luego intentar archivo guardado
        key_file = APP_DIR / "api_key"
        if key_file.exists():
            return key_file.read_text().strip()

        return None

    def save_api_key(self, api_key: str) -> None:
        """Guarda la API key para uso futuro."""
        self._api_key = api_key
        self._client = Groq(api_key=api_key)

        key_file = APP_DIR / "api_key"
        key_file.write_text(api_key)

    def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcribe audio usando Groq Whisper.

        Args:
            audio_data: Bytes del archivo WAV
            language: Código de idioma (ej: "es", "en"). Por defecto usa config.

        Returns:
            Texto transcrito

        Raises:
            ValueError: Si no hay API key configurada
            Exception: Errores de la API
        """
        if not self._client:
            raise ValueError("API key de Groq no configurada")

        if not audio_data:
            return ""

        # Crear archivo temporal en memoria para la API
        transcription = self._client.audio.transcriptions.create(
            file=("audio.wav", audio_data),
            model=GROQ_MODEL,
            language=language or GROQ_LANGUAGE,
            response_format="text"
        )

        return transcription.strip()

    @property
    def is_configured(self) -> bool:
        """Verifica si hay una API key configurada."""
        return self._client is not None

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Valida una API key intentando crear un cliente.

        Args:
            api_key: Key a validar

        Returns:
            True si la key parece válida
        """
        if not api_key or len(api_key) < 10:
            return False

        # La validación real ocurre al hacer una request,
        # pero al menos verificamos formato básico
        return api_key.startswith("gsk_")
