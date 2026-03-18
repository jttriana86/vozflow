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

:: Crear acceso directo
echo.
echo [4/4] Creando acceso directo...
call :CreateShortcut
echo       ✓ Acceso directo creado en el escritorio

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║      ¡Instalación completada!         ║
echo  ╚═══════════════════════════════════════╝
echo.
echo  Para iniciar VozFlow:
echo    • Doble clic en "VozFlow" en el escritorio
echo    • O ejecuta: vozflow.bat
echo.
echo  Necesitarás una API key de Groq (gratis):
echo    https://console.groq.com/keys
echo.
pause
exit /b 0

:CreateShortcut
:: Crear VBS para generar acceso directo
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\createshortcut.vbs"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\VozFlow.lnk" >> "%temp%\createshortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\createshortcut.vbs"
echo oLink.TargetPath = "%~dp0vozflow.bat" >> "%temp%\createshortcut.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%temp%\createshortcut.vbs"
echo oLink.Description = "VozFlow - Speech to Text" >> "%temp%\createshortcut.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\SpeechUX\sapi.cpl,0" >> "%temp%\createshortcut.vbs"
echo oLink.Save >> "%temp%\createshortcut.vbs"
cscript //nologo "%temp%\createshortcut.vbs"
del "%temp%\createshortcut.vbs"
exit /b 0
