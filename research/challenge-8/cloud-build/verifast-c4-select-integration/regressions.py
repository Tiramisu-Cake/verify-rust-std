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


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def run(a, tool, selector_case, c4case, selector_env, c4_env, stage, proof):
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
    report["targets"]["selector_cleanup_off"] = {
        "stage": off, "dead_code_spans": dead,
        "exact_three_deadcode_spans": len(dead) == 3,
        "proof_credit": False,
        "classification": "DIAGNOSTIC_ONLY" if len(dead) == 3 else "INCONCLUSIVE",
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
                       not partial_result["headers"] and bool(partial_result["errors"]))
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
    report["targets"]["theorem_controls"] = {
        name: {"state": "NOT_RUN", "classification": "SEMANTIC_CONTROL_NOT_EXERCISED",
               "reason": "no verified same-source AST composition control hook exposed",
               "proof_credit": False}
        for name in ("wrong_selected_original_relation", "frame", "thread_resources")
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
                    first > entry and "No matching heap chunks" in row["errors"][0])
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
            if expected == "pass":
                intended = row["exit"] == 0 and not row.get("errors")
            elif expected == "dead":
                intended = (row["exit"] == 1 and "dead code" in log and
                            "forget_from_dead_precondition" in log)
            else:
                target_name = ("forget_false_normal_post" if name == "false_normal_post.rs"
                               else "shared_cleanup_false_unwind_post")
                entry = log.find("Verifying function '" + target_name + "'")
                error = log.find("error:", entry) if entry >= 0 else -1
                intended = row["exit"] == 0 and entry >= 0 and error > entry
            mdnew_rows[name] = {"expected": expected, "stage": row,
                "intended_diagnostic": intended, "proof_credit": False,
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
    _record(evidence / "result.json", report)
    return report
