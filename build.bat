@echo off
chcp 65001 >nul
title VozFlow - Crear Ejecutable

echo.
echo  Creando ejecutable VozFlow.exe...
echo.

:: Instalar PyInstaller si no existe
call venv\Scripts\pip install -q pyinstaller

:: Crear ejecutable
call venv\Scripts\pyinstaller --noconfirm --onefile --windowed ^
    --name "VozFlow" ^
    --add-data "config.py;." ^
    --hidden-import "pynput.keyboard._win32" ^
    --hidden-import "pynput.mouse._win32" ^
    main.py

echo.
if exist "dist\VozFlow.exe" (
    echo  ✓ Ejecutable creado en: dist\VozFlow.exe
    echo.
    echo  Puedes distribuir solo el archivo VozFlow.exe
) else (
    echo  ERROR: No se pudo crear el ejecutable
)

pause
