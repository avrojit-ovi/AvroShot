# The payload is pure Python, so there is nothing to debug or strip.
%global debug_package %{nil}

Name:           avroshot
Version:        1.0.0
Release:        1
Summary:        Fast Lightshot-style screenshot and annotation tool
License:        MIT
URL:            https://github.com/avrojit-ovi/AvroShot
Source0:        %{name}-%{version}-linux.tar.gz
BuildArch:      noarch

Requires:       python3 >= 3.10
# PyQt6 / GLib bindings are named differently by the two RPM families.
%if 0%{?suse_version}
Requires:       python3-PyQt6
Requires:       python3-gobject
Requires:       python3-dbus-python
%else
Requires:       python3-qt6
Requires:       python3-gobject
Requires:       python3-dbus
%endif
Requires:       xdg-desktop-portal

Recommends:     wl-clipboard
Recommends:     xclip
Recommends:     libnotify
Suggests:       grim
Suggests:       spectacle

%description
AvroShot freezes your screen with a dimmed overlay, lets you drag and resize
a selection with 8 handles, annotate it with pen, line, arrow, rectangle,
marker and text (with undo/redo), then copy, save or upload it for a
shareable link.

It supports both Wayland (XDG Desktop Portal) and X11 sessions, offers a
system tray mode, delayed capture and a built-in screenshot history.

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a usr %{buildroot}/

%files
/usr/bin/avroshot
/usr/share/avroshot
/usr/share/applications/io.github.avroshot.AvroShot.desktop
/usr/share/icons/hicolor/scalable/apps/avroshot.svg
/usr/share/doc/avroshot

%changelog
* Thu Oct 23 2026 Ovi Chowdhury Joy <72299169+avrojit-ovi@users.noreply.github.com> - 1.0.0-1
- Initial Linux release: Wayland + X11 capture, annotation overlay, tray,
  screenshot history, delayed capture and cloud upload.
