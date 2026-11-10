# Build 1 diagnosis and coordinator scope decision

Build `9d94cb84-55e1-4cae-a55b-9597ddd81d87`, source `55a7fd1c8ada1590ab571b040a6256219ef75e63`:
Cloud FAILURE; K-1 COMPILE_ERROR; every requested verification row NOT_RUN.
The controls-on compiler reports exactly two E0308 mismatched types at trait_contracts.rs:245:73
(K4) and :261:73 (W1). Expected `&fn(&u64, &u64) -> bool`, found the reference to the
`trait_less_u64` function-item type. Full diagnostics are in evidence/compile-context.txt.
The trait-argument placeholder `_` selects the specialized fn-pointer type rather than fixing F
from the function-item reference. This is a frontend/type-resolution error, not a counterexample,
TIMEOUT/OOM, unsupported result, or ordinary FAILED. There are no failed proof checks to classify.

Concrete proposed repair: `PROPOSED-TYPE-RESOLUTION-REPAIR.patch` (NOT APPLIED).
Only K4/W1's enabled lookup is routed through this opt-in generic helper:

```rust
#[cfg(kani_smallsort_controls)]
fn function_item_model_enabled<F>(cmp: &F, len: usize) -> bool {
    <() as SortModel<u64, F>>::enabled(SortEntry::Freeze, cmp, len)
}
```

Both call sites become `let enabled = function_item_model_enabled(&cmp, v.len());`.
Generic argument inference fixes F from &cmp before the explicit SortModel<u64,F> lookup.
The function-item comparator itself remains unchanged at both real/stub calls. Model, ensures,
whitelist, all ordinary roots, names, inputs, layouts, frames, assertions and expected results,
runtime code and tooling remain unchanged. `git apply --check` on the proposal succeeds;
compiler/proof validation is NOT_RUN (no local Rust/Kani execution).

TASK-TRAITPFC-G3.md:96 permits Build 2 repair only for syntax/attribute qualification or old-capture.
This generic helper for type resolution is not explicitly listed. Coordinator decision is needed
before applying it. The kickoff requires asking and stopping on an uncovered decision.
No new Build 2 packet has been declared dispatch-ready and no Build 2 dispatch is authorized.

If admitted: use the sole remaining Build 2 for this repair, with exactly the same 14 rows and
inventory=true; request id traitpfc-g3-20261110-02; 100m / $1.3500 maximum. There is no subsequent
narrowing build, retry, third build, tooling change, domain expansion or additional cap.
After applying: separate library/research [skip ci] commits, refresh source/static/rustfmt/patch
and apply-check identities, exact PRE-BUILD REVIEW SHA, then stop for a new exact-packet GO.
If rejected: record G3 as incomplete/compile-blocked; do not silently coerce the comparator to a
fn pointer or omit the disabled-model assertion, as either would change the intended calibration.

Build1 cost $0.6615 (49 billed minutes); own cap $3.50; residual $2.8385.
Spent + proposed Build2 maximum = $2.0115, own residual after maximum $1.4885.
Observed project used $110.9400 + unfinished reserve $0.6750 + Build2 $1.3500 = $112.9650,
below cap $118.96, residual $5.9950; refresh again before any dispatch.
T0 remains 2026-11-10T19:51:57Z; main deadline 2026-11-11T01:51:57Z,
closeout deadline 2026-11-11T02:21:57Z. No reset or extension.
