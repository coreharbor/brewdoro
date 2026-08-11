from __future__ import annotations

import gi

from brewdoro.i18n import Language, strings_for
from brewdoro.models import TimerMode

gi.require_version("Gio", "2.0")

from gi.repository import Gio  # noqa: E402


NOTIFICATION_ID = "timer-finished"


class NotificationService:
    def __init__(self, application: Gio.Application) -> None:
        self._application = application

    def send_finished(self, mode: TimerMode, language: Language) -> None:
        title, body = strings_for(language).finished_notification(mode)

        notification = Gio.Notification.new(title)
        notification.set_body(body)
        notification.set_icon(Gio.ThemedIcon.new("alarm-symbolic"))
        self._application.send_notification(NOTIFICATION_ID, notification)

    def withdraw_finished(self) -> None:
        self._application.withdraw_notification(NOTIFICATION_ID)
