# AvroShot for Debian / Ubuntu

**`avroshot_1.0.2_all.deb`** — one package for every `apt`/`dpkg` distribution:
Debian 12+, Ubuntu 22.04/24.04+, Linux Mint, Pop!_OS, Zorin OS, elementary OS,
Kali Linux, MX Linux, Deepin and Raspbian-style derivatives.

```bash
sudo apt install ./avroshot_1.0.2_all.deb
```

`apt` resolves the runtime dependencies automatically (`python3-pyqt6`,
`python3-gi`, `python3-dbus`, `xdg-desktop-portal`). `wl-clipboard`/`xclip`
are recommended so copy-to-clipboard works on Wayland/X11.

Then launch **AvroShot** from your application menu, or run `avroshot`.

## Rebuild

```bash
bash linux/packaging/build_deb.sh
```

The package installs:

| Path | Purpose |
| --- | --- |
| `/usr/bin/avroshot` | launcher |
| `/usr/share/avroshot/avroshot/` | Python sources |
| `/usr/share/applications/avroshot.desktop` | application menu entry |
| `/usr/share/icons/hicolor/scalable/apps/avroshot.svg` | icon |
| `/usr/share/doc/avroshot/` | README, CHANGELOG, LICENSE |
