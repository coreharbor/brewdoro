# Brewdoro

Brewdoro — минималистичный Pomodoro-таймер для Linux на Python 3.12, GTK 4 и
Libadwaita. Он поддерживает 25 минут фокуса, короткий 5-минутный и длинный
15-минутный перерыв, точную паузу, сброс, системные уведомления, звук завершения и
анимированную чашку кофе.

## Структура

```text
src/brewdoro/
├── __main__.py          # запуск через python -m brewdoro
├── application.py       # composition root и загрузка CSS
├── models.py            # режимы и состояния
├── notifications.py     # системные уведомления
├── sounds.py            # встроенный звук завершения
├── timer.py             # независимая от GTK модель таймера
├── window.py            # GTK-интерфейс и единственный GLib timeout
├── resources/style.css
└── widgets/coffee_cup.py
```

Модель таймера не зависит от GTK и использует внедряемый источник монотонного
времени. Окно отвечает только за связывание модели с виджетами и жизненный цикл
`GLib.timeout_add()`.

## Запуск на Ubuntu 24.04+

Установите системные зависимости:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-gi python3-cairo python3-gi-cairo \
  gir1.2-gtk-4.0 gir1.2-adw-1
```

PyGObject, GTK и Libadwaita устанавливаются через пакетный менеджер системы, а
не через PyPI. Поэтому окружению нужен доступ к системным Python-пакетам.

### Окружение через uv

```bash
cd /путь/к/Brewdoro
uv venv --python /usr/bin/python3 --system-site-packages .venv
uv pip install --python .venv/bin/python --editable .
```

Запуск установленной команды:

```bash
.venv/bin/brewdoro
```

Запуск непосредственно из исходников без установки пакета:

```bash
PYTHONPATH=src .venv/bin/python -m brewdoro
```

После editable-установки также доступна короткая команда:

```bash
make run
```

### Обычный venv

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --editable .
brewdoro
```

## Проверки

Unit-тесты модели не запускают GTK и используют управляемые тестовые часы:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

Полная локальная проверка при установленных `ruff`, `desktop-file-utils` и
`appstream`:

```bash
make check
```

## Добавление в меню приложений

Сначала создайте окружение и установите пакет в editable-режиме, затем:

```bash
make install-user
```

Команда устанавливает desktop-файл, SVG-иконку и AppStream-метаданные только
для текущего пользователя. Удаление:

```bash
make uninstall-user
```

## Flatpak

Flatpak использует GNOME Platform 50 и не зависит от версии GTK, Python или
Libadwaita в основной системе. Один и тот же пакет можно запускать в Ubuntu,
Debian, Fedora, Arch Linux, openSUSE и других дистрибутивах с Flatpak.

Установите инструменты сборки одним из способов:

```bash
# Ubuntu / Debian
sudo apt install flatpak flatpak-builder

# Fedora
sudo dnf install flatpak flatpak-builder

# Arch Linux
sudo pacman -S flatpak flatpak-builder

# openSUSE
sudo zypper install flatpak flatpak-builder
```

Добавьте Flathub и установите SDK:

```bash
flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

Сборка и установка локального Flatpak:

```bash
flatpak-builder --user --install --force-clean \
  .flatpak-build flatpak/ru.brewdoro.timer.yml
```

Запуск:

```bash
flatpak run ru.brewdoro.timer
```

Удаление:

```bash
flatpak uninstall ru.brewdoro.timer
```

Manifest предоставляет только доступ к Wayland/X11, аудио и системным уведомлениям.
Сеть, файловая система пользователя и фоновые службы приложению не доступны.

## Лицензия

Проект распространяется по лицензии MIT. Полный текст находится в `LICENSE`.
