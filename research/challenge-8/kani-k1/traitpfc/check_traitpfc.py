#!/usr/bin/env python3
"""Source-only packet validation using RENAMEMODS' lexer/expander; no compiler.

Byte allowlists freeze all previous library code. Conservative identifier closures
are source checks, not compiler resolution or proof evidence.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'renamemods', HERE.parent / 'renamemods/check_renamemods.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
s, o = r.s, r.o
BASE = '9b1758ab817af005e96fd52a5fc940d4b6acf984'
KANI = 'f046b70644e113be0df9c22c2e6ea44a65a57566'
NEW = s.VERIFY_DIR + 'trait_contracts.rs'
MAP = '#[cfg(kani_smallsort_controls)]\nmod trait_contracts;\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + '\n')


def main():
    old, new = s.Source(BASE), s.Source(None)
    assert set(new.files) - set(old.files) == {NEW}
    assert not set(old.files) - set(new.files)
    assert new.file_gate[NEW] is True
    for file in old.files:
        expected = old.files[file]
        if file == s.VERIFY_ROOT:
            assert expected.count('mod types;\n') == 1
            expected = expected.replace('mod types;\n', MAP + 'mod types;\n')
        assert new.files[file] == expected, ('previous verify bytes', file)
    contracts = json.loads((HERE / 'contracts.json').read_text())
    assert set(contracts) == {'T1', 'T2', 'T3'}
    small = Path(s.SMALLSORT).read_text()
    stripped = small
    for label, contract in contracts.items():
        marker, attrs = contract['impl'], contract['attributes']
        assert small.count(marker) == 1 and stripped.count(attrs) >= 1
        start = stripped.index(marker)
        pos = stripped.index('    #[inline(always)]\n    fn small_sort<', start)
        assert stripped[pos-len(attrs):pos] == attrs, label
        stripped = stripped[:pos-len(attrs)] + stripped[pos:]
        assert 'ensures' not in attrs
    baseline = subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT])
    assert stripped.encode() == baseline, 'all bodies/signatures/bounds/inline/default bytes'
    assert not o.git('diff', BASE, '--', *r.t.LANES), 'tooling changed'
    assert f'commit = "{KANI}"' in Path('tool_config/kani-version.toml').read_text()
    assert not o.git('diff', '872d5a4338', BASE, '--',
                     'library/core/src/slice/sort', s.CARGO)
    changed = set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines())
    changed |= {NEW}
    assert changed == {s.SMALLSORT, s.VERIFY_ROOT, NEW}, changed
    before, after = o.items(old), o.items(new)
    for key in before:
        assert key in after and before[key].text(docs=True) == after[key].text(docs=True), key
    off0, on0 = old.roots(False), old.roots(True)
    off, on = new.roots(False), new.roots(True)
    rows = json.loads((HERE / 'expected-rows.json').read_text())
    added = {row['name'].removeprefix(s.PREFIX) for row in rows[:6]}
    assert (len(off0), len(on0), len(off), len(on)) == (235, 248, 235, 254)
    assert set(off0) == set(off) and set(on) - set(on0) == added
    assert set(on0) <= set(on)
    closures = {}
    for name in sorted(on0):
        controls = name not in off0
        a = s.closure(old, [on0[name]], controls)
        b = s.closure(new, [on[name]], controls)
        assert set(a) == set(b), ('closure keys', name)
        for key in a:
            assert a[key].text() == b[key].text(), ('closure tokens', name, key)
        closures[s.PREFIX + name] = digest(
            '\n'.join(str(k) + ':' + a[k].text() for k in sorted(a)).encode())
    for label, roots in [('ordinary', off), ('cfg-on', on)]:
        content = ''.join(s.PREFIX + n + '\n' for n in sorted(roots))
        (HERE / (label + '-expected.txt')).write_text(content)
    idx = {it.name: it for it in new.expanded[NEW] if it.kind == 'fn'}
    assert len(idx) == 8
    body = lambda row: s.ser(idx[rows[row]['name'].split('::')[-1]].body[-1].children)
    assert body(3) == body(5), 'S0/S2 are exact real/stub body twins'
    sorted_check = s.ser(s.tree(s.lex(
        'kani::assert(v[0] <= v[1], "forwarded output is sorted");')))
    assert body(5).count(sorted_check) == 1
    assert s.ser(s.tree(s.lex(body(5).replace(sorted_check, '')))) == body(4)
    for i, trait in enumerate(('StableSmallSortTypeImpl', 'UnstableSmallSortTypeImpl',
                               'UnstableSmallSortFreezeTypeImpl')):
        it = on[rows[i]['name'].removeprefix(s.PREFIX)][1]
        assert s.ser(it.all_attrs) == s.ser(s.tree(s.lex(
            f'#[kani::proof_for_contract(<u64 as {trait}>::small_sort)] #[kani::unwind(32)]')))
        assert body(i).index('let input_descending') < body(i).index('small_sort')
        assert 'trait_input_covers ( input_descending )' in body(i)
    stub_attr = s.ser(s.tree(s.lex(
        '#[kani::proof] '
        '#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)] '
        '#[kani::unwind(32)]')))
    for i in (4, 5):
        assert s.ser(on[rows[i]['name'].removeprefix(s.PREFIX)][1].all_attrs) == stub_attr
    for i in (2, 3, 4, 5):
        text = body(i)
        for snippet in ('let mut backing: [u64; 4] = kani::any();',
                        'let v = &mut backing[1..3];',
                        'kani::assert(backing[0] == outside[0] && backing[3] == outside[1], '
                        '"outside slice unchanged");'):
            assert s.ser(s.tree(s.lex(snippet))) in text
    for i in (0, 1):
        assert s.ser(s.tree(s.lex('let mut v: [u64; 2] = kani::any();'))) in body(i)
    assert s.ser(s.tree(s.lex(
        'let mut scratch = [MaybeUninit::<u64>::uninit(); 18];'))) in body(0)
    assert s.ser(idx['trait_less_u64'].body[-1].children) == s.ser(s.tree(s.lex('a < b')))
    assert s.ser(idx['trait_input_covers'].body[-1].children) == s.ser(s.tree(s.lex(
        'kani::cover(input_descending, "descending input returns"); '
        'kani::cover(!input_descending, "non-descending input returns"); '
        'kani::cover(true, "trait small_sort returns");')))
    assert new.files[NEW].count('kani::any()') == 6
    assert 'assume_init' not in new.files[NEW]
    assert new.files[NEW].count('fn trait_less_u64(') == 1
    assert 'a < b' in new.files[NEW]
    request = json.loads((HERE / 'RUN-REQUEST.json').read_text())
    assert (HERE / 'RUN-REQUEST.json').read_bytes() == (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    assert request['request_id'] == 'traitpfc-g1-20261110-01'
    assert request['kind'] == 'diagnostic' and request['agent'] == 'k1-merge'
    assert request['runner'] == 'gcb-e2-standard-4'
    assert request['controls'] is True and request['inventory'] is False
    assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 5
    assert request['harnesses'] == [
        {k: row[k] for k in ('name', 'expect', 'expect_check') if k in row} for row in rows]
    assert [len(row['expected_covers']) for row in rows] == [3, 3, 3, 0, 0, 0, 2, 7]
    assert sum(row['expected_failed'] for row in rows) == 1
    old_long = [line for line in baseline.decode().splitlines() if len(line) > 100]
    current_long = [line for line in small.splitlines() if len(line) > 100]
    assert current_long == old_long and len(old_long) == 3
    assert all(len(line) <= 100 for contract in contracts.values()
               for line in contract['attributes'].splitlines())
    assert all(len(line) <= 100 for f in (s.VERIFY_ROOT, NEW)
               for line in Path(f).read_text().splitlines())
    subprocess.run(['git', 'diff', '--check'], check=True)
    command = [r.l.RUSTFMT, '--check', '--edition', '2024', '--config-path',
               r.l.RUSTFMT_CONFIG, s.SMALLSORT]
    check = subprocess.run(command, check=True, capture_output=True, text=True)
    assert not check.stdout
    (HERE / 'rustfmt-check.txt').write_text(
        'command: ' + ' '.join(command) + '\nexit_code: 0\nstdout: <empty>\nstderr: '
        + (check.stderr or '<empty>') + '\n')
    subprocess.run(['python3', '-B', str(HERE.parent / 'tools/kani_k1.py'), 'validate',
                    str(HERE / 'RUN-REQUEST.json'), '--require-runner', 'gcb-e2-standard-4',
                    '--args-out', str(HERE / 'kani-args.txt'),
                    '--runner-out', str(HERE / 'runner.txt'),
                    '--rustflags-out', str(HERE / 'rustflags.txt')], check=True,
                   stdout=subprocess.DEVNULL)
    write('closures.json', closures)
    write('check-report.json', dict(
        status='PASS_WITH_INHERITED_LINE_LENGTH_EXCEPTION', base_sha=BASE, kani_commit=KANI,
        library_commit=o.git('log', '-1', '--format=%H', '--', 'library'),
        library_tree=o.git('rev-parse', 'HEAD:library'),
        ordinary=235, previous_cfg_on=248, cfg_on=254, added_roots=6,
        previous_expanded_items_unchanged=len(before), previous_closures_unchanged=len(closures),
        unchanged_previous_verify_files=True, smallsort_only_exact_attributes=True,
        tooling_unchanged=True, s0_s2_bodies_identical=True, s1_only_omits_sorted_assert=True,
        rustfmt_check='PASS', new_overlong_lines=[], inherited_overlong_lines=old_long,
        proof_status='NOT_RUN',
        source_checks_are_not_compiler_resolution=True,
        source_sha256={f: digest(Path(f).read_bytes()) for f in
                       (s.SMALLSORT, s.VERIFY_ROOT, NEW)},
        request_sha256=digest((HERE / 'RUN-REQUEST.json').read_bytes()),
        inventory_sha256={label: digest((HERE / (label+'-expected.txt')).read_bytes())
                          for label in ('ordinary', 'cfg-on')}))
    print('PASS source invariants: 235 ordinary, 248 previous roots unchanged; 254 cfg-on; 3-file patch')
    print('REVIEW: three inherited >100-character comments preserved; no new overlong lines')


if __name__ == '__main__':
    main()
