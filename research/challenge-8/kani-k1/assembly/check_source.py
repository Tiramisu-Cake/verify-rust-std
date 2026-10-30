#!/usr/bin/env python3
"""Static transfer audit; does not establish compiler or proof acceptance."""
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scope'))
from source_inventory import ROOT, inventory, source
from source_items import CFG, items, key

BASE = 'ddcc33f837'
OPT = 'f052d6b7ec'
BACKING = 'f28909ac02'
UNSTABLE = '78c040559f'


def normalized(text):
    return re.sub(r'\s+', '', re.sub(r'//[^\n]*', '', text)).replace(CFG, '')


def item_map(text):
    return {key(i): text[i['start']:i['end']] for i in items(text)}


def function(text, name):
    return item_map(text)[('fn', name)]


def nested(text, name):
    return textwrap.dedent(text.split(f'mod {name} {{\n', 1)[1].rsplit('\n}', 1)[0])


def main():
    root = ROOT.parent
    for rev in (OPT, BACKING, UNSTABLE):
        for path in (root.with_suffix('.rs'), ROOT / 'comparators.rs'):
            blobs = [subprocess.check_output(['git', 'show', f'{r}:{path}']) for r in (BASE, rev)]
            assert blobs[0] == blobs[1], (rev, str(path))

    for module in ('merge', 'types'):
        old, current = item_map(source(module, BASE)), item_map(source(module))
        assert old.keys() <= current.keys(), module
        for k, body in old.items():
            assert normalized(body) == normalized(current[k]), (module, k)
    merge = source('merge')
    opt = nested(source('merge', OPT), 'opt_split')
    backing = nested(source('merge', BACKING), 'backing')
    for donor in (opt, backing):
        expected = function(donor, 'general_direct_body')
        expected = expected.replace('general_direct_body', 'general_direct_u64_properties')
        expected = re.sub(r'assert!\(N == 6 \|\| N == 8\)|assert!\(N == 7\)',
                          'assert!(N == 6 || N == 7 || N == 8)', expected)
        expected = expected.replace('super::super::super::small_sort_general',
                                    'super::super::small_sort_general')
        assert normalized(expected) == normalized(function(merge, 'general_direct_u64_properties'))
    expected = function(backing, 'stable_direct_body').replace(
        'stable_direct_body', 'stable_direct_u64_properties')
    assert normalized(expected) == normalized(function(merge, 'stable_direct_u64_properties'))
    assert normalized(function(backing, 'scratch_view')) == normalized(function(merge, 'scratch_view'))

    controls = {
        'stable_value_corruption_control_u64_n2': 'stable_direct_value_corruption_control_u64_n2',
        'unsorted_halves_control_u64_n4': 'merge_aggregate_unsorted_halves_control_u64_n4',
        'allocation_bounds_control_u64': 'merge_aggregate_allocation_bounds_control_u64',
    }
    for old, new in controls.items():
        expected = function(backing, old).replace(old, new)
        assert normalized(expected) == normalized(function(merge, new)), new
    types = source('types')
    for kind, name in (('fn', 'fixed_route_trait_properties'), ('macro', 'fixed_route_trait_case')):
        assert normalized(item_map(source('types', UNSTABLE))[(kind, name)]) == normalized(
            item_map(types)[(kind, name)])
    # UNSTABLE proof calls keep their exact arguments and attributes apart from cfg.
    donor_types = item_map(source('types', UNSTABLE))
    for k, body in item_map(types).items():
        if k[0] == 'call' and k not in item_map(source('types', BASE)):
            assert normalized(body) == normalized(donor_types[k]), k
    assert 'mod opt_split' not in merge and 'mod backing' not in merge
    assert 'stub' not in function(merge, 'general_direct_u64_properties')
    assert 'stub' not in function(merge, 'stable_direct_u64_properties')
    new_macro = item_map(merge)[('macro', 'define_direct_u64_route_harness')]
    assert '#[kani::unwind(34)]' in new_macro and 'stub' not in new_macro
    assert 'after the N8 measurement timed out' not in types
    records = inventory()
    ordinary = {r['name'].split('::verify::')[1] for r in records if not r['opt_in']}
    confirmed = [n for n in (6, 7) if f'merge::stable_direct_u64_n{n}' in ordinary]
    for n in (6, 7, 8):
        assert f'merge::general_direct_u64_n{n}' in ordinary
        assert (f'merge::general_stable_sorted_permutation_u64_n{n}' in ordinary) == (
            f'merge::stable_direct_u64_n{n}' not in ordinary)
    for n in (6, 7, 8):
        assert f'merge::general_stable_direct_u64_n{n}' not in ordinary
        assert f'merge::merge_scratch48_contract_u64_n{n}' not in ordinary
    assert len(records) == 463 and len(ordinary) == 182
    changed = subprocess.check_output(['git', 'diff', BASE, '--name-only', '--', 'library'], text=True).splitlines()
    assert set(changed) == {str(ROOT / (m + '.rs')) for m in ('merge', 'types')}
    for path in changed:
        assert max(map(len, Path(path).read_text().splitlines())) <= 100, path
    report = dict(result='PASS_STATIC_SOURCE_TRANSFER_ONLY', baseline=BASE,
                  library_commit=subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', 'library'], text=True).strip(),
                  library_tree=subprocess.check_output(['git', 'rev-parse', 'HEAD:library'], text=True).strip(),
                  sources=dict(OPT=OPT, BACKING2=BACKING, UNSTABLE8=UNSTABLE),
                  production_and_comparators_match=True, baseline_items_preserved_except_cfg=True,
                  direct_helpers_and_controls_match_donors=True, unwind_and_oracle_unchanged=True,
                  general_helper_change='union of permitted N literals and relative path after flattening',
                  ordinary=182, controls_cfg=463, stable_n6_n7_promoted=confirmed,
                  limitations=['No Rust expansion, compiler warnings, inventory or proof result',
                               'Donor SUCCESS is historical; no proof credit for the assembled tree'])
    (HERE / 'source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
