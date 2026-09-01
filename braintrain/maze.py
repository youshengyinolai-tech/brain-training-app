"""めいろ(迷路)の自動生成とPDF描画。"""

import random
from collections import deque

from .pdf_common import BrainTrainPDF

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

DIFFICULTY_ROWS = {
    "やさしい": 9,
    "ふつう": 13,
    "むずかしい": 17,
}


def _grid_size_for(rows, content_w, content_h):
    cols = max(4, round(rows * content_w / content_h))
    return rows, cols


def generate_maze(difficulty, content_w, content_h, rng=None):
    rng = rng or random.Random()
    rows = DIFFICULTY_ROWS.get(difficulty, DIFFICULTY_ROWS["ふつう"])
    rows, cols = _grid_size_for(rows, content_w, content_h)

    walls = [[{"N": True, "S": True, "E": True, "W": True} for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    start = (0, 0)
    stack = [start]
    visited[0][0] = True

    while stack:
        c, r = stack[-1]
        neighbors = []
        for d, (dc, dr) in DIRS.items():
            nc, nr = c + dc, r + dr
            if 0 <= nc < cols and 0 <= nr < rows and not visited[nr][nc]:
                neighbors.append((d, nc, nr))
        if not neighbors:
            stack.pop()
            continue
        d, nc, nr = rng.choice(neighbors)
        walls[r][c][d] = False
        walls[nr][nc][OPPOSITE[d]] = False
        visited[nr][nc] = True
        stack.append((nc, nr))

    goal = (cols - 1, rows - 1)
    path = _solve(walls, cols, rows, start, goal)

    return {"rows": rows, "cols": cols, "walls": walls, "start": start, "goal": goal, "path": path}


def _solve(walls, cols, rows, start, goal):
    q = deque([start])
    came_from = {start: None}
    while q:
        c, r = q.popleft()
        if (c, r) == goal:
            break
        for d, (dc, dr) in DIRS.items():
            if walls[r][c][d]:
                continue
            nc, nr = c + dc, r + dr
            if (nc, nr) not in came_from:
                came_from[(nc, nr)] = (c, r)
                q.append((nc, nr))
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = came_from.get(cur)
    path.reverse()
    return path


def _draw_maze_walls(pdf, maze, ox, oy, cell):
    rows, cols, walls = maze["rows"], maze["cols"], maze["walls"]
    sx, sy = maze["start"]
    gx, gy = maze["goal"]

    pdf.set_draw_color(20, 20, 20)
    pdf.set_line_width(0.8)

    for r in range(rows):
        for c in range(cols):
            w = walls[r][c]
            x0, y0 = ox + c * cell, oy + r * cell
            x1, y1 = x0 + cell, y0 + cell
            if r == 0 and w["N"] and not (c == sx and r == sy):
                pdf.line(x0, y0, x1, y0)
            elif r > 0 and w["N"]:
                pdf.line(x0, y0, x1, y0)
            if w["W"]:
                pdf.line(x0, y0, x0, y1)
            if r == rows - 1 and w["S"] and not (c == gx and r == gy):
                pdf.line(x0, y1, x1, y1)
            if c == cols - 1 and w["E"]:
                pdf.line(x1, y0, x1, y1)

    pdf.set_font("NotoJP", "B", 10)
    sx0, sy0 = ox + sx * cell, oy + sy * cell
    pdf.set_xy(sx0, sy0 - 7)
    pdf.cell(cell, 6, "スタート", align="C")
    gx0, gy0 = ox + gx * cell, oy + gy * cell
    pdf.set_xy(gx0, gy0 + cell + 1)
    pdf.cell(cell, 6, "ゴール", align="C")


def render_maze_pdf(pdf: BrainTrainPDF, difficulty, rng=None, include_answer=True):
    x, y, w, h = pdf.start_worksheet_page("めいろ", "スタートからゴールまで、せんをひいてね")
    usable_h = h - 8
    maze = generate_maze(difficulty, w, usable_h, rng=rng)
    cell = min(w / maze["cols"], usable_h / maze["rows"])
    grid_w = cell * maze["cols"]
    grid_h = cell * maze["rows"]
    ox = x + (w - grid_w) / 2
    oy = y + (h - grid_h) / 2
    _draw_maze_walls(pdf, maze, ox, oy, cell)

    if include_answer:
        x, y, w, h = pdf.start_worksheet_page("めいろ", show_name_date=False, answer_page=True)
        usable_h = h - 8
        cell2 = min(w / maze["cols"], usable_h / maze["rows"])
        grid_w2 = cell2 * maze["cols"]
        grid_h2 = cell2 * maze["rows"]
        ox2 = x + (w - grid_w2) / 2
        oy2 = y + (h - grid_h2) / 2
        _draw_maze_walls(pdf, maze, ox2, oy2, cell2)
        pdf.set_draw_color(220, 60, 60)
        pdf.set_line_width(1.6)
        points = [(ox2 + (c + 0.5) * cell2, oy2 + (r + 0.5) * cell2) for c, r in maze["path"]]
        pdf.polyline(points)
