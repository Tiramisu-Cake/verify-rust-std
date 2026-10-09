#!/usr/bin/env python3
"""Pure replay of saved C1-65d6 logs through the reviewed classifier/inventory."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "sort4-c1-current-recovery.py"
AUDIT = ROOT / "strict-cut-false-posts-audit.py"
ARCHIVE = Path("/tmp/c1-65d6-read/allprooflogs/cases/sort4-c1-current-recovery")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_functions(path):
    tree = ast.parse(path.read_text())
    nodes = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    prefix = nodes["actual_prefix"]
    inventory_node = next(n for n in prefix.body if isinstance(n, ast.FunctionDef) and n.name == "prefix_ast_inventory")
    audit_tree = ast.parse(AUDIT.read_text())
    proof_node = next(n for n in audit_tree.body if isinstance(n, ast.FunctionDef) and n.name == "proof_entries")
    trace_node = next(n for n in audit_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TRACE_ENTRY" for t in n.targets))
    selected = [nodes["classify_prefix_post_control"], inventory_node, trace_node, proof_node]
    env = {"re": re, "hashlib": hashlib, "Path": Path,
           "sha": lambda p: digest(Path(p))}
    for node in selected:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), env)
    return env["classify_prefix_post_control"], env["prefix_ast_inventory"], env["proof_entries"]


def pinned_admission(text, expected_post):
    rows = re.findall(r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) header_posts=([0-9a-f]{64})", text)
    expected = ("fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9",
                "dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39",
                expected_post,
                "23b6309ae9bf4a14abb31b78d87c9317c3b72b23c2d1ded70151e8ef9f6c761c")
    return rows == [expected]

def fail(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    classify, inventory_fn, proof_entries = selected_functions(RUNNER)
    # Verify saved archive manifest without touching it.
    manifest = json.loads((Path("/tmp/c1-65d6-read") / "files-sha256.json").read_text())
    checked = missing = mismatched = 0
    for rel, expected in manifest.items():
        p = Path("/tmp/c1-65d6-read") / rel
        if not p.is_file():
            missing += 1
        else:
            checked += 1
            if digest(p) != expected:
                mismatched += 1
    fail(missing == 0 and mismatched == 0, "saved archive manifest mismatch")

    log_path = ARCHIVE / "actual-prefix-on.log"
    stage_path = ARCHIVE / "actual-prefix-on-stage.json"
    ast_path = ARCHIVE / "actual-c1-prefix-post-ast.ml"
    log = log_path.read_text(errors="replace")
    stage = json.loads(stage_path.read_text())
    prior_positive = json.loads((ARCHIVE / "actual-prefix-positive-result.json").read_text())
    inv = inventory_fn(ast_path)
    entries = proof_entries(log, "sort4_stable")
    errors = [x for x in log.splitlines() if ": error:" in x or x.startswith("Fatal error:")]
    helper_rows = {}
    for name in ("recover_pair", "join_four_owned_cells"):
        hits = proof_entries(log, name)
        segment = log[hits[0]:entries[0]] if len(hits) == len(entries) == 1 and hits[0] < entries[0] else ""
        helper_rows[name] = {"one_entry_before_target": len(hits) == 1 and bool(segment),
                             "returned": "Executing return statement" in segment,
                             "leak_check": "Leak check." in segment,
                             "error_free": ": error:" not in segment}
    markers = [x for x in log.splitlines() if x.startswith("SORT4-ACTUAL-C1-PREFIX-ONLY admitted ")]
    admission = re.findall(r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) header_posts=([0-9a-f]{64})", log)
    node_hash = re.search(r"post_ast=([0-9a-f]{64}) NOT_CALLABLE_SUMMARY$", markers[0]).group(1) if len(markers) == 1 else None
    positive_ok = (stage.get("exit") == 0 and not errors and len(entries) == 1 and
                   all(all(row.values()) for row in helper_rows.values()) and
                   "0 errors found (147 statements verified)" in log and "Leak check." in log and
                   len(markers) == 1 and "normal_boundary=after_source194" in markers[0] and
                   "before_c2=source195" in markers[0] and "fnmut=1 outcomes=normal,direct_unwind" in markers[0] and
                   len(admission) == 1 and pinned_admission(log, node_hash) and
                   prior_positive["post_splice_ast_inventory"].get("ast_serializer_sha256") == digest(ast_path) and
                   prior_positive.get("raw_log_sha256") == digest(log_path) and
                   prior_positive.get("post_splice_ast_inventory", {}).get("same_invocation_stage_sha256") == digest(stage_path) and
                   not re.search(r"\): dead code$", log, re.M) and
                   "control=none " in markers[0] and inv.get("status") == "CONFIRMED_SOURCE_LINKED_PREFIX_RUNTIME_INVENTORY" and
                   inv.get("runtime_inventory") == {"FnMut": 1, "selector": 0, "copy": 0})
    fail(positive_ok, "positive full gate did not replay")

    controls = {}
    mutant_tests = {}
    expected_ast_hashes = {"normal-false-post": "f094ae667d92bd6e4b6c8f9b7f6fcefd8b425c1a30701d0a6d506b4d24f8ed81",
                           "unwind-false-post": "b5da002fed983f749943f7248f69e61694f72997270eea60ef7cf905862babcc",
                           "normal-omit-join": "336b89f55f64a2a060e6ca69724d4a951789090f1e51cd46898b515ad3fee9c6",
                           "unwind-omit-join": "fefb8be4dc69c218b29ce45e9fc98a1ee89156323f20459f7dae74d65dab8ca0"}
    for control in ("normal-false-post", "unwind-false-post", "normal-omit-join", "unwind-omit-join"):
        p = ARCHIVE / f"actual-prefix-control-{control}.log"
        raw = p.read_text(errors="replace")
        code = int((ARCHIVE / f"actual-prefix-control-{control}-exit-code.txt").read_text().strip())
        row = classify(control, raw, code, proof_entries)
        expected_post_line = 140 if control == "normal-false-post" else 147 if control == "unwind-false-post" else 142 if control == "normal-omit-join" else 149
        first = next((x for x in raw.splitlines() if ": error:" in x), "")
        control_markers = [x for x in raw.splitlines() if x.startswith("SORT4-ACTUAL-C1-PREFIX-ONLY admitted ")]
        target = proof_entries(raw, "sort4_stable")
        branch_text = raw[target[0]:] if len(target) == 1 else ""
        is_join = control.endswith("omit-join")
        primary_pin_ok = (f"verified/lib.rs({expected_post_line}," in first and
                          ("No matching heap chunks: foreach<T>(cons(right_after, cons(left_after, cons(third, cons(fourth, nil)))), own0(T_typeid, t))" in first if is_join else "Cannot prove false" in first))
        branch = "normal-return" if control.startswith("normal-") else "direct-unwind"
        branch_event = ("Executing return statement" in branch_text) if branch == "normal-return" else "unwind" in branch_text.lower()
        admission_rows = re.findall(r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) header_posts=([0-9a-f]{64})", raw)
        marker_ok = (len(control_markers) == 1 and f"control={control} " in control_markers[0] and
                     "NOT_CALLABLE_SUMMARY" in control_markers[0] and
                     f"post_ast={expected_ast_hashes[control]} " in control_markers[0] and
                     len(admission_rows) == 1 and pinned_admission(raw, expected_ast_hashes[control]))
        control_ast = expected_ast_hashes[control] if marker_ok else None
        controls[control] = {**row, "primary_error_exact": primary_pin_ok,
                             "expected_branch": branch, "branch_event_observed_not_proof": branch_event,
                             "control_marker_exact": marker_ok, "control_post_ast_sha256": control_ast,
                             "target_entry_count": len(target), "raw_log_sha256": digest(p),
                             "interpreted_as_intended_negative": bool(row.get("intended_negative") and primary_pin_ok and branch_event and marker_ok)}
        fail(controls[control]["interpreted_as_intended_negative"], f"negative control failed exact replay: {control}")
        # Mutations exercise exact error and control-marker fail-closed behavior.
        mutant_tests[control] = {
            "changed_primary_line_rejected": not classify(control, raw.replace("Cannot prove false.", "Cannot prove true.", 1) if not is_join else raw.replace("No matching heap chunks: foreach<T>", "No matching heap chunks: foreach<U>", 1), code, proof_entries).get("intended_negative"),
            "changed_control_marker_rejected": not classify(control, raw.replace(f"control={control} ", "control=wrong-control ", 1), code, proof_entries).get("intended_negative"),
            "changed_source_pin_rejected_by_full_gate": not pinned_admission(re.sub(r"(SORT4-ACTUAL-AST-SCOPE-TEST admitted source=)[0-9a-f]{64}", r"\g<1>" + "0" * 64, raw), expected_ast_hashes[control]),
        }
    fail(all(all(v.values()) for v in mutant_tests.values()), "negative classifier mutant accepted")

    # Inventory mutants are evaluated with the extracted pure inventory against a disposable in-memory temp artifact.
    import tempfile
    original = ast_path.read_text(errors="replace")
    mutant_tests["inventory"] = {}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "ast.ml"
        for name, mutant in (
            ("unknown_call", original.replace('"std::ops::FnMut::call_mut"', '"unexpected::unknown_call"', 1)),
            ("misplaced_fnmut", re.sub(r'(CallExpr\s*\(\s*loc "verified/lib.rs\()190(,[^"\n]+"\s*,\s*)"std::ops::FnMut::call_mut"', r'\g<1>191\g<2>"std::ops::FnMut::call_mut"', original, count=1)),
        ):
            p.write_text(mutant)
            result = inventory_fn(p)
            mutant_tests["inventory"][name + "_rejected"] = result.get("status") != "CONFIRMED_SOURCE_LINKED_PREFIX_RUNTIME_INVENTORY"
    fail(all(mutant_tests["inventory"].values()), "inventory mutant accepted")

    result = {
        "artifact": "C1-65D6-SERVICE-REPLAY",
        "build_id": "65d6cbb1-43fe-4e6d-a2c3-f4fff112a7aa",
        "classification": "SAVED_EVIDENCE_RECLASSIFICATION_ONLY",
        "proof_credit": False,
        "raw_records_modified": False,
        "archive_manifest": {"checked_files": checked, "missing": missing, "hash_mismatches": mismatched,
                             "manifest_sha256": digest(Path("/tmp/c1-65d6-read/files-sha256.json"))},
        "pins": {"verified_source_sha256": admission[0][0], "original_source_sha256": "3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72",
                 "pre_ast_sha256": admission[0][1], "positive_post_ast_node_sha256": node_hash,
                 "positive_ast_serializer_sha256": digest(ast_path),
                 "positive_log_sha256": digest(log_path), "positive_stage_sha256": digest(stage_path),
                 "prefix_patch_sha256": "2e1621b735e9d8af1d7c73b29d09daf1cd576943307521f67096917d342130e0",
                 "profile_sha256": "841d20589e0d745087791a8949b47a048da6d67ddd0fd1ce6b95975b53a72143"},
        "positive": {"classification": "PREFIX_ONLY_BOUNDED_C1_THEOREM" if positive_ok else "INCONCLUSIVE",
                     "gate_pass": positive_ok, "exit": stage.get("exit"), "target_entries": len(entries),
                     "statement_count": 147, "full_normal_unwind_posts_and_leak": True,
                     "helpers": helper_rows, "inventory": inv,
                     "source_and_ast_admission": admission[0],
                     "callable_summary": False, "actual_full_sort4_proved": False},
        "post_controls": controls,
        "mutant_rejection_tests": mutant_tests,
        "control_scope_note": "The four controls reject the actual normal/unwind returned heap post at its false predicate or missing preserved foreach. Branch events are observations only; their branch labels describe the exact source post position. The control patch marker pins each isolated mutation; this replay adds no CFG proof.",
        "script_sha256": digest(Path(__file__)), "runner_sha256": digest(RUNNER),
    }
    out = Path(__file__).with_name("C1-65D6-SERVICE-REPLAY.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(out), "positive": result["positive"]["classification"],
                      "controls": {k: v["classification"] for k, v in controls.items()},
                      "proof_credit": False}, sort_keys=True))

if __name__ == "__main__":
    main()
