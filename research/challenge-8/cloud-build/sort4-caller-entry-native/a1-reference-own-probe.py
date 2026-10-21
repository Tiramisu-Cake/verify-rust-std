"""Cloud-only faithful generic reference-own body probe and resource controls.

No variant is a caller receipt or matrix admission. Imports are inert.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Mapping

PHASE = 'SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13'
SPEC = 'bin/rust/rust_belt/general.rsspec'


def need(ok, reason):
    if not ok:
        raise RuntimeError('A1-REFERENCE-OWN: ' + reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def variants(fixtures, ghost):
    """Pure source assembly; no extractor, preparation, compiler or verifier."""
    own = 'std::option::Option_own'
    start = "/*@\nlem a1_cleanup_option_ref<'a, T>"
    token = 'thread_token(?t)'
    block = lambda params, pre, post, body: (start + params + '\n    req ' + pre +
        ';\n    ens ' + post + ';\n{\n' + body + '\n}\n@*/\n').encode()
    open_ref = "open shared_ref_type_own::<'a, T>()(t, r);"
    close_ref = "close shared_ref_type_own::<'a, T>()(t, r);"
    generic_body = f'    open {own}::<T>(t, value);\n    match value {{\n        Option::None => {{}}\n        Option::Some(r) => {{}}\n    }}'
    roundtrip_body = (f"    open {own}::<&'a T>(t, value);\n    match value {{\n"
        f"        Option::None => {{}}\n        Option::Some(r) => {{ {open_ref} {close_ref} }}\n    }}\n"
        f"    close {own}::<&'a T>(t, value);")
    some_pre = f"{token} &*& {own}::<&'a T>(t, Option::Some(r))"
    some_body = f"    open {own}::<&'a T>(t, Option::Some(r));\n    {open_ref}"
    sources = {
        'helper': (fixtures.OPTION_CLEANUP_LEMMA, 'ref', None),
        'some-preserve': (block("(r: &'a T)", some_pre,
            "thread_token(t) &*& [_](<T>.share)('a, t, r)", some_body), 'ref', None),
        'ref-roundtrip': (block("(value: std::option::Option<&'a T>)",
            f"{token} &*& {own}::<&'a T>(t, value)",
            f"thread_token(t) &*& {own}::<&'a T>(t, value)", roundtrip_body), 'ref', None),
        'generic-roundtrip': (block('(value: std::option::Option<T>)',
            f'{token} &*& {own}::<T>(t, value)',
            f'thread_token(t) &*& {own}::<T>(t, value)',
            generic_body + f'\n    close {own}::<T>(t, value);'), 'generic', None),
        'negative-generic-erasure': (block('(value: std::option::Option<T>)',
            f'{token} &*& {own}::<T>(t, value)', 'thread_token(t)', generic_body),
            'generic', 'Function leaks heap chunks: own(T_typeid)'),
        'negative-mutable-erasure': (block("(value: std::option::Option<&'a mut T>)",
            f"{token} &*& {own}::<&'a mut T>(t, value)", 'thread_token(t)',
            generic_body.replace('::<T>', "::<&'a mut T>")), 'mut',
            'Function leaks heap chunks: own(ref_mut_typeid('),
        'negative-lifetime-redirect': (block("(r: &'a T)", some_pre,
            "thread_token(t) &*& [_](<T>.share)('static, t, r)", some_body), 'ref',
            "No matching heap chunks: [_]share(T_typeid)(lft_of('static_typeid), t, r)"),
    }
    result = {}
    for name, (lemma, kind, failure) in sources.items():
        anchor_type = {'ref': "&'a T", 'generic': 'T', 'mut': "&'a mut T"}[kind]
        anchor = (f"\npub fn reference_own_anchor<'a, T>(value: std::option::Option<{anchor_type}>) {{ let _ = value; }}\n").encode()
        source = fixtures.OPTION_CLEANUP_IMPORT + lemma + anchor
        original = ghost.strip_ghost(source)
        lines = source.splitlines(keepends=True)
        lo = next(i for i, x in enumerate(lines, 1) if x == b'/*@\n')
        end = next(i for i, x in enumerate(lines, 1) if x == b'@*/\n')
        meta = {'name': 'a1_cleanup_option_ref', 'kind': 'lemma',
                'source_start_line': lo, 'source_end_line': end,
                'body_start_line': lo + 1, 'body_end_line': end - 1,
                'source_sha256': sha(lemma), 'source_bytes_sha256': sha(lemma)}
        need(source != original and b'Option::Some' in lemma, 'faithful source assembly')
        result[name] = {'source': source, 'original': original, 'metadata': meta,
                        'expected_failure': failure, 'source_sha256': sha(source),
                        'original_sha256': sha(original)}
    return result


def classify(stage, log, ast_selection, case):
    """Strict terminal/resource classification; no inference from missing rows."""
    bad = {'status': 'INCONCLUSIVE', 'passed': False, 'proof_credit': False}
    if not isinstance(stage, Mapping) or stage.get('classification') != 'TERMINAL':
        return {**bad, 'reason': 'nonterminal or missing stage'}
    if type(stage.get('exit')) is not int or not isinstance(log, bytes) or stage.get('log_sha256') != sha(log):
        return {**bad, 'reason': 'missing or mismatched terminal exit/log'}
    if not isinstance(ast_selection, Mapping) or ast_selection.get('classification') != 'ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA':
        return {**bad, 'reason': 'manual source-bound helper AST missing'}
    text = log.decode('utf-8', errors='replace')
    diagnostics = [line for line in text.splitlines() if ': error:' in line or 'Parse error' in line or line.startswith(('Fatal error:', 'error:', 'error['))]
    expected = case['expected_failure']
    if expected is None:
        passed = stage['exit'] == 0 and not diagnostics
    else:
        meta = case['metadata']
        # A resource refusal must belong to this lemma's pre/post/body interval.
        matching = [line for line in diagnostics if ': error:' in line and line.split(': error:', 1)[1].strip().startswith(expected) and
            (m := re.search(r'verified/lib\.rs\(([0-9]+),[^)]*\): error:', line)) and
            meta['body_start_line'] <= int(m[1]) <= meta['body_end_line']]
        passed = stage['exit'] == 1 and len(diagnostics) == 1 and len(matching) == 1
    return {'status': ('BODY_VERIFIED' if expected is None else 'EXPECTED_RESOURCE_REJECTION') if passed else 'INCONCLUSIVE',
            'passed': passed, 'observed_exit': stage['exit'], 'diagnostics': diagnostics,
            'expected_failure': expected, 'proof_credit': False}


def run(a, c4, tool, receipt, profile, fixtures, ghost, ast_gates, selector,
        grammar, checkpoint):
    identity = grammar._profile_guard(a, profile, receipt, tool)
    need(identity['authorization_phase_id'] in (PHASE, 'SORT4-NATIVE-P1-MATRIX-2026-10-21-R14', 'SORT4-ACTUAL-BODY-2026-10-21-R15', 'SORT4-ACTUAL-LIFETIME-2026-10-21-R16') and profile.get('execution_mode') in ('reference-own-probe', 'native-p1-target', 'full-matrix', 'actual-sort4-body-v1'), 'exact diagnostic mode')
    normalization = profile.get('shared_reference_own_normalization')
    need(isinstance(normalization, dict) and normalization == receipt.get('shared_reference_own_normalization') and
         normalization.get('source') == SPEC and sha((tool / SPEC).read_bytes()) == normalization.get('result_sha256'),
         'normalized source/receipt/profile identity')
    source_cases = variants(fixtures, ghost)
    env = c4.clean_env(a, tool)
    need(isinstance(env, dict) and not any(k.startswith(('SORT4_A1_', 'O26_WITH_')) for k in env), 'minimal environment omits summaries')
    need(env.get('RUSTUP_TOOLCHAIN') == profile['compiler_toolchain'], 'compiler identity')
    root = Path(a.evidence) / 'a1-reference-own-probe'
    need(not root.exists() and str(root.resolve()).startswith('/workspace/'), 'fresh workspace root')
    root.mkdir(parents=True)
    report = {'schema': 'a1-reference-own-probe-v1', **identity,
              'normalization': normalization, 'variants': {}, 'passed': False,
              'proof_credit': False, 'caller_receipt': False, 'matrix_admission': False}
    for name, case in source_cases.items():
        unit = root / name
        fixture = unit / 'fixture'
        for directory, raw in (('verified', case['source']), ('original', case['original'])):
            target = fixture / directory / 'lib.rs'
            target.parent.mkdir(parents=True)
            target.write_bytes(raw)
        stage_root = unit / 'stage'
        stage_root.mkdir()
        ast_path = stage_root / 'proof-ast.ml'
        row = {'source_sha256': case['source_sha256'], 'original_sha256': case['original_sha256'],
               'metadata': case['metadata'], 'status': 'INCONCLUSIVE', 'passed': False, 'proof_credit': False}
        try:
            stage = c4.stage(a, stage_root, 'reference-own', [str(tool / 'bin/verifast'),
                '-focus', f"verified/lib.rs:{case['metadata']['body_start_line']}",
                '-dump_ast_with_locs', str(ast_path), '-rustc_args', '--edition 2021',
                '-verbose', '6', 'verified/lib.rs'], env, 120, cwd=fixture)
            row['stage'] = stage
            log_path = stage_root / 'reference-own.log'
            log = log_path.read_bytes() if log_path.is_file() else None
            row['log_sha256'] = sha(log) if log is not None else None
            row['ast_sha256'] = sha(ast_path.read_bytes()) if ast_path.is_file() else None
            selected = selector(ast_path.read_text(), ast_gates, case['source'], case['metadata']) if ast_path.is_file() else None
            row['ast_selection'] = selected
            row.update(classify(stage, log, selected, case))
        except Exception as exc:
            row.update(error_type=type(exc).__name__, error=str(exc))
        try:
            row['same_tool_after_stage'] = (grammar._tool_hashes(tool) == identity['tool_hashes'] and sha((tool / SPEC).read_bytes()) == normalization['result_sha256'])
        except Exception as exc:
            row['same_tool_after_stage'] = False
            row['post_stage_identity_error'] = f'{type(exc).__name__}: {exc}'
        if not row['same_tool_after_stage']:
            row.update(status='INCONCLUSIVE', passed=False)
        report['variants'][name] = row
        # Compact snapshots only; stages retain their own separate bounded records.
        tmp = root / '.probe-audit.tmp'
        tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        os.replace(tmp, root / 'probe-audit.json')
        checkpoint('reference-own-' + name + '-observed')
    report['passed'] = len(report['variants']) == len(source_cases) and all(row['passed'] for row in report['variants'].values())
    tmp = root / '.probe-audit.tmp'
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, root / 'probe-audit.json')
    return report
