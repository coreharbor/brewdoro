from __future__ import annotations

import logging

import gi

from brewdoro.i18n import Language, strings_for
from brewdoro.models import TimerMode

gi.require_version("Gio", "2.0")

from gi.repository import Gio  # noqa: E402


NOTIFICATION_ID = "timer-finished"
LOGGER = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, application: Gio.Application) -> None:
        self._application = application

    def send_finished(self, mode: TimerMode, language: Language) -> None:
        try:
            title, body = strings_for(language).finished_notification(mode)

            notification = Gio.Notification.new(title)
            notification.set_body(body)
            notification.set_icon(Gio.ThemedIcon.new("alarm-symbolic"))
            self._application.send_notification(NOTIFICATION_ID, notification)
        except Exception:
            LOGGER.exception("Could not send the timer completion notification")

    def withdraw_finished(self) -> None:
        try:
            self._application.withdraw_notification(NOTIFICATION_ID)
        except Exception:
            LOGGER.exception("Could not withdraw the timer completion notification")
