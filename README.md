# AvroShot 📸

**AvroShot** is a fast, lightweight, **Lightshot-inspired screenshot & annotation tool** built with **Python + PyQt6**. Designed first for **Ubuntu Linux (both Wayland & X11)** with a clean, modular platform architecture ready for **Windows** and **macOS**.

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

## 🚀 Quick Install on Ubuntu

```bash
cd ~/AvroShot/linux
bash install.sh
```

What `install.sh` does:
1. Ensures `PyQt6` is installed.
2. Installs the `avroshot` CLI command to `~/.local/bin/avroshot`.
3. Installs the desktop entry (`io.github.avroshot.AvroShot.desktop`) and vector/PNG icons so **AvroShot** appears in your Ubuntu Application Menu.
4. Configures Wayland screenshot permission and registers the global shortcut **`Super+Shift+S`** (`<Super><Shift>s`).
5. Builds the installable Debian package at `dist/avroshot_1.0.0_all.deb`.

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

## 📦 Building the `.deb` Package

```bash
bash linux/packaging/build_deb.sh
```
The `.deb` package is generated at:
```text
dist/avroshot_1.0.0_all.deb
```
To install it system-wide on any Ubuntu/Debian machine:
```bash
sudo apt install ./dist/avroshot_1.0.0_all.deb
```

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
│   │   └── build_deb.sh     # Debian .deb package builder
│   ├── tests/
│   │   └── test_avroshot.py # Automated test suite
│   ├── install.sh           # One-command Ubuntu installer
│   ├── run_tests.sh         # Test suite runner
│   ├── pyproject.toml
│   └── requirements.txt
├── windows/                 # Windows build tooling
│   ├── icon.ico             # Windows app icon
│   ├── avroshot.iss         # Inno Setup installer script
│   └── build_windows.bat    # One-command Windows build script
├── .github/workflows/
│   └── build-windows.yml    # CI: builds AvroShot.exe + AvroShot-Setup.exe
└── README.md
```

---

## 🪟 Building the Windows Version

Because `avroshot/platforms/` cleanly separates OS-specific capture and clipboard logic from the PyQt6 UI, the same codebase builds on Windows.

**Option A — GitHub Actions (recommended):** push a `v*` tag (or run the *Build Windows Release* workflow manually from the Actions tab). The CI builds on `windows-latest` and produces both:
- `AvroShot.exe` — portable executable
- `AvroShot-Setup.exe` — installable installer (Inno Setup: Start Menu + optional Desktop shortcut)

Download them from the workflow run's artifacts or the GitHub Release page.

**Option B — build locally on a Windows machine:**
```bat
windows\build_windows.bat
```
This runs PyInstaller and compiles the Inno Setup installer (requires [Inno Setup 6](https://jrsoftware.org/isinfo.php) for the installer step; the portable `.exe` is built regardless).

**macOS (`.app`)**: `pip install pyinstaller PyQt6 && pyinstaller --windowed --name AvroShot linux/avroshot/main.py`
