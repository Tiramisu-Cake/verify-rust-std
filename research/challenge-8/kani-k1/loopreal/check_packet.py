#!/usr/bin/env python3
"""Source/request checks only; no cargo, rustc, Kani, CBMC or dispatch."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[3]
BASE = '01cb5fc3cda3ecf2795939285154416f213fa7e2'
TOOLING_BASE = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
RUNTIME = 'library/core/src/slice/sort/shared/smallsort.rs'
VERIFY = 'library/core/src/slice/sort/shared/smallsort/verify.rs'
MODULE = 'library/core/src/slice/sort/shared/smallsort/verify/loopreal.rs'
PREFIX = 'slice::sort::shared::smallsort::verify::'
LANES = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
         'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh',
         'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules',
         '.cargo', 'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']
LOOP_ATTR = re.compile(
    r'^ {8}#\[cfg_attr\(\n {12}kani,\n {12}crate::kani::loop_(?:invariant|modifies)\('
    r'.*?^ {8}\)\]\n', re.M | re.S)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def outer_function(source):
    start = source.index('pub fn insertion_sort_shift_left<')
    end = source.index('\n#[cfg(kani)]\nfn sort4_contract_regions_disjoint', start)
    return source[start:end]


def main():
    assert Path.cwd().resolve() == ROOT
    sys.path.insert(0, str(PACKET.parent / 'tools'))
    import kani_k1
    request_bytes = (PACKET / 'request.json').read_bytes()
    assert request_bytes == (PACKET.parent / 'RUN-REQUEST.json').read_bytes()
    request = kani_k1.validate_request(json.loads(request_bytes))
    assert request['request_id'] == 'loopreal-g1-20261105-02'
    assert request['agent'] == 'k1-network' and request['kind'] == 'diagnostic'
    assert request['controls'] is True and request['kani_jobs'] == 1
    assert request['runner'] == 'gcb-e2-standard-4'
    assert request['harness_timeout_minutes'] == 4
    assert len(request['harnesses']) == 12
    runtime = (ROOT / RUNTIME).read_text()
    clean_runtime, count = LOOP_ATTR.subn('', runtime)
    assert count == 4
    assert clean_runtime.encode() == git('show', f'{BASE}:{RUNTIME}'), 'body/signature/contract changed'
    previous = git('show', 'ffda59d715b3a0bceac59276d18a03f8a61a6015:'+RUNTIME).decode()
    previous_attrs = LOOP_ATTR.findall(previous)
    current_attrs = LOOP_ATTR.findall(runtime)
    assert len(previous_attrs) == len(current_attrs) == 4
    assert current_attrs[1:] == previous_attrs[1:]
    def squash(text):
        return re.sub(r'\s+', '', text)
    expected_inner = squash(previous_attrs[0]).replace(
        'size_of::<T>()>0&&crate::ub_checks::same_allocation',
        'size_of::<T>()==0||(crate::ub_checks::same_allocation', 1)
    expected_inner = expected_inner.replace('==0))]', '==0)))]', 1)
    assert squash(current_attrs[0]) == expected_inner
    registration = b'#[cfg(kani_smallsort_controls)] mod loopreal;\n'
    verify = (ROOT / VERIFY).read_bytes()
    assert verify.count(registration) == 1
    assert verify.replace(registration, b'') == git('show', f'{BASE}:{VERIFY}')
    source = (ROOT / MODULE).read_text()
    roots = [name for attrs, name in re.findall(
        r'^((?:#\[[^\n]+\]\n)+)fn (\w+)\(', source, re.M)
        if '#[kani::proof]' in attrs or '#[kani::proof_for_contract(' in attrs]
    expected_local = {f'{kind}_u64_backing{n}' for kind in ('insert_tail', 'outer_loop')
                      for n in (8, 32, 128)} | {'outer_loop_false_invariant_backing8'}
    assert len(roots) == 7 and set(roots) == expected_local
    local_requested = {h['name'] for h in request['harnesses'] if h['name'].startswith(PREFIX+'loopreal::')}
    assert local_requested == {PREFIX+'loopreal::'+name for name in roots}
    assert source.count('#[kani::proof_for_contract(insert_tail)]') == 3
    assert source.count('#[kani::stub_verified(insert_tail)]') == 4
    assert source.count('fn reading_less_u64(') == 1
    assert source.count('&mut reading_less_u64') == 3  # shared PFC, shared caller, false caller
    assert 'kani::assume(1 <= tail && tail < N);' in source
    assert 'kani::assume(1 <= len && len <= N);' in source
    assert 'kani::assume(1 <= offset && offset <= len);' in source
    assert not re.search(r'^\s*(?:for|while) ', source[:source.index('// Opt-in cfg-copy')], re.M)
    real = outer_function(runtime)
    copy = source[source.index('fn insertion_sort_shift_left_false<'):
                  source.index('\n#[kani::proof]\n#[kani::stub_verified(insert_tail)]\n#[kani::unwind(16)]\nfn outer_loop_false')]
    copy_clean, nattrs = LOOP_ATTR.subn('', copy)
    assert nattrs == 2
    assert copy_clean == LOOP_ATTR.sub('', real).replace(
        'pub fn insertion_sort_shift_left<', 'fn insertion_sort_shift_left_false<', 1)
    assert '&& tail == v_base.wrapping_add(offset)' in copy
    negative = [h for h in request['harnesses'] if h['expect'] == 'FAILED']
    assert len(negative) == 1 and negative[0]['name'].endswith('outer_loop_false_invariant_backing8')
    assert negative[0]['expect_check'].endswith('loopreal::insertion_sort_shift_left_false')
    baselines = json.loads((PACKET / 'regression-baselines.json').read_text())
    ordinary = set((PACKET.parent / 'veightinteg/ordinary-expected.txt').read_text().splitlines())
    assert len(baselines) == 5
    actions_source = json.loads((PACKET / 'actions-v7-timing-source.json').read_text())
    assert actions_source['source_revision_as_supplied'] == 'd1283ff22a'
    assert actions_source['kani_pin_as_supplied'] == 'cd355b0b'
    assert actions_source['independently_verified'] is False
    assert actions_source['k1_rows_available'] is False
    assert actions_source['actions_run_ids'] is None
    expected_actions = {
        PREFIX+'assembly::safety_stable_unit_n16': {'ubuntu': 4.687, 'macOS': 3.657},
        PREFIX+'assembly::safety_stable_unit_n32': {'ubuntu': 35.126, 'macOS': 25.670},
    }
    assert {r['name']: r['verification_time_s_by_platform'] for r in actions_source['rows']} == expected_actions
    assert sum(r['evidence_kind'] == 'bounded_k1_rows' for r in baselines) == 3
    assert sum(r['evidence_kind'] == 'coordinator_reported_actions_timing' for r in baselines) == 2
    for row in baselines:
        assert row['name'] in ordinary
        assert {'name': row['name'], 'expect': 'SUCCESS'} in request['harnesses']
        if row['evidence_kind'] == 'bounded_k1_rows':
            lines = (PACKET / row['bounded_rows_file']).read_text().splitlines()
            old = next(line.split('\t') for line in lines if line.startswith(row['name']+'\t'))
            assert old[1] == row['status'] == 'SUCCESS' and float(old[2]) == row['time_s']
            assert f"head_sha={row['source_sha']}" in lines
            assert f"build_id={row['source_build']}" in lines
        else:
            assert row['evidence_kind'] == 'coordinator_reported_actions_timing'
            assert row['source_reference_file'] == 'actions-v7-timing-source.json'
            assert row['verification_time_s_by_platform'] == expected_actions[row['name']]
            assert row['source_revision_as_supplied'] == 'd1283ff22a'
            assert row['source_pin_as_supplied'] == 'cd355b0b'
            assert row['independently_verified'] is False and row['status'] is None
            assert not {'time_s', 'source_build', 'bounded_rows_file', 'source_request_sha256'} & row.keys()
    covers = json.loads((PACKET / 'expected-covers.json').read_text())
    assert sum(covers.values()) == 34 and len(covers) == 11
    assert set(covers) == {h['name'] for h in request['harnesses'] if h['expect'] == 'SUCCESS'}
    assert git('diff', '--name-only', TOOLING_BASE, '--', *LANES) == b''
    changes = set(git('diff', '--name-only', BASE, '--', 'library').decode().splitlines())
    untracked = set(git('ls-files', '--others', '--exclude-standard', 'library').decode().splitlines())
    assert changes | untracked == {RUNTIME, VERIFY, MODULE}
    ledger = json.loads((PACKET / 'RUN-LEDGER.json').read_text())
    minutes = len(request['harnesses']) * request['harness_timeout_minutes'] + 30
    reserve = round(minutes * 0.0135, 4)
    assert minutes == ledger['build_timeout_minutes'] == 78
    assert reserve == ledger['maximum_reservation_usd'] == 1.053
    assert ledger['spent_usd'] + reserve <= ledger['own_cap_usd'] == 2.0
    assert digest(request_bytes) == ledger['request_sha256']
    report = {'status': 'PASS_STATIC_ONLY', 'task_commit': BASE, 'tooling_base': TOOLING_BASE,
              'request_sha256': digest(request_bytes), 'library_sha256': {
                  p: digest((ROOT / p).read_bytes()) for p in (RUNTIME, VERIFY, MODULE)},
              'runtime': 'four cfg(kani) loop attributes only; bodies/signatures/existing contracts identical',
              'negative_copy': 'real outer signature/body/modifies identical after function rename and attribute removal',
              'local_roots': roots, 'ordinary_regressions': [r['name'] for r in baselines],
              'positive_expected_covers': 34, 'build_timeout_minutes': minutes,
              'baseline_provenance': '3 bounded K-1 rows; 2 coordinator-reported Actions v7 timings, approximate cross-platform comparison only',
              'maximum_reservation_usd': reserve,
              'limitations': 'No compilation, dynamic cfg inventory, actual invariant checks, new timing, memory or proof result established. Actions baseline values are coordinator-reported, not independently verified; no run IDs supplied.'}
    (PACKET / 'check-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
