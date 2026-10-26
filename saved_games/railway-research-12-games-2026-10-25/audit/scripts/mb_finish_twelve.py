import pathlib,json,collections,shutil,csv,hashlib,zipfile,datetime
from monopoly_telemetry.inventory import verify_inventory, write_inventory
ROOT=pathlib.Path('/Users/kushagra/.t3/worktrees/MonopolyBench/t3-930e9681/saved_games/railway-research-12-games-2026-10-25')
def load(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
idx=load(ROOT/'audit/download-index.json');results=load(ROOT/'audit/verification.json')
for n,game in enumerate(idx['games'],1):
    old=ROOT/game['package'];name=f"game-{n:02d}-{game['turns']}turns-{game['job_id'][:8]}";dest=ROOT/name
    old.rename(dest)
    game['package']=name;game['collection_game']=n
    result=next(r for r in results if r['job_id']==game['job_id']);result['package']=name;result['collection_game']=n
    verify_inventory(dest)
for campaign in idx['campaigns']:
    old=ROOT/campaign['package'];dest=ROOT/'campaigns'/campaign['campaign_id'];dest.parent.mkdir(exist_ok=True)
    # The extracted games are now peers. Preserve the original campaign manifest as evidence of the ZIP layout.
    (old/'storage_manifest.json').rename(old/'original-campaign-storage-manifest.json')
    (old/campaign['campaign_id']).rmdir()
    old.rename(dest)
    batch=old.parent
    for file in batch.iterdir():file.rename(dest/file.name)
    batch.rmdir()
    campaign['metadata']=str(dest.relative_to(ROOT));campaign.pop('package')
save(ROOT/'audit/download-index.json',idx);save(ROOT/'audit/verification.json',results)
with (ROOT/'game-index.csv').open('w') as out:
    fields=['collection_game','batch','game','job_id','run_id','turns','git_sha','package','archive','tree_sha256']
    writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(results)

# Verify the retained full campaign ZIPs after flattening the local directory layout.
for c in idx['campaigns']:
    with zipfile.ZipFile(ROOT/c['archive']) as z:
        manifest=json.loads(z.read('storage_manifest.json'))
        assert set(z.namelist())=={f['path'] for f in manifest['files']}|{'storage_manifest.json'}
        for f in manifest['files']:
            data=z.read(f['path'])
            assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
        assert manifest['tree_sha256']==c['tree_sha256']

total=collections.Counter()
for r in results:
    for k,v in r['cost'].items():
        if isinstance(v,(int,float)):total[k]+=v
defaults=sum(r['decisions']['default_actions'] for r in results)
table=['| Game | Seed | Turns | Winner | Defaults | Replay |','| --- | --- | --- | --- | --- | --- |']
for r in results:
    config=load(ROOT/r['package']/'run/run_config.json')
    winner=r['summary'].get('winner_player_id')
    model=next((p['openrouter_model_id'] for p in config['players'] if p['player_id']==winner),str(winner))
    table.append(f"| {r['collection_game']} | {config['seed']} | {r['turns']} | {model} | {r['decisions']['default_actions']} | Passed |")
text='''# Twelve completed Railway research games

All 12 games are saved side by side in this folder. Games 01 to 04 are the first campaign; games 05 to 12 are the second. Existing exploratory saved games were left untouched. No games, purchases, deployments, or provider requests were started for this download and audit. Two final campaign export snapshots were prepared on the server.

Each game folder preserves the server package unchanged, including `run/`, `quality_check/`, `analysis/`, `cloud/`, the saved-game manifest and the storage manifest. The original per-game ZIPs and both final campaign ZIPs are in `archives/`. Campaign metadata, freeze manifests, preflights and server receipts are in `campaigns/`. Its `original-campaign-storage-manifest.json` describes the original ZIP layout, before the games were moved side by side here. The original campaign ZIP remains complete and verified.

`game-index.csv` maps all 12 local folders to their run IDs, job IDs, source SHAs and archive hashes. `audit/download-index.json` records download provenance and manifest hashes. `audit/verification.json` contains the per-game inspection, and `audit/<run_id>/independent-replay.json` contains newly computed replay results. Canonical game files were not regenerated or overwritten.

## Integrity results

- 12 of 12 original game ZIPs and 2 of 2 final campaign ZIPs passed full member-size and SHA-256 verification against their manifests. All extracted game inventories also passed.
- 12 of 12 games passed newly computed state and artifact replay using saved settings and applied actions. The strict completed-run validator passed for every game, including artifact hashes, terminal snapshot, summary and terminal event agreement.
- Every game ended by BANKRUPTCY with no turn cap, medium effort, complete analysis and quality-check outputs. Event sequences were unique and contiguous. Resolved decisions and applied actions matched in identity, order and payload.
- All successful physical calls returned the requested model and permitted provider. The archived calls retain intent, response, billing metadata and transport-failure evidence. Recorded costs reconcile with the live job totals.
- Campaign freeze/config hashes and embedded seed-draw, analysis-contract and run-matrix hashes passed. All three independent seed blocks have the complete cyclic four-seat rotation. There are no technical reruns, recorded pauses, repairs or recovered jobs in these 12.
- An exact-value scan of extracted files found no configured production password, API-key or export-token values. This is not a complete public-release privacy review.

## Research caveats

These are 12 games across three independent seed blocks, with four correlated seat rotations per seed. They are not 12 independent seeds. Keep the old exploratory corpus separate. The first four use source 42f85183 and the next eight use d6808534; the original source, image and treatment identities remain recorded. Independent replay passed against the local engine.

There are DEFAULT_COUNT recorded deterministic engine-default actions after exhausted invalid-output recovery. These are part of the configured execution policy, not clean model answers. Preserve and disclose their per-game and per-model rates. Claude refusal recovery also occurred; records distinguish standard requests from same-model requests without a private-thought requirement. Configured Opus 4.8 fallback does not imply it was used. No physical Opus 4.8 calls appear in this collection.

Cost metadata contains MISSING_COUNT missing-cost calls and UNKNOWN_COUNT unknown-cost calls. The recorded known subtotal is $KNOWN_TOTAL, including $OR_TOTAL in reported OpenRouter charges and $PROVIDER_TOTAL in reported upstream provider charges. This is not a complete final invoice and does not independently establish any OpenAI free-token discount. Missing or unknown charges remain missing or unknown, never zero.

Six physical xAI/Grok calls failed and were retried. No game ended prematurely from those failures. The original transport evidence remains in each cloud ledger and call directory. These observations, model refusals, invalid actions and recovery rates should remain visible in paper analyses rather than selectively excluding affected games.

## Game ledger

GAME_TABLE

## Scope of this review

This review verifies preservation, completion, deterministic replay, routing, accounting reconciliation and the recorded study design. It does not certify scientific conclusions or replace qualitative social coding and manuscript review. The downloads stay local; nothing was committed or pushed. Use the game packages and their recorded source identities for further analysis.
'''
for key,val in {'DEFAULT_COUNT':str(defaults),'MISSING_COUNT':str(total['missing_calls']),'UNKNOWN_COUNT':str(total['unknown_calls']),'KNOWN_TOTAL':f"{total['known_total']:.6f}",'OR_TOTAL':f"{total['openrouter_charge']:.6f}",'PROVIDER_TOTAL':f"{total['provider_charge']:.6f}",'GAME_TABLE':'\n'.join(table)}.items():text=text.replace(key,val)
(ROOT/'README.md').write_text(text)
(ROOT/'audit/inspection-report.txt').write_text(text)
scripts=ROOT/'audit/scripts';scripts.mkdir(exist_ok=True)
for name in ['mb_download_twelve.py','mb_audit_twelve.py','mb_finish_twelve.py']:shutil.copyfile('/tmp/'+name,scripts/name)
(scripts/'README.txt').write_text('Historical scripts used for this import. Download and audit ran before the owner requested a flat game layout. The finalization script moved the games to their peer folders and updated the indexes. Do not rerun these migration scripts blindly. Use verify_collection.py for a repeatable read-only integrity and replay check in the final layout.\n')
print(json.dumps({'games':len(results),'defaults':defaults,'known_cost':total['known_total'],'path':str(ROOT)}))
