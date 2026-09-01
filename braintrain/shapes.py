"""図形描画の共通ヘルパー。まちがいさがし・仲間はずれさがしの両方で使う。"""

import math

SHAPE_KINDS = ["circle", "square", "triangle", "star", "diamond"]

# 見分けやすい色のパレット (R,G,B)
COLORS = {
    "red": (220, 60, 55),
    "blue": (50, 110, 200),
    "green": (60, 160, 90),
    "orange": (235, 150, 40),
    "purple": (150, 90, 190),
    "yellow": (235, 200, 40),
    "pink": (230, 130, 170),
    "teal": (40, 160, 160),
}
COLOR_NAMES = list(COLORS.keys())


def draw_shape(pdf, kind, cx, cy, size, color, style="F"):
    r = size / 2
    pdf.set_fill_color(*color)
    darker = tuple(max(0, c - 60) for c in color)
    pdf.set_draw_color(*darker)
    pdf.set_line_width(0.35)

    if kind == "circle":
        pdf.circle(cx, cy, r, style=style)
    elif kind == "square":
        pdf.rect(cx - r, cy - r, size, size, style=style)
    elif kind == "triangle":
        pdf.regular_polygon(cx - r, cy + r, 3, size, rotateDegrees=-90, style=style)
    elif kind == "diamond":
        pdf.regular_polygon(cx - r, cy + r, 4, size, rotateDegrees=0, style=style)
    elif kind == "star":
        pdf.star(cx, cy, r * 0.42, r * 0.95, 5, rotate_degrees=0, style=style)
    else:
        raise ValueError(kind)


def mark_circle(pdf, cx, cy, size):
    """答え合わせ用に、対象の図形を赤丸で囲む。"""
    pdf.set_draw_color(220, 30, 30)
    pdf.set_line_width(1.1)
    r = size * 0.75
    pdf.circle(cx, cy, r, style="D")
