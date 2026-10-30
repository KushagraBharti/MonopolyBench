"""Build the complete manually coded ledger and exact canonical suffix witnesses.

This reducer links manual semantic decisions; it does not classify language.
It reads existing artifacts and writes only to this analysis directory.
"""
from collections import Counter
from hashlib import sha256
import csv
import json

from extract_sample import ROOT, OUT
from inspect_followups import load_games, context
from manual_coding import CODING
from endpoint_coding import LANDING_POLICIES, TRACES, UNSCORABLE, FORECAST_TYPE, FORECAST_TRACES

NAMES = {'anthropic/claude-opus-5.5':'Opus', 'x-ai/grok-4.7':'Grok',
         'google/gemini-4-argon':'Gemini', 'openai/gpt-6.1-sol':'Sol'}
CONFLICT_PATH = ROOT/'docs/research_raw/paper_phase2_2026-10-28/core_review/sol/received_name_conflict_audit.json'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def main():
    sample, games = load_games()
    assert len(sample) == len(CODING) == 240
    assert set(CODING) == {r['id'] for r in sample}
    assert set(FORECAST_TYPE) == {k for k,v in CODING.items() if 'O' in v[0]}
    assert set(LANDING_POLICIES)|set(TRACES)|set(UNSCORABLE) == {k for k,v in CODING.items() if 'P' in v[0]}
    assert not set(LANDING_POLICIES)&set(TRACES)
    assert not (set(LANDING_POLICIES)|set(TRACES))&set(UNSCORABLE)
    assert all(v==12 for v in Counter(r['game'] for r in sample).values())
    assert all(v==3 for v in Counter((r['game'],r['player_id']) for r in sample).values())

    conflict_source=json.loads(CONFLICT_PATH.read_text())
    conflicts={r['decision_id']:r for r in conflict_source['all_named_conflicts']}
    hashes={}
    indices={}
    for g,rows in games.items():
        run=ROOT/next(r['source_run'] for r in sample if r['game']==g)
        idx={}
        for name in ['actions.jsonl','decisions.jsonl','events.jsonl']:
            p=run/name
            hashes[str(p.relative_to(ROOT))]=digest(p)
            values=[json.loads(x) for x in p.read_text().splitlines()]
            if name=='actions.jsonl':
                idx['actions']={int(x['decision_id'].rsplit('-',1)[1]):(i,x) for i,x in enumerate(values,1)}
            elif name=='decisions.jsonl':
                idx['starts']={x['decision_id']:i for i,x in enumerate(values,1) if x['phase']=='decision_started'}
                idx['resolves']={x['decision_id']:i for i,x in enumerate(values,1) if x['phase']=='decision_resolved'}
            else:
                idx['events']={x['seq']:i for i,x in enumerate(values,1)}
        indices[g]=idx

    def witness(g,d):
        line,a=indices[g]['actions'][d]
        start=games[g]['starts'][a['decision_id']]
        res=games[g]['resolves'][a['decision_id']]
        p=start['prompt_payload']
        run=next(r['source_run'] for r in sample if r['game']==g)
        events=[e for e in games[g]['events'] if res['emitted_event_seq_start']<=e['seq']<=res['emitted_event_seq_end']]
        return {'game':g,'decision_index':d,'decision_id':a['decision_id'],
                'actor':a['actor_player_id'],'turn':a['turn_index'],
                'decision_type':a['decision_type'], 'action':a['action'],
                'cash_before':p['game_state']['you']['cash'],
                'position_before':p['game_state']['you']['position'],
                'holdings_before':p['game_state']['you']['holdings'],
                'bank_before':p['game_state']['bank'], 'menu':p['action_state'],
                'fallback_used':res['fallback_used'],
                'events':events,
                'field_sha256':{k:sha256(str(a['action'][k]).encode()).hexdigest() for k in ['public_message','private_thought'] if a['action'].get(k) is not None},
                'source':{'actions':run+'/actions.jsonl','action_line':line,
                          'decisions':run+'/decisions.jsonl','started_line':indices[g]['starts'][a['decision_id']],
                          'resolved_line':indices[g]['resolves'][a['decision_id']],
                          'events':run+'/events.jsonl','event_lines':[indices[g]['events'][e['seq']] for e in events]},
                'retained_named_conflict': None if a['decision_id'] not in conflicts else {
                    'content_name':conflicts[a['decision_id']]['content_name'],
                    'received_name':conflicts[a['decision_id']]['received_tool_name'],
                    'audit_source':str(CONFLICT_PATH.relative_to(ROOT)),
                    'independently_reparsed_here':False}}

    landing=[]
    traces=[]
    forecasts=[]
    ledger=[]
    for r in sample:
        tags,note=CODING[r['id']]
        row=dict(r)
        row['semantic_tags']=list(tags)
        row['semantic_note']=note
        row['coding_method']='manual reading of the complete two scoped fields; not keyword classification'
        row['statement_scope']={
            'speaker':r['player_id'],
            'own_plan_target':'self' if 'P' in tags else None,
            'opponent_target':'exact player references in the complete source passage; not collapsed into one inferred mental state' if 'O' in tags else None,
            'condition_and_horizon':'retained verbatim in complete scoped fields; operationalized only in the separate endpoint adjudication',
            'quotes':[{'channel':field,'text':entry['value'],'sha256':entry['sha256'],
                       'source_json_pointer':entry['json_pointer']}
                      for field,entry in r['fields'].items() if entry['present']],
            'single_proposition_accuracy_estimated':False}
        row['private_note_source']='absent' if not r['fields']['private_thought']['present'] else ('synthetic_fallback' if r['fallback_used'] else 'received_applied_action_field')
        row['provider_summary_semantically_coded']=False
        row['retained_named_conflict']=None if r['decision_id'] not in conflicts else {
            'content_name':conflicts[r['decision_id']]['content_name'],
            'received_name':conflicts[r['decision_id']]['received_tool_name'],
            'source':str(CONFLICT_PATH.relative_to(ROOT)), 'independently_reparsed_here':False}
        row['next_own_context']=context(r,games[r['game']],12) if set(tags)&{'P','O','R'} else []
        row['context_scope']='mechanically retained; semantic endpoint claims only where separately adjudicated'
        row['plan_endpoint']=None
        if r['id'] in LANDING_POLICIES:
            targets=LANDING_POLICIES[r['id']]
            opportunities=[]
            for d,(line,a) in indices[r['game']]['actions'].items():
                if d<=r['decision_index'] or a['actor_player_id']!=r['player_id'] or a['decision_type']!='BUY_OR_AUCTION_DECISION':
                    continue
                p=games[r['game']]['starts'][a['decision_id']]['prompt_payload']
                if p['action_state']['scenario']['landed_space'] in targets:
                    opportunities.append(witness(r['game'],d))
            item={'id':r['id'],'target_deeds':targets,'endpoint_rule':'first subsequent actual own BUY_OR_AUCTION_DECISION on a named target, to end of recorded game',
                  'all_matching_opportunities':opportunities,
                  'status':'no_observed_opportunity' if not opportunities else ('purchase_applied' if opportunities[0]['action']['action']=='buy_property' else 'purchase_not_applied'),
                  'not_a_memory_score':True,
                  'limit':'An absent opportunity is not nonadherence; intervening state changes are not controlled. The two repeated G6 statements are separate rows, not independent episodes.'}
            if r['id']=='G16d000103':
                item['interpretation']='At d159 purchase remains legal and affordable. The applied note recommends buying while the applied action starts an auction. Another actor bids380 at d162 and receives Virginia after d164. Do not label this observed endpoint a chosen abandonment.'
                item['auction_resolution']=[witness(16,d) for d in range(160,166)]
            landing.append(item)
            row['plan_endpoint']=item
        elif r['id'] in TRACES:
            ds,status,interpretation=TRACES[r['id']]
            item={'id':r['id'],'status':status,'interpretation':interpretation,
                  'selection':'illustrative chronology, not probability sampled and not a denominator for adherence',
                  'source':witness(r['game'],r['decision_index']),
                  'followups':[witness(r['game'],d) for d in ds]}
            traces.append(item)
            row['plan_endpoint']={'status':status,'interpretation':interpretation,'followup_decisions':ds}
        elif 'P' in tags:
            row['plan_endpoint']={'status':'unscorable_as_single_commitment','reason':UNSCORABLE[r['id']],
                                  'what_is_retained':'next twelve actual own decisions, or all remaining if fewer',
                                  'what_is_not_claimed':'a tested failure, success, persistent plan, or absence of subsequent planning'}
        if 'O' in tags:
            row['forecast_type']=FORECAST_TYPE[r['id']]
            row['forecast_scoring']='not pooled: possibility, feasibility, conditional outcome and private intent are different targets'
            if r['id'] in FORECAST_TRACES:
                ds,interpretation=FORECAST_TRACES[r['id']]
                item={'id':r['id'],'interpretation':interpretation,'followups':[witness(r['game'],d)for d in ds]}
                if r['id']=='G03d000207':
                    item['turn_timing_events']=[e for e in games[3]['events'] if e['seq'] in [1486,1494]]
                forecasts.append(item)
                row['forecast_endpoint']={'followup_decisions':ds,'interpretation':interpretation}
            else:
                row['forecast_endpoint']={'status':'not_scored','reason':'No single elicited, horizon-bounded behavioral prediction with controlled opportunity. Financial/path claims require a different target than beliefs or chosen actions.'}
        ledger.append(row)

    # Nontrivial original-record assertions for the selected longitudinal claims.
    checks=[]
    def check(label,condition):
        assert condition,label
        checks.append(label)
    def a(g,d):return witness(g,d)['action']
    def cash(g,d):return witness(g,d)['cash_before']
    check('landing subset exactly eight statement rows',len(landing)==8)
    check('six no-opportunity rows and two actual target menus',Counter(x['status']for x in landing)=={'no_observed_opportunity':6,'purchase_applied':1,'purchase_not_applied':1})
    check('G16 target source cash and legal menu',cash(16,159)==371 and 'buy_property' in witness(16,159)['menu']['available_actions'])
    check('G16 received auction despite buy note',a(16,159)['action']=='start_auction' and 'Buy at list is the only way' in a(16,159)['private_thought'])
    check('G16 rival actual winning bid',a(16,162)['args']['bid_amount']==380 and any(e['type']=='AUCTION_ENDED' and e['payload'].get('winner_player_id')=='p4' and e['payload']['winning_bid']==380 for e in witness(16,164)['events']))
    check('G14 brown later layers and endpoint cash',all(a(14,d)['action']=='build_houses_or_hotel'for d in [146,147,148]) and cash(14,149)==619)
    check('G14 debt next mortgage and endpoint',a(14,191)['args']['space_key']=='MARVIN_GARDENS' and cash(14,192)==20)
    check('G18 debt next mortgage and endpoint',a(18,429)['args']['space_key']=='KENTUCKY_AVENUE' and cash(18,430)==69)
    check('G20 sale attempt then mortgage endpoint',a(20,100)['action']=='propose_trade' and a(20,101)['action']=='reject_trade' and a(20,102)['args']['space_key']=='VERMONT_AVENUE' and cash(20,103)==157)
    check('G20 source bound and revised-bound admission',a(20,42)['args']['bid_amount']==230 and a(20,44)['args']['bid_amount']==232 and 'Prior note said drop' in a(20,44)['private_thought'] and a(20,46)['action']=='drop_out')
    check('G17 forced auction endpoint above cash ceiling',a(17,231)['args']['bid_amount']==100 and cash(17,232)==99 and a(17,232)['action']=='drop_out')
    check('G17 auction ceilings exceeded then revised',a(17,166)['args']['bid_amount']==410 and a(17,169)['args']['bid_amount']==500 and a(17,172)['action']=='drop_out')
    check('G17 financing then hold then partial build',a(17,237)['action']=='end_turn' and cash(17,237)==174 and a(17,241)['args']['build_plan']==[{'space_key':'ORIENTAL_AVENUE','kind':'HOUSE','count':1}])
    check('G19 rejected raise then hold',a(19,93)['action']=='reject_trade' and a(19,94)['action']=='end_turn' and "Don't raise Indiana before the roll" in a(19,94)['private_thought'])
    check('G19 three layers endpoint',all(a(19,d)['action']=='build_houses_or_hotel'for d in [234,235,236]) and cash(19,237)==262)
    check('G12 improved offer followed by reject and stop',a(12,132)['action']=='reject_trade' and a(12,133)['action']=='end_turn' and 'stop bidding against myself' in a(12,133)['private_thought'])
    check('G15 brown policy next-step revision','Do not build browns' in a(15,143)['private_thought'] and a(15,144)['action']=='build_houses_or_hotel')
    check('G20 conditional trade rejected',a(20,257)['action']=='reject_trade' and a(20,258)['action']=='end_turn')
    check('G3 forecast stock endpoint',witness(3,208)['bank_before']['houses_remaining']==3 and witness(3,208)['position_before']=='SHORT_LINE')
    check('G3 first endpoint precedes rival action',indices[3]['actions'][207][1]['actor_player_id']==indices[3]['actions'][208][1]['actor_player_id']=='p1' and next(e for e in games[3]['events'] if e['seq']==1486)['payload']['is_double'])
    check('G3 later stock endpoint follows each rival',{indices[3]['actions'][d][1]['actor_player_id']for d in [209,210,211]}=={'p2','p3','p4'} and witness(3,213)['bank_before']['houses_remaining']==3)
    rival_suffix=[d for d,(_,action) in indices[17]['actions'].items() if d>232 and action['actor_player_id']=='p1']
    check('G17 complete rival suffix through elimination',rival_suffix==[238,243,246,252,253,254,255,256,257,261,264,267] and a(17,267)['action']=='declare_bankruptcy')
    check('G17 no delivered build menu after auction',all('build_houses_or_hotel' not in witness(17,d)['menu']['available_actions']for d in rival_suffix) and cash(17,257)==63)
    check('G2 predicted auction opponent withdrawals',a(2,162)['action']=='drop_out' and a(2,163)['action']=='drop_out')
    dark_blue={h['space_key']:h['houses'] for h in witness(9,164)['holdings_before']['owned'] if h['space_key'] in ['PARK_PLACE','BOARDWALK']}
    check('G9 long goal reaches three houses each',cash(9,164)==17 and dark_blue=={'PARK_PLACE':3,'BOARDWALK':3})
    check('no sampled engine defaults or literal fallback notes',not any(r['fallback_used'] or (r['fields']['private_thought']['value']or'').strip().lower()=='fallback' for r in sample))

    bymodel={}
    for model in NAMES:
        rows=[r for r in ledger if r['model']==model]
        bymodel[NAMES[model]]={'sampled':len(rows),'private_absent':sum(not r['fields']['private_thought']['present']for r in rows),
            'synthetic_fallback_notes':sum(r['private_note_source']=='synthetic_fallback'for r in rows),
            'named_conflict_rows':sum(r['retained_named_conflict']is not None for r in rows),
            'codes':dict(Counter(c for r in rows for c in r['semantic_tags']))}
    results={'population':'240 fixed public-unflagged decisions; three SHA-ranked selections per player-game, not 200/40 sampling strata',
             'scope':'complete public_message and applied private_thought; provider summaries excluded',
             'counts':{'sampled':240,'private_absent':sum(not r['fields']['private_thought']['present']for r in sample),
                       'synthetic_fallback_notes':0,'codes':dict(Counter(c for r in ledger for c in r['semantic_tags'])),
                       'named_conflicts':sum(r['retained_named_conflict']is not None for r in ledger),
                       'landing_policy_rows':len(landing),'landing_endpoint_counts':dict(Counter(x['status']for x in landing)),
                       'illustrative_plan_chronologies':len(traces),'unscorable_prospective_rows':len(UNSCORABLE),
                       'forecast_candidates':len(FORECAST_TYPE),'forecast_event_checks':len(forecasts)},
             'by_model':bymodel,'forecast_types':dict(Counter(FORECAST_TYPE.values())),
             'interpretation':'Category presence is not correctness, planning quality, theory of mind, learning, or a model ranking. Unequal channel availability constrains cross-model comparisons.'}
    (OUT/'row_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ledger))
    dump('landing_policy_endpoints.json',landing)
    dump('longitudinal_witnesses.json',traces)
    dump('forecast_endpoints.json',forecasts)
    dump('results.json',results)
    hashes[str(CONFLICT_PATH.relative_to(ROOT))]=digest(CONFLICT_PATH)
    for p in OUT.glob('*.py'):
        hashes[str(p.relative_to(ROOT))]=digest(p)
    dump('source_hashes.json',hashes)
    dump('validation.json',{'assertions_passed':len(checks),'assertions':checks,'full_primary_fields_read':240,
                            'original_actions_matched':240,'manual_coder_count':1,
                            'engine_branches_executed_in_this_extension':0,
                            'provider_summary_reads_in_primary_coding':0,
                            'sampling_design_correction_recorded_before_primary_fields':True})
    with (OUT/'channel_inventory.csv').open('w')as f:
        w=csv.writer(f)
        w.writerow(['configuration','sampled','private_absent','synthetic_fallback_notes','P','O','R','named_conflicts'])
        for name,m in bymodel.items():
            w.writerow([name,m['sampled'],m['private_absent'],m['synthetic_fallback_notes'],m['codes'].get('P',0),m['codes'].get('O',0),m['codes'].get('R',0),m['named_conflict_rows']])
    print(json.dumps({'results':results['counts'],'validation_assertions':len(checks)}))


if __name__=='__main__':
    main()
