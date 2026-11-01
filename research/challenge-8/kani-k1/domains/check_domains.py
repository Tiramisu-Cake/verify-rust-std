#!/usr/bin/env python3
"""Static consistency checks for the manually researched DOMAINS-v4 registry.

No builds, CI requests, proof execution, or evidence downloads. The ZIP contains
names only; successful execution is an input from TASK-DOMAINS and the audits.
Run from any directory: python3 check_domains.py [path-to-provided-names.zip]
"""

import csv
from collections import Counter
from pathlib import Path
import re
import subprocess
import sys
import zipfile


PIN = "f0ba14f97b3adea21c1c9671db6245afe7a15887"
TREE = "3c23a45984f0f7cc5e43150a566b09fb1937e7c0"
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "library/core/src").is_dir())
VERIFY = ROOT / "library/core/src/slice/sort/shared/smallsort/verify"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main():
    assert git("rev-parse", f"{PIN}:library") == TREE
    assert git("rev-parse", "HEAD:library") == TREE
    assert not git("diff", PIN, "--", "library"), "library differs from source pin"
    rows = list(csv.DictReader((HERE / "pfc-inventory.tsv").open(), delimiter="\t"))
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names)) == 109
    ordinary = [r for r in rows if r["cfg/status v4"].startswith("ordinary;")]
    controls = [r for r in rows if "cfg(kani_smallsort_controls)" in r["cfg/status v4"]]
    inactive = [r for r in rows if r["cfg/status v4"].startswith("cfg(any())")]
    assert (len(ordinary), len(controls), len(inactive)) == (35, 2, 72)
    assert all("NOT_RUN" in r["cfg/status v4"] for r in controls + inactive)

    # All lexical PFC attribute sites, including macro templates, must occur in
    # the registry. This checks coverage/locations, not Rust macro semantics.
    sites = set()
    for p in VERIFY.rglob("*.rs"):
        for n, line in enumerate(p.read_text().splitlines(), 1):
            if re.match(r"\s*#\[kani::proof_for_contract\(", line):
                sites.add((p.relative_to(VERIFY).as_posix(), n))
    recorded = set()
    for r in rows:
        loc = r["location (annotation; invocation)"]
        match = re.match(r"([^:]+):(\d+)", loc)
        assert match, loc
        file, number = match[1], int(match[2])
        lines = (VERIFY / file).read_text().splitlines()
        assert (file, number) in sites, (r["name"], loc)
        target = r["target"].split()[0]
        actual = re.search(r"proof_for_contract\(([^)]+)\)", lines[number - 1])[1]
        assert actual.rsplit("::", 1)[-1] == target, (r["name"], target, actual)
        recorded.add((file, number))
        invocation = re.search(r"invocation(?:/declaration)? (\d+)", loc)
        start = int(invocation[1]) if invocation else number
        short_name = r["name"].rsplit("::", 1)[-1]
        assert re.search(r"\b" + re.escape(short_name) + r"\b",
                         "\n".join(lines[start - 1:start + 7])), (r["name"], loc)
    assert sites == recorded, sorted(sites - recorded)

    archive = Path(sys.argv[1] if len(sys.argv) > 1 else
                   "/root/ch8_changes_since_audit_2026-11-01.zip")
    with zipfile.ZipFile(archive) as z:
        entry, = [n for n in z.namelist() if n.endswith("/names-v4.txt")]
        archived = set(z.read(entry).decode().splitlines())
    prefix = "slice::sort::shared::smallsort::verify::"
    assert len(archived) == 200
    assert all(prefix + r["name"] in archived for r in ordinary)
    assert not any(prefix + r["name"] in archived for r in controls + inactive)
    counts = Counter(r["target"] for r in ordinary)
    assert counts == {"swap_profile": 14, "sort4_profile": 2,
                      "insert_tail_profile": 4, "merge_profile": 12,
                      "stable_cell": 1, "unstable_byte": 1, "freeze_noncopy": 1}

    # This older ledger is only an independent completeness check for retired
    # names. Its historical statuses are not imported as current proof credit.
    old = list(csv.DictReader((HERE.parent / "poneclean/DEACTIVATED.tsv").open(),
                              delimiter="\t"))
    old_names = {r["name"] for r in old if r["legacy_kind"] == "proof_for_contract"
                 and r["action"] == "cfg(any())"}
    assert old_names == {r["name"] for r in inactive}

    report = (HERE.parent / "DOMAINS-v4.md").read_text()
    assert all(r["name"].rsplit("::", 1)[-1] in report for r in ordinary)
    assert len(re.findall(r"^\| (?:S\d\d|Q\d\d|I\d\d|M\d\d|W\d\d) `",
                          report, re.M)) == 22
    assert len(re.findall(r"^\d+\. ", report, re.M)) <= 15
    refs = re.findall(r"https://github.com/Tiramisu-Cake/verify-rust-std/blob/"
                      r"f0ba14f97b/([^)#]+)#L(\d+)", report)
    for file, n in refs:
        lines = (ROOT / file).read_text().splitlines()
        assert 0 < int(n) <= len(lines) and lines[int(n) - 1].strip(), (file, n)
    print(f"OK: library {TREE}; 109 PFC entries / {len(sites)} lexical sites; "
          f"35 ordinary + 2 controls + 72 inactive; 22 domains; {len(refs)} source links")
    print("CI status is supplied evidence; this script does not verify proofs.")


if __name__ == "__main__":
    main()
