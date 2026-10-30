#!/usr/bin/env python3
"""Static scope and manifest checks for INTEG; not compiler or Kani evidence."""
import csv
import json
import subprocess
from collections import Counter

from prepare_integ import (DIRECT_FAILED, DIRECT_ORDINARY, DIRECT_POSITIVE,
                           DIRECT_TIMEOUT, LIBRARY_TREE, RETIRED, short)
from source_inventory import BASELINE, HERE, inventory


def read_tsv(name):
    return list(csv.DictReader((HERE / name).open(), delimiter="\t"))


def names(name):
    return set((HERE / name).read_text().splitlines())


def main():
    baseline, current = inventory(BASELINE), inventory()
    base_names = {r["name"] for r in baseline}
    current_by_name = {r["name"]: r for r in current}
    assert len(base_names) == 423 and len(current_by_name) == 449
    assert base_names <= current_by_name.keys()
    assert len(current_by_name) == len(current)

    manifest = read_tsv("manifest.tsv")
    by_short = {short(r["name"]): r for r in manifest}
    assert len(by_short) == len(manifest) == 449
    assert {r["name"] for r in manifest} == set(current_by_name)
    for r in current:
        m = by_short[short(r["name"])]
        assert all(str(v).strip() for v in m.values()), r["name"]
        assert (m["configuration"] == "opt-in") == r["opt_in"], r["name"]
        assert m["source_library_tree"] == LIBRARY_TREE
        if m["expectation"] == "FAILED":
            assert m["class"] == "expected-fail", r["name"]
        if m["class"] == "positive-direct":
            assert m["p2_candidate"] == "yes" and m["p2_macos_ci"] == "UNKNOWN"

    counts = Counter(r["class"] for r in manifest)
    assert counts == Counter({"ordinary": 176, "budget-deferred": 153,
                              "retired-duplicate": 11, "positive-direct": 10,
                              "timeout-diagnostic": 2, "expected-fail": 28,
                              "deferred-unsupported": 1, "preexisting-opt-in": 68}), counts
    assert sum(r["configuration"] == "ordinary" for r in manifest) == 176

    expected_lists = {
        "ordinary.txt": {"ordinary"},
        "extended-positive.txt": {"budget-deferred", "positive-direct", "preexisting-opt-in"},
        "budget-deferred.txt": {"budget-deferred"},
        "retired-duplicates.txt": {"retired-duplicate"},
        "positive-direct.txt": {"positive-direct"},
        "timeout-diagnostic.txt": {"timeout-diagnostic"},
        "controls-failed.txt": {"expected-fail"},
        "deferred-unsupported.txt": {"deferred-unsupported"},
    }
    for filename, classes in expected_lists.items():
        expected = {r["name"] for r in manifest if r["class"] in classes}
        assert names(filename) == expected, filename
    assert len(DIRECT_ORDINARY) == 12 and len(DIRECT_POSITIVE) == 10
    assert len(DIRECT_TIMEOUT) == 2 and len(DIRECT_FAILED) == 2 and len(RETIRED) == 11
    assert DIRECT_ORDINARY <= by_short.keys() and DIRECT_POSITIVE <= by_short.keys()
    assert all(by_short[n]["class"] == "ordinary" for n in DIRECT_ORDINARY)
    assert all(by_short[n]["class"] == "positive-direct" for n in DIRECT_POSITIVE)
    assert all(by_short[n]["class"] == "timeout-diagnostic" for n in DIRECT_TIMEOUT)
    assert all(by_short[n]["class"] == "retired-duplicate" for n in RETIRED)

    harness = {r["harness"]: r for r in read_tsv("/root/smallsort-pr-drafts/smallsort-harnesses.tsv")}
    returned = {n for n, r in harness.items()
                if r["part1"] == "opt-in" and r["part2"] == "ordinary" and
                (n.startswith(("network::swap_contract_u64_n9", "network::swap_contract_u8_n9",
                               "network::swap_contract_u8_n13")) or
                 n == "network::mutating_route_safety_cell_n9_to12" or
                 n.startswith("network::insertion_safety_u64"))}
    assert len(returned) == 31, len(returned)
    assert all(by_short[n]["class"] == "ordinary" for n in returned)

    paired_cell = [r for r in current if r["macro"] == "insertion_offset_group_cases" and
                   "#[cfg(kani_smallsort_controls)]" in r["args"][1] and
                   short(r["name"]).startswith("network::mutating_insertion_safety_cell_")]
    assert len(paired_cell) == 23
    for cell in paired_cell:
        plain = "network::" + cell["args"][0]
        assert by_short[plain]["class"] == "ordinary"
        assert by_short[short(cell["name"])]["class"] == "budget-deferred"

    table = read_tsv("scope.tsv")
    assert len(table) == 449 and {r["name"] for r in table} == set(current_by_name)
    assert all(r["source_library_tree"] == LIBRARY_TREE and r["class"] for r in table)
    assert all(r["proof_source"] for r in table)
    assert all(r["p2_candidate"] == "yes" and r["p2_macos_ci"] == "UNKNOWN"
               for r in table if r["class"] == "positive-direct")
    changed_control = next(r for r in table if short(r["name"]) ==
                           "merge::general_stable_direct_value_corruption_control_u64_n2")
    assert "different body" in changed_control["proof_source"]
    assert "awaits measurement" in changed_control["proof_source"]
    direct_metrics = metrics = json.loads((HERE / "metrics.json").read_text())
    assert direct_metrics["direct_results_gcb"]["expected-fail"]["known_time_count"] == 2
    assert "successful_time_count" not in direct_metrics["direct_results_gcb"]["expected-fail"]
    assert metrics["ordinary"] == 176 and metrics["p2_candidate_ordinary"] == 339
    assert metrics["p6_incremental"]["returned_count"] == 31
    assert metrics["p6_incremental"]["retired_count"] == 11
    assert metrics["p6_incremental"]["returned_known_vt_s"] == 1159.9
    assert metrics["p6_incremental"]["retired_known_vt_s"] == 245.6
    actual_tree = subprocess.check_output(["git", "rev-parse", "HEAD:library"], text=True).strip()
    assert actual_tree == LIBRARY_TREE, actual_tree

    report = dict(result="PASS_STATIC_INTEG_SCOPE_FORECAST_ONLY", baseline=BASELINE,
                  library_tree=actual_tree, all_names=len(current), ordinary=176,
                  p2_candidate_ordinary=339, classes=dict(counts), direct_ordinary=len(DIRECT_ORDINARY),
                  direct_positive_optin=len(DIRECT_POSITIVE), direct_timeouts=len(DIRECT_TIMEOUT),
                  direct_controls=len(DIRECT_FAILED), retired_duplicates=len(RETIRED),
                  plain_insertions_returned=len(returned),
                  limitations=["Source scan, not Rust expansion or kani list",
                               "No compiler/Kani/build evidence was run by this static check",
                               "Positive DIRECT P2 candidate has no macOS CI evidence"])
    (HERE / "static-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
