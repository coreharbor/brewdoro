from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brewdoro.models import TimerMode
from brewdoro.settings import AppSettings, SettingsStore


class SettingsStoreTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            settings = AppSettings(
                focus_minutes=40,
                short_break_minutes=8,
                long_break_minutes=20,
                sound_enabled=False,
                cycle_enabled=True,
                auto_start_enabled=True,
            )

            self.assertTrue(store.save(settings))
            self.assertEqual(store.load(), settings)
            self.assertEqual(settings.durations.minutes_for(TimerMode.FOCUS), 40)

    def test_invalid_values_fall_back_individually(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                '{"focus_minutes": 0, "short_break_minutes": 9, '
                '"long_break_minutes": true, "sound_enabled": "yes", '
                '"cycle_enabled": true}',
                encoding="utf-8",
            )

            settings = SettingsStore(path).load()

        self.assertEqual(settings.focus_minutes, 25)
        self.assertEqual(settings.short_break_minutes, 9)
        self.assertEqual(settings.long_break_minutes, 15)
        self.assertTrue(settings.sound_enabled)
        self.assertTrue(settings.cycle_enabled)

    def test_broken_json_uses_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("broken", encoding="utf-8")

            self.assertEqual(SettingsStore(path).load(), AppSettings())
