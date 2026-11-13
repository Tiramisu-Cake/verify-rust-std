#!/usr/bin/env python3
"""Read-only Git/Python preparation checks. Never invokes a Rust/proof tool."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((HERE / "EXPORT-MANIFEST.json").read_text())
    c0 = Path("/root/kani-fix-3300-c0")
    baseline = manifest["baseline_only"]
    check(git(c0, "rev-parse", "HEAD").decode().strip() == baseline["sha"], "C0 identity")
    check(not git(c0, "status", "--porcelain").strip(), "C0 dirty")
    for path, digest in baseline["files"].items():
        check(hashlib.sha256((c0 / path).read_bytes()).hexdigest() == digest, "C0 hash: " + path)
    std = Path("/root/verify-rust-std-kani-traitpfc")
    check(git(std, "rev-parse", "HEAD").decode().strip() == manifest["smallsort"]["sha"], "std identity")
    check(not git(std, "status", "--porcelain").strip(), "std dirty")
    for path, digest in manifest["smallsort"]["files"].items():
        check(hashlib.sha256((std / path).read_bytes()).hexdigest() == digest, "std hash: " + path)
    records = []
    for name in ("CI-OVERLAY.json", "REPLAY-OVERLAY.json"):
        record = json.loads((HERE / name).read_text())
        clone = Path(record["clone"])
        check(git(clone, "rev-parse", "HEAD").decode().strip() == record["sha"], name + " HEAD")
        check(not git(clone, "status", "--porcelain").strip(), name + " dirty")
        diff = git(clone, "diff", "--binary", record["base"], record["sha"])
        check(diff == (HERE / record["patch"]).read_bytes(), name + " patch drift")
        check(hashlib.sha256(diff).hexdigest() == record["patch_sha256"], name + " patch digest")
        subprocess.run(["git", "-C", str(clone), "diff", "--check", record["base"], record["sha"]], check=True)
        changed = git(clone, "diff", "--name-only", record["base"], record["sha"]).decode().splitlines()
        if name == "CI-OVERLAY.json":
            check(all(p.startswith((".github/workflows/", "scripts/kani3300-gate/")) for p in changed), "CI overlay scope")
        else:
            check(set(changed) == {"library/core/src/slice/sort/shared/smallsort/verify.rs", "library/core/src/slice/sort/shared/smallsort/verify/replay_uninit_controls.rs"}, "replay overlay scope")
        records.append(record)
    replay = json.loads((HERE / "REPLAY-REQUEST.json").read_text())
    check(replay["status"] == "NOT_RUN_C1_PENDING" and replay["tool_export_sha"] is None and replay["run_budget"] is None, "dispatch must stay unbound")
    check(len(replay["roots"]) == 12, "exact twelve proposed root/profile rows")
    rows = {r["id"]: r for r in replay["roots"]}
    for row in rows.values():
        check(row["status"] == "NOT_RUN", "result must stay NOT_RUN")
        argv = row["argv"]
        check(argv[-3:] == ["--cbmc-args", "--object-bits", "12"], "object bits")
        check("--no-assert-contracts" in argv and "function-contracts" in argv, "contract flags")
        check(("uninit-checks" in argv) == row["uninit"], "uninit profile")
        pair = rows[row["companion"]]
        check(pair["selector"] == row["selector"] and pair["source_unwind"] == row["source_unwind"], "ON/OFF root drift")
        check(row["environment"] == pair["environment"], "ON/OFF cfg drift")
        normalized = [x.replace(row["id"], "<ROW>") for x in argv]
        paired = [x.replace(pair["id"], "<ROW>") for x in pair["argv"]]
        for values in (normalized, paired):
            if "uninit-checks" in values:
                index = values.index("uninit-checks")
                del values[index - 1:index + 1]
        check(normalized == paired, "ON/OFF flags drift")
    ci = Path(records[0]["clone"])
    import yaml
    workflow = yaml.load((ci / ".github/workflows/kani3300-fullgate.yml").read_text(), Loader=yaml.BaseLoader)
    check(set(workflow["on"]) == {"workflow_dispatch"}, "workflow trigger")
    check(list((ci / ".github/workflows").glob("*.yml")) == [ci / ".github/workflows/kani3300-fullgate.yml"], "stock workflow leakage")
    subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "scripts/kani3300-gate", "-p", "test_*.py"], cwd=ci, check=True)
    print("STATIC_PACKAGE_OK; Python synthetic tests only; proof/CI/shell runtime NOT_RUN")


if __name__ == "__main__":
    main()
