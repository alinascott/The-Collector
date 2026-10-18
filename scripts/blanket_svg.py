#!/usr/bin/env python3
"""Draw Chief Blanket 2148-606 as clean geometry (SVG) for the entrance table.

Third Phase transitional layout, measured from the documentation photograph (DASe 12-00532):
three red bands with brown and black stripes, two cream bands with a central black stripe
flanked by brown, and a nine-spot arrangement of stepped diamonds (full diamond at the centre,
halves at the edges, quarters at the corners) outlined in yellow and black, with a small
cream-and-black diamond inside. Edges are stepped the way weft rows step, so they stay crisp
at any size.
"""
from pathlib import Path

W, H = 1340, 911
STEP = 9.11                     # one weft row = H / 100
RED, DEEP, CREAM, TAN, BROWN, BLACK, YELLOW = "#b25a3e", "#a8452f", "#e8cfae", "#d6b58f", "#5d3e2c", "#2f2d20", "#cfa54a"

def rect(y0, y1, fill):
    return f'<rect x="0" y="{y0*H:.1f}" width="{W}" height="{(y1-y0)*H:.1f}" fill="{fill}"/>'

def stripes(y0, y1, n, thick=0.022, start=BROWN):
    out, gap = [], (y1 - y0 - n * thick) / (n + 1)
    col = [start, BLACK]
    for i in range(n):
        y = y0 + gap * (i + 1) + thick * i
        out.append(rect(y, y + thick, col[i % 2]))
    return out

def stepped(cx, cy, a, b, fill):
    """Diamond with half-width a and half-height b, drawn as weft-row steps."""
    rows = max(1, round(2 * b / STEP))
    s = 2 * b / rows
    right, left = [], []
    for i in range(rows):
        y = cy - b + i * s
        yc = y + s / 2
        hw = a * (1 - abs(yc - cy) / b)
        hw = round(hw / (s * 0.75)) * (s * 0.75)
        right += [(cx + hw, y), (cx + hw, y + s)]
        left += [(cx - hw, y), (cx - hw, y + s)]
    pts = right + left[::-1]
    return f'<path d="M{" L".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" fill="{fill}"/>'

def diamond(cx, cy, a, b):
    out, d = [], a * 0.055           # ring thickness
    outer = [BLACK, YELLOW, BLACK, YELLOW, BLACK]
    for k, col in enumerate(outer):
        out.append(stepped(cx, cy, a - k * d, b - k * d * b / a, col))
    k = len(outer)
    out.append(stepped(cx, cy, a - k * d, b - k * d * b / a, RED))      # red field inside the frame
    ia, ib = a * 0.30, b * 0.30                                          # central frame
    for j, col in enumerate([BLACK, CREAM, BLACK, CREAM, DEEP]):
        out.append(stepped(cx, cy, ia - j * ia * 0.17, ib - j * ib * 0.17, col))
    return out

def build():
    els = [rect(0, 1, RED)]
    # red bands with brown/black stripes
    els += stripes(0.015, 0.150, 3)
    els += stripes(0.350, 0.570, 5)
    els += stripes(0.810, 0.985, 3, start=BLACK)
    # cream bands: central black stripe flanked by brown
    for y0, y1 in [(0.155, 0.345), (0.575, 0.805)]:
        m = (y0 + y1) / 2
        els += [rect(y0, y1, CREAM), rect(m - 0.028, m + 0.028, BLACK),
                rect(m - 0.050, m - 0.036, BROWN), rect(m + 0.036, m + 0.050, BROWN)]
    # nine-spot diamonds
    a, b = 0.175 * W, 0.205 * H
    cyc = 0.46 * H
    for cx in (0, W / 2, W):
        for cy in (0, cyc, H):
            els += diamond(cx, cy, a, b)
    body = "\n".join(els)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">\n'
            f'<title>Chief Blanket 2148-606, redrawn</title>\n'
            f'<defs><clipPath id="b"><rect width="{W}" height="{H}"/></clipPath></defs>\n'
            f'<g clip-path="url(#b)">\n{body}\n</g>\n</svg>\n')

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets/table-blanket-2148-606.svg"
    out.write_text(build(), encoding="utf-8")
    print("wrote", out, out.stat().st_size, "bytes")
