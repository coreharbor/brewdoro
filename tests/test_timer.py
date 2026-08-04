from __future__ import annotations

import unittest

from brewdoro.models import TimerMode, TimerState
from brewdoro.timer import BrewdoroTimer


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class BrewdoroTimerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.timer = BrewdoroTimer(clock=self.clock)

    def test_default_state(self) -> None:
        self.assertEqual(self.timer.mode, TimerMode.FOCUS)
        self.assertEqual(self.timer.state, TimerState.IDLE)
        self.assertEqual(self.timer.remaining_seconds, 25 * 60)
        self.assertEqual(self.timer.liquid_level, 1.0)

    def test_tick_uses_deadline_instead_of_counting_callbacks(self) -> None:
        self.timer.start()
        self.clock.advance(12.75)

        self.assertFalse(self.timer.tick())
        self.assertAlmostEqual(self.timer.remaining_seconds, 1487.25)

    def test_pause_freezes_time_and_resume_has_no_jump(self) -> None:
        self.timer.start()
        self.clock.advance(10.25)
        self.assertFalse(self.timer.pause())
        paused_remaining = self.timer.remaining_seconds

        self.clock.advance(120)
        self.assertEqual(self.timer.remaining_seconds, paused_remaining)

        self.timer.start()
        self.clock.advance(1.5)
        self.timer.tick()
        self.assertAlmostEqual(
            self.timer.remaining_seconds,
            paused_remaining - 1.5,
        )

    def test_late_pause_finishes_timer(self) -> None:
        self.timer.start()
        self.clock.advance(self.timer.total_seconds + 0.1)

        self.assertTrue(self.timer.pause())
        self.assertEqual(self.timer.state, TimerState.FINISHED)
        self.assertEqual(self.timer.remaining_seconds, 0.0)

    def test_reset_restores_selected_mode(self) -> None:
        self.timer.select_mode(TimerMode.LONG_BREAK)
        self.timer.start()
        self.clock.advance(42)
        self.timer.tick()

        self.timer.reset()

        self.assertEqual(self.timer.state, TimerState.IDLE)
        self.assertEqual(self.timer.remaining_seconds, 15 * 60)
        self.assertEqual(self.timer.liquid_level, 0.0)

    def test_mode_cannot_change_during_active_session(self) -> None:
        self.timer.start()
        self.assertFalse(self.timer.select_mode(TimerMode.SHORT_BREAK))
        self.assertEqual(self.timer.mode, TimerMode.FOCUS)

        self.timer.pause()
        self.assertFalse(self.timer.select_mode(TimerMode.SHORT_BREAK))
        self.assertEqual(self.timer.mode, TimerMode.FOCUS)

    def test_break_liquid_fills_as_time_elapses(self) -> None:
        self.timer.select_mode(TimerMode.SHORT_BREAK)
        self.assertEqual(self.timer.liquid_level, 0.0)

        self.timer.start()
        self.clock.advance(150)
        self.timer.tick()
        self.assertAlmostEqual(self.timer.liquid_level, 0.5)

        self.clock.advance(150)
        self.assertTrue(self.timer.tick())
        self.assertEqual(self.timer.liquid_level, 1.0)

    def test_finished_timer_can_start_again(self) -> None:
        self.timer.start()
        self.clock.advance(self.timer.total_seconds)
        self.assertTrue(self.timer.tick())

        self.assertTrue(self.timer.start())
        self.assertEqual(self.timer.state, TimerState.RUNNING)
        self.assertEqual(self.timer.remaining_seconds, self.timer.total_seconds)


if __name__ == "__main__":
    unittest.main()
