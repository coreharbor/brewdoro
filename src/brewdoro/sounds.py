from __future__ import annotations

import logging
import os
from contextlib import ExitStack
from importlib import resources
from pathlib import Path
from typing import Final

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


LOGGER = logging.getLogger(__name__)
FINISHED_SOUND: Final = "resources/finished.wav"
FINISHED_VOLUME: Final = 0.7


class SoundService:
    """Play short application sounds without external audio commands."""

    def __init__(self) -> None:
        self._player: Gtk.MediaFile | None = None
        self._resource_stack = ExitStack()
        self._sound_path: Path | None = None

    def play_finished(self) -> None:
        try:
            if self._player is None:
                sound_file = resources.files("brewdoro").joinpath(FINISHED_SOUND)
                self._sound_path = self._resource_stack.enter_context(
                    resources.as_file(sound_file),
                )
                # The GStreamer GtkMediaFile backend can abort the whole process
                # for input streams. A filename uses its supported file path.
                self._player = Gtk.MediaFile.new_for_filename(
                    os.fspath(self._sound_path),
                )
                self._player.set_volume(FINISHED_VOLUME)
            self._player.play()
        except Exception:
            LOGGER.exception("Could not play the timer completion sound")

    def close(self) -> None:
        try:
            if self._player is not None:
                self._player.pause()
                self._player.clear()
            self._resource_stack.close()
        except Exception:
            LOGGER.exception("Could not close the timer completion sound")
        finally:
            self._player = None
            self._sound_path = None
