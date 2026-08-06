# Prism import — 2026-07-28

Source project:
`https://prism.openai.com/?u=9013222e-442a-43cd-937f-834fdc5771b4&pg=1&m=MonopolyBench.tex`

The complete 134-entry Prism export is preserved as
`MonopolyBench-prism-export.zip`. The root text sources and IEEE support files
are also extracted here for inspection.

## Canonical-file decisions

- `MonopolyBench.tex` was newer than the local paper draft. It was copied to
  the canonical `monopolybench_ieee_draft_v0_1.tex`.
- The Prism `research_direction.md` is text-equivalent to the existing
  `docs/archive/research_direction_legacy.md`, so it did not replace the newer,
  concise canonical root document.
- The Prism `full_summary.md` is nearly identical to `docs/full_summary.md` but
  lacks the local status/canonicality notice, so it did not replace that file.
- The Prism `README.md` is retained here as source material. It contains useful
  historical artifact documentation, but it also contains duplicated citation
  text and older setup language, so it did not replace the current root README.
- The two analysis directories inside the export are historical reduced
  exports. They did not replace the newer canonical packages under
  `saved_games/`.

See `manifest.json` for hashes and the exact import mapping.
