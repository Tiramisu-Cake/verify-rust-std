"""Read-only Git/request/identity checks for C, plus disposable-index patch application.
No actual preparation/compiler/verifier/Cloud/dispatch/phase or active-input mutation.
"""
import hashlib
import importlib.util
import json
import os
from decimal import Decimal
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
ROOT = LANE.parents[2]
KANI = Path('/root/kani-fix-3300-t1')
BASE = '989f72351c2b5c5f3b5117315fc84f502e66d904'
FINAL = '12b4137c42f3ee92f12476ea0771ea41a5cd1e8d'


def git(root, *args, env=None):
    return subprocess.check_output(['git', '-C', str(root), *args], env=env).decode().strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = {}

    def require(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)

    request_path = HERE / 'RUN-REQUEST-C.json'
    r = json.loads(request_path.read_text())
    a3 = json.loads((LANE / 'kani3300/t1b-a3/RUN-REQUEST-A3.json').read_text())
    spec = importlib.util.spec_from_file_location('k', LANE / 'tools/kani_k1.py')
    k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
    require('request_validated', k.validate_request(r) == r)
    names = ['cmp3_into_iter_next', 'cmp3_index_range_len', 'cmp3_manually_drop_unsized_len',
             'pincheck_calibration_uninit_read_u8', 'pincheck_calibration_init_read_u8']
    by = {x['name'].rsplit('::', 1)[-1]: x for x in a3['harnesses']}
    require('exact_five_roots_original_expectations', r['harnesses'] == [by[n] for n in names])
    require('one_invocation_unchanged_controls', all(r[x] == a3[x] for x in
            ('schema', 'agent', 'kind', 'runner', 'harness_timeout_minutes', 'kani_jobs', 'controls', 'uninit_checks', 'inventory')))
    require('exact_three_filters', r['diagnostic_trace']['filters'] ==
            ['IndexRange::len', 'cmp3_index_range_len', 'cmp3_manually_drop_unsized_len'])
    require('library_and_pin_unchanged', r['diagnostic_trace']['library_tree'] ==
            git(ROOT, 'rev-parse', 'HEAD:library') == '919cc3e2dc5fb19ea6e7f7be761914b949160a41' and
            r['diagnostic_trace']['base_pin'] == a3['diagnostic_trace']['base_pin'])
    require('kani_final_clean', git(KANI, 'rev-parse', 'HEAD') == FINAL and not git(KANI, 'status', '--porcelain'))
    require('kani_parent_exact', git(KANI, 'rev-parse', 'HEAD^') == BASE)
    require('combined_patch_exact', (ROOT / r['kani_patch']['path']).read_bytes() ==
            subprocess.check_output(['git', '-C', str(KANI), 'diff', '--binary', r['diagnostic_trace']['base_pin'], FINAL]))
    require('patch_sha', sha(ROOT / r['kani_patch']['path']) == r['kani_patch']['sha256'])
    require('applied_tree', git(KANI, 'rev-parse', FINAL + '^{tree}') == r['diagnostic_trace']['expected_applied_tree'])
    # Use an isolated temporary index, never the worktree index or source files.
    with tempfile.TemporaryDirectory() as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
        git(KANI, 'read-tree', r['diagnostic_trace']['base_pin'], env=env)
        git(KANI, 'apply', '--cached', str(ROOT / r['kani_patch']['path']), env=env)
        require('patch_applies_exact_tree', git(KANI, 'write-tree', env=env) == r['diagnostic_trace']['expected_applied_tree'])
        git(KANI, 'apply', '--cached', '--reverse', str(HERE / 'kani-compact.patch'), env=env)
        require('reverse_compact_restores_989', git(KANI, 'write-tree', env=env) == git(KANI, 'rev-parse', BASE + '^{tree}'))
    unchanged = json.loads((HERE / 'UNCHANGED-INPUTS.json').read_text())
    require('active_inputs_tools_recipe_production_patch_unchanged', all(sha(ROOT / path) == digest for path, digest in unchanged.items()))
    require('production_patch_known_sha', sha(LANE / 'kani3300/u4/kani-uninit.patch') ==
            '46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4')
    invocation = json.loads((HERE / 'EFFECTIVE-INVOCATION.json').read_text())
    require('request_invocation_sha', invocation['request_sha256'] == sha(request_path))
    require('exact_argv', (HERE / 'kani-C.args').read_text().splitlines() == k.kani_args(r) and
            invocation['runner_argv'] == ['scripts/run-kani.sh', '--path', '/workspace/src', '--kani-args', *k.kani_args(r)])
    require('exact_env', invocation['env'] == {
        'KANI3300_TRACE_DIR': '/workspace/src/k1-out/trace', 'KANI3300_TRACE_FILTER': ';'.join(r['diagnostic_trace']['filters']),
        'KANI3300_TRACE_ID': sha(request_path), 'KANI3300_TRACE_STAGE': 'kani3300-t1b', 'RUSTFLAGS': '--cfg kani_smallsort_controls'})
    binding = json.loads((HERE / 'BINDING.json').read_text())
    require('binding_exact', binding['kani_commit'] == FINAL and
            binding['request_sha256'] == sha(request_path) and
            binding['combined_patch_sha256'] == r['kani_patch']['sha256'] and
            binding['compact_patch_sha256'] == sha(HERE / 'kani-compact.patch') and
            binding['expected_applied_tree'] == r['diagnostic_trace']['expected_applied_tree'] and
            binding['effective_invocation_sha256'] == sha(HERE / 'EFFECTIVE-INVOCATION.json'))
    budget = json.loads((HERE / 'BUDGET.json').read_text())
    require('static_budget', (Decimal(len(r['harnesses'])) * r['harness_timeout_minutes'] + 30) * Decimal('.0135') ==
            Decimal(budget['reserve_usd']) == Decimal('.4725') <= Decimal(budget['stage_remaining_usd']) == Decimal('.4760'))
    require('budget_no_added_overhead', budget['paid_build_timeout_minutes'] == 35 and budget['invocations'] == 1 and
            budget['overhead_added_again'] == 0 and not budget['reserve_registered'])
    require('document_line_limits', len((HERE / 'STATIC.md').read_text().splitlines()) <= 40 and
            len((HERE / 'PRE-BUILD.md').read_text().splitlines()) <= 30)
    from estimate_capacity import estimate
    capacity = estimate()
    require('capacity_current', capacity == json.loads((HERE / 'CAPACITY.json').read_text()))
    from check_semantics import check
    require('semantic_tokens', len(check()) == 5)
    return {'result': 'PASS', 'checks': checks, 'kani_commit': FINAL,
            'request_sha256': sha(request_path), 'combined_patch_sha256': r['kani_patch']['sha256'],
            'applied_tree': r['diagnostic_trace']['expected_applied_tree'], 'proof_credit': 'NONE',
            'compiler_cloud_dispatch': 'NOT_RUN'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
