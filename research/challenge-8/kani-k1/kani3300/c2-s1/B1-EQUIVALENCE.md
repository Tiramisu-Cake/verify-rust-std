# C2-S1 — B1 behavioral and fixture correspondence

Static correspondence only; no executed equivalence proof. Current B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012` is a dependency atop U, reported by coordinator as draft kani#5172, **not merged**. Public head was not changed or independently refreshed.

Old Part1 production integration `cdb439b0a4c36e9e595019895ab803230f332941`, initial fixtures `dc5f5a406749a73f1c3192e0b5338441e79508bb`, accepted B1I-A fixture correction `6134e42dd1c65dc980336e7d9455aba02d423edf` were compared against current B1 and the accepted C1b final tree.

| Behavior | Old B1I / B1I-A and current B1 | Port choice |
| --- | --- | --- |
| FnDef resolution | Fallible resolver, no `expect_resolve`; Item/Intrinsic/foreign models and actual shim-body availability | Retain common resolver; use checked_body for source availability, with `tcx` passed by both callers |
| Pointer/virtual/LlvmIntrinsic/bodyless calls | Local Unsupported independent of delayed seeds | Retain C1b accepted classifications; no new admission or blanket Unsupported |
| Pending operand effects | Visit call operands before resolution; rejected call exits to shared publication epilogue | Retain `super_terminator` → Unsupported → `break 'call` → common target push; entry loads and earlier checks stay accumulated |
| Delayed targets and alias edges | Failed resolution is not an intrinsic seed; guarded no-body return preserves earlier graph | Retain both behaviors; selected overrides take priority over checked source fallback |
| Shadow transfer boundary | Standalone B1 has a broad recursive shim guard for legacy union slots; B1I adapts to A3 pairing | Retain accepted C1b `has_transfer_protocol`/`transfers_shadow`, unsized boundary and exact paired operations. Do not resurrect standalone legacy recursive guard over nested aggregates |
| Cycle analysis | Later accepted CC behavior uses per-root Result | Retain fresh ActiveCalls per root, provenance key, latched Err; no failed child/root partial graph joins |

This is correspondence within the accepted Part1 model, not byte-identical production trees: current B1 uses legacy memory-operation shapes; C1b already has storage and paired protocol fields. A blind cherry-pick would duplicate/revert these integrations.

## Fixture inventory

FIXTURE-INVENTORY.json records B1/C1b/candidate blobs for all 56 paths (28 Rust inputs and 28 expected files). The candidate is exactly the union of both input path sets:

- 20 shared Rust fixtures: direct, entry initialized/partial, erased/fn-pointer/fn-trait-pointer/global-escaped/pending-ops/virtual/wrapped-pointer, each plain/seeded.
- 6 C1b-only inputs: Item-return initialized/uninit and tuple-MaybeUninit, each plain/seeded; preserve B1I-A corrected actual call classifications, not obsolete `shim-*` names.
- 2 B1-only inputs: generated-positive plain/seeded, covering function-item Fn calls and closure Drop glue. Preserve input and expected files verbatim from B1; actual instance/layout/reachability remains a CI question.

Keep C1b runtime-symbolic `kani::any()` in four entry initialized/partial inputs (no ordinary-union constant regression); keep B1 `-C panic=abort` in these four and both pending-ops inputs to support runtime/optimized custom MIR. Erased-pointer differences are C1b explanatory comments only. Other shared inputs and all shared expected outputs remain unchanged from their selected accepted source. No expected output was authored from an unexecuted run.

FnDef resolution-error/bodyless/generated-instance compiler-input gaps are not closed by source inventory or generated-positive presence. Request execution/MIR binding separately; all tests NOT_RUN.
