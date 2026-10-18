#!/usr/bin/env python3
"""Render the static site (GitHub Pages, served from the repository root).

  python3 scripts/build_site.py                 # all images shown, review items flagged
  python3 scripts/build_site.py --withhold      # images flagged for cultural review are withheld
"""
import csv, html, json, re, sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WITHHOLD = "--withhold" in sys.argv
E = html.escape
SITE = "The Collector"
SUB = "Teaching With the F.A. Williams Collection"
REPO_URL = "https://github.com/alinascott/The-Collector"

def rcsv(p): return list(csv.DictReader(open(REPO / p, encoding="utf-8")))
textiles = rcsv("textiles/textiles.csv")
timgs = defaultdict(list)
for r in rcsv("textiles/textile_images.csv"): timgs[r["textile_id"]].append(r)
photos = rcsv("photography/photographs.csv")
intros = {r["group_slug"]: r for r in rcsv("photography/group_introductions.csv")}
records = rcsv("provenance/records.csv")
events = rcsv("provenance/events.csv")
cross = rcsv("data/crosswalk.csv")
T = {r["id"]: r for r in textiles}; P = {r["id"]: r for r in photos}; R = {r["id"]: r for r in records}

def frag(name):
    s = (REPO / "_source/fragments" / f"{name}.html").read_text(encoding="utf-8")
    meta = json.loads(re.match(r"<!--(.*?)-->", s, re.S).group(1))
    return meta, s.split("-->", 1)[1]

def thumb(p): return p.replace("/web/", "/thumb/")
def withheld(p): return WITHHOLD and p.get("cultural_review")

# ---------- page shell ----------
NAV = [("provenance", "Provenance", "provenance/index.html"), ("textiles", "Textiles", "textiles/index.html"),
       ("photography", "Photography", "photography/index.html"), ("teaching", "Teaching", "teaching/index.html"),
       ("about", "About", "about.html")]
def page(path, title, body, section=""):
    depth = path.count("/"); root = "../" * depth
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{root}{h}" data-path="{k}"{cur if k == section else ""}>{l}</a>' for k, l, h in NAV)
    full_title = SITE if title == SITE else f"{title} · {SITE}"
    out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full_title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:ital,wght@0,400;0,600;1,400&family=Young+Serif&display=swap">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>
<div class="selvage" aria-hidden="true"></div>
<header class="site-head"><div class="wrap">
<a class="brand" href="{root}home.html">{SITE}<small>{SUB}</small></a>
<nav class="main" aria-label="Main">{nav}</nav>
</div></header>
<main class="wrap">
{body.replace("{{ROOT}}", root)}
</main>
<footer class="site-foot"><div class="wrap">
<div class="teaching-note" id="teaching-note"><p class="eyebrow">Teaching note</p>
<p>This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by <a href="{REPO_URL}/issues">opening an issue on GitHub</a>.</p></div>
<p>Textile images and paper records: Department of Art and Art History, The University of Texas at Austin, used with permission. Photographs and lantern slides: Harry Ransom Center, The University of Texas at Austin, shown for education and research; the Ransom Center does not own the rights to these items. <a href="{root}about.html#rights">Rights and takedown</a>.</p>
<p>Compiled by Alina I. Scott. Source data for every page is in the <a href="{REPO_URL}">repository</a> as CSV.</p>
</div></footer>
</body>
</html>
"""
    out = out.replace("{{ROOT}}", root)
    dest = REPO / path; dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")

# ---------- helpers ----------
def textile_card(t):
    img = timgs[t["id"]][0]["image"] if timgs[t["id"]] else ""
    meta = " · ".join(x for x in [t["date"], t["style"]] if x)
    return (f'<a class="card" href="{{{{ROOT}}}}textiles/items/{t["id"]}.html" data-group="{t["accession_group"]}" data-type="{E(t["object_type"].lower())}">'
            f'<span class="thumb"><img src="{{{{ROOT}}}}{thumb(img)}" alt="{E(t["title"])} {t["id"]}" loading="lazy"></span>'
            f'<span class="acc">{t["id"]}</span><span class="t">{E(t["title"])}</span><span class="m">{E(meta) or "&nbsp;"}</span></a>')

def photo_card(p):
    if withheld(p):
        im = '<span class="withheld">Image withheld pending community review</span>'
    else:
        im = f'<img src="{{{{ROOT}}}}{thumb(p["image"])}" alt="{E(p["title"])}" loading="lazy">'
    flag = '<span class="flag">Community review</span>' if p["cultural_review"] else ""
    return (f'<a class="card" href="{{{{ROOT}}}}photography/items/{p["id"]}.html"><span class="thumb">{im}</span>'
            f'<span class="acc">{p["id"]}</span><span class="t">{E(p["title"])}</span>{flag}</a>')

def ref(i):
    """(title, href, thumb, kind) for any id in the crosswalk"""
    if i in T:
        t = T[i]; im = timgs[i][0]["image"] if timgs[i] else ""
        return f'{t["title"]} ({i})', f"textiles/items/{i}.html", thumb(im), "Textile"
    if i in P:
        p = P[i]; return p["title"], f"photography/items/{i}.html", "" if withheld(p) else thumb(p["image"]), "Photograph, Harry Ransom Center"
    if i in R:
        r = R[i]; im = r["images"].split("; ")[0] if r["images"] else ""
        return r["title"], f"provenance/records/{r['slug']}.html", thumb(im), "Paper record"
    return i, "", "", ""

def connections(i):
    rows = []
    for c in cross:
        if i not in (c["from_id"], c["to_id"]): continue
        other = c["to_id"] if c["from_id"] == i else c["from_id"]
        rel = c["relationship"]
        if c["to_id"] == i and rel == "depicts": rel = "depicted in"
        if c["to_id"] == i and rel == "documents": rel = "documented by"
        title, href, th, kind = ref(other)
        img = f'<img src="{{{{ROOT}}}}{th}" alt="" loading="lazy">' if th else '<span class="withheld" style="aspect-ratio:1;width:64px;padding:0"></span>'
        rows.append(f'<a class="link-row" href="{{{{ROOT}}}}{href}">{img}<span><span class="eyebrow">{E(rel)} · {E(kind)}</span><br>'
                    f'<span class="t">{E(title)}</span> <span class="conf {c["confidence"]}">{c["confidence"]}</span><br><span class="e">{E(c["evidence"])}</span></span></a>')
    return "".join(rows)

def dl(pairs):
    return "<dl>" + "".join(f"<dt>{E(k)}</dt><dd>{v}</dd>" for k, v in pairs if v) + "</dl>"

# ---------- home ----------
studio = P["HRC-5182"]
review_n = sum(1 for p in photos if p["cultural_review"])
home = f"""
<section class="hero">
  <div class="pagehead">
    <p class="eyebrow">Teaching With the F.A. Williams Collection</p>
    <h1>One collection, two archives.</h1>
    <p class="lede">In 1940 the sculptor Frederic Allen Williams sat for a portrait in his New York studio on a Diné Chief blanket. His textiles later went to the Texas Memorial Museum and the Department of Art and Art History. His photographs and lantern slides went to the Harry Ransom Center. This site brings them back together.</p>
    <p>It joins the 2018 <em>Woven into History</em> archive of Navajo textiles with Williams's slides and ephemera at the Ransom Center, and follows the collection along three paths.</p>
  </div>
  <figure class="fig">
    <a href="{{{{ROOT}}}}photography/items/HRC-5182.html"><img src="{{{{ROOT}}}}{studio['image']}" alt="Frederic Allen Williams in his studio, 1940, seated on a Chief blanket"></a>
    <figcaption>"Studio 1940." Williams sits on <a href="{{{{ROOT}}}}textiles/items/2148-606.html">Chief Blanket 2148-606</a>, beside the composite sampler <a href="{{{{ROOT}}}}textiles/items/2148-588.html">2148-588</a>. <span class="src">Harry Ransom Center · Lantern slide, series I-F</span></figcaption>
  </figure>
</section>

<section class="stack">
  <h2>Three paths through the collection</h2>
  <div class="paths">
    <a class="path provenance" href="{{{{ROOT}}}}provenance/index.html"><img src="{{{{ROOT}}}}provenance/images/thumb/img_2239.jpg" alt="Texas Memorial Museum catalog card for 1654-129" loading="lazy">
      <span class="body"><span class="eyebrow provenance">Provenance</span><h3>How the collection came apart</h3>
      <span>The Deed of Trust, the 1969 accession record, catalog cards, and the essay that first matched a photograph to a blanket.</span>
      <span class="count">{len(records)} record groups · {len(events)} dated events</span></span></a>
    <a class="path textiles" href="{{{{ROOT}}}}textiles/index.html"><img src="{{{{ROOT}}}}{thumb(timgs['2148-606'][0]['image'])}" alt="Chief Blanket 2148-606" loading="lazy">
      <span class="body"><span class="eyebrow textiles">Textiles</span><h3>Navajo weaving, 1860s–1950s</h3>
      <span>Chief blankets, saddle blankets, a shawl, rugs and samplers, with documentation photographs, details and in-person photographs.</span>
      <span class="count">{len(textiles)} textiles · {sum(len(v) for v in timgs.values())} images</span></span></a>
    <a class="path photography" href="{{{{ROOT}}}}photography/index.html"><img src="{{{{ROOT}}}}photography/images/thumb/HRC-5192.jpg" alt="Lantern slide of The Arrowmaker" loading="lazy">
      <span class="body"><span class="eyebrow photography">Photography</span><h3>Williams's lantern slides</h3>
      <span>Slides of his sculpture, of Williams himself, of Taos and Red River, and his lecture brochures, from the Harry Ransom Center.</span>
      <span class="count">{len(photos)} items · {len(intros)} introductions by Jesse Ritner</span></span></a>
  </div>
</section>

<section class="two">
  <div class="panel"><p class="eyebrow">Archive one</p><h3>Woven into History</h3>
    <p>A public and digital history project begun in 2018 in Dr. Joan Neuberger's graduate course at UT Austin. Textiles photographed for the Art and Art History Visual Resources Collection (DASe), with the paper records that came with them.</p>
    <p class="note">Department of Art and Art History · accession groups 2148, 1654, 1074, 1633</p></div>
  <div class="panel"><p class="eyebrow">Archive two</p><h3>Frederic Allen Williams Collection</h3>
    <p>Williams's own lantern slides and photographs: records of his sculpture, portraits of himself in costume, Taos scenes, and the brochures for his lectures on the "Arts of the Americas."</p>
    <p class="note">Harry Ransom Center · Lantern Slide Collection series I and III; Photograph Collection series III</p></div>
</section>

<section class="callout">
  <p><strong>About the images</strong></p>
  <p>This collection was assembled by a non-Native collector. {review_n} of the photographs show Taos Pueblo people and places, a dance, or Williams dressed as Native and Mexican people. They are marked for community review and carry context on their pages. See <a href="{{{{ROOT}}}}about.html#protocols">cultural protocols</a>.</p>
</section>
"""
page("home.html", SITE, home.replace('<p class="eyebrow">Teaching With the F.A. Williams Collection</p>', '<p class="eyebrow"><a href="{{ROOT}}index.html">Back to the entrance</a></p>'))

# ---------- collage (index.html): the way in ----------
import random
tiles = []
for t in textiles:
    for i in timgs[t["id"]]:
        if i["role"].startswith("in-person"): continue
        if t["id"] == "2148-589": continue     # whirling-log motif needs its essay; keep it out of the collage
        tiles.append(("textiles", "Textile", f'{t["title"]} {t["id"]}', i["image"], f"textiles/items/{t['id']}.html"))
for p in photos:
    if p["cultural_review"]: continue          # flagged images stay out of the collage; they keep their pages
    tiles.append(("photography", "Photograph", p["title"], p["image"], f"photography/items/{p['id']}.html"))
for r in records:
    for im in [x for x in r["images"].split("; ") if x]:
        if "screen-shot" in im: continue      # screenshots of PDFs read poorly at tile size
        tiles.append(("provenance", "Paper record", r["title"], im, f"provenance/records/{r['slug']}.html"))
seen, uniq = set(), []
for tl in tiles:
    key = tl[3].split("/")[-1]
    if key in seen: continue
    seen.add(key); uniq.append(tl)
random.Random(1940).shuffle(uniq)
(REPO / "data").mkdir(exist_ok=True)
(REPO / "data/collage_tiles.json").write_text(json.dumps(
    [dict(zip(["kind", "label", "title", "image", "href"], t)) for t in uniq], ensure_ascii=False, indent=1), encoding="utf-8")
NCOL = 5
cols = [[] for _ in range(NCOL)]
for n, tl in enumerate(uniq): cols[n % NCOL].append(tl)
def tile(tl, hidden=False):
    kind, label, title, img, href = tl
    ah = ' aria-hidden="true" tabindex="-1"' if hidden else ""
    return (f'<a class="tile {kind}" href="{href}"{ah}><img src="{thumb(img)}" alt="{"" if hidden else E(title)}" loading="lazy">'
            f'<span class="cap"><span class="k">{label}</span><span class="n">{E(title)}</span></span></a>')
col_html = ""
for c, items in enumerate(cols):
    dur = 70 + (c * 17) % 45
    col_html += (f'<div class="col" style="--dur:{dur}s" data-dir="{"down" if c % 2 else "up"}"><div class="track">'
                 + "".join(tile(x) for x in items) + "".join(tile(x, True) for x in items) + "</div></div>")
collage = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{SITE}</title>
<meta name="description" content="{SUB}. Select an image to enter the collection.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:wght@400;600&family=Young+Serif&display=swap">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/collage.css">
</head>
<body class="collage-page">
<div class="selvage" aria-hidden="true"></div>
<main class="collage" aria-label="Select an image to enter the collection">
{col_html}
</main>
<div class="threshold" role="presentation">
  <p class="eyebrow">Textiles · Photographs · Paper records</p>
  <h1>{SITE}</h1>
  <p class="sub">{SUB}</p>
  <p class="cue">Select an image to enter the collection</p>
</div>
<footer class="collage-note"><p><strong>Teaching note.</strong> This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by <a href="{REPO_URL}/issues">opening an issue on GitHub</a>.</p></footer>
</body>
</html>
"""
if "--drifting" in sys.argv:  # the earlier drifting-columns entrance; index.html is now built by build_entrances.py
    (REPO / "drifting.html").write_text(collage, encoding="utf-8")
print("collage tiles:", len(uniq))

# ---------- textiles ----------
groups = sorted({t["accession_group"] for t in textiles}, key=lambda g: (g != "2148", g))
types = sorted({t["object_type"].lower() for t in textiles})
chips = '<button class="chip" type="button" aria-pressed="true" data-f="all">All</button>' + \
    "".join(f'<button class="chip" type="button" aria-pressed="false" data-f="g:{g}">Group {g}</button>' for g in groups)
ctx = [frag(n) for n in ["textiles_context__the-navajo", "textiles_context__bedouins-of-the-great-southwestern-desert",
                         "textiles_context__trader-catalogs-weaver-profiles", "textiles_context__whirling-log"]]
ctx_links = "".join(f'<a class="link-row" href="{{{{ROOT}}}}textiles/context/{m["slug"]}.html"><span></span><span><span class="t">{E(m["title"])}</span><br><span class="e">Essay · {m["date"]}</span></span></a>' for m, _ in ctx)
tbody = f"""
<div class="pagehead"><p class="eyebrow textiles">Pathway · Textiles</p><h1>Textiles</h1>
<p class="lede">Seventeen Diné textiles from the University of Texas collections: Chief blankets in the second and third phase styles, saddle and shoulder blankets, a woman's shawl, rugs, and two woven samplers.</p>
<p class="muted">All seventeen are from the Frederic Allen Williams Collection. The prefix is the accession group: 2148 is the Texas Memorial Museum accession of the collection; the accession record names 1654 for further Williams items; 1074 and 1633 hold the rest.</p></div>
<section class="stack"><div class="chips" role="group" aria-label="Filter by accession group">{chips}</div>
<div class="grid" id="tgrid">{''.join(textile_card(t) for t in textiles)}</div></section>
<section class="stack"><h2>Context</h2><p class="muted">Essays from the 2018 site on dyes, trade catalogs, weavers and motifs.</p><div class="links">{ctx_links}</div></section>
<script>
document.querySelectorAll('.chip').forEach(function (b) {{
  b.addEventListener('click', function () {{
    document.querySelectorAll('.chip').forEach(function (x) {{ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }});
    var f = b.dataset.f;
    document.querySelectorAll('#tgrid .card').forEach(function (c) {{ c.hidden = !(f === 'all' || 'g:' + c.dataset.group === f); }});
  }});
}});
</script>"""
page("textiles/index.html", "Textiles", tbody, "textiles")
for m, b in ctx:
    page(f"textiles/context/{m['slug']}.html", m["title"], f"""<div class="pagehead"><p class="eyebrow textiles">Textiles · Context</p><h1>{E(m['title'])}</h1>
<p class="note">Alina Scott · first published {m['date']} on <a href="{m['source']}">Woven into History</a></p></div><article class="prose">{b}</article>""", "textiles")

for t in textiles:
    ims = timgs[t["id"]]
    main = ims[0] if ims else None
    rest = ims[1:]
    def gal(role_pred, label):
        sel = [i for i in rest if role_pred(i["role"])]
        if not sel: return ""
        return (f'<section class="stack"><h3>{label}</h3><div class="gallery">' +
                "".join(f'<figure class="fig"><a href="{{{{ROOT}}}}{i["image"]}"><img src="{{{{ROOT}}}}{thumb(i["image"])}" alt="{E(t["title"])} {t["id"]}, {E(i["role"])}" loading="lazy"></a></figure>' for i in sel) +
                "</div></section>")
    card = f"""<div class="catcard"><div class="top"><span class="acc">{t['id']}</span><span class="eyebrow">Acc. group {t['accession_group']}</span></div>
{dl([("Object", E(t['object_type'])), ("Date", E(t['date']) or '<span class="muted">not recorded</span>'), ("Style", E(t['style'])),
     ("Materials", E(t['materials'])), ("Collector", E(t['collector_as_recorded']) or '<span class="muted">not stated on source</span>'),
     ("Williams link", E(t['williams_attribution'])), ("Photographer", E(t['photographer'])), ("DASe image", E(t['dase_image'])),
     ("Held by", E(t['holding']))])}</div>"""
    conn = connections(t["id"])
    body = f"""
<div class="pagehead"><p class="eyebrow textiles"><a href="{{{{ROOT}}}}textiles/index.html">Textiles</a> · {t['id']}</p><h1>{E(t['title'])}</h1></div>
<div class="item">
  <div class="stack">
    <figure class="fig main-img"><a href="{{{{ROOT}}}}{main['image'] if main else ''}"><img src="{{{{ROOT}}}}{main['image'] if main else ''}" alt="{E(t['title'])} {t['id']}"></a>
      <figcaption>Documentation photograph{(' by ' + E(t['photographer'])) if t['photographer'] else ''}. Department of Art and Art History, UT Austin.</figcaption></figure>
    <div class="prose"><p>{E(t['description'])}.</p>{f'<p class="note">{E(t["notes"])}</p>' if t['notes'] else ''}</div>
    {gal(lambda r: r == 'detail' or 'alternate' in r, 'Details')}
    {gal(lambda r: r.startswith('in-person'), 'In-person photographs, April 2018')}
  </div>
  <aside>{card}
    {f'<section class="stack"><h3>Connections</h3><div class="links">{conn}</div></section>' if conn else ''}
    <p class="note">Source: <a href="{t['source_post']}">original Woven into History post</a>. Subjects: {E(t['subjects'])}.</p>
  </aside>
</div>"""
    page(f"textiles/items/{t['id']}.html", f"{t['title']} {t['id']}", body, "textiles")

# ---------- photography ----------
GORDER = ["williams-work", "williams", "towns", "taos-people", "ephemera"]
GDESC = {"ephemera": "Printed matter from the Frederic Allen Williams Photograph Collection, series III, container 57: his lecture brochures and a 1948 biography.",
         "taos-people": "Portraits made in Taos, several in the painter Bert Phillips's studio and patio. Most sitters are unnamed; a few slides carry first names."}
sections = []
for g in GORDER:
    items = [p for p in photos if p["group_slug"] == g]
    if not items: continue
    gname = items[0]["group"]
    intro = intros.get(g)
    q = f'<blockquote class="note" style="margin:0;max-width:68ch">“{E(intro["introduction"].replace("  ", " "))}” <br>— {E(intro["author"])}, <a href="https://fredericallenwilliams.wordpress.com">Frederic Allen Williams: A Citizen Artist with a Magic Lantern</a></blockquote>' if intro else ""
    d = f'<p class="muted" style="max-width:68ch">{E(GDESC[g])}</p>' if g in GDESC else ""
    sections.append(f'<section class="stack" id="{g}"><h2>{E(gname)}</h2>{q}{d}<div class="grid">{"".join(photo_card(p) for p in items)}</div></section>')
toc = " · ".join(f'<a href="#{g}">{E(next(p["group"] for p in photos if p["group_slug"] == g))}</a>' for g in GORDER)
pbody = f"""
<div class="pagehead"><p class="eyebrow photography">Pathway · Photography</p><h1>Photography</h1>
<p class="lede">Frederic Allen Williams photographed his own work, himself and the places he visited, and lectured with the results. These {len(photos)} items are from his collections at the Harry Ransom Center.</p>
<p class="muted">Titles come from the captions supplied with the images. Titles in square brackets were written for this site where no caption existed. {toc}</p></div>
{''.join(sections)}
<section class="callout" id="takedown"><p><strong>Harry Ransom Center notice</strong></p><p>This material is made available for education and research purposes only. The Harry Ransom Center does not own the rights for these items; it cannot grant or deny permission to use this material. Rights holders may be listed in the <a href="http://norman.hrc.utexas.edu/watch/">WATCH file</a>. Upon request, material will be removed from public view while a rights issue is addressed.</p></section>"""
page("photography/index.html", "Photography", pbody, "photography")

for p in photos:
    if withheld(p):
        img = '<div class="withheld">Image withheld pending community review. The record is kept so the item can be found and requested.</div>'
    else:
        img = f'<figure class="fig main-img"><a href="{{{{ROOT}}}}{p["image"]}"><img src="{{{{ROOT}}}}{p["image"]}" alt="{E(p["title"])}"></a><figcaption>{E(p["collection"])}, Harry Ransom Center.</figcaption></figure>'
    flag = f'<div class="callout"><p><strong>Community review</strong></p><p>{E(p["cultural_review"])}. This image is shown in the preview and will be reviewed before the public site goes live.</p></div>' if p["cultural_review"] else ""
    ser = " ".join(x for x in [("series " + p["series"]) if p["series"] else "", p["subseries_or_container"]] if x)
    card = f"""<div class="catcard"><div class="top"><span class="acc">{p['id']}</span><span class="eyebrow">{E(p['object_type'])}</span></div>
{dl([("Title source", E(p['title_source'])), ("Date", E(p['date'])), ("Slide label", E(p['slide_inscription'])),
     ("Collection", E(p['collection'])), ("Series", E(ser)), ("Repository", E(p['repository'])),
     ("Caption received", E(p['caption_as_received']) or '<span class="muted">none</span>')])}</div>"""
    conn = connections(p["id"])
    body = f"""
<div class="pagehead"><p class="eyebrow photography"><a href="{{{{ROOT}}}}photography/index.html">Photography</a> · <a href="{{{{ROOT}}}}photography/index.html#{p['group_slug']}">{E(p['group'])}</a></p><h1>{E(p['title'])}</h1></div>
<div class="item">
  <div class="stack">{img}<div class="prose"><p>{E(p['description'])}</p>{f'<p class="note">{E(p["notes"])}</p>' if p['notes'] else ''}</div></div>
  <aside>{flag}{card}
  {f'<section class="stack"><h3>Connections</h3><div class="links">{conn}</div></section>' if conn else ''}
  <p class="note">Shown for education and research. The Harry Ransom Center does not own the rights to this item. <a href="{{{{ROOT}}}}photography/index.html#takedown">Takedown notice</a>.</p></aside>
</div>"""
    page(f"photography/items/{p['id']}.html", p["title"], body, "photography")

# ---------- provenance ----------
ess = [frag("provenance__archives-in-conversation"), frag("provenance__decoding-catalog-cards")]
for m, b in ess:
    page(f"provenance/{m['slug']}.html", m["title"], f"""<div class="pagehead"><p class="eyebrow provenance">Provenance · Essay</p><h1>{E(m['title'])}</h1>
<p class="note">Alina Scott · first published {m['date']} on <a href="{m['source']}">Woven into History</a></p></div><article class="prose">{b}</article>""", "provenance")
rec_rows = ""
for r in records:
    m, b = frag(f"records__{r['slug']}")
    ims = [x for x in r["images"].split("; ") if x]
    pdf = f'<p><a href="{{{{ROOT}}}}{r["pdf"]}">Open the full PDF</a> <span class="note">(scanned document)</span></p>' if r["pdf"] else ""
    conn = connections(r["id"])
    page(f"provenance/records/{r['slug']}.html", r["title"], f"""
<div class="pagehead"><p class="eyebrow provenance"><a href="{{{{ROOT}}}}provenance/index.html">Provenance</a> · {r['id']}</p><h1>{E(r['title'])}</h1>
<p class="muted">{E(r['record_type'])} · {E(r['holding'])}</p>{pdf}</div>
<article class="prose" style="max-width:none">{b}</article>
{f'<section class="stack"><h3>Connections</h3><div class="links" style="max-width:68ch">{conn}</div></section>' if conn else ''}
<p class="note">Source: <a href="{r['source_post']}">original Woven into History post</a>.</p>""", "provenance")
    th = thumb(ims[0]) if ims else ""
    rec_rows += f'<a class="card" href="{{{{ROOT}}}}provenance/records/{r["slug"]}.html"><span class="thumb"><img src="{{{{ROOT}}}}{th}" alt="" loading="lazy"></span><span class="acc">{r["id"]}</span><span class="t">{E(r["title"])}</span><span class="m">{E(r["record_type"])}</span></a>'
tl = "".join(f'<li><span class="d">{E(e["date"])}</span><span>{E(e["event"])}<span class="s">{E(e["source"])}{(" · " + E(e["place"])) if e["place"] else ""}</span></span></li>' for e in events)
cards_not_digitized = "2148-582, 2148-583, 2148-591, 2148-604, 1074-104, 1074-115, 1238-62, 1633-75, 2617-1"
provbody = f"""
<div class="pagehead"><p class="eyebrow provenance">Pathway · Provenance</p><h1>Provenance</h1>
<p class="lede">Williams gave the University of Texas his whole collection by a Deed of Trust and kept it during his lifetime. After it reached Austin it was split: the textiles to the Texas Memorial Museum and later the Department of Art and Art History, the photographs and lantern slides to the Harry Ransom Center.</p></div>
<section class="two">
  <div class="stack"><h2>Chain of custody</h2><ol class="timeline">{tl}</ol></div>
  <div class="stack">
    <h2>Start here</h2>
    <div class="links">{''.join(f'<a class="link-row" href="{{{{ROOT}}}}provenance/{m["slug"]}.html"><span></span><span><span class="t">{E(m["title"])}</span><br><span class="e">Essay · {m["date"]}</span></span></a>' for m, _ in ess)}</div>
    <div class="panel"><h3>Accession groups</h3>
      <div class="table-wrap"><table><thead><tr><th>Group</th><th>What the records say</th></tr></thead><tbody>
      <tr><td class="acc">2148</td><td>Texas Memorial Museum accession of the Williams Collection, received September 1969 from storage at Balcones.</td></tr>
      <tr><td class="acc">1654</td><td>"Other items from this collection are accessioned under TMM Acc. No. 1654" (accession record).</td></tr>
      <tr><td class="acc">1074, 1633</td><td>Further textiles from the Williams Collection under separate accession numbers.</td></tr>
      </tbody></table></div></div>
    <div class="panel"><h3>What the record doesn't say yet</h3>
      <ul class="prose" style="gap:6px"><li>The date of the Deed of Trust and of Williams's death.</li>
      <li>When and why the photographs went to the Ransom Center and the textiles did not.</li>
      <li>Who wove these textiles, and through which traders they reached Williams.</li>
      <li>Catalog cards exist for textiles not yet digitized: {cards_not_digitized}.</li></ul></div>
  </div>
</section>
<section class="stack"><h2>Paper records</h2><div class="grid">{rec_rows}</div></section>"""
page("provenance/index.html", "Provenance", provbody, "provenance")

# ---------- teaching ----------
les = [frag(f"teaching__{s}") for s in ["the-wild-west", "colonizing-the-southwest", "space-place-and-manifest-destiny", "oral-and-cultural-history"]]
for m, b in les:
    page(f"teaching/{m['slug']}.html", m["title"], f"""<div class="pagehead"><p class="eyebrow">Teaching · Lesson plan</p><h1>{E(m['title'])}</h1>
<p class="note">Alina Scott · {m['date']}</p></div><article class="prose">{b}</article>""", "teaching")
page("teaching/index.html", "Teaching", f"""<div class="pagehead"><p class="eyebrow">Teaching</p><h1>Teaching with the collection</h1>
<p class="lede">Lesson plans for high school and undergraduate classes that use the textiles, trade catalogs and acquisition records as primary sources.</p></div>
<div class="links" style="max-width:68ch">{''.join(f'<a class="link-row" href="{m["slug"]}.html"><span></span><span><span class="t">{E(m["title"])}</span><br><span class="e">Lesson plan · {m["date"]}</span></span></a>' for m, _ in les)}</div>
<p><a href="files/digital-archive-worksheet.pdf">Digital archive worksheet (PDF)</a> · <a href="files/the-wild-west-slides.pdf">The Wild West? slides (PDF)</a></p>""", "teaching")

# ---------- about ----------
ab = {k: frag(f"about__{k}")[1] for k in ["home", "project-history", "mission", "legal"]}
page("about.html", "About", f"""<div class="pagehead"><p class="eyebrow">About</p><h1>About this collection</h1></div>
<section class="prose"><h2>About <em>The Collector</em></h2><p><em>The Collector</em> is a teaching collection built on two archives: the 2018 <em>Woven into History</em> site on the Williams textiles, and Williams's own slides and ephemera at the Harry Ransom Center.</p></section>
<section class="prose"><h2>From the 2018 site</h2><p><em>Woven into History</em> {ab['home']}</section>
<section class="prose"><h2>Project history</h2><p><em>Woven into History</em> {ab['project-history']}</section>
<section class="prose"><h2>What changed in 2026</h2>
<p>The WordPress site has been rebuilt as a static repository. Its textile posts became rows in <code>textiles/textiles.csv</code>, its paper-record posts became <code>provenance/records.csv</code>, and Williams's slides and ephemera from the Harry Ransom Center were added as <code>photography/photographs.csv</code>. Links between items live in <code>data/crosswalk.csv</code>, each with a confidence level and the evidence for it.</p>
<p>Corrections made while rebuilding are recorded in the item notes and in CORRECTIONS.md.</p></section>
<section class="prose" id="protocols"><h2>Cultural protocols</h2>
<p>The textiles are Diné work collected and catalogued by non-Native people. Several Ransom Center slides show Taos Pueblo people, places and a dance, and others show Williams dressed as Native, Arctic Indigenous and Mexican people. These items are marked for community review. Before the public launch, the plan is to consult the Navajo Nation Historic Preservation Department and Taos Pueblo, apply Local Contexts labels, and withhold any image the communities ask to restrict while keeping its catalog record.</p></section>
<section class="prose" id="rights"><h2>Rights and takedown</h2>{ab['legal']}
<p>Harry Ransom Center material is shown for education and research. The Ransom Center does not own the rights to these items and cannot grant or deny permission. To ask for an item to be removed from public view, open an issue on the <a href="{REPO_URL}/issues">GitHub repository</a>.</p></section>
<section class="prose"><h2>Credits</h2><p>Alina I. Scott, compiler and author of the 2018 essays and lesson plans. Dr. Joan Neuberger (course supervisor) and Dr. Astrid Runggaldier (Art and Art History). Textile photography by Steve Bourget and Kimberly L. Jones. Introductions to the Ransom Center slide groups by Jesse Ritner, PhD.</p></section>
""", "about")
print("built", "(withholding review images)" if WITHHOLD else "")
