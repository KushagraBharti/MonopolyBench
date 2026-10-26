"""Read-only verification. Run with MonopolyBench's python/.venv/bin/python.

The 14 original server ZIPs are kept outside git. Without them, this checks every
committed file against storage_manifest.json and replays all 12 games. Pass the
ZIP folder with --archives to check the ZIPs too; an archives/ folder next to
this collection is used automatically.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from monopoly_arena.long_campaign import _completed_run_exists
from monopoly_telemetry.inventory import inventory, tree_hash, verify_inventory

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description='Verify the 12-game research collection.')
parser.add_argument('--archives', type=Path, help='folder holding the 14 original ZIPs')
args = parser.parse_args()
if args.archives and not args.archives.is_dir():
    parser.error(f'No ZIP folder at {args.archives}')
archives = args.archives or root / 'archives'

index = json.loads((root / 'audit/download-index.json').read_text())
assert len(index['games']) == 12
# The manifest records the whole collection, including the ZIPs kept outside git.
manifest = json.loads((root / 'storage_manifest.json').read_text())
assert manifest['tree_sha256'] == tree_hash(manifest['files'])
recorded = {f['path']: f for f in manifest['files']}
committed = {path: f for path, f in recorded.items() if not path.startswith('archives/')}
present = {f['path']: f for f in inventory(root)['files'] if not f['path'].startswith('archives/')}
assert present == committed, 'Committed files differ from storage_manifest.json'
for game in index['games']:
    package = root / game['package']
    assert verify_inventory(package)['tree_sha256'] == game['tree_sha256']
    with tempfile.TemporaryDirectory(prefix='mb-saved-replay-') as scratch:
        run = Path(scratch) / game['run_id']
        run.symlink_to(package / 'run', target_is_directory=True)
        assert _completed_run_exists(run), game['run_id']
    print(f"Game {game['collection_game']:02d}: integrity, completion and independent replay passed", flush=True)
if not archives.is_dir():
    print(f'12 games verified. Original ZIPs not checked: none at {archives}; pass --archives to check them. No saved files changed.')
    raise SystemExit
for entry in [*index['games'], *index['campaigns']]:
    archive = archives / Path(entry['archive']).name
    with archive.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    assert digest == entry['archive_sha256'] == recorded[entry['archive']]['sha256']
    with zipfile.ZipFile(archive) as handle:
        manifest = json.loads(handle.read('storage_manifest.json'))
        names = handle.namelist()
        assert len(names) == len(set(names))
        assert set(names) == {f['path'] for f in manifest['files']} | {'storage_manifest.json'}
        for item in manifest['files']:
            data = handle.read(item['path'])
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256']
        assert manifest['tree_sha256'] == entry['tree_sha256']
print('12 games and 14 original archives verified. No saved files changed.')
