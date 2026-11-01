#!/usr/bin/env python3
"""Static consistency checks for SMALLSORT-CONTRACT-DOMAINS.md on Part 1 v5.

Python stdlib and Git reads only: no builds, CI requests or proof execution.
The native inventories are the committed cleanup pages (G1: ordinary 200,
G2: with kani_smallsort_controls 382); they establish list membership only.
Run from any directory: python3 check_domains.py
"""

import csv
import json
from collections import Counter
from pathlib import Path
import re
import subprocess


PIN = "5a3009b065"
TREE = "cbe69760c8166d49acf1171c46185dfa3d58b270"
V4_REV = "790458b54e"
HERE = Path(__file__).resolve().parent
K1 = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "library/core/src").is_dir())
SHARED = "library/core/src/slice/sort/shared/"
VERIFY = SHARED + "smallsort/verify/"
PREFIX = "slice::sort::shared::smallsort::verify::"
REPORT = K1 / "SMALLSORT-CONTRACT-DOMAINS.md"
TARGETS = ("swap_profile", "sort4_profile", "insert_tail_profile", "merge_profile",
           "stable_cell", "unstable_byte", "freeze_noncopy")
FORBIDDEN = re.compile(r"\b(?:codex|claude|gcb|cloud build|audit\w*|planner|budget\w*|"
                       r"competitor\w*|poneclean|domains-v4|rust-lang/rust)\b", re.I)
INTERNAL_CODES = re.compile(r"\b(?:[SQIMW]\d\d|A[1-3]|P1-CLEAN|G[12]|v4)\b")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def pin_lines(path, cache={}):
    if path not in cache:
        cache[path] = git("show", f"{PIN}:{path}").splitlines()
    return cache[path]


def declared_at(lines, n):
    """Item name declared at line n: a macro invocation (first argument),
    attributes (next `fn`), or a `fn` line itself."""
    line = lines[n - 1]
    if re.search(r"\w!\($", line):
        return re.match(r"\s*(\w+)", lines[n])[1]
    if re.search(r"\w!\(", line):
        return re.search(r"\w!\((\w+)", line)[1]
    fn = r"\s*(?:pub(?:\(\w+\))? )?(?:unsafe )?fn (\w+)"
    i = n - 1
    while not re.match(fn, lines[i]):
        assert lines[i].lstrip().startswith("#[") and i < n + 4, (n, lines[i])
        i += 1
    return re.match(fn, lines[i])[1]


def inventory_pages(prefix):
    names, total = [], None
    for page in sorted((K1 / "cleanup").glob(f"{prefix}.inventory-page-*.txt")):
        for line in page.read_text().splitlines():
            if line.startswith("total="):
                total = int(line.split("=", 1)[1])
            elif line.startswith(PREFIX):
                names.append(line)
    assert len(names) == len(set(names)) == total, (prefix, len(names), total)
    return set(names)


def main():
    assert git("rev-parse", f"{PIN}:library").strip() == TREE
    assert git("rev-parse", "HEAD:library").strip() == TREE
    files = [f for f in git("ls-tree", "-r", "--name-only", PIN, VERIFY).split()
             if f.endswith(".rs")] + [SHARED + "smallsort/verify.rs"]
    assert not any("correct.rs" in f for f in files)

    # No disabled items remain; verify.rs gates only the mutations module.
    for f in files:
        assert not any("cfg(any())" in line for line in pin_lines(f)), f
    gates = [n for n, line in enumerate(pin_lines(files[-1]), 1) if "cfg(" in line]
    assert [pin_lines(files[-1])[n] for n in gates] == ["mod mutations;"], gates

    rows = list(csv.DictReader((HERE / "pfc-inventory.tsv").open(), delimiter="\t"))
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names)) == 37
    ordinary = [r for r in rows if r["cfg v5"] == "ordinary"]
    controls = [r for r in rows if r["cfg v5"] == "cfg(kani_smallsort_controls)"]
    assert (len(ordinary), len(controls)) == (35, 2) and len(rows) == 37

    # Every lexical PFC attribute site (including macro templates) is recorded;
    # target, invocation and cfg gate are checked per row.
    sites = set()
    for f in files:
        for n, line in enumerate(pin_lines(f), 1):
            if re.match(r"\s*#\[kani::proof_for_contract\(", line):
                sites.add((f.removeprefix(VERIFY), n))
    recorded = set()
    for r in rows:
        loc = r["location (annotation; invocation)"]
        m = re.fullmatch(r"([\w/]+\.rs):(\d+)(?:; invocation (\d+))?", loc)
        assert m, loc
        file, n = m[1], int(m[2])
        lines = pin_lines(VERIFY + file)
        assert (file, n) in sites, (r["name"], loc)
        actual = re.search(r"proof_for_contract\(([^)]+)\)", lines[n - 1])[1]
        assert actual.rsplit("::", 1)[-1] == r["target"], (r["name"], actual)
        recorded.add((file, n))
        start = int(m[3]) if m[3] else n
        short = r["name"].rsplit("::", 1)[-1]
        window = lines[start - 1:start + 7]
        assert re.search(r"\b" + re.escape(short) + r"\b", "\n".join(window)), (r["name"], loc)
        gate_lines = {start - 2, n - 2}
        gated = any("cfg(kani_smallsort_controls)" in lines[i] for i in gate_lines)
        assert gated == (r in controls), (r["name"], loc)
        assert r["name"].split("::")[0] == Path(file).stem, r["name"]
    assert sites == recorded, sorted(sites - recorded)

    counts = Counter(r["target"] for r in ordinary)
    assert counts == {"swap_profile": 14, "sort4_profile": 2, "insert_tail_profile": 4,
                      "merge_profile": 12, "stable_cell": 1, "unstable_byte": 1,
                      "freeze_noncopy": 1}, counts

    # Native list membership: ordinary names in G1 (200), controls only with the cfg (G2).
    g1, g2 = inventory_pages("g1"), inventory_pages("g2")
    assert (len(g1), len(g2)) == (200, 382) and g1 <= g2
    source = json.loads((K1 / "cleanup/source-inventory.json").read_text())
    assert {h["name"] for h in source["ordinary"]["harnesses"]} == g1
    assert all(PREFIX + r["name"] in g1 for r in ordinary)
    assert all(PREFIX + r["name"] in g2 - g1 for r in controls)

    # v4 retired (cfg(any())) PFC names are gone from source and native lists.
    v4 = list(csv.DictReader(git("show", f"{V4_REV}:research/challenge-8/kani-k1/domains/"
                                 "pfc-inventory.tsv").splitlines(), delimiter="\t"))
    retired = [r["name"] for r in v4 if r["cfg/status v4"].startswith("cfg(any())")]
    assert len(retired) == 72
    text = "\n".join("\n".join(pin_lines(f)) for f in files)
    for name in retired:
        assert PREFIX + name not in g2
        assert not re.search(r"\b" + re.escape(name.rsplit("::", 1)[-1]) + r"\b", text), name
    v4_live = {r["name"] for r in v4 if not r["cfg/status v4"].startswith("cfg(any())")}
    assert v4_live == set(names), sorted(v4_live ^ set(names))

    # Public report: size, wording, records, harness names, and every source link.
    report = REPORT.read_text()
    assert report.count("\n") <= 250
    for pattern in (FORBIDDEN, INTERNAL_CODES):
        assert not pattern.search(report), pattern.search(report)[0]
    assert "<V5-KANI-RUN>" in report and "kani/issues/5104" in report
    records = re.findall(r"^\| `(" + "|".join(TARGETS) + r") × ", report, re.M)
    assert len(records) == 22, len(records)
    assert all(f"`{r['name']}`" in report for r in ordinary)
    links = re.findall(r"\[([\w.]+):(\d+)\]\(https://github\.com/Tiramisu-Cake/verify-rust-std/"
                       r"blob/([0-9a-f]+)/([^)#]+)#L(\d+)\)", report)
    assert len(links) == report.count("blob/"), "unparsed source link"
    for text_file, text_n, rev, path, n in links:
        assert rev == PIN and Path(path).name == text_file and text_n == n, (text_file, text_n)
        lines = pin_lines(path)
        assert 0 < int(n) <= len(lines) and lines[int(n) - 1].strip(), (path, n)
    named = re.findall(r"`(?:network|merge|wrap)::(\w+)` \[([\w.]+):(\d+)\]\([^)#]+#L\d+\)", report)
    for short, file, n in named:
        path = next(p for _, _, _, p, _ in links if Path(p).name == file)
        assert declared_at(pin_lines(path), int(n)) == short, (short, file, n)
    print(f"OK: {PIN} library {TREE[:10]}; 37 PFC entries / {len(sites)} lexical sites; "
          f"35 ordinary + 2 controls + 0 cfg(any()); 72 v4-retired absent; "
          f"G1 200 / G2 382 membership; 22 domains; {len(links)} source links "
          f"({len(named)} harness-name links)")
    print("Proof status is the organizer CI run (<V5-KANI-RUN>); this script does not verify proofs.")


if __name__ == "__main__":
    main()
