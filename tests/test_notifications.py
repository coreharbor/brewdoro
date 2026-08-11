from __future__ import annotations

import importlib
import sys
import types
import unittest

from brewdoro.i18n import Language
from brewdoro.models import TimerMode


class FailingApplication:
    def send_notification(self, *_args: object) -> None:
        raise RuntimeError("notification service unavailable")

    def withdraw_notification(self, *_args: object) -> None:
        raise RuntimeError("notification service unavailable")


class FakeNotification:
    @classmethod
    def new(cls, _title: str) -> FakeNotification:
        return cls()

    def set_body(self, _body: str) -> None:
        pass

    def set_icon(self, _icon: object) -> None:
        pass


def import_notifications_with_fake_gio() -> types.ModuleType:
    gi = types.ModuleType("gi")
    gi.require_version = lambda *_args: None

    repository = types.ModuleType("gi.repository")
    repository.Gio = types.SimpleNamespace(
        Application=object,
        Notification=FakeNotification,
        ThemedIcon=types.SimpleNamespace(new=lambda _name: object()),
    )
    gi.repository = repository

    sys.modules["gi"] = gi
    sys.modules["gi.repository"] = repository
    sys.modules.pop("brewdoro.notifications", None)
    return importlib.import_module("brewdoro.notifications")


class NotificationServiceTests(unittest.TestCase):
    def test_notification_backend_failure_does_not_escape(self) -> None:
        notifications = import_notifications_with_fake_gio()
        service = notifications.NotificationService(FailingApplication())

        with self.assertLogs(notifications.LOGGER, level="ERROR"):
            service.send_finished(TimerMode.SHORT_BREAK, Language.ENGLISH)
            service.withdraw_finished()


if __name__ == "__main__":
    unittest.main()
