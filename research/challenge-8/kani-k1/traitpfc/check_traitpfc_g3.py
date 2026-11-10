#!/usr/bin/env python3
"""Source-only preservation/packet checks; no compiler or proof credit.

Reuse RENAMEMODS' lexer/expander. Freeze all inherited ordinary roots and
13 pre-trait controls, including their conservative source closures.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build2', action='store_true', help='check the authorized harness repair')
args = parser.parse_args()
OUT = HERE / 'g3' / 'build2' if args.build2 else HERE / 'g3'
spec = importlib.util.spec_from_file_location(
    'renamemods', HERE.parent / 'renamemods/check_renamemods.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
s, o = r.s, r.o
BASE = '3a16a173b0'
TOOLING = '9b1758ab817af005e96fd52a5fc940d4b6acf984'
KANI = 'f046b70644e113be0df9c22c2e6ea44a65a57566'
ROOTS = s.VERIFY_DIR + 'trait_contracts.rs'
MODEL = s.VERIFY_DIR + 'trait_model.rs'
LIBRARY = {s.SMALLSORT, s.VERIFY_ROOT, ROOTS, MODEL}
BUILD1_PACKET = '55a7fd1c8ada1590ab571b040a6256219ef75e63'


def check_build2_repair():
    """Exact coordinator-approved helper and two call-site substitutions, no broader repair."""
    original = subprocess.check_output(['git', 'show', BUILD1_PACKET + ':' + ROOTS]).decode()
    helper = '''#[cfg(kani_smallsort_controls)]
fn function_item_model_enabled<F>(cmp: &F, len: usize) -> bool {
    <() as SortModel<u64, F>>::enabled(SortEntry::Freeze, cmp, len)
}

'''
    anchor = ('#[cfg(kani_smallsort_controls)]\n#[kani::proof]\n'
              '#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]\n'
              '#[kani::unwind(32)]\nfn rejects_function_item_sorted_u64_backing5()')
    old_call = ('    let enabled = <() as SortModel<u64, _>>::enabled('
                'SortEntry::Freeze, &cmp, v.len());')
    assert original.count(old_call) == 2 and original.count(anchor) == 1
    expected = original.replace(anchor, helper + anchor).replace(
        old_call, '    let enabled = function_item_model_enabled(&cmp, v.len());')
    assert Path(ROOTS).read_text() == expected
    assert o.git('diff', '--name-only', BUILD1_PACKET, '--', 'library').splitlines() == [ROOTS]
    old_request = json.loads((HERE / 'g3/RUN-REQUEST.json').read_text())
    old_request['request_id'] = 'traitpfc-g3-20261110-02'
    assert json.loads((OUT / 'RUN-REQUEST.json').read_text()) == old_request
    old_rows = json.loads((HERE / 'g3/expected-rows.json').read_text())
    new_rows = json.loads((OUT / 'expected-rows.json').read_text())
    for a, b in zip(old_rows, new_rows, strict=True):
        a.pop('designated_failure_source', None)
        b.pop('designated_failure_source', None)
        assert a == b, 'row names/expectations/domains/flags must not change'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')


def tokens(text):
    return s.ser(s.tree(s.lex(text)))


def ensures(entry):
    return f'''    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::SortModel<T, F>>::enabled(
            verify::trait_model::SortEntry::{entry}, is_less, v.len(),
        )) || <() as verify::trait_model::SortModel<T, F>>::sort_postcondition(
            old(<() as verify::trait_model::SortModel<T, F>>::snapshot(v.as_ptr(), v.len())),
            v.as_ptr(), v.len(),
        )
    ))]
'''


def main():
    if args.build2:
        check_build2_repair()
    old, new = s.Source(BASE), s.Source(None)
    assert set(new.files) == set(old.files)
    assert new.file_gate[MODEL] is False and new.file_gate[ROOTS] is False
    for file, text in old.files.items():
        if file not in {MODEL, ROOTS, s.VERIFY_ROOT}:
            assert new.files[file] == text, ('inherited verify file', file)
    before, after = o.items(old), o.items(new)
    for key, item in before.items():
        if key[0] in {MODEL, ROOTS} or key == (s.VERIFY_ROOT, 'inner_doc', 'module_doc'):
            continue
        if key == (s.VERIFY_ROOT, 'mod', 'trait_contracts'):
            assert after[key].text() == tokens('mod trait_contracts;')
        else:
            assert item.text(docs=True) == after[key].text(docs=True), key
    small = Path(s.SMALLSORT).read_text()
    baseline = subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT]).decode()
    pattern = r'    #\[cfg_attr\(kani, crate::kani::ensures\(\|_\|\n.*?    \)\)\]\n'
    assert len(re.findall(pattern, small, re.S)) == 3
    assert re.sub(pattern, '', small, flags=re.S) == re.sub(
        pattern, '', baseline, flags=re.S), 'all non-ensures bytes, API and bodies unchanged'
    contracts = json.loads((HERE / 'contracts.json').read_text())
    attrs = {}
    for (label, contract), entry in zip(contracts.items(), ('Stable', 'Unstable', 'Freeze')):
        start = small.index(contract['impl'])
        pos = small.index('    #[inline(always)]\n    fn small_sort<', start)
        combined = contract['attributes'] + ensures(entry)
        assert small[pos-len(combined):pos] == combined, label
        attrs[label] = ensures(entry)
    assert set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines()) == LIBRARY
    assert set(o.git('diff', '--name-only', TOOLING, '--', 'library').splitlines()) == LIBRARY
    assert not o.git('diff', TOOLING, '--', *r.t.LANES), 'frozen tooling changed'
    assert f'commit = "{KANI}"' in Path('tool_config/kani-version.toml').read_text()
    off0, on0, off, on = old.roots(False), old.roots(True), new.roots(False), new.roots(True)
    inherited = {n: it for n, it in on0.items() if not n.startswith('trait_contracts::')}
    assert len(off0) == 235 and len(inherited) == 248
    assert set(off0) <= set(off) and set(inherited) <= set(on)
    assert (len(on0), len(off), len(on)) == (260, 242, 260)
    closures = {}
    for name in sorted(inherited):
        controls = name not in off0
        a = s.closure(old, [inherited[name]], controls)
        b = s.closure(new, [on[name]], controls)
        assert set(a) == set(b), ('closure keys', name, set(b)-set(a))
        for key in a:
            assert a[key].text() == b[key].text(), ('inherited closure', name, key)
        closures[s.PREFIX + name] = sha(
            '\n'.join(str(k) + ':' + a[k].text() for k in sorted(a)).encode())
    rows = json.loads((OUT / 'expected-rows.json').read_text())
    assert [x['row'] for x in rows] == [
        'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'C1', 'K1', 'K2', 'K3', 'K4', 'W1', 'R1', 'R2']
    positive = {x['name'].removeprefix(s.PREFIX) for x in rows[:7]}
    calibration = {x['name'].removeprefix(s.PREFIX) for x in rows[7:12]}
    assert set(off) - set(off0) == positive
    assert set(on) - set(inherited) == positive | calibration
    assert not (set(on0) - set(inherited)) & set(on), 'no previous research roots copied'
    for label, roots in [('ordinary', off), ('cfg-on', on)]:
        (OUT / (label + '-expected.txt')).write_text(
            ''.join(s.PREFIX + n + '\n' for n in sorted(roots)))
    idx = {it.name: it for it in new.expanded[ROOTS] if it.kind == 'fn'}
    body = lambda row: s.ser(idx[row['name'].split('::')[-1]].body[-1].children)
    for row in rows[:7]:
        it = idx[row['name'].split('::')[-1]]
        b = body(row)
        assert 'kani_smallsort_controls' not in s.ser(it.all_attrs)
        for snippet in ('let mut cmp: U64Cmp = canonical_less_u64;',
                        'kani::assert(enabled, "sort model enabled before call");',
                        'kani::cover(enabled, "sort model enabled before call");',
                        'sort_input_covers(ascending, descending, duplicate);'):
            assert tokens(snippet) in b, (row['row'], snippet)
        assert b.index('kani : : cover') < b.index('small_sort')
        assert 'assume' not in b
        n = row['N']
        if row['target'] == 'T1':
            assert tokens(f'let mut v: [u64; {n}] = kani::any();') in b
            assert tokens(f'let mut scratch = [MaybeUninit::<u64>::uninit(); {n+16}];') in b
        else:
            assert tokens(f'let mut backing: [u64; {n+2}] = kani::any();') in b
            assert tokens(f'let v = &mut backing[1..{n+1}];') in b
            frame = (f'kani::assert(backing[0] == outside[0] && backing[{n+1}] == outside[1], '
                     '"outside slice unchanged");')
            assert tokens(frame) in b
        expected = '#[kani::unwind(32)]'
        if row['row'].startswith('A'):
            expected = f"#[kani::proof_for_contract(<u64 as {row['trait']}>::small_sort)]"
            if row['row'] in {'A5', 'A6'}:
                expected += (' #[kani::stub_verified('
                             '<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]')
            expected += ' #[kani::unwind(32)]'
        else:
            expected = ('#[kani::proof] #[kani::stub_verified('
                        '<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)] '
                        '#[kani::unwind(32)]')
        assert s.ser(it.all_attrs) == tokens(expected)
    for row in rows[7:12]:
        it = idx[row['name'].split('::')[-1]]
        assert tokens('#[cfg(kani_smallsort_controls)]') in s.ser(it.all_attrs)
    consumer = body(rows[6])
    assert tokens('let pre = [v[0], v[1], v[2]];') in consumer
    assert tokens('let post = [v[0], v[1], v[2]];') in consumer
    assert 'SortModel' not in consumer[consumer.index('small_sort'):]
    for k in (rows[10], rows[11]):
        assert tokens('let mut cmp = trait_less_u64;') in body(k)
        assert tokens('kani::assert(!enabled, "function item disables sort model");') in body(k)
    # The common calibration comparator/cover helpers retain their previous bodies.
    old_idx = {it.name: it for it in old.expanded[ROOTS] if it.kind == 'fn'}
    for name in ('trait_less_u64', 'trait_input_covers'):
        assert s.ser(old_idx[name].body) == s.ser(idx[name].body)
    assert tokens('kani::assume(a < b);') in body(rows[8])
    assert tokens('v[0] ^= 1u64 << 63;') in body(rows[7])
    assert sum('kani : : assume' in body(x) for x in rows[:12]) == 1
    assert tokens('a > b') == s.ser(idx['reverse_less'].body[-1].children)
    for row in rows:
        if 'designated_failure_source' in row:
            src = row['designated_failure_source']
            assert src['file_sha256'] == sha(Path(ROOTS).read_bytes())
            line = new.files[ROOTS].splitlines()[src['message_line']-1]
            assert '"' + src['message'] + '"' in line
    model = new.files[MODEL]
    assert not any(x in model for x in ('PairModel', 'kani::any', 'kani::assume', 'transmute'))
    assert not re.search(r'\b(?:G1|G2|G3|traitpfc)\b', model + new.files[ROOTS])
    impls = [it for it in new.items[MODEL] if it.kind == 'impl']
    assert len(impls) == 2
    assert impls[0].text() == tokens('''impl<T, F> SortModel<T, F> for () {
        default fn enabled(_entry: SortEntry, _cmp: &F, _len: usize) -> bool { false }
        default fn snapshot(_base: *const T, _len: usize) -> SortSnapshot {
            SortSnapshot { len: 0, valid: false, vals: [0; 3] }
        }
        default fn sort_postcondition(_pre: SortSnapshot, _base: *const T, _len: usize) -> bool { true }
    }''')
    for entry in ('Stable', 'Unstable', 'Freeze'):
        assert tokens(f'SortEntry::{entry} => len == 2 || len == 3,') in tokens(model)
    for snippet in ('*cmp as *const () == canonical_less_u64 as *const ()',
                    'if len != 2 && len != 3 { return result; }',
                    'result.vals[i] = unsafe { *base.add(i) };',
                    'snapshot_count_u64(pre, pre.vals[i]) != snapshot_count_u64(post, pre.vals[i])'):
        assert tokens(snippet) in tokens(model)
    assert tokens(model).count(tokens(
        'let post = <() as SortModel<u64, U64Cmp>>::snapshot(base, len);')) == 1
    old_long = [line for line in baseline.splitlines() if len(line) > 100]
    assert [line for line in small.splitlines() if len(line) > 100] == old_long
    assert all(len(line) <= 100 for f in (MODEL, ROOTS, s.VERIFY_ROOT)
               for line in new.files[f].splitlines())
    subprocess.run(['git', 'diff', '--check'], check=True)
    command = [r.l.RUSTFMT, '--check', '--edition', '2024', '--config-path',
               r.l.RUSTFMT_CONFIG, s.SMALLSORT]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    assert not result.stdout
    (OUT / 'rustfmt-check.txt').write_text(
        'command: ' + ' '.join(command) + '\nexit_code: 0\nstdout: <empty>\nstderr: '
        + (result.stderr or '<empty>') + '\n')
    request = json.loads((OUT / 'RUN-REQUEST.json').read_text())
    assert (OUT / 'RUN-REQUEST.json').read_bytes() == (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    assert request['request_id'] == ('traitpfc-g3-20261110-02' if args.build2
                                     else 'traitpfc-g3-20261110-01')
    assert request['kind'] == 'diagnostic' and request['agent'] == 'k1-merge'
    assert request['controls'] is True and request['inventory'] is True
    assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 5
    assert request['harnesses'] == [
        {k: row[k] for k in ('name', 'expect', 'expect_check') if k in row} for row in rows]
    subprocess.run(['python3', '-B', str(HERE.parent / 'tools/kani_k1.py'), 'validate',
                    str(OUT / 'RUN-REQUEST.json'), '--require-runner', 'gcb-e2-standard-4',
                    '--args-out', str(OUT / 'kani-args.txt'), '--runner-out', str(OUT / 'runner.txt'),
                    '--rustflags-out', str(OUT / 'rustflags.txt')], check=True,
                   stdout=subprocess.DEVNULL)
    write('contracts.json', dict(ensures=attrs, old_capture='native Copy SortSnapshot',
                                new_requires=[], preserved_g1=contracts))
    write('closures.json', closures)
    write('check-report.json', dict(status='PASS', base_sha=o.git('rev-parse', BASE),
        build_number=2 if args.build2 else 1,
        exact_authorized_build2_repair=args.build2,
        tooling_base=TOOLING, kani_commit=KANI,
        library_commit=o.git('log', '-1', '--format=%H', '--', 'library'),
        library_tree=o.git('rev-parse', 'HEAD:library'),
        baseline_ordinary=235, ordinary=242, baseline_cfg_on=260, cfg_on=260,
        inherited_controls=13, inherited_closures_unchanged=248,
        runtime_bytes_and_g1_requires_modifies_unchanged=True,
        rustfmt_check='PASS', new_overlong_rust_lines=[],
        compiler_resolution='NOT_RUN', proof_status='NOT_RUN', native_inventory='NOT_RUN',
        source_sha256={f: sha(Path(f).read_bytes()) for f in sorted(LIBRARY)},
        request_sha256=sha((OUT / 'RUN-REQUEST.json').read_bytes()),
        inventory_sha256={label: sha((OUT / (label+'-expected.txt')).read_bytes())
                          for label in ('ordinary', 'cfg-on')}))
    print('PASS: 235 ordinary + 13 inherited controls/closures unchanged; ordinary242/cfg-on260')
    print('PASS: exact ensures-only core delta; G1 contracts/API/bodies/tooling unchanged')
    print('PASS: rustfmt, line widths, request; compiler/proof/native inventory NOT_RUN')


if __name__ == '__main__':
    main()
