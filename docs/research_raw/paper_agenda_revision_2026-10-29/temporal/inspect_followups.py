"""Read-only canonical follow-up extraction for manually identified statements."""
import json
from extract_sample import ROOT, OUT
from manual_coding import CODING


def load_games():
    sampled=json.loads((OUT/'sample_fields.json').read_text())
    games={}
    for r in sampled:
        if r['game'] in games:
            continue
        run=ROOT/r['source_run']
        decisions=[json.loads(s) for s in (run/'decisions.jsonl').read_text().splitlines()]
        starts={r['decision_id']:r for r in decisions if r['phase']=='decision_started'}
        resolves={r['decision_id']:r for r in decisions if r['phase']=='decision_resolved'}
        acts=[json.loads(s) for s in (run/'actions.jsonl').read_text().splitlines()]
        events=[json.loads(s) for s in (run/'events.jsonl').read_text().splitlines()]
        games[r['game']]={'starts':starts,'resolves':resolves,'actions':acts,'events':events}
    return sampled,games


def context(r,game,limit=8):
    future=[a for a in game['actions'] if a['actor_player_id']==r['player_id'] and int(a['decision_id'].rsplit('-',1)[1])>r['decision_index']]
    out=[]
    for a in future[:limit]:
        start=game['starts'][a['decision_id']]
        payload=start['prompt_payload']
        state=payload['game_state']
        action=a['action']
        resolved=game['resolves'][a['decision_id']]
        out.append({'decision_index':int(a['decision_id'].rsplit('-',1)[1]),'turn':a['turn_index'],
                    'action':action['action'],'args':action['args'],'cash':state['you']['cash'],
                    'position':state['you']['position'],'public':action.get('public_message'),
                    'private':action.get('private_thought'),'menu':payload['action_state'],
                    'holdings':state['you']['holdings'], 'fallback':resolved['fallback_used'],
                    'event_start':resolved['emitted_event_seq_start'],'event_end':resolved['emitted_event_seq_end']})
    return out


if __name__=='__main__':
    sampled,games=load_games()
    rows=[{'id':r['id'],'future':context(r,games[r['game']],12)} for r in sampled if set(CODING[r['id']][0]) & {'P','O','R'}]
    (OUT/'followup_context.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'source_rows':len(rows),'future_actions':sum(len(x['future']) for x in rows)}))
