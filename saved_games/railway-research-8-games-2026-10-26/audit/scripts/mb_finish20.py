import pathlib,json,collections,shutil
from monopoly_telemetry.inventory import write_inventory
ROOT=pathlib.Path('/Users/kushagra/MonopolyBench-research/railway-research-8-games-2026-10-26')
def load(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
rs=load(ROOT/'audit/verification.json');idx=load(ROOT/'audit/download-index.json')
totals=collections.Counter();defaults=collections.Counter();refusals=collections.defaultdict(collections.Counter);failures=collections.Counter();physical=collections.Counter();diagnostics=[]
for r in rs:
    for k,v in r['cost'].items():
        if isinstance(v,(int,float)):totals[k]+=v
    defaults.update(r['decisions']['default_actions_by_model'])
    for m,s in r['decisions']['claude_refusals_by_model_and_stage'].items():refusals[m].update(s)
    for f in r['transport_failures']:failures[(f['model'],str(f['http_status']),f['error_type'])]+=1
    for m,stats in r['models'].items():physical[m]+=stats['calls']
    ds=[json.loads(x) for x in (ROOT/r['package']/'run/decisions.jsonl').read_text().splitlines()]
    ds=[d for d in ds if d.get('phase')=='decision_resolved']
    problems=[d for d in ds if d.get('fallback_used')]
    counts=collections.Counter(d['openrouter_model_id'] for d in ds)
    diagnostics.append({'collection_game':r['collection_game'],'resolved_decisions_by_model':dict(counts),'defaults':[{'decision_id':d['decision_id'],'turn':d['turn_index'],'model':d['openrouter_model_id'],'decision_type':d['decision_type'],'reason':d['fallback_reason'],'applied_action':d['final_action']['action']} for d in problems]})
save(ROOT/'audit/default-action-details.json',diagnostics)
summary={'games':len(rs),'archives':len(idx['games'])+len(idx['campaigns']),'events':sum(r['decisions']['events'] for r in rs),'resolved_decisions':sum(r['decisions']['resolved'] for r in rs),'cost':dict(totals),'defaults_by_model':dict(defaults),'claude_refusals_by_model_and_stage':dict(refusals),'physical_calls_by_model':dict(physical),'transport_failures':[{'model':m,'http_status':s,'error_type':e,'count':n} for (m,s,e),n in failures.items()],'physical_opus_4_8_calls':sum(r['physical_opus_4_8_calls'] for r in rs)}
save(ROOT/'audit/totals.json',summary)
ledger=['| Game | Seed | Turns | Winner | Engine defaults | Replay |','| --- | --- | --- | --- | --- | --- |']
for r in rs:ledger.append(f"| {r['collection_game']} | {r['seed']} | {r['turns']} | {r['winner_model']} | {r['decisions']['default_actions']} | Passed |")
text=f'''# Eight completed Railway research games, collection games 13-20

All eight games are saved side by side in this folder, in campaign cell order. They belong to campaign `{idx['campaigns'][0]['campaign_id']}`, Research blocks 4–5. Existing collections are separate and unchanged.

Each game folder preserves the server package, including `run/`, `quality_check/`, `analysis/`, `cloud/`, `saved_game_manifest.json` and `storage_manifest.json`. The eight original game ZIPs and final campaign ZIP are in `archives/`. Campaign records and receipts are in `campaigns/<campaign_id>/`. The `original-campaign-storage-manifest.json` there describes the original campaign ZIP layout; the local game folders were assembled directly in their final flat layout. The complete original ZIP retains the server layout.

`game-index.csv` maps the collection numbers, cells, job IDs, run IDs, seeds, code identities and local paths. `audit/download-index.json` records export provenance, ZIP hashes and server tree hashes. Per-game results are in `audit/verification.json`; each run's new replay reports are in `audit/<run_id>/independent-replay.json`. `audit/totals.json` and `audit/default-action-details.json` provide machine-readable caveats. Canonical game artifacts were not regenerated or overwritten.

## Integrity results

- All 8 game ZIPs and the final campaign ZIP passed member-size, SHA-256, CRC and inventory verification, including the campaign's nested game packages. Every extracted game inventory matches the server export's content tree hash.
- The server export entries publish `bytes` and `manifest_sha256`, not a ZIP-file SHA-256. Downloaded byte counts match the server entries. Locally computed ZIP-file SHA-256 hashes are recorded, and each uncompressed member is independently checked against the server-pinned inventory. No unpublished server ZIP-byte hash is claimed.
- All 8 newly computed state and artifact replay checks passed. Every game passed `_completed_run_exists`, including the frozen artifact manifest, completion record, terminal snapshot, summary and event agreement.
- Event sequences are unique and contiguous. The {summary['resolved_decisions']:,} resolved decisions match the applied actions in identity, order and payload. There are {summary['events']:,} canonical events.
- All games ended naturally by BANKRUPTCY, with no turn cap and medium effort. Analysis and quality-check outputs are present. There are no recorded pauses, repairs, recovered jobs or technical reruns.
- Every game records SHA `d6808534a831862682a6940f394c6c87bb2691cb` and treatment fingerprint `9a15ddc829a35e11c6046ff4778508da7f3d8d86de477d7d33837784b1e6ea3e`, with treatment version `audit_corrected_v2`.
- Every successful physical call returned its requested model and an allowed provider. Cost accounting reconciles exactly with the live job totals, within floating-point tolerance.
- Campaign/config freeze hashes, embedded research-record hashes, outcome-blind seed-draw digests and entropy checks passed. Both seeds, 3648314310 and 2766649504, have the complete cyclic four-seat rotation.
- The exact-value credential scan reports counts only in `audit/secret-scan.json`. It found zero matches. This is not a full public-release privacy review.

## Research caveats

These eight games contribute two independent seed blocks with four correlated seat rotations per seed. Together with the earlier collection, the combined design is 20 games across five seed blocks, not 20 independent seeds. The verifier checks disjoint jobs, runs and seeds; collection numbers 1-20; and all five complete cyclic blocks against an explicitly supplied read-only copy of the earlier collection.

There are {sum(defaults.values())} deterministic engine-default actions: {defaults['anthropic/claude-opus-5.5']} for Claude Opus 5.5 and {defaults['google/gemini-4-argon']} for Gemini 4 Argon. Game 13 contains 39 Claude defaults after repeated illogical post-turn choices. All 39 applied `end_turn`; Claude also won this game. Game 18 contains two more Claude defaults, and game 19 contains one Gemini default. These are engine-applied legal actions under the configured recovery policy, not valid model answers. Their frequency and effect must remain visible in the paper. This integrity audit does not establish that model behavior was flawless or justify silently removing affected games.

Claude Opus 5.5 recorded {sum(refusals['anthropic/claude-opus-5.5'].values())} refused resolver attempts, all at the standard stage. No refused same-model action-only or Opus 4.8 recovery attempts were recorded. The configured no-private-thought recovery remains part of the treatment. No physical Opus 4.8 call occurred. Standard, action-only, provider reasoning and emitted private-thought evidence remain separate in the original artifacts.

There are {totals['missing_calls']} missing-cost calls and {totals['unknown_calls']} unknown-cost calls among {totals['calls']:,} physical calls. The known recorded subtotal is ${totals['known_total']:.6f}, with ${totals['openrouter_charge']:.6f} reported OpenRouter charges and ${totals['provider_charge']:.6f} reported upstream provider charges. Missing and unknown amounts are not zero. These records do not establish a complete final invoice or any free-token discount.

Five physical transport calls failed: one Gemini network error, two xAI network errors and two xAI total timeouts. They were retried without recorded job pauses or premature endings. No HTTP 429 or HTTP 5xx response was recorded in the call ledgers. The failed-call intents and available response evidence are preserved.

## Game ledger

{chr(10).join(ledger)}

## Verification and scope

Use MonopolyBench's `python/.venv/bin/python` to run `audit/scripts/verify_collection.py`. ZIPs default to this folder's `archives/`; `--archives /path/to/ZIPs` overrides that location. The earlier collection defaults to the sibling `railway-research-12-games-2026-10-25` and can be overridden with `--earlier /path/to/extracted/earlier-collection`. A missing or incomplete earlier folder produces an explicit fatal error rather than silently skipping combined validation. The counts of games and ZIPs come from the download index.

The comparison reference for this import was a temporary `git archive` extraction of the earlier collection from origin/main commit b480e987227ac044722ad62289f3066edda34ac7. Only that temporary copy was used for combined-set reads. The archive and extraction procedure does not require changing a checkout or registering a worktree. Verification command logs and the final handoff report are kept outside this collection so they do not alter its final manifest.

This review checks preservation, deterministic replay, recorded design, routing and accounting reconciliation. It does not replace downstream qualitative coding or certify the paper's scientific conclusions.
'''
(ROOT/'README.md').write_text(text);(ROOT/'audit/inspection-report.txt').write_text(text)
scripts=ROOT/'audit/scripts'
for src in ['mb_download20.py','mb_audit20.py','mb_import20_auth.py','mb_finish20.py']:shutil.copyfile('/tmp/'+src,scripts/src)
(scripts/'README.txt').write_text('verify_collection.py is the repeatable read-only verifier, adapted from b480e987. It needs the installed MonopolyBench Python packages and requires an earlier collection with an audit/download-index.json. Other scripts record the download/audit/assembly procedure; do not rerun the importer blindly. Auth is loaded from the existing local Railway CLI login and stays in memory. The one-time auth helper expects a CLI at /tmp/mb-railway-cli/node_modules/.bin/railway. No credential values are embedded in these scripts.\n')
print(json.dumps(summary,indent=2))
