# Contributing to Brewdoro

Thanks for helping improve Brewdoro. Small, focused changes are easiest to review and fit the project best.

## Before you start

- Check the [existing issues](https://github.com/coreharbor/brewdoro/issues).
- For a bug, include steps to reproduce it and your Linux distribution.
- For a new feature, explain the problem it solves. Brewdoro aims to stay lightweight and distraction-free.

## Development setup

Brewdoro requires Python 3.12 or newer, GTK 4 and Libadwaita.

On Ubuntu 24.04 or newer, install the system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-gi python3-cairo python3-gi-cairo \
  gir1.2-gtk-4.0 gir1.2-adw-1 desktop-file-utils appstream
```

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/coreharbor/brewdoro.git
cd brewdoro
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --editable . ruff
```

Run Brewdoro from the repository:

```bash
make run
```

## Before opening a pull request

Run the full check suite:

```bash
make check
```

Add or update tests when behavior changes. In the pull request, briefly describe what changed, why it changed and how you tested it.
