#!/usr/bin/env python3
"""The two other views of the entrance, and the toggle that links all three:

  index.html      Table (built by build_entrances.py; this script adds the toggle)
  pairs.html      Pairs: diptychs that cross the two archives (set aside; build with --pairs)
  filmstrip.html  Filmstrip: one horizontal strip ordered by date

  python3 scripts/build_entrance_views.py              # pairs + filmstrip + toggle
  python3 scripts/build_entrance_views.py --lightbox   # also the lightbox draft (not linked)

Run after build_site.py and build_entrances.py.
"""
import csv, html, json, re, sys
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
E = html.escape
REPO_URL = "https://github.com/alinascott/The-Collector"
tiles = json.loads((REPO / "data/collage_tiles.json").read_text(encoding="utf-8"))
def rcsv(p): return list(csv.DictReader(open(REPO / p, encoding="utf-8")))
T = {r["id"]: r for r in rcsv("textiles/textiles.csv")}
P = {r["id"]: r for r in rcsv("photography/photographs.csv")}
TI = {}
for r in rcsv("textiles/textile_images.csv"): TI.setdefault(r["textile_id"], []).append(r)
def thumb(p): return p.replace("/web/", "/thumb/")
def ar(p):
    try:
        w, h = Image.open(REPO / thumb(p)).size; return w / h
    except OSError: return 1.33

CUR = ' aria-current="page"'
def switch(cur):
    """View toggle shown top right on all three entrance views."""
    opts = [("index.html", "Table"), ("filmstrip.html", "Filmstrip")]   # Pairs is set aside for now (build with --pairs)
    return ('<nav class="view-toggle" aria-label="Choose a view"><span>View</span>' +
            "".join(f'<a href="{h}"{CUR if h == cur else ""}>{l}</a>' for h, l in opts) + "</nav>")
def head(extra_class):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>The Collector</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:wght@400;600&family=Young+Serif&display=swap">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/collage.css">
<link rel="stylesheet" href="assets/entrances.css">
<link rel="stylesheet" href="assets/views.css">
</head>
<body class="collage-page {extra_class}">
<div class="selvage" aria-hidden="true"></div>
"""
NOTE = f"""<footer class="collage-note"><p><strong>Teaching note.</strong> This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by <a href="{REPO_URL}/issues">opening an issue on GitHub</a>.</p></footer>"""

# ---------------- 1. lightbox wall ----------------
cells = []
for t in tiles:
    a = ar(t["image"])
    cells.append(f'<a class="lb {t["kind"]}" href="{t["href"]}" style="--ar:{a:.3f}" data-k="{t["label"]}" data-t="{E(t["title"])}">'
                 f'<img src="{thumb(t["image"])}" alt="{E(t["title"])}" loading="lazy" draggable="false"></a>')
lightbox = head("lightbox-page") + f"""
<main class="wall" aria-label="Every image in the collection. Select one to enter">{''.join(cells)}<i class="fill"></i></main>
<div class="loupe" aria-hidden="true"></div>
<div class="lb-tag" aria-hidden="true"><span class="k"></span><span class="t"></span></div>
<div class="label-card">
  <h1>The Collector</h1>
  <p class="sub">Teaching With the F.A. Williams Collection</p>
  <p class="cue">Move the loupe across the wall · Select an image to enter</p>
</div>
{switch("lightbox.html")}
{NOTE}
<script>
(function () {{
  var root = document.documentElement, tag = document.querySelector('.lb-tag');
  var k = tag.querySelector('.k'), t = tag.querySelector('.t');
  addEventListener('pointermove', function (e) {{
    root.style.setProperty('--lx', e.clientX + 'px'); root.style.setProperty('--ly', e.clientY + 'px');
    document.body.classList.add('looking');
    var a = e.target.closest && e.target.closest('.lb');
    if (a) {{ k.textContent = a.dataset.k; t.textContent = a.dataset.t; tag.style.transform = 'translate(' + (e.clientX + 18) + 'px,' + (e.clientY + 18) + 'px)'; tag.hidden = false; }}
    else tag.hidden = true;
  }});
  document.addEventListener('pointerleave', function () {{ document.body.classList.remove('looking'); tag.hidden = true; }});
  document.querySelector('.wall').addEventListener('focusin', function (e) {{
    var a = e.target.closest('.lb'); if (!a) return; var r = a.getBoundingClientRect();
    root.style.setProperty('--lx', (r.left + r.width / 2) + 'px'); root.style.setProperty('--ly', (r.top + r.height / 2) + 'px');
    document.body.classList.add('looking');
  }});
}})();
</script>
</body></html>
"""
if "--lightbox" in sys.argv:
    (REPO / "lightbox.html").write_text(lightbox, encoding="utf-8")

# ---------------- 2. pairs across the archives ----------------
def tx(i):  # textile main image
    t = T[i]; return dict(img=TI[i][0]["image"], href=f"textiles/items/{i}.html", title=f'{t["title"]} {i}', src="Art and Art History", kind="textiles")
def ph(i):
    p = P[i]; return dict(img=p["image"], href=f"photography/items/{i}.html", title=p["title"], src="Harry Ransom Center", kind="photography")
def rec(img, slug, title):
    return dict(img=img, href=f"provenance/records/{slug}.html", title=title, src="Art and Art History · paper record", kind="provenance")
PAIRS = [
    (ph("HRC-5182"), tx("2148-606"), "In 1940 Williams sat for his studio portrait on this Chief blanket.", "depicts · confirmed"),
    (ph("HRC-5178"), tx("2148-588"), "The pillow beside him is two woven samplers sewn together, catalogued as 2148-588.", "depicts · confirmed"),
    (rec("provenance/images/web/img_2232.jpg", "catalog-cards", "Catalog card 2148-586"), tx("2148-586"), "The Texas Memorial Museum card, about 1966–68, and the shawl it describes.", "documents"),
    (rec("provenance/images/web/img_2239.jpg", "catalog-cards", "Catalog card 1654-129"), tx("1654-129"), "\"UT – Williams collection,\" typed on the card for this blanket.", "documents"),
    (rec("provenance/images/web/img_2243.jpg", "catalog-cards", "Catalog card 1074-106"), tx("1074-106"), "The card for a second phase Chief's shoulder blanket.", "documents"),
    (ph("HRC-4849"), rec("provenance/images/web/screen-shot-2018-04-22-at-5-27-44-pm.jpg", "announcement-of-gift", "Announcement of Gift: biography"), "Williams's own 1948 biography, and the one the University wrote when it accepted his collection.", "two accounts of one life"),
    (ph("HRC-4872"), rec("provenance/images/web/screen-shot-2018-05-07-at-10-00-04-am.jpg", "accession-record", "Accession record, 1969"), "His brochure boasts of \"an unequalled collection\"; the museum's record lists it item by item.", "two accounts of one collection"),
    (ph("HRC-5192"), ph("HRC-5182"), "The Arrowmaker on a lantern slide, and the same sculpture at Williams's side in 1940.", "within one archive"),
]
def half(d):
    return (f'<a class="half {d["kind"]}" href="{d["href"]}"><img src="{thumb(d["img"])}" alt="{E(d["title"])}" loading="lazy">'
            f'<span class="who"><span class="k">{E(d["src"])}</span>{E(d["title"])}</span></a>')
dips = ""
for n, (l, r, cap, rel) in enumerate(PAIRS):
    dips += (f'<figure class="dip{" lead" if n == 0 else ""}"><div class="halves">{half(l)}<span class="join" aria-hidden="true"></span>{half(r)}</div>'
             f'<figcaption><span class="rel">{E(rel)}</span>{E(cap)}</figcaption></figure>')
pairs = head("pairs-page") + f"""
<main class="pairs">
  <header class="pairs-head">
    <h1>The Collector</h1>
    <p class="sub">Teaching With the F.A. Williams Collection</p>
    <p class="lede">One collection, kept in two archives. Each pair joins an item from the Harry Ransom Center with one from the Department of Art and Art History. Select an image to enter.</p>
  </header>
  <div class="dips">{dips}</div>
</main>
{switch("pairs.html")}
</body></html>
"""
if "--pairs" in sys.argv:
    (REPO / "pairs.html").write_text(pairs, encoding="utf-8")

# ---------------- 3. filmstrip timeline ----------------
def year_of(s):
    m = re.search(r"(1[89]\d\d)", s or ""); return int(m.group(1)) if m else None
frames = []  # (sort_year, label, d)
for i, t in T.items():
    y = year_of(t["date"])
    if y and i != "2148-589":
        frames.append((y, t["date"], tx(i)))
for i, p in P.items():
    if p["cultural_review"]: continue
    y = year_of(p["date"]) or year_of(p["slide_inscription"])
    if y: frames.append((y, str(y), ph(i)))
frames += [
    (1966, "about 1966–68", rec("provenance/images/web/img_2239.jpg", "catalog-cards", "Catalog card 1654-129")),
    (1966.5, "about 1966–68", rec("provenance/images/web/img_2232.jpg", "catalog-cards", "Catalog card 2148-586")),
    (1967, "about 1966–68", rec("provenance/images/web/img_2243.jpg", "catalog-cards", "Catalog card 1074-106")),
    (1969, "September 1969", rec("provenance/images/web/screen-shot-2018-05-07-at-10-00-04-am.jpg", "accession-record", "Texas Memorial Museum accession record, Acc. No. 2148")),
]
frames.sort(key=lambda f: f[0])
ERAS = [(1860, "Weaving", "Diné weavers make the blankets, 1860s–1900s"), (1922, "The collector", "Williams in New York and Taos"),
        (1950, "Later weaving", ""), (1966, "The archive", "Texas Memorial Museum catalogues the gift")]
strip, last_era = "", None
for y, label, d in frames:
    era = [e for e in ERAS if y >= e[0]][-1]
    if era != last_era:
        strip += f'<div class="era"><span class="k">{era[0]}s</span><span class="n">{E(era[1])}</span><span class="d">{E(era[2])}</span></div>'
        last_era = era
    strip += (f'<a class="frame {d["kind"]}" href="{d["href"]}" style="--ar:{ar(d["img"]):.3f}"><img src="{thumb(d["img"])}" alt="{E(d["title"])}" loading="lazy" draggable="false">'
              f'<span class="when">{E(label)}</span><span class="what">{E(d["title"])}</span></a>')
film = head("film-page") + f"""
<main class="film" aria-label="Timeline of the collection, earliest first. Select an image to enter">
  <div class="reel">
    <div class="leader"><h1>The Collector</h1><p class="sub">Teaching With the F.A. Williams Collection</p>
      <p class="cue">Scroll through time → Select an image to enter</p><p class="note-s">{len(frames)} dated items, from the 1860s to the 1969 accession. Undated items are not on the strip.</p></div>
    {strip}
    <div class="leader end"><p class="cue">1969 → today</p><p class="note-s">The textiles stay with the Department of Art and Art History; the slides and photographs with the Harry Ransom Center. <a href="home.html">Enter the collection</a></p></div>
  </div>
</main>
{switch("filmstrip.html")}
<script>
(function () {{
  var f = document.querySelector('.film');
  f.addEventListener('wheel', function (e) {{ if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {{ f.scrollLeft += e.deltaY; e.preventDefault(); }} }}, {{ passive: false }});
  var down = null, moved = false;
  f.addEventListener('pointerdown', function (e) {{ if (e.pointerType !== 'mouse') return; down = {{ x: e.clientX, s: f.scrollLeft }}; moved = false; }});
  addEventListener('pointermove', function (e) {{ if (!down) return; var dx = e.clientX - down.x; if (Math.abs(dx) > 6) moved = true; if (moved) f.scrollLeft = down.s - dx; }});
  addEventListener('pointerup', function () {{ down = null; }});
  f.addEventListener('click', function (e) {{ if (moved) {{ e.preventDefault(); moved = false; }} }}, true);
}})();
</script>
</body></html>
"""
(REPO / "filmstrip.html").write_text(film, encoding="utf-8")

# Toggle on the table (index.html)
idx = (REPO / "index.html").read_text(encoding="utf-8")
idx = re.sub(r'<nav class="(proto-switch|view-toggle)".*?</nav>\n?', "", idx, flags=re.S)
idx = idx.replace('<link rel="stylesheet" href="assets/entrances.css">', '<link rel="stylesheet" href="assets/entrances.css">\n<link rel="stylesheet" href="assets/views.css">', 1) if "views.css" not in idx else idx
idx = idx.replace("</main>", "</main>\n" + switch("index.html"), 1)
(REPO / "index.html").write_text(idx, encoding="utf-8")
print(f"views: table + filmstrip ({len(frames)} frames)" + (f" + pairs ({len(PAIRS)})" if "--pairs" in sys.argv else ""))
