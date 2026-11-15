import dec,json
D=dec.ROOT+'/docs/research_raw/paper_revision_2026-11-12/integrated/data/'
f=json.load(open(D+'first_action_checks.json'))
eps={ (e['game'],e['first_decision']):e for e in json.load(open(D+'liquidation_episodes.json'))}
six=[r for r in f['rows'] if r['category']=='above_bound' and r['action']!='declare_bankruptcy']
out=[]
for r in six:
    g,i=r['game'],r['decision']; ep=eps[(g,i)]
    print(f"\n=== G{g} d{i} {ep['model']} t{ep['turn']} cash={ep['cash']} debt={ep['debt']} U*={ep['upper_bound']} outcome={ep['outcome']} actions={ep['actions']} n_dec={len(ep['decisions'])} fb={ep['fallback_actions']}")
    for j,did in enumerate(ep['decisions']):
        idx=int(did.rsplit('-',1)[1])
        z=dec.get(g,idx); rz=z['decision_resolved']; s=z['decision_started']
        fa=rz['final_action']
        conds=[a['response_condition']+':'+a['outcome'] for a in rz['attempts']]
        print(f"  d{idx} action={fa['action']} args={json.dumps(fa.get('args'))[:200]} fb={rz['fallback_used']} conds={conds}")
        print(f"     note: {fa.get('private_thought')}")
        print(f"     public: {fa.get('public_message')}")
        a=rz['attempts'][-1]
        m=(a.get('raw_response') or {}).get('choices',[{}])[0].get('message') if a.get('raw_response') else {}
        if m:
            if m.get('content'): print(f"     content: {m.get('content')[:600]}")
            if m.get('reasoning'): print(f"     reasoning: {m.get('reasoning')[:1500]}")
        if j==0:
            sc=s['prompt_payload']['action_state']['scenario']
            print('     menu',sc['options'],'owed',sc['owed_amount'],'to',sc.get('owed_to_player_id'),'reason',sc['reason'])
