#!/usr/bin/env python3
"""Independent bounded static/synthetic S2 review; no compiler or dispatch."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest import mock

G = Path('/root/verify-rust-std-kani3300-g0')
S = Path('/root/verify-rust-std-ch8-s2-batch-w13')
C = Path('/root/kani-ch8-s2-batch-w13')
B = 'research/challenge-8/kani-k1/kani3300/ch8-s2/batch'
P = 'research/challenge-8/kani-k1/kani3300/ch8-s2/merge-pilot'
G0 = 'ae8f7b2feb739fd51fe72063d4aa71fe36b90790'
PILOT = 'c8e4ab764d58bd8b684b660d92c62374530623d4'
SOURCE = '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'
BASE = '99e8456d200fff1299ee5756279cddb23921dc65'
CONTROL = 'fc058c97335e4a064c7827b8534b3af2f7460bc3'
SMALL = 'library/core/src/slice/sort/shared/smallsort.rs'
VERIFY = 'library/core/src/slice/sort/shared/smallsort/verify'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exact_package(commit, prefix, count):
    paths = git(G, 'ls-tree', '-r', '--name-only', commit, prefix).decode().splitlines()
    assert len(paths) == count
    hashes = {}
    for path in paths:
        pinned = git(G, 'show', commit + ':' + path)
        assert (G / path).read_bytes() == pinned, path
        hashes[path.removeprefix(prefix + '/')] = digest(pinned)
    return {'commit': commit, 'files': count, 'sha256': hashes, 'state': 'EXACT_COMMITTED_BYTES'}


def main():
    result = {'batch': exact_package(G0, B, 18), 'pilot': exact_package(PILOT, P, 7)}
    for repo, head in ((S, SOURCE), (C, CONTROL)):
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == head
        assert not git(repo, 'status', '--porcelain')
    before = git(S, 'show', BASE + ':' + SMALL).decode()
    after = git(S, 'show', SOURCE + ':' + SMALL).decode()
    attr = '#[cfg_attr(all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed),'
    added = [line for line in after.splitlines() if line.startswith(attr)]
    assert len(added) == 8
    assert '\n'.join(line for line in after.splitlines() if not line.startswith(attr)) + '\n' == before
    changed = git(S, 'diff', '--name-only', BASE, SOURCE).decode().splitlines()
    expected = ['library/core/Cargo.toml', SMALL, VERIFY + '.rs'] + [
        VERIFY + '/sorting_s2_' + name + '.rs' for name in ('batch', 'span', 'swap')]
    assert set(changed) == set(expected)
    req_bytes = git(C, 'show', CONTROL + ':ch8-s1-control/CI-REQUEST.json')
    assert digest(req_bytes) == 'eccd05f859b0c5982d6eea23fa0d2e209a9099e3cbc6fdfc883b6e2ad826ac23'
    req = json.loads(req_bytes)
    assumptions = json.loads((G / B / 'QUALIFICATION-ASSUMPTIONS.json').read_text())
    network = after[after.index('fn sort13_optimal'):after.index('// Contract-only geometry.')]
    pairs = [[int(a), int(b)] for a, b in re.findall(r'swap_if_less\(v_base, (\d+), (\d+), is_less\)', network)]
    assert len(pairs) == 45 and pairs == assumptions['stubs'][0]['pairs']
    assert all(0 <= a < 13 and 0 <= b < 13 for a, b in pairs)
    batch = git(S, 'show', SOURCE + ':' + VERIFY + '/sorting_s2_batch.rs').decode()
    roots = re.findall(r'^fn (\w+)\(\) \{', batch, re.M)
    assert set(roots) == {row['id'] for row in req['rows']} and len(roots) == 11
    assert 'panic_on_ord_violation' not in batch and 'assume(false)' not in batch
    for row in req['rows']:
        assert row['proof_credit'] == 'NONE' and row['timeout_seconds'] == 600
    sys.path.insert(0, str(C / 'ch8-s1-control'))
    import runner
    import check_package
    argv = runner.build_argv(S, Path('/root/kani-upstream-ch8-s1'),
                             [row['selector'] for row in req['rows']], 34, Path('/synthetic/export.json'))
    assert argv.count('--harness') == 11 and '--fail-fast' not in argv
    assert argv[argv.index('--harness-timeout') + 1] == '600s'
    assert '--exact' in argv and '--no-assert-contracts' in argv and '--jobs=1' in argv
    workflow = check_package.load_yaml((G / B / 'WORKFLOW.yml').read_text())
    job = workflow['jobs']['s2_batch']
    assert job['timeout-minutes'] == 180 and 'strategy' not in job
    assert sum(step['timeout-minutes'] * 60 for step in job['steps']) == 10620 < 10800
    assert runner.PHASE_SECONDS == 8100
    assert runner.COMPILE_SECONDS + sum(row['timeout_seconds'] for row in req['rows']) == 7500
    assert runner.GROUP_RSS_MAX_KIB == 12 * 1024 * 1024
    assert runner.MEMORY_RESERVE_KIB == 2 * 1024 * 1024
    # Independent sampler fixture: exact process-group partition, foreign pid,
    # disappearing process and malformed metadata. No actual tool subprocess.
    with tempfile.TemporaryDirectory(prefix='s2-review-proc-') as tmp:
        proc = Path(tmp)
        for pid, name, group, rss in [(1, 'kani-driver', 77, 11), (2, 'cbmc', 77, 23),
                                      (3, 'kani-compiler', 77, 37), (4, 'python3', 77, 41),
                                      (5, 'cbmc', 99, 999)]:
            entry = proc / str(pid)
            entry.mkdir()
            (entry / 'stat').write_text(f'{pid} ({name}) S 1 {group} 0\n')
            (entry / 'comm').write_text(name + '\n')
            (entry / 'status').write_text(f'VmRSS:\t{rss} kB\n')
        (proc / '6').mkdir()
        (proc / '6' / 'stat').write_text('invalid')
        (proc / '7').mkdir()
        with mock.patch.object(runner, 'Path', return_value=proc):
            components = runner._component_rss_kib(77)
            aggregate = runner._group_rss_kib(77)
        assert components == {'driver': 11, 'backend': 23, 'compiler': 37, 'other': 41}
        assert aggregate == sum(components.values()) == 112
    result.update(state='PASS_STATIC_SYNTHETIC_ONLY', runtime_edit_check='EXACT_BASE_AFTER_8_OPT_IN_ATTRS',
                  changed_source_paths=changed, new_modules=3, swap_pairs=45, roots=roots,
                  argv=argv, request_sha256=digest(req_bytes), sampler_fixture=components,
                  caps={'backend_per_root_s': 600, 'compile_s': 900, 'group_s': 7500,
                        'phase_s': 8100, 'workflow_phase_step_s': 7560, 'job_s': 10800,
                        'step_caps_sum_s': 10620, 'group_GiB': 12, 'headroom_GiB': 2},
                  proof_credit='NONE', compiler_verifier_CI='NOT_RUN')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
