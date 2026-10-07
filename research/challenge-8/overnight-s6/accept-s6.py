#!/usr/bin/env python3
"""Hosted full S6 component matrix on one pinned patched VeriFast profile.

Each checker owns its exact source/MIR certificates and classifications. This
driver merely schedules them, preserves their output and rejects incomplete
or mismatched summaries; it cannot turn a diagnostic into acceptance.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


STOCK_EXPECTED = {
    "u32_positive": "POSITIVE",
    "raw_positive": "POSITIVE",
    "forget_positive": "POSITIVE",
    "ordinary_unwind": "POSITIVE",
    "shared_cleanup": "POSITIVE",
    "u32_false_post": "INTENDED_NEGATIVE",
    "raw_false_post": "INTENDED_NEGATIVE",
    "forget_false_post": "INTENDED_NEGATIVE",
    "false_unwind": "INTENDED_NEGATIVE",
    "u32_contradictory_pre": "INTENDED_DEAD_CODE_REJECTION",
    "forget_contradictory_pre": "INTENDED_DEAD_CODE_REJECTION",
}


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    if not (os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux"):
        raise SystemExit("S6 acceptance requires GitHub-hosted Linux Actions")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stock-home", type=Path, required=True)
    p.add_argument("--tool-home", type=Path, required=True)
    p.add_argument("--schema", type=Path, required=True)
    p.add_argument("--compiler-sysroot", required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    a = p.parse_args()
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    ev = a.evidence.resolve()
    ev.mkdir(parents=True, exist_ok=False)
    common = ["--tool-home", str(a.tool_home), "--schema", str(a.schema),
              "--compiler-sysroot", a.compiler_sysroot]
    stock = ["--stock-home", str(a.stock_home)]
    stages = {}

    def run(name, script, arguments, summary_path, accept):
        remaining = int(a.deadline_epoch - time.time()) - 30
        if remaining < 15:
            result = {"status": "NOT_RUN_BUDGET", "accepted": False}
        else:
            cmd = [sys.executable, str(script), *arguments]
            proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    start_new_session=True)
            try:
                output, _ = proc.communicate(timeout=remaining)
                (ev / (name + ".log")).write_bytes(output)
                print(name, "exit", proc.returncode, flush=True)
                result = {"status": "COMPLETED", "exit": proc.returncode,
                          "summary": str(summary_path.relative_to(ev)),
                          "accepted": False}
                payload = read_json(summary_path)
                if isinstance(payload, dict):
                    result["accepted"] = bool(proc.returncode == 0 and accept(payload))
                else:
                    result["reason"] = "missing or invalid summary"
            except subprocess.TimeoutExpired as exc:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.communicate()
                (ev / (name + ".log")).write_bytes(exc.stdout or b"")
                print(name, "timed out", flush=True)
                result = {"status": "TIMEOUT", "accepted": False,
                          "summary": str(summary_path.relative_to(ev))}
        stages[name] = result
        write_json(ev / "stages.json", stages)
        return result["accepted"]

    stock_dir = ev / "stock" / "cases"
    run("stock_controls", here / "check-stock-s6-2610.py",
        [*common, "--evidence", str(stock_dir), "--deadline-epoch",
         str(a.deadline_epoch - 30)], stock_dir / "summary.json",
        lambda data: isinstance(data, dict) and
        {name: item.get("classification") for name, item in data.items()}
        == STOCK_EXPECTED)

    ctor_dir = ev / "constructor"
    run("constructor", here / "check-maybeuninit-new-pointer.py",
        [*stock, *common, "--evidence", str(ctor_dir), "--components-only"],
        ctor_dir / "summary.json",
        lambda data: data.get("constructor_acceptance") is True and
        data.get("actual_callee_status") == "NOT_RUN")

    def classifier(name, script):
        target = ev / (name + ".json")
        run(name, here / script, ["--evidence", str(target)], target,
            lambda data: data.get("pass") is True)
        return target

    asptr_classifier = classifier("asptr_classifier",
                                  "test-select-pointer-classifier.py")
    asptr_dir = ev / "asptr"
    run("asptr", here / "check-select-pointer.py",
        [*stock, *common, "--evidence", str(asptr_dir),
         "--constructor-summary", str(ctor_dir / "summary.json"),
         "--classifier-summary", str(asptr_classifier)],
        asptr_dir / "summary.json",
        lambda data: data.get("accepted_component") is True and
        data.get("classification") == "COMPONENT_ACCEPTED")

    intrinsic_classifier = classifier("intrinsic_classifier",
                                      "test-select-pointer-intrinsics-classifier.py")
    intrinsic_dir = ev / "intrinsic"
    run("intrinsic", here / "check-select-pointer-intrinsics.py",
        [*stock, *common, "--evidence", str(intrinsic_dir),
         "--constructor-summary", str(ctor_dir / "summary.json"),
         "--as-mut-ptr-summary", str(asptr_dir / "summary.json"),
         "--classifier-summary", str(intrinsic_classifier)],
        intrinsic_dir / "summary.json",
        lambda data: data.get("accepted_component") is True and
        data.get("classification") == "COMPONENT_ACCEPTED")

    drop_classifier = classifier("drop_classifier",
                                 "test-pointer-drop-classifier.py")
    drop_dir = ev / "pointer_drop"
    run("pointer_drop", here / "check-pointer-drop.py",
        [*common, "--evidence", str(drop_dir),
         "--constructor-summary", str(ctor_dir / "summary.json"),
         "--as-mut-ptr-summary", str(asptr_dir / "summary.json"),
         "--intrinsic-summary", str(intrinsic_dir / "summary.json"),
         "--classifier-summary", str(drop_classifier)],
        drop_dir / "summary.json",
        lambda data: data.get("accepted_component") is True and
        data.get("classification") == "COMPONENT_ACCEPTED" and
        len(data.get("admission_cases", [])) == 22)

    accepted = len(stages) == 8 and all(s["accepted"] for s in stages.values())
    overall = {"classification": "ACCEPTED" if accepted else "INCONCLUSIVE",
               "accepted": accepted, "stages": stages,
               "scope": "stock+CFG and four separate S6 components; no actual helper"}
    write_json(ev / "summary.json", overall)
    print(json.dumps({"classification": overall["classification"],
                      "stages": {k: v["status"] for k, v in stages.items()}},
                     sort_keys=True), flush=True)
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
