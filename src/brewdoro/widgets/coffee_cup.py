from __future__ import annotations

import math

import cairo
import gi

gi.require_version("Gtk", "4.0")
gi.require_foreign("cairo")

from gi.repository import Gtk  # noqa: E402


class CoffeeCup(Gtk.DrawingArea):
    """Minimal Cairo-rendered cup whose liquid level represents progress."""

    def __init__(self) -> None:
        super().__init__()
        self._liquid_level = 1.0
        self.set_content_width(136)
        self.set_content_height(86)
        self.set_halign(Gtk.Align.CENTER)
        self.set_draw_func(self._draw)
        self.add_css_class("coffee-cup")

    def set_liquid_level(self, level: float) -> None:
        normalized_level = min(1.0, max(0.0, level))
        if math.isclose(normalized_level, self._liquid_level, abs_tol=0.0001):
            return
        self._liquid_level = normalized_level
        self.queue_draw()

    def get_liquid_level(self) -> float:
        return self._liquid_level

    def _draw(
        self,
        _area: Gtk.DrawingArea,
        context: cairo.Context,
        width: int,
        height: int,
    ) -> None:
        scale = min(width / 136.0, height / 86.0)
        context.save()
        context.translate((width - 136.0 * scale) / 2.0, (height - 86.0 * scale) / 2.0)
        context.scale(scale, scale)
        context.set_line_cap(cairo.LineCap.ROUND)
        context.set_line_join(cairo.LineJoin.ROUND)

        cup_x, cup_y = 10.0, 8.0
        cup_width, cup_height = 96.0, 68.0
        self._cup_body_path(context, cup_x, cup_y, cup_width, cup_height)
        context.save()
        context.clip()

        inner_top = cup_y + 4.0
        inner_bottom = cup_y + cup_height - 4.0
        liquid_height = (inner_bottom - inner_top) * self._liquid_level
        if liquid_height > 0:
            liquid_top = inner_bottom - liquid_height
            liquid_x = cup_x + 4.0
            liquid_width = cup_width - 8.0
            top_radius = min(6.0, liquid_height / 2.0)
            self._liquid_path(
                context,
                liquid_x,
                liquid_top,
                liquid_width,
                liquid_height,
            )
            context.set_source_rgba(0.878, 0.686, 0.408, 1.0)
            context.fill()

            if self._liquid_level < 0.995:
                context.move_to(liquid_x + top_radius, liquid_top)
                context.line_to(liquid_x + liquid_width - top_radius, liquid_top)
                context.set_source_rgba(0.941, 0.788, 0.471, 1.0)
                context.set_line_width(1.5)
                context.stroke()
        context.restore()

        foreground = self.get_color()
        context.set_source_rgba(
            foreground.red,
            foreground.green,
            foreground.blue,
            1.0,
        )
        context.set_line_width(2.5)
        self._cup_body_path(context, cup_x, cup_y, cup_width, cup_height)
        context.stroke()

        context.move_to(cup_x + cup_width, cup_y + 18.0)
        context.curve_to(
            132.0, cup_y + 16.0, 132.0, cup_y + 54.0, cup_x + cup_width, cup_y + 52.0
        )
        context.set_line_width(3.0)
        context.stroke()
        context.restore()

    @staticmethod
    def _liquid_path(
        context: cairo.Context,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
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

    @staticmethod
    def _cup_body_path(
        context: cairo.Context,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        corner = 13.0
        context.new_sub_path()
        context.move_to(x + 5.0, y)
        context.line_to(x + width - 5.0, y)
        context.curve_to(x + width - 2.0, y, x + width, y + 2.0, x + width, y + 6.0)
        context.line_to(x + width, y + height - corner)
        context.curve_to(
            x + width,
            y + height - 4.0,
            x + width - 7.0,
            y + height,
            x + width - corner,
            y + height,
        )
        context.line_to(x + corner, y + height)
        context.curve_to(
            x + 7.0,
            y + height,
            x,
            y + height - 4.0,
            x,
            y + height - corner,
        )
        context.line_to(x, y + 6.0)
        context.curve_to(x, y + 2.0, x + 2.0, y, x + 5.0, y)
        context.close_path()
