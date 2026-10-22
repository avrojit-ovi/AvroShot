# Changelog

All notable changes to AvroShot are documented in this file.

## [1.0.0] — 2026-10-22

### Added — Linux (Ubuntu)
- Lightshot-style frozen fullscreen overlay with dark dim layer.
- Interactive area selection with 8 resize handles and live dimension badge
  (e.g. `800 × 600`).
- Floating dual toolbars: vertical annotation toolbar and horizontal action
  toolbar (Upload / Copy / Save / Cancel).
- Annotation tools: Pen (freehand), Line, Arrow, Rectangle, Marker
  (highlighter), Text — with color picker and thickness control
  (`2px`–`12px`, mouse wheel or `[` / `]`).
- Full Undo / Redo (`Ctrl+Z` / `Ctrl+Y`) via an independent annotation
  object stack.
- Clipboard copy (`Ctrl+C` / `Enter`), save to file (`Ctrl+S`), cloud upload
  with shareable link (`Ctrl+U`) via `0x0.st` or Imgur.
- Delayed capture (`--delay 3`), screenshot history browser
  (`--history`), settings dialog (`--settings`), system tray mode (`--tray`).
- Multi-monitor support; Wayland capture via XDG Desktop Portal
  (`org.freedesktop.portal.Screenshot`) with `grim` / `gnome-screenshot` /
  `spectacle` fallbacks, X11 capture via `QScreen.grabWindow(0)` stitching.
- User-level installer (`linux/install.sh`), GNOME custom shortcut
  registration (`Super+Shift+S`), and Debian `.deb` package builder.

### Added — Windows build tooling
- `windows/` folder: app icon (`.ico`), Inno Setup installer script
  (`avroshot.iss`) producing the installable `AvroShot-Setup.exe`
  (Start Menu + optional Desktop shortcut), and `build_windows.bat`
  one-command build script.
- GitHub Actions workflow (`.github/workflows/build-windows.yml`) building
  `AvroShot.exe` and `AvroShot-Setup.exe` on `windows-latest` for every
  `v*` tag or manual dispatch, and attaching them to the GitHub Release.
- Slimmed PyInstaller configuration (only QtCore/QtGui/QtWidgets needed) so
  the executable stays well below GitHub's file size limits.

### Added — macOS build tooling
- `macos/` folder: app icon source, install guide, and the CI-built
  `AvroShot-macOS-arm64.zip` bundle (Apple Silicon).
- GitHub Actions workflow (`.github/workflows/build-macos.yml`) building
  `AvroShot.app` with PyInstaller on `macos-latest`, zipping it, committing
  it into `macos/`, and attaching it to the GitHub Release on `v*` tags.

### Added — Hotkey GUI (Linux)
- The Settings dialog now has a click-to-record **Global Hotkey** field: click
  it, press e.g. `Super+Shift+S`, and it shows the exact binding that gets
  registered — no need to type `<Super><Shift>s` by hand. `Esc` cancels.
- **Apply Shortcut** binds the recording immediately, and **Save Settings**
  also registers a newly recorded hotkey (previously the value was only
  stored, never bound).

### Fixed
- The user-level `install.sh` launcher pointed at the repository root instead
  of the `linux/` package directory, so every entry point (`avroshot`, the
  dock icon, the tray menu and the global hotkey) died with
  `ModuleNotFoundError: No module named 'avroshot'`.
- The installer now copies the package to `~/.local/share/avroshot`, runs
  `avroshot --version` to verify the launcher, and aborts with a clear message
  instead of leaving a silently broken command behind.

### Added — Linux packages for every distribution
- `linux/packaging/stage_app.sh` stages one shared install tree (sources,
  `avroshot` launcher, desktop entries, icon, docs) reused by every format.
- Debian/Ubuntu `.deb` (Debian 12+, Ubuntu 22.04+, Mint, Pop!_OS, Zorin,
  Kali, MX, Deepin) committed to `linux/debian/`.
- Fedora/RHEL `.rpm` (Fedora, RHEL 9/10, CentOS Stream, Rocky, Alma, Oracle,
  Amazon Linux) committed to `linux/fedora/`.
- openSUSE/SLES `.rpm` built from the same spec with openSUSE binding names
  (`python3-PyQt6`, `python3-dbus-python`), committed to `linux/opensuse/`.
- Arch/Manjaro `.pkg.tar.zst` built with `makepkg` from
  `linux/packaging/PKGBUILD` (AUR-ready), committed to `linux/arch/`.
- GitHub Actions workflow (`.github/workflows/build-linux-packages.yml`) runs
  each build inside the target distribution's container, inspects the produced
  package (`dpkg-deb`, `rpm -qip`, `pacman -Qip`) and commits it.

### Docs
- README with feature list, install guides (Linux + Windows + macOS), CLI
  reference, keyboard shortcuts, and AvroShot vs Lightshot comparison section.
- LICENSE (MIT).
- `windows/README.md` and `macos/README.md` platform install guides.
