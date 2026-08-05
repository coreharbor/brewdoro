from __future__ import annotations

import unittest

from brewdoro.coffee_geometry import draw_liquid_path


class RecordingContext:
    def __init__(self) -> None:
        self.commands: list[tuple[str, tuple[float, ...]]] = []

    def _record(self, name: str, *values: float) -> None:
        self.commands.append((name, values))

    def new_sub_path(self) -> None:
        self._record("new_sub_path")

    def move_to(self, x: float, y: float) -> None:
        self._record("move_to", x, y)

    def line_to(self, x: float, y: float) -> None:
        self._record("line_to", x, y)

    def curve_to(self, *values: float) -> None:
        self._record("curve_to", *values)

    def close_path(self) -> None:
        self._record("close_path")


class CoffeeCupLiquidPathTests(unittest.TestCase):
    def test_liquid_surface_keeps_rounded_corners_at_different_levels(self) -> None:
        for height in (4.0, 24.0, 60.0):
            with self.subTest(height=height):
                context = RecordingContext()
                top_radius = min(6.0, height / 2.0)

                draw_liquid_path(context, 5.0, 5.0, 88.0, height)

                self.assertEqual(
                    context.commands[1],
                    ("move_to", (5.0 + top_radius, 5.0)),
                )
                self.assertEqual(
                    context.commands[2],
                    ("line_to", (93.0 - top_radius, 5.0)),
                )
                self.assertEqual(
                    context.commands[3],
                    (
                        "curve_to",
                        (93.0, 5.0, 93.0, 5.0, 93.0, 5.0 + top_radius),
                    ),
                )
                self.assertEqual(
                    context.commands[-3],
                    ("line_to", (5.0, 5.0 + top_radius)),
                )


if __name__ == "__main__":
    unittest.main()
