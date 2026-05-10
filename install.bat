@echo off
chcp 65001 >nul
title VozFlow - Instalador

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║         VozFlow - Instalador          ║
echo  ║     Speech-to-Text para Windows       ║
echo  ╚═══════════════════════════════════════╝
echo.

:: Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python no está instalado.
    echo.
    echo  Descarga Python desde: https://www.python.org/downloads/
    echo  IMPORTANTE: Marca "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)
echo       ✓ Python encontrado

:: Crear entorno virtual
echo.
echo [2/4] Creando entorno virtual...
if exist venv (
    echo       ✓ Entorno virtual ya existe
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo       ✓ Entorno virtual creado
)

:: Instalar dependencias
echo.
echo [3/4] Instalando dependencias (puede tardar un momento)...
call venv\Scripts\pip install -q --upgrade pip
call venv\Scripts\pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo  ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo       ✓ Dependencias instaladas

:: Crear accesos directos (Escritorio + Menu Inicio)
echo.
echo [4/4] Creando accesos directos...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\create_shortcuts.ps1" -ProjectDir "%~dp0."
if %errorlevel% neq 0 (
    echo  ADVERTENCIA: No se pudieron crear los accesos directos.
    echo  Puedes iniciar VozFlow ejecutando vozflow.bat
)

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║      ¡Instalación completada!         ║
echo  ╚═══════════════════════════════════════╝
echo.
echo  Para iniciar VozFlow:
echo    • Doble clic en "VozFlow" en el escritorio
echo    • O busca "VozFlow" en el menu Inicio (tecla Windows)
echo    • O ejecuta: vozflow.bat
echo.
echo  Necesitarás una API key de Groq (gratis):
echo    https://console.groq.com/keys
echo.
pause
exit /b 0
