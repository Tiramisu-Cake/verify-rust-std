"""Fail-closed Cloud entry and staged A1 first-matrix orchestration.

Source preparation, one tool reconstruction, focused raw collection and the
structural observation bridge are explicit callables. Admission and summary
publication remain unreachable until the same-Build proof classifier and all
26 rows have reviewed observation hooks. Importing this module is inert.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import fields, is_dataclass
from functools import lru_cache
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
AUTHORIZATION_PHASE = "SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6"
HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
PROFILE = HERE / "A1-SCOPE-S3-PROFILE-2026-10-20.json"
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
NATIVE_TARGET_CASES = frozenset({"P0a", "P0b", "P0c", "P1", "N-binding",
                                "N-region-swap", "N-alpha-valid"})
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
    "N-no-F": "no_F",
    "N-clauses": "remove_fnmut and remove_output in separate isolated inputs",
    "N-duplicate": "duplicate_impl_method",
}
SYNTHETIC_INPUT_PLAN = {
    "N-binder-collapse": ("binder_collapse",),
    "N-alpha-valid": ("alpha_valid",),
    "N-free-region": ("free_region_input",),
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

A1_HELPERS = (
    "a1-fixtures.py", "a1-tool.py", "a1-focus-backend.py",
    "a1-compiler-inventory.py", "a1-call-binding.py", "a1-ast-gates.py",
    "a1-synthetic-inputs.py", "a1-synthetic-backend.py",
    "a1-contract-admission.py", "a1-summary-receipt.py",
    "a1-proof-classifier.py", "a1-matrix-classifier.py", "selected-proof.py",
)
FOCUS_SEMANTICS_PINS = {
    "src/verifast.ml": "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c",
    "src/verifast1.ml": "bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207",
    "src/verify_expr.ml": "2d17c36005d6727cb5ff6d831bf905f513065bb591d5d9768ee70778872a6d20",
    "src/vfconsole/vfconsole.ml": "79179baa9ad9e9cb2ee5163f4c9528f665519d894c43093183fd8e9f31b06898",
}


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("A1-RUNNER: " + why)


def _available_artifact_path(artifacts: Any, name: str) -> Path | None:
    """Read a recorded path only when the partial artifact entry supplies it."""
    if not isinstance(artifacts, Mapping):
        return None
    entry = artifacts.get(name)
    if not isinstance(entry, Mapping):
        return None
    value = entry.get("path")
    return Path(value) if isinstance(value, str) and value else None


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
          _sha(pin_path) == manifest.get("selected_binding_pins_sha256"),
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
    correct = call_binding_module.construct_common_binding_claim(
        binding, compiler_inventory)
    _need(correct.get("call_line") == common[0]["call_line"] and
          correct.get("compiler_trait_item_id") == required["small_sort"],
          "constructed common binding claim differs from paired compiler observations")
    call_binding_module.validate_common_binding_claim(binding, compiler_inventory,
                                                       correct)
    wrong_certificate = deepcopy(dict(certificate))
    wrong_certificate["cases"]["P1"]["generated_source_sha256"] = "0" * 64
    _need(wrong_certificate["cases"]["P1"]["generated_source_sha256"] !=
          source_case["generated_source_sha256"],
          "source certificate mutation must change bytes")
    wrong_binding = {**correct, "callee": "StableSmallSortTypeImpl::not_small_sort"}
    forced_redirect = {"SORT4_A1_FORCE_LEGACY_REDIRECT": "1",
                       "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                       "source_pair_sha256": source_case["generated_source_sha256"]}
    region_claim = call_binding_module.mutate_region_binding_claim(
        call_binding_module.construct_common_binding_claim(binding, compiler_inventory))
    values = {"N-source": wrong_certificate,
              "N-binding": wrong_binding,
              "N-region-swap": region_claim,
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
          set(controls) == {"N-source", "N-binding", "N-region-swap",
                            "N-clause-redirect"} and
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
        if case_id in controls:
            result[case_id]["control_input_sha256"] = item["input_sha256"]
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
                                       profile_sha256: str,
                                       pair_source_case: str = "P0a",
                                       receipt_case: str = "P0c") -> tuple[Any, str]:
    """Record two actually checked impls, then bind one exact-pair caller receipt.

    This is runner-reported workflow admission, not independent proof credit.
    It cannot run without the complete 26-case expected input manifest and
    two current focused execution attestations.
    """
    _need(isinstance(certificate, Mapping) and
          isinstance(certificate.get("cases"), Mapping),
          "certified source case metadata required")
    certified_cases = certificate["cases"]
    if pair_source_case == "P0a":
        _need(receipt_case == "P0c", "positive receipt requires its P0c caller")
        impl_source_cases = {"default16": "P0a", "freeze32": "P0b"}
    elif pair_source_case == "N-false31":
        _need(receipt_case == "N-false31",
              "own-false31 receipt requires its own caller")
        impl_source_cases = {"default16": "N-false31", "freeze32": "N-false31"}
    else:
        _need(False, "unsupported positive-receipt certified input pairing")
        raise AssertionError("unreachable")
    _need(set(positive) == {"P0a", "P0b"} and
          set(impl_source_cases.values()).issubset(certified_cases) and
          receipt_case in certified_cases and
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
    impl_inputs = {}
    for impl, case_id in impl_source_cases.items():
        certified = certified_cases.get(case_id)
        raw = positive["P0a" if impl == "default16" else "P0b"].get("raw")
        _need(isinstance(certified, Mapping) and
              isinstance(certified.get("source_id"), str) and
              bool(certified["source_id"]) and
              isinstance(certified.get("unit_id"), str) and
              bool(certified["unit_id"]) and
              isinstance(raw, Mapping) and
              raw.get("source_id") == certified["source_id"] and
              raw.get("unit_id") == certified["unit_id"],
              f"{impl} raw source/unit identity does not match certified {case_id}")
        impl_inputs[impl] = {"source_id": certified["source_id"],
                             "unit_id": certified["unit_id"]}
    gate = admission.A1Admission(
        expected_inventory=expected_inventory,
        expected_run_pins=pins,
        expected_impl_inputs=impl_inputs,
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
                  "source_id": impl_inputs[impl]["source_id"],
                  "unit_id": impl_inputs[impl]["unit_id"],
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
        receipt_case, normal.read_text(encoding="utf-8"),
        readonly.read_text(encoding="utf-8"), dict(certificate),
        (source_package / certificate["cases"][receipt_case]["source_file"])
        .read_text(encoding="utf-8"))
    span = observer["binding"]["mir_body_span"]
    focus = f"verified/lib.rs:{span['lo']['line']}"
    receipt_path = (Path(a.evidence) / "a1-fixtures" / receipt_case /
                    "a1-threshold-summary.receipt")
    receipts.write_cloud_receipt(
        receipt_path, gate, build=os.environ["CLOUD_BUILD_ID"],
        proof=pins["proof_id"], infra=pins["infra_id"],
        profile=profile_sha256, hashes=hashes, caller_focus=focus)
    _need(receipt_path.is_file() and
          (Path(a.evidence) / "a1-fixtures" / receipt_case / "verified/lib.rs").is_file(),
          "positive caller receipt/source absent")
    return gate, str(receipt_path)


def draft_positive_receipt_stage(a, c4, driver, ghost, helper, manifest: dict,
                                 profile: dict, *, tool: Path,
                                 tool_receipt: Mapping[str, Any],
                                 profile_sha256: str,
                                 helpers: Mapping[str, Any],
                                 support_cache: dict[str, dict] | None = None,
                                 progress: dict[str, Any] | None = None,
                                 progress_hook=None) -> dict:
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
    support_cache = support_cache if support_cache is not None else {}
    certificate_path, certificate = prepare_source_fixtures(
        a, helpers, ghost)
    package = certificate_path.parent
    progress = progress if progress is not None else {}
    progress.update(certificate_path=str(certificate_path), certificate=certificate)
    if progress_hook is not None:
        progress_hook("source-constructor")
    legacy = progress.get("legacy_inputs", {})
    off = progress.get("off_input")
    progress.setdefault("positive_cases", {})
    first = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest,
        certificate_path=certificate_path, certificate=certificate,
        helpers=helpers, case_id="P0a", support_cache=support_cache)
    progress["positive_cases"]["P0a"] = first
    if progress_hook is not None:
        progress_hook("P0a-observed")
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
        helpers=helpers, case_id="P0b", native_baseline=native,
        support_cache=support_cache)
    progress["positive_cases"]["P0b"] = second
    if progress_hook is not None:
        progress_hook("P0b-observed")
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
    progress.update(synthetic_inputs=synthetic, admission_controls=controls,
                    expected_case_ids=expected)
    gate, receipt_path = publish_positive_threshold_receipt(
        a, tool=tool, tool_receipt=tool_receipt,
        certificate=certificate, source_package=package,
        positive={"P0a": first, "P0b": second},
        expected_cases=expected, helpers=helpers,
        profile_sha256=profile_sha256)
    progress.update(admission_gate=gate, positive_receipt_path=receipt_path,
                    expected_case_ids=expected)
    if progress_hook is not None:
        progress_hook("positive-receipt-issued")
    caller = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest,
        certificate_path=certificate_path, certificate=certificate,
        helpers=helpers, case_id="P0c", native_baseline=native,
        support_cache=support_cache)
    progress["positive_cases"]["P0c"] = caller
    if progress_hook is not None:
        progress_hook("P0c-observed")
    caller_attestation = caller.get("execution_attestation")
    _need(isinstance(caller_attestation, Mapping) and
          caller_attestation.get("caller_body_verified") is True and
          gate.common_summary_available is True,
          "published common threshold caller was not verified on the exact pair")
    result = {"classification": "DRAFT_POSITIVE_STAGE_SOURCE_REPORTED_ONLY",
            "certificate_path": str(certificate_path),
            "receipt_path": receipt_path,
            "expected_case_ids": expected,
            "positive_cases": {"P0a": first, "P0b": second, "P0c": caller},
            "synthetic_inputs": synthetic,
            "admission_controls": controls,
            "support_cache": support_cache,
            "legacy_inputs": legacy, "off_input": off,
            "admission_gate": gate,
            "proof_credit": False, "first_matrix_complete": False}
    progress.update(result)
    if progress_hook is not None:
        progress_hook("positive-lifecycle-complete")
    return result


def draft_false31_pair_stage(a, c4, ghost, *, tool: Path,
                             tool_receipt: Mapping[str, Any], profile: dict,
                             manifest: dict, certificate_path: Path,
                             certificate: Mapping[str, Any],
                             source_package: Path,
                             positive_native_baseline: Mapping[str, Any],
                             expected_cases: Mapping[str, Any] | None,
                             helpers: Mapping[str, Any],
                             profile_sha256: str,
                             support_cache: dict[str, dict] | None = None,
                             progress: dict[str, Any] | None = None,
                             progress_hook=None) -> dict:
    """Re-prove both threshold bodies on false31's own bytes before its receipt.

    The two body invocations focus the certified N-false31 source pair and are
    isolated from the positive pair's body attestations. Only after both
    current VF0/conformance observations and matching native posts does this
    write a receipt into the N-false31 fixture for the caller invocation.
    """
    support_cache = support_cache if support_cache is not None else {}
    false_case = certificate["cases"]["N-false31"]
    pair = {}
    pair["P0a"] = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest, certificate_path=certificate_path,
        certificate=certificate, helpers=helpers, case_id="N-false31",
        native_baseline=positive_native_baseline, focus_case_id="P0a",
        support_cache=support_cache)
    first = pair["P0a"]
    if progress is not None:
        progress.setdefault("body_cases", {})["P0a"] = first
        if progress_hook is not None:
            progress_hook("N-false31-P0a-observed")
    first_attestation = first.get("execution_attestation")
    _need(isinstance(first_attestation, Mapping) and
          first_attestation.get("focus_body_verified") is True and
          first_attestation.get("focus_conformance_verified") is True and
          first["structure"]["threshold_posts"]["native"] ==
          positive_native_baseline,
          "false31 source pair default threshold body/conformance was not proved")
    native = first["structure"]["threshold_posts"]["native"]
    pair["P0b"] = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest, certificate_path=certificate_path,
        certificate=certificate, helpers=helpers, case_id="N-false31",
        native_baseline=native, focus_case_id="P0b",
        support_cache=support_cache)
    second = pair["P0b"]
    if progress is not None:
        progress.setdefault("body_cases", {})["P0b"] = second
        if progress_hook is not None:
            progress_hook("N-false31-P0b-observed")
    second_attestation = second.get("execution_attestation")
    _need(isinstance(second_attestation, Mapping) and
          second_attestation.get("focus_body_verified") is True and
          second_attestation.get("focus_conformance_verified") is True and
          second["structure"]["threshold_posts"]["native"] == native and
          second["structure"]["threshold_posts"]["native"] ==
          positive_native_baseline,
          "false31 source pair Freeze threshold body/conformance was not proved")

    if not isinstance(expected_cases, Mapping):
        return {"not_run": True, "execution_started": False,
                "reason": "false31 own bodies observed; complete receipt input manifest unavailable",
                "partial_body_cases": pair, "proof_credit": False}

    false_expected = deepcopy(dict(expected_cases))
    # A1Admission constructor requires one paired source/unit identity across
    # the positive alias family. This receipt-only copy rebinds all aliases;
    # the caller separately receives and validates the actual false31 pair.
    for case_id in ("P0a", "P0b", "P0c", "P-dispatch", "P1"):
        false_expected[case_id]["source_id"] = false_case["source_id"]
        false_expected[case_id]["unit_id"] = false_case["unit_id"]
    gate, receipt_path = publish_positive_threshold_receipt(
        a, tool=tool, tool_receipt=tool_receipt, certificate=certificate,
        source_package=source_package, positive=pair,
        expected_cases=false_expected, helpers=helpers,
        profile_sha256=profile_sha256, pair_source_case="N-false31",
        receipt_case="N-false31")
    if progress is not None:
        progress.update(receipt_path=str(receipt_path),
                        receipt_issued_after_both_bodies=True)
        if progress_hook is not None:
            progress_hook("N-false31-receipt-issued")
    caller = collect_source_case(
        a, c4, ghost, tool=tool, tool_receipt=dict(tool_receipt),
        profile=profile, manifest=manifest, certificate_path=certificate_path,
        certificate=certificate, helpers=helpers, case_id="N-false31",
        native_baseline=native, focus_case_id="N-false31",
        support_cache=support_cache)
    if progress is not None:
        progress["caller_case"] = caller
        if progress_hook is not None:
            progress_hook("N-false31-caller-raw-observed")
    candidate = caller.get("proof_candidate")
    attestation = caller.get("execution_attestation")
    boundary = observe_false31_boundary(
        caller, second, certificate, helpers["a1-ast-gates.py"])
    _need(isinstance(candidate, Mapping) and
          candidate.get("classification") == "INTENDED_FOCUSED_FAILURE_CANDIDATE" and
          candidate.get("target_reached") is True and
          candidate.get("predicate") == "len<=31" and
          isinstance(attestation, Mapping) and
          attestation.get("caller_body_reached") is True and
          attestation.get("caller_body_verified") is False and
          boundary.get("classification") ==
          "LEN32_BOUNDARY_ADMISSIBLE_BY_CHECKED_INTERFACE_AND_GUARD" and
          gate.common_summary_available is True and
          Path(receipt_path).is_file(),
          "false31 caller did not fail at its own intended assertion after its own receipt")
    observation = {"classification": "FALSE31_OWN_PAIR_REPROVED_AND_CALLER_OBSERVED",
            "source_pair_sha256": pair["P0a"]["raw"]["source_pair_sha256"],
            "receipt_path": receipt_path, "body_cases": pair,
            "caller_case": caller, "boundary_observation": boundary,
            "observed_input_ids": {"source_id": false_case["source_id"],
                                   "unit_id": false_case["unit_id"]},
            "receipt_issued_after_both_bodies": True,
            "proof_credit": False}
    if progress is not None:
        progress["boundary_observation"] = boundary
    if progress_hook is not None:
        progress_hook("N-false31-caller-observed")
    return observation


def observe_focused_structure(case_id: str, raw: Mapping[str, Any],
                              fixture: Path, certificate: Mapping[str, Any],
                              helpers: Mapping[str, Any], *,
                              native_baseline: Mapping[str, Any] | None = None,
                              focus_case_id: str | None = None) -> dict:
    """Bind one raw focused case to compiler IDs, full native AST and MIR calls.

    The output remains structure-only. It never asserts body execution,
    conformance, verification success, or independent proof credit.
    """
    focus_case_id = focus_case_id or case_id
    _need(case_id in SOURCE_CASE and raw.get("case_id") == case_id and
          raw.get("focus_case_id", case_id) == focus_case_id and
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
    if focus_case_id == "P1":
        actual_pair_digest = hashlib.sha256(
            (raw["source_pair_sha256"]["verified"] + ":" +
             raw["source_pair_sha256"]["original"]).encode("ascii")).hexdigest()
        interface = gates.small_sort_interface(
            paths["proof-ast.ml"].read_text(encoding="utf-8"), inventory,
            baseline=native_baseline,
            actual_source_pair_sha256=actual_pair_digest)
        posts = gates.threshold_posts(paths["proof-ast.ml"].read_text(encoding="utf-8"),
                                      bound, stage="interface",
                                      baseline=None, common_line=common[0])
    else:
        interface = None
        stage = raw["focus_stage"]
        if focus_case_id in {"P0a", "P0b", "N-default-contract",
                            "N-freeze-contract", "N-false31"} and \
                stage == "bodies" and focus_case_id == "N-false31":
            # N-false31 reuses its own source bytes for fresh threshold body
            # proofs; it never borrows P0a/P0b source or receipt identities.
            stage = "bodies"
        posts = gates.threshold_posts(paths["proof-ast.ml"].read_text(encoding="utf-8"),
                                      bound, stage=stage,
                                      baseline=native_baseline, common_line=common[0])
    calls = None
    if focus_case_id in ("P0c", "N-false31", "P1"):
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
            "case_id": case_id, "focus_case_id": focus_case_id,
            "inventory": inventory,
            "bound_impls": bound, "threshold_posts": posts,
            "caller_calls": calls, "small_sort_interface": interface,
            "proof_credit": False,
            "body_count_observed": None,
            "native_conformance_verified": None}


def collect_source_case(a, c4, ghost, *, tool: Path, tool_receipt: dict,
                        profile: dict, manifest: dict, certificate_path: Path,
                        certificate: Mapping[str, Any], helpers: Mapping[str, Any],
                        case_id: str,
                        native_baseline: Mapping[str, Any] | None = None,
                        focus_case_id: str | None = None,
                        support_cache: dict[str, dict] | None = None,
                        evidence_id: str | None = None,
                        control_env: Mapping[str, str] | None = None) -> dict:
    """Run one isolated paired source case and record only raw/structural facts."""
    _need(case_id in SOURCE_CASE and
          int(a.deadline_epoch) - int(time.time()) > 120,
          "source case unsupported or shared deadline exhausted")
    fixture = Path(a.evidence) / "a1-fixtures" / case_id
    focus_case_id = focus_case_id or case_id
    raw = helpers["a1-focus-backend.py"].collect_focus(
        a, c4, ghost, tool, tool_receipt, profile, manifest,
        certificate_path, fixture, case_id,
        inventory_module=helpers["a1-compiler-inventory.py"],
        call_binding_module=helpers["a1-call-binding.py"],
        focus_case_id=focus_case_id, support_cache=support_cache,
        evidence_id=evidence_id, control_env=control_env)
    if raw.get("paired_support", {}).get("paired_support_passed") is not True or \
            raw.get("artifacts", {}).get("proof-ast.ml", {}).get("sha256") is None:
        return {"classification": "INCONCLUSIVE_CURRENT_STAGE",
                "case_id": case_id, "raw": raw, "structure": None,
                "proof_credit": False}
    structure = observe_focused_structure(case_id, raw, fixture, certificate,
                                           helpers, native_baseline=native_baseline,
                                           focus_case_id=focus_case_id)
    expected_case = certificate["cases"][case_id]
    actual_pair = {"verified/lib.rs": _sha(fixture / "verified/lib.rs"),
                   "original/lib.rs": _sha(fixture / "original/lib.rs")}
    expected_original_sha = hashlib.sha256(
        ghost.strip_ghost((fixture / "verified/lib.rs").read_bytes())).hexdigest()
    _need(actual_pair == {"verified/lib.rs": expected_case["generated_source_sha256"],
                          "original/lib.rs": expected_original_sha} and
          raw.get("source_pair_sha256") == {
              "verified": actual_pair["verified/lib.rs"],
              "original": actual_pair["original/lib.rs"]},
          "observed source fixture differs from its immutable constructor certificate")
    ast_path = Path(raw["artifacts"]["proof-ast.ml"]["path"])
    interval = None
    if focus_case_id in {"P0a", "P0b", "P0c", "N-default-contract",
                         "N-freeze-contract", "N-false31"}:
        if focus_case_id in ("P0a", "N-default-contract"):
            selected_impl = "default16"
        elif focus_case_id in ("P0b", "N-freeze-contract"):
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
    if focus_case_id in {"P0a", "P0b", "P0c", "N-default-contract",
                         "N-freeze-contract", "N-false31"}:
        stage = raw.get("stages", {}).get("verification", {})
        log = Path(raw.get("evidence_root", Path(a.evidence) / "focus" / case_id)) / "verification.log"
        _need(log.is_file() and stage.get("log_sha256") == _sha(log),
              "same-invocation verifier diagnostic log missing or changed")
        caller = structure["caller_calls"]
        bundle = {"threshold": structure["threshold_posts"],
                  "caller": caller["ast"] if caller else None,
                  "mir_binding": caller["mir"] if caller else None}
        source = (fixture / "verified/lib.rs").read_text(encoding="utf-8")
        verifier_log = log.read_text(encoding="utf-8")
        candidate_observation = dict(raw)
        candidate_observation["case_id"] = focus_case_id
        candidate = helpers["a1-proof-classifier.py"].classify_focus(
            focus_case_id, candidate_observation, bundle, source, verifier_log)
        _need(candidate.get("proof_credit") is False and
              candidate.get("body_count") is None and
              candidate.get("native_conformance_verified") is None,
              "candidate classifier improperly minted execution/conformance facts")
        if candidate.get("candidate_passed") is True:
            execution = attest_focused_execution(
                focus_case_id, tool=tool, profile=profile,
                raw=candidate_observation,
                structure=structure, interval=interval, candidate=candidate,
                verifier_log=verifier_log)
    return {"classification": "RAW_AND_STRUCTURE_ONLY_UNCLASSIFIED",
            "case_id": case_id, "raw": raw, "structure": structure,
            "fixture_path": str(fixture),
            "observed_input_ids": {"source_id": expected_case["source_id"],
                                   "unit_id": expected_case["unit_id"]},
            "observed_input_sha256": actual_pair,
            "focus_interval": interval, "proof_candidate": candidate,
            "execution_attestation": execution,
            "proof_credit": False}


def collect_native_reference_baseline(a, c4, *, tool: Path,
                                      tool_receipt: Mapping[str, Any],
                                      profile: Mapping[str, Any],
                                      fixture: Path,
                                      p1_raw: Mapping[str, Any],
                                      p1_structure: Mapping[str, Any],
                                      helpers: Mapping[str, Any]) -> dict:
    """Capture the exact P1 interface under the separately built R-only console."""
    reference = tool_receipt.get("native_reference")
    _need(isinstance(reference, Mapping) and
          reference.get("kind") == "separately-built-R-only-native-reference" and
          reference.get("proof_credit") is False and
          reference.get("build_id") == os.environ.get("CLOUD_BUILD_ID") and
          reference.get("build_exit") == 0 and
          reference.get("c_patch_applied") is False and
          reference.get("r_patch_sha256") == profile.get("r_patch_sha256") and
          reference.get("translator_sha256") ==
          profile.get("r_after", {}).get("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml") and
          reference.get("schema_sha256") ==
          profile.get("r_after", {}).get("src/rust_frontend/vf_mir/vf_mir.capnp") and
          reference.get("exporter_source_sha256") ==
          profile.get("r_after", {}).get("src/rust_frontend/vf_mir_exporter/src/lib.rs"),
          "separately built R-only native reference receipt required")
    console = Path(reference.get("console_path", "")).resolve()
    _need(console.is_file() and str(console).startswith("/workspace/") and
          _sha(console) == reference.get("console_binary_sha256") and
          HEX64.fullmatch(str(reference.get("translator_sha256", ""))) and
          reference.get("schema_sha256") == tool_receipt.get("final_schema_sha256") and
          reference.get("exporter_binary_sha256") ==
          tool_receipt.get("exporter_binary_sha256"),
          "R-only reference tool identity/schema/exporter mismatch")
    _need(p1_raw.get("case_id") == "P1" and
          p1_raw.get("focus_stage") == "interface" and
          p1_raw.get("paired_support", {}).get("paired_support_passed") is True and
          p1_raw.get("source_pair_sha256") == {
              "verified": _sha(fixture / "verified/lib.rs"),
              "original": _sha(fixture / "original/lib.rs")},
          "same-build P1 source pair required for native baseline")
    root = Path(a.evidence) / "a1-native-reference" / "P1"
    _need(not root.exists() and int(a.deadline_epoch) - int(time.time()) > 30,
          "fresh R-only baseline destination and deadline required")
    root.mkdir(parents=True)
    env = c4.clean_env(a, tool)
    env.update(SORT4_A1_PHASE_ID=PHASE,
               SORT4_A1_CHECKED_TRAIT_CONTRACT="1",
               SORT4_A1_STAGE="interface",
               SORT4_A1_PROFILE_SHA256=os.environ["SORT4_A1_PROFILE_SHA256"])
    ast_path = root / "r-only-native-reference-ast.ml"
    command = [str(console), "-focus", "verified/lib.rs:0",
               "-dump_ast_with_locs", str(ast_path),
               "-rustc_args", "--edition 2021", "verified/lib.rs"]
    stage = c4.stage(a, root, "r-only-native-reference",
                     command, env, 240, cwd=fixture)
    source_paths = {"verified": "verified/lib.rs", "original": "original/lib.rs"}
    source_after = {key: _sha(fixture / relative_path)
                    for key, relative_path in source_paths.items()}
    expected_source_pair = p1_raw["source_pair_sha256"]
    changed_sources = [key for key in source_paths
                       if source_after[key] != expected_source_pair[key]]
    _need(not changed_sources,
          "R-only baseline changed P1 source pair "
          f"(files={','.join(changed_sources)}; "
          f"expected={expected_source_pair}; observed={source_after})")
    _need(ast_path.is_file(),
          "R-only baseline did not emit its pre-verification AST")
    actual_source_pair_sha256 = hashlib.sha256(
        (source_after["verified"] + ":" + source_after["original"]).encode("ascii")
    ).hexdigest()
    source_pair_id = p1_structure["inventory"]["case_binding"]["source_pair_id"]
    ast_gates = helpers["a1-ast-gates.py"]
    reference_observation = {
        "schema": "a1-r-only-native-reference-receipt-v1",
        "mode": "r-only-native-reference",
        "source_pair_id": source_pair_id,
        "reference_binary_sha256": _sha(console),
        "reference_translator_sha256": reference["translator_sha256"],
        "ast_sha256": _sha(ast_path),
        "source_pair_sha256": source_after,
        "actual_source_pair_sha256": actual_source_pair_sha256,
        "build_id": os.environ["CLOUD_BUILD_ID"],
        "observed_exit": stage.get("exit"),
        "proof_credit": False,
    }
    reference_receipt_path = root / "r-only-native-reference-observation.json"
    reference_receipt_path.write_text(
        json.dumps(reference_observation, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    baseline = ast_gates.small_sort_native_baseline(
        ast_path.read_text(encoding="utf-8"), p1_structure["inventory"],
        source_pair_id=source_pair_id,
        reference_receipt=reference_observation)
    _need(baseline.get("schema") == "a1-small-sort-native-baseline-v1" and
          baseline.get("provenance") == "r-only-native-translation" and
          baseline.get("source_pair_id") == source_pair_id and
          baseline.get("actual_source_pair_sha256") == actual_source_pair_sha256 and
          baseline.get("proof_credit") is False and
          baseline.get("conformance_credit") is False,
          "R-only native baseline provenance/pair identity failed")
    return {"classification": "R_ONLY_NATIVE_INTERFACE_BASELINE_OBSERVED",
            "raw": {"stage": stage, "console_sha256": _sha(console),
                    "translator_sha256": reference["translator_sha256"],
                    "source_pair_sha256": source_after,
                    "ast_path": str(ast_path), "ast_sha256": _sha(ast_path),
                    "reference_observation_path": str(reference_receipt_path),
                    "build_id": os.environ["CLOUD_BUILD_ID"]},
            "baseline": baseline, "proof_credit": False}


def collect_p1_interface_case(a, c4, ghost, *, tool: Path,
                              tool_receipt: Mapping[str, Any], profile: dict,
                              manifest: dict, certificate_path: Path,
                              certificate: Mapping[str, Any],
                              helpers: Mapping[str, Any],
                              support_cache: dict[str, dict] | None = None) -> dict:
    """Observe P1 with final R+C tool against a separately collected R-only AST."""
    fixture = Path(a.evidence) / "a1-fixtures" / "P1"
    raw = helpers["a1-focus-backend.py"].collect_focus(
        a, c4, ghost, tool, dict(tool_receipt), profile, manifest,
        certificate_path, fixture, "P1",
        inventory_module=helpers["a1-compiler-inventory.py"],
        call_binding_module=helpers["a1-call-binding.py"],
        support_cache=support_cache)
    _need(raw.get("case_id") == "P1" and raw.get("focus_case_id") == "P1" and
          raw.get("focus_stage") == "interface" and
          raw.get("focus") == "verified/lib.rs:0" and
          raw.get("paired_support", {}).get("paired_support_passed") is True and
          raw.get("stages", {}).get("verification", {}).get("exit") == 0 and
          raw.get("artifacts", {}).get("proof-ast.ml", {}).get("sha256"),
          "P1 final-tool interface observation did not complete cleanly")
    source = (fixture / "verified/lib.rs").read_text(encoding="utf-8")
    normal = Path(raw["artifacts"]["normal-mir.txt"]["path"]).read_text(encoding="utf-8")
    readonly = Path(raw["artifacts"]["readonly-mir.txt"]["path"]).read_text(encoding="utf-8")
    inventory = helpers["a1-compiler-inventory.py"].observe(
        "P1", normal, readonly, dict(certificate), source)
    reference = collect_native_reference_baseline(
        a, c4, tool=tool, tool_receipt=tool_receipt, profile=profile,
        fixture=fixture, p1_raw=raw,
        p1_structure={"inventory": inventory}, helpers=helpers)
    structure = observe_focused_structure(
        "P1", raw, fixture, certificate, helpers,
        native_baseline=reference["baseline"], focus_case_id="P1")
    interface = structure.get("small_sort_interface")
    _need(isinstance(interface, Mapping) and
          interface.get("classification") == "INTERFACE_STRUCTURE_ONLY_UNRUN_PROOF" and
          interface.get("structural_pass") is True and
          interface.get("body_count") == 0 and
          interface.get("proof_credit") is False and
          interface.get("source_pair_id") == reference["baseline"]["source_pair_id"] and
          interface.get("compiler_interface_digest") ==
          reference["baseline"]["compiler_interface_digest"],
          "P1 full small_sort interface structural gate failed")
    return {"classification": "P1_FULL_INTERFACE_OBSERVED",
            "raw": raw, "inventory": inventory, "baseline": reference,
            "structure": structure, "proof_credit": False,
            "body_count": 0,
            "observed_input_ids": {
                "source_id": certificate["cases"]["P1"]["source_id"],
                "unit_id": certificate["cases"]["P1"]["unit_id"]},
            "observed_input_sha256": {
                "verified/lib.rs": _sha(fixture / "verified/lib.rs"),
                "original/lib.rs": _sha(fixture / "original/lib.rs")}}


def _false31_source_boundary(lines, binding):
    """Find strict boundary order within the paired compiler-bound observer."""
    _need(isinstance(binding, Mapping) and binding.get("caller") == "a1_guard_observer",
          "false31 boundary requires the compiler-bound observer")
    span = binding.get("mir_body_span")
    _need(isinstance(span, Mapping), "false31 caller MIR Body.span missing")
    lo, hi = span.get("lo"), span.get("hi")
    _need(isinstance(lo, Mapping) and isinstance(hi, Mapping),
          "false31 caller MIR Body.span endpoints missing")
    start, end = lo.get("line"), hi.get("line")
    _need(lo.get("source_path") == hi.get("source_path") == "verified/lib.rs" and
          type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
          "false31 caller MIR Body.span invalid")
    guards = [i for i in range(start, end + 1)
              if lines[i - 1].strip() == "if len <= T::small_sort_threshold() {"]
    assertions = [i for i in range(start, end + 1)
                  if lines[i - 1].strip() == "//@ assert len <= 31;"]
    _need(len(guards) == len(assertions) == 1 and guards[0] < assertions[0],
          "certified inclusive threshold guard and false31 assertion must be unique and ordered")
    return guards[0], assertions[0], (start, end)


def observe_false31_boundary(caller_case: Mapping[str, Any],
                             freeze_body_case: Mapping[str, Any],
                             certificate: Mapping[str, Any],
                             ast_gates) -> dict:
    """Bind len=32 boundary admissibility to the actual checked interface/call.

    This is a structural boundary observation. It records the checked native
    threshold range, actual Freeze body observation, and the certified strict
    caller guard in one source pair; it never claims a concrete execution or
    independent proof credit.
    """
    source_case = certificate["cases"]["N-false31"]
    body_attestation = freeze_body_case.get("execution_attestation")
    _need(isinstance(body_attestation, Mapping) and
          body_attestation.get("focus_body_verified") is True and
          body_attestation.get("focus_conformance_verified") is True and
          body_attestation.get("compiler_identity", {}).get("impl") == "freeze32",
          "boundary requires actual same-pair Freeze32 body/conformance attestation")
    caller_raw = caller_case["raw"]
    caller_structure = caller_case["structure"]
    _need(caller_raw.get("source_pair_sha256", {}).get("verified") ==
          source_case["generated_source_sha256"] and
          caller_structure.get("focus_case_id") == "N-false31" and
          caller_structure.get("caller_calls", {}).get("ast", {}).get("classification") ==
          "CALL_AST_STRUCTURE_ONLY",
          "boundary caller AST/source pair is not compiler-bound")
    source = Path(caller_case["fixture_path"]) / "verified/lib.rs"
    _need(source.is_file() and _sha(source) ==
          source_case["generated_source_sha256"],
          "boundary source bytes differ from N-false31 certificate")
    lines = source.read_text(encoding="utf-8").splitlines()
    binding = caller_structure["caller_calls"]["mir"]["binding"]
    guard_line, assertion_line, caller_span = _false31_source_boundary(lines, binding)
    calls = binding.get("calls", [])
    threshold_calls = [row for row in calls
                       if row.get("callee") == "StableSmallSortTypeImpl::small_sort_threshold"]
    _need(len(threshold_calls) == 1 and
          threshold_calls[0].get("call_line") == guard_line,
          "compiler MIR threshold call must bind to the certified inclusive guard line")
    # Use the actual N-false31 caller AST: unlike an impl-body focus, this
    # caller stage has passed the checked common native summary through its
    # exact-pair receipt.
    caller_ast = Path(caller_raw["artifacts"]["proof-ast.ml"]["path"])
    inventory = caller_structure["inventory"]["inventory"]
    common_spans = [span for name, span in inventory["required_method_spans"]
                    if name == "small_sort_threshold"]
    _need(len(common_spans) == 1, "one compiler required threshold span")
    caller_ast_text = caller_ast.read_text(encoding="utf-8")
    select_focused_body(caller_ast_text, ast_gates, focus_line=caller_span[0],
                        expected_name="a1_guard_observer", compiler_span=caller_span)
    fs = ast_gates.functions(caller_ast_text)
    common = [row for row in fs if row["name"] == ast_gates.COMMON and
              row["kind"] == "prototype"]
    _need(len(common) == 1, "one compiler-bound checked common threshold AST prototype required")
    _need(ast_gates._source_line(common[0]["fields"][0]) == common_spans[0][0][1],
          "checked common AST prototype differs from compiler required-item span")
    checked = ast_gates.contract(common[0], True)
    _need(checked.get("checked_range") is True and
          caller_structure["threshold_posts"].get("stage") == "caller" and
          caller_structure["threshold_posts"].get("common_checked") is True,
          "actual AST must retain the inclusive 16..32 common threshold contract")
    return {"classification": "LEN32_BOUNDARY_ADMISSIBLE_BY_CHECKED_INTERFACE_AND_GUARD",
            "source_pair_sha256": caller_raw["source_pair_sha256"],
            "guard_source_line": guard_line, "assertion_source_line": assertion_line,
            "caller_source_span": list(caller_span),
            "guard_expression": "len <= T::small_sort_threshold()",
            "threshold_contract_ast_sha256": _sha(caller_ast),
            "threshold_upper_bound": 32, "boundary_len": 32,
            "boundary_satisfies_guard": 32 <= 32,
            "freeze_body_conformance_observed": True,
            "proof_credit": False,
            "assurance": "source-and-AST structural boundary observation"}


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
    _need(profile.get("execution_mode") in
          {"parser-preflight", "full-matrix", "native-p1-target"},
          "recognized unaccepted A1 execution mode required")
    if profile.get("execution_mode") == "native-p1-target":
        _need(profile.get("authorization_phase_id") in
              ("SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10",
               "SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11"),
              "bounded native P1 target requires R10/R11 authorization")
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
                 "N-source", "N-binding", "N-region-swap",
                 "N-clause-redirect"} else "none")
        cases.append({"case_id": case_id, "source_adapter": source,
                      "focus_mode": mode, "executed": False,
                      "proof_credit": False})
    return {
        "classification": "PLANNED_UNRUN_MATRIX",
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
        "required_runtime_gates": [
            "same-Build immutable source and tool identities",
            "actual focused body/conformance and caller stages",
            "P1 compiler-bound structural interface plus R-only native baseline",
            "synthetic transport/admission classifier routes",
            "all 26 observed rows validated by A1Admission"],
        "first_missing_stage": None,
        "tool_reconstructed": False, "fixtures_generated": False,
        "verification_invoked": False, "matrix_complete": False,
        "dispatch_ready": False, "proof_credit": False,
    }


def _stage_result(case_id: str, observation: Any, *, error: str | None = None) -> dict:
    """Keep lifecycle status separate from expected matrix verdict labels."""
    if not isinstance(observation, Mapping):
        return {"case_id": case_id, "status": "INCONCLUSIVE" if error else "NOT_RUN",
                "observed_stage": None, "observed_outcome": None,
                "reason": error, "proof_credit": False}
    raw = observation.get("raw")
    if isinstance(raw, Mapping):
        nested_stages = raw.get("stages")
        stages = nested_stages if isinstance(nested_stages, Mapping) else {}
    else:
        stages = observation.get("stages", {})
    if not isinstance(stages, Mapping):
        stages = {}
    stage = observation.get("first_causal_stage")
    if stage is None:
        stage = next((name for name, row in stages.items()
                      if isinstance(row, Mapping) and row.get("exit") not in (None, 0)), None)
    outcome = observation.get("classification")
    if outcome is None and isinstance(observation.get("proof_candidate"), Mapping):
        outcome = observation["proof_candidate"].get("classification")
    status = ("INCONCLUSIVE" if isinstance(outcome, str) and
              "INCONCLUSIVE" in outcome else
              "OBSERVED" if stages or raw or outcome else "INCONCLUSIVE")
    return {"case_id": case_id, "status": status,
            "observed_stage": stage, "observed_outcome": outcome,
            "reason": error, "proof_credit": False}


def _safe_action(rows: dict, case_id: str, action) -> Any:
    """Run one adapter without converting setup/early failures into a verdict."""
    try:
        value = action()
        rows[case_id] = value
        return value
    except Exception as exc:
        rows[case_id] = {"adapter_error": f"{type(exc).__name__}: {exc}",
                         "proof_credit": False}
        return None


@lru_cache(maxsize=8)
def _progress_source_sha256(path: str) -> str | None:
    """Hash a parser source path once per bounded set of loaded modules."""
    source = Path(path)
    if not source.is_file():
        return None
    return hashlib.sha256(source.read_bytes()).hexdigest()


def _jsonable(value: Any) -> Any:
    """Preserve progress values and the parser's explicit immutable node schema."""
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()
                if key not in {"admission_gate", "support_cache", "certificate"}}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        kind = type(value).__name__
        parser_module = sys.modules.get(type(value).__module__)
        parser_source = getattr(parser_module, "__file__", None)
        expected_source = Path(__file__).with_name("a1-synthetic-inputs.py")
        source_path = Path(parser_source) if isinstance(parser_source, str) else None
        expected_key = str(expected_source.resolve())
        source_key = str(source_path.resolve()) if source_path is not None else None
        if (source_path is None or source_path.name != expected_source.name or
                _progress_source_sha256(source_key) is None or
                _progress_source_sha256(source_key) !=
                _progress_source_sha256(expected_key) or
                getattr(parser_module, kind, None) is not type(value)):
            raise TypeError("unsupported progress value: " + kind)
        names = tuple(field.name for field in fields(value))
        if kind in {"Text", "Atom", "Number"} and names == ("value",):
            scalar = value.value
            if isinstance(scalar, str):
                return {"kind": kind, "value": scalar}
        elif kind == "Record" and names == ("fields",):
            pairs = value.fields
            if isinstance(pairs, tuple):
                encoded = []
                for pair in pairs:
                    if (not isinstance(pair, tuple) or len(pair) != 2 or
                            not isinstance(pair[0], str)):
                        break
                    encoded.append([pair[0], _jsonable(pair[1])])
                else:
                    return {"kind": "Record", "fields": encoded}
        elif kind == "ListValue" and names == ("values",):
            items = value.values
            if isinstance(items, tuple):
                return {"kind": "ListValue",
                        "values": [_jsonable(item) for item in items]}
    raise TypeError("unsupported progress value: " + type(value).__name__)


def _report_value_for_disk(value, authorization_phase):
    """Replace duplicated authorized row observations with lossless local pointers."""
    r9_authorization_phase = "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9"
    r10_authorization_phase = "SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10"
    r11_authorization_phase = "SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11"
    if (authorization_phase not in (r9_authorization_phase, r10_authorization_phase,
                                    r11_authorization_phase) or
            not isinstance(value, Mapping) or
            value.get("authorization_phase_id") != authorization_phase):
        return value
    details = value.get("observation_details")
    rows = value.get("observed_rows")
    if (not isinstance(details, Mapping) or not isinstance(rows, list) or
            "report_serialization" in value):
        return value

    def same_json_value(left, right):
        # JSON distinguishes values such as true and 1 although Python equality
        # does not; only replace a row when the serialized values are identical.
        if type(left) is not type(right):
            return False
        if isinstance(left, Mapping):
            return (left.keys() == right.keys() and
                    all(same_json_value(left[key], right[key]) for key in left))
        if isinstance(left, list):
            return (len(left) == len(right) and
                    all(same_json_value(a, b) for a, b in zip(left, right)))
        return left == right

    seen = set()
    replacements = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            return value
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id in seen:
            return value
        seen.add(case_id)
        if case_id not in details:
            continue
        row_observation = row.get("observation")
        mapped_observation = details[case_id]
        # Null, malformed, or disagreeing data stays inline; no synthetic
        # reference can turn an incomplete/ambiguous report into a successful one.
        if row_observation is None or mapped_observation is None:
            continue
        if not isinstance(row_observation, Mapping) or not isinstance(mapped_observation, Mapping):
            continue
        if not same_json_value(row_observation, mapped_observation):
            return value
        if "observation_ref" in row:
            return value
        escaped = case_id.replace("~", "~0").replace("/", "~1")
        replacements[index] = {
            "schema": "a1-observation-ref-v1",
            "json_pointer": "/observation_details/" + escaped,
        }
    if not replacements:
        return value

    disk_value = dict(value)
    disk_rows = list(rows)
    for index, reference in replacements.items():
        disk_row = dict(rows[index])
        disk_row.pop("observation", None)
        disk_row["observation_ref"] = reference
        disk_rows[index] = disk_row
    disk_value["observed_rows"] = disk_rows
    disk_value["report_serialization"] = {
        "kind": "row-pointer-v1", "lossless": True, "proof_credit": False,
    }
    return disk_value


def _run_off_observation(a, c4, tool: Path, off_input: Mapping[str, Any],
                        selected_proof) -> dict:
    """Observe the selected positive fixture with the A1 opt-in absent."""
    fixture = Path(str(off_input.get("fixture", ""))).resolve()
    _need(str(fixture).startswith(str(Path(a.evidence).resolve())) and
          (fixture / "verified/lib.rs").is_file() and
          (fixture / "original/lib.rs").is_file(),
          "certified OFF selected source pair required")
    root = Path(a.evidence) / "a1-off-observation"
    _need(not root.exists(), "fresh OFF observation destination required")
    env = c4.clean_env(a, tool)
    _need("SORT4_A1_CHECKED_TRAIT_CONTRACT" not in env and
          "SORT4_A1_PHASE_ID" not in env,
          "A1 opt-in must be absent in OFF environment")
    source_pair_before = {name: _sha(fixture / name)
                          for name in ("verified/lib.rs", "original/lib.rs")}
    _need(source_pair_before == {"verified/lib.rs": off_input.get("verified_sha256"),
                                "original/lib.rs": off_input.get("original_sha256")},
          "OFF exact prepared source pair identity")
    result = c4.verify_case(a, tool, fixture, root, env,
                            target=selected_proof.SELECTED["selected-branch-positive"],
                            ast=True, require_paired_support=False, verbosity=4)
    log_path = root / "verification.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    first = next((line for line in log.splitlines()
                  if ": error:" in line or line.startswith(("Fatal error:", "error:"))), None)
    source_pair_after = {name: _sha(fixture / name)
                         for name in ("verified/lib.rs", "original/lib.rs")}
    source_lines = (fixture / "verified/lib.rs").read_text(encoding="utf-8").splitlines()
    trait_lines = [index for index, line in enumerate(source_lines, 1)
                   if "trait StableSmallSortTypeImpl" in line]
    impl_lines = [index for index, line in enumerate(source_lines, 1)
                  if line.lstrip().startswith("impl<") and "StableSmallSortTypeImpl" in line]
    trait_method_lines = [index for index, line in enumerate(source_lines, 1)
                          if line.strip().startswith("fn small_sort<F:") and
                          (not impl_lines or index < impl_lines[0])]
    error_lines = [int(value) for value in re.findall(r"(?:^|/)verified/lib\.rs\((\d+),", first or "")]
    duplicate_diagnostic = (len(trait_lines) == len(trait_method_lines) == 1 and
                            len(error_lines) == 1 and
                            error_lines[0] == trait_method_lines[0] and
                            "Duplicate type parameter ''_'" in (first or ""))
    immutable = source_pair_after == source_pair_before
    return {"classification": "OFF_BASELINE_OBSERVATION_ONLY",
            "stages": result.get("stages", {}),
            "first_causal_stage": result.get("first_causal_stage"),
            "first_diagnostic": first,
            "paired_support": result.get("support"),
            "source_pair_immutable": result.get("source_pair_immutable"),
            "observed_input_ids": {"source_id": off_input["source_id"],
                                   "unit_id": off_input["unit_id"]}
            if source_pair_after == source_pair_before else None,
            "source_pair_sha256": source_pair_after,
            "prepared_source_pair_sha256": source_pair_before,
            "exact_source_bound_duplicate_parameter_diagnostic": duplicate_diagnostic,
            "duplicate_trait_parameter_at_source_declaration": duplicate_diagnostic and immutable,
            "input_identity_verified": immutable and
                source_pair_after == source_pair_before and
                off_input.get("verified_sha256") == source_pair_after["verified/lib.rs"] and
                off_input.get("original_sha256") == source_pair_after["original/lib.rs"],
            "source_id": off_input["source_id"], "unit_id": off_input["unit_id"],
            "proof_ast_sha256": result.get("proof_ast_sha256"),
            "proof_credit": False}


def classify_dispatch_observation(raw: Mapping[str, Any], *,
                                  expected_source_sha256: str) -> dict:
    """Classify translator dispatch from exact current full-unit trace lines."""
    result = {"classification": "INCONCLUSIVE_DISPATCH_OBSERVATION",
              "proof_credit": False}
    stages = raw.get("stages", {})
    if (raw.get("case_id") != "P-dispatch" or
            raw.get("source_pair_sha256", {}).get("verified") != expected_source_sha256 or
            raw.get("paired_support", {}).get("paired_support_passed") is not True or
            not isinstance(stages, Mapping) or
            stages.get("verification", {}).get("exit") != 0):
        return {**result, "reason": "full-unit translator/stage/source gate missing"}
    log = Path(raw.get("evidence_root", "")) / "verification.log"
    if not log.is_file() or stages["verification"].get("log_sha256") != _sha(log):
        return {**result, "reason": "same-invocation translated-call trace unavailable"}
    lines = log.read_text(errors="replace").splitlines()
    observed = {}
    for tag, name in (("SORT4-A1-DISPATCH", "StableSmallSortTypeImpl::small_sort_threshold"),
                      ("SORT4-A1-DISPATCH", "StableSmallSortTypeImpl::small_sort")):
        matches = [line for line in lines if line.startswith(tag + ":") and
                   ("original=" + name) in line]
        if len(matches) != 1:
            return {**result, "reason": "unique original common dispatch trace missing",
                    "matched_lines": len(matches)}
        match = re.fullmatch(re.escape(tag) + r": original=" + re.escape(name) +
                             r" translated=" + re.escape(name) + r" redirect=false", matches[0])
        if match is None:
            return {**result, "reason": "translator redirected or changed original common call"}
        observed[name] = matches[0]
    if not raw.get("artifacts", {}).get("proof-ast.ml", {}).get("sha256"):
        return {**result, "reason": "same-unit AST missing"}
    return {"classification": "ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED",
            "trace_lines": observed, "source_sha256": expected_source_sha256,
            "verification_exit": 0, "proof_credit": False}


def observe_admission_control(case_id: str, *, call_binding, compiler_inventory,
                              normal: str, readonly: str, certificate: Mapping[str, Any],
                              source: str, control_path: Path) -> dict:
    """Execute the source-reported admission validators on actual paired MIR."""
    result = {"case_id": case_id, "classification": "INCONCLUSIVE_ADMISSION_CONTROL",
              "proof_credit": False}
    input_sha = _sha(control_path)
    if case_id == "N-source":
        mutated_certificate = json.loads(control_path.read_text())
        try:
            call_binding.observe("P1", normal, readonly,
                                 mutated_certificate, source)
        except call_binding.CallBindingError as exc:
            if "generated Rust source does not match case source hashes" == str(exc):
                return {**result, "classification": "SOURCE_CERTIFICATE_REFUSAL_OBSERVED",
                        "stage": "source-admission", "error_type": type(exc).__name__,
                        "observed_error": str(exc), "control_input_sha256": input_sha,
                        "control_input_immutable": _sha(control_path) == input_sha,
                        "observed_input_ids": {"source_id": certificate["cases"]["P1"]["source_id"],
                                               "unit_id": certificate["cases"]["P1"]["unit_id"]}}
            return {**result, "observed_error": str(exc)}
        return {**result, "reason": "mutated certificate unexpectedly admitted"}
    if case_id == "N-binding":
        observation = call_binding.observe("P1", normal, readonly,
                                           dict(certificate), source)
        inventory = compiler_inventory.observe("P1", normal, readonly,
                                                dict(certificate), source)
        wrong_claim = json.loads(control_path.read_text())
        try:
            call_binding.validate_common_binding_claim(observation, inventory,
                                                       wrong_claim)
        except call_binding.CallBindingError as exc:
            if str(exc) != "claim differs from the paired compiler caller MIR binding":
                return {**result, "observed_error": str(exc)}
            return {**result, "classification": "CALL_BINDING_CLAIM_REFUSAL_OBSERVED",
                    "stage": "call-binding-admission", "error_type": type(exc).__name__,
                    "observed_error": str(exc), "control_input_sha256": input_sha,
                    "control_input_immutable": _sha(control_path) == input_sha,
                    "observed_input_ids": {"source_id": certificate["cases"]["P1"]["source_id"],
                                           "unit_id": certificate["cases"]["P1"]["unit_id"]}}
        return {**result, "reason": "mutated caller claim unexpectedly admitted"}
    if case_id == "N-region-swap":
        observation = call_binding.observe("P1", normal, readonly,
                                           dict(certificate), source)
        inventory = compiler_inventory.observe("P1", normal, readonly,
                                                dict(certificate), source)
        claim = json.loads(control_path.read_text())
        try:
            call_binding.validate_common_binding_claim(observation, inventory, claim)
        except call_binding.CallBindingError as exc:
            if str(exc) != "claim input-region role map differs from compiler-derived call/input region map":
                return {**result, "observed_error": str(exc)}
            return {**result, "classification": "INPUT_REGION_ROLE_REFUSAL_OBSERVED",
                    "stage": "call-binding-admission", "error_type": type(exc).__name__,
                    "observed_error": str(exc), "control_input_sha256": input_sha,
                    "control_input_immutable": _sha(control_path) == input_sha,
                    "observed_input_ids": {"source_id": certificate["cases"]["P1"]["source_id"],
                                           "unit_id": certificate["cases"]["P1"]["unit_id"]}}
        return {**result, "reason": "mutated input-region claim unexpectedly admitted"}
    return {**result, "reason": "unsupported pure admission control"}


def classify_redirect_observation(raw: Mapping[str, Any], *,
                                  expected_source_sha256: str) -> dict:
    """Require the forced legacy probe's own first translator refusal."""
    result = {"classification": "INCONCLUSIVE_REDIRECT_CONTROL",
              "proof_credit": False}
    stages = raw.get("stages", {})
    if (raw.get("focus_case_id") != "P0c" or
            raw.get("source_pair_sha256", {}).get("verified") != expected_source_sha256 or
            raw.get("paired_support", {}).get("paired_support_passed") is not True or
            not isinstance(stages, Mapping) or
            stages.get("verification", {}).get("exit") in (None, 0)):
        return {**result, "reason": "forced redirect invocation did not reach failing translator"}
    log = Path(raw.get("evidence_root", "")) / "verification.log"
    if not log.is_file() or stages["verification"].get("log_sha256") != _sha(log):
        return {**result, "reason": "same-invocation redirect diagnostic unavailable"}
    text = log.read_text(errors="replace")
    first = next((line for line in text.splitlines()
                  if ": error:" in line or line.startswith(("Fatal error:", "error:"))), None)
    intended = "SORT4-A1-CONTRACT: legacy clause-ignoring redirect attempted at common call"
    if first is None or intended not in first:
        return {**result, "reason": "first diagnostic differs from intended legacy redirect refusal",
                "first_diagnostic": first}
    return {"classification": "LEGACY_REDIRECT_REFUSAL_OBSERVED",
            "stage": "translated-call-gate", "first_diagnostic": first,
            "verification_exit": stages["verification"]["exit"],
            "proof_credit": False}


def _run_native_target_sequence(run_stage, *, p1_action, binding_actions,
                                alpha_action):
    """Run only the bounded target routes in their required dependency order.

    ``run_stage`` is the runner's deadline/progress-aware action wrapper.
    A missing optional callable is recorded as explicit NOT_RUN; the helper
    never changes or synthesizes an observation returned by that wrapper.
    """
    if not isinstance(binding_actions, Mapping):
        binding_actions = {}
    if callable(p1_action):
        rows = {"P1": run_stage("P1", p1_action)}
    else:
        rows = {"P1": {"not_run": True, "execution_started": False,
                        "reason": "certified P1 source fixture unavailable",
                        "proof_credit": False}}
    for case_id in ("N-binding", "N-region-swap"):
        callback = binding_actions.get(case_id)
        if callable(callback):
            rows[case_id] = run_stage(case_id, callback)
        else:
            rows[case_id] = {"not_run": True, "execution_started": False,
                             "reason": "paired P1 admission-control prerequisites unavailable",
                             "proof_credit": False}
    if callable(alpha_action):
        rows["N-alpha-valid"] = run_stage("N-alpha-valid", alpha_action)
    else:
        rows["N-alpha-valid"] = {
            "not_run": True, "execution_started": False,
            "reason": "same-Build compiler-derived paired baseline unavailable",
            "proof_credit": False}
    return rows


def _native_target_context(positive_progress):
    """Return safe views of partial positive data without rewriting it."""
    positive_cases = (positive_progress.get("positive_cases")
                      if isinstance(positive_progress, Mapping) else None)
    positive_cases = positive_cases if isinstance(positive_cases, Mapping) else {}
    p0a = positive_cases.get("P0a")
    p0a = p0a if isinstance(p0a, Mapping) else {}
    p0a_raw = p0a.get("raw")
    p0a_raw = p0a_raw if isinstance(p0a_raw, Mapping) else {}
    artifacts = p0a_raw.get("artifacts")
    artifacts = artifacts if isinstance(artifacts, Mapping) else {}
    structure = p0a.get("structure")
    structure = structure if isinstance(structure, Mapping) else {}
    inventory = structure.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    inventory_payload = inventory.get("inventory")
    inventory_payload = (inventory_payload if isinstance(inventory_payload, Mapping)
                         else {})
    impls = inventory_payload.get("impls")
    impls = impls if isinstance(impls, list) else []
    bound = structure.get("bound_impls")
    bound = bound if isinstance(bound, Mapping) else {}
    return {"positive_cases": positive_cases, "p0a": p0a, "p0a_raw": p0a_raw,
            "artifacts": artifacts, "structure": structure,
            "impls": [row for row in impls if isinstance(row, Mapping)],
            "bound_impls": bound}


def _classify_native_target_rows(case_status, observed_rows, observations,
                                 target_cases, expected_inputs, classifier,
                                 run_pins, build_id, expected_inventory):
    """Classify observed target rows only; never admits a matrix."""
    observations = observations if isinstance(observations, Mapping) else {}
    target_cases = target_cases if isinstance(target_cases, (set, frozenset)) else set()
    expected_inputs = expected_inputs if isinstance(expected_inputs, Mapping) else {}
    expected_inventory = expected_inventory if isinstance(expected_inventory, Mapping) else {}
    records = []
    for case_id in CASE_ORDER:
        observation = observations.get(case_id)
        if case_id not in target_cases:
            classified = {"case_id": case_id, "status": "NOT_RUN",
                          "matrix_gate_passed": False, "record": None,
                          "reason": "not run in bounded native-p1-target scope",
                          "proof_credit": False}
        elif (isinstance(observation, Mapping) and
              observation.get("not_run") is True and
              observation.get("execution_started") is False):
            classified = {"case_id": case_id, "status": "NOT_RUN",
                          "matrix_gate_passed": False, "record": None,
                          "reason": observation.get("reason"),
                          "proof_credit": False}
        elif (case_id in expected_inputs and
              isinstance(expected_inputs.get(case_id), Mapping) and
              isinstance(observation, Mapping) and classifier is not None and
              isinstance(run_pins, Mapping) and isinstance(build_id, str) and build_id):
            try:
                classified = classifier.classify_case(
                    case_id, observation, expected_input=expected_inputs[case_id],
                    run_pins=run_pins, build_id=build_id,
                    expected_inventory=expected_inventory)
                if not isinstance(classified, Mapping):
                    classified = {"case_id": case_id, "status": "INCONCLUSIVE",
                                  "matrix_gate_passed": False, "record": None,
                                  "reason": "target classifier returned wrong-type metadata",
                                  "proof_credit": False}
            except Exception as exc:
                classified = {"case_id": case_id, "status": "INCONCLUSIVE",
                              "matrix_gate_passed": False, "record": None,
                              "reason": f"target classifier error: {type(exc).__name__}: {exc}",
                              "proof_credit": False}
        else:
            classified = {"case_id": case_id,
                          "status": "INCONCLUSIVE" if observation is not None else "NOT_RUN",
                          "matrix_gate_passed": False, "record": None,
                          "reason": "target observation or exact input/run identities unavailable",
                          "proof_credit": False}
        record = classified.get("record")
        record = record if isinstance(record, Mapping) else None
        status = {
            "status": classified.get("status", "INCONCLUSIVE"),
            "observed_stage": (record or {}).get("stage"),
            "observed_outcome": classified.get("observed_classification"),
            "reason": classified.get("reason"),
            "matrix_gate_passed": classified.get("matrix_gate_passed") is True,
            "proof_credit": False,
            "provenance": classified.get("provenance")}
        case_status[case_id] = status
        if record is not None:
            records.append({**record, "proof_credit": False})
        raw = (observation.get("raw") if isinstance(observation, Mapping) else None)
        nested_ids = (observation.get("observed_input_ids")
                      if isinstance(observation, Mapping) else None)
        if isinstance(raw, Mapping):
            nested_ids = raw
        if not isinstance(nested_ids, Mapping):
            nested_ids = {}
        observed_source_id = nested_ids.get("source_id")
        observed_unit_id = nested_ids.get("unit_id")
        if isinstance(observation, Mapping):
            observed_source_id = observed_source_id or observation.get("source_id")
            observed_unit_id = observed_unit_id or observation.get("unit_id")
        observed_rows.append({"case_id": case_id,
                              "source_id": ((record or {}).get("source_id") or
                                            observed_source_id),
                              "unit_id": ((record or {}).get("unit_id") or
                                          observed_unit_id),
                              "observation": observation,
                              "status": status})
    return records


def run(a, *, c4, audit, driver, manifest: Mapping[str, Any], ghost) -> dict:
    """Run the pinned A1 lifecycle and retain only actually observed results."""
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
    _need(profile.get("profile_pin_source") == "coordinator-environment" and
          profile.get("proof_sha") in (None, "") and
          profile.get("infra_sha") in (None, "") and
          profile.get("cloud_build_enabled") is True,
          "published A1 profile must use the exact coordinator-pinned run identity")
    _need(env.get("SORT4_A1_AUTHORIZATION_PHASE_ID") == AUTHORIZATION_PHASE and
          profile.get("authorization_phase_id") == AUTHORIZATION_PHASE and
          profile.get("experiment_protocol_phase_id") == PHASE,
          "exact authorization to preserved experiment protocol binding")
    plan = preflight_plan(profile, _admission_matrix(
        Path(a.proof_root) / HERE / "a1-contract-admission.py"))
    expected_manifest = Path(a.proof_root) / HERE / "CALLER-ENTRY-MANIFEST.json"
    _need(expected_manifest.is_file() and
          _sha(expected_manifest) == profile.get("caller_manifest_sha256") and
          json.loads(expected_manifest.read_text()) == dict(manifest),
          "exact legacy caller manifest required")
    dependencies = (
        (c4, Path(a.cloud_dir) / "sort4-caller-entry-native/selected-runtime.py",
         manifest["runtime_helpers_sha256"]["selected-runtime.py"]),
        (audit, Path(a.cloud_dir) / "sort4-first-scope-audit.py",
         manifest["runtime_helpers_sha256"]["sort4-first-scope-audit.py"]),
        (driver, Path(a.cloud_dir) / "sort4-caller-entry-native/driver.py",
         profile["caller_driver_sha256"]),
        (ghost, Path(a.cloud_dir) / "sort4-native-c1-bound/ghost-strip.py",
         manifest["ghost_strip_sha256"]),
    )
    for module, path, digest in dependencies:
        _need(Path(module.__file__).resolve() == path.resolve() and
              path.is_file() and _sha(path) == digest,
              "runner dependency differs from exact Cloud/proof pin: " + str(path))
    result = {"classification": "A1_RUNNER_OBSERVED_LIFECYCLE",
              "phase_id": PHASE, "authorization_phase_id": AUTHORIZATION_PHASE,
              "planned_order": list(CASE_ORDER),
              "case_status": {case_id: {"status": "NOT_RUN",
                  "observed_stage": None, "observed_outcome": None,
                  "proof_credit": False} for case_id in CASE_ORDER},
              "observed_rows": [], "matrix_complete": False,
              "dispatch_ready": False, "admission_record_created": False,
              "proof_credit": False,
              "build_id": env["CLOUD_BUILD_ID"], "proof_sha": proof_sha,
              "infra_sha": infra_sha, "profile_sha256": profile_sha}
    native_target_mode = profile.get("execution_mode") == "native-p1-target"
    if native_target_mode:
        result.update(
            target_scope={"mode": "native-p1-target",
                          "case_ids": [case for case in CASE_ORDER
                                       if case in NATIVE_TARGET_CASES],
                          "matrix_admission_invoked": False,
                          "matrix_admission_recorded": False,
                          "proof_credit": False},
            diagnostic_complete=False, evidence_complete=False,
            verification_accepted=False, profile_accepted=False,
            accepted=False, proof_verdict=None, proof_credit=False)
    progress_path = Path(a.evidence) / "a1-lifecycle-progress.json"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    def persist_progress():
        snapshot = _jsonable(result)
        snapshot["observation_details"] = _jsonable(observations)
        snapshot["execution_events"] = _jsonable(execution_events)
        snapshot["positive_lifecycle_progress"] = {
            key: value for key, value in positive_progress.items()
            if key not in ("certificate", "admission_gate", "support_cache")}
        progress_path.write_text(json.dumps(_jsonable(snapshot), indent=2,
                                            sort_keys=True) + "\n")

    execution_events: list[dict[str, Any]] = []

    def action(case_id: str, thunk, *, minimum_remaining: int | None = None):
        minimum = (minimum_remaining if minimum_remaining is not None else
                   120 if case_id in SOURCE_CASE or case_id in
                   {"P1", "N-false31", "N-clause-redirect"} else 30)
        remaining = int(a.deadline_epoch) - int(time.time())
        if remaining <= minimum:
            value = {"not_run": True, "execution_started": False,
                     "reason": "shared Build deadline left no safe stage budget",
                     "deadline_remaining_seconds": max(0, remaining),
                     "proof_credit": False}
            observations[case_id] = value
            execution_events.append({"case_id": case_id, "event": "not_run",
                                     "execution_started": False,
                                     "reason": value["reason"]})
            persist_progress()
            return None
        action_event_start = len(execution_events)
        execution_events.append({"case_id": case_id, "event": "started",
                                 "execution_started": True})
        failed = False
        try:
            value = thunk()
            observations[case_id] = value
            execution_events.append({"case_id": case_id, "event": "completed",
                                     "execution_started": True})
        except Exception as exc:
            failed = True
            prior_stage = next((event.get("stage") for event in reversed(
                                execution_events[action_event_start:])
                                if event.get("event") == "stage_observed"), case_id)
            value = {"adapter_error": f"{type(exc).__name__}: {exc}",
                     "not_run": False, "execution_started": True,
                     "failed_stage": prior_stage,
                     "proof_credit": False}
            diagnostic = getattr(exc, "parser_diagnostic", None)
            if isinstance(diagnostic, dict):
                value["parser_diagnostic"] = diagnostic
            persist_error = getattr(exc, "parser_diagnostic_persist_error", None)
            if isinstance(persist_error, str):
                value["parser_diagnostic_persist_error"] = persist_error
            observations[case_id] = value
            execution_events.append({"case_id": case_id, "event": "adapter_error",
                                     "execution_started": True,
                                     "stage": prior_stage,
                                     "error": value["adapter_error"]})
        persist_progress()
        return None if failed else value

    def stage_progress(stage_name: str):
        case_key = stage_name.split("-observed", 1)[0]
        if case_key.startswith("N-false31-"):
            target = positive_progress.get("false31", {}).get("body_cases", {}).get(
                case_key.removeprefix("N-false31-"), {})
        else:
            target = positive_progress.get("positive_cases", {}).get(case_key, {})
        raw = target.get("raw", {}) if isinstance(target, Mapping) else {}
        candidate = target.get("proof_candidate", {}) if isinstance(target, Mapping) else {}
        execution_events.append({"case_id": case_key, "event": "stage_observed",
                                 "stage": stage_name, "execution_started": True,
                                 "raw_first_causal_stage": raw.get("first_causal_stage")
                                    if isinstance(raw, Mapping) else None,
                                 "candidate_classification": candidate.get("classification")
                                    if isinstance(candidate, Mapping) else None,
                                 "verification_exit": raw.get("stages", {}).get(
                                     "verification", {}).get("exit")
                                    if isinstance(raw, Mapping) else None})
        persist_progress()

    observations: dict[str, Any] = {}
    errors: dict[str, str] = {}
    support_cache: dict[str, dict] = {}
    positive_progress: dict[str, Any] = {}
    helpers = None
    draft = None
    draft_succeeded = False
    try:
        execution_events.append({"case_id": "tool-reconstruction", "event": "started",
                                 "execution_started": True})
        helpers = load_pinned_helpers(Path(a.proof_root), profile)
        tool, tool_receipt = helpers["a1-tool.py"].reconstruct(
            a, c4, audit, driver, dict(manifest), profile)
        result.update(tool_path=str(tool), tool_receipt=tool_receipt,
                      tool_reconstructed=tool_receipt.get("proof_credit") is False)
        execution_events.append({"case_id": "tool-reconstruction", "event": "completed",
                                 "execution_started": True})
        persist_progress()
    except Exception as exc:
        result.update(tool_reconstructed=False,
                      run_error=f"{type(exc).__name__}: {exc}")
        result["first_missing_stage"] = "tool-reconstruction"
        execution_events.append({"case_id": "tool-reconstruction", "event": "adapter_error",
                                 "execution_started": True,
                                 "error": result["run_error"]})
        persist_progress()
    if native_target_mode and not result.get("tool_reconstructed"):
        reason = "bounded target routes not run because tool reconstruction failed"
        for case_id in CASE_ORDER:
            result["case_status"][case_id].update(status="NOT_RUN", reason=reason,
                                                   proof_credit=False,
                                                   matrix_gate_passed=False)
        result.update(
            classification="A1_NATIVE_P1_BOUNDED_TARGET_LIFECYCLE",
            target_scope={"mode": "native-p1-target",
                          "case_ids": [case for case in CASE_ORDER
                                       if case in NATIVE_TARGET_CASES],
                          "matrix_admission_invoked": False,
                          "matrix_admission_recorded": False,
                          "proof_credit": False},
            cases=result["case_status"],
            observed_rows=[{"case_id": case_id, "source_id": None, "unit_id": None,
                            "observation": None,
                            "status": result["case_status"][case_id]}
                           for case_id in CASE_ORDER],
            observed_row_count=0, matrix_complete=False,
            matrix_validation="bounded-target-only-not-admitted",
            admission_record_created=False, dispatch_ready=False,
            diagnostic_complete=False, evidence_complete=False,
            verification_accepted=False, profile_accepted=False,
            accepted=False, proof_verdict=None, proof_credit=False,
            first_missing_stage="tool-reconstruction",
            first_causal_stage="tool-reconstruction",
            first_blocker=next((event for event in execution_events
                                if event.get("event") == "adapter_error"), None),
            execution_events=execution_events, observation_details=observations)
        persist_progress()
        path = Path(a.evidence) / "diagnostic-audit.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_report_value_for_disk(
            _jsonable(result), AUTHORIZATION_PHASE), indent=2, sort_keys=True) + "\n")
        return result
    if helpers is not None and result.get("tool_reconstructed"):
        tool = Path(result["tool_path"])
        receipt = result["tool_receipt"]
        if profile.get("execution_mode") == "parser-preflight":
            def preflight():
                certificate_path, certificate = prepare_source_fixtures(a, helpers, ghost)
                stage_progress("source-constructor")
                return helpers["a1-focus-backend.py"].collect_focus(
                    a, c4, ghost, tool, dict(receipt), profile, dict(manifest),
                    certificate_path, Path(a.evidence) / "a1-fixtures" / "P0a", "P0a",
                    inventory_module=helpers["a1-compiler-inventory.py"],
                    call_binding_module=helpers["a1-call-binding.py"], parser_preflight=True)
            observed = action("P0a", preflight)
            result.update(classification="A1_PARSER_PREFLIGHT_ONLY", proof_attempted=False,
                          observation_details=_jsonable(observations), execution_events=execution_events,
                          parser_preflight_passed=(isinstance(observed, Mapping) and
                              observed.get("parser_preflight_passed") is True))
            for key, row in result["case_status"].items():
                row["reason"] = "parser preflight only; dependent proof/matrix not attempted"
            if isinstance(observed, Mapping):
                result["case_status"]["P0a"].update(status="INCONCLUSIVE",
                    reason=observed.get("adapter_error") or observed.get("reason") or observed.get("classification", "parser preflight only"))
            result["first_blocker"] = ((observed.get("first_blocker") if isinstance(observed, Mapping) else None) or
                next((event for event in execution_events if event.get("event") == "adapter_error"), None))
            persist_progress()
            target = Path(a.evidence) / "diagnostic-audit.json"
            target.write_text(json.dumps(_report_value_for_disk(
                _jsonable(result), AUTHORIZATION_PHASE), indent=2, sort_keys=True) + "\n")
            return result
        # These fixture identities are required by the complete positive
        # receipt's all-26 expected-input manifest. The bounded R10 path retains
        # this inexpensive identity closure but omits their verifier routes.
        legacy_prepared = action("prepare-legacy-fixtures", lambda:
            prepare_legacy_fixtures(a, driver, c4, ghost, dict(manifest)))
        if legacy_prepared is not None:
            positive_progress["legacy_inputs"] = legacy_prepared
        off_prepared = action("prepare-off-fixture", lambda:
            prepare_off_fixture(a, helpers["selected-proof.py"], driver,
                                ghost, dict(manifest), profile))
        if off_prepared is not None:
            positive_progress["off_input"] = off_prepared
        # The current positive lifecycle performs two real body/conformance
        # runs, then writes the exact-pair receipt, then runs its caller.
        draft = action("P0a", lambda:
            draft_positive_receipt_stage(
            a, c4, driver, ghost, c4, dict(manifest), profile,
                tool=tool, tool_receipt=receipt, profile_sha256=profile_sha,
                helpers=helpers, support_cache=support_cache,
                progress=positive_progress, progress_hook=stage_progress))
        draft_succeeded = (isinstance(draft, Mapping) and
                           draft.get("classification") ==
                           "DRAFT_POSITIVE_STAGE_SOURCE_REPORTED_ONLY")
        partial_positive_cases = (positive_progress.get("positive_cases")
                                  if isinstance(positive_progress, Mapping) else None)
        if isinstance(partial_positive_cases, Mapping):
            observations.update(partial_positive_cases)
        certificate_path_value = positive_progress.get("certificate_path")
        certificate = positive_progress.get("certificate")
        certificate_path = (Path(certificate_path_value)
                            if isinstance(certificate_path_value, str) else None)
        expected_cases_for_run = positive_progress.get("expected_case_ids", {})
        persist_progress()
        if draft_succeeded:
            observations["P0b"] = draft["positive_cases"]["P0b"]
            observations["P0c"] = draft["positive_cases"]["P0c"]
            result["case_status"]["P0a"] = _stage_result(
                "P0a", draft["positive_cases"]["P0a"])
            result["case_status"]["P0b"] = _stage_result("P0b", observations["P0b"])
            result["case_status"]["P0c"] = _stage_result("P0c", observations["P0c"])
            certificate_path = Path(draft["certificate_path"])
            certificate = json.loads(certificate_path.read_text())
            result["source_certificate_sha256"] = _sha(certificate_path)
            result["positive_receipt_path"] = draft["receipt_path"]
            result["expected_cases"] = draft["expected_case_ids"]
        if native_target_mode:
            # Execute the bounded R10 route and return before the full-matrix
            # consumers below. P1 always precedes its prepared caller controls
            # and the sole alpha-valid transport observation.
            target_context = _native_target_context(positive_progress)
            p0a = target_context["p0a"]
            p0a_raw = target_context["p0a_raw"]
            p0a_artifacts = target_context["artifacts"]
            normal_path = _available_artifact_path(p0a_artifacts, "normal-mir.txt")
            readonly_path = _available_artifact_path(p0a_artifacts, "readonly-mir.txt")
            controls = positive_progress.get("admission_controls", {})
            controls = controls if isinstance(controls, Mapping) else {}
            source_ready = (certificate_path is not None and
                            certificate_path.is_file() and
                            isinstance(certificate, Mapping) and
                            isinstance(certificate.get("cases"), Mapping) and
                            isinstance(certificate["cases"].get("P1"), Mapping))
            p1_action = (lambda: collect_p1_interface_case(
                a, c4, ghost, tool=tool, tool_receipt=receipt, profile=profile,
                manifest=dict(manifest), certificate_path=certificate_path,
                certificate=certificate, helpers=helpers,
                support_cache=support_cache)) if source_ready else None

            binding_actions = {}
            if (source_ready and normal_path is not None and readonly_path is not None and
                    normal_path.is_file() and readonly_path.is_file()):
                p1_source_path = (certificate_path.parent /
                                  certificate["cases"]["P1"]["source_file"])
                for control_id in ("N-binding", "N-region-swap"):
                    control = controls.get(control_id)
                    if not isinstance(control, Mapping) or not isinstance(control.get("path"), str):
                        continue
                    control_path = Path(control["path"])

                    def run_binding_control(case_id=control_id, path=control_path,
                                            expected_control=control):
                        observed = observe_admission_control(
                            case_id, call_binding=helpers["a1-call-binding.py"],
                            compiler_inventory=helpers["a1-compiler-inventory.py"],
                            normal=normal_path.read_text(encoding="utf-8"),
                            readonly=readonly_path.read_text(encoding="utf-8"),
                            certificate=certificate,
                            source=p1_source_path.read_text(encoding="utf-8"),
                            control_path=path)
                        observed_ids = observed.get("observed_input_ids")
                        observed.update(
                            input_identity_verified=(
                                observed.get("control_input_immutable") is True and
                                observed.get("control_input_sha256") ==
                                    expected_control.get("input_sha256") and
                                isinstance(observed_ids, Mapping) and
                                observed_ids.get("source_id") ==
                                    certificate["cases"]["P1"]["source_id"] and
                                observed_ids.get("unit_id") ==
                                    certificate["cases"]["P1"]["unit_id"]),
                            input_sha256=observed.get("control_input_sha256"),
                            source_id=expected_control.get("source_id"),
                            unit_id=expected_control.get("unit_id"))
                        return observed

                    binding_actions[control_id] = run_binding_control

            synthetic_inputs = positive_progress.get("synthetic_inputs", {})
            alpha_input = (synthetic_inputs.get("N-alpha-valid")
                           if isinstance(synthetic_inputs, Mapping) else None)
            alpha_messages = (alpha_input.get("messages")
                              if isinstance(alpha_input, Mapping) else None)
            alpha_action = None
            if (isinstance(alpha_messages, list) and len(alpha_messages) == 1 and
                    isinstance(alpha_messages[0], Mapping) and
                    alpha_messages[0].get("mutation") == "alpha_valid" and
                    normal_path is not None and normal_path.is_file() and
                    isinstance(p0a.get("structure"), Mapping) and
                    isinstance(alpha_messages[0].get("path"), str)):
                alpha_message = alpha_messages[0]
                alpha_root = Path(alpha_message["path"]).parent / "alpha_valid-run"

                def run_alpha_control():
                    raw = helpers["a1-synthetic-backend.py"].inject(
                        a, c4, helpers["a1-synthetic-inputs.py"], tool=tool,
                        fixture=Path(a.evidence) / "a1-fixtures" / "P1",
                        root=alpha_root, baseline_decoded=normal_path,
                        baseline_sha256=_sha(normal_path), mutation="alpha_valid",
                        impl_def_index=None,
                        env={**c4.clean_env(a, tool),
                             "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                             "SORT4_A1_PHASE_ID": PHASE,
                             "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                             "SORT4_A1_STAGE": "interface"})
                    actual = alpha_root / "synthetic-vfmir.txt"
                    actual_sha = _sha(actual) if actual.is_file() else None
                    if (actual_sha != alpha_message.get("sha256") or
                            raw.get("decoded_input_sha256") != alpha_message.get("sha256") or
                            raw.get("build_id") != env["CLOUD_BUILD_ID"] or
                            raw.get("console_sha256") != receipt.get("console_binary_sha256") or
                    raw.get("source_pair_sha256") !=
                                p0a_raw.get("source_pair_sha256")):
                        return {"transport": raw,
                                "classifier": {"classification":
                                    "INCONCLUSIVE_SYNTHETIC_INPUT_IDENTITY",
                                    "proof_credit": False},
                                "mutation": "alpha_valid", "input_sha256": actual_sha,
                                "proof_credit": False}
                    log_path = alpha_root / "synthetic-translator.log"
                    log_text = (log_path.read_text(errors="replace")
                                if log_path.is_file() else None)
                    classified = helpers["a1-synthetic-backend.py"].classify(
                        raw, mutation="alpha_valid", verifier_log=log_text)
                    return {"messages": [{"transport": raw,
                                          "classifier": classified,
                                          "mutation": "alpha_valid",
                                          "input_sha256": alpha_message["sha256"],
                                          "proof_credit": False}],
                            "source_id": alpha_input["source_id"],
                            "unit_id": alpha_input["unit_id"],
                            "proof_credit": False}

                alpha_action = run_alpha_control

            target_routes = _run_native_target_sequence(
                action, p1_action=p1_action, binding_actions=binding_actions,
                alpha_action=alpha_action)
            for case_id, observation in target_routes.items():
                if observation is not None:
                    observations[case_id] = observation
            persist_progress()

            expected_inputs = (draft.get("expected_case_ids", {})
                               if isinstance(draft, Mapping) else
                               positive_progress.get("expected_case_ids", {}))
            expected_inputs = (dict(expected_inputs)
                               if isinstance(expected_inputs, Mapping) else {})
            hashes = {"verifier": receipt["console_binary_sha256"],
                      "exporter": receipt["exporter_binary_sha256"],
                      "schema": receipt["final_schema_sha256"]}
            receipts = helpers["a1-summary-receipt.py"]
            target_run_pins = {
                "tool_id": receipts.tool_id(hashes), "profile_id": profile_sha,
                "proof_id": proof_sha, "infra_id": infra_sha,
                "target_id": receipts.TARGET}
            structure = p0a.get("structure")
            if not isinstance(structure, Mapping):
                p1_observation = observations.get("P1")
                structure = (p1_observation.get("structure")
                             if isinstance(p1_observation, Mapping) else {})
            bound = structure.get("bound_impls") if isinstance(structure, Mapping) else None
            bound = bound if isinstance(bound, Mapping) else {}
            target_inventory = {}
            for impl, row in bound.items():
                if isinstance(row, Mapping):
                    target_inventory[impl] = {
                        "compiler_impl_id": row.get("compiler_impl_id"),
                        "compiler_item_id": row.get("compiler_item_id")}
            target_records = _classify_native_target_rows(
                result["case_status"], result["observed_rows"], observations,
                NATIVE_TARGET_CASES, expected_inputs,
                helpers.get("a1-matrix-classifier.py"), target_run_pins,
                env.get("CLOUD_BUILD_ID"), target_inventory)
            result["cases"] = result["case_status"]
            result.update(
                classification="A1_NATIVE_P1_BOUNDED_TARGET_LIFECYCLE",
                target_scope={"mode": "native-p1-target",
                              "case_ids": [case for case in CASE_ORDER
                                           if case in NATIVE_TARGET_CASES],
                              "matrix_admission_invoked": False,
                              "matrix_admission_recorded": False,
                              "proof_credit": False},
                target_observed_records=target_records,
                observed_row_count=sum(
                    result["case_status"][case_id]["status"] == "INTENDED_CLASSIFIED"
                    for case_id in NATIVE_TARGET_CASES),
                matrix_complete=False, matrix_validation="bounded-target-only-not-admitted",
                admission_record_created=False, admission_state=None,
                dispatch_ready=False, diagnostic_complete=False,
                evidence_complete=False, verification_accepted=False,
                profile_accepted=False, accepted=False, proof_verdict=None,
                proof_credit=False,
                first_missing_stage=next(
                    (case_id for case_id in CASE_ORDER
                     if case_id in NATIVE_TARGET_CASES and
                     result["case_status"][case_id]["status"] != "INTENDED_CLASSIFIED"),
                    None))
            first_blocker = next((event for event in execution_events
                                  if event.get("event") == "adapter_error"), None)
            result["first_blocker"] = first_blocker
            result["first_causal_stage"] = (
                first_blocker.get("stage") if isinstance(first_blocker, Mapping) else None)
            result["execution_events"] = execution_events
            result["observation_details"] = observations
            persist_progress()
            path = Path(a.evidence) / "diagnostic-audit.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(_report_value_for_disk(
                _jsonable(result), AUTHORIZATION_PHASE), indent=2, sort_keys=True) + "\n")
            return result
        if certificate is not None and certificate_path is not None:
            positive_cases = positive_progress.get("positive_cases", {})
            p0a_partial = positive_cases.get("P0a", {})
            partial_artifacts = p0a_partial.get("raw", {}).get("artifacts", {})
            partial_normal = _available_artifact_path(partial_artifacts, "normal-mir.txt")
            partial_readonly = _available_artifact_path(partial_artifacts, "readonly-mir.txt")
            # Any independent full-unit/interface, negative-body, admission,
            # legacy-regression, and OFF route proceeds even when a positive
            # body or caller gate fails. Only receipt-dependent caller rows
            # require the complete positive lifecycle.
            if "legacy_inputs" not in positive_progress:
                legacy_prepared = action("prepare-legacy-fixtures", lambda:
                    prepare_legacy_fixtures(a, driver, c4, ghost, dict(manifest)))
                if legacy_prepared is not None:
                    positive_progress["legacy_inputs"] = legacy_prepared
            if "off_input" not in positive_progress:
                off_prepared = action("prepare-off-fixture", lambda:
                    prepare_off_fixture(
                        a, helpers["selected-proof.py"], driver, ghost,
                        dict(manifest), profile))
                if off_prepared is not None:
                    positive_progress["off_input"] = off_prepared
            if ("synthetic_inputs" not in positive_progress and
                    partial_normal is not None and
                    isinstance(p0a_partial.get("structure"), Mapping)):
                decoded_path = partial_normal
                prepared = action("prepare-synthetic-inputs", lambda:
                    prepare_synthetic_inputs(
                        a, helpers["a1-synthetic-inputs.py"],
                        baseline_decoded=decoded_path,
                        inventory=p0a_partial["structure"]["inventory"],
                        certificate=certificate))
                if prepared is not None:
                    positive_progress["synthetic_inputs"] = prepared
            if ("admission_controls" not in positive_progress and
                    partial_normal is not None and partial_readonly is not None):
                prepared_controls = action("prepare-admission-controls", lambda:
                    prepare_admission_control_inputs(
                        a, helpers["a1-call-binding.py"],
                        helpers["a1-compiler-inventory.py"],
                        certificate=certificate, certificate_path=certificate_path,
                        normal_decoded=partial_normal,
                        readonly_decoded=partial_readonly))
                if prepared_controls is not None:
                    positive_progress["admission_controls"] = prepared_controls
            expected_cases = positive_progress.get("expected_case_ids")
            if (not isinstance(expected_cases, Mapping) and
                    isinstance(positive_progress.get("synthetic_inputs"), Mapping) and
                    isinstance(positive_progress.get("admission_controls"), Mapping) and
                    isinstance(positive_progress.get("legacy_inputs"), Mapping) and
                    isinstance(positive_progress.get("off_input"), Mapping) and
                    isinstance(p0a_partial.get("structure"), Mapping)):
                expected_cases = action("materialize-matrix-identities", lambda:
                    materialize_expected_cases(
                        helpers["a1-contract-admission.py"], certificate,
                        positive_progress["synthetic_inputs"],
                        positive_progress["legacy_inputs"],
                        positive_progress["off_input"],
                        positive_progress["admission_controls"],
                        p0a_partial["structure"]["bound_impls"]))
                if expected_cases is not None:
                    positive_progress["expected_case_ids"] = expected_cases
                    expected_cases_for_run = expected_cases
            observations.update(positive_cases)
            # Transport controls are invoked against the exact paired
            # compiler-derived decoded message. A classifier must inspect the
            # actual current translator output, never mutation metadata.
            first = positive_cases.get("P0a", {})
            first_artifacts = first.get("raw", {}).get("artifacts", {})
            decoded = _available_artifact_path(first_artifacts, "normal-mir.txt")
            first_structure = first.get("structure")
            first_structure = first_structure if isinstance(first_structure, Mapping) else {}
            synthetic_inputs = positive_progress.get("synthetic_inputs", {})
            mutator = helpers["a1-synthetic-inputs.py"]
            backend = helpers["a1-synthetic-backend.py"]
            impls = [row for row in first_structure.get("inventory", {})
                     .get("inventory", {}).get("impls", [])
                     if row.get("impl") == "default16"]
            impl_index = impls[0]["impl_def_index"] if len(impls) == 1 else None
            for case_id, inputs in (synthetic_inputs.items() if decoded is not None else ()):
                for message in inputs["messages"]:
                    mutation = message["mutation"]
                    root = Path(message["path"]).parent / (mutation + "-run")
                    raw = action(case_id + "/" + mutation, lambda m=mutation, r=root:
                        backend.inject(
                            a, c4, mutator, tool=tool,
                            fixture=Path(a.evidence) / "a1-fixtures" / "P1",
                            root=r, baseline_decoded=decoded,
                            baseline_sha256=_sha(decoded), mutation=m,
                            impl_def_index=impl_index if m == "duplicate_impl_method" else None,
                            env={**c4.clean_env(a, tool),
                                 "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                                 "SORT4_A1_PHASE_ID": PHASE,
                                 "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                                 "SORT4_A1_STAGE": "interface"}))
                    if raw is not None:
                        decoded_actual = Path(root) / "synthetic-vfmir.txt"
                        if (_sha(decoded_actual) != message["sha256"] or
                                raw.get("decoded_input_sha256") != message["sha256"] or
                                raw.get("build_id") != env["CLOUD_BUILD_ID"] or
                                raw.get("console_sha256") != receipt.get("console_binary_sha256") or
                                raw.get("source_pair_sha256") != first.get("raw", {}).get("source_pair_sha256")):
                            observations[case_id + "/" + mutation] = {
                                "transport": raw,
                                "classifier": {"classification":
                                    "INCONCLUSIVE_SYNTHETIC_INPUT_IDENTITY",
                                    "proof_credit": False},
                                "mutation": mutation,
                                "input_sha256": _sha(decoded_actual),
                                "proof_credit": False}
                            persist_progress()
                            continue
                        log_path = Path(root) / "synthetic-translator.log"
                        log_text = log_path.read_text(errors="replace") if log_path.is_file() else None
                        classified = backend.classify(raw, mutation=message["mutation"],
                                                      verifier_log=log_text)
                        observations[case_id + "/" + mutation] = {
                            "transport": raw, "classifier": classified,
                            "mutation": mutation,
                            "input_sha256": message["sha256"],
                            "proof_credit": False}
                        persist_progress()
                values = [observations.get(case_id + "/" + row["mutation"])
                          for row in inputs["messages"]]
                identities_match = all(
                    isinstance(value, Mapping) and
                    value.get("transport", {}).get("decoded_input_sha256") ==
                    row.get("sha256") for value, row in zip(values, inputs["messages"]))
                observations[case_id] = {
                    "messages": values,
                    "source_id": inputs.get("source_id") if identities_match else None,
                    "unit_id": inputs.get("unit_id") if identities_match else None,
                    "proof_credit": False}
                persist_progress()

            # Full-interface, dispatch, and implementation negatives have no
            # dependency on the common caller receipt. Preserve their own source
            # pairs and collect them even when P0a/P0b did not pass.
            p1 = action("P1", lambda:
                collect_p1_interface_case(
                    a, c4, ghost, tool=tool, tool_receipt=receipt, profile=profile,
                    manifest=dict(manifest), certificate_path=certificate_path,
                    certificate=certificate, helpers=helpers,
                    support_cache=support_cache))
            dispatch = action("P-dispatch", lambda:
                collect_source_case(
                    a, c4, ghost, tool=tool, tool_receipt=dict(receipt),
                    profile=profile, manifest=dict(manifest),
                    certificate_path=certificate_path, certificate=certificate,
                    helpers=helpers, case_id="P-dispatch",
                    support_cache=support_cache))
            if dispatch is not None:
                source_sha = certificate["cases"]["P-dispatch"]["generated_source_sha256"]
                observations["P-dispatch"] = {
                    **dispatch, "dispatch_classifier": classify_dispatch_observation(
                        dispatch.get("raw", {}), expected_source_sha256=source_sha)}
                persist_progress()
            p0a_native = first_structure.get("threshold_posts", {}).get("native")
            for case_id in ("N-default-contract", "N-freeze-contract"):
                action(case_id, lambda c=case_id:
                    collect_source_case(
                        a, c4, ghost, tool=tool, tool_receipt=dict(receipt),
                        profile=profile, manifest=dict(manifest),
                        certificate_path=certificate_path, certificate=certificate,
                        helpers=helpers, case_id=c, native_baseline=p0a_native,
                        support_cache=support_cache))

            # False31 alone depends on two successful same-pair threshold body
            # attestations and its own receipt.
            if isinstance(certificate, Mapping) and isinstance(p0a_native, Mapping):
                false31 = action("N-false31", lambda:
                    draft_false31_pair_stage(
                        a, c4, ghost, tool=tool, tool_receipt=receipt,
                        profile=profile, manifest=dict(manifest),
                        certificate_path=certificate_path, certificate=certificate,
                        source_package=certificate_path.parent,
                        positive_native_baseline=p0a_native,
                        expected_cases=(expected_cases_for_run
                                        if isinstance(expected_cases_for_run, Mapping)
                                        else None), helpers=helpers,
                        profile_sha256=profile_sha, support_cache=support_cache,
                        progress=positive_progress.setdefault("false31", {}),
                        progress_hook=stage_progress))
                if false31 is not None:
                    result["case_status"]["N-false31"] = _stage_result("N-false31", false31)
                elif "caller_case" not in positive_progress.get("false31", {}):
                    observations["N-false31"] = {
                        "not_run": True, "execution_started": False,
                        "reason": "false31 caller receipt prerequisites were not established",
                        "partial_body_cases": positive_progress.get("false31", {}).get(
                            "body_cases", {}), "proof_credit": False}
                    persist_progress()

            # Wrong source/caller/region claims use the exact P0a paired MIR
            # inventory when available. Otherwise their constructor or
            # validator failure remains inconclusive while other rows continue.
            controls = positive_progress.get("admission_controls", {})
            if isinstance(controls, Mapping) and isinstance(first_artifacts, Mapping):
                normal_path = _available_artifact_path(first_artifacts, "normal-mir.txt")
                readonly_path = _available_artifact_path(first_artifacts, "readonly-mir.txt")
                if normal_path is not None and readonly_path is not None:
                    source_path = certificate_path.parent / certificate["cases"]["P1"]["source_file"]
                    for control_id in ("N-source", "N-binding", "N-region-swap"):
                        if control_id not in controls:
                            continue
                        path = Path(controls[control_id]["path"])
                        observed = action(control_id, lambda c=control_id, p=path:
                            observe_admission_control(
                                c, call_binding=helpers["a1-call-binding.py"],
                                compiler_inventory=helpers["a1-compiler-inventory.py"],
                                normal=normal_path.read_text(encoding="utf-8"),
                                readonly=readonly_path.read_text(encoding="utf-8"),
                                certificate=certificate,
                                source=source_path.read_text(encoding="utf-8"),
                                control_path=p))
                        if observed is not None:
                            expected_control = controls[control_id]
                            observed_ids = observed.get("observed_input_ids")
                            observed.update(
                                input_identity_verified=(
                                    observed.get("control_input_immutable") is True and
                                    observed.get("control_input_sha256") ==
                                    expected_control["input_sha256"] and
                                    isinstance(observed_ids, Mapping) and
                                    observed_ids.get("source_id") ==
                                        certificate["cases"]["P1"]["source_id"] and
                                    observed_ids.get("unit_id") ==
                                        certificate["cases"]["P1"]["unit_id"]),
                                input_sha256=observed.get("control_input_sha256"),
                                source_id=expected_control["source_id"],
                                unit_id=expected_control["unit_id"])
                            observations[control_id] = observed
                            persist_progress()

            # The forced legacy redirect is a fresh caller run and therefore
            # remains dependent on successful P0a/P0b receipt publication.
            receipt_value = positive_progress.get("positive_receipt_path")
            if (isinstance(receipt_value, str) and Path(receipt_value).is_file() and
                    "N-clause-redirect" in controls):
                control_path = Path(controls["N-clause-redirect"]["path"])
                def run_redirect_control():
                    control_doc = json.loads(control_path.read_text(encoding="utf-8"))
                    _need(control_doc == {
                        "SORT4_A1_FORCE_LEGACY_REDIRECT": "1",
                        "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                        "source_pair_sha256": certificate["cases"]["P0c"]
                            ["generated_source_sha256"]},
                        "exact prepared redirect configuration required")
                    observed_redirect = collect_source_case(
                        a, c4, ghost, tool=tool, tool_receipt=dict(receipt),
                        profile=profile, manifest=dict(manifest),
                        certificate_path=certificate_path, certificate=certificate,
                        helpers=helpers, case_id="P0c", evidence_id="N-clause-redirect",
                        control_env={"SORT4_A1_FORCE_LEGACY_REDIRECT":
                                     control_doc["SORT4_A1_FORCE_LEGACY_REDIRECT"]},
                        support_cache=support_cache)
                    observed_redirect["control_input_sha256"] = _sha(control_path)
                    return observed_redirect
                redirect = action("N-clause-redirect", run_redirect_control)
                if redirect is not None:
                    raw_redirect = redirect.get("raw", {})
                    redirect_class = classify_redirect_observation(
                        raw_redirect,
                        expected_source_sha256=certificate["cases"]["P0c"]
                            ["generated_source_sha256"])
                    control_sha = _sha(control_path)
                    control_doc = json.loads(control_path.read_text())
                    source_identity = redirect.get("observed_input_ids")
                    raw_pair = raw_redirect.get("source_pair_sha256", {})
                    observations["N-clause-redirect"] = {
                        "raw": raw_redirect, "classifier": redirect_class,
                        "input_identity_verified": (
                            redirect.get("control_input_sha256") == control_sha and
                            control_sha == controls["N-clause-redirect"]["input_sha256"] and
                            control_doc.get("SORT4_A1_FORCE_LEGACY_REDIRECT") == "1" and
                            control_doc.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
                            control_doc.get("source_pair_sha256") == raw_pair.get("verified") and
                            isinstance(source_identity, Mapping) and
                            source_identity.get("source_id") == certificate["cases"]["P0c"]["source_id"] and
                            source_identity.get("unit_id") == certificate["cases"]["P0c"]["unit_id"]),
                        "input_sha256": control_sha,
                        "source_id": controls["N-clause-redirect"]["source_id"],
                        "unit_id": controls["N-clause-redirect"]["unit_id"],
                        "proof_credit": False}
                    persist_progress()
        # All R1-R7 are fresh isolated fixtures and actual driver verifier
        # invocations on the one reconstructed final tool.
        legacy = (draft.get("legacy_inputs", {}) if draft_succeeded else
                  positive_progress.get("legacy_inputs", {}))
        if set(legacy) == set(LEGACY_CONTROL):
            legacy_env = c4.clean_env(a, tool)
            for case_id, driver_name in LEGACY_CONTROL.items():
                item = legacy[case_id]
                fixture = Path(item["fixture"])
                observed = action(case_id, lambda n=driver_name, f=fixture:
                    driver.verify_one(a, c4, tool, legacy_env, f, n))
                if observed is not None:
                    verified = fixture / "verified/lib.rs"
                    original = fixture / "original/lib.rs"
                    observed_pair = {"verified": _sha(verified),
                                     "original": _sha(original)}
                    if (observed_pair == {
                            "verified": item["certificate"]["verified_sha256"],
                            "original": item["certificate"]["original_sha256"]} and
                            observed.get("source_pair_immutable") is True):
                        observed.update(
                            input_identity_verified=True,
                            source_id=item["source_id"], unit_id=item["unit_id"],
                            source_pair_sha256=observed_pair)
                    else:
                        observed.update(input_identity_verified=False,
                                        observed_input_ids=None,
                                        source_pair_sha256=observed_pair)
                    result["case_status"][case_id] = _stage_result(case_id, observed)
        # OFF is an actual final-tool run with opt-in absent. Its result is
        # preserved as observed stage data; only the exact duplicate-parameter
        # frontend diagnostic is classified as baseline behavior.
        off_input = (draft.get("off_input") if draft_succeeded else
                     positive_progress.get("off_input"))
        off = (action("OFF", lambda:
            _run_off_observation(a, c4, tool, off_input,
                                 helpers["selected-proof.py"]))
               if isinstance(off_input, Mapping) else None)
        if off is not None:
            result["case_status"]["OFF"] = _stage_result("OFF", off)
    # Interpret each row only after its route-specific observations exist.
    expected_inputs = (draft.get("expected_case_ids", {}) if draft_succeeded else
                       positive_progress.get("expected_case_ids", {}))
    expected_inputs = dict(expected_inputs) if isinstance(expected_inputs, Mapping) else {}
    certificate = positive_progress.get("certificate")
    synthetic_inputs = positive_progress.get("synthetic_inputs", {})
    legacy_inputs = positive_progress.get("legacy_inputs", {})
    controls = positive_progress.get("admission_controls", {})
    off_input = positive_progress.get("off_input")
    admission = helpers.get("a1-contract-admission.py") if helpers else None
    if admission is not None:
        for case_id in CASE_ORDER:
            if case_id in expected_inputs:
                continue
            if case_id in SOURCE_CASE:
                source_row = (certificate.get("cases", {}).get(SOURCE_CASE[case_id], {})
                              if isinstance(certificate, Mapping) else {})
            elif case_id in SYNTHETIC_INPUT_PLAN:
                source_row = synthetic_inputs.get(case_id, {})
            elif case_id in LEGACY_CONTROL:
                source_row = legacy_inputs.get(case_id, {})
            elif case_id == "OFF":
                source_row = off_input if isinstance(off_input, Mapping) else {}
            else:
                source_row = controls.get(case_id, {})
            if not (isinstance(source_row, Mapping) and
                    isinstance(source_row.get("source_id"), str) and
                    isinstance(source_row.get("unit_id"), str)):
                continue
            stage, predicate, location, outcome, classification = admission.MATRIX[case_id]
            expected = {"source_id": source_row["source_id"],
                        "unit_id": source_row["unit_id"],
                        "stage": stage, "predicate": predicate,
                        "location": location, "outcome": outcome,
                        "classification": classification}
            if case_id in SYNTHETIC_INPUT_PLAN:
                messages = source_row.get("messages", ())
                if len(messages) != len(SYNTHETIC_INPUT_PLAN[case_id]):
                    continue
                expected["synthetic_input_sha256"] = tuple(row["sha256"] for row in messages)
            if case_id in controls:
                expected["control_input_sha256"] = source_row.get("input_sha256")
            expected_inputs[case_id] = expected
    expected_inventory = {}
    run_pins = None
    if helpers is not None and result.get("tool_reconstructed"):
        hashes = {"verifier": receipt["console_binary_sha256"],
                  "exporter": receipt["exporter_binary_sha256"],
                  "schema": receipt["final_schema_sha256"]}
        receipts = helpers["a1-summary-receipt.py"]
        run_pins = {"tool_id": receipts.tool_id(hashes),
                    "profile_id": profile_sha, "proof_id": proof_sha,
                    "infra_id": infra_sha, "target_id": receipts.TARGET}
        p0a = observations.get("P0a", {})
        p1 = observations.get("P1", {})
        identity_source = (p0a if isinstance(p0a, Mapping) and
                           isinstance(p0a.get("structure"), Mapping) else p1)
        identity_structure = (identity_source.get("structure")
                              if isinstance(identity_source, Mapping) else None)
        bound = (identity_structure.get("bound_impls", {})
                 if isinstance(identity_structure, Mapping) else {})
        expected_inventory = {
            impl: {"compiler_impl_id": row.get("compiler_impl_id"),
                   "compiler_item_id": row.get("compiler_item_id")}
            for impl, row in bound.items() if isinstance(row, Mapping)}

    records = []
    classifier = helpers.get("a1-matrix-classifier.py") if helpers else None
    for case_id in CASE_ORDER:
        observation = observations.get(case_id)
        if (isinstance(observation, Mapping) and
                observation.get("not_run") is True and
                observation.get("execution_started") is False):
            classified = {"case_id": case_id, "status": "NOT_RUN",
                          "matrix_gate_passed": False, "record": None,
                          "reason": observation.get("reason"),
                          "proof_credit": False}
        elif (case_id in expected_inputs and classifier is not None and
                run_pins is not None and env.get("CLOUD_BUILD_ID")):
            classified = classifier.classify_case(
                case_id, observation, expected_input=expected_inputs[case_id],
                run_pins=run_pins, build_id=env["CLOUD_BUILD_ID"],
                expected_inventory=expected_inventory)
        else:
            classified = {"case_id": case_id,
                          "status": "INCONCLUSIVE" if observation is not None else "NOT_RUN",
                          "matrix_gate_passed": False, "record": None,
                          "reason": "expected input identity or run pins unavailable",
                          "proof_credit": False}
        result["case_status"][case_id] = {
            "status": classified["status"],
            "observed_stage": (classified.get("record") or {}).get("stage"),
            "observed_outcome": classified.get("observed_classification"),
            "reason": classified.get("reason"),
            "matrix_gate_passed": classified.get("matrix_gate_passed") is True,
            "proof_credit": False,
            "provenance": classified.get("provenance")}
        if classified.get("record") is not None:
            records.append(classified["record"])
        persist_progress()

    result["cases"] = result["case_status"]
    result.update(diagnostic_complete=False, evidence_complete=False,
                  verification_accepted=False, profile_accepted=False,
                  accepted=False, proof_verdict=None)
    def actual_id(case_id, key):
        observation = observations.get(case_id)
        if not isinstance(observation, Mapping):
            return None
        raw = observation.get("raw")
        if isinstance(raw, Mapping) and isinstance(raw.get(key), str):
            return raw[key]
        return observation.get(key) if isinstance(observation.get(key), str) else None

    result["observed_rows"] = [
        {"case_id": case_id, "source_id": actual_id(case_id, "source_id"),
         "unit_id": actual_id(case_id, "unit_id"),
         "observation": observations.get(case_id),
         "status": result["case_status"][case_id]}
        for case_id in CASE_ORDER]
    result["observed_row_count"] = sum(
        row["status"] == "INTENDED_CLASSIFIED" for row in result["case_status"].values())
    all_classified = (len(records) == len(CASE_ORDER) and
                      all(row["status"] == "INTENDED_CLASSIFIED"
                          for row in result["case_status"].values()))
    admission_gate = (draft.get("admission_gate") if draft_succeeded else
                      positive_progress.get("admission_gate"))
    if all_classified and admission_gate is not None:
        try:
            admission_gate.record_matrix(records)
            result["matrix_complete"] = True
            result["admission_record_created"] = True
            result["admission_state"] = admission_gate.state()
            result["matrix_validation"] = "all-26-runner-observations-validated"
        except Exception as exc:
            result["matrix_complete"] = False
            result["admission_record_created"] = False
            result["matrix_validation_error"] = f"{type(exc).__name__}: {exc}"
    else:
        result["matrix_complete"] = False
        result["admission_record_created"] = False
        result["matrix_validation"] = "incomplete-or-inconclusive-observations"
    result["dispatch_ready"] = False
    result["first_missing_stage"] = next(
        (case_id for case_id in CASE_ORDER
         if result["case_status"][case_id]["status"] != "INTENDED_CLASSIFIED"), None)
    first_blocker = next((event for event in execution_events
                          if event.get("event") == "adapter_error"), None)
    causal = None
    if first_blocker is None:
        # Scientific adapters can finish normally while their actual output
        # fails the intended predicate. Preserve that failed row without
        # presenting plan order as causal order.
        failed_case = next((case_id for case_id in CASE_ORDER
                            if result["case_status"][case_id]["status"] !=
                            "INTENDED_CLASSIFIED"), None)
        if failed_case is not None:
            observation = observations.get(failed_case, {})
            raw = observation.get("raw", {}) if isinstance(observation, Mapping) else {}
            actual_stage = (raw.get("first_causal_stage")
                            if isinstance(raw, Mapping) else None)
            reason = result["case_status"][failed_case].get("reason")
            first_blocker = {
                "case_id": failed_case,
                "event": "classifier_failure",
                "execution_started": (failed_case in observations and
                                       observation.get("execution_started", True)
                                       if isinstance(observation, Mapping) else False),
                "reason": reason or "mandatory row did not reach intended classification",
                "causal_stage": actual_stage or "UNESTABLISHED",
            }
            causal = actual_stage or "UNESTABLISHED"
    if first_blocker is not None:
        case_id = first_blocker.get("case_id")
        if case_id == "tool-reconstruction":
            causal = "tool-reconstruction"
        else:
            observation = observations.get(case_id, {})
            nested_stage = str(first_blocker.get("stage", ""))
            target_case = None
            if nested_stage.startswith("N-false31-"):
                target_case = nested_stage.removeprefix("N-false31-").removesuffix("-observed")
                observation = positive_progress.get("false31", {}).get(
                    "body_cases", {}).get(target_case, observation)
            elif nested_stage in {"P0a-observed", "P0b-observed", "P0c-observed"}:
                target_case = nested_stage.removesuffix("-observed")
                observation = positive_progress.get("positive_cases", {}).get(target_case, observation)
            elif case_id == "P0a":
                observation = positive_progress.get("positive_cases", {}).get("P0a", observation)
            raw = observation.get("raw", {}) if isinstance(observation, Mapping) else {}
            candidate = observation.get("proof_candidate", {}) if isinstance(observation, Mapping) else {}
            error_context = candidate.get("error_context", {}) if isinstance(candidate, Mapping) else {}
            causal = ((raw.get("first_causal_stage") if isinstance(raw, Mapping) else None) or
                      (candidate.get("first_causal_stage") if isinstance(candidate, Mapping) else None) or
                      (error_context.get("stage") if isinstance(error_context, Mapping) else None) or
                      "UNESTABLISHED")
    result["first_causal_stage"] = causal
    result["first_blocker"] = first_blocker
    all_rows_classified = all(row["status"] == "INTENDED_CLASSIFIED"
                              for row in result["case_status"].values())
    result["diagnostic_complete"] = bool(all_rows_classified and result["matrix_complete"])
    result["execution_events"] = execution_events
    result["observation_details"] = observations
    path = Path(a.evidence) / "diagnostic-audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_report_value_for_disk(
        _jsonable(result), AUTHORIZATION_PHASE), indent=2, sort_keys=True) + "\n")
    return result
