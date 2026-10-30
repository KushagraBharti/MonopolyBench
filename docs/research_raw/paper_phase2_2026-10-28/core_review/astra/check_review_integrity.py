"""Verify review references and coverage without pretending to verify semantics."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
ROOT = HERE.parents[4]


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    digests = {}

    def digest(path):
        path = path.resolve()
        if path not in digests:
            digests[path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return digests[path]

    catalog = rows(CORE / 'candidate_catalog.jsonl')
    sample = rows(CORE / 'public_unflagged_sample.jsonl')
    expected_catalog = {r['catalog_id'] for r in catalog}
    expected_sample = {r['decision_id'] for r in sample}
    assert len(catalog) == len(expected_catalog) == 614
    assert len(sample) == len(expected_sample) == 240
    assert set(Counter((r['game'], r['player_id']) for r in sample).values()) == {3}
    coverage = {}
    for name in ['astra', 'sol', 'opus', 'fable']:
        cases = rows(CORE / name / 'case_reviews.jsonl')
        controls = rows(CORE / name / 'negative_control_reviews.jsonl')
        assert len(cases) == 614 and {r['catalog_id'] for r in cases} == expected_catalog, name
        assert len(controls) == 240 and {r['decision_id'] for r in controls} == expected_sample, name
        for filename in ['game_assessments.md', 'methods_and_findings.md', 'claims.md', 'debate.md']:
            assert (CORE / name / filename).stat().st_size > 100
        coverage[name] = {'catalog_ids': 614, 'sample_ids': 240,
                          'catalog_sha256': digest(CORE / name / 'case_reviews.jsonl'),
                          'sample_sha256': digest(CORE / name / 'negative_control_reviews.jsonl'),
                          'coverage_limit': 'ID coverage, not independent semantic verification'}

    manifest = json.loads((CORE / 'manifest.json').read_text())
    for name, expected in manifest['source_sha256'].items():
        assert digest(ROOT / name) == expected, name
    for name, expected in manifest['generated_sha256'].items():
        assert digest(CORE / name) == expected, name

    source_cache = {}
    root_sample = {r['decision_id']: r for r in rows(HERE / 'negative_control_reviews.jsonl')}
    for unit in sample:
        path = ROOT / unit['packet']
        if path not in source_cache:
            source_cache[path] = rows(path)
        original = source_cache[path][unit['packet_line'] - 1]
        assert original['decision_id'] == unit['decision_id']
        assert root_sample[unit['decision_id']]['packet_sha256'] == digest(path)
        assert root_sample[unit['decision_id']]['status'] == 'reviewed'

    script_by_hash = {digest(p): str(p.relative_to(ROOT)) for p in CORE.rglob('*.py')}
    reports = {}
    source_hash_checks = 0
    source_fields = ['source_sha256', 'sources_sha256', 'source_hashes', 'packet_hashes',
                     'event_source_hashes', 'packet_source_hashes']
    for path in sorted(HERE.glob('*.json')):
        if path.name == 'review_integrity_checks.json':
            continue
        obj = json.loads(path.read_text())
        if not isinstance(obj, dict) or 'script_sha256' not in obj:
            continue
        sha = obj['script_sha256']
        assert sha in script_by_hash, f'Stale script digest: {path.name}'
        reports[path.name] = script_by_hash[sha]
        for field in source_fields:
            mapping = obj.get(field)
            if not isinstance(mapping, dict):
                continue
            for name, expected in mapping.items():
                if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
                    continue
                target = Path(name)
                if not target.is_absolute():
                    target = ROOT / target
                assert target.exists(), f'{path.name}: {name}'
                assert digest(target) == expected, f'{path.name}: changed {name}'
                source_hash_checks += 1

    links = []
    documents = ['methods_and_findings.md', 'claims.md', 'reconciliation.md', 'review_handoff.md']
    for name in documents:
        for link in re.findall(r'\]\(([^)]+)\)', (HERE / name).read_text()):
            if link.startswith(('http:', 'https:', '#')):
                continue
            target = HERE / link
            if target.name != 'review_integrity_checks.json':
                assert target.exists(), f'{name}: {link}'
            links.append({'document': name, 'target': link})

    result = {'status': 'passed', 'coauthor_coverage': coverage,
              'sample_strata': 80, 'source_packet_references_checked': 240,
              'manifest_source_checks': len(manifest['source_sha256']),
              'root_report_script_checks': reports, 'root_report_source_hash_checks': source_hash_checks,
              'final_document_links': links,
              'final_document_sha256': {name: digest(HERE / name) for name in documents},
              'hashed_files': {str(p.relative_to(ROOT)): sha for p, sha in digests.items()},
              'limits': 'Checks coverage, references and content identity. Does not certify semantic correctness, independent reading, human agreement or causal claims.'}
    (HERE / 'review_integrity_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'catalog_per_coauthor': 614, 'sample_per_coauthor': 240,
                      'source_hash_checks': source_hash_checks, 'script_checks': len(reports),
                      'links': len(links), 'hashed_files': len(digests)}))


if __name__ == '__main__':
    main()
