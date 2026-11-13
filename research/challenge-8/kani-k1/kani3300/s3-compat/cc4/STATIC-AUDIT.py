#!/usr/bin/env python3
"""CC4 source preservation / extraction audit. No Rust subprocesses."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-cc4')
OUT = Path(__file__).resolve().parent
BASE = '76a706f8f8c5b0471bd5c8e6b48cdaf45bab9b66'

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def base(path):
    return git('show', f'{BASE}:{path}').decode()

def compact(text):
    return re.sub(r'\s+', '', re.sub(r'//[^\n]*', '', text))

checks = {}
allowed = {
    'docs/src/reference/experimental/contracts.md',
    'kani-compiler/src/kani_middle/points_to/mod.rs',
    'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs',
    'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs',
    'tests/expected/uninit/closure-zst/capture-reference-legal.expected',
    'tests/expected/uninit/closure-zst/capture-union-reference.expected',
}
tracked = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
changed = set(git('diff', '--name-only', BASE).decode().splitlines()) & set(tracked)
checks['only_six_existing_files_changed'] = changed == allowed
checks['all_existing_rust_inputs_other_goldens_and_oracles_identical'] = not any(p.startswith('tests/') and p not in allowed for p in changed)
pta_path = 'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs'
pta = (ROOT/pta_path).read_text()
old = base(pta_path)
# The call transfer is byte-equivalent modulo formatting and diagnostic plumbing.
a = '    fn apply_regular_call_effect('
b = '    /// Find all places where the rvalue'
new_transfer = pta[pta.index(a):pta.index(b)]
new_transfer = new_transfer.replace('        location: Location,\n', '')
new_transfer = new_transfer.replace('.map(|selected| selected.body.clone())', '.cloned()')
new_transfer = re.sub(r'\s*Some\(CallerLocation \{\s*location,\s*span: self.body.basic_blocks\[location.block\].terminator\(\).source_info.span,\s*\}\),', '', new_transfer)
checks['regular_call_transfer_identical_modulo_metadata'] = compact(new_transfer) == compact(old[old.index(a):old.index(b)])
start = '        let analysis ='
end = '\nimpl<\'tcx> Analysis'
checks['dataflow_and_error_result_boundary_identical'] = compact(pta[pta.index(start):pta.index(end)]) == compact(old[old.index(start):old.index(end)])
checks['fresh_per_root_context_and_join_only_ok_preserved'] = all(x in pta for x in ['&RefCell::new(ActiveCalls::new())', 'active_calls.borrow_mut().enter_at(key, caller)?;', 'active_calls.borrow_mut().exit().map(|()| results)', 'let Ok(new_result) = PointsToAnalysis::run('])
checks['bounded_diagnostic_exact_symbols_provenance_callsites_explicit_truncation'] = all(x in pta for x in ['MAX_FRAMES: usize = 12', 'MAX_FRAME_CHARS: usize = 4096', 'owner_symbol', 'selected_origin_symbol', 'RegistrationOverride', 'DiscardedClosureOverride', 'Source', 'caller.location', 'caller.span', 'frames omitted', 'frame truncated'])
delayed = (ROOT/'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs').read_text()
checks['override_bodies_keep_original_selection_and_origin_resolver'] = all(x in delayed for x in ['if is_registration || is_discarded_closure', 'AnalysisBodyOverride { body: body.clone(), provenance }', 'Instance::resolve(run, &instance.args()).unwrap()', '.map(|selected| selected.body.clone())', 'Ok(results) => {', 'global_points_to_graph.join(&results);', 'Err(error) => unsupported_roots.push((instance, error))'])
source_path = 'tests/json-handler/uninit-contract-mode-boundaries/recursive.rs'
src = base(source_path)
helpers = src[src.index('use std::mem::MaybeUninit;'):src.index('#[kani::requires(depth <= 1)]')]
second = src.index('#[kani::requires(depth <= 1)]', src.index('fn recursive_transfer'))
rec = src[src.index('#[kani::requires(depth <= 1)]'):second]
bounded = src[second:src.index('#[kani::proof_for_contract(recursive_transfer)]')]
check = src[src.index('#[kani::proof_for_contract(recursive_transfer)]'):src.index('#[kani::proof]\n')]
ordinary = src[src.index('#[kani::proof]\n'):src.index('#[kani::proof_for_contract(bounded_transfer)]')]
simple = src[src.index('#[kani::proof_for_contract(bounded_transfer)]'):]
fixtures = ROOT/'tests/json-handler/uninit-contract-mode-boundaries/cc4'
for filename, body in {
    'isolated-bounded.rs': helpers+bounded+simple,
    'isolated-recursive-ordinary.rs': helpers+rec+ordinary,
    'mixed-reversed.rs': helpers+rec+bounded+simple+ordinary+check,
}.items():
    actual = (fixtures/filename).read_text()
    actual = actual[actual.index('use std::mem::MaybeUninit;'):]
    checks[f'exact_extraction_{filename}'] = compact(actual) == compact(body)
checks['isolated_bounded_has_no_recursive_sibling_or_new_golden'] = 'fn recursive_transfer' not in (fixtures/'isolated-bounded.rs').read_text() and not list(fixtures.glob('*.expected'))
for name, reason in {
    'capture-reference-legal': 'Failed Checks: Checking memory initialization of type std::cell::UnsafeCell<std::mem::MaybeUninit<u8>> is not supported. Cannot determine layout for a type that contains union of type std::mem::MaybeUninit<u8> as a field.',
    'capture-union-reference': 'Failed Checks: Kani does not yet support performing a dereference on a union field',
}.items():
    text = (ROOT/f'tests/expected/uninit/closure-zst/{name}.expected').read_text()
    checks[f'exact_expected_{name}'] = text.splitlines() == [f'Checking harness {name.replace("-", "_")}...', reason, 'VERIFICATION:- FAILED', 'Complete - 0 successfully verified harnesses, 1 failures, 1 total.']
checks['original_expectation_patch_hash'] = hashlib.sha256((OUT/'expectations.patch').read_bytes()).hexdigest() == 'da87f8729e2b52eb4f3b6095cb105d10031ce70a2f18985ecccb24381d8e5415'
checks['git_diff_check'] = subprocess.run(['git', '-C', str(ROOT), 'diff', '--check'], capture_output=True).returncode == 0
result = {'assurance': 'STATIC_ONLY', 'checks': checks, 'status': 'PASS' if all(checks.values()) else 'FAIL', 'preserved_existing_test_files': sum(p.startswith('tests/') and p not in allowed for p in tracked), 'rust_typecheck': 'NOT_RUN', 'kani_cbmc_ci': 'NOT_RUN', 'exact_selected_mir_path': 'PENDING_COORDINATOR', 'independent_review': 'PENDING_COORDINATOR'}
(OUT/'STATIC-CHECKS.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
