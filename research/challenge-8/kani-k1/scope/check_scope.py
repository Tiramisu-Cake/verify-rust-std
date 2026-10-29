#!/usr/bin/env python3
"""Required static source forecast; deliberately not a compiler/kani-list check."""
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter

from source_inventory import BASELINE, HERE, PREFIX, inventory, source


def main():
    base = inventory(BASELINE)
    current = inventory()
    baseline_names = Counter(r["name"] for r in base)
    current_names = Counter(r["name"] for r in current)
    assert baseline_names == current_names
    assert all(count == 1 for count in current_names.values())
    table = list(csv.DictReader((HERE / "scope.tsv").open(), delimiter="\t"))
    expected = {r["name"]: r for r in table}
    assert len(expected) == len(table) == 328
    assert set(expected) == {r["name"] for r in base if not r["opt_in"]}
    actual = {r["name"]: r for r in current}
    for name, row in expected.items():
        assert actual[name]["opt_in"] == (row["decision"] == "opt-in"), name
        assert all(str(value).strip() for value in row.values()), name
    for r in base:
        if r["opt_in"]:
            assert actual[r["name"]]["opt_in"], r["name"]

    manifests = {}
    for filename in ("ordinary.txt", "extended-positive.txt", "controls-failed.txt",
                     "deferred-unsupported.txt"):
        lines = (HERE / filename).read_text().splitlines()
        assert len(lines) == len(set(lines))
        manifests[filename] = set(lines)
    all_names = Counter(n for names in manifests.values() for n in names)
    assert all_names == baseline_names
    assert manifests["ordinary.txt"] == {r["name"] for r in current if not r["opt_in"]}
    for filename in manifests.keys() - {"ordinary.txt"}:
        assert all(actual[n]["opt_in"] for n in manifests[filename])

    original_library = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASELINE, "library"], text=True).splitlines()
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASELINE, "--", "library"], text=True).splitlines()
    assert set(changed) == {
        "library/core/src/slice/sort/shared/smallsort/verify/" + mod + ".rs"
        for mod in ("correct", "merge", "network")}
    cfg_re = re.compile(r"#\[cfg\(kani_smallsort_controls\)\]\n")
    files = {}
    cfg_count = 0
    for module in ("correct", "merge", "network"):
        before, after = source(module, BASELINE), source(module)
        assert cfg_re.sub("", before) == cfg_re.sub("", after), module
        delta = len(cfg_re.findall(after)) - len(cfg_re.findall(before))
        assert delta > 0
        cfg_count += delta
        assert max(map(len, after.splitlines())) <= 100
        files[module] = dict(sha256=hashlib.sha256(after.encode()).hexdigest(),
                             added_item_cfg=delta,
                             assertions_bodies_helpers_covers_solver_unwind_unchanged=True)
    assert cfg_count == 189
    ordinary = [r for r in current if not r["opt_in"]]
    verified_stub_callers = [r["name"] for r in ordinary if "stub_verified" in r["attributes"]]
    assert not verified_stub_callers, verified_stub_callers
    # No original names are replaced, so every union map is the unchanged original domain.
    mapping = list(csv.DictReader((HERE / "domain-map.tsv").open(), delimiter="\t"))
    assert len(mapping) == len(expected)
    assert {r["original"] for r in mapping} == set(expected)
    assert all(r["original"] == r["successors"] for r in mapping)
    report = dict(result="PASS_STATIC_FORECAST_ONLY", baseline=BASELINE,
                  baseline_ordinary=328, predicted_ordinary=len(ordinary),
                  predicted_controls_enabled=len(current), moved_ordinary=212,
                  unique_baseline_names=len(baseline_names), cfg_insertions=cfg_count,
                  manifest_counts={k: len(v) for k, v in manifests.items()},
                  ordinary_verified_stub_callers=verified_stub_callers,
                  identity_domain_union_rows=len(mapping), files=files,
                  library_baseline_file_count=len(original_library),
                  limitations=["Not Rust macro expansion or actual kani list",
                               "No compilation, Kani, CBMC or CI executed",
                               "Proof outcomes and performance of this cfg selection not established"])
    (HERE / "static-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
