#!/usr/bin/env python3
"""Extract the Woven into History WordPress export into repository data.

Reads  _source/wordpress/*.xml  and the WordPress media folder, and writes:
  textiles/textiles.csv, textiles/textile_images.csv
  provenance/records.csv
  _source/fragments/*.html   (cleaned post bodies, rendered later by build_site.py)
  data/media_manifest.csv    (source file -> repository image path)
  _review/unused_media.csv   (media not used by any published post)
"""
import csv, html, json, os, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEDIA = Path(os.environ.get("WP_MEDIA", REPO.parent / "Art History Collection"))
XML = next((REPO / "_source/wordpress").glob("*.xml"))
NS = {"wp": "http://wordpress.org/export/1.2/",
      "content": "http://purl.org/rss/1.0/modules/content/",
      "excerpt": "http://wordpress.org/export/1.2/excerpt/"}

root = ET.parse(XML).getroot().find("channel")
items = root.findall("item")
def f(i, k): return i.findtext(k, namespaces=NS) or ""

# ---------- attachments ----------
ATT = {}
for i in items:
    if f(i, "wp:post_type") == "attachment":
        rel = re.sub(r".*/uploads/|.*files\.wordpress\.com/", "", f(i, "wp:attachment_url"))
        ATT[f(i, "wp:post_id")] = {"rel": rel, "title": i.findtext("title") or "",
                                    "caption": html.unescape(f(i, "excerpt:encoded")).strip()}
REL2ID = {v["rel"]: k for k, v in ATT.items()}

posts = [i for i in items if f(i, "wp:post_type") in ("post", "page")]
BYID = {f(i, "wp:post_id"): i for i in posts}

# ---------- destinations ----------
DEST = {  # post id -> (section, slug)
    "105": ("textiles/context", "bedouins-of-the-great-southwestern-desert"),
    "478": ("textiles/context", "trader-catalogs-weaver-profiles"),
    "578": ("textiles/context", "whirling-log"),
    "24":  ("textiles/context", "the-navajo"),
    "894": ("provenance", "archives-in-conversation"),
    "730": ("provenance", "decoding-catalog-cards"),
    "225": ("teaching", "space-place-and-manifest-destiny"),
    "231": ("teaching", "oral-and-cultural-history"),
    "566": ("teaching", "colonizing-the-southwest"),
    "607": ("teaching", "the-wild-west"),
    "4": ("about", "home"), "51": ("about", "project-history"), "63": ("about", "mission"),
    "1008": ("about", "legal"), "99": ("about", "related-resources"), "33": ("about", "documents"),
    "25": ("about", "teaching-resources"),
}
RECORD_POSTS = {  # post id -> record id, slug, type
    "682": ("PR-01", "announcement-of-gift", "Deed of Trust announcement"),
    "975": ("PR-02", "accession-record", "Accession record"),
    "504": ("PR-03", "limited-accession-record", "Accession record (excerpt)"),
    "727": ("PR-04", "catalog-cards", "Catalog cards"),
    "905": ("PR-05", "binder-card-catalog", "Binder scans"),
    "592": ("PR-06", "photos-among-paperwork", "Acquisition photographs"),
    "555": ("PR-07", "williams-description", "Collection description"),
    "520": ("PR-08", "scans-and-notes", "Clippings, engravings, business cards"),
}
DRAFTS = ["109", "174", "181", "184", "253"]
PDF_MAP = {  # uploaded pdf -> repository path (duplicates "...1.pdf" collapse)
    "2018/04/announcement-of-gift-frederic-allen-williams.pdf": "provenance/records/announcement-of-gift.pdf",
    "2018/04/announcement-of-gift-frederic-allen-williams1.pdf": "provenance/records/announcement-of-gift.pdf",
    "2018/04/frederic-allen-williams.pdf": "provenance/records/williams-description.pdf",
    "2018/04/frederic-allen-williams1.pdf": "provenance/records/williams-description.pdf",
    "2018/05/accession-records-williams-collection.pdf": "provenance/records/accession-record-2148.pdf",
    "2018/04/scan-apr-5-2018-at-3-12-pm.pdf": "provenance/records/williams-paper-records-part-1.pdf",
    "2018/04/williams-engravings-and-newspaper-clippings.pdf": "provenance/records/williams-engravings-and-clippings.pdf",
    "2018/05/binder-scans-of-card-catalog-and-photographs-williams-collection.pdf": "provenance/records/binder-card-catalog-and-photographs.pdf",
    "2018/04/digital-archive-worksheet.pdf": "teaching/files/digital-archive-worksheet.pdf",
    "2018/04/the-wild-west_-1.pdf": "teaching/files/the-wild-west-slides.pdf",
}
RECORD_PDF = {"PR-01": "announcement-of-gift.pdf", "PR-02": "accession-record-2148.pdf",
              "PR-03": "williams-paper-records-part-1.pdf", "PR-05": "binder-card-catalog-and-photographs.pdf",
              "PR-07": "williams-description.pdf", "PR-08": "williams-engravings-and-clippings.pdf"}
# An image the old site borrowed from the HRC slides: point it at the HRC record instead
HRC_SUBSTITUTE = {"2018/04/img_51821.jpg": "HRC-5182"}

TEXTILE_RE = re.compile(r"\((\d{4}-\d+)\)\s*$")

# ---------- image bookkeeping ----------
manifest = {}   # source rel -> repo path (without size folder)
def image_dest(rel, section):
    if rel in HRC_SUBSTITUTE: return None
    stem = Path(rel).stem
    stem = re.sub(r"-e\d{10,}$", "", stem)
    dest = f"{section}/images/{{size}}/{stem}.jpg"
    manifest.setdefault(rel, dest)
    return manifest[rel]

# ---------- old URL -> new page ----------
URLMAP = {}
for i in posts:
    link = (i.findtext("link") or "").rstrip("/")
    pid = f(i, "wp:post_id"); t = i.findtext("title") or ""
    m = TEXTILE_RE.search(t)
    if m: URLMAP[link] = f"textiles/items/{m.group(1)}.html"
    elif pid in DEST:
        sec, slug = DEST[pid]
        URLMAP[link] = "about.html" if sec == "about" else ("teaching/" + slug + ".html" if sec == "teaching" else f"{sec}/{slug}.html")
    elif pid in RECORD_POSTS:
        URLMAP[link] = f"provenance/records/{RECORD_POSTS[pid][1]}.html"
URLMAP["https://wovenintohistory.wordpress.com"] = "index.html"
for k, v in {"images": "photography/index.html", "photographs": "photography/index.html",
             "textiles": "textiles/index.html", "paper-records": "provenance/index.html"}.items():
    URLMAP[f"https://wovenintohistory.wordpress.com/category/{k}"] = v

def map_href(h):
    h = html.unescape(h)
    hs = h.split("#")[0].rstrip("/")
    hs = hs.replace("http://", "https://")
    if hs in URLMAP: return "{{ROOT}}" + URLMAP[hs]
    m = re.search(r"wp-content/uploads/(.+)$", hs)
    if m:
        rel = m.group(1)
        if rel in PDF_MAP: return "{{ROOT}}" + PDF_MAP[rel]
        if rel in REL2ID: return "{{ROOT}}" + image_dest(rel, "assets").format(size="web")
    return h

# ---------- WordPress body -> clean HTML ----------
BLOCK = re.compile(r"^\s*<(/?)(p|div|figure|ul|ol|li|h\d|blockquote|table|pre|hr)", re.I)
def autop(s):
    out = []
    for chunk in re.split(r"\n\s*\n", s.strip()):
        c = chunk.strip()
        if not c: continue
        if BLOCK.match(c): out.append(c)
        else: out.append("<p>" + c.replace("\n", "<br>\n") + "</p>")
    return "\n".join(out)

def fig(att_id, caption=None, section="assets"):
    a = ATT.get(att_id)
    if not a: return ""
    if a["rel"] in HRC_SUBSTITUTE:
        hid = HRC_SUBSTITUTE[a["rel"]]
        alt_h = html.escape(re.sub("<[^>]+>", "", caption or a["caption"] or a["title"]))
        return (f'<figure class="fig"><a href="{{{{ROOT}}}}photography/items/{hid}.html">'
                f'<img src="{{{{ROOT}}}}photography/images/web/{hid}.jpg" alt="{alt_h}" loading="lazy"></a>'
                f'<figcaption>{caption or a["caption"]} <span class="src">Harry Ransom Center</span></figcaption></figure>')
    p = image_dest(a["rel"], section).format(size="web")
    cap = caption if caption is not None else a["caption"]
    alt = html.escape(re.sub("<[^>]+>", "", cap or a["title"]))
    capt = f"<figcaption>{cap}</figcaption>" if cap else ""
    return f'<figure class="fig"><img src="{{{{ROOT}}}}{p}" alt="{alt}" loading="lazy">{capt}</figure>'

def clean(body, section="assets"):
    keep = []
    def hold(x):
        x = re.sub(r'href="([^"{]+)"', lambda m: f'href="{html.escape(map_href(m.group(1)))}"', x)
        keep.append(x); return f"\x00{len(keep)-1}\x00"
    s = body.replace("&nbsp;", " ").replace("\xa0", " ")
    s = re.sub(r"\[contact-form\].*?\[/contact-form\]", "", s, flags=re.S)
    s = re.sub(r"\[googleapps[^\]]*\]", '<p class="note">The original site embedded a Google Sheets catalog here. It is replaced by the CSV data in this repository.</p>', s)
    def cap(m):
        aid = re.search(r'attachment_(\d+)', m.group(1))
        inner = m.group(2)
        text = re.sub(r"<a[^>]*>\s*<img[^>]*>\s*</a>|<img[^>]*>", "", inner).strip()
        return "\n\n" + hold(fig(aid.group(1) if aid else "", text, section)) + "\n\n"
    s = re.sub(r"\[caption([^\]]*)\](.*?)\[/caption\]", cap, s, flags=re.S)
    def gal(m):
        ids = re.search(r'ids="([\d,]+)"', m.group(0)).group(1).split(",")
        return "\n\n" + hold('<div class="gallery">' + "".join(fig(x, None, section) for x in ids) + "</div>") + "\n\n"
    s = re.sub(r"\[gallery[^\]]*\]", gal, s)
    # stray images
    def img(m):
        src = re.search(r'src="([^"]+)"', m.group(0))
        if not src: return ""
        rel = re.sub(r"\?.*$", "", re.sub(r".*/uploads/|.*files\.wordpress\.com/", "", src.group(1)))
        aid = REL2ID.get(rel)
        return "\n\n" + hold(fig(aid, None, section)) + "\n\n" if aid else ""
    s = re.sub(r"<a[^>]*>\s*<img[^>]*>\s*</a>|<img[^>]*>", img, s)
    s = re.sub(r'href="([^"]+)"', lambda m: f'href="{html.escape(map_href(m.group(1)))}"', s)
    s = re.sub(r'\s(style|class|data-[\w-]+)="[^"]*"', "", s)
    s = re.sub(r"<span>(.*?)</span>", r"\1", s, flags=re.S)
    s = re.sub(r"<p>\s*</p>", "", s)
    out = autop(s)
    out = re.sub(r"<p>\s*(\x00\d+\x00)\s*</p>", r"\1", out)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], out)

FRAG = REPO / "_source/fragments"; FRAG.mkdir(parents=True, exist_ok=True)
def write_frag(name, meta, body):
    (FRAG / f"{name}.html").write_text("<!--" + json.dumps(meta, ensure_ascii=False) + "-->\n" + body, encoding="utf-8")

# ---------- essays, lessons, about pages, drafts ----------
for pid, (sec, slug) in DEST.items():
    i = BYID[pid]
    section = "textiles" if sec.startswith("textiles") else ("provenance" if sec == "provenance" else "assets")
    meta = {"title": html.unescape(i.findtext("title") or ""), "date": f(i, "wp:post_date")[:10],
            "section": sec, "slug": slug, "source": i.findtext("link"), "wp_id": pid}
    write_frag(f"{sec.replace('/', '_')}__{slug}", meta, clean(f(i, "content:encoded"), section))
DR = REPO / "_source/wordpress/drafts"; DR.mkdir(parents=True, exist_ok=True)
for pid in DRAFTS:
    i = BYID[pid]
    (DR / f"{pid}-{re.sub(r'[^a-z0-9]+', '-', (i.findtext('title') or '').lower()).strip('-')}.html").write_text(
        f"<h1>{i.findtext('title')}</h1>\n<p><em>Unpublished draft, {f(i,'wp:post_date')[:10]}</em></p>\n" + clean(f(i, "content:encoded")), encoding="utf-8")

# ---------- textiles ----------
def field(txt, label, nxt):
    m = re.search(label + r"\s*:?\s*(.*?)\s*(?=(" + "|".join(nxt) + r")\b|$)", txt, re.S | re.I)
    return m.group(1).strip(" ;.") if m else ""
LABELS = ["TYPE", r"ID\s*NO\.?", "DATE", "COLLECTOR", "DESCRIPTION", "PHOTOGRAPHER", "PERMISSIONS"]
GENERIC = {"Gallery", "Textiles", "Blog", "Navajo", "Steve Bourget", "Kimberly Jones"}
STYLE_PAT = [("Second Phase", r"second phase"), ("Third Phase Transitional", r"third phase transitional"),
             ("Third Phase", r"third phase"), ("Transitional", r"transitional"), ('"Sunday" saddle blanket', r"sunday"),
             ("Traditional", r"traditional style")]
MAT_PAT = [("Germantown yarn", r"germantown"), ("cotton warp/weft", r"cotton"), ("bayeta", r"bayeta"),
           ("cochineal", r"cochineal"), ("indigo", r"indigo"), ("handspun wool", r"handspun|homespun"),
           ("aniline dyes", r"aniline|analine"), ("wool", r"\bwool\b")]
textiles, timgs = [], []
for i in posts:
    t = html.unescape(i.findtext("title") or "")
    m = TEXTILE_RE.search(t)
    if not m or f(i, "wp:status") != "publish": continue
    acc = m.group(1); c = f(i, "content:encoded")
    ids = re.findall(r"attachment_(\d+)", c) + [x for g in re.findall(r'ids="([\d,]+)"', c) for x in g.split(",")]
    txt = re.sub(r"\[/?caption[^\]]*\]|\[gallery[^\]]*\]", " ", c)
    txt = " ".join(html.unescape(re.sub("<[^>]+>", " ", txt)).replace("\xa0", " ").split())
    txt = re.sub(r"^.*?(?=\bTYPE\b)", "", txt, flags=re.S)
    get = lambda lab: field(txt, lab, [l for l in LABELS if l != lab])
    desc = get("DESCRIPTION"); typ = get("TYPE"); date = get("DATE"); coll = get("COLLECTOR"); phot = get("PHOTOGRAPHER")
    tail = re.search(r"Department of Art and Art History\.\s*(.*)$", txt)
    extra = tail.group(1).strip() if tail else ""
    idfield = get(r"ID\s*NO\.?")
    notes = []
    if idfield and idfield.split()[0].strip(".;") != acc:
        notes.append(f"Original post body gives ID as {idfield.split()[0]}; the title, image and catalog photo numbers indicate {acc}.")
    if "2148-58:" in c or "Woven Sampler: 2148-58[" in c: notes.append("Original image caption read '2148-58'; corrected to 2148-589.")
    if extra and not extra.lower().startswith("view personal"): notes.append(extra.replace('"Getting the Full Picture"', "the essay Archives in Conversation"))
    group = acc.split("-")[0]
    attrib = {"2148": "Williams Collection: TMM accession 2148",
              "1654": "Williams Collection: TMM accession 1654 (named in the 2148 accession record)"}.get(
              group, "Williams Collection (confirmed by Alina Scott, 2026)")
    if acc == "2148-606": attrib = "Williams Collection: visible in Williams's 1940 studio portrait (HRC)"
    style = next((s for s, p in STYLE_PAT if re.search(p, desc, re.I)), "")
    mats = "; ".join(s for s, p in MAT_PAT if re.search(p, desc, re.I))
    cats = [x.text for x in i.findall("category") if x.text and x.text not in GENERIC]
    phot = re.sub(r"Bourget, Steve", "Steve Bourget", phot)
    phot = re.sub(r",?\s*original (documentation )?photograph(y)?", "", phot).strip(" ,")
    # images
    seen, prim = [], None
    for x in ids:
        a = ATT.get(x)
        if not a or a["rel"] in seen: continue
        seen.append(a["rel"])
    docs = [r for r in seen if re.match(r"1[25]-\d{5}(_\d+)?$", Path(r).stem)]
    def size(r):
        try: return (MEDIA / r).stat().st_size
        except OSError: return 0
    if docs: prim = max(docs, key=size)
    base = Path(prim).stem.split("_")[0] if prim else ""
    order = 0
    for r in ([prim] if prim else []) + [r for r in seen if r != prim and not (Path(r).stem.split("_")[0] == base and r in docs)]:
        stem = Path(r).stem
        if r == prim: role = "documentation photograph (Art & Art History DASe)"
        elif re.search(r"-x|zoom|screen-shot", stem): role = "detail"
        elif re.match(r"1[25]-\d{5}", stem): role = "documentation photograph (alternate)"
        else: role = "in-person photograph (Alina Scott, 2018)"
        order += 1
        timgs.append({"textile_id": acc, "order": order, "role": role,
                      "image": image_dest(r, "textiles").format(size="web"), "source_file": r})
    textiles.append({"id": acc, "title": t.replace(f" ({acc})", ""), "object_type": re.sub(r";\s*textiles?$", "", typ.replace("blankt", "blanket")).strip().capitalize(),
                     "date": "" if date.lower() in ("n/a", "") else date.replace(" (creation)", ""),
                     "style": style, "materials": mats, "description": desc,
                     "weaver": "", "collector_as_recorded": coll, "williams_attribution": attrib, "accession_group": group,
                     "photographer": phot, "dase_image": base, "holding": "Department of Art and Art History, UT Austin",
                     "subjects": "; ".join(sorted(set(cats), key=str.lower)), "notes": " ".join(notes),
                     "source_post": i.findtext("link")})
textiles.sort(key=lambda r: (r["accession_group"] != "2148", r["accession_group"], int(r["id"].split("-")[1])))

def wcsv(path, rows):
    path = REPO / path; path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
wcsv("textiles/textiles.csv", textiles)
wcsv("textiles/textile_images.csv", timgs)

# ---------- provenance records ----------
records = []
for pid, (rid, slug, rtype) in RECORD_POSTS.items():
    i = BYID[pid]; c = f(i, "content:encoded")
    ids = [x for g in re.findall(r'ids="([\d,]+)"', c) for x in g.split(",")] + re.findall(r"attachment_(\d+)", c)
    body = clean(c, "provenance")
    write_frag(f"records__{slug}", {"title": html.unescape(i.findtext("title")), "record_id": rid, "slug": slug,
               "date": f(i, "wp:post_date")[:10], "source": i.findtext("link")}, body)
    imgs = []
    for x in ids:
        a = ATT.get(x)
        if a:
            d = image_dest(a["rel"], "provenance")
            if d and d.format(size="web") not in imgs: imgs.append(d.format(size="web"))
    records.append({"id": rid, "title": re.sub(r"\s*\(2148\)\s*$", "", html.unescape(i.findtext("title"))).strip(),
                    "record_type": rtype, "slug": slug,
                    "pdf": ("provenance/records/" + RECORD_PDF[rid]) if rid in RECORD_PDF else "",
                    "images": "; ".join(imgs), "holding": "Department of Art and Art History, UT Austin" if rid != "PR-08" else "Copies at Art and Art History; originals at the Harry Ransom Center",
                    "source_post": i.findtext("link")})
records.sort(key=lambda r: r["id"])
wcsv("provenance/records.csv", records)

# ---------- media manifest + unused ----------
rows = [{"source_file": k, "repo_path": v} for k, v in sorted(manifest.items())]
for k, v in PDF_MAP.items(): rows.append({"source_file": k, "repo_path": v})
wcsv("data/media_manifest.csv", rows)
used = set(manifest) | set(PDF_MAP) | set(HRC_SUBSTITUTE)
unused = [{"file": v["rel"], "wp_title": v["title"], "caption": v["caption"]} for v in ATT.values() if v["rel"] not in used]
wcsv("_review/unused_media.csv", sorted(unused, key=lambda r: r["file"]))
print(f"textiles={len(textiles)} textile_images={len(timgs)} records={len(records)} images={len(manifest)} unused={len(unused)}")
