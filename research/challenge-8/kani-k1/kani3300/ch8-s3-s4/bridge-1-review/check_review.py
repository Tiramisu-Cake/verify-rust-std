#!/usr/bin/env python3
"""Independent immutable bridge1 consistency/source review; never native tools."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
CANDIDATE = 'bcc103354d1418feeda043c6b955b38bb4393598'
TASK = 'e060dab687785f64560a5a563b0689c04d68a215'
PREFIX = 'research/challenge-8/kani-k1/kani3300/ch8-s3-s4/bridge-1/'
CHECKS = []


def git(repo, *args, env=None, data=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, input=data)


def blob(repo, rev, name):
    return git(repo, 'show', rev + ':' + name)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(name):
    return json.loads(blob(REPO, CANDIDATE, PREFIX + name))


def need(condition, label):
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def main():
    pins = read('PINS.json')
    request = read('CI-REQUEST.json')
    tracked = git(REPO, 'ls-tree', '-r', '--name-only', CANDIDATE, PREFIX).decode().splitlines()
    manifest = {}
    for line in blob(REPO, CANDIDATE, PREFIX + 'MANIFEST.sha256').decode().splitlines():
        digest, name = line.split('  ', 1)
        need(name not in manifest and sha(blob(REPO, CANDIDATE, PREFIX + name)) == digest, 'candidate manifest ' + name)
        manifest[name] = digest
    need(len(tracked) == 44 and len(manifest) == 43, 'candidate44files43manifest hashes')
    need(set(tracked) == {PREFIX + n for n in manifest} | {PREFIX + 'MANIFEST.sha256'}, 'manifest exact inventory')
    identity = {}
    for kind in ['source', 'control', 'tool']:
        v = pins[kind]
        repo = Path(v['worktree'])
        need(git(repo, 'rev-parse', v['sha'] + '^{tree}').decode().strip() == v['tree'], kind + ' exact tree')
        need(git(repo, 'show', '-s', '--format=%P', v['sha']).decode().strip().split() == v['parents'], kind + ' exact parents')
        ancestors = git(repo, 'rev-list', '--max-count=' + str(v['depth']), v['sha']).decode().splitlines()
        need(set(v['required_commits_available']) <= set(ancestors), kind + ' depth required ancestor path')
        need(git(repo, 'rev-parse', 'HEAD').decode().strip() == v['sha'], kind + ' current HEAD still exact')
        need(not git(repo, 'status', '--porcelain=v1', '--untracked-files=no').strip(), kind + ' tracked worktree clean')
        identity[kind] = {'sha': v['sha'], 'tree': v['tree'], 'parents': v['parents'], 'depth': v['depth'], 'ancestors': ancestors}
    source = Path(pins['source']['worktree'])
    control = Path(pins['control']['worktree'])
    sr = pins['source']['sha']
    cr = pins['control']['sha']
    need(blob(control, cr, 'ch8-s1-control/CI-REQUEST.json') == blob(REPO, CANDIDATE, PREFIX + 'CI-REQUEST.json'), 'canonical request package/control equal')
    need(sha(blob(control, cr, 'ch8-s1-control/CI-REQUEST.json')) == pins['request']['sha256'], 'exact request hash')
    need(blob(control, cr, '.github/workflows/ch8-s2.yml') == blob(REPO, CANDIDATE, PREFIX + 'WORKFLOW.yml'), 'canonical workflow package/control equal')
    need(sha(blob(control, cr, '.github/workflows/ch8-s2.yml')) == pins['request']['workflow_sha256'], 'exact workflow hash')
    need(request['std_sha'] == sr and request['std_tree'] == pins['source']['tree'] and request['tool_sha'] == pins['tool']['sha'] and request['tool_tree'] == pins['tool']['tree'], 'operative source/tool full pins')
    deps = read('DEPENDENCIES.json')
    for name, entry in deps['source'].items():
        need(entry['source_sha'] == sr and sha(blob(source, sr, name)) == entry['sha256'], '39source dependency ' + name)
    for entry in deps['authored_inputs']:
        need(sha(blob(REPO, entry['commit'], entry['path'])) == entry['sha256'], 'authored committed dependency ' + entry['path'])
    need(len(deps['source']) == 39 and len(deps['authored_inputs']) == 66, '39source66committed dependency counts')
    for name, digest in request['ci_payload_sha256'].items():
        need(sha(blob(control, cr, name)) == digest, 'control payload ' + name)
    need(len(request['ci_payload_sha256']) == 100, '100control payload files')
    actual_delta = git(control, 'diff', '--name-only', pins['tool']['sha'], cr).decode().splitlines()
    need(actual_delta == request['ci_changed_paths'], 'exact100payload117delta16deleted')
    need(set(request['ci_payload_sha256']) == set(actual_delta) - set(request['ci_deleted_paths']) - {'ch8-s1-control/CI-REQUEST.json'}, 'request selfhash exclusion only')
    preserved = read('PRESERVATION.json')
    for name, digest in preserved['protected_python_exact_bytes'].items():
        need(sha(blob(control, cr, name)) == digest and blob(control, cr, name) == blob(control, pins['control']['reference'], name), '58protected old bytes ' + name)
    need(len(preserved['protected_python_exact_bytes']) == 58, '58protected files')
    source_delta = git(source, 'diff', '--name-only', pins['source']['reference'], sr).decode().splitlines()
    leaf = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_bridge1.rs'
    wire = 'library/core/src/slice/sort/shared/smallsort/verify.rs'
    need(source_delta == [wire, leaf], 'source delta only wiring and new module')
    need(blob(source, sr, wire).startswith(blob(source, pins['source']['reference'], wire)), 'old verify exact prefix')
    for cite in read('SOURCE-CITATIONS.json')['ranges']:
        b = blob(source, sr, cite['file'])
        ls = b.decode().splitlines()
        need(sha(b) == cite['file_sha256'] and sha(('\n'.join(ls[cite['start_line']-1:cite['end_line']]) + '\n').encode()) == cite['range_sha256'], 'current source citation ' + cite['file'] + ':' + str(cite['start_line']))
    expected_order = ['checker_order_corrupt', 'checker_count_corrupt', 'sort13_weak', 'i_p01_b01_fullu8', 'sort9_v34_b01_len09_real', 'fallback_cell_b01_n00_16', 'network_u8_b01_n00_08']
    need([r['id'] for r in request['rows']] == pins['ordered_rows'] == expected_order, 'exact selected7 priority')
    need([r['mode'] for r in request['rows']] == ['Original']*3 + ['PFC'] + ['Original']*3, 'only insertion PFC')
    need([r['target'] for r in request['rows']] == [None]*3 + ['insert_tail'] + [None]*3, 'Original targets null')
    need([r['unwind'] for r in request['rows']] == [34]*3 + [36]*4, 'exact source-counted unwind')
    role_rows = []
    for index, r in enumerate(request['rows']):
        rid = r['id']
        binding = request['source_bindings'][rid]
        need(binding['selector'] == r['selector'] and binding['mode'] == r['mode'] and binding['target'] == r['target'], rid + ' source binding mode/target')
        b = blob(source, sr, binding['file'])
        ls = b.decode().splitlines()
        need(sha(b) == binding['sha256'], rid + ' source exact hash')
        for role in r['roles']:
            need(role['source_sha256'] == sha(b) and ls[role['line']-1] == role['source_line'] and
                 'kani::' + ('cover' if role['class'] == 'cover' else 'assert') + '(' in role['source_line'] and
                 role['status'] == ('SATISFIED' if role['class'] == 'cover' else 'FAILURE' if index < 3 else 'SUCCESS'), rid + ' literal role ' + role['description'])
        if index >= 3:
            need(len(r['required_success_messages']) == 4, rid + ' derive four actual assertion roles')
        need(not r['scope_classification']['eligible_as_init_leaf_or_provider_summary'], rid + ' no init/provider scope promotion')
        role_rows.append({'id': rid, 'mode': r['mode'], 'target': r['target'], 'selector': r['selector'], 'unwind': r['unwind'], 'assertion_roles': len(r['roles'])-r['required_cover_count'], 'cover_sites': r['required_cover_count'], 'roles': r['roles'], 'native_properties': 'UNKNOWN_NOT_RUN'})
    text = blob(source, sr, leaf).decode()
    need(text.count('#[kani::proof_for_contract(') == 1 and text.count('#[kani::proof]') == 3 and '#[kani::stub' not in text, 'all positive roots real bodies no replacement')
    for prefix, count in [('B1_F_N', 17), ('B1_N_N', 9)]:
        for n in range(count):
            need(f'kani::cover(n == {n}, "{prefix}{n:02}");' in text, 'each symbolic source length ' + prefix + str(n))
    need('let bytes: [u8; 34] = kani::any();' in text and 'for i in 0..34 { v[i].set(bytes[i]); }' in text and 'enabled::<Cell<u8>, KeyLess<Cell<u8>>>()' in text, 'Cell arbitrary wholelogical bytes and main model active')
    model = blob(source, sr, 'library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs').decode()
    need('active_model!(Cell<u8>);' in model and 'fn value(&self) -> u8 { self.get() }' in model and 'a.value() < b.value()' in model, 'Cell enabled model and pure fullvalue comparator')
    need(not any(x in text for x in ['is_initialized(', 'assume(ordered', '% 2', '& 1', 'stub_verified']), 'no initialization oracle or reduced value domain')
    need(request['unreachable_admission'] == {'mode': 'REJECT_ALL', 'proposal': 'S3-U-SITE-REVIEW-v1', 'enabled': False, 'unknown': 'REJECT', 'role_unreachable': 'REJECT'}, 'strict U disabled proposal no prior transfer')
    caps = request['s3']['caps']
    need(caps == pins['caps'] and 7*caps['slot_seconds'] + caps['controller_seconds'] + caps['cleanup_seconds'] == 5460 <= caps['campaign_seconds'], '7slot oneclock envelope exact')
    need((caps['local_rss_kib'], caps['outer_rss_kib'], caps['headroom_kib'], caps['child_seconds'], caps['compile_seconds']) == (6291456, 12582912, 2097152, 600, 180), 'caps unchanged and compile inside child')
    validation = read('VALIDATION.json')
    final = read('validation/final-validate.json')
    stdout = json.loads(blob(REPO, CANDIDATE, PREFIX + validation['stdout']))
    need(stdout == validation['result'] and stdout['control_sha'] == cr and stdout['control_tree'] == pins['control']['tree'] and stdout['request_sha256'] == pins['request']['sha256'], 'exact final stdout identity')
    need(sum(stdout[k] for k in ['legacy_tests', 'protected_s3_1_tests', 'protected_s3_2_tests', 'bridge1_tests']) == 263 and stdout['errors'] == stdout['failures'] == 0 and stdout['success'], '263tests success receipt')
    need(final['exit_code'] == 0 and final['control_sha'] == cr and final['head_after'] == cr and final['tracked_clean'] and final['tracked_clean_after'], 'final exact clean control receipt')
    need(validation['actual_final_validate_execution_count'] == 1 and final['elapsed_seconds'] == validation['elapsed_seconds'] and final['margin_at_18_minutes'] == 1080/final['elapsed_seconds'] >= 1.5, 'once619.250440s margin1.744 source receipt')
    stderr = blob(REPO, CANDIDATE, PREFIX + validation['stderr']).decode()
    need(stderr.count(' ... ok') == 263 and not re.search(r'^FAILED|^ERROR:|^FAIL:', stderr, re.M), '263 individual test statuses retained')
    for key in ['source_preflight', 'control_preflight']:
        rec = validation[key]
        need(rec['exit_code'] == 0 and rec['control_sha'] == cr and rec['head_after'] == cr and rec['tracked_clean'] and rec['tracked_clean_after'], key + ' exact clean identity')
    patches = []
    with tempfile.TemporaryDirectory(prefix='w14-bridge1-static-') as td:
        tmp = Path(td)
        for index, patch in enumerate(read('PATCHES.json')):
            repo = source if patch['file'].startswith('SOURCE-') else control
            b = blob(REPO, CANDIDATE, PREFIX + patch['file'])
            need(sha(b) == patch['sha256'], 'patch exact bytes ' + patch['file'])
            env = dict(os.environ, GIT_INDEX_FILE=str(tmp / ('index-' + str(index))))
            git(repo, 'read-tree', patch['base'], env=env)
            git(repo, 'apply', '--cached', '--whitespace=nowarn', '-', env=env, data=b)
            tree = git(repo, 'write-tree', env=env).decode().strip()
            need(tree == patch['expected_tree'] == patch['replayed_tree'], 'independent patch tree ' + patch['file'])
            patches.append({'file': patch['file'], 'base': patch['base'], 'tip': patch['tip'], 'tree': tree, 'status': 'PASS'})
        need(len(patches) == 6, 'six independent index patch tree replays')
        ctrl = tmp / 'control'
        std = tmp / 'source'
        ctrl.mkdir(); std.mkdir()
        for name in git(control, 'ls-tree', '-r', '--name-only', cr, 'ch8-s1-control').decode().splitlines():
            target = ctrl / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(control, cr, name))
        for name in deps['source']:
            target = std / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(source, sr, name))
        sys.path.insert(0, str(ctrl / 'ch8-s1-control'))
        policy = importlib.import_module('s34_policy')
        report = policy.validate_source(std, request)
        need(report['status'] == 'STATIC_PASS' and all(x['status'] == 'STATIC_PASS' for x in report['reports'].values()), 'independent frozen source4 gates PASS')
        cfg = report['reports']['cfg_pfc']
        lexical = report['reports']['lexical']
        need({x['function'] for x in lexical['functions']} >= set(read('CFG-DEPENDENCY.json')['all_new_functions']), 'all6 new functions bounded lexical inventory')
        need(len(cfg['rows']) == 7 and not cfg['qualification_from_registration'], 'cfg maps7 contexts no credit')
        gate_summary = {k: {'status': v['status'], 'source_sha': v.get('source_sha'), 'files': len(v['source_files_sha256']), 'limits': v.get('limits', [])} for k, v in report['reports'].items()}
        write('SOURCE-GATES.json', {'status': 'PASS', 'source': sr, 'control': cr, 'gates': gate_summary, 'all_new_functions': read('CFG-DEPENDENCY.json')['all_new_functions'], 'Cell_provider': lexical['concrete_cell_method_provider'], 'production_paths': lexical['required_production_fragments'], 'proof_credit': 'NONE', 'scope': 'Bounded source/static parser only; no compiler/type/MIR resolution'})
    write('IDENTITY-REVIEW.json', {'task': TASK, 'candidate': CANDIDATE, 'identities': identity, 'manifest_files': 43, 'tracked_files': 44, 'source_dependency_files': 39, 'authored_dependency_files': 66, 'protected_files': 58, 'payload_files': 100, 'request_sha256': pins['request']['sha256'], 'workflow_sha256': pins['request']['workflow_sha256'], 'patch_replays': patches, 'validation': validation, 'native_or_fullValidate_rerun': False})
    write('ROW-REVIEW.json', {'rows': role_rows, 'source_assertion_sites': sum(r['assertion_roles'] for r in role_rows), 'source_cover_sites': sum(r['cover_sites'] for r in role_rows), 'native_counts': 'UNKNOWN_NOT_RUN', 'SAT_and_proof_credit': 'NONE'})
    write('STATIC-VALIDATION.json', {'status': 'PASS', 'checks': CHECKS, 'count': len(CHECKS), 'scope': 'Integrity, exact pins, preservation, source-only4gates, six Git patch trees; separate reproduced cardinality blocker remains open'})
    print(json.dumps({'status': 'PASS', 'static_checks': len(CHECKS), 'patches': len(patches), 'rows': 7, 'native_run': False, 'known_count_gate_blocker': 'OPEN'}))


if __name__ == '__main__':
    main()
