#!/usr/bin/env python3
"""Check ASSEMBLY static scope artifacts against the current source scan."""
import csv
import json
import subprocess
from collections import Counter

from source_inventory import HERE, inventory

INTEG = "ddcc33f837"


def read_tsv(name):
    return list(csv.DictReader((HERE / name).open(), delimiter="\t"))


def names(name):
    return set((HERE / name).read_text().splitlines())


def main():
    baseline, current = inventory(INTEG), inventory()
    base_names = {r["name"] for r in baseline}
    current_by_name = {r["name"]: r for r in current}
    assert len(base_names) == 449
    assert sum(not r["opt_in"] for r in baseline) == 176
    assert len(current_by_name) == len(current) == 463
    assert base_names <= current_by_name.keys()

    tree = subprocess.check_output(["git", "rev-parse", "HEAD:library"], text=True).strip()
    manifest = read_tsv("manifest.tsv")
    by_name = {r["name"]: r for r in manifest}
    assert len(by_name) == len(manifest) == 463
    assert set(by_name) == set(current_by_name)
    for r in current:
        m = by_name[r["name"]]
        assert all(str(v).strip() for v in m.values()), r["name"]
        assert (m["configuration"] == "opt-in") == r["opt_in"], r["name"]
        assert m["source_library_tree"] == tree
        if m["expectation"] == "FAILED":
            assert m["class"] == "expected-fail"
        if m["class"] == "positive-direct":
            assert m["p2_candidate"] == "yes" and m["p2_macos_ci"] == "UNKNOWN"

    counts = Counter(r["class"] for r in manifest)
    assert counts["ordinary"] == 182, counts
    assert counts["expected-fail"] == 31 and counts["timeout-diagnostic"] == 4
    assert counts["pending-direct"] in (0, 1, 2)
    assert counts["retired-duplicate"] == 14 - counts["pending-direct"]
    assert counts["budget-deferred"] == 153
    assert counts["positive-direct"] == 10
    assert counts["preexisting-opt-in"] == 68
    assert counts["deferred-unsupported"] == 1
    assert sum(counts.values()) == 463
    assert sum(r["configuration"] == "ordinary" for r in manifest) == 182

    expected_lists = {
        "ordinary.txt": {"ordinary"},
        "extended-positive.txt": {"budget-deferred", "positive-direct", "preexisting-opt-in"},
        "budget-deferred.txt": {"budget-deferred"},
        "retired-duplicates.txt": {"retired-duplicate"},
        "positive-direct.txt": {"positive-direct"},
        "timeout-diagnostic.txt": {"timeout-diagnostic"},
        "controls-failed.txt": {"expected-fail"},
        "deferred-unsupported.txt": {"deferred-unsupported"},
        "pending-direct.txt": {"pending-direct"},
    }
    for filename, classes in expected_lists.items():
        assert names(filename) == {r["name"] for r in manifest if r["class"] in classes}, filename

    direct_names = {f"slice::sort::shared::smallsort::verify::merge::{route}_direct_u64_n{n}"
                    for route in ("general", "stable") for n in (6, 7, 8)}
    direct_ordinary = sum(by_name[n]["class"] == "ordinary" for n in direct_names)
    direct_pending = sum(by_name[n]["class"] == "pending-direct" for n in direct_names)
    assert direct_ordinary + direct_pending == 6
    assert direct_pending == counts["pending-direct"]
    assert all(by_name[n]["class"] == ("pending-direct" if current_by_name[n]["opt_in"] else "ordinary")
               for n in direct_names)
    assert all(by_name[n]["class"] == "expected-fail" for n in (
        "slice::sort::shared::smallsort::verify::merge::stable_direct_value_corruption_control_u64_n2",
        "slice::sort::shared::smallsort::verify::merge::merge_aggregate_unsorted_halves_control_u64_n4",
        "slice::sort::shared::smallsort::verify::merge::merge_aggregate_allocation_bounds_control_u64"))

    table = read_tsv("scope.tsv")
    assert len(table) == 463 and {r["name"] for r in table} == set(current_by_name)
    assert all(r["source_library_tree"] == tree and r["class"] for r in table)
    assert all(r["proof_source"] for r in table)
    assert all(r["p2_candidate"] == "yes" and r["p2_macos_ci"] == "UNKNOWN"
               for r in table if r["class"] == "positive-direct")
    for r in table:
        if r["name"] in direct_names | {
            "slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_general_drop_u8_n8",
            "slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_stable_fallback_cell_u8_n8",
            "slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_unstable_fallback_cell_u8_n8",
        }:
            assert "not a result on the ASSEMBLY candidate tree" in r["gcb_measurement_applicability"]

    metrics = json.loads((HERE / "metrics.json").read_text())
    assert metrics["library_tree"] == tree
    assert metrics["ordinary"] == 182 and metrics["p2_candidate_ordinary"] == 345
    assert metrics["controls_cfg_total"] == 463 and metrics["controls_failed"] == 31
    assert metrics["pending_direct"] == counts["pending-direct"]
    assert metrics["retired_duplicates"] == counts["retired-duplicate"]

    gates = read_tsv("budget-gates.tsv")
    assert all("pending-direct" not in r["class"] for r in gates)
    pr2 = json.loads((HERE / "pr2-static-check.json").read_text())
    assert pr2["ordinary"] == pr2["expected_p2_candidate_ordinary"] == 345
    assert pr2["library_tree"] == tree
    assert pr2["all_names"] == 463
    assert pr2["retained_classes"] and "pending-direct" in pr2["retained_classes"]

    report = dict(result="PASS_STATIC_ASSEMBLY_SCOPE_FORECAST_ONLY", baseline=INTEG,
                  library_tree=tree, all_names=len(current), ordinary=counts["ordinary"],
                  p2_candidate_ordinary=metrics["p2_candidate_ordinary"], controls_cfg_total=463,
                  controls_failed=counts["expected-fail"], pending_direct=counts["pending-direct"],
                  retired_duplicates=counts["retired-duplicate"],
                  direct_ordinary=direct_ordinary, direct_pending=direct_pending,
                  classes=dict(counts),
                  limitations=["Source scan only; not Rust expansion or actual Kani inventories",
                               "Source results are historical and do not establish results on the final library tree",
                               "Stable direct N6/N7 remain pending coordinator confirmation",
                               "No compiler, Kani, CBMC or CI was run"])
    (HERE / "static-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
