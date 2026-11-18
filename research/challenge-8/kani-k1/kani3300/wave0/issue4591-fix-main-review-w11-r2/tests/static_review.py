#!/usr/bin/env python3
"""Independent bounded source/package review; no Rust tools or CI invocation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

import yaml

G0 = Path('/root/verify-rust-std-kani3300-g0')
SRC = Path('/root/kani-issue4591-fix-main-r2-w15')
REL = 'research/challenge-8/kani-k1/kani3300/wave0/issue4591-fix-main-r2'
PKG = G0 / REL
PACKAGE = 'ad50aaeaabe8b3a84dbf64a88d0214a16f4ee316'
HEAD = '3a770b5db51ba07acffce3483bde0901e6533f3a'
TREE = '7a3d5c05b5d663d515c198b2bfa7c4926ae133ac'
MAIN = '969f4648980a8e66cd0ca32fd3e714a55ac32cef'
MAIN_TREE = 'c9a832dc1647c51ac3036429e5f97e73eb717ba7'
OLD_MAIN = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
R1 = 'e6aa083da3c93f3189039077795cc9a0d67d3a6d'
ORIGINAL = 'a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a'
PRIOR_REVIEW = '54ea8a918b761dc67213f7f24ae5163b7f463b42'
RESULTS = []


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def check(name, ok):
    if not ok:
        raise AssertionError(name)
    RESULTS.append(name)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path, ref=HEAD):
    return git(SRC, 'show', ref + ':' + path).decode()


def functions(text):
    """Restricted fixture grammar; no Rust resolution/AST/MIR claim."""
    clean = re.sub(r'//[^\n]*', '', text)
    out = {}
    for m in re.finditer(r'^((?:#\[kani::[^\n]+\]\n)*)fn (\w+)[^\n{]*\{', clean, re.M):
        i, depth = m.end(), 1
        while depth:
            depth += (clean[i] == '{') - (clean[i] == '}')
            i += 1
        check('unique_fixture_function:' + m[2], m[2] not in out)
        out[m[2]] = (m[1].splitlines(), re.sub(r'\s+', '', clean[m.end():i - 1]))
    return out


def expected_matches(expected, output):
    """Compiletest substring groups, preserving adjacent lines joined by backslash."""
    groups, pending = [], []
    for line in expected.split('\n'):
        pending.append(line[:-1] if line.endswith('\\') else line)
        if not line.endswith('\\'):
            groups.append(pending)
            pending = []
    if pending:
        groups.append(pending)
    actual = output.split('\n')
    return all(any(all(token.strip() in got for token, got in zip(group, actual[i:]))
                   for i in range(len(actual) - len(group) + 1)) for group in groups)


def normalized(a, b):
    raw = git(SRC, 'diff', '--binary', '--full-index', a, b)
    return b'\n'.join(line for line in raw.splitlines() if not line.startswith(b'index ')) + b'\n'


def main():
    pins = json.loads((PKG / 'SOURCE-PINS.json').read_text())
    paths = git(G0, 'ls-tree', '-r', '--name-only', PACKAGE, REL).decode().splitlines()
    check('exact27_committed_package_files', len(paths) == 27)
    check('exact_package_file_set', {p.name for p in PKG.iterdir()} == {Path(p).name for p in paths})
    for path in paths:
        check('committed_bytes:' + Path(path).name, (G0 / path).read_bytes() == git(G0, 'show', PACKAGE + ':' + path))
    manifest = json.loads((PKG / 'MANIFEST.json').read_text())['files']
    check('exact26_manifest_entries', len(manifest) == 26 and set(manifest) == {Path(p).name for p in paths} - {'MANIFEST.json'})
    for name, record in manifest.items():
        data = (PKG / name).read_bytes()
        check('manifest:' + name, len(data) == record['bytes'] and sha(data) == record['sha256'])
    check('exact_ci_request', sha((PKG / 'CI-REQUEST.json').read_bytes()) == '50da6854da282d718e28ee93953cd5d27c0bf47b366f538248cd5f461b71fdbe')
    for ref, tree, parent in [(HEAD, TREE, MAIN), (MAIN, MAIN_TREE, OLD_MAIN), (R1, '01140856c15e161ff6fc4c1ce460fd4208a298cd', OLD_MAIN)]:
        check('object:' + ref, git(SRC, 'show', '-s', '--format=%T %P', ref).decode().strip() == tree + ' ' + parent)
    check('exact_worktree_head', git(SRC, 'rev-parse', 'HEAD').decode().strip() == HEAD)
    check('source_clean', not git(SRC, 'status', '--porcelain').strip())
    check('single_candidate_range', git(SRC, 'rev-list', MAIN + '..' + HEAD).decode().split() == [HEAD])
    check('exact_changed_scope', git(SRC, 'diff', '--name-only', MAIN, HEAD).decode().splitlines() == pins['changed_paths'])
    for path, record in pins['changed_files'].items():
        data = git(SRC, 'show', HEAD + ':' + path)
        check('source_blob:' + path, sha(data) == record['sha256'] and git(SRC, 'rev-parse', HEAD + ':' + path).decode().strip() == record['blob'] and data == (SRC / path).read_bytes())
    for path, tree in pins['protected_git_trees'].items():
        check('protected_tree:' + path, all(git(SRC, 'rev-parse', ref + ':' + path).decode().strip() == tree for ref in [MAIN, HEAD]))
    for path, digest in pins['protected_files_sha256'].items():
        check('protected_file:' + path, git(SRC, 'show', MAIN + ':' + path) == git(SRC, 'show', HEAD + ':' + path) and sha(git(SRC, 'show', HEAD + ':' + path)) == digest)
    check('identical_repaired_r1_delta', normalized(OLD_MAIN, R1) == normalized(MAIN, HEAD))
    check('all_upstream_hunks_preserved', normalized(OLD_MAIN, MAIN) == normalized(R1, HEAD))
    upstream_paths = git(SRC, 'diff', '--name-only', OLD_MAIN, MAIN).decode().splitlines()
    check('all31_upstream_paths', len(upstream_paths) == 31)
    for path in upstream_paths:
        if path != 'kani-compiler/src/kani_middle/transform/contracts.rs':
            check('upstream_bytes_preserved:' + path, git(SRC, 'show', MAIN + ':' + path) == git(SRC, 'show', HEAD + ':' + path))
    for path in pins['test_paths']:
        check('all8_fixtures_equal_r1:' + path, source(path) == source(path, R1))
    # Independent exact Git replay, isolated indexes only. Candidate index/worktree untouched.
    replays = []
    for names in [('full-main.patch',), ('fix.patch', 'regression-main.patch'), ('../issue4591-fix-r1/full-main.patch',)]:
        with tempfile.TemporaryDirectory(prefix='w11-r2-index-') as temp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
            git(SRC, 'read-tree', MAIN, env=env)
            for name in names:
                git(SRC, 'apply', '--cached', '--check', str(PKG / name), env=env)
                git(SRC, 'apply', '--cached', str(PKG / name), env=env)
            tree = git(SRC, 'write-tree', env=env).decode().strip()
            check('replay:' + ','.join(names), tree == TREE)
            replays.append({'patches': names, 'tree': tree})
    # Every original function except the two repair harnesses is unchanged.
    texts = {path: source(path) for path in pins['test_paths'] if path.endswith('.rs')}
    parsed = {path: functions(text) for path, text in texts.items()}
    pos = 'tests/kani/FunctionContracts/ordinary_stub.rs'
    neg = 'tests/expected/function-contract/ordinary_stub_fail.rs'
    for path, text in texts.items():
        old = functions(source(path, ORIGINAL))
        for name, value in old.items():
            if name not in ('replacement_contract_target', 'replacement_provider_postcondition'):
                check('original_control_preserved:' + path + ':' + name, parsed[path][name] == value)
        check('no_other_fixture_additions:' + path, set(parsed[path]) - set(old) == ({'discriminating_replacement'} if path == neg else set()))
    check('positive_unconditional_calls', parsed[pos]['replacement_contract_target'][1] == 'contracted_replacement(0);f(kani::any());')
    check('negative_unconditional_calls', parsed[neg]['replacement_provider_postcondition'][1] == 'discriminating_replacement(0);f(1);')
    check('negative_provider_identity_post', parsed[neg]['discriminating_replacement'] == (['#[kani::ensures(|result| *result == 0)]'], 'x'))
    check('direct0_pass_copied1_fail', 0 == 0 and 1 != 0)
    check('positive_domain_and_post', all(x + 3 < 256 for x in range(16)))
    selected, actual_harnesses = [], {}
    for path, funcs in parsed.items():
        for name, (attrs, body) in funcs.items():
            if '#[kani::proof]' in attrs or any(a.startswith('#[kani::proof_for_contract(') for a in attrs):
                actual_harnesses[path, name] = attrs
            for attr in attrs:
                match = re.fullmatch(r'#\[kani::proof_for_contract\((\w+)\)\]', attr)
                if match:
                    target = match[1]
                    check('each_pfc_target_local_definition:' + path + ':' + name, target in funcs)
                    check('each_pfc_own_direct_call:' + path + ':' + name, re.search(r'(?<![\w:])' + target + r'\(', body) is not None)
                    selected.append({'path': path, 'harness': name, 'target': target, 'source_call': body, 'assurance': 'SOURCE_RESOLUTION_REVIEW_NOT_COMPILER_DEFINITION_ID_MEASUREMENT'})
    oracle = json.loads((PKG / 'REGRESSION-ORACLE.json').read_text())
    check('complete38_oracle', len(actual_harnesses) == len(oracle['harnesses']) == 38 and set(actual_harnesses) == {(r['path'], r['harness']) for r in oracle['harnesses']})
    check('oracle_attributes_and_not_run', all(r['attributes'] == actual_harnesses[r['path'], r['harness']] and r['main_new_native'] == r['fixed_new_native'] == 'NOT_RUN' for r in oracle['harnesses']))
    check('oracle_exact_new_objects', oracle['source_head'] == HEAD and oracle['source_tree'] == TREE and oracle['main'] == pins['main'])
    module = source('kani-compiler/src/kani_middle/transform/mod.rs')
    stubs = source('kani-compiler/src/kani_middle/transform/stubs.rs')
    contracts = source('kani-compiler/src/kani_middle/transform/contracts.rs')
    attrs = source('kani-compiler/src/kani_middle/attributes.rs')
    reach = source('kani-compiler/src/kani_middle/reachability.rs')
    check('exact_defid_guard_retained', '!reachable_functions.contains(&def.def_id())' in attrs and attrs == source('kani-compiler/src/kani_middle/attributes.rs', MAIN))
    check('reachable_function_identity', 'MonoItem::Fn(instance) => Some(instance.def.def_id())' in source('kani-compiler/src/kani_middle/mod.rs'))
    check('collector_keeps_requested_identity', 'self.collected.insert(to_visit.clone());' in reach and 'self.transformer.body_ref(self.tcx, instance)' in reach)
    check('each_harness_separate_root', '&[MonoItem::Fn(*harness)]' in source('kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs'))
    check('checked_provider_exact_item', '== function_under_contract' in source('kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs'))
    check('body_source_reset_and_consumed', 'self.body_source = None;' in stubs and 'self.body_source.take()' in stubs and 'let mut body_source = instance;' in module)
    check('source_only_after_validation', re.search(r'if let Some\(body\) = FnStubValidator::validate[^\n]+\{\n\s*self.body_source = Some\(new_instance\);\n\s*return \(true, body\);', stubs) is not None)
    check('explicit_target_precedence', 'self.check_fn == Some(*def) || self.replace_fns.contains(def)' in contracts)
    check('contract_modes_unchanged', contracts[contracts.index('    fn contract_mode('):] == source('kani-compiler/src/kani_middle/transform/contracts.rs', MAIN)[source('kani-compiler/src/kani_middle/transform/contracts.rs', MAIN).index('    fn contract_mode('):])
    check('stub_validation_unchanged', stubs[stubs.index('fn has_body('):] == source('kani-compiler/src/kani_middle/transform/stubs.rs', MAIN)[source('kani-compiler/src/kani_middle/transform/stubs.rs', MAIN).index('fn has_body('):])
    check('only_contract_pass_selects_source', git(SRC, 'grep', '-l', 'fn transform_instance', HEAD, '--', 'kani-compiler').decode().splitlines() == [HEAD + ':kani-compiler/src/kani_middle/transform/contracts.rs', HEAD + ':kani-compiler/src/kani_middle/transform/mod.rs'])
    # Semantic expected-output groups cannot be satisfied by a compilation failure.
    diagnostic = 'Failed to find contract closure `__kani_recursion_check_f`'
    for stem in ['ordinary_stub_fail', 'ordinary_stub_issue_4591']:
        expected = source('tests/expected/function-contract/' + stem + '.expected')
        check('reject_compile_error:' + stem, not expected_matches(expected, diagnostic))
    expected = source('tests/expected/function-contract/ordinary_stub_issue_4591.expected')
    synthetic = ('Check 1: ordinary_stub_issue_4591::caller.assertion.1\n'
                 ' - Status: FAILURE\n - Description: "attempt to add with overflow"\n'
                 'VERIFICATION:- FAILED\nVerification failed for - check_caller\n'
                 'Complete - 0 successfully verified harnesses, 1 failures, 1 total.\n')
    check('issue_caller_overflow_matches', expected_matches(expected, synthetic))
    check('issue_fake_success_rejected', not expected_matches(expected, synthetic.replace('FAILURE', 'SUCCESS')))
    check('issue_unrelated_overflow_rejected', not expected_matches(expected, synthetic.replace('caller.assertion', 'abs_val.assertion')))
    check('real_i32_overflow', 2**31 - 1 + 1 > 2**31 - 1)
    issue_body = json.loads((PKG / 'ISSUE-4591.json').read_text())['issue']['issue']['body'].split('```rust\n', 1)[1].split('```', 1)[0].strip()
    check('verbatim_issue_source', texts['tests/expected/function-contract/ordinary_stub_issue_4591.rs'].split('#[kani::ensures', 1)[1].strip() == issue_body.split('#[kani::ensures', 1)[1].strip())
    neg_expected = source('tests/expected/function-contract/ordinary_stub_fail.expected')
    check('unique_discriminating_post_oracle', neg_expected.count('- Description: "|result| *result == 0"') == 1)
    addition = 'assertion\\\n- Status: FAILURE\\\n- Description: "|result| *result == 0"\n\n'
    check('every_old_negative_expected_group_preserved', neg_expected.replace(addition, '') == source('tests/expected/function-contract/ordinary_stub_fail.expected', ORIGINAL))
    check('negative_all11_named_failures', len(re.findall(r'^Verification failed for - ', neg_expected, re.M)) == 11 and 'Complete - 2 successfully verified harnesses, 11 failures, 13 total.' in neg_expected)
    ci = json.loads((PKG / 'CI-REQUEST.json').read_text())
    inventory = json.loads((PKG / 'WORKFLOW-INVENTORY.json').read_text())['workflows']
    workflow_paths = git(SRC, 'ls-tree', '-r', '--name-only', MAIN, '.github/workflows').decode().splitlines()
    workflows = {Path(p).name: yaml.load(source(p, MAIN), Loader=yaml.BaseLoader) for p in workflow_paths}
    check('all16_native_workflows', len(workflows) == 16 and set(workflows) == set(inventory))
    push = []
    for name, workflow in workflows.items():
        check('actual_workflow:' + name, all(workflow.get(k) == inventory[name][k] for k in ['on', 'jobs', 'name', 'concurrency']))
        event = workflow.get('on', {}).get('push')
        if isinstance(event, dict) and '**' in event.get('branches', []):
            push.append(name)
            check('all_native_jobs:' + name, workflow['jobs'] == ci['native_jobs'][name])
    check('independent_branch_push_event_set', sorted(push) == sorted(ci['workflow_files']) == ['deny.yml', 'format-check.yml', 'kani.yml'])
    instances = []
    for name in push:
        for job, config in workflows[name]['jobs'].items():
            for system in config.get('strategy', {}).get('matrix', {}).get('os', [config.get('runs-on')]):
                instances.append({'workflow': name, 'job': job, 'os': system})
    check('all12_native_instances', len(instances) == 12)
    check('all5_os', workflows['kani.yml']['jobs']['regression']['strategy']['matrix']['os'] == ['macos-15-intel', 'ubuntu-22.04', 'ubuntu-24.04', 'macos-15', 'ubuntu-24.04-arm'])
    script = source('scripts/kani-regression.sh')
    check('native_full_suites', '"kani kani"' in script and '"expected expected"' in script and './scripts/kani-regression.sh' in json.dumps(workflows['kani.yml']))
    spec = importlib.util.spec_from_file_location('reviewed_publication_gate', PKG / 'check_push_head.py')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    final = '7' * 40
    entry = {'sha': final, 'message': 'Support ordinary stubs of contracted functions'}
    check('synthetic_valid_sibling', not gate.check_metadata(pins, final, TREE, [MAIN], [entry]))
    for directive in ['[skip ci]', '[CI SKIP]', '[no ci]', '[skip actions]', '[actions skip]', 'skip-checks: true', 'skip-checks:True']:
        check('reject_skip:' + directive, bool(gate.check_metadata(pins, final, TREE, [MAIN], [dict(entry, message=entry['message'] + '\n\n' + directive)])))
    for label, head, tree, parents, entries in [
        ('candidate', HEAD, TREE, [MAIN], [dict(entry, sha=HEAD)]),
        ('main', MAIN, TREE, [OLD_MAIN], [dict(entry, sha=MAIN)]),
        ('tree_drift', final, '8' * 40, [MAIN], [entry]),
        ('candidate_parent', final, TREE, [HEAD], [entry]),
        ('old_parent', final, TREE, [OLD_MAIN], [entry]),
        ('old_source_parent', final, TREE, [R1], [entry]),
        ('old_tree', final, '01140856c15e161ff6fc4c1ce460fd4208a298cd', [MAIN], [entry]),
        ('merge_parent', final, TREE, [MAIN, HEAD], [entry]),
        ('extra_range', final, TREE, [MAIN], [entry, dict(entry, sha=HEAD)]),
        ('empty_range', final, TREE, [MAIN], []),
    ]:
        check('reject_final:' + label, bool(gate.check_metadata(pins, head, tree, parents, entries)))
    check('future_head_not_created', pins['future_final_head']['sha'] == 'NOT_CREATED' and pins['future_final_head']['parent'] == MAIN and pins['future_final_head']['tree'] == TREE)
    check('source_still_clean', not git(SRC, 'status', '--porcelain').strip())
    print(json.dumps({'status': 'INDEPENDENT_STATIC_AND_MOCK_PASS', 'package': PACKAGE, 'source': HEAD, 'tree': TREE, 'main': MAIN, 'main_tree': MAIN_TREE, 'prior_review': PRIOR_REVIEW,
                      'checks': RESULTS, 'check_count': len(RESULTS), 'replays': replays, 'selected_pfc_targets': selected,
                      'native_job_instances': instances, 'normalized_delta_sha256': sha(normalized(MAIN, HEAD)), 'normalized_upstream_sha256': sha(normalized(OLD_MAIN, MAIN)),
                      'W11-01': 'CLOSED_SOURCE_REVIEW', 'native_main': 'NOT_RUN', 'native_fixed': 'NOT_RUN', 'typechecking': 'NOT_RUN', 'ci': 'NOT_RUN',
                      'limit': 'Source-level reasoning, Git replay/hash checks and synthetic metadata/output only; no measured compiler FnDef/MIR or proof credit.'}, indent=2))


if __name__ == '__main__':
    main()
