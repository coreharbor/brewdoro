# Brewdoro

[Русская версия](README.ru.md)

Brewdoro is a small Pomodoro timer for Linux, built with Python, GTK 4 and
Libadwaita. It stays out of the way while you work and lets you know when the
session is over.

<p align="center">
  <img src="docs/images/brewdoro.jpg" alt="Brewdoro focus timer" width="353">
</p>

## Features

- 25-minute focus sessions
- 5-minute and 15-minute breaks
- Pause, resume and reset
- Desktop notifications and a completion sound
- An animated coffee cup that follows the timer

## Install with Flatpak

Install `flatpak` and `flatpak-builder`, then run:

```bash
flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50

git clone https://github.com/coreharbor/brewdoro.git
cd brewdoro
flatpak-builder --user --install --force-clean \
  .flatpak-build flatpak/ru.brewdoro.timer.yml
flatpak run ru.brewdoro.timer
```

The Flatpak package can show notifications and play sound. It has no access to
the network or your personal files.

## Run from source on Ubuntu 24.04+

```bash
sudo apt update
sudo apt install python3 python3-venv python3-gi python3-cairo python3-gi-cairo \
  gir1.2-gtk-4.0 gir1.2-adw-1

git clone https://github.com/coreharbor/brewdoro.git
cd brewdoro
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --editable .
make install-user
brewdoro
```

## Development

Run the checks with:

```bash
make check
```

The timer model does not depend on GTK, so its tests can run without a desktop
session.

## License

[MIT](LICENSE)
