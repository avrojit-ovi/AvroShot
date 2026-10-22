# AvroShot for openSUSE / SLES

**`avroshot-1.0.0-1.noarch.rpm`** — for openSUSE Tumbleweed, openSUSE Leap 15.6+
and SUSE Linux Enterprise with the openSUSE repositories enabled.

```bash
sudo zypper install ./avroshot-1.0.0-1.noarch.rpm
```

openSUSE names the PyQt6 binding `python3-PyQt6` (Fedora calls it
`python3-qt6`), so this RPM is built from the same spec with the openSUSE
dependency set. `wl-clipboard` / `xclip` are recommended for clipboard support.

Then launch **AvroShot** from your application menu, or run `avroshot`.

## Rebuild

Run this inside an openSUSE container/host (needs `rpmbuild`):

```bash
sudo zypper install rpm-build
bash linux/packaging/build_rpm.sh opensuse
```
