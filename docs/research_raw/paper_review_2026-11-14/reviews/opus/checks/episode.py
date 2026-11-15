import dec,json,sys
D=dec.ROOT+'/docs/research_raw/paper_revision_2026-11-12/integrated/data/'
eps={ (e['game'],e['first_decision']):e for e in json.load(open(D+'liquidation_episodes.json'))}
def show(g,i,full=False):
    ep=eps[(g,i)]
    print(f"=== G{g} d{i} {ep['model']} cash={ep['cash']} debt={ep['debt']} U*={ep['upper_bound']} outcome={ep['outcome']} n={len(ep['decisions'])}")
    for did in ep['decisions']:
        idx=int(did.rsplit('-',1)[1]); z=dec.get(g,idx); rz=z['decision_resolved']; s=z['decision_started']
        cash=s['prompt_payload']['game_state']['you']['cash']
        fa=rz['final_action']
        conds=[a['response_condition']+':'+a['outcome'] for a in rz['attempts']]
        print(f" d{idx} cash_before={cash} {fa['action']} {json.dumps(fa.get('args'))[:300]} {conds} fb={rz['fallback_used']}")
        if full:
            print('   note:',fa.get('private_thought'))
            for k,a in enumerate(rz['attempts']):
                m=(a.get('raw_response') or {}).get('choices',[{}])[0].get('message') if a.get('raw_response') else {}
                if m and m.get('reasoning'): print(f'   reasoning[{k}]:',m['reasoning'][:1200])
                if m and m.get('content'): print(f'   content[{k}]:',str(m['content'])[:400])
if __name__=='__main__':
    show(int(sys.argv[1]),int(sys.argv[2]),len(sys.argv)>3)
