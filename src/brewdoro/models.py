from __future__ import annotations

from enum import Enum, auto
from typing import Final


class TimerMode(Enum):
    FOCUS = (25, "ФОКУС")
    SHORT_BREAK = (5, "КОРОТКИЙ ПЕРЕРЫВ")
    LONG_BREAK = (15, "ДЛИННЫЙ ПЕРЕРЫВ")

    @property
    def minutes(self) -> int:
        return self.value[0]

    @property
    def seconds(self) -> int:
        return self.minutes * 60

    @property
    def label(self) -> str:
        return self.value[1]

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
