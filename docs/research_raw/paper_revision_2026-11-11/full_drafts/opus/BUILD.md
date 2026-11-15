# Building the Opus draft

Everything here reads saved records only. No engine import, game, replay or model call.

Requirements: LuaLaTeX and latexmk (TeX Live; on this Mac `/Library/TeX/texbin`), and Python 3 with Matplotlib, NumPy and PyMuPDF. The provisioned interpreter used here is `/tmp/monopoly-astra-rewrite-venv/bin/python` (a local convenience, not a portable specification).

## Regenerate data, figures and tables

From `full_drafts/opus/tools/`, with a scratch cache directory:

```sh
export OPUS_CACHE=/path/to/scratch/cache   # any writable folder; ~100 MB pickle
PY=/tmp/monopoly-astra-rewrite-venv/bin/python
$PY corpus.py            # load 20 games, hash sources (6,989 decisions, 8,679 attempts, 50,918 events)
$PY offers.py            # rebuild 920 offers; compare with retained ledger
$PY pricing.py           # cash-for-deed prices
$PY bargaining.py        # census, contrasts, concessions, reason-code join
$PY extras.py            # capacity, standing, same-deed pairs
$PY sensitivity.py       # cohort, Grok-conflict and Opus cuts
$PY track.py             # tracker vs 3,246 snapshots (prints mismatches; expect none)
$PY groups.py            # completion episodes, exposure, rent
$PY debts.py             # all debt episodes
$PY estates.py           # standing before each first estate
$PY conditions.py        # refusals, prompt diff, tokens, cost
$PY requests_census.py   # request parameters
$PY build_new_quotes.py  # four new G2 quote definitions
$PY build_figures.py     # assets/*.pdf, *.png
$PY build_tables.py      # sections/gen_tables.tex, sections/gen_prompt.tex
```

Order matters for `pricing.py` → `bargaining.py` → `extras.py`/`sensitivity.py` → `build_tables.py`.

## Build the PDF

```sh
cd full_drafts/opus
./build.sh                                   # writes build/ and manuscript.pdf
$PY tools/verify_quotes.py                   # writes qa/quote_checks.json
```

`build.sh` fixes `SOURCE_DATE_EPOCH`. Generated TeX and figures are checked in, so a document-only build needs no Python.
