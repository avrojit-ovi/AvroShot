#!/usr/bin/env bash
set -euo pipefail

# Build a Debian/Ubuntu .deb package for AvroShot
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="1.0.0"
PKG_NAME="avroshot"
ARCH="all"
BUILD_ROOT="${ROOT_DIR}/packaging/build/${PKG_NAME}_${VERSION}_${ARCH}"
DIST_DIR="${ROOT_DIR}/dist"

rm -rf "${BUILD_ROOT}"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/lib/python3/dist-packages"
mkdir -p "${BUILD_ROOT}/usr/share/applications"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${DIST_DIR}"

# Copy Python package
cp -r "${ROOT_DIR}/avroshot" "${BUILD_ROOT}/usr/lib/python3/dist-packages/"
find "${BUILD_ROOT}/usr/lib/python3/dist-packages/avroshot" -name "__pycache__" -type d -exec rm -rf {} +

# Create /usr/bin/avroshot executable launcher
cat > "${BUILD_ROOT}/usr/bin/avroshot" << 'EOF'
#!/usr/bin/env python3
import sys
from avroshot.main import main

if __name__ == "__main__":
    raise SystemExit(main())
EOF
chmod 0755 "${BUILD_ROOT}/usr/bin/avroshot"

# Copy desktop files and icon
cp "${ROOT_DIR}/assets/io.github.avroshot.AvroShot.desktop" "${BUILD_ROOT}/usr/share/applications/io.github.avroshot.AvroShot.desktop"
cp "${ROOT_DIR}/assets/io.github.avroshot.AvroShot.desktop" "${BUILD_ROOT}/usr/share/applications/avroshot.desktop"
cp "${ROOT_DIR}/assets/avroshot.svg" "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps/avroshot.svg"

# Create DEBIAN/control
cat > "${BUILD_ROOT}/DEBIAN/control" << EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-pyqt6, python3-gi, python3-dbus, xdg-desktop-portal
Recommends: wl-clipboard, xclip, libnotify-bin
Maintainer: AvroShot Contributors <avroshot@users.noreply.github.com>
Homepage: https://github.com/avroshot/AvroShot
Description: Fast Lightshot-style Screenshot & Annotation Tool for Ubuntu Linux
 AvroShot freezes the screen with a dimmed overlay, lets you drag and resize
 a selection with 8 handles, annotate with Pen, Line, Arrow, Rectangle,
 Highlighter Marker, and Text with Undo/Redo, and quickly Copy, Save, or
 Upload for a shareable link. Works on both Wayland and X11.
EOF

chmod 0755 "${BUILD_ROOT}/DEBIAN"
chmod 0644 "${BUILD_ROOT}/DEBIAN/control"

OUT_DEB="${DIST_DIR}/${PKG_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group --build "${BUILD_ROOT}" "${OUT_DEB}"
echo "Built Debian package: ${OUT_DEB}"
