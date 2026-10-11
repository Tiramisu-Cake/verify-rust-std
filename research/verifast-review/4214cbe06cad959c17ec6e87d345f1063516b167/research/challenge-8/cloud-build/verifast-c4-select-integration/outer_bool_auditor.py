#!/usr/bin/env python3
"""Pure saved-data auditor for the exact C3 Bool outer-F positive control.

Imports only stdlib. Never invokes compilation, extraction, proof or dispatch.
Historic fixture name and artifacts are unchanged. This is classification only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

VERSION = "outer-bool-positive-v1"
TARGET = "negative_outer_bound_escape"
CALL = "verified/lib.rs(103,22-83)"
SOURCE = "bca43d1a7b92cac4faf11362f55b35d115306e920fb0999139a57836dbd94cf5"
ORIGINAL = "a70911542588eda2934407957630b1dcc748cee72e5ef64424bb7fc9f9bdd76b"
AST = "5381cca6ef5e90e0f486faaa875dd027e819ba5a151c9705440dd7f5bc20b6c9"
BUILD = "9397d5cd-51e6-4de4-87d0-e2195728f713"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

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



def audit(log: str, ast_text: str, verified: bytes, original: bytes, stage: dict) -> dict:
    """Fail closed on missing or contradictory observations, even with exit 0."""
    checks = {}
    source_hash, original_hash, ast_hash = sha(verified), sha(original), sha(ast_text.encode())
    checks["exact_source_and_ast"] = (source_hash == SOURCE and original_hash == ORIGINAL and ast_hash == AST)
    checks["stage_matches_log_and_sources"] = (
        stage.get("log_sha256") == sha(log.encode()) and
        stage.get("source_pair") == {"original": original_hash, "verified": source_hash})
    checks["stage_success"] = (stage.get("exit") == 0 and stage.get("errors") == [] and
        stage.get("dead_code") == [] and stage.get("zero_errors") is True)
    checks["no_raw_diagnostics"] = not re.search(
        r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$|^.*: dead code$", log)
    headers = re.findall(r"Verifying function '([^']+)'", log)
    checks["target_entered_once_and_last"] = (headers.count(TARGET) == 1 and
        headers[-1:] == [TARGET] and stage.get("headers") == headers)
    pos = log.find("Verifying function '" + TARGET + "'")
    trace = log[pos:] if pos >= 0 else ""
    checks["terminal_completion"] = bool(re.search(
        r"0 errors found \(95 statements verified\) \(target: x86_64-unknown-linux-gnu \(LP64\)\)\s*\Z", trace))
    checks["source_domain"] = (b"F: FnMut(&T, &T) -> bool" in verified and
        b"type_interp::<F>()" in verified and
        b"is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*left, &*right)" in verified and
        [i for i,l in enumerate(verified.decode().splitlines(), 1)
         if "end_lft_binding::<'cmp>()" in l] == [106])
    projection = _outer_projection_ast(ast_text)
    nodes = projection["matching_nodes"]
    checks["exact_projection_before_callback"] = (
        projection["registration_marker_count"] == 1 and projection["registration_node_count"] == 1 and
        len(nodes) == 1 and nodes[0]["call_location"] == CALL and nodes[0]["immediately_before_call"])
    scope_start = ast_text.find('BlockStmt (loc "verified/lib.rs(84,9-38)", [')
    scope = _balanced_node(ast_text, scope_start) if scope_start >= 0 else ""
    target_start = ast_text.find('"' + TARGET + '"')
    declarations = [re.findall(r'"\$_' + str(n) + r'", None, \(ref \(false\), ref \(None\)\)', scope or "")
                    for n in range(27,33)]
    checks["six_locals_inside_scope"] = (target_start >= 0 and scope_start > target_start and
        all(len(v) == 1 for v in declarations) and all(
        ast_text[:scope_start].count('"$_' + str(n) + '", None, (ref (false), ref (None))') == 0
        for n in range(27,33)))
    checks["relocation_observed"] = (re.findall(
        r"(?m)^STRICT-RELOCATE inner=_(\d+) translated=\$_\1 type=.* addresstaken=false$",log)
        == [str(n) for n in range(27,33)] and
        log.count("STRICT-RELOCATE outer_removed=6 inner_insertions=1") == 1)
    export = re.findall(r"(?m)^SORT4-CURRENT-BOUND-AST-EXPORT: target=" + TARGET +
        r" source_sha256=([0-9a-f]{64}) final_flattened_ast_sha256=([0-9a-f]{64}) "
        r"bytes=(\d+) file=(\S+) strict_cut=1 observation_only$",log)
    checks["export_seal"] = (len(export) == 1 and export[0][:2] == (source_hash, ast_hash) and
        int(export[0][2]) == len(ast_text.encode()) and
        export[0][3] == stage.get("cwd", "") + "/final-current-bound-ast.ml")
    checks["translator_registration_and_call"] = (
        log.count("CHALLENGE8_HRTB_EQ F=F T=T lifetime='cmp call=" + CALL) == 1 and
        log.count("CHALLENGE8_HRTB_CALL registered=1 call=" + CALL) == 1)
    # Verbose statements at one coordinate are ambiguous; require the actual
    # Verifying-call event and the pinned AST adjacency, not an invented count.
    checks["actual_callback"] = trace.count(CALL + ": Verifying call") == 1
    call_at = trace.find(CALL + ": Verifying call")
    path = trace[call_at:] if call_at >= 0 else ""
    def ordered(tokens):
        cursor = 0
        for token in tokens:
            at = path.find(token, cursor)
            if at < 0: return False
            cursor = at + len(token)
        return True
    common_pre = ["bin/rust/std/lib.rsspec(47," + x + "): Consuming assertion"
                  for x in ["17-29", "44-47", "69-70", "94-95"]]
    def posts(lines):
        return ["verified/lib.rs(" + loc + "): Consuming assertion" for loc in lines]
    unwind_posts = posts(["56,10-76,1","71,15-27","71,51-52","71,74-75", "72,11-14",
                         "72,38-39","73,12-15","73,40-41","74,14-17","74,41-42"])
    normal_posts = posts(["56,10-76,1","65,5-17","65,41-42","65,64-65", "66,11-14",
                         "66,38-39","67,12-15","67,40-41","68,14-17","68,41-42"])
    cut = "verified/lib.rs(106,9-107,1): Freeing locals."
    leak = "verified/lib.rs(110,1-2): Leak check."
    lifetime = "verified/lib.rs(52,1-110,2): Consuming function lifetime token"
    checks["unwind_resource_closure"] = ordered(common_pre + [
        "bin/rust/std/lib.rsspec(49,27-39): Producing assertion", cut,
        "verified/lib.rs(101,32-33): Verifying call",
        "verified/lib.rs(103,22-83): Executing return statement", lifetime] + unwind_posts + [leak])
    checks["normal_resource_closure"] = ordered(common_pre + [
        "bin/rust/std/lib.rsspec(49,27-39): Producing assertion", cut,
        "verified/lib.rs(101,32-33): Verifying call", leak,
        "bin/rust/std/lib.rsspec(48,17-29): Producing assertion", cut,
        "verified/lib.rs(108,26-27): Verifying call",
        "verified/lib.rs(110,2): Executing return statement", lifetime] + normal_posts + [leak])
    checks["two_complete_paths"] = (path.count(cut) == 2 and path.count(leak) == 2 and
        path.count(lifetime) == 2 and stage.get("return_seen") is True and
        stage.get("leak_check_seen") is True)
    missing = [k for k,v in checks.items() if not v]
    return {"auditor_version":VERSION, "classification": "PASS_POSITIVE_LOCAL_HRTB_CLOSURE"
            if not missing else "INCONCLUSIVE", "checks":checks,"missing":missing,
            "raw_log_sha256":sha(log.encode()), "final_ast_sha256":ast_hash,
            "verified_sha256":source_hash,"original_sha256":original_hash,
            "fresh_proof":False,"proof_credit":False,
            "metadata_escape_negative":"OPEN_NOT_RUN","general_O23":"OPEN"}


# Replay claims a specific historical Build; unlike the reusable observation
# classifier above, it must bind inputs to independently recorded D digests.
SAVED_DIGESTS = {
    "log": "6e28eafac5959aaa4e49591d6631cffae970e5ac83f575d5d96b18bfe9153538",
    "proof": "c66bfbee78e8054cc43f81127d1ca9f661ba8785618d4278664e948b6a985683",
    "manifest": "e6874106322a06fbe20d37c3ea4ab27fe41a5624e071c1d24989c3c5880e6440",
    "summary": "101ed540f4a0984287cf5992e68183c1cfa40f61f5d3e819aaece60f8d8e7b70",
    "inventory": "b464e0af8e9edd1c0ba6f44e50112caf64018886b2fcea05433ad38b4ca3a3bc",
}

def saved_identity(inputs: dict[str, bytes]) -> bool:
    return set(inputs) == set(SAVED_DIGESTS) and all(
        sha(inputs[name]) == digest for name, digest in SAVED_DIGESTS.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--auditor-commit", required=True)
    a = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",a.auditor_commit): parser.error("full auditor commit required")
    base = a.evidence_root / "allprooflogs/cases/integration"
    prefix = base / "regression-lifetime-negative_outer_bound_escape"
    case = base / "regressions/strict-lifetime" / TARGET
    proof_bytes = Path(str(prefix)+"-proof.json").read_bytes()
    log_bytes = prefix.with_suffix(".log").read_bytes()
    saved = {"log": log_bytes, "proof": proof_bytes,
        "manifest": (a.evidence_root / "manifest.json").read_bytes(),
        "summary": (a.evidence_root / "summary.json").read_bytes(),
        "inventory": (a.evidence_root / "files-sha256.json").read_bytes()}
    result = audit(log_bytes.decode(), (case / "final-current-bound-ast.ml").read_text(),
        (case / "verified/lib.rs").read_bytes(), (case / "original/lib.rs").read_bytes(),
        json.loads(proof_bytes))
    result["checks"]["saved_build_identity"] = saved_identity(saved)
    result["saved_input_hashes"] = {name: sha(value) for name,value in saved.items()}
    if not result["checks"]["saved_build_identity"]:
        result["missing"].append("saved_build_identity")
        result["classification"] = "INCONCLUSIVE"
    result.update({"build":BUILD,"tool_commit":"4a34010cc3930eec46fc4e72c1b793ad734fa730",
        "tested_runner_commit":"ca5f54607bf9e36ecbb9a24085cc6cc9e18db98c",
        "delivery_commit":"84f21b3bf244eb352cb91584fc84a73d6703b117",
        "profile":"verifast-c4-select-composition-20261011-c3", "auditor_commit":a.auditor_commit,
        "auditor_sha256":sha(Path(__file__).read_bytes()),
        "historical_verdict":"UNEXPECTED_NEGATIVE_PASS_EXPECTED_CUT106_VC_NOT_OBSERVED_GATE_NOT_CLOSED",
        "historical_cloud_status":"FAILURE_UNCHANGED", "reclassification_basis":"owner-authorized design correction; semantic review a0bd9827"})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["classification"])
    return 0 if not result["missing"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
