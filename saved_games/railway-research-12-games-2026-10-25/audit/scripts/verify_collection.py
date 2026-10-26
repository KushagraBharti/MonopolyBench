"""Read-only verification. Run with MonopolyBench's python/.venv/bin/python."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from monopoly_arena.long_campaign import _completed_run_exists
from monopoly_telemetry.inventory import verify_inventory

root = Path(__file__).resolve().parents[2]
index = json.loads((root / 'audit/download-index.json').read_text())
assert len(index['games']) == 12
if (root / 'storage_manifest.json').exists():
    verify_inventory(root)
for game in index['games']:
    package = root / game['package']
    assert verify_inventory(package)['tree_sha256'] == game['tree_sha256']
    with tempfile.TemporaryDirectory(prefix='mb-saved-replay-') as scratch:
        run = Path(scratch) / game['run_id']
        run.symlink_to(package / 'run', target_is_directory=True)
        assert _completed_run_exists(run), game['run_id']
    print(f"Game {game['collection_game']:02d}: integrity, completion and independent replay passed", flush=True)
for entry in [*index['games'], *index['campaigns']]:
    archive = root / entry['archive']
    with archive.open('rb') as handle:
        assert hashlib.file_digest(handle, 'sha256').hexdigest() == entry['archive_sha256']
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
