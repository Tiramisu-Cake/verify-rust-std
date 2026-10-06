#!/usr/bin/env python3
"""Fail closed on exact Kani case, property, location and result shape.

All check blocks, including successes, are preserved as evidence. This parser
changes no verifier semantics and never substitutes an arbitrary nonzero exit
for an intended negative. Run and exercise it only on hosted Actions.
"""
import argparse
import json
import re
from pathlib import Path

CASES = {
    'prove_sort4_values': ('challenge8_sort4', 12, False),
    'negative_coincident_copy_overlap': ('challenge8_sort4_contract', 0, True),
    'negative_shifted_original_multiset': ('challenge8_sort4_contract', 0, True),
    'prove_shifted_output_witness': ('challenge8_sort4_contract', 1, False),
}


def classify(case, code, log):
    module, covers, negative = CASES[case]
    name = f'slice::sort::shared::smallsort::{module}::{case}'
    checks = []
    reasons = []
    for block in re.finditer(r'(?ms)^Check\s+(\d+):\s*([^\n]+)\n(.*?)(?=^Check\s+\d+:|\Z)', log):
        record = {'number': int(block[1]), 'id': block[2].strip()}
        for field in ('Status', 'Description', 'Location'):
            match = re.search(r'(?m)^\s*- ' + field + r': (.*)$', block[3])
            record[field.lower()] = match[1].strip().strip('"') if match else ''
        checks.append(record)
    failures = [c for c in checks if c['status'] == 'FAILURE']
    summaries = re.findall(r'Complete - (\d+) successfully verified harnesses, (\d+) failures, (\d+) total\.', log)
    markers = re.findall(r'(?m)^VERIFICATION:- (SUCCESSFUL|FAILED)\s*$', log)
    totals = re.findall(r'\*\* (\d+) of (\d+) failed', log)
    cover_totals = re.findall(r'\*\* (\d+) of (\d+) cover properties satisfied', log)
    check_covers = [c for c in checks if '.cover.' in c['id']]
    if not checks or len({c['id'] for c in checks}) != len(checks):
        reasons.append('missing or duplicate check blocks')
    if any(c['status'] not in {'SUCCESS', 'UNREACHABLE', 'SATISFIED', 'FAILURE'}
           or not c['description'] or not c['location']
           or (c['status'] == 'SATISFIED' and '.cover.' not in c['id']) for c in checks):
        reasons.append('unknown status or incomplete check block')
    if re.findall(r'(?m)^Checking harness (\S+)\.\.\.', log) != [name]:
        reasons.append('wrong or missing selected harness')
    expected_summary = ('0', '1', '1') if negative else ('1', '0', '1')
    if summaries != [expected_summary] or markers != [('FAILED' if negative else 'SUCCESSFUL')]:
        reasons.append('wrong or incomplete verification summary')
    if code != (1 if negative else 0):
        reasons.append('wrong raw process exit')
    if totals != [(str(len(failures)), str(len(checks) - len(check_covers)))]:
        reasons.append('failed-check total does not match parsed records')
    if len(check_covers) != covers or any(c['status'] != 'SATISFIED' for c in check_covers):
        reasons.append('missing or unsatisfied covers')
    if cover_totals != ([(str(covers), str(covers))] if covers else []):
        reasons.append('wrong cover summary')
    if re.search(r'(?im)^\s*(error(?:\[E\d+\])?:|could not compile|failed to compile)', log):
        reasons.append('compiler/frontend failure')
    if case == 'negative_coincident_copy_overlap':
        intended = lambda c: (re.fullmatch(r'ptr::copy_nonoverlapping::<i32>\.precondition_instance\.\d+', c['id'])
                              and c['description'] == 'memcpy src/dst overlap'
                              and c['location'] == 'library/core/src/ptr/mod.rs:555:14 in function ptr::copy_nonoverlapping::<i32>')
    elif case == 'negative_shifted_original_multiset':
        # Audit the exact assertion line in the appended source rather than
        # accepting any assertion at a nearby line or any helper failure.
        target = Path('library/core/src/slice/sort/shared/smallsort.rs')
        lines = target.read_text().splitlines()
        assertion_lines = [i + 1 for i, line in enumerate(lines)
                           if 'kani::assert(same_multiset(&after, &before), "original multiset preserved");' in line]
        intended = lambda c: (re.fullmatch(re.escape(name) + r'\.assertion\.\d+', c['id'])
                              and c['description'] == 'original multiset preserved'
                              and len(assertion_lines) == 1
                              and re.fullmatch(r'library/core/src/slice/sort/shared/smallsort.rs:'
                                               + str(assertion_lines[0]) + r':\d+ in function ' + re.escape(name), c['location']))
    else:
        intended = lambda c: False
    if negative:
        if not failures or not all(intended(c) for c in failures):
            reasons.append('failure outside predeclared intended property set')
        if case == 'negative_shifted_original_multiset' and len(failures) != 1:
            reasons.append('expected exactly one original-multiset assertion failure')
    elif failures:
        reasons.append('positive control failed')
    return {'case': case, 'process_exit': code, 'accepted': not reasons,
            'reasons': reasons, 'failed_checks': failures, 'checks': checks,
            'summary': summaries, 'covers': cover_totals}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--exit-code', type=int)
    parser.add_argument('--log', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--aggregate', nargs='*', type=Path)
    args = parser.parse_args()
    if args.aggregate is not None:
        records = [json.loads(p.read_text()) for p in args.aggregate]
        accepted = ([r['case'] for r in records] == list(CASES) and all(r['accepted'] for r in records))
        result = {'accepted': accepted, 'cases': records}
    else:
        if args.case is None or args.exit_code is None or args.log is None:
            parser.error('single case requires --case, --exit-code, --log')
        result = classify(args.case, args.exit_code, args.log.read_text())
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(f"{args.case or 'suite'}: {'ACCEPTED' if result['accepted'] else 'INCONCLUSIVE'}")
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
