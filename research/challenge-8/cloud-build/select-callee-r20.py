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
import subprocess
import sys
import time

REPAIR_REL = Path("research/challenge-8/overnight-assume-actual/r20_final_select_repair.py")
REPAIR_SHA256 = "8ef92bf290b8cfc1945ce8e2e41a9a3743a6e19bef9cf0e3a02e48458802f951"
CASE = "nine-body-a1-owned-forget"
VARIANTS = ("both", "true-only", "false-only")
# "merged" keeps the ghost-statement and MIR block inventory unchanged.
FINGERPRINT_VARIANT = "merged"
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
        write(root / "r20-repair.json", {"complete": False, "variants": rows})
    ran = all(isinstance(v.get("stage"), dict) and v["stage"].get("status") == "RAN" and
              type(v["stage"].get("exit")) is int for v in rows.values())
    record = {"classification": "R20_CALLEE_REPAIR_VARIANTS_OBSERVED", "variants": rows,
              "complete": ran,
              "transform_sha256": REPAIR_SHA256, "accepted": False, "proof_credit": False}
    write(root / "r20-repair.json", record)
    print(json.dumps({k: (v.get("stage") or {}).get("exit") for k, v in rows.items()}))
    if not ran:
        raise SystemExit(3)
    return record


def export_decode(case: Path, out: Path, a) -> dict:
    """NORMAL MIR export and capnp decode of the repaired copy (observation only)."""
    out.mkdir(parents=True)
    env = os.environ.copy()
    env["PATH"] = str(a.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    rows = {}
    steps = (("export", [str(a.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
                         f"--sysroot={a.compiler_sysroot}", "--edition", "2021"],
              None, out / "normal-mir.bin"),
             ("decode", ["capnp", "decode", str(a.schema), "VfMir"],
              out / "normal-mir.bin", out / "normal-mir.txt"))
    for name, argv, stdin, stdout in steps:
        budget = min(120, a.deadline_epoch - int(time.time()) - STAGE_RESERVE_SECONDS)
        if budget < 10 or (stdin is not None and rows.get("export", {}).get("exit") != 0):
            rows[name] = {"status": "NOT_RUN"}
            continue
        with (stdin.open("rb") if stdin else open(os.devnull, "rb")) as inp, \
                stdout.open("wb") as outp, (out / (name + ".stderr")).open("wb") as err:
            result = subprocess.run(["timeout", "--signal=TERM", "--kill-after=10s",
                                     f"{budget}s", *argv], cwd=case, stdin=inp, stdout=outp,
                                    stderr=err, env=env, check=False)
        rows[name] = {"status": "RAN" if result.returncode != 124 else "TIMED_OUT",
                      "exit": result.returncode, "output": stdout.name,
                      "output_sha256": sha(stdout.read_bytes())}
    return rows


def fingerprint(a) -> dict:
    """Fingerprint the FINGERPRINT_VARIANT-repaired unit under the existing intended refusal.

    Records the repaired verified SHA and the ten unit/body snapshot hashes a
    later reviewed certificate-refresh patch must pin. No proof is attempted.
    """
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("SORT4_R20_CALLEE_PHASE_ID") == "SORT4-ACTUAL-SELECT-2026-10-22-R20" and
         not os.environ.get("GITHUB_ACTIONS"), "authorized R20 Cloud callee lane")
    transform = load(a.repo / REPAIR_REL, "r20_final_select_repair", REPAIR_SHA256)
    o26 = load(a.cloud_dir / "o26-recipe.py", "r20_o26_recipe_fp")
    base = a.evidence / "cases/candidate/capture" / CASE
    need((base / "verified/lib.rs").is_file() and (base / "original/lib.rs").is_file(),
         "captured nine-body case")
    verified = (base / "verified/lib.rs").read_bytes()
    original = (base / "original/lib.rs").read_bytes()
    root = a.evidence / "cases/r20-fingerprint"
    repaired = transform.repair(verified, FINGERPRINT_VARIANT)
    cases = {}
    for variant, data in (("none", verified), (FINGERPRINT_VARIANT, repaired)):
        case = cases[variant] = root / variant / CASE
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(data)
    case = cases[FINGERPRINT_VARIANT]
    record = {"classification": "R20_REPAIRED_UNIT_FINGERPRINT", "complete": False,
              "variant": FINGERPRINT_VARIANT, "verified_sha256": sha(repaired),
              "original_sha256": sha(original), "base_verified_sha256": sha(verified),
              "accepted": False, "proof_credit": False}
    write(root / "r20-fingerprint.json", record)
    if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
        record["fingerprint"] = {"status": "NOT_RUN", "reason": "shared deadline reserve"}
        write(root / "r20-fingerprint.json", record)
        raise SystemExit(3)
    record["normal_mir"] = export_decode(case, root / (FINGERPRINT_VARIANT + "-mir"), a)
    write(root / "r20-fingerprint.json", record)
    cap = o26.load_capture(a.repo, "r20_fingerprint")
    args = argparse.Namespace(tool_home=a.tool_home, schema=a.schema,
                              compiler_sysroot=str(a.compiler_sysroot),
                              deadline_epoch=a.deadline_epoch)
    # Location control: the unrepaired copy in the same parent must reproduce
    # the pinned baseline unit/body snapshots, else the new pins are unusable.
    refresh = load(a.cloud_dir / "o26-refresh-recipe.py", "r20_o26_refresh_pins")
    pinned = {"unit": refresh.UNIT, **{f"body-{i}": h for i, h in enumerate(refresh.BODIES)}}
    cap.clear_semantic_opt_ins()
    control = cap.refusal_fingerprint(cases["none"], {"verified_sha256": sha(verified)}, args)
    observed = {k: (v or {}).get("sha256") for k, v in control.get("snapshots", {}).items()}
    record["location_control"] = {"fingerprint": control, "pinned": pinned,
                                  "reproduces_pinned": observed == pinned}
    write(root / "r20-fingerprint.json", record)
    cap.clear_semantic_opt_ins()
    result = cap.refusal_fingerprint(case, {"verified_sha256": sha(repaired)}, args)
    intended = "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE"
    mir = record["normal_mir"]
    mir_complete = all(mir.get(k, {}).get("status") == "RAN" and mir[k].get("exit") == 0
                       for k in ("export", "decode"))
    record.update(fingerprint=result, mir_complete=mir_complete,
                  complete=(result.get("classification") == intended and
                            control.get("classification") == intended and
                            record["location_control"]["reproduces_pinned"] and mir_complete))
    write(root / "r20-fingerprint.json", record)
    print(json.dumps({"classification": result.get("classification"),
                      "verified_sha256": record["verified_sha256"]}))
    if not record["complete"]:
        raise SystemExit(4)
    return record


R20_FLAG = "SORT4_R20_FINAL_SELECT_REPAIR"
PROOF_CASES = (
    # (name, repaired?, opt-in flag?, intent)
    ("merged-optin", True, True, "positive: checked repair under the refreshed certificate"),
    ("merged-no-optin", True, False, "control: refreshed text without opt-in must be refused"),
    ("unrepaired-optin", False, True, "control: opt-in without the repair must be refused"),
)


def proof(a) -> dict:
    """Run the existing O26 proof_stage on repaired/unrepaired copies (S3)."""
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("SORT4_R20_CALLEE_PHASE_ID") == "SORT4-ACTUAL-SELECT-2026-10-22-R20" and
         not os.environ.get("GITHUB_ACTIONS") and R20_FLAG not in os.environ,
         "authorized R20 Cloud callee lane without ambient opt-in")
    transform = load(a.repo / REPAIR_REL, "r20_final_select_repair", REPAIR_SHA256)
    o26 = load(a.cloud_dir / "o26-recipe.py", "r20_o26_recipe_proof")
    base = a.evidence / "cases/candidate/capture" / CASE
    need((base / "verified/lib.rs").is_file() and (base / "original/lib.rs").is_file(),
         "captured nine-body case")
    verified = (base / "verified/lib.rs").read_bytes()
    original = (base / "original/lib.rs").read_bytes()
    repaired = transform.repair(verified, FINGERPRINT_VARIANT)
    root = a.evidence / "cases/r20-proof"
    root.mkdir(parents=True, exist_ok=False)
    rows = {}
    record = {"classification": "R20_REPAIR_PROOF_OBSERVED", "complete": False, "rows": rows,
              "repaired_verified_sha256": sha(repaired), "base_verified_sha256": sha(verified),
              "accepted": False, "proof_credit": False}
    for name, use_repair, flag, intent in PROOF_CASES:
        if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
            rows[name] = {"status": "NOT_RUN", "reason": "shared deadline reserve", "intent": intent}
            write(root / "r20-proof.json", record)
            continue
        case = root / name / CASE
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(repaired if use_repair else verified)
        try:
            if flag:
                os.environ[R20_FLAG] = "1"
            result = o26.proof_stage(a.repo, case, a.tool_home, a.schema, a.compiler_sysroot,
                                     a.deadline_epoch, "r20-" + name, "refresh")
        finally:
            os.environ.pop(R20_FLAG, None)
        rows[name] = {"intent": intent, "opt_in": flag, "repaired": use_repair,
                      "verified_sha256": sha(repaired if use_repair else verified),
                      "stage": result,
                      "log": str((case / ("r20-" + name + ".log")).relative_to(a.evidence))}
        write(root / "r20-proof.json", record)
    record["complete"] = all(isinstance(r.get("stage"), dict) and r["stage"].get("status") == "RAN"
                             and type(r["stage"].get("exit")) is int for r in rows.values())
    write(root / "r20-proof.json", record)
    print(json.dumps({k: (v.get("stage") or {}).get("exit") for k, v in rows.items()}))
    if not record["complete"]:
        raise SystemExit(3)
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
              "repaired_fingerprint": read("cases/r20-fingerprint/r20-fingerprint.json"),
              "repair_proof": read("cases/r20-proof/r20-proof.json"),
              "accepted": False, "verification_accepted": False,
              "proof_credit": False}
    baseline = record["baseline_proof"]
    stage = baseline.get("stage") if isinstance(baseline, dict) else None
    record["baseline_proof_ran"] = (isinstance(stage, dict) and stage.get("status") == "RAN" and
                                    type(stage.get("exit")) is int)
    record["evidence_complete"] = a.runner_exit == 0 and record["baseline_proof_ran"]
    write(a.output, record)
    return record


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("repair")
    for name in ("repo", "cloud-dir", "evidence", "tool-home", "schema", "compiler-sysroot"):
        r.add_argument("--" + name, type=Path, required=True)
    r.add_argument("--deadline-epoch", type=int, required=True)
    f = sub.add_parser("fingerprint")
    for name in ("repo", "cloud-dir", "evidence", "tool-home", "schema", "compiler-sysroot"):
        f.add_argument("--" + name, type=Path, required=True)
    f.add_argument("--deadline-epoch", type=int, required=True)
    q = sub.add_parser("proof")
    for name in ("repo", "cloud-dir", "evidence", "tool-home", "schema", "compiler-sysroot"):
        q.add_argument("--" + name, type=Path, required=True)
    q.add_argument("--deadline-epoch", type=int, required=True)
    d = sub.add_parser("audit")
    d.add_argument("--evidence", type=Path, required=True)
    d.add_argument("--output", type=Path, required=True)
    d.add_argument("--runner-exit", type=int, required=True)
    d.add_argument("--failed-stage", required=True)
    a = p.parse_args()
    {"repair": repair, "fingerprint": fingerprint, "proof": proof, "audit": audit}[a.mode](a)


if __name__ == "__main__":
    main()
