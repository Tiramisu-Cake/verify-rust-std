#!/usr/bin/env python3
"""Apply the approved INTEG2 item-level integration to the ASSEMBLY baseline."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scope'))
from source_inventory import ROOT, source
from source_items import CFG, items

BASE = 'e6a8ad05c9'


def item(text, name):
    found = [i for i in items(text) if i['name'] == name or
             (i['kind'] == 'call' and i['name'].split('(', 1)[1].split(',', 1)[0] == name)]
    assert len(found) == 1, (name, len(found))
    i = found[0]
    return text[i['start']:i['end']]


def ungate(text):
    return text.replace(CFG + '\n', '')


def main():
    merge = source('merge', BASE)
    network = source('network', BASE)
    for name in [f'route_safety_all_routes_n{n}' for n in range(3, 8)]:
        old = item(merge, name)
        assert old.startswith(CFG)
        merge = merge.replace(old, ungate(old), 1)
    for name in [f'network_correctness_u8_n{n}' for n in (10, 11, 12)] + [
            'insertion_permutation_u8_n11']:
        old = item(network, name)
        assert old.startswith(CFG)
        network = network.replace(old, ungate(old), 1)

    old = item(merge, 'general_direct_u64_properties')
    merge = merge.replace(old, old.replace('N == 6 || N == 7 || N == 8', 'N >= 6 && N <= 9'), 1)
    old = item(merge, 'stable_direct_u64_properties')
    fallback = CFG + '\n' + old.replace('stable_direct_u64_properties',
                                        'stable_direct_aggregate_u64_properties')
    const = ungate(item(source('merge', 'b2930031d8'), 'stable_direct_const_u64_properties'))
    const = const.replace('stable_direct_const_u64_properties', 'stable_direct_u64_properties')
    merge = merge.replace(old, const + '\n\n' + fallback, 1)
    anchor = item(merge, 'stable_direct_u64_n8')
    extra = '\n\n' + '\n'.join(
        f'define_direct_u64_route_harness!({route}_direct_u64_n9, {route}_direct_u64_properties, 9);'
        for route in ('general', 'stable'))
    extra += '\n\n' + '\n'.join(
        CFG + '\n' + f'define_direct_u64_route_harness!(\n'
        f'    stable_direct_aggregate_u64_n{n},\n    stable_direct_aggregate_u64_properties,\n    {n}\n);'
        for n in (6, 7, 8))
    merge = merge.replace(anchor, anchor + extra, 1)

    const = ungate(item(source('merge', 'a9daab85b0'), 'general_route_const_properties'))
    const = const.replace('fn general_route_const_properties<\n'
                          '    T: kani::Arbitrary + Copy + FreezeMarker,\n'
                          '    F: FnMut(&T, &T) -> bool,\n'
                          '    const N: usize,\n>(\n    mut cmp: F,\n) {',
                          'fn general_route_const_u64_properties<const N: usize>() {')
    const = const.replace('::<T>', '::<u64>').replace('[T; N]', '[u64; N]')
    const = const.replace('<T as StableSmallSortTypeImpl>', '<u64 as StableSmallSortTypeImpl>')
    const = const.replace('::<T, _, N>', '::<u64, _, N>')
    const = const.replace('    let orig = v;\n', '    let orig = v;\n    let mut cmp = lt_u64;\n')
    assert 'T' not in const.split('{', 1)[0] and 'mut cmp: F' not in const
    anchor = item(merge, 'general_route_properties')
    merge = merge.replace(anchor, anchor + '\n\n' + const, 1)
    for n in range(2, 6):
        old = item(merge, f'general_stable_direct_u64_n{n}')
        new = ('#[kani::proof]\n#[kani::unwind(34)]\n'
               f'fn general_stable_direct_u64_n{n}() {{\n'
               f'    general_route_const_u64_properties::<{n}>();\n}}')
        fallback = CFG + '\n' + old.replace(f'general_stable_direct_u64_n{n}',
                                            f'general_stable_direct_nonconst_u64_n{n}')
        merge = merge.replace(old, new + '\n\n' + fallback + '\n', 1)
    name = 'general_stable_direct_value_corruption_control_u64_n2'
    old = item(merge, name)
    new = old.replace('[MaybeUninit::<u64>::uninit();', '[const { MaybeUninit::<u64>::uninit() };')
    assert new != old
    merge = merge.replace(old, new, 1)
    for ty in ('u64', 'u8'):
        old = item(merge, f'general_stable_sorted_permutation_{ty}_n9')
        if not old.startswith(CFG):
            merge = merge.replace(old, CFG + '\n' + old, 1)

    donor = source('merge', '2c65b6cdd9')
    merge += '\n\n// Direct u8 N9 routes retain nonconst scratch and the shared full-value oracle.\n'
    for name in ('general_direct_u8_n9_properties', 'stable_direct_nonconst_u8_n9_properties',
                 'define_direct_u8_n9_route_harness', 'general_direct_u8_n9',
                 'stable_direct_nonconst_u8_n9'):
        merge += ungate(item(donor, name)) + '\n\n'

    donor = source('network', 'b98ee415fd')
    anchor = item(network, 'insert_tail_value')
    extra = '\n\n// START1 tail intervals jointly cover every tail from 2 through 16.\n'
    for name in ('insert_tail_start1_frame', 'insert_tail_group_value',
                 'insert_tail_start1_group_case', 'insert_tail_contract_u64_start1_tail2_to8',
                 'insert_tail_contract_u64_start1_tail9_to12',
                 'insert_tail_contract_u64_start1_tail13_to16'):
        extra += ungate(item(donor, name)) + '\n\n'
    for side in ('prefix', 'suffix'):
        extra += item(donor, f'insert_tail_contract_u64_start1_{side}_frame_control') + '\n\n'
    network = network.replace(anchor, anchor + extra.rstrip(), 1)
    for module, text in (('merge', merge), ('network', network)):
        (ROOT / (module + '.rs')).write_text(text.rstrip() + '\n')


if __name__ == '__main__':
    main()
