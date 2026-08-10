from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest import mock


class FakeBytes:
    @staticmethod
    def new(data: bytes) -> bytes:
        return data


class FakeMemoryInputStream:
    def __init__(self, data: bytes) -> None:
        self.data = data

    @classmethod
    def new_from_bytes(cls, data: bytes) -> FakeMemoryInputStream:
        return cls(data)


class FakeMediaFile:
    def __init__(self, stream: FakeMemoryInputStream) -> None:
        self.stream = stream
        self.volume = 0.0
        self.played = False

    @classmethod
    def new_for_input_stream(cls, stream: FakeMemoryInputStream) -> FakeMediaFile:
        return cls(stream)

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self) -> None:
        self.played = True


def import_sounds_with_fake_gtk() -> types.ModuleType:
    gi = types.ModuleType("gi")
    gi.require_version = lambda *_args: None

    repository = types.ModuleType("gi.repository")
    repository.Gio = types.SimpleNamespace(MemoryInputStream=FakeMemoryInputStream)
    repository.GLib = types.SimpleNamespace(Bytes=FakeBytes)
    repository.Gtk = types.SimpleNamespace(MediaFile=FakeMediaFile)
    gi.repository = repository

    with mock.patch.dict(
        sys.modules,
        {"gi": gi, "gi.repository": repository},
    ):
        sys.modules.pop("brewdoro.sounds", None)
        return importlib.import_module("brewdoro.sounds")


class SoundServiceTests(unittest.TestCase):
    def test_keeps_input_stream_alive_during_async_playback(self) -> None:
        sounds = import_sounds_with_fake_gtk()
        sound_resource = mock.Mock()
        sound_resource.joinpath.return_value.read_bytes.return_value = b"wave"

        with mock.patch.object(sounds.resources, "files", return_value=sound_resource):
            service = sounds.SoundService()
            service.play_finished()

        self.assertIs(service._player.stream, service._stream)
        self.assertEqual(service._stream.data, b"wave")
        self.assertTrue(service._player.played)


if __name__ == "__main__":
    unittest.main()
