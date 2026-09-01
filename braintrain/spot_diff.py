"""まちがいさがし(間違い探し): 上下2つの絵を見比べて、ちがう部分を見つける教材。"""

import math
import random

from .pdf_common import BrainTrainPDF
from .shapes import COLOR_NAMES, COLORS, SHAPE_KINDS, draw_shape, mark_circle

DIFFICULTY_SETTINGS = {
    "やさしい": {"n": 9, "k": 3},
    "ふつう": {"n": 13, "k": 5},
    "むずかしい": {"n": 17, "k": 7},
}


def _scatter_positions(n, w, h, rng):
    cols = max(1, math.ceil(math.sqrt(n * w / h)))
    rows = max(1, math.ceil(n / cols))
    cell_w = w / cols
    cell_h = h / rows
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    rng.shuffle(cells)
    chosen = cells[:n]
    positions = []
    jitter_x = max(0.0, cell_w * 0.28)
    jitter_y = max(0.0, cell_h * 0.28)
    for c, r in chosen:
        cx = cell_w * (c + 0.5) + rng.uniform(-jitter_x, jitter_x)
        cy = cell_h * (r + 0.5) + rng.uniform(-jitter_y, jitter_y)
        positions.append((cx, cy))
    return positions, min(cell_w, cell_h)


def generate_spot_diff(difficulty, panel_w, panel_h, rng=None):
    rng = rng or random.Random()
    settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["ふつう"])
    n, k = settings["n"], settings["k"]
    positions, cell_min = _scatter_positions(n, panel_w, panel_h, rng)
    base_size = max(9.0, min(16.0, cell_min * 0.55))

    elements = []
    for pos in positions:
        kind = rng.choice(SHAPE_KINDS)
        color_name = rng.choice(COLOR_NAMES)
        elements.append(
            {
                "kind": kind,
                "color": COLORS[color_name],
                "color_name": color_name,
                "size": base_size,
                "pos": pos,
                "diff": None,
            }
        )

    diff_indices = rng.sample(range(n), k)
    for idx in diff_indices:
        el = elements[idx]
        mode = rng.choice(["color", "size", "remove"])
        if mode == "color":
            other_name = rng.choice([c for c in COLOR_NAMES if c != el["color_name"]])
            el["diff"] = ("color", COLORS[other_name])
        elif mode == "size":
            factor = rng.choice([0.6, 1.5])
            el["diff"] = ("size", el["size"] * factor)
        else:
            el["diff"] = ("remove", None)

    return {"elements": elements, "diff_indices": set(diff_indices), "n": n, "k": k}


def _draw_panel(pdf, data, ox, oy, w, h, variant, show_answer):
    pdf.draw_frame(ox, oy, w, h)
    for idx, el in enumerate(data["elements"]):
        cx = ox + el["pos"][0]
        cy = oy + el["pos"][1]
        kind, color, size = el["kind"], el["color"], el["size"]
        is_diff = idx in data["diff_indices"]

        if variant == "B" and is_diff:
            dtype, dval = el["diff"]
            if dtype == "remove":
                if show_answer:
                    mark_circle(pdf, cx, cy, size)
                continue
            if dtype == "color":
                color = dval
            elif dtype == "size":
                size = dval

        draw_shape(pdf, kind, cx, cy, size, color)

        if variant == "B" and is_diff and show_answer:
            mark_circle(pdf, cx, cy, max(size, el["size"]))


def render_spot_diff_pdf(pdf: BrainTrainPDF, difficulty, rng=None, include_answer=True):
    rng = rng or random.Random()

    x, y, w, h = pdf.start_worksheet_page("まちがいさがし", "上と下の絵を見くらべて、ちがうところをさがしてね")
    data = generate_spot_diff(difficulty, w, (h - 14) / 2, rng)

    panel_h = (h - 14) / 2
    pdf.set_font("NotoJP", "B", 12)
    pdf.set_xy(x, y)
    pdf.cell(30, 7, "うえの絵")
    _draw_panel(pdf, data, x, y + 8, w, panel_h, "A", show_answer=False)

    y2 = y + 8 + panel_h + 10
    pdf.set_xy(x, y2 - 8)
    pdf.cell(30, 7, "したの絵")
    _draw_panel(pdf, data, x, y2, w, panel_h, "B", show_answer=False)

    pdf.set_font("NotoJP", "", 11)
    pdf.set_xy(x, y2 + panel_h + 2)
    pdf.cell(w, 6, f"ちがいは ぜんぶで {data['k']}こ あります", align="C")

    if include_answer:
        x, y, w, h = pdf.start_worksheet_page(
            "まちがいさがし", show_name_date=False, answer_page=True
        )
        panel_h = (h - 14) / 2
        pdf.set_font("NotoJP", "B", 12)
        pdf.set_xy(x, y)
        pdf.cell(30, 7, "うえの絵")
        _draw_panel(pdf, data, x, y + 8, w, panel_h, "A", show_answer=False)

        y2 = y + 8 + panel_h + 10
        pdf.set_xy(x, y2 - 8)
        pdf.cell(30, 7, "したの絵(こたえ)")
        _draw_panel(pdf, data, x, y2, w, panel_h, "B", show_answer=True)
