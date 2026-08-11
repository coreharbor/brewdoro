from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brewdoro.models import TimerMode, TimerState
from brewdoro.session import SavedSession, SessionStore
from brewdoro.timer import TimerSnapshot


class SessionStoreTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = SessionStore(Path(directory) / "session.json")
            session = SavedSession(
                timer=TimerSnapshot(
                    mode=TimerMode.FOCUS,
                    state=TimerState.RUNNING,
                    remaining_seconds=1_200.5,
                    deadline=50_000.0,
                ),
                completed_focus_sessions=2,
            )

            self.assertTrue(store.save(session))
            self.assertEqual(store.load(), session)

    def test_invalid_session_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            path.write_text('{"mode": "TEAPOT"}', encoding="utf-8")

            self.assertIsNone(SessionStore(path).load())

    def test_non_finite_times_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            path.write_text(
                '{"mode": "FOCUS", "state": "RUNNING", '
                '"remaining_seconds": NaN, "deadline": 100, '
                '"completed_focus_sessions": 0}',
                encoding="utf-8",
            )

            self.assertIsNone(SessionStore(path).load())
