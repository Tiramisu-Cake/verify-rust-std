#!/usr/bin/env python3
"""Bounded pure-Python replay of retained compact evidence and count policy."""
import ast
import collections
import copy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def oracle(override=False):
    tree = ast.parse((HERE / 'frozen-runner.py').read_text())
    functions = {'canonical', 'require', 'valid_process', 'success', 'observe', 'classify'}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in functions]
    # Replace precisely the named count predicate; keep all later guards intact.
    if override:
        for node in nodes:
            if node.name == 'success':
                for n in ast.walk(node):
                    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                            and n.func.id == 'require' and len(n.args) == 2
                            and isinstance(n.args[1], ast.Constant) and n.args[1].value == 'check counts'):
                        n.args[0] = ast.parse("type(count) is int and 0 < count <= 256 and type(entry['n_properties']) is int and entry['n_properties'] == count and type(checks['success']) is int and 0 <= checks['success'] <= count", mode='eval').body
    namespace = {'re': re, 'SLOTS': {'provider': ('provider', 'provider'), 'verified': ('verified', 'verified_control'), 'ordinary': ('ordinary', 'ordinary_stub')},
                 'MISSING': re.compile(r'^error: Failed to find contract closure `__kani_recursion_check_f` in function `(?:stub_contract_confirm::)?f`$'),
                 'UNSUPPORTED': 'error: ordinary stubbing of contracted function `stub_contract_confirm::f` is unsupported; use `kani::stub_verified` to use its contract'}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), 'frozen-pure-oracle', 'exec'), namespace)
    return namespace


STRICT = oracle()
COUNT = oracle(True)


def retained_observation(slot, record, count_override=False):
    inv = record.get('export_inventory')
    if not isinstance(inv, dict) or type(inv.get('present')) is not bool or type(inv.get('complete')) is not bool:
        return {'outcome': 'INCONCLUSIVE', 'reason': 'missing/invalid export presence metadata'}
    if inv['present'] and (type(inv.get('bytes')) is not int or not 0 < inv['bytes'] <= 2 * 1024 * 1024
                           or not isinstance(inv.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', inv['sha256'])):
        return {'outcome': 'INCONCLUSIVE', 'reason': 'invalid/oversized export inventory'}
    doc = record.get('export', record.get('observation', {}).get('export'))
    if inv['present'] and (not inv['complete'] or not isinstance(doc, dict)):
        return {'outcome': 'INCONCLUSIVE', 'reason': 'present export incomplete/null/invalid/unretained'}
    if not inv['present'] and (inv['complete'] or doc is not None):
        return {'outcome': 'INCONCLUSIVE', 'reason': 'inconsistent absent export'}
    return (COUNT if count_override else STRICT)['observe'](slot, record['process'], doc)


def synthetic():
    p = {'termination': 'EXITED', 'exit': 0, 'signal': None, 'diagnostics': [], 'diagnostics_complete': True,
         'streams': {'stdout': {'complete': True}, 'stderr': {'complete': True}}, 'verification_success': 1,
         'property_inventory': {'verified_control': [
             {'index': 1, 'id': 'a', 'status': 'SUCCESS', 'description': 'assertion failed: f(x) == x + 1', 'location': 'src/lib.rs:26:5 in function verified_control'},
             {'index': 2, 'id': 'b', 'status': 'SUCCESS', 'description': 'safety check', 'location': 'src/lib.rs:26:5 in function verified_control'}]}}
    checks = {k: True for k in ['memory_safety', 'overflow', 'unwinding', 'undefined_function', 'assertion_reach_checks']}
    checks.update(prove_safety_only=False, ignore_global_asm=False)
    doc = {'schema_version': '0.1.0', 'run_state': 'COMPLETE', 'outcome': {'kind': 'COMPLETED'},
           'target': 'x86_64-unknown-linux-gnu', 'enabled_unstable_features': ['function-contracts', 'stubbing', 'export-json'],
           'harness_selection': {'exact': True, 'requested_filters': ['verified_control'], 'unmatched_filters': [], 'matched_count': 1},
           'configuration': {'coverage_enabled': False, 'cbmc_args': [], 'checks': checks},
           'harnesses': [{'name': 'verified_control', 'outcome': {'kind': 'COMPLETED', 'verdict': 'SUCCESS'},
                          'is_automatically_generated': False, 'is_bounded': False, 'n_properties': 2, 'n_failed': 0,
                          'failed_properties': [], 'unsupported_constructs': [], 'covers': {'total': 0},
                          'checks': dict(total=2, success=1, **{k: [] for k in ['failure', 'unreachable', 'undetermined', 'error', 'unknown', 'other']})}]}
    return {'export_inventory': {'present': True, 'complete': True, 'bytes': len(json.dumps(doc).encode()),
                                 'sha256': hashlib.sha256(json.dumps(doc).encode()).hexdigest()}, 'export': doc, 'process': p}


def main():
    v, inp, profile = read('result.json'), read('INPUTS.json'), read('frozen-profile.json')
    validations = {}
    def check(name, condition):
        assert condition, name
        validations[name] = True
    check('result_bytes_digest', hashlib.sha256((HERE/'result.json').read_bytes()).hexdigest() == read('artifact-integrity.json')['result_sha256'])
    payload = {k: val for k, val in v.items() if k != 'integrity'}
    check('canonical_payload', digest(payload) == v['integrity']['canonical_payload_sha256'])
    check('profile_digest', hashlib.sha256((HERE/'frozen-profile.json').read_bytes()).hexdigest() == inp['profile_sha256'])
    check('frozen_oracle_digest', hashlib.sha256((HERE/'frozen-runner.py').read_bytes()).hexdigest() == profile['control_sha256']['tests/script-based-pre/stub-contract-confirm/runner.py'])
    native = read('native-run.json')
    check('native_terminal_identity', native['id'] == inp['run_id'] and native['run_attempt'] == inp['attempt'] and native['status'] == 'completed' and native['conclusion'] == 'failure' and native['head_sha'] == inp['head'] and native['head_branch'] == inp['branch'] and native['event'] == inp['event'] and native['head_commit']['tree_id'] == inp['tree'])
    expected_files = {scope+'/'+p: h for scope in ['source_sha256', 'control_sha256'] for p,h in profile[scope].items()}
    for phase in ['preflight', 'build_preflight', 'source_before', 'source_after']:
        s = v[phase]
        check(phase+'_identity', s['problems'] == [] and s['source']['head'] == inp['stock']['head'] and s['source']['tree'] == inp['stock']['tree'] and s['source']['parent'] == inp['stock']['parent'] and s['control']['head'] == inp['head'] and s['control']['tree'] == inp['tree'] and s['control']['parent'] == inp['parent'])
        check(phase+'_request_files', s['files'] == expected_files and s['request_sha256'] == inp['request_sha256'] == digest(s['request']) and s['request']['profile_sha256'] == inp['profile_sha256'])
        check(phase+'_push', s['push']['head'] == inp['head'] and s['push']['ref'] == 'refs/heads/'+inp['branch'] and s['push']['repository'] == inp['repository'] and s['push']['event'] == 'push')
    check('tool_stability', v['source_before']['tools'] == v['source_after']['tools'] and set(v['source_before']['tools']) == {'cargo', 'rustc', 'cbmc', 'kani-driver', 'kani-compiler'})
    for tool in ['kani-driver','kani-compiler']:
        check(tool+'_separate_stock_path', '/stock/target/kani/bin/' in v['source_before']['tools'][tool]['path'])
    STRICT['valid_process'](v['build'])
    check('setup_build', v['setup'] == 'SUCCESS' and v['setup_action_outcome'] == 'success' and v['build']['exit'] == 0 and v['build']['signal'] is None and v['build']['argv'] == ['cargo','build-dev'] and v['build']['cwd'].endswith('/stock'))
    targets = set()
    slot_results = {}
    for slot, name in [('provider','provider'), ('verified','verified_control'), ('ordinary','ordinary_stub')]:
        s = v['slots'][slot]; p = s['process']; a = p['argv']; ident = p['invocation_identity']
        source = v['source_before']['tools']['kani-driver']['path'].split('/target/')[0]
        cwd = p['cwd']; export = a[a.index('--export-json')+1]; target = a[a.index('--target-dir')+1]
        expected = [source+'/scripts/cargo-kani','kani','--manifest-path',cwd+'/Cargo.toml','--lib','--no-default-features','--features',slot,'--exact','--harness',name,'-j1','-Z','function-contracts','-Z','stubbing','-Z','export-json','--export-json',export,'--output-format=regular','--target-dir',target]
        check(slot+'_argv_identity', a == expected and ident['argv'] == a and ident['slot'] == s['feature'] == slot and ident['harness'] == s['selected_harness'] == name and digest(ident) == p['invocation_sha256'])
        check(slot+'_source_manifest_binding', ident['request_sha256'] == inp['request_sha256'] and ident['fixture_sha256'] == profile['control_sha256']['tests/script-based-pre/stub-contract-confirm/src/lib.rs'] and ident['manifest_sha256'] == profile['control_sha256']['tests/script-based-pre/stub-contract-confirm/Cargo.toml'])
        check(slot+'_environment', all(p['environment'].get(k) == val for k,val in ident['environment'].items()) and ident['environment']['RUSTUP_TOOLCHAIN'] == 'nightly-2026-11-12')
        check(slot+'_fresh_target', target not in targets and target.rsplit('/',1)[0] == export.rsplit('/',1)[0] and target.startswith('/tmp/stub-contract-'+slot+'-'))
        targets.add(target); STRICT['valid_process'](p)
        check(slot+'_diagnostic_blocks', all(d['complete'] is True and hashlib.sha256(d['text'].encode()).hexdigest() == d['sha256'] and len(d['text'].encode()) == d['bytes'] for d in p['diagnostics']))
        props = p.get('property_inventory',{}).get(name,[])
        check(slot+'_property_partition', [x['index'] for x in props] == list(range(1,len(props)+1)) and len({x['id'] for x in props}) == len(props))
        slot_results[slot] = {'producer':s['observation'], 'strict_retained_replay':retained_observation(slot,s), 'count_only_replay':retained_observation(slot,s,True), 'stdout_property_count':len(props), 'stdout_status_counts':dict(collections.Counter(x['status'] for x in props)), 'non_success_properties':[x for x in props if x['status'] != 'SUCCESS'], 'export_inventory':s['export_inventory'], 'retained_export':False, 'native_exit':p['exit'], 'verification_success':p['verification_success']}
    check('ordinary_exact_diagnostic_present', v['slots']['ordinary']['process']['diagnostics'][0]['header'] == 'error: Failed to find contract closure `__kani_recursion_check_f` in function `stub_contract_confirm::f`')
    check('producer_classification_replay', STRICT['classify'](v) == ('INCONCLUSIVE',['provider control failure']))
    tests = {}
    base = synthetic()
    tests['synthetic_strict_count_mismatch_rejected'] = retained_observation('verified',base)['outcome'] == 'INCONCLUSIVE'
    tests['synthetic_count_only_override_accepted'] = retained_observation('verified',base,True)['outcome'] == 'SUCCESS'
    mutations = {
        'wrong_target': lambda s:s['export'].__setitem__('target','aarch64-unknown-linux-gnu'),
        'wrong_export_status': lambda s:s['export'].__setitem__('run_state','PARTIAL'),
        'failed_check': lambda s:s['export']['harnesses'][0]['checks'].__setitem__('failure',['bad']),
        'failed_property': lambda s:s['process']['property_inventory']['verified_control'][0].__setitem__('status','FAILURE'),
        'unreachable_property': lambda s:s['process']['property_inventory']['verified_control'][1].__setitem__('status','UNREACHABLE'),
        'unreachable_bucket': lambda s:s['export']['harnesses'][0]['checks'].__setitem__('unreachable',['b']),
        'unrelated_error': lambda s:s['process']['diagnostics'].append({'header':'error: unrelated'}),
        'disabled_check': lambda s:s['export']['configuration']['checks'].__setitem__('memory_safety',False),
        'wrong_harness': lambda s:s['export']['harness_selection'].__setitem__('requested_filters',['other']),
        'missing_export': lambda s:s.pop('export'),
        'null_export': lambda s:s.__setitem__('export',None),
        'invalid_export': lambda s:s.__setitem__('export',[]),
        'partial_export': lambda s:s['export_inventory'].__setitem__('complete',False),
        'oversized_export': lambda s:s['export_inventory'].__setitem__('bytes',2*1024*1024+1),
        'invalid_export_size': lambda s:s['export_inventory'].__setitem__('bytes',True),
        'invalid_export_digest': lambda s:s['export_inventory'].__setitem__('sha256',None),
        'null_completeness': lambda s:s['export_inventory'].__setitem__('complete',None),
        'missing_count': lambda s:s['export']['harnesses'][0]['checks'].pop('total'),
        'null_count': lambda s:s['export']['harnesses'][0]['checks'].__setitem__('success',None),
        'error_bucket': lambda s:s['export']['harnesses'][0]['checks'].__setitem__('error',['bad']),
        'absent_presence': lambda s:s.pop('export_inventory'),
        'wrong_presence_type': lambda s:s['export_inventory'].__setitem__('present',1),
        'timeout': lambda s:s['process'].__setitem__('termination','TIMEOUT'),
        'nonzero_control_exit': lambda s:s['process'].__setitem__('exit',1),
        'incomplete_stream': lambda s:s['process']['streams']['stdout'].__setitem__('complete',False),
        'incomplete_diagnostics': lambda s:s['process'].__setitem__('diagnostics_complete',False),
    }
    for name, mutate in mutations.items():
        s = copy.deepcopy(base); mutate(s)
        tests[name+'_rejected'] = retained_observation('verified',s,True)['outcome'] == 'INCONCLUSIVE'
    ordinary = copy.deepcopy(v['slots']['ordinary'])
    tests['actual_ordinary_wrapper_not_silently_ignored'] = retained_observation('ordinary',ordinary,True)['outcome'] == 'INCONCLUSIVE'
    for slot in ['provider','verified']:
        tests[slot+'_unretained_export_not_forgiven'] = retained_observation(slot,v['slots'][slot],True)['outcome'] == 'INCONCLUSIVE'
    assert all(tests.values()), tests
    result = {'status':'PASS', 'scope':'STATIC_PYTHON_EVIDENCE_REPLAY_AND_SYNTHETIC_MUTATIONS', 'validations':validations, 'slots':slot_results, 'tests':tests, 'producer_classification':v['classification'], 'producer_reasons':v['reasons'], 'owner_policy_reclassified_observation':'INCONCLUSIVE', 'pinned_counts_only_independently_supported':False, 'blockers':['Both present complete exports are unretained; configuration/check buckets/export target and outcomes cannot be independently replayed.', 'Both inventories contain f.assertion.1 UNREACHABLE; the frozen oracle also rejects unreachable buckets and any non-SUCCESS property, separately from check counts.', 'Ordinary contains the exact f diagnostic plus the cargo-execution wrapper, which the frozen primary-error filter does not exclude.']}
    (HERE/'REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','validation_count':len(validations),'mutation_checks':len(tests),'owner_policy_reclassified_observation':result['owner_policy_reclassified_observation']}))


if __name__ == '__main__':
    main()
