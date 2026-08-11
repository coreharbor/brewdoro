from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import gi

from brewdoro.i18n import Strings
from brewdoro.models import TimerMode
from brewdoro.settings import MAX_MINUTES, MIN_MINUTES, AppSettings

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


class SettingsMenu(Gtk.MenuButton):
    """Compact settings popover that reports immutable setting updates."""

    def __init__(
        self,
        settings: AppSettings,
        on_changed: Callable[[AppSettings], None],
    ) -> None:
        super().__init__()
        self._settings = settings
        self._on_changed = on_changed
        self._title = Gtk.Label()
        self._duration_labels: dict[TimerMode, Gtk.Label] = {}
        self._sound_label = Gtk.Label()
        self._cycle_label = Gtk.Label()
        self._auto_start_label = Gtk.Label()
        self._auto_start_switch = Gtk.Switch()
        self._popover = Gtk.Popover()
        self._build()

    @property
    def popover_visible(self) -> bool:
        return self._popover.get_visible()

    def update_text(self, strings: Strings) -> None:
        self.set_tooltip_text(strings.settings)
        self._title.set_label(strings.settings)
        self._duration_labels[TimerMode.FOCUS].set_label(strings.focus_duration)
        self._duration_labels[TimerMode.SHORT_BREAK].set_label(
            strings.short_break_duration,
        )
        self._duration_labels[TimerMode.LONG_BREAK].set_label(
            strings.long_break_duration,
        )
        self._sound_label.set_label(strings.sound)
        self._cycle_label.set_label(strings.pomodoro_cycle)
        self._auto_start_label.set_label(strings.auto_start)

    def _build(self) -> None:
        self.add_css_class("flat")
        self.add_css_class("settings-button")
        self.set_icon_name("preferences-system-symbolic")
        self.set_direction(Gtk.ArrowType.NONE)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        settings_box.add_css_class("settings-popover")
        settings_box.set_margin_top(12)
        settings_box.set_margin_bottom(12)
        settings_box.set_margin_start(12)
        settings_box.set_margin_end(12)

        self._title.add_css_class("settings-title")
        self._title.set_halign(Gtk.Align.START)
        settings_box.append(self._title)

        for mode, value in (
            (TimerMode.FOCUS, self._settings.focus_minutes),
            (TimerMode.SHORT_BREAK, self._settings.short_break_minutes),
            (TimerMode.LONG_BREAK, self._settings.long_break_minutes),
        ):
            label = Gtk.Label(halign=Gtk.Align.START, hexpand=True)
            spin = Gtk.SpinButton.new_with_range(MIN_MINUTES, MAX_MINUTES, 1)
            spin.set_value(value)
            spin.set_width_chars(3)
            spin.connect("value-changed", self._on_duration_changed, mode)
            self._append_row(settings_box, label, spin)
            self._duration_labels[mode] = label

        sound_switch = Gtk.Switch(active=self._settings.sound_enabled)
        sound_switch.connect("notify::active", self._on_sound_changed)
        self._append_row(settings_box, self._sound_label, sound_switch)

        cycle_switch = Gtk.Switch(active=self._settings.cycle_enabled)
        cycle_switch.connect("notify::active", self._on_cycle_changed)
        self._append_row(settings_box, self._cycle_label, cycle_switch)

        self._auto_start_switch.set_active(self._settings.auto_start_enabled)
        self._auto_start_switch.set_sensitive(self._settings.cycle_enabled)
        self._auto_start_switch.connect(
            "notify::active",
            self._on_auto_start_changed,
        )
        self._append_row(
            settings_box,
            self._auto_start_label,
            self._auto_start_switch,
        )

        self._popover.set_child(settings_box)
        self.set_popover(self._popover)

    @staticmethod
    def _append_row(
        parent: Gtk.Box,
        label: Gtk.Label,
        control: Gtk.Widget,
    ) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        row.add_css_class("settings-row")
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        control.set_valign(Gtk.Align.CENTER)
        row.append(label)
        row.append(control)
        parent.append(row)

    def _replace_settings(self, **changes: object) -> None:
        self._settings = replace(self._settings, **changes)
        self._on_changed(self._settings)

    def _on_duration_changed(
        self,
        spin: Gtk.SpinButton,
        mode: TimerMode,
    ) -> None:
        field_name = {
            TimerMode.FOCUS: "focus_minutes",
            TimerMode.SHORT_BREAK: "short_break_minutes",
            TimerMode.LONG_BREAK: "long_break_minutes",
        }[mode]
        self._replace_settings(**{field_name: spin.get_value_as_int()})

    def _on_sound_changed(
        self,
        switch: Gtk.Switch,
        _property: object,
    ) -> None:
        self._replace_settings(sound_enabled=switch.get_active())

    def _on_cycle_changed(
        self,
        switch: Gtk.Switch,
        _property: object,
    ) -> None:
        enabled = switch.get_active()
        self._auto_start_switch.set_sensitive(enabled)
        self._replace_settings(cycle_enabled=enabled)

    def _on_auto_start_changed(
        self,
        switch: Gtk.Switch,
        _property: object,
    ) -> None:
        self._replace_settings(auto_start_enabled=switch.get_active())
