#!/usr/bin/env python3
"""Cloud-only C4 source/MIR/pre-AST capture; inert on import."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE = Path('research/challenge-8/cloud-build/sort4-c4-bound-prefix')
TRANSLATOR = Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
C3_SOURCE_SHA256 = '087123b12072a19b0490260e509ce6773c1ed3dce0ed7c14c95991fdaf82996e'
C4_BASE_TRANSLATOR_SHA256 = 'd2f132148d409eb9a9e27afd24603d992405ec1984849817da9e427ab070db6e'


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def stage(a, name, command, cwd, env, cap=180, stdin=None, stdout=None):
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    need(seconds > 0, 'deadline before C4 ' + name)
    log_path = a.evidence / ('c4-' + name + '.log')
    resource_path = a.evidence / ('c4-' + name + '-resources.txt')
    with log_path.open('wb') as log:
        input_stream = stdin.open('rb') if stdin else subprocess.DEVNULL
        output_stream = stdout.open('wb') if stdout else log
        try:
            code = subprocess.run(
                ['/usr/bin/time', '-v', '-o', str(resource_path), 'timeout',
                 '--signal=TERM', '--kill-after=10s', str(seconds) + 's', *command],
                cwd=cwd, env={**env, 'PWD': str(cwd)}, stdin=input_stream,
                stdout=output_stream, stderr=log, check=False).returncode
        finally:
            if stdin:
                input_stream.close()
            if stdout:
                output_stream.close()
    record(a.evidence / ('c4-' + name + '-stage.json'), {
        'argv': command, 'cwd': str(cwd), 'exit': code, 'timeout_seconds': seconds,
        'log_sha256': sha(log_path), 'resources': resource_path.name,
        'stdout_sha256': sha(stdout) if stdout and stdout.exists() else None,
        'proof_credit': False})
    return code, log_path.read_text(errors='replace')


def prepare(a):
    """Create an exact C4 ghost-only source fixture in Cloud evidence."""
    source = a.evidence / 'c3-fixture'
    target = a.evidence / 'c4-fixture'
    need(not target.exists(), 'C4 fixture already exists')
    shutil.copytree(source, target, symlinks=True)
    bytes_module = module(a.cloud_dir / 'sort4-native-entry-c1/c2_discovery.py', 'c4_bytes')
    verified = target / 'verified/lib.rs'
    original = target / 'original/lib.rs'
    text = verified.read_bytes()
    need(sha(verified) == C3_SOURCE_SHA256,
         'C4 does not follow the exact reviewed C3 annotated source')
    annotation_path = a.proof_root / HERE / 'C4-ANNOTATION.rs'
    annotation = annotation_path.read_bytes()
    start = b'        //@ let cmp4_k = begin_lifetime();'
    need(annotation.count(start) == 1, 'unique C4 annotation start required')
    annotation = annotation[annotation.index(start):]
    call = b'        let c4 = is_less(&*d, &*b);\n'
    need(text.count(call) == 1, 'unique exact C4 call required')
    text = text.replace(call, annotation, 1)
    need(bytes_module.strip_ghost(text) == original.read_bytes(),
         'C4 ghost-strip runtime mismatch')
    verified.write_bytes(text)
    certificate = {
        'annotated_source_sha256': sha(verified),
        'c3_annotated_source_sha256': C3_SOURCE_SHA256,
        'original_source_sha256': sha(original),
        'annotation_sha256': sha(annotation_path),
        'ghost_strip_byte_identical': True,
        'profile_accepted': False,
        'proof_credit': False,
        'actual_sort4_callable_summary': False,
    }
    record(a.evidence / 'c4-source-certificate.json', certificate)
    return target, certificate


def run(a, tool, env, c3_result, snapshot_fn):
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         os.environ.get('LANE') == 'o26-sort4-c1-current-recovery',
         'C4 capture requires the authorized Cloud lane')
    c3_bound = c3_result.get('bound', c3_result)
    need(c3_bound.get('positive_ok') is True and c3_bound.get('positive_exit') == 0,
         'C4 capture requires a fresh successful C3 bound proof')
    need(c3_result.get('source', {}).get('annotated_source_sha256') == C3_SOURCE_SHA256,
         'C4 capture requires the exact fresh C3 annotated source certificate')

    profile_path = a.proof_root / HERE / 'capture-profile.json'
    profile = json.loads(profile_path.read_text())
    need(profile.get('classification') == 'C4_CAPTURE_ONLY_FULL_ORIGINAL_AST_NOT_PROOF' and
         profile.get('cloud_enabled') is True and
         profile.get('dispatch_authorized') is True,
         'C4 capture profile is not explicitly Cloud-enabled and authorized')
    need(profile.get('c3_full_verdict') == 'INDEPENDENT_RAW_REVIEW_PASS',
         'C4 capture requires the pinned full C3 review verdict')
    review_name = profile.get('c3_review_file')
    need(isinstance(review_name, str) and
         re.fullmatch(r'FRESH-[A-F0-9]{8}-REVIEW\.md', review_name) is not None,
         'C3 review filename must be a pinned fresh Build review basename')
    review_path = (a.proof_root /
        'research/challenge-8/cloud-build/sort4-c3-bound-prefix' / review_name)
    need(review_path.is_file(), 'Pinned fresh C3 raw review file is missing')
    review_text = review_path.read_text()
    review_build_id = profile.get('c3_review_build_id')
    need(isinstance(review_build_id, str) and review_build_id.strip() and
         review_build_id in review_text and
         profile.get('c3_review_sha256') == sha(review_path),
         'C3 review Build ID or exact review-file SHA pin differs')
    c3_profile = json.loads((a.proof_root /
        'research/challenge-8/cloud-build/sort4-c3-bound-prefix/profile.json').read_text())
    expected_controls = c3_profile.get('controls')
    controls = c3_bound.get('controls')
    # These checks establish that reviewed raw cases exist and reached the
    # target; only the hash-pinned independent review assigns their semantics.
    need(isinstance(expected_controls, list) and isinstance(controls, dict) and
         set(controls) == set(expected_controls) and
         all(controls[name].get('exit') in (1, 2) and
             controls[name].get('target_entry_before_first_error') is True
             for name in expected_controls),
         'Fresh C3 result is missing a reviewed-target control failure')
    source_mutant = c3_bound.get('source_mutant')
    need(isinstance(source_mutant, dict) and
         source_mutant.get('target_proof_entries') == 0,
         'Fresh C3 source mutant reached target proof')
    patch = a.proof_root / HERE / 'verifast-c4-capture-TEST.patch'
    need(profile['base_translator_sha256'] == C4_BASE_TRANSLATOR_SHA256 and
         sha(tool / TRANSLATOR) == C4_BASE_TRANSLATOR_SHA256 and
         sha(patch) == profile['incremental_patch_sha256'],
         'C4 capture base translator or incremental patch identity mismatch')

    before = snapshot_fn(a, tool)
    c3_snapshot_path = a.evidence / 'c3-bound-tool-snapshot.json'
    need(c3_snapshot_path.is_file() and
         json.loads(c3_snapshot_path.read_text()) == before,
         'Current tool snapshot differs from the reviewed C3 bound snapshot')
    for label, args in (('patch-check', ['--check']), ('patch-apply', [])):
        command = ['git', '-C', str(tool), 'apply', *args, str(patch)]
        code, _ = stage(a, label, command, tool, env, 60)
        need(code == 0, 'C4 ' + label + ' failed')
    need(sha(tool / TRANSLATOR) == profile['patched_translator_sha256'],
         'patched C4 capture translator hash differs')

    active = env.copy()
    deps = a.work_root / 'vfdeps-adf88dc'
    active.update({
        'PATH': str(deps / 'bin') + os.pathsep + active.get('PATH', ''),
        'LD_LIBRARY_PATH': ':'.join([str(a.compiler_sysroot / 'lib'),
            str(tool / 'bin'), str(deps / 'lib'), active.get('LD_LIBRARY_PATH', '')]),
        'CAPNP_INC_DIR': str(deps / 'include'),
        'RUSTUP_TOOLCHAIN': 'nightly-2026-09-25',
    })
    code, _ = stage(a, 'console-build',
        ['make', '-C', str(tool / 'src'), '../bin/verifast',
         'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'], tool, active, 900)
    need(code == 0, 'C4 capture console build failed')
    after = snapshot_fn(a, tool)
    need(after['head'] == before['head'] and
         all(after['binaries'][key] == value
             for key, value in before['binaries'].items() if key != 'bin/verifast') and
         all(after['critical'][key] == value
             for key, value in before['critical'].items() if key != str(TRANSLATOR)) and
         after['effective_rsspec'] == before['effective_rsspec'] and
         after['proof_std'] == before['proof_std'],
         'C4 capture changed frozen non-translator inputs')
    record(a.evidence / 'c4-capture-tool-snapshot.json', after)

    fixture, certificate = prepare(a)
    command = [str(tool / 'bin/verifast'), '-rustc_args', '--edition 2021',
               '-verbose', '2', 'verified/lib.rs']
    base_env = active.copy()
    base_env.update({
        'SORT4_ACTUAL_AST_SCOPE_TEST': '1',
        'SORT4_ACTUAL_C1_PREFIX_TEST': '0',
        'SORT4_C1_PREFIX_CONTROL': 'none',
        'SORT4_C1_OUTPUT_EQ': '0',
        'SORT4_STRICT_LFT_CUT': '1',
        'SORT4_ACTUAL_C2_DISCOVERY_TEST': '0',
        'SORT4_ACTUAL_C2_BOUND_PREFIX_TEST': '0',
        'SORT4_C2_BOUND_CONTROL': 'none',
        'SORT4_ACTUAL_C3_CAPTURE_TEST': '0',
        'SORT4_C3_CAPTURE_SOURCE_SHA256': '',
        'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST': '0',
        'SORT4_C3_BOUND_CONTROL': 'none',
        'SORT4_ACTUAL_C4_CAPTURE_TEST': '0',
        'SORT4_C4_CAPTURE_SOURCE_SHA256': '',
        'SORT4_ACTUAL_C4_BOUND_PREFIX_TEST': '0',
        'SORT4_C4_BOUND_CONTROL': 'none',
    })

    # Reconfirm C3 remains available with C4 capture/bound modes off.
    base_env.update({'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST': '1'})
    c3_fixture = a.evidence / 'c3-fixture'
    code, raw = stage(a, 'c3-positive-regression', command, c3_fixture, base_env)
    need(code == 0 and '0 errors found (' in raw and 'Leak check.' in raw,
         'C4 capture changed the C3 VF0 regression')

    # Preserve the mandatory unbound C3 capture refusal as a separate case.
    base_env.update({'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST': '0',
                     'SORT4_ACTUAL_C3_CAPTURE_TEST': '1',
                     'SORT4_C3_CAPTURE_SOURCE_SHA256': C3_SOURCE_SHA256})
    c3_pre_ast = c3_fixture / 'actual-c3-capture-pre-ast.ml'
    c3_pre_ast.unlink(missing_ok=True)
    code, raw = stage(a, 'unbound-c3-refusal', command,
                      c3_fixture, base_env)
    need(code in (1, 2) and 'FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF' in raw and
         'Verifying function \'sort4_stable\'' not in raw,
         'C3 mandatory unbound capture refusal lost')

    # C4 capture is a source/MIR/pre-AST diagnostic and must refuse before proof.
    base_env.update({'SORT4_ACTUAL_C3_CAPTURE_TEST': '0',
                     'SORT4_C3_CAPTURE_SOURCE_SHA256': '',
                     'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST': '0',
                     'SORT4_ACTUAL_C4_CAPTURE_TEST': '0',
                     'SORT4_C4_CAPTURE_SOURCE_SHA256': ''})
    capture_mod = module(a.proof_root / 'research/challenge-8/overnight-sort4/capture.py',
                         'c4_graph')
    schema = a.production_source / 'src/rust_frontend/vf_mir/vf_mir.capnp'
    inventories = {}
    for mode, args in (('normal', []),
                       ('readonly', ['--vf-rust-mir-exporter:preprocess-readonly'])):
        binary = a.evidence / f'c4-{mode}-mir.bin'
        decoded = a.evidence / f'c4-{mode}-mir.txt'
        code, _ = stage(a, mode + '-export',
            [str(tool / 'bin/vf-rust-mir-exporter'), 'verified/lib.rs',
             '--sysroot=' + str(a.compiler_sysroot), '--edition', '2021', *args],
            fixture, base_env, stdout=binary)
        need(code == 0, 'C4 ' + mode + ' MIR export failed')
        code, _ = stage(a, mode + '-decode',
            ['capnp', 'decode', str(schema), 'VfMir'], fixture, base_env,
            stdin=binary, stdout=decoded)
        need(code == 0, 'C4 ' + mode + ' MIR decode failed')
        inventories[mode] = capture_mod.graph_inventory(decoded, a.evidence, 'c4-' + mode)

    code, _ = stage(a, 'refinement',
        [str(tool / 'bin/refinement-checker'), '--rustc-args', '--edition 2021',
         'original/lib.rs', 'verified/lib.rs'], fixture, base_env)
    need(code == 0, 'C4 capture refinement failed')

    capture_env = base_env.copy()
    capture_env.update({'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST': '0',
                        'SORT4_ACTUAL_C4_CAPTURE_TEST': '1',
                        'SORT4_C4_CAPTURE_SOURCE_SHA256': certificate['annotated_source_sha256']})
    pre_ast_name = profile.get('pre_ast', 'actual-c4-capture-pre-ast.ml')
    pre_ast = fixture / pre_ast_name
    pre_ast.unlink(missing_ok=True)
    code, raw = stage(a, 'capture-refusal', command, fixture, capture_env)
    result = {
        'classification': 'C4_CAPTURE_NOT_CONFIRMED',
        'accepted': False,
        'proof_credit': False,
        'target_proof': 'NOT_RUN',
        'source': certificate,
        'mir': inventories,
        'exit': code,
        'first_errors': [line for line in raw.splitlines()
                         if ': error:' in line or line.startswith('Fatal error:')],
    }
    if pre_ast.exists():
        shutil.copy2(pre_ast, a.evidence / pre_ast.name)
        result['pre_ast_sha256'] = sha(pre_ast)
    expected_refusal = profile.get('expected_refusal',
        'SORT4-C4-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF')
    if (code in (1, 2) and expected_refusal in raw and pre_ast.exists() and
            'Verifying function \'sort4_stable\'' not in raw):
        result['classification'] = 'FRESH_C4_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF'
    record(a.evidence / 'c4-result.json', result)

    # Optional later bound phase is admitted only from a verified fresh capture.
    bound_profile_path = a.proof_root / HERE / 'profile.json'
    if (bound_profile_path.is_file() and
            json.loads(bound_profile_path.read_text()).get('cloud_enabled') is True):
        need(result['classification'] ==
             'FRESH_C4_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF',
             'C4 bound gate cannot follow an unverified capture')
        bound = module(a.cloud_dir / 'sort4-c4-bound-prefix/bound-driver.py', 'c4_bound')
        service = type('Service', (), {'need': staticmethod(need), 'sha': staticmethod(sha),
            'record': staticmethod(record), 'stage': staticmethod(stage)})
        result['bound'] = bound.run(a, tool, active, result, snapshot_fn, service)
        record(a.evidence / 'c4-result.json', result)
    return result
