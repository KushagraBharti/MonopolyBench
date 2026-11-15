"""Read retained records only. No engine, replay, model, or simulation imports.

Exploratory tabulations fixed here before inspecting their output. Historical
episodes and offer reconstructions are inherited; new counts join them to events.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import statistics as st

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parents[1]
OLD = ROOT / 'docs/research_raw/paper_rewrite_2026-11-10'
HASHES = {}


def read(path, lines=False):
    blob = path.read_bytes()
    HASHES[str(path.relative_to(ROOT))] = hashlib.sha256(blob).hexdigest()
    return [json.loads(x) for x in blob.splitlines() if x.strip()] if lines else json.loads(blob)


def median(xs):
    return st.median(xs) if xs else None


def response_table(rows):
    out = {}
    for cell in ['author_only', 'recipient_only', 'both', 'neither']:
        for stage in ['all', 'opening', 'later']:
            rs = [r for r in rows if r['completion_cell'] == cell and
                  (stage == 'all' or (r['exchange_index'] == 0) == (stage == 'opening'))]
            c = collections.Counter(r['response'] for r in rs)
            out[f'{cell}/{stage}'] = dict(n=len(rs), **c)
    return out


def main():
    offers = read(OLD / 'data/agenda_offers.json')
    legal = [r for r in offers if r['accept_available']]
    assert len(offers) == 920 and len(legal) == 918
    board = read(ROOT / 'contracts/data/board.json')
    spaces = {s['index']: s for s in board['spaces']}
    keys = {re.sub(r'[^A-Z0-9]+', '_', s['name'].upper()).strip('_'): s for s in spaces.values()}
    costs = board['house_cost_by_group']
    out = {'scope': 'Exploratory arithmetic on the frozen twenty-game corpus, not new evaluations.',
           'responses': response_table(legal), 'by_recipient': {}, 'leave_one_block_out': {}}
    for name in ['Sol', 'Gemini', 'Opus', 'Grok']:
        out['by_recipient'][name] = response_table([r for r in legal if r['recipient_model'] == name])
    for block in range(1, 6):
        out['leave_one_block_out'][block] = response_table([r for r in legal if (r['game']-1)//4+1 != block])

    prices = []
    for r in legal:
        a, b = r['offer'], r['request']
        if a['get_out_of_jail_cards'] or b['get_out_of_jail_cards']:
            continue
        kind = None
        if not a['properties'] and len(b['properties']) == 1 and a['cash'] > 0 and b['cash'] == 0:
            kind, deed, cash, completes = 'bid', b['properties'][0], a['cash'], bool(r['author_new_groups'])
        if len(a['properties']) == 1 and not b['properties'] and b['cash'] > 0 and a['cash'] == 0:
            kind, deed, cash, completes = 'ask', a['properties'][0], b['cash'], bool(r['recipient_new_groups'])
        if kind:
            prices.append(dict(game=r['game'], decision=r['decision'], thread=r['thread_id'],
                               author=r['author_model'], recipient=r['recipient_model'], kind=kind,
                               deed=deed, cash=cash, ratio=cash/keys[deed]['price'], completes=completes,
                               mortgaged=bool(r['author_interest_if_accepted']+r['recipient_interest_if_accepted']),
                               stage='opening' if r['exchange_index']==0 else 'later'))
    out['price_cells'] = []
    for kind in ['ask', 'bid']:
        for author in ['Sol', 'Gemini', 'Opus', 'Grok']:
            for mortgage in [False, True]:
                for stage in ['all', 'opening', 'later']:
                    row = dict(kind=kind, author=author, mortgaged=mortgage, stage=stage)
                    for completes in [False, True]:
                        rs = [r for r in prices if r['kind']==kind and r['author']==author and
                              r['mortgaged']==mortgage and r['completes']==completes and
                              (stage=='all' or r['stage']==stage)]
                        row[str(completes)] = dict(n=len(rs), median_ratio=median([r['ratio'] for r in rs]))
                    if row['False']['n'] or row['True']['n']: out['price_cells'].append(row)
    matched = []
    for key in sorted(set((r['game'],r['author'],r['deed']) for r in prices if r['kind']=='ask')):
        rs=[r for r in prices if r['kind']=='ask' and (r['game'],r['author'],r['deed'])==key]
        a=[r['cash'] for r in rs if r['completes']]; b=[r['cash'] for r in rs if not r['completes']]
        if a and b: matched.append(dict(key=key, completing_n=len(a), other_n=len(b),
                                       completing_median=median(a), other_median=median(b)))
    out['same_seller_game_deed_asks']=matched

    eps = read(ROOT / 'docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl', True)
    windows = read(OLD / 'data/first_management_windows.json')['rows']
    win = {(r['game'],r['player'],r['group']):r for r in windows}
    runs = {r['game']: ROOT/r['source_run'] for r in offers}
    debts, exposures, first_estates = [], [], []
    for game, run in sorted(runs.items()):
        events=read(run/'events.jsonl',True)
        assert all(e['seq']==i for i,e in enumerate(events))
        dr=read(run/'decisions.jsonl',True)
        starts={r['decision_id']:r for r in dr if r['phase']=='decision_started'}
        resolutions={r['decision_id']:r for r in dr if r['phase']=='decision_resolved'}
        assert len(starts)==len(resolutions)
        active=None
        for d in starts.values():
            if d['decision_type']!='LIQUIDATION_DECISION':
                assert active is None, (game, 'unclosed liquidation', active)
                continue
            s=d['prompt_payload']['action_state']['scenario']; who=d['player_id']
            sig=(who,d['turn_index'],s['owed_amount'],s.get('owed_to_player_id'),s['reason'])
            if active is None:
                y=d['prompt_payload']['game_state']['you']; owned=y['holdings']['owned']
                salvage=sum((5 if h['hotel'] else h['houses'])*costs.get(keys[h['space_key']]['group'],0)//2 for h in owned)
                mortgage=sum(keys[h['space_key']]['price']//2 for h in owned if not h['mortgaged'])
                active=dict(game=game,signature=sig,model=d['model_display_name'],player=who,
                            first_decision=int(d['decision_id'].split('-')[-1]),turn=d['turn_index'],
                            cash=y['cash'],debt=s['owed_amount'],reason=s['reason'],
                            upper_bound=y['cash']+salvage+mortgage,actions=[],decisions=[],fallback_actions=0)
            assert tuple(active['signature'])==sig
            r=resolutions[d['decision_id']]
            active['actions'].append(r['final_action']['action']); active['decisions'].append(d['decision_id'])
            active['fallback_actions']+=int(r['fallback_used'])
            ev=[e for e in events[r['emitted_event_seq_start']:r['emitted_event_seq_end']+1]
                if e['type']=='CASH_CHANGED' and e['payload']['player_id']==who]
            bankrupt=any(e['payload']['reason'] in ['BANKRUPTCY','BANKRUPTCY_ASSETS_TO_BANK'] for e in ev)
            paid=any(e['payload']['delta']==-s['owed_amount'] and e['payload']['reason']==s['reason'] for e in ev)
            assert not (bankrupt and paid), (game,d['decision_id'])
            if bankrupt or paid:
                active.update(outcome='bankrupt' if bankrupt else 'paid',last_seq=r['emitted_event_seq_end'])
                debts.append(active);active=None
        assert active is None
        for ep in [r for r in eps if r['game']==game and r['route']=='trade']:
            lo,hi=ep['settlement_end_seq'],ep['end_seq_exclusive']
            ev=[e for e in events if lo<e['seq']<hi]
            rent=[e for e in ev if e['type']=='RENT_PAID' and e['payload']['to_player_id']==ep['player_id'] and spaces[e['payload']['space_index']]['group']==ep['group']]
            assert sum(e['payload']['amount'] for e in rent)==ep['rent_until_loss_or_end']
            opp_moves=[e for e in ev if e['type']=='PLAYER_MOVED' and e['actor'].get('player_id')!=ep['player_id']]
            w=win[(game,ep['player_id'],ep['group'])]
            exposures.append(dict(game=game,player=ep['player_id'],model=ep['model'],group=ep['group'],
                                  early=w['built_first_mgmt_turn'],rent=ep['rent_until_loss_or_end'],
                                  rent_payments=len(rent),opponent_movements=len(opp_moves),
                                  acquisition_turn=ep['acquisition_turn'],first_build_turn=ep['first_build_turn'],
                                  end_turn=events[min(hi,len(events)-1)]['turn_index']))
        # Snapshot at the first bankruptcy cash event, before receiving its estate.
        cash={f'p{i}':1500 for i in range(1,5)}; owner={i:None for i in spaces}; levels={i:0 for i in spaces}
        summary=read(run/'summary.json'); first=True
        for e in events:
            p=e['payload'];t=e['type']
            if t=='CASH_CHANGED' and p['reason']=='BANKRUPTCY' and first:
                # The request immediately preceding the elimination supplies creditor.
                prior=[d for d in starts.values() if resolutions[d['decision_id']]['emitted_event_seq_start']<=e['seq']]
                d=prior[-1];s=d['prompt_payload']['action_state']['scenario']; creditor=s.get('owed_to_player_id')
                state=d['prompt_payload']['game_state']
                # Use the delivered state before the eliminating action: residual
                # bankruptcy cash can already have moved before its marker event.
                stats={p['player_id']:dict(cash=p['cash'],deeds=len(p['holdings']['owned']),
                               building_levels=sum(5 if h['hotel'] else h['houses'] for h in p['holdings']['owned']))
                       for p in [state['you'],*state['others']]}
                first_estates.append(dict(game=game,seq=e['seq'],turn=e['turn_index'],creditor=creditor,
                                          winner=summary['winner_player_id'],positions=stats));first=False
            if t=='CASH_CHANGED': cash[p['player_id']]+=p['delta']
            elif t=='PROPERTY_PURCHASED': owner[p['space_index']]=p['player_id']
            elif t=='PROPERTY_TRANSFERRED': owner[p['space_index']]=p['to_player_id']
            elif t=='HOUSE_BUILT': levels[p['space_index']]+=p['count']
            elif t=='HOTEL_BUILT': levels[p['space_index']]=5
            elif t=='HOUSE_SOLD': levels[p['space_index']]-=p['count']
            elif t=='HOTEL_SOLD': levels[p['space_index']]=4
        assert not first
    out['liquidation_summary']={k:dict(n=sum(r['outcome']==k for r in debts),
             decisions=sum(len(r['decisions']) for r in debts if r['outcome']==k),
             fallback_actions=sum(r['fallback_actions'] for r in debts if r['outcome']==k),
             bound_sufficient=sum(r['upper_bound']>=r['debt'] for r in debts if r['outcome']==k),
             action_counts=dict(collections.Counter(a for r in debts if r['outcome']==k for a in r['actions']))) for k in ['paid','bankrupt']}
    out['exposure_summary']={str(early):dict(n=len(rs),rent=sum(r['rent'] for r in rs),
             median_opponent_movements=median([r['opponent_movements'] for r in rs]),
             median_remaining_turns=median([r['end_turn']-r['acquisition_turn'] for r in rs]),
             median_rent=median([r['rent'] for r in rs]),median_acquisition_turn=median([r['acquisition_turn'] for r in rs]),
             median_rent_per_opponent_movement=median([r['rent']/r['opponent_movements'] for r in rs if r['opponent_movements']]))
             for early in [True,False] for rs in [[r for r in exposures if r['early']==early]]}
    out['first_estate_summary']={'n':len(first_estates),'creditor_eventual_winner':sum(r['creditor']==r['winner'] for r in first_estates)}
    for measure in ['cash','deeds','building_levels']:
        out['first_estate_summary'][measure+'_creditor_tied_top']=sum(r['positions'][r['creditor']][measure]==max(x[measure] for x in r['positions'].values()) for r in first_estates)
        out['first_estate_summary'][measure+'_creditor_strict_top']=sum(r['positions'][r['creditor']][measure]>max(x[measure] for p,x in r['positions'].items() if p!=r['creditor']) for r in first_estates)
    for name,data in [('analysis',out),('single_deed_prices',prices),('liquidation_episodes',debts),('trade_group_exposure',exposures),('first_estates',first_estates),('source_hashes',HASHES)]:
        (HERE/'data'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['liquidation_summary','exposure_summary','first_estate_summary']},indent=2))


if __name__=='__main__': main()
