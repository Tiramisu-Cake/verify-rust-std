#!/usr/bin/env python3
"""Source-only G2 packet checks; RENAMEMODS lexer/expander, git, authorized rustfmt.

These checks establish source preservation and packet shape, not Rust resolution,
compiler inventory, contract soundness, or formal proof acceptance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
OUT = HERE / 'g2'
spec = importlib.util.spec_from_file_location(
    'renamemods', HERE.parent / 'renamemods/check_renamemods.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
s, o = r.s, r.o
BASE = 'feb589a306'
TOOLING = '9b1758ab817af005e96fd52a5fc940d4b6acf984'
KANI = 'f046b70644e113be0df9c22c2e6ea44a65a57566'
ROOTS = s.VERIFY_DIR + 'trait_contracts.rs'
MODEL = s.VERIFY_DIR + 'trait_model.rs'
ENSURES = '''    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::PairModel<T, F>>::enabled(is_less, v.len()))
            || (<() as verify::trait_model::PairModel<T, F>>::pair_is_sorted(
                v.as_ptr(), v.len(),
            )
                && <() as verify::trait_model::PairModel<T, F>>::pair_permutation(
                    v.as_ptr(), v.len(),
                    old(<() as verify::trait_model::PairModel<T, F>>::snapshot(
                        v.as_ptr(), v.len(),
                    )),
                ))
    ))]
'''
MAP = '''//! - `trait_model`: cfg(kani) pair model for the opt-in u64/N2 trait postcondition pilot.
//!   `trait_contracts` supplies opt-in PFC, consumer, and negative-control roots.
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def tokens(text):
    return s.ser(s.tree(s.lex(text)))


def main():
    old, new = s.Source(BASE), s.Source(None)
    assert set(new.files) - set(old.files) == {MODEL}
    assert not set(old.files) - set(new.files)
    assert new.file_gate[MODEL] is False and new.file_gate[ROOTS] is True
    for file, text in old.files.items():
        if file == s.VERIFY_ROOT:
            text = text.replace('mod types;', 'pub(super) mod trait_model;\nmod types;')
            text = text.replace('//! - `scratch_geometry`:', MAP + '//! - `scratch_geometry`:')
            assert new.files[file] == text
        elif file == ROOTS:
            assert new.files[file].startswith(text), 'G1 roots/helpers/imports byte unchanged'
        else:
            assert new.files[file] == text, ('previous verify file', file)
    small = Path(s.SMALLSORT).read_text()
    stripped = small
    contracts = json.loads((HERE / 'contracts.json').read_text())
    assert small.count(ENSURES) == 3
    for label, contract in contracts.items():
        marker = contract['impl']
        start = stripped.index(marker)
        pos = stripped.index('    #[inline(always)]\n    fn small_sort<', start)
        attrs = contract['attributes'] + ENSURES
        assert stripped[pos-len(attrs):pos] == attrs, label
        stripped = stripped[:pos-len(ENSURES)] + stripped[pos:]
    baseline = subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT]).decode()
    assert stripped == baseline, 'only ensures; G1 requires/modifies, bodies/API unchanged'
    changed = set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines()) | {MODEL}
    assert changed == {s.SMALLSORT, s.VERIFY_ROOT, ROOTS, MODEL}, changed
    assert not o.git('diff', TOOLING, '--', *r.t.LANES), 'tooling/gates/pins changed'
    assert f'commit = "{KANI}"' in Path('tool_config/kani-version.toml').read_text()
    before, after = o.items(old), o.items(new)
    for key, item in before.items():
        if key == (s.VERIFY_ROOT, "inner_doc", "module_doc"):
            continue  # exact authorized module-map insertion checked above
        assert key in after and item.text(docs=True) == after[key].text(docs=True), key
    off0, on0, off, on = old.roots(False), old.roots(True), new.roots(False), new.roots(True)
    assert (len(off0), len(on0), len(off), len(on)) == (235, 254, 235, 260)
    assert set(off) == set(off0) and set(on0) <= set(on)
    rows = json.loads((OUT / 'expected-rows.json').read_text())
    assert [row['row'] for row in rows] == ['E1','E2','E3','C1','N1','N2','N3','W1','R1','R2']
    assert set(on) - set(on0) == {
        row['name'].removeprefix(s.PREFIX) for row in rows if row['row'] in
        {'E1', 'E2', 'E3', 'C1', 'N1', 'N3'}}
    closures = {}
    for name in sorted(on0):
        controls = name not in off0
        a = s.closure(old, [on0[name]], controls)
        b = s.closure(new, [on[name]], controls)
        assert set(a) == set(b), ('closure keys', name, set(b)-set(a))
        for key in a:
            assert a[key].text() == b[key].text(), ('callback/closure tokens', name, key)
        closures[s.PREFIX + name] = sha(
            '\n'.join(str(k) + ':' + a[k].text() for k in sorted(a)).encode())
    for label, roots in [('ordinary', off), ('cfg-on', on)]:
        (OUT / (label + '-expected.txt')).write_text(
            ''.join(s.PREFIX + n + '\n' for n in sorted(roots)))
    idx = {it.name: it for it in new.expanded[ROOTS] if it.kind == 'fn'}
    assert len(idx) == 16  # eight G1 functions, six roots, covers, reverse comparator
    body = lambda row: s.ser(idx[row['name'].split('::')[-1]].body[-1].children)
    for i, trait in enumerate(('StableSmallSortTypeImpl', 'UnstableSmallSortTypeImpl',
                               'UnstableSmallSortFreezeTypeImpl')):
        attrs = f'#[kani::proof_for_contract(<u64 as {trait}>::small_sort)] #[kani::unwind(32)]'
        assert s.ser(idx[rows[i]['name'].split('::')[-1]].all_attrs) == tokens(attrs)
        for snippet in ('let input_descending = v[1] < v[0];',
                        'let input_equal = v[0] == v[1];',
                        'strong_input_covers(input_descending, input_equal);'):
            assert tokens(snippet) in body(rows[i])
        assert body(rows[i]).index('let input_descending') < body(rows[i]).index('small_sort')
    for row in rows[:4]:
        b = body(row)
        for snippet in ('let mut cmp: U64Cmp = canonical_less_u64;',
                        'let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());',
                        'kani::assert(enabled, "strong model enabled before call");',
                        'kani::cover(enabled, "strong model enabled before call");'):
            assert tokens(snippet) in b
        assert b.index('kani : : cover') < b.index('small_sort')
    for row in (rows[1], rows[2], rows[3], rows[6]):
        for snippet in ('let mut backing: [u64; 4] = kani::any();',
                        'let v = &mut backing[1..3];',
                        'kani::assert(backing[0] == outside[0] && backing[3] == outside[1], '
                        '"outside slice unchanged");'):
            assert tokens(snippet) in body(row)
    consumer = body(rows[3])
    for snippet in ('let pre = (v[0], v[1]);',
                    'kani::assert(v[0] <= v[1], "strong forwarded output is sorted");',
                    'kani::assert((v[0] == pre.0 && v[1] == pre.1) || '
                    '(v[0] == pre.1 && v[1] == pre.0), '
                    '"strong forwarded output preserves full pair",);'):
        assert tokens(snippet) in consumer
    assert consumer.index('let pre') < consumer.index('small_sort')
    for row in (rows[3], rows[6]):
        attrs = ('#[kani::proof] '
                 '#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)] '
                 '#[kani::unwind(32)]')
        assert s.ser(idx[row['name'].split('::')[-1]].all_attrs) == tokens(attrs)
        assert tokens('<u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);') in body(row)
    assert tokens('let mut cmp: U64Cmp = reverse_less;') in body(rows[6])
    assert tokens('kani::assert(!enabled, "reverse pointer disables strong model");') in body(rows[6])
    oracle = body(rows[4])
    checker = tokens('<() as PairModel<u64, U64Cmp>>::pair_permutation(v.as_ptr(), v.len(), pre)')
    assert oracle.count(checker) == 2
    assert tokens('v[0] ^= 1u64 << 63;') in oracle
    assert tokens('a > b') == s.ser(idx['reverse_less'].body[-1].children)
    model = new.files[MODEL]
    assert 'old(' not in model and 'PRE_PAIR' not in model
    assert all(x not in model for x in ('transmute', 'size_of', 'kani::assume'))
    impls = [it for it in new.items[MODEL] if it.kind == 'impl']
    assert len(impls) == 2
    assert impls[0].text() == tokens("""impl<T, F> PairModel<T, F> for () {
        default fn enabled(_cmp: &F, _len: usize) -> bool { false }
        default fn snapshot(_base: *const T, _len: usize) -> (u64, u64) { (0, 0) }
        default fn pair_is_sorted(_base: *const T, _len: usize) -> bool { true }
        default fn pair_permutation(_base: *const T, _len: usize, _pre: (u64, u64))
            -> bool { true }
    }""")
    assert tokens('len == 2 && *cmp as *const () == canonical_less_u64 as *const ()') in tokens(model)
    assert tokens('unsafe { (*base, *base.add(1)) }') in tokens(model)
    assert tokens('post == pre || post == (pre.1, pre.0)') in tokens(model)
    assert tokens('post.0 <= post.1') in tokens(model)
    request = json.loads((OUT / 'RUN-REQUEST.json').read_text())
    assert (OUT / 'RUN-REQUEST.json').read_bytes() == (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    assert request['request_id'] == 'traitpfc-g2-20261110-01'
    assert request['kind'] == 'diagnostic' and request['agent'] == 'k1-merge'
    assert request['controls'] is True and request['inventory'] is True
    assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 5
    assert request['harnesses'] == [
        {k: row[k] for k in ('name','expect','expect_check') if k in row} for row in rows]
    assert sum(row['expected_failed'] for row in rows) == 3
    assert [len(row['expected_covers']) for row in rows] == [5,5,5,1,0,0,0,3,2,7]
    for row in rows:
        if 'designated_failure_source' in row and 'trait_contracts' in row['name']:
            it = idx[row['name'].split('::')[-1]]
            src = row['designated_failure_source']
            assert it.first_line <= src['line'] <= it.last_line
            assert '"'+src['message']+'"' in new.files[ROOTS].splitlines()[src['line']-1]
    old_long = [line for line in baseline.splitlines() if len(line)>100]
    assert [line for line in small.splitlines() if len(line)>100] == old_long
    assert len(old_long) == 3
    assert all(len(line)<=100 for file in (s.VERIFY_ROOT, ROOTS, MODEL)
               for line in new.files[file].splitlines())
    subprocess.run(['git', 'diff', '--check'], check=True)
    command = [r.l.RUSTFMT, '--check', '--edition', '2024', '--config-path',
               r.l.RUSTFMT_CONFIG, s.SMALLSORT]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    assert not result.stdout
    (OUT / 'rustfmt-check.txt').write_text(
        'command: '+' '.join(command)+'\nexit_code: 0\nstdout: <empty>\nstderr: '
        +(result.stderr or '<empty>')+'\n')
    subprocess.run(['python3','-B',str(HERE.parent/'tools/kani_k1.py'),'validate',
                    str(OUT/'RUN-REQUEST.json'),'--require-runner','gcb-e2-standard-4',
                    '--args-out',str(OUT/'kani-args.txt'),'--runner-out',str(OUT/'runner.txt'),
                    '--rustflags-out',str(OUT/'rustflags.txt')], check=True,
                   stdout=subprocess.DEVNULL)
    write('contracts.json', dict(ensures_attribute=ENSURES, old_capture='native',
                               new_requires=[], g1_contracts=contracts))
    write('closures.json', closures)
    write('check-report.json', dict(status='PASS',base_sha=o.git('rev-parse',BASE),
        tooling_base=TOOLING,kani_commit=KANI,
        library_commit=o.git('log','-1','--format=%H','--','library'),
        library_tree=o.git('rev-parse','HEAD:library'),
        ordinary=235,previous_cfg_on=254,cfg_on=260,
        previous_expanded_items_unchanged=len(before)-1,
        authorized_module_map_doc_change=True,previous_closures_unchanged=len(closures),
        g1_roots_bytes_unchanged=True,library_only_exact_ensures_and_model=True,
        rustfmt_check='PASS',new_overlong_lines=[],inherited_overlong_lines=old_long,
        compiler_resolution='NOT_RUN',proof_status='NOT_RUN',native_inventory='NOT_RUN',
        source_sha256={f:sha(Path(f).read_bytes()) for f in sorted(changed)},
        request_sha256=sha((OUT/'RUN-REQUEST.json').read_bytes()),
        inventory_sha256={label:sha((OUT/(label+'-expected.txt')).read_bytes())
                          for label in ('ordinary','cfg-on')}))
    print('PASS source checks: 235 ordinary; 254 previous roots/closures unchanged; 260 cfg-on')
    print('PASS exact ensures-only core diff; G1 contracts/bodies/API/items/callbacks preserved')
    print('PASS rustfmt zero diff, request validation; compiler/proof/native inventory NOT_RUN')


if __name__ == '__main__':
    main()
