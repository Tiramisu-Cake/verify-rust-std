#!/usr/bin/env python3
"""Print future commands for an explicit manifest. This program never executes builds."""
import argparse
import shlex

from source_inventory import HERE


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--manifest", required=True,
                    choices=("ordinary", "extended-positive", "controls-failed"))
args = parser.parse_args()
names = (HERE / (args.manifest + ".txt")).read_text().splitlines()
expected = "FAILED" if args.manifest == "controls-failed" else "PASS"
print(f"# FUTURE REMOTE EXECUTION ONLY; expected {expected}; {len(names)} exact names")
for name in names:
    env = "env -u WORKER_INDEX -u WORKER_TOTAL -u RUSTFLAGS"
    if args.manifest != "ordinary":
        env += " " + shlex.quote("RUSTFLAGS=--cfg kani_smallsort_controls")
    command = ["./scripts/run-kani.sh", "--run", "verify-std", "--kani-args", "--harness", name,
               "--exact", "--jobs=3", "--timeout", "10m", "--unwind", "1000", "--output-format=terse"]
    print("cd /root/verify-rust-std-kani-scope && " + env + " " + shlex.join(command))
print("# Collect every row; FAILED controls must fail the intended property, not setup/timeouts.")
