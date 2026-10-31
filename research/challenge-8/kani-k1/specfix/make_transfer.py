#!/usr/bin/env python3
"""Build specfix/TRANSFER.tsv from specdiag/callers.tsv plus manifest rows missing from it.

Data only: reads the frozen INTEG2 manifest and the SPECDIAG caller map, writes one TSV row per
harness. StageA leaves every ordinary annotation unchanged, so each row records the StageB
target/profile plan and NOT_RUN/OPEN evidence; nothing here is proof credit.
"""
import csv, sys
from pathlib import Path

K1 = Path(__file__).resolve().parents[1]
man = {r["name"].rsplit("::", 1)[1]: r for r in csv.DictReader(open(K1 / "integ2/scope/manifest.tsv"), delimiter="\t")}
callers = list(csv.DictReader(open(K1 / "specdiag/callers.tsv"), delimiter="\t"))

OLD = {
    "swap_if_less": ("a!=b; same_allocation x2; can_dereference x2; can_write x2",
                     "byte same() transfer by pre-state F decision (F called in old); pair order calls F post-state",
                     "2 positions"),
    "insert_tail": ("valid_sorted_tail: writable geometry + F-sorted prefix (calls F)",
                    "F-sorted [begin,tail] (calls F); old(probe_count)==probe_count",
                    "[begin,tail]"),
    "sort4_stable": ("valid_sort4_regions: can_write src+dst, disjoint (no init premise)",
                     "F-sorted dst4 (calls F); probe_count(src4)==probe_count(dst4)",
                     "dst[0..4]"),
    "bidirectional_merge": ("2<=len<=32; valid_merge_destination; merge_inputs_are_sorted (calls F)",
                            "F-sorted_unrolled dst (calls F); probe_count_unrolled equal",
                            "dst[0..len]"),
}
NEW = {
    "swap_if_less": ("swap_profile", "swap_geometry; canonical fn-pointer guard",
                     "model transfer by pure pre-model comparison; model pair order"),
    "insert_tail": ("insert_tail_profile", "canonical guard; tail_region (size>0, same alloc, bounds before distance, 1<=d<32, can_dereference+can_write) && model-sorted prefix",
                    "model-sorted region; old(scalar model_count)==model_count"),
    "sort4_stable": ("sort4_profile", "sort4_regions (can_dereference src4, can_write dst4, disjoint); canonical guard",
                     "model-sorted dst4; model_count(src4)==model_count(dst4)"),
    "bidirectional_merge": ("merge_profile", "canonical guard; merge_regions (2<=N<=32 first) && model-sorted halves",
                            "model-sorted dst; model_count equal"),
}
STAGEA_INSTANCE = {
    "swap_contract_four_positions_u8": "merge::specfix::swap_profile_four_positions_u8",
    "swap_contract_cell_i32_n2": "merge::specfix::swap_profile_cell_i32_n2",
    "swap_contract_drop_u8_n2": "network::swap_profile_drop_u8_n2",
    "sort4_contract_u64_n4": "merge::specfix::sort4_profile_u64_n4",
    "sort4_contract_bytes16_n4": "merge::specfix::sort4_profile_bytes16_n4",
    "contract_insert_tail_u8_prefix": "merge::specfix::insert_tail_profile_u8_prefix",
    "insert_tail_contract_u64_start1_tail2_to8": "merge::specfix::insert_tail_profile_u64_start1_tail2_to8",
    "merge_contract_u8_n8": "merge::specfix::merge_profile_u8_n8",
}
STAGEA_TYPES = {"u8", "u64", "[u8;16]", "Cell<i32>", "DropValue"}
TARGETS = ["swap_if_less", "insert_tail", "sort4_stable", "bidirectional_merge"]

def kind_of(chain, name):
    if "proof_for_contract" in chain:
        return "PFC"
    if "stub_verified" in chain:
        return "stub_verified"
    return "real-body"

def families(fam):
    return [t for t in TARGETS if t in fam]

def row_for(name, fam, T, F, N, backing, chain, pfc_src, origin):
    m = man.get(name, {})
    p1 = "yes" if m.get("configuration") == "ordinary" else "no"
    p2 = "yes" if m.get("p2_candidate") == "yes" else "no"
    kind = kind_of(chain, name)
    fams = families(fam)
    old = [OLD[t] for t in fams]
    new = [NEW[t] for t in fams]
    mutating = "Cell<TaggedKey" in T or "mutat" in name or "arbitrary" in F.lower() or "volatile_reading" in F
    if kind == "PFC":
        prof = new[0][0] if new else "?"
        inst = STAGEA_INSTANCE.get(name, "")
        canon = "lt_*" if F.startswith("lt_") else F
        stageb = (f"retarget PFC name to {prof}::<tag(T={T},F={canon})>; F item -> canonical fn pointer is a new instance; "
                  + ("StageA profile type available" if T.replace(" ", "") in STAGEA_TYPES else "needs new tag/profile impl"))
        evidence = (f"StageA opt-in instance {inst}: G1 row" if inst else "no StageA instance") + "; StageB proof NOT_RUN"
        shim = "none (PFC calls profile; profile PFC runs real raw helper)"
    elif kind == "stub_verified":
        prof = "+".join(n[0] for n in new)
        stageb = f"kani::stub(raw target, adapter) + stub_verified({prof}); consumer F = fn pointer to canonical lt_*"
        shim = "adapter prototype only for bidirectional_merge (merge_adapter); insert/swap adapters StageB"
        evidence = "adapter mechanism: G1 row 10 (merge, u8 N2); this consumer NOT_RUN; binding OPEN"
    else:
        prof = "none (no contract clause consumed)"
        stageb = ("unchanged real body; arbitrary/mutating callback safety stays real-body" if mutating
                  else "unchanged real body; probe-count oracle now guarded (F05)")
        shim = "none"
        evidence = "source unchanged except matches_value_probe guard; fresh run NOT_RUN"
    status = ("StageA: ordinary annotation unchanged (old generic clause stands, F03 OPEN)" if kind != "real-body"
              else "StageA: no contract dependency")
    return {
        "harness": name, "row_origin": origin, "P1_member": p1, "P2_member": p2,
        "manifest_class": m.get("class", "?"), "consumer_kind": kind, "target_family": fam,
        "T": T, "F": F, "N_and_offsets": N, "backing_init_frame": backing,
        "old_requires": " | ".join(o[0] for o in old) or "-",
        "old_ensures": " | ".join(o[1] for o in old) or "-",
        "old_frame": " | ".join(o[2] for o in old) or "-",
        "stageB_target": prof,
        "new_requires": " | ".join(n[1] for n in new) if kind != "real-body" else "-",
        "new_ensures_frame": " | ".join(n[2] for n in new) if kind != "real-body" else "-",
        "model_probe": ("typed full model + shared typed probe" if kind != "real-body" else "unchanged (byte probe, now guarded) or none"),
        "shim_stub_plan": shim, "stageB_plan": stageb, "matching_evidence": evidence,
        "property_preservation": ("same property names/domains planned; source-equivalence argument only, no proof"),
        "status": status, "old_chain": chain, "old_matching_PFC": pfc_src,
    }

rows = []
seen = set()
for r in callers:
    rows.append(row_for(r["harness"], r["target_family"], r["T"], r["F"], r["N_and_offsets"],
                        r["backing_init_and_observed_frame"], r["caller_to_stub_to_target"],
                        r["matching_PFC_source_and_binding"], "callers.tsv"))
    seen.add(r["harness"])
OMISSIONS = {
    "contract_insert_tail_u8_prefix": ("insert_tail", "u8", "lt_u8", "[u8;17], begin=0, tail 1..=16", "initialized exact array; suffix frame asserted", "proof_for_contract(insert_tail) -> insert_tail"),
    "contract_insert_tail_u64_scratch": ("insert_tail", "u64", "lt_u64", "scratch48 starts 0/6/7 len 5..8", "initialized scratch; outside frame asserted", "proof_for_contract(insert_tail) -> insert_tail"),
    "contract_insert_tail_u8_scratch": ("insert_tail", "u8", "lt_u8", "scratch48 starts 0/6/7 len 5..8", "initialized scratch; outside frame asserted", "proof_for_contract(insert_tail) -> insert_tail"),
    "sort4_contract_type_matrix_n4": ("sort4_stable", "i32|u64|[u8;16]|[u8;85]", "lt_i32/lt_u64/lt_b16/lt_b85", "4", "exact arrays, dst uninit", "proof_for_contract(sort4_stable) -> sort4_stable"),
    "sort4_contract_i32_control_n4": ("sort4_stable", "i32", "lt_i32", "4", "exact arrays, dst uninit", "proof_for_contract(sort4_stable) -> sort4_stable"),
    "sort4_contract_bytes16_control_n4": ("sort4_stable", "[u8;16]", "lt_b16", "4", "exact arrays, dst uninit", "proof_for_contract(sort4_stable) -> sort4_stable"),
    "sort4_contract_bytes85_control_n4": ("sort4_stable", "[u8;85]", "lt_b85", "4", "exact arrays, dst uninit", "proof_for_contract(sort4_stable) -> sort4_stable"),
    "insert_tail_contract_u64_start1": ("insert_tail", "u64", "lt_u64", "[u64;17] begin=1 tails 2..16", "prefix/suffix frame", "proof_for_contract(insert_tail) -> insert_tail"),
}
for n, m in man.items():
    if n in seen:
        continue
    item = m["source_item"]
    if n in OMISSIONS:
        fam, T, F, N, b, ch = OMISSIONS[n]
    elif any(k in item for k in TARGETS + ["insertion_sort", "small_sort"]):
        fam, T, F, N, b, ch = ("real body: " + ",".join(k for k in TARGETS if k in item) or "route", "see source", "see source",
                               "see source", "see source", "real body (plain/stub panic only); no target contract")
    else:
        continue
    rows.append(row_for(n, fam, T, F, N, b, ch, "OPEN", "omission:manifest"))
cols = list(rows[0])
w = csv.DictWriter(open(K1 / "specfix/TRANSFER.tsv", "w"), fieldnames=cols, delimiter="\t", lineterminator="\n")
w.writeheader(); w.writerows(rows)
import collections
print(len(rows), collections.Counter((r["row_origin"], r["consumer_kind"], r["P1_member"]) for r in rows))
print("P1 rows", sum(r["P1_member"] == "yes" for r in rows), "P2 rows", sum(r["P2_member"] == "yes" for r in rows))
