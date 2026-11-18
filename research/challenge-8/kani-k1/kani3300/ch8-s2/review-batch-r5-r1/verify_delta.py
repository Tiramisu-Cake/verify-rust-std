#!/usr/bin/env python3
"""Independent exact-input/delta checks; no full Validate or native execution."""
import ast, copy, hashlib, json, os, re, runpy, subprocess, sys
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = Path('/root/verify-rust-std-kani3300-g0')
PACKET = HERE.with_name('batch-r5-r1')
OLD = HERE.with_name('batch-r5')
PACKAGE = 'dc8d28b0117737e95ccc9b91eb470c1a3c42a635'
REVIEW = '022b9893c693f5908d3c9fa2ffe22961bbf8d30b'
P = json.loads((PACKET/'PINS.json').read_text())
C = Path(P['control']['worktree'])
Q = C/'ch8-s1-control'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n')

def functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}

def main():
    assert git(ROOT, 'cat-file', '-t', PACKAGE) == 'commit'
    rel = str(PACKET.relative_to(ROOT))
    committed = git(ROOT, 'ls-tree', '-r', '--name-only', PACKAGE, '--', rel).splitlines()
    actual = sorted(str(p.relative_to(ROOT)) for p in PACKET.rglob('*') if p.is_file())
    assert actual == committed and len(actual) == 70
    manifest = []
    for line in (PACKET/'MANIFEST.sha256').read_text().splitlines():
        expected, name = line.split(None, 1)
        name = name.lstrip('*')
        assert sha((PACKET/name).read_bytes()) == expected, name
        manifest.append(name)
    assert len(manifest) == 69 and len(set(manifest)) == 69
    assert set(manifest) == {str(p.relative_to(PACKET)) for p in PACKET.rglob('*') if p.is_file()} - {'MANIFEST.sha256'}
    for path in committed:
        assert subprocess.check_output(['git','-C',str(ROOT),'show',PACKAGE+':'+path]) == (ROOT/path).read_bytes()
    for revision, path in [(P['frozen_package'], OLD), (REVIEW, HERE.with_name('review-batch-r5'))]:
        assert not git(ROOT, 'diff', revision, '--', str(path.relative_to(ROOT)))
    assert git(ROOT, 'hash-object', str(ROOT/'research/challenge-8/kani-k1/TASK-CH8-S2-R5-R1-DELTA-REVIEW-W14.md'))
    # Reexecute the inspected author static validator, with its only persistent
    # output redirected to this review. It does not execute Validate/check-source.
    module = runpy.run_path(str(PACKET/'validate_package.py'), run_name='review_static_import')
    module['main'].__globals__['dump'] = lambda name, value: dump('REEXECUTED-'+name, value)
    module['main']()

    expected_paths = ['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json',
        'ch8-s1-control/check_package.py','ch8-s1-control/r5_campaign.py',
        'ch8-s1-control/r5_profile.py','ch8-s1-control/test_r5.py','ch8-s1-control/test_s2.py']
    assert git(C, 'diff', '--name-only', P['frozen_control'], P['control']['sha']).splitlines() == expected_paths
    invariance = {}
    allowed = {'check_package.py': {'check_yaml'}, 'r5_profile.py': {'validate_yaml'},
               'r5_campaign.py': {'sealed','root_outcome'}}
    for file, changed in allowed.items():
        before = subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/'+file], text=True)
        after = (Q/file).read_text()
        a, b = functions(before), functions(after)
        assert set(a) == set(b)
        different = sorted(n for n in a if a[n] != b[n])
        assert set(different) == changed
        def rest(text):
            m = ast.parse(text)
            m.body = [n for n in m.body if not isinstance(n, ast.FunctionDef) or n.name not in changed]
            return ast.dump(m, include_attributes=False)
        assert rest(before) == rest(after)
        invariance[file] = {'changed_functions':different, 'other_AST':'IDENTICAL'}
    before = subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/test_r5.py'], text=True)
    after = ast.parse((Q/'test_r5.py').read_text())
    after.body = [n for n in after.body if not isinstance(n, ast.ClassDef) or n.name != 'PortablePrefixTests']
    assert ast.dump(after) == ast.dump(ast.parse(before))
    before_s2 = subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/test_s2.py'], text=True)
    assert before_s2.replace("['step_timeout_sum_minutes'],186", "['step_timeout_sum_minutes'],187") == (Q/'test_s2.py').read_text()
    def entries(revision):
        return dict((line.split('\t',1)[1],line.split('\t',1)[0])
                    for line in git(C,'ls-tree','-r',revision).splitlines())
    before_entries, after_entries = entries(P['frozen_control']), entries(P['control']['sha'])
    assert set(before_entries) == set(after_entries)
    assert sorted(path for path in before_entries if before_entries[path] != after_entries[path]) == expected_paths
    unchanged = sorted(set(before_entries)-set(expected_paths))
    old_request = json.loads((OLD/'CI-REQUEST.json').read_text())
    request = json.loads((Q/'CI-REQUEST.json').read_text())
    changed_keys = sorted(k for k in set(request)|set(old_request) if request.get(k) != old_request.get(k))
    assert changed_keys == ['ci_payload_sha256','control_reference','entry_g0']
    sys.path.insert(0,str(Q))
    import check_package as cp
    old_workflow = cp.load_yaml((OLD/'WORKFLOW.yml').read_text())
    workflow = cp.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text())
    normalized = copy.deepcopy(workflow)
    steps = workflow['jobs']['s2_batch']['steps']
    validate = next(s for s in steps if s['name']=='Validate control and synthetic wrapper')
    next(s for s in normalized['jobs']['s2_batch']['steps'] if s['name']==validate['name'])['timeout-minutes'] = 10
    assert normalized == old_workflow
    assert sum(s['timeout-minutes'] for s in steps) == 187
    assert request['budgets'] == old_request['budgets']
    assert request['r5'] == old_request['r5']
    timing = json.loads((PACKET/'COMBINED-FINAL-VALIDATE-TIMING.json').read_text(), parse_float=Decimal)
    provenance = json.loads((PACKET/'COMBINED-TEST-PROVENANCE.json').read_text(), parse_float=Decimal)
    assert all(provenance[k] == v for k,v in timing.items())
    assert timing['command'] == validate['run']
    assert timing['monotonic_end_ns'] - timing['monotonic_start_ns'] == int(timing['elapsed_seconds']*10**9)
    assert timing['provenance']['control']['sha'] == P['control']['sha']
    assert timing['provenance']['source']['sha'] == P['source']['sha']
    assert timing['provenance']['tool']['sha'] == P['tool']['sha']
    log = (PACKET/'COMBINED-FINAL-VALIDATE.txt').read_bytes()
    assert sha(log) == timing['transcript_sha256']
    assert len(re.findall(rb'^test_.* \.\.\. ok$', log, re.M)) == 134
    prior = json.loads((PACKET/'PRIOR-OBJECT-VALIDATE-TIMING.json').read_text(),parse_float=Decimal)
    for t in (timing,prior):
        assert t['status']=='PASS' and t['exit_code']==0
    elapsed=timing['elapsed_seconds'];cap=Decimal(60*validate['timeout-minutes'])
    assert cap/elapsed>=Decimal('1.5')
    assert (elapsed*Decimal('1.5')/60).to_integral_value(rounding=ROUND_CEILING)==11
    dump('VALIDATE-MARGIN.json', {'final_control':P['control']['sha'],'actual_final_tests':134,
        'actual_final_seconds':str(elapsed),'cap_seconds':str(cap),'margin':str(cap/elapsed),
        'minimum_seconds':str(elapsed*Decimal('1.5')),'minimum_whole_minutes':11,
        'prior_control':prior['provenance']['control']['sha'],'prior_tests':130,
        'prior_seconds':str(prior['elapsed_seconds']),'prior_classification':'INHERITED_PRIOR_OBJECT4e97',
        'margin_against_prior':str(cap/prior['elapsed_seconds']),
        'legacy_Validate_minutes':10,'R5_step_maxima_minutes':187,'legacy_step_maxima_minutes':186,
        'setup_step_maxima_seconds':3180,'setup_aggregate_seconds':1800,'job_seconds':10800,
        'campaign_caps':request['r5']['caps'],'extra_budget_grant':False,
        'new_full_Validate_executions':0,'future_GitHub_duration':'UNKNOWN'})
    dump('INVARIANCE.json', {'status':'INDEPENDENTLY_VERIFIED','package':PACKAGE,
        'package_files':len(actual),'manifest_hashes':len(manifest),'original_package_review':'UNCHANGED',
        'delta_paths':expected_paths,'request_changed_keys':changed_keys,'workflow_only_delta':'Validate10->11',
        'function_AST':invariance,'unchanged_control_file_count':len(unchanged),
        'unchanged_control_tree_except_seven_paths':True,
        'original_R5_tests':'ALL_23_UNCHANGED; four portable tests added',
        'source_tool':'EXACT_UNCHANGED','protected_decoders_bindings':'BYTE_IDENTICAL',
        'scope':'inherit original full review by verified invariance; localized two-finding delta'})
    dump('INPUTS.json', {'task':'taska9cc91d717751d2047e13bc7570a95305f546fa7',
        'review_task_sha256':sha((ROOT/'research/challenge-8/kani-k1/TASK-CH8-S2-R5-R1-DELTA-REVIEW-W14.md').read_bytes()),
        'owner_override':'21:10 /new overrides reuse-context wording',
        'package':PACKAGE,'pins_sha256':sha((PACKET/'PINS.json').read_bytes()),
        'control':P['control'],'source':P['source'],'tool':P['tool'],
        'prior_review':REVIEW,'prior_package':P['frozen_package'],
        'Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','dispatch_authority':'NONE'})
    print('INDEPENDENT_DELTA_PASS: exact70/69, invariance, margin; static six replays and shallow7/5/2')

if __name__ == '__main__': main()
