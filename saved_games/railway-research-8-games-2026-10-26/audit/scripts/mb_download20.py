import sys,json,pathlib,shutil,hashlib,tempfile,time,zipfile
sys.path.insert(0,'/tmp');import mb_import20_auth as a
from monopoly_telemetry.export import unpack_verified
from monopoly_telemetry.inventory import verify_inventory
ROOT=pathlib.Path('/Users/kushagra/MonopolyBench-research/railway-research-8-games-2026-10-26')
CID='campaign-8d77f7b822c6458fa9a5be0e884f74ef'
ROOT.mkdir(parents=True,exist_ok=True)
for name in ['archives','audit','audit/scripts','campaigns/'+CID]:(ROOT/name).mkdir(parents=True,exist_ok=True)
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
before=json.loads(pathlib.Path('/Users/kushagra/.t3/artifacts/monopolybench-railway-20261025/research-blocks-4-5/download-initial.json').read_text())
campaign=before['campaign'];meta=ROOT/'campaigns'/CID
save(ROOT/'audit/live-status.json',{'health':before['health'],'status':before['status'],'observed_at_unix':time.time(),'jobs':[{'job_id':j['job_id'],'status':j['status']} for j in before['jobs']]})
save(meta/'campaign-live.json',campaign)
receipt=meta/'campaign-export-receipt.json'
if receipt.exists(): exported=json.loads(receipt.read_text())
else:
    exported=a.request('campaigns/'+CID+'/export',{});save(receipt,exported)
exports=a.request('exports');save(ROOT/'audit/server-export-entries.json',[e for e in exports if e.get('campaign_id')==CID or e.get('scope_id')==CID])
def download(entry,name):
    archive=ROOT/'archives'/name
    if not archive.exists():
        with a.http.open(a.BASE+'/api/exports/'+entry['export_id']+'/download',timeout=180) as response,archive.with_suffix('.partial').open('wb') as out:shutil.copyfileobj(response,out)
        assert archive.with_suffix('.partial').stat().st_size==entry['bytes']
        archive.with_suffix('.partial').rename(archive)
    assert archive.stat().st_size==entry['bytes']
    with archive.open('rb') as h:digest=hashlib.file_digest(h,'sha256').hexdigest()
    published=entry.get('archive_sha256') or entry.get('zip_sha256')
    if published:assert digest==published
    return archive,digest
index={'source':a.BASE,'downloaded_at_unix':time.time(),'campaigns':[],'games':[],'server_archive_sha256_published':False,'integrity_note':'Server entries expose bytes and manifest_sha256, the canonical content tree hash. ZIP byte SHA-256 is computed locally; each member is independently verified against the server-pinned content inventory.'}
for cell in sorted(campaign['cells'],key=lambda c:c['cell_index']):
    job=cell['game'];number=13+cell['cell_index'];turns=job['snapshot']['turn_index']
    entry=max((e for e in exports if e['scope']=='job' and e['scope_id']==job['job_id']),key=lambda e:e['revision'])
    archive,digest=download(entry,job['job_id']+'.zip')
    package=ROOT/f"game-{number:02d}-{turns}turns-{job['job_id'][:8]}"
    if not package.exists():
        with tempfile.TemporaryDirectory(prefix='mb-import-stage-',dir=ROOT.parent) as tmp:
            stage=pathlib.Path(tmp)/'game';unpack_verified(archive,stage)
            assert verify_inventory(stage)['tree_sha256']==entry['manifest_sha256'];stage.rename(package)
    manifest=verify_inventory(package);assert manifest['tree_sha256']==entry['manifest_sha256']
    index['games'].append({'batch':'research-blocks-4-5','game':cell['cell_index']+1,'collection_game':number,'cell_index':cell['cell_index'],'job_id':job['job_id'],'run_id':job['run_id'],'package':package.name,'archive':str(archive.relative_to(ROOT)),'archive_bytes':archive.stat().st_size,'archive_sha256':digest,'tree_sha256':manifest['tree_sha256'],'files':len(manifest['files']),'export_id':entry['export_id'],'git_sha':job['git_sha'],'turns':turns,'cost':job['cost']})
    save(ROOT/'audit/download-index.json',index)
    print(f'Downloaded and verified game {number}: {len(manifest["files"])} files',flush=True)
entry=next(e for e in exports if e['export_id']==exported['export_id'])
archive,digest=download(entry,'research-blocks-4-5-final-campaign.zip')
with tempfile.TemporaryDirectory(prefix='mb-campaign-stage-',dir=ROOT.parent) as tmp:
    stage=pathlib.Path(tmp)/'campaign';unpack_verified(archive,stage);manifest=verify_inventory(stage)
    assert manifest['tree_sha256']==entry['manifest_sha256']
    evidence=json.loads((stage/'campaign.json').read_text());assert len(evidence['jobs'])==8 and all(j['status']=='completed' for j in evidence['jobs'])
    for game in index['games']:
        nested=stage/CID/(str(game['cell_index'])+'-'+game['run_id']);assert verify_inventory(nested)['tree_sha256']==game['tree_sha256']
    for name in ['campaign.json','cost.json','freeze_manifest.json','preflight.json']:shutil.copyfile(stage/name,meta/name)
    shutil.copyfile(stage/'storage_manifest.json',meta/'original-campaign-storage-manifest.json')
index['campaigns'].append({'archive':str(archive.relative_to(ROOT)),'archive_bytes':archive.stat().st_size,'archive_sha256':digest,'tree_sha256':manifest['tree_sha256'],'files':len(manifest['files']),'export_id':entry['export_id'],'campaign_id':CID,'label':'research-blocks-4-5','revision':entry['revision'],'metadata':str(meta.relative_to(ROOT))})
save(ROOT/'audit/download-index.json',index)
print('Downloaded all 8 games and final campaign ZIP',flush=True)
