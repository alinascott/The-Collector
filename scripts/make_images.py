#!/usr/bin/env python3
"""Make web (1200px) and thumbnail (480px) JPEGs from the original media, and copy PDFs.
Originals are never modified. Re-running skips files that already exist."""
import csv, shutil
from pathlib import Path
from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parent.parent
WP = REPO.parent / "Art History Collection"
SIZES = {"web": 1200, "thumb": 480}

def derive(src, dest_pattern):
    for size, px in SIZES.items():
        out = REPO / dest_pattern.format(size=size)
        if out.exists(): continue
        out.parent.mkdir(parents=True, exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(src))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[-1]); im = bg
        im = im.convert("RGB"); im.thumbnail((px, px), Image.LANCZOS)
        im.save(out, "JPEG", quality=80 if size == "web" else 74, optimize=True, progressive=True)

n = 0
for r in csv.DictReader(open(REPO / "data/media_manifest.csv")):
    src = WP / r["source_file"]
    if r["repo_path"].endswith(".pdf"):
        out = REPO / r["repo_path"]
        if not out.exists(): out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, out)
    else:
        derive(src, r["repo_path"]); n += 1
for r in csv.DictReader(open(REPO / "photography/photographs.csv")):
    derive(REPO.parent / r["source_file"], r["image"].replace("/web/", "/{size}/")); n += 1
print("images processed:", n)
