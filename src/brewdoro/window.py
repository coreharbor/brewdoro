from __future__ import annotations

import logging
import math
from typing import Final

import gi

from brewdoro.cycle import PomodoroCycle
from brewdoro.i18n import Language, LanguageStore, Strings, strings_for
from brewdoro.models import TIMER_MODES, TimerMode, TimerState
from brewdoro.notifications import NotificationService
from brewdoro.session import SavedSession, SessionStore
from brewdoro.settings import AppSettings, SettingsStore
from brewdoro.sounds import SoundService
from brewdoro.timer import BrewdoroTimer

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, GLib, Gtk  # noqa: E402

from brewdoro.widgets import CoffeeCup  # noqa: E402
from brewdoro.widgets.settings_menu import SettingsMenu  # noqa: E402


TICK_INTERVAL_MS: Final = 100
LOGGER = logging.getLogger(__name__)


class BrewdoroWindow(Adw.ApplicationWindow):
    """GTK view and coordinator for a Pomodoro timer model."""

    def __init__(
        self,
        application: Adw.Application,
        timer: BrewdoroTimer,
        notifications: NotificationService,
        sounds: SoundService,
        language_store: LanguageStore | None = None,
        settings: AppSettings | None = None,
        settings_store: SettingsStore | None = None,
        session_store: SessionStore | None = None,
        cycle: PomodoroCycle | None = None,
        restored_finished: bool = False,
    ) -> None:
        super().__init__(application=application)
        self.set_title("Brewdoro")
        self.set_default_size(360, 480)
        self.set_resizable(False)

        self._timer = timer
        self._notifications = notifications
        self._sounds = sounds
        self._timeout_id: int | None = None
        self._language_store = language_store or LanguageStore()
        self._language = self._language_store.load()
        self._strings: Strings = strings_for(self._language)
        self._settings_store = settings_store or SettingsStore()
        self._settings = settings or self._settings_store.load()
        self._session_store = session_store or SessionStore()
        self._cycle = cycle or PomodoroCycle()
        self._syncing_presets = False

        self._mode_label = Gtk.Label()
        self._cycle_label = Gtk.Label()
        self._timer_label = Gtk.Label()
        self._coffee_cup = CoffeeCup()
        self._primary_button = Gtk.Button()
        self._reset_button = Gtk.Button()
        self._language_button = Gtk.MenuButton()
        self._language_popover = Gtk.Popover()
        self._language_option_buttons: dict[Language, Gtk.Button] = {}
        self._settings_menu = SettingsMenu(
            self._settings,
            self._on_settings_changed,
        )
        self._preset_buttons: list[Gtk.ToggleButton] = []

        self._build_ui()
        self._update_text()
        self._update_time_and_cup()
        self._sync_selected_preset()
        self._set_controls_sensitive()
        self._install_keyboard_shortcuts()
        if self._timer.state is TimerState.RUNNING:
            self._timeout_id = GLib.timeout_add(TICK_INTERVAL_MS, self._on_tick)
        elif restored_finished:
            GLib.idle_add(self._show_restored_finished)
        self.connect("close-request", self._on_close_request)

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.add_css_class("app-background")
        self.set_content(root)

        header = Adw.HeaderBar()
        header.add_css_class("flat-header")
        header.set_show_title(False)
        self._build_language_menu(header)
        header.pack_start(self._settings_menu)
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

        self._cycle_label.add_css_class("cycle-label")
        self._cycle_label.set_margin_top(4)
        content.append(self._cycle_label)

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
            button = Gtk.ToggleButton()
            button.add_css_class("preset-button")
            if group_leader is None:
                group_leader = button
            else:
                button.set_group(group_leader)
            button.connect("toggled", self._on_preset_toggled, mode)
            presets_box.append(button)
            self._preset_buttons.append(button)

    def _build_language_menu(self, header: Adw.HeaderBar) -> None:
        self._language_button.add_css_class("flat")
        self._language_button.add_css_class("language-button")
        self._language_button.set_direction(Gtk.ArrowType.NONE)
        header.pack_end(self._language_button)

        language_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
        )
        language_box.set_margin_top(6)
        language_box.set_margin_bottom(6)
        language_box.set_margin_start(6)
        language_box.set_margin_end(6)

        for language in Language:
            button = Gtk.Button(label=language.display_name)
            button.add_css_class("flat")
            button.add_css_class("language-option")
            button.connect("clicked", self._on_language_selected, language)
            language_box.append(button)
            self._language_option_buttons[language] = button

        self._language_popover.set_child(language_box)
        self._language_button.set_popover(self._language_popover)

    def _on_language_selected(
        self,
        _button: Gtk.Button,
        language: Language,
    ) -> None:
        if language is not self._language:
            self._language = language
            self._strings = strings_for(language)
            if not self._language_store.save(language):
                LOGGER.warning("Could not save language preference")
            self._update_text()
        self._language_popover.popdown()

    def _on_settings_changed(self, settings: AppSettings) -> None:
        durations_changed = settings.durations != self._settings.durations
        cycle_was_disabled = self._settings.cycle_enabled and not settings.cycle_enabled
        self._settings = settings
        if cycle_was_disabled:
            self._cycle.reset()
        if durations_changed and not self._timer.update_durations(settings.durations):
            LOGGER.warning("Ignored duration change during an active session")
            return
        self._save_settings()
        self._update_text()
        self._update_time_and_cup()
        self._save_session()

    def _on_primary_clicked(self, _button: Gtk.Button | None) -> None:
        if self._timer.state is TimerState.RUNNING:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self, withdraw_notification: bool = True) -> None:
        if not self._timer.start():
            return
        self._remove_timeout()
        if withdraw_notification:
            self._notifications.withdraw_finished()
        self._update_time_and_cup()
        self._update_text()
        self._set_controls_sensitive()
        self._save_session()
        self._timeout_id = GLib.timeout_add(TICK_INTERVAL_MS, self._on_tick)

    def _pause_timer(self) -> None:
        finished = self._timer.pause()
        self._remove_timeout()
        self._update_time_and_cup()
        if finished:
            self._show_finished()
            return
        self._update_text()
        self._set_controls_sensitive()
        self._save_session()

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
        finished_mode = self._timer.mode
        self._notifications.send_finished(finished_mode, self._language)
        if self._settings.sound_enabled:
            self._sounds.play_finished()

        if self._settings.cycle_enabled:
            next_mode = self._cycle.complete(finished_mode)
            self._timer.select_mode(next_mode)
            self._sync_selected_preset()
            if self._settings.auto_start_enabled:
                self._start_timer(withdraw_notification=False)
                return

        self._update_text()
        self._update_time_and_cup()
        self._set_controls_sensitive()
        self._save_session()

    def _show_restored_finished(self) -> bool:
        self._show_finished()
        return GLib.SOURCE_REMOVE

    def _on_reset_clicked(self, _button: Gtk.Button | None) -> None:
        self._remove_timeout()
        self._notifications.withdraw_finished()
        self._timer.reset()
        self._update_time_and_cup()
        self._update_text()
        self._set_controls_sensitive()
        self._save_session()

    def _on_preset_toggled(
        self,
        button: Gtk.ToggleButton,
        mode: TimerMode,
    ) -> None:
        if (
            self._syncing_presets
            or not button.get_active()
            or not self._timer.select_mode(mode)
        ):
            return
        self._update_text()
        self._update_time_and_cup()
        self._save_session()

    def _update_text(self) -> None:
        self._mode_label.set_label(self._strings.mode_label(self._timer.mode))
        self._primary_button.set_label(
            self._strings.primary_button_label(self._timer.state),
        )
        self._reset_button.set_label(self._strings.reset)
        self._language_button.set_label(self._language.short_label)
        self._language_button.set_tooltip_text(self._strings.change_language)
        self._settings_menu.update_text(self._strings)

        for button, mode in zip(self._preset_buttons, TIMER_MODES, strict=True):
            button.set_label(
                self._strings.preset_label(
                    self._settings.durations.minutes_for(mode),
                ),
            )

        for language, button in self._language_option_buttons.items():
            if language is self._language:
                button.add_css_class("selected-language")
            else:
                button.remove_css_class("selected-language")
        self._update_cycle_label()

    def _update_time_and_cup(self) -> None:
        visible_seconds = max(0, math.ceil(self._timer.remaining_seconds))
        minutes, seconds = divmod(visible_seconds, 60)
        self._timer_label.set_label(f"{minutes:02d}:{seconds:02d}")
        self._coffee_cup.set_liquid_level(self._timer.liquid_level)

    def _update_cycle_label(self) -> None:
        self._cycle_label.set_visible(self._settings.cycle_enabled)
        if self._settings.cycle_enabled:
            self._cycle_label.set_label(
                self._strings.cycle_progress.format(
                    position=self._cycle.position_for(self._timer.mode),
                ),
            )

    def _set_controls_sensitive(self) -> None:
        sensitive = not self._timer.has_active_session
        for button in self._preset_buttons:
            button.set_sensitive(sensitive)
        self._settings_menu.set_sensitive(sensitive)

    def _sync_selected_preset(self) -> None:
        self._syncing_presets = True
        try:
            mode_index = TIMER_MODES.index(self._timer.mode)
            self._preset_buttons[mode_index].set_active(True)
        finally:
            self._syncing_presets = False

    def _install_keyboard_shortcuts(self) -> None:
        controller = Gtk.EventControllerKey()
        controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

    def _on_key_pressed(
        self,
        _controller: Gtk.EventControllerKey,
        keyval: int,
        _keycode: int,
        state: Gdk.ModifierType,
    ) -> bool:
        blocked_modifiers = (
            Gdk.ModifierType.CONTROL_MASK
            | Gdk.ModifierType.ALT_MASK
            | Gdk.ModifierType.SUPER_MASK
        )
        if (
            state & blocked_modifiers
            or self._settings_menu.popover_visible
            or self._language_popover.get_visible()
        ):
            return False

        if keyval == Gdk.KEY_space:
            self._on_primary_clicked(None)
            return True
        if keyval == Gdk.KEY_r:
            self._on_reset_clicked(None)
            return True

        key_modes = {
            Gdk.KEY_1: TimerMode.FOCUS,
            Gdk.KEY_2: TimerMode.SHORT_BREAK,
            Gdk.KEY_3: TimerMode.LONG_BREAK,
            Gdk.KEY_KP_1: TimerMode.FOCUS,
            Gdk.KEY_KP_2: TimerMode.SHORT_BREAK,
            Gdk.KEY_KP_3: TimerMode.LONG_BREAK,
        }
        mode = key_modes.get(keyval)
        if mode is None or self._timer.has_active_session:
            return False
        self._preset_buttons[TIMER_MODES.index(mode)].set_active(True)
        return True

    def _save_settings(self) -> None:
        if not self._settings_store.save(self._settings):
            LOGGER.warning("Could not save application settings")

    def _save_session(self) -> None:
        session = SavedSession(
            timer=self._timer.snapshot(),
            completed_focus_sessions=self._cycle.completed_focus_sessions,
        )
        if not self._session_store.save(session):
            LOGGER.warning("Could not save timer session")

    def _remove_timeout(self) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def _on_close_request(self, _window: Adw.ApplicationWindow) -> bool:
        self._save_session()
        self._remove_timeout()
        self._sounds.close()
        return False
