#!/usr/bin/env python3
"""Cloud-only slice binding fixtures on the single H native integration tool.

Source preparation runs before package installation. Verification only consumes
that immutable preparation; it never reconstructs a historical tool profile.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import lzma
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace


LANE = "verifast-slice-binding-integration"
PROFILE = "verifast-slice-as-mut-ptr-native-c3-20261011-i"
CALLER = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
SLICE_CASES = ("canonical-generic", "canonical-mu", "consumer-positive",
               "consumer-wrong-pointer", "consumer-missing-raw-rights",
               "consumer-mu-cast-no-initialized-T")
REQUIRED_MANIFEST_KEYS = frozenset((
    "tool_c4_patch_sha256", "selector_integration_patch_sha256",
    "composition_patch_sha256", "compressed_delivery",
    "source_modules_pack_sha256", "source_modules_provenance_commit",
    "source_modules_count", "effective_hashes", "stock_effective_hashes",
    "selector_source_sha256", "c4_source_sha256", "producer_final_ast_sha256",
    "producer_typed_location_endpoints", "inherited_c4_controls",
    "outer_scope_capture_pins", "native_zst_tool_patches",
    "slice_binding_source_manifest", "slice_source_delivery",
    "native_zst_profile", "profile_id", "slice_binding_profile",
))
OUTER_SCOPE_PINS = {
    "normal": {
        "body_sha256": ["967b297f9044c1c9ba81b6e5e469c5ef6d013e33b4f17cf8134138fd4fe065c5"],
        "whole_decoded_mir_sha256": "5a2e53473c99720b20f5186469c91c49c562cd8b89c7f9d9160589979e66d220",
    },
    "readonly": {
        "body_sha256": ["1fa420e27a2c8e7e9983a347b3958a6926ca52abc762ee3c8d3c9347fd90e49e"],
        "whole_decoded_mir_sha256": "4d8512c3d899f543c4e4808215151708fe1aa417886a2ec04bd1fa531b460b57",
    },
}
BOOL_SUPPLEMENT = {
    "baseline_build_id": "5cb5b5d3-e4d6-4185-9234-f3a89e79829e",
    "baseline_proof_sha": "7f5f88b54d9d631fee24ec84ab868d42c2f174b3",
    "baseline_manifest_sha256": "7882e54599974e39262ef2e55c8ae632eb0b5434b34c1698c5fc2de87e5a1a0e",
    "baseline_archive_sha256": "a368cccb8b725e0ad8592fae4ee705913c84e8319230c907c33ed4919ecbd536",
    "baseline_console_sha256": "9fc7c65b438e41ad014a08fe2f8b3e8f9b296866e010d8c423468b21565b3fd5",
    "required_regression_targets": [
        "selector_cleanup_off", "cleanup_partial_optin",
        "composition_admission_mutants", "theorem_controls",
        "inherited_baseline_inputs", "strict_lifetime",
        "pointer_value_pointee_rights", "mdnew_retained_fix",
    ],
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError("SLICE-BINDING: " + message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def load(path: Path, label: str):
    spec = importlib.util.spec_from_file_location(label, path)
    need(spec is not None and spec.loader is not None, "module absent: " + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[label] = module
    spec.loader.exec_module(module)
    return module


def context(a) -> tuple[dict, dict]:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == LANE and not os.environ.get("GITHUB_ACTIONS"),
         "Cloud lane identity")
    for name in ("proof_root", "cloud_dir", "evidence", "manifest"):
        need(str(getattr(a, name).resolve()).startswith("/workspace/"),
             name + " outside workspace")
    need(subprocess.check_output(["git", "-C", str(a.proof_root), "rev-parse", "HEAD"],
                                 text=True).strip() == os.environ.get("PROOF_SHA"),
         "proof SHA differs")
    data = json.loads(a.manifest.read_text())
    need(REQUIRED_MANIFEST_KEYS <= set(data),
         "incomplete integration manifest: " +
         ", ".join(sorted(REQUIRED_MANIFEST_KEYS - set(data))))
    need(data["outer_scope_capture_pins"] == OUTER_SCOPE_PINS,
         "reviewed outer normal/readonly capture pins")
    if "bool_required_gates_supplement" in data:
        need(data["bool_required_gates_supplement"] == BOOL_SUPPLEMENT,
             "Bool-only supplement identity and target set")
    need(data.get("slice_binding_profile") == PROFILE and
         data.get("profile_accepted") is False and
         data.get("actual_caller_proved") is False and
         data.get("callable_summary") is False and
         data["effective_hashes"]["src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"] ==
         "a392cf28f72a8ae9c54faabf2454ddaff07757b6f0f98548ed72a7b8daab9ba3",
         "experimental profile identity")
    source_path = a.proof_root / data["slice_binding_source_manifest"]
    source = json.loads(source_path.read_text())
    need(source.get("profile_accepted") is False and
         source.get("as_mut_ptr_patch_sha256") ==
         "f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916",
         "copied candidate source identity")
    return data, source


def supplement_check(a, data: dict) -> None:
    """Seal the rebuilt console before any supplemental verifier invocation."""
    need(data.get("bool_required_gates_supplement") == BOOL_SUPPLEMENT,
         "Bool-only supplement was not selected")
    effective = json.loads((a.evidence / "effective-hashes.json").read_text())
    need(effective.get("exact") is True and
         effective.get("actual", {}).get("bin/verifast") ==
         BOOL_SUPPLEMENT["baseline_console_sha256"] and
         effective.get("expected") == data["effective_hashes"] and
         (a.evidence / "effective-console-sha256.txt").read_text().strip() ==
         BOOL_SUPPLEMENT["baseline_console_sha256"] and
         sha(a.tool_home / "bin/verifast") == BOOL_SUPPLEMENT["baseline_console_sha256"],
         "supplement console differs from primary Build or seven effective pins")


def supplement_record(a, data: dict) -> None:
    """Link only this Build's integration diagnostics to the primary Build."""
    supplement_check(a, data)
    result_path = a.evidence / "result.json"
    need(result_path.is_file(), "supplement integration result absent")
    result = json.loads(result_path.read_text())
    need(result.get("accepted") is False and
         result.get("verification_accepted") is False,
         "supplement result must remain unaccepted")
    regressions = result.get("stages", {}).get("regressions", {})
    targets = regressions.get("targets", {}) if isinstance(regressions, dict) else {}
    expected = set(BOOL_SUPPLEMENT["required_regression_targets"])
    actual = set(targets) if isinstance(targets, dict) else set()
    outer = targets.get("strict_lifetime", {}).get("outer_type_escape", {}) if isinstance(targets, dict) else {}
    row = {
        "classification": "BOOL_REQUIRED_GATES_SUPPLEMENT_RAW_REVIEW_PENDING"
                          if actual == expected and outer.get("intended_site_observed") is True
                          else "BOOL_REQUIRED_GATES_SUPPLEMENT_INCOMPLETE",
        "supplemental_only": True, "profile": PROFILE,
        "baseline_build_id": BOOL_SUPPLEMENT["baseline_build_id"],
        "baseline_proof_sha": BOOL_SUPPLEMENT["baseline_proof_sha"],
        "baseline_manifest_sha256": BOOL_SUPPLEMENT["baseline_manifest_sha256"],
        "baseline_archive_sha256": BOOL_SUPPLEMENT["baseline_archive_sha256"],
        "same_console_sha256": BOOL_SUPPLEMENT["baseline_console_sha256"],
        "required_regression_targets": BOOL_SUPPLEMENT["required_regression_targets"],
        "targets_present": actual == expected,
        "missing_targets": sorted(expected - actual),
        "outer_bool_machine_observed": (
            outer.get("intended_site_observed") is True and
            outer.get("positive_audit", {}).get("classification") ==
            "PASS_POSITIVE_LOCAL_HRTB_CLOSURE"),
        "regression_completion_gates": regressions.get("completion_gates"),
        "integration_result_sha256": sha(result_path),
        "integration_diagnostic_complete": result.get("diagnostic_complete") is True,
        "raw_review_pending": True, "proof_credit": False,
        "accepted": False, "verification_accepted": False,
        "profile_accepted": False,
    }
    save(a.evidence / "bool-supplement.json", row)
    need(actual == expected and row["outer_bool_machine_observed"],
         "supplement missing required targets or outer Bool machine observation")


def materialize_slice(a, data: dict, source: dict) -> None:
    """Restore the exact committed Rust source from bounded transport bytes."""
    delivery = data["slice_source_delivery"]
    need(delivery["raw_path"] == "library/core/src/slice/mod.rs" and
         delivery["raw_sha256"] == source["actual_slice_source_sha256"] and
         delivery["raw_size"] == 229683 and
         delivery["git_blob"] == "16b5766ba08362bbf6ab13e127d71c7d920eccf7",
         "slice delivery manifest")
    archive = a.proof_root / delivery["path"]
    need(archive.is_file() and sha(archive) == delivery["compressed_sha256"],
         "compressed slice source pin")
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ)
    raw = decoder.decompress(archive.read_bytes(), max_length=delivery["raw_size"] + 1)
    need(decoder.eof and not decoder.unused_data and len(raw) == delivery["raw_size"] and
         hashlib.sha256(raw).hexdigest() == delivery["raw_sha256"],
         "exact full slice source transport")
    expected = subprocess.check_output(["git", "-C", str(a.proof_root),
                                        "ls-tree", "HEAD", "--", delivery["raw_path"]],
                                       text=True).strip().split()
    need(expected[:3] == ["100644", "blob", delivery["git_blob"]],
         "proof commit slice Git blob pin")
    actual_oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(actual_oid == delivery["git_blob"], "transport Git blob identity")
    target = a.proof_root / delivery["raw_path"]
    need(not target.is_symlink() and all(not parent.is_symlink() for parent in target.parents),
         "slice source symlink")
    need(not target.exists() or target.read_bytes() == raw,
         "existing slice source differs")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    save(a.evidence / "slice-source-delivery.json", {
        "committed_path": delivery["raw_path"], "git_blob": actual_oid,
        "raw_sha256": delivery["raw_sha256"],
        "compressed_sha256": delivery["compressed_sha256"],
        "full_source_bytes_delivered": True, "compiler_or_verifier_invoked": False,
        "proof_credit": False})


def source_prepare(a, data: dict, source: dict) -> None:
    need(not a.evidence.exists(), "source preparation already exists")
    a.evidence.mkdir(parents=True)
    caller = load(a.cloud_dir / CALLER.relative_to("research/challenge-8/cloud-build") /
                  "driver.py", "slice_binding_caller_sources")
    ghost_path = a.cloud_dir / "sort4-native-c1-bound/ghost-strip.py"
    caller.pinned_file(ghost_path, source["ghost_strip_sha256"], "ghost strip")
    ghost = load(ghost_path, "slice_binding_ghost_strip")
    for relative, label in (("sort4-native-c4/driver.py", "sort4-native-c4/driver.py"),
                            ("overnight-sort4/capture.py", "overnight-sort4/capture.py")):
        path = (a.cloud_dir / relative if relative.startswith("sort4-native") else
                a.proof_root / "research/challenge-8" / relative)
        caller.pinned_file(path, source["runtime_helpers_sha256"][label], label)
        load(path, "slice_binding_preflight_" + label.replace("/", "_"))
    work = SimpleNamespace(proof_root=a.proof_root, evidence=a.evidence)
    slice_path = a.proof_root / "library/core/src/slice/mod.rs"
    method = caller.validate_slice_source_bytes(slice_path.read_bytes(), source)
    certificate = {"source_path": "library/core/src/slice/mod.rs",
                   "source_sha256": sha(slice_path),
                   "canonical_method_body": method,
                   "full_source_bytes_delivered": True,
                   "method_count": 1, "proof_credit": False}
    admission = caller.source_admission_controls(work, source)
    rows = {}
    for name in SLICE_CASES:
        fixture, cert = caller.make_fixture(work, None, ghost, source, name)
        rows[name] = {"fixture": str(fixture.relative_to(a.evidence)),
                      "verified_sha256": cert["verified_sha256"],
                      "original_sha256": cert["original_sha256"],
                      "verification": "NOT_RUN_SOURCE_PREPARATION_ONLY"}
    need(all(row["refused_before_verifier"] for row in admission.values()),
         "source admission controls")
    save(a.evidence / "prepared.json", {
        "profile": PROFILE, "proof_sha": os.environ["PROOF_SHA"],
        "source_manifest_sha256": sha(a.proof_root / data["slice_binding_source_manifest"]),
        "source_certificate": certificate, "source_admission": admission,
        "cases": rows, "compiler_or_verifier_invoked": False,
        "all_sources_prepared_before_tool_build": True, "proof_credit": False})


def run(a, data: dict, source: dict) -> None:
    need(a.tool_home is not None and a.compiler_sysroot is not None and
         a.work_root is not None and a.deadline_epoch is not None,
         "Cloud tool arguments")
    need(not a.evidence.exists(), "result already exists")
    a.evidence.mkdir(parents=True)
    prepared = a.evidence.parents[1] / "source-preparation/slice"
    report = json.loads((prepared / "prepared.json").read_text())
    need(report["profile"] == PROFILE and report["proof_sha"] == os.environ["PROOF_SHA"] and
         report["source_manifest_sha256"] ==
         sha(a.proof_root / data["slice_binding_source_manifest"]) and
         report["all_sources_prepared_before_tool_build"] is True,
         "prepared source identity")
    c4 = load(a.cloud_dir / "sort4-native-c4/driver.py", "slice_binding_c4_helper")
    caller = load(a.cloud_dir / CALLER.relative_to("research/challenge-8/cloud-build") /
                  "driver.py", "slice_binding_caller_checks")
    tool = a.tool_home
    need(sha(tool / "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml") ==
         data["effective_hashes"]["src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"],
         "final translator pin")
    integration = load(a.cloud_dir / "verifast-c4-select-integration/driver.py",
                       "slice_binding_integration_pin")
    integration.pin(SimpleNamespace(proof_root=a.proof_root, manifest=a.manifest,
                                    tool_home=tool, evidence=a.evidence))
    env = c4.clean_env(a, tool)
    results = {}
    save(a.evidence / "result.json", {"profile": PROFILE, "cases": {},
                                     "classification": "NOT_RUN", "proof_credit": False})
    for name in SLICE_CASES:
        fixture = prepared / report["cases"][name]["fixture"]
        need(sha(fixture / "verified/lib.rs") == report["cases"][name]["verified_sha256"] and
             sha(fixture / "original/lib.rs") == report["cases"][name]["original_sha256"],
             "prepared fixture mutated: " + name)
        case_root = a.evidence / name
        result = caller.verify_one(a, c4, tool, env, fixture, name,
                                   root_override=case_root)
        original = (fixture / "original/lib.rs").read_text()
        mir_path = case_root / ("normal-" + caller.CASES[name] + "-full-mir.txt")
        mir_text = mir_path.read_text(errors="replace") if mir_path.is_file() else ""
        result["source_calls"] = {
            "v.as_mut_ptr": original.count("v.as_mut_ptr()"),
            "scratch.as_mut_ptr": original.count("scratch.as_mut_ptr()"),
            "normal_mir_as_mut_ptr_mentions": len(re.findall(r"as_mut_ptr", mir_text))}
        result["normal_full_mir_sha256"] = sha(mir_path) if mir_path.is_file() else None
        result["actual_callee_equivalence_from_marker"] = False
        results[name] = {key: result.get(key) for key in
                         ("classification", "gate_passed", "first_causal_stage",
                          "first_error", "verifier_exit", "paired_support_passed",
                          "proof_ast_sha256", "source_calls", "normal_full_mir_sha256",
                          "actual_callee_equivalence_from_marker")}
        save(a.evidence / "result.json", {"profile": PROFILE, "cases": results,
                                         "classification": "IN_PROGRESS",
                                         "tool_sha256": sha(tool / "bin/verifast"),
                                         "proof_credit": False})
    all_gates = all(row.get("gate_passed") is True for row in results.values())
    save(a.evidence / "result.json", {"profile": PROFILE, "cases": results,
        "classification": ("SLICE_BINDING_CANDIDATE_RAW_REVIEW_REQUIRED" if all_gates else
                           "SLICE_BINDING_FIRST_OBLIGATION_OPEN"),
        "all_expected_observed": all_gates, "source_admission": report["source_admission"],
        "tool_sha256": sha(tool / "bin/verifast"), "proof_credit": False,
        "profile_accepted": False, "actual_caller_proved": False,
        "callable_summary": False})


def audit(a, data: dict, source: dict) -> None:
    root = a.evidence.parents[1]
    rows = {}
    for key, path in (("slice", root / "cases/slice-binding/result.json"),
                      ("integration", root / "cases/integration/result.json"),
                      ("native", root / "cases/native-zst/result.json")):
        rows[key] = json.loads(path.read_text()) if path.is_file() else "NOT_RUN"
    slice_ok = (isinstance(rows["slice"], dict) and
                rows["slice"].get("classification") ==
                "SLICE_BINDING_CANDIDATE_RAW_REVIEW_REQUIRED" and
                rows["slice"].get("all_expected_observed") is True and
                set(rows["slice"].get("cases", {})) == set(SLICE_CASES) and
                all(row.get("gate_passed") is True for row in
                    rows["slice"]["cases"].values()) and
                all(row.get("refused_before_verifier") is True for row in
                    rows["slice"].get("source_admission", {}).values()) and
                len(rows["slice"].get("source_admission", {})) == 3)
    integration_ok = (isinstance(rows["integration"], dict) and
                      all(rows["integration"].get(key) is True for key in
                          ("selector_full_nine_body", "c4_positive", "composition_positive")))
    native_ok = (isinstance(rows["native"], dict) and
                 rows["native"].get("classification") ==
                 "NATIVE_ZST_EXPECTED_OBSERVED_RAW_REVIEW_REQUIRED" and
                 rows["native"].get("profile") == PROFILE and
                 all(isinstance(rows["native"].get(key), dict) and
                     rows["native"][key].get("all_expected_observed") is True for key in
                     ("fresh_c4_controls", "native_c1", "native", "zst")))
    effective_path = root / "cases/integration/effective-hashes.json"
    effective = json.loads(effective_path.read_text()) if effective_path.is_file() else {}
    console = effective.get("actual", {}).get("bin/verifast")
    same_tool = (isinstance(console, str) and
                 isinstance(rows["slice"], dict) and
                 isinstance(rows["native"], dict) and
                 console == rows["slice"].get("tool_sha256") ==
                 rows["native"].get("tool_sha256"))
    components_ok = (slice_ok and integration_ok and native_ok and same_tool and
                     a.slice_exit == 0 and a.native_exit == 0 and
                     a.integration_exit in (0, 1))
    integration_diagnostic = (isinstance(rows["integration"], dict) and
                              rows["integration"].get("diagnostic_complete") is True)
    regression = (rows["integration"].get("stages", {}).get("regressions", {})
                  if isinstance(rows["integration"], dict) else {})
    if not isinstance(regression, dict):
        regression = {}
    result = {"profile": PROFILE, "classification": (
                  "SCOPED_COMPONENT_EVIDENCE_RAW_REVIEW_PENDING" if components_ok else
                  "INCOMPLETE_OR_FIRST_OBLIGATION_OPEN"),
              "cases": rows, "runner_exits": {"slice": a.slice_exit,
                                              "integration": a.integration_exit,
                                              "native": a.native_exit},
              "required_components": {"slice": slice_ok, "nine_body_c4_composition": integration_ok,
                                      "native_c1_c4_zst": native_ok,
                                      "same_compiled_tool": same_tool},
              "scoped_components_complete": components_ok,
              "integration_diagnostic_complete": integration_diagnostic,
              "integration_completion_blockers": (rows["integration"].get("completion_blockers")
                  if isinstance(rows["integration"], dict) else ["integration_result_missing"]),
              "integration_regression_gates": regression.get("completion_gates"),
              "diagnostic_complete": False,
              "raw_review_pending": True, "proof_credit": False,
              "accepted": False, "verification_accepted": False,
              "profile_accepted": False,
              "actual_caller_proved": False, "callable_summary": False}
    save(root / "proof-audit.json", result)
    need(components_ok,
         "one or more fresh gates incomplete")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("materialize-slice", "source-prepare", "run", "audit",
                                         "supplement-check", "supplement-record"))
    for name in ("proof-root", "cloud-dir", "evidence", "manifest"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("tool-home", "compiler-sysroot", "work-root"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--deadline-epoch", type=int)
    for name in ("slice-exit", "integration-exit", "native-exit"):
        parser.add_argument("--" + name, type=int)
    a = parser.parse_args()
    data, source = context(a)
    if a.mode == "materialize-slice":
        materialize_slice(a, data, source)
    elif a.mode == "source-prepare":
        source_prepare(a, data, source)
    elif a.mode == "run":
        run(a, data, source)
    elif a.mode == "supplement-check":
        supplement_check(a, data)
    elif a.mode == "supplement-record":
        supplement_record(a, data)
    else:
        audit(a, data, source)


if __name__ == "__main__":
    main()
