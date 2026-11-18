#!/usr/bin/env python3
"""Independent pinned-package review checks. No compiler, verifier or network."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

G0 = Path('/root/verify-rust-std-kani3300-g0')
SRC = Path('/root/kani-issue4591-fix-w15')
REL = 'research/challenge-8/kani-k1/kani3300/wave0/issue4591-fix'
PKG = G0 / REL
PACKAGE = 'bdf1bb42189257c9654eb55dfcda11b2f08a0b01'
HEAD = 'a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a'
TREE = '98fae98ce9e783bed0393d35657674da09c3aa31'
MAIN = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
RESULTS = []


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def check(name, ok):
    if not ok:
        raise AssertionError(name)
    RESULTS.append(name)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def expected_matches(expected, output):
    """Model compiletest contains_lines/contains, including adjacent groups."""
    groups, pending = [], []
    for line in expected.split('\n'):
        pending.append(line.removesuffix('\\') if line.endswith('\\') else line)
        if not line.endswith('\\'):
            groups.append(pending)
            pending = []
    if pending:
        groups.append(pending)
    actual = output.split('\n')
    return all(any(all(token.strip() in got for token, got in zip(group, actual[i:]))
                   for i in range(len(actual) - len(group) + 1)) for group in groups)


def main():
    pins = json.loads((PKG / 'SOURCE-PINS.json').read_text())
    paths = git(G0, 'ls-tree', '-r', '--name-only', PACKAGE, REL).decode().splitlines()
    check('package_exact_21_files', len(paths) == 21)
    for path in paths:
        check('committed_bytes:' + path.rsplit('/', 1)[1],
              (G0 / path).read_bytes() == git(G0, 'show', f'{PACKAGE}:{path}'))
    manifest = json.loads((PKG / 'MANIFEST.json').read_text())['files']
    check('author_manifest_exact_20_entries', len(manifest) == 20
          and set(manifest) == {Path(p).name for p in paths} - {'MANIFEST.json'})
    for name, record in manifest.items():
        data = (PKG / name).read_bytes()
        check('sealed:' + name, sha(data) == record['sha256'] and len(data) == record['bytes'])
    check('exact_candidate_head', git(SRC, 'rev-parse', 'HEAD').decode().strip() == HEAD)
    check('source_clean', not git(SRC, 'status', '--porcelain').strip())
    check('exact_tree', git(SRC, 'rev-parse', HEAD + '^{tree}').decode().strip() == TREE)
    check('sole_stock_main_parent', git(SRC, 'show', '-s', '--format=%P', HEAD).decode().strip() == MAIN)
    check('sole_candidate_range', git(SRC, 'rev-list', MAIN + '..' + HEAD).decode().split() == [HEAD])
    check('changed_set_exact', git(SRC, 'diff', '--name-only', MAIN, HEAD).decode().splitlines()
          == pins['changed_paths'])
    for path, record in pins['changed_files'].items():
        check('source_bytes:' + path, sha(git(SRC, 'show', HEAD + ':' + path)) == record['sha256'])
    for path, tree in pins['protected_git_trees'].items():
        check('protected:' + path, all(git(SRC, 'rev-parse', ref + ':' + path).decode().strip()
                                     == tree for ref in [MAIN, HEAD]))

    ci = json.loads((PKG / 'CI-REQUEST.json').read_text())
    inventory = json.loads((PKG / 'WORKFLOW-INVENTORY.json').read_text())['workflows']
    workflows = {}
    for path in git(SRC, 'ls-tree', '-r', '--name-only', HEAD, '.github/workflows').decode().splitlines():
        data = git(SRC, 'show', HEAD + ':' + path)
        workflows[Path(path).name] = yaml.load(data, Loader=yaml.BaseLoader)
    check('actual_all_16_workflows', len(workflows) == 16 and set(workflows) == set(inventory))
    push = []
    for name, workflow in workflows.items():
        check('actual_workflow:' + name, all(workflow.get(k) == inventory[name][k]
                                           for k in ['on', 'jobs', 'name', 'concurrency']))
        event = workflow.get('on', {}).get('push')
        if isinstance(event, dict) and '**' in event.get('branches', []):
            push.append(name)
            check('complete_native_jobs:' + name, workflow['jobs'] == ci['native_jobs'][name])
    check('independently_derived_branch_push_set', sorted(push) == sorted(ci['workflow_files']))
    instances = []
    for name in push:
        for job, config in workflows[name]['jobs'].items():
            matrix = config.get('strategy', {}).get('matrix', {})
            for os in matrix.get('os', [config.get('runs-on')]):
                instances.append({'workflow': name, 'job': job, 'os': os})
    check('all_12_native_instances', len(instances) == 12)
    spec = importlib.util.spec_from_file_location('reviewed_gate', PKG / 'check_push_head.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    final = '7' * 40
    entry = {'sha': final, 'message': 'Support ordinary stubs of contracted functions'}
    check('synthetic_same_tree_sibling', not gate.check_metadata(pins, final, TREE, [MAIN], [entry]))
    for directive in ['[skip ci]', '[CI SKIP]', '[no ci]', '[skip actions]', '[actions skip]',
                      'skip-checks: true', 'skip-checks:True']:
        check('reject_directive:' + directive,
              bool(gate.check_metadata(pins, final, TREE, [MAIN],
                                       [dict(entry, message=entry['message'] + '\n\n' + directive)])))
    for label, h, t, parents, entries in [
        ('candidate', HEAD, TREE, [MAIN], [dict(entry, sha=HEAD)]),
        ('tree_drift', final, '8' * 40, [MAIN], [entry]),
        ('skipped_parent', final, TREE, [HEAD], [entry]),
        ('merge', final, TREE, [MAIN, HEAD], [entry]),
        ('extra_range_commit', final, TREE, [MAIN], [entry, dict(entry, sha=HEAD)]),
        ('missing_range', final, TREE, [MAIN], []),
    ]:
        check('reject_head:' + label, bool(gate.check_metadata(pins, h, t, parents, entries)))

    # A compilation error cannot satisfy either semantic expected-output file.
    diagnostic = 'Failed to find contract closure `__kani_recursion_check_f`'
    for stem in ['ordinary_stub_fail', 'ordinary_stub_issue_4591']:
        expected = (SRC / 'tests/expected/function-contract' / (stem + '.expected')).read_text()
        check('compile_error_rejected:' + stem, not expected_matches(expected, diagnostic))
    expected = (SRC / 'tests/expected/function-contract/ordinary_stub_issue_4591.expected').read_text()
    synthetic = ('Check 1: ordinary_stub_issue_4591::caller.assertion.1\n'
                 ' - Status: FAILURE\n - Description: "attempt to add with overflow"\n'
                 'VERIFICATION:- FAILED\nVerification failed for - check_caller\n'
                 'Complete - 0 successfully verified harnesses, 1 failures, 1 total.\n')
    check('synthetic_issue_overflow_group_matches', expected_matches(expected, synthetic))
    check('synthetic_issue_success_rejected', not expected_matches(expected, synthetic.replace('FAILURE', 'SUCCESS')))
    check('synthetic_unrelated_overflow_rejected', not expected_matches(expected, synthetic.replace('caller.assertion', 'abs_val.assertion')))
    check('real_i32_overflow_arithmetic', (2**31 - 1) + 1 > 2**31 - 1)
    check('bounded_u8_distinguishes_body', all(x + 2 < 256 and x + 2 != x + 1 for x in range(9)))

    # Static finding: provider wrapper identity is absent from these harnesses.
    # These checks establish the source premises, not native compilation results.
    findings = []
    for path, harness, provider in [
        ('tests/kani/FunctionContracts/ordinary_stub.rs', 'replacement_contract_target', 'contracted_replacement'),
        ('tests/expected/function-contract/ordinary_stub_fail.rs', 'replacement_provider_postcondition', 'bad_contract'),
    ]:
        text = (SRC / path).read_text()
        body = re.search(r'fn ' + harness + r'\(\) \{([^}]+)\}', text).group(1)
        check('finding_only_copied_provider:' + harness, 'f(' in body and provider + '(' not in body)
        findings.append({'path': path, 'harness': harness, 'pfc_target': provider,
                         'body': body.strip(), 'native': 'NOT_RUN',
                         'static_expected': 'PFC_TARGET_UNREACHABLE_COMPILATION_ERROR'})
    attrs = (SRC / 'kani-compiler/src/kani_middle/attributes.rs').read_text()
    middle = (SRC / 'kani-compiler/src/kani_middle/mod.rs').read_text()
    reach = (SRC / 'kani-compiler/src/kani_middle/reachability.rs').read_text()
    check('finding_exact_defid_reachability_guard', '!reachable_functions.contains(&def.def_id())' in attrs)
    check('finding_reachable_set_uses_function_defid', 'MonoItem::Fn(instance) => Some(instance.def.def_id())' in middle)
    check('finding_collector_keeps_original_item', 'self.collected.insert(to_visit.clone());' in reach
          and 'self.transformer.body_ref(self.tcx, instance)' in reach)
    print(json.dumps({'status': 'STATIC_CHECKS_PASS_WITH_BLOCKING_FINDING',
                      'package': PACKAGE, 'source': HEAD, 'tree': TREE, 'main': MAIN,
                      'checks': RESULTS, 'native_main': 'NOT_RUN', 'native_fixed': 'NOT_RUN',
                      'ci': 'NOT_RUN', 'native_job_instances': instances,
                      'finding_4591_w11_01': findings,
                      'limits': 'Source-level inspection and synthetic output/head metadata; no Rust typechecking, MIR execution or verifier result.'}, indent=2))


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
