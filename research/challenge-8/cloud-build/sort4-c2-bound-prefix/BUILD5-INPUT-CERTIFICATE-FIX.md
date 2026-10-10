# Build5 C2 input-certificate interface fix

Fresh Build `ae8ac387-fa50-46ca-93b2-c715057f4ad3` stopped before the
C2 translator patch or proof with `complete five-call/eight-selector/four-copy
input certificate absent`. C1 and mandatory unbound C2 discovery had already
passed. The producer in `sort4-native-entry-c1/c2_discovery.py` returns
`c2_fnmut_at_expected_source_line` as `[(223, callee)]` in memory; JSON
serialization changes its tuple row to `[223, callee]`. The new consumer had
compared the in-memory tuple row against a list row.

`driver.py` now checks exactly one tuple **or** list row, then compares its
two values to `[223, "std::ops::FnMut::call_mut"]`. It still requires the
same confirmed scaffold/runtime statuses and exact 5 FnMut, 8 selector and
4 copy counts. All later source/MIR/pre-AST pins and mandatory unbound refusal
remain unchanged. The tool patch and `profile.json` hashes are unchanged.

Permitted saved-data/parser-only replay:

```text
PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/cloud-build/sort4-c2-bound-prefix/test_input_inventory.py --evidence /tmp/c2-ae8ac387-read/allprooflogs/cases/sort4-c1-current-recovery
PASS: live tuple, saved JSON list, status/count/row/source-operand mutants
```

This repair has **no C2 proof credit**; a new exact-SHA Cloud Build is required.
