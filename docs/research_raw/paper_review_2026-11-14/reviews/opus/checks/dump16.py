import dec,json
ROOT=dec.ROOT
nc=json.load(open(ROOT+'/docs/research_raw/paper_revision_2026-11-12/integrated/data/necessary_collateral.json'))['necessary_unlocked_collateral']
out=[]
for row in nc:
    g,i=row['game'],row['decision']
    z=dec.get(g,i); s=z['decision_started']; r=z['decision_resolved']
    atts=[]
    for k,a in enumerate(r['attempts']):
        m=(a.get('raw_response') or {}).get('choices',[{}])[0].get('message') if a.get('raw_response') else None
        tcs=[]
        if m:
            for tc in m.get('tool_calls') or []:
                tcs.append({'name':tc['function']['name'],'arguments':tc['function']['arguments']})
        atts.append({'k':k,'outcome':a['outcome'],'condition':a['response_condition'],
          'content':(m or {}).get('content'),'reasoning':(m or {}).get('reasoning'),
          'reasoning_types':[d.get('type') for d in ((m or {}).get('reasoning_details') or [])],
          'tool_calls':tcs,'validation_errors':a.get('validation_errors')})
    p=s['prompt_payload']
    you=p['game_state']['you']
    out.append({'game':g,'decision':i,'turn':s['turn_index'],'player':s['player_id'],'model':s['player_name'],
      'cash':you['cash'],'holdings':you['holdings']['owned'],'bank':p['game_state']['bank'],
      'scenario':p['action_state']['scenario'],'available':p['action_state']['available_actions'],
      'notes':p['game_state']['memory'].get('your_private_thoughts_last_10'),
      'final_action':r['final_action'],'retry':r['retry_used'],'fallback':r['fallback_used'],
      'attempts':atts,'row':row})
json.dump(out,open('dump16.json','w'),indent=1)
for o in out:
    fa=o['final_action']
    print(f"G{o['game']} d{o['decision']} {o['model']} t{o['turn']} cash={o['cash']} owed={o['scenario']['owed_amount']} short={o['scenario']['shortfall']} bank={o['bank']['houses_remaining']}h/{o['bank']['hotels_remaining']}H")
    print('  menu M:',o['scenario']['options'].get('mortgageable_space_keys'),' S:',o['scenario']['options'].get('sellable_building_space_keys'))
    print('  holdings:',[(h['space_key'][:12],h['houses'],'H' if h['hotel'] else '', 'm' if h['mortgaged'] else '') for h in o['holdings']])
    print('  action:',fa['action'],json.dumps(fa['args']),'retry',o['retry'],'fb',o['fallback'],'conds',[a['condition']+':'+a['outcome'] for a in o['attempts']])
    for a in o['attempts']:
        for tc in a['tool_calls']:
            try: keys=list(json.loads(tc['arguments']).keys())
            except Exception as e: keys=str(e)
            print('   att',a['k'],'call',tc['name'],'argorder',keys)
    print('  n_notes', len(o['notes'] or []))
