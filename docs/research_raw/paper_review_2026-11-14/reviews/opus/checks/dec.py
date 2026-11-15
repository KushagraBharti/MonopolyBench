import json,sys,os
ROOT='/Users/kushagra/CS-Projects/MonopolyBench'
GM=json.load(open(ROOT+'/docs/research_raw/paper_revision_2026-11-12/integrated/data/game_map.json'))
_cache={}
def load(g):
    if g in _cache: return _cache[g]
    p=os.path.join(ROOT,GM[str(g)],'decisions.jsonl')
    rows=[json.loads(l) for l in open(p)]
    d={}
    for r in rows:
        idx=int(r['decision_id'].rsplit('-',1)[1])
        d.setdefault(idx,{})[r['phase']]=r
    _cache[g]=d
    return d
def get(g,i):
    return load(g)[i]
if __name__=='__main__':
    g=int(sys.argv[1]); i=int(sys.argv[2]); what=sys.argv[3] if len(sys.argv)>3 else 'summary'
    r=get(g,i)
    s=r['decision_started']; z=r['decision_resolved']
    if what=='summary':
        print('turn',s['turn_index'],'type',s['decision_type'],'player',s['player_id'],s['player_name'])
        print('retry',z['retry_used'],'fallback',z['fallback_used'],z['fallback_reason'])
        print('final_action',json.dumps(z['final_action'])[:2000])
        for k,a in enumerate(z['attempts']):
            print('--- attempt',k,list(a.keys()))
    elif what=='payload':
        print(json.dumps(s['prompt_payload'],indent=1)[:int(sys.argv[4]) if len(sys.argv)>4 else 20000])
    elif what=='attempts':
        print(json.dumps(z['attempts'],indent=1)[:int(sys.argv[4]) if len(sys.argv)>4 else 20000])
