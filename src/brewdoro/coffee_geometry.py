from __future__ import annotations

from typing import Protocol


class PathContext(Protocol):
    def new_sub_path(self) -> None: ...

    def move_to(self, x: float, y: float) -> None: ...

    def line_to(self, x: float, y: float) -> None: ...

    def curve_to(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
    ) -> None: ...

    def close_path(self) -> None: ...


def draw_liquid_path(
    context: PathContext,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    """Build a liquid shape with softly rounded corners."""
    top_radius = min(6.0, height / 2.0)
    bottom_radius = min(10.0, height / 2.0)
    right = x + width
    bottom = y + height

    context.new_sub_path()
    context.move_to(x + top_radius, y)
    context.line_to(right - top_radius, y)
    context.curve_to(right, y, right, y, right, y + top_radius)
    context.line_to(right, bottom - bottom_radius)
    context.curve_to(
        right,
        bottom,
        right - bottom_radius,
        bottom,
        right - bottom_radius,
        bottom,
    )
    context.line_to(x + bottom_radius, bottom)
    context.curve_to(
        x + bottom_radius,
        bottom,
        x,
        bottom,
        x,
        bottom - bottom_radius,
    )
    context.line_to(x, y + top_radius)
    context.curve_to(x, y, x, y, x + top_radius, y)
    context.close_path()
