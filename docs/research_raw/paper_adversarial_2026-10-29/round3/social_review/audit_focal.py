"""Read a fixed set of historical social cases; write only this review directory."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json'
FOCAL = {4: list(range(138, 154)) + [175, 176, 177], 6: [19, 20, 21], 11: [255, 256, 257, 258],
         13: list(range(243, 255)) + [311], 18: list(range(419, 464)),
         19: [135, 136], 20: [1, 2, 3, 4]}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_rows(path):
    return [(i, json.loads(line)) for i, line in enumerate(path.open(), 1)]

def main():
    games = {g['game']: g for g in json.loads(MANIFEST.read_text())['games']}
    sources = {str(MANIFEST.relative_to(ROOT)): digest(MANIFEST)}
    bundles = []
    for game, indices in FOCAL.items():
        run = ROOT / games[game]['run']
        rows = {}
        for name in ['events.jsonl', 'actions.jsonl', 'decisions.jsonl']:
            path = run / name
            rows[name] = read_rows(path)
            sources[str(path.relative_to(ROOT))] = digest(path)
        for idx in indices:
            suffix = f'-dec-{idx:06d}'
            decisions = [(line, r) for line, r in rows['decisions.jsonl'] if r['decision_id'].endswith(suffix)]
            started = next(r for _, r in decisions if r['phase'] == 'decision_started')
            resolved = next(r for _, r in decisions if r['phase'] == 'decision_resolved')
            actions = [(line, r) for line, r in rows['actions.jsonl'] if r['decision_id'].endswith(suffix)]
            lo, hi = resolved['emitted_event_seq_start'], resolved['emitted_event_seq_end']
            events = [(line, r) for line, r in rows['events.jsonl'] if lo <= r['seq'] <= hi]
            files = []
            for path in sorted((run / 'prompts').glob(f'*{suffix}*')):
                rel = str(path.relative_to(ROOT))
                sources[rel] = digest(path)
                files.append(rel)
            bundles.append({'game': game, 'index': idx, 'run': str(run.relative_to(ROOT)),
                            'decisions': decisions, 'actions': actions, 'events': events, 'prompt_files': files})
    baseline = ROOT / 'docs/research_raw/paper_adversarial_2026-10-29/round3/baseline'
    bm = baseline.parent / 'baseline_manifest.json'
    sources[str(bm.relative_to(ROOT))] = digest(bm)
    checks = []
    for rel, expected in json.loads(bm.read_text()).items():
        path = baseline / rel
        actual = digest(path)
        checks.append({'path': str(path.relative_to(ROOT)), 'expected': expected, 'actual': actual, 'match': actual == expected})
    for path in (baseline / 'sections').glob('*.tex'):
        sources[str(path.relative_to(ROOT))] = digest(path)
    (OUT / 'focal_bundles.json').write_text(json.dumps(bundles, indent=2) + '\n')
    (OUT / 'source_hashes.json').write_text(json.dumps(sources, indent=2, sort_keys=True) + '\n')
    (OUT / 'baseline_integrity.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps({'bundles': len(bundles), 'hashed_sources': len(sources), 'baseline_checked': len(checks),
                      'baseline_mismatches': [c['path'] for c in checks if not c['match']]}))

if __name__ == '__main__':
    main()
