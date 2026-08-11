from __future__ import annotations

import locale
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from brewdoro.models import TimerMode, TimerState


class Language(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    CHINESE = "zh"

    @property
    def short_label(self) -> str:
        return {
            Language.ENGLISH: "EN",
            Language.RUSSIAN: "RU",
            Language.CHINESE: "中",
        }[self]

    @property
    def display_name(self) -> str:
        return {
            Language.ENGLISH: "English",
            Language.RUSSIAN: "Русский",
            Language.CHINESE: "中文",
        }[self]


@dataclass(frozen=True)
class Strings:
    focus: str
    short_break: str
    long_break: str
    start: str
    pause: str
    resume: str
    start_again: str
    reset: str
    minute_suffix: str
    change_language: str
    settings: str
    focus_duration: str
    short_break_duration: str
    long_break_duration: str
    sound: str
    pomodoro_cycle: str
    auto_start: str
    cycle_progress: str
    focus_finished_title: str
    focus_finished_body: str
    break_finished_title: str
    break_finished_body: str

    def mode_label(self, mode: TimerMode) -> str:
        return {
            TimerMode.FOCUS: self.focus,
            TimerMode.SHORT_BREAK: self.short_break,
            TimerMode.LONG_BREAK: self.long_break,
        }[mode]

    def primary_button_label(self, state: TimerState) -> str:
        return {
            TimerState.IDLE: self.start,
            TimerState.RUNNING: self.pause,
            TimerState.PAUSED: self.resume,
            TimerState.FINISHED: self.start_again,
        }[state]

    def preset_label(self, minutes: int) -> str:
        return f"{minutes} {self.minute_suffix}"

    def finished_notification(self, mode: TimerMode) -> tuple[str, str]:
        if mode.is_focus:
            return self.focus_finished_title, self.focus_finished_body
        return self.break_finished_title, self.break_finished_body


TRANSLATIONS: Final = {
    Language.ENGLISH: Strings(
        focus="FOCUS",
        short_break="SHORT BREAK",
        long_break="LONG BREAK",
        start="Start",
        pause="Pause",
        resume="Resume",
        start_again="Start again",
        reset="Reset",
        minute_suffix="min",
        change_language="Change language",
        settings="Settings",
        focus_duration="Focus",
        short_break_duration="Short break",
        long_break_duration="Long break",
        sound="Sound",
        pomodoro_cycle="Pomodoro cycle",
        auto_start="Auto-start next stage",
        cycle_progress="Session {position} of 4",
        focus_finished_title="Focus complete",
        focus_finished_body="Time for a short break.",
        break_finished_title="Break complete",
        break_finished_body="Time to get back to work.",
    ),
    Language.RUSSIAN: Strings(
        focus="ФОКУС",
        short_break="КОРОТКИЙ ПЕРЕРЫВ",
        long_break="ДЛИННЫЙ ПЕРЕРЫВ",
        start="Начать",
        pause="Пауза",
        resume="Продолжить",
        start_again="Начать снова",
        reset="Сбросить",
        minute_suffix="мин",
        change_language="Сменить язык",
        settings="Настройки",
        focus_duration="Фокус",
        short_break_duration="Короткий перерыв",
        long_break_duration="Длинный перерыв",
        sound="Звук",
        pomodoro_cycle="Цикл Pomodoro",
        auto_start="Автозапуск этапа",
        cycle_progress="Сессия {position} из 4",
        focus_finished_title="Фокус завершён",
        focus_finished_body="Пора немного отдохнуть.",
        break_finished_title="Перерыв завершён",
        break_finished_body="Можно возвращаться к работе.",
    ),
    Language.CHINESE: Strings(
        focus="专注",
        short_break="短休息",
        long_break="长休息",
        start="开始",
        pause="暂停",
        resume="继续",
        start_again="重新开始",
        reset="重置",
        minute_suffix="分钟",
        change_language="切换语言",
        settings="设置",
        focus_duration="专注",
        short_break_duration="短休息",
        long_break_duration="长休息",
        sound="声音",
        pomodoro_cycle="番茄循环",
        auto_start="自动开始下一阶段",
        cycle_progress="第 {position}/4 次专注",
        focus_finished_title="专注结束",
        focus_finished_body="该休息一下了。",
        break_finished_title="休息结束",
        break_finished_body="可以继续工作了。",
    ),
}


def strings_for(language: Language) -> Strings:
    return TRANSLATIONS[language]


def detect_system_language(locale_name: str | None = None) -> Language:
    if locale_name is None:
        try:
            locale_name = locale.getlocale()[0]
        except ValueError:
            locale_name = None
        locale_name = locale_name or os.environ.get("LANG", "")

    normalized = locale_name.lower().replace("_", "-")
    if normalized.startswith("ru"):
        return Language.RUSSIAN
    if normalized.startswith("zh"):
        return Language.CHINESE
    return Language.ENGLISH


class LanguageStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self._default_path()

    @staticmethod
    def _default_path() -> Path:
        config_home = os.environ.get("XDG_CONFIG_HOME")
        base = Path(config_home) if config_home else Path.home() / ".config"
        return base / "brewdoro" / "language"

    def load(self) -> Language:
        try:
            return Language(self.path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return detect_system_language()

    def save(self, language: Language) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(language.value, encoding="utf-8")
        except OSError:
            return False
        return True
