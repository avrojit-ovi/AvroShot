# AvroShot for Fedora / RHEL

**`avroshot-1.0.2-1.noarch.rpm`** — for Fedora, RHEL 9/10, CentOS Stream,
Rocky Linux, AlmaLinux, Oracle Linux and Amazon Linux.

```bash
sudo dnf install ./avroshot-1.0.2-1.noarch.rpm
```

Runtime dependencies (`python3-qt6`, `python3-gobject`, `python3-dbus`,
`xdg-desktop-portal`) are pulled in automatically. `wl-clipboard` / `xclip`
are recommended for clipboard support.

Then launch **AvroShot** from your application menu, or run `avroshot`.

## Rebuild

Run this inside a Fedora container/host (needs `rpmbuild`):

```bash
sudo dnf install rpm-build
bash linux/packaging/build_rpm.sh fedora
```

The script shares `linux/packaging/avroshot.spec` with the openSUSE build and
selects the right binding package names per RPM family.
