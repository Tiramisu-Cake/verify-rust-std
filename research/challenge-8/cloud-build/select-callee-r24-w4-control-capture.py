#!/usr/bin/env python3
"""Capture source/MIR inputs for the R24 W4 C1--C5 control batch.

This component prepares only the pinned source constructors, runs the existing
normal/readonly/refinement capture pipeline, and asks a separate native tool
copy for unit/body Marshal fingerprints.  It does not admit a caller proof or
install any callback rule.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time
import traceback
from typing import Any


SCHEMA = 'select-r24-w4-control-capture-v1'
SUMMARY_REL = Path('cases/r24-w4-control-capture/W4-CONTROL-CAPTURE.json')
AUDIT_REL = Path('cases/r24-w4-control-capture/W4-CONTROL-CAPTURE-AUDIT.json')
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTROL-CAPTURE-MODE.json')
MODE_SHA256 = 'f7e7211c18611b22ff5178e595dc11c3a9e7e72e091f977d02d9f3b5f22eaaf8'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
SOURCE_REL = Path('library/core/src/slice/sort/shared/smallsort.rs')
SOURCE_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
SOURCE_BLOB = '40939f922bcb6fdc7ee0d30427fa861827043827'
POSITIVE_VERIFIED_SHA256 = 'e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663'
POSITIVE_ORIGINAL_SHA256 = 'b4b0070e224cc60eba58a2116c0009fdda2e3ae599c67344194a709215a374db'
CONSTRUCTOR_PROFILE_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json')
CONSTRUCTOR_PROFILE_SHA256 = 'd1e0d2ddf6cd8eba5dab5a7b2a68a7530595f9b7745c6f8276f20f155b0f546d'
GHOST_STRIP_REL = Path('research/challenge-8/cloud-build/sort4-native-c1-bound/ghost-strip.py')
HELPER_PINS = {
    'sort4_body': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-r21.py', 'ae8c57e0549e3a900ad3660ddd302e0d4029293aa074b6accc132f003b655c16'),
    'c1': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-c1.py', '8af19b63552b7ef6e4b6026b4f188fa00c4344a4bb1b75848008e7b46141441e'),
    'c2_c5': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-c2.py', '4afc89d4790a2b9d8ff5501835f50eb23c26a50033b0fb68ef4f69cdf2fd528d'),
    'recover_pair': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-recover-pair.rs', '7a28ae5734c5288ff466764e6645eff236f30c097a7951ebd086f5bb7f5eff72'),
    'recover_four': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-recover-four.rs', '9637aee892e633c2521d8cef62770a6be0982a1835492b6afffafc97f9246d8b'),
    'ghost_grammar': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-ghost-grammar.py', '603827833b3a5524fa35c1f6c924c2dfcab73ecdbe3a18daa2d249c0ef8e08ce'),
    'ghost_strip': (GHOST_STRIP_REL.as_posix(), '1b1187a78b461fd37980e82b679c6df01e95b440896eea347da4cea8fe27c70d'),
    'capture': ('research/challenge-8/overnight-sort4/capture.py', '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'),
}
CAPTURE_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
CAPTURE_MODE_SHA256 = '1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3'
CAPTURE_HELPER_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-capture.py')
CAPTURE_HELPER_SHA256 = '8f3c8bddd385754aeaa4b784f3273a56e6af2f5356658c4df3d50f7c519f812d'
CAPTURE_PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json')
CAPTURE_PINS_SHA256 = 'f81b062111436a7ab8a40e9776fdc1d1138a7861b5a6d95e018201ee93d5b6a0'
NATIVE_MANIFEST_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTROL-FINGERPRINT-MANIFEST.json')
NATIVE_MANIFEST_SHA256 = '9e66bea48026b4772dee9efa3c93da2dcb56596545b32c3282ff3ecad9250f23'
NATIVE_PATCH_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-control-fingerprint-r24.patch')
NATIVE_PATCH_SHA256 = '22a1275f4b2a0f2b52b1d9febb7ceb9e0a70655b6e1bc24118f9de0e96c12c99'
NATIVE_BASE_TRANSLATOR_SHA256 = 'f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806'
NATIVE_TRANSLATOR_SHA256 = '1276f006b5dd757a9dc9fbf87e4d9491758c24f71ba5dc409f0c08720a528a13'
NATIVE_BINARY_SHA256 = '9176c2244f90482264d52ab30cfedd61248e6e3b0b0126eaf57e1d8310c868cb'
NATIVE_INPUT_IDENTITY_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-F83-TOOL-IDENTITY.json')
NATIVE_INPUT_IDENTITY_SHA256 = '8bee7bcd29354d979e26f96b6e7138662dee38359b8edc54f95d74e8316e962d'
NATIVE_STAGE_REL = Path('research/challenge-8/overnight-sort4/capture.py')
NATIVE_STAGE_SHA256 = '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'
NATIVE_TOOL_SOURCE_HASHES: dict[str, str] = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/rust_belt/general.rsspec': 'ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': 'f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806',
}
NATIVE_TOOL_HOME_NAME = 'r24-w4-control-fingerprint-tool'
NATIVE_INPUT_HOME = Path('/workspace/smallsort-work/r24-w4-contract-input-tool')
NATIVE_OUTPUT_HOME = Path('/workspace/smallsort-work/r24-w4-control-fingerprint-tool')
NATIVE_ENV_KEYS = {
    'SORT4_R24_W4_DATA_FINGERPRINT_MODE',
    'SORT4_R24_W4_DATA_FINGERPRINT_EVIDENCE_DIR',
    'SORT4_R24_W4_DATA_FINGERPRINT_SOURCE_SHA256',
}
NATIVE_FILES = ('native-data.json', 'caller-native-unit.marshal', 'caller-native-body-0.marshal')
NATIVE_STDOUT_PREFIX = 'SORT4-R24-W4-DATA: '
NATIVE_REFUSAL = 'SORT4-R24-W4-DATA: diagnostic refusal: snapshot complete; no proof rule admitted'
NATIVE_REFUSAL_STDERR = 'Fatal error: exception Failure("' + NATIVE_REFUSAL + '")'
NATIVE_ARGV = ('bin/verifast', '-rustc_args', '--edition 2021', '-verbose', '1',
               'verified/lib.rs')
BODY_NAMES = ('positive',
    'c1-missing-fourth-end-token-negative', 'c1-false-old-value-array-post-negative',
    'c2-missing-unselected-share-negative', 'c2-missing-unrelated-end-token-negative',
    'c2-wrong-ordered-ref-pair-negative', 'c2-wrong-ref-resource-negative',
    'c2-wrong-marker-index-negative', 'c2-missing-fourth-debt-token-negative',
    'c2-displaced-marker-negative',
    'c3-missing-unselected-share-negative', 'c3-missing-unrelated-end-token-negative',
    'c3-wrong-ordered-ref-pair-negative', 'c3-wrong-ref-resource-negative',
    'c3-wrong-marker-index-negative', 'c3-missing-fourth-debt-token-negative',
    'c3-displaced-marker-negative', 'c3-index-overflow-marker-negative',
    'c4-missing-unselected-share-negative', 'c4-missing-unrelated-end-token-negative',
    'c4-wrong-ordered-ref-pair-negative', 'c4-wrong-ref-resource-negative',
    'c4-wrong-marker-index-negative', 'c4-missing-fourth-debt-token-negative',
    'c4-displaced-marker-negative', 'c4-index-overflow-marker-negative',
    'c5-missing-unselected-share-negative', 'c5-missing-unrelated-end-token-negative',
    'c5-wrong-ordered-ref-pair-negative', 'c5-wrong-ref-resource-negative',
    'c5-wrong-marker-index-negative', 'c5-missing-fourth-debt-token-negative',
    'c5-displaced-marker-negative', 'c5-index-overflow-marker-negative',
    'c5-scope-escape-negative', 'c5-missing-scope-marker-negative',
    'c5-cross-scope-read-negative')
BATCH_INDICES = tuple(range(8))
SOURCE_COUNTS = {b'is_less(': 5, b'hint::select_unpredictable(': 8,
                 b'ptr::copy_nonoverlapping(': 4}
ALLOWED_SORT4_ENV = {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'}
STAGE_CAPS = {'normal-export': 100, 'normal-decode': 60,
              'readonly-export': 100, 'readonly-decode': 60,
              'refinement': 120, 'native-fingerprint': 180}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_exact(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == \
           json.dumps(right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _metadata_facts(meta: dict[str, Any]) -> dict[str, Any]:
    keys = ('name', 'mir_target', 'focus_line', 'end_line', 'first_comparator_line',
            'callback_call_lines', 'actual_c1_recovery', 'actual_c2_recovery',
            'actual_indexed_calls', 'body_annotation_stage', 'c2_control',
            'control_call_index', 'control_mutation', 'scope_control',
            'native_scope_validator_executed', 'expected_rejection',
            'expected_control', 'source_observation_note', 'summary_eligible',
            'proof_credit', 'generated_source_sha256')
    result = {}
    for key in keys:
        value = meta.get(key)
        if value is None or type(value) in (str, bool, int):
            if value is not None:
                result[key] = value
        elif isinstance(value, list) and all(type(item) in (str, bool, int) for item in value):
            result[key] = value
    return result


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-W4-CONTROL-CAPTURE: ' + message)


def _exact_boundary(record: dict[str, Any], expected: dict[str, Any]) -> bool:
    """Compare JSON boundary scalars without Python's bool/int equivalence."""
    return all(type(record.get(key)) is type(value) and record.get(key) == value
               for key, value in expected.items())


def _assert_path_chain(path: Path, *, allow_missing: bool = False) -> Path:
    raw = Path(path)
    need(raw.is_absolute(), 'filesystem path must be absolute: ' + str(raw))
    need(Path(os.path.normpath(str(raw))) == raw, 'filesystem path must be normalized: ' + str(raw))
    current = Path(raw.anchor)
    for index, part in enumerate(raw.parts[1:]):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            need(allow_missing, 'missing filesystem path component: ' + str(current))
            break
        need(not stat.S_ISLNK(info.st_mode), 'symlink in filesystem path chain: ' + str(current))
        if index < len(raw.parts[1:]) - 1:
            need(stat.S_ISDIR(info.st_mode), 'non-directory filesystem path parent: ' + str(current))
    need(raw.resolve(strict=False) == raw, 'filesystem path resolves through an alias: ' + str(raw))
    return raw


def expected_mode(repo: Path | None = None) -> dict[str, Any]:
    """Closed first-batch mode. The mode hash is pinned separately by its loader."""
    return {
        'schema': 'select-r24-w4-control-capture-mode-v1',
        'enabled': True,
        'owner': 'select-sort4', 'phase_id': R24_PHASE,
        'route_phase_id': R21_PHASE, 'lane': LANE, 'profile': PROFILE,
        'constructor_profile_path': CONSTRUCTOR_PROFILE_REL.as_posix(),
        'constructor_profile_sha256': CONSTRUCTOR_PROFILE_SHA256,
        'capture_mode_path': CAPTURE_MODE_REL.as_posix(),
        'capture_mode_sha256': CAPTURE_MODE_SHA256,
        'capture_helper_path': CAPTURE_HELPER_REL.as_posix(),
        'capture_helper_sha256': CAPTURE_HELPER_SHA256,
        'capture_pins_path': CAPTURE_PINS_REL.as_posix(),
        'capture_pins_sha256': CAPTURE_PINS_SHA256,
        'native_manifest_path': NATIVE_MANIFEST_REL.as_posix(),
        'native_manifest_sha256': NATIVE_MANIFEST_SHA256,
        'native_patch_path': NATIVE_PATCH_REL.as_posix(),
        'native_patch_sha256': NATIVE_PATCH_SHA256,
        'native_base_translator_sha256': NATIVE_BASE_TRANSLATOR_SHA256,
        'native_translator_sha256': NATIVE_TRANSLATOR_SHA256,
        'native_binary_sha256': NATIVE_BINARY_SHA256,
        'native_input_identity_path': NATIVE_INPUT_IDENTITY_REL.as_posix(),
        'native_input_identity_sha256': NATIVE_INPUT_IDENTITY_SHA256,
        'native_tool_source_hashes': NATIVE_TOOL_SOURCE_HASHES,
        'native_stage_path': NATIVE_STAGE_REL.as_posix(),
        'native_stage_sha256': NATIVE_STAGE_SHA256,
        'native_input_home': str(NATIVE_INPUT_HOME),
        'native_output_home': str(NATIVE_OUTPUT_HOME),
        'native_copy_argv': ['/bin/cp', '-a', str(NATIVE_INPUT_HOME), str(NATIVE_OUTPUT_HOME)],
        'native_patch_check_argv': ['git', '-C', str(NATIVE_OUTPUT_HOME), 'apply', '--check', NATIVE_PATCH_REL.as_posix()],
        'native_patch_apply_argv': ['git', '-C', str(NATIVE_OUTPUT_HOME), 'apply', NATIVE_PATCH_REL.as_posix()],
        'native_build_argv': ['make', '-C', str(NATIVE_OUTPUT_HOME / 'src'), '../bin/verifast',
                              'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'],
        'native_fingerprint_argv': [str(NATIVE_OUTPUT_HOME / 'bin/verifast'), *NATIVE_ARGV[1:]],
        'case_order': list(BODY_NAMES), 'universe_count': len(BODY_NAMES),
        'batch_indices': list(BATCH_INDICES),
        'batch_complete_is_universe_complete': False,
        'source_capture_only': True, 'native_fingerprint_only': True,
        'positive_verified_sha256': POSITIVE_VERIFIED_SHA256,
        'positive_original_sha256': POSITIVE_ORIGINAL_SHA256,
        'body_proof_run': False, 'caller_body_proof_admission': False,
        'typed_call_linkage': 'UNKNOWN', 'accepted': False,
        'publication_allowed': False, 'proof_credit': 0,
    }


def _safe_path(root: Path, path: Path, *, allow_missing: bool = False) -> Path:
    root = _assert_path_chain(Path(root), allow_missing=allow_missing)
    path = Path(path)
    need(path.is_absolute(), 'evidence path must be absolute')
    need(path == root or root in path.parents, 'path escapes evidence root')
    current = root
    if current.exists():
        need(current.is_dir() and not current.is_symlink(), 'unsafe evidence root')
    else:
        need(allow_missing, 'evidence root is missing')
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            need(not current.is_symlink(), 'symlink in evidence path: ' + str(current))
            if current != path:
                need(current.is_dir(), 'non-directory evidence parent: ' + str(current))
    resolved_root = root.resolve(strict=False)
    resolved_path = path.resolve(strict=False)
    need(resolved_path == resolved_root or resolved_root in resolved_path.parents,
         'resolved evidence path escapes root')
    return path


def _mkdir_chain(root: Path, directory: Path) -> None:
    root = root.absolute()
    directory = _safe_path(root, directory, allow_missing=True)
    missing: list[Path] = []
    cursor = directory
    while cursor != root and not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    need(cursor == root or root in cursor.parents, 'directory parent escapes root')
    for item in reversed(missing):
        item.mkdir()
        need(item.is_dir() and not item.is_symlink(), 'unsafe created directory')


def _write_json(root: Path, path: Path, value: dict[str, Any]) -> None:
    path = _safe_path(root, path, allow_missing=True)
    _mkdir_chain(root, path.parent)
    if path.exists():
        need(path.is_file() and not path.is_symlink(), 'refuse to replace unsafe JSON file')
    temp = path.with_name('.' + path.name + '.tmp')
    need(not temp.exists() and not temp.is_symlink(), 'temporary JSON path already exists')
    payload = json.dumps(value, sort_keys=True, indent=2) + '\n'
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _safe_path(root, temp)
        os.replace(temp, path)
    except BaseException:
        try:
            temp.unlink(missing_ok=True)
        finally:
            raise


def _read_regular(path: Path, root: Path | None = None) -> bytes:
    path = _assert_path_chain(Path(path), allow_missing=False)
    if root is not None:
        _safe_path(root, path)
    need(path.is_file() and not path.is_symlink(), 'missing, symlink, or non-file: ' + str(path))
    raw = path.read_bytes()
    return raw


def _status(record: object) -> str:
    if not isinstance(record, dict):
        return 'WRONG_TYPE'
    if 'status' in record:
        status = record['status']
        if isinstance(status, str) and status in ('RAN', 'NOT_RUN', 'TIMEOUT', 'ERROR'):
            return status
        return 'WRONG_TYPE'
    if record.get('skipped') is not None or record.get('exit') is None:
        return 'NOT_RUN'
    if type(record.get('exit')) is not int:
        return 'WRONG_TYPE'
    return 'RAN'


def _stage_errors(stage: object, label: str, expected_exit: int = 0,
                  expected_argv: list[str] | None = None,
                  expected_fixture: dict[str, str] | None = None) -> list[str]:
    if not isinstance(stage, dict):
        return [label + ' result is not an object']
    errors = []
    status = _status(stage)
    if status != 'RAN':
        errors.append(label + ' status is ' + status)
    if type(stage.get('exit')) is not int or stage.get('exit') != expected_exit:
        errors.append(label + ' exit differs from ' + str(expected_exit))
    if stage.get('fixture_integrity') is not True:
        errors.append(label + ' source fixture integrity is not true')
    if expected_argv is not None and stage.get('argv') != expected_argv:
        errors.append(label + ' argv differs from pinned command')
    if expected_fixture is not None and (stage.get('fixture_before') != expected_fixture or
            stage.get('fixture_after') != expected_fixture):
        errors.append(label + ' source fixture before/after hashes differ')
    return errors


def _logical_file(repo: Path, cloud_dir: Path, logical: str) -> Path:
    rel = Path(logical)
    if rel == CAPTURE_HELPER_REL:
        return cloud_dir / rel.name
    return repo / rel


def _load(path: Path, name: str, expected_sha: str):
    raw = _read_regular(path)
    need(expected_sha != 'PENDING' and digest(raw) == expected_sha,
         'pinned module differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'cannot import pinned module: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(digest(_read_regular(path)) == expected_sha,
         'pinned module changed during import: ' + str(path))
    return module


def _route(env: dict[str, str]) -> dict[str, str]:
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_PHASE_ENV) == R24_PHASE and env.get(R21_PHASE_ENV) == R21_PHASE and
         env.get('LANE') == LANE and env.get('SORT4_SELECT_PROFILE') == PROFILE and
         not env.get('GITHUB_ACTIONS'), 'exact R24/R21/profile Cloud route required')
    bad = sorted(key for key in env if key.startswith('SORT4_') and key not in ALLOWED_SORT4_ENV)
    need(not bad, 'ambient SORT4 opt-ins refused: ' + ', '.join(bad))
    return {'provider': env['SMALLSORT_EXECUTION_PROVIDER'], 'phase_id': env[R24_PHASE_ENV],
            'route_phase_id': env[R21_PHASE_ENV], 'lane': env['LANE'],
            'profile': env['SORT4_SELECT_PROFILE']}


def _check_mode(repo: Path, mode_path: Path) -> dict[str, Any]:
    exact = repo / MODE_REL
    need(mode_path.resolve() == exact.resolve() and mode_path.is_file() and
         not mode_path.is_symlink(), 'exact control capture mode path required')
    raw = mode_path.read_bytes()
    need(MODE_SHA256 != 'PENDING' and digest(raw) == MODE_SHA256,
         'control capture mode hash differs')
    value = json.loads(raw.decode('utf-8'))
    need(isinstance(value, dict) and value == expected_mode(repo),
         'control capture mode fields differ')
    return value


def _validate_context(args: argparse.Namespace, *, fresh: bool = False):
    raw_paths = {name: Path(getattr(args, name))
                 for name in ('repo', 'cloud_dir', 'evidence', 'tool_home', 'native_tool_home')}
    for name, path in raw_paths.items():
        _assert_path_chain(path, allow_missing=False)
    for name in ('schema', 'mode_file', 'capture_mode_file'):
        path = Path(getattr(args, name))
        _assert_path_chain(path, allow_missing=False)
    repo, cloud_dir, evidence, tool_home, native_home = tuple(
        raw_paths[name] for name in ('repo', 'cloud_dir', 'evidence', 'tool_home', 'native_tool_home'))
    need(all(path.is_absolute() and str(path).startswith('/workspace/')
             for path in (repo, cloud_dir, evidence, tool_home, native_home)),
         'all roots must be absolute Cloud /workspace paths')
    need(tool_home != native_home, 'capture and fingerprint tool homes must be separate')
    need(native_home == NATIVE_INPUT_HOME,
         'native fingerprint input must be the exact C6 F83 diagnostic tool home')
    candidate = getattr(args, 'candidate', None)
    need(isinstance(candidate, str) and re.fullmatch(r'[0-9a-f]{40}', candidate) is not None,
         'exact candidate SHA required')
    if fresh:
        out_root = evidence / SUMMARY_REL.parent
        need(not out_root.exists() and not out_root.is_symlink(),
             'control capture output already exists')
    return repo, cloud_dir, evidence, tool_home, native_home


def _load_constructor_inputs(repo: Path, cloud_dir: Path):
    profile_path = repo / CONSTRUCTOR_PROFILE_REL
    profile_raw = _read_regular(profile_path)
    need(digest(profile_raw) == CONSTRUCTOR_PROFILE_SHA256,
         'R21 constructor profile differs')
    profile = json.loads(profile_raw.decode('utf-8'))
    need(profile.get('actual_indexed_calls') == 5 and
         profile.get('body_action') == 'full-body-c1-recovery' and
         profile.get('cloud_build_enabled') is False and
         profile.get('std_source_sha256', {}).get(SOURCE_REL.as_posix()) == SOURCE_SHA256,
         'R21 profile is not the dormant count-five constructor input')
    modules = {}
    for name, (logical, expected) in HELPER_PINS.items():
        path = _logical_file(repo, cloud_dir, logical)
        if name in ('recover_pair', 'recover_four'):
            need(digest(_read_regular(path)) == expected,
                 'pinned recovery source differs: ' + str(path))
            continue
        modules[name] = _load(path, 'r24_w4_control_' + name, expected)
    need(profile.get('a1_actual_body_sha256') == HELPER_PINS['sort4_body'][1] and
         profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-body-c1.py') == HELPER_PINS['c1'][1] and
         profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-body-c2.py') == HELPER_PINS['c2_c5'][1] and
         profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-recover-pair.rs') == HELPER_PINS['recover_pair'][1] and
         profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-recover-four.rs') == HELPER_PINS['recover_four'][1] and
         profile.get('a1_ghost_grammar_sha256') == HELPER_PINS['ghost_grammar'][1],
         'R21 profile dependency pins differ')
    return profile, modules


def _construct_sources(repo: Path, cloud_dir: Path, modules: dict[str, Any]) -> list[dict[str, Any]]:
    source_path = repo / SOURCE_REL
    source = _read_regular(source_path)
    need(digest(source) == SOURCE_SHA256, 'pinned Rust source bytes differ')
    blob = subprocess.check_output(['git', '-C', str(repo), 'hash-object', str(source_path)], text=True).strip()
    need(blob == SOURCE_BLOB, 'pinned Rust source Git blob differs')
    body, c1, indexed, ghost, capture = (modules[key] for key in
        ('sort4_body', 'c1', 'c2_c5', 'ghost_strip', 'capture'))
    pair_raw = _read_regular(_logical_file(repo, cloud_dir, HELPER_PINS['recover_pair'][0]))
    four_raw = _read_regular(_logical_file(repo, cloud_dir, HELPER_PINS['recover_four'][0]))
    need(digest(pair_raw) == HELPER_PINS['recover_pair'][1] and
         digest(four_raw) == HELPER_PINS['recover_four'][1], 'pinned recovery bytes differ')
    pair, four = pair_raw, four_raw
    c5v, original, c5meta = indexed.construct_c5(
        source, ghost, capture, pair, four, c1, body.construct_actual, body.lemma_metadata)
    refreshed_positive = body.refresh_callback_coordinates(
        ('sort4_stable', c5v, original, c5meta))
    need(isinstance(refreshed_positive, tuple) and len(refreshed_positive) == 4,
         'positive callback coordinate refresh returned wrong shape')
    positive_name, c5v, original, c5meta = refreshed_positive
    need(positive_name == 'sort4_stable' and ghost.strip_ghost(c5v) == original,
         'positive full C5 fixture changed runtime bytes')
    need(digest(c5v) == POSITIVE_VERIFIED_SHA256 and
         digest(original) == POSITIVE_ORIGINAL_SHA256,
         'positive differs from the exact previously captured W4 source pair')
    need(all(original.count(fragment) == count for fragment, count in SOURCE_COUNTS.items()),
         'actual runtime source counts differ from 5/8/4')
    # The source controls must all retain the actual count-five body.  C1/C2
    # mutation helpers support that full body directly. C3/C4 helpers are
    # prefix-only, so their exact mutations are reproduced below against the
    # count-five bytes with a full-source/count check instead of bypassing their
    # prefix precondition or falsifying constructor metadata.
    c1_control_meta = {**c5meta, 'required_lemmas': [row for row in c5meta['required_lemmas']
        if row.get('name') != 'recover_four_sources']}
    control_groups = [
        [('c1-' + row[0], *row[1:]) for row in
         c1.resource_controls(c5v, ghost, c1_control_meta, body.lemma_metadata)],
        indexed.resource_controls(c5v, original, ghost, four, c5meta, body.lemma_metadata),
        _indexed_controls_at_count5(3, c5v, original, ghost, four, c5meta, indexed,
                                   body.lemma_metadata),
        _indexed_controls_at_count5(4, c5v, original, ghost, four, c5meta, indexed,
                                   body.lemma_metadata),
        indexed.resource_controls_c5(c5v, original, ghost, four, c5meta, body.lemma_metadata),
        _c5_scope_controls(c5v, original, ghost, c5meta, indexed),
    ]
    controls = []
    for group in control_groups:
        for name, verified, original_bytes, metadata in group:
            metadata = dict(metadata)
            metadata['generated_source_sha256'] = digest(verified)
            refreshed = body.refresh_callback_coordinates((name, verified, original_bytes, metadata))
            need(isinstance(refreshed, tuple) and len(refreshed) == 4 and refreshed[0] == name,
                 'control callback coordinate refresh returned wrong shape: ' + name)
            controls.append(refreshed)
    need(tuple([('positive' if i == 0 else row[0]) for i, row in
                enumerate([('positive',)] + [(x[0],) for x in controls])]) == BODY_NAMES,
         'constructor control order differs from closed universe')
    all_rows = [{'name': 'positive', 'verified': c5v, 'original': original,
                 'metadata': c5meta, 'kind': 'positive'}]
    all_rows.extend({'name': name, 'verified': verified, 'original': original_bytes,
                     'metadata': meta, 'kind': 'source-control'}
                    for name, verified, original_bytes, meta in controls)
    need(tuple(row['name'] for row in all_rows) == BODY_NAMES,
         'constructor returned noncanonical full control inventory')
    return all_rows


def _indexed_controls_at_count5(k: int, verified: bytes, original: bytes, ghost,
                                four_recovery: bytes, meta: dict[str, Any], indexed,
                                lemma_metadata) -> list[tuple[Any, ...]]:
    need(k in (3, 4) and meta.get('actual_indexed_calls') == 5,
         'C3/C4 controls require the actual count-five constructor output')
    need(ghost.strip_ghost(verified) == original and
         all(original.count(fragment) == count for fragment, count in SOURCE_COUNTS.items()),
         'C3/C4 count-five control changed runtime body or source counts')
    if k == 3:
        marker, typed_call, normal = indexed.MARKER3, indexed.C3_TYPED_CALL, indexed.NORMAL3
        left_pre, right_pre = indexed.C3_LEFT_PRECREATE, indexed.C3_RIGHT_PRECREATE
        operands, drop_slots, token_slot, wrong_left = (b'c', b'a'), (1, 3), 0, b'b'
        expected = indexed.C3_EXPECTED
    else:
        marker, typed_call, normal = indexed.MARKER4, indexed.C4_TYPED_CALL, indexed.NORMAL4
        left_pre, right_pre = indexed.C4_LEFT_PRECREATE, indexed.C4_RIGHT_PRECREATE
        operands, drop_slots, token_slot, wrong_left = (b'd', b'b'), (0, 2), 3, b'a'
        expected = indexed.C4_EXPECTED
    need(verified.count(marker) == verified.count(typed_call) == verified.count(normal) == 1,
         f'C{k} exact marker/call/recovery unavailable in count-five body')
    lifetime = b'cmp%d_k' % k
    share = lambda n: b'        //@ share_full_borrow::<T>(' + lifetime + b', t, ' + indexed._slot(n) + b');\n'
    missing_shares = verified
    for slot in drop_slots:
        need(missing_shares.count(share(slot)) == 1, f'C{k} one share line for slot {slot}')
        missing_shares = missing_shares.replace(share(slot), b'', 1)
    borrow = (b'        //@ borrow(' + lifetime + b', <T>.full_borrow_content(t, ' +
              indexed._slot(token_slot) + b'));\n')
    need(verified.count(borrow) == 1 and verified.count(share(token_slot)) == 1,
         f'C{k} one end-token producer')
    missing_resource = verified.replace(borrow, b'', 1).replace(share(token_slot), b'', 1)
    pre = lambda side, operand: b'        //@ let %s%d_ref = precreate_ref::<T>(%s);\n' % (side, k, operand)
    wrong_order = verified.replace(left_pre + right_pre,
        pre(b'left', operands[1]) + pre(b'right', operands[0]), 1)
    wrong_ref = verified.replace(left_pre, pre(b'left', wrong_left), 1)
    wrong_index = verified.replace(b'__vf_callback_unwind_four(%d);' % k,
        b'__vf_callback_unwind_four(%d);' % (k - 1), 1)
    missing_pred = indexed.ghost_declaration(
        four_recovery, b'pred callback_four_debt_without_fourth<T>')
    debt_marker = marker.replace(b'callback_four_debt::<T>(',
        b'callback_four_debt_without_fourth::<T>(', 1)
    missing_token = indexed._insert_before_target(verified.replace(marker, debt_marker, 1),
        missing_pred)
    displaced = verified.replace(marker + typed_call, typed_call + marker, 1)
    # Count-five source has no later comparator to use as a sentinel. Put a
    # spurious index-six marker after the fifth recovery and before the selector.
    lo_select = indexed.LO_SELECT
    need(verified.count(lo_select) == 1, 'count-five selector anchor missing for overflow control')
    overflow_marker = (b'/*@ {\n'
        b'            __vf_callback_unwind_four(6);\n'
        b'            { close callback_four_debt::<T>(t, cmp6_k, v_base, left6_ref, '
        b'right6_ref, left6_fraction, right6_fraction); }\n'
        b'            { recover_four_sources::<T>(v_base); }\n'
        b'        } @*/\n')
    overflow = verified.replace(lo_select, overflow_marker + lo_select, 1)
    names = ('missing-unselected-share', 'missing-unrelated-end-token',
             'wrong-ordered-ref-pair', 'wrong-ref-resource', 'wrong-marker-index',
             'missing-fourth-debt-token', 'displaced-marker', 'index-overflow-marker')
    candidates = (missing_shares, missing_resource, wrong_order, wrong_ref, wrong_index,
                  missing_token, displaced, overflow)
    rows = []
    for name, candidate, reason in zip(names, candidates, expected):
        need(candidate != verified and ghost.strip_ghost(candidate) == original,
             f'C{k}-{name} must be an annotation-only mutation')
        need(all(original.count(fragment) == count for fragment, count in SOURCE_COUNTS.items()),
             f'C{k}-{name} source runtime counts differ')
        rows.append((f'c{k}-{name}-negative', candidate, original,
                     {**meta, 'control_call_index': k,
                      'control_mutation': name, 'expected_rejection': reason,
                      'summary_eligible': False, 'proof_credit': False}))
    return rows


def _c5_scope_controls(verified: bytes, original: bytes, ghost,
                       meta: dict[str, Any], indexed) -> list[tuple[Any, ...]]:
    need(meta.get('actual_indexed_calls') == 5 and ghost.strip_ghost(verified) == original,
         'C5 scope controls require exact count-five source and runtime equality')
    need(all(original.count(fragment) == count for fragment, count in SOURCE_COUNTS.items()),
         'C5 scope control source counts differ')
    marker = indexed.C5_SCOPE_MARKER
    precreate = indexed.C5_LEFT_PRECREATE
    normal = indexed.NORMAL5
    selector = indexed.LO_SELECT
    need(all(verified.count(anchor) == 1 for anchor in (marker, precreate, normal, selector)),
         'C5 scope-control source anchor is absent or ambiguous')
    escape = verified.replace(precreate, b'', 1)
    escape = escape.replace(marker, precreate + marker, 1)
    missing_marker = verified.replace(marker, b'', 1)
    cross_read = verified.replace(normal, normal + b'        //@ assert left5_ref == left5_ref;\n', 1)
    variants = (
        ('c5-scope-escape-negative', escape, 'scope-validator target remains OPEN; source-only mutation'),
        ('c5-missing-scope-marker-negative', missing_marker, 'scope-validator target remains OPEN; source-only mutation'),
        ('c5-cross-scope-read-negative', cross_read, 'scope-validator target remains OPEN; source-only mutation'),
    )
    rows = []
    for name, candidate, note in variants:
        need(candidate != verified and ghost.strip_ghost(candidate) == original,
             name + ' must change annotations only')
        need(all(original.count(fragment) == count for fragment, count in SOURCE_COUNTS.items()),
             name + ' changed runtime source counts')
        rows.append((name, candidate, original,
                     {**meta, 'scope_control': name,
                      'generated_source_sha256': digest(candidate),
                      'native_scope_validator_executed': False,
                      'source_observation_note': note,
                      'summary_eligible': False, 'proof_credit': False}))
    return rows


def _tool_hashes(tool_home: Path) -> dict[str, str]:
    old_hashes = {
        'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
        'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
        'bin/verifast': '01eaa29335277643e2c16dd35b561e2aecee867fbdd64cf13b8eb1d082602cd6',
        'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
        'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
        'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
        'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
        'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007',
    }
    hashes = {}
    for rel, expected in old_hashes.items():
        raw = _read_regular(tool_home / rel)
        need(digest(raw) == expected, 'frozen 8a capture tool hash differs: ' + rel)
        hashes[rel] = digest(raw)
    return hashes


def _tool_sources(native_home: Path, *, expected_sources: dict[str, str] | None = None,
                  expected_binary: str | None = 'INPUT') -> dict[str, str]:
    need(NATIVE_TRANSLATOR_SHA256 != 'PENDING' and NATIVE_TOOL_SOURCE_HASHES,
         'native fingerprint tool pins are not finalized')
    source_pins = NATIVE_TOOL_SOURCE_HASHES if expected_sources is None else expected_sources
    hashes = {}
    for rel, expected in source_pins.items():
        raw = _read_regular(native_home / rel)
        need(digest(raw) == expected, 'native input tool source hash differs: ' + rel)
        hashes[rel] = digest(raw)
    binary = _read_regular(native_home / 'bin/verifast')
    need(bool(binary), 'native input verifier binary is empty')
    pin = NATIVE_BINARY_SHA256 if expected_binary == 'INPUT' else expected_binary
    if pin is not None and pin != 'PENDING':
        need(digest(binary) == pin, 'native verifier binary pin differs')
    return {**hashes, 'bin/verifast': digest(binary)}


def _patched_source_pins() -> dict[str, str]:
    result = dict(NATIVE_TOOL_SOURCE_HASHES)
    result['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = NATIVE_TRANSLATOR_SHA256
    return result


def _validate_native_input_identity(repo: Path, native_home: Path) -> dict[str, str]:
    path = repo / NATIVE_INPUT_IDENTITY_REL
    raw = _read_regular(path)
    need(digest(raw) == NATIVE_INPUT_IDENTITY_SHA256,
         'source-reported F83 diagnostic tool identity record differs')
    record = json.loads(raw.decode('utf-8'))
    need(isinstance(record, dict) and
         record.get('schema') == 'select-r24-w4-source-reported-tool-identity-v1' and
         record.get('classification') == 'C6_INPUT_DIAGNOSTIC_TOOL_IDENTITY_ONLY' and
         record.get('assurance') == 'SOURCE_REPORTED' and
         record.get('accepted') is False and record.get('publication_allowed') is False and
         record.get('caller_body_proof_admission') is False and
         type(record.get('proof_credit')) is int and record.get('proof_credit') == 0,
         'F83 source-reported identity is not diagnostic-only')
    reported = record.get('tool_hashes')
    need(isinstance(reported, dict) and set(reported) ==
         set(NATIVE_TOOL_SOURCE_HASHES) | {'bin/verifast'},
         'F83 recorded inventory key set differs')
    observed = _tool_sources(native_home)
    need(observed == reported, 'physical F83 tool copy differs from source-reported inventory')
    return observed


def _native_input_identity_record(repo: Path) -> dict[str, Any]:
    path = repo / NATIVE_INPUT_IDENTITY_REL
    raw = _read_regular(path)
    need(digest(raw) == NATIVE_INPUT_IDENTITY_SHA256,
         'source-reported F83 diagnostic tool identity record differs')
    value = json.loads(raw.decode('utf-8'))
    need(isinstance(value, dict), 'F83 source identity JSON is not an object')
    return value


def _normalize_c6_tool_inventory(summary: dict[str, Any]) -> dict[str, str]:
    value = summary.get('diagnostic_tool_hashes_after_build')
    expected_keys = set(NATIVE_TOOL_SOURCE_HASHES) | {'bin/verifast'}
    need(isinstance(value, dict) and set(value) == expected_keys,
         'C6 diagnostic tool inventory has wrong exact key set')
    flattened = {}
    for rel, row in value.items():
        need(isinstance(row, dict) and row.get('regular') is True and
             type(row.get('bytes')) is int and row['bytes'] > 0 and
             isinstance(row.get('sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', row['sha256']) and
             row.get('matches') is True,
             'C6 diagnostic tool entry missing/unsafe/unmatched: ' + rel)
        if rel == 'bin/verifast':
            need(row.get('expected_sha256') == 'DIAGNOSTIC_BUILD_OUTPUT_RECORDED' and
                 row.get('sha256') == NATIVE_BINARY_SHA256,
                 'C6 recorded diagnostic binary differs from exact F83 input binary')
        else:
            need(row.get('expected_sha256') == NATIVE_TOOL_SOURCE_HASHES[rel] and
                 row.get('sha256') == NATIVE_TOOL_SOURCE_HASHES[rel],
                 'C6 diagnostic source hash differs from exact F83 input: ' + rel)
        flattened[rel] = row['sha256']
    return flattened


def _stage_call(stage_runner, name: str, argv: list[str], root: Path,
                env: dict[str, str], fixture_hashes: dict[str, str],
                deadline: int, cap: int, stdin: str | None = None,
                stdout: str | None = None):
    parameters = inspect.signature(stage_runner).parameters
    need(('stdin_name' in parameters and 'stdout_name' in parameters) or
         any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()),
         'stage service must expose the frozen stdin_name/stdout_name API')
    return stage_runner(name, argv, root, env, fixture_hashes, deadline, cap,
                        stdin_name=stdin, stdout_name=stdout)


def _run_capture_case(args: argparse.Namespace, *, row: dict[str, Any],
                      case_root: Path, tool_home: Path, schema: Path,
                      stage_runner, capture_module) -> dict[str, Any]:
    fixture = case_root / 'fixture'
    verified_dir, original_dir = fixture / 'verified', fixture / 'original'
    _mkdir_chain(Path(args.evidence).resolve(), verified_dir)
    _mkdir_chain(Path(args.evidence).resolve(), original_dir)
    verified_path, original_path = verified_dir / 'lib.rs', original_dir / 'lib.rs'
    for path, content in ((verified_path, row['verified']), (original_path, row['original'])):
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    fixture_hashes = {'verified/lib.rs': digest(row['verified']),
                      'original/lib.rs': digest(row['original'])}
    env = dict(os.environ)
    env['PATH'] = str(tool_home / 'bin') + os.pathsep + env.get('PATH', '')
    exporter = str(tool_home / 'bin/vf-rust-mir-exporter')
    schema_arg = str(schema.resolve())
    compiler = str(Path(args.compiler_sysroot).resolve())
    stages: dict[str, Any] = {}
    stages['normal-export'] = _stage_call(stage_runner, 'normal-export',
        [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021'],
        fixture, env, fixture_hashes, args.deadline_epoch, STAGE_CAPS['normal-export'],
        stdout='normal-mir.bin')
    if _status(stages['normal-export']) == 'RAN' and stages['normal-export'].get('exit') == 0:
        stages['normal-decode'] = _stage_call(stage_runner, 'normal-decode',
            ['capnp', 'decode', schema_arg, 'VfMir'], fixture, env, fixture_hashes,
            args.deadline_epoch, STAGE_CAPS['normal-decode'],
            stdin='normal-mir.bin', stdout='normal-mir.txt')
    else:
        stages['normal-decode'] = {'exit': None, 'skipped': 'normal exporter did not complete'}
    stages['readonly-export'] = _stage_call(stage_runner, 'readonly-export',
        [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021',
         '--vf-rust-mir-exporter:preprocess-readonly'], fixture, env, fixture_hashes,
        args.deadline_epoch, STAGE_CAPS['readonly-export'], stdout='readonly-mir.bin')
    if _status(stages['readonly-export']) == 'RAN' and stages['readonly-export'].get('exit') == 0:
        stages['readonly-decode'] = _stage_call(stage_runner, 'readonly-decode',
            ['capnp', 'decode', schema_arg, 'VfMir'], fixture, env, fixture_hashes,
            args.deadline_epoch, STAGE_CAPS['readonly-decode'],
            stdin='readonly-mir.bin', stdout='readonly-mir.txt')
    else:
        stages['readonly-decode'] = {'exit': None, 'skipped': 'readonly exporter did not complete'}
    stages['refinement'] = _stage_call(stage_runner, 'refinement',
        [str(tool_home / 'bin/refinement-checker'), '--rustc-args', '--edition 2021',
         'original/lib.rs', 'verified/lib.rs'], fixture, env, fixture_hashes,
        args.deadline_epoch, STAGE_CAPS['refinement'])
    errors = []
    expected_argv = {
        'normal-export': [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021'],
        'normal-decode': ['capnp', 'decode', schema_arg, 'VfMir'],
        'readonly-export': [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021',
                            '--vf-rust-mir-exporter:preprocess-readonly'],
        'readonly-decode': ['capnp', 'decode', schema_arg, 'VfMir'],
        'refinement': [str(tool_home / 'bin/refinement-checker'), '--rustc-args', '--edition 2021',
                       'original/lib.rs', 'verified/lib.rs'],
    }
    for label in ('normal-export', 'normal-decode', 'readonly-export', 'readonly-decode', 'refinement'):
        errors.extend(_stage_errors(stages.get(label), label,
                                    expected_argv=expected_argv[label],
                                    expected_fixture=fixture_hashes))
    mir_info: dict[str, Any] = {}
    for mode in ('normal', 'readonly'):
        decoded_path = fixture / f'{mode}-mir.txt'
        if not decoded_path.is_file() or decoded_path.is_symlink():
            errors.append(mode + ' decoded MIR is missing')
            continue
        decoded = decoded_path.read_text(encoding='utf-8', errors='strict')
        function_name, function_record = capture_module.complete_function_record(decoded, 'sort4_stable')
        if function_name != 'sort4_stable' or not isinstance(function_record, str):
            errors.append(mode + ' complete_function_record returned wrong target/type')
            continue
        function_path = case_root / f'{mode}-sort4-full-mir.txt'
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(function_path, flags, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(function_record)
            stream.flush()
            os.fsync(stream.fileno())
        graph = capture_module.graph_inventory(decoded_path, case_root, mode)
        mir_info[mode] = {
            'decoded_sha256': digest(decoded.encode('utf-8')),
            'full_function_record': function_path.relative_to(Path(args.evidence)).as_posix(),
            'full_function_record_sha256': digest(function_record.encode('utf-8')),
            'graph_inventory': graph,
            'function_name': function_name,
        }
    source_after = _read_regular(verified_path)
    original_after = _read_regular(original_path)
    if digest(source_after) != fixture_hashes['verified/lib.rs'] or digest(original_after) != fixture_hashes['original/lib.rs']:
        errors.append('source fixture changed during capture')
    return {'stages': stages, 'stage_errors': errors,
            'fixture': {'verified': {'path': verified_path.relative_to(Path(args.evidence)).as_posix(),
                                     'bytes': len(row['verified']), 'sha256': digest(row['verified'])},
                        'original': {'path': original_path.relative_to(Path(args.evidence)).as_posix(),
                                     'bytes': len(row['original']), 'sha256': digest(row['original'])}},
            'mir': mir_info, 'fixture_hashes': fixture_hashes}


def _prepare_native_tool(args: argparse.Namespace, *, work_root: Path,
                         cloud_dir: Path,
                         native_home: Path, stage_runner) -> dict[str, Any]:
    need(NATIVE_PATCH_SHA256 != 'PENDING' and NATIVE_MANIFEST_SHA256 != 'PENDING',
         'native fingerprint patch/manifest pins are not finalized')
    patch_path = _logical_file(Path(args.repo).resolve(), cloud_dir, NATIVE_PATCH_REL.as_posix())
    manifest_path = Path(args.repo).resolve() / NATIVE_MANIFEST_REL
    patch_raw = _read_regular(patch_path)
    manifest_raw = _read_regular(manifest_path)
    need(digest(patch_raw) == NATIVE_PATCH_SHA256 and
         digest(manifest_raw) == NATIVE_MANIFEST_SHA256,
         'native fingerprint patch or manifest hash differs')
    manifest = json.loads(manifest_raw.decode('utf-8'))
    need(isinstance(manifest, dict) and manifest.get('schema') ==
         'select-r24-w4-control-fingerprint-manifest-v1' and
         manifest.get('base_translator_sha256') == NATIVE_BASE_TRANSLATOR_SHA256 and
         manifest.get('result_translator_sha256') == NATIVE_TRANSLATOR_SHA256 and
         manifest.get('patch') == {'path': NATIVE_PATCH_REL.as_posix(),
                                   'sha256': NATIVE_PATCH_SHA256} and
         manifest.get('expected_native_exit') == 2 and
         manifest.get('environment_prefix') == 'SORT4_R24_W4_DATA_FINGERPRINT_' and
         manifest.get('mode_value') == '1' and
         manifest.get('outputs') == list(NATIVE_FILES) and
         manifest.get('expected_refusal') == 'snapshot complete; no proof rule admitted' and
         manifest.get('stdout_prefix') == 'SORT4-R24-W4-DATA:' and
         manifest.get('typed_call_linkage') == 'UNKNOWN' and
         manifest.get('caller_body_proof_admission') is False and
         manifest.get('accepted') is False and manifest.get('publication_allowed') is False and
         type(manifest.get('proof_credit')) is int and manifest.get('proof_credit') == 0,
         'native control fingerprint manifest fields differ')
    source_before = _tool_sources(native_home)
    need(source_before.get('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') ==
         NATIVE_BASE_TRANSLATOR_SHA256, 'native base translator source differs')
    need(source_before.get('bin/verifast') is not None, 'native base binary missing')
    target = NATIVE_OUTPUT_HOME
    _assert_path_chain(target, allow_missing=True)
    need(not target.exists() and not target.is_symlink(), 'native fingerprint copy target already exists')
    env = dict(os.environ)
    env['PATH'] = env.get('PATH', os.defpath)
    copy = _stage_call(stage_runner, 'native-tool-copy',
        ['/bin/cp', '-a', str(native_home), str(target)], work_root, env, {},
        args.deadline_epoch, 180)
    errors = _stage_errors(copy, 'native-tool-copy')
    if not isinstance(copy, dict) or copy.get('argv') != ['/bin/cp', '-a', str(native_home), str(target)]:
        errors.append('native tool copy argv differs')
    if errors:
        return {'target': str(target), 'copy_stage': copy, 'errors': errors}
    _assert_path_chain(target, allow_missing=False)
    source_copied = _tool_sources(target)
    if source_copied != source_before:
        errors.append('native tool source or binary changed while copying')
    check = _stage_call(stage_runner, 'native-patch-check',
        ['git', '-C', str(target), 'apply', '--check', str(patch_path)], work_root,
        env, {}, args.deadline_epoch, 120)
    errors.extend(_stage_errors(check, 'native-patch-check'))
    if not isinstance(check, dict) or check.get('argv') != ['git', '-C', str(target), 'apply', '--check', str(patch_path)]:
        errors.append('native patch-check argv differs')
    apply = None
    build = None
    if not errors:
        apply = _stage_call(stage_runner, 'native-patch-apply',
            ['git', '-C', str(target), 'apply', str(patch_path)], work_root,
            env, {}, args.deadline_epoch, 120)
        errors.extend(_stage_errors(apply, 'native-patch-apply'))
        if not isinstance(apply, dict) or apply.get('argv') != ['git', '-C', str(target), 'apply', str(patch_path)]:
            errors.append('native patch-apply argv differs')
    if not errors:
        build = _stage_call(stage_runner, 'native-tool-build',
            ['make', '-C', str(target / 'src'), '../bin/verifast',
             'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'], work_root, env, {},
            args.deadline_epoch, 540)
        errors.extend(_stage_errors(build, 'native-tool-build'))
        if not isinstance(build, dict) or build.get('argv') != ['make', '-C', str(target / 'src'),
                '../bin/verifast', 'WITHOUT_LABLGTK=yes', 'VERBOSE=yes']:
            errors.append('native tool build argv differs')
    after = None
    if target.is_dir() and not target.is_symlink():
        expected_after = dict(NATIVE_TOOL_SOURCE_HASHES)
        expected_after['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = NATIVE_TRANSLATOR_SHA256
        after = _tool_sources(target, expected_sources=expected_after, expected_binary=None)
        if any(after.get(rel) != value for rel, value in expected_after.items()):
            errors.append('patched native tool source identity differs')
    return {'target': str(target), 'source_before': source_before,
            'source_copied': source_copied, 'source_after_build': after,
            'copy_stage': copy, 'patch_check_stage': check, 'patch_apply_stage': apply,
            'build_stage': build, 'errors': errors}


def _parse_native_marker(stdout_text: str, stderr_text: str, source_sha: str, unit: dict[str, Any],
                         body: dict[str, Any]) -> list[str]:
    errors = []
    marker_re = re.compile(
        r'^SORT4-R24-W4-DATA: source_sha256=([0-9a-f]{64}) '
        r'unit_bytes=([0-9]+) unit_sha256=([0-9a-f]{64}) '
        r'body_bytes=([0-9]+) body_sha256=([0-9a-f]{64}) body_name=sort4_stable$')
    markers = [line for line in stdout_text.splitlines() if line.startswith(NATIVE_STDOUT_PREFIX)]
    if len(markers) != 1:
        errors.append('native fingerprint stdout marker count differs')
        return errors
    match = marker_re.fullmatch(markers[0])
    expected = (source_sha, str(unit['bytes']), unit['sha256'],
                str(body['bytes']), body['sha256'])
    if match is None or match.groups() != expected:
        errors.append('native fingerprint stdout fields differ from physical snapshots')
    combined = stdout_text + '\n' + stderr_text
    if combined.count('SORT4-R24-W4-DATA:') != 2 or stderr_text.splitlines()[:1] != [NATIVE_REFUSAL_STDERR]:
        errors.append('native fingerprint protocol marker/refusal occurrence count differs')
    refusal_lines = [line for line in stderr_text.splitlines()
                     if line.startswith('Fatal error: exception Failure(')]
    if refusal_lines.count(NATIVE_REFUSAL_STDERR) != 1:
        errors.append('native wrapped refusal line differs or is duplicated')
    return errors


def _native_fingerprint(args: argparse.Namespace, *, row: dict[str, Any],
                        case_root: Path, native_home: Path,
                        stage_runner) -> dict[str, Any]:
    fixture = case_root / 'fixture'
    verified = fixture / 'verified/lib.rs'
    source = _read_regular(verified, Path(args.evidence).resolve())
    source_hash = digest(source)
    fingerprint_dir = case_root / 'native' / 'fingerprints'
    _mkdir_chain(Path(args.evidence).resolve(), fingerprint_dir)
    native_env_dir = fingerprint_dir.resolve()
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('SORT4_') and key not in ALLOWED_SORT4_ENV:
            env.pop(key)
    env['PATH'] = str(native_home / 'bin') + os.pathsep + env.get('PATH', '')
    env.update({
        'SORT4_R24_W4_DATA_FINGERPRINT_MODE': '1',
        'SORT4_R24_W4_DATA_FINGERPRINT_EVIDENCE_DIR': str(native_env_dir),
        'SORT4_R24_W4_DATA_FINGERPRINT_SOURCE_SHA256': source_hash,
    })
    argv = [str(native_home / NATIVE_ARGV[0]), *NATIVE_ARGV[1:]]
    stage = _stage_call(stage_runner, 'native-fingerprint', argv, fixture, env,
        {'verified/lib.rs': source_hash}, args.deadline_epoch,
        STAGE_CAPS['native-fingerprint'], stdout='native-fingerprint.stdout.log')
    errors = []
    expected_argv = [str(native_home / NATIVE_ARGV[0]), *NATIVE_ARGV[1:]]
    expected_fixture = {'verified/lib.rs': source_hash}
    if _status(stage) != 'RAN':
        errors.append('native fingerprint stage status is ' + _status(stage))
    stage_obj = stage if isinstance(stage, dict) else {}
    if type(stage_obj.get('exit')) is not int or stage_obj.get('exit') != 2:
        errors.append('native fingerprint stage exit is not exact refusal exit 2')
    if stage_obj.get('fixture_integrity') is not True:
        errors.append('native fingerprint changed its verified source fixture')
    if stage_obj.get('argv') != expected_argv:
        errors.append('native fingerprint argv differs from exact command')
    if stage_obj.get('fixture_before') != expected_fixture or stage_obj.get('fixture_after') != expected_fixture:
        errors.append('native fingerprint source before/after hashes differ')
    records: dict[str, Any] = {}
    file_paths = {
        'unit': fingerprint_dir / 'caller-native-unit.marshal',
        'body': fingerprint_dir / 'caller-native-body-0.marshal',
    }
    for key, path in file_paths.items():
        try:
            raw = _read_regular(path, Path(args.evidence).resolve())
            need(bool(raw), key + ' fingerprint is empty')
            records[key] = {'path': path.relative_to(Path(args.evidence)).as_posix(),
                            'bytes': len(raw), 'sha256': digest(raw)}
        except BaseException as exc:
            errors.append(key + ' fingerprint missing/invalid: ' + str(exc))
    data_path = fingerprint_dir / 'native-data.json'
    native_json: dict[str, Any] | None = None
    try:
        raw = _read_regular(data_path, Path(args.evidence).resolve())
        native_json = json.loads(raw.decode('utf-8'))
        need(isinstance(native_json, dict), 'native-data.json is not an object')
        expected = {
            'schema': 'select-r24-w4-native-data-fingerprint-v1',
            'classification': 'SOURCE_ONLY_NATIVE_DATA_CAPTURE',
            'complete': True,
            'body_name': 'sort4_stable', 'body_index': 0,
            'body_inventory': ['sort4_stable'],
            'expected_refusal': 'snapshot complete; no proof rule admitted',
            'body_proof_run': False, 'accepted': False,
            'publication_allowed': False, 'caller_body_proof_admission': False,
            'typed_call_linkage': 'UNKNOWN', 'proof_credit': 0,
        }
        for key, value in expected.items():
            if type(native_json.get(key)) is not type(value) or native_json.get(key) != value:
                errors.append('native-data field differs: ' + key)
        if native_json.get('build_id') != os.environ.get('CLOUD_BUILD_ID'):
            errors.append('native-data Build ID differs')
        source_record = native_json.get('source')
        if type(source_record) is not dict or type(source_record.get('bytes')) is not int or \
           source_record != {'path': str(verified.resolve()), 'bytes': len(source), 'sha256': source_hash}:
            errors.append('native-data source identity differs from physical case source')
        for key, filename in (('unit', 'caller-native-unit.marshal'),
                              ('body', 'caller-native-body-0.marshal')):
            expected_record = records.get(key)
            reported = native_json.get(key)
            if not isinstance(reported, dict) or expected_record is None:
                errors.append('native-data ' + key + ' identity missing')
            else:
                if type(reported.get('bytes')) is not int or reported.get('path') != filename or reported.get('bytes') != expected_record['bytes'] or reported.get('sha256') != expected_record['sha256']:
                    errors.append('native-data ' + key + ' identity differs from physical snapshot')
    except BaseException as exc:
        errors.append('native-data.json missing/invalid: ' + str(exc))
    stdout_log = stage_obj.get('stdout')
    stderr_log = stage_obj.get('stderr')
    logs = []
    log_texts = {}
    for label, rel in (('stdout', stdout_log), ('stderr', stderr_log)):
        if isinstance(rel, str) and rel not in logs:
            logs.append(rel)
        try:
            if isinstance(rel, str):
                log_texts[label] = _read_regular(fixture / rel, Path(args.evidence).resolve()).decode('utf-8', 'strict')
        except BaseException as exc:
            errors.append('native stage log missing/invalid: ' + str(exc))
    if len(records) == 2:
        errors.extend(_parse_native_marker(log_texts.get('stdout', ''), log_texts.get('stderr', ''),
                                           source_hash, records['unit'], records['body']))
    else:
        errors.append('native marker cannot be bound without both snapshots')
    return {'stage': stage, 'native_data': native_json,
            'snapshots': records, 'log_paths': logs,
            'errors': errors, 'source_sha256': source_hash,
            'complete': not errors}


def _artifact_inventory(root: Path, evidence: Path) -> list[dict[str, Any]]:
    items = []
    need(root.is_dir() and not root.is_symlink() and root.resolve().is_relative_to(evidence.resolve()),
         'case root missing, symlinked, or outside evidence')
    for parent, dirs, files in os.walk(root, topdown=True, followlinks=False):
        parent_path = Path(parent)
        for name in list(dirs):
            path = parent_path / name
            need(not path.is_symlink() and path.is_dir(), 'symlink/non-directory in case artifacts')
        for name in files:
            path = parent_path / name
            raw = _read_regular(path, evidence)
            items.append({'path': path.relative_to(evidence).as_posix(),
                          'bytes': len(raw), 'sha256': digest(raw)})
    return sorted(items, key=lambda item: item['path'])


def _summary_root_inventory(root: Path, evidence: Path) -> list[dict[str, Any]]:
    excluded = {SUMMARY_REL.as_posix(), AUDIT_REL.as_posix()}
    return [row for row in _artifact_inventory(root, evidence)
            if row['path'] not in excluded]


def _validate_capture_inputs(repo: Path, cloud_dir: Path, tool_home: Path,
                             schema: Path, capture_mode: Path) -> tuple[dict[str, str], Any]:
    need(capture_mode.resolve() == (repo / CAPTURE_MODE_REL).resolve() and
         capture_mode.is_file() and not capture_mode.is_symlink() and
         digest(capture_mode.read_bytes()) == CAPTURE_MODE_SHA256,
         'frozen W4 capture mode differs')
    capture_helper = _logical_file(repo, cloud_dir, CAPTURE_HELPER_REL.as_posix())
    need(capture_helper.is_file() and not capture_helper.is_symlink() and
         digest(capture_helper.read_bytes()) == CAPTURE_HELPER_SHA256,
         'frozen W4 capture helper differs')
    pins_path = repo / CAPTURE_PINS_REL
    pins = json.loads(_read_regular(pins_path).decode('utf-8'))
    need(digest(pins_path.read_bytes()) == CAPTURE_PINS_SHA256 and isinstance(pins, dict),
         'frozen W4 capture pins differ')
    capture_module = _load(_logical_file(repo, cloud_dir, HELPER_PINS['capture'][0]),
                           'r24_w4_control_runtime_capture', HELPER_PINS['capture'][1])
    old_hashes = _tool_hashes(tool_home)
    schema_expected = 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469'
    need(schema.resolve() == (tool_home / 'src/rust_frontend/vf_mir/vf_mir.capnp').resolve() and
         digest(_read_regular(schema)) == schema_expected,
         'frozen capture schema is not the exact pinned 8a schema')
    return old_hashes, capture_module


def _provider_record(cloud_dir: Path) -> dict[str, Any]:
    path = cloud_dir / 'provider.py'
    expected = '771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616'
    module = _load(path, 'r24_w4_control_provider', expected)
    record = module.require_supported_provider()
    need(record.get('provider') == 'cloud-build' and record.get('project') == 'smallsort-ci' and
         record.get('region') == 'global' and record.get('os') == 'ubuntu-22.04' and
         record.get('arch') == 'x86_64' and record.get('build_id') == os.environ.get('CLOUD_BUILD_ID'),
         'pinned native Cloud provider record differs')
    need(isinstance(record.get('build_id'), str) and
         re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', record['build_id']),
         'Cloud Build ID is not canonical')
    return record


def _args_schema(args: argparse.Namespace) -> Path:
    return Path(args.tool_home).resolve() / 'src/rust_frontend/vf_mir/vf_mir.capnp'


def _validate_native_schema(schema_arg: Path, native_home: Path) -> str:
    exact = native_home / 'src/rust_frontend/vf_mir/vf_mir.capnp'
    expected = 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469'
    need(schema_arg.resolve() == exact.resolve() and schema_arg.is_file() and
         not schema_arg.is_symlink() and digest(schema_arg.read_bytes()) == expected,
         'args.schema must name exact F83 native schema bytes')
    return digest(schema_arg.read_bytes())


def _prerequisite_errors(summary: object, audit_record: object,
                         candidate: str | None = None) -> list[str]:
    errors = []
    if not isinstance(summary, dict):
        return ['C6 linkage diagnostic summary is missing/wrong-type']
    if not isinstance(audit_record, dict):
        return ['C6 linkage diagnostic physical audit is missing/wrong-type']
    if summary.get('schema') != 'select-r24-w4-contract-inputs-v1' or summary.get('complete') is not True:
        errors.append('C6 contract-input diagnostic summary is not complete')
    if summary.get('phase_id') != R24_PHASE or summary.get('route_phase_id') != R21_PHASE or \
       summary.get('owner') != 'select-sort4' or summary.get('lane') != LANE or \
       summary.get('profile') != PROFILE:
        errors.append('C6 contract-input route/profile context differs')
    if not isinstance(summary.get('build_id'), str) or re.fullmatch(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            summary.get('build_id', '')) is None:
        errors.append('C6 contract-input Build ID is malformed')
    if summary.get('build_id') != os.environ.get('CLOUD_BUILD_ID'):
        errors.append('C6 prerequisite is not from this Cloud Build')
    for key, value in (('caller_body_proof_admission', False), ('accepted', False),
                       ('publication_allowed', False), ('typed_call_linkage', 'UNKNOWN'),
                       ('call_linkage', 'UNKNOWN'), ('caller_body_proof_status', 'UNKNOWN'),
                       ('proof_credit', 0)):
        if summary.get(key) != value or (key == 'proof_credit' and type(summary.get(key)) is not int):
            errors.append('C6 linkage diagnostic boundary differs: ' + key)
    if candidate is not None and summary.get('candidate') != candidate:
        errors.append('C6 linkage diagnostic candidate differs')
    cases = summary.get('cases')
    expected_cases = ('positive', 'false-normal', 'false-unwind', 'duplicate-thread',
                      'mut-pointer', 'extra-declaration')
    if not isinstance(cases, list) or [row.get('case') for row in cases if isinstance(row, dict)] != list(expected_cases):
        errors.append('C6 six-case contract-input inventory is incomplete')
    else:
        expected_classes = ('INPUTS_MATCH', 'EXPECTED_INPUT_REFUSAL', 'EXPECTED_INPUT_REFUSAL',
                            'EXPECTED_INPUT_REFUSAL', 'EXPECTED_INPUT_REFUSAL', 'EXPECTED_INPUT_REFUSAL')
        for row, classification in zip(cases, expected_classes):
            facts = row.get('facts') if isinstance(row, dict) else None
            if row.get('errors') != [] or row.get('expected_classification') != classification or \
               not isinstance(facts, dict) or facts.get('complete') is not True or \
               facts.get('classification') != classification:
                errors.append('C6 contract case is incomplete or misclassified: ' + str(row.get('case')))
    if audit_record.get('schema') != 'select-r24-w4-contract-inputs-v1-audit' or \
       audit_record.get('complete') is not True or audit_record.get('evidence_complete') is not True:
        errors.append('C6 contract-input physical audit is not complete')
    if audit_record.get('accepted') is not False or audit_record.get('publication_allowed') is not False or \
       type(audit_record.get('proof_credit')) is not int or audit_record.get('proof_credit') != 0:
        errors.append('C6 physical audit boundary differs')
    if candidate is not None and (audit_record.get('candidate') != candidate or
                                  audit_record.get('build_id') != summary.get('build_id') or
                                  audit_record.get('build_id') != os.environ.get('CLOUD_BUILD_ID')):
        errors.append('C6 audit candidate/Build identity differs from summary')
    return errors


def run(args: argparse.Namespace, *, prerequisite_summary=None,
        prerequisite_audit=None, stage_runner=None,
        constructor_modules: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the exact pilot source-capture batch with injectable fake services."""
    evidence = _assert_path_chain(Path(getattr(args, 'evidence')), allow_missing=False)
    out_path = evidence / SUMMARY_REL
    report: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_SOURCE_ONLY_CONTROL_CAPTURE',
        'complete': False, 'batch_complete': False, 'universe_complete': False,
        'universe_count': len(BODY_NAMES), 'batch_indices': list(BATCH_INDICES),
        'selected_variants': [BODY_NAMES[index] for index in BATCH_INDICES],
        'r24_session_phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
        'owner': 'select-sort4', 'lane': LANE, 'profile': PROFILE,
        'candidate': getattr(args, 'candidate', None), 'build_id': os.environ.get('CLOUD_BUILD_ID'),
        'body_proof_run': False, 'caller_body_proof_admission': False,
        'typed_call_linkage': 'UNKNOWN', 'accepted': False,
        'publication_allowed': False, 'proof_credit': 0,
        'runner_exit': None, 'failed_stage': 'preflight', 'errors': [],
        'stages': {}, 'tool_build': {}, 'rows': [],
        'artifact_inventory': [],
    }
    report['body_proof_run'] = False
    prereq_errors = _prerequisite_errors(prerequisite_summary, prerequisite_audit,
                                         args.candidate)
    report['prerequisite_summary_sha256'] = digest(json.dumps(
        prerequisite_summary, sort_keys=True, separators=(',', ':')).encode()) \
        if isinstance(prerequisite_summary, dict) else None
    report['prerequisite_audit_sha256'] = digest(json.dumps(
        prerequisite_audit, sort_keys=True, separators=(',', ':')).encode()) \
        if isinstance(prerequisite_audit, dict) else None
    if prereq_errors:
        report['errors'].extend(prereq_errors)
        report['failed_stage'] = 'C6-prerequisites'
    need(not out_path.parent.exists() and not out_path.parent.is_symlink(),
         'control capture output root already exists')
    _mkdir_chain(evidence, out_path.parent)
    _write_json(evidence, out_path, report)
    active_stages: dict[str, Any] = report['stages']

    def recording_stage(*stage_args, **stage_kwargs):
        nonlocal active_stages
        stage_name = stage_args[0] if stage_args else stage_kwargs.get('name')
        try:
            if stage_runner is None:
                capture_runner = capture_module.run_stage
                result = capture_runner(*stage_args, **stage_kwargs)
            else:
                result = stage_runner(*stage_args, **stage_kwargs)
            active_stages[stage_name] = result
            _write_json(evidence, out_path, report)
            return result
        except BaseException as exc:
            active_stages[stage_name] = {'status': 'EXCEPTION',
                                         'exception_type': type(exc).__name__,
                                         'exception': str(exc)}
            try:
                _write_json(evidence, out_path, report)
            except BaseException as save_exc:
                if hasattr(exc, 'add_note'):
                    exc.add_note('stage exception snapshot failed: ' + repr(save_exc))
            raise

    try:
        repo, cloud_dir, evidence, tool_home, native_home = _validate_context(args)
        report['failed_stage'] = 'route-and-mode'
        need(not prereq_errors, '; '.join(prereq_errors))
        report['route'] = _route(dict(os.environ))
        mode = _check_mode(repo, Path(args.mode_file).resolve())
        report['mode_sha256'] = MODE_SHA256
        report['mode_identity'] = {'path': MODE_REL.as_posix(), 'sha256': MODE_SHA256}
        need(subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                     text=True).strip() == args.candidate,
             'proof checkout does not match candidate')
        report['provider_record'] = _provider_record(cloud_dir)
        need(type(args.deadline_epoch) is int and args.deadline_epoch > int(time.time()) + 30,
             'shared deadline lacks minimum reserve')
        report['failed_stage'] = 'capture-tool-preflight'
        report['native_schema_sha256'] = _validate_native_schema(Path(args.schema).resolve(), native_home)
        report['capture_schema_path'] = str(_args_schema(args).resolve())
        report['compiler_sysroot'] = str(Path(args.compiler_sysroot).resolve())
        frozen_hashes, capture_module = _validate_capture_inputs(
            repo, cloud_dir, tool_home, _args_schema(args), Path(args.capture_mode_file).resolve())
        native_input_receipt = _native_input_identity_record(repo)
        input_native_hashes = _validate_native_input_identity(repo, native_home)
        need(_normalize_c6_tool_inventory(prerequisite_summary) == input_native_hashes,
             'same-Build C6 diagnostic tool inventory differs from physical F83 input home')
        report['capture_tool_hashes_before'] = frozen_hashes
        report['native_input_tool_hashes_before'] = input_native_hashes
        report['native_input_identity_record'] = {
            'path': NATIVE_INPUT_IDENTITY_REL.as_posix(),
            'sha256': NATIVE_INPUT_IDENTITY_SHA256,
            'build_id': native_input_receipt.get('build_id'),
            'assurance': native_input_receipt.get('assurance'),
        }
        if constructor_modules is None:
            profile, modules = _load_constructor_inputs(repo, cloud_dir)
        else:
            profile = {'actual_indexed_calls': 5, 'body_action': 'full-body-c1-recovery',
                       'cloud_build_enabled': False}
            modules = constructor_modules
        report['constructor_profile'] = {
            'path': CONSTRUCTOR_PROFILE_REL.as_posix(),
            'sha256': CONSTRUCTOR_PROFILE_SHA256,
            'actual_indexed_calls': profile.get('actual_indexed_calls'),
            'body_action': profile.get('body_action'),
        }
        report['failed_stage'] = 'source-construction'
        source_rows = _construct_sources(repo, cloud_dir, modules)
        need(tuple(row['name'] for row in source_rows) == BODY_NAMES,
             'full source universe differs from the closed mode order')
        report['constructor_inventory'] = [
            {'name': row['name'], 'kind': row['kind'],
             'verified_bytes': len(row['verified']), 'verified_sha256': digest(row['verified']),
             'original_bytes': len(row['original']), 'original_sha256': digest(row['original']),
             'source_metadata': _metadata_facts(row['metadata'])}
            for row in source_rows]
        report['failed_stage'] = 'native-tool-build'
        tool_build_root = out_path.parent / 'tool-build'
        _mkdir_chain(evidence, tool_build_root)
        active_stages = report['tool_build'].setdefault('stages', {})
        build_record = _prepare_native_tool(args, work_root=tool_build_root,
            cloud_dir=cloud_dir, native_home=native_home, stage_runner=recording_stage)
        report['tool_build'].update(build_record)
        report['tool_build']['complete'] = not build_record['errors']
        report['tool_build']['binary_sha256'] = (build_record.get('source_after_build') or {}).get('bin/verifast')
        if build_record.get('errors'):
            report['errors'].extend(build_record['errors'])
            report['runner_exit'] = 4
            report['failed_stage'] = 'native-tool-build'
            report['artifact_inventory'] = _summary_root_inventory(out_path.parent, evidence)
            _write_json(evidence, out_path, report)
            return report
        report['failed_stage'] = 'source-and-native-capture'
        target_tool = Path(build_record['target'])
        rows_by_name = {row['name']: row for row in source_rows}
        report['rows'] = []
        for index in BATCH_INDICES:
            source_row = rows_by_name[BODY_NAMES[index]]
            case_root = out_path.parent / 'variants' / source_row['name']
            _mkdir_chain(evidence, case_root)
            current: dict[str, Any] = {
                'index': index, 'variant': source_row['name'], 'kind': source_row['kind'],
                'status': 'INCOMPLETE', 'complete': False,
                'source_metadata': _metadata_facts(source_row['metadata']),
                'body_proof_run': False, 'caller_body_proof_admission': False,
                'typed_call_linkage': 'UNKNOWN', 'accepted': False,
                'publication_allowed': False, 'proof_credit': 0,
                'stages': {}, 'errors': [],
            }
            report['rows'].append(current)
            active_stages = current['stages']
            _write_json(evidence, out_path, report)
            capture_hashes_before = _tool_hashes(tool_home)
            current['capture_tool_hashes_before'] = capture_hashes_before
            case_capture = _run_capture_case(args, row=source_row,
                case_root=case_root, tool_home=tool_home, schema=_args_schema(args),
                stage_runner=recording_stage, capture_module=capture_module)
            current.update(case_capture)
            current['errors'].extend(case_capture['stage_errors'])
            capture_hashes_after = _tool_hashes(tool_home)
            current['capture_tool_hashes_after'] = capture_hashes_after
            if capture_hashes_before != frozen_hashes or capture_hashes_after != frozen_hashes:
                current['errors'].append('frozen 8a capture tool identity changed during case')
            report['failed_stage'] = 'native-fingerprint:' + source_row['name']
            if build_record.get('errors'):
                current['native'] = {'complete': False, 'stage': {'status': 'NOT_RUN',
                    'skipped': 'native tool build did not complete'},
                    'errors': ['native tool build did not complete']}
                current['errors'].append('native tool build did not complete')
            else:
                before_native = _tool_sources(target_tool,
                    expected_sources=_patched_source_pins(),
                    expected_binary=build_record.get('binary_sha256'))
                if before_native != build_record.get('source_after_build'):
                    current['errors'].append('native tool identity drift before fingerprint stage')
                native = _native_fingerprint(args, row=source_row,
                    case_root=case_root, native_home=target_tool, stage_runner=recording_stage)
                current['native'] = native
                current['errors'].extend(native['errors'])
                after_native = _tool_sources(target_tool,
                    expected_sources=_patched_source_pins(),
                    expected_binary=build_record.get('binary_sha256'))
                if after_native != before_native:
                    current['errors'].append('native tool identity changed during fingerprint stage')
                current['native_tool_hashes_before'] = before_native
                current['native_tool_hashes_after'] = after_native
            current['artifact_inventory'] = _artifact_inventory(case_root, evidence)
            current['complete'] = not current['errors'] and native.get('complete') is True
            current['status'] = 'SOURCE_ONLY_CAPTURE_COMPLETE' if current['complete'] else 'INCOMPLETE'
            _write_json(evidence, out_path, report)
        report['capture_tool_hashes_after'] = _tool_hashes(tool_home)
        if report['capture_tool_hashes_after'] != frozen_hashes:
            report['errors'].append('frozen capture tool changed during source capture')
        source_after = _read_regular(repo / SOURCE_REL)
        report['source_after'] = {'path': SOURCE_REL.as_posix(),
                                  'bytes': len(source_after), 'sha256': digest(source_after)}
        if digest(source_after) != SOURCE_SHA256:
            report['errors'].append('repository Rust source changed during control capture')
        report['native_input_tool_hashes_after'] = _validate_native_input_identity(repo, native_home)
        if report['native_input_tool_hashes_after'] != input_native_hashes:
            report['errors'].append('original C6 native input tool changed during capture')
        report['batch_complete'] = len(report['rows']) == len(BATCH_INDICES) and all(
            row.get('complete') is True for row in report['rows']) and not report['errors']
        report['complete'] = report['batch_complete']
        report['universe_complete'] = report['complete'] and len(BATCH_INDICES) == len(BODY_NAMES)
        report['classification'] = ('COMPLETE_SOURCE_ONLY_CONTROL_CAPTURE'
            if report['complete'] else 'INCOMPLETE_SOURCE_ONLY_CONTROL_CAPTURE')
        report['failed_stage'] = 'complete' if report['complete'] else report['failed_stage']
        report['runner_exit'] = 0 if report['complete'] else 4
        report['artifact_inventory'] = _summary_root_inventory(out_path.parent, evidence)
        _write_json(evidence, out_path, report)
        return report
    except BaseException as exc:
        report['runner_exit'] = 4
        report['failed_stage'] = report.get('failed_stage') or 'exception'
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        try:
            report['artifact_inventory'] = _summary_root_inventory(out_path.parent, evidence)
            _write_json(evidence, out_path, report)
        except BaseException as snapshot_error:
            if hasattr(exc, 'add_note'):
                exc.add_note('partial control-capture snapshot failed: ' + repr(snapshot_error))
        raise


def _recompute_mir_observation(evidence: Path, case_root: Path, mode: str,
                               capture_module) -> dict[str, Any]:
    """Run the pinned graph parser with compare-only output paths."""
    decoded_path = case_root / 'fixture' / (mode + '-mir.txt')
    decoded_raw = _read_regular(decoded_path, evidence)
    decoded = decoded_raw.decode('utf-8', 'strict')
    function_name, record = capture_module.complete_function_record(decoded, 'sort4_stable')
    need(function_name == 'sort4_stable' and type(record) is str,
         'physical MIR record has wrong target/type')
    record_path = case_root / (mode + '-sort4-full-mir.txt')
    need(_read_regular(record_path, evidence) == record.encode('utf-8'),
         'physical full-function record differs from decoded MIR')
    expected_outputs = {mode + '-sort4-full-mir.txt', mode + '-graph-inventory.json'}
    seen: set[str] = set()

    class CompareFile:
        def __init__(self, name):
            self.name = name

        def write_text(self, text):
            need(type(text) is str and self.name not in seen,
                 'graph parser attempted duplicate or invalid output')
            need(_read_regular(case_root / self.name, evidence) == text.encode('utf-8'),
                 'physical graph output differs from recomputed contents: ' + self.name)
            seen.add(self.name)
            return len(text)

    class CompareDirectory:
        def __truediv__(self, name):
            need(type(name) is str and name in expected_outputs,
                 'graph parser attempted an unexpected output path')
            return CompareFile(name)

    graph = capture_module.graph_inventory(decoded_path, CompareDirectory(), mode)
    need(seen == expected_outputs and type(graph) is dict,
         'graph parser did not reproduce both exact physical outputs')
    return {
        'decoded_sha256': digest(decoded_raw),
        'full_function_record': record_path.relative_to(evidence).as_posix(),
        'full_function_record_sha256': digest(record.encode('utf-8')),
        'graph_inventory': graph,
        'function_name': function_name,
    }


def _audit_case(evidence: Path, row: dict[str, Any], report: dict[str, Any],
                capture_tool: Path, native_tool: Path, capture_module) -> list[str]:
    errors = []
    variant = row.get('variant')
    if row.get('complete') is not True or row.get('status') != 'SOURCE_ONLY_CAPTURE_COMPLETE' or row.get('errors') != []:
        errors.append(str(variant) + ' row is not a clean source-only capture')
    case_root = evidence / SUMMARY_REL.parent / 'variants' / str(variant)
    try:
        actual_inventory = _artifact_inventory(case_root, evidence)
        if not _json_exact(actual_inventory, row.get('artifact_inventory')):
            errors.append(str(variant) + ' physical artifact inventory differs')
    except BaseException as exc:
        errors.append(str(variant) + ' artifact inventory invalid: ' + str(exc))
        return errors
    fixture = case_root / 'fixture'
    mir = row.get('mir')
    if type(mir) is not dict or set(mir) != {'normal', 'readonly'}:
        errors.append(str(variant) + ' MIR mode inventory differs')
    else:
        for mode in ('normal', 'readonly'):
            try:
                recomputed = _recompute_mir_observation(evidence, case_root, mode, capture_module)
                if not _json_exact(mir[mode], recomputed):
                    errors.append(str(variant) + ' ' + mode + ' MIR facts differ from physical inputs')
            except BaseException as exc:
                errors.append(str(variant) + ' ' + mode + ' MIR recheck failed: ' +
                              type(exc).__name__ + ': ' + str(exc))
    fixture_records = row.get('fixture')
    if type(fixture_records) is not dict or set(fixture_records) != {'verified', 'original'}:
        errors.append(str(variant) + ' fixture record malformed')
    else:
        for label in ('verified', 'original'):
            record = fixture_records.get(label)
            if not isinstance(record, dict):
                errors.append(str(variant) + ' ' + label + ' fixture record missing')
                continue
            path = fixture / label / 'lib.rs'
            try:
                raw = _read_regular(path, evidence)
                expected_record = {'path': path.relative_to(evidence).as_posix(),
                                   'bytes': len(raw), 'sha256': digest(raw)}
                if not _json_exact(record, expected_record):
                    errors.append(str(variant) + ' ' + label + ' source changed')
            except BaseException as exc:
                errors.append(str(variant) + ' ' + label + ' source invalid: ' + str(exc))
    stages = row.get('stages')
    if not isinstance(stages, dict):
        errors.append(str(variant) + ' stage map malformed')
        return errors
    try:
        current_capture = _tool_hashes(capture_tool)
        if row.get('capture_tool_hashes_before') != current_capture or \
           row.get('capture_tool_hashes_after') != current_capture:
            errors.append(str(variant) + ' frozen capture tool identity changed')
    except BaseException as exc:
        errors.append(str(variant) + ' frozen capture tool identity invalid: ' + str(exc))
    fixture_hashes = row.get('fixture_hashes')
    if not isinstance(fixture_hashes, dict):
        errors.append(str(variant) + ' fixture source hash map malformed')
        fixture_hashes = {}
    compiler = report.get('compiler_sysroot')
    schema_path = report.get('capture_schema_path')
    exporter = str(capture_tool / 'bin/vf-rust-mir-exporter')
    expected_argv = {
        'normal-export': [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021'],
        'normal-decode': ['capnp', 'decode', schema_path, 'VfMir'],
        'readonly-export': [exporter, 'verified/lib.rs', f'--sysroot={compiler}', '--edition', '2021',
                            '--vf-rust-mir-exporter:preprocess-readonly'],
        'readonly-decode': ['capnp', 'decode', schema_path, 'VfMir'],
        'refinement': [str(capture_tool / 'bin/refinement-checker'), '--rustc-args', '--edition 2021',
                       'original/lib.rs', 'verified/lib.rs'],
    }
    if set(stages) != set(expected_argv) or row.get('stage_errors') != []:
        errors.append(str(variant) + ' capture stage inventory/errors differ')
    for name, stage in stages.items():
        if not isinstance(stage, dict):
            errors.append(str(variant) + ' stage ' + name + ' wrong type')
            continue
        stage_path = fixture / (name + '-stage.json')
        try:
            raw = _read_regular(stage_path, evidence)
            physical = json.loads(raw.decode('utf-8'))
            if not _json_exact(physical, stage):
                errors.append(str(variant) + ' stage ' + name + ' physical record differs')
        except BaseException as exc:
            errors.append(str(variant) + ' stage ' + name + ' record missing/invalid: ' + str(exc))
        for key in ('stdout', 'stderr'):
            rel = stage.get(key)
            if isinstance(rel, str):
                try:
                    _read_regular(fixture / rel, evidence)
                except BaseException as exc:
                    errors.append(str(variant) + ' stage ' + name + ' ' + key + ' missing: ' + str(exc))
        if name in expected_argv:
            errors.extend(_stage_errors(stage, str(variant) + ' ' + name,
                expected_argv=expected_argv[name], expected_fixture=fixture_hashes))
    native = row.get('native')
    if not isinstance(native, dict) or native.get('complete') is not True or native.get('errors') != []:
        errors.append(str(variant) + ' native fingerprint record incomplete')
    else:
        facts = native.get('native_data')
        if not isinstance(facts, dict):
            errors.append(str(variant) + ' native-data facts missing')
        else:
            fpdir = case_root / 'native/fingerprints'
            try:
                physical = json.loads(_read_regular(fpdir / 'native-data.json', evidence).decode('utf-8'))
                if not _json_exact(physical, facts):
                    errors.append(str(variant) + ' physical native-data.json differs')
            except BaseException as exc:
                errors.append(str(variant) + ' native-data.json invalid: ' + str(exc))
        native_stage = native.get('stage')
        native_source = native.get('source_sha256')
        snapshot_records = native.get('snapshots')
        if not isinstance(native_stage, dict) or not isinstance(native_source, str) or not isinstance(snapshot_records, dict):
            errors.append(str(variant) + ' native physical verification inputs malformed')
        else:
            source_fixture = {'verified/lib.rs': native_source}
            errors.extend(_stage_errors(native_stage, 'native fingerprint', expected_exit=2,
                expected_argv=[str(native_tool / 'bin/verifast'), *NATIVE_ARGV[1:]],
                expected_fixture=source_fixture))
            try:
                physical_stage = json.loads(_read_regular(
                    fixture / 'native-fingerprint-stage.json', evidence).decode('utf-8'))
                if not _json_exact(native_stage, physical_stage):
                    errors.append(str(variant) + ' native stage differs from physical record')
            except BaseException as exc:
                errors.append(str(variant) + ' native stage record invalid: ' + str(exc))
            physical_snapshots = {}
            for key, filename in (('unit', 'caller-native-unit.marshal'),
                                  ('body', 'caller-native-body-0.marshal')):
                try:
                    path = case_root / 'native/fingerprints' / filename
                    raw = _read_regular(path, evidence)
                    physical_snapshots[key] = {'path': path.relative_to(evidence).as_posix(),
                        'bytes': len(raw), 'sha256': digest(raw)}
                    if not _json_exact(snapshot_records.get(key), physical_snapshots[key]):
                        errors.append(str(variant) + ' native physical ' + key + ' record differs')
                except BaseException as exc:
                    errors.append(str(variant) + ' native physical ' + key + ' invalid: ' + str(exc))
            try:
                fpdir = case_root / 'native/fingerprints'
                source_path = fixture / 'verified/lib.rs'
                source_raw = _read_regular(source_path, evidence)
                if digest(source_raw) != native_source:
                    errors.append(str(variant) + ' native source identity changed')
                physical_facts = json.loads(_read_regular(fpdir / 'native-data.json', evidence).decode('utf-8'))
                if not _json_exact(facts, physical_facts):
                    errors.append(str(variant) + ' native facts differ from physical JSON')
                build_id = report.get('build_id')
                expected_fields = {
                    'schema': 'select-r24-w4-native-data-fingerprint-v1',
                    'classification': 'SOURCE_ONLY_NATIVE_DATA_CAPTURE',
                    'complete': True, 'body_name': 'sort4_stable', 'body_index': 0,
                    'body_inventory': ['sort4_stable'], 'build_id': build_id,
                    'expected_refusal': 'snapshot complete; no proof rule admitted',
                    'body_proof_run': False, 'accepted': False,
                    'publication_allowed': False, 'caller_body_proof_admission': False,
                    'typed_call_linkage': 'UNKNOWN', 'proof_credit': 0,
                    'source': {'path': str(source_path.resolve()), 'bytes': len(source_raw),
                               'sha256': digest(source_raw)},
                    'unit': {'path': 'caller-native-unit.marshal',
                             'bytes': physical_snapshots.get('unit', {}).get('bytes'),
                             'sha256': physical_snapshots.get('unit', {}).get('sha256')},
                    'body': {'path': 'caller-native-body-0.marshal',
                             'bytes': physical_snapshots.get('body', {}).get('bytes'),
                             'sha256': physical_snapshots.get('body', {}).get('sha256')},
                }
                if not _json_exact(physical_facts, expected_fields):
                    errors.append(str(variant) + ' native physical facts have wrong fields/types')
                for key, value in expected_fields.items():
                    if type(physical_facts.get(key)) is not type(value) or physical_facts.get(key) != value:
                        errors.append(str(variant) + ' native physical fact differs: ' + key)
                for key in ('source', 'unit', 'body'):
                    if type(physical_facts.get(key)) is not dict or \
                       type(physical_facts[key].get('bytes')) is not int:
                        errors.append(str(variant) + ' native physical byte count has wrong type: ' + key)
                stdout_name, stderr_name = native_stage.get('stdout'), native_stage.get('stderr')
                if native.get('log_paths') != [stdout_name, stderr_name]:
                    errors.append(str(variant) + ' native log path inventory differs')
                stdout_text = _read_regular(fixture / stdout_name, evidence).decode('utf-8', 'strict')
                stderr_text = _read_regular(fixture / stderr_name, evidence).decode('utf-8', 'strict')
                errors.extend(_parse_native_marker(stdout_text, stderr_text, native_source,
                                                   physical_snapshots['unit'], physical_snapshots['body']))
            except BaseException as exc:
                errors.append(str(variant) + ' native physical audit invalid: ' + str(exc))
        tool_before = row.get('native_tool_hashes_before')
        tool_after = row.get('native_tool_hashes_after')
        try:
            build_record = report.get('tool_build')
            expected_binary = build_record.get('binary_sha256') if isinstance(build_record, dict) else None
            live = _tool_sources(native_tool, expected_sources=_patched_source_pins(),
                                 expected_binary=expected_binary)
            if live != tool_before or live != tool_after:
                errors.append(str(variant) + ' native tool identity drifted after stage')
        except BaseException as exc:
            errors.append(str(variant) + ' native tool identity invalid: ' + str(exc))
    row_boundary = {'body_proof_run': False, 'caller_body_proof_admission': False,
                    'typed_call_linkage': 'UNKNOWN', 'accepted': False,
                    'publication_allowed': False, 'proof_credit': 0}
    for key, expected in row_boundary.items():
        if type(row.get(key)) is not type(expected) or row.get(key) != expected:
            errors.append(str(variant) + ' source-only boundary differs: ' + key)
    return errors


def audit(args: argparse.Namespace, *, prerequisite_summary=None,
          prerequisite_audit=None, stage_runner=None) -> dict[str, Any]:
    """Read-only physical audit for the source-only capture report."""
    evidence = _assert_path_chain(Path(getattr(args, 'evidence')), allow_missing=False)
    report_path = evidence / SUMMARY_REL
    audit_path = evidence / AUDIT_REL
    audit_report: dict[str, Any] = {
        'schema': 'select-r24-w4-control-capture-audit-v1',
        'complete': False, 'evidence_complete': False,
        'batch_complete': False, 'universe_complete': False,
        'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
        'body_proof_run': False, 'caller_body_proof_admission': False,
        'typed_call_linkage': 'UNKNOWN', 'runner_exit': getattr(args, 'runner_exit', None),
        'failed_stage': getattr(args, 'failed_stage', None), 'errors': [],
    }
    try:
        repo, cloud_dir, evidence, tool_home, native_home = _validate_context(args)
        output_arg = getattr(args, 'output', None)
        if output_arg is not None:
            output_path = _assert_path_chain(Path(output_arg), allow_missing=True)
            if output_path != audit_path or output_path.is_symlink():
                raise ValueError('audit output must be the exact evidence-relative audit path')
        _mkdir_chain(evidence, audit_path.parent)
        expected_route = _route(dict(os.environ))
        prereq_errors = _prerequisite_errors(prerequisite_summary, prerequisite_audit,
                                             args.candidate)
        audit_report['errors'].extend(prereq_errors)
        summary_prereq_sha = digest(json.dumps(prerequisite_summary, sort_keys=True,
            separators=(',', ':')).encode()) if isinstance(prerequisite_summary, dict) else None
        audit_prereq_sha = digest(json.dumps(prerequisite_audit, sort_keys=True,
            separators=(',', ':')).encode()) if isinstance(prerequisite_audit, dict) else None
        mode = _check_mode(repo, Path(args.mode_file).resolve())
        raw = _read_regular(report_path, evidence)
        report = json.loads(raw.decode('utf-8'))
        need(isinstance(report, dict), 'control capture summary is not an object')
        expected_context = {
            'classification': 'COMPLETE_SOURCE_ONLY_CONTROL_CAPTURE',
            'r24_session_phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
            'owner': 'select-sort4', 'lane': LANE, 'profile': PROFILE,
            'build_id': os.environ.get('CLOUD_BUILD_ID'),
            'mode_identity': {'path': MODE_REL.as_posix(), 'sha256': MODE_SHA256},
            'route': expected_route, 'provider_record': _provider_record(cloud_dir),
            'stages': {}, 'errors': [],
        }
        for key, value in expected_context.items():
            if not _json_exact(report.get(key), value):
                audit_report['errors'].append('summary context differs: ' + key)
        need(report.get('schema') == SCHEMA and report.get('candidate') == args.candidate and
             report.get('mode_sha256') == MODE_SHA256,
             'control capture summary identity differs')
        if report.get('prerequisite_summary_sha256') != summary_prereq_sha or \
           report.get('prerequisite_audit_sha256') != audit_prereq_sha:
            audit_report['errors'].append('C6 prerequisite records changed since capture')
        need(type(report.get('batch_indices')) is list and
             all(type(index) is int for index in report['batch_indices']) and
             report['batch_indices'] == list(BATCH_INDICES) and
             report.get('selected_variants') == [BODY_NAMES[i] for i in BATCH_INDICES] and
             type(report.get('universe_count')) is int and
             report['universe_count'] == len(BODY_NAMES),
             'summary batch/universe differs from closed pilot mode')
        summary_boundary = {'complete': True, 'batch_complete': True,
                            'universe_complete': False, 'body_proof_run': False,
                            'caller_body_proof_admission': False,
                            'typed_call_linkage': 'UNKNOWN', 'accepted': False,
                            'publication_allowed': False, 'proof_credit': 0}
        for key, expected in summary_boundary.items():
            if type(report.get(key)) is not type(expected) or report.get(key) != expected:
                audit_report['errors'].append('summary boundary differs: ' + key)
        current_git = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        if current_git != args.candidate:
            audit_report['errors'].append('candidate checkout changed')
        capture_mode = Path(args.capture_mode_file).resolve()
        native_schema_sha = _validate_native_schema(Path(args.schema).resolve(), native_home)
        if report.get('native_schema_sha256') != native_schema_sha:
            audit_report['errors'].append('native F83 schema changed since capture')
        frozen_hashes, capture_module = _validate_capture_inputs(repo, cloud_dir, tool_home,
                                                    _args_schema(args), capture_mode)
        if report.get('capture_tool_hashes_before') != frozen_hashes or report.get('capture_tool_hashes_after') != frozen_hashes:
            audit_report['errors'].append('frozen capture tool hashes differ')
        native_input_hashes = _validate_native_input_identity(repo, native_home)
        native_input_receipt = _native_input_identity_record(repo)
        if isinstance(prerequisite_summary, dict) and \
           _normalize_c6_tool_inventory(prerequisite_summary) != native_input_hashes:
            audit_report['errors'].append('same-Build C6 diagnostic tool inventory differs from physical F83 home')
        if report.get('native_input_identity_record') != {
            'path': NATIVE_INPUT_IDENTITY_REL.as_posix(),
            'sha256': NATIVE_INPUT_IDENTITY_SHA256,
            'build_id': native_input_receipt.get('build_id'),
            'assurance': native_input_receipt.get('assurance'),
        }:
            audit_report['errors'].append('F83 input identity report differs')
        if report.get('native_input_tool_hashes_before') != native_input_hashes or \
           report.get('native_input_tool_hashes_after') != native_input_hashes:
            audit_report['errors'].append('original C6 F83 input tool identity differs')
        rows = report.get('rows')
        tool_build = report.get('tool_build')
        source_raw = _read_regular(repo / SOURCE_REL)
        expected_source_after = {'path': SOURCE_REL.as_posix(), 'bytes': len(source_raw),
                                 'sha256': digest(source_raw)}
        if digest(source_raw) != SOURCE_SHA256 or not _json_exact(
                report.get('source_after'), expected_source_after):
            audit_report['errors'].append('repository source changed since capture')
        profile, modules = _load_constructor_inputs(repo, cloud_dir)
        reconstructed = _construct_sources(repo, cloud_dir, modules)
        if not _json_exact(report.get('constructor_profile'), {
            'path': CONSTRUCTOR_PROFILE_REL.as_posix(),
            'sha256': CONSTRUCTOR_PROFILE_SHA256,
            'actual_indexed_calls': profile.get('actual_indexed_calls'),
            'body_action': profile.get('body_action'),
        }):
            audit_report['errors'].append('constructor profile facts changed')
        expected_sources = {row['name']: row for row in reconstructed}
        constructor_inventory = report.get('constructor_inventory')
        expected_inventory = [{'name': row['name'], 'kind': row['kind'],
            'verified_bytes': len(row['verified']), 'verified_sha256': digest(row['verified']),
            'original_bytes': len(row['original']), 'original_sha256': digest(row['original']),
            'source_metadata': _metadata_facts(row['metadata'])}
            for row in reconstructed]
        if not isinstance(constructor_inventory, list) or len(constructor_inventory) != len(expected_inventory):
            audit_report['errors'].append('full 37-case constructor inventory is incomplete')
        else:
            for observed, expected_row in zip(constructor_inventory, expected_inventory):
                if type(observed) is not dict or not _json_exact(observed, expected_row):
                    audit_report['errors'].append('constructor source inventory differs: ' + expected_row['name'])
        if not isinstance(rows, list):
            rows = []
        for row in rows:
            if not isinstance(row, dict) or row.get('variant') not in expected_sources:
                continue
            expected = expected_sources[row['variant']]
            if row.get('kind') != expected['kind']:
                audit_report['errors'].append(row['variant'] + ' source kind differs from pinned constructor')
            if not _json_exact(row.get('source_metadata'), _metadata_facts(expected['metadata'])):
                audit_report['errors'].append(row['variant'] + ' source metadata differs from pinned constructors')
            fixture_facts = row.get('fixture')
            if not isinstance(fixture_facts, dict) or \
               fixture_facts.get('verified', {}).get('sha256') != digest(expected['verified']) or \
               fixture_facts.get('original', {}).get('sha256') != digest(expected['original']):
                audit_report['errors'].append(row['variant'] + ' source fixture does not match pinned constructors')
        expected_build_stages = tool_build.get('stages') if isinstance(tool_build, dict) else None
        target_tool = Path('/workspace/smallsort-work') / NATIVE_TOOL_HOME_NAME
        patch_path = repo / NATIVE_PATCH_REL
        build_argv = {
            'native-tool-copy': ['/bin/cp', '-a', str(native_home), str(target_tool)],
            'native-patch-check': ['git', '-C', str(target_tool), 'apply', '--check', str(patch_path)],
            'native-patch-apply': ['git', '-C', str(target_tool), 'apply', str(patch_path)],
            'native-tool-build': ['make', '-C', str(target_tool / 'src'),
                                 '../bin/verifast', 'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'],
        }
        if type(expected_build_stages) is not dict or set(expected_build_stages) != set(build_argv):
            audit_report['errors'].append('native tool build stage map malformed')
        else:
            stage_root = evidence / SUMMARY_REL.parent / 'tool-build'
            for name, stage in expected_build_stages.items():
                try:
                    physical = json.loads(_read_regular(stage_root / (name + '-stage.json'), evidence).decode('utf-8'))
                    if not _json_exact(physical, stage):
                        audit_report['errors'].append('native tool build stage differs: ' + name)
                    audit_report['errors'].extend(_stage_errors(
                        physical, name, expected_argv=build_argv[name], expected_fixture={}))
                    for key in ('stdout', 'stderr'):
                        logname = stage.get(key) if isinstance(stage, dict) else None
                        if isinstance(logname, str):
                            _read_regular(stage_root / logname, evidence)
                except BaseException as exc:
                    audit_report['errors'].append('native tool build stage invalid ' + name + ': ' + str(exc))
        if not isinstance(tool_build, dict) or tool_build.get('complete') is not True or \
           tool_build.get('errors') != []:
            audit_report['errors'].append('native fingerprint tool build incomplete')
        else:
            for field, stage_name in (
                    ('copy_stage', 'native-tool-copy'), ('patch_check_stage', 'native-patch-check'),
                    ('patch_apply_stage', 'native-patch-apply'), ('build_stage', 'native-tool-build')):
                if type(expected_build_stages) is not dict or not _json_exact(
                        tool_build.get(field), expected_build_stages.get(stage_name)):
                    audit_report['errors'].append('native tool build duplicated stage differs: ' + field)
            if tool_build.get('target') != str(target_tool) or not _json_exact(
                    tool_build.get('source_before'), native_input_hashes) or not _json_exact(
                    tool_build.get('source_copied'), native_input_hashes):
                audit_report['errors'].append('native tool build input/copy context differs')
            try:
                live_native = _tool_sources(target_tool,
                    expected_sources=_patched_source_pins(),
                    expected_binary=(tool_build or {}).get('binary_sha256') if isinstance(tool_build, dict) else None)
                expected_live = tool_build.get('source_after_build')
                if live_native != expected_live or tool_build.get('binary_sha256') != live_native.get('bin/verifast'):
                    audit_report['errors'].append('native fingerprint tool build identity changed')
            except BaseException as exc:
                audit_report['errors'].append('native fingerprint tool unavailable: ' + str(exc))
        if not isinstance(rows, list) or len(rows) != len(BATCH_INDICES):
            audit_report['errors'].append('pilot row inventory incomplete')
            rows = rows if isinstance(rows, list) else []
        for expected_index, row in zip(BATCH_INDICES, rows):
            if not isinstance(row, dict) or type(row.get('index')) is not int or \
               row['index'] != expected_index or row.get('variant') != BODY_NAMES[expected_index]:
                audit_report['errors'].append('pilot row order/type differs at index ' + str(expected_index))
                continue
            audit_report['errors'].extend(_audit_case(
                evidence, row, report, tool_home, target_tool, capture_module))
        physical_all = _summary_root_inventory(evidence / SUMMARY_REL.parent, evidence)
        if not _json_exact(report.get('artifact_inventory'), physical_all):
            audit_report['errors'].append('summary-root physical inventory differs')
        if type(getattr(args, 'runner_exit', None)) is not int or args.runner_exit != 0 or \
           getattr(args, 'failed_stage', None) != 'complete':
            audit_report['errors'].append('outer runner exit/stage does not report complete control capture')
        if type(report.get('runner_exit')) is not int or report['runner_exit'] != 0 or \
           report.get('failed_stage') != 'complete':
            audit_report['errors'].append('captured runner exit/stage does not report complete batch')
        audit_report['summary_sha256'] = digest(raw)
        audit_report['mode_sha256'] = MODE_SHA256
        audit_report['candidate'] = args.candidate
        audit_report['batch_indices'] = list(BATCH_INDICES)
        audit_report['universe_count'] = len(BODY_NAMES)
        audit_report['tool_build_binary_sha256'] = (tool_build or {}).get('binary_sha256') if isinstance(tool_build, dict) else None
        audit_report['complete'] = bool(report.get('complete') is True and not audit_report['errors'])
        audit_report['evidence_complete'] = audit_report['complete']
        audit_report['batch_complete'] = audit_report['complete']
    except BaseException as exc:
        audit_report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        audit_report['complete'] = False
        audit_report['evidence_complete'] = False
    try:
        _mkdir_chain(evidence, audit_path.parent)
        audit_report['audit_written'] = True
        _write_json(evidence, audit_path, audit_report)
    except BaseException as write_exc:
        audit_report['audit_written'] = False
        audit_report['complete'] = False
        audit_report['evidence_complete'] = False
        audit_report['batch_complete'] = False
        audit_report['errors'].append('audit write failed: ' + type(write_exc).__name__ + ': ' + str(write_exc))
    return audit_report
