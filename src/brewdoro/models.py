from __future__ import annotations

from enum import Enum, auto
from typing import Final


class TimerMode(Enum):
    FOCUS = 25
    SHORT_BREAK = 5
    LONG_BREAK = 15

    @property
    def minutes(self) -> int:
        return self.value

    @property
    def seconds(self) -> int:
        return self.minutes * 60

    @property
    def is_focus(self) -> bool:
        return self is TimerMode.FOCUS


class TimerState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


TIMER_MODES: Final = (
    TimerMode.FOCUS,
    TimerMode.SHORT_BREAK,
    TimerMode.LONG_BREAK,
)
