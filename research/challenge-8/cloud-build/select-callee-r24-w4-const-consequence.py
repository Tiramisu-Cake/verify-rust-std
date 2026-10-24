#!/usr/bin/env python3
"""Run and audit the checked W4 const-pointer post consequence.

This component consumes a separately completed const eight-row matrix, then
checks one ordinary post consequence and its missing-premise control with the
same current VeriFast tool identity. It does not establish call linkage or
acceptance. The source precondition uses the callee's actual ``as pointer``
equality and frames ``t == currentThread`` plus ``type_interp::<Element>()``;
the verified body opens only empty ``raw_ptr_own`` and attempts the stronger
typed ``selected == conditional`` conclusion. It establishes no pointee
ownership.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import traceback
import uuid
from typing import Any


SCHEMA = 'select-r24-w4-const-consequence-v1'
AUDIT_SCHEMA = 'select-r24-w4-const-consequence-audit-v1'
SUMMARY_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json')
AUDIT_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE-AUDIT.json')
MATRIX_SUMMARY_REL = Path('cases/r21-fractional-proof/r21-fractional-proof.json')
MATRIX_AUDIT_REL = Path('const-regression-audit.json')
DIAG_REL = Path('select-callee-r24-w4-linkage-diagnostic.py')
DIAG_SHA256 = 'd10258f170072392a65773f609bfe8b7de6ca7625eaa5e176e710483cb7f80b0'
CAPTURE_REL = Path('research/challenge-8/overnight-sort4/capture.py')
CAPTURE_SHA256 = '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'
MODEL_REL = Path('bin/rust/rust_belt/general.rsspec')
MODEL_SHA256 = 'ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d'
MODEL_LINES = (
    b'pred_ctor raw_ptr_own<T>()(t: thread_id_t, v: *T;) = true;',
    b'type_pred_def for <T> <*T>.own = raw_ptr_own::<T>;',
)
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
R24_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
STAGES = (
    'normal-export', 'readonly-export', 'normal-decode', 'readonly-decode',
    'refinement', 'consequence-proof', 'omit-result-relation-proof',
)
FUNCTION = 'select_w4_const_post_consequence'
NEGATIVE_FUNCTION = FUNCTION
SUCCESS_FOOTER = ' (target: x86_64-unknown-linux-gnu (LP64))'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-W4-CONST-CONSEQUENCE: ' + message)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def require_compiler_sysroot(args: argparse.Namespace) -> None:
    value = getattr(args, 'compiler_sysroot', None)
    need(isinstance(value, (str, Path)) and bool(str(value).strip()),
         'compiler sysroot is required for exact stage identity')


def _load(path: Path, name: str, expected_sha: str):
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected_sha,
         'pinned helper missing/changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'cannot load helper: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected_sha, 'helper changed during import: ' + str(path))
    return module


def load_diag(cloud_dir: Path):
    return _load(cloud_dir / DIAG_REL, 'r24_w4_const_consequence_diag', DIAG_SHA256)


def load_capture(repo: Path):
    return _load(repo / CAPTURE_REL, 'r24_w4_const_consequence_capture', CAPTURE_SHA256)


def _build_id() -> str:
    value = os.environ.get('CLOUD_BUILD_ID')
    need(isinstance(value, str) and bool(value), 'native CLOUD_BUILD_ID missing')
    try:
        canonical = str(uuid.UUID(value))
    except (ValueError, AttributeError) as exc:
        raise RuntimeError('R24-W4-CONST-CONSEQUENCE: invalid native CLOUD_BUILD_ID') from exc
    need(canonical == value.lower(), 'native CLOUD_BUILD_ID is not canonical')
    return canonical


def _validate_matrix(evidence: Path, args: argparse.Namespace, native_id: str,
                     summary_arg: object = None, audit_arg: object = None) -> dict[str, Any]:
    summary_path = evidence / MATRIX_SUMMARY_REL
    audit_path = evidence / MATRIX_AUDIT_REL
    need(summary_path.is_file() and not summary_path.is_symlink(),
         'completed const matrix summary missing/unsafe')
    need(audit_path.is_file() and not audit_path.is_symlink(),
         'const matrix physical audit missing/unsafe')
    summary_raw, audit_raw = summary_path.read_bytes(), audit_path.read_bytes()
    summary, audit = json.loads(summary_raw), json.loads(audit_raw)
    need(isinstance(summary, dict) and isinstance(audit, dict),
         'const matrix records must be JSON objects')
    if summary_arg is not None:
        need(summary == summary_arg, 'supplied const matrix summary differs from physical record')
    if audit_arg is not None:
        need(audit == audit_arg, 'supplied const matrix audit differs from physical record')
    need(summary.get('schema') == 'r21-fractional-classified-proof-v1' and
         summary.get('complete') is True and summary.get('body_proof_run') is True and
         summary.get('accepted') is False and summary.get('proof_credit') is False,
         'const eight-row proof matrix is incomplete or crosses proof boundary')
    need(summary.get('current_build_id') == native_id and
         summary.get('r24_session_phase_id') == R24_PHASE and
         summary.get('tool_home') == str(Path(args.native_tool_home).resolve()),
         'const matrix Build/phase/native tool identity differs')
    need(summary.get('variant_order') == list(VARIANTS),
         'const matrix variant order differs')
    rows = summary.get('rows')
    need(isinstance(rows, dict) and set(rows) == set(VARIANTS),
         'const matrix row inventory differs')
    for variant in VARIANTS:
        row = rows[variant]
        need(isinstance(row, dict) and row.get('status') == 'COMPLETE' and
             row.get('source_intact_after_stages') is True and
             isinstance(row.get('stage'), dict) and
             row['stage'].get('argv', [None])[0] ==
             str(Path(args.native_tool_home).resolve() / 'bin/verifast'),
             'const matrix row is incomplete or uses a different native verifier: ' + variant)
    need(audit.get('schema') == 'r21-fractional-proof-audit-v1' and
         audit.get('evidence_complete') is True and
         audit.get('fractional_proof_status') == 'object' and
         audit.get('fractional_proof') == summary and
         audit.get('accepted') is False and audit.get('verification_accepted') is False and
         audit.get('proof_credit') is False,
         'const matrix physical audit is incomplete or mismatched')
    return {
        'summary_path': MATRIX_SUMMARY_REL.as_posix(),
        'summary_sha256': sha(summary_raw),
        'audit_path': MATRIX_AUDIT_REL.as_posix(),
        'audit_sha256': sha(audit_raw),
        'schema': summary['schema'],
        'audit_schema': audit['schema'],
        'native_build_id': native_id,
        'native_tool_home': summary['tool_home'],
        'variant_order': list(VARIANTS),
        'all_eight_rows_complete': True,
    }


def _source(name: str, include_relation: bool) -> bytes:
    relation_req = (
        b'    (selected as pointer) ==\n'
        b'        (if condition { true_val as pointer } else { false_val as pointer }) &*&\n'
        if include_relation else b''
    )
    return (b'#![allow(dead_code)]\n\n'
        # This isolated proof helper needs its exact explicit generic contract.
        # A safe Rust function receives a generated safety-template contract,
        # which cannot supply this explicit type_interp frame during prototype
        # compatibility checking. Unsafe here changes only this proof fixture;
        # its body is still checked under the written req/ens.
        + f'pub unsafe fn {name}<Element>(\n'.encode()
        + b'    condition: bool,\n'
        + b'    true_val: *const Element,\n'
        + b'    false_val: *const Element,\n'
        + b'    selected: *const Element,\n'
        + b')\n/*@\n'
        + b'req thread_token(?t) &*& t == currentThread &*& type_interp::<Element>() &*&\n'
        + relation_req
        + b'    raw_ptr_own::<Element>()(t, selected);\n'
        + b'@*/\n/*@\n'
        + b'ens thread_token(t) &*& t == currentThread &*& type_interp::<Element>() &*& '
        + b'selected == (if condition { true_val } else { false_val });\n'
        + b'@*/\n/*@ on_unwind_ens false; @*/\n'
        + b'{\n    //@ open raw_ptr_own::<Element>()(t, selected);\n}\n')


def _strip_ghost(verified: bytes) -> bytes:
    # Fixtures contain non-nested block annotations and line ghost commands.
    # Preserve line endings so source locations remain stable in both files.
    without_blocks = re.sub(
        rb'/\*@.*?@\*/',
        lambda match: b'\n' * match.group(0).count(b'\n'),
        verified, flags=re.S)
    without_blocks = re.sub(rb'(?m)^[ \t]+(?=\r?$)', b'', without_blocks)
    return re.sub(
        rb'(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)',
        lambda match: (b'\r\n' if match.group(0).endswith(b'\r\n') else
                       b'\n' if match.group(0).endswith(b'\n') else b''),
        without_blocks)


def commands_for(args: argparse.Namespace, *, negative: bool = False) -> dict[str, tuple[list[str], str | None, str]]:
    tool = Path(args.native_tool_home).resolve()
    exporter = str(tool / 'bin/vf-rust-mir-exporter')
    verifier = str(tool / 'bin/verifast')
    schema = str(Path(args.schema).resolve())
    sysroot = str(Path(args.compiler_sysroot).resolve())
    proof_name = 'omit-result-relation-proof' if negative else 'consequence-proof'
    function = NEGATIVE_FUNCTION if negative else FUNCTION
    ast_name = 'omit-result-relation.ast.ml' if negative else 'consequence.ast.ml'
    return {
        'normal-export': ([exporter, 'verified/lib.rs',
            f'--sysroot={sysroot}', '--edition', '2021'], None, 'normal-mir.bin'),
        'readonly-export': ([exporter, 'verified/lib.rs',
            f'--sysroot={sysroot}', '--edition', '2021', '--crate-type', 'lib',
            '--vf-rust-mir-exporter:preprocess-readonly'], None, 'readonly-mir.bin'),
        'normal-decode': (['capnp', 'decode', schema, 'VfMir'], 'normal-mir.bin', 'normal-mir.txt'),
        'readonly-decode': (['capnp', 'decode', schema, 'VfMir'], 'readonly-mir.bin', 'readonly-mir.txt'),
        'refinement': ([str(tool / 'bin/refinement-checker'), '--rustc-args',
            '--edition 2021', 'original/lib.rs', 'verified/lib.rs'], None, 'refinement.log'),
        proof_name: ([verifier, '-rustc_args', '--edition 2021', '-verbose', '1',
            '-dump_ast_with_locs', ast_name, 'verified/lib.rs'], None,
            'omit-result-relation-proof.log' if negative else 'consequence-proof.log'),
    }


def _regular(diag, root: Path, path: Path) -> bool:
    return bool(diag._regular_under(root, path))


def _strict_text(path: Path) -> str:
    return path.read_bytes().decode('utf-8', errors='strict')


def _expected_stage_names(negative: bool) -> tuple[str, ...]:
    return STAGES[:5] + (('omit-result-relation-proof',) if negative else ('consequence-proof',))


def _error_lines(text: str) -> list[tuple[int, str]]:
    found = []
    for line in text.splitlines():
        match = re.match(r'^verified/lib\.rs\(([1-9][0-9]*),[1-9][0-9]*-[1-9][0-9]*\): error: (.+)$', line)
        if match:
            found.append((int(match.group(1)), match.group(2)))
    return found


def _normal_post_line(verified: bytes) -> int:
    marker = b'ens thread_token(t) &*&'
    need(verified.count(marker) == 1, 'postcondition anchor missing or ambiguous')
    return verified[:verified.index(marker)].count(b'\n') + 1


def _verify_log(case: Path, stage: dict[str, Any], *, negative: bool,
                verified: bytes, expected_stdout: str, expected_stderr: str) -> dict[str, Any]:
    prefix = NEGATIVE_FUNCTION if negative else FUNCTION
    need(stage.get('stdout') == expected_stdout and stage.get('stderr') == expected_stderr,
         'proof stdout/stderr targets differ')
    stdout = _strict_text(case / expected_stdout)
    stderr = _strict_text(case / expected_stderr)
    text = stdout + '\n' + stderr
    headers = re.findall(
        r"(?m)^\s*[0-9]+(?:\.[0-9]+)?s: verified/lib\.rs\([^)]*\): Verifying function '" +
        re.escape(prefix) + r"'\s*$", text)
    need(len(headers) == 1, 'proof function header absent or ambiguous: ' + prefix)
    need(not re.search(r'(?im)fatal error|exception|verification failed|timed out|killed by signal', text),
         'unexpected proof error/exception/timeout')
    errors = _error_lines(text)
    if negative:
        expected_line = _normal_post_line(verified)
        need(len(re.findall(r'(?i)\berror:', text)) == 1,
             'omit-relation control contains another diagnostic error')
        need(stage.get('exit') == 1 and len(errors) == 1 and errors[0][0] == expected_line and
             re.search(r'(?i)cannot prove|no matching heap chunks', errors[0][1]) is not None,
             'omit-relation control did not fail uniquely at its normal post')
        need(re.search(r'(?m)^0 errors found \(', text) is None,
             'omit-relation control unexpectedly verified')
        return {'header_count': 1, 'error_count': 1, 'normal_post_error_line': expected_line,
                'log_sha256': sha((case / expected_stdout).read_bytes()),
                'stderr_sha256': sha((case / expected_stderr).read_bytes())}
    need(stage.get('exit') == 0 and not errors, 'positive consequence verifier did not succeed')
    need(re.search(
        r'(?m)^0 errors found \([1-9][0-9]* statements verified\)' +
        re.escape(SUCCESS_FOOTER) + r'$', text) is not None,
         'positive checked-body success summary/target missing')
    need(not re.search(r'(?im)error:', text), 'positive proof log contains an error')
    return {'header_count': 1, 'error_count': 0,
            'log_sha256': sha((case / expected_stdout).read_bytes()),
            'stderr_sha256': sha((case / expected_stderr).read_bytes())}


def _case_inventory(diag, evidence: Path, case: Path, report_path: Path) -> list[dict[str, Any]]:
    need(_regular(diag, evidence, case / 'original/lib.rs') and
         _regular(diag, evidence, case / 'verified/lib.rs'), 'fixture sources missing or unsafe')
    rows = []
    for path in sorted(case.rglob('*')):
        need(not path.is_symlink(), 'fixture artifact symlink: ' + str(path))
        if path.is_file():
            raw = path.read_bytes()
            rows.append({'path': path.relative_to(evidence).as_posix(),
                         'bytes': len(raw), 'sha256': sha(raw)})
        elif not path.is_dir():
            need(False, 'fixture contains non-regular artifact: ' + str(path))
    return rows


def _validate_case(diag, args: argparse.Namespace, evidence: Path, case: Path,
                   name: str, *, negative: bool) -> dict[str, Any]:
    original_path, verified_path = case / 'original/lib.rs', case / 'verified/lib.rs'
    need(_regular(diag, evidence, original_path) and _regular(diag, evidence, verified_path),
         name + ' source pair missing/unsafe')
    original, verified = original_path.read_bytes(), verified_path.read_bytes()
    expected_verified = _source(NEGATIVE_FUNCTION if negative else FUNCTION,
                               include_relation=not negative)
    need(verified == expected_verified and _strip_ghost(verified) == original,
         name + ' exact source/ghost-strip binding differs')
    source_hashes = {'original/lib.rs': sha(original), 'verified/lib.rs': sha(verified)}
    commands = commands_for(args, negative=negative)
    stages: dict[str, Any] = {}
    for stage_name in _expected_stage_names(negative):
        stage_path = case / (stage_name + '-stage.json')
        need(_regular(diag, evidence, stage_path), name + ' stage missing/unsafe: ' + stage_name)
        row = json.loads(stage_path.read_text(encoding='utf-8'))
        need(isinstance(row, dict), name + ' stage has wrong type: ' + stage_name)
        command_name = stage_name
        argv, stdin_name, stdout_name = commands[command_name]
        expected_stderr = stage_name + '-stderr.log'
        need(row.get('argv') == argv and row.get('stdout') == stdout_name and
             row.get('stderr') == expected_stderr, name + ' stage command/output differs: ' + stage_name)
        need(row.get('fixture_before') == source_hashes and row.get('fixture_after') == source_hashes and
             row.get('fixture_integrity') is True, name + ' stage source snapshot differs: ' + stage_name)
        need(type(row.get('exit')) is int and type(row.get('timeout_seconds')) is int and
             1 <= row['timeout_seconds'] <= 1200,
             name + ' stage missing/timeout/wrong result: ' + stage_name)
        need(_regular(diag, evidence, case / stdout_name) and
             _regular(diag, evidence, case / expected_stderr),
             name + ' stage stdout/stderr missing: ' + stage_name)
        stdout_path, stderr_path = case / stdout_name, case / expected_stderr
        if stage_name in ('normal-decode', 'readonly-decode', 'refinement'):
            _strict_text(stdout_path); _strict_text(stderr_path)
        expected_exit = 1 if stage_name == 'omit-result-relation-proof' else 0
        need(row['exit'] == expected_exit, name + ' stage did not have expected exit: ' + stage_name)
        stages[stage_name] = row
    for stage_name in ('normal-export', 'readonly-export', 'normal-decode',
                       'readonly-decode', 'refinement'):
        need(stages[stage_name]['exit'] == 0, name + ' source preparation stage failed: ' + stage_name)
    proof_name = 'omit-result-relation-proof' if negative else 'consequence-proof'
    proof = stages[proof_name]
    proof_stdout = proof['stdout']; proof_stderr = proof['stderr']
    need(_regular(diag, evidence, case / ('omit-result-relation.ast.ml' if negative
         else 'consequence.ast.ml')), name + ' verifier AST artifact missing/unsafe')
    ast_path = case / ('omit-result-relation.ast.ml' if negative else 'consequence.ast.ml')
    ast_raw = ast_path.read_bytes()
    need(bool(ast_raw), name + ' verifier AST artifact is empty')
    ast_raw.decode('utf-8', errors='strict')
    proof_log = _verify_log(case, proof, negative=negative, verified=verified,
                            expected_stdout=proof_stdout, expected_stderr=proof_stderr)
    return {'name': name, 'source_hashes': source_hashes, 'source_unchanged': True,
            'stages': stages, 'checked_body_run': True,
            'classification': ('EXPECTED_NORMAL_POST_FAILURE' if negative else
                               'CHECKED_CONSEQUENCE_SOURCE_REPORTED'),
            'proof_log': proof_log,
            'ast': {'path': ast_path.name, 'bytes': len(ast_raw), 'sha256': sha(ast_raw)},
            'artifact_inventory': _case_inventory(diag, evidence, case, evidence / SUMMARY_REL)}


def _context(args: argparse.Namespace, diag) -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
    require_compiler_sysroot(args)
    need(isinstance(args.candidate, str) and re.fullmatch(r'[0-9a-f]{40}', args.candidate) is not None,
         'exact lowercase candidate SHA required')
    need(type(args.deadline_epoch) is int and args.deadline_epoch > 0,
         'valid shared deadline required')
    roots = diag._validate_context(args)
    route = diag._validate_route()
    repo, cloud, evidence, tool_home, native_tool_home = roots
    need(Path(args.schema).is_file() and not Path(args.schema).is_symlink(),
         'current same-tool VfMir schema missing')
    schema_sha = sha(Path(args.schema).read_bytes())
    need(schema_sha == diag.TOOL_HASHES['src/rust_frontend/vf_mir/vf_mir.capnp'],
         'same-tool VfMir schema hash differs')
    need(Path(args.mode_file).is_file() and not Path(args.mode_file).is_symlink() and
         Path(args.capture_mode_file).is_file() and not Path(args.capture_mode_file).is_symlink(),
         'outer qualification/capture mode inputs missing')
    frozen_tool = diag._tool_hashes(tool_home)
    native_tool = diag._native_tool_identity(native_tool_home)
    model = native_tool_home / MODEL_REL
    need(model.is_file() and not model.is_symlink() and sha(model.read_bytes()) == MODEL_SHA256,
         'current native raw-pointer model pin differs')
    model_raw = model.read_bytes()
    for line in MODEL_LINES:
        need(model_raw.count(line) == 1, 'raw-pointer model definition differs')
    return {'repo': repo, 'cloud': cloud, 'evidence': evidence,
            'tool_home': tool_home, 'native_tool_home': native_tool_home}, route, {
                'schema_sha256': schema_sha, 'model_sha256': sha(model_raw),
                'frozen_tool_identity_sha256': sha(json.dumps(frozen_tool, sort_keys=True).encode()),
                'native_tool_identity_sha256': sha(json.dumps(native_tool, sort_keys=True).encode())}


def _matrix_inputs(evidence: Path, args, native_id: str, summary=None, audit=None):
    return _validate_matrix(evidence, args, native_id, summary, audit)


def _initial(args: argparse.Namespace) -> dict[str, Any]:
    return {'schema': SCHEMA, 'complete': False,
            'classification': 'INCOMPLETE_W4_CONST_CONSEQUENCE',
            'candidate': args.candidate, 'native_build_id': None,
            'scope': 'SOURCE_REPORTED_CHECKED_POST_CONSEQUENCE_ONLY',
            'body_proof_run': False, 'call_linkage': 'UNKNOWN',
            'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
            'failed_stage': 'preflight', 'errors': [], 'artifact_inventory': []}


def run(args: argparse.Namespace, *, diag=None, stage=None,
        const_matrix_summary: dict[str, Any] | None = None,
        const_matrix_audit: dict[str, Any] | None = None) -> dict[str, Any]:
    diag = diag or load_diag(Path(args.cloud_dir))
    roots, route, _ids = _context(args, diag)
    repo, cloud, evidence = roots['repo'], roots['cloud'], roots['evidence']
    tool_home, native_tool_home = roots['tool_home'], roots['native_tool_home']
    output = evidence / SUMMARY_REL
    need(not output.exists() and not output.is_symlink(), 'fresh consequence output required')
    report = _initial(args)
    report['route'] = route
    write_json(output, report)
    try:
        native_id = _build_id()
        matrix = _matrix_inputs(evidence, args, native_id,
                                const_matrix_summary, const_matrix_audit)
        report.update(native_build_id=native_id, const_matrix=matrix)
        report['failed_stage'] = 'fixture-setup'
        write_json(output, report)
        model = native_tool_home / MODEL_REL
        case_root = evidence / SUMMARY_REL.parent
        case_root.mkdir(parents=True, exist_ok=True)
        cases = {}
        for name, negative in (('positive', False), ('omit-result-relation', True)):
            case = case_root / name
            (case / 'original').mkdir(parents=True)
            (case / 'verified').mkdir()
            verified = _source(NEGATIVE_FUNCTION if negative else FUNCTION,
                               include_relation=not negative)
            original = _strip_ghost(verified)
            (case / 'original/lib.rs').write_bytes(original)
            (case / 'verified/lib.rs').write_bytes(verified)
            cases[name] = {'path': case, 'negative': negative}
        report['sources'] = {
            name: {'original_sha256': sha((item['path'] / 'original/lib.rs').read_bytes()),
                   'verified_sha256': sha((item['path'] / 'verified/lib.rs').read_bytes()),
                   'ghost_strip_identity': True}
            for name, item in cases.items()}
        write_json(output, report)
        if stage is None:
            capture = load_capture(repo)
            stage = capture.run_stage
        before_native = diag._native_tool_identity(native_tool_home)
        before_frozen = diag._tool_hashes(tool_home)
        env = dict(os.environ)
        env['PATH'] = str(native_tool_home / 'bin') + os.pathsep + env.get('PATH', '')
        report.update(native_tool_identity_before=before_native,
                      frozen_tool_identity_before=before_frozen,
                      model={'path': MODEL_REL.as_posix(), 'sha256': MODEL_SHA256},
                      source_stage_inventory={}, tool_identity_after_each_stage=[])
        for name, item in cases.items():
            case, negative = item['path'], item['negative']
            source_hashes = {'original/lib.rs': sha((case / 'original/lib.rs').read_bytes()),
                             'verified/lib.rs': sha((case / 'verified/lib.rs').read_bytes())}
            commands = commands_for(args, negative=negative)
            stage_records = {}
            proof_stage = 'omit-result-relation-proof' if negative else 'consequence-proof'
            order = ('normal-export', 'normal-decode', 'readonly-export',
                     'readonly-decode', 'refinement', proof_stage)
            for stage_name in order:
                argv, stdin_name, stdout_name = commands[stage_name]
                stage_native_before = diag._native_tool_identity(native_tool_home)
                stage_frozen_before = diag._tool_hashes(tool_home)
                need(stage_native_before == before_native and stage_frozen_before == before_frozen,
                     'tool identity changed before stage: ' + name + '/' + stage_name)
                report['failed_stage'] = name + '/' + stage_name
                write_json(output, report)
                row = stage(stage_name, argv, case, env, source_hashes,
                            args.deadline_epoch, 1200, stdin_name, stdout_name)
                stage_native_after = diag._native_tool_identity(native_tool_home)
                stage_frozen_after = diag._tool_hashes(tool_home)
                identity = {'case': name, 'stage': stage_name,
                    'native_before': stage_native_before, 'native_after': stage_native_after,
                    'frozen_before': stage_frozen_before, 'frozen_after': stage_frozen_after,
                    'stable': stage_native_before == stage_native_after and
                              stage_frozen_before == stage_frozen_after}
                report['tool_identity_after_each_stage'].append(identity)
                need(identity['stable'], 'tool identity changed during stage: ' + name + '/' + stage_name)
                need(isinstance(row, dict), name + ' stage returned wrong type: ' + stage_name)
                stage_records[stage_name] = row
                report['source_stage_inventory'][name] = stage_records
                if stage_name in ('consequence-proof', 'omit-result-relation-proof') and \
                   type(row.get('exit')) is int:
                    report['body_proof_run'] = True
                write_json(output, report)
                expected_exit = 1 if stage_name == 'omit-result-relation-proof' else 0
                need(type(row.get('exit')) is int and row.get('exit') == expected_exit and
                     row.get('fixture_before') == source_hashes and
                     row.get('fixture_after') == source_hashes and
                     row.get('fixture_integrity') is True and
                     type(row.get('timeout_seconds')) is int and 1 <= row['timeout_seconds'] <= 1200,
                     name + ' stage failed, timed out, or source drifted: ' + stage_name)
            case_report = _validate_case(diag, args, evidence, case, name, negative=negative)
            report.setdefault('cases', {})[name] = case_report
            report['failed_stage'] = 'source-inventory'
            write_json(output, report)
        after_native = diag._native_tool_identity(native_tool_home)
        after_frozen = diag._tool_hashes(tool_home)
        need(before_native == after_native and before_frozen == after_frozen,
             'tool identity changed across matrix-bound consequence stages')
        need(len(report['tool_identity_after_each_stage']) == 12 and
             all(row.get('stable') is True and row.get('native_before') == before_native and
                 row.get('native_after') == before_native and
                 row.get('frozen_before') == before_frozen and
                 row.get('frozen_after') == before_frozen
                 for row in report['tool_identity_after_each_stage']),
             'per-stage tool identity inventory is incomplete or changed')
        need(sha(model.read_bytes()) == MODEL_SHA256, 'raw-pointer model changed during consequence')
        matrix_after = _matrix_inputs(evidence, args, native_id,
                                      const_matrix_summary, const_matrix_audit)
        need(matrix_after == matrix, 'const matrix inputs changed during consequence run')
        report.update(native_tool_identity_after=after_native,
                      frozen_tool_identity_after=after_frozen,
                      tool_identity_stable=True, model_stable=True,
                      complete=True, classification='COMPLETE_W4_CONST_CONSEQUENCE_SOURCE_REPORTED',
                      failed_stage='complete')
        report['artifact_inventory'] = _artifact_inventory(evidence, case_root, output)
        write_json(output, report)
        return report
    except BaseException as exc:
        report['complete'] = False
        report['classification'] = 'INCOMPLETE_W4_CONST_CONSEQUENCE'
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        report['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                               'traceback': traceback.format_exc()}
        try:
            report['artifact_inventory'] = _artifact_inventory(
                evidence, evidence / SUMMARY_REL.parent, output)
        except BaseException as snapshot_exc:
            report['inventory_error'] = type(snapshot_exc).__name__ + ': ' + str(snapshot_exc)
        try:
            report['native_tool_identity_after'] = diag._native_tool_identity(native_tool_home)
            report['frozen_tool_identity_after'] = diag._tool_hashes(tool_home)
        except BaseException as snapshot_exc:
            report['tool_snapshot_error'] = type(snapshot_exc).__name__ + ': ' + str(snapshot_exc)
        try:
            write_json(output, report)
        except BaseException as snapshot_exc:
            if hasattr(exc, 'add_note'):
                exc.add_note('consequence partial summary write failed: ' + str(snapshot_exc))
        raise


def _artifact_inventory(evidence: Path, case_root: Path, output: Path) -> list[dict[str, Any]]:
    rows = []
    if not case_root.exists():
        return rows
    need(case_root.is_dir() and not case_root.is_symlink(), 'case root unsafe')
    excluded = {output.resolve(), (evidence / AUDIT_REL).resolve()}
    for path in sorted(case_root.rglob('*')):
        need(not path.is_symlink(), 'artifact symlink: ' + str(path))
        if path.is_file() and path.resolve() not in excluded:
            raw = path.read_bytes()
            rows.append({'path': path.relative_to(evidence).as_posix(),
                         'bytes': len(raw), 'sha256': sha(raw)})
        elif not path.is_file() and not path.is_dir():
            need(False, 'artifact is not regular: ' + str(path))
    return rows


def audit(args: argparse.Namespace, *, diag=None,
          const_matrix_summary: dict[str, Any] | None = None,
          const_matrix_audit: dict[str, Any] | None = None) -> dict[str, Any]:
    diag = diag or load_diag(Path(args.cloud_dir))
    errors = []
    evidence = Path(args.evidence).resolve()
    summary = None
    try:
        roots, route, _ids = _context(args, diag)
        native_id = _build_id()
        need(roots['evidence'] == evidence, 'evidence root differs')
        need(_regular(diag, evidence, evidence / SUMMARY_REL), 'consequence summary missing/unsafe')
        summary = json.loads((evidence / SUMMARY_REL).read_text(encoding='utf-8'))
        need(isinstance(summary, dict) and summary.get('schema') == SCHEMA and
             summary.get('complete') is True and summary.get('candidate') == args.candidate and
             summary.get('native_build_id') == native_id and summary.get('route') == route and
             summary.get('failed_stage') == 'complete',
             'consequence summary identity/completeness differs')
        need(summary.get('body_proof_run') is True and summary.get('call_linkage') == 'UNKNOWN' and
             summary.get('accepted') is False and summary.get('publication_allowed') is False and
             type(summary.get('proof_credit')) is int and summary['proof_credit'] == 0,
             'consequence result crossed the proof-admission boundary')
        matrix = _matrix_inputs(evidence, args, native_id, const_matrix_summary, const_matrix_audit)
        need(summary.get('const_matrix') == matrix, 'consequence matrix provenance differs')
        for name, negative in (('positive', False), ('omit-result-relation', True)):
            case = evidence / SUMMARY_REL.parent / name
            observed = _validate_case(diag, args, evidence, case, name, negative=negative)
            need(summary.get('cases', {}).get(name) == observed,
                 name + ' physical source/stage/log/AST evidence changed')
        before, after = summary.get('native_tool_identity_before'), summary.get('native_tool_identity_after')
        native_now = diag._native_tool_identity(roots['native_tool_home'])
        frozen_now = diag._tool_hashes(roots['tool_home'])
        need(before == after == native_now and
             summary.get('frozen_tool_identity_before') ==
             summary.get('frozen_tool_identity_after') == frozen_now and
             summary.get('tool_identity_stable') is True,
             'current native/frozen tool identities differ')
        per_stage = summary.get('tool_identity_after_each_stage')
        expected_stage_keys = [
            (case_name, stage_name)
            for case_name, proof_name in (
                ('positive', 'consequence-proof'),
                ('omit-result-relation', 'omit-result-relation-proof'))
            for stage_name in ('normal-export', 'normal-decode', 'readonly-export',
                               'readonly-decode', 'refinement', proof_name)]
        need(isinstance(per_stage, list) and len(per_stage) == len(expected_stage_keys) and
             all(isinstance(row, dict) for row in per_stage) and
             [(row.get('case'), row.get('stage')) for row in per_stage] == expected_stage_keys and
             all(row.get('native_before') == before == row.get('native_after') and
                 row.get('frozen_before') == summary.get('frozen_tool_identity_before') ==
                 row.get('frozen_after') and row.get('stable') is True for row in per_stage),
             'per-stage tool identity inventory changed or is incomplete')
        need(summary.get('model') == {'path': MODEL_REL.as_posix(), 'sha256': MODEL_SHA256} and
             summary.get('model_stable') is True,
             'raw-pointer model binding differs')
        need(summary.get('artifact_inventory') == _artifact_inventory(
            evidence, evidence / SUMMARY_REL.parent, evidence / SUMMARY_REL),
             'consequence artifact inventory changed')
        need(args.runner_exit == 0 and args.failed_stage == 'complete',
             'consequence runner did not complete')
    except BaseException as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
    result = {'schema': AUDIT_SCHEMA, 'evidence_complete': not errors,
              'complete': not errors, 'summary_path': SUMMARY_REL.as_posix(),
              'summary': summary, 'errors': errors,
              'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
              'call_linkage': 'UNKNOWN'}
    output = evidence / AUDIT_REL
    write_json(output, result)
    return result


