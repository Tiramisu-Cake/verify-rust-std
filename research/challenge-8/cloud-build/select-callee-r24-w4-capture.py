#!/usr/bin/env python3
"""Capture R24's unchanged generic sort4_stable source and typed MIR inputs.

This Cloud-only stage constructs the already pinned c1-c5 ghost annotation
fixture, exports/decodes normal and readonly MIR, and runs refinement. It never
runs VeriFast or establishes body proof or select call linkage.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback
import uuid
from typing import Any


SCHEMA = 'select-r24-w4-capture-v1'
SUMMARY_REL = Path('cases/r24-w4-capture/W4-CAPTURE.json')
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
MODE_SHA256 = '1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
PROFILE_LABEL = 'experimental-s6-26.10-v1'
SOURCE_REL = Path('library/core/src/slice/sort/shared/smallsort.rs')
SOURCE_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
SOURCE_BLOB = '40939f922bcb6fdc7ee0d30427fa861827043827'
CONSTRUCTOR_PROFILE = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json')
CONSTRUCTOR_PROFILE_SHA256 = 'd1e0d2ddf6cd8eba5dab5a7b2a68a7530595f9b7745c6f8276f20f155b0f546d'
CONST_QUALIFICATION = Path('research/challenge-8/task-history/select-callee-r24/CONST-CALLEE-QUALIFICATION.json')
CONST_QUALIFICATION_SHA256 = '1d50cc12011cd8bae26f1a69fee7e43579ab3ef9bacf5708eac33875a4a00794'
PUBLISHED_INTERFACE = Path('research/challenge-8/task-history/select-callee-r23/P2-INTERFACE.json')
PUBLISHED_INTERFACE_SHA256 = '656b15c1f295db2f7935f14067cf17067f04186994009715772157eb97fd2322'
QUALIFIED_PROFILE_SHA256 = '4ae19eea0042c0dd1dbbe2aa7ca04dccea7df7355bbe2c00ceea3e934b83af13'
PROVIDER_SHA256 = '771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616'
TOOL_HASHES = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/verifast': '01eaa29335277643e2c16dd35b561e2aecee867fbdd64cf13b8eb1d082602cd6',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007',
}
HELPER_PINS = {
    'sort4_body': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-r21.py', 'ae8c57e0549e3a900ad3660ddd302e0d4029293aa074b6accc132f003b655c16'),
    'c1': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-c1.py', '8af19b63552b7ef6e4b6026b4f188fa00c4344a4bb1b75848008e7b46141441e'),
    'c2_c5': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-body-c2.py', '4afc89d4790a2b9d8ff5501835f50eb23c26a50033b0fb68ef4f69cdf2fd528d'),
    'recover_pair': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-recover-pair.rs', '7a28ae5734c5288ff466764e6645eff236f30c097a7951ebd086f5bb7f5eff72'),
    'recover_four': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-actual-recover-four.rs', '9637aee892e633c2521d8cef62770a6be0982a1835492b6afffafc97f9246d8b'),
    'ghost_grammar': ('research/challenge-8/cloud-build/sort4-caller-entry-native/a1-ghost-grammar.py', '603827833b3a5524fa35c1f6c924c2dfcab73ecdbe3a18daa2d249c0ef8e08ce'),
    'ghost_strip': ('research/challenge-8/cloud-build/sort4-native-c1-bound/ghost-strip.py', '1b1187a78b461fd37980e82b679c6df01e95b440896eea347da4cea8fe27c70d'),
    'capture': ('research/challenge-8/overnight-sort4/capture.py', '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'),
}
BLOCKED_ENV = {
    'SORT4_A1_PHASE_ID', 'SORT4_A1_AUTHORIZATION_PHASE_ID',
    'SORT4_A1_CHECKED_TRAIT_CONTRACT', 'SORT4_A1_PROFILE_SHA256',
}
ALLOWED_SORT4_ENV = {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'}
COUNTS = {b'is_less(': 5, b'hint::select_unpredictable(': 8,
          b'ptr::copy_nonoverlapping(': 4}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError('R24-W4-CAPTURE: ' + message)


def _require_workspace_paths(args: argparse.Namespace) -> None:
    for name in ('repo', 'cloud_dir', 'evidence', 'tool_home', 'schema', 'compiler_sysroot'):
        path = Path(getattr(args, name)).resolve()
        _need(path.is_relative_to(Path('/workspace')),
              name + ' path must be under Cloud /workspace')


def expected_mode() -> dict[str, Any]:
    return {
        'schema': 'select-r24-w4-capture-mode-v1', 'enabled': True,
        'source_only': True, 'body_proof_run': False, 'call_linkage': False,
        'proof_admission': False, 'publication_allowed': False,
        'accepted': False, 'independent_proof_credit': 0,
        'owner': 'select-sort4', 'phase_id': R24_PHASE,
        'route_phase_id': R21_PHASE, 'lane': LANE,
        'profile': PROFILE_LABEL,
        'const_qualification_path': CONST_QUALIFICATION.as_posix(),
        'const_qualification_sha256': CONST_QUALIFICATION_SHA256,
        'published_interface_path': PUBLISHED_INTERFACE.as_posix(),
        'published_interface_sha256': PUBLISHED_INTERFACE_SHA256,
        'qualified_profile_sha256': QUALIFIED_PROFILE_SHA256,
        'constructor_profile_path': CONSTRUCTOR_PROFILE.as_posix(),
        'constructor_profile_sha256': CONSTRUCTOR_PROFILE_SHA256,
        'source_path': SOURCE_REL.as_posix(), 'source_sha256': SOURCE_SHA256,
        'source_git_blob': SOURCE_BLOB,
        'helpers': {name: {'path': path, 'sha256': digest}
                    for name, (path, digest) in HELPER_PINS.items()},
        'tool_hashes': TOOL_HASHES,
    }


def _read_mode(repo: Path, mode_path: Path) -> dict[str, Any]:
    expected_path = repo / MODE_REL
    _need(mode_path.resolve() == expected_path.resolve() and mode_path.is_file() and
          not mode_path.is_symlink(), 'exact mode manifest path required')
    raw = mode_path.read_bytes()
    _need(sha(raw) == MODE_SHA256,
          'mode manifest SHA differs')
    try:
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('R24-W4-CAPTURE: malformed mode JSON') from exc
    _need(value == expected_mode(), 'mode manifest fields differ')
    return value


def _validate_route(env: dict[str, str]) -> dict[str, str]:
    _need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
          env.get(R24_PHASE_ENV) == R24_PHASE and
          env.get(R21_PHASE_ENV) == R21_PHASE and env.get('LANE') == LANE and
          env.get('SORT4_SELECT_PROFILE') == PROFILE_LABEL and
          not env.get('GITHUB_ACTIONS'), 'exact R24/R21/profile Cloud route required')
    bad = sorted(key for key in env if key.startswith('SORT4_') and
                 key not in ALLOWED_SORT4_ENV)
    _need(not bad, 'ambient SORT4 opt-ins refused: ' + ', '.join(bad))
    return {
        'provider': env.get('SMALLSORT_EXECUTION_PROVIDER', ''),
        'phase_id': env.get(R24_PHASE_ENV, ''),
        'route_phase_id': env.get(R21_PHASE_ENV, ''),
        'lane': env.get('LANE', ''), 'profile': env.get('SORT4_SELECT_PROFILE', ''),
    }


def _load(path: Path, name: str, expected: str):
    _need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected,
          'pinned helper differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    _need(spec is not None and spec.loader is not None, 'helper cannot be imported: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    _need(sha(path.read_bytes()) == expected, 'helper changed during import: ' + str(path))
    return module


def _provider(cloud_dir: Path, expected: dict[str, Any]) -> dict[str, str]:
    path = cloud_dir / 'provider.py'
    _need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == PROVIDER_SHA256,
          'pinned provider module missing or changed')
    module = _load(path, 'r24_w4_provider', PROVIDER_SHA256)
    record = module.require_supported_provider()
    _need(record.get('provider') == 'cloud-build' and
          record.get('project') == 'smallsort-ci' and record.get('region') == 'global' and
          record.get('os') == 'ubuntu-22.04' and record.get('arch') == 'x86_64' and
          record.get('build_id') == os.environ.get('CLOUD_BUILD_ID'),
          'native Cloud provider identity differs')
    _need(bool(re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', record['build_id'])),
          'native Build ID is not canonical')
    return record


def _validate_published_inputs(repo: Path, mode: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    const_path = repo / CONST_QUALIFICATION
    interface_path = repo / PUBLISHED_INTERFACE
    _need(const_path.is_file() and not const_path.is_symlink() and
          sha(const_path.read_bytes()) == CONST_QUALIFICATION_SHA256,
          'qualified const callee receipt differs')
    _need(interface_path.is_file() and not interface_path.is_symlink() and
          sha(interface_path.read_bytes()) == PUBLISHED_INTERFACE_SHA256,
          'published P2 interface differs')
    const = json.loads(const_path.read_text(encoding='utf-8'))
    interface = json.loads(interface_path.read_text(encoding='utf-8'))
    _need(const.get('accepted') is True and const.get('status') ==
          'QUALIFIED_UNDER_EXACT_EXPERIMENTAL_PROFILE' and
          type(const.get('proof_credit')) is int and const.get('proof_credit') == 0 and
          const.get('tool_hashes') == TOOL_HASHES,
          'const callee qualification/profile boundary differs')
    _need(interface.get('schema') == 'select-p2-interface-v1' and
          interface.get('status') == 'PUBLISHED' and
          interface.get('contract_text_sha256') ==
          'dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870',
          'published P2 interface is not the pinned contract')
    profile_pin = interface.get('proof_profile', {}).get('qualified_profile', {})
    _need(profile_pin.get('path') ==
          'research/challenge-8/task-history/select-callee-r24/P2-MUT-QUALIFIED-PROFILE.json' and
          profile_pin.get('sha256') == QUALIFIED_PROFILE_SHA256,
          'published interface qualified-profile pin differs')
    qualified_profile_path = repo / profile_pin['path']
    _need(qualified_profile_path.is_file() and not qualified_profile_path.is_symlink() and
          sha(qualified_profile_path.read_bytes()) == QUALIFIED_PROFILE_SHA256,
          'published qualified profile bytes differ')
    _need(mode['qualified_profile_sha256'] == QUALIFIED_PROFILE_SHA256,
          'qualified experimental profile pin differs')
    return const, interface


def _tool_hashes(tool_home: Path) -> dict[str, str]:
    paths = {
        'bin/refinement-checker': tool_home / 'bin/refinement-checker',
        'bin/verifast': tool_home / 'bin/verifast',
        'bin/vf-rust-mir-exporter': tool_home / 'bin/vf-rust-mir-exporter',
        'src/frontend/ocaml_expr_of_ast.ml': tool_home / 'src/frontend/ocaml_expr_of_ast.ml',
        'src/rust_frontend/vf_mir/vf_mir.capnp': tool_home / 'src/rust_frontend/vf_mir/vf_mir.capnp',
        'src/rust_frontend/vf_mir_translator/rust_parser.ml': tool_home / 'src/rust_frontend/vf_mir_translator/rust_parser.ml',
        'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': tool_home / 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
        'bin/rust/std/lib.rsspec': tool_home / 'bin/rust/std/lib.rsspec',
    }
    _need(all(path.is_file() and not path.is_symlink() for path in paths.values()),
          'qualified tool/profile files missing or symlinked')
    return {key: sha(path.read_bytes()) for key, path in paths.items()}


def _load_constructor_inputs(repo: Path, mode: dict[str, Any]):
    profile_path = repo / CONSTRUCTOR_PROFILE
    _need(profile_path.is_file() and not profile_path.is_symlink() and
          sha(profile_path.read_bytes()) == CONSTRUCTOR_PROFILE_SHA256,
          'R21 constructor profile pin differs (navigation only)')
    profile = json.loads(profile_path.read_text(encoding='utf-8'))
    _need(profile.get('actual_indexed_calls') == 5 and
          profile.get('body_action') == 'full-body-c1-recovery' and
          profile.get('cloud_build_enabled') is False and
          profile.get('std_source_sha256', {}).get(SOURCE_REL.as_posix()) == SOURCE_SHA256,
          'R21 profile is not the dormant count-five constructor input')
    modules = {}
    for name in ('sort4_body', 'c1', 'c2_c5', 'ghost_grammar', 'ghost_strip', 'capture'):
        rel, digest = HELPER_PINS[name]
        modules[name] = _load(repo / rel, 'r24_w4_' + name, digest)
    _need(profile.get('a1_actual_body_sha256') == HELPER_PINS['sort4_body'][1] and
          profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-body-c1.py') == HELPER_PINS['c1'][1] and
          profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-body-c2.py') == HELPER_PINS['c2_c5'][1] and
          profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-recover-pair.rs') == HELPER_PINS['recover_pair'][1] and
          profile.get('actual_body_dependencies_sha256', {}).get('a1-actual-recover-four.rs') == HELPER_PINS['recover_four'][1] and
          profile.get('a1_ghost_grammar_sha256') == HELPER_PINS['ghost_grammar'][1],
          'R21 constructor profile dependency pins differ')
    return profile, modules


def _source_comparator_lines(source: bytes) -> list[int]:
    hits: dict[int, list[int]] = {index: [] for index in range(1, 6)}
    for line_number, line in enumerate(source.splitlines(), 1):
        match = re.match(rb'\s*let\s+c([1-5])\s*=\s*is_less\(', line)
        if match:
            hits[int(match.group(1))].append(line_number)
    _need(all(len(hits[index]) == 1 for index in hits),
          'source does not have one exact c1-c5 comparator expression each')
    lines = [hits[index][0] for index in range(1, 6)]
    _need(lines == sorted(set(lines)), 'source comparator calls are not uniquely ordered')
    return lines


def _refresh_coordinates(refresh, case: tuple[Any, ...]) -> tuple[bytes, bytes, dict[str, Any]]:
    refreshed = refresh(case)
    _need(isinstance(refreshed, tuple) and len(refreshed) == 4,
          'refresh_callback_coordinates must return (case_name, verified, original, metadata)')
    case_name, verified, original, metadata = refreshed
    _need(case_name == 'sort4_stable', 'refreshed target name differs')
    _need(isinstance(verified, bytes) and isinstance(original, bytes) and
          isinstance(metadata, dict), 'refreshed source pair/metadata has wrong type')
    return verified, original, metadata


def _construct(repo: Path, evidence: Path, modules: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    source_path = repo / SOURCE_REL
    _need(source_path.is_file() and not source_path.is_symlink(), 'pinned std source missing')
    source = source_path.read_bytes()
    _need(sha(source) == SOURCE_SHA256, 'actual std source SHA differs')
    source_comparator_lines = _source_comparator_lines(source)
    blob = subprocess.check_output(['git', '-C', str(repo), 'hash-object', str(source_path)], text=True).strip()
    _need(blob == SOURCE_BLOB, 'actual std source Git blob differs')
    body = modules['sort4_body']
    c1 = modules['c1']
    c5 = modules['c2_c5']
    ghost = modules['ghost_strip']
    cap = modules['capture']
    pair = (repo / HELPER_PINS['recover_pair'][0]).read_bytes()
    four = (repo / HELPER_PINS['recover_four'][0]).read_bytes()
    _need(sha(pair) == HELPER_PINS['recover_pair'][1] and sha(four) == HELPER_PINS['recover_four'][1],
          'recovery helper bytes changed')
    verified, original, metadata = c5.construct_c5(
        source, ghost, cap, pair, four, c1, body.construct_actual, body.lemma_metadata)
    verified, original, metadata = _refresh_coordinates(
        body.refresh_callback_coordinates,
        ('sort4_stable', verified, original, metadata))
    _need(metadata.get('actual_indexed_calls') == 5 and
          metadata.get('callback_call_lines') and len(metadata['callback_call_lines']) == 5 and
          metadata['callback_call_lines'] == sorted(set(metadata['callback_call_lines'])) and
          ghost.strip_ghost(verified) == original,
          'c5 source constructor/count/runtime identity failed')
    _need(all(original.count(fragment) == count for fragment, count in COUNTS.items()),
          'complete body source counts are not 5/8/4')
    out = evidence / 'cases/r24-w4-capture/fixture'
    (out / 'verified').mkdir(parents=True)
    (out / 'original').mkdir(parents=True)
    (out / 'verified/lib.rs').write_bytes(verified)
    (out / 'original/lib.rs').write_bytes(original)
    return {
        'source_path': SOURCE_REL.as_posix(), 'source_sha256': sha(source),
        'source_git_blob': blob,
        'original_sha256': sha(original), 'verified_sha256': sha(verified),
        'ghost_strip_identity': True, 'runtime_source_sha256': sha(original),
        'source_call_counts': {key.decode(): value for key, value in COUNTS.items()},
        'signature': cap.FUNCTION_HEADER.decode('utf-8'),
        'target': metadata.get('name'), 'body_annotation_stage': metadata.get('body_annotation_stage'),
        'source_comparator_lines': source_comparator_lines,
        'c1_c5_comparator_lines': metadata.get('callback_call_lines'),
        'c1_c5_coordinates_source_reported': True,
        'c5_metadata': metadata,
        'fixture_paths': {
            'original': 'cases/r24-w4-capture/fixture/original/lib.rs',
            'verified': 'cases/r24-w4-capture/fixture/verified/lib.rs',
        },
        'fixture_files': {'original/lib.rs': original, 'verified/lib.rs': verified},
    }


def _safe_file(root: Path, rel: str) -> tuple[bytes, dict[str, Any]]:
    path = root / rel
    _need(not path.is_symlink() and path.is_file() and path.resolve().is_relative_to(root.resolve()),
          'capture artifact missing/symlinked/outside root: ' + rel)
    raw = path.read_bytes()
    return raw, {'path': path.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)}


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def _artifact_inventory(root: Path, summary_path: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob('*')):
        if path == summary_path:
            continue
        _need(not path.is_symlink(), 'capture artifact symlink: ' + str(path))
        if path.is_file():
            raw = path.read_bytes()
            rows.append({'path': path.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
        elif not path.is_dir():
            _need(False, 'capture artifact is not regular: ' + str(path))
    return rows


def _selector_observation(record: str) -> dict[str, Any]:
    lines = record.splitlines()
    rows = [{'line': index + 1, 'text': line.strip()}
            for index, line in enumerate(lines) if 'select_unpredictable' in line]
    # Keep source sites and raw decoded representation, but do not infer a typed
    # callee linkage from textual MIR serializer output.
    return {'source_call_count': 8, 'raw_record_lines': rows,
            'raw_occurrences': len(rows), 'typed_call_linkage': 'UNKNOWN',
            'reason': 'capture stage has no reviewed MIR call-target parser'}


def _status(stage: object) -> str:
    if not isinstance(stage, dict):
        return 'MISSING_OR_WRONG_TYPE'
    if stage.get('skipped') is not None or stage.get('exit') is None:
        return 'NOT_RUN'
    if type(stage.get('exit')) is not int:
        return 'WRONG_TYPE'
    return 'RAN'


def _ordered_ints(value: object, count: int) -> bool:
    return (isinstance(value, list) and len(value) == count and
            all(type(item) is int and item > 0 for item in value) and
            value == sorted(set(value)))


def _check_stage(stage: object, label: str) -> list[str]:
    if not isinstance(stage, dict):
        return [label + ' stage missing/wrong type']
    errors = []
    if _status(stage) != 'RAN':
        errors.append(label + ' stage is ' + _status(stage))
    elif stage.get('exit') != 0:
        errors.append(label + ' stage exit is not zero')
    if stage.get('fixture_integrity') is not True:
        errors.append(label + ' fixture integrity is not true')
    return errors


def collect(args: argparse.Namespace, *, stage_runner=None) -> dict[str, Any]:
    repo, cloud_dir, evidence, tool_home = map(Path, (args.repo, args.cloud_dir, args.evidence, args.tool_home))
    summary_path = evidence / SUMMARY_REL
    _require_workspace_paths(args)
    _need(not (evidence / SUMMARY_REL.parent).exists() and
          not (evidence / SUMMARY_REL.parent).is_symlink(),
          'W4 capture output root already exists')
    report: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_W4_CAPTURE', 'complete': False,
        'body_proof_run': False, 'call_linkage': False, 'call_linkage_status': 'UNKNOWN',
        'proof_admission': False, 'publication_allowed': False, 'accepted': False,
        'proof_credit': 0, 'independent_proof_credit': 0,
        'runner_exit': None, 'failed_stage': 'preflight', 'stages': {},
        'errors': [], 'artifact_inventory': [],
    }
    _atomic_json(summary_path, report)
    try:
        _require_workspace_paths(args)
        _validate_route(dict(os.environ))
        _need(subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == args.candidate,
              'proof checkout does not match candidate SHA')
        mode = _read_mode(repo, Path(args.mode_file))
        _validate_published_inputs(repo, mode)
        provider = _provider(cloud_dir, mode)
        report.update(r24_session_phase_id=R24_PHASE, route_phase_id=R21_PHASE,
                      lane=LANE, owner='select-sort4', mode_sha256=MODE_SHA256,
                      provider_record=provider, candidate=args.candidate)
        report['failed_stage'] = 'tool-preflight'
        actual_tool_hashes = _tool_hashes(tool_home)
        _need(actual_tool_hashes == TOOL_HASHES, 'same-version qualified tool hashes differ')
        _need(Path(args.schema).resolve() == (tool_home / 'src/rust_frontend/vf_mir/vf_mir.capnp').resolve(),
              'schema is not the exact same-tool schema')
        _need(sha(Path(args.schema).read_bytes()) == TOOL_HASHES['src/rust_frontend/vf_mir/vf_mir.capnp'],
              'schema hash differs')
        _need(type(args.deadline_epoch) is int and args.deadline_epoch > int(time.time()) + 30,
              'shared deadline lacks minimum reserve')
        report['tool_hashes'] = actual_tool_hashes
        report['schema_sha256'] = sha(Path(args.schema).read_bytes())
        _atomic_json(summary_path, report)
        profile, modules = _load_constructor_inputs(repo, mode)
        report['failed_stage'] = 'source-preparation'
        _atomic_json(summary_path, report)
        source = _construct(repo, evidence, modules, profile)
        source_hashes = {rel: digest for rel, digest in (
            ('original/lib.rs', source['original_sha256']),
            ('verified/lib.rs', source['verified_sha256']))}
        fixture_root = evidence / SUMMARY_REL.parent / 'fixture'
        capture = modules['capture']
        if stage_runner is None:
            runner = capture.run_stage
            def stage_runner(name, argv, fixture, env, hashes, deadline, cap, stdin=None, stdout=None):
                return runner(name, argv, fixture, env, hashes, deadline, cap, stdin, stdout)
        env = dict(os.environ)
        env['PATH'] = str(tool_home / 'bin') + os.pathsep + env.get('PATH', '')
        exporter = str(tool_home / 'bin/vf-rust-mir-exporter')
        stages = report['stages']
        report['failed_stage'] = 'normal-export'
        stages['normal-export'] = stage_runner('normal-export', [exporter, 'verified/lib.rs',
            f'--sysroot={Path(args.compiler_sysroot).resolve()}', '--edition', '2021'],
            fixture_root, env, source_hashes, args.deadline_epoch, 100, stdout='normal-mir.bin')
        if _status(stages['normal-export']) == 'RAN' and stages['normal-export'].get('exit') == 0:
            report['failed_stage'] = 'normal-decode'
            stages['normal-decode'] = stage_runner('normal-decode',
                ['capnp', 'decode', str(Path(args.schema).resolve()), 'VfMir'], fixture_root,
                env, source_hashes, args.deadline_epoch, 60, 'normal-mir.bin', 'normal-mir.txt')
        else:
            stages['normal-decode'] = {'exit': None, 'skipped': 'normal export did not complete'}
        report['failed_stage'] = 'readonly-export'
        stages['readonly-export'] = stage_runner('readonly-export', [exporter, 'verified/lib.rs',
            f'--sysroot={Path(args.compiler_sysroot).resolve()}', '--edition', '2021',
            '--vf-rust-mir-exporter:preprocess-readonly'], fixture_root, env, source_hashes,
            args.deadline_epoch, 100, stdout='readonly-mir.bin')
        if _status(stages['readonly-export']) == 'RAN' and stages['readonly-export'].get('exit') == 0:
            report['failed_stage'] = 'readonly-decode'
            stages['readonly-decode'] = stage_runner('readonly-decode',
                ['capnp', 'decode', str(Path(args.schema).resolve()), 'VfMir'], fixture_root,
                env, source_hashes, args.deadline_epoch, 60, 'readonly-mir.bin', 'readonly-mir.txt')
        else:
            stages['readonly-decode'] = {'exit': None, 'skipped': 'readonly export did not complete'}
        report['failed_stage'] = 'refinement'
        stages['refinement'] = stage_runner('refinement', [str(tool_home / 'bin/refinement-checker'),
            '--rustc-args', '--edition 2021', 'original/lib.rs', 'verified/lib.rs'],
            fixture_root, env, source_hashes, args.deadline_epoch, 120)
        for label in ('normal-export', 'normal-decode', 'readonly-export', 'readonly-decode', 'refinement'):
            report['errors'].extend(_check_stage(stages.get(label), label))
        report['source'] = {k: v for k, v in source.items() if k != 'fixture_files'}
        _atomic_json(summary_path, report)
        for mode_name in ('normal', 'readonly'):
            rel = f'{mode_name}-mir.txt'
            path = fixture_root / rel
            if path.is_file() and not path.is_symlink():
                decoded = path.read_text(encoding='utf-8', errors='strict')
                function_path = evidence / SUMMARY_REL.parent / f'{mode_name}-sort4-full-mir.txt'
                graph = capture.graph_inventory(path, evidence / SUMMARY_REL.parent, mode_name)
                record = capture.complete_function_record(decoded, 'sort4_stable')[1]
                function_path.write_text(record, encoding='utf-8')
                report.setdefault('mir', {})[mode_name] = {
                    'decoded_sha256': sha(decoded.encode()), 'graph_inventory': graph,
                    'full_function_record': function_path.relative_to(evidence).as_posix(),
                    'full_function_record_sha256': sha(record.encode()),
                    'selector_call_observation': _selector_observation(record),
                }
            else:
                report['errors'].append(mode_name + ' decoded MIR artifact missing or symlinked')
        source_after = (repo / SOURCE_REL).read_bytes()
        report['source']['repository_source_unchanged'] = sha(source_after) == SOURCE_SHA256
        if not report['source']['repository_source_unchanged']:
            report['errors'].append('source file changed during capture')
        for key, rel in source['fixture_paths'].items():
            try:
                fixture_raw, _ = _safe_file(evidence, rel)
                expected = source[key + '_sha256']
                if sha(fixture_raw) != expected:
                    report['errors'].append(key + ' fixture changed during capture')
            except (OSError, ValueError) as exc:
                report['errors'].append(key + ' fixture final check failed: ' + str(exc))
        tool_hashes_after = _tool_hashes(tool_home)
        report['tool_hashes_after'] = tool_hashes_after
        if tool_hashes_after != actual_tool_hashes:
            report['errors'].append('tool identity changed during capture')
        report['errors'] = list(dict.fromkeys(report['errors']))
        if report['errors']:
            report['failed_stage'] = next(
                (name for name in ('normal-export', 'normal-decode', 'readonly-export',
                                   'readonly-decode', 'refinement')
                 if _check_stage(stages.get(name), name)), 'capture-validation')
        report['failed_stage'] = 'complete' if not report['errors'] else report['failed_stage']
        report['runner_exit'] = 0 if not report['errors'] else 4
        report['complete'] = not report['errors']
        report['classification'] = 'COMPLETE_SOURCE_REPORTED_W4_CAPTURE' if report['complete'] else 'INCOMPLETE_W4_CAPTURE'
    except BaseException as exc:
        report['runner_exit'] = 4
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        report['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                               'traceback': traceback.format_exc()}
        if not report.get('failed_stage'):
            report['failed_stage'] = 'exception'
        # Preserve the original exception even if writing a partial report fails.
        try:
            report['artifact_inventory'] = _artifact_inventory(evidence / SUMMARY_REL.parent, summary_path)
            _atomic_json(summary_path, report)
        except BaseException as write_exc:
            report['partial_write_error'] = type(write_exc).__name__ + ': ' + str(write_exc)
        raise
    try:
        report['artifact_inventory'] = _artifact_inventory(evidence / SUMMARY_REL.parent, summary_path)
    except BaseException as exc:
        report['complete'] = False
        report['classification'] = 'INCOMPLETE_W4_CAPTURE'
        report['runner_exit'] = 4
        report['errors'].append(type(exc).__name__ + ': artifact inventory failed')
        report['inventory_error'] = type(exc).__name__ + ': ' + str(exc)
    _atomic_json(summary_path, report)
    return report


def audit(args: argparse.Namespace) -> dict[str, Any]:
    _require_workspace_paths(args)
    evidence = Path(args.evidence)
    path = evidence / SUMMARY_REL
    _need(path.is_file() and not path.is_symlink(), 'capture summary missing/symlinked')
    report = json.loads(path.read_text(encoding='utf-8'))
    _need(isinstance(report, dict) and report.get('schema') == SCHEMA,
          'capture summary schema differs')
    _validate_route(dict(os.environ))
    mode = _read_mode(Path(args.repo), Path(args.mode_file))
    _validate_published_inputs(Path(args.repo), mode)
    provider = _provider(Path(args.cloud_dir), mode)
    errors = []
    if report.get('provider_record') != provider: errors.append('native provider binding differs')
    if report.get('candidate') != args.candidate: errors.append('proof candidate binding differs')
    if report.get('mode_sha256') != MODE_SHA256: errors.append('mode digest binding differs')
    if report.get('complete') is not True: errors.append('run summary is incomplete')
    if report.get('body_proof_run') is not False or report.get('call_linkage') is not False or report.get('proof_credit') != 0:
        errors.append('capture-only boundary flags differ')
    if report.get('call_linkage_status') != 'UNKNOWN':
        errors.append('capture must not claim typed call linkage')
    if type(args.runner_exit) is not int or args.runner_exit != 0: errors.append('runner exit is not zero')
    if args.failed_stage != 'complete': errors.append('runner did not complete requested stage')
    if report.get('source', {}).get('repository_source_unchanged') is not True:
        errors.append('repository source was not observed unchanged')
    if report.get('tool_hashes') != TOOL_HASHES:
        errors.append('qualified tool hashes differ')
    if report.get('tool_hashes_after') != TOOL_HASHES:
        errors.append('qualified tool hashes after stages differ')
    stages = report.get('stages')
    if not isinstance(stages, dict):
        errors.append('stage inventory missing')
    else:
        for name in ('normal-export', 'normal-decode', 'readonly-export',
                     'readonly-decode', 'refinement'):
            errors.extend(_check_stage(stages.get(name), name))
    source_record = report.get('source')
    if isinstance(source_record, dict):
        if source_record.get('source_sha256') != SOURCE_SHA256 or \
           source_record.get('source_git_blob') != SOURCE_BLOB or \
           source_record.get('source_call_counts') != {key.decode(): value for key, value in COUNTS.items()} or \
           source_record.get('ghost_strip_identity') is not True or \
           source_record.get('c1_c5_coordinates_source_reported') is not True or \
           source_record.get('target') != 'sort4_stable' or \
           not _ordered_ints(source_record.get('source_comparator_lines'), 5) or \
           not _ordered_ints(source_record.get('c1_c5_comparator_lines'), 5):
            errors.append('source/c1-c5 identity binding differs')
        try:
            source_now = (Path(args.repo) / SOURCE_REL).read_bytes()
            if sha(source_now) != SOURCE_SHA256 or \
               _source_comparator_lines(source_now) != source_record.get('source_comparator_lines'):
                errors.append('physical source/c1-c5 line binding differs')
        except BaseException as exc:
            errors.append('physical source check failed: ' + type(exc).__name__ + ': ' + str(exc))
    mir = report.get('mir')
    if not isinstance(mir, dict) or set(mir) != {'normal', 'readonly'}:
        errors.append('normal/readonly full-body MIR captures missing')
    else:
        for key in ('normal', 'readonly'):
            row = mir.get(key)
            if not isinstance(row, dict) or \
               not isinstance(row.get('selector_call_observation'), dict) or \
               row['selector_call_observation'].get('typed_call_linkage') != 'UNKNOWN' or \
               not isinstance(row.get('full_function_record_sha256'), str):
                errors.append(key + ' MIR record/linkage boundary malformed')
    try:
        _require_workspace_paths(args)
        case_root = evidence / SUMMARY_REL.parent
        actual_inventory = _artifact_inventory(case_root, path)
        if actual_inventory != report.get('artifact_inventory'):
            errors.append('physical artifact inventory differs')
        src = report.get('source')
        if not isinstance(src, dict):
            errors.append('source record missing')
        else:
            for key in ('original', 'verified'):
                rel = src.get('fixture_paths', {}).get(key)
                if not isinstance(rel, str):
                    errors.append(key + ' fixture path missing')
                    continue
                raw, _ = _safe_file(evidence, rel)
                expected = src.get(key + '_sha256')
                if sha(raw) != expected:
                    errors.append(key + ' fixture bytes differ')
            original, _ = _safe_file(evidence, src['fixture_paths']['original'])
            verified, _ = _safe_file(evidence, src['fixture_paths']['verified'])
            _, constructors = _load_constructor_inputs(Path(args.repo), mode)
            if constructors['ghost_strip'].strip_ghost(verified) != original:
                errors.append('physical verified/original ghost-strip identity differs')
    except BaseException as exc:
        errors.append('physical capture audit failed: ' + type(exc).__name__ + ': ' + str(exc))
    report['audit'] = {'evidence_complete': not errors, 'errors': errors,
                       'runner_exit': args.runner_exit, 'failed_stage': args.failed_stage}
    report['evidence_complete'] = not errors
    report.update(accepted=False, publication_allowed=False, proof_credit=0)
    output = Path(args.output) if args.output else evidence / 'w4-capture-audit.json'
    _atomic_json(output, report)
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'audit'):
        p = sub.add_parser(name)
        for arg in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'schema', 'compiler-sysroot', 'mode-file'):
            p.add_argument('--' + arg, required=True)
        p.add_argument('--candidate', required=True)
        if name == 'run':
            p.add_argument('--deadline-epoch', required=True, type=int)
        else:
            p.add_argument('--deadline-epoch', type=int)
            p.add_argument('--output')
            p.add_argument('--runner-exit', required=True, type=int)
            p.add_argument('--failed-stage', required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = collect(args) if args.command == 'run' else audit(args)
    except BaseException:
        if isinstance(sys.exc_info()[1], (KeyboardInterrupt, SystemExit)):
            raise
        print('R24-W4-CAPTURE: incomplete; see partial summary', file=sys.stderr)
        return 4
    return 0 if (report.get('complete') if args.command == 'run' else report.get('evidence_complete')) else 4


if __name__ == '__main__':
    raise SystemExit(main())
