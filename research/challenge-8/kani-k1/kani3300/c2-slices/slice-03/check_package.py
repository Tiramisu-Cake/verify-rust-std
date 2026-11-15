#!/usr/bin/env python3
"""Final handoff integrity check; refresh only the research file manifest."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = '/root/kani-fix-3300-c2-slices-w14'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads((HERE / path).read_text())


def main():
    source, static, audit, req, tests = [read(p) for p in [
        'SLICE.json', 'STATIC-VALIDATION.json', 'SEAM-AUDIT-03.json', 'CI-REQUEST.json', 'TEST-MANIFEST.json']]
    head = subprocess.check_output(['git', '-C', REPO, 'rev-parse', 'HEAD']).decode().strip()
    assert head == source['source_sha'] == static['source_sha'] == audit['head'] == req['source_sha'] == tests['source_sha']
    assert source['source_tree'] == static['source_tree'] == req['source_tree']
    assert source['base_sha'] == static['base_sha'] == audit['base'] == req['parent'] == '932fb8395a58f8c86c0d702ba2cae835823b2962'
    assert not subprocess.check_output(['git', '-C', REPO, 'status', '--porcelain'])
    assert audit['status'] == 'PASS_BOUNDED_STATIC_SEAM_AUDIT' and not audit['errors']
    assert audit['contracts_sha256'] == sha((HERE / 'CALL-CONTRACTS-03.json').read_bytes())
    assert audit['tool_sha256'] == sha((HERE.parent / 'seam-audit/check_seams.py').read_bytes())
    for name, expected in source['maps'].items():
        assert sha((HERE.parent / name).read_bytes()) == expected, name
    for name, expected in source['patches'].items():
        assert sha((HERE / name).read_bytes()) == expected['sha256'], name
    oracle = read('ORACLE-DELTA.json')
    assert len(oracle['selected_complete_fixtures']) == 19 and len(oracle['deferred_owner3_fixtures']) == 9
    assert len(read('SOURCE-PARTS.json')['parts']) == static['owner3_part_hashes_checked'] == 22
    selected = oracle['selected_complete_fixtures']
    assert all(r['oracle']['precision'] == 'F_LITERAL_ONLY_NO_EXACT_PROPERTY_COUNT' for r in selected)
    assert sum('VERIFICATION:- SUCCESSFUL' in r['oracle']['verdict_lines'] for r in selected) == 10
    assert sum('VERIFICATION:- FAILED' in r['oracle']['verdict_lines'] for r in selected) == 9
    assert req['static_counts'] == tests['deduplicated_suite_counts']
    assert req['selector_count'] == tests['deduplicated_selector_count'] == 336
    assert sum(r['existing_path_ignored'] for r in req['static_counts'].values()) == 9
    assert source['qualification_status'] == req['native_results'] == 'NOT_RUN'
    assert source['nested_offset_integration_status'] == source['worker15_review'] == 'PENDING'
    assert source['deferred_integration_heads'] == [4] and req['no_authorization_to_dispatch']
    report = {'status': 'PASS_STATIC_PACKAGE_INTEGRITY', 'source_sha': head,
        'checks': ['exact source/base/tree across reports', 'source clean', 'seam tool/contract hashes',
            'all pinned map/patch hashes', '22 source parts', '19 exact-map fixture records and9 pending4',
            '10 positive/9 negative literal-only intended goldens', '336 selectors and9 existing ignores',
            'native NOT_RUN/review PENDING preserved'], 'native_builds_push_CI': 'NOT_RUN'}
    (HERE / 'PACKAGE-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    manifest = {'source_sha': head, 'source_tree': source['source_tree'], 'base_sha': source['base_sha'],
        'files': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
            for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'MANIFEST.json']}
    (HERE / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
