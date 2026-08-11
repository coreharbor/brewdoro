from __future__ import annotations

import importlib
import sys
import types
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock


class FakeMediaFile:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.volume = 0.0
        self.play_count = 0
        self.paused = False
        self.cleared = False

    @classmethod
    def new_for_filename(cls, filename: str) -> FakeMediaFile:
        return cls(filename)

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self) -> None:
        self.play_count += 1

    def pause(self) -> None:
        self.paused = True

    def clear(self) -> None:
        self.cleared = True


def import_sounds_with_fake_gtk() -> types.ModuleType:
    gi = types.ModuleType("gi")
    gi.require_version = lambda *_args: None

    repository = types.ModuleType("gi.repository")
    repository.Gtk = types.SimpleNamespace(MediaFile=FakeMediaFile)
    gi.repository = repository

    with mock.patch.dict(
        sys.modules,
        {"gi": gi, "gi.repository": repository},
    ):
        sys.modules.pop("brewdoro.sounds", None)
        return importlib.import_module("brewdoro.sounds")


class SoundServiceTests(unittest.TestCase):
    def test_uses_filename_instead_of_crash_prone_input_stream(self) -> None:
        sounds = import_sounds_with_fake_gtk()
        sound_resource = mock.Mock()
        sound_resource.joinpath.return_value = mock.sentinel.sound_file
        sound_path = Path("/opt/brewdoro/finished.wav")

        with (
            mock.patch.object(sounds.resources, "files", return_value=sound_resource),
            mock.patch.object(
                sounds.resources,
                "as_file",
                return_value=nullcontext(sound_path),
            ),
        ):
            service = sounds.SoundService()
            service.play_finished()
            service.play_finished()

        self.assertEqual(service._player.filename, str(sound_path))
        self.assertEqual(service._player.play_count, 2)
        self.assertEqual(service._player.volume, sounds.FINISHED_VOLUME)

    def test_closes_player_before_releasing_sound_file(self) -> None:
        sounds = import_sounds_with_fake_gtk()
        sound_resource = mock.Mock()
        sound_resource.joinpath.return_value = mock.sentinel.sound_file
        sound_path = Path("/opt/brewdoro/finished.wav")

        with (
            mock.patch.object(sounds.resources, "files", return_value=sound_resource),
            mock.patch.object(
                sounds.resources,
                "as_file",
                return_value=nullcontext(sound_path),
            ),
        ):
            service = sounds.SoundService()
            service.play_finished()
            player = service._player
            service.close()

        self.assertTrue(player.paused)
        self.assertTrue(player.cleared)
        self.assertIsNone(service._player)
        self.assertIsNone(service._sound_path)


if __name__ == "__main__":
    unittest.main()
