"""C2 pre-dispatch preflight: static Git metadata in disposable indexes only.

No real prepare/compiler/Cloud, active-input installation or live ledger access.
Run from the assigned research worktree before any future coordinator dispatch.
"""
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
ROOT = LANE.parents[2]
KANI = Path('/root/kani-fix-3300-t1')
PIN = 'f046b70644e113be0df9c22c2e6ea44a65a57566'
FINAL = '12b4137c42f3ee92f12476ea0771ea41a5cd1e8d'
sys.path.insert(0, str(LANE / 'tools'))
import kani_k1 as k


def git(root, *args, env=None, data=None):
    return subprocess.check_output(['git', '-C', str(root), *args], env=env, input=data).decode().strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_report(request):
    # Same path/hash/nonempty/4MiB guards as Cloud prepare, same bytes checked/applied.
    data = k.patch_bytes(request, ROOT)
    assert data is not None
    with tempfile.TemporaryDirectory() as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
        git(KANI, 'read-tree', PIN, env=env)
        git(KANI, 'apply', '--cached', '--check', '-', env=env, data=data)
        git(KANI, 'apply', '--cached', '-', env=env, data=data)
        # Same command, stripped output, UTF-8 encoding and shared bound as prepare_kani.
        stat = k.validate_patch_diffstat(git(KANI, 'diff', '--cached', '--stat', PIN, env=env))
        tree = git(KANI, 'write-tree', env=env)
        paths = git(KANI, 'diff', '--cached', '--name-only', PIN, env=env).splitlines()
        git(KANI, 'apply', '--cached', '--reverse', str(LANE / 'kani3300/t1b-s/kani-compact.patch'), env=env)
        restored = git(KANI, 'write-tree', env=env)
    return {'tree': tree, 'paths': paths, 'diffstat': stat, 'a3_restored_tree': restored}


def main():
    checks = {}

    def require(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)

    request_path = HERE / 'RUN-REQUEST-C2.json'
    r = json.loads(request_path.read_text())
    require('request_all_schema_bounds', k.validate_request(r) == r)
    a3 = json.loads((LANE / 'kani3300/t1b-a3/RUN-REQUEST-A3.json').read_text())
    by = {x['name'].rsplit('::', 1)[-1]: x for x in a3['harnesses']}
    require('three_roots_original_expectations', r['harnesses'] == [by[n] for n in
            ('cmp3_into_iter_next', 'cmp3_index_range_len', 'cmp3_manually_drop_unsized_len')])
    require('one_invocation_controls_uninit_timeout_unchanged', all(r[x] == a3[x] for x in
            ('schema', 'agent', 'kind', 'runner', 'harness_timeout_minutes', 'kani_jobs', 'controls', 'uninit_checks', 'inventory')))
    require('pin_library_filters_exact', r['diagnostic_trace']['base_pin'] == PIN and
            r['diagnostic_trace']['library_tree'] == git(ROOT, 'rev-parse', 'HEAD:library') ==
            '919cc3e2dc5fb19ea6e7f7be761914b949160a41' and r['diagnostic_trace']['filters'] ==
            ['IndexRange::len', 'cmp3_index_range_len', 'cmp3_manually_drop_unsized_len'])
    require('kani_diagnostic_unchanged_clean', git(KANI, 'rev-parse', 'HEAD') == FINAL and
            not git(KANI, 'status', '--porcelain', '--untracked-files=all'))
    require('runner_pin_exact', f'commit = "{PIN}"' in (ROOT / 'tool_config/kani-version.toml').read_text())
    before = (git(KANI, 'rev-parse', 'HEAD'), git(KANI, 'write-tree'), git(KANI, 'status', '--porcelain'))
    report = patch_report(r)
    identities = json.loads((HERE / 'PATCH-IDENTITIES.json').read_text())
    a3paths = [s.split(' b/', 1)[1] for s in (LANE / 'kani3300/t1b-r/kani-combined.patch').read_text().splitlines()
               if s.startswith('diff --git ')]
    diagpaths = git(KANI, 'diff', '--name-only', '989f72351c', FINAL).splitlines()
    require('exact_deployment_paths_without_historical_tests', report['paths'] ==
            sorted(set(a3paths + diagpaths)) == identities['deployment_paths'] and
            len(report['paths']) == 15 and not any(p.startswith('tests/') for p in report['paths']))
    require('all_non_test_changes_preserved', report['paths'] ==
            git(KANI, 'diff', '--name-only', PIN, FINAL, '--', '.', ':!tests').splitlines())
    require('exact_combined_patch', k.patch_bytes(r, ROOT) == subprocess.check_output(
            ['git', '-C', str(KANI), 'diff', '--binary', PIN, FINAL, '--', *report['paths']]))
    require('deployment_tree_exact', report['tree'] == r['diagnostic_trace']['expected_applied_tree'] == identities['deployment_tree'])
    require('reverse_diagnostic_restores_A3_deployment', report['a3_restored_tree'] ==
            '53927d9bc0ccbff8183aa91ffb6c29d1c8a74465')
    require('prepare_patch_bytes_and_diffstat_bounds', report['diffstat'] == identities['diffstat'] and
            len(report['diffstat'].encode()) == identities['diffstat_utf8_bytes'] <= k.MAX_PATCH_DIFFSTAT_BYTES and
            len(k.patch_bytes(r, ROOT)) == identities['patch_bytes'] <= 4 * 1024 * 1024)
    # Regression: the prior rejected C must fail this preflight, before any Build.
    old = json.loads((LANE / 'kani3300/t1b-s/RUN-REQUEST-C.json').read_text())
    try:
        patch_report(old)
    except k.RequestError as exc:
        require('old_C_rejected_before_build', str(exc) == 'patch diffstat exceeds bounded report size')
    else:
        raise AssertionError('old C unexpectedly accepted')
    require('kani_head_index_worktree_preserved', before ==
            (git(KANI, 'rev-parse', 'HEAD'), git(KANI, 'write-tree'), git(KANI, 'status', '--porcelain')))
    frozen = json.loads((HERE / 'UNCHANGED-INPUTS.json').read_text())
    require('active_inputs_runner_recipe_production_patch_unchanged', all(sha(ROOT / p) == s for p, s in frozen.items()))
    inv = json.loads((HERE / 'EFFECTIVE-INVOCATION.json').read_text())
    require('argv_and_env_exact', inv['invocations'] == 1 and inv['request_sha256'] == sha(request_path) and
            (HERE / 'kani-C2.args').read_text().splitlines() == k.kani_args(r) and
            inv['runner_argv'] == ['scripts/run-kani.sh', '--path', '/workspace/src', '--kani-args', *k.kani_args(r)] and
            inv['env'] == {'KANI3300_TRACE_DIR': '/workspace/src/k1-out/trace',
                           'KANI3300_TRACE_FILTER': ';'.join(r['diagnostic_trace']['filters']),
                           'KANI3300_TRACE_ID': sha(request_path), 'KANI3300_TRACE_STAGE': 'kani3300-t1b',
                           'RUSTFLAGS': '--cfg kani_smallsort_controls'})
    binding = json.loads((HERE / 'BINDING.json').read_text())
    require('binding_exact', binding['kani_commit'] == FINAL and binding['base_pin'] == PIN and
            binding['deployment_tree'] == report['tree'] and binding['combined_patch_sha256'] == r['kani_patch']['sha256'] and
            binding['request_sha256'] == sha(request_path) and binding['effective_invocation_sha256'] == sha(HERE / 'EFFECTIVE-INVOCATION.json') and
            all(sha(ROOT / p) == s for p, s in binding['tooling_files'].items()))
    budget = json.loads((HERE / 'BUDGET.json').read_text())
    require('reserve_within_cap_no_extra_overhead', (Decimal(3) * r['harness_timeout_minutes'] + 30) * Decimal('.0135') ==
            Decimal(budget['reserve_usd']) == Decimal('.4455') <= Decimal(budget['remaining_usd']) == Decimal('.4490') and
            budget['paid_timeout_minutes'] == 33 and budget['invocations'] == 1 and budget['extra_overhead_minutes'] == 0 and
            not budget['reserve_registered'] and not budget['dispatch_authorized'])
    require('pre_build_at_most_30_lines', len((HERE / 'PRE-BUILD.md').read_text().splitlines()) <= 30)
    return {'result': 'PASS', 'checks': checks, 'request_sha256': sha(request_path),
            'patch_sha256': r['kani_patch']['sha256'], 'deployment_tree': report['tree'],
            'diffstat_utf8_bytes': len(report['diffstat'].encode()), 'prepare_compiler_cloud_dispatch': 'NOT_RUN', 'proof_credit': 'NONE'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
