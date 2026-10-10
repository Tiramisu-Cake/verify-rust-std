#!/usr/bin/env python3
"""Cloud-only isolated test driver for the production-base strict cut.

Importing this module is inert. It never dispatches a Cloud Build; callers must
invoke run() from the dedicated authorized Cloud lane.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE = Path('research/challenge-8/cloud-build/sort4-compatible-strict-cut')
TRANSLATOR = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
KERNEL = 'src/verifast.ml'
PATCH_NAME = 'verifast-compatible-strict-cut-TEST.patch'
EXPECTED_TRANSLATOR = '4d3a190fcec695415b41162ddf8d71aec6e2826d2b69e7692df306a568add98c'
EXPECTED_KERNEL = 'adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0'
MARKER_OFF_REFUSAL = 'Strict lifetime binding requires explicit overnight opt-in'
CRITICAL = (KERNEL, TRANSLATOR, 'src/rust_frontend/vf_mir_translator/rust_parser.ml',
            'src/rust_frontend/vf_mir/vf_mir.capnp', 'bin/verifast',
            'bin/vf-rust-mir-exporter', 'bin/refinement-checker')
EXECUTABLES = ('bin/verifast', 'bin/vf-rust-mir-exporter',
               'bin/refinement-checker')
POSITIVE = frozenset(('ordinary_default_off', 'positive_basic',
                      'positive_early_return', 'positive_direct_unwind',
                      'positive_outgoing_goto'))
NEGATIVE = frozenset(('negative_heap_escape', 'negative_outer_type_escape',
                      'negative_typed_chunk_survives_cut',
                      'negative_type_after_cut'))
INCONCLUSIVE_SOURCE_FORMS = frozenset((
    'negative_outer_type_escape', 'negative_outer_bound_escape'))
CASE_RE = re.compile(rb'(?ms)^// CASE_BEGIN ([a-z][a-z0-9_]*)\r?\n(.*?)^// CASE_END \1\r?$')
TRACE_ENTRY = re.compile(r"(?m)^\s*\d+(?:\.\d+)?s: .*: Verifying function '([^']+)'\s*$")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f'missing source utility: {path}')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def strip_ghost(data: bytes) -> bytes:
    data = re.sub(rb'/\*@.*?@\*/(?:\r?\n)?', b'', data, flags=re.S)
    return re.sub(rb'(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)', b'', data)


def snapshot(tool: Path, applied_patch: Path, profile: dict) -> dict:
    return {
        'head': subprocess.check_output(
            ['git', '-C', str(tool), 'rev-parse', 'HEAD'], text=True).strip(),
        'critical': {name: sha(tool / name) for name in CRITICAL},
        'binaries': {name: sha(tool / name) for name in EXECUTABLES},
        'effective_rsspec': {
            str(path.relative_to(tool)): sha(path)
            for path in sorted((tool / 'bin/rust').rglob('*.rsspec'))},
        'production_applied_patch_sha256': sha(applied_patch),
        'proof_sha': os.environ['PROOF_SHA'],
        'infra_sha': os.environ['INFRA_SHA'],
        'profile': profile.get('classification'),
        'accepted': False,
    }


def stage(a: argparse.Namespace, root: Path, name: str, argv: list[str],
          env: dict[str, str], cap: int, *, stdin: str | None = None,
          stdout: str | None = None) -> dict:
    remain = int(a.deadline_epoch - time.time()) - 20
    seconds = min(cap, remain)
    result = {'name': name, 'argv': argv, 'state': 'NOT_RUN', 'exit': None,
              'proof_verdict': None}
    if seconds <= 0:
        result['reason'] = 'session deadline reserve'
        write(root / (name + '-stage.json'), result)
        return result
    output = root / (stdout or name + '.log')
    error = root / (name + '-stderr.log') if stdout else output
    result.update(state='RUNNING', timeout_seconds=seconds)
    write(root / (name + '-stage.json'), result)
    with output.open('wb') as out:
        err = error.open('wb') if error != output else subprocess.STDOUT
        inp = (root / stdin).open('rb') if stdin else open(os.devnull, 'rb')
        try:
            code = subprocess.run(
                ['/usr/bin/time', '-v', '-o', str(root / (name + '-resources.txt')),
                 'timeout', '--signal=TERM', '--kill-after=10s', str(seconds) + 's',
                 *argv], cwd=root, env={**env, 'PWD': str(root)}, stdin=inp,
                stdout=out, stderr=err, check=False).returncode
        finally:
            inp.close()
            if error != output:
                err.close()
    result.update(state='TERMINAL', exit=code, stdout=output.name,
                  stderr=error.name, stdout_sha256=sha(output),
                  stderr_sha256=sha(error))
    write(root / (name + '-stage.json'), result)
    return result


def extract_cases(template: bytes) -> dict[str, bytes]:
    rows = CASE_RE.findall(template)
    result = {name.decode(): body for name, body in rows}
    need(len(rows) == len(result), 'duplicate case delimiter in fixtures.rs')
    need(result, 'fixtures.rs contains no physical cases')
    return result


def pin_production(a: argparse.Namespace, profile: dict) -> None:
    source = a.production_source
    need(source.is_dir() and a.stock_home.is_dir(), 'production or stock tool home missing')
    need(sha(source / TRANSLATOR) == profile['base_translator_sha256'] == EXPECTED_TRANSLATOR and
         sha(source / KERNEL) == profile['base_kernel_sha256'] == EXPECTED_KERNEL,
         'production source does not match the exact translator/kernel bases')
    current = subprocess.check_output(
        ['git', '-C', str(source), 'diff', '--binary'], stderr=subprocess.STDOUT)
    need(current == a.production_applied_patch.read_bytes(),
         'production source differs from the supplied canonical applied patch')
    need(os.environ.get('PROOF_SHA', '').lower() == subprocess.check_output(
        ['git', '-C', str(a.proof_root), 'rev-parse', 'HEAD'], text=True).strip().lower(),
         'proof checkout SHA does not match the dispatched pin')


def install_two_file_patch(tool: Path, patch: Path, profile: dict,
                           root: Path, env: dict[str, str], a: argparse.Namespace) -> None:
    data = patch.read_text()
    headers = re.findall(r'^diff --git a/(\S+) b/(\S+)$', data, flags=re.M)
    expected = {(TRANSLATOR, TRANSLATOR), (KERNEL, KERNEL)}
    need(set(headers) == expected and len(headers) == 2,
         'strict-cut patch must contain exactly translator and kernel files')
    need(digest(patch.read_bytes()) == profile['patch_sha256'],
         'strict-cut patch SHA differs from profile')
    before_names = set(subprocess.check_output(
        ['git', '-C', str(tool), 'diff', '--name-only'], text=True).splitlines())
    tracked = subprocess.check_output(
        ['git', '-C', str(tool), 'ls-files', '-z']).decode().split('\0')
    before_hashes = {name: sha(tool / name) for name in tracked
                     if name and (tool / name).is_file()}
    for label, args in (('patch-check', ['--check']), ('patch-apply', [])):
        row = stage(a, root, label,
                    ['git', '-C', str(tool), 'apply', *args, str(patch)], env, 60)
        need(row.get('exit') == 0, 'two-file strict-cut patch ' + label + ' failed')
    changed = subprocess.check_output(
        ['git', '-C', str(tool), 'diff', '--name-only'], text=True).splitlines()
    need(set(changed) == before_names | {TRANSLATOR, KERNEL},
         'strict-cut patch altered the frozen production diff file set')
    need(all((tool / name).is_file() and sha(tool / name) == value
             for name, value in before_hashes.items()
             if name not in {TRANSLATOR, KERNEL}),
         'strict-cut patch changed a frozen tracked production file')
    need(sha(tool / TRANSLATOR) == profile['patched_translator_sha256'] and
         sha(tool / KERNEL) == profile['patched_kernel_sha256'],
         'patched translator/kernel hashes differ from profile')


def run_case(a: argparse.Namespace, tool: Path, profile: dict, template: bytes,
             case: str, body: bytes, capture, schema: Path, env_base: dict[str, str]) -> dict:
    root = a.evidence / 'cases' / case
    root.mkdir(parents=True)
    verified = template + b'\n' + body
    original = strip_ghost(verified)
    (root / 'verified/lib.rs').parent.mkdir(parents=True, exist_ok=True)
    (root / 'verified/lib.rs').write_bytes(verified)
    (root / 'original/lib.rs').parent.mkdir(parents=True, exist_ok=True)
    (root / 'original/lib.rs').write_bytes(original)
    cert = {'case': case, 'verified_sha256': digest(verified),
            'original_sha256': digest(original),
            'runtime_source_unchanged': strip_ghost(verified) == original,
            'source_only': True, 'tool_profile': profile['classification']}
    write(root / 'source-certificate.json', cert)

    env = env_base.copy()
    env.pop('SORT4_STRICT_LFT_CUT', None)
    env['SORT4_ACTUAL_AST_SCOPE_TEST'] = '0'
    env['SORT4_HRTB_OUTPUT'] = '0'
    env['SORT4_HRTB_OUTPUT_TARGETS'] = ''
    env['SORT4_STRICT_LFT_TRACE'] = '0'
    env['SORT4_STRICT_LFT_RELOCATE'] = '0'
    env['SORT4_COMPAT_STRICT_CUT_AST_CAPTURE'] = '0'
    env['SORT4_COMPAT_STRICT_CUT_AST_CAPTURE_ONLY'] = '0'
    mir_rows = {}
    support = {}
    exporter = str(tool / 'bin/vf-rust-mir-exporter')
    for mode, extra in (('normal', []),
                        ('readonly', ['--vf-rust-mir-exporter:preprocess-readonly'])):
        binary = root / f'{mode}-mir.bin'
        decoded = root / f'{mode}-mir.txt'
        export_row = stage(a, root, mode + '-export',
            [exporter, 'verified/lib.rs', '--sysroot=' + str(a.compiler_sysroot),
             '--edition', '2021', '--crate-type', 'lib', *extra], env, 120,
            stdout=binary.name)
        decode_row = {'exit': None, 'state': 'NOT_RUN'}
        if export_row.get('exit') == 0:
            decode_row = stage(a, root, mode + '-decode',
                ['capnp', 'decode', str(schema), 'VfMir'], env, 60,
                stdin=binary.name, stdout=decoded.name)
        support[mode + '-export'] = export_row.get('exit') == 0
        support[mode + '-decode'] = decode_row.get('exit') == 0
        if decode_row.get('exit') == 0:
            text = decoded.read_text(errors='replace')
            try:
                _name, record = capture.complete_function_record(text, case)
                record_path = root / f'{mode}-target-full-mir.txt'
                record_path.write_text(record)
                mir_rows[mode] = {'decoded_sha256': sha(decoded),
                    'decoded_bytes': decoded.stat().st_size,
                    'target_record_sha256': sha(record_path),
                    'target_record_bytes': len(record.encode()),
                    'direct_continue_edges': record.count('unwindAction = (continue = void)'),
                    'target_record_path': record_path.name}
            except (ValueError, OSError, IndexError) as exc:
                support[mode + '-target-record'] = False
                mir_rows[mode] = {'classification': 'TARGET_MIR_RECORD_NOT_FOUND',
                                  'error': str(exc), 'decoded_sha256': sha(decoded)}
            else:
                support[mode + '-target-record'] = True

    refine_row = stage(a, root, 'refinement',
        [str(tool / 'bin/refinement-checker'), '--rustc-args',
         '--edition 2021 --crate-type lib', 'original/lib.rs', 'verified/lib.rs'], env, 120)
    support['refinement'] = refine_row.get('exit') == 0
    support_ok = all(support.values())
    write(root / 'fresh-support.json', {'support_passed': support_ok,
        'stages': support, 'pre_ast_sha256': None,
        'mir': mir_rows, 'proof_started': False})

    result = {'case': case, 'accepted': False, 'proof_credit': False,
              'source_certificate': cert, 'fresh_support': support,
              'mir': mir_rows, 'proof': {'state': 'NOT_RUN', 'exit': None},
              'classification': 'SETUP_OR_SOURCE_MIR_BLOCKER'}
    if not support_ok:
        write(root / 'case-result.json', result)
        return result

    proof_env = env.copy()
    marker_off = case == 'marker_default_off'
    ordinary_off = case == 'ordinary_default_off'
    if not marker_off and not ordinary_off:
        proof_env['SORT4_STRICT_LFT_CUT'] = '1'
        proof_env['SORT4_COMPAT_STRICT_CUT_AST_CAPTURE'] = '1'
        proof_env['SORT4_COMPAT_STRICT_CUT_AST_CAPTURE_ONLY'] = '1'
        proof_env['SORT4_COMPAT_STRICT_CUT_CAPTURE_TARGET'] = case
    ast_path = root / 'strict-cut-pre-proof-ast.ml'
    need(not ast_path.exists(), 'pre-proof AST capture output already exists')
    command = [str(tool / 'bin/verifast'), '-rustc_args',
               '--edition 2021 --crate-type lib', '-verbose', '2', 'verified/lib.rs']
    proof = stage(a, root, 'verification', command, proof_env, 240)
    log = (root / 'verification.log').read_text(errors='replace') if (root / 'verification.log').is_file() else ''
    capture_line = re.search(r'(?m)^COMPAT-STRICT-CUT-AST-CAPTURE target=' + re.escape(case) +
                             r' source=verified/lib\.rs immutable_md5=[0-9a-f]{32}$', log)
    capture_ok = (ordinary_off or marker_off or
                  (capture_line is not None and ast_path.is_file() and ast_path.stat().st_size > 0))
    cert['pre_ast_capture_token'] = capture_line.group(0) if capture_line else None
    cert['pre_ast_sha256'] = sha(ast_path) if ast_path.is_file() else None
    cert['pre_ast_capture_ok'] = capture_ok
    write(root / 'source-certificate.json', cert)
    entries = [(match.group(1), match.start()) for match in TRACE_ENTRY.finditer(log)]
    target_entries = [at for name, at in entries if name == case]
    errors = [line for line in log.splitlines() if ': error:' in line or
              line.startswith('Fatal error:') or re.search(r'\): dead code$', line)]
    first_error_at = log.find(errors[0]) if errors else -1
    entry_before_error = bool(target_entries and first_error_at >= 0 and
                              target_entries[0] < first_error_at)
    proof_row = {'state': proof.get('state'), 'exit': proof.get('exit'),
        'target_entries': len(target_entries), 'target_entry_before_first_error': entry_before_error,
        'errors': errors, 'first_error': errors[0] if errors else None,
        'strict_opt_in': proof_env.get('SORT4_STRICT_LFT_CUT') == '1',
        'leak_checks': log.count('Leak check.'),
        'zero_errors_marker': '0 errors found (' in log,
        'return_seen': 'Executing return statement' in log}
    if marker_off:
        proof_row['first_refusal_stage'] = 'translator/static_error' if MARKER_OFF_REFUSAL in log else 'NOT_CONFIRMED'
        proof_row['first_refusal_location'] = errors[0] if errors else None
        proof_row['marker_off_refusal_confirmed'] = (
            proof.get('exit') in (1, 2) and bool(errors) and MARKER_OFF_REFUSAL in errors[0] and not target_entries)
        classification = 'MARKER_OFF_ADMISSION_REFUSAL' if proof_row['marker_off_refusal_confirmed'] else 'MARKER_OFF_REFUSAL_NOT_CONFIRMED'
    elif not ordinary_off:
        refusal = 'COMPAT-STRICT-CUT-AST-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF'
        captured = (capture_ok and proof.get('exit') in (1, 2) and
                    bool(errors) and refusal in errors[0] and not target_entries)
        classification = ('FRESH_AST_CAPTURED_REFUSED_NOT_PROOF' if captured
                          else 'CAPTURE_OR_ADMISSION_BLOCKER')
        proof_row.update(state='NOT_RUN', capture_exit=proof.get('exit'),
                         capture_refusal_confirmed=captured)
    elif case in POSITIVE:
        positive = (capture_ok and proof.get('exit') == 0 and not errors and proof_row['zero_errors_marker'] and
                    proof_row['leak_checks'] > 0 and len(target_entries) == 1 and
                    proof_row['return_seen'])
        proof_row['positive_vf0_candidate'] = positive
        classification = 'POSITIVE_VF0_CANDIDATE_PENDING_REVIEW' if positive else 'POSITIVE_NOT_CONFIRMED'
    elif case in NEGATIVE:
        intended = capture_ok and proof.get('exit') in (1, 2) and entry_before_error and bool(errors)
        proof_row['intended_negative_candidate'] = intended
        proof_row['raw_attribution'] = 'PENDING_INDEPENDENT_FIRST_VC_REVIEW'
        classification = 'NEGATIVE_DIAGNOSTIC_PENDING_RAW_REVIEW' if intended else 'NEGATIVE_NOT_REACHED_OR_SETUP_FAILURE'
    else:
        classification = 'DIAGNOSTIC_ONLY'
    result.update(classification=classification, proof=proof_row)
    write(root / 'case-result.json', result)
    return result


def run(a: argparse.Namespace) -> dict:
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         os.environ.get('LANE') == 'o26-compatible-strict-cut-test' and
         not os.environ.get('GITHUB_ACTIONS'), 'identified compatible-strict-cut Cloud lane required')
    for key in ('production_source', 'production_applied_patch', 'stock_home',
                'compiler_sysroot', 'evidence', 'proof_root', 'work_root', 'cloud_dir'):
        need(str(getattr(a, key)).startswith('/workspace/'),
             f'{key} must be inside /workspace')
    need(not a.evidence.exists(), 'fresh compatible strict-cut evidence directory required')
    a.evidence.mkdir(parents=True)
    need(os.environ.get('PROOF_SHA') and os.environ.get('INFRA_SHA'),
         'pinned proof and infra SHAs are required')
    profile_path = a.proof_root / HERE / 'profile.json'
    profile = json.loads(profile_path.read_text())
    need(profile.get('classification') == 'EXPERIMENTAL_PRODUCTION_COMPATIBLE_STRICT_CUT' and
         profile.get('profile_accepted') is False and profile.get('cloud_enabled') is True and
         profile.get('dispatch_authorized') is True and
         profile.get('diagnostic_mode') == 'CAPTURE_ONLY_NO_STRICT_ON_PROOF',
         'strict-cut profile is not explicitly enabled as an unaccepted experiment')
    need(profile.get('base_translator_sha256') == EXPECTED_TRANSLATOR and
         profile.get('base_kernel_sha256') == EXPECTED_KERNEL,
         'strict-cut profile has a different production base')
    pin_production(a, profile)

    source_patch = a.production_applied_patch
    before_production = {
        'source_head': subprocess.check_output(
            ['git', '-C', str(a.production_source), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_translator_sha256': sha(a.production_source / TRANSLATOR),
        'source_kernel_sha256': sha(a.production_source / KERNEL),
        'source_patch_sha256': sha(source_patch),
        'stock_verifast_sha256': sha(a.stock_home / 'bin/verifast'),
        'sysroot': str(a.compiler_sysroot),
        'proof_sha': os.environ['PROOF_SHA'], 'infra_sha': os.environ['INFRA_SHA'],
    }
    write(a.evidence / 'production-input-pins.json', before_production)

    tool = a.work_root / 'compatible-strict-cut-tool'
    need(not tool.exists(), 'isolated strict-cut tool directory already exists')
    shutil.copytree(a.production_source, tool, symlinks=True)
    patch = a.proof_root / HERE / PATCH_NAME
    pre = snapshot(tool, source_patch, profile)
    write(a.evidence / 'tool-snapshot-before.json', pre)
    install_two_file_patch(tool, patch, profile, a.evidence / 'patch',
                           os.environ.copy(), a)

    deps = a.work_root / 'vfdeps-adf88dc'
    env = os.environ.copy()
    env['PATH'] = os.pathsep.join((str(tool / 'bin'), str(a.stock_home / 'bin'),
                                   str(deps / 'bin'), env.get('PATH', '')))
    env['LD_LIBRARY_PATH'] = os.pathsep.join((str(a.compiler_sysroot / 'lib'),
        str(tool / 'bin'), str(a.stock_home / 'bin'), str(deps / 'lib'),
        env.get('LD_LIBRARY_PATH', '')))
    env['CAPNP_INC_DIR'] = str(deps / 'include')
    env['RUSTUP_TOOLCHAIN'] = 'nightly-2026-09-25'
    for key in list(env):
        if key.startswith(('SORT4_', 'O26_WITH_')):
            env.pop(key, None)
    build = stage(a, a.evidence, 'console-build',
        ['make', '-C', str(tool / 'src'), '../bin/verifast',
         'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'], env, 900)
    need(build.get('exit') == 0, 'isolated strict-cut console build failed')
    after_build = snapshot(tool, source_patch, profile)
    allowed = {TRANSLATOR, KERNEL}
    need(after_build['head'] == pre['head'] and
         all(after_build['critical'][name] == value for name, value in pre['critical'].items()
             if name not in allowed and name != 'bin/verifast') and
         all(after_build['binaries'][name] == value for name, value in pre['binaries'].items()
             if name != 'bin/verifast') and
         after_build['effective_rsspec'] == pre['effective_rsspec'] and
         after_build['production_applied_patch_sha256'] == pre['production_applied_patch_sha256'] and
         after_build['proof_sha'] == pre['proof_sha'] and after_build['infra_sha'] == pre['infra_sha'],
         'strict-cut patch/build changed frozen production inputs')
    need(sha(tool / TRANSLATOR) == profile['patched_translator_sha256'] and
         sha(tool / KERNEL) == profile['patched_kernel_sha256'],
         'strict-cut patched file hashes changed during build')
    write(a.evidence / 'tool-snapshot-after-build.json', after_build)

    template_path = a.proof_root / HERE / 'fixtures.rs'
    template = template_path.read_bytes()
    cases = extract_cases(template)
    common = template[:template.index(b'// CASE_BEGIN')]
    # Hold the unwind callee outside the case list; run_case places it in the
    # same physical source only for the direct-unwind proof case.
    expected = sorted(POSITIVE | NEGATIVE | {'marker_default_off',
                     'negative_wrong_marker', 'negative_duplicate_marker'} |
                     INCONCLUSIVE_SOURCE_FORMS)
    absent = [name for name in expected if name not in cases]
    result_cases = {}
    capture = load_module(a.proof_root / 'research/challenge-8/overnight-sort4/capture.py',
                          'strict_cut_capture')
    schema = tool / 'src/rust_frontend/vf_mir/vf_mir.capnp'
    for case in expected:
        if case not in cases:
            result_cases[case] = {'classification': 'NOT_RUN', 'reason': 'fixture source missing'}
            continue
        if case in INCONCLUSIVE_SOURCE_FORMS:
            result_cases[case] = {'classification': 'NOT_RUN',
                'reason': 'source form does not establish the intended outer escape predicate'}
            continue
        selected = cases[case]
        if case == 'positive_direct_unwind':
            selected = cases['cut_may_unwind'] + b'\n' + selected
        result_cases[case] = run_case(a, tool, profile, common, case,
                                      selected, capture, schema, env)

    # Required semantic and legacy regression gates not yet represented by
    # independently reviewed source forms remain explicitly unrun.
    not_run = {
        'outer_variable_type_escape': 'NOT_RUN: current source form uses a ghost-only lifetime in Rust syntax and does not prove an outer binding survives the cut',
        'outer_bound_escape': 'NOT_RUN: current type_interp assertion does not register tparam_bounds_table metadata',
        'wrong_or_duplicate_marker_semantic_negative': 'NOT_RUN: admission refusals are not target-proof semantic negatives',
        'inferred_alias_and_unresolved_or_cyclic_bounds': 'NOT_RUN: no reviewed isolated source fixture yet',
        'missing_debt_or_missing_owner': 'NOT_RUN: service fixture has no reviewed debt/owner resource protocol',
        'wrong_goto_cfg_ingress_or_reentry': 'NOT_RUN: exact CFG-specific source form not supplied',
        'allocation_initialization_address_free_mutation': 'NOT_RUN: fresh path-level mutation source not supplied',
        'C1_C2_mandatory_unbound_refusals': 'NOT_RUN: frozen C1/C2 experimental patch profiles are not in this production-base tool',
        'stock_pointer_add_lowering': 'NOT_RUN: dedicated fresh pointer-lowering regression has not been staged',
        'frozen_production_tests': 'NOT_RUN: no production-suite command authorized in this isolated service gate',
    }
    outcomes = [row.get('classification') for row in result_cases.values()]
    positives_ok = all(result_cases.get(name, {}).get('proof', {}).get('positive_vf0_candidate') is True
                       for name in POSITIVE)
    marker_gate = result_cases.get('marker_default_off', {}).get('proof', {}).get(
        'marker_off_refusal_confirmed') is True
    core_subset = (positives_ok and marker_gate and all(
        'NEGATIVE_DIAGNOSTIC_PENDING_RAW_REVIEW' == result_cases.get(name, {}).get('classification')
        for name in NEGATIVE))
    result = {
        'classification': 'COMPATIBLE_STRICT_CUT_CAPTURE_ONLY_PARTIAL_OR_BLOCKED',
        'profile_accepted': False, 'native_sort4_composition_credit': False,
        'source_sha': os.environ['PROOF_SHA'], 'infra_sha': os.environ['INFRA_SHA'],
        'tool_profile': profile['classification'], 'two_file_patch_sha256': sha(patch),
        'fresh_case_results': result_cases, 'not_run_required_gates': not_run,
        'fixture_sources_missing': absent, 'case_outcomes': outcomes,
        'core_subset_passed': core_subset,
        'diagnostic_complete': False,
        'completion_blockers': ['required escape, inference, debt/owner, CFG, pointer-lowering, C1/C2 and frozen-production gates remain NOT_RUN or await independent raw attribution'],
        'accepted': False,
    }
    write(a.evidence / 'diagnostic-audit.json', result)
    print(json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ('production-source', 'production-applied-patch', 'stock-home',
                 'compiler-sysroot', 'evidence', 'proof-root', 'work-root', 'cloud-dir'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--deadline-epoch', required=True, type=int)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
