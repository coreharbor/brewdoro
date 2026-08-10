from __future__ import annotations

import logging
from importlib import resources
from typing import Final

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, GLib, Gtk  # noqa: E402


LOGGER = logging.getLogger(__name__)
FINISHED_SOUND: Final = "resources/finished.wav"
FINISHED_VOLUME: Final = 0.7


class SoundService:
    """Play short application sounds without external audio commands."""

    def __init__(self) -> None:
        self._player: Gtk.MediaFile | None = None
        self._stream: Gio.MemoryInputStream | None = None

    def play_finished(self) -> None:
        try:
            sound_file = resources.files("brewdoro").joinpath(FINISHED_SOUND)
            sound_data = sound_file.read_bytes()
            stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(sound_data))
            player = Gtk.MediaFile.new_for_input_stream(stream)
            player.set_volume(FINISHED_VOLUME)
            player.play()
            # Gtk does not take ownership of the input stream. Keep it alive for
            # the asynchronous playback instead of letting Python release it
            # when this method returns.
            self._stream = stream
            self._player = player
        except Exception:
            LOGGER.exception("Could not play the timer completion sound")
