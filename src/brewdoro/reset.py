from __future__ import annotations

from enum import Enum, auto


class ResetTarget(Enum):
    TIMER = auto()
    SESSION = auto()


class ResetSequence:
    """Turn two consecutive reset presses into a deliberate session reset."""

    def __init__(self) -> None:
        self._session_pending = False

    @property
    def session_pending(self) -> bool:
        return self._session_pending

    def press(self, session_can_reset: bool) -> ResetTarget:
        if self._session_pending and session_can_reset:
            self._session_pending = False
            return ResetTarget.SESSION

        self._session_pending = session_can_reset
        return ResetTarget.TIMER

    def cancel(self) -> None:
        self._session_pending = False
