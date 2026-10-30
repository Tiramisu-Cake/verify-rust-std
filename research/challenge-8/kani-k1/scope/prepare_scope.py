#!/usr/bin/env python3
"""Shared scope helpers; the entry point generates INTEG, never edits library source."""
import csv
from pathlib import Path

from source_inventory import BASELINE, HERE

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
    module, macro, name = r["module"], r["macro"], r["name"].split("::")[-1]
    if module == "types":
        prop = "logical trait behavior and full-value permutation"
    elif module == "smoke":
        prop = "efficient-swap finite type predicate"
    elif "control" in name or "reject_" in name:
        prop = "negative control"
    elif macro and "contract" in macro:
        prop = "contract, frame, or precondition property"
    elif macro and ("safety" in macro or "dispatch" in macro):
        prop = "bounded safety and normal-return covers"
    else:
        prop = "proof harness property"
    domain = f"{compact(r['entry'])}; model definitions at {BASELINE}:{r['path']}"
    return prop, domain


def main():
    from prepare_integ import main as integ_main
    integ_main()


if __name__ == "__main__":
    main()
