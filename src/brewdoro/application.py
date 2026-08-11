from __future__ import annotations

import sys
from importlib import resources
from typing import Final

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_foreign("cairo")

from gi.repository import Adw, Gdk, Gtk  # noqa: E402

from brewdoro.notifications import NotificationService  # noqa: E402
from brewdoro.cycle import PomodoroCycle  # noqa: E402
from brewdoro.session import SessionStore  # noqa: E402
from brewdoro.settings import SettingsStore  # noqa: E402
from brewdoro.sounds import SoundService  # noqa: E402
from brewdoro.timer import BrewdoroTimer  # noqa: E402
from brewdoro.window import BrewdoroWindow  # noqa: E402


APPLICATION_ID: Final = "ru.brewdoro.timer"


class BrewdoroApplication(Adw.Application):
    """Composition root for the application and its dependencies."""

    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)
        self._window: BrewdoroWindow | None = None

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        self._load_css()

    def do_activate(self) -> None:
        if self._window is None:
            settings_store = SettingsStore()
            settings = settings_store.load()
            session_store = SessionStore()
            saved_session = session_store.load()
            timer = BrewdoroTimer(durations=settings.durations)
            cycle = PomodoroCycle(
                saved_session.completed_focus_sessions if saved_session else 0,
            )
            restored_finished = (
                timer.restore(saved_session.timer) if saved_session else False
            )
            notifications = NotificationService(self)
            sounds = SoundService()
            self._window = BrewdoroWindow(
                self,
                timer,
                notifications,
                sounds,
                settings=settings,
                settings_store=settings_store,
                session_store=session_store,
                cycle=cycle,
                restored_finished=restored_finished,
            )
        self._window.present()

    def _load_css(self) -> None:
        provider = Gtk.CssProvider()
        style_resource = resources.files("brewdoro").joinpath("resources/style.css")
        with resources.as_file(style_resource) as style_path:
            provider.load_from_path(str(style_path))

        display = Gdk.Display.get_default()
        if display is None:
            return
        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )


def main() -> int:
    application = BrewdoroApplication()
    return application.run(sys.argv)
