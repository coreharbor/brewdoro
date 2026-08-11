<div align="center">

# ☕ Brewdoro

**A minimal Pomodoro timer for Linux with an animated coffee cup.**

**Focus. Brew. Repeat.**

<br>

<img src="docs/images/social-preview.jpg" alt="Brewdoro — Pomodoro timer for Linux" width="800">

</div>

## About

**Brewdoro** is a small and distraction-free Pomodoro timer designed for the Linux desktop.

Instead of another progress bar, Brewdoro uses a coffee cup: while you focus, the coffee slowly disappears. During your break, the cup fills back up.

No accounts. No clutter. Just a timer, a cup of coffee, and your work.

## ✨ Features

- ☕ Animated coffee cup that visualizes timer progress
- 🎯 Focus and break cycles
- 🔁 Pomodoro session tracking
- 🌙 Minimal dark interface
- 🐧 Designed specifically for Linux
- 🎨 Native GTK 4 + Libadwaita UI
- 🌍 English, Russian and Chinese localization
- ⚡ Lightweight and distraction-free

## 📸 Screenshot

<div align="center">

<img src="docs/images/brewdoro.png" alt="Brewdoro application screenshot" width="420">

</div>

## 📦 Installation

### Flatpak

Brewdoro is not on Flathub yet, but you can build and install it locally with Flatpak.

First install the required runtime and SDK:

```bash
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

Clone Brewdoro:

```bash
git clone https://github.com/coreharbor/brewdoro.git
cd brewdoro
```

Build and install:

```bash
flatpak-builder --user --install --force-clean build-dir flatpak/ru.brewdoro.timer.yml
```

Run:

```bash
flatpak run ru.brewdoro.timer
```

## 🚀 Usage

Open Brewdoro and press **Start**.

During a focus session, the coffee gradually drains as the timer approaches zero. When it’s time for a break, the cup starts filling again.

Complete your sessions, take your breaks, and repeat.

## 🛠️ Built with

Brewdoro is built with:

- **Python**
- **GTK 4**
- **Libadwaita**
- **Flatpak**

The goal is to keep the application small, native-looking and comfortable to use on modern Linux desktops.

## 🌍 Translations

Brewdoro currently supports:

- 🇬🇧 English
- 🇷🇺 Russian
- 🇨🇳 Chinese

More translations are welcome.

Read the [Russian README](README.ru.md).

## 🧑‍💻 Development

Clone the repository:

```bash
git clone https://github.com/coreharbor/brewdoro.git
cd brewdoro
```

The project source code lives in [`src/brewdoro/`](src/brewdoro/).

Flatpak packaging files are located in [`flatpak/`](flatpak/).

Application metadata and desktop integration files are located in [`data/`](data/).

## 🤝 Contributing

If you find a bug, have an idea for Brewdoro, or want to improve a translation, read the [contribution guide](CONTRIBUTING.md) and open an issue or pull request.

## ⭐ Support Brewdoro

If Brewdoro is useful to you, consider giving the repository a **star**. It helps more Linux users discover the project.

<div align="center">

☕ **Focus. Brew. Repeat.**

</div>
