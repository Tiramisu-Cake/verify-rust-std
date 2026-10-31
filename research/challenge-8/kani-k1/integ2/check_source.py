#!/usr/bin/env python3
"""Audit the bounded source integration; this is not compiler or proof evidence."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scope'))
from source_inventory import MODULES, ROOT, inventory, source
from source_items import CFG, imports, items
from assemble_library import BASE, item, ungate


def tokens(text):
    # Keep literal contents intact while ignoring comments and formatting outside literals.
    parts = re.findall(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/|\w+|[^\s]', text)
    return [p for p in parts if not p.startswith(('//', '/*'))]


def identity(i):
    if i['kind'] == 'call':
        return i['kind'], i['name'].split('(', 1)[1].split(',', 1)[0]
    return i['kind'], i['name']


def mapped(text):
    return {identity(i): text[i['start']:i['end']] for i in items(text)}


def same(a, b):
    assert tokens(a) == tokens(b)


def symbol_table(text):
    result = {}
    for i in items(text):
        if i['kind'] in ('fn', 'macro'):
            assert i['name'] not in result, i['name']
            result[i['name']] = identity(i)
        elif i['kind'] == 'use':
            for path in imports(i['body']):
                name = path.rsplit('::', 1)[-1]
                assert name not in result, name
                result[name] = path
    return result


def main():
    merge, network = source('merge'), source('network')
    old_merge = source('merge', BASE)
    cfg_changes = {
        'merge': {('call', f'route_safety_all_routes_n{n}') for n in range(3, 8)} |
                 {('call', 'general_stable_sorted_permutation_u8_n9')},
        'network': {('call', f'network_correctness_u8_n{n}') for n in (10, 11, 12)} |
                   {('call', 'insertion_permutation_u8_n11')},
    }
    changed_bodies = {('fn', name) for name in (
        'general_direct_u64_properties', 'stable_direct_u64_properties',
        'general_stable_direct_value_corruption_control_u64_n2')}
    replaced = {('call', f'general_stable_direct_u64_n{n}') for n in range(2, 6)}
    changes, dependencies, preserved = [], [], 0
    for module in MODULES:
        old_text, text = source(module, BASE), source(module)
        old, current = mapped(old_text), mapped(text)
        expected_removed = replaced if module == 'merge' else set()
        assert old.keys() - current.keys() == expected_removed, module
        old_symbols, new_symbols = symbol_table(old_text), symbol_table(text)
        for symbol, target in old_symbols.items():
            assert new_symbols[symbol] == target, (module, symbol)
        for key, body in old.items():
            if key in expected_removed:
                changes.append(dict(module=module, item=key, change='macro caller to const helper proof'))
                continue
            actual = current[key]
            if module == 'merge' and key in changed_bodies:
                changes.append(dict(module=module, item=key, change='approved body delta'))
                continue
            if key in cfg_changes.get(module, set()):
                same(ungate(body), ungate(actual))
                assert body.count(CFG) != actual.count(CFG)
                changes.append(dict(module=module, item=key, change='cfg only'))
            else:
                same(body, actual)
                preserved += 1
            refs = sorted(set(tokens(body)) & old_symbols.keys())
            assert {r: old_symbols[r] for r in refs} == {r: new_symbols[r] for r in refs}
            dependencies.append(dict(module=module, item=key, resolved_local_symbols=refs))
        for key in current.keys() - old.keys():
            changes.append(dict(module=module, item=key, change='added item'))

    old = item(old_merge, 'general_direct_u64_properties')
    same(item(merge, 'general_direct_u64_properties'),
         old.replace('N == 6 || N == 7 || N == 8', 'N >= 6 && N <= 9'))
    old = item(old_merge, 'general_stable_direct_value_corruption_control_u64_n2')
    same(item(merge, 'general_stable_direct_value_corruption_control_u64_n2'), old.replace(
        '[MaybeUninit::<u64>::uninit();', '[const { MaybeUninit::<u64>::uninit() };'))
    same(ungate(item(merge, 'stable_direct_aggregate_u64_properties')),
         item(old_merge, 'stable_direct_u64_properties').replace(
             'stable_direct_u64_properties', 'stable_direct_aggregate_u64_properties'))
    same(item(merge, 'stable_direct_u64_properties'), ungate(item(
        source('merge', 'b2930031d8'), 'stable_direct_const_u64_properties')).replace(
            'stable_direct_const_u64_properties', 'stable_direct_u64_properties'))

    expected = ungate(item(source('merge', 'a9daab85b0'), 'general_route_const_properties'))
    expected = expected.replace('fn general_route_const_properties<\n'
        '    T: kani::Arbitrary + Copy + FreezeMarker,\n'
        '    F: FnMut(&T, &T) -> bool,\n    const N: usize,\n>(\n    mut cmp: F,\n) {',
        'fn general_route_const_u64_properties<const N: usize>() {')
    expected = re.sub(r'\bT\b', 'u64', expected)
    expected = expected.replace('    let orig = v;\n', '    let orig = v;\n    let mut cmp = lt_u64;\n')
    same(item(merge, 'general_route_const_u64_properties'), expected)
    for n in range(2, 6):
        same(item(merge, f'general_stable_direct_u64_n{n}'),
             f'#[kani::proof]\n#[kani::unwind(34)]\nfn general_stable_direct_u64_n{n}() {{\n'
             f'general_route_const_u64_properties::<{n}>();\n}}')
        same(ungate(item(merge, f'general_stable_direct_nonconst_u64_n{n}')),
             item(old_merge, f'general_stable_direct_u64_n{n}').replace(
                 f'general_stable_direct_u64_n{n}', f'general_stable_direct_nonconst_u64_n{n}'))
    for n in (6, 7, 8):
        same(ungate(item(merge, f'stable_direct_aggregate_u64_n{n}')),
             f'define_direct_u64_route_harness!(stable_direct_aggregate_u64_n{n}, '
             f'stable_direct_aggregate_u64_properties, {n});')
    for route in ('general', 'stable'):
        same(item(merge, f'{route}_direct_u64_n9'),
             f'define_direct_u64_route_harness!({route}_direct_u64_n9, '
             f'{route}_direct_u64_properties, 9);')
    for name in ('general_direct_u8_n9_properties', 'stable_direct_nonconst_u8_n9_properties',
                 'define_direct_u8_n9_route_harness', 'general_direct_u8_n9',
                 'stable_direct_nonconst_u8_n9'):
        same(item(merge, name), ungate(item(source('merge', '2c65b6cdd9'), name)))
    for name in ('insert_tail_start1_frame', 'insert_tail_group_value',
                 'insert_tail_start1_group_case', 'insert_tail_contract_u64_start1_tail2_to8',
                 'insert_tail_contract_u64_start1_tail9_to12',
                 'insert_tail_contract_u64_start1_tail13_to16',
                 'insert_tail_contract_u64_start1_prefix_frame_control',
                 'insert_tail_contract_u64_start1_suffix_frame_control'):
        same(ungate(item(network, name)), ungate(item(source('network', 'b98ee415fd'), name)))
    paths = subprocess.check_output(['git', 'diff', BASE, '--name-only', '--', 'library'],
                                    text=True).splitlines()
    assert set(paths) == {str(ROOT / (m + '.rs')) for m in ('merge', 'network')}
    for path in paths:
        assert max(map(len, Path(path).read_text().splitlines())) <= 100
    records = inventory()
    assert len(records) == 479 and sum(not r['opt_in'] for r in records) == 197
    assert not any(s in merge for s in ('stable_direct_const_u64_n8',
                                       'stable_direct_nonconst_u64_n9',
                                       'stable_direct_const_u8_n9'))
    locations = {}
    for module, name, needle in (
        ('merge', 'assert_sorted_and_probe_preserved', '        assert!'),
        ('merge', 'assert_sorted_and_probe_preserved', '    assert!(\n'),
        ('network', 'insert_tail_start1_frame', '        assert!'),
        ('network', 'insert_tail_start1_frame', '    assert!(prefix_unchanged')):
        text = source(module)
        body = item(text, name)
        pos = text.index(body) + body.index(needle)
        locations[f'{module}::{name}::{needle.strip()}'] = dict(
            path=str(ROOT / (module + '.rs')), line=text.count('\n', 0, pos) + 1)
    report = dict(status='PASS_STATIC_SOURCE_AUDIT_ONLY', baseline=BASE,
                  library_commit=subprocess.check_output(
                      ['git', 'log', '-1', '--format=%H', '--', 'library'], text=True).strip(),
                  library_tree=subprocess.check_output(
                      ['git', 'rev-parse', 'HEAD:library'], text=True).strip(),
                  changed_library_files=paths, changed_items=changes,
                  preserved_items=preserved, preserved_resolved_local_bindings=dependencies,
                  source_sha256={p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
                  expected_control_locations=locations, ordinary=197, controls_cfg=479,
                  donor_bodies_match=True, production_tool_lane_unchanged=True,
                  limitations=['Lexical local dependency audit, not Rust name resolution',
                               'No compiler, native inventory or proof result on candidate tree',
                               'Intentional stable helper replacement affects direct N6..8 consumers'])
    (HERE / 'source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ('preserved_resolved_local_bindings', 'source_sha256')}, indent=2))


if __name__ == '__main__':
    main()
