"""Offline evidence binding for S1-07 proof-for-contract (PFC) rows.

This module deliberately consumes only retained structured JSON and source
text.  It does not try to demangle Rust symbols or infer a target impl from a
symbol spelling.  Such inference needs compiler metadata from the same build.
"""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any


PRODUCER_COMMIT = "0aac16ef62da9e9d5645782d458593e5d78143ba"
PINNED_CONTROL_COMMIT = "b37f6f75c5b7b77e84297cd7104f9c0868502fd4"
PINNED_STD_COMMIT = "5be85699b8826e3286c0bf89efb9affefac0acb5"


class _GitFile:
    def __init__(self, repo: Path, commit: str, relative: str) -> None:
        self.repo = repo
        self.commit = commit
        self.relative = relative

    @property
    def label(self) -> str:
        return f"git:{self.commit}:{self.relative}"

    def __str__(self) -> str:
        return self.label


def _load(value: Any) -> Any:
    if isinstance(value, (str, Path)):
        p = Path(value)
        if p.is_dir():
            p = p / "collected.json"
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    return value


def _root(value: Any) -> Path | None:
    if not isinstance(value, (str, Path)):
        return None
    p = Path(value)
    return p.parent if p.is_file() else p


def _rows(doc: Any) -> list[dict[str, Any]]:
    if isinstance(doc, dict):
        rows = doc.get("rows")
        if isinstance(rows, list):
            return [x for x in rows if isinstance(x, dict)]
        # Request documents may nest rows under variants.
        found: list[dict[str, Any]] = []
        variants = doc.get("variants", [])
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict):
                    found.extend(_rows(variant))
        return found
    return []


def _norm(s: Any) -> str | None:
    if not isinstance(s, str):
        return None
    return re.sub(r"\s+", "", s)


def _split_args(s: str) -> list[str]:
    """Split macro args on top-level commas, respecting Rust delimiters."""
    out: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    for i, ch in enumerate(s):
        if ch in pairs:
            stack.append(pairs[ch])
        elif stack and ch == stack[-1]:
            stack.pop()
        elif ch == "," and not stack:
            out.append(s[start:i].strip())
            start = i + 1
    tail = s[start:].strip()
    if tail:
        out.append(tail)
    return out


def _source_path(repo: Path, file: Any, commit: str = PINNED_STD_COMMIT) -> _GitFile | None:
    if not isinstance(file, str):
        return None
    # Evidence paths are repository relative; compiler export paths can have
    # an absolute CI prefix, so match their repository suffix safely. Return a
    # git object reference, never a working-tree path.
    rel = file.replace("\\", "/").lstrip("/")
    if rel.startswith("library/"):
        return _GitFile(repo, commit, rel)
    marker = "/library/"
    if marker in file:
        return _GitFile(repo, commit, "library/" + file.split(marker, 1)[1])
    # Only accept paths that are in the expected source subtree.
    if rel.startswith("library/"):
        return _GitFile(repo, commit, rel)
    return None


def _lines(path: _GitFile | Path | None) -> list[str]:
    if path is None:
        return []
    if isinstance(path, _GitFile):
        result = subprocess.run(
            ["git", "-C", str(path.repo), "show", f"{path.commit}:{path.relative}"],
            capture_output=True, check=False,
        )
        if result.returncode != 0:
            return []
        return result.stdout.decode("utf-8", errors="replace").splitlines()
    return path.read_text(encoding="utf-8").splitlines()


def _at(path: _GitFile | Path | None, line: int | None, text: str | None = None) -> dict[str, Any] | None:
    if path is None or line is None or line < 1:
        return None
    lines = _lines(path)
    if line > len(lines):
        return None
    label = path.label if isinstance(path, _GitFile) else str(path)
    return {"file": label, "line": line, "text": text if text is not None else lines[line - 1].strip()}


def _macro_info(std_repo: Path, file: Any, locations: Any, selector: str) -> dict[str, Any]:
    source_path = _source_path(std_repo, file)
    if source_path is None:
        return {"status": "PENDING", "gap": "source file for macro invocation is absent"}
    lines = _lines(source_path)
    call = None
    invocation = None
    if isinstance(locations, list):
        for loc in locations:
            if not isinstance(loc, dict):
                continue
            n = loc.get("line")
            src = loc.get("source")
            if isinstance(src, str) and "!" in src and isinstance(n, int):
                m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*!\s*\(", src)
                if m:
                    call, invocation = m.group(1), _at(source_path, n, src.strip())
                    break
    if call is None:
        # Direct, non-macro harnesses have a function definition as their
        # source anchor. This is explicit metadata, not ordinal matching.
        for loc in locations if isinstance(locations, list) else []:
            if isinstance(loc, dict) and isinstance(loc.get("line"), int):
                n = loc["line"]
                if 1 <= n <= len(lines) and re.search(r"\bfn\s+" + re.escape(selector.split("::")[-1]) + r"\b", lines[n - 1]):
                    invocation = _at(source_path, n)
                    call = "direct-function"
                    break
    definition = None
    if call and call != "direct-function":
        for i, line in enumerate(lines, 1):
            if re.search(r"\bmacro_rules!\s*" + re.escape(call) + r"\b", line):
                definition = _at(source_path, i)
                # The defining pattern and generated proof attribute are
                # nearby; retain line anchors separately.
                end = min(len(lines), i + 14)
                for j in range(i, end):
                    if "proof_for_contract" in lines[j]:
                        definition["proof_for_contract"] = _at(source_path, j + 1)
                        break
                break
    source_attribute = None
    if call == "direct-function" and invocation:
        n = invocation["line"]
        for j in range(max(1, n - 8), n):
            if "proof_for_contract" in lines[j - 1]:
                source_attribute = _at(source_path, j)
                break
    macro_args = None
    if invocation and call not in (None, "direct-function"):
        # Read the complete invocation from source; intake snippets can be
        # truncated at a newline for multi-line macro calls.
        n = invocation["line"]
        chunk = "\n".join(lines[n - 1:min(len(lines), n + 12)])
        m = re.search(r"\b" + re.escape(call) + r"\s*!\s*\(", chunk)
        if m:
            begin = m.end()
            depth = 1
            end = begin
            while end < len(chunk) and depth:
                if chunk[end] == "(":
                    depth += 1
                elif chunk[end] == ")":
                    depth -= 1
                end += 1
            if depth == 0:
                macro_args = _split_args(chunk[begin:end - 1])
    if definition and definition.get("proof_for_contract"):
        source_attribute = definition["proof_for_contract"]
    expanded_attribute = None
    if source_attribute:
        raw = source_attribute.get("text", "")
        if macro_args and call not in (None, "direct-function"):
            # The two S1 macro definitions use argument order
            # name,type-or-ty,new,trait,...; substitute exactly those tokens.
            if len(macro_args) > 3:
                raw = raw.replace("$type", macro_args[1]).replace("$ty", macro_args[1])
                raw = raw.replace("$trait", macro_args[3])
        m = re.search(r"proof_for_contract\s*\((.*)\)\s*\]", raw)
        if m:
            expanded_attribute = m.group(1).strip()
    return {
        "name": call,
        "invocation": invocation,
        "definition": definition,
        "source_target_attribute": source_attribute,
        "expanded_target_attribute": expanded_attribute,
        "arguments": macro_args,
        "type_argument": macro_args[1] if macro_args and len(macro_args) > 1 else None,
        "trait_argument": macro_args[3] if macro_args and len(macro_args) > 3 else None,
        "status": "ANCHORED" if invocation else "PENDING",
    }


def _target_sites(std_repo: Path, trait: Any) -> dict[str, Any]:
    path = _GitFile(std_repo, PINNED_STD_COMMIT, "library/core/src/slice/sort/shared/smallsort.rs")
    lines = _lines(path)
    candidates = []
    if not isinstance(trait, str):
        return {"file": str(path), "candidates": [], "status": "PENDING"}
    impl_re = re.compile(r"^\s*impl(?:<[^>]*>)?(?:\s+[^{}]+?)?\s+" + re.escape(trait) + r"\s+for\s+([^\s{]+)")
    for i, line in enumerate(lines):
        match = impl_re.search(line)
        if not match:
            continue
        # Scan this impl body to the next top-level impl/trait declaration;
        # retain source attribute lines and method signature as evidence.
        j = i + 1
        while j < len(lines) and not re.match(r"^(?:impl|pub\(crate\) trait|trait)\b", lines[j]):
            j += 1
        body = lines[i:j]
        method = None
        attrs: list[dict[str, Any]] = []
        for k, text in enumerate(body):
            if "kani::requires" in text or "kani::modifies" in text or "kani::ensures" in text:
                attrs.append({"line": i + k + 1, "text": text.strip()})
            if re.search(r"\bfn\s+small_sort\s*<", text):
                method = {"line": i + k + 1, "text": text.strip()}
        if method:
            candidates.append({
                "impl_header": {"line": i + 1, "text": line.strip()},
                "impl_self_type_pattern": match.group(1),
                "method": method,
                "contract_attributes": attrs,
            })
    return {"file": str(path), "candidates": candidates, "status": "PENDING_IMPL_IDENTITY" if len(candidates) != 1 else "SOURCE_CANDIDATE"}


def _property_inventory(root: Path | None, group_id: str | None, selector: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None, dict[str, Any]]:
    if root is None:
        return [], [], None, {"count": 0, "sha256": None, "reference": None, "export_sha256": None}
    if not group_id:
        return [], [], None, {"count": 0, "sha256": None, "reference": None, "export_sha256": None}
    evidence_root = root / "evidence" / group_id
    props: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    export_harness = None
    if not evidence_root.is_dir():
        return [], [], None, {"count": 0, "sha256": None, "reference": None, "export_sha256": None}
    p = evidence_root / "properties.json"
    if p.is_file():
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = {}
        matches = [h for h in doc.get("harnesses", []) if isinstance(h, dict) and h.get("name") == selector]
        if len(matches) == 1:
            props = [x for x in matches[0].get("properties", []) if isinstance(x, dict)]
            anchors.append({"kind": "rich_properties", "path": str(p.relative_to(root)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    export = evidence_root / "export.json"
    export_sha = None
    if export.is_file():
        export_sha = hashlib.sha256(export.read_bytes()).hexdigest()
        try:
            doc = json.loads(export.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = {}
        matches = [h for h in doc.get("harnesses", []) if isinstance(h, dict) and h.get("name") == selector]
        if len(matches) == 1:
            export_harness = matches[0]
            anchors.append({"kind": "same_group_export", "path": str(export.relative_to(root)), "sha256": export_sha})
    meta = {
        "count": len(props),
        "sha256": next((x["sha256"] for x in anchors if x["kind"] == "rich_properties"), None),
        "reference": next((x["path"] for x in anchors if x["kind"] == "rich_properties"), None),
        "export_sha256": export_sha,
    }
    return props, anchors, export_harness, meta


def _is_target_contract_site(prop: dict[str, Any]) -> bool:
    """Retain only exact target contract closure sites as candidate anchors."""
    cls = str(prop.get("class", ""))
    ident = str(prop.get("id", ""))
    desc = str(prop.get("description", ""))
    if "sorting_model::post" in desc:
        return True
    # Kani emits the method contract closure as closure#2, with a nested
    # closure#1 for requires/modifies instrumentation. Name matching alone is
    # insufficient, so retain only rows carrying that concrete target path.
    target_closure = "small_sort::<" in ident and ("::{closure#2}" in ident or "::{closure#2}" in str(prop.get("location_display", "")))
    generated_contract_classes = {
        "assertion", "assigns", "single_top_level_call", "no_recursive_call",
        "no_alloc_dealloc_in_requires", "no_alloc_dealloc_in_ensures", "frees",
    }
    if target_closure and cls in generated_contract_classes:
        return True
    # An assigns record can name a contract target without using the closure
    # spelling; require the concrete method path in its own evidence fields.
    return cls.startswith("assigns") and "small_sort" in (ident + " " + desc)


def _producer_anchors(control: Path) -> dict[str, Any]:
    """Anchor the pinned producer behavior used to interpret its symbol field."""
    specs = {
        "target_registration": (
            "kani-compiler/src/kani_middle/metadata.rs",
            "attributes.interpret_for_contract_attribute()",
        ),
        "contract_symbol_export": (
            "kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs",
            "AssignsContract { recursion_tracker, contracted_function_name: modify.mangled_name() }",
        ),
        "wrapper_resolution": (
            "kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs",
            "find_closure(check_instance, contract_attrs.modifies_wrapper.as_str())",
        ),
    }
    out: dict[str, Any] = {}
    for name, (rel, needle) in specs.items():
        p = _GitFile(control, PRODUCER_COMMIT, rel)
        found = None
        for i, line in enumerate(_lines(p), 1):
            if needle in line:
                found = _at(p, i)
                break
        out[name] = found
    return out


def analyze(run: Any, request: Any, std_repo: Any, control_repo: Any) -> dict[str, Any]:
    """Return PFC binding evidence and explicit gaps, without guessing.

    ``run`` and ``request`` may be decoded JSON objects or paths to JSON files
    (``run`` may also be the run directory). Repositories may be ``Path``
    objects or path strings. Source anchors are loaded from the pinned git
    objects named in this module, never from the checkouts' working trees.
    """
    run_doc, req_doc = _load(run), _load(request)
    std = Path(std_repo)
    control = Path(control_repo)
    root = _root(run)
    run_rows = {r.get("id"): r for r in _rows(run_doc) if r.get("mode") == "PFC"}
    request_rows = {r.get("id"): r for r in _rows(req_doc) if r.get("mode") == "PFC"}
    group_by_row: dict[str, str] = {}
    if isinstance(req_doc, dict):
        for group in req_doc.get("execution_groups", []):
            if not isinstance(group, dict) or not isinstance(group.get("id"), str):
                continue
            for row_id in group.get("row_ids", []):
                if isinstance(row_id, str):
                    group_by_row[row_id] = group["id"]
    bindings: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for row_id, row in sorted(run_rows.items()):
        # S1-07 collector no longer embeds structured_preflight. Read the exact
        # same-group export and pinned request source binding directly.
        source = req_doc["source_bindings"][row_id]
        _, _, harness, _ = _property_inventory(root, group_by_row[row_id], row["selector"])
        pf = {"expected_target_fn": source.get("target")}
        attrs = harness.get("attributes", {}) if isinstance(harness.get("attributes"), dict) else {}
        kind = attrs.get("kind", {}) if isinstance(attrs.get("kind"), dict) else {}
        pfc = kind.get("ProofForContract", {}) if isinstance(kind.get("ProofForContract"), dict) else {}
        selector = row.get("selector")
        target = pf.get("expected_target_fn") or source.get("target")
        target_norm = _norm(target)
        attr_target = pfc.get("target_fn")
        attr_matches = bool(target_norm and _norm(attr_target) == target_norm)
        contract = harness.get("contract") if isinstance(harness.get("contract"), dict) else {}
        symbol = contract.get("contracted_function_name")
        source_path = _source_path(std, source.get("file"))
        macro = _macro_info(std, source.get("file"), source.get("locations"), selector or "")
        # Macro arguments are the independent source route to concrete type
        # and trait. For direct harnesses, parse the target attribute itself.
        type_arg = macro.get("type_argument")
        trait_arg = macro.get("trait_argument")
        if macro.get("name") == "direct-function" and isinstance(target, str):
            m = re.match(r"\s*<\s*(.*?)\s+as\s+(.*?)\s*>\s*::\s*small_sort\s*$", target)
            if m:
                type_arg, trait_arg = m.group(1).strip(), m.group(2).strip()
        # A target attr is the fallback source for a split/truncated macro
        # invocation. It corroborates, but does not replace, the callsite.
        if (not type_arg or not trait_arg) and isinstance(target, str):
            m = re.match(r"\s*<\s*(.*?)\s+as\s+(.*?)\s*>\s*::\s*small_sort\s*$", target)
            if m:
                type_arg = type_arg or m.group(1).strip()
                trait_arg = trait_arg or m.group(2).strip()
        candidate_sites = _target_sites(std, trait_arg)
        group_id = group_by_row.get(row_id)
        properties, property_files, group_export, property_inventory = _property_inventory(root, group_id, selector or "")
        group_export_attrs = group_export.get("attributes", {}) if isinstance(group_export, dict) else {}
        group_export_kind = group_export_attrs.get("kind", {}) if isinstance(group_export_attrs, dict) else {}
        group_export_pfc = group_export_kind.get("ProofForContract", {}) if isinstance(group_export_kind, dict) else {}
        group_export_contract = group_export.get("contract", {}) if isinstance(group_export, dict) else {}
        group_export_symbol = group_export_contract.get("contracted_function_name") if isinstance(group_export_contract, dict) else None
        property_anchors = [
            {"id": p.get("id"), "class": p.get("class"), "description": p.get("description"),
             "status": p.get("status"), "file": p.get("file"), "line": p.get("line"),
             "location_display": p.get("location_display")}
            for p in properties if _is_target_contract_site(p)
        ]
        req_row = request_rows.get(row_id, {})
        request_selector = req_row.get("selector")
        exact_selector = request_selector == selector and bool(selector)
        source_attr_target = macro.get("expanded_target_attribute")
        source_attr_matches = bool(target_norm and _norm(source_attr_target) == target_norm)
        source_attr_matches_export = bool(source_attr_matches and _norm(attr_target) == _norm(source_attr_target))
        export_matches_preflight = bool(
            group_export
            and group_export.get("name") == harness.get("name") == selector
            and group_export.get("crate_name") == harness.get("crate_name")
            and _norm(group_export_pfc.get("target_fn")) == _norm(attr_target)
            and group_export_symbol == symbol
        )
        missing = []
        if not exact_selector:
            missing.append("request row with exact id/selector is absent or differs")
        if source.get("crate") != harness.get("crate_name"):
            missing.append("source binding crate does not agree with exported harness crate")
        if not macro.get("invocation"):
            missing.append("same-compilation macro invocation/callsite source anchor is absent")
        if not attr_matches:
            missing.append("exported ProofForContract target does not match the source-qualified target")
        if not macro.get("source_target_attribute") or not source_attr_matches_export:
            missing.append("pinned source ProofForContract attribute, expanded from macro arguments when applicable, does not match export target")
        if not group_id:
            missing.append("request execution_groups has no exact group for this row id")
        if not export_matches_preflight:
            missing.append("same-group harness export identity/target/contract symbol does not match structured preflight")
        if group_export and len(properties) != group_export.get("n_properties"):
            missing.append("same-group rich property inventory count does not match same-group harness export")
        if not isinstance(symbol, str) or not symbol:
            missing.append("exported contracted_function_name is absent")
        if not properties:
            missing.append("same-group retained property id-to-source-site inventory is absent")
        if not candidate_sites.get("candidates"):
            missing.append("target impl contract attribute source candidates were not found")
        # A source target attribute and mangled name do not identify which
        # specialized impl FnDef rustc resolved. Keep that semantic link open.
        missing.append("compiler-resolved target DefPath/impl identity is not exported; mangled name alone is insufficient")
        bindings.append({
            "id": row_id,
            "selector": selector,
            "crate": harness.get("crate_name"),
            "static_source_binding_status": (
                "SOURCE_BOUND"
                if exact_selector and source.get("crate") == harness.get("crate_name")
                and bool(macro.get("invocation")) and attr_matches
                and bool(candidate_sites.get("candidates"))
                else "PENDING"
            ),
            "same_compilation_binding_status": "PENDING_TARGET_IMPL_WRAPPER_IDENTITY",
            "execution_group": group_id,
            "macro_instance": macro,
            "type": type_arg,
            "trait": trait_arg,
            "target": {
                "qualified": target,
                "export_attribute_target": attr_target,
                "attribute_matches_source_target": attr_matches,
                "pinned_source_attribute": macro.get("source_target_attribute"),
                "pinned_source_attribute_expanded_target": source_attr_target,
                "source_attribute_matches_export": source_attr_matches_export,
                "contracted_function_name": symbol,
                "contracted_function_name_role": "mangled modifies-wrapper symbol per pinned producer codegen",
                "resolved_impl": None,
                "status": "PENDING",
            },
            "export": {
                "harness_name": harness.get("name"),
                "harness_crate": harness.get("crate_name"),
                "harness_file": harness.get("file"),
                "harness_line": harness.get("line"),
                "attributes": attrs,
                "contract": contract,
                "producer_reported_target": pf.get("expected_target_fn"),
            },
            "sites": {
                "target_contract_candidates": candidate_sites,
                "property_inventory_files": property_files,
                "property_inventory": property_inventory,
                "property_site_candidates_are_bound": False,
                "same_group_export_harness": group_export,
                "property_sites": property_anchors,
                "property_site_candidate_count": len(property_anchors),
                "property_count": len(properties),
            },
            "gaps": missing,
        })
        if missing:
            gaps.append({"id": row_id, "selector": selector, "missing": missing})

    # Provenance is reported for caller review; the analyzer does not silently
    # swap a checkout or claim these revisions if the inputs differ.
    return {
        "schema": "s1-07-pfc-binding-analysis-v1",
        "producer_commit_required": PRODUCER_COMMIT,
        "run_rows": len(run_rows),
        "request_rows": len(request_rows),
        "bindings": bindings,
        "gaps": gaps,
        "producer_semantics_anchors": _producer_anchors(control),
        "unexported_same_compilation_metadata": [
            "resolved target DefPathHash/DefId and canonical fully-qualified path for each PFC harness, linked from harness attribute resolution",
            "harness DefPathHash/DefId, crate disambiguator, and macro expansion backtrace with invocation span and macro-definition span",
            "type and trait substitutions after monomorphization, including selected specialization impl identity",
            "resolved #[kani::proof_for_contract] target FnDef -> check/checked_with -> modifies_wrapper closure -> emitted contracted_function_name instance identity chain",
            "effective exported requires/ensures/modifies clauses for that exact target FnDef and modifies wrapper, each with source spans",
            "wrapper call edge from harness through helper macros/functions to the resolved target and wrapper, with source spans",
            "property records linked to the harness DefPathHash and source span (property id, class, description, status, file, line)",
            "single compilation/export identity tying all above fields to the same rustc/Kani compilation and retained property inventory",
        ],
        "provenance_inputs": {
            "std_repo": str(std),
            "control_repo": str(control),
            "required_std_commit": PINNED_STD_COMMIT,
            "required_control_commit": PINNED_CONTROL_COMMIT,
        },
    }
