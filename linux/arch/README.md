# AvroShot for Arch Linux / Manjaro

**`avroshot-1.0.0-1-any.pkg.tar.zst`** — for Arch Linux, Manjaro,
EndeavourOS, Garuda Linux, CachyOS and other `pacman` distributions.

```bash
sudo pacman -U ./avroshot-1.0.0-1-any.pkg.tar.zst
```

Dependencies (`python`, `python-pyqt6`, `python-gobject`, `python-dbus`,
`xdg-desktop-portal`) are resolved by `pacman`. Optional extras:
`wl-clipboard`, `xclip`, `libnotify`, `grim`, `spectacle`, `gnome-screenshot`.

Then launch **AvroShot** from your application menu, or run `avroshot`.

## Rebuild

Run this on an Arch host **as a normal user** (`makepkg` refuses to run as root):

```bash
sudo pacman -S --needed base-devel
bash linux/packaging/build_arch.sh
```

The recipe is `linux/packaging/PKGBUILD`, so it can also be published to the AUR
unchanged.
