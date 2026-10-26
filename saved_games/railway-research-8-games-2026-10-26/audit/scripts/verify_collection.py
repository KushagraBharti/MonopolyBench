"""Read-only verification, adapted from origin/main b480e987's 12-game verifier.

Counts come from download-index.json. The sibling earlier collection is required
for the combined 20-game check. Pass --earlier for another read-only copy.
The local archives/ folder is used by default; --archives overrides it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
import collections

from monopoly_arena.long_campaign import _completed_run_exists
from monopoly_telemetry.inventory import inventory, tree_hash, verify_inventory

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description='Verify this collection and the combined 20-game research set.')
parser.add_argument('--archives', type=Path, help='folder holding the original ZIPs; uses root/archives when present')
parser.add_argument('--earlier', type=Path, default=root.parent / 'railway-research-12-games-2026-10-25', help='earlier 12-game collection, including its audit/download-index.json')
args = parser.parse_args()
if args.archives and not args.archives.is_dir():
    parser.error(f'No ZIP folder at {args.archives}')
archives = args.archives or root / 'archives'

index = json.loads((root / 'audit/download-index.json').read_text())
game_count = len(index['games'])
entries = [*index['games'], *index['campaigns']]
archive_count = len(entries)
assert game_count > 0
earlier_index = args.earlier / 'audit/download-index.json'
if not earlier_index.is_file():
    parser.error(f'EARLIER COLLECTION MISSING OR INCOMPLETE: {earlier_index}. Combined 20-game validation cannot be skipped; pass --earlier with an extracted reference.')
earlier = json.loads(earlier_index.read_text())
for field in ['job_id', 'run_id']:
    assert len({g[field] for g in index['games']}) == game_count
    assert len({g[field] for g in earlier['games']}) == len(earlier['games'])
    assert {g[field] for g in index['games']}.isdisjoint(g[field] for g in earlier['games']), f'Shared {field}'
earlier_runs = [(g, json.loads((args.earlier / g['package'] / 'run/run_config.json').read_text())) for g in earlier['games']]
current_runs = [(g, json.loads((root / g['package'] / 'run/run_config.json').read_text())) for g in index['games']]
assert {r['seed'] for _, r in earlier_runs}.isdisjoint(r['seed'] for _, r in current_runs), 'Shared seed across collections'
combined = earlier_runs + current_runs
assert len(combined) == 20
assert sorted(g['collection_game'] for g, _ in combined) == list(range(1, 21)), 'Collection numbering must cover 1-20 exactly'
blocks = collections.defaultdict(list)
for game, config in combined:
    assert game['run_id'] == config['run_id']
    blocks[config['seed']].append(config)
assert len(blocks) == 5, 'Expected five independent seed blocks'
roster = ['anthropic/claude-opus-5.5', 'openai/gpt-6.1-sol', 'google/gemini-4-argon', 'x-ai/grok-4.7']
expected_rotations = collections.Counter(tuple(roster[i:] + roster[:i]) for i in range(4))
for seed, runs in blocks.items():
    assert len(runs) == 4, f'Seed {seed} does not have four games'
    actual = collections.Counter(tuple(p['openrouter_model_id'] for p in run['players']) for run in runs)
    assert actual == expected_rotations, f'Seed {seed} does not have all cyclic rotations'
print('Combined check passed: 20 unique games, collection numbers 1-20, five disjoint seed blocks with all cyclic rotations.', flush=True)
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
    print(f'{game_count} games verified. Original ZIPs not checked: none at {archives}; pass --archives to check them. No saved files changed.')
    raise SystemExit
for entry in entries:
    archive = archives / Path(entry['archive']).name
    with archive.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    assert digest == entry['archive_sha256'] == recorded[entry['archive']]['sha256']
    assert archive.stat().st_size == recorded[entry['archive']]['bytes']
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
print(f'{game_count} games and {archive_count} original archives verified. No saved files changed.')
