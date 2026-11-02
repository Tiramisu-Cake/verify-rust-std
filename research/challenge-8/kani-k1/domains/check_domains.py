#!/usr/bin/env python3
"""Static consistency checks for the public SmallSort contract-domain report.

Checks the Part 1 v6 source pin, committed MACSPLIT G1 ordinary inventory,
and statically derived cfg-on set. The cfg-on v6 set is not a native inventory.
Python stdlib and Git reads only; no builds, CI requests, or proof execution.
Run from any directory: python3 check_domains.py
"""

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


PIN = "d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097"
LINK_PIN = PIN[:10]
TREE = "d4ec476a7a001363e58f19948c188a9c2078e370"
PARENT = "c0bd09c354a50bf9fe4dcc7cc5f9c34503658479"
INVENTORY_HEAD = "71d18696613bdd6b00648a0d7b44d1cd3c6da940"
HEAD_LIBRARY = "cbe69760c8166d49acf1171c46185dfa3d58b270"
V4_REV = "790458b54e"
V5_PIN = "5a3009b065"
HERE = Path(__file__).resolve().parent
K1 = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "library/core/src").is_dir())
SHARED = "library/core/src/slice/sort/shared/smallsort/"
VERIFY = SHARED + "verify/"
PREFIX = "slice::sort::shared::smallsort::verify::"
REPORT = K1 / "SMALLSORT-CONTRACT-DOMAINS.md"
TARGETS = ("swap_profile", "sort4_profile", "insert_tail_profile", "merge_profile",
           "stable_cell", "unstable_byte", "freeze_noncopy")
OLD_NAMES = {
    "network::dispatch_safety_stable_unstable_bytes17_n32",
    "network::insert_tail_contract_u64_start1_tail13_to16",
}
NEW_NAMES = {
    "network::dispatch_safety_stable_bytes17_n32",
    "network::dispatch_safety_unstable_bytes17_n32",
    "network::insert_tail_contract_u64_start1_tail13_to14",
    "network::insert_tail_contract_u64_start1_tail15_to16",
}
CI_URL = "https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41404150041"
FORBIDDEN = re.compile(r"\b(?:codex|claude|gcb|cloud build|audit\w*|planner|budget\w*|"
                       r"competitor\w*|poneclean|domains-v4|rust-lang/rust)\b", re.I)
INTERNAL_CODES = re.compile(r"\b(?:[SQIMW]\d\d|A[1-3]|P1-CLEAN|G[12]|v[45])\b")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def pin_lines(path, cache={}):
    if path not in cache:
        cache[path] = git("show", f"{PIN}:{path}").splitlines()
    return cache[path]


def declared_at(lines, n):
    """Item name declared at line n: macro invocation, attribute, or fn."""
    line = lines[n - 1]
    if re.search(r"\w!\($", line):
        return re.match(r"\s*(\w+)", lines[n])[1]
    if re.search(r"\w!\(", line):
        return re.search(r"\w!\((\w+)", line)[1]
    fn = r"\s*(?:pub(?:\(\w+\))? )?(?:unsafe )?fn (\w+)"
    i = n - 1
    while not re.match(fn, lines[i]):
        assert i < n + 4 and lines[i].lstrip().startswith("#["), (n, lines[i])
        i += 1
    return re.match(fn, lines[i])[1]


def read_name_list(path):
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def g1_inventory():
    path = K1 / "macsplit/g1.inventory-pages.txt"
    names, totals, metadata = [], set(), {}
    for line in path.read_text().splitlines():
        if line.startswith("total="):
            totals.add(int(line.split("=", 1)[1]))
        elif "=" in line and not line.startswith(PREFIX):
            key, value = line.split("=", 1)
            metadata.setdefault(key, set()).add(value)
        elif line.startswith(PREFIX):
            names.append(line)
    assert totals == {202}, totals
    assert len(names) == len(set(names)) == 202
    assert metadata.get("head_sha") == {INVENTORY_HEAD}, metadata
    assert metadata.get("build_id") == {"cbce904f-449c-4fe7-bb75-c14b1f70fbec"}, metadata
    assert metadata.get("request_id") == {"macsplit-g1-inventory-202-20261102"}, metadata
    return set(names)


def native_inventory_pages(prefix):
    names, totals = [], set()
    for page in sorted((K1 / "cleanup").glob(f"{prefix}.inventory-page-*.txt")):
        for line in page.read_text().splitlines():
            if line.startswith("total="):
                totals.add(int(line.split("=", 1)[1]))
            elif line.startswith(PREFIX):
                names.append(line)
    assert len(totals) == 1 and len(names) == len(set(names)) == next(iter(totals)), (
        prefix, len(names), totals
    )
    return set(names)


def map_v5_names(names):
    """Apply the two source-level v5→v6 name changes to full harness names."""
    old_full = {PREFIX + name for name in OLD_NAMES}
    new_full = {PREFIX + name for name in NEW_NAMES}
    assert old_full <= names
    return (names - old_full) | new_full


def verify_source_inventory(g1, g2_v6_static):
    """Reconcile the v5 source forecast and file hashes to the v6 source pin."""
    source = json.loads((K1 / "cleanup/source-inventory.json").read_text())
    files = source["source_files"]
    hashes = source["source_file_sha256"]
    assert set(files) == set(hashes)
    changed = git("diff", "--name-only", V5_PIN, PIN, "--", "library/").splitlines()
    assert changed == [VERIFY + "network.rs"], changed
    for path in files:
        v5_bytes = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{V5_PIN}:{path}"])
        v6_bytes = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{PIN}:{path}"])
        assert hashlib.sha256(v5_bytes).hexdigest() == hashes[path], path
        if path != VERIFY + "network.rs":
            assert v6_bytes == v5_bytes, path
        else:
            old_macro = (b"dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes17_n32, "
                        b"[u8; 17], [32]);")
            new_macro = (b"dispatch_safety_cases!(dispatch_safety_stable_bytes17_n32, [u8; 17], "
                        b"true, [32]);\ndispatch_safety_cases!(dispatch_safety_unstable_bytes17_n32, "
                        b"[u8; 17], false, [32]);")
            old_tail = (b"insert_tail_start1_group_case!(\n"
                        b"    insert_tail_contract_u64_start1_tail13_to16,\n"
                        b"    13,\n"
                        b"    16,\n"
                        b"    [13, 14, 15, 16]\n"
                        b");")
            new_tail = (b"insert_tail_start1_group_case!(insert_tail_contract_u64_start1_tail13_to14, "
                        b"13, 14, [13, 14]);\n\n"
                        b"insert_tail_start1_group_case!(insert_tail_contract_u64_start1_tail15_to16, "
                        b"15, 16, [15, 16]);")
            assert v5_bytes.count(old_macro) == 1 and v5_bytes.count(old_tail) == 1
            assert v6_bytes == v5_bytes.replace(old_macro, new_macro).replace(old_tail, new_tail)

    ordinary_records = source["ordinary"]["harnesses"]
    cfg_on_records = source["cfg_on"]["harnesses"]
    ordinary_v5 = {h["name"] for h in ordinary_records}
    cfg_on_v5 = {h["name"] for h in cfg_on_records}
    assert all(h["gates"] == [] for h in ordinary_records)
    assert all(h["gates"] in ([], ["kani_smallsort_controls"]) for h in cfg_on_records)
    gated_v5 = {h["name"] for h in cfg_on_records if h["gates"] == ["kani_smallsort_controls"]}
    assert len(gated_v5) == 182
    old_full = {PREFIX + name for name in OLD_NAMES}
    ordinary_by_name = {h["name"]: h for h in ordinary_records}
    assert old_full <= ordinary_v5
    assert all(ordinary_by_name[name]["gates"] == [] for name in old_full)
    mapped_ordinary = map_v5_names(ordinary_v5)
    mapped_cfg_on = map_v5_names(cfg_on_v5)
    assert len(ordinary_v5) == 200 and mapped_ordinary == g1
    assert len(cfg_on_v5) == 382 and mapped_cfg_on == g2_v6_static
    assert gated_v5 == g2_v6_static - g1
    assert len(g2_v6_static - g1) == 182

    # The split dispatch invocation uses the ordinary proof-emitting macro.
    network_v6 = git("show", f"{PIN}:{VERIFY}network.rs")
    macro_start = network_v6.index("macro_rules! dispatch_safety_cases")
    macro_end = network_v6.index("\n}", macro_start) + 2
    macro_text = network_v6[macro_start:macro_end]
    assert "#[kani::proof]" in macro_text and "cfg(kani_smallsort_controls)" not in macro_text
    lines = network_v6.splitlines()
    for name in ("dispatch_safety_stable_bytes17_n32", "dispatch_safety_unstable_bytes17_n32"):
        index = next(i for i, line in enumerate(lines) if f"dispatch_safety_cases!({name}" in line)
        previous_item = next((line.strip() for line in reversed(lines[:index]) if line.strip()), "")
        assert previous_item != "#[cfg(kani_smallsort_controls)]"
    return len(files)


def main():
    # The pin and inventory are both v6 source trees. This documentation worktree
    # deliberately retains the v5 library tree and is not the source under check.
    assert git("rev-parse", f"{PIN}^{{commit}}").strip() == PIN
    assert git("rev-parse", f"{PIN}^1").strip() == PARENT
    assert git("rev-parse", f"{PIN}:library").strip() == TREE
    assert git("rev-parse", f"{INVENTORY_HEAD}:library").strip() == TREE
    assert git("rev-parse", "HEAD:library").strip() == HEAD_LIBRARY
    assert git("rev-parse", "HEAD:library").strip() != TREE

    files = [f for f in git("ls-tree", "-r", "--name-only", PIN, VERIFY).split()
             if f.endswith(".rs")] + [SHARED + "verify.rs"]
    assert not any("correct.rs" in f for f in files)

    # No disabled items remain; verify.rs gates only the opt-in mutations module.
    for f in files:
        assert not any("cfg(any())" in line for line in pin_lines(f)), f
    gates = [n for n, line in enumerate(pin_lines(files[-1]), 1) if "cfg(" in line]
    assert [pin_lines(files[-1])[n - 1].strip() for n in gates] == [
        "#[cfg(kani_smallsort_controls)]"
    ], gates
    assert pin_lines(files[-1])[gates[0]].strip() == "mod mutations;"

    rows = list(csv.DictReader((HERE / "pfc-inventory.tsv").open(), delimiter="\t"))
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names)) == 38
    ordinary = [r for r in rows if r["cfg v6"] == "ordinary"]
    controls = [r for r in rows if r["cfg v6"] == "cfg(kani_smallsort_controls)"]
    assert (len(ordinary), len(controls), len(rows)) == (36, 2, 38)

    # Every lexical PFC attribute site (including macro templates) is recorded;
    # target, invocation, and cfg gate are checked per row.
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
        gated = any(0 <= i < len(lines) and "cfg(kani_smallsort_controls)" in lines[i]
                    for i in gate_lines)
        assert gated == (r in controls), (r["name"], loc)
        assert r["name"].split("::")[0] == Path(file).stem, r["name"]
    assert sites == recorded, sorted(sites ^ recorded)
    assert len(sites) == 18, len(sites)

    counts = Counter(r["target"] for r in ordinary)
    assert counts == {"swap_profile": 14, "sort4_profile": 2, "insert_tail_profile": 5,
                      "merge_profile": 12, "stable_cell": 1, "unstable_byte": 1,
                      "freeze_noncopy": 1}, counts

    # Native ordinary membership is exactly the committed MACSPLIT G1 list.
    g1 = g1_inventory()
    ordinary_expected = read_name_list(K1 / "macsplit/ordinary-expected.txt")
    assert len(ordinary_expected) == 202 and ordinary_expected == g1
    assert all(PREFIX + r["name"] in g1 for r in ordinary)

    # Derive, but do not label as native, the v6 cfg-on set from native v5 G2.
    g2_v5 = native_inventory_pages("g2")
    g2_expected = read_name_list(K1 / "cleanup/cfg-on-expected.txt")
    assert g2_v5 == g2_expected
    assert len(g2_v5) == 382
    g2_v6_static = map_v5_names(g2_v5)
    assert len(g2_v6_static) == 384
    assert g1 <= g2_v6_static
    assert all(PREFIX + r["name"] in g2_v6_static - g1 for r in controls)
    # Confirm the changed ordinary names and opt-in controls have the expected
    # source-level cfg provenance at the v6 pin.
    network = pin_lines(VERIFY + "network.rs")
    joined_network = "\n".join(network)
    assert "dispatch_safety_cases!(dispatch_safety_stable_bytes17_n32" in joined_network
    assert "dispatch_safety_cases!(dispatch_safety_unstable_bytes17_n32" in joined_network
    assert "insert_tail_contract_u64_start1_tail13_to14" in joined_network
    assert "insert_tail_contract_u64_start1_tail15_to16" in joined_network

    source_file_count = verify_source_inventory(g1, g2_v6_static)

    # v4 live PFC names map the combined insertion-tail harness to two entries.
    v4 = list(csv.DictReader(git("show", f"{V4_REV}:research/challenge-8/kani-k1/domains/"
                                 "pfc-inventory.tsv").splitlines(), delimiter="\t"))
    retired = [r["name"] for r in v4 if r["cfg/status v4"].startswith("cfg(any())")]
    assert len(retired) == 72
    text = "\n".join("\n".join(pin_lines(f)) for f in files)
    for name in retired:
        assert PREFIX + name not in g2_v6_static
        assert not re.search(r"\b" + re.escape(name.rsplit("::", 1)[-1]) + r"\b", text), name
    v4_live = {r["name"] for r in v4 if not r["cfg/status v4"].startswith("cfg(any())")}
    # The v4 PFC register predates these additions; only its combined
    # insertion-tail contract row is replaced by two v6 PFC rows.
    tail_old = {name for name in OLD_NAMES if name.startswith("network::insert_tail_")}
    tail_new = {name for name in NEW_NAMES if name.startswith("network::insert_tail_")}
    mapped_v4_live = (v4_live - tail_old) | tail_new
    assert mapped_v4_live == set(names), sorted(mapped_v4_live ^ set(names))

    # Public report: size, wording, records, harness names, and source links.
    report = REPORT.read_text()
    assert report.count("\n") <= 250
    for pattern in (FORBIDDEN, INTERNAL_CODES):
        assert not pattern.search(report), pattern.search(report)[0]
    assert "<V5-KANI-RUN>" not in report and CI_URL in report
    assert "kani/issues/5104" in report
    records = re.findall(r"^\| `(" + "|".join(TARGETS) + r") × ", report, re.M)
    assert len(records) == 22, len(records)
    assert all(f"`{r['name']}`" in report for r in ordinary)
    links = re.findall(r"\[([\w.]+):(\d+)\]\(https://github\.com/Tiramisu-Cake/verify-rust-std/"
                       r"blob/([0-9a-f]+)/([^)#]+)#L(\d+)\)", report)
    assert len(links) == report.count("blob/"), "unparsed source link"
    for text_file, text_n, rev, path, n in links:
        assert rev == LINK_PIN and Path(path).name == text_file and text_n == n, (text_file, text_n)
        lines = pin_lines(path)
        assert 0 < int(n) <= len(lines) and lines[int(n) - 1].strip(), (path, n)
    named = re.findall(r"`(?:network|merge|wrap)::(\w+)` \[([\w.]+):(\d+)\]\([^)#]+#L\d+\)", report)
    for short, file, n in named:
        path = next(p for _, _, _, p, _ in links if Path(p).name == file)
        assert declared_at(pin_lines(path), int(n)) == short, (short, file, n)
    print(f"OK: source pin {PIN} library {TREE[:10]}; documentation HEAD library "
          f"{HEAD_LIBRARY[:10]} (distinct); 38 PFC entries / {len(sites)} lexical sites; "
          f"36 ordinary + 2 controls + 0 cfg(any()); 72 retired absent; "
          f"native G1 {len(g1)}; static cfg-on v6 {len(g2_v6_static)}; "
          f"22 domains; {len(links)} source links ({len(named)} harness-name links)")
    print(f"Source forecast: {source_file_count} files reconciled to native ordinary and "
          "statically derived cfg-on sets.")
    print(f"Proof status: organizer CI run {CI_URL}; cfg-on v6 membership is statically derived, "
          "not a native inventory. This script does not verify proofs.")


if __name__ == "__main__":
    main()
