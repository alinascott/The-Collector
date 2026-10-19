#!/usr/bin/env python3
"""The entrance page (index.html): a matte table with three stacks of prints, one for each
pathway (Provenance, Textiles, Photography). Choosing a stack spreads its prints across the
table; choosing a print opens that item's page. Built from data/collage_tiles.json
(written by build_site.py), so run this after build_site.py.

  python3 scripts/build_entrances.py            # index.html (the table)
  python3 scripts/build_entrances.py --mosaic   # also mosaic.html, the earlier mosaic draft
"""
import html, json, math, random, sys
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
E = html.escape
tiles = json.loads((REPO / "data/collage_tiles.json").read_text(encoding="utf-8"))
REPO_URL = "https://github.com/alinascott/The-Collector"
def thumb(p): return p.replace("/web/", "/thumb/")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>The Collector</title>
<meta name="description" content="Teaching With the F.A. Williams Collection. Select an image to enter the collection.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:wght@400;600&family=Young+Serif&display=swap">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/collage.css">
<link rel="stylesheet" href="assets/entrances.css">
</head>
"""
NOTE = f"""<footer class="collage-note"><p><strong>Teaching note.</strong> This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by <a href="{REPO_URL}/issues">opening an issue on GitHub</a>.</p></footer>"""
CUR = ' aria-current="page"'
def switch(cur):
    opts = [("index.html", "Drifting"), ("table.html", "Table"), ("mosaic.html", "Mosaic")]
    return ('<nav class="proto-switch" aria-label="Compare entrances (draft only)"><span>Compare</span>' +
            "".join(f'<a href="{h}"{CUR if h == cur else ""}>{l}</a>' for h, l in opts) + "</nav>")

# ======================= the table: three stacks on a matte surface =======================
PATHS = [
    ("provenance", "Provenance", "Paper records", "How the collection came apart: the Deed of Trust, the 1969 accession record, catalog cards and acquisition photographs.", "provenance/index.html"),
    ("textiles", "Textiles", "Textiles", "Diné weaving from the 1860s to the 1950s: Chief blankets, saddle blankets, a shawl, rugs and samplers.", "textiles/index.html"),
    ("photography", "Photography", "Photographs", "Williams's lantern slides and lecture ephemera from the Harry Ransom Center.", "photography/index.html"),
]
import csv
piles = {k: [] for k, *_ in PATHS}
primary = {}
for r in csv.DictReader(open(REPO / "textiles/textile_images.csv", encoding="utf-8")):
    primary.setdefault(f"textiles/items/{r['textile_id']}.html", r["image"])
seen_href = set()
for t in tiles:
    if t["kind"] == "textiles":            # one print per textile: its documentation photograph
        if t["href"] in seen_href: continue
        seen_href.add(t["href"])
        t = dict(t, image=primary.get(t["href"], t["image"]))
    piles[t["kind"]].append(t)
rng = random.Random(1898)

BOXES = {  # archival drop-front boxes: colour and proportions, after a standard document box
    "provenance":  dict(tone="grey",  w=230, h=150, d=135),
    "textiles":    dict(tone="black", w=190, h=176, d=150),
    "photography": dict(tone="grey",  w=230, h=150, d=135),
}
def stack_html(kind, name, label, desc, href):
    items, bx = piles[kind], BOXES[kind]
    peeks = "".join(f'<span class="peek" style="--i:{i}"><img src="{thumb(t["image"])}" alt="" loading="lazy" draggable="false"></span>'
                    for i, t in enumerate(items[:3]))
    folders = "".join(f'<span class="folder" style="--i:{i}"><span class="tab"></span></span>' for i in range(3))
    return (f'<button class="stack box {kind} tone-{bx["tone"]}" type="button" data-kind="{kind}" aria-controls="pile-{kind}" aria-expanded="false" '
            f'aria-label="{E(name)}: {len(items)} {E(label.lower())}" style="--w:{bx["w"]}px;--h:{bx["h"]}px;--d:{bx["d"]}px">'
            f'<span class="scene" aria-hidden="true"><span class="box3d">'
            f'<span class="face back"></span><span class="face inner-back"></span><span class="face left"></span>'
            f'<span class="face bottom"></span>{folders}{peeks}'
            f'<span class="face right"><span class="edge"></span><span class="tie"></span></span>'
            f'<span class="face front"><span class="edge l"></span><span class="edge r"></span></span>'
            f'<span class="hinge"><span class="lid out"></span><span class="lid in"></span></span>'
            f'</span></span></button>')

def pile_html(kind, name, label, desc, href):
    prints = ""
    for t in piles[kind]:
        rot = round(rng.uniform(-2.5, 2.5), 1)
        prints += (f'<a class="print {kind}" href="{t["href"]}" style="--r:{rot}deg">'
                   f'<img src="{thumb(t["image"])}" alt="{E(t["title"])}" loading="lazy" draggable="false">'
                   f'<span class="pcap">{E(t["title"])}</span></a>')
    return (f'<section class="pile {kind}" id="pile-{kind}" data-kind="{kind}" hidden aria-labelledby="pile-{kind}-h">'
            f'<header class="pile-head"><button class="back" type="button">← All three stacks</button>'
            f'<p class="eyebrow">{E(label)} · {len(piles[kind])}</p><h2 id="pile-{kind}-h">{E(name)}</h2><p class="d">{E(desc)}</p>'
            f'<a class="path-link" href="{href}">Go to the {E(name)} pathway</a></header>'
            f'<div class="prints">{prints}</div></section>')

stacks = "".join(stack_html(*p) for p in PATHS)
spreads = "".join(pile_html(*p) for p in PATHS)
table = HEAD + f"""<body class="collage-page table-page stacks-page">
<script>
/* the opening question: shown once per visit, then fades into the table */
(function () {{ var seen = false; try {{ seen = sessionStorage.getItem('collector-intro') === '1'; }} catch (e) {{}}
  if (!seen && !location.hash) document.documentElement.classList.add('intro-on'); }})();
</script>
<div class="intro" aria-live="polite"><p class="intro-q">What have you learned about Indigenous communities<span class="dots">…</span> and how?</p></div>
<div class="selvage" aria-hidden="true"></div>
<main class="matte" aria-label="Three archival boxes. Open one to see its contents">
  <div class="label-card">
    <h1>The Collector</h1>
    <p class="sub">Teaching With the F.A. Williams Collection</p>
    <p class="cue">Open a box · then choose an image</p>
  </div>
  <div class="stacks">{stacks}</div>
  <a class="table-credit" href="textiles/items/1633-76.html">The table: detail of Saddle Blanket 1633-76, “Sunday” style, 1950–1960. Photograph by Steve Bourget, Department of Art and Art History.</a>
</main>
<div class="spread" hidden>{spreads}</div>
<script>
(function () {{
  var root = document.documentElement, intro = document.querySelector('.intro');
  if (root.classList.contains('intro-on')) {{
    var done = false;
    function finish() {{
      if (done) return; done = true;
      try {{ sessionStorage.setItem('collector-intro', '1'); }} catch (e) {{}}
      root.classList.add('intro-out');
      setTimeout(function () {{ root.classList.remove('intro-on', 'intro-out'); }}, 1400);
    }}
    setTimeout(finish, 3000);
    intro.addEventListener('click', finish);
    addEventListener('keydown', function k() {{ finish(); removeEventListener('keydown', k); }});
  }}
}})();
(function () {{
  var body = document.body, spread = document.querySelector('.spread');
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches, opener = null;
  function open(kind, from, animate) {{
    var pile = document.getElementById('pile-' + kind); if (!pile) return;
    spread.querySelectorAll('.pile').forEach(function (p) {{ p.hidden = p !== pile; }});
    spread.hidden = false; spread.scrollTop = 0; body.classList.add('opened');
    document.querySelectorAll('.stack').forEach(function (s) {{ s.setAttribute('aria-expanded', s.dataset.kind === kind ? 'true' : 'false'); }});
    opener = from || document.querySelector('.stack[data-kind="' + kind + '"]');
    if (history.replaceState) history.replaceState(null, '', '#' + kind);
    pile.querySelector('h2').setAttribute('tabindex', '-1'); pile.querySelector('h2').focus({{ preventScroll: true }});
    if (!animate || still || !opener) return;
    var o = opener.querySelector('.box3d').getBoundingClientRect(), ox = o.left + o.width / 2, oy = o.top + o.height / 2;
    pile.querySelectorAll('.print').forEach(function (c, i) {{
      var r = c.getBoundingClientRect();
      c.style.transition = 'none';
      c.style.transform = 'translate(' + (ox - r.left - r.width / 2) + 'px,' + (oy - r.top - r.height / 2) + 'px) scale(.45) rotate(' + ((i % 7) - 3) * 4 + 'deg)';
      c.style.opacity = '0';
      c.getBoundingClientRect();
      c.style.transition = 'transform .55s cubic-bezier(.2,.7,.2,1) ' + Math.min(i * 22, 500) + 'ms, opacity .3s ' + Math.min(i * 22, 500) + 'ms';
      c.style.transform = ''; c.style.opacity = '';
    }});
  }}
  function close() {{
    spread.hidden = true; body.classList.remove('opened');
    document.querySelectorAll('.stack').forEach(function (s) {{ s.setAttribute('aria-expanded', 'false'); }});
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    if (opener) opener.focus();
  }}
  document.querySelectorAll('.stack').forEach(function (s) {{
    s.addEventListener('click', function () {{ open(s.dataset.kind, s, true); }});
  }});
  spread.querySelectorAll('.back').forEach(function (b) {{ b.addEventListener('click', close); }});
  addEventListener('keydown', function (e) {{ if (e.key === 'Escape' && !spread.hidden) close(); }});
  var h = location.hash.replace('#', '');
  if (h && document.getElementById('pile-' + h)) open(h, null, false);
}})();
</script>
</body>
</html>
"""
(REPO / "index.html").write_text(table, encoding="utf-8")
items = [t for k in piles for t in piles[k]]
if "--mosaic" in sys.argv:
    # ======================= mosaic of Chief Blanket 2148-606 =======================
    TARGET = REPO / "provenance/images/web/12-00532_1024.jpg"
    CROP = (55, 42, 970, 668)
    C, R = 52, 36
    tgt = Image.open(TARGET).convert("RGB").crop(CROP).resize((C, R), Image.BOX)
    def avg(p):
        im = Image.open(REPO / thumb(p)).convert("RGB").resize((1, 1), Image.BOX)
        return im.getpixel((0, 0))
    pool = [(t, avg(t["image"])) for t in tiles]
    def dist(a, b):  # weighted RGB distance
        return 2 * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + 3 * (a[2] - b[2]) ** 2
    mr = random.Random(606)
    grid, cells_html = [], []
    for r in range(R):
        row = []
        for c in range(C):
            col = tgt.getpixel((c, r))
            ranked = sorted(range(len(pool)), key=lambda i: dist(pool[i][1], col))
            avoid = {row[-1] if row else None, grid[-1][c] if grid else None, row[-2] if len(row) > 1 else None}
            choices = [i for i in ranked[:8] if i not in avoid] or ranked[:1]
            i = mr.choice(choices[:4]); row.append(i)
            t = pool[i][0]
            hexc = "#%02x%02x%02x" % col
            cells_html.append(f'<a class="m" href="{t["href"]}" style="--c:{hexc};--d:{(r + c) * 14}ms" data-k="{t["label"]}" data-t="{E(t["title"])}">'
                              f'<img src="{thumb(t["image"])}" alt="{E(t["title"])}" loading="lazy" draggable="false"></a>')
        grid.append(row)
    mosaic = HEAD + f"""<body class="collage-page mosaic-page">
    <div class="selvage" aria-hidden="true"></div>
    <main class="mosaic-wrap" aria-label="Mosaic of Chief Blanket 2148-606 made from images in the collection">
      <div class="mosaic" style="--cols:{C};--rows:{R}">{''.join(cells_html)}</div>
    </main>
    <aside class="mosaic-info" aria-live="polite">
      <h1>The Collector</h1>
      <p class="sub">Teaching With the F.A. Williams Collection</p>
      <p class="about">From a distance: <a href="textiles/items/2148-606.html">Chief Blanket 2148-606</a>, the blanket Frederic Allen Williams sat on in his 1940 studio portrait. Up close: {len(tiles)} images from the collection.</p>
      <div class="now"><span class="k">Select an image to enter</span><span class="t">&nbsp;</span><a class="open" href="#" hidden>Open</a></div>
    </aside>
    {switch("mosaic.html")}
    {NOTE}
    <script>
    (function () {{
      var m = document.querySelector('.mosaic'), info = document.querySelector('.mosaic-info .now');
      var k = info.querySelector('.k'), t = info.querySelector('.t'), open = info.querySelector('.open');
      var touch = matchMedia('(hover: none)').matches, picked = null;
      function show(a) {{ k.textContent = a.dataset.k; t.textContent = a.dataset.t; open.href = a.href; }}
      m.addEventListener('mouseover', function (e) {{ var a = e.target.closest('.m'); if (a) show(a); }});
      m.addEventListener('focusin', function (e) {{ var a = e.target.closest('.m'); if (a) show(a); }});
      if (touch) m.addEventListener('click', function (e) {{
        var a = e.target.closest('.m'); if (!a) return;
        if (picked !== a) {{ e.preventDefault(); if (picked) picked.classList.remove('picked'); picked = a; a.classList.add('picked'); show(a); open.hidden = false; }}
      }});
      requestAnimationFrame(function () {{ document.body.classList.add('woven'); }});
    }})();
    </script>
    </body>
    </html>
    """
    (REPO / "mosaic.html").write_text(mosaic, encoding="utf-8")
print("index.html (table): " + ", ".join(f"{k} {len(v)}" for k, v in piles.items()))
