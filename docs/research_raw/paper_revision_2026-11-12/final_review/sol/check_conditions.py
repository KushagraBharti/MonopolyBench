"""Read historical configuration and incident evidence; do not execute games."""
from check_saved_records import records, offers, ROOT, PAPER, OUT, read, co, json, re

result={}
intents=co.Counter();settings=co.Counter()
for collection in sorted((ROOT/'saved_games').glob('railway-research-*-games-2026-10-*')):
    for p in sorted(collection.glob('game-*/cloud/calls/*.intent.json')):
        o=read(p);body=o.get('payload') or o.get('request_payload') or o.get('request') or o
        if 'model' not in body:body=o.get('request_body',body)
        intents[(body.get('model'),body.get('tool_choice'))]+=1
        settings[(json.dumps(body.get('reasoning'),sort_keys=True),body.get('parallel_tool_calls'),'temperature' in body,'top_p' in body,'max_tokens' in body)]+=1
result['requests']=dict(count=sum(intents.values()),model_and_choice=[[list(k),v] for k,v in intents.items()],settings=[[list(k),v] for k,v in settings.items()])
scenario=read(PAPER/'data/first_action_checks.json')['scenario_note']
result['liquidation_instruction_count']=sum(scenario in json.dumps(st,ensure_ascii=False) for r in records.values() for st in r['starts'].values())
refusal=co.Counter();refusal_messages=co.Counter();response_paths=co.Counter();accept_conflicts=[]
for g,r in records.items():
    for d,x in r['resolved'].items():
        for i,a in enumerate(x['attempts']):
            if 'opus' in x['openrouter_model_id']:
                response_paths[(a.get('response_condition'),a.get('outcome'))]+=1
            if 'opus' in x['openrouter_model_id'] and a.get('outcome')=='refused':
                refusal['first' if i==0 else 'later']+=1
                msg=a.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
                refusal_messages[msg.get('refusal') or msg.get('content')]+=1
        if 'grok' in x['openrouter_model_id'] and x['final_action']['action']=='accept_trade':
            aa=[a for a in x['attempts'] if a.get('outcome')=='valid'];t=aa[-1].get('assistant_content') or ''
            named=re.search(r'"name"\s*:\s*"([a-z_]+)"',t)
            if named and named[1]!='accept_trade':accept_conflicts.append([g,d,named[1]])
result['refusals']=dict(counts=refusal,messages=list(refusal_messages.items()),response_paths=[[list(k),v] for k,v in response_paths.items()])
result['grok_accept_conflicts']=accept_conflicts
result['semantic_population']=dict(co.Counter(o['completion_cell'] for o in offers if o['accept_available'] and o['response']=='reject_trade' and o['completion_cell'] in ['recipient_only','both']))
result['semantic_excluded_unacceptable']=[dict(game=o['game'],decision=o['decision'],cell=o['completion_cell']) for o in offers if not o['accept_available'] and o['response']=='reject_trade' and o['completion_cell'] in ['recipient_only','both']]
receipts=[]
for g,source,dest in [(2,122,124),(15,166,169),(15,175,176),(13,250,251),(13,252,253),(19,135,136),(18,431,441),(18,431,442),(20,96,97)]:
    message=records[g]['resolved'][source]['final_action']['public_message']
    request=records[g]['starts'][dest]
    match=message in json.dumps(request,ensure_ascii=False)
    # JSON encoding can escape quotes, so also search individual memory fields.
    match=match or any(v.get('message')==message for v in request['prompt_payload']['game_state']['memory']['public_timeline_last_20'])
    receipts.append(dict(game=g,source_decision=source,recipient_decision=dest,delivered=match,message=message))
result['receipts']=receipts
assert all(r['delivered'] for r in receipts)
events=[]
for g,r in records.items():
    for e in r['events']:
        if e['type']=='CASH_CHANGED' and e['payload'].get('reason')=='BANKRUPTCY':
            following=[v for v in r['events'][e['seq']+1:] if v['turn_index']==e['turn_index'] and v['type']=='PROPERTY_PURCHASED' and v['payload'].get('price')==0]
            events.append(dict(game=g,turn=e['turn_index'],seq=e['seq'],debtor=e['payload']['player_id'],inherited_deeds=[v['payload'] for v in following]))
result['elimination_events']=events
result['g20_payment']=dict(actions=[records[20]['resolved'][d]['final_action']['action'] for d in range(327,337)],
    final_cash=records[20]['starts'][337]['prompt_payload']['game_state']['you']['cash'],
    sales=sum(e['payload']['delta'] for e in records[20]['events'] if e['turn_index']==108 and e['type']=='CASH_CHANGED' and e['payload'].get('reason')=='SELL_BUILDING'),
    mortgages=sum(e['payload']['delta'] for e in records[20]['events'] if e['turn_index']==108 and e['type']=='CASH_CHANGED' and e['payload'].get('reason')=='MORTGAGE'))
result['g7_orange_rent']=sum(e['payload']['amount'] for e in records[7]['events'] if e['type']=='RENT_PAID' and e['payload']['to_player_id']=='p1' and e['payload']['space_index'] in [16,18,19] and e['turn_index']>=68)
result['g2_sol_yellow_rent']=sum(e['payload']['amount'] for e in records[2]['events'] if e['type']=='RENT_PAID' and e['payload']['to_player_id']=='p1' and e['payload']['space_index'] in [26,27,29] and e['turn_index']>=69)
(OUT/'conditions_and_incidents.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['elimination_events','receipts']},indent=2))
