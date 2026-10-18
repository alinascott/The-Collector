# The Collector: Teaching With the F.A. Williams Collection

**Site:** https://alinascott.github.io/The-Collector/ (once GitHub Pages is turned on) · **Repository:** https://github.com/alinascott/The-Collector

> **Teaching note.** This collection is intended for educational use only. It may contain harmful language and images of inappropriate dress. It should be read carefully and in the context of the teaching materials. If you believe any material should not be included on this site, contact the owner by [opening an issue](https://github.com/alinascott/The-Collector/issues).

The sculptor Frederic Allen Williams (b. 1898) gave the University of Texas his entire collection by a Deed of Trust. Once it reached Austin it was split up. His Diné (Navajo) textiles went to the Texas Memorial Museum and later the Department of Art and Art History. His photographs and lantern slides went to the Harry Ransom Center.

This repository brings the two archives back together:

- **Woven into History** (2018), Alina Scott's public history site on the textiles and their paper records, rebuilt from its WordPress export.
- **Frederic Allen Williams Collection, Harry Ransom Center**: lantern slides and ephemera.

The site is static HTML served by GitHub Pages from the repository root. Every page is generated from the CSV files below.

## Three pathways

| Folder | What it holds | Data |
|---|---|---|
| `provenance/` | Chain of custody, the Deed of Trust announcement, 1969 accession record, catalog cards, binder scans, acquisition photographs; two essays | `records.csv`, `events.csv`, `records/*.pdf` |
| `textiles/` | 17 textiles with documentation photographs, details and in-person photographs; four context essays | `textiles.csv`, `textile_images.csv` |
| `photography/` | 46 Harry Ransom Center items: slides of Williams's sculpture, of Williams, of Taos and Red River, of Taos people, and lecture ephemera | `photographs.csv`, `group_introductions.csv` |

Plus `teaching/` (four lesson plans) and `data/crosswalk.csv`, which links items across the archives. Each link has a relationship (`depicts`, `documents`, `related`), a confidence level (`confirmed`, `probable`, `related`) and the evidence for it.

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
python3 scripts/build_site.py --withhold   # same, but withhold images flagged for community review
```

Once the CSVs have been edited by hand, don't re-run the two extract scripts, because they overwrite them. Run `build_site.py` only.

## Please read

- [PROTOCOLS.md](PROTOCOLS.md): cultural protocols and community review
- [RIGHTS.md](RIGHTS.md): permissions, licensing and takedown
- [CORRECTIONS.md](CORRECTIONS.md): corrections made in the rebuild and open questions

Compiled by Alina I. Scott, Ph.D.
