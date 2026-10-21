"""Pure interpretation of current A1 observations into workflow records.

No expectation tuple is an observed verdict. Each route below first requires
its own executed stages, classifier and input identity before emitting the
semantic stage/predicate/location labels checked by A1Admission. These remain
runner reports, never independent proof credit. No files or tools are read.
"""
from __future__ import annotations

from collections.abc import Mapping

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
                gate = _mapping(structure.get('small_sort_interface'), 'full small_sort P1 gate')
                require(gate.get('structural_pass') is True and gate.get('body_count') == 0 and
                        gate.get('proof_credit') is False and set(gate.get('impls', {})) == {'default16', 'freeze32'} and
                        gate.get('compiler_clauses_source_bound') is True and
                        all(row.get('native_matches_r_only_baseline') is True for row in gate['impls'].values()),
                        'full compiler-bound native P1 comparison incomplete')
                labels = dict(stage='export-decode-refinement', predicate='full-interface-shape',
                              location='small_sort interface', outcome='pass', classification='POSITIVE_INTENDED')
            else:
                require(observation.get('dispatch_classifier', {}).get('classification') ==
                        'ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED' and
                        structure.get('caller_calls', {}).get('ast', {}).get('classification') == 'CALL_AST_STRUCTURE_ONLY',
                        'original common dispatch not observed in both trace and AST')
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
