"""Second implementation, primarily driven by original delivered decision menus.

No import from the extension reducer and no engine execution. The reviewer read
the first implementation before writing this cross-check; implementation is
independent, expectations are not blinded.
"""
import collections
import copy
import hashlib
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
EXT=HERE.parents[1]/'negotiation'

def loadlines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]

def players(payload):
    state=payload['game_state']
    return {x['player_id']:x for x in [state['you'],*state['others']]}

board=json.loads((ROOT/'contracts/data/board.json').read_text())['spaces']
names={s['index']:re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_') for s in board}
space={names[s['index']]:s for s in board}
groups=collections.defaultdict(set)
for s in board:
    if s['kind']=='PROPERTY':groups[s['group']].add(names[s['index']])

def fullgroups(hold):
    return set(g for g, keys in groups.items() if keys.issubset(hold))

def calculate(start, action):
    payload=start['prompt_payload']; ps=players(payload)
    scen=payload['action_state']['scenario']; current=scen['current_offer']
    recipient=start['player_id']; author=current['from_player_id']
    receive=current['if_you_accept']['you_receive']; give=current['if_you_accept']['you_give']
    holdings={p:{d['space_key']:d for d in v['holdings']['owned']} for p,v in ps.items()}
    original=copy.deepcopy(holdings)
    assert set(receive['properties'])<=holdings[author].keys()
    assert set(give['properties'])<=holdings[recipient].keys()
    # Integer ceiling of ten percent of mortgage principal. Transfer charges
    # agree with float implementation at all board principals in this corpus.
    fees={author:0,recipient:0}
    for sender,receiver,bundle in [(author,recipient,receive),(recipient,author,give)]:
        for k in bundle['properties']:
            deed=holdings[sender].pop(k)
            if deed['mortgaged']: fees[receiver]+=(space[k]['price']+19)//20
            holdings[receiver][k]=deed
    net=receive['cash']-give['cash']
    balances={author:ps[author]['cash']-net-fees[author],recipient:ps[recipient]['cash']+net-fees[recipient]}
    delta={p:fullgroups(holdings[p])-fullgroups(original[p]) for p in (author,recipient)}
    broken={p:fullgroups(original[p])-fullgroups(holdings[p]) for p in (author,recipient)}
    new=(bool(delta[author]),bool(delta[recipient]))
    cell={(False,False):'neither',(True,False):'author_only',(False,True):'recipient_only',(True,True):'both'}[new]
    all_deeds={k:d for h in original.values() for k,d in h.items()}
    built_groups={space[k]['group'] for k,d in all_deeds.items() if d['houses'] or d['hotel']}
    tradable=all(not all_deeds[k]['houses'] and not all_deeds[k]['hotel'] and space[k]['group'] not in built_groups for k in receive['properties']+give['properties'])
    cards=(ps[author]['get_out_of_jail_cards']>=receive['get_out_of_jail_cards'] and ps[recipient]['get_out_of_jail_cards']>=give['get_out_of_jail_cards'])
    accept='accept_trade' in payload['action_state']['available_actions']
    assert accept==(min(balances.values())>=0 and tradable and cards)
    row={'decision_id':start['decision_id'],'decision':int(start['decision_id'].rsplit('-',1)[1]),'author':author,'recipient':recipient,'offer':receive,'request':give,'response':action['action']['action'],'accept_available':accept,'completion_cell':cell,
         'author_new_groups':sorted(delta[author]),'recipient_new_groups':sorted(delta[recipient]),'author_lost_groups':sorted(broken[author]),'recipient_lost_groups':sorted(broken[recipient]),
         'author_cash_if_accepted':balances[author],'recipient_cash_if_accepted':balances[recipient],
         'author_interest_if_accepted':fees[author],'recipient_interest_if_accepted':fees[recipient],
         'author_holdings_if_accepted':sorted(holdings[author]),'recipient_holdings_if_accepted':sorted(holdings[recipient])}
    return row,holdings,balances

def compare(row, supplied):
    for key,value in row.items():assert supplied[key]==value,(row['game'],row['decision'],key,value,supplied[key])

supplied={x['decision_id']:x for x in json.loads((EXT/'offers.json').read_text())}
runs=[]
for collection in ('railway-research-12-games-2026-10-25','railway-research-8-games-2026-10-26'):
    runs.extend((ROOT/'saved_games'/collection).glob('game-*/run'))
runs.sort(key=lambda p:int(p.parent.name.split('-')[1]))
assert len(runs)==20
ownrows=[]; threads=[]; flows=[]; sources={}; exceptions=[]; count=collections.Counter()
for run in runs:
    game=int(run.parent.name.split('-')[1])
    for name in ('decisions.jsonl','actions.jsonl','events.jsonl','summary.json','run_config.json'):
        p=run/name;sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    ds=loadlines(run/'decisions.jsonl'); starts={x['decision_id']:x for x in ds if x['phase']=='decision_started'}
    resolved={x['decision_id']:x for x in ds if x['phase']!='decision_started'}
    actions={x['decision_id']:x for x in loadlines(run/'actions.jsonl')}
    events=loadlines(run/'events.jsonl')
    winner=json.loads((run/'summary.json').read_text())['winner_player_id']
    alias={'openai/gpt-6.1-sol':'Sol','google/gemini-4-argon':'Gemini','anthropic/claude-opus-5.5':'Opus','x-ai/grok-4.7':'Grok'}
    models={p['player_id']:alias[p['openrouter_model_id']] for p in json.loads((run/'run_config.json').read_text())['players']}
    count['events']+=len(events);count['decisions']+=len(starts)
    local={}; expected_states={}
    for did,start in starts.items():
        if start['decision_type']!='TRADE_RESPONSE_DECISION':continue
        row,holdings,balances=calculate(start,actions[did]);row['game']=game
        row['author_model']=models[row['author']];row['recipient_model']=models[row['recipient']]
        compare(row,supplied[did]);local[did]=row;ownrows.append(row)
        assert supplied[did]['public_message']==actions[did]['action'].get('public_message','')
        assert supplied[did]['applied_private_note']==actions[did]['action'].get('private_thought','')
        count['full_applied_text_checks']+=1
        expected_states[did]=(holdings,balances)
        count['retries']+=resolved[did]['retry_used'];count['defaults']+=resolved[did]['fallback_used']
        count['action_only_responses']+=resolved[did]['sequence_meta'].get('response_condition')=='same_model_without_private_thought'
        if not row['accept_available']:
            exceptions.append({'row':row,'available_actions':start['prompt_payload']['action_state']['available_actions'],
                               'players':players(start['prompt_payload']),'public':actions[did]['action'].get('public_message'),'private':actions[did]['action'].get('private_thought')})
    current=None; pending=None; thread=None; pairs=collections.Counter(); owners={}; deaths=0
    for i,event in enumerate(events):
        typ=event['type']; p=event['payload']; actor=event['actor'].get('player_id')
        if typ=='LLM_DECISION_REQUESTED':current=p['decision_id']
        if typ=='TRADE_PROPOSED':
            assert thread is None
            pair=tuple(sorted([p['initiator_player_id'],p['counterparty_player_id']]))
            thread={'game':game,'start_seq':event['seq'],'start_turn':event['turn_index'],'initiator':actor,'initiator_model':models[actor],'counters':0,'prior_pair_threads':pairs[pair]}
            pairs[pair]+=1
        if typ in ('TRADE_COUNTERED','TRADE_ACCEPTED','TRADE_REJECTED'):
            assert thread is not None and pending is not None
            row=local[current]
            assert pending['actor']['player_id']==row['author']
            assert pending['payload']['offer']==row['offer'] and pending['payload']['request']==row['request']
            assert actor==row['recipient']
            count['orientation_checks']+=1
            if typ=='TRADE_COUNTERED':thread['counters']+=1
            else:
                thread.update(terminal=typ,terminal_seq=event['seq'],elapsed_turns=event['turn_index']-thread['start_turn'],final_author=row['author'])
                threads.append(thread);thread=None
            if typ=='TRADE_ACCEPTED':
                # Independently add actual immediate transaction deltas to the
                # delivered pre-state and compare predicted ownership/cash plus
                # the next original prompt. No branch execution is claimed.
                ps=players(starts[current]['prompt_payload'])
                bal={a:b['cash'] for a,b in ps.items()}
                hold={a:{d['space_key']:d for d in b['holdings']['owned']} for a,b in ps.items()}
                j=i+1
                while j<len(events) and events[j]['type']!='LLM_DECISION_REQUESTED':
                    after=events[j];ap=after['payload']
                    if after['type']=='CASH_CHANGED':bal[ap['player_id']]+=ap['delta']
                    if after['type']=='PROPERTY_TRANSFERRED':
                        k=names[ap['space_index']];hold[ap['to_player_id']][k]=hold[ap['from_player_id']].pop(k)
                    j+=1
                expected_hold,expected_cash=expected_states[current]
                next_ps=players(starts[events[j]['payload']['decision_id']]['prompt_payload'])
                for actor in (row['author'],row['recipient']):
                    assert bal[actor]==expected_cash[actor]==next_ps[actor]['cash']
                    assert hold[actor]==expected_hold[actor]=={d['space_key']:d for d in next_ps[actor]['holdings']['owned']}
                assert next_ps[row['author']]['get_out_of_jail_cards']==ps[row['author']]['get_out_of_jail_cards']-row['offer']['get_out_of_jail_cards']+row['request']['get_out_of_jail_cards']
                assert next_ps[row['recipient']]['get_out_of_jail_cards']==ps[row['recipient']]['get_out_of_jail_cards']+row['offer']['get_out_of_jail_cards']-row['request']['get_out_of_jail_cards']
                count['accepted_state_checks']+=1
                for actor,bundle in [(row['recipient'],row['offer']),(row['author'],row['request'])]:
                    if bundle['cash']:flows.append(('trade_cash',bundle['cash'],actor==winner,False))
        if typ in ('TRADE_PROPOSED','TRADE_COUNTERED'):pending=event
        if typ=='CASH_CHANGED' and p['reason']=='BANKRUPTCY':deaths+=1
        if typ=='CASH_CHANGED' and p['reason']=='BANKRUPTCY_CASH' and p['delta']<0:
            nxt=events[i+1];np=nxt['payload']
            receiver=np['player_id'] if nxt['type']=='CASH_CHANGED' and np.get('reason')=='BANKRUPTCY_CASH' and np['delta']==-p['delta'] else 'BANK'
            flows.append(('estate_cash',-p['delta'],receiver==winner,deaths==2))
        if typ=='PROPERTY_PURCHASED':
            key=p['space_index']
            if owners.get(key) is not None:
                assert p['price']==0
                flows.append(('estate_deed',1,p['player_id']==winner,deaths==3))
            owners[key]=p['player_id']
        if typ=='PROPERTY_TRANSFERRED':
            assert owners[p['space_index']]==p['from_player_id']
            owners[p['space_index']]=p['to_player_id']
            flows.append(('trade_deed',1,p['to_player_id']==winner,False))
        if typ=='CASH_CHANGED' and p['reason']=='BANKRUPTCY_ASSETS_TO_BANK':
            owners={k:v for k,v in owners.items() if v!=p['player_id']}
        if typ=='RENT_PAID':flows.append(('paid_rent',p['amount'],p['to_player_id']==winner,False))
    assert thread is None and deaths==3

assert len(ownrows)==len(supplied)
legal=[r for r in ownrows if r['accept_available']]
selfs=[r for r in legal if r['recipient_new_groups']]
both=[r for r in legal if r['completion_cell']=='both']
table={}
for cell in ('neither','author_only','recipient_only','both'):
    table[cell]=dict(collections.Counter(r['response'] for r in legal if r['completion_cell']==cell))
flow_results={}
for kind in sorted(set(x[0] for x in flows)):
    xs=[x for x in flows if x[0]==kind]
    flow_results[kind]={'events':len(xs),'amount':sum(x[1] for x in xs),'winner_amount':sum(x[1] for x in xs if x[2])}
    if kind.startswith('estate'):
        flow_results[kind]['nonterminal_amount']=sum(x[1] for x in xs if not x[3])
        flow_results[kind]['nonterminal_winner_amount']=sum(x[1] for x in xs if not x[3] and x[2])

# Mutation checks test this reviewer's full-field comparator, not the original
# reducer. Alter fields in a copy; require detection without touching sources.
mutations={}
target=next(r for r in ownrows if r['recipient_new_groups'])
for key,value in [('recipient_new_groups',[]),('recipient_cash_if_accepted',target['recipient_cash_if_accepted']+1),('author',target['recipient']),('accept_available',not target['accept_available']),('response','invented_action')]:
    bad=copy.deepcopy(supplied[target['decision_id']]);bad[key]=value
    try:compare(target,bad)
    except AssertionError:mutations[key]=True
    else:mutations[key]=False
assert all(mutations.values())

out={'scope':'Independent implementation from original decision menus, actions and events; no engine replay, paid call, full-prompt semantic validation or confidence interval.',
     'checks':dict(count),'threads':len(threads),'responses':len(ownrows),'acceptance_legal':len(legal),
     'responses_by_action':dict(collections.Counter(r['response'] for r in ownrows)),
     'own_completion':dict(collections.Counter(r['response'] for r in selfs)),
     'both_completion':dict(collections.Counter(r['response'] for r in both)),
     'completion_table':table,'own_completion_breaking_old_group':sum(bool(r['recipient_lost_groups']) for r in selfs),
     'rejected_own_completion_breaking_old_group':sum(bool(r['recipient_lost_groups']) and r['response']=='reject_trade' for r in selfs),
     'threads_with_counters':sum(t['counters']>0 for t in threads),'settled_after_counters':sum(t['counters']>0 and t['terminal']=='TRADE_ACCEPTED' for t in threads),
     'settled_final_author_changed':sum(t['final_author']!=t['initiator'] and t['terminal']=='TRADE_ACCEPTED' for t in threads),
     'max_counters':max(t['counters'] for t in threads),'max_elapsed_turns':max(t['elapsed_turns'] for t in threads),
     'repeat_pair_threads':sum(t['prior_pair_threads']>0 for t in threads),'flow_results':flow_results,'mutation_checks':mutations,'source_hashes':sources}
out['model_counts']={m:{'responses':len([r for r in ownrows if r['recipient_model']==m]),
                        'response_types':dict(collections.Counter(r['response'] for r in ownrows if r['recipient_model']==m)),
                        'initiated':sum(t['initiator_model']==m for t in threads),
                        'initiated_settled':sum(t['initiator_model']==m and t['terminal']=='TRADE_ACCEPTED' for t in threads)} for m in alias.values()}
out['longest_threads']=[t for t in threads if t['counters']==out['max_counters']]
(HERE/'independent_census.json').write_text(json.dumps(out,indent=2)+'\n')
(HERE/'independent_offer_rows.json').write_text(json.dumps(ownrows,indent=2)+'\n')
(HERE/'edge_cases.json').write_text(json.dumps(exceptions,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='source_hashes'},indent=2))
