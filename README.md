# AvroShot 📸

**AvroShot** is a fast, lightweight, **Lightshot-inspired screenshot & annotation tool** built with **Python + PyQt6** — the **Lightshot alternative for Ubuntu / Linux** that Windows users have always had. Designed first for **Ubuntu Linux (both Wayland & X11)** with a clean, modular platform architecture ready for **Windows** and **macOS**.

> **Looking for Lightshot on Linux?** Lightshot has no official Linux version. AvroShot brings the exact Lightshot workflow — freeze screen, drag-select, annotate, copy/save/upload — to Ubuntu, and it is **100% free and open source** with **no ads, no account, no telemetry**.

---

## 📥 Download & Install

Grab the latest build from the
[Releases page](https://github.com/avrojit-ovi/AvroShot/releases/latest):

| Platform | File | What it is |
| :--- | :--- | :--- |
| **Windows 10/11** | **`AvroShot-Setup.exe`** | **Recommended.** Installable setup — installs AvroShot permanently (all users or just you), adds Start Menu entries and an uninstaller, and shows up in *Settings → Apps*. |
| **Windows 10/11** | `AvroShot.exe` | Portable executable — no install needed, just run it. |
| **macOS (Apple Silicon)** | `AvroShot-macOS-arm64.zip` | Unzip, then drag `AvroShot.app` into **Applications**. |
| **Ubuntu / Fedora / openSUSE / Arch** | `.deb`, `.rpm`, `.pkg.tar.zst` | Prebuilt packages committed under [`linux/`](linux/), or run `linux/install.sh`. |

On Windows, double-click **`AvroShot-Setup.exe`** and follow the wizard — pick
**Install for all users** (Program Files, one admin prompt) or **Install for me
only** (`%LOCALAPPDATA%\Programs`, no admin). If SmartScreen says *"Windows
protected your PC"*, click **More info → Run anyway**: the build is open source
but not code-signed. If **Smart App Control** blocks the setup with *"we could
not verify its publisher"*, turn it off in *Windows Security → App & browser
control → Smart App Control settings* and run the setup again — see
[the Windows guide](windows/README.md#windows-blocked-avroshot-application-control--smart-app-control).
To remove it later, use *Settings → Apps → AvroShot → Uninstall* or the
**Uninstall AvroShot** Start Menu shortcut.

---

## ✨ Features

### Core Lightshot Experience
- **Instant Frozen Screen Overlay**: Freezes your desktop with a customizable dark overlay.
- **Interactive Area Selection**: Click and drag anywhere to highlight the bright capture area.
- **8 Resize Handles**: Drag any of the 4 corners or 4 edge handles to fine-tune the selection, or drag inside with the Select (`V`) tool to move it.
- **Live Dimension Badge**: Shows real-time `Width × Height` (e.g., `800 × 600`) right above your selection.
- **Floating Dual Toolbars**:
  - **Vertical Annotation Toolbar** on the side of your selection.
  - **Horizontal Action Toolbar** (`Upload`, `Copy`, `Save`, `Cancel`) below your selection.

### Annotation Tools
- **Pen (`P`)**: Smooth freehand drawing.
- **Line (`L`)**: Crisp straight lines.
- **Arrow (`A`)**: Directional arrows with proportional arrowheads.
- **Rectangle (`R`)**: Highlight boxes and frames.
- **Marker / Highlighter (`M`)**: Semi-transparent highlighter stroke.
- **Text (`T`)**: Click anywhere inside the selection to type high-contrast text labels.
- **Color Picker & Line Thickness**: Pick any custom color and cycle thickness (`2px`–`12px` or scroll the mouse wheel / `[` `]`).
- **Full Undo / Redo (`Ctrl+Z` / `Ctrl+Y`)**: Every drawn annotation is stored as an independent `AnnotationShape` object on an undo/redo stack.

### Extra Power Features
- **Cloud Image Upload (`Ctrl+U`)**: Upload your cropped screenshot in one click (`0x0.st` or `Imgur`) and automatically copy the shareable link to your clipboard.
- **Delayed Capture (`--delay 3`)**: Capture menus or tooltips after a countdown timer.
- **Screenshot History (`--history`)**: Browse, preview, copy, save, or re-upload previous captures.
- **System Tray Mode (`--tray`)**: Keep AvroShot in your system tray for quick 1-click capture, 3s delay capture, history, and preferences.
- **Multi-Monitor & Wayland/X11 Support**:
  - **Wayland**: Uses `org.freedesktop.portal.Screenshot` (XDG Desktop Portal) with automatic permission registration plus fallbacks (`grim`, `gnome-screenshot`, `spectacle`).
  - **X11**: Uses multi-screen `QScreen.grabWindow(0)` stitching.
  - **Windows & macOS**: Built-in platform backend classes (`avroshot/platforms/windows.py`, `avroshot/platforms/macos.py`) ready for packaging with PyInstaller.

---

## 🆚 AvroShot vs Lightshot vs Other Screenshot Tools

Why should you use AvroShot instead of Lightshot, Flameshot, Shutter, or the built-in GNOME Screenshot?

| Feature | **AvroShot** | Lightshot | Flameshot | Shutter | GNOME Screenshot |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Runs on Linux (Ubuntu)** | ✅ Wayland + X11 | ❌ Windows/Mac only | ✅ X11-first | ✅ X11-only | ✅ basic |
| **Lightshot-style freeze & drag-select** | ✅ | ✅ | ❌ different UX | ❌ | ❌ |
| **8 resize handles + live size badge** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Annotation tools (Pen/Line/Arrow/Rect/Marker/Text)** | ✅ 6 tools | ✅ | ✅ | ⚠️ via editor | ❌ |
| **Undo / Redo stack** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Color picker + thickness control** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **One-click upload + shareable link** | ✅ 0x0.st / Imgur | ⚠️ prnt.sc only | ✅ Imgur | ❌ | ❌ |
| **Screenshot history** | ✅ built-in | ❌ | ❌ | ✅ | ❌ |
| **System tray quick capture** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Delayed capture** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Free & open source** | ✅ MIT | ❌ freeware, closed | ✅ | ✅ | ✅ |
| **No ads / no account / no telemetry** | ✅ | ❌ ads in app | ✅ | ✅ | ✅ |
| **Works offline** | ✅ fully | ⚠️ upload needs web | ✅ | ✅ | ✅ |
| **Cross-platform (Linux + Windows + macOS)** | ✅ | ⚠️ no Linux | ❌ | ❌ | ❌ |

### Why AvroShot is the better choice

1. **It actually runs on Linux.** Lightshot is Windows/Mac-only. AvroShot is built for Ubuntu first, with native **Wayland (XDG Desktop Portal)** support — not just X11.
2. **Identical muscle memory.** Freeze screen → drag area → annotate on top → copy / save / upload. If you know Lightshot, you already know AvroShot — same shortcuts, same workflow.
3. **Everything Lightshot hides behind its own service.** AvroShot uploads to open, neutral hosts (`0x0.st` or **Imgur**) and copies the link instantly — no forced prnt.sc account, no gallery lock-in.
4. **Zero ads, zero telemetry.** Lightshot shows ads and phones home. AvroShot is MIT-licensed source code you can read and build yourself.
5. **Extras Lightshot doesn't have.** Built-in screenshot history browser, configurable save patterns, delay capture, and a real settings dialog.
6. **Lightweight and fast.** Python + PyQt6, no Electron, no background bloat — starts instantly, uses little RAM.
7. **One app everywhere.** The same codebase covers Linux, Windows, and macOS — your workflow travels with you.

**Bottom line:** if you want the Lightshot experience on Ubuntu — with more features, no ads, and full control over where your screenshots go — **AvroShot is the tool to use.**

---

## 🚀 Quick Install on Ubuntu

```bash
cd ~/AvroShot/linux
bash install.sh
```

What `install.sh` does:
1. Ensures `PyQt6` is installed.
2. Copies the app to `~/.local/share/avroshot` and installs the `avroshot`
   command to `~/.local/bin/avroshot` (verified before the installer exits).
3. Installs **one** desktop entry (`io.github.avroshot.AvroShot.desktop`) and the
   AvroShot icon (SVG + 16–256 px PNGs, icon cache refreshed). Clicking
   **AvroShot** in the application grid opens its Settings window.
4. Configures Wayland screenshot permission and registers the global shortcut **`Super+Shift+S`** (`<Super><Shift>s`).
5. Builds the installable Debian package at `linux/debian/avroshot_1.0.2_all.deb`.

---

## ⌨️ Setting the Global Hotkey (GUI)

The hotkey is configurable from AvroShot's own Settings window — no terminal needed:

1. Open **Settings** in any of these ways:
   - Click the **AvroShot icon** in the dock / application grid (it opens Settings),
   - Click the **tray icon** (start it once with `avroshot --tray`) → **Settings…**,
   - Right-click the icon → **Capture Screen Now / 3s Delay / Tray / History**
     for the direct actions,
   - or run `avroshot --settings`.
2. Click the **Global Hotkey** box and press the combination you want, e.g.
   `Super+Shift+S`. The field records the keys directly, so there is no need to
   type `<Super><Shift>s` by hand (`Esc` cancels the recording).
3. Press **Apply Shortcut** to bind it immediately — or **Save Settings**, which
   also binds a newly recorded hotkey.

The binding is stored in GNOME's custom shortcuts, so it also shows up under
**Settings → Keyboard → Keyboard Shortcuts → Custom Shortcuts**. The default is
`Super+Shift+S`.

---

## ⌨️ CLI Usage & Keyboard Shortcuts

```bash
avroshot                    # Capture screen immediately and open Lightshot overlay
avroshot --capture          # Same as above
avroshot --delay 3          # Wait 3 seconds, then capture screen
avroshot --tray             # Run AvroShot in the system tray
avroshot --history          # Open Screenshot History dialog
avroshot --settings         # Open AvroShot Settings dialog
avroshot --fullscreen-copy  # Instantly copy full screen to clipboard
avroshot --fullscreen-save ~/Pictures/shot.png  # Save full screen directly to file
avroshot --register-shortcut "<Super><Shift>s"  # Bind Ubuntu custom shortcut
```

### Shortcuts Inside the Capture Overlay
| Shortcut | Action |
| :--- | :--- |
| **Mouse Drag** | Select area / Resize via 8 handles |
| **Right Click** | Reset current selection (or exit if no selection) |
| **`P` / `L` / `A` / `R` / `M` / `T`** | Pen / Line / Arrow / Rectangle / Marker / Text |
| **`V`** | Move / Resize selection mode |
| **Mouse Wheel** or **`[` / `]`** | Decrease / Increase stroke thickness |
| **`Ctrl+Z`** / **`Ctrl+Y`** | Undo / Redo annotation |
| **`Ctrl+A`** | Select entire screen |
| **`Ctrl+C`** or **`Enter`** | Copy cropped screenshot to Clipboard |
| **`Ctrl+S`** | Save cropped screenshot to Disk |
| **`Ctrl+U`** | Upload image & copy shareable link |
| **`Esc`** | Cancel capture |

---

## 📦 Prebuilt Linux Packages

Every package is built natively on its own distribution by the
[Build Linux Packages](.github/workflows/build-linux-packages.yml) workflow and
committed straight into the matching folder — no build step needed to install:

| Distribution family | Package | Folder |
| :--- | :--- | :--- |
| Debian 12+, Ubuntu 22.04+, Mint, Pop!_OS, Zorin, Kali, MX, Deepin | `avroshot_1.0.2_all.deb` | [`linux/debian`](linux/debian) |
| Fedora, RHEL 9/10, CentOS Stream, Rocky, Alma, Oracle, Amazon Linux | `avroshot-1.0.2-1.noarch.rpm` | [`linux/fedora`](linux/fedora) |
| openSUSE Tumbleweed / Leap 15.6+, SLES | `avroshot-1.0.2-1.noarch.rpm` | [`linux/opensuse`](linux/opensuse) |
| Arch Linux, Manjaro, EndeavourOS, Garuda, CachyOS | `avroshot-1.0.2-1-any.pkg.tar.zst` | [`linux/arch`](linux/arch) |

```bash
# Debian / Ubuntu / Mint / Pop!_OS / Kali
sudo apt install ./linux/debian/avroshot_1.0.2_all.deb

# Fedora / RHEL / Rocky / Alma / CentOS Stream
sudo dnf install ./linux/fedora/avroshot-1.0.2-1.noarch.rpm

# openSUSE / SLES
sudo zypper install ./linux/opensuse/avroshot-1.0.2-1.noarch.rpm

# Arch / Manjaro / EndeavourOS
sudo pacman -U ./linux/arch/avroshot-1.0.2-1-any.pkg.tar.zst
```

Each package depends on the distribution's own Python + PyQt6 build (so Qt
matches your theme and updates), installs `/usr/bin/avroshot`, the application
menu entry and the icon, and is rebuildable from one shared staging tree:

```bash
bash linux/packaging/build_deb.sh           # .deb   -> linux/debian/
bash linux/packaging/build_rpm.sh fedora    # .rpm   -> linux/fedora/
bash linux/packaging/build_rpm.sh opensuse  # .rpm   -> linux/opensuse/
bash linux/packaging/build_arch.sh          # Arch   -> linux/arch/
```

> Tip: push a `v*` tag (or run the workflow manually) and CI rebuilds every
> package, commits it into its folder and attaches it to the GitHub Release.

---

## 🗂️ Project Structure

```text
AvroShot/
├── linux/                    # Linux (Ubuntu) source code
│   ├── avroshot/
│   │   ├── __init__.py      # App metadata & version
│   │   ├── __main__.py      # python3 -m avroshot entrypoint
│   │   ├── main.py          # CLI argument parser & runner
│   │   ├── config.py        # Cross-platform settings manager (Linux/Windows/macOS)
│   │   ├── annotations.py   # Pen, Line, Arrow, Rect, Marker, Text & Undo/Redo stack
│   │   ├── history.py       # Screenshot history manager & JSON index
│   │   ├── uploader.py      # 0x0.st & Imgur anonymous uploader + QThread worker
│   │   ├── platforms/
│   │   │   ├── base.py      # Abstract PlatformBackend interface
│   │   │   ├── linux.py     # Ubuntu Wayland (XDG Portal) & X11 backend
│   │   │   ├── windows.py   # Windows backend
│   │   │   └── macos.py     # macOS backend
│   │   └── ui/
│   │       ├── __init__.py  # Vector app icon generator
│   │       ├── overlay.py   # Fullscreen Lightshot overlay, 8 handles, size badge
│   │       ├── toolbar.py   # Floating annotation & action toolbars
│   │       ├── history_dialog.py # Screenshot history browser
│   │       ├── settings_dialog.py # Preferences dialog
│   │       └── tray.py      # System tray icon & app controller
│   ├── assets/
│   │   ├── avroshot.svg
│   │   └── io.github.avroshot.AvroShot.desktop
│   ├── packaging/
│   │   ├── stage_app.sh     # Shared install-tree staging for all packages
│   │   ├── build_deb.sh     # Debian/Ubuntu .deb builder
│   │   ├── build_rpm.sh     # Fedora/openSUSE .rpm builder
│   │   ├── avroshot.spec    # Shared RPM spec (per-family Requires)
│   │   ├── build_arch.sh    # Arch/Manjaro package builder
│   │   └── PKGBUILD         # Arch recipe (AUR-ready)
│   ├── debian/              # avroshot_1.0.2_all.deb (committed by CI)
│   ├── fedora/              # avroshot-1.0.2-1.noarch.rpm (committed by CI)
│   ├── opensuse/            # avroshot-1.0.2-1.noarch.rpm (committed by CI)
│   ├── arch/                # avroshot-1.0.2-1-any.pkg.tar.zst (committed by CI)
│   ├── tests/
│   │   └── test_avroshot.py # Automated test suite
│   ├── install.sh           # One-command Ubuntu installer
│   ├── run_tests.sh         # Test suite runner
│   ├── pyproject.toml
│   └── requirements.txt
├── windows/                 # Windows build tooling
│   ├── AvroShot-Setup.exe   # Prebuilt installable setup - the recommended download (committed by CI)
│   ├── AvroShot.exe         # Prebuilt portable executable (committed by CI)
│   ├── icon.ico             # Windows app icon
│   ├── avroshot.iss         # Inno Setup installer script
│   └── build_windows.bat    # One-command Windows build script
├── macos/                   # macOS build tooling
│   ├── AvroShot-macOS-arm64.zip  # Prebuilt .app bundle (committed by CI)
│   ├── icon.png             # macOS app icon source
│   └── README.md            # macOS install guide
├── .github/workflows/
│   ├── build-windows.yml    # CI: builds AvroShot.exe + AvroShot-Setup.exe
│   ├── build-macos.yml      # CI: builds AvroShot.app + zip
│   └── build-linux-packages.yml  # CI: builds deb, rpm, Arch packages
└── README.md
```

---

## 🪟 Building the Windows Version

Because `avroshot/platforms/` cleanly separates OS-specific capture and clipboard logic from the PyQt6 UI, the same codebase builds on Windows.

**Option A — GitHub Actions (recommended):** push a `v*` tag (or run the *Build Windows Release* workflow manually from the Actions tab). The CI builds on `windows-latest` and produces both:
- `AvroShot-Setup.exe` — **the installable setup** (Inno Setup). Installs AvroShot permanently
  for all users or just the current user, adds Start Menu entries and an uninstaller, and
  registers it in *Settings → Apps*. CI installs and uninstalls it as a smoke test.
- `AvroShot.exe` — portable executable, for users who don't want an install.

Download them from the workflow run's artifacts or the GitHub Release page.

**Option B — build locally on a Windows machine:**
```bat
windows\build_windows.bat
```
This runs PyInstaller and compiles the Inno Setup installer. [Inno Setup 6 or 7](https://jrsoftware.org/isdl.php)
is required: the script stops with an error instead of producing a portable-only build.

---

## 🍎 Building the macOS Version

The macOS build is produced by CI on `macos-latest` (Apple Silicon):

- **`macos/AvroShot-macOS-arm64.zip`** — contains `AvroShot.app`. Unzip, drag to **Applications**, then right-click → **Open** the first time (the build isn't notarized with a paid Apple certificate).
- Also attached to the [latest release](https://github.com/avrojit-ovi/AvroShot/releases/latest).

See [macos/README.md](macos/README.md) for Gatekeeper workaround, Screen Recording permission, and local build steps.
