#!/usr/bin/env python3
"""LEANHELPERS checks. Python/git and authorized rustfmt only; no compiler.

Import OPTINMOVE's lexer/expander. Whole-file exact transformation checks limit the
patch to the three authorized edits. Dependency analysis is conservative by identifier,
not compiler resolution. Split the old CopyOnDrop impl into its individual methods for
logical closures, avoiding its generic T becoming a spurious global dependency.
"""
from collections import Counter
import argparse
import copy
import csv
import io
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('optinmove', HERE.parent / 'optinmove/check_optinmove.py')
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)
s, t = o.s, o.t
BASE = '461dac0c43902c7a929e7164492ad4a5f84a4a3b'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
MERGE = s.VERIFY_DIR + 'merge.rs'
NETWORK = s.VERIFY_DIR + 'network.rs'
SCRATCH = s.VERIFY_DIR + 'scratchgeom.rs'
SPECFIX = s.VERIFY_DIR + 'merge/specfix.rs'
RUSTFMT = ('/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/'
           'scratchpad/rustfmt.sh')
RUSTFMT_CONFIG = str(HERE.parent / 'codefix/rustfmt.toml')
METHODS = {'probe_count', 'probe_count_unrolled', 'regions_are_disjoint'}
GROUPS = {'MUTANT': {'drop_route_properties'},
          'START': {'insert_tail_start1_frame', 'insert_tail_group_value'},
          'CopyOnDrop': METHODS}


def replace(text, before, after, count=1):
    assert text.count(before) == count, (before, text.count(before), count)
    return text.replace(before, after)


def expected_sources(files):
    """An exact, reviewable allowlist; all unmentioned source bytes must survive."""
    out = dict(files)
    a = out[MERGE]
    a = replace(a, '// Normal return only. MUTANT values select duplicate-tag and extra-drop controls.',
                '// Normal return only; tag multiplicities and destructor counts are checked separately.')
    a = replace(a, 'const PERM: bool, const MUTANT: u8>()\n-> bool {',
                'const PERM: bool>() -> bool {')
    a = replace(a, '    const { assert!(MUTANT <= 2) };\n', '')
    a = replace(a, '''    if MUTANT == 1 {
        // Negative control: duplicate a tag, losing another; addresses remain valid and disjoint.
        unsafe {
            let base = v.as_mut_ptr();
            ptr::copy_nonoverlapping(base, base.add(1), 1);
        }
    } else if MUTANT == 2 {
        // Deliberately observe one extra destructor before array destruction.
        unsafe { crate::mem::drop(ptr::read(v.as_ptr())) };
    }
''', '')
    a = replace(a, 'drop_route_properties::<$n, $upper, $perm, 0>()',
                'drop_route_properties::<$n, $upper, $perm>()')
    begin = a.index('impl<T> CopyOnDrop<T> {\n')
    end = a.index('// Key orders admit', begin)
    block = a[begin:end]
    assert block.endswith('}\n')
    block = block.split('\n', 1)[1][:-2]
    block = replace(block,
                    '    // Value-count and geometry helpers live here to mention `T` without adding runtime state.\n',
                    '')
    block = '\n'.join(line[4:] if line.startswith('    ') else line
                      for line in block.split('\n'))
    for name in sorted(METHODS):
        block = replace(block, 'fn ' + name + '(', 'fn ' + name + '<T>(')
    a = a[:begin] + block + a[end:]
    a = replace(a, '    CopyOnDrop, SMALL_SORT_GENERAL_SCRATCH_LEN,',
                '    SMALL_SORT_GENERAL_SCRATCH_LEN,')
    for name in ('probe_count', 'probe_count_unrolled'):
        a = replace(a, 'CopyOnDrop::<T>::' + name + '(', name + '::<T>(', count=2)
    # Coordinator-authorized rustfmt-only repair, including four OPTINMOVE calls.
    a = replace(a, """    assert!(
        probe_count::<T>(v.as_ptr(), 4)
            == probe_count::<T>(dst.as_ptr() as *const T, 4)
    );""", '    assert!(probe_count::<T>(v.as_ptr(), 4) == '
                'probe_count::<T>(dst.as_ptr() as *const T, 4));')
    a = replace(a, '        probe_count_unrolled::<T>(orig.as_ptr(), N)\n'
                '            == probe_count_unrolled::<T>(out.as_ptr(), N),',
                '        probe_count_unrolled::<T>(orig.as_ptr(), N) == '
                'probe_count_unrolled::<T>(out.as_ptr(), N),')
    for n in range(2, 6):
        a = replace(a,
                    f'    general_stable_direct_u64_n{n}, general_route_const_u64_properties, {n}',
                    f'    general_stable_direct_u64_n{n},\n'
                    f'    general_route_const_u64_properties,\n    {n}')
    out[MERGE] = a

    a = out[NETWORK]
    a = replace(a, 'fn insert_tail_start1_frame<const START: usize>',
                'fn insert_tail_start1_frame')
    a = replace(a, '''    const { assert!(START == 1) };
    let mut i = 0;
    while i < START {
        assert!(v[i] == pre[i], "insert-tail contract covers prefix before begin unchanged");
        i += 1;
    }
''', '''    assert!(v[0] == pre[0], "insert-tail contract covers prefix before begin unchanged");
''')
    a = replace(a, 'fn insert_tail_group_value<const START: usize, const LO: usize, const HI: usize>',
                'fn insert_tail_group_value<const LO: usize, const HI: usize>')
    a = replace(a, '        assert!(START == 1);\n', '')
    a = replace(a, 'assert!(START < LO && LO <= HI && HI < 17)',
                'assert!(1 < LO && LO <= HI && HI < 17)')
    a = replace(a, '// SAFETY: START == 1 < LO <= tail <= HI < 17;',
                '// SAFETY: 1 < LO <= tail <= HI < 17;')
    a = replace(a, 'base.add(START)', 'base.add(1)')
    a = replace(a, 'insert_tail_start1_frame::<START>', 'insert_tail_start1_frame')
    a = replace(a, 'insert_tail_group_value::<1, $lo, $hi>',
                'insert_tail_group_value::<$lo, $hi>')
    out[NETWORK] = a

    a = out[SCRATCH]
    a = replace(a, '{CopyOnDrop, SMALL_SORT_GENERAL_THRESHOLD, StableSmallSortTypeImpl}',
                '{SMALL_SORT_GENERAL_THRESHOLD, StableSmallSortTypeImpl}')
    a = replace(a, 'use super::merge::set_value_probe;',
                'use super::merge::{probe_count_unrolled, regions_are_disjoint, set_value_probe};')
    a = replace(a, 'CopyOnDrop::<u64>::regions_are_disjoint', 'regions_are_disjoint::<u64>')
    a = replace(a, 'CopyOnDrop::<u64>::probe_count_unrolled', 'probe_count_unrolled::<u64>', count=2)
    out[SCRATCH] = a

    a = out[SPECFIX]
    a = replace(a, 'use super::{lt_u8, lt_u64};', 'use super::{lt_u8, lt_u64, regions_are_disjoint};')
    a = replace(a, '    CopyOnDrop, bidirectional_merge, insert_tail, sort4_stable, swap_if_less,',
                '    bidirectional_merge, insert_tail, sort4_stable, swap_if_less,')
    a = replace(a, 'CopyOnDrop::<T>::regions_are_disjoint', 'regions_are_disjoint::<T>', count=2)
    out[SPECFIX] = a
    return out


def logical_source(src):
    """Same method bodies, keyed individually, with T supplied by their old impl."""
    src = copy.deepcopy(src)
    expanded = []
    for it in src.expanded[MERGE]:
        if it.kind == 'impl' and it.name == 'impl < T > CopyOnDrop < T >':
            methods = s.split_items(it.body[-1].children)
            assert {m.name for m in methods} == METHODS
            for m in methods:
                m.file = MERGE
            expanded.extend(methods)
        else:
            expanded.append(it)
    src.expanded[MERGE] = expanded
    return src


def calls(it, names):
    """Call tokens, with item and call ordinal as stable source-site coordinates."""
    found = []
    def walk(ts):
        for i, tok in enumerate(ts):
            if tok.kind != 'group':
                continue
            macro = i >= 2 and s.is_i(ts[i - 2], 'assert') and s.is_p(ts[i - 1], '!')
            kani = (i >= 4 and s.is_i(ts[i - 4], 'kani')
                    and s.is_p(ts[i - 3], ':') and s.is_p(ts[i - 2], ':')
                    and s.is_i(ts[i - 1]) and ts[i - 1].text in names)
            if tok.text == '(' and ((macro and 'assert' in names) or kani):
                found.append((ts[i - 1].text if kani else 'assert!', s.ser(tok.children)))
            walk(tok.children)
    walk(it.tokens())
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rustfmt', default=RUSTFMT, help='authorized rustfmt wrapper')
    args = parser.parse_args()
    old, new = s.Source(BASE), s.Source(None)
    expected = expected_sources(old.files)
    assert set(old.files) == set(new.files)
    assert expected == new.files, 'bytes differ outside the exact authorized transformations'
    off, on = new.roots(False), new.roots(True)
    for label, roots, count in [('ordinary', off, 233), ('cfg-on', on, 246)]:
        names = ''.join(s.PREFIX + n + '\n' for n in sorted(roots))
        assert len(roots) == count
        assert names == (HERE.parent / 'optinmove' / (label + '-expected.txt')).read_text()
        assert set(roots) == set(old.roots(label == 'cfg-on'))
        (HERE / (label + '-expected.txt')).write_text(names)
    before, after = logical_source(old), logical_source(new)
    bi, ai = o.items(before), o.items(after)
    assert set(bi) - set(ai) <= {k for k in bi if k[1] == 'use'}
    for name in METHODS:
        key = (MERGE, 'fn', name)
        # Exactly the old body, adding only the generic parameter to the signature.
        assert replace(bi[key].text(), 'fn ' + name + ' (',
                       'fn ' + name + ' < T > (') == ai[key].text()
    affected = {g: [] for g in GROUPS}
    unchanged, closure_hashes, sites = [], {}, {}
    roots_old = before.roots(True)
    for name, root in sorted(after.roots(True).items()):
        controls = name not in off
        a = s.closure(before, [roots_old[name]], controls)
        b = s.closure(after, [root], controls)
        groups = [g for g, funcs in GROUPS.items()
                  if any(k[1] == 'fn' and k[2] in funcs for k in set(a) | set(b))]
        for g in groups:
            affected[g].append(name)
        if not groups:
            assert roots_old[name][1].text() == root[1].text(), ('root changed', name)
            assert set(a) == set(b), ('closure keys changed', name, set(a) ^ set(b))
            assert all(a[k].text() == b[k].text() for k in a), ('closure changed', name)
            unchanged.append(name)
            closure_hashes[name] = o.digest('\n'.join(str(k) + a[k].text() for k in sorted(a)))
        # No covers occur in the moved methods or deleted branches. Every existing
        # cover remains in the same item and call ordinal with its complete arguments.
        ac = {str(k): calls(it, {'cover'}) for k, it in a.items() if calls(it, {'cover'})}
        bc = {str(k): calls(it, {'cover'}) for k, it in b.items() if calls(it, {'cover'})}
        assert ac == bc, ('cover site changed', name)
        for k in set(a) & set(b):
            assert t.normalized(a[k].text())[1] == t.normalized(b[k].text())[1], (name, k)
        sites[name] = dict(sorted(ac.items()))
    assert subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT]) == Path(s.SMALLSORT).read_bytes()
    assert set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines()) == {
        MERGE, NETWORK, SCRATCH, SPECFIX}
    assert not o.git('diff', '--name-only', TOOLING, '--', *t.LANES)
    for f, text in new.files.items():
        assert not t.overlong_lines(text), (f, t.overlong_lines(text))
        comments = '\n'.join(x for x in text.splitlines() if x.lstrip().startswith('//'))
        assert not t.FORBIDDEN.search(comments), f
        assert all(not t.FORBIDDEN.search(m) for m in t.normalized(text)[1]), f
    subprocess.run(['git', 'diff', '--check'], check=True)
    format_paths = [s.SMALLSORT, *sorted(new.files)]
    format_before = {f: Path(f).read_bytes() for f in format_paths}
    rustfmt_command = [args.rustfmt, '--check', '--edition', '2024', '--config-path',
                       RUSTFMT_CONFIG, s.SMALLSORT]
    formatted = subprocess.run(rustfmt_command, check=True, capture_output=True, text=True)
    assert not formatted.stdout, ('unexpected rustfmt check output', formatted.stdout)
    assert format_before == {f: Path(f).read_bytes() for f in format_paths}
    (HERE / 'rustfmt-check.txt').write_text(
        'command: ' + ' '.join(rustfmt_command) + '\nexit_code: 0\nstdout: <empty>\nstderr: '
        + (formatted.stderr or '<empty>') + '\nsource_bytes_unchanged: true\n')
    request_path = HERE / 'RUN-REQUEST.json'
    request = json.loads(request_path.read_text())
    assert request_path.read_bytes() == (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    assert request['request_id'] == 'leanhelpers-g1-20261106-01'
    assert request['agent'] == 'k1-merge' and request['kind'] == 'diagnostic'
    assert request['runner'] == 'gcb-e2-standard-4' and request['kani_jobs'] == 1
    assert request['controls'] is True and request['inventory'] is False
    assert request['harness_timeout_minutes'] == 8
    wanted = [
        'merge::drop_fallback_drop_count_n2',
        'merge::drop_fallback_tag_permutation_n2',
        'merge::sort4_arbitrary_comparator_u64_n4',
        'merge::general_stable_direct_u8_n2',
        'scratchgeom::stable_u64_min_scratch_n2',
        'merge::merge_contract_u8_n5',
        'network::insert_tail_contract_u64_start1_tail15_to16',
    ]
    assert request['harnesses'] == [
        {'name': s.PREFIX + n, 'expect': 'SUCCESS'} for n in wanted]
    baseline = json.loads((HERE / 'baseline-rows.json').read_text())
    assert [r['name'] for r in baseline['rows']] == [s.PREFIX + n for n in wanted]
    for row in baseline['rows']:
        source = row['source']
        data = subprocess.check_output(
            ['git', 'show', source['commit'] + ':' + source['path']], text=True)
        if 'row' in source:
            assert o.digest(data) == baseline['v8c_tsv_sha256']
            records = {r['harness']: r for r in csv.DictReader(io.StringIO(data), delimiter='\t')}
            previous = records[row['name'].removeprefix(s.PREFIX)]
            assert previous == source['row'] and previous['ubuntu_status'] == 'SUCCESSFUL'
            assert row['seconds'] == float(previous['ubuntu_vt_s'])
            assert row['covers'] == previous['ubuntu_covers']
        else:
            assert source['excerpt'] in data
            assert str(row['seconds']) in source['excerpt']
            assert row['covers'].replace(' of ', '/') in source['excerpt']
    expected_covers = json.loads((HERE / 'expected-covers.json').read_text())
    assert expected_covers == {r['name']: int(r['covers'].split()[0])
                               for r in baseline['rows']}
    assert sum(expected_covers.values()) == 14
    for row in request['harnesses']:
        assert row['expect'] == 'SUCCESS'
        assert row['name'].removeprefix(s.PREFIX) in set().union(*map(set, affected.values()))
    counts = {g: len(ns) for g, ns in affected.items()}
    union = set().union(*map(set, affected.values()))
    report = {
        'status': 'PASS', 'base_sha': BASE, 'tooling_base': TOOLING,
        'library_commit': o.git('log', '-1', '--format=%H', '--', 'library'),
        'library_tree': o.git('rev-parse', 'HEAD:library'),
        'ordinary': len(off), 'cfg_on': len(on), 'controls': len(set(on) - set(off)),
        'affected_by_change': counts, 'affected_union': len(union),
        'affected_ordinary': len(union & set(off)), 'affected_controls': len(union - set(off)),
        'unchanged_roots_and_closures': len(unchanged), 'unchanged_names': unchanged,
        'unchanged_closure_sha256': closure_hashes,
        'closure_model': 'Conservative inherited identifier resolver; old impl split into methods.',
        'scope': 'Source tokens only, not compiler resolution, inventory, or new proof credit.',
        'exact_authorized_source_transformations': True,
        'method_bodies_token_identical': True, 'assert_messages_identical': True,
        'cover_item_call_ordinal_and_arguments_identical': True,
        'smallsort_bytes_identical': True, 'tooling_unchanged': True,
        'rustfmt_check': {'status': 'PASS', 'command': rustfmt_command, 'exit_code': 0,
                          'stdout_empty': True, 'source_bytes_unchanged': True},
        'overlong_lines': [], 'forbidden_comments_and_messages': [],
        'source_sha256': {f: o.digest(text) for f, text in sorted(new.files.items())},
        'request_sha256': o.digest(request_path.read_text()),
        'baseline_rows_and_covers_source_checked': True,
    }
    ocounts = Counter(n.split('::')[0] for n in union)
    report['affected_by_module'] = dict(sorted(ocounts.items()))
    for filename, data in [('check-report.json', report), ('affected-roots.json', affected),
                           ('cover-sites.json', sites)]:
        (HERE / filename).write_text(json.dumps(data, indent=2) + '\n')
    (HERE / 'line-delta.tsv').write_text('added\tdeleted\tfile\n' +
        o.git('diff', '--numstat', BASE, '--', 'library') + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'ordinary', 'cfg_on',
                     'affected_by_change', 'affected_union', 'unchanged_roots_and_closures']}))


if __name__ == '__main__':
    main()
