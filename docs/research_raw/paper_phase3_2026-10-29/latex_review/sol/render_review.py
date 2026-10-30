"""Render an existing PDF and inventory pages without changing the source PDF."""

import argparse
import hashlib
import json
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("pdf", type=Path)
parser.add_argument("--tag", default="review")
args = parser.parse_args()
here = Path(__file__).resolve().parent
out = here / "renders" / args.tag / args.pdf.stem
out.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(args.pdf)
records = []
thumbs = []
for idx, page in enumerate(doc):
    png = out / f"page-{idx + 1:03}.png"
    page.get_pixmap(matrix=pymupdf.Matrix(1.25, 1.25), alpha=False).save(png)
    (out / f"page-{idx + 1:03}.txt").write_text(page.get_text(sort=True))
    spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
             for line in b["lines"] for s in line["spans"] if s["text"].strip()]
    # Text bboxes are unrotated even when /Rotate changes the rendered page.
    outside = []
    for span in spans:
        rect = pymupdf.Rect(span["bbox"]) * page.rotation_matrix
        if (rect.x0 < -0.5 or rect.y0 < -0.5 or rect.x1 > page.rect.width + 0.5
                or rect.y1 > page.rect.height + 0.5):
            outside.append(span["text"])
    records.append({"page": idx + 1, "size_pt": list(page.rect),
                    "span_count": len(spans), "outside_page_text": outside,
                    "image_count": len(page.get_images()),
                    "links": len(page.get_links()),
                    "smallest_text_pt": min((s["size"] for s in spans), default=None)})
    image = Image.open(png).convert("RGB")
    image.thumbnail((290, 370))
    tile = Image.new("RGB", (310, 405), "#d8d8d8")
    tile.paste(image, ((310 - image.width) // 2, 25))
    ImageDraw.Draw(tile).text((8, 5), f"{args.pdf.stem}: {idx + 1}", fill="black")
    thumbs.append(tile)

for offset in range(0, len(thumbs), 12):
    subset = thumbs[offset:offset + 12]
    sheet = Image.new("RGB", (310 * 4, 405 * ((len(subset) + 3) // 4)), "white")
    for i, tile in enumerate(subset):
        sheet.paste(tile, (310 * (i % 4), 405 * (i // 4)))
    sheet.save(out / f"contact-{offset + 1:03}-{offset + len(subset):03}.png")

result = {"source": str(args.pdf.resolve()),
          "sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
          "page_count": len(doc), "pages": records}
(out / "render_inventory.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"out": str(out), "pages": len(doc),
                  "outside_page_text": sum(len(r["outside_page_text"]) for r in records)}))
