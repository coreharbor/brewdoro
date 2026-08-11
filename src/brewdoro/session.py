from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

from brewdoro.models import TimerMode, TimerState
from brewdoro.timer import TimerSnapshot


@dataclass(frozen=True)
class SavedSession:
    timer: TimerSnapshot
    completed_focus_sessions: int = 0


class SessionStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self._default_path()

    @staticmethod
    def _default_path() -> Path:
        state_home = os.environ.get("XDG_STATE_HOME")
        base = Path(state_home) if state_home else Path.home() / ".local" / "state"
        return base / "brewdoro" / "session.json"

    def load(self) -> SavedSession | None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return None
            deadline = raw.get("deadline")
            if deadline is not None:
                deadline = float(deadline)
            completed = raw.get("completed_focus_sessions", 0)
            if type(completed) is not int or not 0 <= completed <= 4:
                return None
            remaining_seconds = float(raw["remaining_seconds"])
            if not math.isfinite(remaining_seconds) or (
                deadline is not None and not math.isfinite(deadline)
            ):
                return None
            return SavedSession(
                timer=TimerSnapshot(
                    mode=TimerMode[str(raw["mode"])],
                    state=TimerState[str(raw["state"])],
                    remaining_seconds=max(0.0, remaining_seconds),
                    deadline=deadline,
                ),
                completed_focus_sessions=completed,
            )
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
            return None

    def save(self, session: SavedSession) -> bool:
        snapshot = session.timer
        payload = {
            "mode": snapshot.mode.name,
            "state": snapshot.state.name,
            "remaining_seconds": snapshot.remaining_seconds,
            "deadline": snapshot.deadline,
            "completed_focus_sessions": session.completed_focus_sessions,
        }
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.path.with_suffix(".tmp")
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.path)
        except OSError:
            return False
        return True
