"""Pure interpretation of current A1 observations into workflow records.

No expectation tuple is an observed verdict. Each route below first requires
its own executed stages, classifier and input identity before emitting the
semantic stage/predicate/location labels checked by A1Admission. These remain
runner reports, never independent proof credit. No files or tools are read.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import re

BODY = {'P0a': 'default16', 'P0b': 'freeze32',
        'N-default-contract': 'default16', 'N-freeze-contract': 'freeze32'}
SYNTHETIC = {
    'N-binder-collapse': ('binder_collapse',), 'N-alpha-valid': ('alpha_valid',),
    'N-free-region': ('free_region_input',),
    'N-no-F': ('no_F',), 'N-clauses': ('remove_fnmut', 'remove_output'),
    'N-duplicate': ('duplicate_impl_method',),
}
# These labels describe a validated observation; they are never copied from
# the caller's expected verdict or used without the route's evidence gates.
SYNTHETIC_LABELS = {
    'N-binder-collapse': ('identity-validation', 'distinct-input-binder-identities', 'synthetic required-fn input'),
    'N-alpha-valid': ('identity-validation', 'consistent-bijective-region-renaming', 'synthetic required-fn input'),
    'N-free-region': ('well-scopedness', 'all-regions-in-scope', 'synthetic input type'),
    'N-no-F': ('generic-scope-validation', 'method-F-present-and-constrained', 'synthetic trait declaration'),
    'N-clauses': ('interface-admission', 'full-HRTB-FnMut-Output-bool-clauses', 'trait interface certificate'),
    'N-duplicate': ('inventory-admission', 'exact-closed-impl-item-inventory', 'compiler impl inventory'),
}
REGRESSIONS = {
    'R1': ('canonical_slice_as_mut_ptr', None),
    'R2': ('canonical_slice_as_mut_ptr_mu', None),
    'R3': ('native_slice_pointer_consumer', None),
    'R4': ('native_slice_pointer_consumer assertion', 'v_base != source_base'),
    'R5': ('native_slice_pointer_consumer assertion', 'unrelated[..1] |-> ?unrelated_values'),
    'R6': ('native_slice_pointer_consumer assertion', 'scratch_base[..1] |-> ?initialized_values'),
    'R7': ('selected_threshold_body', None),
}


class ObservationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ObservationError(message)


def _mapping(value, label):
    require(isinstance(value, Mapping), label + ' missing')
    return value


def _source_bounds_text(bounds):
    if (not isinstance(bounds, (tuple, list)) or len(bounds) != 2 or
            any(not isinstance(point, (tuple, list)) or len(point) != 3
                for point in bounds)):
        return None
    lo, hi = bounds
    if (lo[0] != 'verified/lib.rs' or hi[0] != lo[0] or
            type(lo[1]) is not int or lo[1] <= 0 or type(hi[1]) is not int or hi[1] <= 0 or
            type(lo[2]) is not int or lo[2] < 0 or type(hi[2]) is not int or hi[2] < 0 or
            (hi[1], hi[2]) < (lo[1], lo[2])):
        return None
    end = f'{hi[1]},{hi[2]}' if hi[1] != lo[1] else str(hi[2])
    return f'{lo[0]}({lo[1]},{lo[2]}-{end})'


def _stage_exit(raw, name):
    value = raw.get('stages', {}).get(name)
    return value.get('exit') if isinstance(value, Mapping) else value


def _source_observation(case, observation, expected_input, build_id):
    raw = _mapping(observation.get('raw'), 'current raw source observation')
    require(raw.get('case_id') == case and raw.get('build_id') == build_id,
            'source case or Build identity differs')
    require(raw.get('source_id') == expected_input.get('source_id') and
            raw.get('unit_id') == expected_input.get('unit_id'),
            'observed source/unit identity differs from constructed input')
    require(raw.get('paired_support', {}).get('paired_support_passed') is True,
            'current paired export/decode/refinement incomplete')
    require(raw.get('focus_is_export_or_translation_filter') is False,
            'complete unit inventory missing')
    require(raw.get('artifacts', {}).get('proof-ast.ml', {}).get('sha256'),
            'same-invocation AST missing')
    return raw, _mapping(observation.get('structure'), 'source/AST structure gate')


def _p1_interface_gate(gate, raw, structure, expected_inventory, run_pins,
                       observation, expected_input):
    """Validate the current producer's complete, non-credit P1 schema.

    The per-implementation R-only comparison is deliberately not conflated
    with the separate common-prototype comparison performed by the producer.
    """
    gate = _mapping(gate, 'full small_sort P1 gate')
    top_keys = {
        'schema', 'classification', 'source_pair_id',
        'actual_source_pair_sha256', 'compiler_interface_digest',
        'normalized_native', 'native_sha256', 'impls', 'structural_pass',
        'compiler_clauses_source_bound', 'ast_clause_representation',
        'compiler_clause_digest', 'positional_alpha_roles', 'body_count',
        'proof_credit', 'conformance_credit', 'native_contract_credit',
    }
    require(set(gate) == top_keys,
            'P1 gate does not have the exact current producer schema')
    require(gate.get('schema') == 'a1-small-sort-interface-observation-v1' and
            gate.get('classification') == 'INTERFACE_STRUCTURE_ONLY_UNRUN_PROOF',
            'P1 gate schema/classification is stale or ambiguous')
    require(gate.get('structural_pass') is True and
            gate.get('compiler_clauses_source_bound') is True and
            type(gate.get('body_count')) is int and gate['body_count'] == 0 and
            gate.get('proof_credit') is False and
            gate.get('conformance_credit') is False and
            gate.get('native_contract_credit') is False and
            gate.get('ast_clause_representation') ==
            'none; compiler-required interface is separately validated',
            'P1 structural-only/source-bound predicates incomplete')
    ast_artifact = _mapping(raw.get('artifacts', {}).get('proof-ast.ml'),
                            'P1 same-invocation proof AST artifact')
    require(isinstance(ast_artifact.get('sha256'), str) and
            re.fullmatch(r'[0-9a-f]{64}', ast_artifact['sha256']) is not None,
            'P1 same-invocation proof AST identity is malformed')

    observed_pins = _mapping(observation.get('run_identity'),
                             'P1 same-run tool/profile identity')
    pin_keys = {'tool_id', 'profile_id', 'proof_id', 'infra_id', 'target_id'}
    expected_pins = _mapping(run_pins, 'current run pins')
    require(set(observed_pins) == pin_keys and set(expected_pins) == pin_keys and
            all(isinstance(observed_pins.get(key), str) and
                observed_pins[key] == expected_pins.get(key)
                for key in pin_keys - {'target_id'}) and
            isinstance(observed_pins.get('target_id'), str) and
            bool(observed_pins['target_id']) and
            observed_pins['target_id'] == expected_pins.get('target_id') and
            re.fullmatch(r'[0-9a-f]{64}', observed_pins['tool_id']) is not None and
            re.fullmatch(r'[0-9a-f]{64}', observed_pins['profile_id']) is not None and
            re.fullmatch(r'[0-9a-f]{40}', observed_pins['proof_id']) is not None and
            re.fullmatch(r'[0-9a-f]{40}', observed_pins['infra_id']) is not None,
            'P1 observation tool/profile/proof/infra/target pins differ from this run')

    pair = _mapping(raw.get('source_pair_sha256'), 'P1 raw source-pair hashes')
    require(set(pair) == {'verified', 'original'} and
            all(isinstance(pair.get(key), str) and
                re.fullmatch(r'[0-9a-f]{64}', pair[key]) is not None
                for key in ('verified', 'original')),
            'P1 raw source-pair hashes malformed')
    actual_pair = hashlib.sha256(
        (pair['verified'] + ':' + pair['original']).encode('ascii')).hexdigest()
    inventory = _mapping(structure.get('inventory'), 'P1 compiler inventory')
    case_binding = _mapping(inventory.get('case_binding'),
                            'P1 compiler inventory source-pair binding')
    inventory_payload = _mapping(inventory.get('inventory'),
                                 'P1 compiler inventory payload')
    required = _mapping(inventory_payload.get('required_small_sort'),
                         'P1 required compiler interface')
    generated_source = case_binding.get('generated_source_sha256')
    require(isinstance(case_binding.get('source_pair_id'), str) and
            bool(case_binding['source_pair_id']) and
            case_binding.get('source_id') == expected_input.get('source_id') and
            isinstance(generated_source, str) and
            re.fullmatch(r'[0-9a-f]{64}', generated_source) is not None and
            generated_source == case_binding.get('source_pair_id') == pair['verified'] and
            gate.get('source_pair_id') == case_binding['source_pair_id'] and
            gate.get('actual_source_pair_sha256') == actual_pair and
            gate.get('compiler_interface_digest') == required.get('interface_digest') and
            gate.get('compiler_clause_digest') ==
            hashlib.sha256(repr(required.get('clauses')).encode()).hexdigest() and
            gate.get('positional_alpha_roles') == required.get('alpha_roles'),
            'P1 producer gate is stale or bound to another source pair')

    native = _mapping(gate.get('normalized_native'), 'P1 common native clauses')
    require(set(native) == {'pre', 'returning', 'unwind'},
            'P1 common native pre/normal/unwind inventory incomplete')
    native_hashes = _mapping(gate.get('native_sha256'), 'P1 common native hashes')
    require(set(native_hashes) == {'pre', 'returning', 'unwind'} and
            all(isinstance(native_hashes.get(key), str) and
                re.fullmatch(r'[0-9a-f]{64}', native_hashes[key]) is not None and
                native_hashes[key] == hashlib.sha256(repr(native[key]).encode()).hexdigest()
                for key in ('pre', 'returning', 'unwind')),
            'P1 common native clause hashes are stale or malformed')
    for digest_key in ('compiler_interface_digest', 'compiler_clause_digest'):
        require(isinstance(gate.get(digest_key), str) and
                re.fullmatch(r'[0-9a-f]{64}', gate[digest_key]) is not None,
                'P1 compiler digest is missing or malformed: ' + digest_key)

    rows = _mapping(gate.get('impls'), 'P1 implementation rows')
    require(set(rows) == {'default16', 'freeze32'},
            'P1 implementation row inventory is not exact')
    compiler_impls = inventory_payload.get('impls')
    require(isinstance(compiler_impls, (tuple, list)) and len(compiler_impls) == 2 and
            all(isinstance(item, Mapping) for item in compiler_impls) and
            {item.get('impl') for item in compiler_impls} == {'default16', 'freeze32'},
            'P1 current compiler impl inventory is not exactly default16/freeze32')
    compiler_impls_by_name = {item['impl']: item for item in compiler_impls}
    identities = inventory_payload.get('impl_small_sort_identities')
    require(isinstance(identities, (tuple, list)) and len(identities) == 2 and
            {row.get('impl') for row in identities if isinstance(row, Mapping)} ==
            {'default16', 'freeze32'},
            'P1 current compiler implementation identity inventory incomplete')
    identities_by_impl = {row['impl']: row for row in identities}
    identity_keys = {
        'alias', 'ast_body_line', 'compiler_signature', 'compiler_signature_digest',
        'impl', 'impl_def_index', 'item_def_id', 'item_def_index',
        'source_body_span', 'source_fn_sig_span',
    }
    seen_impl_ids, seen_item_ids = set(), set()
    row_keys = {
        'alias', 'compiler_impl_id', 'compiler_item_id',
        'compiler_signature_digest', 'positional_alpha_map',
        'compiler_positional_region_map', 'native_sha256',
        'actual_definition_bound_to_compiler_item',
        'native_matches_r_only_original_impl',
    }
    for impl in ('default16', 'freeze32'):
        row = _mapping(rows[impl], 'P1 ' + impl + ' row')
        require(set(row) == row_keys,
                'P1 ' + impl + ' row schema is stale, incomplete, or ambiguous')
        expected = _mapping(expected_inventory.get(impl),
                            'expected P1 ' + impl + ' compiler identity')
        current_identity = _mapping(identities_by_impl.get(impl),
                                    'current compiler ' + impl + ' identity')
        compiler_impl = compiler_impls_by_name[impl]
        require(set(expected) == {'compiler_impl_id', 'compiler_item_id'},
                'expected P1 ' + impl + ' threshold identity schema differs')
        impl_id = expected.get('compiler_impl_id')
        threshold_id = expected.get('compiler_item_id')
        require(isinstance(impl_id, str) and re.fullmatch(r'[1-9][0-9]*', impl_id) and
                isinstance(threshold_id, str) and
                re.fullmatch(r'[1-9][0-9]*', threshold_id) and
                set(current_identity) == identity_keys and
                current_identity.get('impl') == impl and
                type(current_identity.get('impl_def_index')) is int and
                current_identity['impl_def_index'] > 0 and
                type(current_identity.get('item_def_index')) is int and
                current_identity['item_def_index'] > 0 and
                current_identity['impl_def_index'] not in seen_impl_ids and
                current_identity['item_def_index'] not in seen_item_ids and
                str(current_identity['impl_def_index']) == impl_id and
                type(compiler_impl.get('impl_def_index')) is int and
                compiler_impl['impl_def_index'] > 0 and
                compiler_impl.get('impl_def_index') == current_identity['impl_def_index'] and
                isinstance(compiler_impl.get('items'), (tuple, list)) and
                len(compiler_impl['items']) == 2 and
                all(isinstance(item, Mapping) for item in compiler_impl['items']) and
                {item.get('name') for item in compiler_impl['items']} ==
                {'small_sort_threshold', 'small_sort'},
                'P1 ' + impl + ' compiler impl/threshold inventory binding failed')
        seen_impl_ids.add(current_identity['impl_def_index'])
        compiler_items = {item['name']: item for item in compiler_impl['items']}
        threshold_item = compiler_items['small_sort_threshold']
        small_sort_item = compiler_items['small_sort']
        require(all(set(item) == {'body', 'def_id', 'def_index', 'name',
                                  'small_sort_signature'}
                    for item in compiler_items.values()) and
                all(type(item.get('def_index')) is int and item['def_index'] > 0 and
                    isinstance(item.get('def_id'), str) and item['def_id']
                    for item in compiler_items.values()) and
                all(isinstance(item.get('body'), Mapping) and
                    item['body'].get('def_path') == item['def_id']
                    for item in compiler_items.values()) and
                isinstance(small_sort_item.get('small_sort_signature'), Mapping) and
                isinstance(small_sort_item['small_sort_signature'].get('digest'), str) and
                re.fullmatch(r'[0-9a-f]{64}',
                             small_sort_item['small_sort_signature']['digest']) is not None and
                threshold_item.get('small_sort_signature') is None and
                threshold_item['def_index'] != small_sort_item['def_index'] and
                str(threshold_item['def_index']) == threshold_id and
                threshold_item['def_index'] not in seen_item_ids and
                small_sort_item['def_index'] not in seen_item_ids and
                current_identity.get('item_def_index') == small_sort_item['def_index'] and
                current_identity.get('item_def_id') == small_sort_item['def_id'] and
                current_identity.get('compiler_signature_digest') ==
                small_sort_item['small_sort_signature']['digest'] and
                current_identity.get('source_body_span') ==
                small_sort_item.get('body', {}).get('mir_span') and
                current_identity.get('source_fn_sig_span') ==
                small_sort_item.get('body', {}).get('fn_sig_span'),
                'P1 ' + impl + ' named threshold/small_sort compiler item join failed')
        seen_item_ids.update((threshold_item['def_index'], small_sort_item['def_index']))
        item_id = str(small_sort_item['def_index'])
        require(row.get('compiler_impl_id') == impl_id and
                row.get('compiler_item_id') == item_id and
                row.get('alias') == f'__a1_impl_{impl_id}_item_{item_id}_small_sort' and
                current_identity.get('alias') == row.get('alias') and
                current_identity.get('compiler_signature_digest') ==
                row.get('compiler_signature_digest') and
                isinstance(row.get('compiler_signature_digest'), str) and
                re.fullmatch(r'[0-9a-f]{64}', row['compiler_signature_digest']) is not None and
                row.get('actual_definition_bound_to_compiler_item') is True and
                row.get('native_matches_r_only_original_impl') is True,
                'P1 ' + impl + ' original-impl comparison/compiler identity failed')
        for map_key in ('positional_alpha_map', 'compiler_positional_region_map'):
            value = row.get(map_key)
            require(isinstance(value, (tuple, list)) and value and
                    all(isinstance(pair_row, (tuple, list)) and len(pair_row) == 2 and
                        all(isinstance(part, str) and part for part in pair_row)
                        for pair_row in value) and
                    len({pair_row[0] for pair_row in value}) == len(value) and
                    (map_key != 'compiler_positional_region_map' or
                     len({pair_row[1] for pair_row in value}) == len(value)),
                    'P1 ' + impl + ' ' + map_key + ' malformed or non-injective region map')
        row_hashes = _mapping(row.get('native_sha256'),
                              'P1 ' + impl + ' native hashes')
        require(set(row_hashes) == {'pre', 'returning', 'unwind'} and
                all(row_hashes.get(key) == native_hashes[key]
                    for key in ('pre', 'returning', 'unwind')),
                'P1 ' + impl + ' native component hashes differ from common contract')
    alpha_roles = gate.get('positional_alpha_roles')
    require(isinstance(alpha_roles, (tuple, list)) and bool(alpha_roles) and
            all(isinstance(role, str) and role for role in alpha_roles),
            'P1 compiler positional alpha roles missing')


def _body_case(case, observation, expected_input, expected_inventory, build_id):
    raw, structure = _source_observation(case, observation, expected_input, build_id)
    candidate = _mapping(observation.get('proof_candidate'), 'focused classifier')
    executed = _mapping(observation.get('execution_attestation'), 'focused execution attestation')
    impl = BODY[case]
    identity = _mapping(executed.get('compiler_identity'), 'compiler impl identity')
    expected = _mapping(expected_inventory.get(impl), 'expected impl identity')
    require(identity.get('impl') == impl and all(identity.get(key) == expected.get(key)
            for key in ('compiler_impl_id', 'compiler_item_id')),
            'body target is not the compiler-bound impl item')
    require(executed.get('body_count') == 1 and executed.get('focus_body_reached') is True and
            executed.get('focus_conformance_verified') is True and
            executed.get('normal_posts_preserved') is True and executed.get('unwind_posts_preserved') is True,
            'one actual body and full native conformance not established')
    require(structure.get('threshold_posts', {}).get('classification') == 'STRUCTURE_ONLY_UNRUN_PROOF',
            'native threshold AST gate absent')
    negative = case.startswith('N-')
    if negative:
        require(candidate.get('classification') == 'INTENDED_FOCUSED_FAILURE_CANDIDATE' and
                candidate.get('predicate') == 'result<=32' and
                candidate.get('target_reached') is True and
                candidate.get('error_context', {}).get('stage') == 'impl-body' and
                executed.get('focus_body_verified') is False and _stage_exit(raw, 'verification') not in (None, 0),
                'negative did not reach its own intended body post')
        location = 'mutated default threshold body' if impl == 'default16' else 'mutated Freeze threshold body'
        stage, predicate, outcome, classification = 'impl-body-post', 'result<=32', 'fail', 'NEGATIVE_INTENDED'
        body = dict(stage=stage, predicate=predicate, location=location, outcome='fail',
                    classification='runner-reported-intended-negative', target_reached=True,
                    failure_observed=True, verified=False)
        envelope = dict(stage='native-envelope-conformance', predicate='normal+unwind-posts-preserved',
                        location=location, outcome='pass', classification='runner-reported-conformance-preserved',
                        normal_posts_preserved=True, unwind_posts_preserved=True)
    else:
        require(candidate.get('classification') == 'FOCUSED_VF0_CANDIDATE' and
                candidate.get('candidate_passed') is True and candidate.get('body_verified') is True and
                executed.get('focus_body_verified') is True and _stage_exit(raw, 'verification') == 0,
                'positive actual body/conformance did not finish VF0')
        stage, predicate, outcome, classification = 'impl-body-and-conformance', '16<=result<=32', 'pass', 'NATIVE_INTENDED_PASS'
        location = 'default threshold body' if impl == 'default16' else 'Freeze threshold body'
        body = dict(stage='impl-body', predicate=predicate, location=impl + ' threshold item', outcome='pass',
                    classification='runner-reported-body-pass')
        envelope = dict(stage='native-envelope-conformance', predicate=predicate, location=impl + ' threshold item',
                        outcome='pass', classification='runner-reported-conformance-pass')
    return dict(stage=stage, predicate=predicate, location=location, outcome=outcome, classification=classification,
                focus_mode='actual-body-and-conformance', focus_only=True, body_count=1,
                focused_item_id=identity['compiler_item_id'], proof_kind='actual_body',
                compiler_identity=dict(identity), body=body, native_envelope=envelope,
                focus_body_reached=True, focus_body_verified=not negative, focus_conformance_verified=True)


def _caller_case(case, observation, expected_input, build_id):
    raw, structure = _source_observation(case, observation, expected_input, build_id)
    candidate = _mapping(observation.get('proof_candidate'), 'caller classifier')
    executed = _mapping(observation.get('execution_attestation'), 'caller execution attestation')
    require(executed.get('body_count') == 1 and executed.get('caller_body_reached') is True and
            structure.get('threshold_posts', {}).get('common_checked') is True and
            structure.get('caller_calls', {}).get('ast', {}).get('owner') == 'a1_guard_observer',
            'caller did not reach the compiler-bound observer using the checked summary')
    if case == 'P0c':
        require(candidate.get('classification') == 'FOCUSED_VF0_CANDIDATE' and
                candidate.get('body_verified') is True and executed.get('caller_body_verified') is True and
                _stage_exit(raw, 'verification') == 0, 'positive observer did not finish VF0')
        return dict(stage='caller-proof', predicate='len<=32-and-len+16<=48', location='guard observer assertions',
                    outcome='pass', classification='POSITIVE_INTENDED', focus_mode='caller-body', focus_only=True,
                    focus_target='a1_guard_observer', body_count=1, caller_body_reached=True,
                    caller_body_verified=True, assertions_reached=['len<=32', 'requirement<=48'])
    require(candidate.get('classification') == 'INTENDED_FOCUSED_FAILURE_CANDIDATE' and
            candidate.get('predicate') == 'len<=31' and candidate.get('target_reached') is True and
            candidate.get('intended_failure_observed') is True and executed.get('caller_body_verified') is False and
            _stage_exit(raw, 'verification') not in (None, 0),
            'false31 error is receipt/frontend/other predicate, or missing')
    return dict(stage='caller-assertion', predicate='len<=31', location='guard observer assertion', outcome='fail',
                classification='NEGATIVE_INTENDED', focus_mode='caller-body', focus_only=True,
                focus_target='a1_guard_observer', body_count=1, caller_body_reached=True,
                caller_body_verified=False, reached_predicate='len<=31', assertion_failure_observed=True)


def _interface(fields):
    return dict(**fields, focus_mode='interface-only', focus_only=True,
                focus_target='verified/lib.rs:0', body_count=0, interface_verified=True,
                case_credit=fields['classification'])


def classify_case(case_id, observation, *, expected_input, run_pins, build_id, expected_inventory):
    """Interpret one complete current observation; never run a scientific stage."""
    if observation is None:
        return dict(case_id=case_id, status='NOT_RUN', matrix_gate_passed=False, record=None, proof_credit=False)
    if isinstance(observation, Mapping) and observation.get('not_run') is True:
        return dict(case_id=case_id, status='NOT_RUN', matrix_gate_passed=False, record=None,
                    reason=observation.get('reason'), proof_credit=False)
    result = dict(case_id=case_id, status='INCONCLUSIVE', matrix_gate_passed=False, record=None, proof_credit=False)
    try:
        observation = _mapping(observation, 'case observation')
        require(observation.get('proof_credit') is False, 'observation improperly claims independent proof credit')
        require(all(isinstance(expected_input.get(key), str) and expected_input[key]
                    for key in ('source_id', 'unit_id')), 'constructed input identities missing')
        provenance = 'compiler-derived-focused-verifier'
        if case_id in BODY:
            fields = _body_case(case_id, observation, expected_input, expected_inventory, build_id)
        elif case_id == 'P0c':
            fields = _caller_case(case_id, observation, expected_input, build_id)
        elif case_id == 'N-false31':
            if observation.get('classification') == 'FALSE31_OWN_PAIR_RECEIPT_ISSUED_CALLER_BLOCKED':
                return {**result,
                        'reason': 'false31 caller/checked-helper prerequisite incomplete'}
            if observation.get('classification') == 'FALSE31_OWN_PAIR_RECEIPT_ISSUED_CALLER_STRUCTURE_UNAVAILABLE':
                return {**result,
                        'reason': 'false31 caller structure unavailable after own-pair receipt'}
            require(observation.get('classification') == 'FALSE31_OWN_PAIR_REPROVED_AND_CALLER_OBSERVED' and
                    observation.get('receipt_issued_after_both_bodies') is True,
                    'false31 own-pair receipt ordering not established')
            caller = _mapping(observation.get('caller_case'), 'false31 caller')
            raw = _mapping(caller.get('raw'), 'false31 caller raw')
            pair = raw.get('source_pair_sha256')
            require(isinstance(pair, Mapping) and observation.get('source_pair_sha256') == pair,
                    'false31 source pair differs')
            for body_id in ('P0a', 'P0b'):
                body = _mapping(observation.get('body_cases', {}).get(body_id), 'false31 own body target')
                impl = BODY[body_id]
                own_identity = body.get('execution_attestation', {}).get('compiler_identity', {})
                require(body.get('raw', {}).get('source_pair_sha256') == pair and
                        body.get('raw', {}).get('build_id') == build_id and
                        body.get('raw', {}).get('focus_case_id') == body_id and
                        body.get('raw', {}).get('source_id') == expected_input['source_id'] and
                        body.get('raw', {}).get('unit_id') == expected_input['unit_id'] and
                        own_identity.get('impl') == impl and
                        all(own_identity.get(key) == expected_inventory[impl].get(key)
                            for key in ('compiler_impl_id', 'compiler_item_id')) and
                        body.get('execution_attestation', {}).get('body_count') == 1 and
                        body.get('proof_candidate', {}).get('classification') == 'FOCUSED_VF0_CANDIDATE' and
                        body.get('execution_attestation', {}).get('focus_body_verified') is True and
                        body.get('execution_attestation', {}).get('focus_conformance_verified') is True,
                        'false31 missing own-pair actual threshold body/conformance proof')
            boundary = _mapping(observation.get('boundary_observation'), 'false31 boundary observation')
            require(boundary.get('classification') == 'LEN32_BOUNDARY_ADMISSIBLE_BY_CHECKED_INTERFACE_AND_GUARD' and
                    boundary.get('source_pair_sha256') == pair and
                    boundary.get('threshold_upper_bound') == boundary.get('boundary_len') == 32 and
                    boundary.get('guard_expression') == 'len <= T::small_sort_threshold()' and
                    boundary.get('boundary_satisfies_guard') is True and boundary.get('proof_credit') is False,
                    'threshold32/len32 boundary is not admitted by actual interface/guard')
            fields = _caller_case(case_id, caller, expected_input, build_id)
        elif case_id in ('P1', 'P-dispatch'):
            raw, structure = _source_observation(case_id, observation, expected_input, build_id)
            require(raw.get('focus') == 'verified/lib.rs:0' and _stage_exit(raw, 'verification') == 0,
                    'interface translation did not complete cleanly')
            if case_id == 'P1':
                _p1_interface_gate(structure.get('small_sort_interface'), raw,
                                   structure, expected_inventory, run_pins,
                                   observation, expected_input)
                labels = dict(stage='export-decode-refinement', predicate='full-interface-shape',
                              location='small_sort interface', outcome='pass', classification='POSITIVE_INTENDED')
            else:
                dispatch = _mapping(observation.get('dispatch_classifier'),
                                    'source-bound dispatch trace classifier')
                require(dispatch.get('classification') ==
                        'ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED' and
                        dispatch.get('proof_credit') is False and
                        dispatch.get('verification_exit') == 0 and
                        dispatch.get('source_sha256') == raw.get('source_pair_sha256', {}).get('verified'),
                        'original common dispatch trace identity is incomplete')
                expected_calls = {
                    ('quicksort', 'StableSmallSortTypeImpl::small_sort_threshold'),
                    ('quicksort', 'StableSmallSortTypeImpl::small_sort'),
                    ('a1_guard_observer', 'StableSmallSortTypeImpl::small_sort_threshold')}
                trace_rows = dispatch.get('trace_lines')
                require(isinstance(trace_rows, (tuple, list)) and len(trace_rows) == 3 and
                        all(isinstance(row, Mapping) for row in trace_rows),
                        'dispatch trace must retain all three joined owner/callee rows')
                trace_keys = [(row.get('owner'), row.get('callee')) for row in trace_rows]
                require(set(trace_keys) == expected_calls and len(set(trace_keys)) == 3 and
                        all(row.get('original') == row.get('callee') and
                            row.get('translated') == row.get('callee') and
                            row.get('redirect') is False and
                            isinstance(row.get('ast_call_span'), str) and
                            isinstance(row.get('mir_call_span'), str)
                            for row in trace_rows),
                        'dispatch rows are not a unique exact owner/callee/span join')
                trace_by_key = {(row.get('owner'), row.get('callee')): row
                                for row in trace_rows}
                caller_calls = _mapping(structure.get('caller_calls'),
                                        'paired dispatch caller structure')
                pair = _mapping(caller_calls.get('dispatch_pair'),
                                'both certified dispatch owners')
                require(set(pair) == {'quicksort', 'a1_guard_observer'},
                        'dispatch caller owners are missing or ambiguous')
                for owner in ('quicksort', 'a1_guard_observer'):
                    entry = _mapping(pair.get(owner), owner + ' MIR/AST binding')
                    mir = _mapping(entry.get('mir'), owner + ' compiler MIR binding')
                    binding = _mapping(mir.get('binding'), owner + ' caller binding')
                    ast = _mapping(entry.get('ast'), owner + ' AST call structure')
                    calls = binding.get('calls')
                    ast_calls = ast.get('calls')
                    expected_names = (['StableSmallSortTypeImpl::small_sort_threshold',
                                       'StableSmallSortTypeImpl::small_sort']
                                      if owner == 'quicksort' else
                                      ['StableSmallSortTypeImpl::small_sort_threshold'])
                    case_binding = _mapping(binding.get('case_binding'),
                                            owner + ' source-pair binding')
                    require(binding.get('caller') == owner and
                            case_binding.get('case_id') == 'P-dispatch' and
                            case_binding.get('generated_source_sha256') == dispatch.get('source_sha256') and
                            binding.get('proof_credit') is False and
                            ast.get('owner') == owner and
                            ast.get('classification') == 'CALL_AST_STRUCTURE_ONLY' and
                            ast.get('proof_credit') is False and
                            isinstance(calls, (tuple, list)) and
                            [row.get('callee') for row in calls if isinstance(row, Mapping)] == expected_names and
                            len(calls) == len(expected_names) and
                            isinstance(ast_calls, (tuple, list)) and
                            [row.get('callee') for row in ast_calls if isinstance(row, Mapping)] == expected_names and
                            len(ast_calls) == len(expected_names),
                            owner + ' dispatch source/MIR/AST join is incomplete')
                    for mir_call, ast_call in zip(calls, ast_calls):
                        joined = trace_by_key[(owner, mir_call['callee'])]
                        mir_span = mir_call.get('mir_call_span_ast')
                        ast_span = ast_call.get('ast_call_span_bounds')
                        require(_source_bounds_text(mir_span) is not None and
                                _source_bounds_text(ast_span) is not None and
                                joined.get('ast_call_span') == ast_call.get('ast_call_span') and
                                joined.get('mir_call_span') ==
                                _source_bounds_text(mir_span) and
                                ast_span[0][1] == mir_call.get('call_line') and
                                mir_span[0][1] == mir_call.get('call_line'),
                                owner + ' dispatch trace spans do not match their AST/MIR records')
                labels = dict(stage='translated-call-gate', predicate='original-common-trait-item',
                              location='threshold/small_sort call AST', outcome='pass', classification='POSITIVE_INTENDED')
            fields = _interface(labels)
        elif case_id in SYNTHETIC:
            provenance = 'synthetic-transport-control'
            messages = observation.get('messages')
            require(isinstance(messages, (tuple, list)) and tuple(x.get('mutation') for x in messages) == SYNTHETIC[case_id],
                    'isolated synthetic mutation family incomplete')
            require(tuple(x.get('transport', {}).get('decoded_input_sha256') for x in messages) ==
                    tuple(expected_input.get('synthetic_input_sha256', ())), 'synthetic input hashes differ')
            for message in messages:
                transport = _mapping(message.get('transport'), 'synthetic transport stage')
                classifier = _mapping(message.get('classifier'), 'synthetic stage classifier')
                require(transport.get('build_id') == build_id and
                        transport.get('synthetic') is True and transport.get('compiler_derived') is False and
                        transport.get('refinement_derived') is False and classifier.get('proof_credit') is False and
                        classifier.get('compiler_derived') is False and classifier.get('refinement_derived') is False,
                        'synthetic input given compiler/refinement/proof provenance')
                require(_stage_exit(transport, 'synthetic-encode') == 0 and
                        isinstance(_stage_exit(transport, 'synthetic-translator'), int), 'synthetic transport not executed')
                expected_class = 'SYNTHETIC_REPRESENTATION_ACCEPTED' if case_id == 'N-alpha-valid' else 'SYNTHETIC_REFUSAL_OBSERVED'
                require(classifier.get('classification') == expected_class and classifier.get('summary_available') is False,
                        'synthetic translator stopped before intended gate or had another diagnostic')
            stage, predicate, location = SYNTHETIC_LABELS[case_id]
            fields = _interface(dict(stage=stage, predicate=predicate, location=location,
                                    outcome='accept-representation' if case_id == 'N-alpha-valid' else 'refuse',
                                    classification='REPRESENTATION_ONLY' if case_id == 'N-alpha-valid' else 'NEGATIVE_INTENDED'))
        elif case_id in ('N-source', 'N-binding', 'N-region-swap', 'N-clause-redirect'):
            provenance = 'synthetic-admission-control'
            require(observation.get('input_identity_verified') is True and
                    isinstance(expected_input.get('control_input_sha256'), str) and
                    len(expected_input['control_input_sha256']) == 64 and
                    observation.get('input_sha256') == expected_input.get('control_input_sha256') and
                    observation.get('source_id') == expected_input['source_id'] and
                    observation.get('unit_id') == expected_input['unit_id'], 'admission control input continuity missing')
            classifier = observation.get('classifier', observation)
            if case_id == 'N-source':
                require(classifier.get('classification') == 'SOURCE_CERTIFICATE_REFUSAL_OBSERVED', 'source refusal was not intended')
                labels = ('source-admission', 'exact-source-and-item-identity', 'source certificate')
            elif case_id == 'N-binding':
                require(classifier.get('classification') == 'CALL_BINDING_CLAIM_REFUSAL_OBSERVED', 'binding refusal was not intended')
                labels = ('call-binding-admission', 'original-generic-trait-binding', 'translated trait call')
            elif case_id == 'N-region-swap':
                require(classifier.get('classification') == 'INPUT_REGION_ROLE_REFUSAL_OBSERVED', 'region-role refusal was not at caller binding admission')
                labels = ('call-binding-admission', 'compiler-input-region-map', 'generic trait call binding')
            else:
                require(classifier.get('classification') == 'LEGACY_REDIRECT_REFUSAL_OBSERVED', 'legacy redirect refusal was not intended')
                labels = ('translated-call-gate', 'no-clause-ignoring-impl-redirect', 'dispatch trace and call AST')
            fields = _interface(dict(stage=labels[0], predicate=labels[1], location=labels[2],
                                     outcome='refuse', classification='NEGATIVE_INTENDED'))
        elif case_id == 'OFF' or case_id in REGRESSIONS:
            provenance = 'default-off-baseline' if case_id == 'OFF' else 'fresh-final-tool-regression'
            require(observation.get('input_identity_verified') is True and
                    observation.get('source_id') == expected_input['source_id'] and
                    observation.get('unit_id') == expected_input['unit_id'], 'current fixture input continuity missing')
            if case_id == 'OFF':
                require(observation.get('classification') == 'OFF_BASELINE_OBSERVATION_ONLY' and
                        observation.get('duplicate_trait_parameter_at_source_declaration') is True and
                        'Duplicate type parameter' in (observation.get('first_diagnostic') or '') and
                        observation.get('source_pair_immutable') is True,
                        'OFF did not reproduce exact source-bound duplicate trait parameter')
                fields = dict(stage='frontend', predicate='duplicate-trait-parameter', location='trait declaration',
                              outcome='baseline', classification='BASELINE_ONLY', focus_mode='none', focus_only=False)
            else:
                location, predicate = REGRESSIONS[case_id]
                negative = predicate is not None
                require(observation.get('gate_passed') is True and observation.get('paired_support_passed') is True and
                        observation.get('proof_ast_captured') is True and observation.get('source_pair_immutable') is True and
                        observation.get('classification') == ('INTENDED_ASSERTION_NEGATIVE_RAW_REVIEW_REQUIRED' if negative else
                            'FRESH_VF0_CANDIDATE_RAW_REVIEW_REQUIRED'), 'regression did not reach its intended current gate')
                require(observation.get('first_causal_stage') == ('verification' if negative else 'NONE_OBSERVED'),
                        'regression failed before intended stage')
                fields = dict(stage='verification' if negative else 'NONE_OBSERVED',
                              predicate=predicate or 'full normal/unwind/free/leak/dead-code obligations', location=location,
                              outcome='fail' if negative else 'pass', classification='NEGATIVE_INTENDED' if negative else 'POSITIVE_INTENDED',
                              focus_mode='none', focus_only=False)
        else:
            raise ObservationError('unknown matrix case')
        record = {**dict(run_pins), **fields, 'case_id': case_id,
                  'source_id': expected_input['source_id'], 'unit_id': expected_input['unit_id'],
                  'build_id': build_id, 'record_kind': 'runner_attestation', 'skipped': False,
                  'proof_credit': False, 'evidence_provenance': provenance}
        return {**result, 'status': 'INTENDED_CLASSIFIED', 'matrix_gate_passed': True,
                'record': record, 'provenance': provenance, 'observed_classification': fields['classification']}
    except (ObservationError, KeyError, TypeError, AttributeError, ValueError) as exc:
        return {**result, 'reason': str(exc)}
