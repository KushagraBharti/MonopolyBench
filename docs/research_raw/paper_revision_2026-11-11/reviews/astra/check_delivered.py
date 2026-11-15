"""Compare delivered drafts by read-only arithmetic on retained records.

No engine/model imports, evaluations, branches or simulations. Outputs stay in
this review directory. Semantic labels are joined, never re-annotated.
"""
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = HERE.parents[4]
SOURCES = {}

def read(path):
    path = Path(path)
    SOURCES[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())

offers = read(REPO / 'docs/research_raw/paper_rewrite_2026-11-10/data/agenda_offers.json')
rebuilt = read(BASE / 'full_drafts/opus/data/offers_rebuilt.json')
assert len(offers) == len(rebuilt) == 920
by_key = {(r['game'], r['decision']): r for r in rebuilt}
mapping = {'author_only': 'Author only', 'recipient_only': 'Recipient only', 'both': 'Both', 'neither': 'Neither'}
for r in offers:
    q = by_key[r['game'], r['decision']]
    assert (r['response'], r['accept_available'], r['author'], r['recipient']) == (q['response'], q['accept_legal'], q['author'], q['recipient'])
    assert mapping[r['completion_cell']] == q['cell']
    assert r['offer']['cash'] == q['author_gives']['cash']
    assert r['request']['cash'] == q['author_asks']['cash']
    assert r['offer']['properties'] == q['author_gives']['properties']
    assert r['request']['properties'] == q['author_asks']['properties']

def count(rows):
    return {'n': len(rows), **Counter(r['response'] for r in rows)}

def contrast(rows):
    return {c: count([r for r in rows if r['completion_cell'] == c]) for c in mapping}

out = {'compared_offer_rows': 920}
legal = [r for r in offers if r['accept_available']]
opening = [r for r in legal if r['exchange_index'] == 0]
out['opening'] = contrast(opening)
out['opening_by_recipient'] = {m: contrast([r for r in opening if r['recipient_model'] == m]) for m in ['Sol', 'Gemini', 'Opus', 'Grok']}

def bundle(r):
    return tuple((tuple(sorted(r[k]['properties'])), r[k]['get_out_of_jail_cards']) for k in ['offer', 'request'])

threads = defaultdict(list)
for r in offers:
    threads[r['thread_id']].append(r)
concessions = []
for tid, rows in threads.items():
    previous = {}
    for r in sorted(rows, key=lambda r: r['exchange_index']):
        p = previous.get(r['author'])
        if p and bundle(r) == bundle(p) and r['net_cash_author_to_recipient'] > p['net_cash_author_to_recipient']:
            concessions.append({**r, 'prior_own_offer_decision': p['decision'], 'concession': r['net_cash_author_to_recipient'] - p['net_cash_author_to_recipient']})
        previous[r['author']] = r
assert len(concessions) == 199
opconc = read(BASE / 'full_drafts/opus/data/bargaining.json')['concession_rows']
assert {(r['game'], r['decision'], r['concession']) for r in concessions} == {(r['game'], r['decision'], r['concession']) for r in opconc}
out['concessions'] = contrast(concessions)
out['concession_legal'] = sum(r['accept_available'] for r in concessions)
out['concession_unique_threads'] = {c: len({r['thread_id'] for r in concessions if r['completion_cell'] == c}) for c in mapping}
out['concession_conditions'] = dict(Counter(r['response_condition'] for r in concessions))

# One deed per matched game/seller set; first ask and median are different estimands.
price = read(BASE / 'full_drafts/opus/data/pricing.json')['rows']
paired = defaultdict(list)
for r in price:
    if r['kind'] == 'ask' and len(r['deeds']) == 1:
        paired[r['game'], r['seller'], r['deeds'][0]].append(r)
pairs = []
for key, rows in sorted(paired.items()):
    a = sorted([r for r in rows if r['buyer_completes']], key=lambda r: r['decision'])
    b = sorted([r for r in rows if not r['buyer_completes']], key=lambda r: r['decision'])
    if not a or not b:
        continue
    direction = lambda x, y: 'higher' if x > y else ('lower' if x < y else 'equal')
    pairs.append({'game': key[0], 'seller': rows[0]['seller_model'], 'deed': key[2],
                  'completing': [[r['decision'], r['cash'], r['any_mortgaged']] for r in a],
                  'other': [[r['decision'], r['cash'], r['any_mortgaged']] for r in b],
                  'first_direction': direction(a[0]['cash'], b[0]['cash']),
                  'median_direction': direction(median(r['cash'] for r in a), median(r['cash'] for r in b))})
out['same_deed'] = pairs
out['same_deed_first'] = dict(Counter(r['first_direction'] for r in pairs))
out['same_deed_median'] = dict(Counter(r['median_direction'] for r in pairs))

# Compare independently derived episode endpoints and action sequences.
ad = read(BASE / 'full_drafts/astra/data/liquidation_episodes.json')
sd = read(BASE / 'full_drafts/sol/data/debt_episodes.json')
od = read(BASE / 'full_drafts/opus/data/debt_episodes.json')['episodes']
ak = {(r['game'], r['first_decision']): r for r in ad}
sk = {(r['game'], int(r['first_decision'].split('-dec-')[-1])): r for r in sd}
ok = {(r['game'], r['first_decision']): r for r in od}
assert ak.keys() == sk.keys() == ok.keys()
for k, a in ak.items():
    s, o = sk[k], ok[k]
    assert (a['outcome'] == 'paid') == (s['outcome'] == 'paid')
    assert (a['outcome'] == 'paid') == (o['outcome'] == 'paid')
    assert a['debt'] == s['debt'] == o['owed']
    assert a['actions'] == o['actions']
    assert a['decisions'] == s['decisions']
conflicts = read(REPO / 'docs/research_raw/paper_rewrite_2026-11-10/data/resolution_conditions.json')['selected_grok_conflicts']
conflict_ids = {r['decision_id'] for r in conflicts}
paid = [r for r in ad if r['outcome'] == 'paid']
out['debt_comparison'] = {'rows': len(ad), 'paid': len(paid), 'paid_multiaction': sum(len(r['actions']) > 1 for r in paid),
                          'paid_actions': dict(Counter(a for r in paid for a in r['actions'])),
                          'paid_fallback_actions': sum(r['fallback_actions'] for r in paid),
                          'paid_conflicts': [{'game': r['game'], 'first_decision': r['first_decision'], 'conflicting_ids': [d for d in r['decisions'] if d in conflict_ids]} for r in paid if any(d in conflict_ids for d in r['decisions'])]}

# Compare pre-final-action (Astra/Sol) and immediately pre-estate (Opus) states.
# A final mortgage can change cash before automatic elimination without changing
# who owns the deeds. Record such timing differences rather than equating states.
ae = read(BASE / 'full_drafts/astra/data/first_estates.json')
se = read(BASE / 'full_drafts/sol/data/first_estate_positions.json')
oe = read(BASE / 'full_drafts/opus/data/first_estates.json')['rows']
estate_differences = []
for a, s, o in zip(ae, se, oe):
    assert a['game'] == s['game'] == o['game']
    assert a['creditor'] == s['creditor'] == o['creditor']
    ss = {r['player']: r for r in s['positions']}
    oo = {k.split('/')[-1]: v for k, v in o['standing'].items()}
    for p, r in a['positions'].items():
        assert r['cash'] == ss[p]['cash']
        if r['cash'] != oo[p]['cash']:
            estate_differences.append({'game': a['game'], 'player': p, 'before_final_action': r['cash'], 'before_estate': oo[p]['cash']})
        assert r['deeds'] == ss[p]['deeds'] == oo[p]['deeds']
        assert r['building_levels'] == ss[p]['building_equivalents'] == oo[p]['buildings']
        assert ss[p]['prior_paid_rent'] == oo[p]['rent_in']
out['pre_estate_comparison'] = {'games': 20, 'Astra_Sol_pre_action_states_match': True, 'cash_timing_differences_to_Opus': estate_differences, 'deeds_buildings_prior_rent_match': True}

codes = read(REPO / 'docs/research_raw/paper_agenda_revision_2026-10-29/reviews/negotiation/reason_comparison.json')['categories']['D']
keys = codes['common_positive_keys']
out['agreed_rival_codes_by_game'] = {g: sum(k.startswith(f'G{g:02d}d') for k in keys) for g in range(1,21)}
out['agreed_rival_G1_G15'] = out['agreed_rival_codes_by_game'][1] + out['agreed_rival_codes_by_game'][15]
out['sources'] = SOURCES
(HERE / 'delivered_comparison.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sources', 'same_deed', 'opening_by_recipient']}, indent=2))
