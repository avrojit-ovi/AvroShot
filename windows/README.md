# AvroShot for Windows — Install Guide

Two files are built for Windows and published on the
[GitHub Releases page](https://github.com/avrojit-ovi/AvroShot/releases):

| File | What it is |
| :--- | :--- |
| **`AvroShot-Setup.exe`** | **Recommended.** Installable setup. Installs AvroShot permanently, adds Start Menu entries and an uninstaller, and registers it in *Settings → Apps*. |
| `AvroShot.exe` | Portable executable. No install needed — just run it from any folder. |

## Install in 3 steps

1. Download **`AvroShot-Setup.exe`** from the
   [latest release](https://github.com/avrojit-ovi/AvroShot/releases/latest).
2. Double-click it. If Windows SmartScreen shows "Windows protected your PC",
   click **More info → Run anyway** (AvroShot is open source — the code is
   fully auditable in this repository).
3. Follow the wizard. Done — launch **AvroShot** from the Start Menu.

### Install for all users or just for you

The setup asks which mode you want:

- **Install for all users** — installs into `C:\Program Files\AvroShot` and is
  available to every account on the PC. Windows asks for administrator
  approval once.
- **Install for me only** — installs into `%LOCALAPPDATA%\Programs\AvroShot`
  with no administrator prompt.

Either way the app is a permanent, registered install: it shows up in
**Settings → Apps → Installed apps** with its version and icon, and there is an
**Uninstall AvroShot** entry in the Start Menu folder.

## First run on Windows

- **Capture screen**: launch **AvroShot** from the Start Menu, or run
  `AvroShot.exe` (portable) — or `avroshot --capture`.
- **Global hotkey**: bind `Print Screen` (or any key) to AvroShot in
  *Windows Settings → Time & language → Typing → Advanced keyboard settings*,
  or use AutoHotkey. A native hotkey registration is planned for a future
  release.
- **Save folder**: screenshots go to `Pictures\AvroShot` by default
  (changeable in Settings).

## Uninstall

*Settings → Apps → Installed apps → AvroShot → Uninstall*, or the
**Uninstall AvroShot** shortcut in the Start Menu folder. Your saved
screenshots and settings in `%APPDATA%\AvroShot` are left untouched.

## Building from source on Windows

```bat
git clone https://github.com/avrojit-ovi/AvroShot.git
cd AvroShot\windows
build_windows.bat
```

Requirements: Python 3.10+ and [Inno Setup 6 or 7](https://jrsoftware.org/isdl.php).
The script builds `dist\AvroShot.exe` (portable) and then compiles
`dist\AvroShot-Setup.exe` (installable); it stops with an error if Inno Setup
is missing, because a release must never ship the portable exe alone.

You can also let CI do it: run the **Build Windows Release** workflow from the
Actions tab (or push a `v*` tag). CI builds both files, installs and uninstalls
the setup in a smoke test, commits both into `windows/`, and attaches them to
the release.

## Antivirus false positives

PyInstaller-packed executables are occasionally flagged by heuristics-based
scanners. AvroShot is open source (MIT) — you can verify every line, or build
the exe yourself with the script above.

## Windows blocked AvroShot (Application Control / Smart App Control)

AvroShot's binaries are **not code-signed** (there is no paid signing
certificate behind this project), so Windows may refuse to start them:

- **Smart App Control** (Windows 11) silently blocks unsigned apps that have no
  reputation. You may see *"Part of this app has been blocked … we can't
  confirm who published AvroShot.exe"*.
- **SmartScreen** shows *"Windows protected your PC"*; click **More info → Run
  anyway**.
- A work or school PC with an **Application Control / WDAC policy** blocks it
  outright — that policy is set by your administrator, not by AvroShot.

If Smart App Control blocks the app, either install the **portable
`AvroShot.exe`** and allow it when prompted, or turn Smart App Control off:

1. Open **Windows Security** → **App & browser control**.
2. Select **Smart App Control settings** → **Off**.

Note that turning Smart App Control off is permanent for that Windows install
(it cannot be switched back on without reinstalling Windows), so decide
consciously. The setup itself already launches AvroShot through Explorer, so an
all-users install does not need administrator rights for the app to start.
