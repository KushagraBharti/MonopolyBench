# Residual of the 34/42 first-management deployment statistic (existing-log analysis, Opus phase 3)

**Question.** The phase-2 ledger (R05) reports two figures for trade-completed groups:
- 34 of the 42 buildable at entry to the owner's first management turn are built in that turn;
- the per-model figures are Sol 14/15, Gemini/Argon 13/13, Opus 5/7 and Grok 2/7.

What happened in the eight entry-buildable groups that were *not* built?

**Method.** `scripts/deployment_residuals.py` produced `deployment_residuals.json`. It is mechanical, read-only and makes no provider calls. Inputs:
- the phase-1 group episodes (`paper_phase1_2026-10-28/sol/group_episodes.jsonl`), filtered to trade route, entry-legal and not built;
- Sol's engine-default list (`build_recovery_audit.json`, `defaults`);
- Sol's received content/tool-name conflict list (`received_name_conflict_audit.json`, `all_named_conflicts`);
- the owner's resolved decisions in that turn from canonical `run/decisions.jsonl`.

The script asserts 63 trade groups and 42 entry-buildable groups. Input hashes are in the JSON.

I then read the turn-ending decision's assistant content for all eight cases in the original `decisions.jsonl` attempts.

## Result (8 of 8 accounted for)

| Game | Owner | Group | What ends the turn without building that group | Class |
|---|---|---|---|---|
| G2 | Opus | Light blue | d075 END is an **engine default** after a rejected build plan | Execution (default) |
| G18 | Opus | Brown | d084 END is an **engine default** after a rejected build plan | Execution (default) |
| G4 | Sol | Pink | d136 END is an **engine default** after a rejected build plan | Execution (default) |
| G8 | Grok | Orange | d163: the received tool call is `end_turn`, but the content calls `build_houses_or_hotel` (1-1-1 orange; "Orange is live. One house each…") | Received-call conflict against a build request |
| G12 | Grok | Pink | d166: the received `end_turn` conflicts with content calling `build_houses_or_hotel` (3-2-2 pinks; "Pinks are built") | Received-call conflict against a build request |
| G20 | Grok | Red | d097: the received `end_turn` conflicts with content calling `mortgage_property` as the first step of a stated mortgage-then-build plan for the reds | Received-call conflict against a financing-to-build request |
| G1 | Grok | Yellow | d119 `end_turn`, no conflict on that decision. The content's private thought says "Do NOT build this turn … houses collect $0 and only shrink the buffer". An earlier decision in the same turn (d112, the reject→accept name flip) is a conflict | Explicit chosen hold |
| G15 | Grok | Brown | d129 `end_turn`, no conflict on that decision. Private thought: "Any build or cash trade makes NY a bankruptcy. Do not house browns yet". An earlier jail decision in the turn has a conflict | Explicit chosen hold |

**Summary.**
- Of the eight residual groups, three end in an engine default after a rejected build plan (Opus 2, Sol 1).
- Three end in a received END whose content requests building or build financing (all Grok, under `tool_choice="required"`).
- Two are explicit chosen holds with recorded reserve rationales (both Grok).

## What this changes

- **The conditional per-model rates must not be read as willingness to build.** Every non-build behind Sol's 14/15 and Opus's 5/7 is an engine default. Three of Grok's five non-builds behind 2/7 are received END calls against build-requesting content.
- Within this conditional population, the only recorded *chosen* non-deployments are two Grok holds with explicit liquidity reasoning. Whether those holds were wise is not assessed.
- **For figures.** Any panel showing 14/15, 13/13, 5/7 and 2/7 (for example Astra's F4, right panel) should annotate the residual by class (default / received-call conflict / chosen hold) or sit beside this table. This makes concrete Astra's own requirement that "F4 must stay paired with resolution-policy qualification".

## Limits

- The classification covers only the owner's resolved decisions in that turn. It does not assess the later trajectory or whether building would have helped.
- Received-call conflicts are not localized to the model, provider or gateway (R23).
- Content is a recorded channel, not privileged intent. It is quoted here only to establish the disagreement with the applied action.
- The engine defaults follow the recovery policy: Opus's refusal → action-only retry; Sol's two-attempt corrective path. Phase-2 R06 shows that all 61 Opus default plans execute after reordering. Most of Sol's default plans were unaffordable (Astra reconciliation).
- This is a post hoc analysis of an already-inspected cohort.

## Follow-up checks (self-answered; Sol's thread had finished, so the questions could not be delivered)

- **G4 d136 (Sol default).** Per `core_review/sol/build_recovery_audit.json` → `defaults`:
  - Attempt 0 submits 3-3-3 pinks from $540 cash. That is uneven and also unaffordable after interleaving ("Insufficient cash to build").
  - Attempt 1 is also "Insufficient cash to build".
  - Describe it as **"a default after unaffordable plans"**, not as discarded affordable development. Smaller construction was legal. The Opus G2 d075 and G18 d084 defaults belong to R06's 61 plans that execute after reordering.
- **The three Grok conflicts** (`received_name_conflict_audit.json` → `all_named_conflicts`), all `content_form = named_json_call`, response condition `standard`:
  - **G8 d163.** Content: `build_houses_or_hotel` 1-1-1 orange. Received: `end_turn`. The received private note says "1-1-1 is down, cash $172": the received END's own note describes a build that was never applied (a phantom-build note in the received arguments).
  - **G12 d166.** Content: `build_houses_or_hotel` 3-2-2 pinks, which as written would itself have failed the per-entry even-building check. Received: `end_turn`, with the note "Built 3-2-2, cash $26". Same pattern.
  - **G20 d097** (attempt index 1). Content: `mortgage_property` New York. Received: `end_turn`, with public and private strings equal to the content's. The arguments differ only by the content's `space_key`.
- **Wording consequences.**
  - Say "content requested a build (G8, G12) or the first financing step of a build (G20)", not "a legal build was lost". Only G8's 1-1-1 entries are per-entry even, and its affordability ($300 from a stated $472) has not been re-checked against the canonical state here.
  - The G8 and G12 received ENDs whose notes claim completed construction connect this residual to the phase-2 phantom-build observations. That makes them received-call conflicts with internally inconsistent arguments, not chosen holds.

## Independent reconciliation (Fable, 2026-10-29)

Fable reproduced this result independently with `phase3/fable/scripts/first_management_causes.py` (outputs `fable/exhibits/first_management_causes.{json,csv}`). Fable's inputs were Fable's own phase-1 episode file and Sol's conflict decision IDs. Fable classified **all 63** trade-completed groups by the turn-ending post-turn decision of the owner's first actual management turn.

Columns, per agent: groups / built / never legal at any menu that turn / engine default after a refusal-consumed retry / other engine default / received Grok conflict at the turn-ending END / valid END.

| Agent | Groups | Built | Never legal that turn | Default (refusal-consumed retry) | Other default | Received conflict at END | Valid END |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sol | 17 | 16 | 0 | 0 | 1 | 0 | 0 |
| Gemini | 18 | 17 | 0 | 0 | 0 | 0 | 1 |
| Opus | 15 | 7 | 5 | 3 | 0 | 0 | 0 |
| Grok | 13 | 3 | 4 | 0 | 0 | 4 | 2 |

**Totals:** 43 built, 9 never legal, 4 defaults, 4 conflicts, 3 valid ENDs.

**Agreement with my entry-buildable 42.** Restricted to those 42, Fable's eight non-builds match my eight exactly. The two extra groups in Fable's 63-group view are:
- **G13 Opus light blue:** it became legal later in the window; the turn ends in a refusal-consumed default at d210, after a build on another group at d207.
- **G13 Grok yellow:** it became legal later; the turn ends at d151 with a received END conflict.

**A self-correction to report.** Fable's first pass mislabelled G15 Grok brown as a conflict, because d126 earlier in the same turn is a conflict. My classifier has the same exposure: it flags "any conflict in the turn". My final class for G15 rests on reading the turn-ending d129 content, not on that flag.

**Preferred rule (Fable's):** classify by the turn-ending decision and keep earlier-decision flags only as secondary columns. Adopted.

**Unit note.** Fable's "valid END" count of 3 includes one Gemini END among the 63 groups. That Gemini group is outside my 42 because it was not buildable at entry, so my "two chosen holds" figure applies to the entry-buildable population only.
