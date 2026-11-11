"""Static A3 preparation checks; no build, compiler, verifier or Cloud calls."""
import hashlib
import importlib.util
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
ROOT = LANE.parents[2]
KANI = Path('/root/kani-fix-3300-t1')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = {}

    def require(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    request_path = HERE / 'RUN-REQUEST-A3.json'
    r = json.loads(request_path.read_text())
    old = json.loads((LANE / 'kani3300/t1b-r/RUN-REQUEST-A2.json').read_text())
    spec = importlib.util.spec_from_file_location('kani_k1', LANE / 'tools/kani_k1.py')
    k = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(k)
    require('validated_request', k.validate_request(r) == r)
    require('same_roots_and_expectations', r['harnesses'] == old['harnesses'] and len(r['harnesses']) == 9)
    require('exact_allowed_delta', {key: value for key, value in r.items() if key not in
            ('request_id', 'purpose', 'harness_timeout_minutes', 'diagnostic_trace')} ==
            {key: value for key, value in old.items() if key not in
            ('request_id', 'purpose', 'harness_timeout_minutes', 'diagnostic_trace')})
    require('trace_pins_unchanged', {k: v for k, v in r['diagnostic_trace'].items() if k != 'filters'} ==
            {k: v for k, v in old['diagnostic_trace'].items() if k != 'filters'})
    filters = ['cmp3_index_range_len', 'cmp3_manually_drop_unsized_len',
               'kani_cmp3::manually_drop_unsized_len', 'IndexRange::len', 'pincheck_calibration_']
    require('narrow_filter_and_activation', r['diagnostic_trace']['filters'] == filters and
            all(any(f in h['name'] for f in filters) for h in [r['harnesses'][i] for i in (0, 3, 7, 8)]))
    require('same_library', git(ROOT, 'rev-parse', 'HEAD:library') == r['diagnostic_trace']['library_tree'])
    require('kani_unchanged_clean', git(KANI, 'rev-parse', 'HEAD') ==
            '989f72351c2b5c5f3b5117315fc84f502e66d904' and not git(KANI, 'status', '--porcelain'))
    require('combined_patch_digest', sha(ROOT / r['kani_patch']['path']) == r['kani_patch']['sha256'] ==
            '0e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298')
    require('production_patch_digest', sha(LANE / 'kani3300/u4/kani-uninit.patch') ==
            '46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4')
    require('budget', r['harness_timeout_minutes'] == 1 and
            (Decimal(len(r['harnesses'])) + 30) * Decimal('.0135') == Decimal('.5265') <= Decimal('.5975'))
    invocation = json.loads((HERE / 'EFFECTIVE-INVOCATION.json').read_text())
    require('request_sha', invocation['request_sha256'] == sha(request_path))
    require('exact_args', (HERE / 'kani-A3.args').read_text().splitlines() == k.kani_args(r) and
            invocation['runner_argv'] == ['scripts/run-kani.sh', '--path', '/workspace/src', '--kani-args', *k.kani_args(r)])
    require('exact_env', invocation['env'] == {
        'KANI3300_TRACE_DIR': '/workspace/src/k1-out/trace', 'KANI3300_TRACE_FILTER': ';'.join(filters),
        'KANI3300_TRACE_ID': sha(request_path), 'KANI3300_TRACE_STAGE': 'kani3300-t1b',
        'RUSTFLAGS': '--cfg kani_smallsort_controls'})
    tooling = json.loads((HERE / 'TOOLING-FILES.json').read_text())
    require('tooling_hashes', all(sha(ROOT / path) == digest for path, digest in tooling.items()))
    require('prebuild_line_limit', len((HERE / 'PRE-BUILD.md').read_text().splitlines()) <= 30)
    print(json.dumps({'checks': checks, 'result': 'PASS', 'request_sha256': sha(request_path),
                      'reserve_usd': '0.5265', 'remaining_after_reserve_usd': '0.0710',
                      'compiler_cloud_dispatch': 'NOT_RUN', 'proof_credit': 'NONE'}, indent=2))


if __name__ == '__main__':
    main()
