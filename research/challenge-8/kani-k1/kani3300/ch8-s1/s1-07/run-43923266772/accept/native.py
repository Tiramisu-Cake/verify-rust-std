"""Conservative interpretation of embedded stock Kani metadata for S1-07.

This module validates retained native JSON records and attaches only the
identity/attribute edges the 0aac producer actually exports. It deliberately
does not infer an implementation from mangled symbols or bind properties to
harnesses from source locations alone.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PRODUCER = "0aac16ef62da9e9d5645782d458593e5d78143ba"
PRODUCER_LIMITS = [
    {
        "field": "manual PFC target definition DefId grouping",
        "available": True,
        "producer_anchor": "kani-compiler/src/kani_middle/metadata.rs:81-95",
        "reason": "manual proof_for_contract resolution returns def; ContractedFunction is keyed by def.def_id() and lists the harness",
    },
    {
        "field": "selected concrete/monomorphized impl instance identity",
        "available": False,
        "producer_anchor": "kani-compiler/src/kani_middle/metadata.rs:86-94,149-153",
        "reason": "contract metadata retains target definition name/file/harness list; it does not export the specialization selected by the harness or the target instance edge",
    },
    {
        "field": "checked_with / modifies_wrapper / effective contract clause graph",
        "available": False,
        "producer_anchor": "kani-compiler/src/kani_middle/metadata.rs",
        "reason": "native metadata exports the target name and contracted_function_name symbol, not resolution edges or clause bodies",
    },
    {
        "field": "property-to-harness origin / cover predicate expansion",
        "available": False,
        "producer_anchor": "native proof_harnesses record schema",
        "reason": "proof_harnesses contains harness records only; no property IDs, source origins, cover predicate, or expansion graph",
    },
    {
        "field": "single compiler-instance identity",
        "available": False,
        "producer_anchor": "binding-metadata.json compilation_id=null",
        "reason": "retained metadata supplies invocation_id and artifact digests but compilation_id is null",
    },
]


def _load(value: Any) -> Any:
    if isinstance(value, (str, Path)):
        p = Path(value)
        if p.is_dir():
            p = p / "collected.json"
        return json.loads(p.read_text(encoding="utf-8"))
    return value


def _norm(value: Any) -> str | None:
    return "".join(str(value).split()) if isinstance(value, str) else None


def _pointer(doc: Any, pointer: str) -> Any:
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        return None
    current = doc
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not re.fullmatch(r'0|[1-9][0-9]*', part):
                return None
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current


def _records(meta_entry: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    checks = {"state": meta_entry.get("state"), "sha256_valid": False,
              "bytes_valid": False, "json_valid": False, "error": None}
    text = meta_entry.get("text")
    if not isinstance(text, str):
        checks["error"] = "embedded text absent"
        return [], checks
    raw = text.encode("utf-8")
    checks["sha256_valid"] = hashlib.sha256(raw).hexdigest() == meta_entry.get("sha256")
    checks["bytes_valid"] = len(raw) == meta_entry.get("bytes")
    try:
        doc = json.loads(text)
        checks["json_valid"] = isinstance(doc, dict)
    except (TypeError, json.JSONDecodeError):
        checks["error"] = "embedded text is not JSON"
        return [], checks
    if not checks["sha256_valid"] or not checks["bytes_valid"]:
        checks["error"] = "embedded content digest/length mismatch"
        return [], checks
    if not checks["json_valid"]:
        checks["error"] = "embedded JSON root is not an object"
        return [], checks
    rows = doc.get("proof_harnesses", [])
    if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
        checks["json_valid"] = False
        checks["error"] = "malformed proof_harnesses list"
        return [], checks
    return rows, checks


def analyze(run: Any, request: Any, pfc_report: Any, semantic_report: Any,
            unreachable_report: Any, control_repo: Any) -> dict[str, Any]:
    """Validate S1-07 stock metadata and annotate the three acceptance reports.

    ``control_repo`` is accepted for API compatibility; producer source anchors
    are pinned constants because this helper performs no mutable-tree reads.
    """
    run_dir = Path(run) if isinstance(run, (str, Path)) else None
    if run_dir and run_dir.is_file():
        run_dir = run_dir.parent
    req = _load(request) if request is not None else {}
    pfc = _load(pfc_report) if pfc_report is not None else {}
    semantic = _load(semantic_report) if semantic_report is not None else {}
    unreachable = _load(unreachable_report) if unreachable_report is not None else {}
    del control_repo

    evidence_dir = run_dir / "evidence" if run_dir else None
    group_data: dict[str, dict[str, Any]] = {}
    integrity: list[dict[str, Any]] = []
    if evidence_dir and evidence_dir.is_dir():
        for path in sorted(evidence_dir.glob("*/binding-metadata.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                integrity.append({"file": str(path), "valid": False, "error": str(exc)})
                continue
            group = doc.get("group_id")
            native = doc.get("native_metadata", [])
            by_path: dict[str, dict[str, Any]] = {}
            for entry in native if isinstance(native, list) else []:
                if not isinstance(entry, dict):
                    continue
                records, checks = _records(entry)
                integrity.append({"group": group, "path": entry.get("path"), **checks})
                if checks["sha256_valid"] and checks["bytes_valid"] and checks["json_valid"]:
                    by_path[str(entry.get("path"))] = {"entry": entry, "records": records}
            group_data[str(group)] = {"doc": doc, "native": by_path}

    def resolve(group: Any, row_id: Any, selector: Any, requested_target: Any) -> dict[str, Any]:
        gd = group_data.get(str(group))
        if not gd:
            return {"status": "NO_GROUP_METADATA"}
        row = next((r for r in gd["doc"].get("rows", [])
                    if isinstance(r, dict) and r.get("row_id") == row_id), None)
        if not row:
            return {"status": "NO_ROW_METADATA"}
        refs = row.get("native_harness_records", [])
        found = []
        invalid_refs = []
        for ref in refs if isinstance(refs, list) else []:
            if not isinstance(ref, dict):
                continue
            source = gd["native"].get(str(ref.get("metadata_path")))
            if source is None:
                invalid_refs.append(ref)
                continue
            record = _pointer({"proof_harnesses": source["records"]}, ref.get("pointer", ""))
            if not isinstance(record, dict):
                invalid_refs.append(ref)
                continue
            if (record.get("pretty_name") == ref.get("name") == selector
                    and record.get("crate_name") == ref.get("crate")):
                attrs = record.get("attributes", {})
                kind = attrs.get("kind", {}) if isinstance(attrs, dict) else {}
                pfc_attr = kind.get("ProofForContract", {}) if isinstance(kind, dict) else {}
                target = pfc_attr.get("target_fn") if isinstance(pfc_attr, dict) else None
                contract = record.get("contract", {})
                native_doc = json.loads(source["entry"]["text"])
                contract_rows = native_doc.get("contracted_functions", [])
                contract_matches = [x for x in contract_rows
                                    if isinstance(x, dict)
                                    and isinstance(x.get("harnesses"), list)
                                    and selector in x["harnesses"]]
                found.append({
                    "metadata_path": ref.get("metadata_path"),
                    "metadata_sha256": source["entry"]["sha256"],
                    "pointer": ref.get("pointer"),
                    "harness": record.get("pretty_name"),
                    "crate": record.get("crate_name"),
                    "source": {"file": record.get("original_file"),
                               "start_line": record.get("original_start_line"),
                               "end_line": record.get("original_end_line")},
                    "pfc_target_fn": target,
                    "pfc_target_matches_report": bool(target and _norm(target) == _norm(requested_target)),
                    "resolved_target_definition_records": [
                        {"function": x.get("function"), "file": x.get("file"),
                         "harness_membership": selector in x.get("harnesses", [])}
                        for x in contract_matches],
                    "manual_target_definition_link": len(contract_matches) == 1,
                    "contracted_function_name": contract.get("contracted_function_name") if isinstance(contract, dict) else None,
                    "contracted_function_name_interpretation": "opaque symbol only; no instance inference",
                    "attributes": attrs,
                    "is_bounded": record.get("is_bounded"),
                    "record_scope": row.get("native_record_scope"),
                })
        return {"status": "EXACT_HARNESS_RECORD" if found else "NO_EXACT_HARNESS_RECORD",
                "records": found, "invalid_refs": invalid_refs}

    group_for = {rid: g['id'] for g in req['execution_groups'] for rid in g['row_ids']}
    harness_annotations = [dict(row_id=r['id'], group=group_for[r['id']],
                               **resolve(group_for[r['id']], r['id'], r['selector'], r.get('target')))
                           for r in req['rows']]
    bindings = pfc.get("bindings", []) if isinstance(pfc, dict) else []
    pfc_annotations = []
    for binding in bindings if isinstance(bindings, list) else []:
        if not isinstance(binding, dict):
            continue
        requested_target = binding.get("target", {}).get("qualified") if isinstance(binding.get("target"), dict) else binding.get("target")
        found = resolve(binding.get("execution_group"), binding.get("id"), binding.get("selector"), requested_target)
        if found.get("records"):
            rec = found["records"][0]
            found["edges_closed"] = ["exact native proof_harnesses selector/crate record"]
            if rec["manual_target_definition_link"]:
                found["edges_closed"].append("manual PFC harness linked to one contracted_functions target-definition record by producer's resolved DefId grouping")
            if rec["pfc_target_matches_report"]:
                found["edges_closed"].append("native ProofForContract target_fn string matches report target")
            found["edges_open"] = ["selected concrete impl/DefPath identity",
                                    "checked_with resolution and check call edge",
                                    "modifies_wrapper resolution and contracted instance identity",
                                    "effective requires/ensures/modifies clauses and source spans",
                                    "property-to-harness/wrapper origin edges",
                                    "same compiler instance identity"]
        pfc_annotations.append({"id": binding.get("id"), "selector": binding.get("selector"), **found})
        binding["native_metadata"] = found

    # Native records attest harness identities only. Keep semantic and UNREACHABLE
    # property rows explicitly unbound; report counts without manufacturing IDs.
    sem_rows = semantic.get("rows", {}) if isinstance(semantic, dict) else {}
    sem_count = len(sem_rows)
    unreach_records = unreachable.get("records", []) if isinstance(unreachable, dict) else []
    unreach_count = len(unreach_records) if isinstance(unreach_records, list) else 0
    annotation = {
        "schema": "s1-07-stock-native-binding-v1",
        "producer_commit": PRODUCER,
        "integrity": {"metadata_entries": len(integrity), "all_valid": bool(integrity) and all(
            x.get("sha256_valid") and x.get("bytes_valid") and x.get("json_valid") for x in integrity),
            "entries": integrity},
        "pfc": pfc_annotations,
        "harnesses": harness_annotations,
        "semantic_property_binding": {
            "rows_seen": sem_count, "native_property_origin_records": 0,
            "status": "OPEN_PROPERTY_ORIGIN_AND_COVER_EXPANSION",
            "reason": "stock proof_harnesses has harness records, no assertion/property/cover IDs or origins",
        },
        "unreachable_property_binding": {
            "rows_seen": unreach_count, "native_property_origin_records": 0,
            "status": "OPEN_PROPERTY_ORIGIN",
            "reason": "native metadata can corroborate a harness record but cannot bind an UNREACHABLE property ID to its source assertion/callsite",
        },
        "producer_limits": PRODUCER_LIMITS,
    }
    if isinstance(semantic, dict):
        semantic["native_metadata_binding"] = annotation["semantic_property_binding"]
    if isinstance(unreachable, dict):
        unreachable["native_metadata_binding"] = annotation["unreachable_property_binding"]
    return annotation
