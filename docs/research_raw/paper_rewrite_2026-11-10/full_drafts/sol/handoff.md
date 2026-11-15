# Complete independent Sol manuscript

The entire paper is complete in `manuscript.tex` and `manuscript.pdf`. It is approximately 8,450 main source prose words by a simple TeX-stripping count, including the abstract but excluding quote macro bodies, tables, figure captions, bibliography and appendices. The final PDF has 25 pages, with the conclusion on page 20, references on pages 20–21 and appendices on pages 22–25.

I wrote all domains myself, used no subagents and did not read any other new author full draft. `initial_position.md` was written before the manuscript. I have not initiated cross-review, messaged finished peers, committed or pushed. All authored outputs are under this `full_drafts/sol/` folder. No controlled evaluation, game, model call, training, reference-policy run or synthetic verifier test was performed.

## Thesis and substantive choices

The paper is a behavioral study of bargaining for productive assets. Its connected sequence is acquisition, executable development, financial distress and creditor redistribution. Social exchanges make those dependencies explicit. Audit and replay support that account; they are not the paper's claimed general method contribution.

I promoted the complete current-author/recipient completion table, accompanied by net cash medians and a new response chart. Its behavioral interpretation is contested development under different terms, supported by specific rival-sensitive reasons. I do not claim a causal rival-completion effect or agreement-bias result. I put information and response defects before methods/results. Construction defaults remain failures of the configured system, while their allocation/encoding distinction changes the explanation. The finance section links all sixty eliminations to accessible funds, then connects rent and nonterminal inheritance without an effect-on-winning claim.

Seven main incidents have different roles: G13 insurance/omission, G18 withdrawal, G20 cash denial, G3 stock obstacle, G7 bargaining bluff, G19 correction with acceptance and G12 conflicting payable bankruptcy. G20 disclosure is an appendix incident. G13 retains the d250-before-d251 chronology, available Ventnor route, refusal-posture reading, probability error, information defect and later Short Line transfer. G12 is not grouped under a uniform mortgage-omission story. Q1–Q8 and broader questions A–C all have explicit discussion and appendix coverage.

Temporal evidence is compact and balanced: sustained target success, opportunity censoring, conflicting execution, public-capacity forecasts, revision and error recurrence. I moved reference-policy/fixture readiness to a short appendix and removed an unexecuted future-experiment appendix. There is no promise that rewriting resolves the critique's substantive experimental objections.

## Dissent and integration advice

1. I disagree with making audit methodology the central identity under the no-new-evaluations restriction. The existing validation supports specified historical facts, not general measurement gain. A behavioral paper can stand on its connected trajectories without claiming to have validated a reusable scientific method.
2. I disagree with retaining only two social cases. Seven distinct cases, including explicit correction and severe execution controls, substantiate the economic narrative better than two alarming anecdotes. They should be shortened through prose and quote selection, not by erasing mechanism diversity.
3. I would not lead with “own completion is insufficient for agreement.” The descriptive asymmetric cells with cash terms and explicit reasons are more meaningful, provided the integrated version does not convert their association into rationality or a causal effect. I omit unverified consistency across games/blocks/configurations.
4. I would omit the winner-grid opening and spending-ROI-looking scatter. Cohort context belongs in the appendix; zero receipts and inherited exposure are clearer in prose and counts. Creditor concentration is consequential but explicitly winner-conditioned.
5. I would resist rebuilding the introduction around eight purportedly completed capability studies. One economic question organizes this version. All eleven requested questions remain covered at their actual evidential level.

The descriptive nature of the central pattern remains a scientific limitation, not a wording defect. This draft makes a coherent complete observational contribution; it does not turn it into a controlled capability study or claim acceptance at a particular venue.

## Verification and provenance

`check_existing_data.py` re-tabulated retained offer cells/response styles, cash medians, 63 management windows, 103 spending units, sixty elimination rows and all five typed transfer ledgers. It loaded all 28 original quote fields, checked file/field hashes and JSON pointers and verified thirty exact spans. The quote-definition file is byte-identical to the old generated one. `data_checks.json` records exact inputs and results. This is a consistency/source check, not a newly performed engine audit.

Legal payment witnesses, construction reorderings, stock-lock checks, replay, memory/delivery reconstructions and full raw-response localization are explicitly inherited from prior work. I inspected the portable runner's canonicalizer source without executing it. No engine or verifier test was rerun. Source limitations and inherited reviewer identity are in `evidence_map.md`.

The document received a clean LuaLaTeX/latexmk build. `render_checks.json` records 25 rendered pages, no geometry violations, no undefined citations/references and zero overfull/underfull boxes. I directly reviewed all contact sheets and full-size pages 7, 10, 11, 23 and 25. `qa/render_review.md` records the layout corrections and review limits. This is not a claim that every page was read at full-resolution or every semantic claim independently rederived.

`literature_updates.md` distinguishes primary full-text/body checks from abstract-only checks, exact arXiv versions from proceedings, inherited unused bibliography entries and unavailable supplementary critique material. Recent additions include Agent Evaluation Reliability, Measurement-First Auditing and the accepted ACL 2026 MERIT paper. No comparator code was executed.

## Paths and build

- `manuscript.tex` is the entry point; it includes local `preamble.tex`, `transcript_quotes.tex`, `conduct.tex`, `temporal_discussion.tex` and `appendices.tex`.
- `references.bib` is a local copy with three added cited works and inspected proceedings URLs. `transcript_manifest.json` is a local copy of the original manifest.
- `assets/` contains both local PDF figures. The LaTeX build is self-contained within this folder apart from system TeX packages/fonts.
- Analysis inputs are read through `../../../paper_draft_2026-10-29/data/`. Original quote sources resolve from repository root using manifest paths. That dependency is documented rather than duplicated as canonical raw games.
- `requirements-document.txt` records the local Python document/plot environment. `.venv/` is a local build dependency directory, not paper evidence and need not enter a future release archive.

From this folder, build the PDF with:

```bash
bash build.sh
```

To reproduce retained-data consistency and plot generation, then document rendering, use the local environment or install `requirements-document.txt` in a new one:

```bash
.venv/bin/python check_existing_data.py
bash build.sh
.venv/bin/python inspect_pdf.py
```

Those commands do not import the game engine or call models. They require the retained original data for source checks; building the already-generated LaTeX/PDF assets does not.

I am stopping here pending the root's newly assigned all-four-draft cross-review phase.
