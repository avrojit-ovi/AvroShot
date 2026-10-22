@echo off
REM Build AvroShot.exe (portable) and AvroShot-Setup.exe (installable) on Windows.
REM Run from a Windows machine (or CI) with Python 3.10+ installed.
REM Inno Setup 6 or 7 is required for the installable setup - it is not optional:
REM without it the release would ship a portable exe only.
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

echo [3/4] Compiling the installer with Inno Setup...
call set "PF86=%%ProgramFiles(x86)%%"
set "LOCALPF=%LocalAppData%\Programs"

set "ISCC="
if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%PF86%\Inno Setup 7\ISCC.exe" set "ISCC=%PF86%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%PF86%\Inno Setup 6\ISCC.exe" set "ISCC=%PF86%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LOCALPF%\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALPF%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ChocolateyInstall%\bin\ISCC.exe" set "ISCC=%ChocolateyInstall%\bin\ISCC.exe"

if not defined ISCC goto :no_inno

echo Using %ISCC%
"%ISCC%" /O"%DIST%" "%~dp0avroshot.iss"
if errorlevel 1 goto :compile_failed
if not exist "%DIST%\AvroShot-Setup.exe" goto :compile_failed

echo [4/4] Done.
echo   Portable:  %DIST%\AvroShot.exe
echo   Installer: %DIST%\AvroShot-Setup.exe
endlocal
exit /b 0

:no_inno
echo ERROR: Inno Setup 6/7 was not found, so AvroShot-Setup.exe cannot be built.
echo Install it from https://jrsoftware.org/isdl.php and run this script again.
echo (Only AvroShot.exe was built - do not publish a release without the installer.)
exit /b 1

:compile_failed
echo ERROR: Inno Setup failed to produce %DIST%\AvroShot-Setup.exe.
echo Check the compiler output above for the failing line in windows\avroshot.iss.
exit /b 1
