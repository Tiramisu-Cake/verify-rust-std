#!/usr/bin/env python3
"""CC2 source/preservation audit only; no Rust execution or proof acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-cc2')
BASE = 'b2e1a392ad27bd21758473bc208ff66c2d7d0405'
VISITOR = 'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs'
PREFIX = 'tests/expected/uninit/ordinary-slots/'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args])


checks = {}
changed = set(git('diff', BASE, '--name-only').decode().splitlines())
new = set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
allowed = {VISITOR} | {PREFIX + stem + ext for stem in ('positive', 'payload', 'padding')
                     for ext in ('.rs', '.expected')}
checks['bounded_source_scope_and_existing_inputs_preserved'] = changed | new <= allowed
a = (SOURCE / VISITOR).read_text()
old = git('show', f'{BASE}:{VISITOR}').decode()
entry = a.split('if bb_idx == 0 {')[1].split('self.visit_basic_block(bb);')[0]
checks['only_argument_slots_seeded'] = all(s in entry for s in (
    '.enumerate().skip(1).take(body.arg_count())', 'let place = Place::from(local);',
    'self.needs_set(&place)', '!decl.ty.kind().is_union()',
    'PointeeInfo::from_ty(decl.ty)', 'Ok(PointeeLayout::Sized { .. })',
    'MemoryInitOp::SetRef {', 'operand: Operand::Copy(place)',
    'value: true', 'position: InsertPosition::Before')) and 'projection' not in entry
checks['entry_preserved_for_empty_bb0'] = (
    'self.current_target.source = SourceInstruction::Terminator { bb };' in a
    and a.split('fn visit_terminator')[1].split('self.super_terminator')[0].count('vec![]') == 0)
checks['statement_checks_and_copies_unchanged'] = (
    a.split('fn visit_statement')[1].split('fn visit_terminator')[0]
    == old.split('fn visit_statement')[1].split('fn visit_terminator')[0])
checks['address_creation_read_policy_unchanged'] = (
    a.split('fn visit_rvalue')[1].split('fn visit_place')[0]
    == old.split('fn visit_rvalue')[1].split('fn visit_place')[0])
checks['source_get_and_destination_set_policy_unchanged'] = (
    a.split('// If we are mutating the place, initialize it.')[1]
    == old.split('// If we are mutating the place, initialize it.')[1])
checks['alias_walk_termination_and_both_call_sites'] = all(s in a for s in (
    'fn needs_set(&self, place: &Place) -> bool', 'visited_pairs.contains(&state)',
    'self.points_to.ancestors(&state.0)', 'self.points_to.ancestors(&state.1)',
    'let needs_set = self.needs_set(place);'))
fixtures = list((SOURCE / PREFIX).glob('*.rs'))
checks['three_fixtures_nine_roots_with_per_test_bits12'] = (
    len(fixtures) == 3 and sum(p.read_text().count('#[kani::proof') for p in fixtures) == 9
    and all('--cbmc-args --object-bits 12' in p.read_text()
            and p.with_suffix('.expected').exists() for p in fixtures))
p = (SOURCE / PREFIX / 'positive.rs').read_text()
checks['discriminating_reads_precede_local_address_setters'] = (
    p.index('kani::cover!(initialized,') < p.index('std::ptr::addr_of!(initialized)')
    and p.index('reference_identity(value);') < p.index('std::ptr::addr_of!(value)')
    and p.index('assert!(value.tag == 7,') < p.index('cast::<MaybeUninit<RefWrapper'))
checks['capture_free_contract_has_no_parameters'] = (
    '#[kani::ensures(|result: &bool| *result)]\nfn capture_free_slots() -> bool' in p)
n = (SOURCE / PREFIX / 'payload.rs').read_text()
checks['paired_initialized_and_reached_payload_holes_present'] = all(s in n for s in (
    'fn initialized_payloads()', 'fn reference_slot_preserves_hole()',
    'fn raw_slot_preserves_hole()', 'fn entry_does_not_hide_caller_read()',
    '"reference body reached payload read"', '"raw body reached payload read"',
    'consume_byte(unsafe { hole.as_ptr().read() })'))
manifest = json.loads((SOURCE / 'tests/json-handler/uninit-contract-oracles/oracles.json').read_text())
checks['eight_strong_oracle_inputs_hash_identical'] = len(manifest['cases']) == 8 and all(
    hashlib.sha256((SOURCE / c['input']).read_bytes()).hexdigest() == c['sha256']
    for c in manifest['cases'])
checks['git_diff_check'] = subprocess.run(
    ['git', '-C', str(SOURCE), 'diff', '--check'], capture_output=True).returncode == 0
result = {'assurance': 'STATIC_ONLY', 'checks': checks,
          'status': 'PASS' if all(checks.values()) else 'FAIL',
          'rust_typecheck': 'NOT_RUN', 'kani_cbmc_ci': 'NOT_RUN',
          'selected_model_binding': 'UNKNOWN'}
print(json.dumps(result, indent=2))
sys.exit(0 if all(checks.values()) else 1)
