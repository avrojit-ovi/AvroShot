# AvroShot for macOS

The macOS build is produced by CI on `macos-latest` and published here as
**`AvroShot-macOS-<arch>.zip`** (`arm64` = Apple Silicon M1/M2/M3/M4).

You can also find it on the
[GitHub Releases page](https://github.com/avrojit-ovi/AvroShot/releases).

## Install

1. Download `AvroShot-macOS-arm64.zip`.
2. Double-click the zip — it unpacks **`AvroShot.app`**.
3. Drag `AvroShot.app` into your **Applications** folder.
4. **First launch:** right-click (or Control-click) `AvroShot.app` →
   **Open** → **Open** again.

That last step is needed because the build is not signed with an Apple
Developer certificate (Apple charges $99/year for that). After the first
launch macOS remembers your choice and you can open it normally.

If macOS says the app is "damaged" or from an unidentified developer, run:

```bash
xattr -dr com.apple.quarantine /Applications/AvroShot.app
```

## What works on macOS

- Full-screen capture via the built-in `screencapture` utility
- Lightshot-style frozen overlay, drag-select, resize handles, size badge
- All annotation tools (pen, line, arrow, rectangle, marker, text), undo/redo
- Copy to clipboard, save to file, upload + shareable link
- Screenshot history, settings, system-tray (menu bar) mode

macOS will ask for **Screen Recording** permission the first time you
capture — approve it in *System Settings → Privacy & Security → Screen
Recording*, then relaunch AvroShot.

## Building locally

```bash
git clone https://github.com/avrojit-ovi/AvroShot.git
cd AvroShot
pip install -r linux/requirements.txt pyinstaller
pyinstaller --windowed --name AvroShot \
  --osx-bundle-identifier io.github.avroshot.AvroShot \
  --paths linux linux/avroshot/main.py
```
