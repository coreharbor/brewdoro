from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brewdoro.i18n import (
    Language,
    LanguageStore,
    detect_system_language,
    strings_for,
)
from brewdoro.models import TimerMode, TimerState


class TranslationTests(unittest.TestCase):
    def test_every_language_translates_each_timer_state(self) -> None:
        for language in Language:
            strings = strings_for(language)
            with self.subTest(language=language):
                for mode in TimerMode:
                    self.assertTrue(strings.mode_label(mode))
                for state in TimerState:
                    self.assertTrue(strings.primary_button_label(state))
                self.assertTrue(strings.preset_label(25))
                self.assertTrue(strings.reset_session)
                self.assertTrue(strings.settings)
                self.assertTrue(strings.sound)
                self.assertIn("2", strings.cycle_progress.format(position=2))

    def test_chinese_uses_simplified_labels(self) -> None:
        strings = strings_for(Language.CHINESE)

        self.assertEqual(strings.mode_label(TimerMode.FOCUS), "专注")
        self.assertEqual(strings.primary_button_label(TimerState.IDLE), "开始")
        self.assertEqual(strings.preset_label(25), "25 分钟")

    def test_finished_notification_matches_selected_language(self) -> None:
        strings = strings_for(Language.ENGLISH)

        self.assertEqual(
            strings.finished_notification(TimerMode.FOCUS),
            ("Focus complete", "Time for a short break."),
        )
        self.assertEqual(
            strings.finished_notification(TimerMode.SHORT_BREAK),
            ("Break complete", "Time to get back to work."),
        )

    def test_detects_supported_system_languages(self) -> None:
        self.assertEqual(detect_system_language("ru_RU.UTF-8"), Language.RUSSIAN)
        self.assertEqual(detect_system_language("zh_CN.UTF-8"), Language.CHINESE)
        self.assertEqual(detect_system_language("en_US.UTF-8"), Language.ENGLISH)
        self.assertEqual(detect_system_language("de_DE.UTF-8"), Language.ENGLISH)


class LanguageStoreTests(unittest.TestCase):
    def test_saves_and_loads_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LanguageStore(Path(directory) / "language")

            self.assertTrue(store.save(Language.CHINESE))
            self.assertEqual(store.load(), Language.CHINESE)

    def test_invalid_saved_language_falls_back_to_system_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "language"
            path.write_text("klingon", encoding="utf-8")

            self.assertIn(LanguageStore(path).load(), set(Language))


if __name__ == "__main__":
    unittest.main()
