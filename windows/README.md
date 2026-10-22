# AvroShot for Windows — Install Guide

Two files are built for Windows and published on the
[GitHub Releases page](https://github.com/avrojit-ovi/AvroShot/releases):

| File | What it is |
| :--- | :--- |
| **`AvroShot-Setup.exe`** | **Recommended.** Installable package (Inno Setup). Adds Start Menu entry, optional Desktop shortcut, and an uninstaller. |
| `AvroShot.exe` | Portable executable. No install needed — just run it from any folder. |

## Install in 3 steps

1. Download **`AvroShot-Setup.exe`** from the
   [latest release](https://github.com/avrojit-ovi/AvroShot/releases/latest).
2. Double-click it. If Windows SmartScreen shows "Windows protected your PC",
   click **More info → Run anyway** (AvroShot is open source — the code is
   fully auditable in this repository).
3. Follow the wizard. Done — launch **AvroShot** from the Start Menu.

## First run on Windows

- **Capture screen**: run `AvroShot.exe` or `avroshot --capture`.
- **Global hotkey**: bind `Print Screen` (or any key) to AvroShot in
  *Windows Settings → Time & language → Typing → Advanced keyboard settings*,
  or use AutoHotkey. A native hotkey registration is planned for a future
  release.
- **Save folder**: screenshots go to `Pictures\AvroShot` by default
  (changeable in Settings).

## Building from source on Windows

```bat
git clone https://github.com/avrojit-ovi/AvroShot.git
cd AvroShot\windows
build_windows.bat
```

Requirements: Python 3.10+, [Inno Setup 6](https://jrsoftware.org/isinfo.php)
(for the installer; the portable exe is built regardless).

## Antivirus false positives

PyInstaller-packed executables are occasionally flagged by heuristics-based
scanners. AvroShot is open source (MIT) — you can verify every line, or build
the exe yourself with the script above.
