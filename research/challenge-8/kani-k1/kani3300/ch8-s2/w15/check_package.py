#!/usr/bin/env python3
"""Static identity/inventory checks only; never imports/executes Rust or proof runners."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
INPUTS = json.loads((ROOT / 'INPUTS.json').read_text())
WORKTREE = INPUTS['source_worktree']
PREFIX = 'library/core/src/slice/sort/shared/smallsort/verify/'


def git(*args):
    return subprocess.check_output(['git', '-C', WORKTREE, *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    for path in ROOT.rglob('*.json'):
        json.loads(path.read_text())
    base, source = INPUTS['base'], INPUTS['source']
    assert git('rev-parse', source + '^').decode().strip() == base
    assert git('rev-parse', source + '^{tree}').decode().strip() == INPUTS['source_tree']
    assert git('rev-parse', 'HEAD').decode().strip() == source
    assert not git('status', '--porcelain').strip(), 'source worktree must be clean'
    delta = git('diff', '--name-only', base, source).decode().splitlines()
    expected = {PREFIX + 'sorting_merge_' + part + '.rs'
                for part in ['model', 'probe', 'invariant', 'controls']}
    assert set(delta) == expected, delta
    assert git('diff', '--diff-filter=A', '--name-only', base, source).decode().splitlines() == delta
    git('diff', '--check', base, source)
    for path in ['library/core/src/slice/sort/shared/smallsort.rs',
                 'library/core/src/slice/sort/shared/smallsort/verify.rs',
                 PREFIX + 'merge.rs', 'tool_config/kani-version.toml']:
        assert git('rev-parse', base + ':' + path) == git('rev-parse', source + ':' + path)
    dep = git('show', INPUTS['model_source'] + ':' + INPUTS['model_path'])
    assert sha(dep) == INPUTS['model_sha256']
    interface = ROOT.parents[1] / 'ch8-s1/w11/INTERFACE.md'
    assert sha(interface.read_bytes()) == INPUTS['interface_sha256']
    assert (ROOT / 'source.patch').read_bytes() == git('format-patch', '--no-signature', '--stdout', base + '..' + source)
    request = json.loads((ROOT / 'CI-REQUEST.json').read_text())
    roots = {}
    source_bytes = {}
    for path in delta:
        data = git('show', source + ':' + path).decode()
        source_bytes[path] = sha(data.encode())
        assert '#[kani::stub' not in data
        assert '#[kani::proof_for_contract' not in data
        module = Path(path).stem
        for name in re.findall(r'#\[kani::proof\]\s*#\[kani::unwind\(\d+\)\]\s*fn\s+(\w+)', data):
            selector = 'slice::sort::shared::smallsort::verify::' + module + '::' + name
            roots[selector] = data
    assert len(roots) == 12
    assert set(roots) == {row['selector'] for row in request['rows']}
    assert sum(row['estimated_seconds_unmeasured'] for row in request['rows']) == 1650
    for row in request['rows']:
        assert row['property_ids'] is None and row['state'] == 'NOT_RUN'
        assert row['unwind'] in (4, 34)
        if row['selector'].endswith(('s2_merge_rejects_wrong_count', 's2_merge_rejects_unsorted_output')):
            assert row['obligations'][0] in roots[row['selector']]
    assert request['dispatch_cap_shared'] == 2
    assert request['combined_export_sha'] is None and request['ci_control_sha'] is None
    assert request['root_hard_seconds'] == 600 and request['jobs'] == 1
    assert request['aggregate_rss_cap_kib'] / 1048576 == 6
    assert request['uninit'] is False and request['valid_value'] is False
    proposal = (ROOT / 'INTEGRATION-PROPOSAL.md').read_text()
    assert 'cfg(all(kani_smallsort_sorting, kani_smallsort_controls))' in proposal
    result = {'state': 'STATIC_CHECKS_PASS', 'source': source, 'source_files': source_bytes,
              'roots': len(roots), 'request_sha256': sha((ROOT / 'CI-REQUEST.json').read_bytes()),
              'patch_sha256': sha((ROOT / 'source.patch').read_bytes()),
              'checks': ['JSON syntax', 'source parent/tree/clean status', 'four addition-only files',
                         'protected source identities', 'model/interface dependency hashes',
                         'patch identity', '12 root selectors and controls inventory',
                         'no stubs/PFC', 'request caps and estimates', 'control registration cfg'],
              'not_run': ['Rust parsing/compilation', 'loop extraction', 'verifier', 'CI'],
              'proof_credit': 'NONE'}
    (ROOT / 'static-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
