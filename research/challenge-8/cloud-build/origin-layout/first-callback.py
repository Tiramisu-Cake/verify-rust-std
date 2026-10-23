#!/usr/bin/env python3
"""Cloud-only first actual comparator campaign. Import has no side effects.

The prefix is mechanically cut immediately before tail.read, and never stands
in for the complete actual insert_tail. Full-body final posts stay unchanged.
"""
from __future__ import annotations
import hashlib
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
PROFILE = 'experimental-merge-guard-addressability-v1'
R5_PROFILE = 'experimental-merge-guard-addressability-emitter-r5-v1'
R7_PROFILE = 'experimental-merge-late-callback-recovery-r7-v1'
R8_PROFILE = 'experimental-merge-owned-array-allocation-r8-v1'
R9_PROFILE = 'experimental-merge-guard-current-return-r9-v1'
R10_PROFILE = 'experimental-merge-moving-gap-r10-v1'
R11_PROFILE = 'experimental-merge-label-storage-r11-v1'
R22_PROFILE = R11_PROFILE
R11_LABEL_TRACE_ENV = 'SMALLSORT_R11_LABEL_STORAGE_TRACE'
R11_LABEL_PLACEMENT_ENV = 'SMALLSORT_R11_LABEL_STORAGE_PLACEMENT'
R9_GUARD_RETURN_RECOVERY_ENV = 'SMALLSORT_R9_GUARD_RETURN_RECOVERY'
R17_PHASE_ID = 'MERGE-CALLER-REFINEMENT-R17-2026-10-21'
R17_CANDIDATE_TOOL_COMMIT = 'a66c1d30214e463a16a325cdef30b0ec8555e0af'
R17_PROFILE_REGISTRATION = {
    'schema': 'merge-r17-profile-registration-v1',
    'phase_id': R17_PHASE_ID,
    'baseline_profile_path': 'research/challenge-8/cloud-build/origin-layout/R17-BASELINE-PROFILE-20261021.json',
    'starting_tool_commit': '660b576b6b1608db913c51e0785b443a8733396f',
    'starting_source_sha': '6fd50c699500cbac5c65912174d4aa49b49db19f',
    'owner': 'merge', 'lane': 'merge',
    'candidate_tool_commit': R17_CANDIDATE_TOOL_COMMIT,
    'tool_source_paths': ['src/refinement_checker/refinement_checker.ml'],
    'source_applicability': ('paired RawPtr bare local only; exact mutability/full MIR and decoded local type/place; '
                             'existing equal-state allocation reconciliation; no borrow or memory authority'),
}
R19_PHASE_ID = 'MERGE-UNWIND-CLEANUP-R19-2026-10-22'
R19_CANDIDATE_TOOL_COMMIT = '39f6b0cacd00575c8ca2d39e9f15632723bf1227'
R19_PROFILE_REGISTRATION = {
    'schema': 'merge-r19-profile-registration-v1',
    'phase_id': R19_PHASE_ID,
    'baseline_profile_sha256': '947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d',
    'starting_tool_commit': R17_CANDIDATE_TOOL_COMMIT,
    'starting_source_sha': '6fd50c699500cbac5c65912174d4aa49b49db19f',
    'owner': 'merge', 'lane': 'merge',
    'candidate_tool_commit': R19_CANDIDATE_TOOL_COMMIT,
    'tool_source_paths': ['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
    'source_applicability': ('one marked checked ghost block after the single insert_tail call in '
                             'b2_three_from_local, also on its Continue unwind edge; no posts, '
                             'runtime, CFG or trusted premise change'),
}
R20_METADATA_TOOL_COMMIT = '578120769161e217e53bd569bafdccbd4b2e020e'
R20_METADATA_PROFILE_SHA256 = '949633103e909f27a721573ae88f4d3180278de5bcc2c60031239f93fe0b0301'
R20_METADATA_EXPORTER_SHA256 = '8bcb126ea684d1c671b96425940b0d24904fdaa3beb69a09316bd222316fca42'
R20_METADATA_SCHEMA_SHA256 = 'a894cfc85246c0c33b239c0ee5b729762475f79f46931546937f082e1a6ad7c5'
R20_METADATA_REFINER_CORE_SHA256 = '7be8a6f16ce45173866bddcc6b6d606ac4ef2a6748885eca1fc982611c753614'
R20_METADATA_PATCH_SHA256 = '3112458ee12910ea17f69465a271d2cda848c7e50223a4b0c2b30c5e892ea33b'
# The candidate includes the exporter compile fixes and the later synthetic-Lifetime translator fix.
R22_COMPILE_FIX_PROFILE_SHA256 = 'd2640ee7088ecfe61c8115bc27df81c45e77742ce990295c22cdf6de90eb7579'
R22_COMPILE_FIX_TOOL_COMMIT = '65f0bb35e4f188cf8ce405a67253127173c5c3a1'
R22_COMPILE_FIX_EXPORTER_SHA256 = '0b456d055d498429c3da5bd4b7a1eb455b1b691bb0133a5f61bb449aad4e4345'
R22_COMPILE_FIX_PATCH_SHA256 = '6d76e07dec9b8d3e093e442d74ed9b930f6e9b85da3d0ea74e912a8a94b7f20d'
R22_COMPILE_FIX_TRANSLATOR_SHA256 = 'e5fe47a16b1a94dcfd07d7d7c0355d4e5acb999650f00498d11606909960dde2'
R22_COMPILE_FIX_REGISTRATION = {
    'schema': 'merge-r22-compile-fix-registration-v1',
    'phase_id': 'MERGE-CALLER-ACCEPTANCE-R22-2026-10-23',
    'baseline_profile_sha256': R20_METADATA_PROFILE_SHA256,
    'starting_tool_commit': R20_METADATA_TOOL_COMMIT,
    'candidate_tool_commit': R22_COMPILE_FIX_TOOL_COMMIT,
    'tool_source_paths': ['src/rust_frontend/vf_mir_exporter/src/lib.rs', 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
    'source_applicability': ('compile-only Rust fixes: reborrow the erased-region Cap’n Proto builder before initializing identity; import the generated pointer-coercion data module; initialize identity=Nothing on three synthetic Lifetime records. No emitted MIR, schema, refinement, proof, runtime, CFG, postcondition, or control change.'),
}
R20_METADATA_REGISTRATION = {
    'schema': 'merge-r20-source-preserving-metadata-registration-v1',
    'phase_id': 'MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23',
    'baseline_profile_sha256': '1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb',
    'starting_tool_commit': R19_CANDIDATE_TOOL_COMMIT,
    'starting_source_sha': '6fd50c699500cbac5c65912174d4aa49b49db19f',
    'owner': 'merge', 'lane': 'merge',
    'candidate_tool_commit': R20_METADATA_TOOL_COMMIT,
    'tool_source_paths': ['src/refinement_checker/refinement_checker.ml',
                          'src/rust_frontend/vf_mir/vf_mir.capnp',
                          'src/rust_frontend/vf_mir_exporter/src/lib.rs'],
    'source_applicability': 'source-preserving MIR metadata: real CastData.sourceTy is encoded as Some(exact operand type); the schema permits None, and synthetic built-in Cast fixtures explicitly use None. Pointer-coercion metadata remains exact when present. Inference-region identity remains body-scoped; synthetic fixture regions use identity None and empty region_scope_id, never an inferred identity. Retains diagnostic-only context for the existing unequal LocalAddressTaken refusal (function, paired block/command positions and full listings, same standalone fatal diagnostic) and the prior closed-usize Value/Leaf interpreter case (UIntPtrWidth outer/value type match, scalar size 1..8 and bits fit). Strict RawPtr projected-place classifier unchanged; other index cases unsupported/inconclusive; no pointer, resource, lifetime or memory-model rule.',
}
BODY_ISOLATION_NAME = 'actual_insert_tail_body_isolated'
RAW_LOCAL_CALLER_NAME = 'actual_three_from_local_raw'
SUPPORTED_PROFILES = (PROFILE, R5_PROFILE, R7_PROFILE, R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE)
R9_GUARD_TRACE_ENV = 'SMALLSORT_R9_GUARD_TRACE'
PREFIX_NAME = b'insert_tail_first_callback_prefix'
CUT = b'        // SAFETY: after this read'

SINGLETON_FACTS = b"""    //@ length_drop(1, xs);
    //@ length_take(1, drop(1, xs));
    //@ length_drop(1, drop(1, xs));
    //@ note(length(take(1, drop(1, xs))) == 1);
    //@ note(length(drop(1, drop(1, xs))) == 1);
    //@ drop_length(drop(1, drop(1, xs)));
"""

ENTRY_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(head(take(1, drop(1, xs))));
        //@ close own::<u64>(t)(head(drop(1, drop(1, xs))));
        //@ close foreach(take(1, drop(1, xs)), own::<u64>(t));
        //@ close foreach(drop(1, drop(1, xs)), own::<u64>(t));
        //@ close array::<u64>(sift, 1, take(1, drop(1, xs)));
        //@ close array::<u64>(tail, 1, drop(1, drop(1, xs)));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_join(drop(1, xs), own::<u64>(t), 1);
        //@ foreach_join(xs, own::<u64>(t), 1);
"""
CURRENT_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(current_sift);
        //@ close own::<u64>(t)(current_tail);
        //@ close foreach(cons(current_sift, nil), own::<u64>(t));
        //@ close foreach(cons(current_tail, nil), own::<u64>(t));
        //@ close array::<u64>(sift, 1, cons(current_sift, nil));
        //@ close array::<u64>(tail, 1, cons(current_tail, nil));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_append(cons(current_sift, nil), cons(current_tail, nil));
        //@ foreach_append(take(1, xs), append(cons(current_sift, nil), cons(current_tail, nil)));
"""


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'missing pinned module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _r17_registration_matches(profile_path, selected_profile, validated_receipt):
    try:
        profile = json.loads(Path(profile_path).read_text())
        registration = profile.get('r17_registration')
        return (selected_profile == R11_PROFILE and profile.get('profile') == selected_profile and
                type(validated_receipt) is dict and validated_receipt.get('profile') == selected_profile and
                type(registration) is dict and registration == R17_PROFILE_REGISTRATION and
                (profile.get('effective_tool_commit') == R17_CANDIDATE_TOOL_COMMIT or
                 (profile.get('effective_tool_commit') == R19_CANDIDATE_TOOL_COMMIT and
                  profile.get('r19_registration') == R19_PROFILE_REGISTRATION) or
                 _r20_metadata_registration_matches(profile_path, selected_profile, profile) or
                 _r22_compile_fix_registration_matches(profile_path, selected_profile, profile)))
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return False


def _r19_registration_matches(profile_path, selected_profile):
    try:
        profile = json.loads(Path(profile_path).read_text())
        return (selected_profile == R11_PROFILE and profile.get('profile') == selected_profile and
                profile.get('r19_registration') == R19_PROFILE_REGISTRATION and
                (profile.get('effective_tool_commit') == R19_CANDIDATE_TOOL_COMMIT or
                 _r20_metadata_registration_matches(profile_path, selected_profile, profile) or
                 _r22_compile_fix_registration_matches(profile_path, selected_profile, profile)))
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return False


def _r20_metadata_registration_matches(profile_path, selected_profile, profile=None):
    try:
        raw = Path(profile_path).read_bytes()
        if _sha(raw) != R20_METADATA_PROFILE_SHA256:
            return False
        if profile is None:
            profile = json.loads(raw)
        chain = profile.get('ordered_patch_chain')
        return (selected_profile == R11_PROFILE and profile.get('profile') == R11_PROFILE and
                profile.get('r19_registration') == R19_PROFILE_REGISTRATION and
                profile.get('r20_metadata_registration') == R20_METADATA_REGISTRATION and
                profile.get('effective_tool_commit') == R20_METADATA_TOOL_COMMIT and
                profile.get('exporter_source_sha256') == R20_METADATA_EXPORTER_SHA256 and
                profile.get('schema_sha256') == R20_METADATA_SCHEMA_SHA256 and
                profile.get('refiner_core_source_sha256') == R20_METADATA_REFINER_CORE_SHA256 and
                profile.get('guard_return_trace_patch_sha256') == R20_METADATA_PATCH_SHA256 and
                type(chain) is list and len(chain) == 19 and type(chain[-1]) is dict and
                chain[-1].get('path') == 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch' and
                chain[-1].get('sha256') == R20_METADATA_PATCH_SHA256)
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return False


def _r22_compile_fix_registration_matches(profile_path, selected_profile, profile=None):
    try:
        raw = Path(profile_path).read_bytes()
        if _sha(raw) != R22_COMPILE_FIX_PROFILE_SHA256:
            return False
        if profile is None:
            profile = json.loads(raw)
        chain = profile.get('ordered_patch_chain')
        if not (selected_profile == R22_PROFILE and profile.get('profile') == R22_PROFILE and
                profile.get('r19_registration') == R19_PROFILE_REGISTRATION and
                profile.get('r20_metadata_registration') == R20_METADATA_REGISTRATION and
                profile.get('r22_compile_fix_registration') == R22_COMPILE_FIX_REGISTRATION and
                profile.get('effective_tool_commit') == R22_COMPILE_FIX_TOOL_COMMIT and
                profile.get('exporter_source_sha256') == R22_COMPILE_FIX_EXPORTER_SHA256 and
                profile.get('translator_sha256') == R22_COMPILE_FIX_TRANSLATOR_SHA256 and
                profile.get('guard_return_trace_patch_sha256') == R22_COMPILE_FIX_PATCH_SHA256 and
                type(chain) is list and len(chain) == 19 and type(chain[-1]) is dict and
                chain[-1].get('path') == 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch' and
                chain[-1].get('sha256') == R22_COMPILE_FIX_PATCH_SHA256):
            return False
        reversed_profile = dict(profile)
        reversed_profile.pop('r22_compile_fix_registration', None)
        reversed_profile['profile'] = R11_PROFILE
        reversed_profile['effective_tool_commit'] = R20_METADATA_TOOL_COMMIT
        reversed_profile['exporter_source_sha256'] = R20_METADATA_EXPORTER_SHA256
        reversed_profile['translator_sha256'] = '1cb46fbbf1aed7654766c820a33ef3651139efa877e1ef3b13a25b02d9897c8b'
        reversed_profile['guard_return_trace_patch_sha256'] = R20_METADATA_PATCH_SHA256
        reversed_profile['ordered_patch_chain'] = list(chain)
        reversed_profile['ordered_patch_chain'][-1] = {
            'path': 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch',
            'sha256': R20_METADATA_PATCH_SHA256,
        }
        reversed_bytes = (json.dumps(reversed_profile, indent=2, ensure_ascii=False) + '\n').encode()
        return _sha(reversed_bytes) == R20_METADATA_PROFILE_SHA256
    except (OSError, json.JSONDecodeError, AttributeError, TypeError, UnicodeDecodeError):
        return False


def _r19_raw_case_matches(evidence, raw_case):
    try:
        record = json.loads((Path(evidence) / 'raw_local_caller' / 'preparation.json').read_text())
        return (type(record) is dict and record.get('case') == RAW_LOCAL_CALLER_NAME and
                record.get('verified_sha256') == _sha((raw_case / 'verified/lib.rs').read_bytes()) and
                record.get('original_sha256') == _sha((raw_case / 'original/lib.rs').read_bytes()))
    except (OSError, json.JSONDecodeError, AttributeError, TypeError):
        return False


def _run_raw_local_caller_after_controls(controls_result, diagnostic):
    result = diagnostic()
    result['rawptr_controls'] = {
        'classification': controls_result.get('classification') if type(controls_result) is dict else None,
        'all_matched': type(controls_result) is dict and controls_result.get('all_matched') is True,
        'proof_credit': False}
    return result


def _rawptr_controls_summary(controls_result):
    return {'classification': controls_result.get('classification') if type(controls_result) is dict else None,
            'all_matched': type(controls_result) is dict and controls_result.get('all_matched') is True,
            'proof_credit': False}


def _run_r17_controls_if_registered(enabled, captured, run):
    if not enabled:
        return dict(classification='NOT_APPLICABLE_R17_REGISTRATION_ABSENT',
                    all_matched=False,
                    reason='selected GLUE profile lacks the exact validated R17 registration',
                    accepted=False, proof_credit=False, b2_achieved=False)
    if (captured is None or captured.get('preparation_sha256') is None or
            captured.get('full_body_execution_observation') is None):
        raise ValueError('pre-dispatch full-body identity/receipt capture is incomplete')
    if captured.get('receipt_error') is not None:
        return dict(classification='INCONCLUSIVE', all_matched=False,
                    reason='pre-dispatch full-body preparation receipt capture failed',
                    accepted=False, proof_credit=False, b2_achieved=False)
    return run()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _one(data, old, new, label):
    if data.count(old) != 1:
        raise ValueError(f'{label}: expected one exact anchor')
    return data.replace(old, new, 1)


def _add_singleton_facts(source):
    anchor = b"    //@ let cmp_k = begin_lifetime();\n"
    return _one(source, anchor, SINGLETON_FACTS + anchor,
                'pure singleton length facts before callback lifetime')


TAIL_READ_OPEN = b"""        //@ assert array::<u64>(begin, 3, ?read_current);
        //@ array_split::<u64>(begin, 2);
        //@ open array::<u64>(tail, 1, drop(2, read_current));
"""


def _open_tail_read(source):
    anchor = b'        let tmp = ManuallyDrop::new(tail.read());\n'
    return _one(source, anchor, TAIL_READ_OPEN + anchor,
                'open CURRENT tail singleton before original read')


TMP_REFERENCE_INIT = b"""        //@ let r4_tmp_ref = precreate_ref::<u64>(&tmp);
        //@ init_ref_readonly::<u64>(r4_tmp_ref, 1/2);
"""


GUARD_EMPTY_TAIL_HELPER = b"""/*@
lem r7_guard_empty_tail(p: *u64)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& [1/4]array::<u64>(p + 1, 0, nil);
{
    points_to_limits::<u64>(p);
    assert pointer_within_limits(p + 1) == true;
    close [1/4]array::<u64>(p + 1, 0, nil);
}
@*/
"""


def _prepare_guard_empty_tail(source):
    anchor = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
    return _one(source, anchor, anchor +
                b'        //@ r7_guard_empty_tail(gap_guard.src as *mut u64);\n'
                b'        //@ initialized_storage_alignment(gap_guard.src as *mut u64);\n'
                b'        //@ points_to_limits::<u64>(gap_guard.src as *mut u64);\n'
                b'        //@ assert gap_guard.src as usize != 0;\n'
                b'        //@ assert gap_guard.src as usize % std::mem::align_of::<u64>() == 0;\n'
                b'        //@ assert object_pointer_within_limits(gap_guard.src, std::mem::size_of::<u64>()) == true;\n'
                b'        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<u64>();\n',
                'checked empty array tail at original guard reference provenance')


def _prepare_tmp_reference(source):
    anchor = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
    return _one(source, anchor, TMP_REFERENCE_INIT + anchor,
                'checked reference initialization before original guard')


FIRST_SHIFT_PREP = b"""        //@ note(sift == begin + 1);
        //@ array_split::<u64>(begin, 1);
        //@ assert array::<u64>(sift, 1, ?r4_shift_current);
        //@ open array::<u64>(sift, 1, r4_shift_current);
        //@ initialized_storage_alignment(sift);
        //@ points_to_limits::<u64>(sift);
        //@ uninitialized_storage_alignment(gap_guard.dst);
        //@ points_to__limits::<u64>(gap_guard.dst);
        //@ assert sift as usize != 0;
        //@ assert gap_guard.dst as usize != 0;
        //@ assert sift as usize % std::mem::align_of::<u64>() == 0;
        //@ assert gap_guard.dst as usize % std::mem::align_of::<u64>() == 0;
        //@ assert object_pointer_within_limits(sift, std::mem::size_of::<u64>()) == true;
        //@ assert object_pointer_within_limits(gap_guard.dst, std::mem::size_of::<u64>()) == true;
        //@ assert sift as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ assert gap_guard.dst as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ assert sift as usize + std::mem::size_of::<u64>() <= gap_guard.dst as usize;
"""


def _prepare_first_shift(source):
    anchor = b'        loop {\n'
    return _one(source, anchor, FIRST_SHIFT_PREP +
                b'        //@ let r5_late_k = begin_lifetime();\n' + anchor +
                b"            /*@ let_lft 'late = r5_late_k; @*/\n",
                'CURRENT first shift and block-start late lifetime binding')


R10_MOVING_GAP_INVARIANT = b"""            /*@ inv thread_token(t) &*& t == currentThread &*&
                lifetime_token(func_lft) &*& type_interp::<u64>() &*& type_interp::<F>() &*&
                *is_less |-> ?r10_f &*& <F>.own(t, r10_f) &*&
                foreach(?r10_previous_owners, own::<u64>(t)) &*&
                tail == begin + 2 &*&
                gap_guard.src |-> ?r10_src &*& gap_guard.dst |-> ?r10_dst &*&
                gap_guard.len |-> 1 &*& struct_CopyOnDrop_padding(&gap_guard) &*&
                r10_src as *mut u64 == r4_tmp_ref &*&
                ref_readonly_end_token::<u64>(r4_tmp_ref, &tmp, 1/4) &*&
                ref_initialized::<u64>(r4_tmp_ref) &*&
                [1/4](*r4_tmp_ref |-> _) &*& [1/4]array::<u64>(r4_tmp_ref + 1, 0, nil) &*&
                [1/4](*&tmp |-> _) &*&
                array::<u64>(begin, 1, ?r10_first_current) &*&
                *(begin + 1) |-> _ &*& array::<u64>(tail, 0, nil) &*&
                array::<u64>(tail + 1, 0, nil) &*&
                if sift == begin + 1 {
                    r10_dst == tail &*& *tail |-?-> _
                } else {
                    sift == begin &*& r10_dst == begin + 1 &*& *tail |-> _
                };
            @*/
"""

R11_MOVING_GAP_INVARIANT = (R10_MOVING_GAP_INVARIANT
    .replace(b"[1/4](*r4_tmp_ref |-> _) ", b"[1/4](*r4_tmp_ref |-> ?r11_ref_current) ")
    .replace(b"[1/4](*&tmp |-> _) ", b"[1/4](*&tmp |-> ?r11_tmp_current) ")
    .replace(b"                *(begin + 1) |-> _ &*& array::<u64>(tail, 0, nil) &*&\n",
             b"                array::<u64>(tail, 0, nil) &*&\n")
    .replace(b"                    r10_dst == tail &*& *tail |-?-> _\n",
             b"                    *(begin + 1) |-> ?r11_middle_current &*&\n"
             b"                    r10_dst == tail &*& *tail |-?-> _\n")
    .replace(b"                    sift == begin &*& r10_dst == begin + 1 &*& *tail |-> _\n",
             b"                    sift == begin &*& r10_dst == begin + 1 &*&\n"
             b"                    *(begin + 1) |-?-> _ &*& *tail |-> ?r11_tail_current\n"))

R10_ITERATION_PREP = b"""            /*@ if sift == begin {
                open array::<u64>(begin, 1, r10_first_current);
                open array::<u64>(begin + 1, 0, _);
            } @*/
            //@ initialized_storage_alignment(sift);
            //@ points_to_limits::<u64>(sift);
            //@ uninitialized_storage_alignment(gap_guard.dst);
            //@ points_to__limits::<u64>(gap_guard.dst);
            //@ assert sift as usize != 0;
            //@ assert gap_guard.dst as usize != 0;
            //@ assert sift as usize % std::mem::align_of::<u64>() == 0;
            //@ assert gap_guard.dst as usize % std::mem::align_of::<u64>() == 0;
            //@ assert object_pointer_within_limits(sift, std::mem::size_of::<u64>()) == true;
            //@ assert object_pointer_within_limits(gap_guard.dst, std::mem::size_of::<u64>()) == true;
            //@ assert sift as usize <= usize::MAX - std::mem::size_of::<u64>();
            //@ assert gap_guard.dst as usize <= usize::MAX - std::mem::size_of::<u64>();
            //@ assert sift as usize + std::mem::size_of::<u64>() <= gap_guard.dst as usize;
"""

R10_BREAK_PREP = b"""        /*@ if gap_guard.dst == begin {
            assert *(begin + 1) |-> ?r10_written_current;
            close array::<u64>(begin + 1, 1, cons(r10_written_current, nil));
        } @*/
"""


def _prepare_r10_moving_gap(source, *, profile=R10_PROFILE):
    invariant = R11_MOVING_GAP_INVARIANT if profile == R11_PROFILE else R10_MOVING_GAP_INVARIANT
    anchor = b"        loop {\n            /*@ let_lft 'late = r5_late_k; @*/\n"
    source = _one(source, anchor,
                  b"        //@ open array::<u64>(tail, 0, _);\n"
                  b"        //@ close array::<u64>(tail, 0, nil);\n"
                  b"        //@ open array::<u64>(tail + 1, 0, _);\n"
                  b"        //@ close array::<u64>(tail + 1, 0, nil);\n"
                  b"        loop {\n" +
                  b"            /*@ let_lft 'late = r5_late_k; @*/\n" +
                  invariant + R10_ITERATION_PREP,
                  'checked moving-gap invariant first at actual loop head')
    anchor = b"        }\n    }\n    /*@ {\n        guard_current_return_recover();"
    return _one(source, anchor, b"        }\n" + R10_BREAK_PREP +
                b"    }\n    /*@ {\n        guard_current_return_recover();",
                'checked physical break normalization before original implicit Drop')


U64_SHARE_REPRESENTATION = b"""/*@
pred r6_u64_share(k: lifetime_t, t: thread_id_t, p: *u64) =
    frac_borrow(k, u64_full_borrow_content(t, p));
type_pred_def <u64>.share = r6_u64_share;

lem r6_close_u64_share(k: lifetime_t, t: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p));
    ens [_](<u64>.share)(k, t, p);
{
    assert [?r6_share_fraction]frac_borrow(k, u64_full_borrow_content(t, p));
    close [r6_share_fraction]r6_u64_share(k, t, p);
    leak [r6_share_fraction]r6_u64_share(k, t, p);
}

lem r6_u64_share_mono(k: lifetime_t, k1: lifetime_t, t: thread_id_t, p: *u64)
    req [_](<u64>.share)(k, t, p) &*& lifetime_inclusion(k1, k) == true;
    ens [_](<u64>.share)(k1, t, p);
{
    open [_]r6_u64_share(k, t, p);
    frac_borrow_mono(k, k1, u64_full_borrow_content(t, p));
    assert [?r6_mono_fraction]frac_borrow(k1, u64_full_borrow_content(t, p));
    close [r6_mono_fraction]r6_u64_share(k1, t, p);
    leak [r6_mono_fraction]r6_u64_share(k1, t, p);
}
@*/
"""


def _add_u64_share_representation(source):
    anchor = b'use core::{mem::ManuallyDrop, ptr};\n'
    return _one(source, anchor, anchor + U64_SHARE_REPRESENTATION,
                'checked concrete u64 canonical share representation')


LATE_REFERENCE_PREP = b"""            //@ let r4_cmp_tmp_ref = precreate_ref::<u64>(&tmp);
            //@ init_ref_readonly::<u64>(r4_cmp_tmp_ref, 1/2);
            //@ assert array::<u64>(sift, 1, ?r4_cmp_current);
            //@ open array::<u64>(sift, 1, r4_cmp_current);
            //@ open array::<u64>(sift + 1, 0, _);
            //@ close array::<u64>(sift + 1, 0, nil);
            //@ let r4_cmp_sift_ref = precreate_ref::<u64>(sift);
            //@ init_ref_readonly::<u64>(r4_cmp_sift_ref, 1/2);
            //@ assert [?r5_tmp_share](*r4_cmp_tmp_ref |-> ?r5_tmp_value);
            //@ close [r5_tmp_share]u64_full_borrow_content(t, r4_cmp_tmp_ref)();
            //@ close scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))();
            //@ borrow(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ full_borrow_into_frac(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ frac_borrow_implies_scaled(r5_late_k, r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref));
            //@ assert [?r5_sift_share](*r4_cmp_sift_ref |-> ?r5_sift_value);
            //@ close [r5_sift_share]u64_full_borrow_content(t, r4_cmp_sift_ref)();
            //@ close scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))();
            //@ borrow(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ full_borrow_into_frac(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ frac_borrow_implies_scaled(r5_late_k, r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref));
            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_tmp_ref);
            //@ close_ref_own::<'late, u64>(r4_cmp_tmp_ref);
            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_sift_ref);
            //@ close_ref_own::<'late, u64>(r4_cmp_sift_ref);
            //@ close <(&'late u64, &'late u64)>.own(t, std_tuple_2_::<&'late u64, &'late u64> { 0: r4_cmp_tmp_ref, 1: r4_cmp_sift_ref });
"""
LATE_CALL = b"            if !is_less/*@::<F, (&'late u64, &'late u64), 'late>@*/(&tmp, &*sift) {\n"


def _prepare_late_references(source):
    anchor = b'            if !is_less(&tmp, &*sift) {\n'
    return _one(source, anchor, LATE_REFERENCE_PREP + LATE_CALL,
                'checked fractional share and Args ownership before late comparator')


LATE_CLOSE = b"""            //@ merge_fractions lifetime_token(r5_late_k);
            //@ assert [1/2]lifetime_token(r5_late_k);
"""
LATE_RECOVER = b"""            //@ assert lifetime_token(r5_late_k);
            //@ end_lifetime(r5_late_k);
            //@ borrow_end(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ open scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))();
            //@ open [r5_tmp_share]u64_full_borrow_content(t, r4_cmp_tmp_ref)();
            //@ end_ref_readonly::<u64>(r4_cmp_tmp_ref);
            //@ borrow_end(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ open scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))();
            //@ open [r5_sift_share]u64_full_borrow_content(t, r4_cmp_sift_ref)();
            //@ end_ref_readonly::<u64>(r4_cmp_sift_ref);
            //@ merge_fractions points_to::<u64>(sift, _);
            //@ assert *sift |-> ?r7_sift_current;
            //@ close array::<u64>(sift, 1, cons(r7_sift_current, nil));
"""


GUARD_POST_DROP_RECOVERY = b"""    //@ assert ref_readonly_end_token::<u64>(?r8_guard_ref, ?r8_tmp_origin, ?r8_tmp_share);
    //@ open CopyOnDrop_drop_effect(t, r8_guard_ref, ?r8_drop_dst, 1);
    //@ open [1/4]array::<u64>(r8_guard_ref, 1, ?r8_drop_current);
    //@ open [1/4]array::<u64>(r8_guard_ref + 1, 0, _);
    //@ end_ref_readonly::<u64>(r8_guard_ref);
    //@ merge_fractions points_to::<u64>(r8_tmp_origin, _);
"""

R9_GUARD_RETURN_MARKER = b"""    /*@ {
        guard_current_return_recover();
        assert ref_readonly_end_token::<u64>(?r9_guard_ref, ?r9_tmp_origin, ?r9_tmp_share);
        open [1/4]array::<u64>(r9_guard_ref, 1, ?r9_drop_current);
        open [1/4]array::<u64>(r9_guard_ref + 1, 0, _);
        end_ref_readonly::<u64>(r9_guard_ref);
        merge_fractions points_to::<u64>(r9_tmp_origin, _);
        assert [1/2](*r9_tmp_origin |-> ?r9_tmp_current);
        assert *tail |-> ?r9_tail_current;
        close array::<u64>(tail + 1, 0, nil);
        close array::<u64>(tail, 1, cons(r9_tail_current, nil));
        open array::<u64>(begin + 1, 1, _);
        assert *(begin + 1) |-> ?r15_middle_current;
        close array::<u64>(begin + 1, 2, cons(r15_middle_current, cons(r9_tail_current, nil)));
        open array::<u64>(begin, 1, _);
        assert *begin |-> ?r15_first_current;
        close array::<u64>(begin, 3, cons(r15_first_current, cons(r15_middle_current, cons(r9_tail_current, nil))));
        assert array::<u64>(begin, 3, ?r9_current_values);
        r9_current_u64_owners(t, r9_current_values);
    } @*/
"""

R9_CURRENT_U64_OWNERS_LEMMA = b"""/*@ lem r9_drop_u64_owners(t: thread_id_t, vs: list<u64>)
    req foreach(vs, own::<u64>(t));
    ens true;
{
    open foreach(vs, own::<u64>(t));
    match vs {
        nil => { }
        cons(v, rest) => {
            open own::<u64>(t)(v);
            open u64_own(t, v);
            r9_drop_u64_owners(t, rest);
        }
    }
}

lem r9_make_u64_owners(t: thread_id_t, vs: list<u64>)
    req true;
    ens foreach(vs, own::<u64>(t));
{
    match vs {
        nil => { close foreach(nil, own::<u64>(t)); }
        cons(v, rest) => {
            r9_make_u64_owners(t, rest);
            close u64_own(t, v);
            close own::<u64>(t)(v);
            close foreach(vs, own::<u64>(t));
        }
    }
}

lem r9_current_u64_owners(t: thread_id_t, vs: list<u64>)
    req foreach(?r9_previous, own::<u64>(t));
    ens foreach(vs, own::<u64>(t));
{
    r9_drop_u64_owners(t, r9_previous);
    r9_make_u64_owners(t, vs);
} @*/

"""


def _prepare_post_drop_recovery(source, old):
    anchor = b'        }\n    }\n}\n\n' + old.WRAPPER_SIGNATURE
    return _one(source, anchor, b'        }\n    }\n' +
                GUARD_POST_DROP_RECOVERY + b'}\n\n' + old.WRAPPER_SIGNATURE,
                'checked original guard debt after branch Drop before function free')


def _prepare_r9_guard_return_recovery(source, old):
    if (R9_GUARD_RETURN_MARKER in source or
            R9_CURRENT_U64_OWNERS_LEMMA in source):
        raise ValueError('R9 recovery marker or current-owner lemma already exists')
    anchor = b'        }\n    }\n}\n\n' + old.WRAPPER_SIGNATURE
    source = _one(source, anchor,
                  b'        }\n    }\n' + R9_GUARD_RETURN_MARKER + b'}\n\n' +
                  old.WRAPPER_SIGNATURE,
                  'R9 checked guard-return recovery marker')
    return _one(source, old.WRAPPER_SIGNATURE,
                R9_CURRENT_U64_OWNERS_LEMMA + old.WRAPPER_SIGNATURE,
                'R9 concrete-u64 current owner lemma declaration and checked body')


def _prepare_late_scope(source):
    source = _one(source, b'        //@ let r5_late_k = begin_lifetime();\n',
                  b'', 'move semantic lifetime begin to reached late preparation')
    anchor = b'            //@ let r4_cmp_tmp_ref = precreate_ref::<u64>(&tmp);\n'
    source = _one(source, anchor,
                  b'            //@ let r5_late_k = begin_lifetime();\n'
                  b'            //@ let r7_late_unwind = false;\n' + anchor,
                  'fresh semantic lifetime and outcome flag outside late type binding')
    anchor = b'            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_tmp_ref);\n'
    source = _one(source, anchor,
                  b"            //@ late_callback_scope_begin::<'late>();\n" + anchor,
                  'late type scope starts after physical variables are captured')
    markers = (b"            /*@ { late_callback_close::<'late>(); " +
               _commands(LATE_CLOSE) + b" } @*/\n" +
               b"            //@ late_callback_scope_end::<'late>();\n" +
               b"            /*@ { late_callback_recover::<'late>(); " +
               _commands(LATE_RECOVER) + b" } @*/\n")
    return _one(source, LATE_CALL, LATE_CALL + markers,
                'actual late normal and Cleanup resource scope markers')


def _commands(fragment):
    lines = fragment.splitlines()
    if any(not line.lstrip().startswith(b'//@ ') for line in lines):
        raise ValueError('recovery must contain only explicit ghost commands')
    return b' '.join(line.lstrip()[4:] for line in lines)


def _markers(old, mutation=None):
    split = b"        //@ end_lft_binding::<'cmp>();\n"
    if old.B2_COMPARE_RECOVER.count(split) != 1:
        raise ValueError('callback lifetime split changed')
    close, recover = old.B2_COMPARE_RECOVER.split(split)
    recover = _one(recover, ENTRY_OWNER_REJOIN, CURRENT_OWNER_REJOIN,
                   'CURRENT owner and physical-cell rejoin')
    for pointer, value in (('tail', 'current_tail'), ('sift', 'current_sift')):
        opened = f'        //@ open_full_borrow_content::<u64>(t, {pointer});\n'.encode()
        bound = f'        //@ assert *{pointer} |-> ?{value};\n'.encode()
        recover = _one(recover, opened, opened + bound,
                       f'bind returned CURRENT {pointer} value')
    if mutation == 'lost_reference_fraction':
        close = _one(close, b'close_frac_borrow(tail_ref_frac,',
                     b'close_frac_borrow(tail_ref_frac + 1,', 'bad reference fraction')
    if mutation == 'lost_reference_token':
        close = _one(close, b'assert [1/2]lifetime_token(cmp_k);',
                     b'assert lifetime_token(cmp_k);', 'insufficient lifetime token')
    return (b"            /*@ { first_callback_close::<'cmp>(); " +
            _commands(close) + b" } @*/\n" +
            b"            //@ first_callback_scope_end::<'cmp>();\n" +
            b"            /*@ { first_callback_recover::<'cmp>(); " +
            _commands(recover) + b' } @*/\n')


def _cut_prefix(source):
    wrapper = b'pub unsafe fn b2_three_from_local'
    if source.count(CUT) != 1 or source.count(wrapper) != 1:
        raise ValueError('prefix cut or wrapper boundary is not unique')
    cut = source.index(CUT)
    wrapper_at = source.index(wrapper, cut)
    suffix = source[wrapper_at:]
    wrapper_contract = source.rfind(b'/*@\nreq thread_token', cut, wrapper_at)
    if wrapper_contract >= 0:
        suffix = source[wrapper_contract:]
    result = source[:cut] + b'    }\n}\n\n' + suffix
    result = _one(result, b'unsafe fn insert_tail<',
                  b'unsafe fn ' + PREFIX_NAME + b'<', 'prefix function name')
    result = _one(result, b'insert_tail(begin, begin.add(2), is_less);',
                  PREFIX_NAME + b'(begin, begin.add(2), is_less);', 'prefix wrapper')
    if b'tail.read()' in result or b'if !is_less(&tmp' in result:
        raise ValueError('prefix includes forbidden post-cut runtime')
    return result


def prepare(evidence, *, prefix=False, mutation=None, profile=PROFILE):
    old = _load('first_callback_original_preparation', HERE / 'actual-insert-tail-b2.py')
    record = old._prepare(evidence)  # Cloud-only inherited actual-source binding.
    case = evidence / 'cases' / old.CASE
    original = (case / 'original/lib.rs').read_bytes()
    verified = (case / 'verified/lib.rs').read_bytes()
    full_original = original
    verified = _add_u64_share_representation(verified)
    verified = _one(verified, U64_SHARE_REPRESENTATION,
                    U64_SHARE_REPRESENTATION + GUARD_EMPTY_TAIL_HELPER,
                    'checked guard empty-tail helper')
    verified = _add_singleton_facts(verified)
    verified = _one(verified,
                    old.B2_COMPARE_RECOVER.replace(b'        ', b'            '),
                    b'', 'remove old false recovery')
    verified = _one(verified, old.B2_COMPARE_RECOVER, b'',
                    'remove old true recovery')
    call = (b"        if !is_less/*@::<F, (&'cmp u64, &'cmp u64), 'cmp>@*/"
            b'(&*tail, &*sift) {\n')
    markers = _markers(old, mutation)
    verified = _one(verified, call, call + markers, 'first actual comparator markers')
    negative = b''
    if mutation == 'lost_current_f':
        negative = b'            //@ leak <F>.own(t, _);\n'
    elif mutation == 'lost_cell_owner':
        negative = (b'            //@ array_split::<u64>(begin, 1);\n'
                    b'            //@ leak array::<u64>(begin, 1, _);\n'
                    b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner\n')
    if negative:
        verified = _one(verified, markers, markers + negative,
                        'explicit negative-only resource loss on false path')
    if mutation not in (None, 'lost_reference_fraction', 'lost_reference_token',
                         'lost_current_f', 'lost_cell_owner'):
        raise ValueError('unknown first-comparator mutation')
    if not prefix:
        verified = _prepare_late_references(_prepare_first_shift(_prepare_guard_empty_tail(
            _prepare_tmp_reference(_open_tail_read(verified)))))
        if profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE):
            verified = _prepare_late_scope(verified)
        if profile in (R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE):
            if profile == R8_PROFILE:
                verified = _prepare_post_drop_recovery(verified, old)
            else:
                verified = _prepare_r9_guard_return_recovery(verified, old)
        if profile in (R10_PROFILE, R11_PROFILE):
            verified = _prepare_r10_moving_gap(verified, profile=profile)
    def runtime(data):
        return re.sub(rb'/\*.*?\*/|//[^\n]*', b'', data, flags=re.S)
    if runtime(verified) != runtime(original):
        clean = lambda data: b'\n'.join(x.strip() for x in runtime(data).splitlines() if x.strip())
        if clean(verified) != clean(original):
            raise ValueError('new recovery changed runtime tokens')
    if prefix:
        original, verified = _cut_prefix(original), _cut_prefix(verified)
    if mutation is None and (b'//@ leak' in verified or b'//@ assume' in verified):
        raise ValueError('positive cannot discard or assume resources')
    if old.INSERT_CONTRACT not in verified:
        raise ValueError('full CURRENT normal/unwind final posts changed')
    (case / 'original/lib.rs').write_bytes(original)
    (case / 'verified/lib.rs').write_bytes(verified)
    record.update(schema='first-actual-callback-source-v1', profile=profile,
                  original_sha256=_sha(original), verified_sha256=_sha(verified),
                  full_specialized_original_sha256=_sha(full_original),
                  prefix=prefix, mutation=mutation,
                  cut='immediately before tail.read/ManuallyDrop/guard; true path returns at cut' if prefix else None,
                  source_relation='exact pre-cut runtime segment plus closing braces and renamed function/wrapper' if prefix else 'complete actual body; ghost-only annotation replacement',
                  final_posts_sha256=_sha(old.INSERT_CONTRACT),
                  callback_marker_sha256=_sha(markers),
                  late_callback_scope_recovery_requested=(profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE) and not prefix),
                  guard_return_recovery_marker_sha256=(
                      _sha(R9_GUARD_RETURN_MARKER) if profile in (R9_PROFILE, R10_PROFILE, R11_PROFILE) and not prefix else None),
                  guard_return_recovery_requested=(profile in (R9_PROFILE, R10_PROFILE, R11_PROFILE) and not prefix),
                  first_callback_unwind_recovery_qualified=False,
                  first_callback_unwind_status='NOT_RUN', proof_credit=False)
    record['actual_first_call_line'] = old._line(verified, call.rstrip(b'\n'))
    for key, anchor in (
        ('actual_read_line', b'let tmp = ManuallyDrop::new(tail.read());'),
        ('actual_guard_line', b'let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };'),
        ('actual_shift_line', b'ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);'),
        ('actual_update_line', b'gap_guard.dst = sift;'),
        ('actual_late_call_line', LATE_CALL.strip())):
        record[key] = None if prefix else old._line(verified, anchor)
    record['false_return_line'] = old._line(verified, b'            return;')
    if prefix:
        record['true_cut_line'] = verified[:verified.index(b'    }\n}\n\n', verified.index(call))].count(b'\n') + 1
    else:
        record['true_frontier_line'] = old._line(verified, b'let tmp = ManuallyDrop::new(tail.read());')
    (evidence / 'preparation.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    return case, record


def _pinned_actual_body_identities(old):
    raw = old.SOURCE.read_bytes()
    if (_sha(raw) != old.PINNED_SOURCE_SHA256 or
            old._git_blob(raw) != old.PINNED_SOURCE_BLOB):
        raise ValueError('pinned SmallSort source identity changed')
    drop_raw = old._extract(raw, old.DROP_START, old.DROP_END, b'}\n\n')
    insert_raw = old._extract(raw, old.INSERT_START, old.INSERT_END, b'\n}\n')
    if (_sha(drop_raw) != old.PINNED_DROP_SHA256 or
            len(drop_raw) != old.PINNED_DROP_BYTES or
            _sha(insert_raw) != old.PINNED_INSERT_SHA256 or
            len(insert_raw) != old.PINNED_INSERT_BYTES):
        raise ValueError('pinned Drop/insert source extraction changed')
    specialized_drop = old._specialize_drop(drop_raw)
    specialized_insert = old._specialize_insert(insert_raw)
    if specialized_insert.count(old.INSERT_SIGNATURE) != 1:
        raise ValueError('pinned specialized insert signature is not unique')
    return {
        'source_sha256': old.PINNED_SOURCE_SHA256,
        'source_git_blob': old.PINNED_SOURCE_BLOB,
        'actual_drop_sha256': old.PINNED_DROP_SHA256,
        'actual_insert_tail_sha256': old.PINNED_INSERT_SHA256,
        'actual_insert_tail_bytes': old.PINNED_INSERT_BYTES,
        'mechanically_specialized_drop_sha256': _sha(specialized_drop),
        'mechanically_specialized_insert_sha256': _sha(specialized_insert),
        'specialized_drop': specialized_drop,
        'specialized_insert': specialized_insert,
        'original_body': (b'#![no_std]\nuse core::{mem::ManuallyDrop, ptr};\n\n' +
                          specialized_drop + b'\n' + specialized_insert),
    }

def _body_runtime_equal(original, verified):
    strip_comments = lambda data: re.sub(rb'/\*.*?\*/|//[^\n]*', b'', data, flags=re.S)
    original_runtime = strip_comments(original)
    verified_runtime = strip_comments(verified)
    if original_runtime == verified_runtime:
        return True
    nonempty_lines = lambda data: b'\n'.join(
        line.strip() for line in data.splitlines() if line.strip())
    return nonempty_lines(original_runtime) == nonempty_lines(verified_runtime)


def _body_isolation_suffixes(old):
    signature = old.WRAPPER_SIGNATURE
    if (old.WRAPPER_RUNTIME.count(signature) != 1 or
            old.WRAPPER_RUNTIME.count(b'let mut values = [10_u64, 20_u64, 5_u64];') != 1 or
            old.WRAPPER_RUNTIME.count(b'let begin = values.as_mut_ptr();') != 1 or
            old.WRAPPER_RUNTIME.count(b'insert_tail(begin, begin.add(2), is_less);') != 1 or
            old.WRAPPER_RUNTIME.count(b'/*@') or old.WRAPPER_RUNTIME.count(b'//@')):
        raise ValueError('synthetic caller runtime suffix changed')
    verified_suffix = _one(old.WRAPPER_RUNTIME, signature,
                           signature + old.WRAPPER_CONTRACT,
                           'attached synthetic caller contract')
    return old.WRAPPER_RUNTIME, verified_suffix


RAW_ARRAY_INV_LEMMA = b'''/*@

lem r18_u64_array_inv(p: *u64, count: usize)
    req [?f]array::<u64>(p, count, ?vs);
    ens [f]array::<u64>(p, count, vs) &*& count == length(vs) &*&
        pointer_within_limits(p) == true &*& pointer_within_limits(p + count) == true;
{
    array_inv::<u64>();
}

@*/
'''
R20_ARRAY_SLICE_CONTENT_SHA256 = 'f333ab38af041cb3e67c2713a7ca5a86d73f16c7e41cebe69ace71481b0e3b17'


def _raw_local_caller_suffixes(old):
    signature = old.WRAPPER_SIGNATURE
    if (old.WRAPPER_RUNTIME.count(signature) != 1 or
            old.WRAPPER_RUNTIME.count(b'let mut values = [10_u64, 20_u64, 5_u64];') != 1 or
            old.WRAPPER_RUNTIME.count(b'let begin = values.as_mut_ptr();') != 1 or
            old.WRAPPER_RUNTIME.count(b'insert_tail(begin, begin.add(2), is_less);') != 1 or
            old.WRAPPER_RUNTIME.count(b'/*@') or old.WRAPPER_RUNTIME.count(b'//@')):
        raise ValueError('canonical caller runtime suffix changed')
    original = _one(old.WRAPPER_RUNTIME, b'let begin = values.as_mut_ptr();',
                     b'let begin = &raw mut values as *mut u64;',
                     'raw local array data-pointer derivation')
    before_call = (b'    /*@ { r18_u64_array_inv(begin, 3);\n'
                   b'        assert array::<u64>(begin, 3, ?r16_current);\n'
                   b'        r9_make_u64_owners(t, r16_current); } @*/\n')
    after_call = (b'    /*@ { r19_insert_tail_unwind_cleanup();\n'
                  b'        assert array::<u64>(begin, 3, ?r16_normal_current);\n'
                  b'        r9_drop_u64_owners(t, r16_normal_current);\n'
                  b'        array_to_array_(begin); } @*/\n')
    verified_runtime = _one(original, b'    insert_tail(begin, begin.add(2), is_less);\n',
        before_call + b'    insert_tail(begin, begin.add(2), is_less);\n' + after_call,
        'raw caller checked current ownership and normal local cleanup')
    verified = _one(verified_runtime, signature,
                    signature + old.WRAPPER_CONTRACT,
                    'attached raw-wrapper contract')
    if not verified.startswith(b'\n') or verified.count(RAW_ARRAY_INV_LEMMA) != 0:
        raise ValueError('raw-wrapper suffix boundary changed')
    content_lemmas = (HERE / 'r20-array-slice-content.rs').read_bytes()
    if _sha(content_lemmas) != R20_ARRAY_SLICE_CONTENT_SHA256:
        raise ValueError('checked array3/slice content helper pin mismatch')
    return original, b'\n' + RAW_ARRAY_INV_LEMMA + content_lemmas + verified


def _raw_owner_lemma_body():
    helper = R9_CURRENT_U64_OWNERS_LEMMA
    if not helper.endswith(b'@*/\n\n'):
        raise ValueError('checked current-u64 owner helper newline contract changed')
    return helper[:-1]


def _raw_parent_body(evidence, parent_case, parent_record, old,
                     parent_preparation_sha, parent_source_unchanged,
                     parent_stage_receipt_gate):
    canonical = _pinned_actual_body_identities(old)
    expected_parent = Path(evidence).resolve() / 'full_body' / 'cases' / 'actual_three_current_full_posts'
    if (Path(parent_case).resolve() != expected_parent.resolve() or
            type(parent_record) is not dict or parent_record.get('prefix') is not False or
            parent_record.get('mutation') is not None or
            parent_record.get('profile') not in SUPPORTED_PROFILES or
            any(parent_record.get(key) != canonical[key] for key in (
                'source_sha256', 'source_git_blob', 'actual_drop_sha256',
                'actual_insert_tail_sha256', 'actual_insert_tail_bytes',
                'mechanically_specialized_insert_sha256'))):
        raise ValueError('raw caller requires the exact pinned unmutated full-body parent')
    parent_original = (expected_parent / 'original/lib.rs').read_bytes()
    parent_verified = (expected_parent / 'verified/lib.rs').read_bytes()
    if (_sha(parent_original) != parent_record.get('original_sha256') or
            _sha(parent_verified) != parent_record.get('verified_sha256')):
        raise ValueError('captured parent source pair changed')
    original_suffix, verified_suffix = _body_isolation_suffixes(old)
    if not parent_original.endswith(original_suffix) or not parent_verified.endswith(verified_suffix):
        raise ValueError('parent caller suffix is not the exact canonical wrapper')
    original_body = parent_original[:-len(original_suffix)]
    verified_body = parent_verified[:-len(verified_suffix)]
    if (original_body != canonical['original_body'] or
            not _body_runtime_equal(original_body, verified_body) or
            original_body.count(old.INSERT_SIGNATURE) != 1 or
            _sha(original_body[original_body.index(old.INSERT_SIGNATURE):]) !=
                parent_record.get('mechanically_specialized_insert_sha256') or
            verified_body.count(old.INSERT_CONTRACT) != 1 or
            old.WRAPPER_CONTRACT in verified_body or
            _sha(old.INSERT_CONTRACT) != parent_record.get('final_posts_sha256')):
        raise ValueError('parent does not contain the exact pinned body and original posts')
    owner_helper_body = _raw_owner_lemma_body()
    if (verified_body.count(owner_helper_body) != 1 or
            not verified_body.endswith(owner_helper_body)):
        raise ValueError('raw caller requires the exact checked current-u64 owner helper at the wrapper boundary')
    prep_path = Path(evidence) / 'full_body' / 'preparation.json'
    prep_bytes = prep_path.read_bytes()
    if _sha(prep_bytes) != parent_preparation_sha or json.loads(prep_bytes) != parent_record:
        raise ValueError('captured parent preparation receipt changed')
    if (parent_source_unchanged is not True or
            type(parent_stage_receipt_gate) is not dict or
            parent_stage_receipt_gate.get('admitted') is not True):
        raise ValueError('captured parent source/stage gate did not admit the candidate')
    return canonical, original_body, verified_body


def _prepare_raw_local_caller(evidence, parent_case, parent_record, old,
                              parent_preparation_sha, parent_source_unchanged,
                              parent_stage_receipt_gate):
    canonical, original_body, verified_body = _raw_parent_body(
        evidence, parent_case, parent_record, old, parent_preparation_sha,
        parent_source_unchanged, parent_stage_receipt_gate)
    original_suffix, verified_suffix = _raw_local_caller_suffixes(old)
    root = Path(evidence) / 'raw_local_caller'
    case = root / 'cases' / RAW_LOCAL_CALLER_NAME
    case.mkdir(parents=True, exist_ok=False)
    (case / 'original').mkdir()
    (case / 'verified').mkdir()
    original = original_body + original_suffix
    verified = verified_body + verified_suffix
    (case / 'original/lib.rs').write_bytes(original)
    (case / 'verified/lib.rs').write_bytes(verified)
    record = {
        'schema': 'r16-raw-local-caller-v1', 'profile': parent_record['profile'],
        'case': RAW_LOCAL_CALLER_NAME, 'parent_case': str(Path(parent_case).resolve()),
        'parent_preparation_sha256': parent_preparation_sha,
        'parent_source_unchanged': True, 'parent_stage_receipt_gate': parent_stage_receipt_gate,
        'parent_original_sha256': parent_record['original_sha256'],
        'parent_verified_sha256': parent_record['verified_sha256'],
        'source_sha256': parent_record['source_sha256'], 'source_git_blob': parent_record['source_git_blob'],
        'actual_drop_sha256': parent_record['actual_drop_sha256'],
        'actual_insert_tail_sha256': parent_record['actual_insert_tail_sha256'],
        'actual_insert_tail_bytes': parent_record['actual_insert_tail_bytes'],
        'mechanically_specialized_insert_sha256': parent_record['mechanically_specialized_insert_sha256'],
        'mechanically_specialized_drop_sha256': canonical['mechanically_specialized_drop_sha256'],
        'final_posts_sha256': _sha(old.INSERT_CONTRACT),
        'original_parent_suffix_sha256': _sha(_body_isolation_suffixes(old)[0]),
        'verified_parent_suffix_sha256': _sha(_body_isolation_suffixes(old)[1]),
        'original_raw_suffix_sha256': _sha(original_suffix),
        'verified_raw_suffix_sha256': _sha(verified_suffix),
        'original_sha256': _sha(original), 'verified_sha256': _sha(verified),
        'canonical_original_body_sha256': _sha(canonical['original_body']),
        'caller_suffix_exact': True, 'body_bytes_preserved': True,
        'posts_preserved': True, 'runtime_unchanged': True,
        'same_local_values': True, 'same_comparator_and_callee_args': True,
        'raw_pointer_wrapper_only': True, 'original_caller_prefix_gate_unchanged': True,
        'accepted': False, 'proof_credit': False, 'b2_achieved': False,
        'independent_credit': False,
    }
    (root / 'preparation.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return case, record


def _raw_local_caller_source_gate(case, parent_case, parent_record, record, old,
                                  parent_preparation_sha, captured_stage_receipt_gate):
    try:
        if (type(record) is not dict or type(captured_stage_receipt_gate) is not dict or
                captured_stage_receipt_gate.get('admitted') is not True or
                record.get('parent_stage_receipt_gate') != captured_stage_receipt_gate):
            return False
        canonical, original_body, verified_body = _raw_parent_body(
            Path(case).resolve().parents[2], parent_case, parent_record, old,
            parent_preparation_sha, True, captured_stage_receipt_gate)
        evidence_root = Path(case).resolve().parents[2]
        expected_case = evidence_root / 'raw_local_caller' / 'cases' / RAW_LOCAL_CALLER_NAME
        expected_parent = evidence_root / 'full_body' / 'cases' / 'actual_three_current_full_posts'
        if (record.get('schema') != 'r16-raw-local-caller-v1' or
                Path(case).resolve() != expected_case.resolve() or
                Path(parent_case).resolve() != expected_parent.resolve() or
                record.get('case') != RAW_LOCAL_CALLER_NAME or
                record.get('parent_case') != str(expected_parent.resolve()) or
                record.get('profile') != parent_record.get('profile') or
                record.get('parent_source_unchanged') is not True):
            return False
        original_suffix, verified_suffix = _raw_local_caller_suffixes(old)
        original = (case / 'original/lib.rs').read_bytes()
        verified = (case / 'verified/lib.rs').read_bytes()
        parent_prep = (expected_parent.parent.parent / 'preparation.json').read_bytes()
        isolated_prep = (expected_case.parent.parent / 'preparation.json').read_bytes()
        if json.loads(parent_prep) != parent_record or json.loads(isolated_prep) != record:
            return False
        return (
            _sha(parent_prep) == parent_preparation_sha and
            record.get('parent_preparation_sha256') == parent_preparation_sha and
            record.get('source_sha256') == canonical['source_sha256'] and
            record.get('source_git_blob') == canonical['source_git_blob'] and
            record.get('actual_drop_sha256') == canonical['actual_drop_sha256'] and
            record.get('actual_insert_tail_sha256') == canonical['actual_insert_tail_sha256'] and
            record.get('actual_insert_tail_bytes') == canonical['actual_insert_tail_bytes'] and
            record.get('mechanically_specialized_insert_sha256') == parent_record.get('mechanically_specialized_insert_sha256') and
            record.get('mechanically_specialized_drop_sha256') == canonical['mechanically_specialized_drop_sha256'] and
            record.get('original_parent_suffix_sha256') == _sha(_body_isolation_suffixes(old)[0]) and
            record.get('verified_parent_suffix_sha256') == _sha(_body_isolation_suffixes(old)[1]) and
            record.get('original_raw_suffix_sha256') == _sha(original_suffix) and
            record.get('verified_raw_suffix_sha256') == _sha(verified_suffix) and
            record.get('parent_original_sha256') == _sha((expected_parent / 'original/lib.rs').read_bytes()) and
            record.get('parent_verified_sha256') == _sha((expected_parent / 'verified/lib.rs').read_bytes()) and
            original == original_body + original_suffix and
            verified == verified_body + verified_suffix and
            verified_body.endswith(_raw_owner_lemma_body()) and
            verified_body.count(_raw_owner_lemma_body()) == 1 and
            original.endswith(original_suffix) and verified.endswith(verified_suffix) and
            original.count(b'let begin = &raw mut values as *mut u64;') == 1 and
            b'let begin = values.as_mut_ptr();' not in original and
            _body_runtime_equal(original, verified) and
            record.get('original_sha256') == _sha(original) and
            record.get('verified_sha256') == _sha(verified) and
            record.get('canonical_original_body_sha256') == _sha(canonical['original_body']) and
            record.get('final_posts_sha256') == _sha(old.INSERT_CONTRACT) and
            record.get('caller_suffix_exact') is True and record.get('body_bytes_preserved') is True and
            record.get('posts_preserved') is True and record.get('runtime_unchanged') is True and
            record.get('raw_pointer_wrapper_only') is True and
            record.get('same_local_values') is True and
            record.get('same_comparator_and_callee_args') is True and
            record.get('original_caller_prefix_gate_unchanged') is True and
            record.get('accepted') is False and record.get('proof_credit') is False and
            record.get('b2_achieved') is False and record.get('independent_credit') is False)
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return False


def _prepare_body_isolation(evidence, parent_case, parent_record, old,
                            parent_preparation_sha, parent_source_unchanged,
                            parent_stage_receipt_gate):
    canonical = _pinned_actual_body_identities(old)
    expected_parent = Path(evidence).resolve() / 'full_body' / 'cases' / 'actual_three_current_full_posts'
    if (Path(parent_case).resolve() != expected_parent.resolve() or
            type(parent_record) is not dict or parent_record.get('prefix') is not False or
            parent_record.get('mutation') is not None or
            parent_record.get('profile') not in SUPPORTED_PROFILES or
            any(parent_record.get(key) != canonical[key] for key in (
                'source_sha256', 'source_git_blob', 'actual_drop_sha256',
                'actual_insert_tail_sha256', 'actual_insert_tail_bytes',
                'mechanically_specialized_insert_sha256')) or
            type(parent_record.get('mechanically_specialized_insert_sha256')) is not str):
        raise ValueError('body isolation requires the exact pinned unmutated full-body preparation')
    parent_original = (parent_case / 'original/lib.rs').read_bytes()
    parent_verified = (parent_case / 'verified/lib.rs').read_bytes()
    if (_sha(parent_original) != parent_record.get('original_sha256') or
            _sha(parent_verified) != parent_record.get('verified_sha256')):
        raise ValueError('full-body source pair differs from its preparation record')
    original_suffix, verified_suffix = _body_isolation_suffixes(old)
    if (not parent_original.endswith(original_suffix) or
            not parent_verified.endswith(verified_suffix)):
        raise ValueError('caller suffix is not the exact appended original/verified wrapper')
    original_body = parent_original[:-len(original_suffix)]
    verified_body = parent_verified[:-len(verified_suffix)]
    if (original_body != canonical['original_body'] or
            not verified_body or
            not _body_runtime_equal(original_body, verified_body) or
            original_body.count(old.INSERT_SIGNATURE) != 1):
        raise ValueError('prepared original body differs from the pinned definition, Drop, or runtime')
    specialized_start = old.INSERT_SIGNATURE
    if (not original_body or original_body.count(specialized_start) != 1 or
            _sha(original_body[original_body.index(specialized_start):]) !=
            parent_record.get('mechanically_specialized_insert_sha256') or
            not verified_body or parent_verified.count(old.INSERT_CONTRACT) != 1 or
            old.INSERT_CONTRACT not in verified_body or
            old.WRAPPER_CONTRACT in verified_body):
        raise ValueError('body/posts boundary or wrapper-contract removal is ambiguous')
    if _sha(old.INSERT_CONTRACT) != parent_record.get('final_posts_sha256'):
        raise ValueError('full actual normal/unwind posts differ from preparation identity')

    parent_prep = Path(evidence) / 'full_body' / 'preparation.json'
    parent_prep_bytes = parent_prep.read_bytes()
    if (_sha(parent_prep_bytes) != parent_preparation_sha or
            json.loads(parent_prep_bytes) != parent_record):
        raise ValueError('full-body preparation receipt changed since pre-dispatch capture')
    if (parent_source_unchanged is not True or
            type(parent_stage_receipt_gate) is not dict or
            parent_stage_receipt_gate.get('admitted') is not True):
        raise ValueError('full-body source/stage receipts did not admit the pre-dispatch source')
    parent_prep_sha = parent_preparation_sha
    root = Path(evidence) / 'body_isolation'
    case = root / 'cases' / BODY_ISOLATION_NAME
    case.mkdir(parents=True, exist_ok=False)
    (case / 'original').mkdir()
    (case / 'verified').mkdir()
    (case / 'original/lib.rs').write_bytes(original_body)
    (case / 'verified/lib.rs').write_bytes(verified_body)
    record = {
        'schema': 'r16-actual-body-isolation-v1',
        'profile': parent_record['profile'],
        'case': BODY_ISOLATION_NAME,
        'parent_case': str(Path(parent_case).resolve()),
        'parent_preparation_sha256': parent_prep_sha,
        'parent_source_unchanged': True,
        'parent_stage_receipt_gate': parent_stage_receipt_gate,
        'parent_original_sha256': parent_record['original_sha256'],
        'parent_verified_sha256': parent_record['verified_sha256'],
        'source_sha256': parent_record.get('source_sha256'),
        'actual_drop_sha256': parent_record.get('actual_drop_sha256'),
        'actual_insert_tail_sha256': parent_record.get('actual_insert_tail_sha256'),
        'actual_insert_tail_bytes': parent_record.get('actual_insert_tail_bytes'),
        'source_git_blob': parent_record.get('source_git_blob'),
        'mechanically_specialized_drop_sha256': canonical['mechanically_specialized_drop_sha256'],
        'mechanically_specialized_insert_sha256': parent_record.get('mechanically_specialized_insert_sha256'),
        'original_removed_suffix_sha256': _sha(original_suffix),
        'verified_removed_suffix_sha256': _sha(verified_suffix),
        'original_removed_suffix_bytes': len(original_suffix),
        'verified_removed_suffix_bytes': len(verified_suffix),
        'original_sha256': _sha(original_body),
        'verified_sha256': _sha(verified_body),
        'original_body_sha256': _sha(original_body),
        'canonical_original_body_sha256': _sha(canonical['original_body']),
        'verified_body_sha256': _sha(verified_body),
        'final_posts_sha256': parent_record['final_posts_sha256'],
        'caller_suffix_exact': True,
        'body_bytes_preserved': True,
        'posts_preserved': True,
        'runtime_unchanged': True,
        'target': 'complete concrete-u64 insert_tail definition and selected Drop only',
        'caller_prefix_full_b2_independent_credit': False,
        'accepted': False,
        'proof_credit': False,
    }
    (root / 'preparation.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return case, record


def _body_isolation_source_gate(case, parent_case, parent_record, record, old,
                                parent_preparation_sha):
    try:
        if (type(record) is not dict or record.get('schema') != 'r16-actual-body-isolation-v1' or
                type(parent_record) is not dict or record.get('profile') != parent_record.get('profile') or
                record.get('case') != BODY_ISOLATION_NAME or
                record.get('caller_prefix_full_b2_independent_credit') is not False or
                record.get('parent_source_unchanged') is not True or
                type(record.get('parent_stage_receipt_gate')) is not dict or
                record['parent_stage_receipt_gate'].get('admitted') is not True):
            return False
        canonical = _pinned_actual_body_identities(old)
        evidence_root = Path(case).resolve().parents[2]
        expected_case = evidence_root / 'body_isolation' / 'cases' / BODY_ISOLATION_NAME
        expected_parent = evidence_root / 'full_body' / 'cases' / 'actual_three_current_full_posts'
        if (Path(case).resolve() != expected_case.resolve() or
                Path(parent_case).resolve() != expected_parent.resolve() or
                record.get('parent_case') != str(expected_parent.resolve()) or
                any(parent_record.get(key) != canonical[key] for key in (
                    'source_sha256', 'source_git_blob', 'actual_drop_sha256',
                    'actual_insert_tail_sha256', 'actual_insert_tail_bytes',
                    'mechanically_specialized_insert_sha256')) or
                any(record.get(key) != canonical[key] for key in (
                    'source_sha256', 'source_git_blob', 'actual_drop_sha256',
                    'actual_insert_tail_sha256', 'actual_insert_tail_bytes',
                    'mechanically_specialized_insert_sha256',
                    'mechanically_specialized_drop_sha256'))):
            return False
        original = (case / 'original/lib.rs').read_bytes()
        verified = (case / 'verified/lib.rs').read_bytes()
        parent_original = (parent_case / 'original/lib.rs').read_bytes()
        parent_verified = (parent_case / 'verified/lib.rs').read_bytes()
        prep_path = Path(parent_case).parent.parent / 'preparation.json'
        prep_bytes = prep_path.read_bytes()
        if json.loads(prep_bytes) != parent_record:
            return False
        isolated_prep = (Path(case).parent.parent / 'preparation.json').read_bytes()
        if json.loads(isolated_prep) != record:
            return False
        original_suffix, verified_suffix = _body_isolation_suffixes(old)
        return (
            record.get('parent_original_sha256') == parent_record.get('original_sha256') == _sha(parent_original) and
            record.get('parent_verified_sha256') == parent_record.get('verified_sha256') == _sha(parent_verified) and
            record.get('parent_preparation_sha256') == parent_preparation_sha == _sha(prep_bytes) and
            parent_record.get('prefix') is False and parent_record.get('mutation') is None and
            parent_original.endswith(original_suffix) and parent_verified.endswith(verified_suffix) and
            original == parent_original[:-len(original_suffix)] == canonical['original_body'] and
            verified == parent_verified[:-len(verified_suffix)] and
            record.get('canonical_original_body_sha256') == _sha(canonical['original_body']) and
            original.count(old.INSERT_SIGNATURE) == 1 and
            _sha(original[original.index(old.INSERT_SIGNATURE):]) ==
                parent_record['mechanically_specialized_insert_sha256'] and
            record.get('original_removed_suffix_sha256') == _sha(original_suffix) and
            record.get('verified_removed_suffix_sha256') == _sha(verified_suffix) and
            record.get('original_sha256') == record.get('original_body_sha256') == _sha(original) and
            record.get('verified_sha256') == record.get('verified_body_sha256') == _sha(verified) and
            record.get('final_posts_sha256') == parent_record.get('final_posts_sha256') == _sha(old.INSERT_CONTRACT) and
            _body_runtime_equal(original, verified) and
            verified.count(old.INSERT_CONTRACT) == 1 and
            old.WRAPPER_CONTRACT not in verified and
            record.get('caller_suffix_exact') is True and record.get('body_bytes_preserved') is True and
            record.get('posts_preserved') is True and record.get('runtime_unchanged') is True)
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return False


def _body_json_safe(value, *, depth=0):
    if depth > 6:
        return repr(value)[:2000]
    if value is None or type(value) in (bool, int, float, str):
        return value if type(value) is not str else value[:10000]
    if type(value) in (list, tuple):
        return [_body_json_safe(item, depth=depth + 1) for item in value[:128]]
    if type(value) is dict:
        return {str(key)[:200]: _body_json_safe(item, depth=depth + 1)
                for key, item in list(value.items())[:128]}
    return repr(value)[:2000]


def _body_exception_record(error):
    attrs = vars(error) if hasattr(error, '__dict__') else {}
    return {
        'type': type(error).__name__,
        'message': str(error)[:10000],
        'args_repr': repr(error.args)[:10000],
        'attributes': _body_json_safe(attrs),
        'returncode': _body_json_safe(getattr(error, 'returncode', None)),
        'last_snapshot': _body_json_safe(getattr(error, 'last_snapshot', None)),
        'snapshots': _body_json_safe(getattr(error, 'snapshots', None)),
    }


def _body_isolation_outcome(classification, reason, *, evidence, case=None,
                            record=None, execution=None, phase=None, error=None,
                            receipt_error=None, source_exact=None,
                            result_subdir='body_isolation'):
    execution = execution if type(execution) is dict else {}
    result = {
        'schema': 'r16-actual-body-isolation-result-v1',
        'classification': classification,
        'reason': reason,
        'phase': phase,
        'source_exact': source_exact,
        'verifier_target_observed': classification == 'BODY_UNIT_VERIFIER_EXIT0',
        'body_bytes_preserved': record.get('body_bytes_preserved') is True if type(record) is dict else False,
        'posts_preserved': record.get('posts_preserved') is True if type(record) is dict else False,
        'accepted': False,
        'proof_credit': False,
        'full_target': False,
        'b2_achieved': False,
        'caller_or_prefix_gate': False,
        'independent_credit': False,
        'qualification': False,
    }
    for source_key, output_key in (
            ('stages', 'stages'), ('status', 'execution_status'),
            ('classification', 'execution_classification'),
            ('last_snapshot', 'last_snapshot'), ('snapshots', 'snapshots'),
            ('stage_receipt_gate', 'stage_receipt_gate'),
            ('source_unchanged_at_every_stage', 'source_unchanged_at_every_stage'),
            ('exception', 'exception')):
        if source_key in execution:
            result[output_key] = _body_json_safe(execution[source_key])
    if error is not None:
        result['exception'] = _body_exception_record(error)
    if receipt_error is not None:
        result['receipt_exception'] = _body_exception_record(receipt_error)
    destination = Path(case) / 'classification.json' if case is not None else Path(evidence) / result_subdir / 'classification.json'
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    except OSError as write_error:
        result['result_write_exception'] = _body_exception_record(write_error)
    return result


def _run_body_isolation_diagnostic(evidence, parent_case, parent_record, old,
                                  consumer, args, selected_profile, dispatch,
                                  *, parent_preparation_sha, parent_source_unchanged,
                                  parent_stage_receipt_gate, prepare_fn=None,
                                  source_gate_fn=None, classify_fn=None,
                                  outcome_fn=None, unit_label='body-only'):
    prepare_fn = _prepare_body_isolation if prepare_fn is None else prepare_fn
    source_gate_fn = _body_isolation_source_gate if source_gate_fn is None else source_gate_fn
    classify_fn = _classify_body_isolation if classify_fn is None else classify_fn
    outcome_fn = _body_isolation_outcome if outcome_fn is None else outcome_fn
    body_case = None
    body_record = None
    body_execution = None
    phase = 'prepare'
    try:
        if (parent_source_unchanged is not True or
                type(parent_stage_receipt_gate) is not dict or
                parent_stage_receipt_gate.get('admitted') is not True):
            return outcome_fn(
                'NOT_RUN', f'parent full-body source/stage receipt gate failed before {unit_label} dispatch',
                evidence=evidence, phase='parent_stage_gate', source_exact=False)
        body_case, body_record = prepare_fn(
            evidence, parent_case, parent_record, old, parent_preparation_sha,
            parent_source_unchanged, parent_stage_receipt_gate)
        phase = 'source_gate'
        if not source_gate_fn(body_case, parent_case, parent_record, body_record, old,
                              parent_preparation_sha):
            return outcome_fn(
                'NOT_RUN', f'source identity gate failed before {unit_label} dispatch',
                evidence=evidence, case=body_case, record=body_record, phase=phase,
                source_exact=False)
        phase = 'source_hashes'
        body_before = consumer._hashes(body_case)
        phase = 'dispatch'
        previous_r8 = getattr(args, 'r8_owned_array_allocation', False)
        args.r8_owned_array_allocation = selected_profile in (
            R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE)
        native_body = selected_profile == R11_PROFILE
        dispatch_error = None
        try:
            body_execution = dispatch(body_case, args, actual_callback_case=True,
                                      body_isolation_native=native_body)
        except Exception as error:
            dispatch_error = error
        finally:
            args.r8_owned_array_allocation = previous_r8
        if dispatch_error is not None:
            return outcome_fn(
                'INCONCLUSIVE', f'{unit_label} dispatch raised an exception',
                evidence=evidence, case=body_case, record=body_record,
                execution=body_execution, phase=phase, error=dispatch_error,
                source_exact=True)
        if type(body_execution) is not dict:
            phase = 'execution_shape'
            return outcome_fn(
                'INCONCLUSIVE', f'{unit_label} execution result has the wrong type',
                evidence=evidence, case=body_case, record=body_record,
                phase=phase, source_exact=True)
        phase = 'source_hashes_after'
        body_after = consumer._hashes(body_case)
        body_execution['source_unchanged_at_every_stage'] = body_before == body_after
        phase = 'stage_receipts'
        receipt_error = None
        try:
            stage_map = body_execution.get('stages')
            body_execution['stage_receipt_gate'] = consumer._stage_receipts(
                body_case, stage_map if type(stage_map) is dict else {}, body_before)
            body_execution['source_unchanged_at_every_stage'] = (
                body_execution['source_unchanged_at_every_stage'] and
                body_execution['stage_receipt_gate'].get('admitted') is True)
        except Exception as error:
            receipt_error = error
        if receipt_error is not None:
            return outcome_fn(
                'INCONCLUSIVE', f'{unit_label} stage receipt classification raised an exception',
                evidence=evidence, case=body_case, record=body_record,
                execution=body_execution, phase=phase, receipt_error=receipt_error,
                source_exact=True)
        phase = 'classification'
        try:
            result = classify_fn(
                body_case, parent_case, parent_record, body_record, body_execution, old,
                parent_preparation_sha)
            result['phase'] = phase
            return result
        except Exception as error:
            return outcome_fn(
                'INCONCLUSIVE', f'{unit_label} result classification raised an exception',
                evidence=evidence, case=body_case, record=body_record,
                execution=body_execution, phase=phase, error=error,
                source_exact=True)
    except Exception as error:
        return outcome_fn(
            'INCONCLUSIVE', f'{unit_label} setup or source validation raised an exception',
            evidence=evidence, case=body_case, record=body_record,
            execution=body_execution, phase=phase, error=error,
            source_exact=False if phase == 'source_gate' else None)

def _classify_body_isolation(case, parent_case, parent_record, record, execution, old, parent_preparation_sha):
    if type(execution) is not dict:
        execution = {'execution_type': type(execution).__name__}
    stages = execution.get('stages')
    if execution.get('status') == 'NOT_RUN' or execution.get('classification') == 'NOT_RUN':
        classification = 'NOT_RUN'
        reason = 'body-only diagnostic was explicitly marked not run'
    elif not _body_isolation_source_gate(case, parent_case, parent_record, record, old, parent_preparation_sha):
        classification = 'INCONCLUSIVE'
        reason = 'body-only source, suffix, post or parent-stage identity did not match'
    elif type(stages) is not dict:
        classification = 'INCONCLUSIVE'
        reason = 'required stage result map is missing or has the wrong type'
    elif any(type(stages.get(name)) is not int for name in ('exporter', 'decode', 'verifast', 'refinement')):
        classification = 'INCONCLUSIVE'
        reason = 'required stage result is missing, null or has the wrong type'
    elif execution.get('exception') is not None:
        classification = 'INCONCLUSIVE'
        reason = 'body-only execution raised an exception'
    elif execution.get('source_unchanged_at_every_stage') is not True or \
            type(execution.get('stage_receipt_gate')) is not dict or \
            execution['stage_receipt_gate'].get('admitted') is not True:
        classification = 'INCONCLUSIVE'
        reason = 'exact source/stage receipts were absent, stale or mismatched'
    else:
        log_path = case / 'verifast.log'
        log = log_path.read_text(errors='replace') if log_path.is_file() else ''
        errors = [line for line in log.splitlines() if re.search(r'\berror:', line, re.I)]
        dead = [line for line in log.splitlines() if re.search(r'dead code', line, re.I)]
        target_verified = any(
            (match := re.search(r"Verifying function ['\"]([^'\"]+)['\"]", line)) and
            match.group(1).rsplit('::', 1)[-1] == 'insert_tail'
            for line in log.splitlines())
        stage_zero = all(stages[name] == 0 for name in ('exporter', 'decode', 'verifast', 'refinement'))
        if stage_zero and target_verified and not errors and not dead:
            classification = 'BODY_UNIT_VERIFIER_EXIT0'
            reason = 'complete isolated actual body reached typed verification with all required stages at exit 0'
        elif 124 in stages.values():
            classification = 'INCONCLUSIVE'
            reason = 'a required stage timed out'
        elif 125 in stages.values():
            classification = 'INCONCLUSIVE'
            reason = 'a required stage was skipped or setup did not complete'
        else:
            classification = 'INCONCLUSIVE'
            reason = ('actual insert_tail verifier target was not established' if not target_verified else
                      'a required stage failed, verifier reported an error, or source contained dead code')
    source_exact = _body_isolation_source_gate(
        case, parent_case, parent_record, record, old, parent_preparation_sha)
    result = _body_isolation_outcome(
        classification, reason, evidence=Path(case).parents[2], case=case,
        record=record, execution=execution, phase='classification',
        source_exact=source_exact)
    return result


def _raw_local_caller_outcome(classification, reason, *, evidence, **kwargs):
    result = _body_isolation_outcome(
        classification, reason, evidence=evidence, result_subdir='raw_local_caller', **kwargs)
    result['schema'] = 'r16-raw-local-caller-result-v1'
    result['candidate'] = 'checked raw local-array caller adapter'
    result['verifier_target_observed'] = classification == 'RAW_LOCAL_CALLER_BOTH_TARGETS_EXIT0'
    result['accepted'] = False
    result['proof_credit'] = False
    result['full_target'] = False
    result['b2_achieved'] = False
    result['caller_or_prefix_gate'] = False
    result['independent_credit'] = False
    result['qualification'] = False
    destination = (Path(kwargs['case']) / 'classification.json' if kwargs.get('case') is not None
                   else Path(evidence) / 'raw_local_caller' / 'classification.json')
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    except OSError as write_error:
        result['result_write_exception'] = _body_exception_record(write_error)
    return result


def _classify_raw_local_caller(case, parent_case, parent_record, record, execution,
                               old, parent_preparation_sha, captured_stage_receipt_gate):
    if type(execution) is not dict:
        execution = {'execution_type': type(execution).__name__}
    stages = execution.get('stages')
    source_gate = _raw_local_caller_source_gate(
        case, parent_case, parent_record, record, old, parent_preparation_sha,
        captured_stage_receipt_gate)
    if execution.get('status') == 'NOT_RUN' or execution.get('classification') == 'NOT_RUN':
        classification, reason = 'NOT_RUN', 'raw local caller was explicitly marked not run'
    elif not source_gate:
        classification, reason = 'INCONCLUSIVE', 'raw caller source/parent/stage identity did not match'
    elif type(stages) is not dict:
        classification, reason = 'INCONCLUSIVE', 'required stage result map is missing or has the wrong type'
    elif any(type(stages.get(name)) is not int for name in ('exporter', 'decode', 'verifast', 'refinement')):
        classification, reason = 'INCONCLUSIVE', 'required stage result is missing, null or has the wrong type'
    elif execution.get('exception') is not None:
        classification, reason = 'INCONCLUSIVE', 'raw local caller execution raised an exception'
    elif execution.get('source_unchanged_at_every_stage') is not True or \
            type(execution.get('stage_receipt_gate')) is not dict or \
            execution['stage_receipt_gate'].get('admitted') is not True:
        classification, reason = 'INCONCLUSIVE', 'exact raw-caller source/stage receipts were absent or mismatched'
    else:
        log_path = Path(case) / 'verifast.log'
        log = log_path.read_text(errors='replace') if log_path.is_file() else ''
        lines = log.splitlines()
        errors = [line for line in lines if re.search(r'\berror:', line, re.I)]
        dead = [line for line in lines if re.search(r'dead code', line, re.I)]
        targets = set()
        for line in lines:
            match = re.search(r"Verifying function ['\"]([^'\"]+)['\"]", line)
            if match:
                targets.add(match.group(1).rsplit('::', 1)[-1])
        both_targets = {'insert_tail', 'b2_three_from_local'} <= targets
        if all(stages[name] == 0 for name in ('exporter', 'decode', 'verifast', 'refinement')) and both_targets and not errors and not dead:
            classification = 'RAW_LOCAL_CALLER_BOTH_TARGETS_EXIT0'
            reason = 'actual insert_tail and raw local caller targets reached typed verification with all required stages at exit 0'
        elif 124 in stages.values():
            classification, reason = 'INCONCLUSIVE', 'a required stage timed out'
        elif 125 in stages.values():
            classification, reason = 'INCONCLUSIVE', 'a required stage was skipped or setup did not complete'
        else:
            classification, reason = 'INCONCLUSIVE', ('both actual body and raw wrapper verifier targets were not established'
                if not both_targets else 'a required stage failed, verifier reported an error, or source contained dead code')
    return _raw_local_caller_outcome(
        classification, reason, evidence=Path(case).parents[2], case=case, record=record,
        execution=execution, phase='classification', source_exact=source_gate)


def _run_raw_local_caller_diagnostic(evidence, parent_case, parent_record, old,
                                     consumer, args, selected_profile, dispatch,
                                     *, parent_preparation_sha, parent_source_unchanged,
                                     parent_stage_receipt_gate):
    source_gate = lambda case, pcase, prec, rec, module, prep: _raw_local_caller_source_gate(
        case, pcase, prec, rec, module, prep, parent_stage_receipt_gate)
    classify = lambda case, pcase, prec, rec, run, module, prep: _classify_raw_local_caller(
        case, pcase, prec, rec, run, module, prep, parent_stage_receipt_gate)
    return _run_body_isolation_diagnostic(
        evidence, parent_case, parent_record, old, consumer, args, selected_profile, dispatch,
        parent_preparation_sha=parent_preparation_sha,
        parent_source_unchanged=parent_source_unchanged,
        parent_stage_receipt_gate=parent_stage_receipt_gate,
        prepare_fn=_prepare_raw_local_caller, source_gate_fn=source_gate,
        classify_fn=classify, outcome_fn=_raw_local_caller_outcome,
        unit_label='raw local caller')


def _execute_case_with_r9_trace(execute_case, case, args, env, *, profile,
                                prefix=False, actual_callback_case=False,
                                r11_native_fullbody=False, validated_receipt=None):
    case_env = dict(env)
    case_env.pop(R9_GUARD_TRACE_ENV, None)
    case_env.pop(R11_LABEL_TRACE_ENV, None)
    case_env.pop(R11_LABEL_PLACEMENT_ENV, None)
    case_env.pop(R9_GUARD_RETURN_RECOVERY_ENV, None)
    placement_active = (profile == R11_PROFILE and not prefix and actual_callback_case)
    native_active = placement_active and r11_native_fullbody
    if profile in (R9_PROFILE, R10_PROFILE, R11_PROFILE) and not prefix and actual_callback_case:
        case_env[R9_GUARD_TRACE_ENV] = '1'
        if profile == R11_PROFILE:
            case_env[R11_LABEL_TRACE_ENV] = '1'
        case_env[R9_GUARD_RETURN_RECOVERY_ENV] = '1'
    if placement_active:
        case_env[R11_LABEL_PLACEMENT_ENV] = '1'
    if native_active:
        if not isinstance(validated_receipt, dict) or validated_receipt.get('profile') != profile:
            raise RuntimeError('R11 fullbody native placement requires the validated current R11 receipt')
    sentinel = object()
    previous = getattr(args, 'r11_native_run', sentinel) if native_active else sentinel
    if native_active:
        args.r11_native_run = validated_receipt
    try:
        return execute_case(case, args, case_env)
    finally:
        if native_active:
            if previous is sentinel:
                delattr(args, 'r11_native_run')
            else:
                args.r11_native_run = previous


def _r11_storage_placement_env(env):
    scoped = dict(env)
    scoped.pop(R11_LABEL_PLACEMENT_ENV, None)
    scoped.pop(R11_LABEL_TRACE_ENV, None)
    scoped.pop(R9_GUARD_TRACE_ENV, None)
    scoped.pop(R9_GUARD_RETURN_RECOVERY_ENV, None)
    scoped[R11_LABEL_PLACEMENT_ENV] = '1'
    scoped[R11_LABEL_TRACE_ENV] = '1'
    scoped[R9_GUARD_TRACE_ENV] = '1'
    scoped[R9_GUARD_RETURN_RECOVERY_ENV] = '1'
    return scoped


def classify(case, record, execution, *, baseline_positive=False):
    stages = execution.get('stages', {})
    text = (case / 'verifast.log').read_text(errors='replace') if (case / 'verifast.log').is_file() else ''
    refinement = ''.join((case / name).read_text(errors='replace')
                         for name in ('refinement.log', 'refinement.out') if (case / name).is_file())
    errors = [line for line in text.splitlines() if re.search(r'\berror:', line, re.I)]
    exact = (_sha((case/'original/lib.rs').read_bytes()) == record['original_sha256'] and
             _sha((case/'verified/lib.rs').read_bytes()) == record['verified_sha256'] and
             execution.get('source_unchanged_at_every_stage') is True and
             execution.get('stage_receipt_gate', {}).get('admitted') is True)
    hrtb = bool(re.search(r'MERGE_HRTB_CALL registered=1 .*T=u64 .*', text))
    local = 'MERGE_FIRST_CALLBACK_LOCAL_CONTINUE' in text
    official = ('QUALIFIED_FIRST_FNMUT_CONTINUE_EDGE:' in refinement and stages.get('refinement') == 0)
    first_error = errors[0] if errors else None
    admitted = exact and hrtb and local and official and stages.get('exporter') == 0 and stages.get('decode') == 0
    mutation = record['mutation']
    negative_match = False
    if mutation:
        intended = {
            'lost_reference_fraction': ('ref_initialized', 'close_frac_borrow_token', 'Cannot prove condition'),
            'lost_reference_token': ('lifetime_token',),
            'lost_current_f': ('own',),
            'lost_cell_owner': ('array',),
        }[mutation]
        source = (case/'verified/lib.rs').read_bytes()
        if mutation in ('lost_reference_fraction', 'lost_reference_token'):
            anchor = b'first_callback_close::<'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        elif mutation == 'lost_current_f':
            contract_at = source.index(b'unsafe fn ' + PREFIX_NAME)
            normal_post_at = source.index(b'    *is_less |-> ?normal_f &*& <F>.own(t, normal_f);', contract_at)
            expected_line = source[:normal_post_at].count(b'\n')+1
        else:
            anchor = b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        target_executed = bool(re.search(
            rf'verified/lib\.rs\({expected_line},\d+[^\n]*Executing statement', text))
        error_at_target = bool(first_error and f'({expected_line},' in first_error)
        before_error = text.split(first_error, 1)[0] if first_error else ''
        executions = re.findall(r'verified/lib\.rs\((\d+),\d+[^\n]*Executing statement', before_error)
        last_at_target = bool(executions and int(executions[-1]) == expected_line)
        canonical_spec_error = bool(first_error and (
            mutation == 'lost_reference_fraction' and
            re.search(r'lifetime_logic\.rsspec\(282,', first_error) or
            mutation == 'lost_cell_owner' and
            re.search(r'prelude_core\.rsspec\(293,', first_error)))
        negative_match = bool(baseline_positive and admitted and
                              stages.get('verifast') not in (0,125,None) and first_error and
                              (error_at_target or (canonical_spec_error and last_at_target)) and
                              any(word in first_error for word in intended))
    prefix_proved = bool(admitted and record['prefix'] and mutation is None and
                         stages.get('verifast') == 0 and not errors and 'dead code' not in text.lower())
    runtime_frontiers = {}
    for key in ('actual_first_call_line', 'actual_read_line', 'actual_guard_line', 'actual_shift_line',
                'actual_update_line', 'actual_late_call_line', 'false_return_line'):
        line = record.get(key)
        runtime_frontiers[key] = bool(line and re.search(
            rf'verified/lib\.rs\({line},\d+[^\n]*(?:Executing statement|Executing return statement)', text))
    result = dict(schema='first-callback-result-v1', accepted=False,
                  classification='PREFIX_CURRENT_NORMAL_UNWIND_PROVED' if prefix_proved else
                  'INTENDED_RESOURCE_NEGATIVE' if negative_match else 'INCONCLUSIVE',
                  prefix=record['prefix'], cut=record['cut'], mutation=mutation,
                  stages=stages, source_exact=exact, runtime_frontiers=runtime_frontiers,
                  hrtb_registration_observed=hrtb, local_first_continue_observed=local,
                  official_first_continue_qualified=official,
                  current_false_true_panic_proved=prefix_proved,
                  intended_negative=negative_match,
                  full_insert_tail_proved=False, b2_achieved=False,
                  first_error=first_error, proof_credit=prefix_proved,
                  next_frontier='full body diagnostic required' if prefix_proved else first_error,
                  limitations='Prefix is partial. Registration/reached-call/refiner exit0 alone give no resource credit.')
    (case/'classification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


def run(evidence, args, env, execute_case, validated_receipt):
    if not callable(execute_case):
        raise TypeError('hosted execute_case required')
    campaign_env = dict(env)
    campaign_env.pop(R9_GUARD_TRACE_ENV, None)
    campaign_env.pop(R11_LABEL_TRACE_ENV, None)
    campaign_env.pop(R11_LABEL_PLACEMENT_ENV, None)
    campaign_env.pop(R9_GUARD_RETURN_RECOVERY_ENV, None)
    selected_profile = getattr(args, 'profile', None)
    profile_path = os.environ.get('SMALLSORT_MERGE_PROFILE')
    if (selected_profile not in SUPPORTED_PROFILES or not profile_path or
            json.loads(Path(profile_path).read_text()).get('profile') != selected_profile):
        raise RuntimeError('first callback requires the exact supported experimental profile')
    profile_card = json.loads(Path(profile_path).read_text())
    if 'r22_compile_fix_registration' in profile_card and not _r22_compile_fix_registration_matches(profile_path, selected_profile, profile_card):
        raise RuntimeError('R22 compile-fix registration is not the exact reversible exporter extension')
    if selected_profile == R11_PROFILE and (
            not isinstance(validated_receipt, dict) or
            validated_receipt.get('profile') != selected_profile):
        raise RuntimeError('R11 first callback requires the validated current R11 receipt')
    proof = _load('first_callback_hosted_proof', HERE.parents[1] / 'merge/overnight/copy-on-drop-prove.py')
    proof.require_hosted_cloud()
    consumer = _load('first_callback_receipt', HERE/'concrete-consumer.py')
    provider, proof_sha = proof.require_hosted_cloud()
    consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    r17_controls_enabled = _r17_registration_matches(
        profile_path, selected_profile, validated_receipt)
    r19_controls_enabled = _r19_registration_matches(profile_path, selected_profile)
    evidence.mkdir(parents=True, exist_ok=False)
    def dispatch(case, case_args, case_env=None, *, prefix=False, actual_callback_case=False,
                 body_isolation_native=False):
        case_path = Path(case)
        if body_isolation_native and (selected_profile != R11_PROFILE or not actual_callback_case):
            raise RuntimeError('R11 body-isolation native placement requires current R11 actual-body scope')
        return _execute_case_with_r9_trace(
            execute_case, case_path, case_args, campaign_env if case_env is None else case_env,
            profile=selected_profile,
            prefix=prefix, actual_callback_case=actual_callback_case,
            r11_native_fullbody=(
                (case_path.name == 'actual_three_current_full_posts' and
                 case_path.parent.name == 'cases' and
                 case_path.parent.parent.name == 'full_body') or body_isolation_native),
            validated_receipt=validated_receipt)
    share_controls = _load('r6_share_controls', HERE/'r6-share-controls.py')
    results = {'share_representation_controls': share_controls.run(
        evidence/'share-representation-controls', args, campaign_env,
        lambda case, case_args, case_env: dispatch(case, case_args, case_env),
        representation=U64_SHARE_REPRESENTATION)}
    array_controls = _load('r7_array_controls', HERE/'r7-array-controls.py')
    results['guard_array_controls'] = array_controls.run(
        evidence/'guard-array-controls', args, campaign_env,
        lambda case, case_args, case_env: dispatch(case, case_args, case_env),
        helper=GUARD_EMPTY_TAIL_HELPER)
    cases = [('prefix', True, None), ('full_body', False, None)] + [
        (name, True, name) for name in ('lost_reference_fraction', 'lost_reference_token',
                                      'lost_current_f', 'lost_cell_owner')]
    previous_flag = getattr(args, 'first_fnmut_continue', False)
    previous_r8_flag = getattr(args, 'r8_owned_array_allocation', False)
    args.first_fnmut_continue = True
    args.r8_owned_array_allocation = False
    captured_parent_identity = None
    full_body_execution_observation = None
    try:
        for name, prefix, mutation in cases:
            if mutation and not results['prefix']['current_false_true_panic_proved']:
                results[name] = dict(classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED',
                                     intended_negative=False, proof_credit=False)
                continue
            case, record = prepare(evidence/name, prefix=prefix, mutation=mutation, profile=selected_profile)
            if name == 'full_body':
                captured_parent_identity = {'record': copy.deepcopy(record), 'preparation_sha256': None,
                                            'receipt_error': None}
                try:
                    prep_bytes = (evidence/'full_body/preparation.json').read_bytes()
                    if json.loads(prep_bytes) != record:
                        raise ValueError('full-body preparation receipt did not match prepared record')
                    captured_parent_identity['preparation_sha256'] = _sha(prep_bytes)
                except Exception as error:
                    captured_parent_identity['receipt_error'] = error
            before = consumer._hashes(case)
            args.r8_owned_array_allocation = (selected_profile in (R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE) and not prefix)
            try:
                execution = dispatch(case, args, prefix=prefix,
                                     actual_callback_case=(name == 'full_body'))
            finally:
                args.r8_owned_array_allocation = False
            execution['stage_receipt_gate'] = consumer._stage_receipts(case, execution.get('stages', {}), before)
            execution['source_unchanged_at_every_stage'] = (before == consumer._hashes(case) and
                execution['stage_receipt_gate'].get('admitted') is True)
            if name == 'full_body':
                full_body_execution_observation = {
                    'source_unchanged': execution.get('source_unchanged_at_every_stage'),
                    'stage_receipt_gate': copy.deepcopy(execution.get('stage_receipt_gate')),
                }
            results[name] = classify(case, record, execution,
                                     baseline_positive=results.get('prefix', {}).get('current_false_true_panic_proved', False))
        parent_case = evidence/'full_body/cases/actual_three_current_full_posts'
        try:
            old_body = _load('r16_body_isolation_source', HERE / 'actual-insert-tail-b2.py')
            if (captured_parent_identity is None or
                    captured_parent_identity.get('preparation_sha256') is None or
                    full_body_execution_observation is None):
                raise ValueError('pre-dispatch full-body identity/receipt capture is incomplete')
            if captured_parent_identity.get('receipt_error') is not None:
                results['body_isolation'] = _body_isolation_outcome(
                    'INCONCLUSIVE', 'pre-dispatch full-body preparation receipt capture failed',
                    evidence=evidence, phase='parent_identity',
                    error=captured_parent_identity['receipt_error'])
            else:
                results['body_isolation'] = _run_body_isolation_diagnostic(
                    evidence, parent_case, captured_parent_identity['record'], old_body,
                    consumer, args, selected_profile, dispatch,
                    parent_preparation_sha=captured_parent_identity['preparation_sha256'],
                    parent_source_unchanged=full_body_execution_observation.get('source_unchanged'),
                    parent_stage_receipt_gate=full_body_execution_observation.get('stage_receipt_gate'))
        except Exception as error:
            results['body_isolation'] = _body_isolation_outcome(
                'INCONCLUSIVE', 'body-only parent identity setup raised an exception',
                evidence=evidence, phase='parent_identity', error=error)
        try:
            control_identity = (dict(captured_parent_identity,
                                     full_body_execution_observation=full_body_execution_observation)
                                if captured_parent_identity is not None else None)
            def run_rawptr_controls():
                rawptr_controls = _load('r17_rawptr_controls', HERE / 'r17-rawptr-controls.py')
                return rawptr_controls.run(
                    evidence, args, campaign_env, dispatch, consumer, selected_profile,
                    source_sha256=captured_parent_identity['record'].get('source_sha256'))
            results['rawptr_controls'] = _run_r17_controls_if_registered(
                r17_controls_enabled, control_identity, run_rawptr_controls)
        except Exception as error:
            results['rawptr_controls'] = dict(
                classification='INCONCLUSIVE', all_matched=False,
                reason='RawPtr control setup or dispatch raised an exception',
                exception_type=type(error).__name__, exception=str(error),
                accepted=False, proof_credit=False, b2_achieved=False)
        try:
            if (captured_parent_identity is None or
                    captured_parent_identity.get('preparation_sha256') is None or
                    full_body_execution_observation is None):
                raise ValueError('pre-dispatch full-body identity/receipt capture is incomplete')
            if captured_parent_identity.get('receipt_error') is not None:
                results['raw_local_caller'] = _raw_local_caller_outcome(
                    'INCONCLUSIVE', 'pre-dispatch full-body preparation receipt capture failed',
                    evidence=evidence, phase='parent_identity',
                    error=captured_parent_identity['receipt_error'])
                results['raw_local_caller']['rawptr_controls'] = _rawptr_controls_summary(
                    results.get('rawptr_controls'))
            else:
                old_raw = _load('r16_raw_local_caller_source', HERE / 'actual-insert-tail-b2.py')
                results['raw_local_caller'] = _run_raw_local_caller_after_controls(
                    results.get('rawptr_controls'),
                    lambda: _run_raw_local_caller_diagnostic(
                        evidence, parent_case, captured_parent_identity['record'], old_raw,
                        consumer, args, selected_profile, dispatch,
                        parent_preparation_sha=captured_parent_identity['preparation_sha256'],
                        parent_source_unchanged=full_body_execution_observation.get('source_unchanged'),
                        parent_stage_receipt_gate=full_body_execution_observation.get('stage_receipt_gate')))
        except Exception as error:
            results['raw_local_caller'] = _raw_local_caller_outcome(
                'INCONCLUSIVE', 'raw local caller parent identity setup raised an exception',
                evidence=evidence, phase='parent_identity', error=error)
            results['raw_local_caller']['rawptr_controls'] = _rawptr_controls_summary(
                results.get('rawptr_controls'))
        raw_case = evidence / 'raw_local_caller' / 'cases' / RAW_LOCAL_CALLER_NAME
        if not r19_controls_enabled:
            results['r19_unwind_controls'] = dict(
                classification='NOT_APPLICABLE_R19_REGISTRATION_ABSENT', all_matched=False,
                accepted=False, proof_credit=False, b2_achieved=False)
        elif not (raw_case / 'verified/lib.rs').is_file() or not _r19_raw_case_matches(evidence, raw_case):
            results['r19_unwind_controls'] = dict(
                classification='NOT_RUN_RAW_CALLER_NOT_PREPARED', all_matched=False,
                accepted=False, proof_credit=False, b2_achieved=False)
        else:
            try:
                r19_controls = _load('r19_unwind_controls', HERE / 'r19-unwind-controls.py')
                results['r19_unwind_controls'] = r19_controls.run(
                    evidence, raw_case, args, dispatch, consumer, selected_profile,
                    source_sha256=captured_parent_identity['record'].get('source_sha256'))
            except Exception as error:
                results['r19_unwind_controls'] = dict(
                    classification='INCONCLUSIVE', all_matched=False,
                    reason='R19 unwind control setup or dispatch raised an exception',
                    exception_type=type(error).__name__, exception=str(error),
                    accepted=False, proof_credit=False, b2_achieved=False)
        if selected_profile == R11_PROFILE:
            placement = _load('r11_storage_placement_controls', HERE/'r11-storage-placement-controls.py')
            positive_case = evidence/'full_body/cases/actual_three_current_full_posts'
            source_record = json.loads((evidence/'full_body/preparation.json').read_text())
            placement_env = _r11_storage_placement_env(campaign_env)
            previous_r11_r8 = getattr(args, 'r8_owned_array_allocation', False)
            args.r8_owned_array_allocation = True
            try:
                results['storage_placement_controls'] = placement.run(
                    evidence/'r11-storage-placement-controls', args, placement_env,
                    positive_case, source_record, validated_run=validated_receipt)
            finally:
                args.r8_owned_array_allocation = previous_r11_r8
        if selected_profile == R7_PROFILE:
            geometry_controls = _load('r8_geometry_controls', HERE/'r8-geometry-controls.py')
            results['allocation_geometry_controls'] = geometry_controls.run(
                evidence/'allocation-geometry-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env))
        if selected_profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE):
            late_controls = _load('r7_late_admission', HERE/'r7-late-admission-controls.py')
            results['late_scope_admission_controls'] = late_controls.run(
                evidence/'late-scope-admission-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(
                    case, case_args, case_env,
                    actual_callback_case=(selected_profile in (R9_PROFILE, R10_PROFILE, R11_PROFILE))),
                evidence/'full_body/cases/actual_three_current_full_posts',
                json.loads((evidence/'full_body/preparation.json').read_text()))
        if selected_profile in (R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE):
            freshness = _load('r8_freshness_controls', HERE/'r8-freshness-controls.py')
            freshness_kwargs = ({'validated_run': validated_receipt}
                                if selected_profile in (R10_PROFILE, R11_PROFILE) else {})
            results['owned_array_allocation_freshness_controls'] = freshness.run(
                evidence/'owned-array-allocation-freshness-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env),
                **freshness_kwargs)
        if selected_profile in (R9_PROFILE, R10_PROFILE, R11_PROFILE):
            guard_controls = _load('r9_guard_return_controls', HERE/'r9-guard-return-controls.py')
            args.r8_owned_array_allocation = True
            try:
                results['guard_return_recovery_controls'] = guard_controls.run(
                    evidence/'guard-return-recovery-controls', args, campaign_env,
                    lambda case, case_args, case_env: dispatch(
                        case, case_args, case_env, actual_callback_case=True),
                    evidence/'full_body/cases/actual_three_current_full_posts',
                    json.loads((evidence/'full_body/preparation.json').read_text()))
            finally:
                args.r8_owned_array_allocation = False
        if results['prefix']['current_false_true_panic_proved']:
            controls = _load('first_callback_admission', HERE/'first-callback-admission-controls.py')
            results['admission_controls'] = controls.run(
                evidence/'admission-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env),
                evidence/'prefix/cases/actual_three_current_full_posts',
                {**json.loads((evidence/'prefix/preparation.json').read_text()),
                 'full_body_case': str(evidence/'full_body/cases/actual_three_current_full_posts'),
                 'full_body_source_record': json.loads((evidence/'full_body/preparation.json').read_text())})
        else:
            results['admission_controls'] = dict(all_matched=False,
                classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED', proof_credit=False)
    finally:
        args.first_fnmut_continue = previous_flag
        args.r8_owned_array_allocation = previous_r8_flag
    aggregate = dict(schema='first-callback-campaign-v1', profile=selected_profile, accepted=False,
                     results=results, b2_achieved=False,
                     body_only_component_observation=(
                         results.get('body_isolation', {}).get('classification') ==
                         'BODY_UNIT_VERIFIER_EXIT0'),
                     prefix_current_normal_unwind_proved=results['prefix']['current_false_true_panic_proved'],
                     all_target_controls_matched=(
                         results['prefix']['current_false_true_panic_proved'] and
                         all(results[name].get('intended_negative') is True for name in
                             ('lost_reference_fraction', 'lost_reference_token', 'lost_current_f', 'lost_cell_owner')) and
                         results['admission_controls'].get('all_matched') is True),
                     rawptr_controls_matched=(results.get('rawptr_controls', {}).get('all_matched') is True),
                     r19_unwind_controls_matched=(results.get('r19_unwind_controls', {}).get('all_matched') is True),
                     classification='DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH')
    (evidence/'aggregate.json').write_text(json.dumps(aggregate, indent=2, sort_keys=True)+'\n')
    return aggregate
