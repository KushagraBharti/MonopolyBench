import sys, json, pathlib, shutil, hashlib, tempfile, time
sys.path.insert(0, '/tmp')
sys.argv = ['helper', '_library_import']
import mb_pr9_release as a
from monopoly_telemetry.export import unpack_verified
from monopoly_telemetry.inventory import verify_inventory

ROOT = pathlib.Path('/Users/kushagra/.t3/worktrees/MonopolyBench/t3-930e9681/saved_games/railway-research-12-games-2026-10-25')
ROOT.mkdir(parents=True, exist_ok=True)
CS = [('first-four', 'campaign-81cf4868c2db4b77a0f0319b59fd6dee', 4), ('next-eight', 'campaign-c0761df29478459ab4cea725626ea259', 8)]
def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n')
def download(entry, archive, dest):
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        partial = archive.with_suffix('.partial')
        with a.http.open(a.BASE + '/api/exports/' + entry['export_id'] + '/download', timeout=180) as response, partial.open('wb') as out:
            shutil.copyfileobj(response, out)
        assert partial.stat().st_size == entry['bytes']
        partial.rename(archive)
    assert archive.stat().st_size == entry['bytes']
    if not dest.exists():
        with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
            stage = pathlib.Path(tmp) / 'package'
            unpack_verified(archive, stage)
            assert verify_inventory(stage)['tree_sha256'] == entry['manifest_sha256']
            stage.rename(dest)
    manifest = verify_inventory(dest)
    assert manifest['tree_sha256'] == entry['manifest_sha256']
    return {'archive': str(archive.relative_to(ROOT)), 'package': str(dest.relative_to(ROOT)), 'archive_bytes': archive.stat().st_size, 'archive_sha256': hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest(), 'tree_sha256': manifest['tree_sha256'], 'files': len(manifest['files']), 'export_id': entry['export_id']}

save(ROOT / 'audit/live-status.json', a.request('status'))
index = {'source': a.BASE, 'downloaded_at_unix': time.time(), 'campaigns': [], 'games': []}
for label, cid, expected in CS:
    folder = ROOT / label
    folder.mkdir(exist_ok=True)
    campaign = a.request('campaigns/' + cid)
    assert campaign['status'] == 'done' and len(campaign['cells']) == expected
    save(folder / 'campaign-live.json', campaign)
    receipt_path = folder / 'campaign-export-receipt.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
    else:
        receipt = a.request('campaigns/' + cid + '/export', {})
        save(receipt_path, receipt)
    exports = a.request('exports')
    entry = next(e for e in exports if e['export_id'] == receipt['export_id'])
    print('Downloading final campaign snapshot: ' + label, flush=True)
    record = download(entry, ROOT / 'archives' / (label + '-final-campaign.zip'), folder / 'final-campaign')
    evidence = json.loads((folder / 'final-campaign/campaign.json').read_text())
    assert len(evidence['jobs']) == expected and all(j['status'] == 'completed' for j in evidence['jobs'])
    record.update({'label': label, 'campaign_id': cid, 'revision': entry['revision']})
    index['campaigns'].append(record)
    for cell in sorted(campaign['cells'], key=lambda c:c['cell_index']):
        job = cell['game']
        assert all(job[k] == v for k,v in [('status','completed'),('replay_status','passed'),('analysis_status','completed'),('export_status','ready')])
        entry = max((e for e in exports if e['scope']=='job' and e['scope_id']==job['job_id']), key=lambda e:e['revision'])
        name = str(cell['cell_index']) + '-' + job['run_id']
        package = folder / 'final-campaign' / cid / name
        manifest = verify_inventory(package)
        assert manifest['tree_sha256'] == entry['manifest_sha256']
        # Keep the original per-game ZIP as well as the verified campaign tree.
        archive = ROOT / 'archives' / (job['job_id'] + '.zip')
        if not archive.exists():
            with a.http.open(a.BASE + '/api/exports/' + entry['export_id'] + '/download', timeout=180) as response, archive.with_suffix('.partial').open('wb') as out:
                shutil.copyfileobj(response, out)
            archive.with_suffix('.partial').rename(archive)
        assert archive.stat().st_size == entry['bytes']
        game = {'batch':label, 'game':cell['cell_index']+1, 'job_id':job['job_id'], 'run_id':job['run_id'], 'package':str(package.relative_to(ROOT)), 'archive':str(archive.relative_to(ROOT)), 'archive_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(), 'tree_sha256':manifest['tree_sha256'], 'files':len(manifest['files']), 'export_id':entry['export_id'], 'git_sha':job['git_sha'], 'turns':job['snapshot']['turn_index'], 'cost':job['cost']}
        index['games'].append(game)
        save(ROOT/'audit/download-index.json', index)
        print('Saved '+label+' game '+str(game['game'])+' ('+str(game['files'])+' files)', flush=True)
save(ROOT/'audit/download-index.json', index)
assert len(index['games']) == 12
print('All 12 downloaded: '+str(ROOT), flush=True)
