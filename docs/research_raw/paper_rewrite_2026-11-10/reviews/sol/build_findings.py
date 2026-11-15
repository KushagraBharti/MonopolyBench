"""Generate exact passage locators for this review, without changing manuscripts."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
items=[]
def add(id,severity,file,passage,evidence,resolution,status='performed_source_reading_and_retained_data_checks'):
    path=BASE/file
    s=path.read_text()
    assert passage in s,(id,passage)
    items.append({'id':f'SOL-XR-{id:03}','severity':severity,'source':{'path':str(path.relative_to(BASE)),'line_1based':s[:s.index(passage)].count('\n')+1,'exact_passage':passage},'evidence':evidence,'check_status':status,'resolution':resolution})
add(1,'high','full_drafts/opus/sections/bargaining.tex','collects no rent on them',
    'G2 yellow completion episode has rent_until_loss_or_end=44. Original events.jsonl seq1566, turn77, pays Sol $44 on Atlantic. Spending unit has $0 developed rent, $300 outlay and $150 salvage. Fresh original event reading and ledger comparison; see performed_checks.json/g2.',
    'Say zero developed yellow rent and $44 undeveloped rent after completion. Do not describe the sold houses as later inherited intact.')
add(2,'high','full_drafts/opus/sections/opus_quotes.tex','At \\$325 p4 retains \\$520, enough for nine yellow houses immediately.',
    'Original G2 d124 private field hash/span checked here. Nine yellow houses at $150 cost $1,350; $520 alone buys three. Astra independently noted the same error.',
    'Preserve the quote exactly and explicitly correct its capacity arithmetic outside the quote. Do not validate full collateral-accessible capacity.')
add(3,'high','full_drafts/fable_5_2/sections/bargaining.tex','Mostly when the holder runs short of cash.',
    'Fresh sale tabulation reproduces 21/48 completing cash sales with seller below $100, versus 21/30 among all cash sales with a seller below $100. These are different conditioning sets. Median seller cash is $194 versus $571 in neither-completing cash settlements.',
    'Use exact counts and medians. Delete mostly, main, and counterfactual claims that liquid holders would not sell.')
add(4,'high','full_drafts/fable_5_2/sections/bargaining.tex','The systems price the completion itself, on both sides of the table.',
    '373/429 completer-pays direction reproduced. Bundles and game states differ. Counter checks also reproduce general cash-demand increases outside completion cells. Neither identifies a marginal premium.',
    'Report completing-side cash direction and source-attributed valuation claims; do not claim an identified completion premium.')
add(5,'medium','full_drafts/fable_5_2/sections/bargaining.tex','A deed that completes a group costs the same from the bank as any other.',
    'Board deed list prices differ. The bank does not condition the listed price of a given deed on its buyer completing a group.',
    'Delete the misleading comparison or state the per-deed rule precisely. It still does not identify a negotiated premium.','performed_source_reading')
add(6,'high','full_drafts/opus/sections/abstract.tex','most of the shortfall comes from engine defaults',
    'Fresh first-window tabulation: Opus 15 completions, 7 built, 5 no observed build option, 3 defaults. Defaults are not most of eight full-window residuals.',
    'State 5/3 split; restrict any both-entry-nonbuilds statement to the entry-buildable population.')
add(7,'high','full_drafts/fable_5_2/sections/development.tex','It then lost most of their early value',
    'Current receipts and inherited target-feasibility checks do not identify forgone economic value. No corrected continuation or rent counterfactual was evaluated.',
    'Report requested allocations not executed and actual receipt totals separately. Delete most value lost.')
add(8,'high','full_drafts/fable_5_2/sections/development.tex','Nine could not legally be built on.',
    'Fresh window ledger reproduces nine cases with no construction option on recorded menus. Settlement mortgage status/low cash establishes immediate constraints, not all unvisited financing paths.',
    'Use no construction option appeared in their recorded first window; leave exhaustive financing feasibility unresolved.')
add(9,'high','full_drafts/fable_5_2/sections/insolvency.tex','the protection bought lasted 43 turns',
    'Observed G13 settlement at turn107 and bankruptcy at turn150; inherited alternate $130 plus Ventnor route exists. No continuation identifies survival caused by the actual sale or price.',
    'State Grok remained in play for 43 more turns before the yellows transferred to Sol. Do not attribute that duration to purchased protection.')
add(10,'high','full_drafts/sol/conduct.tex','The earlier payment purchases time',
    'Same G13 causal-duration problem as SOL-XR-009. This is my own earlier wording, not exempt from correction.',
    'State the actual receipt, immediate cash position and later bankruptcy separately.')
add(11,'medium','full_drafts/astra/discussion.tex','an insurance sale can postpone',
    'The current trajectory establishes a later event; its timing without the sale is unidentified.',
    'Say the sale is followed by continued play and a later transfer, without a delay effect.')
add(12,'high','full_drafts/opus/sections/liquidity.tex','every text channel argues against the action that was applied',
    'The original G12 quote field is checked here. Public message says Bankruptcy. The pinks go with the rest. Content and private note oppose declaration. G19 likewise has a proposal-supporting public message.',
    'Name the two conflicting channels. Public output supports the received call; do not say every channel.')
add(13,'medium','full_drafts/opus/sections/discussion.tex','Displayed options understated finance in all three payable eliminations',
    'The displayed menu includes sales. The stated subtotals sum cash plus currently displayed mortgages only. G12 d249 witness uses house sales. Historical payment witnesses are inherited, not re-executed.',
    'Attribute understatement to a mortgage-only subtotal, not necessarily the supplied menu or information.')
add(14,'medium','full_drafts/opus/sections/construction.tex','a sound allocation that cannot be expressed',
    'Historical target checks establish reachable purchase multisets under another ordering; the interface can express them. Sound investment and future income were not tested.',
    'Use reachable allocation submitted in an invalid encoding. Do not infer strategic investment quality.','performed_source_reading_with_inherited_engine_results')
add(15,'medium','full_drafts/opus/sections/setup.tex','refusal recovery used in 1,605 decisions',
    'Fresh original G2 d129 chain is illogical then refused. There are 1,605 refused decisions, but only 1,604 first-refusal recovery chains.',
    'Separate refusal occurrence from action-only recovery and disclose shared two-attempt budget.')
add(16,'medium','full_drafts/opus/sections/bargaining.tex','Rows omit cells with fewer than two counters',
    'Same caption lists omitted cells containing six and five counters. Read source table; ledger transition checks confirm full population is 394.',
    'Show a full transition table or identify exactly which cells are displayed; remove incorrect filtering rule.')
add(17,'medium','full_drafts/astra/main.tex','Recipients consequently do not respond to incoming cash alone.',
    'Different cell medians do not identify which attributes cause responses. Some explicit rival-consequence texts support attention to other considerations, independently of this invalid aggregate inference.',
    'Tie rival consideration to quoted/coded reasons. Retain medians as descriptions.')
add(18,'medium','full_drafts/sol/manuscript.tex','The latter offers most often induce counters.',
    'The counted response is observational and the offers differ. This is my own unnecessary causal verb.',
    'Replace induce with receive.')
add(19,'medium','full_drafts/sol/temporal_discussion.tex',"its validated ontology",
    'Fresh primary reading of Empty Commitments v2 §§3.4/5.6 reports checks of detector, judge and labels on its own sample. That does not establish general ontology validity or transfer to these promises.',
    'Say its ontology or specify the checked components and domain, without a general validation adjective.','performed_primary_source_section_reading')
add(20,'medium','full_drafts/fable_5_2/sections/bargaining.tex','The figures match the ledger.',
    'G15 $830/$233 arithmetic matches. The note says $600 for one house each; that is a complete green layer, not minimum construction. Source shows 19 bank houses and a rule allowing levels to differ by one. No post-acceptance route was executed here.',
    'Specify which cash figures match; say $600 buys three green houses while $233 covers one $200 house. Do not imply exhaustive collateral or timing validation.')
add(21,'medium','full_drafts/fable_5_2/sections/setup.tex','A false private note written under the standard prompt departs from a request',
    'Prompt asks notes to reflect true reasoning. A factual mistake can faithfully express a mistaken belief; truthfulness is not guaranteed factual accuracy.',
    'Say false private text alone establishes neither knowing dishonesty nor instruction violation.','performed_source_reading')
add(22,'medium','full_drafts/opus/sections/conduct.tex','in 15 the arguments are identical',
    'Retained raw comparison distinguishes 15 equal parsed objects from only 5 equal literal argument substrings. This count is inherited; no raw-string census rerun here.',
    'Specify parsed arguments for 15 and literal arguments for 5; do not imply byte identity.','inherited_raw_response_comparison_with_performed_passage_review')
add(23,'medium','full_drafts/opus/sections/discussion.tex','Conduct audits can start at pressure points.',
    'Purposively selected cases provide no population concentration or validation of a review-priority policy. Arena scarcity association is observational and judge-sensitive, not a validation of this recommendation.',
    'Describe the economic stakes of selected cases. If retained as a proposal, label it untested rather than a finding.')
add(24,'medium','full_drafts/opus/sections/bargaining.tex','built on without return',
    'Fresh G2 original-event check finds $44 undeveloped rent, plus $150 salvage. Zero developed rent is narrower than no return.',
    'Correct the interpretation as well as the outcome paragraph. Preserve all separate receipt measures.')
add(25,'low','full_drafts/sol/temporal_discussion.tex','the causal order that agents confront',
    'The section describes a chronological/implemented economic sequence. It does not identify causal effects on strategy or outcomes.',
    'Use economic sequence or specify an individual rule-determined transition.')
add(26,'medium','full_drafts/sol/temporal_discussion.tex','cannot be treated as a deliberate abandonment',
    'A same-response note favoring purchase conflicts with the applied auction. That prevents a clean intention attribution, but does not prove all deliberate-change hypotheses impossible.',
    'Use does not establish deliberate abandonment.')
add(27,'medium','full_drafts/fable_5_2/sections/related.tex','These studies score outcomes against a defined utility',
    'The grouped literature includes rank-based multi-agent games as well as utility-defined bargaining. Abstract-only inspection cannot support one shared objective or an endorsement of all rankings.',
    'Describe each closest comparator by its inspected design; omit broad grouping and superiority claims.','performed_passage_review_with_limited_primary_section_checks')
(HERE/'findings.json').write_text(json.dumps({'reviewer':'Sol xhigh','schema_version':'whole-paper-review-v1','note':'Exact frozen passages, not edits. New retained-data/source checks are distinguished from inherited engine/raw-response results.','findings':items},indent=2)+'\n')
print(f'Wrote {len(items)} exact-passage findings.')
