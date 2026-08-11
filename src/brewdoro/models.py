from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class TimerDurations:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15

    def minutes_for(self, mode: TimerMode) -> int:
        return {
            TimerMode.FOCUS: self.focus_minutes,
            TimerMode.SHORT_BREAK: self.short_break_minutes,
            TimerMode.LONG_BREAK: self.long_break_minutes,
        }[mode]

    def seconds_for(self, mode: TimerMode) -> int:
        return self.minutes_for(mode) * 60
