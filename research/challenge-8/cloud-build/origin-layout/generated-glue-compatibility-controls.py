#!/usr/bin/env python3
"""Cloud-only exact-refiner compatibility controls for the v8 Drop glue route.

The module is inert on import.  Its caller supplies a successful captured v8
case and the hosted stage runner.  Decoded MIR mutations never become source
or proof evidence; each replay is tied to copied original binary exports.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
METHOD = '<CopyOnDrop as core::ops::Drop>::drop'
SUCCESS = 'No refinement errors found'
MISSING = 'Return local has no value in the refinement environment'
PINNED_REFINER_SOURCE_SHA256_BY_PROFILE = {
    'experimental-merge-actual-glue-body-v8':
        'e232312e5f24ca98e25fe32fe0be5300eca4deda69438af2ebf90985061b3dc8',
    'experimental-merge-guard-addressability-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-guard-addressability-emitter-r5-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-late-callback-recovery-r7-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-owned-array-allocation-r8-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-guard-current-return-r9-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-moving-gap-r10-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
    'experimental-merge-label-storage-r11-v1':
        'd20a433c93563b87ff0a48241c94e366df06dba2f87b5e7f85ba47edb6980dd1',
}
LEGACY_DROP_DEFAULTS = (
    'kind=Drop {\n'
    '              selected_drop_path=""; selected_drop_hash=""; selected_guard_path="";\n'
    '              is_bare_local=false; is_replace=false; generated_body_key="";'
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_admission():
    path = HERE / 'generated-glue-admission-controls.py'
    spec = importlib.util.spec_from_file_location('compat_admission_helpers', path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'missing admission helpers: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _method(text: str) -> tuple[int, int, str]:
    anchor = f'      defPath = "{METHOD}",'
    if text.count(anchor) != 1:
        raise ValueError('ordinary selected Drop body is absent or nonunique')
    start = text.index(anchor)
    end = text.find('\n      defPath = ', start + len(anchor))
    if end < 0:
        raise ValueError('cannot bound ordinary selected Drop body')
    return start, end, text[start:end]


def _remove_return_assignment(body: str) -> str:
    """Delete the unique MIR statement assigning the ordinary unit return."""
    target = 'local = (name = "_0")'
    if body.count(target) != 1:
        raise ValueError('ordinary body must assign _0 exactly once')
    at = body.index(target)
    start = body.rfind('( sourceInfo = (', 0, at)
    if start < 0:
        raise ValueError('cannot find _0 statement boundary')
    depth = 0
    quoted = False
    escaped = False
    end = None
    for i in range(start, len(body)):
        ch = body[i]
        if quoted:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None or body[end:].lstrip()[:1] != ']':
        raise ValueError('_0 assignment must be last MIR statement')
    comma = start - 1
    while comma >= 0 and body[comma].isspace():
        comma -= 1
    if body[comma] != ',':
        raise ValueError('missing preceding statement separator')
    result = body[:comma] + body[end:]
    if target in result:
        raise ValueError('_0 assignment removal incomplete')
    return result


def _ordinary_mutant(text: str, nonunit: bool, remove: bool) -> str:
    start, end, body = _method(text)
    if remove:
        body = _remove_return_assignment(body)
    if nonunit:
        # Both output and local _0 must change together so the test reaches
        # the return-value rule rather than a signature/layout setup failure.
        old = 'ty = (kind = (tuple = []))'
        if body.count(old) < 1:
            raise ValueError('ordinary unit _0 type absent')
        body = body.replace(old, 'ty = (kind = (uInt = (u64 = void)))', 1)
        old = 'output = (kind = (tuple = []))'
        if body.count(old) != 1:
            raise ValueError('ordinary unit output absent or nonunique')
        body = body.replace(old, 'output = (kind = (uInt = (u64 = void)))', 1)
    return text[:start] + body + text[end:]


def _synthetic_defaults_gate(source: Path, refiner: Path, profile: str) -> dict:
    """Bind both old Box Drop constructors to exact source and built binary."""
    content = source.read_text()
    count = content.count(LEGACY_DROP_DEFAULTS)
    total = content.count('kind=Drop {')
    expected = PINNED_REFINER_SOURCE_SHA256_BY_PROFILE.get(profile)
    row = {'profile': profile, 'source_path': str(source), 'source_sha256': _sha(source),
           'expected_source_sha256': expected,
           'refiner_sha256': _sha(refiner), 'synthetic_drop_count': total,
           'explicit_unqualified_default_count': count,
           'classification': 'STATIC_SOURCE_COMPATIBILITY_ONLY_NO_PROOF_CREDIT'}
    row['matched'] = (expected is not None and row['source_sha256'] == expected and
                      total == 2 and count == 2)
    return row


def _ordinary_default_off(evidence: Path, args, env: dict[str, str], base) -> dict:
    """Cloud frontend smoke for an unqualified ordinary Rust Drop terminator."""
    case = evidence / 'ordinary-default-off'
    (case / 'original').mkdir(parents=True)
    (case / 'verified').mkdir()
    fixture = (
        'pub struct OrdinaryDrop(*mut u64);\n'
        'impl Drop for OrdinaryDrop {\n'
        '    fn drop(&mut self) { unsafe { *self.0 = 1; } }\n'
        '}\n'
        'pub fn ordinary_drop(ptr: *mut u64) {\n'
        '    let _guard = OrdinaryDrop(ptr);\n'
        '}\n')
    for side in ('original', 'verified'):
        (case / side / 'lib.rs').write_text(fixture)
    source_sha = _sha(case / 'verified/lib.rs')
    child_env = dict(env)
    for flag in ('SMALLSORT_ACTUAL_GLUE_BODY', 'SMALLSORT_DROP_RECEIVER_CONTROL',
                 'SMALLSORT_GLUE_OBSERVATION_DIR'):
        child_env.pop(flag, None)
    exporter = base.run_stage(case, 'ordinary-exporter', [
        str(Path(args.tool_home) / 'bin/vf-rust-mir-exporter'), 'verified/lib.rs',
        f'--sysroot={args.compiler_sysroot}', '--edition', '2021',
        '--crate-type', 'lib', '--vf-rust-mir-exporter:preprocess-readonly'],
        child_env, timeout_seconds=args.stage_seconds,
        stdout_name='ordinary-compiler-mir.bin')
    row = {'classification': 'DEFAULT_OFF_FRONTEND_COMPATIBILITY_ONLY_NO_PROOF_CREDIT',
           'fixture_source_sha256': source_sha,
           'source_sha256_after': _sha(case / 'verified/lib.rs'),
           'exporter_sha256': _sha(Path(args.tool_home) / 'bin/vf-rust-mir-exporter'),
           'verifier_sha256': _sha(Path(args.tool_home) / 'bin/verifast'),
           'exporter_exit_code': exporter, 'generated_flag_absent':
           'SMALLSORT_ACTUAL_GLUE_BODY' not in child_env}
    if exporter:
        row['matched'] = False
        row['stage'] = 'EXPORTER_SETUP_FAILURE'
        return row
    include_dirs = list(dict.fromkeys([Path(args.schema).parent, *getattr(args, "capnp_include", ())]))
    decode_args = ['capnp', 'decode']
    for directory in include_dirs:
        decode_args.extend(['-I', str(directory)])
    decode_args.extend([str(args.schema), 'VfMir'])
    decoder = base.run_stage(case, 'ordinary-decode', decode_args, child_env,
                             timeout_seconds=args.stage_seconds,
                             stdin=case / 'ordinary-compiler-mir.bin',
                             stdout_name='ordinary-decode.out')
    row['decoder_exit_code'] = decoder
    if decoder:
        row['matched'] = False
        row['stage'] = 'DECODE_SETUP_FAILURE'
        return row
    decoded = (case / 'ordinary-decode.out').read_text()
    row['decoded_sha256'] = _sha(case / 'ordinary-decode.out')
    row['ordinary_drop_mir_present'] = ('defPath = "ordinary_drop"' in decoded and
                                        'drop = (' in decoded)
    row['no_generated_body'] = ('defPath = "__vf_generated_drop_glue"' not in decoded and
                                'enabled = true' not in decoded)
    row['no_generated_drop_reference'] = 'generatedBodyKey = "__vf_generated_drop_glue"' not in decoded
    verifier = base.run_stage(case, 'ordinary-verifast', [
        str(Path(args.tool_home) / 'bin/verifast'), '-rustc_args', '--edition 2021',
        '-verbose', '1', '-dump_ast_with_locs', 'ordinary-proof-ast.ml',
        'verified/lib.rs'], child_env, combine=True,
        timeout_seconds=args.verifier_seconds)
    row['verifier_exit_code'] = verifier
    ast_path = case / 'ordinary-proof-ast.ml'
    if ast_path.is_file():
        parser_path = HERE.parents[1] / 'merge/overnight/stack-proof-ast-admission.py'
        spec = importlib.util.spec_from_file_location('ordinary_drop_compat_ast', parser_path)
        if spec is None or spec.loader is None:
            raise RuntimeError('AST parser unavailable for ordinary Drop control')
        parser = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = parser
        spec.loader.exec_module(parser)
        tree = parser.OcamlAstText(ast_path.read_text(errors='replace')).parse()
        functions = [node for node in parser.nodes(tree, 'Func')
                     if len(node.args) == 13 and node.args[4] == 'ordinary_drop']
        calls = [node.args[1] for function in functions
                 for node in parser.nodes(function, 'CallExpr')
                 if len(node.args) == 6 and isinstance(node.args[1], str)]
        row['ordinary_ast_function_count'] = len(functions)
        row['ordinary_drop_in_place_call_count'] = calls.count('std::ptr::drop_in_place')
        row['generated_call_count'] = calls.count('__vf_generated_drop_glue')
        row['receiver_rewrite_call_count'] = sum(calls.count(name) for name in
                                                 ('create_ref_mut', 'end_ref_mut'))
        row['ast_sha256'] = _sha(ast_path)
    row['matched'] = (row['generated_flag_absent'] and
                      row['fixture_source_sha256'] == row['source_sha256_after'] and
                      row['ordinary_drop_mir_present'] and row['no_generated_body'] and
                      row['no_generated_drop_reference'] and
                      row.get('ordinary_ast_function_count') == 1 and
                      row.get('ordinary_drop_in_place_call_count', 0) >= 1 and
                      row.get('generated_call_count') == 0 and
                      row.get('receiver_rewrite_call_count') == 0)
    row['stage'] = 'ORDINARY_DEFAULT_OFF_AST_COMPATIBILITY' if row['matched'] else 'WRONG_OR_MISSING_AST_ROUTE'
    return row


def run(evidence: Path, args, env: dict[str, str], base, positive_case: Path) -> dict:
    """Replay captured exports through a byte-identical copied official refiner."""
    evidence = Path(evidence)
    positive_case = Path(positive_case)
    if evidence.exists():
        raise FileExistsError(f'refusing to reuse compatibility evidence: {evidence}')
    evidence.mkdir(parents=True)
    admission = _load_admission()
    capture_dir = evidence.parent / 'admission-controls/refiner-export-capture'
    admission_receipt_path = evidence.parent / 'admission-controls/receipt.json'
    if not admission_receipt_path.is_file():
        raise FileNotFoundError('successful same-campaign admission capture receipt is required')
    admission_receipt = json.loads(admission_receipt_path.read_text())
    capture_row = admission_receipt.get('official_refiner_export_capture', {})
    if capture_row.get('matched') is not True:
        raise RuntimeError('official refiner export capture was not qualified')
    files = {
        'original_source': positive_case / 'original/lib.rs',
        'verified_source': positive_case / 'verified/lib.rs',
        'original_raw': capture_dir / 'original-refiner-export.bin',
        'verified_raw': capture_dir / 'verified-refiner-export.bin',
        'original_decoded': capture_dir / 'sources/original-refiner-decode.out',
        'verified_decoded': capture_dir / 'sources/verified-refiner-decode.out',
    }
    for name, path in files.items():
        if not path.is_file():
            raise FileNotFoundError(f'{name}: {path}')
    refiner = Path(args.tool_home) / 'bin/refinement-checker'
    capnp = shutil.which('capnp')
    if capnp is None or not refiner.is_file():
        raise FileNotFoundError('hosted capnp and official refiner are required')
    source_gate = _synthetic_defaults_gate(
        Path(args.tool_home) / 'src/refinement_checker/refinement_checker.ml', refiner, args.profile)
    gate_case = evidence / 'source-compatibility' / 'cases' / 'legacy_synthetic_drop_defaults'
    gate_case.mkdir(parents=True)
    (gate_case / 'classification.json').write_text(json.dumps({
        'case': 'legacy_synthetic_drop_defaults', 'profile': args.profile,
        'classification': 'STATIC_SOURCE_COMPATIBILITY_ONLY_NO_PROOF_CREDIT',
        'accepted': False, 'proof_credit': False, 'source_gate': source_gate,
    }, indent=2) + '\n')
    if not source_gate['matched']:
        raise RuntimeError(f'legacy synthetic Drop defaults changed: {source_gate}')
    if capture_row.get('refiner_sha256') != _sha(refiner) or any(
            capture_row.get('raw_sha256', {}).get(side) != _sha(files[side + '_raw'])
            for side in ('original', 'verified')):
        raise RuntimeError('admission capture no longer matches pinned refiner or raw exports')
    receipt = {
        'schema': 'generated-glue-compatibility-controls-v1',
        'classification': 'REFINER_COMPATIBILITY_ONLY_NO_PROOF_CREDIT',
        'profile': args.profile,
        'inputs_sha256': {key: _sha(path) for key, path in files.items()},
        'refiner_sha256': _sha(refiner),
        'schema_sha256': _sha(Path(args.schema)),
        'capnp_sha256': _sha(Path(capnp)),
        'legacy_synthetic_drop_defaults': source_gate,
        'admission_capture_receipt_sha256': _sha(admission_receipt_path),
        'cases': {},
    }
    temp = evidence / 'messages'
    temp.mkdir()
    original = files['original_decoded'].read_text()
    verified = files['verified_decoded'].read_text()

    def encode(name: str, content: str) -> Path:
        path = temp / f'{name}.bin'
        with path.open('wb') as output:
            result = subprocess.run([capnp, 'encode', '-I', str(Path(args.schema).parent),
                                     str(args.schema), 'VfMir'], input=content, text=True,
                                    stdout=output, stderr=subprocess.PIPE,
                                    cwd=positive_case, env=env, check=False)
        if result.returncode or not path.stat().st_size:
            raise RuntimeError(f'{name}: capnp encode failed: {result.stderr!r}')
        return path

    def invoke(name: str, orig: Path, ver: Path) -> dict:
        case = evidence / name
        case.mkdir()
        bin_dir = case / 'bin'
        bin_dir.mkdir()
        copied = bin_dir / 'refinement-checker'
        shutil.copy2(refiner, copied)
        copied.chmod(copied.stat().st_mode | 0o111)
        if _sha(copied) != receipt['refiner_sha256']:
            raise RuntimeError('official refiner copy changed')
        _, wrapper_sha = admission._write_wrapper(bin_dir, orig, ver)
        sources = case / 'sources'
        (sources / 'original').mkdir(parents=True)
        (sources / 'verified').mkdir()
        shutil.copy2(files['original_source'], sources / 'original/lib.rs')
        shutil.copy2(files['verified_source'], sources / 'verified/lib.rs')
        before = {side: _sha(sources / side / 'lib.rs') for side in ('original', 'verified')}
        child_env = dict(env)
        child_env['PATH'] = str(bin_dir) + os.pathsep + child_env.get('PATH', '')
        code = base.run_stage(sources, 'official-refinement', [str(copied), '--rustc-args',
                              '--edition 2021', 'original/lib.rs', 'verified/lib.rs'],
                              child_env, timeout_seconds=args.stage_seconds)
        log = ''.join((sources / filename).read_text(errors='replace')
                      for filename in ('official-refinement.log', 'official-refinement.out')
                      if (sources / filename).exists())
        (case / 'official-log.txt').write_text(log)
        after = {side: _sha(sources / side / 'lib.rs') for side in ('original', 'verified')}
        return {'exit_code': code, 'log_sha256': _sha(case / 'official-log.txt'),
                'original_message_sha256': _sha(orig), 'verified_message_sha256': _sha(ver),
                'copied_refiner_sha256': _sha(copied), 'wrapper_sha256': wrapper_sha,
                'sources_unchanged': before == after, 'log': log}

    # The raw and re-encoded baselines establish that this argv-checked replay
    # reaches the same successful official-refiner path as the captured case.
    encoded_original = encode('pristine-original', original)
    encoded_verified = encode('pristine-verified', verified)
    for name, orig, ver in (
        ('raw_baseline', files['original_raw'], files['verified_raw']),
        ('encoded_baseline', encoded_original, encoded_verified),
    ):
        row = invoke(name, orig, ver)
        row['matched'] = row['exit_code'] == 0 and SUCCESS in row['log'] and row['sources_unchanged']
        row.pop('log')
        receipt['cases'][name] = row
        if not row['matched']:
            receipt['all_matched'] = False
            receipt['status'] = 'BASELINE_FAILED'
            (evidence / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            return receipt

    mutations = {
        'ordinary_unit_missing_0': (
            _ordinary_mutant(original, False, True),
            _ordinary_mutant(verified, False, True), MISSING),
        'ordinary_nonunit_missing_0': (
            _ordinary_mutant(original, True, True),
            _ordinary_mutant(verified, True, True), MISSING),
        'ordinary_present_absent_0': (
            original, _ordinary_mutant(verified, False, True), MISSING),
    }
    for name, (orig_text, ver_text, expected) in mutations.items():
        row = invoke(name, encode(name + '-original', orig_text),
                     encode(name + '-verified', ver_text))
        row['expected_message'] = expected
        row['matched'] = row['exit_code'] != 0 and expected in row['log'] and row['sources_unchanged']
        row.pop('log')
        receipt['cases'][name] = row

    # Binding the call result to _0 on one side would populate its return
    # environment, but the generated-body shape gate must refuse it first.
    # This outcome is useful evidence of scope and is not Return-rule credit.
    generated_mismatch = admission._generated_body(
        verified,
        'destination = (\n                  local = (name = "_3"),',
        'destination = (\n                  local = (name = "_0"),',
        'generated populated return destination')
    row = invoke('generated_present_absent_0', encoded_original,
                 encode('generated-present-absent-verified', generated_mismatch))
    shape_message = 'Generated DropGlue: verified call operands, destination, target, or unwind differ'
    row['expected_earlier_message'] = shape_message
    row['earlier_gate_matched'] = (row['exit_code'] != 0 and shape_message in row['log'] and
                                  row['sources_unchanged'])
    row.pop('log')
    receipt['cases']['generated_present_absent_0'] = row
    receipt['generated_present_absent_0'] = {
        'qualified': False,
        'stage': 'PRE_RETURN_GENERATED_SHAPE_GATE',
        'reason': 'generated call destination must be _3, return block empty, and both MIR bodies equal',
    }
    receipt['executed_controls_matched'] = (
        all(receipt['cases'][name]['matched'] for name in mutations) and
        row['earlier_gate_matched'])
    receipt['default_off_ordinary_drop'] = _ordinary_default_off(evidence, args, env, base)
    # Generated Some/None is intentionally classified at its mandatory
    # earlier shape gate. Never relabel this as a direct Return comparison.
    receipt['all_matched'] = (receipt['executed_controls_matched'] and
                              receipt['default_off_ordinary_drop']['matched'] and
                              source_gate['matched'])
    receipt['status'] = ('COMPATIBILITY_CONTROLS_MATCHED_WITH_EARLIER_GENERATED_GATE'
                         if receipt['all_matched'] else 'COMPATIBILITY_CONTROL_FAILURES')
    (evidence / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt
