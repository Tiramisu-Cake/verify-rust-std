#!/usr/bin/env python3
"""Write poneclean/DEACTIVATED.tsv: every cfg-on proof of the baseline tree that is not cfg-on now.

Usage: python3 -I make_deactivated.py > DEACTIVATED.tsv. Static source forecast (source_sets.py);
legacy evidence refs are recorded per row and are two different refs, never one identity.
"""
import csv, hashlib, importlib.util, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K1 = HERE.parent
spec = importlib.util.spec_from_file_location("ss", HERE / "source_sets.py")
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

BASE = "6f3a2629615cc7184b840d3c21aaea54b129267e"
INTEG2 = "a847dcf80b81c2f09b35a6c90787da13b0cdf4bd"
PART2 = "028040f941ca36b0a68b2e5fcade2c0b59fbcca1"  # origin/submission/ch8-smallsort-part2
P2_FILE = "research/challenge-8/kani-k1/integ2/scope/p2-ordinary.txt"


def git(*a):
    return subprocess.run(["git", "-C", str(ss.REPO), *a], check=True, capture_output=True,
                          text=True).stdout


tree = lambda rev: git("rev-parse", f"{rev}^{{tree}}").strip()
p2_text = git("show", f"{INTEG2}:{P2_FILE}")
P2 = set(p2_text.split())
P2_SHA = hashlib.sha256(p2_text.encode()).hexdigest()
base, cur, part2 = ss.sets(BASE), ss.sets(None), ss.sets(PART2)
brec = {r["name"]: r for r in base["records"]}
transfer = {r["harness"]: r for r in csv.DictReader(open(K1 / "specfix/TRANSFER.tsv"), delimiter="\t")}
RAW = re.compile(r"(?:^|::)(swap_if_less|sort4_stable|insert_tail|bidirectional_merge)$")
SUPERSEDED = {
    "swap_profile_four_positions_u8": "network::swap_contract_four_positions_u8",
    "swap_profile_cell_i32_n2": "network::swap_contract_cell_i32_n2",
    "swap_profile_drop_u8_n2": "network::swap_contract_drop_u8_n2",
    "sort4_profile_u64_n4": "merge::sort4_contract_u64_n4",
    "sort4_profile_bytes16_n4": "merge::sort4_contract_bytes16_n4",
    "insert_tail_profile_u8_prefix": "correct::contract_insert_tail_u8_prefix",
    "insert_tail_profile_u64_start1_tail2_to8": "network::insert_tail_contract_u64_start1_tail2_to8",
    "merge_profile_u8_n8": "merge::merge_contract_u8_n8",
}
PREDICATE = {"uninit_tail_predicate_admission": "valid_sorted_tail",
             "uninit_sort4_predicate_admission": "valid_sort4_regions",
             "readonly_source_predicates": "valid_sort4_regions"}

gone = sorted(set(base["cfg_on"]) - set(cur["cfg_on"]))
retired_now = set(cur["retired"])
w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["name", "action", "legacy_kind", "legacy_target", "baseline_cfg", "baseline_location",
            "p2_343_integ2", "integ2_ref", "integ2_tree", "integ2_p2_manifest_sha256",
            "part2_branch_status", "part2_ref", "part2_tree", "reason", "previous_status"])
it, pt = tree(INTEG2), tree(PART2)
for name in gone:
    r = brec[name]
    short = name.split("verify::", 1)[1]
    fn = short.rsplit("::", 1)[1]
    target = r["pfc"] or ";".join(r["stub_verified"]) or ""
    if r["pfc"]:
        kind = "proof_for_contract"
    elif r["stub_verified"]:
        kind = "stub_verified"
    else:
        kind = "proof"
    raw = bool((r["pfc"] and RAW.search(r["pfc"])) or any(RAW.search(x) for x in r["stub_verified"]))
    if fn in SUPERSEDED:
        action = "removed"
        reason = f"StageA opt-in profile PFC superseded by the migrated ordinary name {SUPERSEDED[fn]}"
        status = "A2 SUCCESS on library tree 31997f7781 (specfix-a2-20261031)"
    elif kind == "proof_for_contract" and raw:
        action = "cfg(any())"
        reason = "proof_for_contract of a raw helper whose generic contract was removed"
    elif kind == "stub_verified" and raw:
        action = "cfg(any())"
        reason = "stub_verified of a raw helper whose generic contract was removed"
    elif fn in PREDICATE:
        action = "cfg(any())"
        reason = f"diagnoses the removed contract predicate {PREDICATE[fn]}"
    else:
        raise SystemExit(f"unclassified deactivation: {name}")
    if fn not in SUPERSEDED:
        t = transfer.get(fn)
        if t:
            status = f"{t['manifest_class']} ({t['consumer_kind']}, P2_member={t['P2_member']})"
        elif short.startswith("merge::specdiag::"):
            status = "SPECDIAG diagnostic (opt-in, specdiag module)"
        else:
            status = "opt-in (not in TRANSFER.tsv)"
    assert (action == "cfg(any())") == (name in retired_now), name
    p2s = "ordinary" if name in part2["ordinary"] else ("controls" if name in part2["cfg_on"] else "absent")
    w.writerow([short, action, kind, target, r["cls"], f"{r['file']}:{r['line']}",
                "yes" if name in P2 else "no", INTEG2, it, P2_SHA, p2s, PART2, pt, reason, status])
