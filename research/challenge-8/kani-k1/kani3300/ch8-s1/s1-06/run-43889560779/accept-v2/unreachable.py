"""Conservative offline classification of retained UNREACHABLE properties.

The function consumes only structured request/group evidence and a pinned-source
reader.  ``source_access`` is either a callable taking a repository-relative
path and returning UTF-8 text, or a mapping from path to UTF-8 text.  It never
executes commands or infers a role from an identifier's helper name.
"""
from __future__ import annotations

import collections
import re
import subprocess


CHECK_BUCKETS = ("failure", "unreachable", "undetermined", "error", "unknown", "other")
COVER_BUCKETS = ("satisfied", "unsatisfiable", "unreachable", "undetermined", "error", "unknown", "other")
STD_SOURCE_COMMIT = "5be85699b8826e3286c0bf89efb9affefac0acb5"


def _get(reader, path):
    try:
        return reader(path) if callable(reader) else reader[path]
    except (KeyError, FileNotFoundError, OSError, TypeError):
        return None


def _source_path(record):
    file = record.get("file")
    if not isinstance(file, str):
        return None
    marker = "/export/"
    if marker in file:
        file = file.split(marker, 1)[1]
    elif file.startswith("/home/runner/work/kani/kani/export/"):
        file = file.split("/home/runner/work/kani/kani/export/", 1)[1]
    if file.startswith("library/"):
        return file
    return None


def _function(record):
    loc = record.get("location_display")
    if isinstance(loc, str) and " in function " in loc:
        return loc.rsplit(" in function ", 1)[1]
    return None


def _context(text, line, radius=2):
    if not isinstance(text, str) or not isinstance(line, (str, int)):
        return None
    try:
        n = int(line)
    except (TypeError, ValueError):
        return None
    lines = text.splitlines()
    if n < 1 or n > len(lines):
        return None
    lo, hi = max(1, n - radius), min(len(lines), n + radius)
    return {"start_line": lo, "end_line": hi,
            "lines": [{"line": i, "text": lines[i - 1]} for i in range(lo, hi + 1)]}


def _post_contract_anchors(text):
    if not isinstance(text, str):
        return []
    return [{"line": i, "text": line.strip()}
            for i, line in enumerate(text.splitlines(), 1)
            if "kani::ensures" in line and "sorting_model::post" in line]


def _buckets(harness, key, expected):
    value = harness.get(key)
    if not isinstance(value, dict) or any(not isinstance(value.get(k), list) for k in expected):
        return None
    return value


def _domain(record, path, fn):
    if path is None:
        return "UNKNOWN_SOURCE_DOMAIN"
    if path.startswith("library/core/src/slice/sort/shared/smallsort/verify/"):
        if fn and "sorting_model" in fn:
            return "SMALLSORT_VERIFICATION_MODEL"
        return "SMALLSORT_HARNESS"
    if path.startswith("library/core/src/slice/sort/shared/smallsort"):
        return "SMALLSORT_IMPLEMENTATION"
    if path.startswith("library/kani_core/") or "__CPROVER" in str(record.get("id", "")):
        return "CONTRACT_RUNTIME_OR_GENERATED"
    if path.startswith("library/core/"):
        return "CORE_LIBRARY_HELPER"
    return "UNKNOWN_SOURCE_DOMAIN"


def _row_length(row, source_access):
    value = row.get("N")
    try:
        return int(value), "request.N"
    except (TypeError, ValueError):
        pass
    # The two PFC controls omit N from the request, but their selected source
    # functions have literal two-element vectors. Derive that only from pinned
    # source text and an exact selector-to-function match.
    selector = row.get("selector", "")
    if "sorting_entry_controls::" in selector:
        function = selector.rsplit("::", 1)[-1]
        path = "library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs"
        source = _get(source_access, path)
        if source:
            match = re.search(r"\bfn\s+" + re.escape(function) + r"\s*\([^)]*\)\s*\{", source)
            if match:
                body = source[match.end():]
                vector = re.search(r"\blet\s+mut\s+v\s*=\s*\[([^\]]*)\]", body)
                if vector:
                    elements = [piece.strip() for piece in vector.group(1).split(",") if piece.strip()]
                    if elements:
                        return len(elements), "pinned sorting_entry_controls.rs vector literal"
    return None, "exact length absent"


def _site_decision(role, record, row, path, fn, source_access):
    """Resolve only sites whose source guard and row domain establish exclusion."""
    description = record.get("description", "")
    if not isinstance(description, str) or not re.match(
            r"^(attempt to |index out of bounds:|division by zero|remainder with a divisor of zero)",
            description):
        return "UNKNOWN_ASSERTION_KIND", "description is not a recognized generated arithmetic/bounds check"
    line = record.get("line")
    try:
        line = int(line)
    except (TypeError, ValueError):
        return "UNKNOWN_APPLICABILITY", "numeric source line is absent"
    length, length_basis = _row_length(row, source_access)
    if role == "DEPENDENCY_ASSERTION":
        return "UNKNOWN_OBLIGATION_APPLICABILITY", (
            "source site is a generated core-helper safety check; export lacks exact caller/target-domain "
            "and check-reachability binding, so helper status is not an exemption")
    if role == "HARNESS_ASSERTION_OR_COVER":
        if path.endswith("/verify/sorting_entry_smoke.rs") and line == 137 and length is not None and length != 1:
            return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                f"pinned smoke_exact_n source guards this assertion with exact_n == 1; domain N={length} "
                f"({length_basis}) makes that branch false")
        if path.endswith("/verify/sorting_entry_smoke.rs") and line == 23 and length in (0, 1):
            return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                f"pinned invoke! source computes n + 16 only in the n >= 2 arm; domain N={length} "
                f"({length_basis}) selects the other arm")
        return "UNKNOWN_HARNESS_ASSERTION_APPLICABILITY", (
            "exact harness statement is retained, but its branch condition is not excluded by the request domain")
    if role == "POST_PREDICATE_SAFETY_CHECK" or role == "MODEL_POST_PREDICATE_SAFETY_CHECK":
        if path.endswith("/verify/sorting_model.rs") and line in (97, 100) and length in (0, 1):
            return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                f"pinned smoke_exact_n harness and PFC target have N={length} ({length_basis}); all matching "
                "post invocations are length N or one-element canaries, so active_post's first-loop i=1 guard "
                "excludes its line 97/100 sites. Its later i=0 loop is deliberately not exempted")
        return "UNKNOWN_OBLIGATION_BINDING", (
            "property is an arithmetic/bounds check inside the post predicate; export does not distinguish "
            "target-ensures evaluation from harness invocation or establish its domain at this site")
    if role == "TARGET_OR_MODEL_ASSERTION":
        if path.endswith("/verify/sorting_entry_smoke.rs") and line == 137 and length is not None and length != 1:
            return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                f"pinned smoke_exact_n source guards this assertion with exact_n == 1; domain N={length} "
                f"({length_basis}) makes that branch false")
        if not path.endswith("/slice/sort/shared/smallsort.rs"):
            return "UNKNOWN_TARGET_SECTION_APPLICABILITY", (
                "source assertion is in the verification model or another target site; no exact required-section rule applies")
        target_text = row.get("target") or ""
        target_type = row.get("type")
        copy_network_route = (
            target_type == "u8" and "UnstableSmallSort" in target_text and length is not None and length <= 3
        )
        if length is not None:
            if line in (146, 167, 183, 186) and row.get("type") in {"u8", "NonCopyByte"}:
                type_path = "library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs"
                type_source = _get(source_access, type_path) or ""
                smallsort_source = _get(source_access, path) or ""
                byte_layout = (row.get("type") == "u8" or
                               ("#[repr(transparent)]" in type_source and
                                "struct NonCopyByte(u8)" in type_source))
                constants = all(token in smallsort_source for token in
                                ("SMALL_SORT_GENERAL_SCRATCH_LEN: usize = SMALL_SORT_GENERAL_THRESHOLD + 16",
                                 "SMALL_SORT_NETWORK_SCRATCH_LEN: usize = SMALL_SORT_NETWORK_THRESHOLD",
                                 "SMALL_SORT_GENERAL_THRESHOLD: usize = 32",
                                 "SMALL_SORT_NETWORK_THRESHOLD: usize = 32"))
                if byte_layout and constants:
                    return "ALLOWED_NON_OVERFLOWING_TYPE_SIZE_GUARD", (
                        f"pinned dispatch expression multiplies a one-byte {row.get('type')} by the pinned "
                        "32/48-element scratch constants; generated overflow guard cannot overflow")
            if line in (734, 735) and length < 4:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"sort4_stable requires a four-element region; exact domain N={length} ({length_basis}) is smaller")
            if line == 268 and length < 16:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"the pointer-add site is guarded by len >= 16; exact domain N={length} ({length_basis}) is smaller")
            if line == 381 and length < 18:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"small_sort_network sets no_merge = len < 18 and returns before the second-region site; "
                    f"exact domain N={length} ({length_basis}) is smaller")
            if copy_network_route and line in (251, 256, 291):
                return "ALLOWED_NON_SELECTED_SPECIALIZATION_BRANCH", (
                    "pinned u8 Copy impl selects small_sort_network when has_efficient_in_place_swap is true; "
                    "the small_sort_general_with_scratch source site belongs to the unselected general route")
            if copy_network_route and line in (917, 933, 934, 935):
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"pinned u8 Copy impl selects small_sort_network; its no_merge = len < 18 guard returns "
                    f"before bidirectional_merge for exact N={length} ({length_basis})")
            if line == 350 and length < 2:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"small_sort_network returns at len < 2 before this division; exact domain N={length} ({length_basis})")
            if line in (251, 256, 291) and length < 2:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"small_sort_general_with_scratch returns at len < 2 before this site; exact domain N={length} ({length_basis})")
            if line in (917, 933, 934, 935) and length < 2:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"the selected small-sort implementation returns for len < 2 before merge; exact domain N={length} ({length_basis})")
            if line == 61 and length < 2:
                return "ALLOWED_EXPECTED_BRANCH_UNREACHABLE", (
                    f"StableSmallSortTypeImpl calls insertion_sort_shift_left only when len >= 2; exact domain N={length} ({length_basis})")
        return "UNKNOWN_TARGET_SECTION_APPLICABILITY", (
            "target safety-check site is exact, but retained row/domain metadata does not establish that this site is "
            "outside the required target path or that its containing section is optional")
    return "UNKNOWN_ROLE_OR_APPLICABILITY", "source-site role does not match a closed decision rule"


def _classify_role(record, row, path, fn, source, pfc_bound):
    """Only make role claims that have a pinned source-site anchor."""
    id_ = record.get("id", "")
    if path is None or source is None:
        return "UNKNOWN", "NO_PINNED_SOURCE_SITE"
    line = record.get("line")
    try:
        n = int(line)
    except (TypeError, ValueError):
        return "UNKNOWN", "NO_NUMERIC_SOURCE_LINE"
    # These are safety assertions inside the predicate body, not assertions of
    # the predicate's Boolean postcondition. The same monomorphized function
    # can be called from a target ensures clause or a harness; export records do
    # not retain the originating callsite/macro instance.
    if fn and "sorting_model::active_post" in fn:
        excerpt = _context(source, n, 3)
        if not excerpt:
            return "UNKNOWN", "POST_SITE_LINE_UNRESOLVED"
        if row.get("mode") == "PFC" and pfc_bound:
            return "POST_PREDICATE_SAFETY_CHECK", "PINNED_ACTIVE_POST_BODY; PFC_TARGET_MATCHED; CALLSITE_BINDING_ABSENT"
        if row.get("mode") == "PFC":
            return "POST_PREDICATE_SAFETY_CHECK", "PINNED_ACTIVE_POST_BODY; PFC_TARGET_MISSING_OR_UNBOUND; CALLSITE_BINDING_ABSENT"
        return "MODEL_POST_PREDICATE_SAFETY_CHECK", "PINNED_ACTIVE_POST_BODY_WITHOUT_PFC_TARGET_BINDING"
    # Harness sites are reported separately; they are not presumed equivalent
    # to target assertions or contract obligations.
    if path.endswith("/verify/sorting_entry_smoke.rs") or path.endswith("/verify/sorting_entry_controls.rs"):
        return "HARNESS_ASSERTION_OR_COVER", "PINNED_HARNESS_SOURCE_SITE"
    # A source assertion in an implementation body is a target/model operation;
    # whether it is an explicit required relation is left unresolved below.
    if path.startswith("library/core/src/slice/sort/shared/smallsort"):
        return "TARGET_OR_MODEL_ASSERTION", "PINNED_SMALLSORT_IMPLEMENTATION_SITE"
    if path.startswith("library/core/"):
        return "DEPENDENCY_ASSERTION", "PINNED_CORE_HELPER_SITE"
    return "UNKNOWN", "SOURCE_ROLE_RULE_NOT_ESTABLISHED"


def analyze_groups(request, groups_data, source_access):
    """Return exact row/property classifications for check and cover UNREACHABLE.

    ``request`` is the structured CI request with ``rows``. ``groups_data`` is
    a mapping keyed by the group id in a request row's evidence ``group`` field;
    each value has ``properties`` and optionally ``export`` and ``receipt`` JSON
    objects (or a path-like mapping with those keys already decoded).
    """
    req_rows = request.get("rows") if isinstance(request, dict) else None
    if not isinstance(req_rows, list):
        return {"schema": "ch8-s1-unreachable-analysis-v1", "records": [],
                "unknown": ["REQUEST_ROWS_MISSING_OR_MALFORMED"], "summary": {}}
    rows_by_id = {r.get("id"): r for r in req_rows if isinstance(r, dict)}
    group_rows = {}
    execution_groups = request.get("execution_groups", [])
    if isinstance(execution_groups, list):
        for execution_group in execution_groups:
            if not isinstance(execution_group, dict):
                continue
            group_id = execution_group.get("id")
            row_ids = execution_group.get("row_ids", [])
            if isinstance(group_id, str) and isinstance(row_ids, list):
                for row_id in row_ids:
                    row = rows_by_id.get(row_id)
                    if row is not None:
                        group_rows[(group_id, row.get("selector"))] = row
    records, unknown = [], []
    contract_source = _get(source_access, "library/core/src/slice/sort/shared/smallsort.rs")
    post_anchors = _post_contract_anchors(contract_source)
    for group_id, group in groups_data.items():
        if not isinstance(group, dict):
            unknown.append({"group": group_id, "reason": "GROUP_DATA_MALFORMED"})
            continue
        props_doc = group.get("properties")
        if isinstance(props_doc, str):
            # File contents may be supplied directly; otherwise callers pass
            # decoded structured JSON to keep this API filesystem-agnostic.
            import json
            try:
                props_doc = json.loads(props_doc)
            except ValueError:
                unknown.append({"group": group_id, "reason": "PROPERTIES_JSON_MALFORMED"})
                continue
        harnesses = props_doc.get("harnesses") if isinstance(props_doc, dict) else None
        if not isinstance(harnesses, list):
            unknown.append({"group": group_id, "reason": "RICH_HARNESSES_MISSING"})
            continue
        export_doc = group.get("export")
        export_harnesses = export_doc.get("harnesses", []) if isinstance(export_doc, dict) else []
        export_by_name = {h.get("name"): h for h in export_harnesses if isinstance(h, dict)}
        for rich_h in harnesses:
            if not isinstance(rich_h, dict):
                unknown.append({"group": group_id, "reason": "RICH_HARNESS_MALFORMED"})
                continue
            selector = rich_h.get("name")
            row = group_rows.get((group_id, selector))
            if row is None:
                unknown.append({"group": group_id, "selector": selector,
                                "reason": "HARNESS_NOT_IN_REQUEST"})
                continue
            exp_h = export_by_name.get(selector, {})
            checks = _buckets(exp_h, "checks", CHECK_BUCKETS)
            covers = _buckets(exp_h, "covers", COVER_BUCKETS)
            check_ids = set(checks["unreachable"]) if checks else None
            cover_ids = set(covers["unreachable"]) if covers else None
            rich_records = rich_h.get("properties")
            if not isinstance(rich_records, list):
                unknown.append({"group": group_id, "row": row.get("id"),
                                "reason": "RICH_PROPERTY_LIST_MISSING"})
                continue
            for prop in rich_records:
                if not isinstance(prop, dict) or prop.get("status") != "UNREACHABLE":
                    continue
                pid = prop.get("id")
                if not isinstance(pid, str):
                    unknown.append({"group": group_id, "row": row.get("id"),
                                    "reason": "UNREACHABLE_ID_MISSING"})
                    continue
                if prop.get("class") == "cover" and cover_ids is not None and pid in cover_ids:
                    status_kind = "cover"
                elif prop.get("class") != "cover" and check_ids is not None and pid in check_ids:
                    status_kind = "check"
                else:
                    status_kind = "UNKNOWN_INVENTORY_BINDING"
                path = _source_path(prop)
                source = _get(source_access, path) if path else None
                fn = _function(prop)
                attrs = exp_h.get("attributes", {}) if isinstance(exp_h, dict) else {}
                mode_attr = attrs.get("kind", {}) if isinstance(attrs, dict) else {}
                pfc = mode_attr.get("ProofForContract", {}) if isinstance(mode_attr, dict) else {}
                actual_target = pfc.get("target_fn") if isinstance(pfc, dict) else None
                contract = exp_h.get("contract", {}) if isinstance(exp_h, dict) else {}
                contracted_symbol = contract.get("contracted_function_name") if isinstance(contract, dict) else None
                normalize = lambda s: re.sub(r"\s+", "", s) if isinstance(s, str) else None
                pfc_bound = bool(row.get("mode") == "PFC" and row.get("target") and
                                 normalize(actual_target) == normalize(row.get("target")))
                role, role_basis = _classify_role(prop, row, path, fn, source, pfc_bound)
                decision_basis = None
                target = row.get("target")
                in_target_domain = (path or "").startswith("library/core/src/slice/sort/shared/smallsort")
                if role in {"POST_PREDICATE_SAFETY_CHECK", "MODEL_POST_PREDICATE_SAFETY_CHECK"}:
                    decision, decision_basis = _site_decision(role, prop, row, path, fn, source_access)
                elif status_kind == "UNKNOWN_INVENTORY_BINDING" or role == "UNKNOWN":
                    decision = "UNKNOWN"
                elif status_kind == "cover":
                    decision = "REVIEW_NEGATIVE_COMPANION_COVER"
                elif role == "HARNESS_ASSERTION_OR_COVER":
                    decision, decision_basis = _site_decision(role, prop, row, path, fn, source_access)
                else:
                    decision, decision_basis = _site_decision(role, prop, row, path, fn, source_access)
                context = _context(source, prop.get("line"), 2) if source else None
                records.append({
                    "group": group_id, "row_id": row.get("id"), "selector": selector,
                    "property_id": pid, "class": prop.get("class"),
                    "status": prop.get("status"), "status_kind": status_kind,
                    "description": prop.get("description"),
                    "site": {"export_file": prop.get("file"), "source_path": path,
                             "line": prop.get("line"), "location_display": prop.get("location_display"),
                             "function": fn, "source_context": context},
                    "domain": _domain(prop, path, fn), "role": role,
                    "role_basis": role_basis,
                    "target": {"requested_target": target,
                               "exported_pfc_target": actual_target,
                               "relation": ("EXACT_PFC_TARGET_MATCH" if pfc_bound else
                                            "SAME_SMALLSORT_SOURCE_DOMAIN" if in_target_domain else "DEPENDENCY_OR_UNKNOWN")},
                    "wrapper": {"relation": "PROOF_FOR_CONTRACT_TARGET_MATCH" if pfc_bound else
                                "PROOF_FOR_CONTRACT_TARGET_EXPORTED_REQUEST_TARGET_MISSING_OR_MISMATCH" if row.get("mode") == "PFC" and actual_target else
                                "NO_EXACT_PFC_WRAPPER_BINDING",
                                "exported_contracted_function_name": contracted_symbol,
                                "post_contract_source_anchors": post_anchors if "POST_PREDICATE_SAFETY_CHECK" in role else [],
                                "note": "Source anchors establish that smallsort targets declare this post; a same-compilation wrapper-to-property binding is separate metadata."},
                    "decision": decision,
                    "decision_basis": decision_basis,
                    "evidence_anchor": {"group": group_id, "harness": selector,
                                        "property_id": pid, "source_path": path,
                                        "line": prop.get("line"),
                                        "class_status": [prop.get("class"), prop.get("status")]}
                })
    # The expected row/property must not be deduplicated: two harnesses can
    # report the same underlying ID and each is a separate exact observation.
    decisions = collections.Counter(r["decision"] for r in records)
    roles = collections.Counter(r["role"] for r in records)
    domains = collections.Counter(r["domain"] for r in records)
    return {"schema": "ch8-s1-unreachable-analysis-v1", "records": records,
            "unknown": unknown,
            "summary": {"records": len(records), "checks": sum(r["status_kind"] == "check" for r in records),
                        "covers": sum(r["status_kind"] == "cover" for r in records),
                        "decisions": dict(sorted(decisions.items())),
                        "roles": dict(sorted(roles.items())),
                        "domains": dict(sorted(domains.items())),
                        "mandatory_unreachable_blockers": sum(r["decision"] == "BLOCK_MANDATORY_POST_UNREACHABLE" for r in records),
                        "unknown_bindings": sum(r["decision"].startswith("UNKNOWN") for r in records),
                        "proof_credit": "NONE"}}


def analyze(run, request, std_repo):
    """Load only compact structured group evidence and classify it.

    ``run`` is the S1 run directory; ``std_repo`` is the std git repository.
    Source reads use only ``git show`` at the fixed pinned commit below (or a
    caller-supplied accessor that itself reads that commit). The only run files read are
    ``evidence/*/{properties,export,receipt}.json``. Source files are opened
    only for paths named by those structured property records and the
    smallsort contract declaration file.
    """
    import json
    from pathlib import Path

    run_path = Path(run)
    groups = {}
    read_errors = []
    for properties_path in sorted((run_path / "evidence").glob("*/properties.json")):
        group_id = properties_path.parent.name
        group = {}
        for name in ("properties", "export", "receipt"):
            path = properties_path.parent / (name + ".json")
            try:
                group[name] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                read_errors.append({"group": group_id, "file": name + ".json",
                                    "reason": type(exc).__name__})
        groups[group_id] = group

    if callable(std_repo):
        source_access = std_repo
    else:
        std_path = Path(std_repo)
        def source_access(relative_path):
            try:
                return subprocess.run(
                    ["git", "-C", str(std_path), "show", STD_SOURCE_COMMIT + ":" + relative_path],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                ).stdout.decode("utf-8")
            except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
                return None

    result = analyze_groups(request, groups, source_access)
    result["run_evidence_root"] = "evidence/"
    result["source_commit"] = STD_SOURCE_COMMIT
    result["structured_read_errors"] = read_errors
    result["summary"]["structured_read_errors"] = len(read_errors)
    return result
