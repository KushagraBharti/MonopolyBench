# Astra independent complete revision

Start with `manuscript.pdf`, then `handoff.md`. This is one complete candidate paper, not the final integrated edition.

## Build

From this directory, use Python 3 with matplotlib, PyMuPDF and Pillow and a LuaLaTeX/latexmk installation:

```sh
python tools/analyze_records.py
python tools/build_assets.py
bash build.sh
python tools/verify_document.py
```

The first two commands read the existing records and generate owned analysis outputs/assets. They do not run gameplay, an engine, a model, replays or a baseline. `build.sh` fixes the source date and places intermediate TeX files in `build/`. Verification writes rendered pages, contact sheets, extracted text and results under `qa/`.

The scripts assume this directory remains in the repository structure. Original quote source files and retained population ledgers are dependencies; the manuscript package does not duplicate the entire saved-game archive. Source paths and hashes are in `data/source_hashes.json` and the three quote manifests. No source manuscript or canonical data is modified.
