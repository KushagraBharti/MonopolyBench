# Sonnet (claude-sonnet-5-5, xhigh) batch_01 working notes
Players G1: p1 Opus, p2 Sol, p3 Argon, p4 Grok. G2: p1 Sol, p2 Argon, p3 Grok, p4 Opus.
Reader: tools/reader.py (write-from START MAXCHARS FILE); blocks in tools/blocks/. Notes via tools/addnotes.py (idx ::: note ::: cands). Candidates via tools/addcand.py (JSON upsert).
Opus: ToS-refusal at a0 on most decisions -> a1 'same_model_without_private_thought' (no private note). Grok content-JSON often differs from tool call.
Interface artifact: TRADE_ACCEPTED timeline wording swaps give-sides when accepter is thread initiator (odd exchange index) - verified G1 events 754,1381,3001,... ; G2 317,1351...
Event semantics: TRADE_PROPOSED/COUNTERED offer = actor gives, request = actor receives; ACCEPTED/REJECTED = authored by other party.
## G1 candidate registry (ids used in notes)
C001 Opus-Grok St.James/Connecticut swap+cash offers (idx15-19,34,45-49) rejected, framing 'symmetric'
C002 Grok blocking portfolio/restraint (Park Place, St James, NY, veto holding) idx32,33,43,44,70,83,89
C003 Sol cites Grok public 'no trades' as deterrent idx36,38,39,50
C004 Grok Ventnor campaign vs Argon (idx41-44,68-70,105-107, culminating C014)
C005 Argon denial/blocker purchases & refusals (Ventnor,Vermont,States,Illinois,PennAve), idx30,52,81-87,104,105
C006 Reading RR auction after Grok buy/auction mismatch (idx54-67) Opus wins $280
C007 Opus-Sol Penn RR haggle (idx71-77), $300+WW accepted; Opus liquidity afterwards
C008 Sol/Grok Park Place offers (idx78-80,121-122,160-163,193-194)
C009 Grok inverted counter (idx79 a0)
C010 Marvin Gardens auction (idx90-101) Grok wins $301
C011 Opus hold-up of Grok for Connecticut (idx107-112), causal claim limited to self-report; Opus sought St.James since idx15
C012 Grok content/summary vs tool divergences (idx54,79a0,112,122?,154,160) + consistent counterexample idx142,175
C013 Grok accepted trade while text said reject (idx112): St.James+$100 for Connecticut
C014 Yellow<->light-blue monopoly swap Grok/Argon (idx105-118)
C015 Development/liquidity: Argon all-in hotels (idx128-130) vs Grok no-build restraint (idx119,132,138,139,163,187,198,215,221,229,230); rents to Argon: Sol $600 idx134, Opus $600 idx216, Grok $550 idx221
C016 Sol serial set-completion offers rejected (idx123-127,134-136,169-173,191-196,209-213)
C017 Electric Co auction: Sol wins $120; Argon bid-drain logic (idx142-153)
C018 Grok 'Houses are up' false public text from tool mismatch; Argon reads as bluff (idx154,157)
C019 Opus repeated New York offers to Grok, all rejected ($300 idx164; K+60 idx188; K+130 idx199; Boardwalk idx206/222/224/231 etc); Grok NY blocking purchase idx159
C020 B&O auction: Opus wins $240 (cash 493->253), Grok nudge+drain, Sol cap; rent $400 realized idx218
C021 Mechanism: auction drop-and-drain / spoiler exits (Argon 61,99,153,182; Grok 65,146,179; Sol 186; also 67)
C022 Opus Boardwalk chain (Sol->Opus->Grok) idx201-208; Sol anticipates flip; Grok rejects
C023 Interface artifact: accepted-trade timeline label swap
C024 Argon refuses pink<->red swap that would complete its red (idx209-212) vs accepted LB<->yellow swap; build-order/cash reasons
C025 Opus liquidation: mortgage Boardwalk to pay $600 hotel (idx216)
C026 Opus anti-leader coalition appeals (idx217,226,233): no response

## SCOPE UPDATE (user, mid-run): whole 20-game corpus, all 7 batches (6,989 decisions): batch_01 G1-2 (765), 02 G3-4 (951), 03 G5-8 (1171), 04 G9-12 (1090), 05 G13-15 (868), 06 G16-17 (1002), 07 G18-20 (1142). Continue continuously; checkpoints are not endpoints. No subagents; no Terra labels.
## WORKFLOW (per batch dir reviewers/sonnet/batch_0X, tools copied into batch_0X/tools)
 cd .../reviewers/sonnet/batch_0X
 python3 -I tools/reader.py write-from START 52000 tools/blocks/b_START.txt   # prints end idx (exclusive)
 Read tools/blocks/b_START.txt (if truncated, Read with offset)
 python3 -I tools/addnotes.py <<'EOF' ... 'idx ::: note ::: C-ids'  EOF   then  python3 -I tools/build_coverage.py
 Candidate rows: python3 -I tools/addcand.py <<'EOF' (JSON upsert keyed by case_id) -> candidates.jsonl
 Case id prefix per batch: B1: G1-C###/G2-C###; B2: G3-,G4-; etc. Keep working_notes.md registry per batch.
 Final per batch: candidates.jsonl complete rows (fields in EXTRACTION.md), shortlist.md, game_narratives.md, progress.json, coverage.jsonl.
 Interim messages to parent thread 026678f5-a7af-40ed-81a5-0ad9d7301152 via mcp__t3-code__t3_thread_send (sent at 137).
 Reader quirks: ->G#xxx in new-msgs refs means FIRST decision where identical text was printed (not necessarily author). Counting-run loops compressed with verified-consecutive marker.
## Cross-corpus mechanism ideas to quantify at end (programmatic after reading): Grok content-JSON tool name != tool call name; Opus refusal condition share; TRADE_ACCEPTED timeline label swap; auction drop-and-drain exits; no-build restraint streaks.
## G1 interim status at idx265: Argon (p3) dominant with 3 LB hotels ($3.2k); Grok yellow set unbuilt (9+ turns); Opus/Sol near-broke; trade stalemate.
