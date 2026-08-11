from __future__ import annotations

import unittest

from brewdoro.models import TimerDurations, TimerMode, TimerState
from brewdoro.timer import BrewdoroTimer, TimerSnapshot


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
        self.assertTrue(self.timer.is_reset)

    def test_timer_is_only_reset_when_idle_at_full_duration(self) -> None:
        self.timer.start()
        self.assertFalse(self.timer.is_reset)

        self.timer.pause()
        self.assertFalse(self.timer.is_reset)

        self.timer.reset()
        self.assertTrue(self.timer.is_reset)

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

    def test_finish_event_is_emitted_only_once(self) -> None:
        self.timer.start()
        self.clock.advance(self.timer.total_seconds)

        self.assertTrue(self.timer.tick())
        self.assertFalse(self.timer.tick())
        self.assertFalse(self.timer.pause())

    def test_custom_durations_are_used_by_every_mode(self) -> None:
        timer = BrewdoroTimer(
            clock=self.clock,
            durations=TimerDurations(40, 8, 20),
        )

        self.assertEqual(timer.total_seconds, 40 * 60)
        timer.select_mode(TimerMode.SHORT_BREAK)
        self.assertEqual(timer.total_seconds, 8 * 60)
        timer.select_mode(TimerMode.LONG_BREAK)
        self.assertEqual(timer.total_seconds, 20 * 60)

    def test_restores_running_timer_from_absolute_deadline(self) -> None:
        self.clock.now = 1_000
        snapshot = TimerSnapshot(
            mode=TimerMode.SHORT_BREAK,
            state=TimerState.RUNNING,
            remaining_seconds=240,
            deadline=1_120,
        )

        self.assertFalse(self.timer.restore(snapshot))
        self.assertEqual(self.timer.mode, TimerMode.SHORT_BREAK)
        self.assertEqual(self.timer.state, TimerState.RUNNING)
        self.assertEqual(self.timer.remaining_seconds, 120)

    def test_reports_timer_that_finished_while_application_was_closed(self) -> None:
        self.clock.now = 1_000
        snapshot = TimerSnapshot(
            mode=TimerMode.FOCUS,
            state=TimerState.RUNNING,
            remaining_seconds=10,
            deadline=990,
        )

        self.assertTrue(self.timer.restore(snapshot))
        self.assertEqual(self.timer.state, TimerState.FINISHED)
        self.assertEqual(self.timer.remaining_seconds, 0)

    def test_paused_timer_does_not_advance_while_application_is_closed(self) -> None:
        self.clock.now = 10_000
        snapshot = TimerSnapshot(
            mode=TimerMode.FOCUS,
            state=TimerState.PAUSED,
            remaining_seconds=321.5,
            deadline=None,
        )

        self.assertFalse(self.timer.restore(snapshot))
        self.assertEqual(self.timer.state, TimerState.PAUSED)
        self.assertEqual(self.timer.remaining_seconds, 321.5)

    def test_restored_idle_timer_is_reset(self) -> None:
        snapshot = TimerSnapshot(
            mode=TimerMode.SHORT_BREAK,
            state=TimerState.IDLE,
            remaining_seconds=123,
            deadline=None,
        )

        self.assertFalse(self.timer.restore(snapshot))
        self.assertTrue(self.timer.is_reset)
        self.assertEqual(self.timer.remaining_seconds, self.timer.total_seconds)


if __name__ == "__main__":
    unittest.main()
