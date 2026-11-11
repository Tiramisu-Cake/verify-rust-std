"""Static packet validation only: no compiler, verifier, build or Cloud operations."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from decimal import Decimal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LANE = ROOT / 'research/challenge-8/kani-k1'
KANI = Path('/root/kani-fix-3300-t1')
TASK_BASE = '5b1dc4d73262bca86913e43d1fcac7f3a3561d6d'

def git(root, *args, data=None, env=None):
    return subprocess.check_output(['git', '-C', str(root), *args], input=data, env=env)

def read(path):
    return json.loads(path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    checks = {}
    def require(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)
    b = read(HERE / 'PATCH-BINDING.json')
    old = LANE / 'kani3300/t1b'
    a = read(HERE / 'RUN-REQUEST-A2.json')
    original = read(old / 'RUN-REQUEST.json')
    production = (LANE / 'kani3300/u4/kani-uninit.patch').read_bytes()
    diag = (HERE / 'kani-diagnostic.patch').read_bytes()
    combined = (HERE / 'kani-combined.patch').read_bytes()
    repair = (HERE / 'kani-repair.patch').read_bytes()
    require('production_patch_unchanged', sha(production) == b['production_patch_sha256'] ==
            '46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4')
    require('kani_clean_and_branch', not git(KANI, 'status', '--porcelain') and
            git(KANI, 'branch', '--show-current').decode().strip() == 'diag/kani-3300-t1')
    require('kani_commit_parent', git(KANI, 'rev-parse', b['diagnostic_commit']+'^').decode().strip() == b['diagnostic_parent'])
    require('repair_only_type_annotation', repair == git(KANI, 'diff', '--binary', b['diagnostic_parent'], b['diagnostic_commit']) and
            [line for line in repair.decode().splitlines() if line[:1] in ('+', '-') and not line.startswith(('+++', '---'))] ==
            ['-        let instances = items', '+        let instances: Vec<Instance> = items'])
    require('diagnostic_patch_exact', diag == git(KANI, 'diff', '--binary', b['CMP2'], b['diagnostic_commit']))
    require('patch_hashes', sha(diag) == b['diagnostic_patch_sha256'] and sha(combined) == b['combined_patch_sha256'] and sha(repair) == b['repair_patch_sha256'])
    with tempfile.TemporaryDirectory(prefix='kani3300-t1br-check-') as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp)/'index'))
        git(KANI, 'read-tree', b['kani_base_pin'], env=env)
        git(KANI, 'apply', '--cached', '--whitespace=error', '-', data=production, env=env)
        require('production_applied_tree', git(KANI, 'write-tree', env=env).decode().strip() == b['production_applied_tree'])
        git(KANI, 'apply', '--cached', '--whitespace=error', '-', data=diag, env=env)
        require('combined_applied_tree', git(KANI, 'write-tree', env=env).decode().strip() == b['expected_applied_tree'])
        require('combined_patch_exact', combined == git(KANI, 'diff', '--cached', '--binary', b['kani_base_pin'], env=env))
        git(KANI, 'apply', '--cached', '--reverse', '-', data=diag, env=env)
        require('reverse_restores_production', git(KANI, 'write-tree', env=env).decode().strip() == b['production_applied_tree'])
    spec = importlib.util.spec_from_file_location('kani_k1', LANE/'tools/kani_k1.py')
    k = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(k)
    k.validate_request(a, max_total_minutes=720)
    require('valid_request', True)
    require('all_9_roots_and_expectations_unchanged', a['harnesses'] == original['harnesses'] and len(a['harnesses']) == 9)
    require('same_recipe_except_authorized_timeout', all(a[key] == original[key] for key in
            ('schema', 'agent', 'kind', 'runner', 'kani_jobs', 'controls', 'uninit_checks', 'inventory')))
    old_trace = dict(original['diagnostic_trace'], expected_applied_tree=b['expected_applied_tree'])
    require('trace_inputs_preserved', a['diagnostic_trace'] == old_trace)
    require('patch_request_bound', a['kani_patch']['sha256'] == sha(combined) and
            (ROOT/a['kani_patch']['path']).read_bytes() == combined)
    args = k.kani_args(a)
    old_args = k.kani_args(original)
    require('argv_only_timeout_changed', args == ['2m' if x == '3m' else x for x in old_args])
    (HERE/'kani-A2.args').write_text('\n'.join(args)+'\n')
    require('no_runtime_trace_flags', not any(x in args for x in ('--trace','--cbmc-args','--keep-temps','--no-slice-formula')))
    t = read(old/'TOOLING-BINDING.json')
    require('tooling_unchanged', all(sha((ROOT/name).read_bytes()) == digest for name,digest in read(old/'TOOLING-FILES.json').items()))
    require('recipe_pins_unchanged', all(sha((ROOT/name).read_bytes()) == digest for name,digest in t['recipe_files'].items()))
    require('library_tree_unchanged', git(ROOT, 'rev-parse', 'HEAD:library').decode().strip() == a['diagnostic_trace']['library_tree'] and not git(ROOT, 'diff', 'HEAD', '--', 'library'))
    require('old_packets_unchanged', not git(ROOT, 'diff', TASK_BASE, '--', str(old.relative_to(ROOT))))
    api = read(old/'API-SOURCES.json')
    require('pinned_api_source_hashes', all(sha((Path(api['local_source_root'])/s['path']).read_bytes()) == s['sha256'] for s in api['sources']))
    outcomes = read(LANE/'kani3300/t1a/HARNESS-OUTCOMES.json')['roots']
    require('baseline_9_timings_under_new_timeout', [r['name'] for r in outcomes] == [h['name'] for h in a['harnesses']] and
            max(r['time_s'] for r in outcomes) < a['harness_timeout_minutes']*60)
    reserve = (Decimal(len(a['harnesses'])*a['harness_timeout_minutes'])+30)*Decimal('0.0135')
    require('remaining_cap', a['harness_timeout_minutes'] == 2 and reserve == Decimal('0.6480') and reserve <= Decimal('0.719'))
    for name,limit in [('SWEEP.md',25),('PRE-BUILD.md',30)]:
        require(name+'_line_cap', len((HERE/name).read_text().splitlines()) <= limit)
    report = dict(status='PASS', checks=checks, request_A2_sha256=sha((HERE/'RUN-REQUEST-A2.json').read_bytes()),
                  expected_applied_tree=b['expected_applied_tree'], planned_reserve_usd=str(reserve),
                  spend_prior_usd='0.081', remaining_cap_usd='0.719', cumulative_worst_case_usd='0.729',
                  cloud='NOT_RUN', compilation='NOT_RUN', proof_credit='NONE')
    (HERE/'STATIC-CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(checks)} static checks; compiler/Cloud NOT_RUN')

if __name__ == '__main__':
    main()
