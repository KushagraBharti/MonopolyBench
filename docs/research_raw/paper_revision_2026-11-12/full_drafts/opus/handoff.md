# Handoff: Opus independent draft, 12 November 2026

## Status

Complete and frozen pending the all-four cross-review. No collision: `full_drafts/opus/` did not exist when this task started. I did not open any other author's 12 November draft (`astra/`, `fable_5_2/` and `sol/` exist alongside this folder). No subagents, commits or pushes.

- `manuscript.pdf`: 29 pages, SHA-256 `22cdfdc4238ad5660a9d892f48dc27d2253562cadb41ba3f10b1d02e5d63b012`. Main text pp. 1–19, about 5,995 prose words by `qa/wordcount.py` (excludes tables, figures, quotation cards and source lines). Every page inspected in contact sheets; both figures and the page-6 and page-9 layouts inspected at higher resolution.
- Build: `bash build.sh` regenerates every number, table, figure and quotation insert from stored records, then the PDF (about 40 s). `qa/verify_document.py` passes: 42 displayed quotations found in the PDF text, 50 key numbers tied to `data/`, no LaTeX warnings, no unresolved references.
- All 72 `baseline_manifest.json` hashes unchanged. No tracked repository file changed.

## Title and thesis

"Before the Menu Changes: Prospective Statements and Applied Actions of LLM Agents in Twenty Monopoly Games." Where agents state before acting how an action changes their own or others' options, the action follows the statement, right or wrong (Grok's channel conflicts excepted). Finance leads: 14 of 16 debts needing released collateral were paid, with 13 explicit prospective texts, while both failures came from totals that omitted the released collateral. The swap/cash pattern is reported as an exploratory, composition-sensitive description whose cause is not identified.

## Charter items

| Requirement | Where |
|---|---|
| Full form × completion table, proposer strata, stage | Tables 3, 4, 7, 8 |
| Five seed blocks and justified uncertainty | §2.5, §4.4, Fig. 2, Tables 9–10 |
| 16 necessary / 14 paid vs 19 uses vs 188 | §3, Table 2, Fig. 1, Table 15 |
| Prospective text, channels, no cognition claims | §3.2–3.3, Incident 1 |
| Disjoint 61/74 population | §4.5, App. C |
| Grok required tool choice (source-verified) | §2.2, Table 1 |
| G18 survival motive | Incident 8 |
| Both replay modes; URL, commits, seeds, game map, entry point | App. A, Table 6 |
| Eight RQs and A–C | App. F, Table 16 |
| Eight incidents with exact quotes, channels, receipts, outcomes | §3–5, App. H, `data/quote_manifest.json` |

## Checked versus inherited

Checked from records in this draft: everything in `evidence_map.md` marked "Checked". Inherited: the offer ledger's post-trade reconstruction, the 61/74 codes, the three payment witnesses and G7 menu search, historical replay executions, the fourteen paired histories, cost and token accounting.

## Decisions for the human owner

1. **Byline and authorship.** The PDF carries no human byline ("Independent draft for coauthor review"). Appendix I discloses LLM drafting. The owner needs to supply authorship and the venue's AI-assistance statement.
2. **Publication of the analysis package.** The scripts and the ledgers they read sit in untracked folders (`paper_rewrite_2026-11-10/`, `paper_revision_2026-11-11/`, `paper_revision_2026-11-12/`). Appendix A says so. A checkpoint commit is needed before the repository URL fully supports reproduction.
3. **Human annotation.** The 16 first-decision texts and 74 coded rejections have only LLM readings, mine for the 16. I am an Opus-family model reading Opus texts among others. Human coding would be new measurement, so it is the owner's call.
4. **Format.** A nine-page venue version would need to move most incidents to the appendix. Table 5 gives each incident's level and could guide that choice.
5. **Environment.** The build uses `/tmp/monopoly-astra-rewrite-venv`, which may not survive a reboot. `requirements-manuscript.txt` from `paper_rewrite_2026-11-10/` lists the packages.

## Substantive dissent for cross-review

- The swap/cash contrast should not carry the title or the headline (`findings_and_limits.md`).
- "Refusal triggered by completion" is causal language; completion was not manipulated.
- 128/131 is a valid partition, not difficulty evidence. A reactive-policy score must not be printed unless one is actually run.
- I kept all eight incidents in the main text, each with a stated level. If cross-review compresses them, keep G20 payment, G15 and G19, and move the others intact to the appendix.

## Charter objections

None that I violated. One tension: eight incidents with cards, complete tables and 5,000–6,000 prose words produce a 19-page main text. That is a research draft, not a venue-length paper.
