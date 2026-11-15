"""Read retained records only. No engine import, branch, game, or model call."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[2]
sources = {}

def digest(b):
    return hashlib.sha256(b).hexdigest()

def read(p):
    p = Path(p)
    b = p.read_bytes()
    sources[str(p.relative_to(ROOT))] = digest(b)
    return b.decode()

def load(p):
    return json.loads(read(p))

def pointer(obj, path):
    for key in path.strip('/').split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    return obj

offers = load(BASE / 'data/agenda_offers.json')
legal = [r for r in offers if r['accept_available']]
threads = load(BASE / 'data/agenda_threads.json')
flows = load(BASE / 'data/agenda_flows.json')
conditions = load(BASE / 'data/resolution_conditions.json')
windows = load(BASE / 'data/first_management_windows.json')['rows']
episodes = [json.loads(l) for l in read(ROOT / 'docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl').splitlines()]
chains = defaultdict(list)
for r in offers:
    chains[(r['game'], r['thread_id'])].append(r)
counter_rows = []
for chain in chains.values():
    chain.sort(key=lambda r:r['exchange_index'])
    assert [r['exchange_index'] for r in chain] == list(range(len(chain)))
    for i, r in enumerate(chain):
        if r['response'] != 'counter_trade':
            assert i == len(chain)-1
            continue
        n = chain[i+1]
        assert r['recipient'] == n['author'] and r['author'] == n['recipient']
        same = all(sorted(r[a]['properties']) == sorted(n[b]['properties']) and r[a]['get_out_of_jail_cards'] == n[b]['get_out_of_jail_cards'] for a,b in [('offer','request'),('request','offer')])
        delta = -n['net_cash_author_to_recipient']-r['net_cash_author_to_recipient']
        counter_rows.append({'game':r['game'],'decision':r['decision'],'cell':r['completion_cell'],'same_group': bool(r['author_new_groups']) and set(r['author_new_groups']) == set(n['recipient_new_groups']), 'counterer_completes':bool(n['author_new_groups']),'same_noncash':same,'cash_delta':delta,'interest_adjusted_delta':n['author_cash_if_accepted']-r['recipient_cash_if_accepted']})
ao = [r for r in counter_rows if r['cell']=='author_only']
kept = [r for r in ao if r['same_group']]
only = [r for r in kept if not r['counterer_completes']]
pure = [r for r in only if r['same_noncash']]
assert (len(counter_rows),len(ao),len(kept),len(only),len(pure)) == (394,111,92,88,79)
assert sum(r['cash_delta']>0 for r in only)==85
assert all(r['cash_delta']>0 for r in pure)
counter_summary = {'all':394,'author_only':111,'same_original_group':92,'only_original_group':88,'cash_increases_in_88':85,'unchanged_noncash':79,'pure_cash_increases':79,'median_delta_88':median(r['cash_delta'] for r in only),'interest_deltas_agree_in_88':all(r['cash_delta']==r['interest_adjusted_delta'] for r in only)}
counter_summary['other_cells'] = {c:{'n':len(s),'cash_increases':sum(r['cash_delta']>0 for r in s)} for c in ['recipient_only','both','neither'] if (s:=[r for r in counter_rows if r['cell']==c])}
cells={c:dict(Counter(r['response'] for r in legal if r['completion_cell']==c)) for c in ['author_only','recipient_only','both','neither']}
styles={m:{c:{'n':len(s),**Counter(r['response'] for r in s)} for c in ['author_only','recipient_only'] if (s:=[r for r in legal if r['recipient_model']==m and r['completion_cell']==c])} for m in ['Sol','Gemini','Opus','Grok']}
positions={str(i):{c:dict(Counter(r['response'] for r in legal if (r['exchange_index']>0)==i and r['completion_cell']==c)) for c in ['author_only','recipient_only']} for i in [False,True]}
settled=[r for r in legal if r['response']=='accept_trade' and r['net_cash_author_to_recipient']]
sales=[]
for r in settled:
    receiver='recipient' if r['net_cash_author_to_recipient']>0 else 'author'
    payer='author' if receiver=='recipient' else 'recipient'
    sales.append({'game':r['game'],'decision':r['decision'],'seller_cash':r[f'{receiver}_cash_before'],'payer_completes':bool(r[f'{payer}_new_groups']),'neither':r['completion_cell']=='neither'})
completing=[r for r in sales if r['payer_completes']]
nc=[r for r in sales if r['neither']]
cash={'completer_pays':sum((r['net_cash_author_to_recipient']>0 if r['completion_cell']=='author_only' else r['net_cash_author_to_recipient']<0) for r in legal if r['completion_cell'] in ['author_only','recipient_only']), 'one_sided':429, 'cash_settlements':len(sales),'payer_completing':len(completing),'under_100_completing':sum(r['seller_cash']<100 for r in completing),'median_seller_cash_completing':median(r['seller_cash'] for r in completing),'median_seller_cash_neither':median(r['seller_cash'] for r in nc),'sensitivity':{str(t):{'all':sum(r['seller_cash']<t for r in sales),'completing':sum(r['seller_cash']<t for r in completing)} for t in [50,100,150,200]}}
assert (cash['completer_pays'],cash['payer_completing'],cash['under_100_completing'])==(373,48,21)
ids={r['decision_id'] for r in conditions['selected_grok_conflicts']}
assert len(ids)==139
conf_open=[r for r in threads if r['initiator_model']=='Grok' and any(x.endswith(f"dec-{r['start_decision']:06}") and r['game']==q['game'] for q in conditions['selected_grok_conflicts'] for x in [q['decision_id']])]
conf_resp=[r for r in offers if r['decision_id'] in ids]
conf_accept=[r for r in conf_resp if r['response']=='accept_trade']
conflicts={'openings':len(conf_open),'settled_openings':sum(r['terminal']=='TRADE_ACCEPTED' for r in conf_open),'responses':len(conf_resp),'acceptances':len(conf_accept),'opus_completing_acceptances':sum(r['author_model']=='Opus' and bool(r['author_new_groups']) for r in conf_accept)}
assert tuple(conflicts.values())==(64,17,11,7,3)
economy={'routes':dict(Counter(r['route'] for r in episodes)),'nonterminal_inherited_completions':sum(r['route']=='creditor_inheritance' and r['access_status']!='no_access_before_game_end' for r in episodes),'trade_rent_by_owner':{m:sum(r['rent_until_loss_or_end'] for r in episodes if r['route']=='trade' and r['model']==m) for m in ['Sol','Gemini','Opus','Grok']},'window_causes':dict(Counter(r['cause'] for r in windows)),'opus_nonbuilds':dict(Counter(r['cause'] for r in windows if r['model']=='Opus' and not r['built_first_mgmt_turn']))}
assert economy['nonterminal_inherited_completions']==52

file_lines={}
def field(q):
    p=ROOT/q['source']
    if str(p) not in file_lines:
        file_lines[str(p)]=read(p).splitlines()
    assert sources[q['source']]==q['source_sha256']
    row=json.loads(file_lines[str(p)][q['jsonl_line_1based']-1]) if q['jsonl_line_1based'] is not None else json.loads('\n'.join(file_lines[str(p)]))
    s=pointer(row,q['json_pointer'])
    assert digest(s.encode())==q['field_sha256']
    return s,row,p

quote_checks=[]
manifest=load(BASE/'data/transcript_manifest.json')
for q in manifest['quotes']:
    for e in q['excerpts']:
        f=manifest['fields'][e['field_id']];s,_,_=field(f)
        assert s[e['span'][0]:e['span'][1]]==e['text']
        quote_checks.append({'id':q['id'],'span':e['span'],'exact':True})
for relative in ['full_drafts/opus/data/opus_quote_manifest.json','full_drafts/fable_5_2/data/transcript_manifest_supplement.json']:
    for q in load(BASE/relative)['quotes']:
        s,row,p=field(q)
        excerpts=q.get('excerpts',[{'span':q.get('span_codepoints'),'text':q.get('excerpt')}])
        for e in excerpts:
            assert s[e['span'][0]:e['span'][1]]==e['text']
        item={'id':q['id'],'exact':True,'source':q['source'],'line':q['jsonl_line_1based']}
        if q['json_pointer']=='/final_action/public_message':
            actor=row['player_id']; later=[json.loads(l) for l in file_lines[str(p)] if 'decision_started' in l]
            current=int(row['decision_id'].rsplit('-',1)[1]); following=next(r for r in later if int(r['decision_id'].rsplit('-',1)[1])>current and r['player_id']!=actor)
            item['next_actor']=following['player_id'];item['next_decision']=following['decision_id'];item['full_message_in_next_prompt']=s in json.dumps(following['prompt_payload'],ensure_ascii=False)
            assert item['full_message_in_next_prompt']
        quote_checks.append(item)

g15=next(r for r in offers if r['game']==15 and r['decision']==169)
run=ROOT/g15['source_run']; rows=[json.loads(l) for l in file_lines[str(run/'decisions.jsonl')]]
g15prompt=next(r for r in rows if r['phase']=='decision_started' and r['decision_id']==g15['decision_id'])['prompt_payload']['game_state']
g15check={'cash_if_accepted':[g15['author_cash_if_accepted'],g15['recipient_cash_if_accepted']],'houses_remaining':g15prompt['bank']['houses_remaining'],'cash_buys_one_green':233>=200,'cash_does_not_buy_three_greens':233<600,'scope':'Arithmetic and source reading only, no counterfactual engine execution or maximum-finance claim.'}

g2run=ROOT/next(r for r in offers if r['game']==2)['source_run']
g2events=[json.loads(l) for l in read(g2run/'events.jsonl').splitlines()]
spending=load(BASE/'data/t05_spending_units.json')
g2unit=next(r for r in spending if r['game']==2 and r['configuration']=='Sol' and r['group']=='YELLOW')
g2episode=next(r for r in episodes if r['game']==2 and r['model']=='Sol' and r['group']=='YELLOW')
g2rent=next(r for r in g2events if r['seq']==1566)
assert g2rent['type']=='RENT_PAID' and g2rent['payload']['amount']==44 and g2rent['payload']['to_player_id']=='p1'
g2rows=[json.loads(l) for l in file_lines[str(g2run/'decisions.jsonl')]]
g2d129=next(r for r in g2rows if r['phase']=='decision_resolved' and r['decision_id'].endswith('000129'))
g2check={'yellow_episode_paid_rent':g2episode['rent_until_loss_or_end'],'yellow_spending_unit':g2unit,'rent_event':g2rent,'d129_attempt_outcomes':[a.get('outcome') for a in g2d129['attempts']],'scope':'Retained accounting and original event inspection. Zero developed rent is not zero rent. No alternate continuation was evaluated.'}

baseline=load(BASE/'baseline_source_hashes.json')
changed=[p for p,h in baseline.items() if not (ROOT/p).exists() or digest((ROOT/p).read_bytes())!=h]
assert not changed
own_path=(BASE/'full_drafts/sol'/'../../../paper_draft_2026-10-29/artifacts/historical-claim-audit.zip').resolve()
report={'scope':'Fresh retained-data tabulations and original-field checks; no new evaluation or engine execution. Semantic codes and historical feasibility certificates remain inherited.','counteroffers':counter_summary,'offer_cells':cells,'configuration_cells':styles,'thread_position':positions,'cash':cash,'conflicts':conflicts,'economy':economy,'quote_checks':quote_checks,'g15':g15check,'g2':g2check,'preservation':{'frozen_sources':len(baseline),'changed':changed},'sol_artifact_path_exists':own_path.exists(),'sources':sources}
(HERE/'performed_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['quote_checks','sources','configuration_cells','offer_cells','thread_position']},indent=2))
