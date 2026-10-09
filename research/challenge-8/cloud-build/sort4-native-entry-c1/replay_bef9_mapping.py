#!/usr/bin/env python3
"""Replay only pure mapping classifiers over immutable saved native evidence."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--extracted', type=Path, required=True)
    ap.add_argument('--record', type=Path, required=True)
    args = ap.parse_args()
    home = Path(__file__).resolve().parent
    # This module AST-selects only pure collector functions/constants. Its
    # unittest runner is under __main__; no proof/export/build entrypoint loads.
    spec = importlib.util.spec_from_file_location('pure_native_classifier', home/'test_native_entry_classifier.py')
    pure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pure)
    rows = json.loads(args.record.read_text())
    evidence = args.extracted/'allprooflogs/cases/sort4-caller-entry'
    for case, saved in rows['cases'].items():
        root = evidence/'cases'/case
        fixture = root/'fixture'
        log = (fixture/'verification.log').read_text(errors='replace')
        entries = list(re.finditer(r"(?m)^\s*\d+\.\d+s: [^\n]*: Verifying function 'small_sort_general_with_scratch'\s*$", log))
        entry = entries[0].start() if len(entries) == 1 else None
        result = pure.namespace['native_entry_mapping'](
            fixture, json.loads((root/'source-certificate.json').read_text()),
            (root/'normal-full-prefix-mir.txt').read_text(),
            (root/'readonly-full-prefix-mir.txt').read_text(),
            log[entry:] if entry is not None else '', entry)
        assert result['status'] == saved['replayed_mapping_gate'], case
        for mode in ('normal', 'readonly'):
            actual = result['artificial_ghost_boundary']['normal_and_readonly'][mode]
            expected = saved['ghost_spans_normal_readonly'][mode]
            assert actual['mir_ghost_statement'] == [expected['ghost_span']], case
            assert actual['full_function_record_sha256'] == expected['full_mir_sha256'], case
        for rel, expected in saved['saved_input_sha256'].items():
            assert hashlib.sha256((root/rel).read_bytes()).hexdigest() == expected, (case, rel)
    rows['replay_command'] = (f'python3 -B {Path(__file__).relative_to(home.parents[3])} '
                              f'--extracted {args.extracted} --record {args.record}')
    rows['replay_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.record.write_text(json.dumps(rows, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'cases': len(rows['cases']), 'mapping_gates_reproduced': True,
                      'saved_inputs_hash_verified': True, 'proof_credit': False}))


if __name__ == '__main__':
    main()
