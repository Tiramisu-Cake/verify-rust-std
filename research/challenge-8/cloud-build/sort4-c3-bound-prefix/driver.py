#!/usr/bin/env python3
"""Cloud-only C3 capture/proof driver, inert on import. Never dispatches builds."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path('research/challenge-8/cloud-build/sort4-c3-bound-prefix')
TRANSLATOR = Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def record(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def module(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def stage(a, name, cmd, cwd, env, cap=180, stdin=None, stdout=None):
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    need(seconds > 0, 'deadline before C3 ' + name)
    logpath = a.evidence / ('c3-' + name + '.log')
    resource = a.evidence / ('c3-' + name + '-resources.txt')
    with logpath.open('wb') as log:
        inp = stdin.open('rb') if stdin else subprocess.DEVNULL
        out = stdout.open('wb') if stdout else log
        try:
            code = subprocess.run(['/usr/bin/time', '-v', '-o', str(resource),
                'timeout', '--signal=TERM', '--kill-after=10s', str(seconds) + 's', *cmd],
                cwd=cwd, env={**env, 'PWD': str(cwd)}, stdin=inp, stdout=out,
                stderr=log, check=False).returncode
        finally:
            if stdin: inp.close()
            if stdout: out.close()
    record(a.evidence / ('c3-' + name + '-stage.json'), {
        'argv': cmd, 'cwd': str(cwd), 'exit': code, 'timeout_seconds': seconds,
        'log_sha256': sha(logpath), 'resources': resource.name,
        'stdout_sha256': sha(stdout) if stdout and stdout.exists() else None,
        'proof_credit': False})
    return code, logpath.read_text(errors='replace')

def prepare(a):
    """Cloud-only source splice; never called by local service tests."""
    source = a.evidence / 'c2-discovery-fixture'
    target = a.evidence / 'c3-fixture'
    need(not target.exists(), 'C3 fixture already exists')
    shutil.copytree(source, target, symlinks=True)
    c2 = module(a.cloud_dir / 'sort4-native-entry-c1/c2_discovery.py', 'c3_bytes')
    verified = target / 'verified/lib.rs'
    original = target / 'original/lib.rs'
    text = verified.read_bytes()
    need(sha(verified) == 'ecd83f8c0840a07f138bc8afa2a36c661f296d748693afa2a0a61667cb3372e4',
         'C3 does not follow exact C2 source')
    helper = (a.proof_root / HERE / 'selected-four.rs').read_bytes()
    need(c2.strip_ghost(helper) == b'', 'helper leaves runtime bytes')
    anchor = b'pub unsafe fn sort4_stable'
    need(text.count(anchor) == 1, 'unique sort4 target required')
    text = text.replace(anchor, helper + anchor, 1)
    annotation = (a.proof_root / HERE / 'C3-ANNOTATION.rs').read_bytes()
    start = b'        //@ let cmp3_k = begin_lifetime();'
    need(annotation.count(start) == 1, 'unique C3 annotation start required')
    annotation = annotation[annotation.index(start):]
    call = b'        let c3 = is_less(&*c, &*a);\n'
    need(text.count(call) == 1, 'unique exact C3 call required')
    text = text.replace(call, annotation, 1)
    setup = b'        let a = v_base.add(c1 as usize);'
    need(text.count(setup) == 1, 'exact selected pointer setup required')
    text = text.replace(setup,
        b'        //@ selected_four_limits::<T>(v_base, c1, c2);\n' + setup, 1)
    need(c2.strip_ghost(text) == original.read_bytes(), 'C3 ghost-strip runtime mismatch')
    verified.write_bytes(text)
    cert = {'annotated_source_sha256': sha(verified), 'original_source_sha256': sha(original),
            'helper_sha256': sha(a.proof_root / HERE / 'selected-four.rs'),
            'annotation_sha256': sha(a.proof_root / HERE / 'C3-ANNOTATION.rs'),
            'ghost_strip_byte_identical': True, 'profile_accepted': False,
            'proof_credit': False, 'actual_sort4_callable_summary': False}
    record(a.evidence / 'c3-source-certificate.json', cert)
    return target, cert

def run(a, tool, env, c2_result, snapshot_fn):
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         os.environ.get('LANE') == 'o26-sort4-c1-current-recovery',
         'C3 stages require authorized Cloud lane')
    need(c2_result.get('positive_ok') is True and c2_result.get('positive_exit') == 0,
         'C3 requires fresh completed C2 target')
    profile_path = a.proof_root / HERE / 'capture-profile.json'
    profile = json.loads(profile_path.read_text())
    patch = a.proof_root / HERE / 'verifast-c3-capture-TEST.patch'
    need(sha(tool / TRANSLATOR) == profile['base_translator_sha256'] and
         sha(patch) == profile['incremental_patch_sha256'], 'C3 capture tool/patch identity mismatch')
    before = snapshot_fn(a, tool)
    for mode, cmd in [('patch-check', ['git', '-C', str(tool), 'apply', '--check', str(patch)]),
                      ('patch-apply', ['git', '-C', str(tool), 'apply', str(patch)])]:
        code, _ = stage(a, mode, cmd, tool, env, 60)
        need(code == 0, 'C3 ' + mode + ' failed')
    need(sha(tool / TRANSLATOR) == profile['patched_translator_sha256'], 'patched C3 hash differs')
    active = env.copy()
    deps = a.work_root / 'vfdeps-adf88dc'
    active.update({'PATH': str(deps / 'bin') + os.pathsep + active.get('PATH', ''),
                   'LD_LIBRARY_PATH': ':'.join([str(a.compiler_sysroot / 'lib'),
                       str(tool / 'bin'), str(deps / 'lib'), active.get('LD_LIBRARY_PATH', '')]),
                   'CAPNP_INC_DIR': str(deps / 'include'), 'RUSTUP_TOOLCHAIN': 'nightly-2026-09-25'})
    code, _ = stage(a, 'console-build', ['make', '-C', str(tool / 'src'), '../bin/verifast',
                       'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'], tool, active, 900)
    need(code == 0, 'C3 capture console build failed')
    after = snapshot_fn(a, tool)
    need(after['head'] == before['head'] and
         all(after['binaries'][k] == v for k, v in before['binaries'].items()
             if k != 'bin/verifast') and
         all(after['critical'][k] == v for k, v in before['critical'].items()
             if k != str(TRANSLATOR)) and after['effective_rsspec'] == before['effective_rsspec']
         and after['proof_std'] == before['proof_std'], 'C3 changed frozen non-translator inputs')
    record(a.evidence / 'c3-capture-tool-snapshot.json', after)
    fixture, cert = prepare(a)
    # Independently preserve old C2 positive and mandatory unbound refusal under
    # the new default-off translator, without repeating its historic matrix.
    baseenv = active.copy()
    baseenv.update({'SORT4_ACTUAL_AST_SCOPE_TEST': '1', 'SORT4_ACTUAL_C1_PREFIX_TEST': '0',
        'SORT4_C1_PREFIX_CONTROL': 'none', 'SORT4_C1_OUTPUT_EQ': '0',
        'SORT4_STRICT_LFT_CUT': '1', 'SORT4_ACTUAL_C3_CAPTURE_TEST': '0',
        'SORT4_ACTUAL_C2_DISCOVERY_TEST': '0', 'SORT4_ACTUAL_C2_BOUND_PREFIX_TEST': '1',
        'SORT4_C2_BOUND_CONTROL': 'none'})
    command = [str(tool / 'bin/verifast'), '-rustc_args', '--edition 2021', '-verbose', '2', 'verified/lib.rs']
    oldfixture = a.evidence / 'c2-discovery-fixture'
    code, raw = stage(a, 'default-off-c2', command, oldfixture, baseenv)
    need(code == 0 and '0 errors found (' in raw and 'Leak check.' in raw,
         'C3 default-off C2 regression failed')
    baseenv.update({'SORT4_ACTUAL_C2_BOUND_PREFIX_TEST': '0', 'SORT4_ACTUAL_C2_DISCOVERY_TEST': '1'})
    code, raw = stage(a, 'mandatory-unbound-c2-refusal', command, oldfixture, baseenv)
    need(code in (1,2) and 'UNBOUND_C2_LIFETIME_NOT_PROOF' in raw,
         'C2 mandatory unbound refusal lost')
    capturemod = module(a.proof_root / 'research/challenge-8/overnight-sort4/capture.py', 'c3_graph')
    schema = a.production_source / 'src/rust_frontend/vf_mir/vf_mir.capnp'
    rows = {}
    for mode, args in [('normal', []), ('readonly', ['--vf-rust-mir-exporter:preprocess-readonly'])]:
        binary = a.evidence / f'c3-{mode}-mir.bin'
        text = a.evidence / f'c3-{mode}-mir.txt'
        code, _ = stage(a, mode + '-export', [str(tool / 'bin/vf-rust-mir-exporter'),
            'verified/lib.rs', '--sysroot=' + str(a.compiler_sysroot), '--edition', '2021', *args],
            fixture, active, stdout=binary)
        need(code == 0, 'C3 ' + mode + ' exporter failed')
        code, _ = stage(a, mode + '-decode', ['capnp','decode',str(schema),'VfMir'],
                         fixture, active, stdin=binary, stdout=text)
        need(code == 0, 'C3 ' + mode + ' decode failed')
        rows[mode] = capturemod.graph_inventory(text, a.evidence, 'c3-' + mode)
    code, _ = stage(a, 'refinement', [str(tool / 'bin/refinement-checker'), '--rustc-args',
                 '--edition 2021', 'original/lib.rs', 'verified/lib.rs'], fixture, active)
    need(code == 0, 'C3 refinement failed')
    baseenv.update({'SORT4_ACTUAL_C2_DISCOVERY_TEST': '0', 'SORT4_ACTUAL_C3_CAPTURE_TEST': '1',
                   'SORT4_C3_CAPTURE_SOURCE_SHA256': cert['annotated_source_sha256']})
    code, raw = stage(a, 'capture-refusal', command, fixture, baseenv)
    ast = fixture / 'actual-c3-capture-pre-ast.ml'
    result = {'classification': 'C3_CAPTURE_NOT_CONFIRMED', 'accepted': False,
        'proof_credit': False, 'source': cert, 'mir': rows, 'exit': code,
        'first_errors': [line for line in raw.splitlines() if ': error:' in line or line.startswith('Fatal error:')],
        'target_proof': 'NOT_RUN'}
    if ast.exists():
        shutil.copy2(ast, a.evidence / ast.name)
        result['pre_ast_sha256'] = sha(ast)
    if code in (1,2) and 'FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF' in raw and ast.exists():
        result['classification'] = 'FRESH_C3_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF'
    record(a.evidence / 'c3-result.json', result)
    bound_profile = a.proof_root / HERE / 'profile.json'
    if bound_profile.is_file() and json.loads(bound_profile.read_text()).get('cloud_enabled') is True:
        need(result['classification'] == 'FRESH_C3_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF',
             'C3 bound cannot follow failed/unconfirmed capture')
        bound = module(a.cloud_dir / 'sort4-c3-bound-prefix/bound-driver.py', 'c3_bound')
        service = type('Service', (), {'need': staticmethod(need), 'sha': staticmethod(sha),
            'record': staticmethod(record), 'stage': staticmethod(stage)})
        result['bound'] = bound.run(a, tool, active, result, snapshot_fn, service)
        record(a.evidence / 'c3-result.json', result)
    c4_profile_path = a.proof_root / 'research/challenge-8/cloud-build/sort4-c4-bound-prefix/capture-profile.json'
    if c4_profile_path.is_file():
        c4_profile = json.loads(c4_profile_path.read_text())
        if c4_profile.get('cloud_enabled') is True and c4_profile.get('dispatch_authorized') is True:
            need(result.get('bound', {}).get('positive_ok') is True and
                 result['bound'].get('positive_exit') == 0,
                 'C4 capture requires fresh completed C3 target')
            c4 = module(a.cloud_dir / 'sort4-c4-bound-prefix/driver.py', 'c4_capture')
            result['c4'] = c4.run(a, tool, active, result, snapshot_fn)
            record(a.evidence / 'c3-result.json', result)
    return result
