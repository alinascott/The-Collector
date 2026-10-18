#!/usr/bin/env python3
"""Draw Saddle Blanket 1633-76 as clean geometry (SVG) for the entrance table.

"Sunday" style, 1950–1960, measured from the documentation photograph (DASe 12-00496):
a heathered orange-and-black band with four square-spiral (meander) units in cream around
a small striped centre mark; a red field with fine cream warp lines; a darker red band;
and a heathered band split by a cream stripe. The drawing tiles edge to edge, so the corner
tassels are left off.
"""
from pathlib import Path

W, H = 1340, 1030
RED, MAROON, CREAM, GREY, DARK, ORANGE, RUST = "#b9442b", "#8c3328", "#ece0cc", "#c9c0ae", "#2b2116", "#d0691f", "#7a4a1e"

def band(y0, y1, fill):
    return f'<rect x="0" y="{y0*H:.1f}" width="{W}" height="{(y1-y0)*H:.1f}" fill="{fill}"/>'

def spiral(x0, y0, w, h, t, mirror=False):
    """Square spiral (meander) drawn as one stroked path, outside in."""
    pts, d = [], t * 2.0
    x1, y1 = x0 + w, y0 + h
    pts.append((x0, y1)); pts.append((x0, y0))
    k = 0
    while True:
        a, b = x0 + k * d, y0 + k * d
        c, e = x1 - k * d, y1 - k * d
        if c - a < 2 * d or e - b < 2 * d: break
        pts += [(c, b), (c, e), (a + d, e), (a + d, b + d)]
        k += 1
    if mirror:
        cx = x0 + w / 2; pts = [(2 * cx - x, y) for x, y in pts]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{ORANGE}"/>'
            f'<path d="{path}" fill="none" stroke="{CREAM}" stroke-width="{t:.1f}" stroke-linejoin="miter" stroke-linecap="square"/>')

def build():
    defs = f"""<defs>
<pattern id="warp" width="5" height="10" patternUnits="userSpaceOnUse"><rect width="5" height="10" fill="{RED}"/><rect x="3.4" width="1.3" height="10" fill="{CREAM}" opacity=".55"/></pattern>
<pattern id="warpdark" width="5" height="10" patternUnits="userSpaceOnUse"><rect width="5" height="10" fill="{MAROON}"/><rect x="3.4" width="1.3" height="10" fill="{CREAM}" opacity=".45"/></pattern>
<pattern id="heather" width="6" height="8" patternUnits="userSpaceOnUse"><rect width="6" height="8" fill="{RUST}"/><rect x="0" width="2.2" height="8" fill="{DARK}"/><rect x="3.2" width="1.6" height="8" fill="{ORANGE}"/></pattern>
</defs>"""
    els = []
    # top band with meanders, 0 – 0.19
    els.append(f'<rect x="0" y="0" width="{W}" height="{0.19*H:.1f}" fill="url(#heather)"/>')
    els.append(band(0, 0.008, DARK)); els.append(band(0.182, 0.19, DARK))
    uw, uh, gap = 0.18 * W, 0.125 * H, 0.04 * W
    y = 0.032 * H
    xs = [0.035 * W, 0.035 * W + uw + gap]
    xs += [W - x - uw for x in xs][::-1]
    for n, x in enumerate(xs):
        els.append(spiral(x, y, uw, uh, 0.0125 * H, mirror=(n % 2 == 1)))
    # small striped centre mark
    cx = W / 2
    for i in range(5):
        els.append(f'<rect x="{cx - 22 + i*9:.1f}" y="{y:.1f}" width="5" height="{uh:.1f}" fill="{CREAM if i % 2 == 0 else DARK}"/>')
    # red field, darker band
    els.append(f'<rect x="0" y="{0.19*H:.1f}" width="{W}" height="{0.49*H:.1f}" fill="url(#warp)"/>')
    els.append(f'<rect x="0" y="{0.68*H:.1f}" width="{W}" height="{0.09*H:.1f}" fill="url(#warpdark)"/>')
    # bottom band split by a cream stripe
    els.append(f'<rect x="0" y="{0.77*H:.1f}" width="{W}" height="{0.23*H:.1f}" fill="url(#heather)"/>')
    els.append(band(0.77, 0.776, DARK))
    els.append(band(0.875, 0.915, GREY)); els.append(band(0.875, 0.879, CREAM)); els.append(band(0.911, 0.915, CREAM))
    els.append(band(0.992, 1.0, DARK))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">\n'
            f'<title>Saddle Blanket 1633-76, redrawn</title>\n{defs}\n' + "\n".join(els) + "\n</svg>\n")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets/table-saddle-blanket-1633-76.svg"
    out.write_text(build(), encoding="utf-8")
    print("wrote", out, out.stat().st_size, "bytes")
