#!/usr/bin/env python3
"""Source-only packet checks; reuse RENAMEMODS' lexer and macro expander.

Old roots retain the inherited conservative global identifier closures. Restored
roots use a module-local closure with explicit import/path checks: global name
collisions in unrelated modules are not dependencies of these four functions.
Neither check is compiler name resolution or proof evidence.
"""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'renamemods', HERE.parent / 'renamemods/check_renamemods.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
s, t, o = r.s, r.t, r.o
BASE = '4f52065504'
BASE_TREE = 'def2d65ddc5e73ed6ccb94df0afbb36e475d80d8'
HISTORY = '44b972435aeff6ea88cd01e64ccea3727a98294e'
TOOLING = r.TOOLING
HELPER = s.VERIFY_DIR + 'helper_contracts.rs'
OLD_HELPER = s.VERIFY_DIR + 'realcontracts.rs'
NEW = {'insertion_safety_u64_len2', 'insertion_safety_u64_len3'}
ADDED = NEW | {'exercise_insertion_fixed'}
OLD_IMPORT = 'use super::super::{bidirectional_merge, insert_tail, sort4_stable, swap_if_less};'
NEW_IMPORT = '''use super::super::{
    bidirectional_merge, insert_tail, insertion_sort_shift_left, sort4_stable, swap_if_less,
};'''
OLD_DOMAIN = '''//!   u64 tail insertion at positions 1 through 4 in five elements; sort4 of u64 with separate
//!   source and destination arrays; u64 merge of two or four elements with separate output.'''
NEW_DOMAIN = '''//!   u64 insertion sort of two or three elements with any valid offset; u64 tail insertion at
//!   positions 1 through 4 in five elements; sort4 of u64 with separate source and destination
//!   arrays; u64 merge of two or four elements with separate output.'''
COMMENT = '// Fixed lengths with any nonzero offset up to and including the slice length.\n'
MESSAGES = {
    'realcontracts fixed insertion offset one returns':
        'helper contract insertion offset one returns',
    'realcontracts fixed insertion final offset returns':
        'helper contract insertion final offset returns',
    'realcontracts fixed insertion below final offset returns':
        'helper contract insertion below final offset returns',
    'realcontracts fixed insertion returns': 'helper contract insertion returns',
    'realcontracts comparator true': 'helper contract comparator true',
    'realcontracts comparator false': 'helper contract comparator false',
}


def write(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def without_control_cfg(it):
    cfg = s.ser(s.tree(s.lex('#[cfg(kani_smallsort_controls)]')))
    text = s.ser(it.tokens())
    assert text.count(cfg) == 1, it.name
    return text.replace(cfg, '', 1).strip()


def local_closure(src, file, start):
    names = o.local_reachable(src, file, [start])
    idx = {it.name: it for it in src.expanded[file] if it.kind == 'fn'}
    assert names <= set(idx)
    return {name: idx[name] for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--active-request', choices=('g1', 'g2'), default='g1')
    args = parser.parse_args()
    old, new, historic = s.Source(BASE), s.Source(None), s.Source(HISTORY)
    assert o.git('rev-parse', BASE + ':library') == BASE_TREE
    assert set(old.files) == set(new.files), 'no file moves or module splits'
    changed = {f for f in old.files if old.files[f] != new.files[f]}
    assert changed == {HELPER, s.VERIFY_ROOT}

    # Exact byte allowlist: import, one contiguous addition and the specified map entry.
    text = new.files[HELPER]
    begin = text.index(COMMENT)
    end = text.index('#[kani::proof_for_contract(insert_tail)]', begin)
    addition = text[begin:end]
    added_items = s.split_items(s.tree(s.lex(addition)))
    assert {it.name for it in added_items} == ADDED and len(added_items) == 3
    assert (text[:begin] + text[end:]).replace(NEW_IMPORT, OLD_IMPORT, 1) == old.files[HELPER]
    assert text.count(NEW_IMPORT) == 1 and old.files[HELPER].count(OLD_IMPORT) == 1
    assert new.files[s.VERIFY_ROOT] == old.files[s.VERIFY_ROOT].replace(OLD_DOMAIN, NEW_DOMAIN, 1)
    assert old.files[s.VERIFY_ROOT].count(OLD_DOMAIN) == 1
    assert 'The five real helper write sets' in new.files[s.VERIFY_ROOT]

    # Every old expanded item except the explicitly changed import/docs is exact.
    bi, ai = o.items(old), o.items(new)
    added_keys = {(HELPER, 'fn', n) for n in ADDED}
    changed_imports = {k for k in bi.keys() ^ ai.keys() if k[1] == 'use'}
    assert len(changed_imports) == 2
    assert set(ai) - set(bi) == added_keys | (changed_imports & set(ai))
    assert set(bi) - set(ai) == changed_imports & set(bi)
    unchanged_items = 0
    for key in bi.keys() & ai.keys():
        if key[1] == 'inner_doc':
            continue
        assert bi[key].text() == ai[key].text(), key
        unchanged_items += 1
    old_off, old_on = old.roots(False), old.roots(True)
    off, on = new.roots(False), new.roots(True)
    added_roots = {'helper_contracts::' + n for n in NEW}
    assert (len(old_off), len(old_on), len(off), len(on)) == (233, 246, 235, 248)
    assert set(off) - set(old_off) == set(on) - set(old_on) == added_roots
    assert set(old_off) <= set(off) and set(old_on) <= set(on)
    closures = {}
    for name in sorted(old_on):
        controls = name not in old_off
        a = s.closure(old, [old_on[name]], controls)
        b = s.closure(new, [on[name]], controls)
        assert set(a) == set(b), ('old closure keys', name)
        for key in a:
            assert a[key].text() == b[key].text(), ('old closure tokens', name, key)
        closures[s.PREFIX + name] = dict(items=len(a), sha256=o.digest(
            '\n'.join(str(k) + ':' + a[k].text() for k in sorted(a))))
    for label, roots in [('ordinary', off), ('cfg-on', on)]:
        (HERE / (label + '-expected.txt')).write_text(
            ''.join(s.PREFIX + n + '\n' for n in sorted(roots)))

    inverse = {json.dumps(v): json.dumps(k) for k, v in MESSAGES.items()}
    historical_closures = {}
    expected_local = {'exercise_insertion_fixed', 'arbitrary_less', 'comparison_covers'}
    for name in sorted(ADDED):
        a = local_closure(historic, OLD_HELPER, name)
        b = local_closure(new, HELPER, name)
        assert set(a) == set(b) == expected_local | {name}
        for dep in a:
            before = without_control_cfg(a[dep]) if dep in ADDED else a[dep].text()
            after = r.canonical(b[dep].tokens(), inverse)
            assert r.canonical(before) == after, ('restored closure tokens', name, dep)
        historical_closures[name] = dict(items=sorted(a), canonical_sha256=o.digest(
            '\n'.join(dep + ':' + r.canonical(b[dep].tokens(), inverse) for dep in sorted(b))))
    # Pin the external call shapes and import binding, rather than following every
    # unqualified 'arbitrary_less' in unrelated modules via the global name index.
    assert historic.files[OLD_HELPER].count(
        '#[cfg(kani_smallsort_controls)]\nuse super::super::insertion_sort_shift_left;') == 1
    assert text.count(NEW_IMPORT) == 1
    new_local = {it.name: it for it in new.expanded[HELPER] if it.kind == 'fn'}
    assert s.idents(new_local['exercise_insertion_fixed'].tokens()) & set(new_local) == {
        'exercise_insertion_fixed', 'arbitrary_less'}
    assert s.idents(new_local['arbitrary_less'].tokens()) & set(new_local) == {
        'arbitrary_less', 'comparison_covers'}
    assert s.idents(new_local['comparison_covers'].tokens()) & set(new_local) == {'comparison_covers'}
    for name in NEW:
        assert not s.gated(new_local[name].all_attrs)
        assert s.proof_kind(new_local[name].all_attrs) == s.proof_kind(
            historic.roots(True)['realcontracts::' + name][1].all_attrs)
    write('message-map.json', [dict(before=k, after=v) for k, v in MESSAGES.items()])
    write('closures.json', dict(unchanged_roots=closures, restored_local=historical_closures,
        scope='Inherited global conservative identifier closures for old roots; module-local '
              'function closure and explicit import/path binding for restored roots; not compiler resolution.'))
    pfc_expected = json.loads((HERE / 'pfc-expected.json').read_text())
    assert pfc_expected['historical_commit'] == HISTORY
    result_commit = pfc_expected['historical_result_commit']
    historical_result = subprocess.check_output(['git', 'show', result_commit +
        ':research/challenge-8/kani-k1/RESULT-REALCONTRACTS.md'], text=True)
    for row, n, seconds in zip(pfc_expected['rows'], (2, 3), ('81.02985', '105.375145')):
        assert row == dict(name=s.PREFIX + f'helper_contracts::insertion_safety_u64_len{n}',
                           expect='SUCCESS', failed_checks=0, covers_satisfied=6,
                           covers_total=6, prior_seconds=seconds)
        assert (f'| G2 / realcontracts::insertion_safety_u64_len{n} | SUCCESS | SUCCESS | '
                f'{seconds} | 0/160; 6/6 |') in historical_result
        local = local_closure(new, HELPER, f'insertion_safety_u64_len{n}')
        assert sum(t.count_covers(it.text()) for it in local.values()) == 6
    assert len(pfc_expected['rows']) == 2

    assert subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT]) == Path(s.SMALLSORT).read_bytes()
    assert set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines()) == changed
    assert not o.git('diff', '--name-only', TOOLING, '--', *t.LANES)
    forbidden_stage = re.compile(r'\b(?:INSERTPFC|INTEGCHECK|RENAMEMODS|TIDYDOCS|'
                                 r'LEANHELPERS|OPTINMOVE|REALCONTRACTS|REALCONTRACTSTWO)\b', re.I)
    for f in changed:
        assert not t.overlong_lines(new.files[f]), f
        diff = difflib.unified_diff(old.files[f].splitlines(), new.files[f].splitlines())
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                assert not t.FORBIDDEN.search(line[1:]), (f, line)
                assert not forbidden_stage.search(line[1:]), (f, line)
    subprocess.run(['git', 'diff', '--check'], check=True)
    before_format = {f: Path(f).read_bytes() for f in new.files}
    cmd = [r.l.RUSTFMT, '--check', '--edition', '2024', '--config-path',
           r.l.RUSTFMT_CONFIG, HELPER, s.VERIFY_ROOT]
    fmt = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert not fmt.stdout and before_format == {f: Path(f).read_bytes() for f in new.files}
    (HERE / 'rustfmt-check.txt').write_text('command: ' + ' '.join(cmd) +
        '\nexit_code: 0\nstdout: <empty>\nstderr: ' + (fmt.stderr or '<empty>') +
        '\nsource_bytes_unchanged: true\n')

    # Keep original control coordinates intact; only relocate the changed file.
    controls = json.loads((HERE / 'controls-expected.json').read_text())
    source_controls = json.loads((HERE.parent / 'integcheck/controls-expected.json').read_text())
    assert controls['sources'] == source_controls['sources']
    assert len(controls['controls']) == len(source_controls['controls']) == 13
    for original, current in zip(source_controls['controls'], controls['controls']):
        expected = json.loads(json.dumps(original))
        file = original['expected_location']['file']
        lines = Path(file).read_text().splitlines()
        if file == HELPER:
            matches = [i for i, line in enumerate(lines, 1)
                       if line.strip() == original['current_source_line'].strip()]
            assert len(matches) == 1
            expected['expected_location']['line'] = matches[0]
            expected['source_file_sha256'] = o.digest(Path(file).read_text())
        assert current == expected, ('control expectation', current['name'])
        assert current['current_source_line'].strip() == lines[current['expected_location']['line'] - 1].strip()
        assert current['source_file_sha256'] == o.digest(Path(file).read_text())

    root_request = HERE.parent / 'RUN-REQUEST.json'
    active_file = 'RUN-REQUEST.json' if args.active_request == 'g1' else 'G2-RUN-REQUEST.json'
    assert root_request.read_bytes() == (HERE / active_file).read_bytes()
    requests, validated = {}, []
    for label, filename, count, timeout in [('g1', 'RUN-REQUEST.json', 15, 5),
                                           ('g2', 'G2-RUN-REQUEST.json', 0, 44)]:
        path = HERE / filename
        request = json.loads(path.read_text())
        assert request['request_id'] == f'insertpfc-{label}-20261107-01'
        assert request['agent'] == 'k1-merge' and request['runner'] == 'gcb-e2-standard-4'
        assert request['controls'] is True and request['harness_timeout_minutes'] == timeout
        assert len(request['harnesses']) == count
        assert request['kind'] == ('diagnostic' if label == 'g1' else 'inventory')
        assert request['inventory'] is (label == 'g2')
        if label == 'g1':
            assert request['kani_jobs'] == 1
            wanted = [dict(name=s.PREFIX + 'helper_contracts::' + n, expect='SUCCESS')
                      for n in sorted(NEW)] + [dict(name=c['name'], expect='FAILED',
                          expect_check=c['expect_check']) for c in controls['controls']]
            assert request['harnesses'] == wanted
        result = subprocess.run(['python3', '-B', str(HERE.parent / 'tools/kani_k1.py'),
            'validate', str(path), '--args-out', str(HERE / (label + '-validated-args.txt')),
            '--runner-out', str(HERE / (label + '-validated-runner.txt')),
            '--rustflags-out', str(HERE / (label + '-validated-rustflags.txt')),
            '--require-runner', 'gcb-e2-standard-4', '--max-total-minutes', '720'],
            check=True, capture_output=True, text=True)
        validated.append(result.stdout.strip())
        requests[label] = dict(sha256=o.digest(path.read_text()), rows=count,
            harness_timeout_minutes=timeout, paid_minutes=(count * timeout if count else timeout) + 30)
    assert requests['g1']['paid_minutes'] == 105 and requests['g2']['paid_minutes'] == 74
    assert 'OVERHEAD_MINUTES=30' in (HERE.parent / 'tools/k1g.sh').read_text()
    assert 'VERIFY_SLACK_MINUTES=24' in (HERE.parent / 'tools/gcb-k1.sh').read_text()
    ledger = json.loads((HERE / 'RUN-LEDGER.json').read_text())
    assert ledger['owner'] == 'k1-merge' and ledger['slug'] == 'insertpfc'
    assert ledger['library_commit'] == o.git('log', '-1', '--format=%H', '--', 'library')
    assert ledger['library_tree'] == o.git('rev-parse', 'HEAD:library')
    assert ledger['tooling_base'] == TOOLING
    assert (ledger['build_limit'], ledger['retry_limit'], ledger['compile_error_repair_limit']) == (2, 0, 1)
    assert ledger['own_cap_usd'] == '2.5000' and ledger['project_cap_usd'] == '118.9600'
    assert ledger['planned_combined_reserve_usd'] == '2.4165'
    for entry, label, cutoff in zip(ledger['planned_builds'], ('g1', 'g2'), (99, 68)):
        assert entry['stage'] == 'insertpfc-' + label
        assert entry['request_sha256'] == requests[label]['sha256']
        assert entry['paid_build_timeout_minutes'] == requests[label]['paid_minutes']
        assert entry['verify_cutoff_after_validate_minutes'] == cutoff
    assert len(ledger['planned_builds']) == 2
    result_lines = (HERE.parent / 'RESULT-INSERTPFC.md').read_text().splitlines()
    assert len(result_lines) <= 40
    assert any('105' in line and '100' in line and '2.4165' in line for line in result_lines)
    (HERE / 'request-validation.txt').write_text('\n'.join(validated) + '\n')
    write('check-report.json', dict(status='PASS', base_sha=o.git('rev-parse', BASE),
        base_library_tree=BASE_TREE, historical_sha=HISTORY, tooling_base=TOOLING,
        library_commit=o.git('log', '-1', '--format=%H', '--', 'library'),
        library_tree=o.git('rev-parse', 'HEAD:library'), library_changed_files=sorted(changed),
        expanded_unchanged_items=unchanged_items, unchanged_root_closures=246,
        restored_roots=2, restored_exercise=1, historical_local_closure='PASS',
        ordinary=235, controls=13, cfg_on=248, smallsort_bytes_identical=True,
        tooling_unchanged=True, rustfmt_check='PASS', overlong_lines=[], forbidden_added_lines=[],
        active_request=args.active_request,
        names_sha256={label: o.digest((HERE / (label + '-expected.txt')).read_text())
                      for label in ('ordinary', 'cfg-on')}, requests=requests,
        coordinator_deviation='2026-11-07: G1 paid timeout 105 instead of task 100; '
                              'combined reserve $2.4165 within own cap $2.50 approved.',
        planned_combined_reserve_usd='2.4165', runtime_status='NOT_RUN', new_proof_credit=False))
    print('PASS: 246 unchanged closures; 2 restored PFCs plus exercise; ordinary 235; cfg-on 248')


if __name__ == '__main__':
    main()
