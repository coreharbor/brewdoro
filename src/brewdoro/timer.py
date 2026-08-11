from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from brewdoro.models import TimerDurations, TimerMode, TimerState


@dataclass(frozen=True)
class TimerSnapshot:
    mode: TimerMode
    state: TimerState
    remaining_seconds: float
    deadline: float | None


class BrewdoroTimer:
    """State machine that keeps timer calculations independent from GTK."""

    def __init__(
        self,
        clock: Callable[[], float] = time.time,
        mode: TimerMode = TimerMode.FOCUS,
        durations: TimerDurations | None = None,
    ) -> None:
        self._clock = clock
        self._durations = durations or TimerDurations()
        self._mode = mode
        self._state = TimerState.IDLE
        self._remaining_seconds = float(self.total_seconds)
        self._deadline: float | None = None

    @property
    def mode(self) -> TimerMode:
        return self._mode

    @property
    def state(self) -> TimerState:
        return self._state

    @property
    def total_seconds(self) -> int:
        return self._durations.seconds_for(self._mode)

    @property
    def remaining_seconds(self) -> float:
        return self._remaining_seconds

    @property
    def has_active_session(self) -> bool:
        return self._state in (TimerState.RUNNING, TimerState.PAUSED)

    @property
    def liquid_level(self) -> float:
        remaining_ratio = min(
            1.0,
            max(0.0, self._remaining_seconds / self.total_seconds),
        )
        if self._mode.is_focus:
            return remaining_ratio
        return 1.0 - remaining_ratio

    def start(self) -> bool:
        if self._state is TimerState.RUNNING:
            return False
        if self._state is TimerState.FINISHED or self._remaining_seconds <= 0:
            self._remaining_seconds = float(self.total_seconds)
        self._deadline = self._clock() + self._remaining_seconds
        self._state = TimerState.RUNNING
        return True

    def pause(self) -> bool:
        """Pause the timer and return whether it finished at this instant."""
        if self._state is not TimerState.RUNNING:
            return False
        self._refresh_remaining()
        if self._remaining_seconds <= 0:
            self._finish()
            return True
        self._deadline = None
        self._state = TimerState.PAUSED
        return False

    def tick(self) -> bool:
        """Refresh remaining time and return True exactly when it finishes."""
        if self._state is not TimerState.RUNNING:
            return False
        self._refresh_remaining()
        if self._remaining_seconds <= 0:
            self._finish()
            return True
        return False

    def reset(self) -> None:
        self._deadline = None
        self._remaining_seconds = float(self.total_seconds)
        self._state = TimerState.IDLE

    def select_mode(self, mode: TimerMode) -> bool:
        if self.has_active_session:
            return False
        self._mode = mode
        self.reset()
        return True

    def update_durations(self, durations: TimerDurations) -> bool:
        if self.has_active_session:
            return False
        self._durations = durations
        self.reset()
        return True

    def snapshot(self) -> TimerSnapshot:
        return TimerSnapshot(
            mode=self._mode,
            state=self._state,
            remaining_seconds=self._remaining_seconds,
            deadline=self._deadline,
        )

    def restore(self, snapshot: TimerSnapshot) -> bool:
        """Restore a saved session and report if it finished while away."""
        self._mode = snapshot.mode
        self._deadline = None
        total_seconds = float(self.total_seconds)

        if snapshot.state is TimerState.RUNNING and snapshot.deadline is not None:
            self._remaining_seconds = min(
                total_seconds,
                max(0.0, snapshot.deadline - self._clock()),
            )
            if self._remaining_seconds <= 0:
                self._finish()
                return True
            self._deadline = snapshot.deadline
            self._state = TimerState.RUNNING
            return False

        if snapshot.state is TimerState.PAUSED:
            self._remaining_seconds = min(
                total_seconds,
                max(0.0, snapshot.remaining_seconds),
            )
            self._state = (
                TimerState.PAUSED
                if self._remaining_seconds > 0
                else TimerState.FINISHED
            )
            return False

        if snapshot.state is TimerState.FINISHED:
            self._remaining_seconds = 0.0
            self._state = TimerState.FINISHED
            return False

        self._remaining_seconds = total_seconds
        self._state = TimerState.IDLE
        return False

    def _refresh_remaining(self) -> None:
        if self._deadline is None:
            return
        self._remaining_seconds = max(0.0, self._deadline - self._clock())

    def _finish(self) -> None:
        self._deadline = None
        self._remaining_seconds = 0.0
        self._state = TimerState.FINISHED
