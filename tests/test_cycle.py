from __future__ import annotations

import unittest

from brewdoro.cycle import PomodoroCycle
from brewdoro.models import TimerMode


class PomodoroCycleTests(unittest.TestCase):
    def test_uses_short_breaks_before_fourth_focus_session(self) -> None:
        cycle = PomodoroCycle()

        for completed in range(1, 4):
            self.assertEqual(cycle.complete(TimerMode.FOCUS), TimerMode.SHORT_BREAK)
            self.assertEqual(cycle.completed_focus_sessions, completed)
            self.assertEqual(cycle.complete(TimerMode.SHORT_BREAK), TimerMode.FOCUS)

    def test_uses_long_break_after_fourth_focus_session_and_resets(self) -> None:
        cycle = PomodoroCycle(completed_focus_sessions=3)

        self.assertEqual(cycle.complete(TimerMode.FOCUS), TimerMode.LONG_BREAK)
        self.assertEqual(cycle.position_for(TimerMode.LONG_BREAK), 4)
        self.assertEqual(cycle.complete(TimerMode.LONG_BREAK), TimerMode.FOCUS)
        self.assertEqual(cycle.completed_focus_sessions, 0)
        self.assertEqual(cycle.position_for(TimerMode.FOCUS), 1)

    def test_invalid_saved_progress_is_clamped(self) -> None:
        self.assertEqual(PomodoroCycle(-4).completed_focus_sessions, 0)
        self.assertEqual(PomodoroCycle(99).completed_focus_sessions, 4)
