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
    "research/challenge-8/cloud-build/verifast-c4-select-integration/outer-bound-escape.rs",
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
ADMISSION_MARKERS = {
    "source": "SORT4-C4-BOUND: verified source SHA256 differs",
    "contract": "SORT4-C4-BOUND: verified source SHA256 differs",
    "type": "TYPE: exact original first selector call/type/operands",
    "Move": "MOVE: exact original first selector operand setup",
    "edge": "EDGE: source-derived normal/unwind successor identity",
    # Reviewed normalized-edge mutation must reach the unchanged cleanup
    # predecessor inventory predicate; admission refusal is not a semantic VC.
    "reachable_unwind": "owner shared cleanup predecessor inventory",
}
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


def _balanced_node(text: str, start: int) -> str | None:
    """Return one formatter-emitted constructor, respecting quoted strings."""
    opening = text.find("(", start)
    if opening < 0:
        return None
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _outer_projection_ast(ast_text: str) -> dict:
    """Audit the exact exported FnOnce projection node for the outer fixture."""
    marker = '"#register_type_projection_equality"'
    offsets = [match.start() for match in re.finditer(re.escape(marker), ast_text)]
    nodes = []
    for offset in offsets:
        start = ast_text.rfind("ExprStmt (CallExpr (", 0, offset)
        if start < 0:
            continue
        node = _balanced_node(ast_text, start)
        if node is not None and marker in node:
            nodes.append((start, node))
    matching = []
    for start, node in nodes:
        refs = re.findall(
            r"RustRefTypeExpr \(loc \"[^\"]+\", IdentTypeExpr \(loc \"[^\"]+\", None, \"'cmp\"\), Shared, IdentTypeExpr \(loc \"[^\"]+\", None, \"T\"\)\)",
            node)
        ref_shape = r'RustRefTypeExpr \(loc "[^"]+", IdentTypeExpr \(loc "[^"]+", None, "\'cmp"\), Shared, IdentTypeExpr \(loc "[^"]+", None, "T"\)\)'
        tuple_shape = (r'StructTypeExpr \(loc "[^"]+", Some \("std_tuple_2_"\), None, \[\], \[' +
                       ref_shape + r';\s*' + ref_shape + r'\]\)')
        node_shape = (r'ExprStmt \(CallExpr \(loc "[^"]+", "#register_type_projection_equality", \[\s*'
                      r'ProjectionTypeExpr \(loc "[^"]+", IdentTypeExpr \(loc "[^"]+", None, "F"\), '
                      r'"std::ops::FnOnce", \[\s*' + tuple_shape + r'\s*\], "Output"\);\s*'
                      r'ManifestTypeExpr \(loc "[^"]+", Bool\)\s*\], \[\], \[\], Static\)\)')
        candidate = (
            re.fullmatch(node_shape, node) is not None and
            node.count(marker) == 1 and
            node.count("ProjectionTypeExpr") == 1 and
            node.count('IdentTypeExpr (loc ') >= 3 and
            re.search(r"IdentTypeExpr \(loc \"[^\"]+\", None, \"F\"\)", node) is not None and
            node.count('"std::ops::FnOnce"') == 1 and
            node.count('Some ("std_tuple_2_")') == 1 and
            len(refs) == 2 and
            node.count('"Output"') == 1 and
            node.count("ManifestTypeExpr") == 1 and
            node.count(", Bool)") == 1 and
            node.rstrip().endswith("Static))")
        )
        if candidate:
            loc = re.search(r"CallExpr \(loc \"(verified/lib\.rs\(\d+,\d+-\d+\))\"", node)
            if loc:
                end = start + len(node)
                switch_start = ast_text.find("SwitchStmt (", end)
                gap = ast_text[end:switch_start].strip() if switch_start >= 0 else None
                switch = (_balanced_node(ast_text, switch_start)
                          if switch_start >= 0 else None)
                between = gap[:-1].strip() if isinstance(gap, str) and gap.endswith(";") else "x"
                immediately_before_call = (
                    set(between) <= {")"} and switch is not None and
                    '"std::ops::FnMut::call_mut"' in switch and
                    loc.group(1) in switch)
                matching.append({"node": node, "call_location": loc.group(1),
                                 "offset": start, "end_offset": end,
                                 "following_switch_offset": switch_start,
                                 "immediately_before_call": immediately_before_call})
    return {"registration_marker_count": len(offsets),
            "registration_node_count": len(nodes),
            "matching_node_count": len(matching),
            "matching_nodes": matching}


def _inherited_regressions(a, tool, capture) -> dict:
    """Reuse only reviewed rows whose rule and fixture inputs are still exact."""
    path = a.proof_root / HERE / "manifest.json"
    manifest = (json.loads(path.read_text()) if path.is_file() else {}) if \
        os.environ.get("LANE") != "verifast-native-zst-integration" else {}
    inputs = manifest.get("inherited_regression_inputs", {})
    targets = manifest.get("inherited_regression_targets", {})
    actual_inputs = {
        "kernel_sha256": _sha(tool / "src/verifast.ml"),
        "parser_sha256": _sha(tool / "src/rust_frontend/vf_mir_translator/rust_parser.ml"),
        "prelude_sha256": _sha(tool / "bin/rust/std/lib.rsspec"),
        "strict_case_template_sha256": _sha(a.proof_root / REQUIRED_FILES[0]),
    }
    # The native/ZST lane changes verifast1.ml; historical C3 rows cannot be
    # inherited even when their narrower old input list still matches.
    input_pins_exact = os.environ.get("LANE") != "verifast-native-zst-integration" and bool(inputs) and all(
        inputs.get(name) == digest for name, digest in actual_inputs.items())
    strict_expected = {
        "positive_basic": ("positive", None),
        "negative_typed_chunk_survives_cut": (
            "owner_escape", "A lifetime-scoped heap chunk is still live at the binding end"),
        "negative_unclosed_fractional_access": ("debt", "lifetime_token"),
        "negative_reserved_half_after_lifetime_end": ("debt_or_token", "lifetime_token"),
    }
    strict_sources = {}
    template = (a.proof_root / REQUIRED_FILES[0]).read_bytes()
    for name in strict_expected:
        verified = capture.select_case(template, name)
        original = capture.strip_ghost(verified)
        strict_sources[name] = {
            "verified": hashlib.sha256(verified).hexdigest(),
            "original": hashlib.sha256(original).hexdigest(),
        }

    def valid_row(row, source_pair=None):
        return (isinstance(row, dict) and row.get("classification") == "REUSED_UNCHANGED_BASELINE" and
                row.get("raw_vc_review") == "REVIEWED" and
                row.get("intended_site_observed") is True and
                bool(re.fullmatch(r"[0-9a-f]{64}", str(row.get("raw_log_sha256", "")))) and
                (source_pair is None or row.get("source_pair") == source_pair))

    strict_rows = targets.get("strict_lifetime", {})
    strict_reusable = input_pins_exact and set(strict_rows) == set(strict_expected) and all(
        valid_row(strict_rows.get(name), strict_sources[name]) for name in strict_expected)
    pointer_rows = targets.get("pointer_value_pointee_rights", {})
    pointer_sources = {}
    for name in ("positive", "no-pointee-rights"):
        fixture = a.proof_root / HERE / "pointer-value-fixtures" / (name + ".rs")
        verified = fixture.read_bytes() if fixture.is_file() else b""
        original = capture.strip_ghost(verified)
        pointer_sources[name] = {"verified": hashlib.sha256(verified).hexdigest(),
                                 "original": hashlib.sha256(original).hexdigest()}
    pointer_reusable = input_pins_exact and set(pointer_rows) == {"positive", "no-pointee-rights"} and all(
        valid_row(pointer_rows.get(name), pointer_sources[name])
        for name in ("positive", "no-pointee-rights"))

    md_rows = targets.get("mdnew_retained_fix", {}).get("fixtures", {})
    mdnew_dir = os.environ.get("VERIFAST_MDNEW_FIXTURE_DIR")
    md_inputs_exact = bool(mdnew_dir)
    if mdnew_dir:
        fixture_root = Path(mdnew_dir)
        for name, (digest, _) in MDNEW_FIXTURES.items():
            source = fixture_root / name
            md_inputs_exact = md_inputs_exact and source.is_file() and _sha(source) == digest
    md_reusable = (input_pins_exact and md_inputs_exact and
        set(md_rows) == set(MDNEW_FIXTURES) and all(
            isinstance(row, dict) and row.get("classification") == "REUSED_UNCHANGED_BASELINE" and
            row.get("raw_vc_review") == "REVIEWED" and row.get("intended_diagnostic") is True and
            bool(re.fullmatch(r"[0-9a-f]{64}", str(row.get("raw_log_sha256", "")))) and
            row.get("expected") == MDNEW_FIXTURES[name][1]
            for name, row in md_rows.items()) and
        targets.get("mdnew_retained_fix", {}).get("all_intended") is True)
    return {
        "inputs_exact": input_pins_exact,
        "actual_inputs": actual_inputs,
        "strict_lifetime": strict_rows if strict_reusable else None,
        "pointer_value_pointee_rights": pointer_rows if pointer_reusable else None,
        "mdnew_retained_fix": md_rows if md_reusable else None,
        "mdnew_fixture_inputs_exact": md_inputs_exact,
        "review": inputs.get("review"),
        "evidence_build": inputs.get("build"),
    }


def _module(path: Path):
    spec = importlib.util.spec_from_file_location("c4_select_lifetime_capture", path)
    _need(spec is not None and spec.loader is not None, "lifetime capture helper missing")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cloud_guard() -> None:
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          os.environ.get("LANE") in ("verifast-c4-select-integration",
                                      "verifast-native-zst-integration") and
          not os.environ.get("GITHUB_ACTIONS"), "Cloud integration lane required")


def prepare_source_fixtures(a, root: Path) -> dict:
    """Materialize every source-only regression fixture; never invokes the tool."""
    _cloud_guard()
    _need(not root.exists() and not root.is_symlink(),
          "source-preparation fixture root must be unused")
    root.mkdir(parents=True)
    capture = _module(a.proof_root / REQUIRED_FILES[1])
    _module(a.cloud_dir / "o26-r3-frame-test.py")
    template = (a.proof_root / REQUIRED_FILES[0]).read_bytes()
    strict_root = root / "strict-lifetime"
    strict_root.mkdir()
    strict_cases = (
        "positive_basic", "negative_typed_chunk_survives_cut",
        "negative_unclosed_fractional_access",
        "negative_reserved_half_after_lifetime_end")
    strict_rows = {}
    for name in strict_cases:
        verified = capture.select_case(template, name)
        original = capture.strip_ghost(verified)
        case = strict_root / name
        (case / "verified").mkdir(parents=True)
        (case / "original").mkdir()
        (case / "verified/lib.rs").write_bytes(verified)
        (case / "original/lib.rs").write_bytes(original)
        _record(case / "source-certificate.json", {
            "case": name, "verified_sha256": hashlib.sha256(verified).hexdigest(),
            "original_sha256": hashlib.sha256(original).hexdigest(),
            "runtime_source_unchanged": original == capture.strip_ghost(verified),
            "proof_credit": False})
        strict_rows[name] = {"verified_sha256": hashlib.sha256(verified).hexdigest(),
                             "original_sha256": hashlib.sha256(original).hexdigest()}

    outer_source = a.proof_root / REQUIRED_FILES[3]
    outer_verified = outer_source.read_bytes()
    accepted = capture.select_case(template, "positive_f_bound")
    expected = accepted.replace(
        b"pub unsafe fn callback_positive<T, F: FnMut(&T, &T) -> bool>",
        b"pub unsafe fn negative_outer_bound_escape<T, F: FnMut(&T, &T) -> bool>", 1)
    _need(outer_verified == expected,
          "outer-bound fixture must differ only by the target function name")
    outer = root / "negative_outer_bound_escape"
    (outer / "verified").mkdir(parents=True)
    (outer / "original").mkdir()
    (outer / "verified/lib.rs").write_bytes(outer_verified)
    outer_original = capture.strip_ghost(outer_verified)
    (outer / "original/lib.rs").write_bytes(outer_original)
    _record(outer / "source-certificate.json", {
        "candidate_source": "overnight-lifetime/cases.rs#positive_f_bound",
        "candidate_sha256": hashlib.sha256(accepted).hexdigest(),
        "fixture_sha256": hashlib.sha256(outer_verified).hexdigest(),
        "target_name_only_change": True,
        "ghost_strip_runtime_identity": outer_original == capture.strip_ghost(outer_verified),
        "proof_credit": False})

    pointer_rows = {}
    for name in ("positive", "no-pointee-rights"):
        source = a.proof_root / HERE / "pointer-value-fixtures" / (name + ".rs")
        verified = source.read_bytes()
        case = root / ("pointer-value-" + name)
        (case / "verified").mkdir(parents=True)
        (case / "original").mkdir()
        original = capture.strip_ghost(verified)
        (case / "verified/lib.rs").write_bytes(verified)
        (case / "original/lib.rs").write_bytes(original)
        pointer_rows[name] = {"verified_sha256": hashlib.sha256(verified).hexdigest(),
                              "original_sha256": hashlib.sha256(original).hexdigest()}

    mdnew_dir = Path(os.environ.get("VERIFAST_MDNEW_FIXTURE_DIR",
                                    str(a.proof_root / HERE / "mdnew-fixtures")))
    mdnew_rows = {}
    mdnew_root = root / "mdnew-retained-fix"
    mdnew_root.mkdir()
    for name, (digest, expected_kind) in MDNEW_FIXTURES.items():
        source = mdnew_dir / name
        _need(source.is_file() and _sha(source) == digest,
              "MDnew fixture missing or differs from reviewed candidate: " + name)
        target = mdnew_root / name
        shutil.copyfile(source, target)
        mdnew_rows[name] = {"sha256": digest, "expected": expected_kind}
    report = {"classification": "SOURCE_FIXTURES_PREPARED_ONLY",
        "proof_credit": False, "strict_lifetime": strict_rows,
        "outer_bound_escape": {"verified_sha256": hashlib.sha256(outer_verified).hexdigest(),
                               "original_sha256": hashlib.sha256(outer_original).hexdigest()},
        "pointer_value": pointer_rows, "mdnew_retained_fix": mdnew_rows,
        "compiler_or_extractor_started": False, "verifier_started": False}
    _record(root / "fixture-inventory.json", report)
    return report


def _run_lifetime(a, selector_case, c4_env, proof, capture, inherited=None, mir_capture=None) -> dict:
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
    inherited_rows = (inherited or {}).get("strict_lifetime")
    results = {}
    if inherited_rows is not None:
        for case_name, (category, expected) in {
            name: (category, expected) for name, category, expected in cases
        }.items():
            row = inherited_rows[case_name]
            results[case_name] = {
                "category": category, "expected_vc": expected,
                "intended_site_observed": row["intended_site_observed"],
                "state": "REUSED_UNCHANGED_BASELINE",
                "source_pair": row["source_pair"],
                "raw_log_sha256": row["raw_log_sha256"],
                "raw_vc_review": row["raw_vc_review"],
                "evidence_build": row["evidence_build"],
                "proof_credit": False,
            }
    else:
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
    outer_source = a.proof_root / REQUIRED_FILES[3]
    outer_verified = outer_source.read_bytes()
    accepted_callback = capture.select_case(template, "positive_f_bound")
    expected_outer = accepted_callback.replace(
        b"pub unsafe fn callback_positive<T, F: FnMut(&T, &T) -> bool>",
        b"pub unsafe fn negative_outer_bound_escape<T, F: FnMut(&T, &T) -> bool>", 1)
    _need(accepted_callback != expected_outer and outer_verified == expected_outer,
          "outer-bound fixture must be the exact callback case with only target name changed")
    outer_original = capture.strip_ghost(outer_verified)
    outer_case = root / "negative_outer_bound_escape"
    (outer_case / "verified").mkdir(parents=True, exist_ok=False)
    (outer_case / "original").mkdir()
    (outer_case / "verified/lib.rs").write_bytes(outer_verified)
    (outer_case / "original/lib.rs").write_bytes(outer_original)
    _record(outer_case / "source-certificate.json", {
        "candidate_source": "overnight-lifetime/cases.rs#positive_f_bound",
        "candidate_sha256": hashlib.sha256(accepted_callback).hexdigest(),
        "fixture_sha256": hashlib.sha256(outer_verified).hexdigest(),
        "target_name_only_change": outer_verified == expected_outer,
        "ghost_strip_runtime_identity": outer_original == capture.strip_ghost(outer_verified),
        "proof_credit": False,
    })
    _need(mir_capture is not None, "outer full MIR capture callback required")
    outer_inventory = mir_capture(a, outer_case, "outer-bound", ["negative_outer_bound_escape"])
    immutable = json.loads(a.manifest.read_text())
    _need(outer_inventory == immutable["outer_scope_capture_pins"],
          "outer normal/readonly full MIR differs from reviewed capture")
    outer_env = env.copy()
    outer_env["SORT4_STRICT_LFT_RELOCATE"] = "1"
    outer_env["SORT4_STRICT_LFT_CUT"] = "1"
    outer_env["SORT4_HRTB_OUTPUT"] = "1"
    outer_env["SORT4_HRTB_OUTPUT_TARGETS"] = "negative_outer_bound_escape"
    ast_export = (outer_case / "final-current-bound-ast.ml").resolve()
    _need(not ast_export.exists(), "current-bound AST export path must be unused")
    outer_env["SORT4_CURRENT_BOUND_AST_EXPORT"] = str(ast_export)
    outer_result, outer_log = proof(
        a, "regression-lifetime-negative_outer_bound_escape", outer_case,
        outer_env, 300)
    auditor = _module(Path(__file__).with_name("outer_bool_auditor.py"))
    ast_text = ast_export.read_text() if ast_export.is_file() else ""
    positive = auditor.audit(outer_log, ast_text, outer_verified, outer_original, outer_result)
    results["outer_type_escape"] = {
        "category": "positive_local_hrtb_normal_unwind_closure",
        "historical_fixture_name": "negative_outer_bound_escape",
        "stage": outer_result, "expected_vc": None, "expected_cut_line": 106,
        "positive_audit": positive,
        "intended_site_observed": positive["classification"] == "PASS_POSITIVE_LOCAL_HRTB_CLOSURE",
        "raw_vc_review": "PENDING_INDEPENDENT_POSITIVE_REVIEW",
        "metadata_escape_negative": "OPEN_NOT_RUN", "general_O23": "OPEN",
        "proof_credit": False, "raw_log_sha256": hashlib.sha256(outer_log.encode()).hexdigest(),
    }
    _record(root / "result.json", {"classification": "DIAGNOSTIC_ONLY",
        "inherited_baseline_used": inherited_rows is not None,
        "inherited_evidence_build": (inherited or {}).get("evidence_build"),
        "cases": results, "accepted": False, "proof_credit": False})
    return results


def run(a, tool, selector_case, c4case, selector_env, c4_env, stage, proof,
        composition_controls=None, composition_admission_mutants=None, mir_capture=None):
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

    admission_input = composition_admission_mutants or {}
    admission_rows = {}
    for category in ADMISSION_CATEGORIES:
        supplied = admission_input.get(category)
        marker = supplied.get("refusal_marker") if isinstance(supplied, dict) else None
        logs = supplied.get("raw_log", "") if isinstance(supplied, dict) else ""
        stage_result = supplied.get("stage", supplied.get("result", {})) if isinstance(supplied, dict) else {}
        if not isinstance(stage_result, dict):
            stage_result = {}
        headers = stage_result.get("headers", [])
        marker_matches = (isinstance(marker, str) and
            ADMISSION_MARKERS[category] in marker and marker in logs)
        preflight_only = (category not in ("source", "contract") or
            isinstance(supplied, dict) and supplied.get("preflight_only") is True and
            stage_result.get("compiler_or_extractor_started") is False)
        mutation_exact = bool(supplied.get("mutation_fingerprints")) if isinstance(supplied, dict) else False
        if category in ("source", "contract"):
            fingerprints = supplied.get("mutation_fingerprints", {}) if isinstance(supplied, dict) else {}
            expected_source = json.loads(a.manifest.read_text())["c4_source_sha256"]
            mutation_exact = (isinstance(fingerprints, dict) and
                fingerprints.get("expected") == expected_source and
                all(isinstance(fingerprints.get(key), str) and
                    re.fullmatch(r"[a-f0-9]{64}", fingerprints[key])
                    for key in ("expected", "mutated", "runtime_before", "runtime_after")) and
                fingerprints["expected"] != fingerprints["mutated"] and
                ((fingerprints["runtime_before"] == fingerprints["runtime_after"]) ==
                 (category == "contract")) and
                supplied.get("raw_log_sha256") == hashlib.sha256((logs + "\n").encode()).hexdigest())
        exact = (isinstance(supplied, dict) and
            supplied.get("intended_refusal") == "EXACT_TARGET_REFUSAL" and
            marker_matches and preflight_only and
            not headers and stage_result.get("exit") in (1, 2) and
            mutation_exact)
        admission_rows[category] = {
            **(supplied if isinstance(supplied, dict) else {}),
            "state": "EXACT_TARGET_REFUSAL" if exact else "NOT_RUN_OR_UNCONFIRMED",
            "classification": "ADMISSION_REFUSAL" if exact else "INCONCLUSIVE",
            "refusal_marker_observed_in_log": bool(marker_matches),
            "preflight_only": preflight_only,
            "no_verifier_headers": not headers,
            "category_mutation_fingerprints_exact": mutation_exact,
            "proof_credit": False,
        }
    report["targets"]["composition_admission_mutants"] = admission_rows
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
            name: {
                "state": ("EXACT_TARGET_VC_OBSERVED" if
                    isinstance((composition_controls or {}).get(control_name), dict) and
                    (composition_controls or {})[control_name].get("intended_negative") == "EXACT_TARGET_VC_OBSERVED"
                    else "NOT_RUN_OR_UNCONFIRMED"),
                "classification": ("SEMANTIC_CONTROL_REVIEWED" if
                    isinstance((composition_controls or {}).get(control_name), dict) and
                    (composition_controls or {})[control_name].get("raw_vc_review") == "REVIEWED"
                    else "SEMANTIC_CONTROL_RAW_REVIEW_PENDING"),
                "result": (composition_controls or {}).get(control_name),
                "proof_credit": False,
            }
            for name, control_name in (
                ("frame", "leak-current-four-cell-frame"),
                ("thread_resources", "leak-thread-token"))
        },
    }

    lifetime_capture = _module(a.proof_root / REQUIRED_FILES[1])
    inherited = _inherited_regressions(a, tool, lifetime_capture)
    report["targets"]["inherited_baseline_inputs"] = {
        "inputs_exact": inherited["inputs_exact"],
        "actual_inputs": inherited["actual_inputs"],
        "evidence_build": inherited["evidence_build"],
        "review": inherited["review"],
        "proof_credit": False,
    }
    report["targets"]["strict_lifetime"] = _run_lifetime(
        a, selector_case, c4_env, proof, lifetime_capture, inherited, mir_capture)

    pointer_rows = {}
    inherited_pointer = inherited["pointer_value_pointee_rights"]
    if inherited_pointer is not None:
        for name in ("positive", "no-pointee-rights"):
            row = inherited_pointer[name]
            pointer_rows[name] = {
                "state": "REUSED_UNCHANGED_BASELINE",
                "intended_site_observed": row["intended_site_observed"],
                "source_pair": row["source_pair"],
                "raw_log_sha256": row["raw_log_sha256"],
                "raw_vc_review": row["raw_vc_review"],
                "evidence_build": row["evidence_build"],
                "proof_credit": False,
            }
    else:
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
    inherited_mdnew = inherited["mdnew_retained_fix"]
    if inherited_mdnew is not None:
        for name, row in inherited_mdnew.items():
            mdnew_rows[name] = {
                **row,
                "state": "REUSED_UNCHANGED_BASELINE",
                "proof_credit": False,
            }
        report["targets"]["mdnew_retained_fix"] = {
            "state": "REUSED_UNCHANGED_BASELINE",
            "classification": "DIAGNOSTIC_ONLY",
            "fixtures": mdnew_rows,
            "all_intended": all(row["intended_diagnostic"] for row in mdnew_rows.values()),
            "evidence_build": inherited["evidence_build"],
            "review": inherited["review"],
            "proof_credit": False,
        }
    elif mdnew_dir:
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
    for category, row in admission_rows.items():
        if row["state"] != "EXACT_TARGET_REFUSAL":
            blockers.append("composition_admission_mutant_not_exact:" + category)
    mdnew = report["targets"]["mdnew_retained_fix"]
    if mdnew.get("state") not in ("RUN", "REUSED_UNCHANGED_BASELINE") or not mdnew.get("all_intended"):
        blockers.append("mdnew_retained_fix_exact_diagnostics_not_observed")
    # Admission and same-post semantic controls are supplied by the driver's
    # exact-source, same-profile preparation callbacks and checked here.
    if not relation_exact:
        blockers.append("wrong_selected_original_relation_exact_control_not_observed")
    if not relation or relation.get("raw_vc_review") != "REVIEWED":
        blockers.append("wrong_selected_original_relation_raw_review_pending")
    if not report["targets"]["strict_lifetime"]["outer_type_escape"].get("intended_site_observed"):
        blockers.append("strict_lifetime_outer_bool_positive_closure_not_observed")
    if report["targets"]["strict_lifetime"]["outer_type_escape"].get("raw_vc_review") != "REVIEWED":
        blockers.append("strict_lifetime_outer_bool_positive_raw_review_pending")
    for target, control_name in (("frame", "leak-current-four-cell-frame"),
                                 ("thread_resources", "leak-thread-token")):
        control = report["targets"]["theorem_controls"][target]
        if control.get("state") != "EXACT_TARGET_VC_OBSERVED":
            blockers.append("not_run:composition_" + target + "_control")
        if not isinstance(control.get("result"), dict) or control["result"].get("raw_vc_review") != "REVIEWED":
            blockers.append("composition_" + target + "_raw_review_pending")
    report["completion_gates"] = {
        "ready": not blockers, "blockers": blockers,
        "proof_credit": False,
    }
    _record(evidence / "result.json", report)
    return report
