#!/usr/bin/env python3
"""Offline comparison of the coordinator-provided S1 root output, not an oracle update."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
SOURCE = Path('/root/kani-fix-3300-c2-s1')
OUT = Path(__file__).resolve().parent
REGULAR = OUT / 'ci-quick-43600410208/ordinary_ensures_legal.regular.txt'
MANIFEST = SOURCE / 'tests/json-handler/uninit-part1-composition/roots.json'
CHECKER = SOURCE / 'tests/json-handler/uninit-contract-oracles/checker.py'
# This prefix is visible in the supplied closure IDs; no receipt is reconstructed.
VISIBLE_PREFIX = '/home/runner/work/kani/kani'
TESTED = 'ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c'
FORMATTED = '69b13711e60a87458200833445d47488ab466344'
C1B = '3f2c12f46e9e32899e8d84e89c65cb6483ba685a'
UPSTREAM_FIX = '2ec6953d9'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=SOURCE).decode().strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Execute only the existing parser/normalizer definitions, without importing runners.
module = ast.parse(CHECKER.read_text())
functions = [node for node in module.body
             if isinstance(node, (ast.ClassDef, ast.FunctionDef))
             and node.name in {'Rejected', 'require', 'regular_properties',
                               'normalize', 'normalize_property'}]
namespace = {'re': re}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(CHECKER), 'exec'), namespace)
lines = REGULAR.read_text().splitlines()
text = '\n'.join(line.removeprefix('isolated-ordinary_ensures_legal: ') for line in lines)
actual = namespace['regular_properties'](text)
normalized = [namespace['normalize_property'](row, VISIBLE_PREFIX) for row in actual]
manifest = json.loads(MANIFEST.read_text())
root_index, root = next((i, row) for i, row in enumerate(manifest['roots'])
                        if row['name'] == 'ordinary_ensures_legal')
expected = root['expected_inventory']
assert len(expected) == 227 and len(actual) == 229
assert [int(n) for n in re.findall(r'^Check (\d+):', text, re.M)] == list(range(1, 230))
assert '** 0 of 229 failed (9 unreachable)' in text and 'VERIFICATION:- SUCCESSFUL' in text
old = {row['id']: (i, row) for i, row in enumerate(expected, 1)}
new = {row['id']: (i, row) for i, row in enumerate(normalized, 1)}
assert len(old) == 227 and len(new) == 229
lost = sorted(set(old) - set(new))
assert not lost, f'STOP: lost checks: {lost}'
added = set(new) - set(old)
assert added == {'kani::internal::enter_contract_clause.assertion.1',
                 'kani::internal::exit_contract_clause.assertion.1'}
header_lines = [i for i, line in enumerate(lines, 1)
                if re.match(r'^isolated-ordinary_ensures_legal: Check \d+:', line)]
assert len(header_lines) == len(actual)

# Exact old/new locations, tied to upstream #5093's source diff.
shifts = {}
for function, groups in {
    'enter_contract_clause': [(range(1, 7), '833:45', '833:33'),
                              (range(7, 13), '833:21', '835:25')],
    'exit_contract_clause': [(range(1, 7), '846:45', '849:33'),
                             (range(7, 13), '846:21', '851:25')],
    'in_contract_clause': [(range(1, 7), '892:26', '898:26')],
}.items():
    for numbers, before, after in groups:
        for number in numbers:
            pid = f'kani::internal::{function}.pointer_dereference.{number}'
            shifts[pid] = (f'library/kani_core/src/lib.rs:{before} in function kani::internal::{function}',
                           f'library/kani_core/src/lib.rs:{after} in function kani::internal::{function}')

rows = []
retained_rank = 0
for i, (raw, current) in enumerate(zip(actual, normalized), 1):
    path_fields = [key for key in raw if raw[key] != current[key]]
    record = {'actual_check_number': i, 'regular_file_line': header_lines[i - 1],
              'raw_actual': raw, 'diagnostic_existing_normalizer_result': current,
              'existing_normalization_changed_fields': path_fields}
    if current['id'] in old:
        retained_rank += 1
        old_index, before = old[current['id']]
        assert before['description'] == current['description']
        assert before['status'] == current['status']
        record.update({'expected_index_1_based': old_index,
                       'expected_json_pointer': f'/roots/{root_index}/expected_inventory/{old_index - 1}',
                       'expected': before,
                       'check_number_changed': i != old_index,
                       'retained_property_order_changed': retained_rank != old_index})
        if before != current:
            assert current['id'] in shifts
            assert (before['location'], current['location']) == shifts[current['id']]
            record.update({'classification': 'UPSTREAM_LOCATION_DRIFT',
                           'reason': 'Upstream #5093 splits static depth load/store into guarded arithmetic; pointer access columns/lines change, later in_contract_clause moves by six lines. Same ID, description and status.',
                           'source_cause': git('rev-parse', UPSTREAM_FIX) + ':library/kani_core/src/lib.rs'})
        elif path_fields:
            record.update({'classification': 'EXISTING_NORMALIZATION_ONLY',
                           'reason': 'Raw checkout/toolchain paths differ; existing checker.normalize (unchanged) maps the exact supplied row back to its inventory identity. No new normalization rule.',
                           'source_cause': 'tests/json-handler/uninit-contract-oracles/checker.py:45-64; run.py:217-228'})
        else:
            record.update({'classification': 'EXACT_ROW',
                           'reason': 'Exact ID, description, status and location; any changed Check number is presentation only.',
                           'source_cause': 'kani-driver/src/cbmc_property_renderer.rs:295-296; compare.py:109-110'})
    else:
        assert current['status'] == 'SUCCESS'
        function = 'enter_contract_clause' if 'enter_' in current['id'] else 'exit_contract_clause'
        line, operation = (835, 'add') if function.startswith('enter') else (851, 'subtract')
        assert current['description'] == f'attempt to {operation} with overflow'
        assert current['location'] == f'library/kani_core/src/lib.rs:{line}:49 in function kani::internal::{function}'
        record.update({'expected_index_1_based': None, 'expected': None,
                       'classification': 'UPSTREAM_REAL_ADDED_CHECK',
                       'reason': 'Upstream #5093 replaces saturating method call with guarded depth + 1 / depth - 1. Ordinary arithmetic emits a real overflow assertion; this is not an ID rename. The guard bounds the operation; supplied status is SUCCESS.',
                       'source_cause': git('rev-parse', UPSTREAM_FIX) + f':library/kani_core/src/lib.rs:{line}'})
    rows.append(record)
assert retained_rank == 227
counts = Counter(row['classification'] for row in rows)
assert counts == {'EXACT_ROW': 184, 'EXISTING_NORMALIZATION_ONLY': 13,
                  'UPSTREAM_LOCATION_DRIFT': 30, 'UPSTREAM_REAL_ADDED_CHECK': 2}
assert sum(row.get('retained_property_order_changed', False) for row in rows) == 90
assert sum(row.get('check_number_changed', False) for row in rows) == 227
assert Counter(row['status'] for row in expected) == {'SUCCESS': 218, 'UNREACHABLE': 9}
assert Counter(row['status'] for row in actual) == {'SUCCESS': 220, 'UNREACHABLE': 9}
# All source material used for attribution matches the pinned heads.
for path in ['library/kani_core/src/lib.rs', 'library/kani_core/src/mem_init.rs',
             'tests/json-handler/uninit-part1-composition/roots.json',
             'tests/json-handler/uninit-part1-composition/mixed.rs',
             'tests/json-handler/uninit-contract-oracles/checker.py']:
    assert git('rev-parse', TESTED + ':' + path) == git('rev-parse', FORMATTED + ':' + path)
assert git('rev-parse', C1B + ':library/kani_core/src/mem_init.rs') == git('rev-parse', TESTED + ':library/kani_core/src/mem_init.rs')
assert git('rev-parse', C1B + ':' + str(MANIFEST.relative_to(SOURCE))) == git('rev-parse', TESTED + ':' + str(MANIFEST.relative_to(SOURCE)))
result = {
    'scope': 'Offline supplied regular-output/inventory comparison for one isolated root; no oracle update or CI execution',
    'ci_run': '43600410208', 'tested_source': TESTED, 'formatted_candidate': FORMATTED,
    'ci_overlay_coordinator_reported_short_sha': 'ddd242820b',
    'inputs': {str(path): sha256(path) for path in [REGULAR, MANIFEST, CHECKER]},
    'upstream_source_cause': git('rev-parse', UPSTREAM_FIX),
    'diagnostic_prefix_visible_in_regular_closure_IDs': VISIBLE_PREFIX,
    'normalizer_limitation': 'Only existing normalization is applied for diagnosis; original receipt/export absent, prefix inferred from supplied IDs. No reconstructed CI receipt, new normalization, or oracle acceptance.',
    'counts': dict(counts), 'lost_checks': lost, 'status_or_description_changes': [],
    'retained_reordered_after_removing_added_rows': 90,
    'check_numbers_changed': 227,
    'expected_statuses': dict(Counter(row['status'] for row in expected)),
    'actual_statuses': dict(Counter(row['status'] for row in actual)),
    'root_conclusion': 'All 227 old rows have unique counterparts; 2 real upstream overflow checks added; no lost check in the supplied inventory.',
    'order_cause_limit': 'Renderer numbers backend-vector order without sorting; compare.check_single uses Counter, so permutation alone cannot reject. Particular backend permutation causality is not established from regular output alone; not root/harness-order isolation credit.',
    'rows': rows,
}
(OUT / 'DRIFT-CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
source_diff = subprocess.check_output(['git', 'diff', C1B, TESTED, '--', 'library/kani_core/src/lib.rs'], cwd=SOURCE)
(OUT / 'DRIFT-SOURCE.diff').write_bytes(source_diff)
print(json.dumps({key: result[key] for key in ['counts', 'lost_checks', 'status_or_description_changes', 'retained_reordered_after_removing_added_rows', 'check_numbers_changed']}, indent=2))
