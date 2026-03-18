"""
VozFlow - Configuración
"""
import os
from pathlib import Path

# Rutas
APP_NAME = "VozFlow"
APP_DIR = Path.home() / ".vozflow"
APP_DIR.mkdir(exist_ok=True)

# Audio
SAMPLE_RATE = 16000  # Whisper espera 16kHz
CHANNELS = 1
DTYPE = "int16"
CHUNK_SIZE = 1024
AUDIO_GAIN = 2.0  # Amplificación del micrófono

# Hotkeys
HOTKEY_HOLD = {"ctrl", "alt"}  # Mantener presionado para grabar
DOUBLE_TAP_KEY = "ctrl"  # Doble tap para modo manos libres
DOUBLE_TAP_INTERVAL = 0.3  # Segundos entre taps

# UI
PILL_WIDTH = 120
PILL_HEIGHT = 40
PILL_OPACITY = 0.95
PILL_CORNER_RADIUS = 20

# Colores
COLOR_IDLE = "#2D2D2D"
COLOR_RECORDING = "#E53935"
COLOR_PROCESSING = "#1E88E5"
COLOR_SUCCESS = "#43A047"

# Groq API
GROQ_MODEL = "whisper-large-v3"
GROQ_LANGUAGE = "es"  # Cambiar según necesidad

# Tiempos
PASTE_DELAY = 0.1  # Delay antes de pegar (segundos)
MIN_RECORDING_TIME = 0.5  # Mínimo tiempo de grabación
