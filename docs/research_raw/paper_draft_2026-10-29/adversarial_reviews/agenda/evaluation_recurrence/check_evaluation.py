"""Review-only re-execution using retained actions and original scenario JSON."""
import collections
import gzip
import hashlib
import importlib.util
import json
import statistics
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/research_raw/paper_agenda_revision_2026-10-29/evaluation'
sys.path.insert(0,str(BASE))
import run_offline as runner
import verify_offline as verifier


def main():
    replay=[]
    counts=collections.Counter()
    statuses=collections.Counter()
    winners=[]
    for folder in sorted((BASE/'results/games').iterdir()):
        result=verifier.replay(folder)
        replay.append(result)
        summary=json.loads((folder/'summary.json').read_text())
        statuses[summary['status']]+=1
        counts.update(summary['action_counts'])
        if summary['winner_policy']:
            winners.append({k:summary[k] for k in ['run_id','winner_policy','decisions_applied']})
    fixture_counts=collections.Counter()
    errors=[]
    rejected_refs=[]
    keyword=[]
    house_flags=[]
    state_flags=[]
    equal_actions=[]
    references=[]
    for path in sorted((ROOT/'contracts/micro/scenarios').glob('*.json')):
        fixture=json.loads(path.read_text())
        decision=fixture['decision_point']
        sid=fixture['scenario_id']
        actions=[]
        for policy in sorted(runner.BASELINE_IDS):
            action=runner.choose_baseline_action(decision,policy)
            invalid=runner.validate_fixture_action(decision,action)
            fixture_counts[(policy,bool(invalid))]+=1
            if invalid:
                errors.append(dict(scenario_id=sid,policy=policy,errors=invalid))
            actions.append(json.dumps({'name':action['action'],'args':action['args']},sort_keys=True))
        if len(set(actions))==1:
            equal_actions.append(sid)
        action=fixture['reference_policy']['action']
        invalid=runner.validate_fixture_action(decision,action)
        if invalid:
            rejected_refs.append(dict(scenario_id=sid,action=action,errors=invalid))
        references.append((sid,bool(invalid)))
        rubric=fixture['evaluation']['rubric']
        points=sum(x['max_points'] for x in rubric)
        expression=sum(x['max_points'] for x in rubric if x['type']=='private_thought_mentions')
        keyword.append(expression/points)
        state=decision['state']
        expected_houses=32-sum(x['houses'] for x in state['board'])
        flag=state['bank']['houses_remaining']!=expected_houses
        if flag:
            house_flags.append(sid)
        groups=collections.defaultdict(list)
        flags=[]
        for square in state['board']:
            if square.get('group'):
                groups[square['group']].append(square)
        if flag: flags.append('house_stock')
        if state['bank']['hotels_remaining']!=12-sum(bool(s['hotel']) for s in state['board']): flags.append('hotel_stock')
        for group,squares in groups.items():
            levels=[5 if s['hotel'] else s['houses'] for s in squares]
            if not any(levels):continue
            owners={s['owner_id'] for s in squares}
            if len(owners)!=1 or None in owners:flags.append('split_owned')
            if any(s['mortgaged'] for s in squares):flags.append('mortgaged_development')
            if max(levels)-min(levels)>1:flags.append('uneven')
        if decision.get('liquidation'):
            liq=decision['liquidation']
            cash=next(x['cash'] for x in state['players'] if x['player_id']==decision['player_id'])
            if liq['shortfall']!=max(0,liq['owed_amount']-cash):flags.append('shortfall')
        if flags:state_flags.append(dict(scenario_id=sid,flags=flags))
    raw=(ROOT/'python/packages/engine/src/monopoly_engine/engine.py').read_bytes()
    archive=ROOT/'docs/research_raw/paper_draft_2026-10-29/artifacts/historical-claim-audit.zip'
    with zipfile.ZipFile(archive) as z:
        historical=z.read('historical-claim-audit/vendor/monopoly_engine/engine.py')
    protected=json.loads((BASE/'results/sources_before.json').read_text())
    mismatch=[p for p,h in protected.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    result=dict(replayed_games=len(replay),replayed_actions=sum(x['actions'] for x in replay),
                replayed_events=sum(x['events'] for x in replay),statuses=dict(statuses),winners=winners,
                action_counts=dict(counts),fixture_rejections=len(errors),invalid_references=len(rejected_refs),
                by_policy={p:dict(legal=fixture_counts[(p,False)],invalid=fixture_counts[(p,True)]) for p in sorted(runner.BASELINE_IDS)},
                keyword_scenarios=sum(x>0 for x in keyword),keyword_median=statistics.median(keyword),keyword_max=max(keyword),
                equal_policy_outputs=len(equal_actions),house_stock_flags=len(house_flags),
                state_flag_cases=len(state_flags),state_flag_counts=dict(collections.Counter(f for x in state_flags for f in x['flags'])),
                both_screens_pass=sum(not bad and sid not in {x['scenario_id'] for x in state_flags} for sid,bad in references),
                engine_exact_bytes_equal=raw==historical,engine_sha256=hashlib.sha256(raw).hexdigest(),
                protected_files=len(protected),protected_hash_mismatches=mismatch,
                scope='Verifier re-executed unchanged engine, plus separate recount from original scenario files. Not an independent engine implementation.',
                replay_rows=replay,reference_failures=rejected_refs)
    (OUT/'evaluation_reexecution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['replay_rows','reference_failures']},indent=2))


if __name__=='__main__':main()
