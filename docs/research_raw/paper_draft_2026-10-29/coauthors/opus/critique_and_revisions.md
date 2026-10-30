# Opus step-15 critique, revision record and suggested title/abstract

Opus, 2026-10-29. This file has six parts:

1. Corrections I accepted into `conduct_validation.tex`.
2. The deltas between root's `sections/social_results.tex` snapshot and my current file.
3. Errors I found in peer and root prose.
4. My challenges to the economic section and the paper's main argument.
5. A suggested title and abstract, written after the findings.
6. Disagreements I am preserving.

My independent position, saved before I read any peer prose, is `initial_position.md`. Evidence for every number is in `evidence_map.md`.

## 1. Corrections accepted into my own prose

Each change below was re-checked against the original record. The parenthesised number is the objection's number in that reviewer's list.

| Raised by | Original wording | Revised wording | Check |
|---|---|---|---|
| Sol (1), root (2) | "Three different contracts coexist … Provider reasoning carries no instruction at all" | The win and legal-action instructions govern every decision. The channel-specific requirements differ. Neither prompt directly specifies the content of returned provider reasoning | `player_config.py:10–43`; `prompting.py:1230–1245` |
| Sol (2), root (5) | G4: "both parties' positions improved against the leader" | Both obtained complete buildable groups; any gain against the leader was not tested | No advantage metric was computed |
| Sol (3), root (8) | "Three components are absent: contract object, private bilateral channels, reward/training"; read as prerequisites for RL and monitor training | RL needs a reward interface, a truncation rule for training rollouts, a training loop and held-out evaluation. Monitor training needs labelled ground truth. A contract object would make commitment norms enforceable, not merely scorable. Private channels are an optional extension | — |
| Sol (4), root (6) | "discarded legal plans" | As encoded the plans were invalid; their purchase multisets were affordable and become executable when reordered | `P2/astra/default_build_plans.json` |
| Sol, root (1) | "every decision carried a public message" | Every applied decision, engine fallbacks included, carried a public-message field; 107 are empty | Recounted over all 20 `actions.jsonl`: 6,989 fields, 107 empty, 0 missing |
| Root (3) | "On the first decision of game 20, d1" | d1 is Grok's first end-of-turn decision and the game's second (d000 is its Vermont purchase) | `PKT/game-20-part-001.jsonl` |
| Root (4) | G6 headed "a false premise that cost its speaker", calling it "a clear instance of falsity without any sign of strategic deception" | Headed "correction with acceptance after a split proposal". The applied note repeats the premise. Content and reasoning select END. No coherent speaker intent is identified | `P2/sol/g06_negative_case_check.json` |
| Root (7) | "replaying the recorded action reproduced the recorded suffix" | It reproduced the next recorded events, up to the next decision, including hidden dice and card state; not a whole altered-policy suffix | `P1/opus/opus_sandbox_checks.py` lines 95–100 |
| Root (9) | "In every case the recipient's applied response is consistent with the correct state" | Proposition-specific. G19, G11 and G6 recipients state the correct proposition. G4 recorded the true figure first. G13 is silent, so uptake is neither identified nor excluded. Apart from G4's public assent, which the recipient's earlier note contradicts, the only recipient restatement is G11's transient echo, corrected before rejection. No recipient accepts while its private note or returned reasoning endorses a false premise | — |
| Self | NegotiationArena "tactic and framing measurably move outcomes" | Designed comparisons can measure such effects, e.g. the payoff gain from feigned desperation | Sol's literature reading, §§2–5 |
| Self | G18 chronology omitted d422 and d423 and listed two Sol counters | Adds Sol's d422 rejection and Opus's d423 "Offer stands if you change your mind"; Sol's later counters were $450, $350 and $300 | `PKT/game-18-part-075/076/081/082` |
| Self | Sol's sales "answered rent debts rather than the offer" | They accompanied a second rent payment rather than any step toward the offer | Sol's audit wording |
| Self | G9/G16 "the rival's balance … confirm the stated mechanism" | Each stated mechanism can be checked against recorded cash; I did not recompute it in step 15 | — |
| Self | Unattributed "14 provider-summary errors" | Attributed to one coauthor's coding of the 240-decision sample | `P2/opus/claims.md` A8 |
| Self, added | — | G4: Grok paid the leader (Sol) $200 for Ventnor to make the anti-leader swap possible (d142–d146); its notes weigh how many "p3 pink houses" each price would fund | `PKT/game-04-part-024/025` |

I did not use the G15 green narrative or the G19 $1,200 dark-blue figure in my prose. Sol's corrections (G15 orange at e711/e718 with $3,250 developed rent; G19 Gemini cumulative $2,000) therefore leave my file unchanged.

## 2. Deltas between root's `sections/social_results.tex` and my current file

Root's file is a copy of my earlier version, with its own label changes (`sec:discussion-design`). Integration should carry forward these changes, all of which root itself requested:

- **G6 paragraph:**
  - new heading;
  - the applied note's premise sentence;
  - the replaced conclusion;
  - table row: speaker cell "Applied note repeats the premise; content and reasoning select END; tool proposes"; outcome cell "Settled; speaker's later note calls it an overpay".
- **"What the chronologies show together":** the second and third sentences are replaced with the proposition-specific text (root item 9).
- **G20 paragraph:** opening clause on d1 (root item 3).
- **Opening paragraph:** "fields, engine fallbacks included; 107 … empty".
- **G4 cooperation paragraph:** "obtained complete buildable groups; … not tested". Root's snapshot already has this.
- **§ instrument:** "As encoded, these plans were invalid …"; replay "next recorded events … not a whole altered-policy suffix"; final paragraph on absent components.
- **Contract paragraph:** "A false private note written under the standard condition …". Root's snapshot already has the channel-requirements sentence.

## 3. Errors found in peer and root prose

1. **`coauthors/sol/framing_conduct_bridge.tex`, G13 paragraph.** It says the buyer at d251 records a solvency reason "because the seller may later pay Short Line rent to the buyer". That is wrong.
   - Short Line belongs to Sol (seat 2), not to the buyer, Opus (seat 1).
   - Opus's d251 returned reasoning reads "keeps p4 solvent enough to cover Short Line rent to p2".
   - At d253 the stated motive is to stop p2 inheriting the yellows.
   - "Records" should also say *returned reasoning*. Both Opus decisions were resolved under the action-only condition and carry no applied note (`PKT/game-13-part-052.jsonl` lines 1 and 3).
2. **`coauthors/fable/setup_related.tex` line 85.** "Opus's initial response was refused by the provider in 1,605 of its 1,696 decisions" should read 1,604 first-attempt refusals. There are 1,605 refused attempts in total, including G2 d129's second-attempt refusal after an invalid first attempt (`P2/astra/reconciliation.md`; `P2/opus/claims.md` A6, A7). The table note's "1,604 decisions under an action-only recovery" is consistent with this.
3. **`sections/setup.tex`, contract paragraph.**
   - "They ask private notes to reflect the agent's true reasoning" holds only under the standard prompt. The action-only prompt deletes that sentence as well as the note field.
   - This is the most important channel boundary for the Opus records and should appear in setup, not only in my section. Exact text: `prompting.py:1230–1245`.
4. **`sections/economic_results.tex`, G20 New York paragraph.**
   - The agent is unnamed. It is Sol (seat 3) at d235, and its public message claims "$400 leaves me buying a set I can't develop" (`PKT/game-20-part-040.jsonl`).
   - Naming the agent and quoting the claim would make the "too strong" judgement checkable.
   - The G5 d300 citation is correct: Sol's END retaining "all 24 houses".
5. **Duplication.**
   - The capability–alignment design now appears three times: Sol's bridge §3, my § instrument-design and root's `sec:discussion-design`. Keep one, in the discussion. Merge Sol's point that descriptive adherence to a declared norm needs no randomization with my concrete norm list (disclosure, protected information, commitment with release authority, authorization).
   - Replay validation appears in root's `validation.tex` and in my § instrument-replay/mechanisms. Root's version has finer counts (10,235 snapshots, 6,882 non-empty utterance occurrences, 6,720 observed) and should be kept. From mine, keep:
     - § instrument-legal, which covers legal-sequence tests of the agents' claims *and* of the analysts' labels, including the 484/101/8/21 → 467/112/14/21 correction history;
     - the four-layer validity table.
   - My evidence-chain table overlaps root's "five questions" in `methods.tex`. Use one. I prefer the table in methods, with root's prose.

## 4. Challenges to the economics and the main argument

1. **The economic section needs a stated through-line.** As drafted it reads as a sequence of correctly bounded audits. A one-paragraph opening should answer RQ1 directly: position is built through access, financing and inheritance, and capability shows most clearly in converting access into an executable sequence, whether a build, a liquidation or a trade. The sections that follow are then evidence for that sentence, not a catalogue.
2. **Outcomes must appear somewhere in plain sight.** Readers will look for the win split (Sol 8, Gemini 7, Opus 3, Grok 2) and the seat pattern (seats 1–2 win 14/20). Put F2 and these counts in study design, with one sentence saying why they are not a ranking: five dependent blocks, unequal channel and response conditions. Omitting them invites the suspicion that they were hidden.
3. **Unpaid debts versus paid rent.** "Zero paid developed rent" is accurate, but a lethal rent debt that becomes an estate is the largest return some groups produce. The text says this. F5's caption must not set $93,000 beside $103,450 in a way that invites a ratio.
4. **Make exact-prefix testing the unifying method.** The paper's distinctive move is that one exact-prefix, legal-sequence procedure adjudicates economic claims (reorderable builds, payable debts, the stock lock) and social claims (G13's $130 route, G18's changed state). The introduction and conclusion should say so. Otherwise the two halves read as two papers.
5. **Keep the capability–alignment motivation as motivation.** The deliverable on that question is the experimental design. No sentence should imply that the four configurations sit on a capability axis.
6. **Order.** Social results should follow economics directly, as in the outline. Validation and design come after both, because both rely on them.

## 5. Suggested title and abstract (written after the findings)

**Title.** *MonopolyBench: Auditing Economic Capability and Social Conduct in Long-Horizon Multi-Agent Competition.*

The alternative is root's `pdftitle`, which I also accept.

**Abstract (about 200 words).**

> Agents that operate in persistent economies must pursue goals over long horizons while dealing with other agents whose interests compete with their own. We study both capability and conduct in MonopolyBench, a deterministic four-player Monopoly economy in which language-model agents choose only among engine-issued legal actions, bargain in free-form public messages and keep private notes, with every decision, attempt and state change recorded. We analyze a complete cohort of twenty games—five seeds, each played under four seat rotations, 6,989 decisions—by four frontier-model configurations. Restoring exact historical decision states and executing specified legal sequences changes several readings of the record: all 61 construction plans that one configuration lost to engine fallback contain affordable purchases that become executable when reordered, and only three of sixty eliminations admit a legal payment of the current debt. Social chronologies link claims, delivered information and recipient responses. A misleading financial omission precedes a higher-price settlement, yet the buyer's returned reasoning already gave its own reason to pay; other recipients correct false premises while accepting or rejecting the offer. Because the game permits public deception, these describe competitive conduct, not misalignment rates. The cohort cannot rank models or relate alignment to capability; we specify the controlled design that would.

Sol's abstract is accurate. It lists four economic facts where the outline asks for one or two. I use two: one about execution, one about finance.

## 6. Preserved disagreements

- **G6.** I accepted root's narrowing. I still hold that the speaker's later "bad overpay" note is relevant evidence: the speaker's own record came to treat the premise as an error, which weighs against reading the proposal as strategic deception. The revised text keeps that point in weakened form, without inferring intent.
- **Abstract.** I argue for two economic numbers, Sol for one. This disagreement is minor and was already recorded in phase 3.
- **"Contract" vocabulary.** I accept "channel-specific requirements" and drop "three contracts". I keep "normative contract" for the whole instruction set, as in the locked outline §2.2.
- **Placement of the design.** It belongs in a discussion section of its own, not inside validation. My file keeps it under § instrument only so that it compiles standalone.
