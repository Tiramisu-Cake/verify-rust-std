#!/usr/bin/env python3
"""Bounded, local regular-output replay; never invokes Cargo or Kani."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

BASE = Path('/root/kani-fix-3300-worker14')
FIXED = Path('/root/kani-fix-3300-c1b')
LOG = Path('/root/kani3300-h1-ci/gateA-json-failures.log')
PREFIX = '/home/runner/work/kani/kani/export'
ORIGINAL_PREFIX = '/home/runner/work/kani/kani'
SPEC = importlib.util.spec_from_file_location(
    'c1b_checker', FIXED / 'tests/json-handler/uninit-contract-oracles/checker.py')
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    if isinstance(value, dict):
        return {key: canonical(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return CHECKER.normalize(value, ORIGINAL_PREFIX)


def load(repo, filename):
    return json.loads((repo / 'tests/json-handler' / filename).read_text())


def main():
    manifest_checks = []
    for filename in ('uninit-contract-oracles/oracles.json', 'uninit-part1-composition/roots.json'):
        before, after = load(BASE, filename), load(FIXED, filename)
        assert canonical(before) == after, filename
        manifest_checks.append({'file': filename, 'only_canonical_paths_changed': True,
                                'base_sha256': digest(BASE / 'tests/json-handler' / filename),
                                'fixed_sha256': digest(FIXED / 'tests/json-handler' / filename)})
    log = LOG.read_text()
    oracle_cases = {case['id']: case for case in load(FIXED, 'uninit-contract-oracles/oracles.json')['cases']}
    old_cases = {case['id']: case for case in load(BASE, 'uninit-contract-oracles/oracles.json')['cases']}
    replay = []
    for part in log.split('Oracle observation: ')[1:]:
        observation = json.loads(part.splitlines()[0])
        if observation['status'] != 'FAIL':
            continue
        case = oracle_cases[observation['case']]
        text = '\n'.join(line.removeprefix('Kani output: ') for line in part.splitlines()
                         if line.startswith('Kani output: ')) + '\n'
        rows = CHECKER.regular_properties(text)
        by_id = {row['id']: row for row in rows}
        differences = []
        for expected in old_cases[case['id']]['binding']['required_regular']:
            actual = by_id[expected['id']]
            if actual != expected:
                assert all(actual[key] == value for key, value in expected.items() if key != 'location')
                differences.append({'id': expected['id'], 'expected': expected['location'],
                                    'actual': actual['location']})
        normalized = {CHECKER.normalize(row['id'], PREFIX): CHECKER.normalize_property(row, PREFIX)
                      for row in rows}
        expected_rows = case['binding']['required_regular']
        assert all(normalized[row['id']] == row for row in expected_rows)
        replay.append({'case': case['id'], 'original_reason': observation['reason'],
                       'required_regular_rows': len(expected_rows), 'canonical_exact_match': True,
                       'original_differences': differences})
    assert {row['case'] for row in replay} == {'p2', 'postcondition-hole', 'clause'}

    text = '\n'.join(line.removeprefix('isolated-immutable_legal: ') for line in log.splitlines()
                     if line.startswith('isolated-immutable_legal: ')) + '\n'
    actual = CHECKER.regular_properties(text)
    case = load(FIXED, 'uninit-part1-composition/roots.json')['roots'][0]
    old = load(BASE, 'uninit-part1-composition/roots.json')['roots'][0]
    expected = case['expected_inventory']
    by_id = {row['id']: row for row in actual}
    differences = []
    for row in old['expected_inventory']:
        observed = by_id[row['id']]
        if observed != row:
            assert all(observed[key] == value for key, value in row.items() if key != 'location')
            differences.append(row['id'])
    normalized = [CHECKER.normalize_property(row, PREFIX) for row in actual]
    freeze = lambda row: json.dumps(row, sort_keys=True)
    assert Counter(map(freeze, normalized)) == Counter(map(freeze, expected))
    report = {'scope': 'LOCAL_REGULAR_REPLAY_ONLY; full JSON validation and gate rerun NOT_RUN',
              'run': '43514459160', 'log': str(LOG), 'log_sha256': digest(LOG),
              'manifest_checks': manifest_checks, 'oracle_replay': replay,
              'composition_replay': {'root': case['name'], 'actual_rows': len(actual),
                                     'expected_rows': len(expected), 'same_ids_statuses_descriptions': True,
                                     'original_location_mismatch_count': len(differences),
                                     'canonical_exact_match': True}}
    print(json.dumps(report, indent=2) + '\n', end='')


if __name__ == '__main__':
    main()
