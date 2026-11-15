"""Render the pinned integrated PDF to page PNGs and plain text (document-only).

Reads the PDF read-only; writes only under the reviewer's own directory.
Usage: python render_pinned_pdf.py <pdf> <outdir> <expected_sha256>
"""
import hashlib
import json
import sys
from pathlib import Path

import pymupdf

pdf, outdir, expected = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
if digest != expected:
    raise SystemExit(f"PIN MISMATCH {digest}")
doc = pymupdf.open(pdf)
outdir.mkdir(parents=True, exist_ok=True)
pages = []
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1.55, 1.55))
    pix.save(outdir / f"page_{i:02d}.png")
    text = page.get_text()
    (outdir / f"page_{i:02d}.txt").write_text(text)
    pages.append({"page": i, "chars": len(text), "images": len(page.get_images())})
(outdir / "render_index.json").write_text(
    json.dumps({"pdf_sha256": digest, "page_count": len(doc), "pages": pages}, indent=1)
)
print(digest, len(doc))
