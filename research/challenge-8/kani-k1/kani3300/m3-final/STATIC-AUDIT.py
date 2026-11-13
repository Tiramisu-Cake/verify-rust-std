#!/usr/bin/env python3
"""Static M3 handoff identity/scope checks. Does not invoke Rust tools or CI."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
BASE = '53d883add5b0ab18202f1e6b7cc33356549a6a83'
PREFIXES = ('tests/expected/uninit/mixed-promoted-allocations/',
            'tests/expected/uninit/part1-composition/',
            'tests/json-handler/uninit-part1-composition/')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(repo):
    manifest = json.loads((HERE / 'TEST-MANIFEST.json').read_text())
    imported = json.loads((HERE / 'IMPORT-MANIFEST.json').read_text())
    assert git(repo, 'rev-parse', 'HEAD') == manifest['prepared_source_sha']
    assert git(repo, 'rev-parse', 'HEAD^{tree}') == manifest['prepared_source_tree']
    assert git(repo, 'rev-parse', BASE + '^{tree}') == '36678461cfc79f4efc1a2b979ddb03f92f18cefc'
    assert git(repo, 'merge-base', BASE, 'HEAD') == BASE
    assert len(imported['files']) == 16
    assert sum(x['repair_changed'] for x in imported['files']) == 4
    for row in imported['files']:
        assert digest(repo / row['path']) == row['sha256'], row['path']
        blob = subprocess.check_output(['git', '-C', str(repo), 'show',
                                        imported['snapshot'] + ':' + row['path']])
        assert hashlib.sha256(blob).hexdigest() == row['sha256']
    for row in manifest['files']:
        assert digest(repo / row['path']) == row['sha256'], row['path']
    controls = json.loads((HERE / 'CONTROL-MANIFEST.json').read_text())
    for row in controls['files']:
        assert digest(repo / row['path']) == row['sha256'], row['path']
        baseline = subprocess.check_output(['git', '-C', str(repo), 'show',
                                             BASE + ':' + row['path']])
        assert hashlib.sha256(baseline).hexdigest() == row['sha256']
    known = {row['path'] for row in manifest['files']}
    actual = {str(p.relative_to(repo)) for prefix in PREFIXES
              for p in (repo / prefix).rglob('*') if p.is_file()
              and '__pycache__' not in p.parts}
    assert actual == known, ('missing/extra package paths', actual ^ known)
    diff = git(repo, 'diff', '--name-only', BASE).splitlines()
    untracked = git(repo, 'ls-files', '--others', '--exclude-standard').splitlines()
    assert all(path.startswith(PREFIXES) for path in diff + untracked), diff + untracked
    assert git(repo, 'diff', '--name-only', BASE, '--', 'scripts/validate_json_export.py',
               'tests/json-handler/uninit-contract-oracles',
               'tests/json-handler/uninit-contract-mode-boundaries') == ''
    composition = repo / PREFIXES[1]
    sources = sorted(composition.glob('*.rs'))
    assert len(sources) == 8
    roots = []
    for source in sources:
        text = source.read_text()
        assert 'MU<[MU<' not in text and 'kani::assume(' not in text
        assert '#[kani::should_panic]' not in text
        assert source.with_suffix('.expected').is_file()
        roots.extend(re.findall(r'#\[kani::proof\]\s*fn (\w+)\(', text))
    assert len(roots) == 9 and len(set(roots)) == 9
    return {'scope': 'PASS tests-only; existing suites/validator unchanged',
            'import': 'PASS 16 exact snapshot files; four repaired Rust sources',
            'package_files': len(known), 'composition_selectors': 8,
            'composition_roots': 9, 'unchanged_control_files': len(controls['files']),
            'identities': 'PASS',
            'rust_typecheck': 'NOT_RUN', 'MIR_Kani_CBMC_CI': 'NOT_RUN',
            'producer_order': 'ORDER_UNCONTROLLED', 'proof_credit': 'NONE'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('/root/kani-fix-3300-m3'))
    print(json.dumps(check(parser.parse_args().repo), indent=2))
