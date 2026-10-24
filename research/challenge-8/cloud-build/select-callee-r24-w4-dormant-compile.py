#!/usr/bin/env python3
"""Build an isolated dormant W4 native candidate and record identity only.

This controller does not run a verifier stage. The output is an observed tool
identity for a later, separately reviewed step; it grants no proof credit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import Any

SCHEMA = 'select-r24-w4-dormant-compile-v1'
AUDIT_SCHEMA = 'select-r24-w4-dormant-compile-v1-audit'
SUMMARY_REL = Path('cases/r24-w4-dormant-compile/W4-DORMANT-COMPILE.json')
AUDIT_REL = Path('cases/r24-w4-dormant-compile/W4-DORMANT-COMPILE-AUDIT.json')
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-DORMANT-COMPILE-MODE.json')
MODE_SHA256 = 'dd92fea0c2f6d159168a2857264e363911f7099a76aa5d754563557eaa9ad222'

R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
ROUTE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'

CONTROL_HELPER_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-control-capture.py')
CONTROL_HELPER_SHA256 = '553f41f96018a67b4bcbfbe2ba94900934a3517726a9e9cc2d2a9fd8d9fe6cf6'
INPUT_HOME = Path('/workspace/smallsort-work/r24-w4-contract-input-tool')
TARGET_HOME = Path('/workspace/smallsort-work/r24-w4-dormant-tool')
INPUT_IDENTITY_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-F83-TOOL-IDENTITY.json')
INPUT_IDENTITY_SHA256 = '8bee7bcd29354d979e26f96b6e7138662dee38359b8edc54f95d74e8316e962d'
MANIFEST_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-DORMANT-NATIVE-MANIFEST.json')
MANIFEST_SHA256 = '117a87c69942da9fa0fcb6b3acbffdeca3415afae49172aca2c3bcdd6d83a1fc'
PATCH_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-dormant-native-r24.patch')
PATCH_SHA256 = 'f131b3442d07650c47e9cd958fee51693b5ee6066151b9042fe4bcd43b3958f5'
BASE_TRANSLATOR_SHA256 = 'f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806'
RESULT_TRANSLATOR_SHA256 = 'c473820307acd581e46378d02368c79f9ae86e540ae76aab5d1621ed40322092'
INPUT_BINARY_SHA256 = '9176c2244f90482264d52ab30cfedd61248e6e3b0b0126eaf57e1d8310c868cb'
STAGE_REL = Path('research/challenge-8/overnight-sort4/capture.py')
STAGE_SHA256 = '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'
CONST_SUMMARY_REL = SUMMARY_REL.parent.parent / 'r24-w4-const-qualification/W4-CONST-QUALIFICATION.json'
CONST_AUDIT_REL = SUMMARY_REL.parent.parent / 'r24-w4-const-qualification/W4-CONST-QUALIFICATION-AUDIT.json'

OUTPUT_ROOT_REL = SUMMARY_REL.parent
STAGES = ('copy', 'patch-check', 'patch-apply', 'compile')
CAP = 600


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_exact(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == \
           json.dumps(right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-W4-DORMANT-COMPILE: ' + message)


def _load_helper(repo: Path, cloud_dir: Path):
    path = cloud_dir / CONTROL_HELPER_REL.name
    raw = _read_regular(path)
    need(digest(raw) == CONTROL_HELPER_SHA256, 'control-capture helper identity differs')
    spec = importlib.util.spec_from_file_location('r24_w4_dormant_control_helper', path)
    need(spec is not None and spec.loader is not None, 'cannot load pinned control helper')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(digest(_read_regular(path)) == CONTROL_HELPER_SHA256,
         'control helper changed during import')
    return module


def _assert_chain(path: Path, *, missing: bool = False) -> Path:
    raw = Path(path)
    need(raw.is_absolute() and Path(os.path.normpath(str(raw))) == raw,
         'path must be normalized absolute: ' + str(raw))
    current = Path(raw.anchor)
    for i, part in enumerate(raw.parts[1:]):
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            need(missing, 'missing path component: ' + str(current))
            break
        need(not stat.S_ISLNK(info.st_mode), 'symlink in path chain: ' + str(current))
        if i < len(raw.parts[1:]) - 1:
            need(stat.S_ISDIR(info.st_mode), 'non-directory path parent: ' + str(current))
    need(raw.resolve(strict=False) == raw, 'path resolves through alias: ' + str(raw))
    return raw


def _read_regular(path: Path, root: Path | None = None) -> bytes:
    path = _assert_chain(Path(path))
    if root is not None:
        _safe_path(root, path)
    need(path.is_file() and not path.is_symlink(), 'not a regular file: ' + str(path))
    return path.read_bytes()


def _safe_path(root: Path, path: Path, *, missing: bool = False) -> Path:
    root = _assert_chain(root, missing=missing)
    path = _assert_chain(path, missing=missing)
    need(path == root or root in path.parents, 'path escapes evidence root')
    return path


def _mkdir(root: Path, directory: Path) -> None:
    _safe_path(root, directory, missing=True)
    todo = []
    current = directory
    while current != root and not current.exists():
        todo.append(current)
        current = current.parent
    need(current == root or root in current.parents, 'directory parent escapes evidence root')
    for path in reversed(todo):
        path.mkdir()
        need(path.is_dir() and not path.is_symlink(), 'unsafe created directory')


def _write_json(helper, root: Path, path: Path, value: dict[str, Any]) -> None:
    """Atomic, no-follow JSON write; remains available if the pinned helper is missing."""
    path = _safe_path(root, path, missing=True)
    _mkdir(root, path.parent)
    if path.exists():
        need(path.is_file() and not path.is_symlink(), 'refuse to replace unsafe JSON file')
    temp = path.with_name('.' + path.name + '.tmp')
    need(not temp.exists() and not temp.is_symlink(), 'temporary JSON path already exists')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(value, sort_keys=True, indent=2) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        _safe_path(root, temp)
        os.replace(temp, path)
    except BaseException:
        try:
            temp.unlink(missing_ok=True)
        finally:
            raise


def _tool_hashes(helper, home: Path, expected: dict[str, str], *, binary: str | None = None) -> dict[str, str]:
    observed = {}
    for rel, sha in expected.items():
        raw = _read_regular(home / rel)
        need(digest(raw) == sha, 'tool source identity differs: ' + rel)
        observed[rel] = sha
    binary_raw = _read_regular(home / 'bin/verifast')
    need(binary_raw, 'verifier binary is empty')
    binary_sha = digest(binary_raw)
    if binary is not None:
        need(binary_sha == binary, 'verifier binary identity differs')
    return {**observed, 'bin/verifast': binary_sha}


def _observe_tool(home: Path, keys: set[str]) -> dict[str, str]:
    observed = {}
    for rel in sorted(keys - {'bin/verifast'}):
        observed[rel] = digest(_read_regular(home / rel))
    binary = _read_regular(home / 'bin/verifast')
    need(binary, 'observed verifier binary is empty')
    observed['bin/verifast'] = digest(binary)
    return observed


def _artifact_inventory(helper, root: Path, evidence: Path) -> list[dict[str, Any]]:
    excluded = {SUMMARY_REL.as_posix(), AUDIT_REL.as_posix()}
    return [row for row in helper._artifact_inventory(root, evidence)
            if row.get('path') not in excluded]


def _current_build() -> str:
    return os.environ.get('CLOUD_BUILD_ID', '')


def _route(helper) -> dict[str, str]:
    return helper._route(dict(os.environ))


def _mode(repo: Path, mode_path: Path) -> dict[str, Any]:
    mode_path = _assert_chain(mode_path)
    need(mode_path == repo / MODE_REL, 'exact dormant compile mode path required')
    raw = _read_regular(mode_path)
    need(MODE_SHA256 != 'PENDING' and digest(raw) == MODE_SHA256,
         'dormant compile mode pin differs')
    mode = json.loads(raw.decode('utf-8'))
    need(type(mode) is dict and _json_exact(mode, expected_mode()), 'dormant compile mode fields differ')
    return mode


def expected_mode() -> dict[str, Any]:
    return {
        'schema': 'select-r24-w4-dormant-compile-mode-v1', 'enabled': True,
        'phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
        'owner': 'select-sort4', 'lane': LANE, 'profile': PROFILE,
        'input_identity_path': INPUT_IDENTITY_REL.as_posix(),
        'input_identity_sha256': INPUT_IDENTITY_SHA256,
        'input_tool_home': str(INPUT_HOME), 'target_tool_home': str(TARGET_HOME),
        'control_helper_path': CONTROL_HELPER_REL.as_posix(),
        'control_helper_sha256': CONTROL_HELPER_SHA256,
        'stage_path': STAGE_REL.as_posix(), 'stage_sha256': STAGE_SHA256,
        'manifest_path': MANIFEST_REL.as_posix(), 'manifest_sha256': MANIFEST_SHA256,
        'patch_path': PATCH_REL.as_posix(), 'patch_sha256': PATCH_SHA256,
        'base_translator_sha256': BASE_TRANSLATOR_SHA256,
        'result_translator_sha256': RESULT_TRANSLATOR_SHA256,
        'input_binary_sha256': INPUT_BINARY_SHA256,
        'stages': list(STAGES), 'cap_seconds': CAP,
    }


def _validate_prerequisite(helper, repo: Path, evidence: Path, candidate: str,
                           build_id: str) -> dict[str, Any]:
    summary_path = evidence / CONST_SUMMARY_REL
    audit_path = evidence / CONST_AUDIT_REL
    summary = json.loads(_read_regular(summary_path, evidence).decode('utf-8'))
    audit = json.loads(_read_regular(audit_path, evidence).decode('utf-8'))
    need(type(summary) is dict and type(audit) is dict, 'qualification prerequisite records malformed')
    summary_sha = digest(_read_regular(summary_path, evidence))
    need(summary.get('schema') == 'select-r24-w4-const-qualification-v1' and
         summary.get('complete') is True and summary.get('candidate') == candidate and
         summary.get('build_id') == build_id and summary.get('phase_id') == R24_PHASE and
         summary.get('route_phase_id') == R21_PHASE and summary.get('lane') == LANE and
         summary.get('profile') == PROFILE and summary.get('accepted') is False and
         summary.get('publication_allowed') is False and type(summary.get('proof_credit')) is int and
         summary.get('proof_credit') == 0,
         'same-Build const qualification prerequisite is incomplete or misbound')
    need(audit.get('schema') == 'select-r24-w4-const-qualification-v1-audit' and
         audit.get('complete') is True and audit.get('evidence_complete') is True and
         audit.get('candidate') == candidate and audit.get('build_id') == build_id and
         type(audit.get('runner_exit')) is int and audit.get('runner_exit') == 0 and
         audit.get('failed_stage') == 'complete' and
         audit.get('summary_sha256') == summary_sha and audit.get('accepted') is False and
         audit.get('publication_allowed') is False and type(audit.get('proof_credit')) is int and
         audit.get('proof_credit') == 0,
         'same-Build qualification physical audit is incomplete or misbound')
    _validate_nested_prerequisites(summary, candidate, build_id)
    return {'summary_path': CONST_SUMMARY_REL.as_posix(), 'summary_sha256': summary_sha,
            'audit_path': CONST_AUDIT_REL.as_posix(), 'audit_sha256': digest(_read_regular(audit_path, evidence)),
            'build_id': build_id, 'candidate': candidate}


def _validate_nested_prerequisites(summary: dict[str, Any], candidate: str,
                                   build_id: str) -> None:
    """Validate nested evidence against each producer's actual record schema."""
    source = summary.get('source_observation')
    need(type(source) is dict and source.get('complete') is True,
         'source observation prerequisite is incomplete')

    consequence = summary.get('consequence')
    need(type(consequence) is dict and
         consequence.get('schema') == 'select-r24-w4-const-consequence-v1' and
         consequence.get('complete') is True and consequence.get('classification') ==
             'COMPLETE_W4_CONST_CONSEQUENCE_SOURCE_REPORTED' and
         consequence.get('scope') == 'SOURCE_REPORTED_CHECKED_POST_CONSEQUENCE_ONLY' and
         consequence.get('candidate') == candidate and consequence.get('native_build_id') == build_id and
         consequence.get('failed_stage') == 'complete' and consequence.get('body_proof_run') is True and
         consequence.get('call_linkage') == 'UNKNOWN' and consequence.get('accepted') is False and
         consequence.get('publication_allowed') is False and
         type(consequence.get('proof_credit')) is int and consequence.get('proof_credit') == 0 and
         'caller_body_proof_admission' not in consequence,
         'const-consequence producer summary schema/boundary differs')
    consequence_audit = summary.get('consequence_audit')
    need(type(consequence_audit) is dict and
         consequence_audit.get('schema') == 'select-r24-w4-const-consequence-audit-v1' and
         consequence_audit.get('complete') is True and consequence_audit.get('evidence_complete') is True and
         consequence_audit.get('summary_path') == 'cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json' and
         _json_exact(consequence_audit.get('summary'), consequence) and
         consequence_audit.get('call_linkage') == 'UNKNOWN' and consequence_audit.get('accepted') is False and
         consequence_audit.get('publication_allowed') is False and
         type(consequence_audit.get('proof_credit')) is int and consequence_audit.get('proof_credit') == 0 and
         'caller_body_proof_admission' not in consequence_audit,
         'const-consequence producer audit schema/boundary differs')

    contract = summary.get('postqualification_diagnostic')
    need(type(contract) is dict and contract.get('schema') == 'select-r24-w4-contract-inputs-v1' and
         contract.get('complete') is True and contract.get('candidate') == candidate and
         contract.get('build_id') == build_id and contract.get('phase_id') == R24_PHASE and
         contract.get('route_phase_id') == R21_PHASE and contract.get('owner') == 'select-sort4' and
         contract.get('lane') == LANE and contract.get('profile') == PROFILE and
         contract.get('typed_call_linkage') == 'UNKNOWN' and contract.get('call_linkage') == 'UNKNOWN' and
         contract.get('caller_body_proof_admission') is False and contract.get('accepted') is False and
         contract.get('publication_allowed') is False and type(contract.get('proof_credit')) is int and
         contract.get('proof_credit') == 0,
         'C6 contract-input producer summary schema/boundary differs')
    contract_audit = summary.get('postqualification_diagnostic_audit')
    need(type(contract_audit) is dict and
         contract_audit.get('schema') == 'select-r24-w4-contract-inputs-v1-audit' and
         contract_audit.get('complete') is True and contract_audit.get('evidence_complete') is True and
         contract_audit.get('candidate') == candidate and contract_audit.get('build_id') == build_id and
         contract_audit.get('typed_call_linkage') == 'UNKNOWN' and
         contract_audit.get('caller_body_proof_admission') is False and
         contract_audit.get('accepted') is False and contract_audit.get('publication_allowed') is False and
         type(contract_audit.get('proof_credit')) is int and contract_audit.get('proof_credit') == 0,
         'C6 contract-input producer audit schema/boundary differs')

    control = summary.get('source_control_capture')
    need(type(control) is dict and control.get('schema') == 'select-r24-w4-control-capture-v1' and
         control.get('complete') is True and control.get('candidate') == candidate and
         control.get('build_id') == build_id and control.get('r24_session_phase_id') == R24_PHASE and
         control.get('route_phase_id') == R21_PHASE and control.get('owner') == 'select-sort4' and
         control.get('lane') == LANE and control.get('profile') == PROFILE and
         control.get('body_proof_run') is False and control.get('universe_complete') is False and
         control.get('typed_call_linkage') == 'UNKNOWN' and
         control.get('caller_body_proof_admission') is False and control.get('accepted') is False and
         control.get('publication_allowed') is False and type(control.get('proof_credit')) is int and
         control.get('proof_credit') == 0,
         'source control-capture producer summary schema/boundary differs')
    control_audit = summary.get('source_control_capture_audit')
    need(type(control_audit) is dict and
         control_audit.get('schema') == 'select-r24-w4-control-capture-audit-v1' and
         control_audit.get('complete') is True and control_audit.get('evidence_complete') is True and
         control_audit.get('candidate') == candidate and
         control_audit.get('typed_call_linkage') == 'UNKNOWN' and
         control_audit.get('caller_body_proof_admission') is False and
         control_audit.get('accepted') is False and control_audit.get('publication_allowed') is False and
         type(control_audit.get('proof_credit')) is int and control_audit.get('proof_credit') == 0,
         'source control-capture producer audit schema/boundary differs')


def _validate_context(args, helper, *, fresh: bool = False):
    raw_repo = Path(args.repo)
    repo = _assert_chain(raw_repo)
    cloud_dir = _assert_chain(Path(args.cloud_dir))
    evidence = _assert_chain(Path(args.evidence), missing=True)
    native_home = _assert_chain(Path(args.native_tool_home))
    need(repo.is_dir() and cloud_dir.is_dir() and native_home.is_dir(), 'context root is missing')
    need(repo == repo.resolve() and raw_repo == repo, 'repo root alias refused')
    need(Path(args.native_tool_home) == INPUT_HOME, 'native tool home must be exact F83 input home')
    need(len(args.candidate) == 40 and all(c in '0123456789abcdef' for c in args.candidate),
         'candidate must be full lowercase Git SHA')
    current = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    need(current == args.candidate, 'candidate checkout differs')
    build_id = _current_build()
    need(build_id and build_id.count('-') == 4, 'CLOUD_BUILD_ID missing or malformed')
    route = _route(helper)
    need(int(args.deadline_epoch) > int(time.time()) + 10, 'deadline reserve unavailable')
    if fresh:
        _safe_path(evidence, evidence / SUMMARY_REL, missing=True)
        need(not (evidence / SUMMARY_REL).exists(), 'dormant compile summary already exists')
        need(not (evidence / AUDIT_REL).exists(), 'dormant compile audit already exists')
        need(not TARGET_HOME.exists() and not TARGET_HOME.is_symlink(),
             'dormant output tool home already exists')
    mode = _mode(repo, repo / MODE_REL)
    prereq = _validate_prerequisite(helper, repo, evidence, args.candidate, build_id)
    identity_raw = _read_regular(repo / INPUT_IDENTITY_REL)
    need(digest(identity_raw) == INPUT_IDENTITY_SHA256, 'historical F83 identity file pin differs')
    identity = json.loads(identity_raw.decode('utf-8'))
    need(type(identity) is dict and
         identity.get('schema') == 'select-r24-w4-source-reported-tool-identity-v1' and
         identity.get('assurance') == 'SOURCE_REPORTED' and
         identity.get('classification') == 'C6_INPUT_DIAGNOSTIC_TOOL_IDENTITY_ONLY' and
         identity.get('accepted') is False and identity.get('publication_allowed') is False and
         identity.get('caller_body_proof_admission') is False and type(identity.get('proof_credit')) is int and
         identity.get('proof_credit') == 0, 'F83 input identity is not diagnostic-only')
    tool_hashes = identity.get('tool_hashes')
    need(type(tool_hashes) is dict and set(tool_hashes) ==
         (set(helper.NATIVE_TOOL_SOURCE_HASHES) | {'bin/verifast'}),
         'historical input tool inventory malformed')
    observed = _tool_hashes(helper, native_home,
        {key: val for key, val in tool_hashes.items() if key != 'bin/verifast'},
        binary=tool_hashes.get('bin/verifast'))
    need(observed == tool_hashes, 'physical F83 native input inventory differs')
    manifest_raw = _read_regular(repo / MANIFEST_REL)
    need(MANIFEST_SHA256 != 'PENDING' and digest(manifest_raw) == MANIFEST_SHA256,
         'dormant native manifest pin differs')
    manifest = json.loads(manifest_raw.decode('utf-8'))
    need(type(manifest) is dict and manifest.get('schema') == 'select-r24-w4-dormant-native-manifest-v1' and
         manifest.get('dormant') is True and manifest.get('caller_body_proof_admission') is False and
         manifest.get('accepted') is False and manifest.get('publication_allowed') is False and
         type(manifest.get('proof_credit')) is int and manifest.get('proof_credit') == 0 and
         manifest.get('base_translator_sha256') == BASE_TRANSLATOR_SHA256 and
         tool_hashes.get('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') == BASE_TRANSLATOR_SHA256 and
         RESULT_TRANSLATOR_SHA256 != 'PENDING' and
         manifest.get('result_translator_sha256') == RESULT_TRANSLATOR_SHA256 and
         manifest.get('patch') == {'path': PATCH_REL.as_posix(), 'sha256': PATCH_SHA256},
         'dormant native manifest shape/pins differ')
    patch_raw = _read_regular(repo / PATCH_REL)
    need(PATCH_SHA256 != 'PENDING' and digest(patch_raw) == PATCH_SHA256,
         'dormant patch pin differs')
    need(fresh or TARGET_HOME.is_dir(), 'dormant tool output directory missing for audit')
    return repo, cloud_dir, evidence, native_home, route, mode, prereq, identity, manifest


def _stage_call(stage_runner, name, argv, root, env, deadline):
    import inspect
    params = inspect.signature(stage_runner).parameters
    need('stdin_name' in params and 'stdout_name' in params,
         'stage API must expose frozen stdin_name/stdout_name arguments')
    return stage_runner(name, argv, root, env, {}, deadline, CAP,
                        stdin_name=None, stdout_name=None)


def _stage_status(stage: Any) -> tuple[str, int | None]:
    if type(stage) is not dict:
        return 'WRONG_TYPE', None
    if 'status' in stage:
        status = stage['status']
        if type(status) is not str or status not in ('RAN', 'NOT_RUN', 'TIMEOUT', 'ERROR'):
            return 'WRONG_TYPE', stage.get('exit') if type(stage.get('exit')) is int else None
    else:
        if stage.get('skipped') is not None or stage.get('exit') is None:
            return 'NOT_RUN', None
        if type(stage.get('exit')) is not int:
            return 'WRONG_TYPE', None
        status = 'RAN'
    exit_code = stage.get('exit')
    if type(exit_code) is not int:
        return 'WRONG_TYPE', None
    return status, exit_code


def _stage_commands(repo: Path, target: Path, patch: Path) -> dict[str, list[str]]:
    return {
        'copy': ['/bin/cp', '-a', str(INPUT_HOME), str(target)],
        'patch-check': ['git', '-C', str(target), 'apply', '--check', str(patch)],
        'patch-apply': ['git', '-C', str(target), 'apply', str(patch)],
        'compile': ['make', '-C', str(target / 'src'), '../bin/verifast',
                    'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'],
    }


def _run_stage_chain(helper, stage_runner, *, repo, evidence, target, patch, deadline):
    root = evidence / SUMMARY_REL.parent / 'tool-build'
    _mkdir(evidence, root)
    env = dict(os.environ)
    commands = _stage_commands(repo, target, patch)
    stages: dict[str, Any] = {}
    errors = []
    for name in STAGES:
        argv = commands[name]
        try:
            stage = _stage_call(stage_runner, 'dormant-' + name, argv, root, env, deadline)
            if type(stage) is dict:
                if not _json_exact(stage.get('argv'), argv):
                    errors.append(name + ' command argv differs from exact dormant command')
                if stage.get('fixture_integrity') is not True or \
                   stage.get('fixture_before') != {} or stage.get('fixture_after') != {}:
                    errors.append(name + ' stage fixture integrity differs')
            stages[name] = stage
            if errors:
                break
            physical_errors = _physical_stages(
                helper, evidence,
                {'commands': commands, 'stages': {name: stage}}, names=(name,))
            if physical_errors:
                errors.extend(physical_errors)
                break
            status, exit_code = _stage_status(stage)
            if status != 'RAN' or exit_code != 0:
                errors.append(name + ' stage status/exit is ' + status + '/' + str(exit_code))
                break
        except BaseException as exc:
            stages[name] = {'status': 'EXCEPTION', 'exception_type': type(exc).__name__,
                            'exception': str(exc)}
            errors.append(name + ' stage raised ' + type(exc).__name__ + ': ' + str(exc))
            result = {'commands': commands, 'stages': stages, 'errors': errors,
                      'complete': False, '_exception_object': exc}
            return result
    result = {'commands': commands, 'stages': stages, 'errors': errors,
              'complete': len(stages) == len(STAGES) and not errors}
    if result['complete']:
        physical_errors = _physical_stages(helper, evidence, result)
        if physical_errors:
            result['errors'].extend(physical_errors)
            result['complete'] = False
    return result


def _physical_stages(helper, evidence: Path, report: dict[str, Any],
                     names: tuple[str, ...] = STAGES) -> list[str]:
    errors = []
    stage_root = evidence / SUMMARY_REL.parent / 'tool-build'
    commands = report.get('stages', {})
    if type(commands) is not dict:
        return ['stage inventory malformed']
    for name in names:
        stage = commands.get(name)
        if type(stage) is not dict:
            errors.append(name + ' stage missing/wrong type')
            continue
        path = stage_root / ('dormant-' + name + '-stage.json')
        try:
            physical = json.loads(_read_regular(path, evidence).decode('utf-8'))
            if not _json_exact(physical, stage):
                errors.append(name + ' recorded stage differs from physical stage JSON')
            if stage.get('argv') != report.get('commands', {}).get(name):
                errors.append(name + ' command target differs from pinned argv')
            if stage.get('fixture_integrity') is not True or \
               stage.get('fixture_before') != {} or stage.get('fixture_after') != {}:
                errors.append(name + ' fixture integrity differs')
            for channel in ('stdout', 'stderr'):
                logfile = stage.get(channel)
                if type(logfile) is not str or Path(logfile).name != logfile:
                    errors.append(name + ' ' + channel + ' log name malformed')
                    continue
                _read_regular(stage_root / logfile, evidence)
        except BaseException as exc:
            errors.append(name + ' physical stage evidence invalid: ' + type(exc).__name__ + ': ' + str(exc))
    return errors


def _save_partial(helper, evidence: Path, path: Path, report: dict[str, Any]) -> None:
    try:
        _write_json(helper, evidence, path, report)
    except BaseException as exc:
        if isinstance(report.get('errors'), list):
            report['errors'].append('summary write failed: ' + type(exc).__name__ + ': ' + str(exc))


def run(args: argparse.Namespace, *, stage_runner=None, helper=None) -> dict[str, Any]:
    raw_evidence = Path(args.evidence)
    evidence = _assert_chain(raw_evidence, missing=True)
    repo = _assert_chain(Path(args.repo))
    cloud_dir = _assert_chain(Path(args.cloud_dir))
    summary_path = evidence / SUMMARY_REL
    report: dict[str, Any] = {
        'schema': SCHEMA, 'complete': False,
        'classification': 'INCOMPLETE_DORMANT_TOOL_COMPILE_IDENTITY',
        'candidate': getattr(args, 'candidate', None), 'build_id': _current_build() or None,
        'phase_id': R24_PHASE, 'route_phase_id': R21_PHASE, 'owner': 'select-sort4',
        'lane': LANE, 'profile': PROFILE, 'accepted': False,
        'publication_allowed': False, 'caller_body_proof_admission': False,
        'proof_credit': 0, 'body_proof_run': False, 'callee_qualification': False,
        'proof_qualification': False, 'typed_call_linkage': 'UNKNOWN',
        'mode_path': MODE_REL.as_posix(), 'mode_sha256': MODE_SHA256,
        'repo': str(repo), 'evidence_root': str(evidence),
        'native_tool_home': str(INPUT_HOME), 'target_tool_home': str(TARGET_HOME),
        'native_stage_path': STAGE_REL.as_posix(), 'native_stage_sha256': STAGE_SHA256,
        'manifest_path': MANIFEST_REL.as_posix(), 'patch_path': PATCH_REL.as_posix(),
        'input_identity_path': INPUT_IDENTITY_REL.as_posix(),
        'errors': [], 'stages': {}, 'commands': {}, 'native_tool_hashes_before': None,
        'native_tool_hashes_after': None, 'binary_sha256': None,
    }
    # Evidence root and destination must be absent before any creation.
    try:
        _safe_path(evidence, summary_path, missing=True)
        need(not (evidence / SUMMARY_REL.parent).exists(), 'dormant compile summary subtree already exists')
        need(not (evidence / AUDIT_REL).exists(), 'dormant compile audit already exists')
        helper = helper or _load_helper(repo, cloud_dir)
        repo, cloud_dir, evidence, native_home, route, mode, prereq, identity, manifest = \
            _validate_context(args, helper, fresh=True)
        if stage_runner is None:
            stage_module = helper._load(repo / STAGE_REL, 'r24_w4_dormant_capture_stage', STAGE_SHA256)
            stage_runner = stage_module.run_stage
        before = _tool_hashes(helper, native_home,
            {k: v for k, v in identity['tool_hashes'].items() if k != 'bin/verifast'},
            binary=identity['tool_hashes']['bin/verifast'])
        report.update({'prerequisite': prereq, 'mode': mode, 'route': route,
                       'native_tool_hashes_before': before,
                       'manifest_sha256': MANIFEST_SHA256,
                       'patch_sha256': PATCH_SHA256,
                       'input_identity_sha256': INPUT_IDENTITY_SHA256})
        _write_json(helper, evidence, summary_path, report)
        target = TARGET_HOME
        patch = repo / PATCH_REL
        result = _run_stage_chain(helper, stage_runner, repo=repo, evidence=evidence,
                                  target=target, patch=patch, deadline=args.deadline_epoch)
        stage_exception = result.pop('_exception_object', None)
        report.update(result)
        input_after = _tool_hashes(helper, native_home,
            {k: v for k, v in identity['tool_hashes'].items() if k != 'bin/verifast'},
            binary=identity['tool_hashes']['bin/verifast'])
        report['native_input_tool_hashes_after'] = input_after
        if input_after != before:
            report['errors'].append('F83 input tool changed during dormant build')
            report['complete'] = False
            result['complete'] = False
        if result['complete']:
            expected_sources = dict(identity['tool_hashes'])
            expected_sources.pop('bin/verifast')
            expected_sources['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = \
                manifest['result_translator_sha256']
            after = _tool_hashes(helper, target, expected_sources)
            report['native_tool_hashes_after'] = after
            report['binary_sha256'] = after['bin/verifast']
            report['complete'] = True
            report['classification'] = 'DORMANT_COMPILE_TOOL_IDENTITY_ONLY'
            report['observed_identity'] = after
        else:
            try:
                report['native_tool_hashes_after'] = _observe_tool(
                    target, set(identity['tool_hashes']))
            except BaseException as exc:
                report['errors'].append('partial target inventory: ' + type(exc).__name__ + ': ' + str(exc))
        report['accepted'] = False
        report['publication_allowed'] = False
        report['caller_body_proof_admission'] = False
        report['callee_qualification'] = False
        report['proof_qualification'] = False
        report['typed_call_linkage'] = 'UNKNOWN'
        report['proof_credit'] = 0
        report['body_proof_run'] = False
        report['input_identity_sha256'] = INPUT_IDENTITY_SHA256
        report['artifact_inventory'] = _artifact_inventory(
            helper, evidence / SUMMARY_REL.parent, evidence)
        _write_json(helper, evidence, summary_path, report)
        if stage_exception is not None:
            raise stage_exception
        return report
    except BaseException as exc:
        report['errors'].append('exception: ' + type(exc).__name__ + ': ' + str(exc))
        report['complete'] = False
        report['classification'] = 'INCOMPLETE_DORMANT_TOOL_COMPILE_IDENTITY'
        report['accepted'] = False
        report['publication_allowed'] = False
        report['caller_body_proof_admission'] = False
        report['proof_credit'] = 0
        try:
            if helper is None:
                helper = _load_helper(repo, cloud_dir)
            _save_partial(helper, evidence, summary_path, report)
        except BaseException as save_exc:
            try:
                exc.add_note('partial summary preservation failed: ' + repr(save_exc))
            except Exception:
                pass
        raise


def audit(args: argparse.Namespace, *, helper=None) -> dict[str, Any]:
    evidence = _assert_chain(Path(args.evidence))
    audit_path = evidence / AUDIT_REL
    summary_path = evidence / SUMMARY_REL
    audit_record: dict[str, Any] = {
        'schema': AUDIT_SCHEMA, 'complete': False, 'evidence_complete': False,
        'accepted': False, 'publication_allowed': False, 'caller_body_proof_admission': False,
        'proof_credit': 0, 'body_proof_run': False, 'callee_qualification': False,
        'proof_qualification': False, 'typed_call_linkage': 'UNKNOWN',
        'runner_exit': getattr(args, 'runner_exit', None),
        'failed_stage': getattr(args, 'failed_stage', None), 'errors': [],
    }
    try:
        helper = helper or _load_helper(_assert_chain(Path(args.repo)),
                                        _assert_chain(Path(args.cloud_dir)))
        repo, cloud_dir, evidence, native_home, route, mode, prereq, identity, manifest = \
            _validate_context(args, helper, fresh=False)
        outarg = Path(getattr(args, 'output', audit_path))
        _safe_path(evidence, outarg, missing=True)
        need(outarg == audit_path, 'audit output must be exact evidence-relative path')
        summary_raw = _read_regular(summary_path, evidence)
        report = json.loads(summary_raw.decode('utf-8'))
        need(type(report) is dict and report.get('schema') == SCHEMA and
             report.get('candidate') == args.candidate and report.get('build_id') == _current_build(),
             'summary identity differs')
        expected_classification = ('DORMANT_COMPILE_TOOL_IDENTITY_ONLY'
                                   if report.get('complete') is True
                                   else 'INCOMPLETE_DORMANT_TOOL_COMPILE_IDENTITY')
        if report.get('classification') != expected_classification:
            audit_record['errors'].append('summary classification/complete state differs')
        if report.get('repo') != str(repo) or report.get('evidence_root') != str(evidence) or \
           report.get('native_tool_home') != str(native_home) or \
           report.get('target_tool_home') != str(TARGET_HOME) or \
           report.get('native_stage_path') != STAGE_REL.as_posix() or \
           report.get('native_stage_sha256') != STAGE_SHA256 or \
           report.get('manifest_path') != MANIFEST_REL.as_posix() or \
           report.get('patch_path') != PATCH_REL.as_posix() or \
           report.get('input_identity_path') != INPUT_IDENTITY_REL.as_posix() or \
           report.get('phase_id') != R24_PHASE or report.get('route_phase_id') != R21_PHASE or \
           report.get('owner') != 'select-sort4' or report.get('lane') != LANE or \
           report.get('profile') != PROFILE or report.get('mode_path') != MODE_REL.as_posix() or \
           report.get('mode_sha256') != MODE_SHA256 or \
           report.get('manifest_sha256') != MANIFEST_SHA256 or \
           report.get('patch_sha256') != PATCH_SHA256 or \
           report.get('input_identity_sha256') != INPUT_IDENTITY_SHA256:
            audit_record['errors'].append('summary repo/tool/route/pin context differs')
        if report.get('prerequisite') != prereq:
            audit_record['errors'].append('qualification prerequisite changed')
        if not _json_exact(report.get('mode'), mode) or not _json_exact(report.get('route'), route):
            audit_record['errors'].append('mode or route binding changed')
        audit_record['errors'].extend(_physical_stages(helper, evidence, report))
        physical_inventory = _artifact_inventory(helper, evidence / SUMMARY_REL.parent, evidence)
        if not _json_exact(report.get('artifact_inventory'), physical_inventory):
            audit_record['errors'].append('physical tool-build artifact inventory differs')
        input_before = _tool_hashes(helper, native_home,
            {k: v for k, v in identity['tool_hashes'].items() if k != 'bin/verifast'},
            binary=identity['tool_hashes']['bin/verifast'])
        if input_before != report.get('native_tool_hashes_before') or \
           input_before != report.get('native_input_tool_hashes_after'):
            audit_record['errors'].append('F83 input tool identity differs from recorded before/after snapshot')
        expected_commands = _stage_commands(repo, TARGET_HOME, repo / PATCH_REL)
        if not _json_exact(report.get('commands'), expected_commands):
            audit_record['errors'].append('stage command inventory differs')
        stage_map = report.get('stages')
        complete_stages = type(stage_map) is dict and set(stage_map) == set(STAGES) and all(
            _stage_status(stage_map.get(name)) == ('RAN', 0) for name in STAGES)
        if report.get('complete') is True and not complete_stages:
            audit_record['errors'].append('complete summary has incomplete stage chain')
        if report.get('complete') is True:
            expected_sources = dict(identity['tool_hashes'])
            expected_sources.pop('bin/verifast')
            expected_sources['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = \
                manifest['result_translator_sha256']
            live = _tool_hashes(helper, TARGET_HOME, expected_sources,
                                binary=report.get('binary_sha256'))
            if live != report.get('observed_identity') or live != report.get('native_tool_hashes_after'):
                audit_record['errors'].append('measured dormant tool identity drifted')
        elif report.get('classification') != 'INCOMPLETE_DORMANT_TOOL_COMPILE_IDENTITY':
            audit_record['errors'].append('incomplete summary classification differs')
        if report.get('accepted') is not False or report.get('publication_allowed') is not False or \
           report.get('caller_body_proof_admission') is not False or report.get('body_proof_run') is not False or \
           report.get('callee_qualification') is not False or report.get('proof_qualification') is not False or \
           report.get('typed_call_linkage') != 'UNKNOWN' or \
           type(report.get('proof_credit')) is not int or report.get('proof_credit') != 0:
            audit_record['errors'].append('summary proof/acceptance boundary differs')
        if type(report.get('errors')) is not list or \
           (report.get('complete') is True and report.get('errors') != []):
            audit_record['errors'].append('summary error inventory differs from completeness')
        if type(getattr(args, 'runner_exit', None)) is not int or args.runner_exit != 0 or \
           getattr(args, 'failed_stage', None) != 'complete' or \
           report.get('complete') is not True:
            audit_record['errors'].append('outer run result is not a completed compile-only identity capture')
        audit_record.update({'candidate': args.candidate, 'build_id': _current_build(),
                             'summary_path': SUMMARY_REL.as_posix(),
                             'summary_sha256': digest(summary_raw),
                             'mode_sha256': MODE_SHA256})
        audit_record['complete'] = not audit_record['errors']
        audit_record['evidence_complete'] = audit_record['complete']
    except BaseException as exc:
        audit_record['errors'].append(type(exc).__name__ + ': ' + str(exc))
    try:
        audit_record['audit_written'] = True
        _write_json(helper, evidence, audit_path, audit_record)
    except BaseException as exc:
        audit_record['audit_written'] = False
        audit_record['errors'].append('audit write failed: ' + type(exc).__name__ + ': ' + str(exc))
    return audit_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('run', 'audit'):
        p = sub.add_parser(action)
        p.add_argument('--repo', type=Path, required=True)
        p.add_argument('--cloud-dir', type=Path, required=True)
        p.add_argument('--evidence', type=Path, required=True)
        p.add_argument('--native-tool-home', type=Path, required=True)
        p.add_argument('--deadline-epoch', type=int, required=True)
        p.add_argument('--candidate', required=True)
        if action == 'audit':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--runner-exit', type=int, required=True)
            p.add_argument('--failed-stage', required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == 'run':
            result = run(args)
            print(json.dumps({'complete': result.get('complete'), 'classification': result.get('classification'),
                              'accepted': False, 'proof_credit': 0}, sort_keys=True))
            return 0 if result.get('complete') is True else 4
        result = audit(args)
        print(json.dumps({'complete': result.get('complete'), 'evidence_complete': result.get('evidence_complete'),
                          'accepted': False, 'proof_credit': 0}, sort_keys=True))
        return 0 if result.get('complete') is True else 4
    except BaseException as exc:
        print('R24-W4-DORMANT-COMPILE: ' + type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
