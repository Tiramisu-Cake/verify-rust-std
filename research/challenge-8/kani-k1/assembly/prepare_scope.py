#!/usr/bin/env python3
"""Generate ASSEMBLY's static scope from the current source inventory.

This is a source forecast only. Historical measurements remain attributed to
their original library/source trees and are not promoted to this candidate.
"""
import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

SCOPE = Path(__file__).resolve().parents[1] / "scope"
sys.path.insert(0, str(SCOPE))
from prepare_scope import compact, tsv  # noqa: E402
from source_inventory import BASELINE, HERE, inventory  # noqa: E402

INTEG = "ddcc33f837"
MANIFEST_PATH = "research/challenge-8/kani-k1/scope/manifest.tsv"
SCOPE_PATH = "research/challenge-8/kani-k1/scope/scope.tsv"
DIRECT_SOURCES = {
    "merge::general_direct_u64_n6": ("f052d6b7ec", "73fb790ad0d78e81c5a2928651650398dbe7d673", "OPT G1 SUCCESS"),
    "merge::general_direct_u64_n8": ("f052d6b7ec", "c81c10e3061e07bb83c732d81413632ada757d2c", "OPT G2 SUCCESS"),
    "merge::general_direct_u64_n7": ("f28909ac02823ffd652a3d530d6b96add6bd4fea", "30b8b975c574dd76a6e770c7001e2a85577dc578",
                                     "BACKING2 SUCCESS; coordinator source/library SHA and covers confirmed"),
    "merge::stable_direct_u64_n6": ("f28909ac02823ffd652a3d530d6b96add6bd4fea", "30b8b975c574dd76a6e770c7001e2a85577dc578",
                                     "BACKING2 SUCCESS; coordinator source/library SHA and covers confirmed"),
    "merge::stable_direct_u64_n7": ("f28909ac02823ffd652a3d530d6b96add6bd4fea", "30b8b975c574dd76a6e770c7001e2a85577dc578",
                                     "BACKING2 SUCCESS; coordinator source/library SHA and covers confirmed"),
    "merge::stable_direct_u64_n8": ("bff6e4863e4f69cfbd3b3f0cda4cc01e9d9f3c22", "740d22674ca200f3270fb298651302019d347828", "BACKING SUCCESS"),
}
UNSTABLE_DONOR = "78c040559f448ea3cf05ec152ab1143014068570"
UNSTABLE_MEASUREMENTS = {
    "types::sorted_permutation_traits_general_drop_u8_n8":
        ("5ff343a759b87c3927f7f3f90981d15f30e9e946", "SUCCESS", "G1"),
    "types::sorted_permutation_traits_fallback_cell_u8_n8":
        ("5ff343a759b87c3927f7f3f90981d15f30e9e946", "TIMEOUT", "G1"),
    "types::sorted_permutation_traits_stable_fallback_cell_u8_n8":
        ("b177a4bd5d46ae30edf1d75379ff7c43a7f19720", "SUCCESS", "G3"),
    "types::sorted_permutation_traits_unstable_fallback_cell_u8_n8":
        ("b177a4bd5d46ae30edf1d75379ff7c43a7f19720", "SUCCESS", "G3"),
    "types::sorted_permutation_traits_general_drop_u8_n9":
        ("b177a4bd5d46ae30edf1d75379ff7c43a7f19720", "TIMEOUT", "G3"),
}
CONTROL_DONOR = "bff6e4863e4f69cfbd3b3f0cda4cc01e9d9f3c22"
CONTROL_MEASUREMENT = "740d22674ca200f3270fb298651302019d347828"

DIRECT_GENERAL = {f"merge::general_direct_u64_n{n}" for n in (6, 7, 8)}
DIRECT_STABLE = {f"merge::stable_direct_u64_n{n}" for n in (6, 7, 8)}
DIRECT_NAMES = DIRECT_GENERAL | DIRECT_STABLE
COMBINED_B_RETIRED = {f"merge::general_stable_direct_u64_n{n}" for n in (6, 7)}
HISTORICAL_CONTRACT = {f"merge::merge_scratch48_contract_u64_n{n}" for n in range(5, 9)}
POSITIVE_A_U8 = {f"merge::merge_scratch48_contract_u8_n{n}" for n in range(5, 9)}
UNSTABLE_ORDINARY = {
    "types::sorted_permutation_traits_general_drop_u8_n8",
    "types::sorted_permutation_traits_stable_fallback_cell_u8_n8",
    "types::sorted_permutation_traits_unstable_fallback_cell_u8_n8",
}
UNSTABLE_TIMEOUT = {
    "types::sorted_permutation_traits_fallback_cell_u8_n8",
    "types::sorted_permutation_traits_general_drop_u8_n9",
}
NEW_CONTROLS = {
    "merge::stable_direct_value_corruption_control_u64_n2",
    "merge::merge_aggregate_unsorted_halves_control_u64_n4",
    "merge::merge_aggregate_allocation_bounds_control_u64",
}
def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def revision_tsv(revision, path):
    raw = subprocess.check_output(["git", "show", f"{revision}:{path}"], text=True)
    return list(csv.DictReader(raw.splitlines(), delimiter="\t"))


def short(name):
    return name.split("::verify::", 1)[-1]


def main():
    current = inventory()
    by_name = {short(r["name"]): r for r in current}
    baseline = inventory(INTEG)
    assert len(baseline) == 449
    old_manifest = {short(r["name"]): r for r in revision_tsv(INTEG, MANIFEST_PATH)}
    old_scope = {short(r["name"]): r for r in revision_tsv(INTEG, SCOPE_PATH)}
    assert len(old_manifest) == len(old_scope) == 449
    assert sum(r["configuration"] == "ordinary" for r in old_manifest.values()) == 176
    assert len(by_name) == len(current) == 463
    assert DIRECT_NAMES | UNSTABLE_ORDINARY | UNSTABLE_TIMEOUT | NEW_CONTROLS <= by_name.keys()

    tree = git("rev-parse", "HEAD:library")
    rows, manifest, domain_map = [], [], []
    retired = set()
    for n in range(2, 6):
        retired.add(f"merge::general_stable_sorted_permutation_u64_n{n}")
    retired |= {f"merge::general_stable_sorted_permutation_u8_n{n}" for n in range(2, 9)}

    classes = {}
    for name, r in by_name.items():
        old = old_manifest.get(name)
        if name in NEW_CONTROLS:
            klass = "expected-fail"
        elif name in UNSTABLE_TIMEOUT:
            klass = "timeout-diagnostic"
        elif name in UNSTABLE_ORDINARY:
            klass = "ordinary"
        elif name in COMBINED_B_RETIRED:
            klass = "retired-duplicate"
        elif name in HISTORICAL_CONTRACT:
            klass = "historical-contract"
        elif name in POSITIVE_A_U8:
            klass = "positive-direct"
        elif name in DIRECT_NAMES:
            klass = "ordinary" if not r["opt_in"] else "pending-direct"
        elif name.startswith("merge::general_stable_sorted_permutation_u64_n") and name.endswith(("_n6", "_n7", "_n8")):
            n = name.rsplit("_n", 1)[1]
            general = by_name[f"merge::general_direct_u64_n{n}"]
            stable = by_name[f"merge::stable_direct_u64_n{n}"]
            if not general["opt_in"] and not stable["opt_in"]:
                klass = "retired-duplicate"
                retired.add(name)
            else:
                klass = "ordinary" if not r["opt_in"] else "retired-duplicate"
        elif old:
            klass = old["class"]
        elif r["opt_in"]:
            klass = "budget-deferred"
        else:
            klass = "ordinary"
        if klass == "ordinary":
            assert not r["opt_in"], (name, "ordinary harness is cfg gated")
        else:
            assert r["opt_in"], (name, klass, "nonordinary harness must be cfg gated")
        classes[name] = klass

    expected_by_class = {
        "ordinary": "PASS", "budget-deferred": "PASS", "pending-direct": "PASS",
        "positive-direct": "PASS", "preexisting-opt-in": "PASS",
        "retired-duplicate": "PASS", "historical-contract": "PASS",
        "timeout-diagnostic": "TIMEOUT600",
        "expected-fail": "FAILED", "deferred-unsupported": "DEFERRED_UNSUPPORTED",
    }
    for r in current:
        name = short(r["name"])
        klass = classes[name]
        oldm, olds = old_manifest.get(name), old_scope.get(name)
        expect = expected_by_class[klass]
        p2 = "yes" if klass == "positive-direct" else "no"
        origin = oldm["origin"] if oldm else "ASSEMBLY source"
        proof_src = olds["proof_source"] if olds else "no eligible result on this candidate source tree"
        proof_tree = olds["proof_library_tree"] if olds else tree + " (unmeasured candidate source)"
        applicability = olds["gcb_measurement_applicability"] if olds else "no candidate-tree measurement"
        gcb_time = olds["gcb_time_s"] if olds else "UNKNOWN"
        gcb_rss = olds["gcb_rss_kib"] if olds else "UNKNOWN"
        prop = olds["property"] if olds else "proof harness property"
        domain = olds["domain"] if olds else f"model definitions at {BASELINE}:{r['path']}"
        domain = domain.replace("4dd5393bbb4524104c8b05cb70910c6836c3b8de", tree)

        if name in UNSTABLE_ORDINARY | UNSTABLE_TIMEOUT:
            measured_source, source_status, run = UNSTABLE_MEASUREMENTS[name]
            proof_src = (f"UNSTABLE8 {run} {source_status}; code donor {UNSTABLE_DONOR}; "
                         f"measured source {measured_source}; historical source result only, "
                         "not this assembled candidate")
            proof_tree = git("rev-parse", f"{measured_source}:library") + f" (UNSTABLE8 {run} measurement tree)"
            applicability = "UNSTABLE8 source result; not a result on the ASSEMBLY candidate tree"
            origin = "UNSTABLE8 source"
            if name.startswith("types::sorted_permutation_traits_general_drop"):
                prop = "DropKey logical sortedness and full-value permutation"
                domain = ("any u8[N]; logical_less; combined general/stable DropKey route; "
                          "unwind 50; source model in UNSTABLE8 donor tree")
            elif "fallback_cell" in name:
                prop = "Cell logical sortedness and full-value permutation"
                route = "combined fallback" if name in UNSTABLE_TIMEOUT else (
                    "fixed stable route" if "_stable_" in name else "fixed unstable route")
                domain = f"any u8[N] plus probe; logical_less; {route}; unwind 50"
            if name in UNSTABLE_TIMEOUT:
                gcb_time, gcb_rss = "UNKNOWN", "UNKNOWN"
        elif name in DIRECT_NAMES:
            donor, measured_source, source_status = DIRECT_SOURCES[name]
            proof_src = (f"{source_status}; code donor {donor}; measured source {measured_source}; "
                         "historical source harness only, "
                         "not this assembled candidate")
            proof_tree = git("rev-parse", f"{measured_source}:library") + " (direct-route measurement tree)"
            applicability = "source result; not a result on the ASSEMBLY candidate tree"
            origin = "OPT/BACKING source"
            prop = "u64 sortedness and full-value permutation via shared value probe"
            route = "general split route" if name.startswith("merge::general_") else "stable aggregate route"
            scratch = "aggregate 48-slot scratch" if name.startswith("merge::stable_") else "general route scratch"
            domain = (f"any u64[N]; lt_u64; arbitrary full-value probe; {route}; "
                      f"{scratch}; unwind 34")
        elif name in NEW_CONTROLS:
            proof_src = (f"BACKING controls FAILED; code donor {CONTROL_DONOR}; measured source "
                         f"{CONTROL_MEASUREMENT}; historical source body only, not this assembled candidate")
            proof_tree = git("rev-parse", f"{CONTROL_MEASUREMENT}:library") + " (BACKING control measurement tree)"
            applicability = "source control result; not a result on the ASSEMBLY candidate tree"
            origin = "BACKING control source"
            if name == "merge::stable_direct_value_corruption_control_u64_n2":
                prop = "value corruption while preserving sortedness; shared full-value oracle must fail"
                domain = "any u64[2]; stable aggregate route; flip low payload bit; shared probe oracle; unwind 34"
            elif name == "merge::merge_aggregate_unsorted_halves_control_u64_n4":
                prop = "raw merge call violates sorted-halves precondition"
                domain = "initialized u64[4] source halves [6,0] and [2,4]; raw bidirectional_merge; unwind 34"
            else:
                prop = "raw write beyond aggregate scratch allocation"
                domain = "u64 aggregate scratch allocation of 48 elements; write at offset 48; unwind 34"
        if name in DIRECT_NAMES | UNSTABLE_ORDINARY | UNSTABLE_TIMEOUT | NEW_CONTROLS:
            domain += f"; ASSEMBLY harness at {r['path']} in candidate tree {tree}"

        expectation = expect
        row = dict(name=r["name"], configuration="ordinary" if klass == "ordinary" else "opt-in",
                   **{"class": klass}, expectation=expectation, p2_candidate=p2,
                   p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                   origin=origin, source_library_tree=tree, source_path=r["path"],
                   source_line=r["line"], source_item=compact(r["entry"]))
        manifest.append(row)

        macvt = olds.get("mac_vt_s", "UNKNOWN") if olds else "UNKNOWN"
        macstatus = olds.get("mac_status", "UNKNOWN") if olds else "UNKNOWN"
        rows.append(dict(name=r["name"], **{"class": klass}, property=prop, domain=domain,
                         mac_vt_s=macvt, mac_status=macstatus, proof_source=proof_src,
                         proof_library_tree=proof_tree, source_library_tree=tree,
                         gcb_time_s=gcb_time, gcb_rss_kib=gcb_rss,
                         gcb_measurement_applicability=applicability,
                         p2_candidate=p2, p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                         configuration=row["configuration"], expectation=expectation,
                         source_path=r["path"], source_line=r["line"], source_item=compact(r["entry"])))
        domain_map.append(dict(name=r["name"], **{"class": klass}, source_path=r["path"],
                               source_line=r["line"], union="identity: exact current harness name"))

    tsv(SCOPE / "manifest.tsv", manifest)
    tsv(SCOPE / "scope.tsv", rows)
    tsv(SCOPE / "domain-map.tsv", domain_map)
    list_classes = {
        "ordinary.txt": {"ordinary"},
        "extended-positive.txt": {"budget-deferred", "positive-direct", "preexisting-opt-in"},
        "budget-deferred.txt": {"budget-deferred"},
        "retired-duplicates.txt": {"retired-duplicate"},
        "positive-direct.txt": {"positive-direct"},
        "timeout-diagnostic.txt": {"timeout-diagnostic"},
        "controls-failed.txt": {"expected-fail"},
        "deferred-unsupported.txt": {"deferred-unsupported"},
        "pending-direct.txt": {"pending-direct"},
        "historical-contracts.txt": {"historical-contract"},
    }
    for filename, selected in list_classes.items():
        (SCOPE / filename).write_text("".join(r["name"] + "\n" for r in manifest
                                             if r["class"] in selected))

    counts = collections.Counter(classes.values())
    ordinary = counts["ordinary"]
    p2_count = sum(counts[c] for c in ("ordinary", "budget-deferred", "positive-direct"))
    both_routes_ordinary = sum(
        not by_name[f"merge::general_direct_u64_n{n}"]["opt_in"] and
        not by_name[f"merge::stable_direct_u64_n{n}"]["opt_in"]
        for n in (6, 7, 8))
    pending7 = (by_name["merge::general_direct_u64_n7"]["opt_in"] and
                by_name["merge::stable_direct_u64_n7"]["opt_in"])
    assert ordinary == 182 - int(pending7), (ordinary, pending7)
    assert p2_count == ordinary + 153 + 4 and len(manifest) == 463
    assert counts["expected-fail"] == 31 and counts["timeout-diagnostic"] == 4
    assert counts["pending-direct"] == sum(r["opt_in"] for name, r in by_name.items()
                                           if name in DIRECT_NAMES)
    assert counts["pending-direct"] in (0, 1, 2, 3)
    assert counts["retired-duplicate"] == 13 + both_routes_ordinary
    assert counts["historical-contract"] == 4 and counts["positive-direct"] == 4
    old_metrics = json.loads(subprocess.check_output(
        ["git", "show", f"{INTEG}:research/challenge-8/kani-k1/scope/metrics.json"], text=True))
    metrics = dict(status="ASSEMBLY_STATIC_FORECAST_ONLY", baseline=INTEG,
                   library_tree=tree, counts=dict(counts), total=len(manifest), ordinary=ordinary,
                   p2_candidate_ordinary=p2_count,
                   p2_formula="ordinary + 153 budget-deferred + 4 positive A-u8; ordinary is cfg-derived",
                   controls_cfg_total=len(manifest),
                   controls_failed=31,
                   pending_direct=counts["pending-direct"],
                   retired_duplicates=counts["retired-duplicate"],
                   p6_incremental=old_metrics["p6_incremental"],
                   direct_results_gcb=old_metrics["direct_results_gcb"],
                   classification_decisions={
                       "combined_B_u64_N6_N7": ("retired-duplicate: old combined any-stable direct callers "
                                                 "duplicate the prepared route-split pairs; keep opt-in as retired "
                                                 "diagnostics and exclude P2; "
                                                 "their historical SUCCESS remains supporting evidence only"),
                       "A_u64_N5_N8": ("historical-contract: old array-backed fixture is not equivalent to the "
                                       "new aggregate-backed stable route; retain opt-in and exclude P2; "
                                       "historical SUCCESS remains supporting evidence only"),
                       "A_u8_N5_N8": "positive-direct: retain the existing four positive opt-in candidates",
                       "conditional_C_replacement": ("retire C N6/N7/N8 only when both direct routes for that N "
                                                      "are ordinary; current formula is retired=13+fully-promoted "
                                                      "pairs; ordinary=182 only when at least one N7 route is "
                                                      "ordinary, otherwise 181"),
                   },
                   source_claims={"unstable8": ("code donor 78c040559f; G1 measured source 5ff343a759b87c3927f7f3f90981d15f30e9e946; "
                                                "G3 measured source b177a4bd5d46ae30edf1d75379ff7c43a7f19720"),
                                  "direct_u64": ("OPT measured sources 73fb790ad0d78e81c5a2928651650398dbe7d673 and "
                                                 "c81c10e3061e07bb83c732d81413632ada757d2c; BACKING/BACKING2 measured "
                                                 "sources 740d22674ca200f3270fb298651302019d347828 and "
                                                 "30b8b975c574dd76a6e770c7001e2a85577dc578"),
                                  "backing_controls": ("measured source 740d22674ca200f3270fb298651302019d347828; "
                                                       "historical FAILED only; current candidate controls await measurement")},
                   limitations=["Source inventory forecast, not Rust expansion or actual kani list",
                                "Historical source results do not establish results on this candidate library tree",
                                "BACKING2 promotion confirmed; assembled candidate verification is not yet run",
                                "No compiler, Kani, CBMC or CI executed"])
    (SCOPE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": metrics["status"], "library_tree": tree,
                      "counts": dict(counts), "ordinary": ordinary,
                      "p2_candidate_ordinary": p2_count}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
