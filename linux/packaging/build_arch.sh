#!/usr/bin/env bash
# Build the Arch Linux package: linux/arch/avroshot-<version>-1-any.pkg.tar.zst
#
# Covers Arch Linux, Manjaro, EndeavourOS, Garuda, CachyOS and other
# pacman-based distributions.
#
# Requires makepkg (from pacman/base-devel) and must NOT run as root.
set -euo pipefail

PACKAGING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "${PACKAGING_DIR}/.." && pwd)"
OUT_DIR="${LINUX_DIR}/arch"
VERSION="$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' "${LINUX_DIR}/avroshot/__init__.py")"
[ -n "${VERSION}" ] || { echo "error: could not read VERSION" >&2; exit 1; }

command -v makepkg >/dev/null 2>&1 || {
    echo "error: makepkg not found. Install base-devel on Arch: pacman -S --needed base-devel" >&2
    exit 1
}
if [ "$(id -u)" -eq 0 ]; then
    echo "error: makepkg refuses to run as root - build as a normal user" >&2
    exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

SRC_ROOT="${WORK}/avroshot-${VERSION}"
mkdir -p "${SRC_ROOT}"
bash "${PACKAGING_DIR}/stage_app.sh" "${SRC_ROOT}"
tar -C "${WORK}" -czf "${WORK}/avroshot-${VERSION}-linux.tar.gz" "avroshot-${VERSION}"

BUILD_DIR="${WORK}/makepkg"
mkdir -p "${BUILD_DIR}"
cp "${PACKAGING_DIR}/PKGBUILD" "${BUILD_DIR}/PKGBUILD"
sed -i "s/^pkgver=.*/pkgver=${VERSION}/" "${BUILD_DIR}/PKGBUILD"
mv "${WORK}/avroshot-${VERSION}-linux.tar.gz" "${BUILD_DIR}/"

( cd "${BUILD_DIR}" && makepkg --force --nodeps --noprogressbar )

mkdir -p "${OUT_DIR}"
rm -f "${OUT_DIR}"/*.pkg.tar.zst
BUILT_PKG="$(find "${BUILD_DIR}" -maxdepth 1 -name '*.pkg.tar.zst' | head -n 1)"
[ -n "${BUILT_PKG}" ] || { echo "error: makepkg produced no package" >&2; exit 1; }
cp "${BUILT_PKG}" "${OUT_DIR}/avroshot-${VERSION}-1-any.pkg.tar.zst"

echo "Built Arch package: ${OUT_DIR}/avroshot-${VERSION}-1-any.pkg.tar.zst"
