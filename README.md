# The Collector: Teaching With the F.A. Williams Collection

**Site:** https://alinascott.github.io/The-Collector/ (once GitHub Pages is turned on) · **Repository:** https://github.com/alinascott/The-Collector

> **Teaching note.** This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by [opening an issue](https://github.com/alinascott/The-Collector/issues).

The sculptor Frederic Allen Williams (b. 1898) gave the University of Texas his entire collection by a Deed of Trust. Once it reached Austin it was split up. His Diné (Navajo) textiles went to the Texas Memorial Museum and later the Department of Art and Art History. His photographs and lantern slides went to the Harry Ransom Center.

This repository brings the two archives back together:

- **Woven into History** (2018), Alina Scott's public history site on the textiles and their paper records, rebuilt from its WordPress export.
- **Frederic Allen Williams Collection, Harry Ransom Center**: lantern slides and ephemera.

The site is static HTML served by GitHub Pages from the repository root. Every page is generated from the CSV files below.

## Entrance

`index.html` is the way in. It opens on a black screen with the question *What have you learned about Indigenous communities… and how?* for three seconds, then fades into the Table. A click or key press skips it, and it shows once per browser session. A **View** toggle in the top right switches between two entrances: **Table** (the default) and **Filmstrip** (`filmstrip.html`, dated items in order from the 1860s to the 1969 accession). A third view, **Pairs**, is set aside for now; build it with `python3 scripts/build_entrance_views.py --pairs`. The teaching note is left off the entrance views and appears on every page inside the site.

The Table is a matte table with three archival document boxes, one for each pathway: Provenance (32 paper records), Textiles (16 textiles) and Photography (28 photographs). The boxes carry no labels. Hovering over a box opens its lid, and the first prints rise out of it. Choosing a box spreads its prints across the table, and choosing a print opens that item's page. "All three stacks" or the Escape key goes back. A stack can be linked to directly as `index.html#provenance`, `#textiles` or `#photography`. The former front page is now `home.html`, and the site name in every header links to it. Images flagged for community review, and sampler 2148-589, are left out of the entrance but keep their own pages.

The table is built by `scripts/build_entrances.py`, which runs after `build_site.py`. Earlier table surfaces, redrawn blankets 1633-76 and 2148-606, are kept in `scripts/saddle_svg.py` and `scripts/blanket_svg.py`. The styles are in `assets/entrances.css` and `assets/views.css`.

## Three pathways

| Folder | What it holds | Data |
|---|---|---|
| `provenance/` | Chain of custody, the Deed of Trust announcement, 1969 accession record, catalog cards, binder scans, acquisition photographs; two essays | `records.csv`, `events.csv`, `records/*.pdf` |
| `textiles/` | 17 textiles with documentation photographs, details and in-person photographs; four context essays | `textiles.csv`, `textile_images.csv` |
| `photography/` | 46 Harry Ransom Center items: slides of Williams's sculpture, of Williams, of Taos and Red River, of Taos people, and lecture ephemera | `photographs.csv`, `group_introductions.csv` |

Plus `teaching/` (the teacher guide and four lesson plans; edit the guide in `_source/pages/teacher-guide.html`) and `data/crosswalk.csv`, which links items across the archives. Each link has a relationship (`depicts`, `documents`, `related`), a confidence level (`confirmed`, `probable`, `related`) and the evidence for it.

## Identifiers

- Textiles use their University of Texas accession numbers (`2148-606`). All are from the Frederic Allen Williams Collection. The prefix is the accession group: 2148 is the Texas Memorial Museum accession of the collection (September 1969), the accession record names 1654 for further Williams items, and 1074 and 1633 hold the rest.
- Harry Ransom Center items use `HRC-` plus the image file number (`HRC-5182`). Titles come from the captions file; titles in [square brackets] were supplied where no caption existed.
- Paper record groups use `PR-01` to `PR-08`.

## Rebuilding

The scripts expect the original media beside this folder (in `Art History Collection/` and `Harry Ransom Center /`). The originals are not uploaded to GitHub. You only need them to rebuild the images.

```
python3 scripts/extract_wordpress.py   # WordPress XML -> textiles/records CSVs + essay fragments
python3 scripts/hrc_photographs.py     # HRC captions + cataloger notes -> photographs.csv
python3 scripts/make_images.py         # 1200px web and 480px thumbnail JPEGs, PDFs
python3 scripts/build_site.py          # render the HTML
python3 scripts/build_entrances.py     # the entrance table (index.html)
python3 scripts/build_entrance_views.py   # Filmstrip and the View toggle
python3 scripts/build_site.py --withhold   # same, but withhold images flagged for community review
```

Once the CSVs have been edited by hand, don't re-run the two extract scripts, because they overwrite them. Run `build_site.py` only.

## Please read

- [PROTOCOLS.md](PROTOCOLS.md): cultural protocols and community review
- [RIGHTS.md](RIGHTS.md): permissions, licensing and takedown
- [CORRECTIONS.md](CORRECTIONS.md): corrections made in the rebuild and open questions

Compiled by Alina I. Scott, Ph.D.
