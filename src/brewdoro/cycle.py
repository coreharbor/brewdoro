from __future__ import annotations

from brewdoro.models import TimerMode


FOCUS_SESSIONS_PER_CYCLE = 4


class PomodoroCycle:
    def __init__(self, completed_focus_sessions: int = 0) -> None:
        self._completed_focus_sessions = min(
            FOCUS_SESSIONS_PER_CYCLE,
            max(0, completed_focus_sessions),
        )

    @property
    def completed_focus_sessions(self) -> int:
        return self._completed_focus_sessions

    def position_for(self, mode: TimerMode) -> int:
        if mode.is_focus:
            return min(
                FOCUS_SESSIONS_PER_CYCLE,
                self._completed_focus_sessions + 1,
            )
        return max(1, self._completed_focus_sessions)

    def complete(self, mode: TimerMode) -> TimerMode:
        if mode.is_focus:
            self._completed_focus_sessions = min(
                FOCUS_SESSIONS_PER_CYCLE,
                self._completed_focus_sessions + 1,
            )
            if self._completed_focus_sessions >= FOCUS_SESSIONS_PER_CYCLE:
                return TimerMode.LONG_BREAK
            return TimerMode.SHORT_BREAK

        if mode is TimerMode.LONG_BREAK:
            self._completed_focus_sessions = 0
        return TimerMode.FOCUS

    def reset(self) -> None:
        self._completed_focus_sessions = 0
