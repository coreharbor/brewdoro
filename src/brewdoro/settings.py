from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from brewdoro.models import TimerDurations


MIN_MINUTES = 1
MAX_MINUTES = 120


@dataclass(frozen=True)
class AppSettings:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    sound_enabled: bool = True
    cycle_enabled: bool = False
    auto_start_enabled: bool = False

    @property
    def durations(self) -> TimerDurations:
        return TimerDurations(
            focus_minutes=self.focus_minutes,
            short_break_minutes=self.short_break_minutes,
            long_break_minutes=self.long_break_minutes,
        )


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self._default_path()

    @staticmethod
    def _default_path() -> Path:
        config_home = os.environ.get("XDG_CONFIG_HOME")
        base = Path(config_home) if config_home else Path.home() / ".config"
        return base / "brewdoro" / "settings.json"

    def load(self) -> AppSettings:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return AppSettings()
            return AppSettings(
                focus_minutes=_minutes(raw.get("focus_minutes"), 25),
                short_break_minutes=_minutes(raw.get("short_break_minutes"), 5),
                long_break_minutes=_minutes(raw.get("long_break_minutes"), 15),
                sound_enabled=_boolean(raw.get("sound_enabled"), True),
                cycle_enabled=_boolean(raw.get("cycle_enabled"), False),
                auto_start_enabled=_boolean(
                    raw.get("auto_start_enabled"),
                    False,
                ),
            )
        except (OSError, json.JSONDecodeError):
            return AppSettings()

    def save(self, settings: AppSettings) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.path.with_suffix(".tmp")
            temporary_path.write_text(
                json.dumps(asdict(settings), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.path)
        except OSError:
            return False
        return True


def _minutes(value: object, default: int) -> int:
    if type(value) is not int or not MIN_MINUTES <= value <= MAX_MINUTES:
        return default
    return value


def _boolean(value: object, default: bool) -> bool:
    return value if type(value) is bool else default
