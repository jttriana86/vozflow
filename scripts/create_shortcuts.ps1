# Creates VozFlow shortcuts on the Desktop and Start Menu.
# Idempotent: safe to run multiple times. Overwrites existing VozFlow.lnk files.
#
# Usage (from project root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\create_shortcuts.ps1
#
# install.bat calls this script automatically. Run it manually only if shortcuts
# get deleted or you move the project to a new folder.

[CmdletBinding()]
param(
    [string]$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path $ProjectDir).Path.TrimEnd('\')
$target = Join-Path $ProjectDir "venv\Scripts\pythonw.exe"
$icon = Join-Path $ProjectDir "assets\logo.ico"

if (-not (Test-Path $target)) {
    Write-Error "No se encontro $target. Ejecuta install.bat primero."
    exit 1
}
if (-not (Test-Path $icon)) {
    Write-Warning "No se encontro $icon. El acceso directo se creara con icono por defecto."
    $iconLocation = $target + ",0"
} else {
    $iconLocation = $icon + ",0"
}

$wsh = New-Object -ComObject WScript.Shell

$destinations = @(
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("Programs")
)

foreach ($dest in $destinations) {
    $lnkPath = Join-Path $dest "VozFlow.lnk"
    $lnk = $wsh.CreateShortcut($lnkPath)
    $lnk.TargetPath = $target
    $lnk.Arguments = "main.py"
    $lnk.WorkingDirectory = $ProjectDir
    $lnk.IconLocation = $iconLocation
    $lnk.Description = "VozFlow - Speech to Text"
    $lnk.Save()
    Write-Host "  OK  $lnkPath"
}
