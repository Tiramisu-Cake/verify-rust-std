"""Fail-closed Cloud entry and staged A1 first-matrix orchestration.

Source preparation, one tool reconstruction, focused raw collection and the
structural observation bridge are explicit callables. Admission and summary
publication remain unreachable until the same-Build proof classifier and all
26 rows have reviewed observation hooks. Importing this module is inert.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Mapping


PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
PROFILE = HERE / "A1-RCG-PROFILE-2026-10-17.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")

# Order is part of the first-matrix plan. OFF checks default-off behavior;
# P0a/P0b are actual focused threshold bodies and native conformance, before
# any caller summary can be published. R1-R7 are fresh on the final A1 tool.
CASE_ORDER = (
    "OFF", "P0a", "P0b", "P0c", "P-dispatch", "P1",
    "N-binder-collapse", "N-alpha-valid", "N-free-region", "N-region-swap",
    "N-no-F", "N-clauses", "N-default-contract", "N-freeze-contract",
    "N-false31", "N-source", "N-binding", "N-clause-redirect",
    "N-duplicate", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
)
SOURCE_CASE = {
    "P0a": "P0a", "P0b": "P0b", "P0c": "P0c",
    "P-dispatch": "P-dispatch", "P1": "P1",
    "N-default-contract": "N-default-contract",
    "N-freeze-contract": "N-freeze-contract", "N-false31": "N-false31",
}
SYNTHETIC_MUTATION = {
    "N-binder-collapse": "binder_collapse",
    "N-alpha-valid": "alpha_valid",
    "N-free-region": "free_region_input",
    "N-region-swap": "input_region_swap",
    "N-no-F": "no_F",
    "N-clauses": "remove_fnmut and remove_output in separate isolated inputs",
    "N-duplicate": "duplicate_impl_method",
}
SYNTHETIC_INPUT_PLAN = {
    "N-binder-collapse": ("binder_collapse",),
    "N-alpha-valid": ("alpha_valid",),
    "N-free-region": ("free_region_input",),
    "N-region-swap": ("input_region_swap",),
    "N-no-F": ("no_F",),
    "N-clauses": ("remove_fnmut", "remove_output"),
    "N-duplicate": ("duplicate_impl_method",),
}
LEGACY_CONTROL = {
    "R1": "canonical-generic", "R2": "canonical-mu",
    "R3": "consumer-positive", "R4": "consumer-wrong-pointer",
    "R5": "consumer-missing-raw-rights",
    "R6": "consumer-mu-cast-no-initialized-T",
    "R7": "threshold-body-positive",
}

# Each missing adapter must return actual same-Build compiler, AST, stage, and
# location observations. A declared expected outcome or service-shaped record
# is not an implementation of any hook.
MISSING_BACKEND_HOOKS = {
    "reviewed_helper_pins":
        "Freeze and review exact hashes for every A1 source helper in a1_helper_sha256; no unpinned dynamic import.",
    "focused_threshold_body_and_conformance":
        "Derive exactly one actually checked body and separate native conformance from pinned focus/kernel semantics, same-invocation verifier stage/VF0 and full AST posts; a focus flag or AST alone is insufficient.",
    "exact_a1_classifier":
        "Classify actual current verifier stage and first causal predicate/location, including negative post failures, before writing any service-shaped record.",
    "full_small_sort_p1_interface":
        "Bind compiler RequiredFn Self/F and all three scoped input regions plus full clauses to the final common small_sort Func and both numeric impl signatures; compare complete native pre/returning/unwind AST subtrees under a scoped positional alpha map. Existing threshold-only AST gates cannot supply P1.",
    "synthetic_and_admission_controls":
        "Complete isolated decoded-VfMir transport, legacy redirect, source/binding mutation refusals, and N-clauses isolated inputs; preserve interface-only zero-body credit.",
    "fresh_legacy_controls":
        "Run R1-R7 in isolated sources on the final tool using driver.verify_one/classify and adapt only current observed stages to A1 admission records.",
    "default_off_control":
        "Run OFF with the A1 R/C opt-in disabled on the final tool and classify the original duplicate trait-parameter behavior without proof credit.",
}

A1_HELPERS = (
    "a1-fixtures.py", "a1-tool.py", "a1-focus-backend.py",
    "a1-compiler-inventory.py", "a1-call-binding.py", "a1-ast-gates.py",
    "a1-synthetic-inputs.py", "a1-synthetic-backend.py",
    "a1-contract-admission.py", "a1-summary-receipt.py",
    "a1-proof-classifier.py", "selected-proof.py",
)
FOCUS_SEMANTICS_PINS = {
    "src/verifast.ml": "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c",
    "src/verifast1.ml": "bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207",
    "src/verify_expr.ml": "c2246e54f06fe099b5ddb6ba500aba4f6186498b1a44cb8a51b3389b18fe8ca9",
    "src/vfconsole/vfconsole.ml": "79179baa9ad9e9cb2ee5163f4c9528f665519d894c43093183fd8e9f31b06898",
}


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("A1-RUNNER: " + why)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pinned_helpers(proof_root: Path, profile: Mapping[str, Any]) -> dict[str, Any]:
    """Import only the exact reviewed proof-checkout helper bytes.

    This performs no Cloud work. A missing helper or hash stops before any
    fixture generation, reconstruction, or verifier process.
    """
    hashes = profile.get("a1_helper_sha256")
    _need(isinstance(hashes, dict) and set(hashes) == set(A1_HELPERS),
          "complete exact a1_helper_sha256 map required")
    loaded = {}
    for filename in A1_HELPERS:
        expected = hashes[filename]
        path = (proof_root / HERE / filename).resolve()
        _need(path.is_file() and HEX64.fullmatch(expected) is not None and
              _sha(path) == expected, "pinned A1 helper differs: " + filename)
        name = "a1_runner_" + filename.replace("-", "_").replace(".", "_")
        spec = importlib.util.spec_from_file_location(name, path)
        _need(spec is not None and spec.loader is not None,
              "A1 helper cannot be imported: " + filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        _need(Path(module.__file__).resolve() == path and _sha(path) == expected,
              "A1 helper changed during import: " + filename)
        loaded[filename] = module
    return loaded


def prepare_source_fixtures(a, helpers: Mapping[str, Any], ghost) -> tuple[Path, dict]:
    """Construct eight certified Rust units and isolated source pairs in Cloud."""
    module = helpers["a1-fixtures.py"]
    source_root = Path(a.proof_root).resolve()
    package = module.construct(source_root)
    output = Path(a.evidence) / "a1-source-package"
    module._write_package(package, output)
    cert_path = output / "source-certificate.json"
    cert = json.loads(cert_path.read_text())
    _need(set(cert["cases"]) == set(SOURCE_CASE.values()) and
          cert.get("phase_id") == PHASE and
          cert.get("proof_credit") is False,
          "exact eight source-certified A1 units")
    for case_id, row in cert["cases"].items():
        source = (output / row["source_file"]).read_bytes()
        _need(hashlib.sha256(source).hexdigest() == row["generated_source_sha256"],
              "certified source bytes changed: " + case_id)
        fixture = Path(a.evidence) / "a1-fixtures" / case_id
        (fixture / "verified").mkdir(parents=True, exist_ok=False)
        (fixture / "original").mkdir(parents=True, exist_ok=False)
        (fixture / "verified/lib.rs").write_bytes(source)
        (fixture / "original/lib.rs").write_bytes(ghost.strip_ghost(source))
    positive = [cert["cases"][case]["generated_source_sha256"]
                for case in ("P0a", "P0b", "P0c", "P-dispatch", "P1")]
    _need(len(set(positive)) == 1, "positive source pair bytes are not identical")
    return cert_path, cert


def prepare_legacy_fixtures(a, driver, helper, ghost, manifest: dict) -> dict:
    """Create fresh R1-R7 source pairs from pinned legacy templates only."""
    rows = {}
    for case_id, name in LEGACY_CONTROL.items():
        fixture, cert = driver.make_fixture(a, helper, ghost, manifest, name)
        verified = fixture / "verified/lib.rs"
        original = fixture / "original/lib.rs"
        _need(verified.is_file() and original.is_file() and
              _sha(verified) == cert["verified_sha256"] and
              _sha(original) == cert["original_sha256"] and
              original.read_bytes() == ghost.strip_ghost(verified.read_bytes()),
              "fresh legacy source pair changed: " + case_id)
        source_id = cert["source_template_sha256"]
        unit_id = hashlib.sha256((cert["verified_sha256"] + ":" +
                                  cert["original_sha256"] + ":" +
                                  cert["target"]).encode("ascii")).hexdigest()
        rows[case_id] = {"fixture": str(fixture), "certificate": cert,
                         "source_id": source_id, "unit_id": unit_id,
                         "proof_credit": False}
    _need(set(rows) == set(LEGACY_CONTROL), "seven fresh legacy controls")
    return rows


def prepare_off_fixture(a, selected, driver, ghost, manifest: dict,
                        profile: Mapping[str, Any]) -> dict:
    """Use the exact old selected positive source with A1 opt-in disabled."""
    pin_path = Path(a.proof_root) / HERE / "SELECTED-BRANCH-BINDING-PINS.json"
    _need(pin_path.is_file() and
          _sha(pin_path) == profile.get("stable_threshold_pins_sha256"),
          "old selected source pin inventory changed")
    pins = json.loads(pin_path.read_text())
    selected.source_correspondence(a, manifest, driver, ghost)
    template_path = Path(a.proof_root) / HERE / "selected-branch-cases.rs"
    template = template_path.read_text(encoding="utf-8")
    name = "selected-branch-positive"
    fixture = selected.make_selected_fixture(
        a, driver, ghost, template, name,
        pins["case_verified_lib_md5"][name])
    verified = fixture / "verified/lib.rs"
    original = fixture / "original/lib.rs"
    _need(original.read_bytes() == ghost.strip_ghost(verified.read_bytes()),
          "OFF selected source pair changed")
    unit_id = hashlib.sha256((_sha(verified) + ":" + _sha(original) + ":" +
                              selected.SELECTED[name]).encode("ascii")).hexdigest()
    return {"fixture": str(fixture), "source_id": _sha(template_path),
            "unit_id": unit_id, "verified_sha256": _sha(verified),
            "original_sha256": _sha(original), "proof_credit": False}


def prepare_synthetic_inputs(a, mutator, *, baseline_decoded: Path,
                             inventory: Mapping[str, Any],
                             certificate: Mapping[str, Any]) -> dict:
    """Materialize isolated decoded controls from an actual paired VfMir dump.

    These messages have synthetic-only provenance. Actual translator
    invocation and refusal classification remain separate later stages.
    """
    _need(baseline_decoded.is_file() and
          baseline_decoded.is_relative_to(Path(a.evidence).resolve()) and
          set(SYNTHETIC_INPUT_PLAN) == set(SYNTHETIC_MUTATION),
          "paired same-Build synthetic baseline required")
    original = baseline_decoded.read_text(encoding="utf-8")
    _need(len(mutator.parse_records(original)) == 1,
          "one complete compiler-derived baseline VfMir message")
    baseline_sha = _sha(baseline_decoded)
    positive = certificate["cases"]["P1"]
    synthetic_source_id = hashlib.sha256(
        (positive["source_id"] + ":" + baseline_sha).encode("ascii")).hexdigest()
    selected = [row for row in inventory["inventory"]["impls"]
                if row["impl"] == "default16"]
    _need(len(selected) == 1, "one compiler default impl for duplicate control")
    impl_id = selected[0]["impl_def_index"]
    root = Path(a.evidence) / "a1-synthetic-inputs"
    root.mkdir(parents=True, exist_ok=False)
    rows = {}
    for case_id, mutations in SYNTHETIC_INPUT_PLAN.items():
        case_root = root / case_id
        case_root.mkdir()
        messages = []
        for mutation in mutations:
            rendered, metadata = mutator.mutate_required_fn(
                original, mutation,
                impl_def_index=impl_id if mutation == "duplicate_impl_method" else None)
            _need(metadata.get("synthetic") is True and
                  metadata.get("compiler_derived") is False and
                  metadata.get("proof_credit") is False,
                  "synthetic provenance marker required")
            path = case_root / (mutation + ".txt")
            path.write_text(rendered, encoding="utf-8")
            messages.append({"mutation": mutation, "path": str(path),
                             "sha256": _sha(path), "metadata": metadata})
        rows[case_id] = {"baseline_sha256": baseline_sha,
                         "messages": messages,
                         "source_id": synthetic_source_id,
                         "unit_id": hashlib.sha256(json.dumps({
                             "verified": positive["generated_source_sha256"],
                             "target": "StableSmallSortTypeImpl::small_sort",
                             "mutations": [(row["mutation"], row["sha256"])
                                           for row in messages],
                         }, sort_keys=True).encode()).hexdigest(),
                         "proof_credit": False}
    _need(set(rows) == set(SYNTHETIC_INPUT_PLAN),
          "complete isolated synthetic input family")
    return rows


def prepare_admission_control_inputs(a, call_binding_module, inventory_module, *,
                                     certificate: Mapping[str, Any],
                                     certificate_path: Path,
                                     normal_decoded: Path,
                                     readonly_decoded: Path) -> dict:
    """Materialize wrong certificate, wrong binding, and forced redirect inputs.

    This only prepares bytes. Their refusals require later actual admission or
    translator observations at the intended stages.
    """
    _need(normal_decoded.is_file() and readonly_decoded.is_file() and
          certificate_path.is_file(), "same-Build control inputs missing")
    source_case = certificate["cases"]["P1"]
    source_path = certificate_path.parent / source_case["source_file"]
    source = source_path.read_text(encoding="utf-8")
    _need(_sha(source_path) == source_case["generated_source_sha256"],
          "control source bytes changed")
    normal_text = normal_decoded.read_text(encoding="utf-8")
    readonly_text = readonly_decoded.read_text(encoding="utf-8")
    binding = call_binding_module.observe(
        "P1", normal_text, readonly_text, dict(certificate), source)
    compiler_inventory = inventory_module.observe(
        "P1", normal_text, readonly_text, dict(certificate), source)
    _need(binding["case_binding"]["source_pair_id"] ==
          compiler_inventory["case_binding"]["source_pair_id"],
          "P1 control inventory and call binding source pair differ")
    common = [row for row in binding["binding"]["calls"]
              if row["callee"] == "StableSmallSortTypeImpl::small_sort"]
    _need(len(common) == 1, "one original common small_sort binding")
    required = {name: ident for ident, name in
                compiler_inventory["inventory"]["required_method_ids"]}
    _need(set(required) == {"small_sort_threshold", "small_sort"},
          "closed required-item compiler inventory")
    correct = {"schema": "a1-common-binding-claim-v1", "caller": "quicksort",
               "method": "small_sort", "call_line": common[0]["call_line"],
               "callee": "StableSmallSortTypeImpl::small_sort",
               "substs": ["T", "F"], "late_bound_lifetime_count": 3,
               "argument_roots": ["v", "scratch", "is_less"],
               "compiler_trait_item_id": required["small_sort"]}
    call_binding_module.validate_common_binding_claim(binding, compiler_inventory,
                                                       correct)
    wrong_certificate = deepcopy(dict(certificate))
    wrong_certificate["cases"]["P1"]["generated_source_sha256"] = "0" * 64
    _need(wrong_certificate["cases"]["P1"]["generated_source_sha256"] !=
          source_case["generated_source_sha256"],
          "source certificate mutation must change bytes")
    wrong_binding = {**correct, "selected_impl_id":
                     compiler_inventory["inventory"]["impls"][0]["impl_def_index"]}
    forced_redirect = {"SORT4_A1_FORCE_LEGACY_REDIRECT": "1",
                       "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                       "source_pair_sha256": source_case["generated_source_sha256"]}
    values = {"N-source": wrong_certificate,
              "N-binding": wrong_binding,
              "N-clause-redirect": forced_redirect}
    root = Path(a.evidence) / "a1-admission-controls"
    root.mkdir(parents=True, exist_ok=False)
    source_id = hashlib.sha256((source_case["source_id"] + ":" +
                                _sha(normal_decoded) + ":" +
                                _sha(readonly_decoded)).encode("ascii")).hexdigest()
    rows = {}
    for case_id, value in values.items():
        path = root / (case_id + ".json")
        path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
        rows[case_id] = {"path": str(path), "input_sha256": _sha(path),
                         "source_id": source_id,
                         "unit_id": hashlib.sha256((case_id + ":" + _sha(path) +
                                                    ":" + source_case["unit_id"])
                                                   .encode("ascii")).hexdigest(),
                         "proof_credit": False}
    return rows


def materialize_expected_cases(admission_module, certificate: Mapping[str, Any],
                               synthetic: Mapping[str, Any],
                               legacy: Mapping[str, Any], off: Mapping[str, Any],
                               controls: Mapping[str, Mapping[str, Any]],
                               bound_impls: Mapping[str, Mapping[str, str]]) -> dict:
    """Bind all 26 expected IDs to actual produced source/input bytes."""
    _need(set(admission_module.MATRIX) == set(CASE_ORDER) and
          set(synthetic) == set(SYNTHETIC_INPUT_PLAN) and
          set(legacy) == set(LEGACY_CONTROL) and
          set(controls) == {"N-source", "N-binding", "N-clause-redirect"} and
          set(bound_impls) == {"default16", "freeze32"},
          "complete produced first-matrix source/input inventory")
    source_cases = certificate["cases"]
    _need(set(source_cases) == set(SOURCE_CASE.values()),
          "eight exact certified source units")
    result = {}
    for case_id in CASE_ORDER:
        if case_id in SOURCE_CASE:
            item = source_cases[SOURCE_CASE[case_id]]
        elif case_id in SYNTHETIC_INPUT_PLAN:
            item = synthetic[case_id]
        elif case_id in LEGACY_CONTROL:
            item = legacy[case_id]
        elif case_id == "OFF":
            item = off
        else:
            item = controls[case_id]
        source_id, unit_id = item.get("source_id"), item.get("unit_id")
        _need(all(isinstance(value, str) and HEX64.fullmatch(value)
                  for value in (source_id, unit_id)),
              "case source/unit identities must be full produced SHA256 values")
        stage, predicate, location, outcome, classification = admission_module.MATRIX[case_id]
        result[case_id] = {"source_id": source_id, "unit_id": unit_id,
                           "stage": stage, "predicate": predicate,
                           "location": location, "outcome": outcome,
                           "classification": classification}
        if case_id in SYNTHETIC_INPUT_PLAN:
            digests = tuple(row["sha256"] for row in item["messages"])
            _need(len(digests) == len(SYNTHETIC_INPUT_PLAN[case_id]) and
                  all(HEX64.fullmatch(digest) for digest in digests),
                  "actual isolated synthetic message hashes required")
            result[case_id]["synthetic_input_sha256"] = digests
        if case_id in ("P0a", "P0b", "N-default-contract", "N-freeze-contract"):
            impl = "default16" if case_id in ("P0a", "N-default-contract") else "freeze32"
            result[case_id]["focused_item_id"] = bound_impls[impl]["compiler_item_id"]
    return result


def publish_positive_threshold_receipt(a, *, tool: Path, tool_receipt: Mapping[str, Any],
                                       certificate: Mapping[str, Any],
                                       source_package: Path,
                                       positive: Mapping[str, Mapping[str, Any]],
                                       expected_cases: Mapping[str, Any],
                                       helpers: Mapping[str, Any],
                                       profile_sha256: str) -> tuple[Any, str]:
    """Record two actually checked impls, then bind one exact-pair caller receipt.

    This is runner-reported workflow admission, not independent proof credit.
    It cannot run without the complete 26-case expected input manifest and
    two current focused execution attestations.
    """
    _need(set(positive) == {"P0a", "P0b"} and
          set(expected_cases) == set(CASE_ORDER),
          "both current impl runs and complete expected source IDs required")
    admission = helpers["a1-contract-admission.py"]
    receipts = helpers["a1-summary-receipt.py"]
    bound = positive["P0a"]["structure"]["bound_impls"]
    _need(bound == positive["P0b"]["structure"]["bound_impls"] and
          positive["P0a"]["structure"]["threshold_posts"]["native"] ==
          positive["P0b"]["structure"]["threshold_posts"]["native"],
          "both positive modes disagree on compiler IDs or native contracts")
    source_pairs = [positive[case]["raw"]["source_pair_sha256"]
                    for case in ("P0a", "P0b")]
    _need(source_pairs[0] == source_pairs[1] and
          all(case["execution_attestation"] is not None and
              case["proof_candidate"]["classification"] ==
              "FOCUSED_VF0_CANDIDATE" and
              case["execution_attestation"]["focus_body_verified"] is True and
              case["execution_attestation"]["focus_conformance_verified"] is True
              for case in positive.values()),
          "two actual positive focused bodies and conformance missing")
    hashes = {"verified": source_pairs[0]["verified"],
              "original": source_pairs[0]["original"],
              "verifier": tool_receipt["console_binary_sha256"],
              "exporter": tool_receipt["exporter_binary_sha256"],
              "schema": tool_receipt["final_schema_sha256"]}
    expected_inventory = {impl: {"compiler_impl_id": row["compiler_impl_id"],
                                 "compiler_item_id": row["compiler_item_id"]}
                          for impl, row in bound.items()}
    pins = {"tool_id": receipts.tool_id(hashes),
            "profile_id": profile_sha256,
            "proof_id": os.environ["PROOF_SHA"],
            "infra_id": os.environ["INFRA_SHA"],
            "target_id": receipts.TARGET}
    gate = admission.A1Admission(
        expected_inventory=expected_inventory,
        expected_run_pins=pins,
        expected_impl_inputs={
            impl: {"source_id": certificate["cases"][case]["source_id"],
                   "unit_id": certificate["cases"][case]["unit_id"]}
            for impl, case in (("default16", "P0a"), ("freeze32", "P0b"))},
        expected_cases=expected_cases)
    source_pair_id = receipts.source_pair_id(hashes)
    inventory_rows = [{"impl": impl, **row}
                      for impl, row in expected_inventory.items()]
    for impl, case_id in (("default16", "P0a"), ("freeze32", "P0b")):
        case = positive[case_id]
        observed = case["execution_attestation"]
        raw = case["raw"]
        _need(raw["build_id"] == os.environ["CLOUD_BUILD_ID"] and
              raw["source_pair_sha256"] == source_pairs[0] and
              observed["compiler_identity"] == {"impl": impl,
                  **expected_inventory[impl]},
              "current build/pair/impl attestation mismatch")
        assertion = {"stage": "impl-body", "predicate": "16<=result<=32",
                     "location": f"{impl} threshold item", "outcome": "pass",
                     "classification": "proved-by-runner"}
        conformance = {"stage": "native-envelope-conformance",
                       "predicate": "16<=result<=32",
                       "location": f"{impl} threshold item", "outcome": "pass",
                       "classification": "proved-by-runner",
                       "normal_posts_preserved": observed["normal_posts_preserved"],
                       "unwind_posts_preserved": observed["unwind_posts_preserved"]}
        record = {**pins, "build_id": raw["build_id"],
                  "record_kind": "runner_attestation", "proof_credit": False,
                  "impl": impl, "inventory": inventory_rows,
                  "source_id": certificate["cases"][case_id]["source_id"],
                  "unit_id": certificate["cases"][case_id]["unit_id"],
                  "source_pair_id": source_pair_id,
                  "proof_kind": "actual_body", "skipped": False,
                  "focus_mode": "actual-body-and-conformance",
                  "focus_only": True, "body_count": observed["body_count"],
                  "compiler_identity": observed["compiler_identity"],
                  "focused_item_id": observed["compiler_identity"]["compiler_item_id"],
                  "focus_body_verified": observed["focus_body_verified"],
                  "focus_conformance_verified": observed["focus_conformance_verified"],
                  "body": assertion, "native_envelope": conformance}
        gate.record_implementation(record)
    _need(gate.common_summary_available is True,
          "positive two-impl admission did not publish common summary")
    normal = Path(positive["P0a"]["raw"]["artifacts"]["normal-mir.txt"]["path"])
    readonly = Path(positive["P0a"]["raw"]["artifacts"]["readonly-mir.txt"]["path"])
    observer = helpers["a1-call-binding.py"].observe(
        "P0c", normal.read_text(encoding="utf-8"),
        readonly.read_text(encoding="utf-8"), dict(certificate),
        (source_package / certificate["cases"]["P0c"]["source_file"])
        .read_text(encoding="utf-8"))
    span = observer["binding"]["mir_body_span"]
    focus = f"verified/lib.rs:{span['lo']['line']}"
    receipt_path = (Path(a.evidence) / "a1-fixtures" / "P0c" /
                    "a1-threshold-summary.receipt")
    receipts.write_cloud_receipt(
        receipt_path, gate, build=os.environ["CLOUD_BUILD_ID"],
        proof=pins["proof_id"], infra=pins["infra_id"],
        profile=profile_sha256, hashes=hashes, caller_focus=focus)
    _need(receipt_path.is_file() and
          (Path(a.evidence) / "a1-fixtures" / "P0c" / "verified/lib.rs").is_file(),
          "positive caller receipt/source absent")
    return gate, str(receipt_path)


def draft_positive_receipt_stage(a, c4, driver, ghost, helper, manifest: dict,
                                 profile: dict, *, tool: Path,
                                 tool_receipt: Mapping[str, Any],
                                 profile_sha256: str,
                                 helpers: Mapping[str, Any]) -> dict:
    """Stage current positive inputs and an exact-pair P0c receipt, if proved.

    This is not called by `run` until every matrix backend and its pins are
    reviewed. The caller supplies the one already reconstructed final tool;
    this function never rebuilds or copies it. Every observation comes from
    the current Cloud Build and the same certified source bytes.
    """
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          os.environ.get("SORT4_A1_PHASE_ID") == PHASE and
          os.environ.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
          int(a.deadline_epoch) - int(time.time()) > 120,
          "current Cloud A1 positive stage and shared deadline required")
    _need(set(helpers) == set(A1_HELPERS) and
          tool_receipt.get("classification") == "A1_TOOL_BUILT_UNRUN_PROOF" and
          tool_receipt.get("proof_credit") is False,
          "one pinned final tool and complete helper map required")
    certificate_path, certificate = prepare_source_fixtures(
        a, helpers, ghost)
    package = certificate_path.parent
    legacy = prepare_legacy_fixtures(a, driver, helper, ghost, manifest)
    off = prepare_off_fixture(
        a, helpers["selected-proof.py"], driver, ghost, manifest, profile)
    first = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest,
        certificate_path=certificate_path, certificate=certificate,
        helpers=helpers, case_id="P0a")
    first_attestation = first.get("execution_attestation")
    _need(isinstance(first_attestation, Mapping) and
          first_attestation.get("focus_body_verified") is True and
          first["execution_attestation"]["focus_conformance_verified"] is True,
          "actual default threshold body/native conformance not established")
    native = first["structure"]["threshold_posts"]["native"]
    second = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest,
        certificate_path=certificate_path, certificate=certificate,
        helpers=helpers, case_id="P0b", native_baseline=native)
    second_attestation = second.get("execution_attestation")
    _need(isinstance(second_attestation, Mapping) and
          second_attestation.get("focus_body_verified") is True and
          second["execution_attestation"]["focus_conformance_verified"] is True,
          "actual Freeze threshold body/native conformance not established")
    baseline = first["raw"]["artifacts"]
    normal = Path(baseline["normal-mir.txt"]["path"])
    readonly = Path(baseline["readonly-mir.txt"]["path"])
    synthetic = prepare_synthetic_inputs(
        a, helpers["a1-synthetic-inputs.py"], baseline_decoded=normal,
        inventory=first["structure"]["inventory"], certificate=certificate)
    controls = prepare_admission_control_inputs(
        a, helpers["a1-call-binding.py"], helpers["a1-compiler-inventory.py"],
        certificate=certificate, certificate_path=certificate_path,
        normal_decoded=normal, readonly_decoded=readonly)
    expected = materialize_expected_cases(
        helpers["a1-contract-admission.py"], certificate, synthetic,
        legacy, off, controls, first["structure"]["bound_impls"])
    gate, receipt_path = publish_positive_threshold_receipt(
        a, tool=tool, tool_receipt=tool_receipt,
        certificate=certificate, source_package=package,
        positive={"P0a": first, "P0b": second},
        expected_cases=expected, helpers=helpers,
        profile_sha256=profile_sha256)
    caller = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest,
        certificate_path=certificate_path, certificate=certificate,
        helpers=helpers, case_id="P0c", native_baseline=native)
    caller_attestation = caller.get("execution_attestation")
    _need(isinstance(caller_attestation, Mapping) and
          caller_attestation.get("caller_body_verified") is True and
          gate.common_summary_available is True,
          "published common threshold caller was not verified on the exact pair")
    return {"classification": "DRAFT_POSITIVE_STAGE_SOURCE_REPORTED_ONLY",
            "certificate_path": str(certificate_path),
            "receipt_path": receipt_path,
            "expected_case_ids": expected,
            "positive_cases": {"P0a": first, "P0b": second, "P0c": caller},
            "synthetic_inputs": synthetic,
            "admission_controls": controls,
            "legacy_inputs": legacy, "off_input": off,
            "proof_credit": False, "first_matrix_complete": False}


def observe_focused_structure(case_id: str, raw: Mapping[str, Any],
                              fixture: Path, certificate: Mapping[str, Any],
                              helpers: Mapping[str, Any], *,
                              native_baseline: Mapping[str, Any] | None = None) -> dict:
    """Bind one raw focused case to compiler IDs, full native AST and MIR calls.

    The output remains structure-only. It never asserts body execution,
    conformance, verification success, or independent proof credit.
    """
    _need(case_id in SOURCE_CASE and raw.get("case_id") == case_id and
          raw.get("paired_support", {}).get("paired_support_passed") is True,
          "paired current source support is required")
    paths = {}
    for name in ("normal-mir.txt", "readonly-mir.txt", "proof-ast.ml"):
        artifact = raw.get("artifacts", {}).get(name)
        _need(isinstance(artifact, dict) and isinstance(artifact.get("path"), str),
              "missing same-case artifact: " + name)
        path = Path(artifact["path"]).resolve()
        _need(path.is_file() and path.is_relative_to(Path(fixture).resolve().parent.parent)
              and artifact.get("sha256") == _sha(path),
              "stale or foreign same-case artifact: " + name)
        paths[name] = path
    source_path = fixture / "verified/lib.rs"
    original_path = fixture / "original/lib.rs"
    source = source_path.read_text(encoding="utf-8")
    _need(hashlib.sha256(source.encode()).hexdigest() ==
          certificate["cases"][case_id]["generated_source_sha256"] and
          raw.get("source_pair_sha256", {}).get("verified") == _sha(source_path) and
          raw.get("source_pair_sha256", {}).get("original") == _sha(original_path),
          "raw observation source differs from certified unit")
    normal = paths["normal-mir.txt"].read_text(encoding="utf-8")
    readonly = paths["readonly-mir.txt"].read_text(encoding="utf-8")
    inventory = helpers["a1-compiler-inventory.py"].observe(
        case_id, normal, readonly, dict(certificate), source)
    shape = inventory["inventory"]
    bound = {}
    for impl in shape["impls"]:
        threshold = [row for row in impl["items"]
                     if row["name"] == "small_sort_threshold"]
        _need(len(threshold) == 1, "one threshold item per compiler impl")
        item = threshold[0]
        bound[impl["impl"]] = {
            "compiler_impl_id": str(impl["impl_def_index"]),
            "compiler_item_id": str(item["def_index"]),
            # Ast.Func location and -focus use Body.span, while the native
            # contract diagnostics originate at fnSigSpan.
            "source_line": item["body"]["mir_span"][0][1],
            "diagnostic_post_line": item["body"]["fn_sig_span"][0][1],
            "mir_span": item["body"]["mir_span"],
            "imp_span": item["body"]["imp_span"],
        }
    common = [span[0][1] for name, span in shape["required_method_spans"]
              if name == "small_sort_threshold"]
    _need(len(common) == 1, "one compiler required threshold source span")
    gates = helpers["a1-ast-gates.py"]
    posts = gates.threshold_posts(paths["proof-ast.ml"].read_text(encoding="utf-8"),
                                  bound, stage=raw["focus_stage"],
                                  baseline=native_baseline, common_line=common[0])
    calls = None
    if case_id in ("P0c", "N-false31", "P1"):
        calls = helpers["a1-call-binding.py"].observe(
            case_id, normal, readonly, dict(certificate), source)
        binding = calls["binding"]
        owner = binding["caller"]
        lines = dict(binding["source_call_lines"])
        owner_marker = ("fn a1_guard_observer<" if owner == "a1_guard_observer"
                        else "pub fn quicksort<")
        owner_lines = [i for i, line in enumerate(source.splitlines(), 1)
                       if owner_marker in line]
        _need(len(owner_lines) == 1, "one source-certified caller declaration")
        caller_span = binding["mir_body_span"]
        caller_ast_line = caller_span["lo"]["line"]
        _need(caller_span["lo"]["source_path"] == "verified/lib.rs" and
              caller_span["hi"]["source_path"] == "verified/lib.rs" and
              caller_ast_line >= owner_lines[0],
              "caller AST location does not bind to compiler MIR body")
        expected = ((gates.COMMON,) if owner == "a1_guard_observer" else
                    (gates.COMMON, gates.SMALL_SORT))
        operands = {call["callee"]: tuple(call["expected_ast_arguments"])
                    for call in binding["calls"]}
        calls = {"mir": calls,
                 "ast": gates.caller_calls(
                     paths["proof-ast.ml"].read_text(encoding="utf-8"),
                     owner=owner, expected=expected, source_line=caller_ast_line,
                     call_lines=lines, expected_arguments=operands)}
    return {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
            "case_id": case_id, "inventory": inventory,
            "bound_impls": bound, "threshold_posts": posts,
            "caller_calls": calls, "proof_credit": False,
            "body_count_observed": None,
            "native_conformance_verified": None}


def collect_source_case(a, c4, ghost, *, tool: Path, tool_receipt: dict,
                        profile: dict, manifest: dict, certificate_path: Path,
                        certificate: Mapping[str, Any], helpers: Mapping[str, Any],
                        case_id: str,
                        native_baseline: Mapping[str, Any] | None = None) -> dict:
    """Run one isolated paired source case and record only raw/structural facts."""
    _need(case_id in SOURCE_CASE and
          int(a.deadline_epoch) - int(time.time()) > 120,
          "source case unsupported or shared deadline exhausted")
    fixture = Path(a.evidence) / "a1-fixtures" / case_id
    raw = helpers["a1-focus-backend.py"].collect_focus(
        a, c4, ghost, tool, tool_receipt, profile, manifest,
        certificate_path, fixture, case_id,
        inventory_module=helpers["a1-compiler-inventory.py"],
        call_binding_module=helpers["a1-call-binding.py"])
    if raw.get("paired_support", {}).get("paired_support_passed") is not True or \
            raw.get("artifacts", {}).get("proof-ast.ml", {}).get("sha256") is None:
        return {"classification": "INCONCLUSIVE_CURRENT_STAGE",
                "case_id": case_id, "raw": raw, "structure": None,
                "proof_credit": False}
    structure = observe_focused_structure(case_id, raw, fixture, certificate,
                                           helpers, native_baseline=native_baseline)
    ast_path = Path(raw["artifacts"]["proof-ast.ml"]["path"])
    interval = None
    if case_id in {"P0a", "P0b", "P0c", "N-default-contract",
                   "N-freeze-contract", "N-false31"}:
        if case_id in ("P0a", "N-default-contract"):
            selected_impl = "default16"
        elif case_id in ("P0b", "N-freeze-contract"):
            selected_impl = "freeze32"
        else:
            selected_impl = None
        if selected_impl:
            item = structure["bound_impls"][selected_impl]
            span = item["mir_span"]
            expected_name = structure["threshold_posts"]["impls"][selected_impl]["alias"]
            compiler_span = (span[0][1], span[1][1])
            _need(raw.get("compiler_item_identity_observed", {}).get("compiler_item_id") ==
                  item["compiler_item_id"],
                  "focused body compiler item identity changed")
        else:
            caller_binding = structure["caller_calls"]["mir"]["binding"]
            span = caller_binding["mir_body_span"]
            expected_name = caller_binding["caller"]
            compiler_span = (span["lo"]["line"], span["hi"]["line"])
        interval = select_focused_body(
            ast_path.read_text(encoding="utf-8"),
            helpers["a1-ast-gates.py"],
            focus_line=raw["focus_source_line"], expected_name=expected_name,
            compiler_span=compiler_span)
    candidate = None
    execution = None
    if case_id in {"P0a", "P0b", "P0c", "N-default-contract",
                   "N-freeze-contract", "N-false31"}:
        stage = raw.get("stages", {}).get("verification", {})
        log = Path(a.evidence) / "focus" / case_id / "verification.log"
        _need(log.is_file() and stage.get("log_sha256") == _sha(log),
              "same-invocation verifier diagnostic log missing or changed")
        caller = structure["caller_calls"]
        bundle = {"threshold": structure["threshold_posts"],
                  "caller": caller["ast"] if caller else None,
                  "mir_binding": caller["mir"] if caller else None}
        source = (fixture / "verified/lib.rs").read_text(encoding="utf-8")
        verifier_log = log.read_text(encoding="utf-8")
        candidate = helpers["a1-proof-classifier.py"].classify_focus(
            case_id, raw, bundle, source, verifier_log)
        _need(candidate.get("proof_credit") is False and
              candidate.get("body_count") is None and
              candidate.get("native_conformance_verified") is None,
              "candidate classifier improperly minted execution/conformance facts")
        if candidate.get("candidate_passed") is True:
            execution = attest_focused_execution(
                case_id, tool=tool, profile=profile, raw=raw,
                structure=structure, interval=interval, candidate=candidate,
                verifier_log=verifier_log)
    return {"classification": "RAW_AND_STRUCTURE_ONLY_UNCLASSIFIED",
            "case_id": case_id, "raw": raw, "structure": structure,
            "focus_interval": interval, "proof_candidate": candidate,
            "execution_attestation": execution,
            "proof_credit": False}


def _ast_source_span(location: Any) -> tuple[int, int] | None:
    """Parse pinned Ast.string_of_loc line bounds for verified/lib.rs only."""
    if not isinstance(location, tuple) or len(location) != 2 or location[0] != "loc":
        raise RuntimeError("A1-RUNNER: malformed location-bearing AST node")
    value = location[1]
    match = re.fullmatch(
        r"(?:.*/)?verified/lib\.rs\(([1-9][0-9]*),[0-9]+"
        r"(?:-(?:([1-9][0-9]*),)?[0-9]+)?\)", value)
    if match is None:
        return None
    lo = int(match.group(1))
    hi = int(match.group(2)) if match.group(2) else lo
    _need(hi >= lo, "AST source span order")
    return lo, hi


def select_focused_body(ast_text: str, ast_gates, *, focus_line: int,
                        expected_name: str,
                        compiler_span: tuple[int, int]) -> dict:
    """Count exact source intervals selected by frozen inclusive -focus.

    The AST emitter precedes verification and contains the complete package.
    This gate selects one definition interval; it does not grant proof credit.
    """
    _need(focus_line > 0 and compiler_span[0] == focus_line and
          compiler_span[1] >= focus_line,
          "compiler Body.span does not contain its requested focus")
    selected = []
    for row in ast_gates.functions(ast_text):
        if row["kind"] != "definition":
            continue
        func_span = _ast_source_span(row["fields"][0])
        if func_span is None:
            continue
        body, = ast_gates.node(row["fields"][10], "Some", 1)
        _, close = ast_gates.node(body, "tuple", 2)
        close_span = _ast_source_span(close)
        _need(close_span is not None and close_span[0] == func_span[1],
              "AST close brace differs from Func source span end")
        if func_span[0] <= focus_line <= close_span[1]:
            selected.append({"name": row["name"], "func_span": func_span,
                             "close_span": close_span})
    _need(len(selected) == 1 and selected[0]["name"] == expected_name and
          selected[0]["func_span"] == compiler_span and
          selected[0]["close_span"][1] == compiler_span[1],
          "focus does not select exactly one compiler-bound AST definition")
    return {"classification": "ONE_SOURCE_INTERVAL_SELECTED_STRUCTURE_ONLY",
            "focus_line": focus_line, "body_count_from_intervals": 1,
            "selected": selected[0], "proof_credit": False}


def body_entry_context(verifier_log: str, first_error: str, *,
                       alias: str, body_line: int) -> bool:
    """Recognize the pinned text error's exact body-entry context frame.

    The final console prints the first SymbolicExecutionError, then its
    `Executing` context frames. The final kernel enters `Verifying function`
    only after prototype compatibility returns. A header-only failure cannot
    carry this body frame. Ambiguity, another error, or absent context fails
    closed; the AST selection alone remains structural.
    """
    _need(isinstance(verifier_log, str) and isinstance(first_error, str) and
          bool(first_error) and isinstance(alias, str) and bool(alias) and
          isinstance(body_line, int) and body_line > 0,
          "exact error/body identity required for context gate")
    lines = verifier_log.splitlines()
    errors = [i for i, line in enumerate(lines)
              if ": error:" in line or line.startswith(("Fatal error:",
                                                          "error:", "error["))]
    if len(errors) != 1 or lines[errors[0]] != first_error:
        return False
    note = re.compile(
        r"(?:.*/)?verified/lib\.rs\(" + str(body_line) +
        r",[0-9]+(?:-(?:[1-9][0-9]*,)?[0-9]+)?\): note: " +
        re.escape("Verifying function '" + alias + "'") + r"\Z")
    frames = [line for line in lines[errors[0] + 1:] if note.fullmatch(line)]
    return len(frames) == 1


def attest_focused_execution(case_id: str, *, tool: Path,
                             profile: Mapping[str, Any],
                             raw: Mapping[str, Any],
                             structure: Mapping[str, Any],
                             interval: Mapping[str, Any],
                             candidate: Mapping[str, Any],
                             verifier_log: str) -> dict | None:
    """Runner-reported inference from exact frozen focus/header order and VF0.

    The final source pins bind inclusive focus, prototype compatibility before
    body execution, and the AST emitter's pre-verification full-unit dump.
    This is a candidate attestation, never independent proof credit.
    """
    pins = profile.get("a1_focus_semantics_sha256")
    _need(isinstance(pins, dict) and pins == FOCUS_SEMANTICS_PINS,
          "reviewed exact final focus/header source pins required")
    _need(all((tool / name).is_file() and _sha(tool / name) == digest
              for name, digest in FOCUS_SEMANTICS_PINS.items()),
          "final focused verifier source differs from reviewed semantics")
    _need(candidate.get("candidate_passed") is True and
          candidate.get("proof_credit") is False and
          interval.get("body_count_from_intervals") == 1 and
          interval.get("focus_line") == raw.get("focus_source_line") and
          raw.get("focus") == f"verified/lib.rs:{interval['focus_line']}",
          "one actually reached focused body candidate required")
    if case_id in ("P0a", "P0b", "N-default-contract", "N-freeze-contract"):
        impl = "default16" if case_id in ("P0a", "N-default-contract") else "freeze32"
        body = structure["bound_impls"][impl]
        ast = structure["threshold_posts"]["impls"][impl]
        _need(ast["alias"] == interval["selected"]["name"] and
              ast["compiler_impl_id"] == body["compiler_impl_id"] and
              ast["compiler_item_id"] == body["compiler_item_id"] and
              raw["compiler_item_identity_observed"]["compiler_item_id"] ==
              body["compiler_item_id"],
              "body/prototype/compiler numeric item binding")
        _need(candidate.get("classification") in
              ("FOCUSED_VF0_CANDIDATE", "INTENDED_FOCUSED_FAILURE_CANDIDATE"),
              "body checker did not reach a classified terminal stage")
        # A failing generated post at fnSigSpan can occur during header
        # compatibility before the body continuation. Require the exact
        # current error's kernel body-entry context, not an AST interval or
        # matching diagnostic alone. The console emits that context after the
        # first SymbolicExecutionError; absent or ambiguous context refuses.
        if case_id in ("N-default-contract", "N-freeze-contract"):
            context = candidate.get("error_context")
            if not isinstance(context, Mapping) or \
                    context.get("stage") != "impl-body" or \
                    context.get("body_frame_observed") is not True or \
                    context.get("header_frame_observed") is not False:
                return None
            if not body_entry_context(
                    verifier_log, candidate.get("first_error"),
                    alias=ast["alias"], body_line=body["source_line"]):
                return None
        return {"classification": "RUNNER_REPORTED_FOCUSED_BODY_AND_CONFORMANCE",
                "case_id": case_id, "body_count": 1,
                "focus_body_reached": True,
                "focus_body_verified": candidate.get("body_verified") is True,
                "focus_conformance_verified": True,
                "compiler_identity": {"impl": impl,
                    "compiler_impl_id": body["compiler_impl_id"],
                    "compiler_item_id": body["compiler_item_id"]},
                "normal_posts_preserved": True,
                "unwind_posts_preserved": True,
                "proof_credit": False,
                "assurance": "runner-inference-from-pinned-kernel-order-and-current-VF-stage"}
    _need(case_id in ("P0c", "N-false31") and
          interval["selected"]["name"] == "a1_guard_observer" and
          candidate.get("classification") in
          ("FOCUSED_VF0_CANDIDATE", "INTENDED_FOCUSED_FAILURE_CANDIDATE"),
          "one certified observer body required")
    return {"classification": "RUNNER_REPORTED_FOCUSED_OBSERVER",
            "case_id": case_id, "body_count": 1,
            "caller_body_reached": True,
            "caller_body_verified": candidate.get("body_verified") is True,
            "proof_credit": False,
            "assurance": "runner-inference-from-pinned-focus-and-current-VF-stage"}


def _admission_matrix(path: Path) -> dict[str, tuple[str, ...]]:
    """Read the service case inventory without importing or executing it."""
    _need(path.is_file(), "A1 admission module missing")
    source = ast.parse(path.read_text(), filename=str(path))
    rows = [node.value for node in source.body
            if isinstance(node, ast.AnnAssign) and
            isinstance(node.target, ast.Name) and node.target.id == "MATRIX"]
    _need(len(rows) == 1, "A1 admission MATRIX declaration changed")
    matrix = ast.literal_eval(rows[0])
    _need(isinstance(matrix, dict), "A1 admission MATRIX is not a literal map")
    return matrix


def preflight_plan(profile: Mapping[str, Any], matrix: Mapping[str, Any] | None = None) -> dict:
    """Pure, reviewable plan; it never grants dispatch or proof credit."""
    _need(len(CASE_ORDER) == 26 and len(set(CASE_ORDER)) == 26,
          "first-matrix order must contain 26 distinct rows")
    if matrix is not None:
        _need(set(matrix) == set(CASE_ORDER), "admission MATRIX differs from runner plan")
    _need(profile.get("phase_id") == PHASE and
          profile.get("profile_accepted") is False and
          profile.get("first_matrix_status") == "NOT_RUN",
          "unaccepted exact A1 profile required")
    cases = []
    for case_id in CASE_ORDER:
        source = ("a1-fixtures:" + SOURCE_CASE[case_id] if case_id in SOURCE_CASE else
                  "a1-synthetic-inputs:" + SYNTHETIC_MUTATION[case_id]
                  if case_id in SYNTHETIC_MUTATION else
                  "driver:" + LEGACY_CONTROL[case_id]
                  if case_id in LEGACY_CONTROL else
                  "current compiler/translator observation adapter")
        mode = ("actual-body-and-conformance" if case_id in
                ("P0a", "P0b", "N-default-contract", "N-freeze-contract") else
                "caller-body" if case_id in ("P0c", "N-false31") else
                "interface-only" if case_id in
                {"P-dispatch", "P1", *SYNTHETIC_MUTATION,
                 "N-source", "N-binding", "N-clause-redirect"} else "none")
        cases.append({"case_id": case_id, "source_adapter": source,
                      "focus_mode": mode, "executed": False,
                      "proof_credit": False})
    return {
        "classification": "BLOCKED_UNIMPLEMENTED_STAGE",
        "phase_id": PHASE,
        "case_count": len(cases), "cases": cases,
        "planned_order": list(CASE_ORDER),
        "producer_apis": {
            "tool": "a1-tool.reconstruct(a,c4,audit,driver,manifest,profile)",
            "source": "a1-fixtures.construct/_write_package",
            "synthetic": "a1-synthetic-inputs.mutate_required_fn",
            "legacy_stage": "selected-runtime.source_support/verify_case",
            "legacy_classifier": "driver.verify_one/classify",
            "admission": "a1-contract-admission.A1Admission",
            "receipt": "a1-summary-receipt.write_cloud_receipt",
        },
        "missing_backend_hooks": MISSING_BACKEND_HOOKS.copy(),
        "first_missing_stage": "full_small_sort_p1_interface",
        "tool_reconstructed": False, "fixtures_generated": False,
        "verification_invoked": False, "matrix_complete": False,
        "dispatch_ready": False, "proof_credit": False,
    }


def run(a) -> dict:
    """Cloud-only admission checkpoint; no tool or proof stage is reachable."""
    env = os.environ
    _need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          env.get("SORT4_A1_PHASE_ID") == PHASE and
          env.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
          bool(env.get("CLOUD_BUILD_ID")) and bool(env.get("CLOUD_BUILD_PROJECT_ID")) and
          not env.get("GITHUB_ACTIONS"), "exact Cloud provider, phase, and opt-in")
    for name in ("proof_root", "production_source", "work_root", "evidence", "cloud_dir"):
        path = Path(getattr(a, name)).resolve()
        _need(str(path).startswith("/workspace/"), name + " must be in /workspace")
    _need(int(a.deadline_epoch) - int(time.time()) > 30, "shared Build deadline exhausted")
    profile_path = Path(a.proof_root) / PROFILE
    profile_sha = env.get("SORT4_A1_PROFILE_SHA256")
    _need(profile_path.is_file() and profile_sha is not None and
          HEX64.fullmatch(profile_sha) is not None and
          _sha(profile_path) == profile_sha, "exact published A1 profile bytes")
    proof_sha = env.get("PROOF_SHA")
    infra_sha = env.get("INFRA_SHA")
    _need(proof_sha is not None and HEX40.fullmatch(proof_sha) is not None and
          infra_sha is not None and HEX40.fullmatch(infra_sha) is not None and
          profile_path.is_file(), "full proof/infra pins")
    actual = subprocess.check_output(
        ["git", "-C", str(a.proof_root), "rev-parse", "HEAD"], text=True).strip()
    _need(actual == proof_sha, "proof checkout SHA differs")
    profile = json.loads(profile_path.read_text())
    _need(profile.get("proof_sha") == proof_sha and
          profile.get("infra_sha") == infra_sha and
          profile.get("cloud_build_enabled") is True,
          "published A1 profile has no matching authorized run pins")
    result = preflight_plan(profile, _admission_matrix(
        Path(a.proof_root) / HERE / "a1-contract-admission.py"))
    result.update(build_id=env["CLOUD_BUILD_ID"], proof_sha=proof_sha,
                  infra_sha=infra_sha, profile_sha256=profile_sha)
    # The checkpoint is written only in an isolated Cloud evidence directory.
    # It is not a result row and must never be fed to A1Admission.
    path = Path(a.evidence) / "a1-first-matrix-preflight.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as output:
        output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
