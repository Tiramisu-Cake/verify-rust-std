#!/usr/bin/env python3
"""Cloud-only provenance and verdict audit for the blocked first-scope TEST."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path('research/challenge-8')
MANIFEST = ROOT / 'overnight-callback/ACTUAL-SORT4-AST-SCOPE-TEST.json'
PATCH = ROOT / 'overnight-callback/verifast-actual-sort4-first-scope-TEST.patch'
TRANSLATOR = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
KERNEL = 'src/verifast.ml'
SOURCE = 'fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9'
ORIGINAL = '3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72'
AST = 'dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39'
FIRST = 'verified/lib.rs(185,13-36): error: No such function: __vf_sort4_first_unwind'
STRICT_OPT_IN = 'Strict lifetime binding requires explicit overnight opt-in'
RELEASE_STATUS = 'cloud_test_reviewed_unaccepted_default_off'
RELEASE_RESULT = 'reviewed_for_isolated_cloud_test'
CASES = ('positive_basic', 'ordinary_unmarked', 'positive_early_return',
         'positive_direct_unwind', 'negative_wrong_marker',
         'negative_duplicate_marker', 'negative_marker_outside_binding',
         'negative_unknown_binding', 'negative_nested_marker',
         'negative_malformed_marker', 'negative_type_name_after_cut',
         'negative_type_argument_after_cut', 'negative_typed_chunk_survives_cut',
         'negative_unclosed_fractional_access',
         'negative_reserved_half_after_lifetime_end',
         'negative_end_lifetime_twice', 'opt-in-absent')
OPEN_GATES = (
    'strict CUT and false-post raw first-obligation review is only a TEST release',
    'actual AST source, node corruption and default-off controls',
    'all-path lifetime liveness, CFG ingress, and scope/alias escape negatives',
    'heap, bound, pointer provenance, validity, initialization and leak retention',
    'no-cut and combined S6 regression',
    'full destination initialization, unrestricted generic and ZST contracts',
    'separate functional permutation, order and stability composition',
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def read(path: Path) -> dict:
    need(path.is_file(), f'missing evidence: {path}')
    value = json.loads(path.read_text())
    need(isinstance(value, dict), f'evidence is not a record: {path}')
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(('git', '-C', str(root), *args))


def snapshot(root: Path, proof: Path) -> dict:
    names = git(root, 'diff', '--name-only', 'HEAD').decode().splitlines()
    critical = (KERNEL, TRANSLATOR,
                'src/rust_frontend/vf_mir_translator/rust_parser.ml',
                'src/rust_frontend/vf_mir/vf_mir.capnp')
    binaries = ('bin/verifast', 'bin/vf-rust-mir-exporter',
                'bin/refinement-checker', 'bin/vf-cxx-ast-exporter',
                'bin/libz3.so')
    std = ('library/core/src/hint.rs', 'library/core/src/intrinsics/mod.rs',
           'library/core/src/mem/manually_drop.rs',
           'library/core/src/mem/maybe_dangling.rs',
           'library/core/src/mem/maybe_uninit.rs',
           'library/core/src/mem/mod.rs', 'library/core/src/ptr/mod.rs',
           'library/core/src/ptr/mut_ptr.rs',
           'library/core/src/slice/sort/shared/smallsort.rs')
    return {
        'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
        'tracked_diff_sha256': hashlib.sha256(git(root, 'diff', '--binary', 'HEAD')).hexdigest(),
        'modified_names': names,
        'modified_hashes': {name: sha(root / name) for name in names},
        'critical': {name: sha(root / name) for name in critical},
        'effective_rsspec': {str(p.relative_to(root)): sha(p)
                             for p in sorted((root / 'bin/rust').rglob('*.rsspec'))},
        'binaries': {name: sha(root / name) for name in binaries},
        'proof_std': {name: sha(proof / name) for name in std},
    }


def load_module(path: Path, label: str):
    spec = importlib.util.spec_from_file_location(label, path)
    need(spec is not None and spec.loader is not None, f'missing module {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def first_error(log: str) -> str | None:
    for line in log.splitlines():
        if ': error:' in line or line.startswith('Fatal error:'):
            return line
    return None


def code(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def raw_observations(a) -> dict:
    """Retain exact log lines even if a later provenance gate refuses."""
    path = a.evidence / 'test-on-full-verification.log'
    lines = path.read_text(errors='replace').splitlines() if path.is_file() else []
    def matches(*parts: str) -> list[dict]:
        return [{'line': n + 1, 'text': line} for n, line in enumerate(lines)
                if all(part in line for part in parts)][:24]
    return {
        'first_callback_source_190_calls': matches('verified/lib.rs(190', 'Verifying call'),
        'strict_cut_mentions': matches('end_lft_binding') +
                               matches('strict_lft_binding_scope'),
        'pair_recovery_mentions': matches('recover_pair'),
        'four_cell_join_mentions': matches('join_four_owned_cells'),
        'unwinding_mentions': matches('unwinding'),
        'return_statements': matches('Executing return statement'),
        'leak_checks': matches('Leak check.'),
    }


def preflight(a) -> dict:
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         not os.environ.get('GITHUB_ACTIONS'), 'Cloud Build provider required')
    m = read(a.proof_root / MANIFEST)
    if (m.get('status') != RELEASE_STATUS or
            m.get('admission_result') != RELEASE_RESULT):
        return {'classification': 'BLOCKED_UNTIL_REVIEW', 'blocked': True,
                'verification_accepted': False, 'actual_sort4_proved': False,
                'reason': 'committed source/MIR, storage and strict-control review is not released',
                'manifest_status': m.get('status'),
                'manifest_admission_result': m.get('admission_result')}
    patch_sha = m.get('profile_components', {}).get('overlay_patch_sha256')
    need(isinstance(patch_sha, str) and
         re.fullmatch('[0-9a-f]{64}', patch_sha) is not None and
         sha(a.proof_root / PATCH) == patch_sha,
         'reviewed overlay patch SHA is missing or differs')
    lines = (a.proof_root / PATCH).read_text().splitlines()
    need([line for line in lines if line.startswith(('--- ', '+++ '))] ==
         [f'--- a/{TRANSLATOR}', f'+++ b/{TRANSLATOR}'],
         'overlay must affect only translator')
    need(m.get('source') == {'verified_sha256': SOURCE,
                             'ghost_stripped_sha256': ORIGINAL} and
         m.get('pre_rewrite_ast_func_sha256') == AST and
         m.get('opt_in') == 'SORT4_ACTUAL_AST_SCOPE_TEST=1' and
         m.get('complete_typed_mir', {}).get('normal_record_sha256') ==
             '667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d' and
         m.get('complete_typed_mir', {}).get('readonly_record_sha256') ==
             '925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5' and
         [m.get('complete_typed_mir', {}).get(k) for k in
          ('normal_blocks', 'normal_locals', 'fnmut_calls', 'select_calls',
           'copy_calls', 'cleanup_or_drop', 'first_unwind')] ==
             [55, 137, 5, 8, 4, 0, 'Continue'],
         'reviewed O24 source/MIR/AST manifest differs')
    relocation = read(a.relocation_evidence / 'diagnostic-audit.json')
    controls = read(a.controls_evidence / 'diagnostic-audit.json')
    false_posts = read(a.false_posts_evidence / 'diagnostic-audit.json')
    need(relocation.get('classification') == 'FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY' and
         relocation.get('diagnostic_match') is True and
         relocation.get('accepted') is False and
         controls.get('classification') == 'CONTROLS_DISCOVERY_REVIEW_REQUIRED' and
         controls.get('accepted') is False and
         len(controls.get('cases', [])) == 17 and
         {row.get('case') if row.get('strict_lifetime_opt_in') else 'opt-in-absent'
          for row in controls['cases']} == set(CASES) and
         false_posts.get('classification') ==
             'FALSE_POST_CONTROLS_DISCOVERY_REVIEW_REQUIRED' and
         false_posts.get('accepted') is False and
         {row.get('case') for row in false_posts.get('cases', [])} ==
             {'normal-false', 'unwind-false'} and
         all(row.get('classification') ==
             'FALSE_POST_FIRST_BOUNDARY_CANDIDATE_REVIEW_REQUIRED'
             for row in false_posts['cases']),
         'same-Build strict relocation/matrix/false-post gates differ')
    need(git(a.production_source, 'diff', '--binary', 'HEAD') ==
         a.production_applied_patch.read_bytes(), 'production patch changed')
    base = snapshot(a.work_root / 'cut-relocation-isolated-source', a.proof_root)
    source = read(a.relocation_evidence / 'source-audit.json')
    need(base['binaries']['bin/verifast'] == source.get('relocation_console_sha256') and
         base['critical'][KERNEL] == sha(a.relocation_evidence /
                                         'cut-verifast-before-relocation.ml') and
         base['effective_rsspec'] and
         'bin/rust/std/lib.rsspec' in base['effective_rsspec'],
         'strict relocated console/kernel/spec identity differs')
    return {'classification': 'FIRST_SCOPE_PREFLIGHT_REVIEWED_TEST_ONLY',
            'blocked': False, 'verification_accepted': False,
            'patch_sha256': patch_sha, 'proof_sha': git(a.proof_root, 'rev-parse', 'HEAD').decode().strip(),
            'base_tool_snapshot': base,
            'relocation_audit_sha256': sha(a.relocation_evidence / 'diagnostic-audit.json'),
            'controls_audit_sha256': sha(a.controls_evidence / 'diagnostic-audit.json'),
            'false_posts_audit_sha256': sha(a.false_posts_evidence / 'diagnostic-audit.json')}


def baseline(a) -> dict:
    prior = read(a.evidence / 'preflight.json')
    need(prior.get('classification') == 'FIRST_SCOPE_PREFLIGHT_REVIEWED_TEST_ONLY',
         'reviewed preflight absent')
    module = load_module(a.cloud_dir / 'sort4-ast-audit.py', 'first_scope_o24_audit')
    captured = module.preflight(a.evidence / 'baseline')
    result = read(a.evidence / 'baseline/actual-sort4-result.json')
    profile = read(a.evidence / 'baseline/input-profile.json')
    base = snapshot(a.work_root / 'cut-relocation-isolated-source', a.proof_root)
    production_console = sha(a.production_source / 'bin/verifast')
    relocation_source = read(a.relocation_evidence / 'source-audit.json')
    need(base == prior['base_tool_snapshot'] and
         profile.get('tool_sha256', {}).get('verifast') ==
             production_console and
         production_console == relocation_source.get('production_console_sha256') and
         production_console != base['binaries']['bin/verifast'] and
         result.get('first_verifier_error') == FIRST and
         result.get('verifier_exit') in (1, 2) and
         result.get('actual_sort4_proved') is False,
         'same-Build isolated O24 baseline first refusal differs')
    return {'classification': 'FIRST_SCOPE_EXACT_O24_BASELINE',
            'verification_accepted': False,
            'complete_mir_ast_source_pins': captured,
            'first_error': result['first_verifier_error'],
            'production_console_sha256': production_console,
            'base_tool_snapshot': base}


def tool(a) -> dict:
    pre = read(a.evidence / 'preflight.json')
    old = pre['base_tool_snapshot']
    root = a.work_root / 'cut-relocation-isolated-source'
    new_root = a.work_root / 'sort4-first-scope-isolated-source'
    need(snapshot(root, a.proof_root) == old,
         'base isolated strict relocation tool changed')
    new = snapshot(new_root, a.proof_root)
    patched_line = (a.evidence / 'test-patched-translator.sha256').read_text().strip()
    expected_line = (new['critical'][TRANSLATOR] + '  ' +
                     str(new_root / TRANSLATOR))
    need(new['head'] == old['head'] and
         patched_line == expected_line and
         (a.evidence / 'test-patched-translator-after-build.txt').read_text().strip() ==
             str(new_root / TRANSLATOR) + ': OK' and
         new['modified_names'] == old['modified_names'] and
         TRANSLATOR in new['modified_names'] and
         new['critical'][TRANSLATOR] != old['critical'][TRANSLATOR] and
         new['binaries']['bin/verifast'] != old['binaries']['bin/verifast'] and
         new['critical'][KERNEL] == old['critical'][KERNEL] and
         new['effective_rsspec'] == old['effective_rsspec'] and
         new['proof_std'] == old['proof_std'] and
         all(value == old['modified_hashes'][name] for name, value in
             new['modified_hashes'].items() if name != TRANSLATOR) and
         all(value == old['critical'][name] for name, value in
             new['critical'].items() if name != TRANSLATOR) and
         all(value == old['binaries'][name] for name, value in
             new['binaries'].items() if name != 'bin/verifast'),
         'first-scope tool changed kernel/spec/source/binary beyond translator and console')
    return {'classification': 'FIRST_SCOPE_TRANSLATOR_ONLY_TEST_TOOL',
            'verification_accepted': False,
            'base_snapshot': old, 'test_snapshot': new,
            'observed_translator_sha256': new['critical'][TRANSLATOR],
            'observed_console_sha256': new['binaries']['bin/verifast']}


def matrix(a) -> dict:
    identity = read(a.evidence / 'tool-check.json')
    need(identity.get('classification') == 'FIRST_SCOPE_TRANSLATOR_ONLY_TEST_TOOL',
         'new console tool identity absent')
    old_rows = read(a.controls_evidence / 'diagnostic-audit.json')['cases']
    previous = {row['case'] if row['strict_lifetime_opt_in'] else 'opt-in-absent': row
                for row in old_rows}
    need(set(previous) == set(CASES), 'prior strict control inventory differs')
    current = []
    for key in CASES:
        case = key if key != 'opt-in-absent' else 'positive_basic'
        run = a.evidence / 'new-tool-matrix/cases' / key
        inner = run / (case if key != 'opt-in-absent' else
                       'positive_basic-without-opt-in')
        row = read(inner / 'result.json')
        summary = read(run / 'summary.json')
        old = previous[key]
        stages = row.get('stages', {})
        errors = row.get('full_error_lines', [])
        observed_first = errors[0] if errors else None
        need(code(a.evidence / f'new-tool-matrix/capture-{key}-exit-code.txt') == 0 and
             summary.get('cases') == [row] and
             row.get('case') == case and
             row.get('strict_lifetime_opt_in') is (key != 'opt-in-absent') and
             row.get('classification') == old['classification'] and
             row.get('accepted') is False and
             row.get('source_hashes') == old['source_hashes'] and
             observed_first == old['first_error'] and
             row.get('target_headers') == old['target_headers'] and
             row.get('callee_headers') == old['callee_headers'] and
             all(stages.get(s, {}).get('exit') == 0 and
                 stages[s].get('source_exact') is True for s in
                 ('normal-export', 'normal-decode', 'readonly-export',
                  'readonly-decode', 'refinement')) and
             stages.get('full-verification', {}).get('exit') ==
                 old['stage_exits']['full-verification'] and
             row.get('decoded_body_inventory_ok') is True,
             f'{key}: new console changed strict CUT control verdict')
        for rel, expected in row['source_hashes'].items():
            need(sha(inner / rel) == expected,
                 f'{key}: new console source pair differs')
        for mode in ('normal', 'readonly'):
            mir = old['mir'][mode]
            need(sha(inner / f'{mode}-mir.bin') == mir['bin_sha256'] and
                 sha(inner / f'{mode}-mir.txt') == mir['full_text_sha256'] and
                 row['decoded_body_inventory'][mode]['target_body_sha256'] ==
                     mir['target_body_sha256'],
                 f'{key}: new console changed full {mode} MIR')
        log = (inner / 'full-verification.log').read_text(errors='replace')
        need(first_error(log) == old['first_error'] and
             [line for line in log.splitlines() if ': error:' in line or
              line.startswith('Fatal error:')] == errors and
             log.count(f"Verifying function '{case}'") == old['target_headers'],
             f'{key}: new console raw proof differs')
        current.append({'case': key, 'classification': row['classification'],
                        'first_error': observed_first,
                        'normal_mir_sha256': sha(inner / 'normal-mir.bin'),
                        'readonly_mir_sha256': sha(inner / 'readonly-mir.bin')})
    return {'classification': 'FIRST_SCOPE_NEW_CONSOLE_17_CONTROLS_IDENTICAL',
            'test_only': True, 'verification_accepted': False,
            'all_seventeen_same_first_obligation_and_full_mir': True,
            'cases': current}


def final(a) -> dict:
    pre = read(a.evidence / 'preflight.json')
    exact = read(a.evidence / 'baseline-check.json')
    identity = read(a.evidence / 'tool-check.json')
    controls = read(a.evidence / 'new-tool-matrix-check.json')
    need(pre.get('classification') == 'FIRST_SCOPE_PREFLIGHT_REVIEWED_TEST_ONLY' and
         exact.get('classification') == 'FIRST_SCOPE_EXACT_O24_BASELINE' and
         identity.get('classification') == 'FIRST_SCOPE_TRANSLATOR_ONLY_TEST_TOOL' and
         controls.get('classification') == 'FIRST_SCOPE_NEW_CONSOLE_17_CONTROLS_IDENTICAL',
         'prior first-scope gates missing')
    need(snapshot(a.work_root / 'cut-relocation-isolated-source', a.proof_root) ==
         pre['base_tool_snapshot'] and
         snapshot(a.work_root / 'sort4-first-scope-isolated-source', a.proof_root) ==
         identity['test_snapshot'] and
         git(a.production_source, 'diff', '--binary', 'HEAD') ==
         a.production_applied_patch.read_bytes(),
         'source/tool changed after actual TEST')
    # Re-audited parent results are copied byte-for-byte, with raw parent evidence
    # retained in the same Build archive and independently checked at preflight.
    for label, root in (('relocation', a.relocation_evidence),
                        ('controls', a.controls_evidence),
                        ('false-posts', a.false_posts_evidence)):
        need((a.evidence / f'prior-{label}-audit.json').read_bytes() ==
             (root / 'diagnostic-audit.json').read_bytes(),
             f'{label} parent audit changed')
    old = read(a.evidence / 'baseline/actual-sort4-result.json')
    source = a.evidence / 'baseline/actual-sort4-fixture'
    need(sha(source / 'verified/lib.rs') == SOURCE and
         sha(source / 'original/lib.rs') == ORIGINAL and
         sha(a.production_source / 'bin/verifast') ==
             exact['production_console_sha256'] and
         old.get('first_verifier_error') == FIRST,
         'actual source or baseline first refusal changed')
    off_path = a.evidence / 'test-off-full-verification.log'
    on_path = a.evidence / 'test-on-full-verification.log'
    need(off_path.is_file() and on_path.is_file(), 'full actual verifier logs missing')
    off = off_path.read_text(errors='replace')
    on = on_path.read_text(errors='replace')
    off_exit = code(a.evidence / 'test-off-full-verification-exit-code.txt')
    on_exit = code(a.evidence / 'test-on-full-verification-exit-code.txt')
    need((a.evidence / 'actual-mode-env.txt').read_text().splitlines() == [
        'off: SORT4_ACTUAL_AST_SCOPE_TEST=0; SORT4_STRICT_LFT_CUT absent',
        'on: SORT4_ACTUAL_AST_SCOPE_TEST=1; SORT4_STRICT_LFT_CUT=1'],
        'explicit first-scope/off strict-cut opt-ins differ')
    off_errors = [line for line in off.splitlines()
                  if ': error:' in line or line.startswith('Fatal error:')]
    off_ok = (off_exit in (1, 2) and len(off_errors) == 1 and
              re.fullmatch(r'verified/lib\.rs\([0-9,-]+\): error: ' +
                           re.escape(STRICT_OPT_IN), off_errors[0]) is not None and
              'SORT4-ACTUAL-AST-SCOPE-TEST admitted' not in off)
    admitted_rows = re.findall(
        r'SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) '
        r'pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) '
        r'header_posts=([0-9a-f]{64})', on)
    admitted = (len(admitted_rows) == 1 and admitted_rows[0][0] == SOURCE and
                admitted_rows[0][1] == AST and
                admitted_rows[0][2] != AST)
    target = "Verifying function 'sort4_stable'"
    errors = [line for line in on.splitlines()
              if ': error:' in line or line.startswith('Fatal error:')]
    error = errors[0] if errors else None
    target_reached = target in on
    entered = off_ok and admitted and target_reached
    positive = (entered and on_exit == 0 and not errors and
                re.search(r'0 errors found \(\d+ statements verified\)', on) is not None and
                'Leak check.' in on)
    substantive_blocker = (entered and on_exit in (1, 2) and
                           error is not None and error != FIRST and
                           error.startswith('verified/lib.rs(') and
                           on.index(target) < on.index(error))
    meaningful = positive or substantive_blocker
    # Exact raw lines are observations, never path/resource proof claims.
    observations = raw_observations(a)
    classification = ('EXPERIMENTAL_ACTUAL_BODY_VF0_NOT_ACCEPTED' if positive else
                      'FIRST_SUBSTANTIVE_ACTUAL_BLOCKER_DIAGNOSTIC' if meaningful else
                      'INCONCLUSIVE_SETUP_OR_ADMISSION')
    return {'classification': classification,
            'diagnostic_complete': meaningful, 'verification_accepted': False,
            'actual_sort4_proved': False, 'test_only': True,
            'positive_full_body_exit_zero': positive,
            'first_substantive_actual_blocker': substantive_blocker,
            'full_actual_normal_and_unwind_posts_accepted': False,
            'off_strict_cut_opt_in_refusal': off_ok,
            'off_first_error': off_errors[0] if off_errors else None,
            'baseline_original_first_185_refusal': old['first_verifier_error'],
            'on_admission_seen': admitted, 'target_header_seen': target_reached,
            'admission_hashes': admitted_rows[0] if admitted else None,
            'full_actual_proof_exit': on_exit, 'first_error': error,
            'raw_log_observations_not_path_proofs': observations,
            'raw_evidence_paths': {
                'off': str(off_path), 'on': str(on_path),
                'baseline': str(a.evidence / 'baseline/full-verification.log')},
            'observed_translator_sha256': identity['observed_translator_sha256'],
            'observed_console_sha256': identity['observed_console_sha256'],
            'source_sha256': SOURCE, 'original_sha256': ORIGINAL,
            'open_gates': OPEN_GATES}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('preflight', 'baseline', 'tool', 'matrix', 'final'))
    for name in ('production-source', 'production-applied-patch', 'stock-home',
                 'compiler-sysroot', 'evidence', 'proof-root', 'work-root',
                 'cloud-dir', 'relocation-evidence', 'controls-evidence',
                 'false-posts-evidence', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    try:
        result = {'preflight': preflight, 'baseline': baseline,
                  'tool': tool, 'matrix': matrix, 'final': final}[a.mode](a)
    except Exception as exc:
        result = {'classification': 'INCONCLUSIVE_SETUP_OR_ADMISSION',
                  'diagnostic_complete': False, 'verification_accepted': False,
                  'actual_sort4_proved': False, 'test_only': True,
                  'reason': str(exc), 'open_gates': OPEN_GATES}
        if a.mode == 'final':
            result['raw_log_observations_not_path_proofs'] = raw_observations(a)
            result['raw_evidence_paths'] = {
                'off': str(a.evidence / 'test-off-full-verification.log'),
                'on': str(a.evidence / 'test-on-full-verification.log')}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    if a.mode == 'final':
        observed = result.get('raw_log_observations_not_path_proofs', {})
        print(json.dumps({
            'classification': result['classification'],
            'first_error': result.get('first_error'),
            'raw_milestone_line_counts': {k: len(v) for k, v in observed.items()},
            'raw_evidence_paths': result.get('raw_evidence_paths', {}),
            'verification_accepted': False}, sort_keys=True), flush=True)
    if result['classification'] in ('BLOCKED_UNTIL_REVIEW',
                                    'INCONCLUSIVE_SETUP_OR_ADMISSION'):
        raise SystemExit(f'first-scope {result["classification"]}: {result.get("reason")}')
    print(json.dumps({'classification': result['classification'],
                      'verification_accepted': False}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
