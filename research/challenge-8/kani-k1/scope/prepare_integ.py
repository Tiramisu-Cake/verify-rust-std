#!/usr/bin/env python3
"""Build INTEG manifests and historical cost notes from the working tree."""
import collections
import csv
import json
from pathlib import Path

from prepare_scope import FAILED as OLD_FAILED, DEFERRED, compact, describe, tsv
from source_inventory import BASELINE, HERE, P6, PREFIX, ROOT, inventory

LIBRARY_TREE = "4dd5393bbb4524104c8b05cb70910c6836c3b8de"
DIRECT_LIBRARY_TREE = "e16a8ee5 (DIRECT pilot library tree; task-reported)"
DIRECT_RESULTS = HERE.parent / "direct" / "results.tsv"
HARNESS_TABLE = Path("/root/smallsort-pr-drafts/smallsort-harnesses.tsv")
RETIRED = {
    f"merge::general_stable_sorted_permutation_{ty}_n{n}"
    for ty, ns in (("u64", range(2, 6)), ("u8", range(2, 9)))
    for n in ns
}
DIRECT_ORDINARY = {
    *(f"merge::general_stable_direct_u64_n{n}" for n in range(2, 6)),
    *(f"merge::general_stable_direct_u8_n{n}" for n in range(2, 9)),
    "merge::merge_scratch48_contract_u8_n9",
}
DIRECT_POSITIVE = {
    "merge::general_stable_direct_u64_n6",
    "merge::general_stable_direct_u64_n7",
    *(f"merge::merge_scratch48_contract_{ty}_n{n}"
      for ty in ("u64", "u8") for n in range(5, 9)),
}
DIRECT_TIMEOUT = {
    "merge::general_stable_direct_u64_n8",
    "merge::general_stable_direct_u8_n9",
}
DIRECT_FAILED = {
    "merge::general_stable_direct_value_corruption_control_u64_n2",
    "merge::merge_scratch48_unsorted_halves_control_u64_n4",
}
REVISED_DIRECT_CONTROL = "merge::general_stable_direct_value_corruption_control_u64_n2"
FAILED = OLD_FAILED | DIRECT_FAILED


def short(name):
    return name.split("::verify::", 1)[-1]


def main():
    current = inventory()
    by_name = {short(r["name"]): r for r in current}
    assert len(by_name) == 449, len(by_name)
    base = {short(r["name"]): r for r in inventory(BASELINE)}
    assert RETIRED | DIRECT_ORDINARY | DIRECT_POSITIVE | DIRECT_TIMEOUT | DIRECT_FAILED <= by_name.keys()
    assert not (DIRECT_ORDINARY & DIRECT_POSITIVE or DIRECT_ORDINARY & DIRECT_TIMEOUT or
                DIRECT_ORDINARY & DIRECT_FAILED or DIRECT_POSITIVE & DIRECT_TIMEOUT or
                DIRECT_POSITIVE & DIRECT_FAILED or DIRECT_TIMEOUT & DIRECT_FAILED)
    assert len(RETIRED) == 11 and len(DIRECT_ORDINARY) == 12 and len(DIRECT_POSITIVE) == 10
    assert len(DIRECT_TIMEOUT) == 2 and len(DIRECT_FAILED) == 2

    direct = {}
    with DIRECT_RESULTS.open() as f:
        for line, row in enumerate(csv.DictReader(f, delimiter="\t"), 2):
            direct["merge::" + row["name"]] = (line, row)
    c3a = json.loads((HERE / "c3a-evidence.json").read_text())["harnesses"]
    harness = {r["harness"]: r for r in csv.DictReader(HARNESS_TABLE.open(), delimiter="\t")}
    failed_short = set(FAILED)
    deferred_short = set(DEFERRED)

    rows, manifest, domain_map = [], [], []
    for r in current:
        name = short(r["name"])
        old = base.get(name)
        if name in RETIRED:
            klass = "retired-duplicate"
        elif name in DIRECT_POSITIVE:
            klass = "positive-direct"
        elif name in DIRECT_TIMEOUT:
            klass = "timeout-diagnostic"
        elif name in failed_short:
            klass = "expected-fail"
        elif name in deferred_short:
            klass = "deferred-unsupported"
        elif not r["opt_in"]:
            klass = "ordinary"
        elif old and old["opt_in"]:
            klass = "preexisting-opt-in"
        else:
            klass = "budget-deferred"
        if name in DIRECT_ORDINARY:
            assert not r["opt_in"], (name, "direct ordinary is gated")
            klass = "ordinary"
        if klass == "ordinary":
            assert not r["opt_in"], name
        else:
            assert r["opt_in"], (name, klass)

        expect = ("FAILED" if klass == "expected-fail" else
                  "TIMEOUT600" if klass == "timeout-diagnostic" else
                  "DEFERRED_UNSUPPORTED" if klass == "deferred-unsupported" else "PASS")
        row = dict(name=r["name"], configuration="ordinary" if klass == "ordinary" else "opt-in",
                   **{"class": klass}, expectation=expect,
                   p2_candidate="yes" if klass == "positive-direct" else "no",
                   p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                   origin="INTEG DIRECT" if name in direct else
                   "pre-existing opt-in" if old and old["opt_in"] else
                   "P1 budget selection" if old else "INTEG source",
                   source_library_tree=LIBRARY_TREE, source_path=r["path"], source_line=r["line"],
                   source_item=compact(r["entry"]))
        manifest.append(row)

        drec = direct.get(name)
        hrec = harness.get(name)
        if drec:
            dline, d = drec
            p6_time, p6_status = "UNKNOWN", "UNKNOWN"
            proof_source = (f"direct/results.tsv:{dline}; {d['build']} {d['status']}; historical DIRECT result" if
                            name != REVISED_DIRECT_CONTROL else
                            f"direct/results.tsv:{dline}; {d['build']} FAILED; historical control had a different body; "
                            "current shared-oracle control awaits measurement")
            gcb_vt, gcb_rss = d["time"], d["rss"]
            proof_sha = DIRECT_LIBRARY_TREE
            measurement_applicability = ("historical different control body; current shared-oracle control awaits measurement"
                                         if name == REVISED_DIRECT_CONTROL else
                                         "historical DIRECT result on pilot tree; not macOS CI")
        elif r["name"] in c3a:
            c = c3a[r["name"]]
            p6_time, p6_status = "UNKNOWN", "UNKNOWN"
            proof_source = f"{c['source']}; {c['status']}; source match: {c.get('source_match', '')}"
            gcb_vt, gcb_rss = c.get("gcb_vt_seconds", "UNKNOWN"), c.get("memory", "UNKNOWN")
            proof_sha = c["measured_code_library_sha"] + " (measured library tree)"
            measurement_applicability = "historical C3a source; see source_match and C3a notes"
        elif hrec:
            p6_time = hrec["p6_macos_vt_s"] if hrec["p6_macos_vt_s"] else "UNKNOWN"
            p6_status = hrec["p6_macos"] or "UNKNOWN"
            proof_source = f"smallsort-harnesses.tsv:{name}; П-6 macOS; Actions 40748125754 (historical)"
            gcb_vt, gcb_rss = "UNKNOWN", "UNKNOWN"
            proof_sha = P6
            measurement_applicability = "historical P-6 evidence; not a result on INTEG tree"
        else:
            p6_time, p6_status, proof_source, gcb_vt, gcb_rss, proof_sha = (
                "UNKNOWN", "UNKNOWN", "no eligible historical result", "UNKNOWN", "UNKNOWN", LIBRARY_TREE)
            measurement_applicability = "no historical measurement"
        prop, domain = describe(r)
        domain = domain.replace(f"model definitions at {BASELINE}:",
                                f"model definitions at library tree {LIBRARY_TREE}:")
        rows.append(dict(name=r["name"], **{"class": klass}, property=prop, domain=domain,
                         mac_vt_s=p6_time, mac_status=p6_status, proof_source=proof_source,
                         proof_library_tree=proof_sha, source_library_tree=LIBRARY_TREE,
                         gcb_time_s=gcb_vt, gcb_rss_kib=gcb_rss,
                         gcb_measurement_applicability=measurement_applicability,
                         p2_candidate="yes" if klass == "positive-direct" else "no",
                         p2_macos_ci="UNKNOWN" if klass == "positive-direct" else "not applicable",
                         configuration=row["configuration"], expectation=expect,
                         source_path=r["path"], source_line=r["line"], source_item=compact(r["entry"])))
        domain_map.append(dict(name=r["name"], **{"class": klass},
                               source_path=r["path"], source_line=r["line"],
                               union="identity: exact current harness name"))

    tsv(HERE / "manifest.tsv", manifest)
    tsv(HERE / "scope.tsv", rows)
    tsv(HERE / "domain-map.tsv", domain_map)
    lists = {
        "ordinary.txt": {"ordinary"},
        "extended-positive.txt": {"budget-deferred", "positive-direct", "preexisting-opt-in"},
        "budget-deferred.txt": {"budget-deferred"},
        "retired-duplicates.txt": {"retired-duplicate"},
        "positive-direct.txt": {"positive-direct"},
        "timeout-diagnostic.txt": {"timeout-diagnostic"},
        "controls-failed.txt": {"expected-fail"},
        "deferred-unsupported.txt": {"deferred-unsupported"},
    }
    for filename, classes in lists.items():
        (HERE / filename).write_text("".join(
            r["name"] + "\n" for r in manifest if r["class"] in classes))

    counts = collections.Counter(r["class"] for r in manifest)
    ordinary = [r for r in manifest if r["class"] == "ordinary"]
    assert len(ordinary) == 176 and len(manifest) == 449
    assert counts["budget-deferred"] == 153
    assert counts["retired-duplicate"] == 11
    assert counts["positive-direct"] == 10
    assert counts["timeout-diagnostic"] == 2
    assert counts["expected-fail"] == 28 and counts["deferred-unsupported"] == 1
    assert counts["preexisting-opt-in"] == 68
    # Incremental P1 proof-time arithmetic is deliberately P-6 only for old names.
    returned = [harness[n] for n in harness if
                harness[n]["part1"] == "opt-in" and harness[n]["part2"] == "ordinary" and
                (n.startswith(("network::swap_contract_u64_n9", "network::swap_contract_u8_n9",
                               "network::swap_contract_u8_n13")) or
                 n == "network::mutating_route_safety_cell_n9_to12" or
                 (n.startswith("network::insertion_safety_u64") and
                  harness[n]["part1"] == "opt-in" and harness[n]["part2"] == "ordinary"))]
    removed = [harness[n] for n in harness if n in RETIRED]
    added_vt = sum(float(x["p6_macos_vt_s"]) for x in returned if x["p6_macos_vt_s"])
    removed_vt = sum(float(x["p6_macos_vt_s"]) for x in removed if x["p6_macos_vt_s"])
    direct_by_class = collections.defaultdict(list)
    for n in DIRECT_ORDINARY | DIRECT_POSITIVE | DIRECT_TIMEOUT | DIRECT_FAILED:
        if n in direct:
            direct_by_class["ordinary" if n in DIRECT_ORDINARY else
                            "positive-direct" if n in DIRECT_POSITIVE else
                            "timeout-diagnostic" if n in DIRECT_TIMEOUT else "expected-fail"].append(direct[n][1])
    direct_summary = {}
    for klass, vals in sorted(direct_by_class.items()):
        valid = [float(v["time"]) for v in vals if v["time"] not in ("", "None")]
        direct_summary[klass] = dict(rows=len(vals), known_time_count=len(valid),
                                     gcb_time_sum_s=round(sum(valid), 4),
                                     gcb_time_max_s=max(valid) if valid else None,
                                     timeout_count=sum(v["status"] == "TIMEOUT" for v in vals),
                                     gcb_rss_max_kib=max((int(v["rss"]) for v in vals
                                                          if v["rss"].isdigit()), default=None))
    metrics = dict(status="INTEG_STATIC_FORECAST_ONLY", library_tree=LIBRARY_TREE,
                   counts=dict(counts), total=len(manifest), ordinary=len(ordinary),
                   p2_candidate_ordinary=339, p2_formula="328 + 12 ordinary DIRECT + 10 positive DIRECT - 11 retired duplicates",
                   p6_incremental=dict(returned_count=len(returned), returned_known_vt_s=round(added_vt, 4),
                                       retired_count=len(removed), retired_known_vt_s=round(removed_vt, 4),
                                       new_direct_ordinary_macos_vt="UNKNOWN; no P-6 macOS VT evidence"),
                   direct_results_gcb=direct_summary,
                   limitations=["Source inventory forecast, not Rust expansion or actual kani list",
                                "P-6 VT is historical harness VT, not a runtime prediction",
                                "direct/results.tsv timings and RSS are GCB measurements; not Mac VT",
                                "P-7 autoharness is excluded; no cross-platform coefficient or jobs estimate"])
    (HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    write_cost_note(metrics)
    print(json.dumps({"counts": dict(counts), "ordinary": len(ordinary),
                      "p2_candidate_ordinary": 339, "p6_incremental": metrics["p6_incremental"],
                      "direct_results_gcb": direct_summary}, ensure_ascii=False, indent=2))


def write_cost_note(metrics):
    inc = metrics["p6_incremental"]
    lines = ["# INTEG scope cost note", "",
             "Static arithmetic from the historical P-6 macOS harness VT table; this is not a runtime forecast.",
             "P-6 partition source: Actions run `40748125754`, all 8 partitions. P-7 autoharness is excluded.", "",
             "| Change in P1 | Names | Known P-6 macOS ΣVT, seconds |", "|---|---:|---:|"]
    lines += [f"| Returned to ordinary: 3 swap + 1 mutating route + 27 plain insertion | {inc['returned_count']} | +{inc['returned_known_vt_s']:.1f} |",
              f"| Retired duplicate callers | {inc['retired_count']} | −{inc['retired_known_vt_s']:.1f} |",
              "| New DIRECT ordinary | 12 | UNKNOWN (no P-6 macOS VT) |", "",
              "DIRECT measurements from `direct/results.tsv` are GCB evidence and are reported separately below. Their elapsed seconds and RSS are not added to P-6 macOS VT.", "",
              "| DIRECT class | Rows | Known historical GCB time Σ, seconds | Timeout rows | Max GCB RSS, KiB |", "|---|---:|---:|---:|---:|"]
    for klass, d in metrics["direct_results_gcb"].items():
        lines.append(f"| {klass} | {d['rows']} | {d['gcb_time_sum_s']:.4f} | {d['timeout_count']} | {d['gcb_rss_max_kib']} |")
    lines += ["", "The expected-fail row contains historical failed-control timings, not successful proof times. The revised shared-oracle control's old GCB result used a different body; its current result awaits measurement.",
              "No P-7 autoharness projection, division by job count, or GCB-to-Mac coefficient is applied.", ""]
    (HERE / "integ-cost.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
