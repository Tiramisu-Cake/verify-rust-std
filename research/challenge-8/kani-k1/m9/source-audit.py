#!/usr/bin/env python3
"""M9 source-only scope/cfg audit; does not replace compilation or measurements."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "scope"))
import source_items as items
import source_inventory as inventory

BASE = "97fdf0a21e517fc99ab0a5180bfb7ee3128685c9"
ASSEMBLY = "d4e5a0907b4d3e73b251afbc32b1bcdca58c8b18"
PATH = "library/core/src/slice/sort/shared/smallsort/verify/merge.rs"


def source(rev):
    return subprocess.check_output(["git", "show", f"{rev}:{PATH}"], cwd=ROOT, text=True)


old = source(BASE)
new = (ROOT / PATH).read_text()
old_items = items.items(old)
new_items = items.items(new)
guard_old = "const { assert!(N == 6 || N == 7 || N == 8) };"
guard_new = "const { assert!(N >= 6 && N <= 9) };"
helpers = {"general_direct_u64_properties", "stable_direct_u64_properties"}
variants = {"stable_direct_nonconst_u64_properties", "stable_direct_const_u64_properties"}
calls = {
    "general_direct_u64_n9": ("general_direct_u64_properties", 9),
    "stable_direct_u64_n9": ("stable_direct_u64_properties", 9),
    "stable_direct_nonconst_u64_n9": ("stable_direct_nonconst_u64_properties", 9),
    "stable_direct_const_u64_n9": ("stable_direct_const_u64_properties", 9),
    "stable_direct_const_u64_n8": ("stable_direct_const_u64_properties", 8),
}
old_keys = {items.key(i) for i in old_items}
added = [i for i in new_items if items.key(i) not in old_keys]
assert len(added) == 7
assert all(i["gated"] for i in added)
retained = [i for i in new_items if items.key(i) in old_keys]
assert [items.key(i) for i in retained] == [items.key(i) for i in old_items]
for before, after in zip(old_items, retained):
    a = old[before["start"]:before["end"]]
    b = new[after["start"]:after["end"]]
    if before["name"] in helpers:
        assert a.count(guard_old) == 1
        a = a.replace(guard_old, guard_new)
    assert a == b, before["name"]


def body(text, name):
    i = next(i for i in items.items(text) if i["kind"] == "fn" and i["name"] == name)
    return text[i["content"]:i["end"]]


aggregate = body(new, "stable_direct_u64_properties")
allocation = (
    "let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();\n"
    "    let scratch = scratch_view(&mut holder);"
)
assert allocation in aggregate
for name in variants:
    form = ("const { MaybeUninit::<u64>::uninit() }" if "_const_" in name
            else "MaybeUninit::<u64>::uninit()")
    expected = aggregate.replace("stable_direct_u64_properties", name).replace(
        allocation, f"let mut scratch = [{form}; SMALL_SORT_GENERAL_SCRATCH_LEN];"
    ).replace("small_sort(&mut v, scratch,", "small_sort(&mut v, &mut scratch,")
    assert body(new, name) == expected, name

records_old = inventory.records("merge", text=old)
records_new = inventory.records("merge", text=new)
for controls in (False, True):
    a = {r["name"] for r in records_old if controls or not r["opt_in"]}
    b = {r["name"] for r in records_new if controls or not r["opt_in"]}
    expected = {inventory.PREFIX + "merge::" + n for n in calls} if controls else set()
    assert b - a == expected and not a - b
for name, (helper, n) in calls.items():
    record = next(r for r in records_new if r["name"].endswith("::" + name))
    assert record["opt_in"] and record["args"] == [name, helper, str(n)]
macro = next(i for i in new_items if i["name"] == "define_direct_u64_route_harness")
macro_text = new[macro["content"]:macro["end"]]
assert "#[kani::proof]" in macro_text and "#[kani::unwind(34)]" in macro_text
assert "$body::<$n>();" in macro_text and "stub" not in macro_text

assembly = source(ASSEMBLY)
unchanged = ["scratch_view", "assert_sorted_and_probe_preserved", "lt_u64", "set_value_probe"]
for name in unchanged:
    assert body(new, name) == body(assembly, name), name
changed = subprocess.check_output(
    ["git", "diff", "--name-only", BASE, "--", "library"], cwd=ROOT, text=True
).splitlines()
assert changed == [PATH]
assert max(map(len, new.splitlines())) <= 100
report = {
    "status": "PASS", "baseline": BASE, "assembly_library_sha": ASSEMBLY,
    "source_sha256": hashlib.sha256(new.encode()).hexdigest(),
    "existing_items": "exact except two guards extended to 6..=9",
    "new_private_opt_in_helpers": sorted(variants), "new_opt_in_harnesses": calls,
    "stable_variants": "exact aggregate body except name, scratch allocation and borrow",
    "unchanged_from_assembly": unchanged, "unwind": 34, "stubs": False,
    "cfg_forecast": {"ordinary_delta": 0, "controls_delta": 5},
    "rust_max_columns": max(map(len, new.splitlines())),
    "limitation": "source audit, not compiler inventory or measurement controls",
}
print(json.dumps(report, indent=2, sort_keys=True))
