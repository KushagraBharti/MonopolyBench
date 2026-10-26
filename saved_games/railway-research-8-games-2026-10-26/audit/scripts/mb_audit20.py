import sys,json,pathlib,hashlib,collections,tempfile,zipfile,math,csv,time
sys.path.insert(0,'/tmp');import mb_import20_auth as auth
from monopoly_telemetry import build_run_files
from monopoly_telemetry.inventory import verify_inventory
from monopoly_arena.replay_verification import build_replay_verification_reports
from monopoly_arena.long_campaign import _completed_run_exists
from monopoly_arena.route_validator import validate_route
from monopoly_telemetry.execution_cost import execution_cost
from monopoly_arena.job_store import encode
ROOT=pathlib.Path('/Users/kushagra/MonopolyBench-research/railway-research-8-games-2026-10-26')
SHA='d6808534a831862682a6940f394c6c87bb2691cb'
FINGERPRINT='9a15ddc829a35e11c6046ff4778508da7f3d8d86de477d7d33837784b1e6ea3e'
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
idx=load(ROOT/'audit/download-index.json');assert len(idx['games'])==8
results=[]
for g in idx['games']:
    package=ROOT/g['package'];run=package/'run';out=ROOT/'audit'/g['run_id'];out.mkdir(exist_ok=True)
    manifest=verify_inventory(package);assert manifest['tree_sha256']==g['tree_sha256']
    with zipfile.ZipFile(ROOT/g['archive']) as z:
        names=z.namelist();assert len(names)==len(set(names))
        assert set(names)=={f['path'] for f in manifest['files']}|{'storage_manifest.json'}
        for f in manifest['files']:
            data=z.read(f['path']);assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
    parsed=collections.Counter()
    for p in package.rglob('*'):
        if p.suffix=='.json':load(p);parsed['json']+=1
        elif p.suffix=='.jsonl':rows(p);parsed['jsonl']+=1
    config=load(run/'run_config.json');summary=load(run/'summary.json')
    assert g['git_sha']==SHA and config['treatment_fingerprint']==FINGERPRINT
    assert config['treatment_version']=='audit_corrected_v2' and config['max_turns'] is None
    assert config['response_policy']['version']=='claude_refusal_recovery_v1'
    assert all(p['reasoning']['effort']=='medium' for p in config['players'])
    events=rows(run/'events.jsonl');actions=rows(run/'actions.jsonl');decisions=rows(run/'decisions.jsonl')
    resolved=[d for d in decisions if d.get('phase')=='decision_resolved']
    assert events[-1]['type']=='GAME_ENDED' and summary['reason']=='BANKRUPTCY'
    assert len({e['seq'] for e in events})==len(events) and len({e['event_id'] for e in events})==len(events)
    assert all(b['seq']==a['seq']+1 for a,b in zip(events,events[1:]))
    assert [d['decision_id'] for d in resolved]==[a['decision_id'] for a in actions]
    assert all(d['final_action']==a['action'] for d,a in zip(resolved,actions))
    with tempfile.TemporaryDirectory(prefix='mb-twenty-replay-') as tmp:
        link=pathlib.Path(tmp)/g['run_id'];link.symlink_to(run,target_is_directory=True)
        replay=build_replay_verification_reports(build_run_files(pathlib.Path(tmp),g['run_id']))
        save(out/'independent-replay.json',replay)
        assert all(r['status']=='passed' for r in replay.values())
        assert _completed_run_exists(link)
    ledger=load(package/'cloud/ledger.json');calls=ledger['calls'];models=collections.defaultdict(collections.Counter)
    failures=[]
    for call in calls:
        cp=package/'cloud/calls';intent=load(cp/(call['call_id']+'.intent.json'))
        rp=cp/(call['call_id']+'.response.json');response=load(rp) if rp.exists() else None
        model=intent['payload']['model'];st=models[model];st['calls']+=1
        st['http:'+str(call.get('http_status'))]+=1;st['state:'+str(call.get('state'))]+=1;st['byok:'+str(call.get('is_byok'))]+=1
        if response and response.get('ok'):
            validate_route(intent['payload'],response['response_json']);st['validated_routes']+=1
        else:
            st['failed_physical_calls']+=1
            failures.append({'call_id':call['call_id'],'model':model,'http_status':call.get('http_status'),'error_type':call.get('error_type'),'response_artifact_present':rp.exists()})
    defaults=collections.Counter(d['openrouter_model_id'] for d in resolved if d.get('fallback_used'))
    refusals=collections.defaultdict(collections.Counter)
    outcomes=collections.Counter();conditions=collections.Counter()
    for d in resolved:
        for attempt in d.get('attempts',[]):
            model=attempt.get('requested_model') or d['openrouter_model_id'];stage=attempt.get('response_condition','unrecorded')
            outcomes[attempt.get('outcome','unrecorded')]+=1;conditions[stage]+=1
            if model.startswith('anthropic/') and attempt.get('outcome')=='refused':refusals[model][stage]+=1
    cost=execution_cost(calls)
    for k in ['known_total','openrouter_charge','provider_charge']:assert math.isclose(cost[k],g['cost'][k],abs_tol=1e-8)
    for k in ['calls','missing_calls','unknown_calls']:assert cost[k]==g['cost'][k]
    stats={'resolved':len(resolved),'actions':len(actions),'events':len(events),'invalid_attempts':sum(bool(a.get('validation_errors')) for d in resolved for a in d.get('attempts',[])),'invalid_decisions':sum(any(a.get('validation_errors') for a in d.get('attempts',[])) for d in resolved),'default_actions':sum(defaults.values()),'default_actions_by_model':dict(defaults),'retry_decisions':sum(bool(d.get('retry_used')) for d in resolved),'attempt_conditions':dict(conditions),'attempt_outcomes':dict(outcomes),'claude_refusals_by_model_and_stage':dict(refusals)}
    winner=next(p['openrouter_model_id'] for p in config['players'] if p['player_id']==summary['winner_player_id'])
    r={**g,'seed':config['seed'],'winner_model':winner,'treatment_version':config['treatment_version'],'treatment_fingerprint':config['treatment_fingerprint'],'integrity':'passed','independent_replay':'passed','strict_completed_run':'passed','parsed_files':dict(parsed),'summary':summary,'decisions':stats,'models':dict(models),'cost':cost,'transport_failures':failures,'physical_opus_4_8_calls':models.get('anthropic/claude-opus-4.8',{}).get('calls',0),'pauses':ledger['pauses'],'executions':len(ledger['executions']),'recovered':ledger['jobs'][0]['recovered'],'repaired':ledger['jobs'][0]['repaired'],'analysis_files':sum(p.is_file() for p in (package/'analysis').rglob('*')),'quality_files':sum(p.is_file() for p in (package/'quality_check').rglob('*'))}
    assert r['analysis_files'] and r['quality_files']
    results.append(r);save(ROOT/'audit/verification.json',results)
    print(json.dumps({'game':g['collection_game'],'turns':g['turns'],'replay':'passed','strict_completion':'passed','defaults':dict(defaults),'physical_opus_4_8':r['physical_opus_4_8_calls'],'missing_cost':cost['missing_calls'],'unknown_cost':cost['unknown_calls'],'transport_failures':len(failures)}),flush=True)

campaign=idx['campaigns'][0];meta=ROOT/campaign['metadata'];live=load(meta/'campaign-live.json');cfg=live['config'];freeze=load(meta/'freeze_manifest.json')
assert hashlib.sha256(encode(cfg).encode()).hexdigest()==freeze['config_sha256']==live['config_sha256']
assert freeze['git_sha']==SHA and set(cfg['seeds'])=={3648314310,2766649504}
for record in cfg['research_freeze'].values():assert hashlib.sha256(encode(record['content']).encode()).hexdigest()==record['sha256']
draw=cfg['research_freeze']['seed_draw']['content'];entropy=bytes.fromhex(draw['entropy_hex'])
assert hashlib.sha256(entropy).hexdigest()==draw['entropy_sha256']
assert set(cfg['seeds']).isdisjoint(draw['excluded_seeds'])
for d in draw['seeds']:
    digest=hashlib.sha256(b'MonopolyBench/outcome-blind-seed-draw/v1\0'+live['campaign_id'].encode()+b'\0'+entropy+d['draw_counter'].to_bytes(8,'big')).digest()
    assert digest.hex()==d['draw_digest_sha256'] and int.from_bytes(digest[:4],'big')==d['seed']
roster=['anthropic/claude-opus-5.5','openai/gpt-6.1-sol','google/gemini-4-argon','x-ai/grok-4.7']
for i,seed in enumerate(cfg['seeds']):
    cells=sorted((c for c in live['cells'] if c['seed']==seed),key=lambda c:c['cell_index']);assert len(cells)==4
    assert [c['models_by_seat'] for c in cells]==[roster[n:]+roster[:n] for n in range(4)]
    assert all(c['rerun_count']==0 for c in cells)
save(ROOT/'audit/cohorts.json',[{'campaign_id':live['campaign_id'],'cells':8,'seeds':cfg['seeds'],'config_sha256':live['config_sha256'],'git_sha':SHA,'treatment_fingerprint':FINGERPRINT,'execution_policy':cfg['execution_policy_version'],'response_policy':cfg['response_policy'],'seat_balance':'passed','draw_hashes':'passed','final_revision':campaign['revision']}])
with (ROOT/'game-index.csv').open('w') as out:
    fields=['collection_game','cell_index','job_id','run_id','seed','turns','winner_model','git_sha','treatment_fingerprint','package','archive','tree_sha256'];w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(results)

# Exact-value scan: output and receipt contain counts only, never values or matching paths.
needles=[v.encode() for k,v in auth.variables.items() if any(t in k for t in ['PASSWORD','TOKEN','API_KEY','SECRET']) and isinstance(v,str) and len(v)>=8]
for handler in auth.http.handlers:
    if hasattr(handler,'cookiejar'):needles.extend(c.value.encode() for c in handler.cookiejar if len(c.value)>=8)
matches=files_scanned=0
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix!='.zip':
        data=p.read_bytes();files_scanned+=1;matches+=sum(value in data for value in needles)
save(ROOT/'audit/secret-scan.json',{'files_scanned':files_scanned,'secret_values_checked':len(needles),'matches':matches})
assert matches==0
print('All 8 game audits passed; exact-value secret matches: 0',flush=True)
