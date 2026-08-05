from __future__ import annotations

import math
from typing import Final

import gi

from brewdoro.models import TIMER_MODES, TimerMode, TimerState
from brewdoro.notifications import NotificationService
from brewdoro.sounds import SoundService
from brewdoro.timer import BrewdoroTimer

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk  # noqa: E402

from brewdoro.widgets import CoffeeCup  # noqa: E402


TICK_INTERVAL_MS: Final = 100


class BrewdoroWindow(Adw.ApplicationWindow):
    """GTK view and coordinator for a Pomodoro timer model."""

    def __init__(
        self,
        application: Adw.Application,
        timer: BrewdoroTimer,
        notifications: NotificationService,
        sounds: SoundService,
    ) -> None:
        super().__init__(application=application)
        self.set_title("Brewdoro")
        self.set_default_size(360, 480)
        self.set_resizable(False)

        self._timer = timer
        self._notifications = notifications
        self._sounds = sounds
        self._timeout_id: int | None = None

        self._mode_label = Gtk.Label(label=self._timer.mode.label)
        self._timer_label = Gtk.Label()
        self._coffee_cup = CoffeeCup()
        self._primary_button = Gtk.Button(label="Начать")
        self._reset_button = Gtk.Button(label="Сбросить")
        self._preset_buttons: list[Gtk.ToggleButton] = []

        self._build_ui()
        self._update_time_and_cup()
        self.connect("close-request", self._on_close_request)

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.add_css_class("app-background")
        self.set_content(root)

        header = Adw.HeaderBar()
        header.add_css_class("flat-header")
        header.set_show_title(False)
        root.append(header)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            vexpand=True,
        )
        content.set_size_request(296, -1)
        content.set_margin_bottom(32)
        root.append(content)

        self._mode_label.add_css_class("mode-label")
        content.append(self._mode_label)

        self._timer_label.add_css_class("timer-label")
        self._timer_label.set_margin_top(12)
        content.append(self._timer_label)

        self._coffee_cup.set_margin_top(18)
        content.append(self._coffee_cup)

        self._primary_button.add_css_class("suggested-action")
        self._primary_button.add_css_class("primary-button")
        self._primary_button.set_hexpand(True)
        self._primary_button.set_margin_top(26)
        self._primary_button.connect("clicked", self._on_primary_clicked)
        content.append(self._primary_button)

        self._reset_button.add_css_class("flat")
        self._reset_button.add_css_class("reset-button")
        self._reset_button.set_halign(Gtk.Align.CENTER)
        self._reset_button.set_margin_top(8)
        self._reset_button.connect("clicked", self._on_reset_clicked)
        content.append(self._reset_button)

        presets_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            homogeneous=True,
        )
        presets_box.add_css_class("presets")
        presets_box.set_margin_top(28)
        content.append(presets_box)

        group_leader: Gtk.ToggleButton | None = None
        for mode in TIMER_MODES:
            button = Gtk.ToggleButton(label=f"{mode.minutes} мин")
            button.add_css_class("preset-button")
            if group_leader is None:
                group_leader = button
            else:
                button.set_group(group_leader)
            button.connect("toggled", self._on_preset_toggled, mode)
            presets_box.append(button)
            self._preset_buttons.append(button)

        self._preset_buttons[0].set_active(True)

    def _on_primary_clicked(self, _button: Gtk.Button) -> None:
        if self._timer.state is TimerState.RUNNING:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self) -> None:
        if not self._timer.start():
            return
        self._remove_timeout()
        self._notifications.withdraw_finished()
        self._update_time_and_cup()
        self._primary_button.set_label("Пауза")
        self._set_presets_sensitive(False)
        self._timeout_id = GLib.timeout_add(TICK_INTERVAL_MS, self._on_tick)

    def _pause_timer(self) -> None:
        finished = self._timer.pause()
        self._remove_timeout()
        self._update_time_and_cup()
        if finished:
            self._show_finished()
            return
        self._primary_button.set_label("Продолжить")

    def _on_tick(self) -> bool:
        if self._timer.state is not TimerState.RUNNING:
            self._timeout_id = None
            return GLib.SOURCE_REMOVE

        finished = self._timer.tick()
        self._update_time_and_cup()
        if finished:
            self._show_finished()
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _show_finished(self) -> None:
        self._remove_timeout()
        self._primary_button.set_label("Начать снова")
        self._set_presets_sensitive(True)
        self._notifications.send_finished(self._timer.mode)
        self._sounds.play_finished()

    def _on_reset_clicked(self, _button: Gtk.Button) -> None:
        self._remove_timeout()
        self._notifications.withdraw_finished()
        self._timer.reset()
        self._update_time_and_cup()
        self._primary_button.set_label("Начать")
        self._set_presets_sensitive(True)

    def _on_preset_toggled(
        self,
        button: Gtk.ToggleButton,
        mode: TimerMode,
    ) -> None:
        if not button.get_active() or not self._timer.select_mode(mode):
            return
        self._mode_label.set_label(mode.label)
        self._update_time_and_cup()
        self._primary_button.set_label("Начать")

    def _update_time_and_cup(self) -> None:
        visible_seconds = max(0, math.ceil(self._timer.remaining_seconds))
        minutes, seconds = divmod(visible_seconds, 60)
        self._timer_label.set_label(f"{minutes:02d}:{seconds:02d}")
        self._coffee_cup.set_liquid_level(self._timer.liquid_level)

    def _set_presets_sensitive(self, sensitive: bool) -> None:
        for button in self._preset_buttons:
            button.set_sensitive(sensitive)

    def _remove_timeout(self) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def _on_close_request(self, _window: Adw.ApplicationWindow) -> bool:
        self._remove_timeout()
        return False
