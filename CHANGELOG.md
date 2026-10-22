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

### Docs
- README with feature list, install guides (Linux + Windows + macOS), CLI
  reference, keyboard shortcuts, and AvroShot vs Lightshot comparison section.
- LICENSE (MIT).
- `windows/README.md` and `macos/README.md` platform install guides.
