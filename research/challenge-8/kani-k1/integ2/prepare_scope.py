#!/usr/bin/env python3
"""Generate INTEG2's source-only static scope after library edits are ready.

No Kani expansion or proof result is inferred here. Existing ASSEMBLY evidence is
retained only for exact unchanged harness names; all new/replaced names remain
unmeasured on the INTEG2 candidate tree.
"""
import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE / "scope"
REPO = HERE.parents[3]
SOURCE_SCOPE = REPO / "research/challenge-8/kani-k1/scope"
sys.path.insert(0, str(SOURCE_SCOPE))
from prepare_scope import compact, tsv  # noqa: E402
from source_inventory import BASELINE, inventory  # noqa: E402

BASE = "e6a8ad05c9"
MANIFEST_PATH = "research/challenge-8/kani-k1/scope/manifest.tsv"
SCOPE_PATH = "research/challenge-8/kani-k1/scope/scope.tsv"

# P1-max additions and exact class decisions from TASK-INTEG2.
RETURNED_P1 = {
    *(f"network::network_correctness_u8_n{n}" for n in (10, 11, 12)),
    "network::insertion_permutation_u8_n11",
    *(f"merge::route_safety_all_routes_n{n}" for n in range(3, 8)),
}
DIRECT_ORDINARY = {
    *(f"merge::stable_direct_u64_n{n}" for n in range(6, 10)),
    "merge::general_direct_u64_n9",
    "merge::general_direct_u8_n9",
    "merge::stable_direct_nonconst_u8_n9",
    *(f"network::insert_tail_contract_u64_start1_tail{a}_to{b}"
      for a, b in ((2, 8), (9, 12), (13, 16))),
}
FALLBACK = {
    *(f"merge::stable_direct_aggregate_u64_n{n}" for n in (6, 7, 8)),
    *(f"merge::general_stable_direct_nonconst_u64_n{n}" for n in range(2, 6)),
}
RETIRED = {
    *(f"merge::general_stable_sorted_permutation_u64_n{n}" for n in (2, 3, 4, 5, 9)),
    "merge::general_stable_sorted_permutation_u8_n9",
    *(f"merge::general_stable_direct_u64_n{n}" for n in (6, 7)),
}
TIMEOUT_DIAGNOSTIC = {"network::insert_tail_contract_u64_start1"}
NEW_CONTROLS = {
    "merge::general_stable_direct_value_corruption_control_u64_n2",
    "network::insert_tail_contract_u64_start1_prefix_frame_control",
    "network::insert_tail_contract_u64_start1_suffix_frame_control",
}
A_U8 = {f"merge::merge_scratch48_contract_u8_n{n}" for n in range(5, 9)}
CONST_B_U64 = {f"merge::general_stable_direct_u64_n{n}" for n in range(2, 6)}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def rows_at(revision, path):
    raw = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=REPO, text=True)
    return list(csv.DictReader(raw.splitlines(), delimiter="\t"))


def short(name):
    return name.split("::verify::", 1)[-1]


def main():
    current = inventory()
    by_name = {short(r["name"]): r for r in current}
    old_manifest = {short(r["name"]): r for r in rows_at(BASE, MANIFEST_PATH)}
    old_scope = {short(r["name"]): r for r in rows_at(BASE, SCOPE_PATH)}
    assert len(old_manifest) == len(old_scope) == 463
    assert set(RETURNED_P1 | DIRECT_ORDINARY | FALLBACK | RETIRED |
               TIMEOUT_DIAGNOSTIC | NEW_CONTROLS | A_U8) <= by_name.keys()

    tree = git("rev-parse", "HEAD:library")
    classes = {}
    for name, src in by_name.items():
        old = old_manifest.get(name)
        if name in NEW_CONTROLS:
            klass = "expected-fail"
        elif name in TIMEOUT_DIAGNOSTIC:
            klass = "timeout-diagnostic"
        elif name in FALLBACK:
            klass = "fallback"
        elif name in RETIRED:
            klass = "retired-duplicate"
        elif name in A_U8:
            klass = "positive-direct"
        elif name in RETURNED_P1 | DIRECT_ORDINARY:
            klass = "ordinary" if not src["opt_in"] else "pending-direct"
        elif old:
            klass = old["class"]
        elif src["opt_in"]:
            klass = "budget-deferred"
        else:
            klass = "ordinary"
        if klass == "ordinary":
            assert not src["opt_in"], (name, "ordinary harness is cfg gated")
        else:
            assert src["opt_in"], (name, klass, "nonordinary harness is not cfg gated")
        classes[name] = klass

    expected = {"ordinary": "PASS", "budget-deferred": "PASS", "pending-direct": "PASS",
                "positive-direct": "PASS", "preexisting-opt-in": "PASS",
                "retired-duplicate": "PASS", "fallback": "PASS",
                "historical-contract": "PASS", "timeout-diagnostic": "TIMEOUT600",
                "expected-fail": "FAILED", "deferred-unsupported": "DEFERRED_UNSUPPORTED"}
    manifest, scope = [], []
    for src in current:
        name = short(src["name"])
        klass = classes[name]
        prior_m, prior_s = old_manifest.get(name), old_scope.get(name)
        # Exact-name old rows keep only clearly historical provenance. Renamed/new
        # work is explicitly source-only and unmeasured on this library tree.
        measured = prior_m is not None and prior_s is not None and name not in (
            RETURNED_P1 | DIRECT_ORDINARY | FALLBACK | NEW_CONTROLS |
            TIMEOUT_DIAGNOSTIC | RETIRED | CONST_B_U64)
        proof_source = prior_s["proof_source"] if measured else "source-only; no eligible INTEG2 candidate result"
        proof_tree = prior_s["proof_library_tree"] if measured else tree + " (unmeasured INTEG2 candidate)"
        applicability = prior_s["gcb_measurement_applicability"] if measured else "no INTEG2 candidate measurement"
        p2 = klass in {"ordinary", "budget-deferred", "positive-direct"}
        row = dict(name=src["name"], configuration="ordinary" if klass == "ordinary" else "opt-in",
                   **{"class": klass}, expectation=expected[klass], p2_candidate="yes" if p2 else "no",
                   p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                   origin=prior_m["origin"] if measured else "INTEG2 source-only",
                   source_library_tree=tree, source_path=src["path"], source_line=src["line"],
                   source_item=compact(src["entry"]))
        manifest.append(row)
        scope.append(dict(name=src["name"], **{"class": klass},
                          property=prior_s["property"] if measured else "proof harness property",
                          domain=prior_s["domain"] if measured else
                          f"candidate source at {tree}:{src['path']}:{src['line']}; static item only",
                          mac_vt_s=prior_s["mac_vt_s"] if measured else "UNKNOWN",
                          mac_status=prior_s["mac_status"] if measured else "UNKNOWN",
                          proof_source=proof_source, proof_library_tree=proof_tree,
                          source_library_tree=tree,
                          gcb_time_s=prior_s["gcb_time_s"] if measured else "UNKNOWN",
                          gcb_rss_kib=prior_s["gcb_rss_kib"] if measured else "UNKNOWN",
                          gcb_measurement_applicability=applicability,
                          p2_candidate="yes" if p2 else "no",
                          p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                          configuration=row["configuration"], expectation=expected[klass],
                          source_path=src["path"], source_line=src["line"], source_item=compact(src["entry"])))

    counts = collections.Counter(classes.values())
    p1 = counts["ordinary"]
    p2_names = sorted(r["name"] for r in manifest
                      if r["class"] in {"ordinary", "budget-deferred", "positive-direct"})
    cfg_names = sorted(r["name"] for r in manifest)
    baseline_manifest = old_manifest.values()
    baseline_p1 = sorted(r["name"] for r in baseline_manifest if r["class"] == "ordinary")
    baseline_p2 = sorted(r["name"] for r in old_manifest.values()
                         if r["class"] in {"ordinary", "budget-deferred", "positive-direct"})
    assert p1 == 197, (p1, counts)
    assert len(p2_names) == 343, (len(p2_names), counts)
    assert len(baseline_p1) == 182 and len(baseline_p2) == 339
    assert len(cfg_names) == len(current)
    assert counts["positive-direct"] == 4
    assert counts["expected-fail"] == 33
    assert counts["timeout-diagnostic"] >= 1

    SCOPE.mkdir(parents=True, exist_ok=True)
    tsv(SCOPE / "manifest.tsv", manifest)
    tsv(SCOPE / "scope.tsv", scope)
    (SCOPE / "p1-ordinary.txt").write_text("\n".join(sorted(r["name"] for r in manifest
        if r["class"] == "ordinary")) + "\n")
    (SCOPE / "p2-ordinary.txt").write_text("\n".join(p2_names) + "\n")
    (SCOPE / "cfg-on.txt").write_text("\n".join(cfg_names) + "\n")
    (SCOPE / "p1-baseline.txt").write_text("\n".join(baseline_p1) + "\n")
    (SCOPE / "p2-baseline.txt").write_text("\n".join(baseline_p2) + "\n")
    for filename, before, after in (("p1-diff-from-baseline.txt", baseline_p1,
                                     sorted(r["name"] for r in manifest if r["class"] == "ordinary")),
                                    ("p2-diff-from-baseline.txt", baseline_p2, p2_names)):
        before_set, after_set = set(before), set(after)
        lines = [*("+ " + n for n in sorted(after_set - before_set)),
                 *("- " + n for n in sorted(before_set - after_set))]
        (SCOPE / filename).write_text("\n".join(lines) + "\n")
    report = dict(status="INTEG2_STATIC_SOURCE_FORECAST_ONLY", baseline=BASE,
                  library_tree=tree, counts=dict(counts), total=len(manifest),
                  p1_ordinary=p1, p2_candidate_ordinary=len(p2_names), cfg_on_total=len(cfg_names),
                  exact_name_sets={"p1": "p1-ordinary.txt", "p2": "p2-ordinary.txt",
                                   "cfg_on": "cfg-on.txt", "p1_baseline": "p1-baseline.txt",
                                   "p2_baseline": "p2-baseline.txt",
                                   "p1_diff": "p1-diff-from-baseline.txt",
                                   "p2_diff": "p2-diff-from-baseline.txt"},
                  p2_formula="ordinary + selected budget-deferred + A-u8 N5..8; fallback/retired/diagnostic excluded",
                  limitations=["Source forecast only; not Rust expansion or actual Kani inventory",
                               "All new or renamed INTEG2 harnesses are source-only and unmeasured",
                               "Static P2 patch application/name check is a separate source-only check",
                               "No Rust, Cargo, Kani, build, or CI executed"])
    (SCOPE / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
