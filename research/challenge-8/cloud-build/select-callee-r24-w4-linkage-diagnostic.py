#!/usr/bin/env python3
"""Fresh R24 W4 MIR call inventory plus one diagnostic native first barrier.

This entry intentionally does not claim a body proof or checked caller
linkage.  It reuses the frozen W4 capture producer, then runs a typed MIR
inventory and one ordinary VeriFast AST-location diagnostic in a separate
physical fixture directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
from typing import Any


SCHEMA = 'select-r24-w4-linkage-diagnostic-v1'
SUMMARY_REL = Path('cases/r24-w4-linkage-diagnostic/W4-LINKAGE-DIAGNOSTIC.json')
AUDIT_REL = Path('cases/r24-w4-linkage-diagnostic/W4-LINKAGE-DIAGNOSTIC-AUDIT.json')
CASE_REL = Path('cases/r24-w4-linkage-diagnostic/native')
CAPTURE_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
CAPTURE_MODE_SHA256 = '1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3'
CAPTURE_HELPER_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-capture.py')
CAPTURE_HELPER_SHA256 = '8f3c8bddd385754aeaa4b784f3273a56e6af2f5356658c4df3d50f7c519f812d'
CAPTURE_PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json')
CAPTURE_PINS_SHA256 = 'f81b062111436a7ab8a40e9776fdc1d1138a7861b5a6d95e018201ee93d5b6a0'
MIR_CALLS_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-mir-calls.py')
MIR_CALLS_SHA256 = 'ea7a738a5c564a4c2d00b72dc47aa67f5277b44080aa7eaf28e2fc2d01c25d51'
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-LINKAGE-DIAGNOSTIC-MODE.json')
MODE_SHA256 = '381853c2c5186f627bb90f92e8770bb5d996e69605321420a5765a2bad5e2b5f'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
SOURCE_REL = Path('library/core/src/slice/sort/shared/smallsort.rs')
SOURCE_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
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
ALLOWED_SORT4_ENV = {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'}
NATIVE_ARGV = ('bin/verifast', '-rustc_args', '--edition 2021', '-verbose', '1',
               '-dump_ast_with_locs', 'w4-first-barrier.ast.ml', 'verified/lib.rs')
ALLOWED_NATIVE_EXITS = {0, 1, 2}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError('R24-W4-LINKAGE-DIAGNOSTIC: ' + message)


def _load(path: Path, name: str, expected_sha: str):
    need(expected_sha != 'PENDING' and path.is_file() and not path.is_symlink() and
         digest(path.read_bytes()) == expected_sha, 'pinned helper missing or changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'cannot import helper: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(digest(path.read_bytes()) == expected_sha, 'helper changed during import: ' + str(path))
    return module


def _load_json_pin(repo: Path, rel: Path, expected_sha: str) -> dict[str, Any]:
    path = repo / rel
    need(expected_sha != 'PENDING' and path.is_file() and not path.is_symlink() and
         digest(path.read_bytes()) == expected_sha, 'pinned JSON missing/changed: ' + rel.as_posix())
    value = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(value, dict), 'pinned JSON is not an object: ' + rel.as_posix())
    return value


def expected_mode() -> dict[str, Any]:
    """Closed diagnostic boundary; excludes its own raw mode-file hash."""
    return {
        'schema': 'select-r24-w4-linkage-diagnostic-mode-v1',
        'enabled': True,
        'owner': 'select-sort4',
        'phase_id': R24_PHASE,
        'route_phase_id': R21_PHASE,
        'lane': LANE,
        'profile': PROFILE,
        'capture_mode_path': CAPTURE_MODE_REL.as_posix(),
        'capture_mode_sha256': CAPTURE_MODE_SHA256,
        'capture_pins_path': CAPTURE_PINS_REL.as_posix(),
        'capture_pins_sha256': CAPTURE_PINS_SHA256,
        'mir_calls_path': MIR_CALLS_REL.as_posix(),
        'mir_calls_sha256': MIR_CALLS_SHA256,
        'tool_hashes': TOOL_HASHES,
        'call_linkage': False,
        'body_proof_admission': False,
        'native_diagnostic_only': True,
        'accepted': False,
        'publication_allowed': False,
        'independent_proof_credit': 0,
    }


def _validate_context(args: argparse.Namespace, *, fresh: bool = False) -> tuple[Path, Path, Path, Path]:
    repo, cloud, evidence, tool_home = (Path(args.repo).resolve(), Path(args.cloud_dir).resolve(),
                                        Path(args.evidence).resolve(), Path(args.tool_home).resolve())
    need(all(str(p).startswith('/workspace/') for p in (repo, cloud, evidence, tool_home)),
         'all run roots must be absolute Cloud /workspace paths')
    need(args.candidate and len(args.candidate) == 40 and
         all(c in '0123456789abcdef' for c in args.candidate), 'exact candidate SHA required')
    if fresh:
        need(not (evidence / SUMMARY_REL.parent).exists() and
             not (evidence / SUMMARY_REL.parent).is_symlink(),
             'diagnostic output root already exists')
    return repo, cloud, evidence, tool_home


def _validate_route() -> dict[str, str]:
    env = dict(os.environ)
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_PHASE_ENV) == R24_PHASE and env.get(R21_PHASE_ENV) == R21_PHASE and
         env.get('LANE') == LANE and env.get('SORT4_SELECT_PROFILE') == PROFILE and
         not env.get('GITHUB_ACTIONS'), 'exact R24/R21/profile native Cloud route required')
    bad = sorted(key for key in env if key.startswith('SORT4_') and key not in ALLOWED_SORT4_ENV)
    need(not bad, 'ambient SORT4 opt-ins refused: ' + ', '.join(bad))
    return {'provider': env['SMALLSORT_EXECUTION_PROVIDER'], 'phase_id': env[R24_PHASE_ENV],
            'route_phase_id': env[R21_PHASE_ENV], 'lane': env['LANE'], 'profile': env['SORT4_SELECT_PROFILE']}


def _validate_mode(repo: Path, mode_path: Path, capture_mode_path: Path,
                   pins_path: Path, analyzer_path: Path) -> dict[str, Any]:
    need(MODE_SHA256 != 'PENDING' and mode_path.resolve() == repo.joinpath(MODE_REL).resolve() and
         mode_path.is_file() and not mode_path.is_symlink() and digest(mode_path.read_bytes()) == MODE_SHA256,
         'exact diagnostic mode path/hash required')
    mode = json.loads(mode_path.read_text(encoding='utf-8'))
    need(isinstance(mode, dict) and mode == expected_mode(),
         'diagnostic mode fields differ')
    need(capture_mode_path.resolve() == repo.joinpath(CAPTURE_MODE_REL).resolve() and
         capture_mode_path.is_file() and not capture_mode_path.is_symlink() and
         digest(capture_mode_path.read_bytes()) == CAPTURE_MODE_SHA256,
         'frozen source capture mode differs')
    _load_json_pin(repo, CAPTURE_PINS_REL, CAPTURE_PINS_SHA256)
    need(analyzer_path.is_file() and not analyzer_path.is_symlink() and
         digest(analyzer_path.read_bytes()) == MIR_CALLS_SHA256,
         'typed MIR call analyzer pin differs')
    return mode


def _tool_hashes(tool_home: Path) -> dict[str, str]:
    result = {}
    for rel in TOOL_HASHES:
        path = tool_home / rel
        need(path.is_file() and not path.is_symlink(), 'qualified tool file missing/symlinked: ' + rel)
        result[rel] = digest(path.read_bytes())
    need(result == TOOL_HASHES, 'current tool identity differs from 8a026 profile')
    return result


def _capture_args(args: argparse.Namespace, capture_mode: Path) -> argparse.Namespace:
    values = vars(args).copy()
    values.update(mode_file=str(capture_mode), output=None)
    return argparse.Namespace(**values)


def _capture_source_files(evidence: Path, capture_report: dict[str, Any], capture: Any,
                          native_root: Path) -> dict[str, str]:
    source = capture_report.get('source')
    need(isinstance(source, dict), 'fresh source record missing')
    paths = source.get('fixture_paths')
    need(isinstance(paths, dict), 'fresh source fixture paths missing')
    native_root.mkdir(parents=True, exist_ok=False)
    hashes: dict[str, str] = {}
    for name in ('original', 'verified'):
        rel = paths.get(name)
        need(isinstance(rel, str), name + ' source fixture path malformed')
        raw, _ = capture._safe_file(evidence, rel)
        expected = source.get(name + '_sha256')
        need(isinstance(expected, str) and digest(raw) == expected, name + ' source fixture hash differs')
        destination = native_root / name / 'lib.rs'
        destination.parent.mkdir(parents=True, exist_ok=False)
        destination.write_bytes(raw)
        hashes[name + '/lib.rs'] = expected
    return hashes


def _analyze(capture: Any, analyzer: Any, evidence: Path, capture_report: dict[str, Any],
             pins: dict[str, Any]) -> dict[str, Any]:
    mir = capture_report.get('mir')
    need(isinstance(mir, dict) and set(mir) == {'normal', 'readonly'},
         'normal/readonly MIR records missing')
    texts = {}
    for mode in ('normal', 'readonly'):
        rec = mir[mode]
        need(isinstance(rec, dict), mode + ' MIR record malformed')
        rel = rec.get('full_function_record')
        need(isinstance(rel, str), mode + ' complete function record path missing')
        raw, _ = capture._safe_file(evidence, rel)
        expected = rec.get('full_function_record_sha256')
        need(isinstance(expected, str) and digest(raw) == expected, mode + ' MIR record digest differs')
        texts[mode] = raw.decode('utf-8', errors='strict')
    out = analyzer.analyze_pair(texts['normal'], texts['readonly'])
    need(isinstance(out, dict), 'typed MIR analyzer returned wrong type')
    if out.get('complete') is not True:
        return out
    normal, readonly = out.get('normal'), out.get('readonly')
    need(isinstance(normal, dict) and isinstance(readonly, dict) and
         isinstance(normal.get('calls'), list) and isinstance(readonly.get('calls'), list) and
         len(normal['calls']) == len(readonly['calls']) == 8,
         'typed MIR analyzer did not find exact eight selector call sites')
    need(out.get('status') == 'COMPLETE_TYPED_MIR_OBSERVATION' and
         out.get('typed_call_linkage') == 'UNKNOWN' and
         out.get('typed_callee_family_observation') == 'OBSERVED_STRUCTURAL_MIR_CALLS' and
         out.get('source_site_mapping') == 'EQUAL_EMITTED_COORDINATES_ONLY',
         'typed MIR normal/readonly structural call observation incomplete')
    return out


def _stage_is_ran(stage: object) -> bool:
    return isinstance(stage, dict) and type(stage.get('exit')) is int and stage.get('skipped') is None


def _native_stage(capture: Any, args: argparse.Namespace, evidence: Path,
                  tool_home: Path, hashes: dict[str, str], stage_runner=None) -> dict[str, Any]:
    native_root = evidence / CASE_REL
    env = {'PATH': str(tool_home / 'bin') + os.pathsep + os.defpath,
           R24_PHASE_ENV: R24_PHASE, R21_PHASE_ENV: R21_PHASE, 'SORT4_SELECT_PROFILE': PROFILE}
    argv = [str(tool_home / part) if part == 'bin/verifast' else part for part in NATIVE_ARGV]
    runner = stage_runner or capture.run_stage
    return runner('first-barrier', argv, native_root, env, hashes, args.deadline_epoch,
                  1200, stdout='w4-first-barrier.log')


def _source_state(repo: Path) -> dict[str, Any]:
    path = repo / SOURCE_REL
    if path.is_file() and not path.is_symlink():
        raw = path.read_bytes()
        return {'path': SOURCE_REL.as_posix(), 'sha256': digest(raw),
                'expected_sha256': SOURCE_SHA256, 'intact': digest(raw) == SOURCE_SHA256}
    return {'path': SOURCE_REL.as_posix(), 'sha256': None,
            'expected_sha256': SOURCE_SHA256, 'intact': False}


def _native_facts(evidence: Path, stage: object) -> dict[str, Any]:
    row = {'stage': stage, 'status': 'MISSING_OR_WRONG_TYPE', 'logs': {},
           'verifier_invoked': False, 'actual_body_proof_status': 'UNKNOWN',
           'stage_record': None}
    if not isinstance(stage, dict):
        return row
    row['status'] = 'RAN' if _stage_is_ran(stage) else 'NOT_RUN_OR_WRONG_TYPE'
    row['verifier_invoked'] = _stage_is_ran(stage)
    for key in ('stdout', 'stderr'):
        rel = stage.get(key)
        if isinstance(rel, str):
            path = evidence / CASE_REL / rel
            if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to((evidence / CASE_REL).resolve()):
                raw = path.read_bytes()
                try:
                    raw.decode('utf-8', errors='strict')
                    text_error = None
                except UnicodeDecodeError as exc:
                    text_error = str(exc)
                row['logs'][key] = {'path': (CASE_REL / rel).as_posix(), 'bytes': len(raw),
                                    'sha256': digest(raw), 'utf8_error': text_error}
            else:
                row['logs'][key] = {'path': rel, 'missing_or_unsafe': True}
    stage_record = evidence / CASE_REL / 'first-barrier-stage.json'
    if stage_record.is_file() and not stage_record.is_symlink() and \
       stage_record.resolve().is_relative_to((evidence / CASE_REL).resolve()):
        raw = stage_record.read_bytes()
        try:
            stored = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            stored = None
        row['stage_record'] = {'path': (CASE_REL / 'first-barrier-stage.json').as_posix(),
                               'bytes': len(raw), 'sha256': digest(raw), 'matches_stage': stored == stage}
    else:
        row['stage_record'] = {'missing_or_unsafe': True}
    return row


def _validate_native(evidence: Path, stage: object, facts: dict[str, Any], hashes: dict[str, str],
                     tool_home: Path) -> list[str]:
    errors = []
    if not _stage_is_ran(stage):
        errors.append('native stage missing, NOT_RUN, or wrong type')
        return errors
    argv = stage.get('argv')
    if argv != [str(tool_home / 'bin/verifast'), *NATIVE_ARGV[1:]]:
        errors.append('native argv differs from exact first-barrier command')
    if stage.get('stdout') != 'w4-first-barrier.log' or stage.get('stderr') != 'w4-first-barrier.log':
        errors.append('native stdout/stderr target differs from pinned diagnostic log')
    if facts.get('stage_record', {}).get('matches_stage') is not True:
        errors.append('physical native stage record missing or differs')
    if stage.get('fixture_before') != hashes or stage.get('fixture_after') != hashes or \
       stage.get('fixture_integrity') is not True:
        errors.append('native source-stage-target fixture binding differs')
    if type(stage.get('exit')) is not int or stage.get('exit') not in ALLOWED_NATIVE_EXITS:
        errors.append('native exit is outside raw diagnostic set 0/1/2')
    logs = facts.get('logs', {})
    for key in ('stdout', 'stderr'):
        log = logs.get(key)
        if not isinstance(log, dict) or log.get('missing_or_unsafe') is True or log.get('utf8_error'):
            errors.append(key + ' native log missing, unsafe, or not UTF-8')
    for rel, expected in hashes.items():
        path = evidence / CASE_REL / rel
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
            errors.append('physical native source fixture differs: ' + rel)
    return errors


def _initial_report(args: argparse.Namespace) -> dict[str, Any]:
    return {'schema': SCHEMA, 'complete': False, 'classification': 'INCOMPLETE_W4_LINKAGE_DIAGNOSTIC',
            'candidate': args.candidate, 'capture_complete': False, 'typed_call_inventory_complete': False,
            'verifier_invoked': False, 'actual_body_proof_status': 'UNKNOWN',
            'call_linkage': False, 'accepted': False, 'publication_allowed': False,
            'proof_credit': 0, 'independent_proof_credit': 0, 'runner_exit': None,
            'failed_stage': 'preflight', 'errors': [], 'artifact_inventory': []}


def _services(services: dict[str, Any] | None, cloud: Path):
    services = services or {}
    capture = services.get('capture') or _load(cloud / CAPTURE_HELPER_REL.name,
                                                'r24_w4_capture_frozen', CAPTURE_HELPER_SHA256)
    analyzer = services.get('analyzer') or _load(cloud / MIR_CALLS_REL.name,
                                                  'r24_w4_mir_calls', MIR_CALLS_SHA256)
    return capture, analyzer


def run(args: argparse.Namespace, *, services: dict[str, Any] | None = None) -> dict[str, Any]:
    repo, cloud, evidence, tool_home = _validate_context(args, fresh=True)
    output = evidence / SUMMARY_REL
    report = _initial_report(args)
    write_json(output, report)
    try:
        route = _validate_route()
        capture_mode = Path(args.capture_mode_file).resolve()
        mode_path = Path(args.mode_file).resolve()
        analyzer_path = cloud / MIR_CALLS_REL.name
        mode = _validate_mode(repo, mode_path, capture_mode, repo / CAPTURE_PINS_REL,
                              analyzer_path)
        report.update(route=route, mode_sha256=MODE_SHA256,
                      capture_mode_sha256=CAPTURE_MODE_SHA256,
                      capture_pins_sha256=CAPTURE_PINS_SHA256,
                      analyzer_sha256=MIR_CALLS_SHA256, tool_hashes=_tool_hashes(tool_home),
                      source_before=_source_state(repo))
        need(report['source_before'].get('intact') is True,
             'repository source differs before fresh capture')
        capture, analyzer = _services(services, cloud)
        capture_args = _capture_args(args, capture_mode)
        report['failed_stage'] = 'fresh-capture'
        write_json(output, report)
        capture_report = capture.collect(capture_args, stage_runner=(services or {}).get('capture_stage_runner'))
        report['capture'] = {'schema': capture_report.get('schema'), 'complete': capture_report.get('complete'),
                             'summary_path': (Path('cases/r24-w4-capture/W4-CAPTURE.json')).as_posix(),
                             'summary_sha256': digest((evidence / 'cases/r24-w4-capture/W4-CAPTURE.json').read_bytes())
                             if (evidence / 'cases/r24-w4-capture/W4-CAPTURE.json').is_file() else None}
        if capture_report.get('complete') is not True:
            report['errors'].append('frozen source/MIR capture incomplete')
            report['source_after'] = _source_state(repo)
            report['source_intact'] = report['source_after'] == report['source_before']
            report['tool_hashes_after'] = _tool_hashes(tool_home)
            return _finish(report, output, evidence, 4)
        need(capture_report.get('candidate') == args.candidate,
             'fresh capture candidate differs')
        pins = _load_json_pin(repo, CAPTURE_PINS_REL, CAPTURE_PINS_SHA256)
        _validate_capture_pins(capture_report, pins)
        report['capture_complete'] = True
        report['failed_stage'] = 'typed-mir-analysis'
        write_json(output, report)
        typed = _analyze(capture, analyzer, evidence, capture_report, pins)
        report['typed_call_inventory'] = typed
        report['typed_call_inventory_complete'] = typed.get('complete') is True
        if typed.get('complete') is not True:
            errors = typed.get('errors')
            report['errors'].extend(errors if isinstance(errors, list) and errors else
                                    ['typed MIR analyzer reported UNKNOWN/incomplete'])
        source_before = report['source_before']
        need(source_before.get('intact') is True, 'repository source differs before native diagnostic')
        native_root = evidence / CASE_REL
        hashes = _capture_source_files(evidence, capture_report, capture, native_root)
        report['native_source_hashes'] = hashes
        report['failed_stage'] = 'first-barrier'
        write_json(output, report)
        stage = _native_stage(capture, args, evidence, tool_home, hashes,
                              (services or {}).get('native_stage_runner'))
        facts = _native_facts(evidence, stage)
        report['native'] = facts
        report['verifier_invoked'] = facts['verifier_invoked']
        source_after = _source_state(repo)
        report['source_before'] = source_before
        report['source_after'] = source_after
        report['source_intact'] = source_after.get('intact') is True and source_after == source_before
        report['tool_hashes_after'] = _tool_hashes(tool_home)
        report['errors'].extend(_validate_native(evidence, stage, facts, hashes, tool_home))
        if report['source_intact'] is not True:
            report['errors'].append('repository source changed during diagnostic')
        if report['tool_hashes_after'] != report['tool_hashes']:
            report['errors'].append('qualified tool identity changed during diagnostic')
        complete = not report['errors']
        report['complete'] = complete
        report['classification'] = 'COMPLETE_RAW_W4_DIAGNOSTIC' if complete else 'INCOMPLETE_W4_LINKAGE_DIAGNOSTIC'
        report['failed_stage'] = 'complete' if complete else 'first-barrier'
        return _finish(report, output, evidence, 0 if complete else 4)
    except BaseException as exc:
        report['complete'] = False
        report['classification'] = 'INCOMPLETE_W4_LINKAGE_DIAGNOSTIC'
        report['runner_exit'] = 4
        report.setdefault('errors', []).append(type(exc).__name__ + ': ' + str(exc))
        if 'source_before' in report:
            try:
                report['source_after'] = _source_state(repo)
                report['source_intact'] = report['source_after'] == report['source_before']
            except BaseException as snapshot_exc:
                report['source_snapshot_error'] = type(snapshot_exc).__name__ + ': ' + str(snapshot_exc)
        if 'tool_hashes' in report:
            try:
                report['tool_hashes_after'] = _tool_hashes(tool_home)
            except BaseException as snapshot_exc:
                report['tool_snapshot_error'] = type(snapshot_exc).__name__ + ': ' + str(snapshot_exc)
        report['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                               'traceback': traceback.format_exc()}
        try:
            _finish(report, output, evidence, 4)
        except BaseException as write_exc:
            report['partial_write_error'] = type(write_exc).__name__ + ': ' + str(write_exc)
            try:
                write_json(output, report)
            except BaseException:
                pass
        raise


def _validate_capture_pins(report: dict[str, Any], pins: dict[str, Any]) -> None:
    source = report.get('source')
    need(isinstance(source, dict), 'fresh capture source record malformed')
    pinned_source = pins.get('source')
    need(isinstance(pinned_source, dict) and source.get('source_sha256') == pinned_source.get('source_sha256') == SOURCE_SHA256 and
         source.get('source_git_blob') == pinned_source.get('source_git_blob') ==
         '40939f922bcb6fdc7ee0d30427fa861827043827' and source.get('target') == pinned_source.get('target') == 'sort4_stable' and
         source.get('original_sha256') == pinned_source.get('original_sha256') and
         source.get('verified_sha256') == pinned_source.get('verified_sha256'),
         'fresh capture source identity differs')
    for key in ('normal', 'readonly'):
        mir = report.get('mir', {}).get(key) if isinstance(report.get('mir'), dict) else None
        pinned_mir = pins.get('mir', {}).get(key) if isinstance(pins.get('mir'), dict) else None
        need(isinstance(mir, dict) and isinstance(pinned_mir, dict) and
             mir.get('full_function_record_sha256') == pinned_mir.get('full_function_record_sha256') and
             mir.get('full_function_record') == pinned_mir.get('full_function_record'),
             key + ' full function MIR pin differs')
    need(report.get('tool_hashes') == pins.get('tool_hashes') == TOOL_HASHES,
         'fresh capture tool hash inventory differs')
    need(source.get('repository_source_unchanged') is True,
         'fresh capture did not observe repository source unchanged')


def _finish(report: dict[str, Any], output: Path, evidence: Path, runner_exit: int) -> dict[str, Any]:
    report['runner_exit'] = runner_exit
    report['accepted'] = False
    report['publication_allowed'] = False
    report['proof_credit'] = 0
    report['independent_proof_credit'] = 0
    report['call_linkage'] = False
    report['actual_body_proof_status'] = 'UNKNOWN'
    try:
        report['artifact_inventory'] = _inventory(evidence, output)
    except BaseException as exc:
        report['complete'] = False
        report['classification'] = 'INCOMPLETE_W4_LINKAGE_DIAGNOSTIC'
        report.setdefault('errors', []).append('artifact inventory: ' + type(exc).__name__ + ': ' + str(exc))
        report['runner_exit'] = 4
    write_json(output, report)
    return report


def _inventory(evidence: Path, output: Path) -> list[dict[str, Any]]:
    root = evidence / SUMMARY_REL.parent
    excluded = {output.resolve(), (evidence / AUDIT_REL).resolve()}
    inventory = []
    if root.exists():
        need(root.is_dir() and not root.is_symlink(), 'diagnostic artifact root unsafe')
        for path in sorted(root.rglob('*')):
            need(not path.is_symlink(), 'diagnostic artifact symlink: ' + str(path))
            if path.is_file() and path.resolve() not in excluded:
                raw = path.read_bytes()
                inventory.append({'path': path.relative_to(evidence).as_posix(),
                                  'bytes': len(raw), 'sha256': digest(raw)})
            elif not path.is_file() and not path.is_dir():
                need(False, 'diagnostic artifact is not a regular file: ' + str(path))
    return inventory


def audit(args: argparse.Namespace, *, services: dict[str, Any] | None = None) -> dict[str, Any]:
    repo, cloud, evidence, tool_home = _validate_context(args)
    output = Path(args.output).resolve() if args.output else evidence / AUDIT_REL
    need(output.is_relative_to(evidence) and not output.is_symlink(),
         'audit output must be a regular path under evidence')
    report = {'schema': SCHEMA + '-audit', 'evidence_complete': False, 'accepted': False,
              'publication_allowed': False, 'proof_credit': 0, 'runner_exit': args.runner_exit,
              'failed_stage': args.failed_stage, 'errors': []}
    write_json(output, report)
    try:
        capture_mode = Path(args.capture_mode_file).resolve()
        mode_path = Path(args.mode_file).resolve()
        capture, analyzer = _services(services, cloud)
        route = _validate_route()
        mode = _validate_mode(repo, mode_path, capture_mode, repo / CAPTURE_PINS_REL,
                              cloud / MIR_CALLS_REL.name)
        report['mode_sha256'] = MODE_SHA256
        report['tool_hashes'] = _tool_hashes(tool_home)
        capture_args = _capture_args(args, capture_mode)
        capture_args.output = str(evidence / 'W4-CAPTURE-AUDIT.json')
        capture_audit = capture.audit(capture_args)
        report['capture_audit'] = {'evidence_complete': capture_audit.get('evidence_complete'),
                                   'path': str(Path(capture_args.output).relative_to(evidence)),
                                   'sha256': digest(Path(capture_args.output).read_bytes())}
        summary_path = evidence / SUMMARY_REL
        need(summary_path.is_file() and not summary_path.is_symlink(), 'diagnostic summary missing')
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        need(isinstance(summary, dict) and summary.get('schema') == SCHEMA,
             'diagnostic summary schema differs')
        if args.runner_exit != 0 or args.failed_stage != 'complete':
            report['errors'].append('runner exit/stage does not report complete diagnostic')
        if summary.get('candidate') != args.candidate or summary.get('complete') is not True:
            report['errors'].append('summary candidate/completion differs')
        if summary.get('route') != route or summary.get('mode_sha256') != MODE_SHA256 or \
           summary.get('capture_mode_sha256') != CAPTURE_MODE_SHA256 or \
           summary.get('capture_pins_sha256') != CAPTURE_PINS_SHA256 or \
           summary.get('analyzer_sha256') != MIR_CALLS_SHA256:
            report['errors'].append('summary route or mode/dependency identity differs')
        if summary.get('tool_hashes') != TOOL_HASHES or summary.get('tool_hashes_after') != TOOL_HASHES:
            report['errors'].append('summary tool identity differs')
        if summary.get('accepted') is not False or summary.get('publication_allowed') is not False or \
           type(summary.get('proof_credit')) is not int or summary.get('proof_credit') != 0 or \
           summary.get('call_linkage') is not False or summary.get('actual_body_proof_status') != 'UNKNOWN':
            report['errors'].append('diagnostic-only boundary differs')
        if capture_audit.get('evidence_complete') is not True:
            report['errors'].append('frozen capture audit incomplete')
        if summary.get('verifier_invoked') is not True:
            report['errors'].append('summary does not report native diagnostic invocation')
        pins = _load_json_pin(repo, CAPTURE_PINS_REL, CAPTURE_PINS_SHA256)
        cap_path = evidence / 'cases/r24-w4-capture/W4-CAPTURE.json'
        cap_report = json.loads(cap_path.read_text(encoding='utf-8'))
        _validate_capture_pins(cap_report, pins)
        typed = _analyze(capture, analyzer, evidence, cap_report, pins)
        if typed != summary.get('typed_call_inventory'):
            report['errors'].append('typed MIR analysis changed since run')
        native = summary.get('native')
        stage = native.get('stage') if isinstance(native, dict) else None
        hashes = summary.get('native_source_hashes')
        facts = _native_facts(evidence, stage)
        if facts != native:
            report['errors'].append('native stage/log inventory changed since run')
        if not isinstance(hashes, dict):
            report['errors'].append('native source hash map missing')
            hashes = {}
        report['errors'].extend(_validate_native(evidence, stage, facts, hashes, tool_home))
        source_before, source_after = summary.get('source_before'), _source_state(repo)
        if source_before != source_after or summary.get('source_after') != source_after or \
           summary.get('source_intact') is not True:
            report['errors'].append('physical repository source changed since run')
        current_hashes = _tool_hashes(tool_home)
        if current_hashes != summary.get('tool_hashes') or current_hashes != summary.get('tool_hashes_after'):
            report['errors'].append('physical qualified tool identity differs')
        if _inventory(evidence, summary_path) != summary.get('artifact_inventory'):
            report['errors'].append('physical diagnostic artifact inventory differs')
        report['evidence_complete'] = not report['errors']
        report['summary_path'] = SUMMARY_REL.as_posix()
        report['summary_sha256'] = digest(summary_path.read_bytes())
    except BaseException as exc:
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        report['exception'] = {'type': type(exc).__name__, 'message': str(exc)}
    write_json(output, report)
    return report


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    subs = top.add_subparsers(dest='command', required=True)
    for cmd in ('run', 'audit'):
        p = subs.add_parser(cmd)
        for name in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'schema', 'compiler-sysroot',
                     'capture-mode-file', 'mode-file', 'candidate'):
            p.add_argument('--' + name, required=True)
        if cmd == 'run':
            p.add_argument('--deadline-epoch', required=True, type=int)
        else:
            p.add_argument('--output')
            p.add_argument('--runner-exit', required=True, type=int)
            p.add_argument('--failed-stage', required=True)
    return top


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run(args) if args.command == 'run' else audit(args)
        if args.command == 'run':
            return 0 if result.get('complete') is True else 4
        return 0 if result.get('evidence_complete') is True else 4
    except BaseException:
        if isinstance(sys.exc_info()[1], (KeyboardInterrupt, SystemExit)):
            raise
        print('R24-W4-LINKAGE-DIAGNOSTIC: incomplete; see partial record', file=sys.stderr)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
