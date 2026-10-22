# AvroShot for Windows — Install Guide

Two files are built for Windows and published on the
[GitHub Releases page](https://github.com/avrojit-ovi/AvroShot/releases):

| File | What it is |
| :--- | :--- |
| **`AvroShot-Setup.exe`** | **Recommended.** Installable setup. Installs AvroShot permanently, adds Start Menu entries and an uninstaller, and registers it in *Settings → Apps*. |
| `AvroShot.exe` | Portable executable. No install needed — just run it from any folder. |

> **⚠️ Smart App Control (Windows 11) blocks unsigned apps — including this
> setup.** If you see *"Smart App Control blocked an app that may be unsafe …
> we could not verify its publisher"*, Windows is refusing the download because
> AvroShot is not code-signed. Open **Windows Security → App & browser control
> → Smart App Control settings → Off**, then run the setup again. See
> [Windows blocked AvroShot](#windows-blocked-avroshot-application-control--smart-app-control)
> below for the details and the alternative.

## Install in 3 steps

1. Download **`AvroShot-Setup.exe`** from the
   [latest release](https://github.com/avrojit-ovi/AvroShot/releases/latest).
   Extract it out of any archive/temp folder first — run it from a normal
   folder such as `Downloads`.
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
certificate behind this project), so Windows may refuse to run them:

- **Smart App Control** (Windows 11) blocks unsigned apps that have no
  reputation. It can block **the setup**, the portable exe, or the installed app:
  - *"Smart App Control blocked an app that may be unsafe … we could not verify
    its publisher"* — the download itself was refused.
  - *"Part of this app has been blocked … we can't confirm who published
    AvroShot.exe"* — setup finished but Windows stopped the launch.
- **SmartScreen** shows *"Windows protected your PC"*; click **More info → Run
  anyway**.
- A work or school PC with an **Application Control / WDAC policy** blocks it
  outright — that policy is set by your administrator, not by AvroShot.

Smart App Control has **no per-app "allow" button**, so an unsigned build can
only run once it is off:

1. Open **Windows Security** → **App & browser control**.
2. Select **Smart App Control settings** → **Off**.
3. Run `AvroShot-Setup.exe` again (from a normal folder, not from inside a zip).

Turning Smart App Control off is permanent for that Windows installation (it
cannot be switched back on without reinstalling Windows), so decide
consciously. You can check the state at any time:

```bat
reg query "HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy" /v VerifiedAndReputablePolicyState
```

`0x1` = enforced, `0x2` = evaluation, missing/`0x0` = off.

### If you cannot turn Smart App Control off

Run AvroShot from source instead — `python.exe` is signed and trusted, so the
scripts run where the packed exe is blocked. Install Python 3.10+ from
[python.org](https://www.python.org/downloads/windows/) with *Add python.exe to
PATH* ticked, then:

```bat
git clone https://github.com/avrojit-ovi/AvroShot.git
cd AvroShot\linux
python -m pip install -r requirements.txt
python -m avroshot
```

The setup launches the installed app through Explorer so it always starts with
normal (unelevated) rights — an all-users install no longer needs administrator
rights for AvroShot to start.
