import sys, json, pathlib, hashlib, collections, tempfile, zipfile, math, csv, datetime
from monopoly_telemetry import build_run_files
from monopoly_telemetry.inventory import verify_inventory
from monopoly_arena.replay_verification import build_replay_verification_reports
from monopoly_arena.long_campaign import _completed_run_exists
from monopoly_arena.route_validator import validate_route
from monopoly_telemetry.execution_cost import execution_cost
from monopoly_arena.job_store import encode

ROOT = pathlib.Path('/Users/kushagra/.t3/worktrees/MonopolyBench/t3-930e9681/saved_games/railway-research-12-games-2026-10-25')
def load(p): return json.loads(p.read_text())
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def save(p, v): p.write_text(json.dumps(v, indent=2)+'\n')
index = load(ROOT/'audit/download-index.json')
assert len(index['games']) == 12
results=[]
for game in index['games']:
    pkg=ROOT/game['package']; run=pkg/'run'; audit=ROOT/'audit'/game['run_id'];audit.mkdir(exist_ok=True)
    manifest=verify_inventory(pkg)
    assert manifest['tree_sha256']==game['tree_sha256']
    # Independently read every original ZIP entry and compare it with the package inventory.
    expected={f['path']:f for f in manifest['files']}
    with zipfile.ZipFile(ROOT/game['archive']) as z:
        assert len(z.namelist())==len(set(z.namelist()))
        assert set(z.namelist())==set(expected)|{'storage_manifest.json'}
        for name,f in expected.items():
            data=z.read(name)
            assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256'], name
    # Parse all serialized evidence, including prompt/response and cloud call files.
    json_files=jsonl_files=0
    for p in pkg.rglob('*'):
        if p.suffix=='.json': load(p);json_files+=1
        elif p.suffix=='.jsonl': rows(p);jsonl_files+=1
    events=rows(run/'events.jsonl'); actions=rows(run/'actions.jsonl'); decisions=rows(run/'decisions.jsonl')
    resolved=[d for d in decisions if d.get('phase')=='decision_resolved']
    summary=load(run/'summary.json'); config=load(run/'run_config.json')
    assert events[-1]['type']=='GAME_ENDED' and summary['reason']=='BANKRUPTCY'
    assert len({e['seq'] for e in events})==len(events)
    assert all(b['seq']==a['seq']+1 for a,b in zip(events,events[1:]))
    assert len({e['event_id'] for e in events})==len(events)
    assert config.get('max_turns') is None
    assert all(p.get('reasoning',{}).get('effort')=='medium' for p in config['players'])
    # Scratch links give the validator the original run identity without modifying downloaded evidence.
    with tempfile.TemporaryDirectory(prefix='mb-twelve-replay-') as tmp:
        link=pathlib.Path(tmp)/game['run_id']; link.symlink_to(run, target_is_directory=True)
        files=build_run_files(pathlib.Path(tmp),game['run_id'])
        replay=build_replay_verification_reports(files)
        save(audit/'independent-replay.json',replay)
        assert all(r['status']=='passed' for r in replay.values()), 'Independent replay failed'
        assert _completed_run_exists(link), 'Strict completed-run validator failed'
    ledger=load(pkg/'cloud/ledger.json'); calls=ledger['calls']; model_stats=collections.defaultdict(collections.Counter)
    for call in calls:
        cp=pkg/'cloud/calls'; intent=load(cp/(call['call_id']+'.intent.json'))
        response_path=cp/(call['call_id']+'.response.json')
        # A lost transport reply can legitimately have an intent without a response.
        response=load(response_path) if response_path.exists() else None
        model=intent['payload']['model']; st=model_stats[model]; st['calls']+=1
        st['state:'+str(call.get('state'))]+=1
        st['http:'+str(call.get('status_code',call.get('http_status')))]+=1
        st['byok:'+str(call.get('is_byok'))]+=1
        if response is not None and response.get('ok'):
            validate_route(intent['payload'],response['response_json']);st['valid_routes']+=1
        elif response is None: st['missing_transport_response']+=1
        else: st['unsuccessful_transport']+=1
    accounting=execution_cost(calls)
    for k in ['known_total','openrouter_charge','provider_charge']:
        assert math.isclose(accounting[k],game['cost'][k],abs_tol=1e-8)
    for k in ['calls','missing_calls','unknown_calls']: assert accounting[k]==game['cost'][k]
    stats={'resolved':len(resolved),'actions':len(actions),'events':len(events),'invalid_attempts':sum(bool(a.get('validation_errors')) for d in resolved for a in d.get('attempts',[])), 'invalid_decisions':sum(any(a.get('validation_errors') for a in d.get('attempts',[])) for d in resolved),'default_actions':sum(bool(d.get('fallback_used')) for d in resolved),'retry_decisions':sum(bool(d.get('retry_used')) for d in resolved),'attempt_conditions':dict(collections.Counter(a.get('response_condition','unrecorded') for d in resolved for a in d.get('attempts',[]))),'attempt_outcomes':dict(collections.Counter(a.get('outcome','unrecorded') for d in resolved for a in d.get('attempts',[])))}
    result={**game,'integrity':'passed','independent_replay':'passed','strict_completed_run':'passed','parsed_json_files':json_files,'parsed_jsonl_files':jsonl_files,'summary':summary,'decisions':stats,'models':dict(model_stats),'cost':accounting,'pauses':ledger['pauses'],'executions':len(ledger['executions']),'analysis_files':sum(p.is_file() for p in (pkg/'analysis').rglob('*')),'quality_files':sum(p.is_file() for p in (pkg/'quality_check').rglob('*'))}
    assert result['analysis_files']>0 and result['quality_files']>0
    results.append(result);save(ROOT/'audit/verification.json',results)
    print(json.dumps({'batch':game['batch'],'game':game['game'],'independent_replay':'passed','strict_completed':'passed','turns':game['turns'],'decisions':stats,'calls':len(calls)}),flush=True)

cohorts=[]
for campaign in index['campaigns']:
    pkg=ROOT/campaign['package'];verify_inventory(pkg)
    evidence=load(pkg/'campaign.json');live=load(pkg.parent/'campaign-live.json')
    frozen=load(pkg/'freeze_manifest.json')
    cfg=live['config'];roster=['anthropic/claude-opus-5.5','openai/gpt-6.1-sol','google/gemini-4-argon','x-ai/grok-4.7']; groups=collections.defaultdict(list)
    assert hashlib.sha256(encode(cfg).encode()).hexdigest()==live['config_sha256']==frozen['config_sha256']
    assert frozen['git_sha']==live['git_sha']
    for record in cfg['research_freeze'].values():
        assert hashlib.sha256(encode(record['content']).encode()).hexdigest()==record['sha256']
    assert load(pkg/'preflight.json')['passed'] is True
    for cell in live['cells']: groups[cell['seed']].append(cell)
    assert len(groups)*4==len(live['cells'])
    for seed,cells in groups.items():
        assert len(cells)==4 and all(c['rerun_count']==0 for c in cells)
        for seat in range(4): assert collections.Counter(c['models_by_seat'][seat] for c in cells)==collections.Counter(roster)
    cohorts.append({'campaign_id':campaign['campaign_id'],'cells':len(live['cells']),'seeds':list(groups),'config_sha256':live['config_sha256'],'git_sha':live['git_sha'],'execution_policy':cfg.get('execution_policy_version'),'response_policy':cfg.get('response_policy'),'seat_balance':'passed','freeze_files':list(frozen),'final_revision':campaign['revision']})
save(ROOT/'audit/cohorts.json',cohorts)
with (ROOT/'game-index.csv').open('w') as out:
    names=['batch','game','job_id','run_id','turns','git_sha','package','archive','tree_sha256']
    w=csv.DictWriter(out,fieldnames=names,extrasaction='ignore');w.writeheader();w.writerows(results)
print('All 12 artifact audits passed',flush=True)
