"""Offline semantic bindings for the S1-06 success assertions and SAT covers.

This module intentionally does not infer property ordinals from macro expansion
order.  A macro invocation can emit several placeholder assertions at the same
callsite; those IDs are returned as candidates until the producer records a
same-compilation expansion-to-property map.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


SOURCE_SHA = "5be85699b8826e3286c0bf89efb9affefac0acb5"
PLACEHOLDER = "This is a placeholder message; Kani doesn't support message formatted at runtime"

# Manual w13 source audit. These are source coordinates in SOURCE_SHA; the
# analyzer additionally emits the selected invocation, operation, and cover
# lines per row. Counts sum to the 113 required covers in this intake.
SOURCE_CASE_AUDIT = {
    "ENTRY_SMOKE_MACRO": {
        "covers": 22,
        "file": "library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_smoke.rs",
        "anchors": {
            "assumption": [39], "actual_target_invoke": [51, 130],
            "post_and_canaries": [[52, 56], [131, 135]],
            "symbolic_n_cover_statements": [66, 79],
            "exact_n_cover_dispatch": [145], "exact_n_useful_cover": [146],
        },
        "interpretation": "Selected smoke! root, n<=3 assumption, target invocation, post/canary assertions, then required return/input covers.",
    },
    "ENTRY_EXACT_N_MACRO": {
        "covers": 56,
        "file": "library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_smoke.rs",
        "anchors": {
            "actual_target_invoke": [130], "post_and_canaries": [[131, 135]],
            "nested_dispatch": [145], "nested_N_arms": [87, 110],
            "useful_cover": [146],
        },
        "interpretation": "Selected smoke_exact_n! invocation carries concrete type and N; exact_n_covers! dispatches that N arm after target call and post/canary checks.",
    },
    "MODEL_CONTROLS_POSITIVE": {
        "covers": 18,
        "file": "library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs",
        "anchors": {"assumption": [32], "sorted_prefix": [44],
                    "model_relations": [[42, 56]], "covers": [57, 62]},
        "interpretation": "Selected positive! root, len<=3 assumption and model consistency/permutation/comparator assertions precede the covers; this is a model-control fixture, not a SmallSort target call.",
    },
    "DIRECT_CONTROL_OR_COMPANION": {
        "covers": 5,
        "files": [
            "library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs",
            "library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs",
        ],
        "anchors": {
            "inactive_helper_calls": [80, 84, 90], "inactive_legal_storage_cover": [91],
            "corruption_post_checks_and_return_cover": [[128, 132], 133],
            "snapshot_checks_and_return_cover": [[159, 174], 175],
            "entry_default_actual_call_post_cover": [[17, 18], 19, 20],
            "entry_override_actual_call_post_cover": [[30, 31], 32, 33],
        },
        "interpretation": "Selected direct companion/control harness call sequence is inspected through its own return cover; actual SmallSort calls are reported only for the two activation companions.",
    },
    "ORDINARY_BRIDGE_CHECK_MACRO": {
        "covers": 12,
        "file": "library/core/src/slice/sort/shared/smallsort/verify/smoke.rs",
        "anchors": {"nested_check_assert": [18], "nested_check_cover": [19],
                    "type_specific_invocations": [22, 33]},
        "interpretation": "Each exact property description is mapped through its selected check!(T, expected) type invocation to assert has_efficient_in_place_swap::<T>() then the concat/stringify cover.",
    },
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _source(repo: Path, path: str) -> str | None:
    """Read a file from the pinned git tree, never from a mutable worktree."""
    path = path.removeprefix("library/core/")
    path = "library/core/" + path if not path.startswith("library/") else path
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{SOURCE_SHA}:{path}"],
            check=True, capture_output=True, text=True,
        )
        return result.stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _rel_file(value: str) -> str:
    marker = "/library/core/"
    if marker in value:
        return "library/core/" + value.split(marker, 1)[1]
    if value.startswith("library/core/"):
        return value
    return value


def _property_path(run_dir: Path, group: str) -> Path:
    return run_dir / "evidence" / group / "properties.json"


def _balanced_region(lines: list[str], start: int) -> tuple[int, int]:
    """Return inclusive start/end lines around a brace-delimited Rust item."""
    depth = 0
    opened = False
    for i in range(start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if opened and depth == 0:
                    return start, i
    return start, min(len(lines) - 1, start)


def _macro_regions(lines: list[str]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for i, line in enumerate(lines):
        m = re.search(r"macro_rules!\s+([A-Za-z_][A-Za-z0-9_]*)", line)
        if m:
            out[m.group(1)] = _balanced_region(lines, i)
    return out


def _function_lines(lines: list[str], name: str) -> tuple[int, int] | None:
    pat = re.compile(r"\bfn\s+" + re.escape(name) + r"\s*[<(]")
    for i, line in enumerate(lines):
        if pat.search(line):
            return _balanced_region(lines, i)
    return None


def _macro_invocation(lines: list[str], function_name: str) -> tuple[int, str] | None:
    # Harnesses defined by macro_rules! have a concrete invocation named after
    # the selected harness; use that invocation as the expansion callsite.
    for i, line in enumerate(lines):
        m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)!\s*\(\s*" +
                      re.escape(function_name) + r"\b", line)
        if m:
            return i + 1, m.group(1)
    return None


def _site_lines(source: str, message: str, role: str) -> list[int]:
    lines = source.splitlines()
    out: list[int] = []
    for i, line in enumerate(lines):
        if message not in line:
            continue
        # Multi-line literal is unusual in this corpus; retaining a source site
        # still helps diagnose it, but only the requested role is considered.
        window = " ".join(lines[max(0, i - 2):min(len(lines), i + 2)])
        if role == "cover" and re.search(r"(?:kani::)?cover\s*\(", window):
            out.append(i + 1)
        elif role == "assertion" and re.search(r"assert!\s*\(", window):
            start = next((j + 1 for j in range(i, max(-1, i - 3), -1)
                          if re.search(r"assert!\s*\(", lines[j])), i + 1)
            out.append(start)
    return out


def _source_context(source: str, function_name: str, message: str,
                    role: str, property_line: int | None) -> dict[str, Any]:
    lines = source.splitlines()
    sites = _site_lines(source, message, role)
    fn_region = _function_lines(lines, function_name)
    invocation = _macro_invocation(lines, function_name)
    macros = _macro_regions(lines)
    active_macro: str | None = invocation[1] if invocation else None

    if fn_region and any(fn_region[0] <= site - 1 <= fn_region[1] for site in sites):
        active_sites = [site for site in sites if fn_region[0] <= site - 1 <= fn_region[1]]
        expansion = "direct-function"
    elif active_macro and active_macro in macros:
        lo, hi = macros[active_macro]
        active_sites = [site for site in sites if lo <= site - 1 <= hi]
        expansion = "macro-invocation"
        # Nested helper macros (for example exact_n_covers!) are live only
        # when called from the selected root macro's body.
        body = "\n".join(lines[lo:hi + 1])
        for nested, (nlo, nhi) in macros.items():
            if re.search(r"\b" + re.escape(nested) + r"!\s*\(", body):
                active_sites.extend(site for site in sites if nlo <= site - 1 <= nhi)
    else:
        active_sites = []
        expansion = "unresolved"

    # The ordinary bridge builds descriptions with concat!/stringify!, so the
    # resulting label has no literal in Rust source. Bind it through the
    # selected type-specific `check!(T, ...)` invocation and the macro body.
    if role == "cover" and not active_sites and fn_region:
        m = re.fullmatch(r"efficient swap predicate for (.+)", message)
        if m:
            ty = m.group(1)
            for i in range(fn_region[0], fn_region[1] + 1):
                if re.search(r"\bcheck!\s*\(\s*" + re.escape(ty) + r"\s*,", lines[i]):
                    active_sites.append(i + 1)
            if active_sites:
                expansion = "nested-macro-callsite"
                active_macro = "check"

    active_sites = sorted(set(active_sites))
    role_order = False
    assumptions: list[int] = []
    operations: list[int] = []
    cover_anchors = active_sites[:]
    target_in_active_context = False
    target_call_lines: list[int] = []
    invocation_source = None
    cover_arm = None
    if invocation:
        invocation_source = lines[invocation[0] - 1].strip()
    n_match = re.search(r"S1_(?:entry|model)_N([0-3])", message)
    if n_match:
        cover_arm = {"N": int(n_match.group(1)),
                     "case": re.sub(r"^S1_(?:entry|model)_N[0-3]_?", "", message)}
    if active_sites:
        if expansion == "nested-macro-callsite" and active_macro in macros and fn_region:
            mlo, mhi = macros[active_macro]
            macro_body = "\n".join(lines[mlo:mhi + 1])
            body = lines[fn_region[0]:fn_region[1] + 1]
            operations = [fn_region[0] + i + 1 for i, line in enumerate(body)
                          if "check!(" in line]
            role_order = ("assert!(" in macro_body and "cover(" in macro_body
                          and bool(operations))
        elif active_macro and active_macro in macros:
            lo, hi = macros[active_macro]
            body = lines[lo:hi + 1]
            assumptions = [lo + i + 1 for i, line in enumerate(body)
                           if "kani::assume(" in line or "$exact_n" in line]
            target_call_lines = [lo + i + 1 for i, line in enumerate(body)
                                 if "invoke!(" in line or "small_sort(" in line]
            operations = target_call_lines + [lo + i + 1 for i, line in enumerate(body)
                                               if "post(" in line or "assert!(" in line]
            cover_anchors = [lo + i + 1 for i, line in enumerate(body)
                             if "cover(" in line or "exact_n_covers!(" in line]
            target_in_active_context = bool(target_call_lines)
            if "invoke!(" in "\n".join(body) and "invoke" in macros:
                ilo, ihi = macros["invoke"]
                target_in_active_context = "small_sort(" in "\n".join(lines[ilo:ihi + 1])
            role_order = bool(cover_anchors and (
                (target_call_lines and min(target_call_lines) < min(cover_anchors)
                 and (not assumptions or min(assumptions) < min(target_call_lines)))
                or (not target_call_lines and operations and min(operations) < min(cover_anchors)
                    and (not assumptions or min(assumptions) < min(operations)))))
            if "exact_n_covers!" in "\n".join(body):
                if cover_arm is None:
                    cover_arm = {}
                cover_arm["nested_cover_macro"] = "exact_n_covers"
                cover_arm["nested_arm_source_lines"] = [i + 1 for i, line in enumerate(lines)
                                                         if "S1_entry_N" in line and message in line]
        elif fn_region:
            body = lines[fn_region[0]:fn_region[1] + 1]
            assumptions = [fn_region[0] + i + 1 for i, line in enumerate(body)
                           if "kani::assume(" in line or "let n:" in line]
            operations = [fn_region[0] + i + 1 for i, line in enumerate(body)
                          if "small_sort(" in line or "invoke!(" in line
                          or "post(" in line or "sorted_prefix(" in line
                          or "assert!(" in line or "check!(" in line
                          or re.search(r"\binactive\s*\(", line)]
            cover_anchors = [fn_region[0] + i + 1 for i, line in enumerate(body)
                             if "cover(" in line or "check!(" in line]
            target_in_active_context = any("small_sort(" in line or "invoke!(" in line for line in body)
            target_call_lines = [fn_region[0] + i + 1 for i, line in enumerate(body)
                                 if "small_sort(" in line or "invoke!(" in line]
            if target_call_lines:
                role_order = bool(cover_anchors
                                  and (not assumptions or min(assumptions) < min(target_call_lines))
                                  and min(target_call_lines) < min(cover_anchors))
            else:
                role_order = bool(operations and cover_anchors
                                  and (not assumptions or min(assumptions) < min(operations))
                                  and min(operations) < min(cover_anchors))

    # The w13 cover set has four known source shapes. Keep this acceptance
    # deliberately case-based: unknown macro/control-flow shapes fail closed.
    source_case = "UNRECOGNIZED_SOURCE_SHAPE"
    rationale = "No approved S1-06 source-case mapping matched this selected harness."
    if active_sites and active_macro == "smoke":
        source_case = "ENTRY_SMOKE_MACRO"
        rationale = "Selected smoke! invocation -> invoke! actual target call -> required cover statements."
        role_order = bool(role_order and target_in_active_context and target_call_lines
                          and cover_anchors and min(target_call_lines) < min(cover_anchors)
                          and assumptions and min(assumptions) < min(target_call_lines))
    elif active_sites and active_macro == "smoke_exact_n":
        source_case = "ENTRY_EXACT_N_MACRO"
        rationale = "Selected smoke_exact_n! invocation -> target call -> exact_n_covers! N arm -> SAT cover."
        role_order = bool(role_order and target_in_active_context and target_call_lines
                          and cover_anchors and min(target_call_lines) < min(cover_anchors)
                          and assumptions and min(assumptions) < min(target_call_lines)
                          and cover_arm and cover_arm.get("nested_cover_macro") == "exact_n_covers")
    elif active_sites and active_macro == "positive" and function_name in {
            "model_u8_n0_3", "model_cell_n0_3", "model_noncopy_n0_3"}:
        source_case = "MODEL_CONTROLS_POSITIVE"
        rationale = "Selected positive! invocation; len<=3 assumption and model assertions precede covers."
        role_order = bool(role_order and assumptions and operations and cover_anchors
                          and min(assumptions) < min(operations) < min(cover_anchors))
    elif (active_sites and expansion == "nested-macro-callsite"
          and function_name == "predicate_efficient_swap_type_matrix"
          and message.startswith("efficient swap predicate for ")):
        source_case = "ORDINARY_BRIDGE_CHECK_MACRO"
        rationale = "Type-specific check!(T, expected) selects assert/concat cover macro expansion."
        role_order = bool(role_order and active_macro == "check")
    elif (active_sites and expansion == "direct-function"
          and function_name in {"inactive_pairs_read_free", "corruption_companion",
                                "snapshot_guards_companion", "stable_default_activation",
                                "stable_freeze_activation"}):
        source_case = "DIRECT_CONTROL_OR_COMPANION"
        rationale = "Selected direct harness call/setup precedes its named cover statement."
        role_order = bool(role_order and fn_region and cover_anchors)
    else:
        role_order = False

    return {
        "source_role_sites": sites,
        "active_source_role_sites": active_sites,
        "expansion_context": expansion,
        "root_macro": active_macro,
        "root_macro_invocation_source": invocation_source,
        "cover_arm": cover_arm,
        "harness_function": function_name,
        "property_source_line": property_line,
        "property_line_is_root_macro_callsite": bool(invocation and property_line == invocation[0]),
        "source_role_order_after_assumptions_and_call": role_order,
        "source_case": source_case,
        "source_case_rationale": rationale,
        "assumption_source_lines": assumptions,
        "operation_source_lines": operations,
        "cover_source_lines": cover_anchors,
        "actual_small_sort_call_observed_in_active_context": target_in_active_context,
        "target_call_source_lines": target_call_lines,
    }


def analyze(run: str | Path, request: str | Path | dict[str, Any],
            std_repo: str | Path) -> dict[str, Any]:
    """Return row-indexed semantic success and SAT-cover binding records.

    `run` is the S1-06 run directory. `request` may be CI-REQUEST.json or an
    already loaded request mapping. `std_repo` is the source git repository;
    source is always read from the fixed w13 commit above.
    """
    run_dir = Path(run)
    if isinstance(request, (str, Path)):
        request_obj = _read_json(Path(request))
    else:
        request_obj = request
    accept = _read_json(run_dir / "accept" / "ACCEPT.json")
    req_rows = {row["id"]: row for row in request_obj.get("rows", [])}
    source_root = Path(std_repo)
    out_rows: dict[str, Any] = {}
    gaps: list[dict[str, Any]] = []
    success_total = success_exact = success_candidates = 0
    cover_total = cover_exact = cover_semantic = 0

    for row in accept.get("rows", []):
        row_id = row["id"]
        req = req_rows.get(row_id, {})
        group = row.get("group", "")
        props_file = _property_path(run_dir, group)
        try:
            props_doc = _read_json(props_file)
        except (OSError, json.JSONDecodeError):
            props_doc = {"harnesses": []}
        harnesses = [h for h in props_doc.get("harnesses", [])
                     if h.get("name") == row.get("selector")]
        properties = [p for h in harnesses for p in h.get("properties", [])]
        function_name = row.get("selector", "").rsplit("::", 1)[-1]
        export_file = run_dir / "evidence" / group / "export.json"
        try:
            export_doc = _read_json(export_file)
        except (OSError, json.JSONDecodeError):
            export_doc = {"harnesses": []}
        export_harness = next((h for h in export_doc.get("harnesses", [])
                               if h.get("name") == row.get("selector")), {})
        prop_file = export_harness.get("file") or next(
            (p.get("file", "") for p in properties
             if p.get("file", "").startswith("/home/runner/work/kani/kani/export/library/core/")), "")
        source_file = _rel_file(prop_file) if prop_file else ""
        source_text = _source(source_root, source_file) if source_file else None
        source_lines = source_text.splitlines() if source_text is not None else []

        success_records = []
        for item in row.get("required_success", []):
            success_total += 1
            message = item.get("message", "")
            cited_ids = list(item.get("property_ids", []))
            cited = [p for p in properties if p.get("id") in cited_ids]
            # Historical exact IDs are rechecked against the matching harness,
            # exact callsite, class, status, and pinned source assertion.
            exact: list[dict[str, Any]] = []
            for p in cited:
                try:
                    line_no = int(p.get("line", 0))
                except (TypeError, ValueError):
                    line_no = 0
                ctx = _source_context(source_text or "", function_name, message,
                                      "assertion", line_no) if source_text else {}
                same_line_asserts = [q for q in properties
                                     if q.get("class") == "assertion"
                                     and PLACEHOLDER in q.get("description", "")
                                     and str(q.get("line")) == str(p.get("line"))]
                source_line = source_lines[line_no - 1] if 0 < line_no <= len(source_lines) else ""
                source_sites = _source_context(source_text or "", function_name, message,
                                               "assertion", line_no) if source_text else {}
                if (p.get("class") == "assertion" and p.get("status") == "SUCCESS"
                        and PLACEHOLDER in p.get("description", "")
                        and _rel_file(p.get("file", "")) == source_file
                        and p.get("id", "").startswith(row.get("selector", "") + ".")
                        and len(same_line_asserts) == 1
                        and line_no in source_sites.get("active_source_role_sites", [])):
                    exact.append({"property_id": p.get("id"), "status": p.get("status"),
                                  "class": p.get("class"), "description": p.get("description"),
                                  "source": ctx})
            helper_binding: dict[str, Any] | None = None
            if row_id == "inactive_pairs_read_free" and source_text:
                helper_line = next((i + 1 for i, line in enumerate(source_lines)
                                    if message in line), None)
                root_region = _function_lines(source_lines, function_name)
                caller_lines = []
                if root_region:
                    caller_lines = [i + 1 for i in range(root_region[0], root_region[1] + 1)
                                    if re.search(r"\binactive\s*\(", source_lines[i])]
                helper_props = [p for p in properties
                                if p.get("class") == "assertion"
                                and p.get("status") == "SUCCESS"
                                and PLACEHOLDER in p.get("description", "")
                                and "::inactive::<" in p.get("id", "")
                                and str(p.get("line")) == str(helper_line)]
                instances = sorted({re.sub(r"\.assertion\.\d+$", "", p["id"])
                                    for p in helper_props})
                if (helper_line is not None and len(caller_lines) == 3
                        and len(instances) == len(caller_lines) == len(helper_props)):
                    helper_binding = {
                        "property_ids": [p["id"] for p in helper_props],
                        "source": {
                            "expansion_context": "generic-helper-callsite-set",
                            "helper": "inactive<T, F>",
                            "helper_assertion_line": helper_line,
                            "caller": function_name,
                            "helper_callsite_lines": caller_lines,
                            "instantiation_ids": instances,
                            "complete_instances_for_source_calls": True,
                        },
                    }
            if helper_binding:
                binding = "EXACT_SUCCESS_SEMANTIC_SET"
                success_exact += 1
                candidates = helper_binding["property_ids"]
            elif len(exact) == 1:
                binding = "EXACT_SUCCESS_SEMANTIC"
                success_exact += 1
                candidates = [exact[0]["property_id"]]
            else:
                # Macro placeholders carry no message discriminator. Keep the
                # full same-callsite candidate set and never choose by ordinal.
                callsite = item.get("assertion_call_lines", [])
                macro_callsite = _macro_invocation(source_lines, function_name)
                generated_lines = {str(line) for line in row.get("source_anchors", [])
                                   if isinstance(line, int)}
                if macro_callsite:
                    generated_lines.add(str(macro_callsite[0]))
                candidates_props = [p for p in properties
                                    if p.get("class") == "assertion"
                                    and p.get("status") == "SUCCESS"
                                    and PLACEHOLDER in p.get("description", "")
                                    and _rel_file(p.get("file", "")) == source_file
                                    and p.get("id", "").startswith(row.get("selector", "") + ".")
                                    and (str(p.get("line")) in generated_lines
                                         or (not macro_callsite and str(p.get("line")) in {str(x) for x in callsite}))]
                candidates = [p.get("id") for p in candidates_props]
                binding = "CANDIDATES_PENDING" if candidates else "NO_PROPERTY_CANDIDATE"
                if candidates:
                    success_candidates += 1
            src_sites = _source_context(source_text or "", function_name, message,
                                        "assertion", None) if source_text else {}
            src_sites["source_file"] = source_file
            src_sites["source_sha"] = SOURCE_SHA
            success_records.append({
                "message": message,
                "property_ids_from_historical_receipt": cited_ids,
                "binding": binding,
                "candidate_property_ids": candidates,
                "candidate_property_status": "SUCCESS",
                "candidate_binding_source": helper_binding["source"] if helper_binding else None,
                "placeholder_preserved": any(PLACEHOLDER in p.get("description", "")
                                              for p in cited + [q for q in properties if q.get("id") in candidates]),
                "source": src_sites,
            })
            if binding not in ("EXACT_SUCCESS_SEMANTIC", "EXACT_SUCCESS_SEMANTIC_SET"):
                gaps.append({"row": row_id, "kind": "success_property_binding",
                             "message": message,
                             "missing_same_compilation_metadata": [
                                 "property ID to macro-expanded assertion/message-token mapping",
                                 "expanded assertion source span or expansion backtrace",
                                 "macro definition instance and substituted arguments",
                             ]})

        cover_records = []
        for item in row.get("required_covers", []):
            cover_total += 1
            message = item.get("message", "")
            property_id = item.get("property_id")
            p = next((x for x in properties if x.get("id") == property_id), None)
            prop_line = None
            if p is not None:
                try:
                    prop_line = int(p.get("line", 0))
                except (TypeError, ValueError):
                    pass
            src = _source_context(source_text or "", function_name, message,
                                  "cover", prop_line) if source_text else {}
            src["source_file"] = source_file
            src["source_sha"] = SOURCE_SHA
            exact_prop = bool(p and p.get("class") == "cover"
                              and p.get("status") == "SATISFIED"
                              and p.get("description") == message)
            if exact_prop:
                cover_exact += 1
            semantic = bool(exact_prop and src.get("active_source_role_sites")
                            and src.get("source_role_order_after_assumptions_and_call"))
            if semantic:
                cover_semantic += 1
            cover_records.append({
                "message": message,
                "property_id": property_id,
                "property_status": p.get("status") if p else None,
                "property_class": p.get("class") if p else None,
                "property_description": p.get("description") if p else None,
                "binding": "EXACT_SAT_COVER_SEMANTIC" if semantic else
                           ("EXACT_PROPERTY_SOURCE_CONTEXT_GAP" if exact_prop else "PROPERTY_BINDING_GAP"),
                "source": src,
                "claim_limit": "SAT cover only; does not establish domain completeness or theorem validity",
            })
            if not semantic:
                gaps.append({"row": row_id, "kind": "cover_source_semantics",
                             "message": message,
                             "property_id": property_id,
                             "missing_same_compilation_metadata": [
                                 "cover property to expanded source expression/source span mapping",
                                 "macro expansion call chain when the cover is macro-generated",
                                 "source control-flow reachability after the actual target call",
                             ]})
        out_rows[row_id] = {"success": success_records, "covers": cover_records}

    return {
        "schema": "ch8-s1-06-semantic-bindings-v1",
        "source_sha": SOURCE_SHA,
        "source_case_audit": SOURCE_CASE_AUDIT,
        "rows": out_rows,
        "summary": {
            "required_success_messages": success_total,
            "success_exact_semantic": success_exact,
            "success_pending_with_candidates": success_candidates,
            "required_covers": cover_total,
            "covers_exact_property": cover_exact,
            "covers_semantic_source_role_order": cover_semantic,
            "source_case_cover_counts": {
                case: sum(1 for row in out_rows.values() for cover in row["covers"]
                          if cover["source"].get("source_case") == case)
                for case in SOURCE_CASE_AUDIT
            },
            "gaps": len(gaps),
            "proof_credit": "NONE",
            "domain_completeness_claim": False,
        },
        "gaps": gaps,
    }
