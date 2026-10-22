#!/usr/bin/env bash
# Build an RPM for the Fedora/RHEL family or for openSUSE.
#
#   build_rpm.sh [fedora|opensuse]
#
# Output: linux/<family>/avroshot-<version>-1.noarch.rpm
#
# Requires rpmbuild (fedora: `dnf install rpm-build`, openSUSE: `zypper in rpm-build`).
set -euo pipefail

FAMILY="${1:-fedora}"
case "${FAMILY}" in
    fedora|opensuse) ;;
    *) echo "error: unknown RPM family '${FAMILY}' (expected fedora or opensuse)" >&2; exit 1 ;;
esac

PACKAGING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "${PACKAGING_DIR}/.." && pwd)"
OUT_DIR="${LINUX_DIR}/${FAMILY}"
VERSION="$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' "${LINUX_DIR}/avroshot/__init__.py")"
[ -n "${VERSION}" ] || { echo "error: could not read VERSION" >&2; exit 1; }

command -v rpmbuild >/dev/null 2>&1 || {
    echo "error: rpmbuild not found. Fedora: dnf install rpm-build | openSUSE: zypper in rpm-build" >&2
    exit 1
}

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

SRC_ROOT="${WORK}/avroshot-${VERSION}"
mkdir -p "${SRC_ROOT}"
bash "${PACKAGING_DIR}/stage_app.sh" "${SRC_ROOT}"
cp "${PACKAGING_DIR}/avroshot.spec" "${WORK}/avroshot.spec"
sed -i "s/^Version:.*/Version:        ${VERSION}/" "${WORK}/avroshot.spec"

TOPDIR="${WORK}/rpmbuild"
mkdir -p "${TOPDIR}/SOURCES" "${TOPDIR}/SPECS" "${TOPDIR}/BUILD" \
         "${TOPDIR}/BUILDROOT" "${TOPDIR}/RPMS" "${TOPDIR}/SRPMS"
tar -C "${WORK}" -czf "${TOPDIR}/SOURCES/avroshot-${VERSION}-linux.tar.gz" "avroshot-${VERSION}"
cp "${WORK}/avroshot.spec" "${TOPDIR}/SPECS/avroshot.spec"

rpmbuild -bb \
    --define "_topdir ${TOPDIR}" \
    --define "_rpmdir ${TOPDIR}/RPMS" \
    "${TOPDIR}/SPECS/avroshot.spec"

mkdir -p "${OUT_DIR}"
rm -f "${OUT_DIR}"/avroshot-*.rpm
BUILT_RPM="$(find "${TOPDIR}/RPMS" -name '*.rpm' | head -n 1)"
[ -n "${BUILT_RPM}" ] || { echo "error: rpmbuild produced no RPM" >&2; exit 1; }
cp "${BUILT_RPM}" "${OUT_DIR}/avroshot-${VERSION}-1.noarch.rpm"

echo "Built ${FAMILY} RPM: ${OUT_DIR}/avroshot-${VERSION}-1.noarch.rpm"
