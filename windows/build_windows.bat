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
  --collect-all PyQt6 ^
  --hidden-import avroshot.platforms.windows ^
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
