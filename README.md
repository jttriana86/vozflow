# VozFlow

**Dictado por voz para Windows** - Habla y el texto aparece donde tengas el cursor.

Alternativa gratuita a Wispr Flow (~$0.60/mes vs $15/mes).

---

## Instalacion Rapida

### 1. Descargar
```bash
git clone https://github.com/TU_USUARIO/vozflow.git
cd vozflow
```

### 2. Instalar
Doble clic en **`install.bat`** y listo.

### 3. Obtener API Key (gratis)
1. Ve a [console.groq.com/keys](https://console.groq.com/keys)
2. Crea una cuenta (es gratis)
3. Genera una API key
4. Pegala cuando VozFlow te la pida

### 4. Usar
Doble clic en **VozFlow** en el escritorio (o ejecuta `vozflow.bat`)

---

## Como Funciona

| Atajo | Que hace |
|-------|----------|
| **Ctrl + Alt** (mantener) | Graba mientras mantienes. Suelta para pegar el texto. |
| **Ctrl + Ctrl** (doble tap) | Modo manos libres. Presiona Ctrl de nuevo para terminar. |

### Ejemplo:
1. Abre Word, Notepad, tu navegador, o cualquier app
2. Pon el cursor donde quieras escribir
3. Manten **Ctrl + Alt**
4. Di: *"Hola, esto es una prueba de dictado"*
5. Suelta las teclas
6. El texto aparece escrito

---

## Configuracion

Click derecho en el icono de VozFlow (bandeja del sistema) > **Configuracion**

- **API Key**: Tu clave de Groq
- **Microfono**: Selecciona cual usar
- **Idioma**: Espanol, English, Portugues, etc.
- **Iniciar con Windows**: Para que siempre este disponible

---

## Estructura

```
vozflow/
├── install.bat      <- Ejecutar para instalar
├── vozflow.bat      <- Ejecutar para iniciar
├── build.bat        <- Crear ejecutable .exe
├── main.py          <- Punto de entrada
├── app.py           <- Controlador principal
├── config.py        <- Configuracion
├── core/
│   ├── audio.py     <- Captura de microfono
│   ├── hotkey.py    <- Deteccion de teclas
│   ├── transcriber.py <- API de Groq Whisper
│   └── clipboard.py <- Pegado automatico
└── ui/
    ├── pill.py      <- Indicador visual flotante
    ├── tray.py      <- Icono en bandeja
    └── settings.py  <- Ventana de configuracion
```

---

## Requisitos

- Windows 10 / 11
- Python 3.10+ ([descargar](https://www.python.org/downloads/))
- Conexion a internet (para la API)
- Microfono

---

## Solucion de Problemas

### "No detecta el microfono"
Windows Settings > Privacy > Microphone > Permitir acceso

### "El texto no se pega"
Algunas apps bloquean el pegado automatico. Intenta en Notepad para verificar.

### "Error de API"
Verifica que tu API key sea correcta y tengas internet.

### "No inicia"
Asegurate de tener Python instalado y marcado "Add to PATH"

---

## Crear Ejecutable (Opcional)

Si quieres un `.exe` sin necesidad de Python:

```bash
build.bat
```

El ejecutable estara en `dist/VozFlow.exe`

---

## Como Funciona (Tecnico)

1. `pynput` detecta Ctrl+Alt a nivel global
2. `sounddevice` captura el audio del microfono
3. El audio se envia a **Groq Whisper API** (transcripcion)
4. `pyautogui` simula Ctrl+V para pegar el texto
5. `PyQt6` maneja la UI (indicador flotante + tray)

---

## Licencia

MIT - Usalo como quieras.

---

## Creditos

Inspirado en [SFlow](https://github.com/daniel-carreon/sflow) (macOS).
