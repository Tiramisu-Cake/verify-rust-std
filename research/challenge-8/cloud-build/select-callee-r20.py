#!/usr/bin/env python3
"""Cloud-only R20 callee lane helpers: ghost-repair variants and audit.

`repair` copies the captured nine-body owned-forget case, applies the pinned
ghost-only transform `r20_final_select_repair.py` and runs the existing O26
`proof_stage` on each copy under the same activation set as the baseline.
`audit` writes a bounded summary. Verifier exits are observations: no
admission, acceptance or proof credit is derived here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time

REPAIR_REL = Path("research/challenge-8/overnight-assume-actual/r20_final_select_repair.py")
REPAIR_SHA256 = "3f1ab8b87317365c7501d503432082f29856f5290190a1b6d83aef8ca241abf8"
CASE = "nine-body-a1-owned-forget"
VARIANTS = ("both", "true-only", "false-only")
STAGE_RESERVE_SECONDS = 150


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("R20-CALLEE: " + why)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(path: Path, name: str, expected: str | None = None):
    if expected is not None:
        need(path.is_file() and sha(path.read_bytes()) == expected, "pinned module " + path.name)
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module spec " + path.name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def repair(a) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("SORT4_R20_CALLEE_PHASE_ID") == "SORT4-ACTUAL-SELECT-2026-10-22-R20" and
         not os.environ.get("GITHUB_ACTIONS"), "authorized R20 Cloud callee lane")
    transform = load(a.repo / REPAIR_REL, "r20_final_select_repair", REPAIR_SHA256)
    o26 = load(a.cloud_dir / "o26-recipe.py", "r20_o26_recipe")
    base = a.evidence / "cases/candidate/capture" / CASE
    need((base / "verified/lib.rs").is_file() and (base / "original/lib.rs").is_file(),
         "captured nine-body case")
    verified = (base / "verified/lib.rs").read_bytes()
    original = (base / "original/lib.rs").read_bytes()
    root = a.evidence / "cases/r20-repair"
    root.mkdir(parents=True, exist_ok=False)
    rows = {}
    for variant in VARIANTS:
        if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
            rows[variant] = {"status": "NOT_RUN", "reason": "shared deadline reserve"}
            continue
        case = root / variant / CASE
        case.parent.mkdir(parents=True)
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        repaired = transform.repair(verified, variant)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(repaired)
        result = o26.proof_stage(a.repo, case, a.tool_home, a.schema, a.compiler_sysroot,
                                 a.deadline_epoch, "r20-" + variant, "refresh")
        rows[variant] = {"verified_sha256": sha(repaired), "original_sha256": sha(original),
                         "base_verified_sha256": sha(verified), "stage": result,
                         "log": str((case / ("r20-" + variant + ".log")).relative_to(a.evidence))}
        write(root / "r20-repair.json", rows)
    record = {"classification": "R20_CALLEE_REPAIR_VARIANTS_OBSERVED", "variants": rows,
              "transform_sha256": REPAIR_SHA256, "accepted": False, "proof_credit": False}
    write(root / "r20-repair.json", record)
    print(json.dumps({k: (v.get("stage") or {}).get("exit") for k, v in rows.items()}))
    return record


def audit(a) -> dict:
    ev = a.evidence

    def read(rel):
        path = ev / rel
        try:
            return json.loads(path.read_text()) if path.is_file() else None
        except (OSError, ValueError):
            return {"unreadable": rel}

    stages = {}
    for path in sorted(ev.glob("*-exit-code.txt")):
        try:
            stages[path.name[:-len("-exit-code.txt")]] = int(path.read_text().strip())
        except ValueError:
            stages[path.name[:-len("-exit-code.txt")]] = None
    record = {"schema": "r20-select-callee-audit-v1",
              "runner_exit": a.runner_exit, "failed_stage": a.failed_stage,
              "stage_exits": stages,
              "source_preflight": read("source-preflight.json"),
              "capture_compare": read("cases/candidate/capture-compare.json"),
              "baseline_proof": read("cases/candidate/proof-stage.json"),
              "repair_variants": read("cases/r20-repair/r20-repair.json"),
              "accepted": False, "verification_accepted": False,
              "proof_credit": False, "evidence_complete": a.runner_exit == 0}
    write(a.output, record)
    return record


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("repair")
    for name in ("repo", "cloud-dir", "evidence", "tool-home", "schema", "compiler-sysroot"):
        r.add_argument("--" + name, type=Path, required=True)
    r.add_argument("--deadline-epoch", type=int, required=True)
    d = sub.add_parser("audit")
    d.add_argument("--evidence", type=Path, required=True)
    d.add_argument("--output", type=Path, required=True)
    d.add_argument("--runner-exit", type=int, required=True)
    d.add_argument("--failed-stage", required=True)
    a = p.parse_args()
    repair(a) if a.mode == "repair" else audit(a)


if __name__ == "__main__":
    main()
