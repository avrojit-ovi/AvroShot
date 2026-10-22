#!/usr/bin/env bash
# Stage the distro-independent install tree shared by every Linux package builder.
#
#   stage_app.sh <destdir>
#
# The resulting tree is a plain filesystem root (usr/bin, usr/share/...) that
# .deb, .rpm and Arch builders copy straight into their package root.
set -euo pipefail

DEST="${1:?usage: stage_app.sh <destdir>}"
PACKAGING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "${PACKAGING_DIR}/.." && pwd)"
REPO_DIR="$(cd "${LINUX_DIR}/.." && pwd)"
VERSION="$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' "${LINUX_DIR}/avroshot/__init__.py")"

if [ -z "${VERSION}" ]; then
    echo "error: could not read VERSION from avroshot/__init__.py" >&2
    exit 1
fi

APP_ROOT="${DEST}/usr/share/avroshot"
rm -rf "${DEST}"
mkdir -p "${APP_ROOT}" \
    "${DEST}/usr/bin" \
    "${DEST}/usr/share/applications" \
    "${DEST}/usr/share/icons/hicolor/scalable/apps" \
    "${DEST}/usr/share/doc/avroshot"

# Python package (no bytecode / caches)
tar -C "${LINUX_DIR}" --exclude='__pycache__' --exclude='*.pyc' -cf - avroshot \
    | tar -C "${APP_ROOT}" -xf -

# Launcher: puts the installed tree on PYTHONPATH and runs `python3 -m avroshot`
cat > "${DEST}/usr/bin/avroshot" << 'EOF'
#!/bin/sh
# AvroShot - Lightshot-style screenshot & annotation tool
APP_DIR="/usr/share/avroshot"
PYTHONPATH="${APP_DIR}${PYTHONPATH:+:${PYTHONPATH}}"
export PYTHONPATH
exec python3 -m avroshot "$@"
EOF
chmod 0755 "${DEST}/usr/bin/avroshot"

# One menu entry only - a second file would show up as a duplicate AvroShot icon
install -m 0644 "${LINUX_DIR}/assets/io.github.avroshot.AvroShot.desktop" \
    "${DEST}/usr/share/applications/io.github.avroshot.AvroShot.desktop"

# Icon
install -m 0644 "${LINUX_DIR}/assets/avroshot.svg" \
    "${DEST}/usr/share/icons/hicolor/scalable/apps/avroshot.svg"

# Docs
install -m 0644 "${REPO_DIR}/README.md" "${DEST}/usr/share/doc/avroshot/README.md"
install -m 0644 "${REPO_DIR}/CHANGELOG.md" "${DEST}/usr/share/doc/avroshot/CHANGELOG.md"
install -m 0644 "${REPO_DIR}/LICENSE" "${DEST}/usr/share/doc/avroshot/LICENSE"

# Normalise ownership-independent permissions so every package format agrees
find "${DEST}" -type d -exec chmod 0755 {} +
find "${DEST}" -type f -exec chmod 0644 {} +
chmod 0755 "${DEST}/usr/bin/avroshot"

echo "Staged AvroShot ${VERSION} install tree in ${DEST}"
