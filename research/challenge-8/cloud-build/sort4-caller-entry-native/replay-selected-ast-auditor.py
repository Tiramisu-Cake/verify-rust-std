#!/usr/bin/env python3
"""Run only selected-callgraph AST parser controls on synthetic text."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDITOR = HERE / "selected-proof.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    spec = importlib.util.spec_from_file_location("selected_ast_auditor", AUDITOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("selected AST auditor module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    controls = module._synthetic_callgraph_controls()
    if not all(row["refused"] for name, row in controls.items()
               if name != "baseline-shape-accepted"):
        raise RuntimeError("a synthetic selected AST control was accepted")
    report = {"auditor_sha256": sha(AUDITOR),
              "synthetic_controls": controls,
              "baseline_accepted": controls["baseline-shape-accepted"]["refused"] is False,
              "all_negative_controls_refused": True,
              "compiler_or_verifier_executed": False,
              "proof_credit": False}
    output = HERE / "REPLAY-SELECTED-AST-AUDITOR.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"report": str(output),
                      "auditor_sha256": report["auditor_sha256"],
                      "negative_controls": len(controls) - 1,
                      "all_negative_controls_refused": True,
                      "proof_credit": False}, indent=2))


if __name__ == "__main__":
    main()
