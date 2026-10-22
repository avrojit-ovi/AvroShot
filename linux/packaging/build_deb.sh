#!/usr/bin/env bash
# Build the Debian/Ubuntu package: linux/debian/avroshot_<version>_all.deb
#
# Works on Debian, Ubuntu, Linux Mint, Pop!_OS, Zorin OS, elementary OS,
# Kali Linux, MX Linux and any other dpkg/apt distribution.
set -euo pipefail

PACKAGING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "${PACKAGING_DIR}/.." && pwd)"
REPO_DIR="$(cd "${LINUX_DIR}/.." && pwd)"
OUT_DIR="${LINUX_DIR}/debian"
PKG_NAME="avroshot"

VERSION="$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' "${LINUX_DIR}/avroshot/__init__.py")"
[ -n "${VERSION}" ] || { echo "error: could not read VERSION" >&2; exit 1; }

BUILD_ROOT="$(mktemp -d)"
trap 'rm -rf "${BUILD_ROOT}"' EXIT

bash "${PACKAGING_DIR}/stage_app.sh" "${BUILD_ROOT}"

# Debian wants the licence under usr/share/doc/<pkg>/copyright
install -m 0644 "${REPO_DIR}/LICENSE" "${BUILD_ROOT}/usr/share/doc/avroshot/copyright"

INSTALLED_SIZE="$(du -sk "${BUILD_ROOT}/usr" | cut -f1)"

mkdir -p "${BUILD_ROOT}/DEBIAN"
cat > "${BUILD_ROOT}/DEBIAN/control" << EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Architecture: all
Maintainer: Ovi Chowdhury Joy <72299169+avrojit-ovi@users.noreply.github.com>
Installed-Size: ${INSTALLED_SIZE}
Depends: python3 (>= 3.10), python3-pyqt6, python3-gi, python3-dbus, xdg-desktop-portal
Recommends: wl-clipboard | xclip, libnotify-bin, grim
Suggests: spectacle, gnome-screenshot
Section: graphics
Priority: optional
Homepage: https://github.com/avrojit-ovi/AvroShot
Description: Fast Lightshot-style screenshot and annotation tool
 AvroShot freezes your screen with a dimmed overlay, lets you drag and
 resize a selection with 8 handles, annotate it with pen, line, arrow,
 rectangle, marker and text (with undo/redo), then copy, save or upload
 it for a shareable link.
 .
 It supports both Wayland (XDG Desktop Portal) and X11 sessions, offers
 a system tray mode, delayed capture and a built-in screenshot history.
EOF

# Refresh the desktop/icon caches after install so the menu entry shows up
cat > "${BUILD_ROOT}/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 0755 "${BUILD_ROOT}/DEBIAN/postinst"

# Same cleanup on removal
cat > "${BUILD_ROOT}/DEBIAN/postrm" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 0755 "${BUILD_ROOT}/DEBIAN/postrm"

find "${BUILD_ROOT}" -type d -exec chmod 0755 {} +
chmod 0644 "${BUILD_ROOT}/DEBIAN/control"

mkdir -p "${OUT_DIR}"
OUT_DEB="${OUT_DIR}/${PKG_NAME}_${VERSION}_all.deb"
# Drop packages from older versions first: CI inspects and commits whatever sits
# in this folder, and a leftover .deb makes the avroshot_*.deb glob ambiguous.
rm -f "${OUT_DIR}/${PKG_NAME}"_*.deb
dpkg-deb --root-owner-group --build "${BUILD_ROOT}" "${OUT_DEB}" >/dev/null

echo "Built Debian package: ${OUT_DEB}"
