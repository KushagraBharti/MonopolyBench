# Verification record (Opus, 14 November 2026)

## Scope compliance

**Nothing new was executed:**
- no game, engine execution, replay, policy rollout or verifier search;
- no baseline, synthetic state or provider/model call;
- no saved-request probe and no subagent.

**Nothing outside this folder was changed:**
- no manuscript, prompt, engine or canonical-game edit;
- no commit or push.

I wrote only under `reviews/opus/`. Scripts in `checks/` read stored JSON records and board data and do arithmetic. They never import or run the engine. Board values come from `contracts/data/board.json`. I did not open any peer review folder before finishing the independent outputs.

## Pin

| | Before | After |
|---|---|---|
| Checked at | 2026-11-14T18:55:35 (`pin_check_before.txt`) | 2026-11-14T19:21:53 (`pin_check_after.txt`) |
| Manifest SHA-256 | `04d0a0d3ac02a337ebfc4c7426c184f85862e53d60984e8beaba724ab29e5460` | identical |
| Entries | 84/84 match | 84/84 match |
| PDF SHA-256 | `5ab7b1c4…2518e52` | identical |

## Checks performed this round

| Check | Method | Result |
|---|---|---|
| Two failures, both channels, first actions | `dec.py`: original `decisions.jsonl` raw responses for G12 d190 and G17 d234 | Both calls are `declare_bankruptcy`. Applied notes are exactly as printed. Sol's reasoning.summary adds "bankruptcy might transfer property anyway". Gemini's reasoning.text ends "start thinking of additional options". |
| All 16 initial fields and provenance | `dump16.py` and a string comparison against `necessary_texts.tex` | 16/16 identical after LaTeX normalisation. Opus refused attempts carry no text. Channel split 11 notes / 5 Opus provider texts. |
| Both channels for all 16 | `dump16.json` | Transient U0-bounded inventories in success provider texts: G5, G8, G13, G18 d309, G18 d313. |
| U\*, U0, C+M0 for all 188 entries | `partition.py`, from entry prompts and board values | 0 U\* mismatches against the stored `upper_bound`. Partition 62/53/16; paid 62/52/14. Bound coverage 132/56. |
| Failure sums = U0 | `partition.json` | G12 d190: 408 = U0. G17 d234: 530 = U0. |
| Middle-category released-use episodes | `partition.py` plus hand derivation from holdings and bank stock | No-release routes exist for G3 d228, d356, d461, d482 and G18 d428. Derived by hand, not engine-validated. |
| Six above-bound financing starts and G12 d249 | `six.py`; content/call conflict scan across all 188 first decisions | 5/6 are Grok, each with content naming `declare_bankruptcy`. G9 d194 and G20 d273 have notes that say declare. G12 d249's note inside its declare call says bankruptcy is wrong. Seven first-decision conflicts overall, all Grok. |
| Carried notes | `your_private_thoughts_last_10` in all 16 entry prompts | Reserve figures $130 and $30 confirmed. Counterexamples: G13, G20 d327, G1, G5. Opus had 0 notes in G6, G11, G17 d254 and G20 d291. |
| Fallback and menu semantics | Read `decision_resolver.py`, `llm_runner.py` and `engine.py` at HEAD; `git diff d6808534..HEAD` is empty for engine and arena | The resolver fallback declares only when no sale or mortgage is legal. The `llm_runner` duplicate is dead code. Auto-payment confirmed. Hotel sale needs ≥4 bank houses. Sell-plan validation is end-state only. No interest on inherited deeds; buildings pass intact to a player creditor. |
| Hotel/bank stock in all 188 entries | entry prompts | 26 entries hold hotels. Among the sixteen, only G20 d327 (bank 15). |
| Joint generation | Argument order in stored tool-call JSON | The note follows the function in all note cases. It follows the action's arguments in 8/9 of the necessity sale/mortgage cases, and in Sol 81/81, Grok 36/40 and Gemini 56/77 across corpus liquidation calls. |
| Denominators | Counts | 338 liquidation decisions; 58 inside the 16 episodes; 6,989 decisions in the corpus. Episodes by model: Opus 58, Sol 42, Grok 38, Gemini 50. |
| Statistics | Exact computations | Clopper–Pearson 14/16: 61.7–98.4%; 128/131: 93.5–99.5%. Fisher 2/16 vs 1/115: p = 0.039; 2/16 vs 0/115: p = 0.014. Neither is valid as inference (post-hoc partition). |
| Costs | `usage_attempts.jsonl`, known-cost attempts | Mean USD per priced attempt: Opus 0.0287, Sol 0.0094, Gemini 0.0110, Grok 0.0328. Total 141.71. |
| Paper length, references, layout, repository | `extracted.txt`, `.bbl` files, page PNGs, git | About 8,100 words to References, which begin on p.12. 12 references, against 16 on 11 Nov. p.6 has a blank right-column remainder. origin/main is 2026-10-29; the package is untracked. |
| Bargaining numbers | My 12 Nov independent script and output (`final_review/opus/recompute_bargaining_output.json`); pinned data unchanged | Reproduced. Grok cash-bid within-recipient gap is −0.2. |
| Literature | Web fetch of primary pages (see `literature_matrix.md`) | Depth recorded per source. Content passes through a summariser. |

## Inherited, not rechecked this round

- **Historical engine audit witnesses.** I read the printed sequences; nothing was re-executed.
- **Replay-report pass results.**
- **The 61/74 semantic coding.** Two LLM readers; not human.
- **The 139-conflict census.**
- **Incident continuations.** I re-traced them on 12 November, not this round.
- **Gemini's estimate of $1,414 for Sol's liquidation resources in G20.** Taken from the paper.
- **Payment and elimination labels per episode.** Ledger outcomes; the first decisions were re-read.

## Limitations

- **My coding is LLM coding.** The classification of the sixteen texts into dependency / ordered / inclusive / omission is my (Opus) reading. It is not human validation and should be coded independently by humans.
- **The "16/16 by construction" result is code reasoning.** It assumes the code at HEAD equals the code at run time; the engine is unchanged since `d6808534`. Hand-derived routes assume the menu semantics I read. Neither is an engine-validated witness.
- **Generation order is inferred.** It comes from the serialised argument order in stored provider responses. Providers may re-serialise structured arguments: Sol's consistent order looks schema-driven. The function-before-arguments ordering is structural.
- **Provider reasoning fields may be condensed.** The `reasoning.summary` and `reasoning.text` fields are provider-surfaced and possibly summarised. Absence of a quantity in them is not evidence of absence from internal computation.
- **Two rules points are not fully re-verified.** The official rulebook PDF could not be text-extracted. The building-transfer rule on bankruptcy to a player is recalled, not re-verified. The 10% rule is confirmed via the Hasbro FAQ.
- **Some comparator details remain unverified:**
  - MafiaScope's 672 games;
  - PlanBench's ~26,000 prompts;
  - the Menu paper's same-candidate ablation;
  - the Li et al. venue;
  - VB2's full leaderboard;
  - Project Vend.
