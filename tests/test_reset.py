from __future__ import annotations

import unittest

from brewdoro.reset import ResetSequence, ResetTarget


class ResetSequenceTests(unittest.TestCase):
    def test_second_press_resets_session_when_progress_exists(self) -> None:
        sequence = ResetSequence()

        self.assertEqual(sequence.press(session_can_reset=True), ResetTarget.TIMER)
        self.assertTrue(sequence.session_pending)
        self.assertEqual(sequence.press(session_can_reset=True), ResetTarget.SESSION)
        self.assertFalse(sequence.session_pending)

    def test_press_only_resets_timer_without_session_progress(self) -> None:
        sequence = ResetSequence()

        self.assertEqual(sequence.press(session_can_reset=False), ResetTarget.TIMER)
        self.assertFalse(sequence.session_pending)
        self.assertEqual(sequence.press(session_can_reset=False), ResetTarget.TIMER)

    def test_cancel_requires_a_new_first_press(self) -> None:
        sequence = ResetSequence()

        sequence.press(session_can_reset=True)
        sequence.cancel()

        self.assertEqual(sequence.press(session_can_reset=True), ResetTarget.TIMER)
        self.assertTrue(sequence.session_pending)

    def test_lost_session_progress_cancels_pending_reset(self) -> None:
        sequence = ResetSequence()

        sequence.press(session_can_reset=True)

        self.assertEqual(sequence.press(session_can_reset=False), ResetTarget.TIMER)
        self.assertFalse(sequence.session_pending)


if __name__ == "__main__":
    unittest.main()
