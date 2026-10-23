"""Exact R23 source-preserving profile extension; reverses to diagnostic profile3fec."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

BASELINE_SHA256 = '3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88'
PROFILE_SHA256 = '0124f6a0266d92ce9e70054b4410b663883c3e6233242019ae525f6cd146c7b7'
REGISTRATION = {'schema': 'merge-r23-checked-source-borrow-registration-v1', 'phase_id': 'MERGE-CALLER-ACCEPTANCE-R23-2026-10-24', 'baseline_profile_sha256': '3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88', 'starting_tool_commit': 'fc0208d4f53583d458670cd07bd0370636d4b2eb', 'candidate_tool_commit': '966c6d23f75da38472a1b1039ee99fe5a88f2632', 'tool_source_paths': ['src/rust_frontend/vf_mir_exporter/src/lib.rs', 'src/rust_frontend/vf_mir/vf_mir.capnp', 'src/refinement_checker/refinement_checker.ml', 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml', 'src/rust_frontend/vf_mir_translator/vf_mir_capnp_alias.ml'], 'source_pins': {'src/rust_frontend/vf_mir_exporter/src/lib.rs': 'bf321171e83a28ddc64f026e203c32f2cb7b0c3353bfe1197131eab287eb1381', 'src/rust_frontend/vf_mir/vf_mir.capnp': 'e9942a875a4177de95c6c6b0777e4b2dfcfea65ffd576d8ebc94950d9a2ca014', 'src/refinement_checker/refinement_checker.ml': 'b68454fafab7e1360fccae300b14712356c230e7a28a25b252c7a50121dc269a', 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '44dc56339c4b23c753b1f4e59e89520cfb3ba09514464fd1aad19493a1c16ace', 'src/rust_frontend/vf_mir_translator/vf_mir_capnp_alias.ml': 'a11c33a8a6b9ecb3021443fffe7abc7ff4884924dbb5ea4f3dc523b800f352de'}, 'activation_environment': 'SMALLSORT_R23_SOURCE_ARRAY_BORROW', 'source_applicability': 'exact marked u64 array3 Ref/Unsize/as_mut_ptr chain; checked source lifetime and reversible existing full_borrow resources; complete actual callee/helper typed cast-body equivalence; original normal/unwind action and runtime unchanged; default off; no new trusted premise'}
PATCH = {'path': 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch', 'sha256': '2a90b5b527da6a6b5eb4c56fc55f00035a0f4adf4fe13673ad9ce2fe35793acc'}
BASELINE_VALUES = {'effective_tool_commit': 'fc0208d4f53583d458670cd07bd0370636d4b2eb', 'exporter_source_sha256': '7bdf554c34feaa15a96f0d652be272bddae2c915a0122e5af09adfe9acd4430d', 'schema_sha256': 'ed44ed45da772052e0b767beb47ef33af958ac6ee7bd03f3c100d9f906f6eb92', 'refiner_core_source_sha256': '11a0ff9057e6da92a684c20b1cda1e4825d986ea6d80980a7a967f236f0c9db8', 'translator_sha256': 'bc60d926e5b34aeaa5f18ca6b08d2f9c0e707bd2d537e9081ea762d5a41fcfb2', 'guard_return_trace_patch_sha256': '097f1ea2caba540a6c2fbff51bcded4726f4fb73536dbc6e803423f70b9df9c5'}
CANDIDATE_VALUES = {'effective_tool_commit': '966c6d23f75da38472a1b1039ee99fe5a88f2632', 'exporter_source_sha256': 'bf321171e83a28ddc64f026e203c32f2cb7b0c3353bfe1197131eab287eb1381', 'schema_sha256': 'e9942a875a4177de95c6c6b0777e4b2dfcfea65ffd576d8ebc94950d9a2ca014', 'refiner_core_source_sha256': 'b68454fafab7e1360fccae300b14712356c230e7a28a25b252c7a50121dc269a', 'translator_sha256': '44dc56339c4b23c753b1f4e59e89520cfb3ba09514464fd1aad19493a1c16ace', 'guard_return_trace_patch_sha256': '2a90b5b527da6a6b5eb4c56fc55f00035a0f4adf4fe13673ad9ce2fe35793acc'}


def serialize(profile):
    return (json.dumps(profile, indent=2, ensure_ascii=False) + "\n").encode()

def reverse_profile(profile):
    if type(profile) is not dict or hashlib.sha256(serialize(profile)).hexdigest() != PROFILE_SHA256:
        raise ValueError("R23 exact profile bytes differ")
    if profile.get("r23_source_borrow_registration") != REGISTRATION:
        raise ValueError("R23 source-borrow registration differs")
    chain = profile.get("ordered_patch_chain")
    if type(chain) is not list or len(chain) != 19 or chain[-1] != PATCH:
        raise ValueError("R23 complete ordered patch chain differs")
    if any(profile.get(key) != value for key, value in CANDIDATE_VALUES.items()):
        raise ValueError("R23 exact candidate source/tool pin differs")
    baseline = copy.deepcopy(profile)
    del baseline["r23_source_borrow_registration"]
    baseline["ordered_patch_chain"][-1]["sha256"] = BASELINE_VALUES["guard_return_trace_patch_sha256"]
    baseline.update(BASELINE_VALUES)
    if hashlib.sha256(serialize(baseline)).hexdigest() != BASELINE_SHA256:
        raise ValueError("R23 extension does not reverse byte-exactly to profile3fec")
    return baseline

def validate_tool_sources(tool_home, profile):
    reverse_profile(profile)
    for relative, expected in REGISTRATION["source_pins"].items():
        if hashlib.sha256((Path(tool_home) / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("R23 actual tool source differs: " + relative)

HELPER_PINS = {'R23-SOURCE-BORROW-TEMPLATE-20261024.rs': 'e7e0580876e2b43c964d4e366188fcdc462b5a5817b5c14e422ad7e1b8a7f19f', 'r23-array3-borrow-content.rs': 'dd925b2a140875496fb14d1a80368a29cfb60626da91821ab593c67e95c929ef', 'r23-checked-slice-as-mut-ptr.rs': '14f3ab4939f5cdc4c0fde69157464b132811dbbbbe9962f15b67ae276c8663c6'}

def validate_helper_sources(root):
    for relative, expected in HELPER_PINS.items():
        if hashlib.sha256((Path(root) / relative).read_bytes()).hexdigest() != expected:
            raise ValueError("R23 source helper differs: " + relative)
