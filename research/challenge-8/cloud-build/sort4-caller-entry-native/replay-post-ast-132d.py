#!/usr/bin/env python3
"""Isolated parser/auditor replay on saved Build132d AST; never runs a toolchain."""
import hashlib, importlib.util, json, pathlib, shutil, sys, tempfile
from datetime import datetime, timezone

repo = pathlib.Path(__file__).resolve().parents[4]
module_path = pathlib.Path(__file__).with_name("selected-proof.py")
spec = importlib.util.spec_from_file_location("selected_proof", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
raw = pathlib.Path("/tmp/select-session2-132d-raw")
case_root = raw / "allprooflogs/cases/sort4-c1-current-recovery/cases/selected-branch-positive"
ast_path = case_root / "fixture/proof-ast.ml"
result_path = case_root / "case-result.json"
admission_path = case_root / "pre-binding/selected-pre-binding-mir-admission.json"
result = json.loads(result_path.read_text())
admission = json.loads(admission_path.read_text())
ast = ast_path.read_text(errors="replace")
with tempfile.TemporaryDirectory(prefix="selected-post-ast-132d-") as temporary:
    root = pathlib.Path(temporary)
    shutil.copy2(ast_path, root / "proof-ast.ml")
    audit = module.post_ast_audit(root, result, "selected_freeze_basecase",
                                  "selected-branch-positive", "normal", admission)
    controls = module._synthetic_selected_ast_inventory_controls(ast)
    assert all(row["refused"] for key, row in controls.items()
               if key != "baseline-selected-Func-inventory-accepted")
    assert audit["callgraph"]["complete"] and len(audit["callgraph"]["observed_edges"]) == 3
    assert audit["threshold_prototype_posts"]["normal_present"]
    assert audit["threshold_prototype_posts"]["unwind_present"]
    report = {
        "purpose": "parser-only post-AST audit replay; no compiler, verifier, extractor, or proof runner",
        "replay_timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "replay_command": "python3 research/challenge-8/cloud-build/sort4-caller-entry-native/replay-post-ast-132d.py",
        "raw_build_id": json.loads((raw / "manifest.json").read_text())["build_id"],
        "case": "selected-branch-positive", "original_verdict": result,
        "input_sha256": hashlib.sha256(ast_path.read_bytes()).hexdigest(),
        "consumer_admission_sha256": hashlib.sha256(admission_path.read_bytes()).hexdigest(),
        "selected_proof_module_sha256": hashlib.sha256(module_path.read_bytes()).hexdigest(),
        "replay_result": "PASS", "proof_credit": False,
        "threshold_inventory": {"prototype_count": 1, "definition_count": 1,
                                "prototype_normal_unwind_posts_retained": True},
        "definition_posts": {name: {"normal": row["normal_post_present"],
                                     "unwind": row["unwind_post_present"]}
                             for name, row in audit["functions"].items()},
        "selected_callgraph_edge_count": len(audit["callgraph"]["observed_edges"]),
        "synthetic_func_inventory_controls": controls,
    }
    out = pathlib.Path(__file__).with_name("REPLAY-POST-AST-132D.json")
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(out)
