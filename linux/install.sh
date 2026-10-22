#!/usr/bin/env bash
set -euo pipefail

# User-level installer for AvroShot on Ubuntu Linux (Wayland & X11)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
APPS_DIR="${HOME}/.local/share/applications"
ICON_THEME_DIR="${HOME}/.local/share/icons/hicolor"
ICON_SCALABLE_DIR="${ICON_THEME_DIR}/scalable/apps"

mkdir -p "${BIN_DIR}" "${APPS_DIR}" "${ICON_SCALABLE_DIR}"

echo "[1/5] Checking Python & PyQt6..."
if ! python3 -c "import PyQt6" >/dev/null 2>&1; then
    echo "Installing PyQt6 for current user..."
    pip install --user --break-system-packages PyQt6
fi

echo "[2/5] Installing avroshot command to ${BIN_DIR}/avroshot..."
# Copy the package into ~/.local/share/avroshot so the command keeps working
# even if the repository folder is moved or deleted afterwards.
APP_DIR="${HOME}/.local/share/avroshot"
rm -rf "${APP_DIR}/avroshot"
mkdir -p "${APP_DIR}"
cp -r "${ROOT_DIR}/avroshot" "${APP_DIR}/"
find "${APP_DIR}/avroshot" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
cat > "${BIN_DIR}/avroshot" << EOF
#!/usr/bin/env python3
import sys

APP_DIR = ${APP_DIR@Q}
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from avroshot.main import main

if __name__ == "__main__":
    raise SystemExit(main())
EOF
chmod +x "${BIN_DIR}/avroshot"

if ! "${BIN_DIR}/avroshot" --version >/dev/null 2>&1; then
    echo "ERROR: ${BIN_DIR}/avroshot cannot start - the avroshot package was not found in ${APP_DIR}." >&2
    echo "       Fix PyQt6 first (pip install --user PyQt6) and re-run this script." >&2
    exit 1
fi

echo "[3/5] Installing Desktop Application entry & icons..."
# Older installs wrote a second desktop file, which showed up as a duplicate
# 'AvroShot' entry in the application grid - drop it.
rm -f "${APPS_DIR}/avroshot.desktop"

cp "${ROOT_DIR}/assets/avroshot.svg" "${ICON_SCALABLE_DIR}/avroshot.svg"

# Render the PNG sizes the shell actually asks for, then refresh the caches.
# Without the cache refresh the grid keeps showing a generic gear icon.
PYTHONPATH="${APP_DIR}" python3 - << 'PY'
import os

from PyQt6.QtWidgets import QApplication

from avroshot.ui import create_app_icon

app = QApplication([])
icon = create_app_icon(256)
base = os.path.expanduser("~/.local/share/icons/hicolor")
for size in (16, 24, 32, 48, 64, 128, 256):
    target = os.path.join(base, f"{size}x{size}", "apps")
    os.makedirs(target, exist_ok=True)
    icon.pixmap(size, size).save(os.path.join(target, "avroshot.png"), "PNG")
print("Rendered AvroShot icons:", ", ".join(f"{s}x{s}" for s in (16, 24, 32, 48, 64, 128, 256)))
PY

# Single menu entry: launching it opens the Settings window, the captured
# shortcut and the right-click actions handle screenshots.
sed "s|^Exec=avroshot|Exec=${BIN_DIR}/avroshot|g" \
    "${ROOT_DIR}/assets/io.github.avroshot.AvroShot.desktop" \
    > "${APPS_DIR}/io.github.avroshot.AvroShot.desktop"
chmod +x "${APPS_DIR}/io.github.avroshot.AvroShot.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q "${APPS_DIR}" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "${ICON_THEME_DIR}" >/dev/null 2>&1 || true
fi

echo "[4/5] Configuring Wayland Portal screenshot permission & Global Shortcut..."
"${BIN_DIR}/avroshot" --register-shortcut "<Super><Shift>s" || true

echo "[5/5] Building .deb package in ${ROOT_DIR}/debian/..."
bash "${ROOT_DIR}/packaging/build_deb.sh"

echo ""
echo "✅ AvroShot installed successfully!"
echo "   • Command:        ${BIN_DIR}/avroshot"
echo "   • Hotkey:         Super+Shift+S (Windows+Shift+S)"
echo "   • App Launcher:   'AvroShot' in the applications grid opens Settings"
echo "   • Capture:        Super+Shift+S, or right-click the icon for the actions"
echo "   • Debian Package: ${ROOT_DIR}/debian/avroshot_1.0.0_all.deb"
