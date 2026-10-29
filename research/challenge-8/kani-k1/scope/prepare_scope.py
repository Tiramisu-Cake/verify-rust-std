#!/usr/bin/env python3
"""Prepare SCOPE-B manifests/table; --apply synchronizes proof cfgs, preserving review fixes."""
import argparse
import collections
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from selection import select
from source_inventory import BASELINE, HERE, P6, PREFIX, ROOT, inventory, source

FAILED = {
    "assembly::reject_mutant_insert_tail_u8_n2",
    "assembly::reject_mutant_merge_u8_n4",
    "assembly::reject_mutant_merge_up_u8_n2",
    "assembly::reject_mutant_network_prefix_u8_n10",
    "assembly::reject_mutant_swap_u8_n2",
    "correct::reject_unsorted_prefix_insert_tail_u8_n3",
    "merge::drop_duplicate_tag_control_n2",
    "merge::drop_extra_drop_control_n2",
    "merge::drop_general_reachability_control_n2",
    "merge::intrinsic_assumption_safety_control_u64_n4",
    "merge::merge_arbitrary_order_assertion_control_u64_n4",
    "merge::merge_arbitrary_order_permutation_failure_control_u64_n4",
    "merge::merge_rejects_unsorted_halves_control_u64_n4",
    "merge::merge_unsorted_halves_control_u64_n4",
    "merge::merge_unsorted_halves_control_u8_n4",
    "merge::out_of_bounds_pointer_control_u64_n4",
    "merge::overlapping_copy_control_u64_n4",
    "merge::unchecked_add_overflow_control_u64_n4",
    "network::control_network_mutant_presorted_u8_n10",
    "network::control_network_normal_return_assertion",
    "network::control_order_violation_assertion",
    "network::control_order_violation_merge_assertion",
    "network::control_swap_contract_precondition_u8",
    "smoke::reject_efficient_swap_bytes9",
    "types::reject_logical_permutation_drop_n2",
    "types::reject_logical_sortedness_cell_n2",
}
DEFERRED = {"network::swap_contract_zero_sized_n2"}


def tsv(path, rows):
    assert rows
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def compact(s):
    return " ".join(s.split())


def describe(r):
    mod, m, n, args = r["module"], r["macro"], r["name"].split("::")[-1], r["args"]
    # Exact invocation is included independently, so every type/length/route literal is retained.
    domain = f"{compact(r['entry'])}; model definitions at {BASELINE}:{r['path']}"
    prop, route = "bounded safety / normal return", ""
    if mod == "types":
        prop = "logical sortedness + full logical multiset, stable/unstable trait entry"
        route = "Cell<u8>: !Freeze fallback/insertion; DropKey: Freeze non-Copy general; scratch48"
    elif mod == "smoke":
        prop = "efficient-swap finite type predicate matrix"
        route = "u8/u16/u64/u128, bytes9/16/17/85/86, SwapDrop, Cell<i32>, unit"
    elif m == "fallback_stub_harness":
        prop, route = "sortedness + full-value probe multiplicity", "direct fallback, insert_tail verified stub"
    elif m == "general_stub_harness":
        prop, route = "sortedness + full-value probe multiplicity", "stable trait / direct general; insert_tail + merge stubs; scratch48"
    elif m == "scratch_contract_harness":
        prop, route = "insert_tail contract + frame", "scratch allocation48, begin {0,6,7}, region lengths5..8, key upper-bit order"
    elif n == "contract_insert_tail_u8_prefix":
        prop, route = "insert_tail contract + suffix frame", "[u8;17], begin0, tail1..16, lt_u8=(a>>1)<(b>>1), sorted-prefix requires"
    elif m in ("define_merge_contract_harness", "define_small_merge_contract_harness"):
        prop, route = "bidirectional_merge contract", "full-width u8/u64, key upper-bit order, exact source/destination arrays, disjoint; sorted halves requires"
    elif m == "define_sort4_contract_and_comparator_harnesses":
        prop = "sort4_stable contract" if "contract" in n else "sort4 safety under arbitrary reading comparator"
        route = "exact N4 source/destination arrays; disjoint, u8/u64, full values"
    elif m == "define_general_sortedness_harness":
        prop, route = "sortedness + full-value probe multiplicity", "direct general / stable trait, real insertion/sort4, merge verified stub, scratch48"
    elif m in ("define_fallback_property_harness", "define_fallback_route_harness"):
        prop, route = "sortedness + full-value probe multiplicity", "real direct fallback/insertion, exact u8/u64 arrays, upper-bit key order"
    elif m == "define_route_safety_harness":
        prop, route = "safety + three normal-return covers", "route0 direct general u64 / route1 unstable non-Copy WrappedU64 / route2..255 stable u64; scratch48; real bodies"
    elif m == "define_drop_route_harness":
        prop = "normal-return Drop count" if "drop_count" in n else "tag multiplicity"
        route = "DropTaggedValue{u64 key,u8 tag}; real bodies, arbitrary reading comparator; "
        route += "general/stable scratch48" if args[2] == "true" else "fallback/insertion at offset1"
    elif m == "insert_tail_contract_case":
        prop, route = "insert_tail contract + prefix/suffix frame", "[u64;17], lt_u64 upper-bit key order, exact START and all tail literals, sorted-prefix requires"
    elif m == "network_correctness_cases":
        prop = "sortedness; full-route permutation only N<9, structural argument plus separate suffix witnesses above"
        route = "real unstable trait, full-width u8/u64, strict total order, width9/13 networks then insertion suffix"
    elif m == "insertion_permutation_case":
        prop, route = "real insertion suffix full-value permutation", "exact array; insertion offset9 if N<13 else13; arbitrary reading comparator, no sorted-prefix assumption"
    elif m in ("insertion_safety_cases", "mutating_insertion_cases", "insertion_offset_group_cases"):
        prop, route = "safety + all selected offset covers", "real insertion; full u64 or TaggedKey Cell with both compared keys mutated; exact N and offsets from invocation"
    elif m == "mutating_route_permutation_case":
        prop, route = "tag multiplicity + original tag sequence", "TaggedKey Cell, mutating comparator, real stable/unstable/insertion, offsets1..N; N2/3/4"
    elif m == "mutating_route_cases":
        prop, route = "safety + stable/unstable normal-return covers", "TaggedKey Cell !Freeze; mutate both compared keys, real fallback, exact length union"
    elif m in ("dispatch_safety_cases", "dispatch_pair_safety_cases", "dispatch_reachability_case"):
        prop = "real trait dispatch safety + normal return"
        route = "stable/unstable per invocation; u8 efficient-copy network vs stable general; bytes16/17/85 general; Drop non-Copy general; bytes86 unstable fallback; stable scratch48"
    elif m in ("unstable_dispatch_network_cases", "unstable_freeze_network_cases"):
        prop, route = "safety + normal return", "real u64 unstable/Freeze trait, arbitrary volatile reading comparator, network/insertion/merge, exact lengths"
    elif m in ("swap_contract_exact_array_case", "swap_contract_arbitrary_indices_case") or n.startswith("swap_contract_"):
        prop = "swap_if_less contract + frame / both swap directions"
        if "four_positions" in n:
            route = "exact allocation4, distinct selected positions, u8/i32/u64 upper-bit key comparator"
        elif "indices_n17" in n or m == "swap_contract_arbitrary_indices_case":
            route = "exact allocationN, arbitrary distinct positions, strict_less<u8/u64>, full values"
        else:
            route = "exact allocation2, (0,1)/(1,0); strict u8/u64, byte-array first-byte key, Drop/Cell logical key"
    elif mod == "assembly":
        prop = "real-body sensitivity positive witness" if m == "paired_case" else "stable unit-ZST safety + normal return"
        route = "real swap / insertion / merge-up / merge / network prefix selected by invocation" if m == "paired_case" else "unit ZST exact N1/2/7/8/16/17/31/32, stable trait, scratch48"
    return prop, route + "; " + domain


def dependencies(r):
    n, m = r["name"].split("::")[-1], r["macro"]
    attrs = r["attributes"]
    stubs = re.findall(r"kani\s*::\s*stub_verified\s*\(([^)]+)\)", attrs)
    proofs = []
    gap = "none: no verified-contract stub assumption"
    if stubs:
        gap = "UNCLOSED allocation-locality transfer; isolated proof_for_contract is not caller-domain proof"
    if m == "fallback_stub_harness":
        t = r["args"][1]
        if t == "u8":
            proofs = ["correct::contract_insert_tail_u8_prefix: [u8;17], begin0 tail1..16; exact caller allocationN differs"]
        else:
            proofs = ["merge::insert_tail_contract_integer_types_n2_to16: opt-in base-region exact arrays2..16; network::insert_tail_contract_u64_start1..15: [u64;17] shifted regions do NOT prove begin0"]
    elif m in ("define_general_sortedness_harness", "general_stub_harness"):
        t, length = r["args"][1], int(r["args"][3])
        if length >= 2:
            suffix = "n2_to4" if length <= 4 else f"n{length}"
            proofs = [f"merge::merge_contract_{t}_{suffix}: matching T/N/comparator, exact arrays; caller source/dst scratch48 geometry not established"]
        else:
            gap = "no merge call at N0/1; stub attribute present but callee unreachable"
        if m == "general_stub_harness":
            proofs.append(f"correct::contract_insert_tail_{t}_scratch: allocation48, starts0/6/7, lengths5..8")
    used = [compact(x) for x in stubs]
    contract = re.findall(r"kani\s*::\s*proof_for_contract\s*\(([^)]+)\)", attrs)
    if contract:
        used += ["proof_for_contract=" + compact(x) + "; requires assumed, ensures/frame checked in listed domain" for x in contract]
    if not used:
        used = ["real callee bodies; no verified-contract stub assumption"]
    if "kani::stub(" in attrs:
        used.append("manual panic boundary (or selected mutant for negative controls); preserve source attribute")
    return " | ".join(proofs) or "none", gap, " | ".join(used)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    baseline = inventory(BASELINE)
    ordinary = [r for r in baseline if not r["opt_in"]]
    assert len(ordinary) == 328
    if args.apply:
        current = {r["name"]: r for r in inventory()}
        by_module = collections.defaultdict(dict)
        for r in ordinary:
            item = current[r["name"]]
            offset, keep = item["offset"], select(r)[1]
            previous = by_module[r["module"]].setdefault(offset, keep)
            assert previous == keep, "one macro invocation cannot mix cfg decisions"
        for module, offsets in by_module.items():
            text = source(module)
            for offset, keep in sorted(offsets.items(), reverse=True):
                # Attach at the first non-whitespace byte; retain preceding blank lines.
                while text[offset].isspace():
                    offset += 1
                cfg = "#[cfg(kani_smallsort_controls)]\n"
                if keep and text.startswith(cfg, offset):
                    text = text[:offset] + text[offset + len(cfg):]
                elif not keep and not text.startswith(cfg, offset):
                    text = text[:offset] + cfg + text[offset:]
            (ROOT / (module + ".rs")).write_text(text)

    mac_path = HERE.parent / "c3c-inputs/mac-times.tsv"
    mac = {row[0]: float(row[1]) for row in csv.reader(mac_path.open(), delimiter="\t")}
    c3a = json.loads((HERE / "c3a-evidence.json").read_text())["harnesses"]
    memory = list(csv.DictReader((HERE.parent / "c3c/per-harness-memory.tsv").open(), delimiter="\t"))
    memory = {r["harness"]: r for r in memory if r["запуск"] == "baseline-memory"}
    timeouts = {PREFIX + n for n in (
        "merge::merge_contract_u64_n16", "network::insertion_permutation_u64_n12",
        "network::insert_tail_contract_u64_start1")}
    rows, mapping, groups = [], [], collections.defaultdict(list)
    for r in ordinary:
        name = r["name"]
        group, keep, reason = select(r)
        prop, domain = describe(r)
        required, gap, used = dependencies(r)
        time = "UNKNOWN" if name in c3a or name in timeouts else mac[name]
        status = "UNKNOWN" if name in c3a else "TIMEOUT600" if name in timeouts else "SUCCESS"
        proof_source = "П-6 partitions 8/8, Actions 40748125754; task-reported historical evidence"
        proof_sha, head, gcb, mem = P6, "UNKNOWN", "UNKNOWN", "UNKNOWN (not zero)"
        if name in memory:
            mm = memory[name]
            mem = (f"GCB baseline CBMC_HWM_KiB={mm['CBMC_HWM_KiB']}; "
                   f"head={mm['исходный_SHA']}; library={BASELINE}; build={mm['ID_сборки']}; "
                   f"attribution={mm['атрибуция']}; no Mac peak / whole-job bound")
        if name in c3a:
            c = c3a[name]
            proof_source = f"RESULT-C3A (see RESULT-C3A-source.md); {c['status']}; {c.get('source_match', '')}"
            proof_sha = c["measured_code_library_sha"] + " (library tree)"
            head, gcb, mem = c["measurement_head"], c["gcb_vt_seconds"], c["memory"]
        row = dict(name=name, family=group, property=prop, domain=domain,
                   required_proofs=required, contract_domain_gap=gap, used_contracts=used,
                   mac_vt_s=time, mac_status=status,
                   mac_source="UNKNOWN: C3a has no eligible r group" if name in c3a else
                   f"{mac_path.relative_to(HERE.parent)}; П-6 mac autoharness; {P6}" if name not in timeouts else
                   f"TASK-SCOPE/RESULT-C3C; П-6 mac autoharness; {P6}; timeout limit not VT",
                   proof_source=compact(proof_source), proof_sha=proof_sha,
                   measurement_head=head, gcb_vt_s=gcb, memory=mem,
                   decision="ordinary" if keep else "opt-in", reason=reason,
                   source_sha=BASELINE, path=r["path"], baseline_line=r["line"],
                   source_item=compact(r["entry"]))
        rows.append(row)
        mapping.append(dict(original=name, successors=name, union="identity: exact original domain unchanged",
                            original_ordinary="yes" if keep else "no",
                            original_additionally_opt_in="no separate copy; also compiled with controls" if keep else "yes",
                            split="none; no C3c successor imported"))
        groups[group].append(row)
    tsv(HERE / "scope.tsv", rows)
    tsv(HERE / "domain-map.tsv", mapping)
    manifest = []
    for r in baseline:
        name, short = r["name"], r["name"][len(PREFIX):]
        is_ordinary = not r["opt_in"] and select(r)[1]
        expect = "DEFERRED_UNSUPPORTED" if short in DEFERRED else "FAILED" if short in FAILED else "PASS"
        assert not is_ordinary or expect == "PASS"
        manifest.append(dict(name=name, configuration="ordinary" if is_ordinary else "opt-in",
                             expectation=expect, origin="pre-existing opt-in" if r["opt_in"] else "e9655515 ordinary",
                             note="ZST contract instrumentation unsupported, not an expected counterexample" if short in DEFERRED else
                             "intended expectation; not a new proof result"))
    assert FAILED | DEFERRED <= {r["name"][len(PREFIX):] for r in baseline}
    tsv(HERE / "manifest.tsv", manifest)
    for filename, predicate in (
        ("ordinary.txt", lambda r: r["configuration"] == "ordinary"),
        ("extended-positive.txt", lambda r: r["configuration"] == "opt-in" and r["expectation"] == "PASS"),
        ("controls-failed.txt", lambda r: r["expectation"] == "FAILED"),
        ("deferred-unsupported.txt", lambda r: r["expectation"] == "DEFERRED_UNSUPPORTED"),
    ):
        (HERE / filename).write_text("".join(r["name"] + "\n" for r in manifest if predicate(r)))
    def stats(rr):
        times = [r["mac_vt_s"] for r in rr if isinstance(r["mac_vt_s"], float)]
        return dict(count=len(rr), known_count=len(times), known_vt_sum_s=round(sum(times), 4),
                    known_max_s=max(times) if times else None,
                    known_above_120=sum(t > 120 for t in times),
                    unknown=sum(r["mac_status"] == "UNKNOWN" for r in rr),
                    timeout600=sum(r["mac_status"] == "TIMEOUT600" for r in rr))
    keep = [r for r in rows if r["decision"] == "ordinary"]
    metrics = dict(status="PROPOSED_SCOPE_CI_NOT_TESTED", baseline=BASELINE, p6=P6,
                   source_mac_sha256=hashlib.sha256(mac_path.read_bytes()).hexdigest(),
                   before=stats(rows), ordinary=stats(keep),
                   moved=stats([r for r in rows if r["decision"] == "opt-in"]),
                   groups={k: dict(before=stats(v), after=stats([r for r in v if r["decision"] == "ordinary"]))
                           for k, v in sorted(groups.items())},
                   manifests=dict(collections.Counter(r["configuration"] + "/" + r["expectation"] for r in manifest)),
                   notes=["Known sum plus 4 unknown C3a times, not zero; no confirmed full max or >120 count",
                          "jobs3 => at most 3 simultaneous proofs; up to 3 known-heavy proofs may overlap",
                          "VT is not job wall or machine memory, all predictions require same-SHA CI"])
    (HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: metrics[k] for k in ("status", "before", "ordinary", "moved", "manifests")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
