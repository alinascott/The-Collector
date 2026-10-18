#!/usr/bin/env python3
"""Build photography/photographs.csv from the HRC captions file plus cataloger notes.

The captions file (_source/hrc/image-titles-and-captions.rtf) is the source for titles
and HRC series. CATALOGER below holds what was added while checking each image:
transcribed slide labels, supplied titles for uncaptioned items, and flags.
"""
import csv, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HRC = Path(REPO.parent / "Harry Ransom Center ")

def rtf_text(p):
    s = p.read_bytes().decode("latin-1")
    s = re.sub(r"\\'([0-9a-f]{2})", lambda m: bytes.fromhex(m.group(1)).decode("cp1252"), s)
    s = re.sub(r"\{\\\*?\\(fonttbl|colortbl|expandedcolortbl)[^{}]*(\{[^{}]*\}[^{}]*)*\}", "", s)
    s = re.sub(r'HYPERLINK "[^"]*"', "", s)
    s = re.sub(r"\\\n", "\n", s)
    s = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", s).replace("{", "").replace("}", "").replace("\\*", "")
    return s

FOLDERS = {"Ephemera": "ephemera", "Slides of Williams’ work": "williams-work",
           "Lantern Slides of Towns": "towns", "Slides of Williams": "williams", "Slides of Indigenous People": "taos-people"}

def parse():
    text = rtf_text(REPO / "_source/hrc/image-titles-and-captions.rtf")
    text = text.split("Takedown Notice")[0]
    out, intros, folder, pending = {}, {}, None, None
    for line in [l.strip() for l in text.splitlines()]:
        if not line or line in ("‘", "——"): continue
        m = re.match(r"Folder:\s*(?:The )?(.+)", line)
        if m:
            name = m.group(1).strip().replace("Magic Lantern", "Slides of Williams’ work")
            folder = FOLDERS.get(name, name); pending = None; continue
        if line.startswith("Introduction by"):
            intros[folder] = line.split(":", 1)[1].strip(); continue
        m = re.match(r"(img_\d+(?:-\w+)?)(?:\.webp)?$", line)
        if m:
            pending = m.group(1); out[pending] = {"folder": folder, "caption": ""}; continue
        if pending and not out[pending]["caption"]:
            out[pending]["caption"] = line
    return out, intros

def split_caption(c):
    """'“Title” – Frederic Allen Williams Lantern Slide Collection ...: series I, sub-series A'"""
    c = c.replace("“", '"').replace("”", '"').replace("’", "'")
    m = re.search(r"Frederic Allen Williams (Lantern Slide|Photograph) Collection.*?:\s*series\s+([IVX]+),\s*(sub-series\s+\w+|container\s+\d+)", c)
    coll = series = sub = ""
    if m:
        coll = f"Frederic Allen Williams {m.group(1)} Collection"; series = m.group(2); sub = m.group(3)
        c = c[:m.start()]
    c = c.replace('– "The Arrowmaker" –', "–")      # paste artifact repeated in the captions file
    title = c.strip(" –-\u2013\"").replace('"', "").strip()
    title = re.sub(r"\s*–\s*$", "", title)
    return title, coll, series, sub

# Added while viewing each image. inscription = handwritten/typed label on the slide mount.
CATALOGER = {
 # Ephemera (series III, container 57) -- uncaptioned; titles supplied from the printed text
 "img_4849": dict(title='[Reprint from "International Who\'s Who," January 1948]', date="1948", type="Printed biography (reprint)",
   desc="Biographical entry for Frederic Allen Williams, sculptor, with his studio address at 58 West 57th Street, New York."),
 "img_4850-2": dict(title='[Brochure cover: "Frederic Allen Williams, Tenth Year of Lectures on the Arts of the Americas, Illustrated in Color"]', type="Lecture brochure",
   desc="Cover of a lecture brochure with a portrait of Williams beside one of his sculptures. 58 West 57th Street, New York."),
 "img_4851": dict(title='[Brochure page: "Solidarity of the Americas"]', type="Lecture brochure",
   desc="Brochure text presenting Williams's lectures on pre-Columbian and Mexican art as cultural diplomacy, with an endorsement by Leon I. Helguera."),
 "img_4853": dict(title="[Brochure page: lecture descriptions and press notices]", type="Lecture brochure",
   desc="Notes that the lectures were illustrated with 3¼ × 4 inch Kodachrome lantern slides, with press quotations about Williams's work."),
 "img_4854-2": dict(title="[Brochure spread: the Shrine of the Americas]", type="Lecture brochure",
   desc="Two-page text on the Shrine of the Americas, with a list of supporters."),
 "img_4872": dict(title="[Brochure page: the Shrine of the Americas and Williams's Kodachrome slide collection]", type="Lecture brochure",
   desc="States that the Shrine of the Americas was copyrighted in 1939, that Williams had kept a studio in New York since 1922, and that he had built a collection of 3¼ × 4 inch Kodachrome slides of western scenes."),
 "img_4879": dict(title="[Williams on horseback in a parade]", type="Photograph",
   desc="Williams in a western hat on a dark horse, with flags behind him."),
 # Slides of Williams's work (series I, sub-series A)
 "img_5192": dict(insc="", desc="Bronze-toned sculpture of a seated figure shaping an arrow. Williams's best-known work. The same sculpture appears in the 1940 studio portraits."),
 "img_5188": dict(insc="Frederic Allen Williams – Deer Dancer", desc="Painted relief of a deer dancer."),
 "img_5196": dict(insc="Frederic Allen Williams sculptor – Maid of Taos – Taos 1931", desc="Standing figure in a shawl, photographed against black."),
 "img_5198": dict(insc="Frederic Allen Williams – Poly. Sc. – Buffalo Dancer", desc="Two views of a polychrome sculpture of a buffalo dancer."),
 "img_5201": dict(insc="Frederic Allen Williams – Poly. Sc. – Taos Girl and Deer", desc="Two views of a polychrome sculpture of a girl with a deer."),
 "img_5202": dict(insc="F.A.W. sculpture – terra cotta – Maid of Taos glazed", desc="Glazed terra cotta figure with a ram, arranged among flowers."),
 "img_5206": dict(insc="F.A. Williams – Madonna – porcelain – azaleas", desc="Porcelain Madonna and child among azaleas."),
 "img_5207": dict(insc="F.A. Williams – Sculptor – Shrine of Americas – Plains – Andes – Mayas – Chimu – Jungles",
   desc="Five figures from the Shrine of the Americas.", note="The captions file reads 'Chinsu'; the slide label reads 'Chimu' (Chimú). Title uses the slide label."),
 "img_5209": dict(insc="F.A. Williams – Aztec turkeys – mask – Garden Garniture", desc="Mask flanked by two turkey sculptures, set against flowers."),
 "img_5210": dict(insc="F.A. Williams – Sculptor – Shrine of Americas – West Indies – Pueblo – Alaskan – Aztec – Eskimo",
   desc="Five figures from the Shrine of the Americas.", note="The captions file reads 'Alacken'; the slide label appears to read 'Alaskan'. Please confirm."),
 # Slides of Williams (series I, sub-series F; one series III)
 "img_5129": dict(desc="Black-and-white photograph of a man with a horse beside a mountain stream.", note="Filed with the slides of Williams, but the HRC series (III, sub-series A) is the scenes series."),
 "img_5186": dict(insc="Frederic Allen Williams – Taos 1929 – modeling 'The Sioux Worshipper'", date="1929", desc="Williams at work on a clay sundial figure."),
 "img_5182": dict(date="1940", desc="Williams seated in his New York studio among his sculptures and collection. He sits on Chief Blanket 2148-606; the composite sampler 2148-588 is the pillow beside him; The Arrowmaker sculpture is at his side.", related="2148-606; 2148-588"),
 "img_5178": dict(date="1940", desc="A second exposure of the 1940 studio portrait, with the same arrangement of textiles and sculpture.", related="2148-606; 2148-588"),
 "img_5213": dict(title="[Williams with a horse at a log fence]", desc="Color slide of Williams leading a saddled horse beside a split-log fence."),
 "img_5219": dict(title="[Portrait of Williams in autumn]", desc="Color portrait of Williams in a suede jacket in front of autumn leaves."),
 "img_5221": dict(desc="Williams in a blue shirt and western hat, holding a pale horse by the bridle.",
   note="The captions file reads 'Hoffmann-palaniun'; the horse shown suggests 'palomino'. Please check the slide label."),
 "img_5223": dict(insc="F.A.W. Sept. 1945 – Indian", date="1945", desc="Two views of Williams in a feather headdress and fringed regalia.", review="Williams in Native regalia (redface/'playing Indian'); needs interpretive framing."),
 "img_5226": dict(insc="Indian 1946", date="1946", desc="Two close views of Williams in a feather headdress.", review="Williams in Native regalia (redface/'playing Indian'); needs interpretive framing."),
 "img_5227": dict(insc="F.A.W. Sept. 1946 – Eskimo", date="1946", desc="Two views of Williams in a fur parka.", review="Williams in Arctic Indigenous dress; needs interpretive framing."),
 "img_5229": dict(title="[Williams in an embroidered western shirt with a saddle]", desc="Color slide of Williams in a red embroidered shirt and hat beside a tooled saddle, with his reflection in a mirror."),
 "img_5231": dict(insc="Nov. 14 1940 – Mex. costume – by Voss", date="1940-11-14", desc="Williams in a sombrero and striped serape, smoking.", review="Williams in costume as 'Mexican'; needs interpretive framing."),
 # Lantern slides of towns (series III, sub-series A)
 "img_5143": dict(insc="Taos – North Pueblo", desc="The multi-story North House at Taos Pueblo.", review="Taos Pueblo"),
 "img_5141": dict(insc="Taos", desc="Taos Pueblo buildings with Taos Mountain behind.", review="Taos Pueblo"),
 "img_5142": dict(insc="Taos from top of pueblo", desc="View across Taos Pueblo from a rooftop.", review="Taos Pueblo"),
 "img_5161": dict(insc="Red River City", desc="Wooden false-front buildings in the mining town of Red River, New Mexico."),
 "img_5101": dict(insc="Taos Plaza 1934", date="1934", desc="Taos plaza with horses and a wagon in front of adobe storefronts."),
 "img_5165": dict(insc="Taos – Kit Carson House", desc="The portal of the Kit Carson House in Taos."),
 # Slides of Indigenous people (series III, sub-series A)
 "img_5164": dict(title="[Two women at Taos Pueblo]", insc="Taos", desc="Two women in shawls standing in front of adobe buildings.", review="Taos Pueblo people"),
 "img_5100-edit": dict(insc="Taos – autumn", desc="Woman in a white shawl beneath hanging chile ristras.", review="Taos Pueblo people"),
 "img_5153": dict(insc="Taos – in Bert Phillips patio", desc="Woman in a shawl holding a young child.", review="Taos Pueblo people",
   note="The captions file gives this as 'in Bert Phillip's studio 1934', but the slide label reads 'in Bert Phillips patio'. The captions for img_5153 and img_5154 appear to be swapped."),
 "img_5098-edit": dict(title="[Woman baking at an horno]", desc="Woman tending an outdoor adobe oven (horno).", review="Taos Pueblo people"),
 "img_5108": dict(title="[Portrait of a man in profile with an eagle feather]", desc="Profile portrait of an older man with braids and a feather.", review="Indigenous person; identity unknown",
   note="No caption in the captions file and no visible label on the slide."),
 "img_5139": dict(insc="Taos – Hoop dance", desc="Dancers with hoops, photographed outdoors.", review="Dance; check whether it may be shown publicly"),
 "img_5132": dict(insc="Taos – Manuel", desc="Man wrapped in a white blanket standing against an adobe wall.", review="Taos Pueblo people"),
 "img_5110": dict(title="[Portrait of a man in a feather headdress]", desc="Seated man in a feather headdress and beaded clothing.", review="Indigenous person; identity unknown"),
 "img_5151": dict(insc="Taos – in Bert Phillips patio", desc="Woman in a shawl seated in a garden, touching a stone sculpture.", review="Taos Pueblo people"),
 "img_5107": dict(insc="Taos – Albertina (?)", desc="Woman seated on the ground in front of a field.", review="Taos Pueblo people",
   note="The captions file reads 'alberto's wife'; the slide label may read 'Albertina'. Please check."),
 "img_5154": dict(insc="Taos – in Bert Phillips studio 1934", date="1934", desc="Young woman in a shawl seated with a small child on a striped blanket.", review="Taos Pueblo people",
   note="The captions file gives this as 'in Bert Phillips Studio' (no date); the slide label adds 1934. See also img_5153."),
}
SWAP_FIX = {"img_5153": "in Bert Phillips' patio", "img_5154": "in Bert Phillips' studio, 1934",
            "img_5207": "Shrine of the Americas: Plains – Andes – Mayas – Chimú – Jungles",
            "img_5107": "Alberto's wife"}
GROUP_TITLES = {"ephemera": "Ephemera", "williams-work": "Slides of Williams's work", "towns": "Lantern slides of towns",
                "williams": "Slides of Williams", "taos-people": "Slides of Indigenous people"}

def main():
    caps, intros = parse()
    files = {p.stem: p for p in HRC.rglob("*.webp")}
    rows = []
    for stem, p in sorted(files.items(), key=lambda kv: kv[0]):
        c = caps.get(stem, {"folder": FOLDERS.get(p.parent.name.strip()), "caption": ""})
        title, coll, series, sub = split_caption(c["caption"])
        cat = CATALOGER.get(stem, {})
        title_source = "HRC captions file"
        if stem in SWAP_FIX: title, title_source = SWAP_FIX[stem], "HRC captions file, corrected from slide label"
        if not title and cat.get("title"): title, title_source = cat["title"], "supplied by cataloger"
        if not title: title, title_source = "[Untitled]", "none"
        if not coll:
            coll = "Frederic Allen Williams Lantern Slide Collection" if c["folder"] != "ephemera" else "Frederic Allen Williams Photograph Collection"
        hid = "HRC-" + stem.replace("img_", "")
        rows.append({
            "id": hid, "title": title, "title_source": title_source,
            "group": GROUP_TITLES.get(c["folder"], ""), "group_slug": c["folder"],
            "object_type": cat.get("type", "Lantern slide"),
            "date": cat.get("date", ""), "slide_inscription": cat.get("insc", ""),
            "description": cat.get("desc", ""),
            "repository": "Harry Ransom Center, The University of Texas at Austin",
            "collection": coll, "series": series, "subseries_or_container": sub,
            "caption_as_received": c["caption"].replace("\u2013", "–"),
            "related_textiles": cat.get("related", ""),
            "cultural_review": cat.get("review", ""), "notes": cat.get("note", ""),
            "image": f"photography/images/web/{hid}.jpg", "source_file": str(p.relative_to(REPO.parent)),
        })
    order = list(GROUP_TITLES)
    rows.sort(key=lambda r: (order.index(r["group_slug"]) if r["group_slug"] in order else 9, r["id"]))
    out = REPO / "photography/photographs.csv"; out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(REPO / "photography/group_introductions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["group_slug", "group", "introduction", "author"])
        for k, v in intros.items(): w.writerow([k, GROUP_TITLES.get(k, k), v, "Jesse Ritner, PhD"])
    missing = [s for s in caps if s not in files]
    print(f"photographs={len(rows)} intros={len(intros)} caption-without-file={missing}")

main()
