#!/usr/bin/env python3
"""Exact-name and classification checks for INTEG2's static source forecast."""
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE / "scope"
REPO = HERE.parents[3]
BASE = "e6a8ad05c9"
SCOPE_PATH = "research/challenge-8/kani-k1/scope/manifest.tsv"


def names(filename):
    return set((SCOPE / filename).read_text().splitlines())


def main():
    inventory = subprocess.check_output(
        ["python3", "-c", "import sys; sys.path.insert(0, 'research/challenge-8/kani-k1/scope'); "
         "from source_inventory import inventory; print('\\n'.join(r['name'] for r in inventory()))"],
        cwd=REPO, text=True).splitlines()
    tree = subprocess.check_output(["git", "rev-parse", "HEAD:library"], cwd=REPO, text=True).strip()
    manifest = list(csv.DictReader((SCOPE / "manifest.tsv").open(), delimiter="\t"))
    scope = list(csv.DictReader((SCOPE / "scope.tsv").open(), delimiter="\t"))
    by_name = {r["name"]: r for r in manifest}
    assert len(inventory) == len(set(inventory)) == len(manifest) == len(scope) == 479
    assert set(inventory) == set(by_name) == {r["name"] for r in scope}
    assert all(r["source_library_tree"] == tree for r in manifest + scope)
    assert all(r["proof_source"] for r in scope)

    p1 = {r["name"] for r in manifest if r["class"] == "ordinary"}
    p2 = {r["name"] for r in manifest if r["p2_candidate"] == "yes"}
    cfg_on = set(inventory)
    assert p1 == names("p1-ordinary.txt") and len(p1) == 197
    assert p2 == names("p2-ordinary.txt") and len(p2) == 343
    assert cfg_on == names("cfg-on.txt") and len(cfg_on) == 479
    counts = Counter(r["class"] for r in manifest)
    assert counts["expected-fail"] == 33 and counts["timeout-diagnostic"] == 5
    assert counts["fallback"] == 7 and counts["retired-duplicate"] == 18
    assert counts["positive-direct"] == 4 and counts["ordinary"] == 197

    for n in range(6, 9):
        name = f"slice::sort::shared::smallsort::verify::merge::stable_direct_aggregate_u64_n{n}"
        assert by_name[name]["class"] == "fallback" and by_name[name]["p2_candidate"] == "no"
    for n in range(2, 6):
        name = f"slice::sort::shared::smallsort::verify::merge::general_stable_direct_nonconst_u64_n{n}"
        assert by_name[name]["class"] == "fallback" and by_name[name]["p2_candidate"] == "no"
    for name in (
        "slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1",
        "slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_prefix_frame_control",
        "slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_suffix_frame_control",
    ):
        assert name not in p2
    for name in (
        "slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n5",
        "slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n6",
        "slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n7",
        "slice::sort::shared::smallsort::verify::merge::merge_scratch48_contract_u8_n8",
    ):
        assert name in p2

    old_raw = subprocess.check_output(["git", "show", f"{BASE}:{SCOPE_PATH}"], cwd=REPO, text=True)
    old = list(csv.DictReader(old_raw.splitlines(), delimiter="\t"))
    old_p1 = {r["name"] for r in old if r["class"] == "ordinary"}
    old_p2 = {r["name"] for r in old
              if r["class"] in {"ordinary", "budget-deferred", "positive-direct"}}
    assert len(old_p1) == 182 and len(old_p2) == 339
    for filename, before, after in (("p1", old_p1, p1), ("p2", old_p2, p2)):
        diff = (SCOPE / f"{filename}-diff-from-baseline.txt").read_text().splitlines()
        expected = sorted([*("+ " + x for x in after - before), *("- " + x for x in before - after)])
        assert diff == expected, filename

    metrics = json.loads((SCOPE / "metrics.json").read_text())
    p2_report = json.loads((SCOPE / "p2-static-check.json").read_text())
    assert metrics["library_tree"] == p2_report["library_tree"] == tree
    assert metrics["p1_ordinary"] == 197 and metrics["p2_candidate_ordinary"] == 343
    assert p2_report["result"] == "PASS_STATIC_INTEG2_P2_FORECAST_ONLY"
    assert p2_report["ordinary"] == p2_report["expected_p2_candidate_ordinary"] == 343
    assert p2_report["all_names"] == 479 and p2_report["patch_only_removes_budget_cfg_lines"]
    assert p2_report["patch_applied_to_temporary_source_copy"]
    patch = (SCOPE / "p2-ungate.patch").read_text().splitlines()
    removed = [line[1:].strip() for line in patch if line.startswith("-") and not line.startswith("---")]
    added = [line[1:].strip() for line in patch if line.startswith("+") and not line.startswith("+++")]
    assert removed and set(removed) == {"#[cfg(kani_smallsort_controls)]"} and not added
    assert "network::insert_tail_contract_u64_start1" not in "\n".join(
        line for line in patch if "insert_tail_contract_u64_start1," in line)

    print(json.dumps({"result": "PASS_STATIC_INTEG2_SCOPE_FORECAST_ONLY", "library_tree": tree,
                      "p1": len(p1), "p2": len(p2), "cfg_on": len(cfg_on),
                      "baseline_p1": len(old_p1), "baseline_p2": len(old_p2),
                      "p2_patch_cfg_lines": len(removed)}, indent=2))


if __name__ == "__main__":
    main()
