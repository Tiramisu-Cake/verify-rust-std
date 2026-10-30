#!/usr/bin/env python3
"""Transfer only the ASSEMBLY blocks; BACKING2 entries await coordinator confirmation."""
import subprocess
import textwrap
from pathlib import Path

ROOT = Path('library/core/src/slice/sort/shared/smallsort/verify')
CFG = '#[cfg(kani_smallsort_controls)]\n'


def source(rev, module):
    return subprocess.check_output(['git', 'show', f'{rev}:{ROOT}/{module}.rs'], text=True)


def prepare(confirmed=False):
    types = source('ddcc33f837', 'types')
    donor = source('78c040559f', 'types')
    start = donor.index('// N8/N9 trait-route measurements')
    end = donor.index(CFG + '#[kani::proof]', start)
    block = donor[start:end]
    block = block.replace('// N8/N9 trait-route measurements stay opt-in until their time and memory budgets are reviewed.',
                          '// Combined Cell N8 and DropKey N9 remain opt-in timeout diagnostics.')
    block = block.replace('// Fixing the route avoids combining both Cell branches after the N8 measurement timed out.',
                          '// Fixed routes check each Cell branch independently.')
    for item in ('fixed_trait_case!(sorted_permutation_traits_general_drop_u8_n8,',
                 'fn fixed_route_trait_properties<', 'macro_rules! fixed_route_trait_case',
                 'fixed_route_trait_case!(sorted_permutation_traits_stable_fallback_cell_u8_n8,',
                 'fixed_route_trait_case!(sorted_permutation_traits_unstable_fallback_cell_u8_n8,'):
        assert CFG + item in block
        block = block.replace(CFG + item, item)
    anchor = CFG + '#[kani::proof]'
    pos = types.index(anchor, types.index('fixed_trait_case!(sorted_permutation_traits_fallback_cell_u8_n7,'))
    ordinary_drop = 'fixed_trait_case!(sorted_permutation_traits_general_drop_u8_n8, DropKey, 8);\n'
    block = ordinary_drop + '\n' + block.replace(ordinary_drop, '')
    types = types[:pos] + block + types[pos:]
    (ROOT / 'types.rs').write_text(types)

    merge = source('ddcc33f837', 'merge')
    backing = source('f28909ac02', 'merge').split('mod backing {\n', 1)[1]
    backing = textwrap.dedent(backing.rsplit('\n}', 1)[0])
    start = backing.index('fn scratch_view')
    # Extract helpers by the first proof attribute after them.
    end = backing.index('#[kani::proof]', start)
    helpers = backing[start:end].rstrip() + '\n\n'
    helpers = helpers.replace('general_direct_body', 'general_direct_u64_properties')
    helpers = helpers.replace('stable_direct_body', 'stable_direct_u64_properties')
    helpers = helpers.replace('const { assert!(N == 7) };',
                              'const { assert!(N == 6 || N == 7 || N == 8) };')
    helpers = helpers.replace('super::super::super::small_sort_general',
                              'super::super::small_sort_general')
    group = '// Direct u64 routes use real merge bodies and the shared full-value oracle.\n' + helpers
    group += '''macro_rules! define_direct_u64_route_harness {
    ($name:ident, $body:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            $body::<$n>();
        }
    };
}

'''
    for route in ('general', 'stable'):
        for n in (6, 7, 8):
            if not confirmed and ((route == 'stable' and n in (6, 7)) or
                                  (route == 'general' and n == 7)):
                group += CFG
            group += (f'define_direct_u64_route_harness!({route}_direct_u64_n{n}, '
                      f'{route}_direct_u64_properties, {n});\n')
    group += '\n'
    controls = backing[backing.rfind('#[kani::proof]', 0, backing.index('fn stable_value_corruption_control')):]
    # Include all attributes for the first control, including unwind.
    for old, new in (
        ('stable_value_corruption_control_u64_n2', 'stable_direct_value_corruption_control_u64_n2'),
        ('unsorted_halves_control_u64_n4', 'merge_aggregate_unsorted_halves_control_u64_n4'),
        ('allocation_bounds_control_u64', 'merge_aggregate_allocation_bounds_control_u64'),
    ):
        controls = controls.replace(old, new)
    controls = controls.replace('#[kani::proof]', CFG + '#[kani::proof]')
    group += controls.rstrip() + '\n\n'
    anchor = '// Flip a payload bit after real sorting: keys stay sorted, full-value counts must detect it.'
    assert merge.count(anchor) == 1
    merge = merge.replace(anchor, group + anchor)
    for n in (6, 7, 8):
        if confirmed or n == 8:
            item = f'define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n{n},'
            assert CFG + item not in merge
            merge = merge.replace(item, CFG + item)
    control = merge.index('fn general_stable_direct_value_corruption_control_u64_n2()')
    flip = merge.index('    v[0] ^= 1;', control)
    cover = '    kani::cover(true, "general/stable direct sort returns before payload corruption");\n'
    merge = merge[:flip] + cover + merge[flip:]
    (ROOT / 'merge.rs').write_text(merge)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--backing2-confirmed', action='store_true')
    args = parser.parse_args()
    prepare(args.backing2_confirmed)
