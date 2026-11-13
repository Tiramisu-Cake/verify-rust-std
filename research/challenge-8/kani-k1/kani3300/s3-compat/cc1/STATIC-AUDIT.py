#!/usr/bin/env python3
"""Source checks only. Does not compile Rust or simulate verifier acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-cc1')
BASE = 'fef9e0f38c0c645027f20223a562c7008969d9a9'
POINTS = 'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs'
DELAYED = 'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs'
PREFIX = 'tests/expected/uninit/points-to-cycles/'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args])


checks = {}
changed = git('diff', BASE, '--name-only').decode().splitlines()
checks['bounded_write_scope'] = all(p in {POINTS, DELAYED} or p.startswith(PREFIX) for p in changed)
a = (SOURCE / POINTS).read_text()
b = (SOURCE / DELAYED).read_text()
checks['root_local_context'] = a.count('&RefCell::new(ActiveCalls::new())') == 1
checks['exact_instance_and_selected_body_key'] = all(s in a for s in (
    "instance: Instance<'tcx>", 'overridden: bool',
    'overridden: body_overrides.contains_key(&rustc_internal::stable(instance))'))
checks['error_result_and_balanced_exit'] = a.count('-> Result<PointsToGraph<') == 2 and all(
    s in a for s in ('active_calls.borrow_mut().enter(key)?;',
                    'active_calls.borrow_mut().exit().map(|()| results)'))
checks['no_graph_cache_added'] = 'HashMap::new()' not in a and 'cache' not in a.split('struct ActiveCalls<K>')[1].split('/// Main points-to')[0]
checks['both_callbacks_guard_error'] = a.count('if self.active_calls.borrow().error.is_some()') == 2
checks['failed_child_not_joined'] = 'let Ok(new_result) = PointsToAnalysis::run(' in a and 'self.active_calls,\n            initial_graph,' in a
checks['only_successful_roots_merged'] = 'Ok(results) => {\n                            global_points_to_graph.join(&results);' in b and 'Err(error) => unsupported_roots.push((instance, error))' in b
checks['unsupported_at_entry_after_instrumentation'] = b.index('for (instance, error) in unsupported_roots') > b.index('UninitInstrumenter::run(') and all(s in b for s in (
    'SourceInstruction::Terminator { bb: 0 }', 'SourceInstruction::Statement { bb: 0, idx: 0 }',
    '&self.unsupported_check_type,', '&error.reason,',
    'transformer.cache.insert(instance, TransformationResult(body.into(), true))'))
checks['seven_rust_unit_controls_present_not_executed'] = a.count('#[test]') == 7
checks['s3_override_selection_preserved'] = all(s in b for s in (
    'marker.as_str() == "kani_register_contract"',
    'TerminatorKind::Unreachable', 'body_overrides.insert(*instance, body.clone());'))
# Preserve all pre-existing contracts/transfer/layout/check logic and golden inputs.
protected = git('ls-tree', '-r', '--name-only', BASE,
    'kani-compiler/src/kani_middle/transform/check_uninit',
    'kani-compiler/src/kani_middle/transform/contracts.rs',
    'library/kani_core/src/mem_init.rs',
    'tests/expected/uninit',
    'tests/json-handler/uninit-contract-oracles',
    'tests/json-handler/uninit-contract-mode-boundaries').decode().splitlines()
checks['protected_existing_sources_identical'] = all(
    git('show', f'{BASE}:{p}') == (SOURCE / p).read_bytes()
    for p in protected if p != DELAYED)
manifest = json.loads((SOURCE / 'tests/json-handler/uninit-contract-oracles/oracles.json').read_text())
checks['eight_oracle_input_hashes_preserved'] = len(manifest['cases']) == 8 and all(
    hashlib.sha256((SOURCE / c['input']).read_bytes()).hexdigest() == c['sha256']
    for c in manifest['cases'])
fixtures = sorted((SOURCE / PREFIX).glob('*.rs'))
checks['six_source_controls_with_expected_files'] = len(fixtures) == 6 and all(p.with_suffix('.expected').exists() for p in fixtures)
checks['two_input_graphs_and_observable_hole_read'] = all(s in (SOURCE / PREFIX / 'dag.rs').read_text() for s in (
    'left(a.as_ptr()).read()', 'right(b.as_ptr()).read()', 'MaybeUninit::<u8>::uninit()'))
checks['mixed_root_declaration_orders'] = all(
    ((SOURCE / PREFIX / name).read_text().index('fn self_cycle()') <
     (SOURCE / PREFIX / name).read_text().index('fn independent_nonrecursive()')) == first
    for name, first in [('roots-cycle-first.rs', True), ('roots-acyclic-first.rs', False)])
print(json.dumps({'kind': 'STATIC_ONLY', 'checks': checks, 'passed': all(checks.values()),
                  'protected_file_count': len(protected) - 1,
                  'rust_typecheck': 'NOT_RUN', 'rust_units': 'NOT_RUN', 'verifier': 'NOT_RUN'}, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
