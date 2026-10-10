#!/usr/bin/env python3
"""Cloud-only, evidence-producing regressions for the C4/selector phase.

Import is inert. ``run`` receives the phase driver callbacks so this module
cannot compile, export, refine, or verify except inside that driver's guarded
Cloud lane.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE = Path("research/challenge-8/cloud-build/verifast-c4-select-integration")
REQUIRED_FILES = (
    "research/challenge-8/overnight-lifetime/cases.rs",
    "research/challenge-8/overnight-lifetime/capture.py",
    "research/challenge-8/cloud-build/verifast-c4-select-integration/driver.py",
)
# These files live in the independently pinned infra checkout and must be
# staged by the recipe at VERIFAST_MDNEW_FIXTURE_DIR if that gate is enabled.
EXTERNAL_REQUIRED_FILES = tuple(
    "research/challenge-8/verifast-input/bf63b7dff2e053eea8541996d856fac4be11f6f1/bundle::tests/rust/purely_unsafe/manuallydrop_new_cfg/" + name
    for name in (
        "dead_code_pre.rs", "false_normal_post.rs", "forget.rs",
        "shared_cleanup.rs", "shared_false_unwind.rs",
    )
)
EXTERNAL_REQUIRED_FILES += (
    "research/challenge-8/verifast-input/bf63b7dff2e053eea8541996d856fac4be11f6f1/manifest",
)
MDNEW_FIXTURES = {
    "dead_code_pre.rs": ("b1317808274abeca09fc9b5b4e9079c7426822347205970217123993e0af70c2", "dead"),
    "false_normal_post.rs": ("23a1360b673fe6ece1f8903e69aae104f9e8dadfc34061d09062a993f6071f0d", "fail"),
    "forget.rs": ("2a6f0d16bd29cc9ea6c10e3b63e6b94000249d72e94d64f99d45cefb277ce1f7", "pass"),
    "shared_cleanup.rs": ("e3f91c8a2e0dfa9a1c281350b59318b5553847b1940add46d44061662d456d33", "pass"),
    "shared_false_unwind.rs": ("24c003dcb4f99c8bec2240dc3a61d5747f8c96b27b518686a0dbe32aef1158db", "fail"),
}
ADMISSION_CATEGORIES = (
    "source", "contract", "type", "Move", "edge", "reachable_unwind",
)
EXPECTED_CLEANUP_OFF = [
    "verified/lib.rs(135,1-239,2): dead code",
    "verified/lib.rs(238,5-6): dead code",
    "verified/lib.rs(238,5-6): dead code",
]
EXPECTED_MDNEW_DEAD = [
    "dead_code_pre.rs(1,1-7,2): dead code",
    "dead_code_pre.rs(6,13-43): dead code",
    "dead_code_pre.rs(6,41-42): dead code",
    "dead_code_pre.rs(7,2): dead code",
]
STAGE_ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")
STAGE_DEAD = re.compile(r"(?m)^.*: dead code$")


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stage_diagnostics(log: str) -> dict:
    return {
        "errors": STAGE_ERROR.findall(log),
        "dead_code": STAGE_DEAD.findall(log),
        "headers": re.findall(r"Verifying function '([^']+)'", log),
        "zero_errors": "0 errors found (" in log,
        "return_seen": "Executing return statement" in log,
        "leak_check_seen": "Leak check." in log,
    }


def _record(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _module(path: Path):
    spec = importlib.util.spec_from_file_location("c4_select_lifetime_capture", path)
    _need(spec is not None and spec.loader is not None, "lifetime capture helper missing")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cloud_guard() -> None:
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          os.environ.get("LANE") == "verifast-c4-select-integration" and
          not os.environ.get("GITHUB_ACTIONS"), "Cloud integration lane required")


def _run_lifetime(a, selector_case, c4_env, proof, capture) -> dict:
    """Run the saved isolated strict-cut cases through the parent's proof callback."""
    template_path = a.proof_root / REQUIRED_FILES[0]
    template = template_path.read_bytes()
    cases = (
        ("positive_basic", "positive", None),
        ("negative_typed_chunk_survives_cut", "owner_escape",
         "A lifetime-scoped heap chunk is still live at the binding end"),
        ("negative_unclosed_fractional_access", "debt",
         "lifetime_token"),
        ("negative_reserved_half_after_lifetime_end", "debt_or_token",
         "lifetime_token"),
    )
    root = a.evidence / "regressions" / "strict-lifetime"
    root.mkdir(parents=True, exist_ok=True)
    env = c4_env.copy()
    # Keep only strict lifetime semantics; this source is not the C4 AST target.
    for key in tuple(env):
        if key.startswith("SORT4_ACTUAL_") or key.startswith("SORT4_C4_"):
            env[key] = "0" if key.endswith(("TEST", "PREFIX_TEST", "CAPTURE_TEST")) else env[key]
    env["SORT4_STRICT_LFT_CUT"] = "1"
    env.pop("SORT4_HRTB_OUTPUT", None)
    env.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    results = {}
    for case_name, category, expected in cases:
        verified = capture.select_case(template, case_name)
        original = capture.strip_ghost(verified)
        case = root / case_name
        (case / "verified").mkdir(parents=True, exist_ok=False)
        (case / "original").mkdir()
        (case / "verified/lib.rs").write_bytes(verified)
        (case / "original/lib.rs").write_bytes(original)
        _record(case / "source-certificate.json", {
            "case": case_name, "verified_sha256": hashlib.sha256(verified).hexdigest(),
            "original_sha256": hashlib.sha256(original).hexdigest(),
            "runtime_source_unchanged": original == capture.strip_ghost(verified),
            "proof_credit": False,
        })
        result, log = proof(a, "regression-lifetime-" + case_name, case, env, 300)
        exact = (result["exit"] == 0 and not result["errors"] and
                 result["zero_errors"] and result["return_seen"] and result["leak_check_seen"])
        if expected is None:
            intended = exact
        else:
            intended = capture.expected_error(case_name, log, result["exit"])
        results[case_name] = {
            "category": category, "stage": result, "expected_vc": expected,
            "intended_site_observed": intended, "proof_credit": False,
            "raw_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        }
    results["outer_type_escape"] = {
        "state": "NOT_RUN", "reason": "saved strict-cut fixture classifies this source form as inconclusive until fresh MIR/source evidence",
        "proof_credit": False,
    }
    _record(root / "result.json", {"classification": "DIAGNOSTIC_ONLY",
        "cases": results, "accepted": False, "proof_credit": False})
    return results


def run(a, tool, selector_case, c4case, selector_env, c4_env, stage, proof,
        composition_controls=None):
    """Execute only narrow, callback-mediated regressions and record NOT_RUN gaps."""
    _cloud_guard()
    evidence = a.evidence / "regressions"
    evidence.mkdir(parents=True, exist_ok=True)
    report = {"classification": "REGRESSION_DIAGNOSTICS_ONLY", "accepted": False,
              "proof_credit": False, "targets": {}}

    # Historical selector cleanup projection is opt-in. Without its certificate,
    # exactly the three original false-unwind cleanup blocks should remain dead.
    off_env = dict(selector_env)
    off_env.pop("SORT4_R3_CLEANUP_PROJECTION_TEST", None)
    off_env.pop("SORT4_R3_CLEANUP_PROJECTION_TEST_REPO_ROOT", None)
    off, off_log = proof(a, "selector-cleanup-off", selector_case, off_env, 300)
    dead = off.get("dead_code", [])
    frame_log = _module(a.cloud_dir / "o26-r3-frame-test.py")
    off_frame = frame_log.log_proof_evidence(off_log, {"exit": off["exit"]})
    cleanup_off_exact = (
        off["exit"] == 1 and dead == EXPECTED_CLEANUP_OFF and
        not off["errors"] and off_frame["first_error"] is None and
        off_frame["prefix7_ordered"] and off_frame["nested_before_outer"] and
        off_frame["helper_full_normal_unwind_observed"] and
        off_frame["nested_full_normal_unwind_observed"] and
        len(off_frame["outer_counts"]) == 4 and
        all(value == 2 for value in off_frame["outer_counts"].values())
    )
    report["targets"]["selector_cleanup_off"] = {
        "stage": off, "dead_code_spans": dead,
        "expected_dead_code_spans": EXPECTED_CLEANUP_OFF,
        "exact_three_deadcode_spans": cleanup_off_exact,
        "frame_log_audit": off_frame,
        "proof_credit": False,
        "classification": "DIAGNOSTIC_ONLY" if cleanup_off_exact else "INCONCLUSIVE",
        "raw_log_sha256": hashlib.sha256(off_log.encode()).hexdigest(),
    }

    # Exercise a deliberately incomplete cleanup opt-in. Admission must refuse
    # before any selector body is verified; this is not a semantic negative.
    partial = dict(selector_env)
    partial["SORT4_R3_CLEANUP_PROJECTION_TEST"] = "1"
    partial.pop("SORT4_R3_CLEANUP_PROJECTION_TEST_REPO_ROOT", None)
    partial_result, partial_log = proof(a, "selector-cleanup-partial-optin-refusal",
                                        selector_case, partial, 120)
    partial_refused = (partial_result["exit"] in (1, 2) and
                       not partial_result["headers"] and
                       "SORT4-R3-CLEANUP-PROJECTION-TEST" in partial_log and
                       "exact root/test opt-in pair" in partial_log)
    report["targets"]["cleanup_partial_optin"] = {
        "stage": partial_result, "refused_before_function": partial_refused,
        "raw_log_sha256": hashlib.sha256(partial_log.encode()).hexdigest(),
        "classification": "ADMISSION_REFUSAL" if partial_refused else "INCONCLUSIVE",
        "proof_credit": False,
    }

    # The current composition hook does not expose a typed mutant-preparation
    # callback. Do not fabricate AST, CFG, Move, or callee artifacts here.
    report["targets"]["composition_admission_mutants"] = {
        category: {"state": "NOT_RUN", "classification": "ADMISSION_NOT_EXERCISED",
                   "reason": "no same-source typed AST/CFG mutant hook in the phase callbacks",
                   "proof_credit": False}
        for category in ADMISSION_CATEGORIES
    }
    relation = (composition_controls or {}).get("wrong-selected-original")
    relation_exact = (isinstance(relation, dict) and
                      relation.get("intended_negative") == "EXACT_TARGET_VC_OBSERVED")
    report["targets"]["theorem_controls"] = {
        "wrong_selected_original_relation": {
            "state": "EXACT_TARGET_VC_OBSERVED" if relation_exact else "NOT_RUN_OR_UNCONFIRMED",
            "classification": "SEMANTIC_CONTROL_RAW_REVIEW_PENDING",
            "result": relation, "proof_credit": False,
        },
        **{
            name: {"state": "NOT_RUN", "classification": "SEMANTIC_CONTROL_NOT_EXERCISED",
                   "reason": "no isolated same-source frame/thread mutant hook exposed",
                   "proof_credit": False}
            for name in ("frame", "thread_resources")
        },
    }

    lifetime_capture = _module(a.proof_root / REQUIRED_FILES[1])
    report["targets"]["strict_lifetime"] = _run_lifetime(
        a, selector_case, c4_env, proof, lifetime_capture)

    pointer_rows = {}
    for name in ("positive", "no-pointee-rights"):
        source = a.proof_root / HERE / "pointer-value-fixtures" / (name + ".rs")
        case = evidence / ("pointer-value-" + name)
        (case / "verified").mkdir(parents=True, exist_ok=False)
        (case / "original").mkdir()
        verified = source.read_bytes()
        (case / "verified/lib.rs").write_bytes(verified)
        (case / "original/lib.rs").write_bytes(lifetime_capture.strip_ghost(verified))
        env = dict(c4_env)
        env["SORT4_ACTUAL_AST_SCOPE_TEST"] = "0"
        env["SORT4_ACTUAL_C4_BOUND_PREFIX_TEST"] = "0"
        row, log = proof(a, "regression-pointer-value-" + name, case, env, 180)
        target = "pointer_value_identity" if name == "positive" else "pointer_value_cannot_own_pointee"
        entry = log.find("Verifying function '" + target + "'")
        first = log.find(row["errors"][0]) if row["errors"] else -1
        intended = (row["exit"] == 0 and row["zero_errors"] and not row["errors"]
                    if name == "positive" else row["exit"] in (1,2) and entry >= 0 and
                    first > entry and "No matching heap chunks" in row["errors"][0] and
                    re.search(r"\(3,\d+(?:-\d+(?:,\d+)?)?\): error:",
                        row["errors"][0]) is not None)
        pointer_rows[name] = {"stage": row, "intended_site_observed": intended,
                              "raw_vc_review": "PENDING", "proof_credit": False}
    report["targets"]["pointer_value_pointee_rights"] = pointer_rows

    # Recipe may stage the separately reviewed candidate's source fixtures.
    # Verify every byte against its manifest before invoking the patched tool.
    mdnew_dir = os.environ.get("VERIFAST_MDNEW_FIXTURE_DIR")
    mdnew_rows = {}
    if mdnew_dir:
        fixture_root = Path(mdnew_dir)
        target = evidence / "mdnew-retained-fix"
        for name, (digest, expected) in MDNEW_FIXTURES.items():
            source = fixture_root / name
            _need(source.is_file() and _sha(source) == digest,
                  "MDnew fixture missing or differs from reviewed candidate: " + name)
            case = target / name.removesuffix(".rs")
            case.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(source, case / name)
            args = [str(tool / "bin/verifast"), "-verbose", "2"]
            if expected == "fail":
                args.append("-allow_should_fail")
            args.append(name)
            row, log = stage(a, "regression-mdnew-" + name.removesuffix(".rs"),
                             args, case, {}, 180)
            diagnostics = _stage_diagnostics(log)
            if expected == "pass":
                required_headers = (("forget",) if name == "forget.rs" else
                    ("new", "ordinary_caller", "shared_cleanup", "normal_first_cleanup"))
                intended = (row["exit"] == 0 and diagnostics["zero_errors"] and
                    not diagnostics["errors"] and not diagnostics["dead_code"] and
                    all(diagnostics["headers"].count(header) == 1
                        for header in required_headers) and
                    diagnostics["return_seen"] and diagnostics["leak_check_seen"])
            elif expected == "dead":
                intended = (row["exit"] == 1 and
                    diagnostics["dead_code"] == EXPECTED_MDNEW_DEAD and
                    not diagnostics["errors"] and
                    "forget_from_dead_precondition" in diagnostics["headers"])
            else:
                target_name = ("forget_false_normal_post" if name == "false_normal_post.rs"
                               else "shared_cleanup_false_unwind_post")
                expected_line = 3 if name == "false_normal_post.rs" else 14
                source_text = source.read_text()
                marked_lines = [number for number, text in enumerate(
                    source_text.splitlines(), 1) if "//~should_fail" in text]
                event = rf"{re.escape(name)}\({expected_line},\d+-\d+\): Consuming (?:assertion|expression)"
                intended = (
                    row["exit"] == 0 and diagnostics["zero_errors"] and
                    not diagnostics["errors"] and not diagnostics["dead_code"] and
                    diagnostics["headers"].count(target_name) == 1 and
                    diagnostics["return_seen"] and diagnostics["leak_check_seen"] and
                    marked_lines == [expected_line] and
                    len(re.findall(event, log)) == 2 and
                    len(re.findall(rf"{re.escape(name)}\({expected_line},\d+-\d+\): Consuming assertion", log)) == 1 and
                    len(re.findall(rf"{re.escape(name)}\({expected_line},\d+-\d+\): Consuming expression", log)) == 1
                )
            mdnew_rows[name] = {"expected": expected, "stage": row, "raw_vc_review": "PENDING",
                "diagnostics": diagnostics, "expected_source_line":
                    (7 if expected == "dead" else
                     3 if name == "false_normal_post.rs" else
                     14 if name == "shared_false_unwind.rs" else None),
                "intended_diagnostic": intended,
                "expected_failure_harness": expected == "fail",
                "expected_failure_interpretation": (
                    "-allow_should_fail succeeded after consuming the annotated false contract; this is not a printed verifier error"
                    if expected == "fail" else None),
                "proof_credit": False,
                "raw_log_sha256": hashlib.sha256(log.encode()).hexdigest()}
        report["targets"]["mdnew_retained_fix"] = {
            "state": "RUN", "classification": "DIAGNOSTIC_ONLY",
            "fixtures": mdnew_rows, "all_intended": all(
                row["intended_diagnostic"] for row in mdnew_rows.values()),
            "proof_credit": False,
        }
    else:
        report["targets"]["mdnew_retained_fix"] = {
            "state": "NOT_RUN", "classification": "RETAINED_FIX_REGRESSION_NOT_RUN",
            "reason": "recipe must stage the pinned candidate fixtures and set VERIFAST_MDNEW_FIXTURE_DIR",
            "proof_credit": False,
        }
    blockers = []
    if not cleanup_off_exact:
        blockers.append("selector_cleanup_off_exact_spans_and_full_diagnostic_not_observed")
    if not partial_refused:
        blockers.append("cleanup_partial_optin_refusal_not_observed")
    if any(not row["intended_site_observed"] for row in pointer_rows.values()):
        blockers.append("pointer_value_expected_site_not_observed")
    if not all(row.get("intended_site_observed", False)
               for row in report["targets"]["strict_lifetime"].values()
               if isinstance(row, dict) and "intended_site_observed" in row):
        blockers.append("strict_lifetime_expected_site_not_observed")
    mdnew = report["targets"]["mdnew_retained_fix"]
    if mdnew.get("state") != "RUN" or not mdnew.get("all_intended"):
        blockers.append("mdnew_retained_fix_exact_diagnostics_not_observed")
    # These are explicit phase gates. The current callbacks cannot construct
    # the required same-source AST/CFG mutants or isolated frame/thread controls.
    blockers.extend("not_run:" + category for category in ADMISSION_CATEGORIES)
    if not relation_exact:
        blockers.append("wrong_selected_original_relation_exact_control_not_observed")
    blockers.extend(("not_run:strict_lifetime_outer_type_escape",
                     "not_run:composition_frame_control",
                     "not_run:composition_thread_resource_control"))
    report["completion_gates"] = {
        "ready": not blockers, "blockers": blockers,
        "proof_credit": False,
    }
    _record(evidence / "result.json", report)
    return report
