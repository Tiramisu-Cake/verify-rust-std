#!/usr/bin/env python3
"""CC3 preservation/API/source audit; never invokes a Rust tool or solver."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-cc3')
HERE = Path(__file__).resolve().parent
API = Path(sys.argv[2] if len(sys.argv) > 2 else '/tmp/kani3300-cc3-api')
BASE = '9631aaf89e869624fbfc8cd22d327ce194eb779d'
LAYOUT = 'kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs'
PREFIX = 'tests/expected/uninit/closure-upvars/'
OLD_PREFIX = 'tests/expected/uninit/closure-zst/'
GOLDENS = {'capture-scalar', 'capture-padded', 'capture-reference-legal',
           'capture-reference-hole', 'capture-raw-legal', 'capture-raw-hole',
           'capture-mu-reference-new', 'capture-mu-reference-uninit',
           'capture-mu-value-new', 'capture-mu-value-uninit',
           'capture-union-reference', 'capture-union-value'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = {}
changed = set(git('diff', BASE, '--name-only').decode().splitlines())
new = set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
allowed = {LAYOUT} | {PREFIX + stem + ext for stem in ('ordinary', 'layout', 'holes')
                     for ext in ('.rs', '.expected')} | {
                         OLD_PREFIX + stem + '.expected' for stem in GOLDENS}
checks['bounded_changed_source_scope'] = changed | new == allowed
old = git('show', f'{BASE}:{LAYOUT}').decode()
current = (SOURCE / LAYOUT).read_text()
start = current.index('                RigidTy::Closure(_, _) => {')
end = current.index('                RigidTy::FnDef(_, _)', start)
restored = current[:start] + current[end:]
restored = restored.replace('                | RigidTy::FnPtr(_)\n',
                            '                | RigidTy::FnPtr(_)\n                | RigidTy::Closure(_, _)\n')
checks['only_nonzero_closure_arm_changed_all_other_layout_guards_identical'] = restored == old
arm = current[start:end]
checks['actual_upvars_own_layout_composed_offsets_error_propagation'] = all(s in arm for s in (
    'rustc_middle::ty::tls::with(|tcx|', 'rustc_internal::internal(tcx, ty)',
    'args.as_closure().upvar_tys().iter().map(rustc_internal::stable).collect()',
    'assert_eq!(upvar_tys.len(), offsets.len())',
    'layout.fields.fields_by_offset_order()', 'upvar_tys[idx]',
    'current_offset + offsets[idx].bytes()', ')?);')) and not any(
        s in arm for s in ('new_tuple', 'vec![true;', 'unwrap_or', 'assume', 'is_union'))
checks['existing_closure_rust_inputs_unchanged'] = all(
    p.read_bytes() == git('show', f'{BASE}:{p.relative_to(SOURCE)}')
    for p in (SOURCE / OLD_PREFIX).glob('*.rs'))
checks['original_mode_inputs_and_collector_unchanged'] = all(
    p.read_bytes() == git('show', f'{BASE}:{p.relative_to(SOURCE)}')
    for p in (SOURCE / 'tests/json-handler/uninit-contract-mode-boundaries').iterdir()
    if p.is_file())
manifest = json.loads((SOURCE / 'tests/json-handler/uninit-contract-oracles/oracles.json').read_text())
checks['eight_strong_oracle_hashes_preserved'] = len(manifest['cases']) == 8 and all(
    sha(SOURCE / c['input']) == c['sha256'] for c in manifest['cases'])
fixtures = {p.stem: p.read_text() for p in (SOURCE / PREFIX).glob('*.rs')}
roots = {stem: re.findall(r'#\[kani::proof(?:_for_contract\([^\n]*\))?\]\s*'
                          r'(?:#\[[^\n]*\]\s*)*fn (\w+)\(', text)
         for stem, text in fixtures.items()}
checks['three_new_fixtures_eight_roots_bits12_and_goldens'] = (
    set(fixtures) == {'ordinary', 'layout', 'holes'}
    and sum(map(len, roots.values())) == 8
    and all('--cbmc-args --object-bits 12' in text for text in fixtures.values())
    and all((SOURCE / PREFIX / (stem + '.expected')).exists() for stem in fixtures))
checks['actual_typed_copy_requests_and_copy_bound_present'] = all(s in fixtures['layout'] for s in (
    'F: Copy + Fn() -> bool', 'std::ptr::addr_of!(wrapped).read()',
    'Offset { prefix: 7, callback }', 'touch(&inner)', 'touch(&unit)', 'touch(&padded)'))
checks['bool_ref_contract_and_both_branches_preserved'] = all(s in fixtures['ordinary'] for s in (
    'captured_bool(true)', 'captured_bool(false)',
    'ensures(|result: &MaybeUninit<u8>| !initialized || payload_is_17(result))',
    'kani::proof_for_contract(captured_contract)', 'exercise_contract(kani::any())',
    'captured contract true result consumed', 'captured contract false storage returned'))
checks['valid_ref_payload_pair_and_reached_padding_read_present'] = all(s in fixtures['holes'] for s in (
    'two_refs(true)', 'two_refs(false)', 'let enabled = &flag;', 'let payload = &data;',
    'two-ref body reached payload read', 'closure padding byte read reached',
    'let copied = unsafe { std::ptr::addr_of!(callback).read() };',
    'std::ptr::addr_of!(capture).cast::<u8>().wrapping_add(1)', 'unsafe { padding.read() }'))
checks['negative_goldens_require_reads_and_byvalue_union_boundary'] = all(
    'type `*const u8`' in (SOURCE / OLD_PREFIX / (stem + '.expected')).read_text()
    and 'type `u8`' in (SOURCE / OLD_PREFIX / (stem + '.expected')).read_text()
    and 'unsupported type {closure@' not in (SOURCE / OLD_PREFIX / (stem + '.expected')).read_text()
    for stem in ['capture-reference-hole', 'capture-raw-hole', 'capture-mu-reference-uninit']) and all(
    'contains union of type' in (SOURCE / OLD_PREFIX / (stem + '.expected')).read_text()
    for stem in ['capture-mu-value-new', 'capture-mu-value-uninit', 'capture-union-value'])
api = json.loads((HERE / 'RUSTC-API.json').read_text())
toolchain = json.loads((HERE / 'TOOLCHAIN.json').read_text())
checks['official_nightly_pin_and_all_api_source_hashes'] = (
    toolchain['git_commit_hash'] == api['revision'] == '7189d39d9ce936881b8132c6addeaf3e295cd455'
    and toolchain['date'] == '2026-10-23'
    and all(sha(API / rec['path'].replace('/', '__')) == rec['sha256']
            for rec in api['sources']))
checks['git_diff_check'] = subprocess.run(
    ['git', '-C', str(SOURCE), 'diff', '--check'], capture_output=True).returncode == 0
result = dict(assurance='STATIC_ONLY', checks=checks,
              status='PASS' if all(checks.values()) else 'FAIL',
              rust_typecheck='NOT_RUN', kani_cbmc_ci='NOT_RUN',
              selected_model_binding='UNKNOWN', independent_review='PENDING_COORDINATOR')
print(json.dumps(result, indent=2))
sys.exit(0 if all(checks.values()) else 1)
