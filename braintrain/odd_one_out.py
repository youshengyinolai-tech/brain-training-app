"""なかまはずれ(仲間はずれ)さがし: たくさん並んだ同じ図形の中から
1つだけ違うものを見つける教材。"""

import random

from .pdf_common import BrainTrainPDF
from .shapes import COLOR_NAMES, COLORS, SHAPE_KINDS, draw_shape, mark_circle

DIFFICULTY_SETTINGS = {
    "やさしい": {"rows": 2, "cols": 3, "mode": "color_far"},
    "ふつう": {"rows": 3, "cols": 3, "mode": "shape"},
    "むずかしい": {"rows": 3, "cols": 4, "mode": "color_near", "size_variant": True},
}

NEAR_COLOR_PAIRS = [
    ("red", "pink"),
    ("blue", "teal"),
    ("purple", "pink"),
    ("orange", "yellow"),
    ("green", "teal"),
]

NUM_PUZZLES_PER_PAGE = 4


def _make_puzzle(settings, rng):
    rows, cols = settings["rows"], settings["cols"]
    n = rows * cols
    odd_index = rng.randrange(n)
    base_kind = rng.choice(SHAPE_KINDS)
    base_color_name = rng.choice(COLOR_NAMES)
    base_color = COLORS[base_color_name]
    base_size = 14.0

    items = [{"kind": base_kind, "color": base_color, "size": base_size} for _ in range(n)]

    mode = settings["mode"]
    if mode == "shape":
        other_kind = rng.choice([k for k in SHAPE_KINDS if k != base_kind])
        items[odd_index]["kind"] = other_kind
    elif mode == "color_far":
        other_name = rng.choice([c for c in COLOR_NAMES if c != base_color_name])
        items[odd_index]["color"] = COLORS[other_name]
    elif mode == "color_near":
        pair = rng.choice(NEAR_COLOR_PAIRS)
        if base_color_name not in pair:
            # 塗り替えてペアの一方を基準色にする
            base_color_name = pair[0]
            base_color = COLORS[base_color_name]
            for it in items:
                it["color"] = base_color
            other_name = pair[1]
        else:
            other_name = pair[1] if base_color_name == pair[0] else pair[0]
        items[odd_index]["color"] = COLORS[other_name]
        if settings.get("size_variant") and rng.random() < 0.4:
            items[odd_index]["color"] = base_color
            items[odd_index]["size"] = base_size * rng.choice([0.72, 1.3])

    rng.shuffle(items)
    # シャッフル後にoddの位置を再特定(色/形/サイズが基準と異なるものを探す)
    for idx, it in enumerate(items):
        if it["kind"] != base_kind or it["color"] != base_color or it["size"] != base_size:
            odd_index = idx
            break

    return {"rows": rows, "cols": cols, "items": items, "odd_index": odd_index}


def generate_odd_one_out_page(difficulty, rng=None):
    rng = rng or random.Random()
    settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["ふつう"])
    return [_make_puzzle(settings, rng) for _ in range(NUM_PUZZLES_PER_PAGE)]


def _draw_puzzle_box(pdf, puzzle, bx, by, bw, bh, label, show_answer):
    pdf.draw_frame(bx, by, bw, bh)
    pdf.set_font("NotoJP", "B", 12)
    pdf.set_xy(bx + 3, by + 2)
    pdf.cell(20, 8, label)

    rows, cols = puzzle["rows"], puzzle["cols"]
    pad_top = 12
    grid_w = bw - 10
    grid_h = bh - pad_top - 6
    cell_w = grid_w / cols
    cell_h = grid_h / rows
    shape_size = min(cell_w, cell_h) * 0.6

    for idx, item in enumerate(puzzle["items"]):
        r, c = divmod(idx, cols)
        cx = bx + 5 + cell_w * (c + 0.5)
        cy = by + pad_top + cell_h * (r + 0.5)
        draw_shape(pdf, item["kind"], cx, cy, shape_size, item["color"])
        if show_answer and idx == puzzle["odd_index"]:
            mark_circle(pdf, cx, cy, shape_size)


def render_odd_one_out_pdf(pdf: BrainTrainPDF, difficulty, rng=None, include_answer=True):
    rng = rng or random.Random()
    puzzles = generate_odd_one_out_page(difficulty, rng)

    x, y, w, h = pdf.start_worksheet_page("なかまはずれさがし", "1つだけちがうものに、まるをつけてね")
    box_w = (w - 8) / 2
    box_h = (h - 8) / 2
    positions = [(x, y), (x + box_w + 8, y), (x, y + box_h + 8), (x + box_w + 8, y + box_h + 8)]
    labels = ["もんだい１", "もんだい２", "もんだい３", "もんだい４"]
    for (bx, by), label, puzzle in zip(positions, labels, puzzles):
        _draw_puzzle_box(pdf, puzzle, bx, by, box_w, box_h, label, show_answer=False)

    if include_answer:
        x, y, w, h = pdf.start_worksheet_page(
            "なかまはずれさがし", show_name_date=False, answer_page=True
        )
        box_w = (w - 8) / 2
        box_h = (h - 8) / 2
        positions = [(x, y), (x + box_w + 8, y), (x, y + box_h + 8), (x + box_w + 8, y + box_h + 8)]
        for (bx, by), label, puzzle in zip(positions, labels, puzzles):
            _draw_puzzle_box(pdf, puzzle, bx, by, box_w, box_h, label, show_answer=True)
