@echo off
REM Build AvroShot.exe + installable AvroShot-Setup.exe on Windows.
REM Run from a Windows machine (or CI) with Python 3.10+ installed.
setlocal

set ROOT=%~dp0..
set SRC=%ROOT%\linux
set DIST=%ROOT%\dist
set WORK=%ROOT%\build

echo [1/4] Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install -r "%SRC%\requirements.txt" pyinstaller

echo [2/4] Building AvroShot.exe with PyInstaller...
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name AvroShot ^
  --icon "%~dp0icon.ico" ^
  --paths "%SRC%" ^
  --hidden-import avroshot.platforms.windows ^
  --exclude-module PyQt6.QtQml ^
  --exclude-module PyQt6.QtQuick ^
  --exclude-module PyQt6.QtQuick3D ^
  --exclude-module PyQt6.QtQuickWidgets ^
  --exclude-module PyQt6.Qt3DCore ^
  --exclude-module PyQt6.QtNetwork ^
  --exclude-module PyQt6.QtMultimedia ^
  --exclude-module PyQt6.QtWebEngineCore ^
  --exclude-module PyQt6.QtPdf ^
  --exclude-module PyQt6.QtSql ^
  --exclude-module PyQt6.QtTest ^
  --exclude-module PyQt6.QtDesigner ^
  --exclude-module PyQt6.QtHelp ^
  --exclude-module PyQt6.QtOpenGL ^
  --exclude-module PyQt6.QtSvg ^
  --distpath "%DIST%" ^
  --workpath "%WORK%" ^
  --specpath "%WORK%" ^
  "%SRC%\avroshot\main.py"

if not exist "%DIST%\AvroShot.exe" (
  echo ERROR: AvroShot.exe was not produced.
  exit /b 1
)

echo [3/4] Compiling installer with Inno Setup...
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo Inno Setup 6 not found - skipping installer, but AvroShot.exe is ready.
  echo Download Inno Setup from https://jrsoftware.org/isinfo.php to build the installer.
  exit /b 0
)
%ISCC% /O"%DIST%" "%~dp0avroshot.iss"

echo [4/4] Done.
echo   Portable:  %DIST%\AvroShot.exe
echo   Installer: %DIST%\AvroShot-Setup.exe
endlocal
