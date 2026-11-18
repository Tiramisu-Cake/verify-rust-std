# Literal role plan — NOT_APPLIED

File B = `library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs`
at bd62, SHA256
`e0f47062d71f256fed49b8ad8144c2a83c9a96ecd85646605b1c2fe9b707d0dc`.
Lines below refer to those immutable bytes. `INPUTS.json` binds dependencies.

## Minimal cfg/import/assertion sketch

```rust
// Keep verify.rs's existing opt-in gate and batch's existing import:
#[cfg(all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed))]
pub(super) mod sorting_s2_batch;
// Already present in B: use crate::{kani, ...}; no new import is needed.

// Example only: same operand, execution point and literal; no assume/print/cover.
kani::assert(
    post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&input), &out),
    "S2_NEG_CHECKER_COUNT",
);
```

All six sites use exactly that transformation: `assert!(P, "S2_NEG_...");`
→ `kani::assert(P, "S2_NEG_...");`. No extra cfg around a failing assertion.
Effective inherited cfg includes `kani`, sorting, controls and s2_assumed; future
S3 cfg must bind matching providers and consumers explicitly. No macro alias
that loses the literal, no panicking formatting path, no label on `true`.

| Root / B line | Exact literal | Preserved failing predicate/input path | Future expected inventory |
|---|---|---|---|
| merge_order_corrupt /121 | S2_NEG_MERGE_ORDER | actual merge; assume out[0]<out[31]; exchange endpoints; same full post on src/out | one bound FAILED assertion at intended site; native FAILED |
| merge_count_corrupt /128 | S2_NEG_MERGE_COUNT | actual merge; src=[1;32]; out[31]=2; same full post | same |
| checker_count_corrupt /134 | S2_NEG_CHECKER_COUNT | input=[1;32], out[31]=2; sorted output, changed full counts | same |
| checker_order_corrupt /140 | S2_NEG_CHECKER_ORDER | input=[1,2], output=[2,1]; counts equal, order false | same |
| sort13_weak /149 | S2_NEG_SORT13_WEAK | descending 12..0; ordinary stub of uncontracted s2_swap_seam to no-op; faithful network copy; unchanged post | same |
| general32_weak /163 | S2_NEG_GENERAL32_WEAK | [2;16] followed by [1;16]; ordinary weak copy merge seam; existing verified sort8/insert premises retained; unchanged post | same, dependency-qualified scope still required |

The constructed bad arrays explain why the intended predicates can fail; they
are not actual native traces. Merge controls must still execute the real merge
and reach the mutation; a compilation/snapshot/assertion failure before that
site is not its detection. Weak callers remain source-copy diagnostic identities,
separate from actual positive bodies. general32 weak with assumed dependencies
remains diagnostic even if its tagged failure is observed. Do not add assumptions
that make a bad predicate unreachable or bypass helper/frame failures.

S1-08 role policy supplies the interface discipline: complete same-invocation
inventory, exact description/class/status, source hash/coordinates/selector,
unique producer ID and no duplicates/missing/null/wrong-type records. Adapt its
positive SUCCESS role to an intended FAILED negative; retain negative-oracle
checks and native verdict/exit consistency. Resolve IDs from actual rich/native
inventory; do not infer `.assertion.1`. Until observed, each new ID is UNKNOWN.
An ID, source coordinate or label alone does not establish AST/MIR instance
binding, causality or proof credit. Generic runtime-formatted FAIL remains
unadmitted; do not import the separate stub-confirm exception.

## Supporting positive roles and gates

The same B contains 16 other labelled assertion sites. First S3 should normalize
all 22 sites to literal `kani::assert`, so success/frame/activation roles do not
keep the same formatting defect while six negatives are fixed. Preserve these
exact expressions and labels, including the loop and witness invocation sites:

| B lines | Labels |
|---|---|
|23,24|S2_MERGE_SOURCE_FRAME, S2_MERGE_CANARIES|
|30,32|S2_ACTIVE_MERGE32_REAL, S2_MERGE32_SORTED_FULL_COUNT|
|43,47,48|S2_ACTIVE_SORT13_ASSUMED, S2_SORT13_SORTED_FULL_COUNT, S2_SORT13_CANARIES|
|60,64,65|S2_ACTIVE_GENERAL32_ASSUMED, S2_GENERAL32_SORTED_FULL_COUNT, S2_GENERAL32_CANARIES|
|75,82,83|S2_ACTIVE_SWAP_PFC, S2_SWAP_EXACT_TRANSFER, S2_SWAP_FULL_FRAME|
|98,103,111|S2_SUMMARY_WITNESS_FULL_COUNT, S2_ACTIVE_SUMMARY_WITNESS, S2_PAIR_WITNESS|

These are source sites, not a prediction of compiled property count: loops and
callee sites may yield multiple source instances. For loop/witness/frame roles,
retain complete source-instance-set binding; do not insist on one property by
label alone or discard extra generated checks. Covers remain untouched.

Frozen full inventory stays 11 roots /20 covers /6 negatives; R5 selected was
9/16/5, deferred general32 pair (4 covers,1 negative). Required positive messages
total16 over five roots: swap3, witness3, merge4, sort13 3, general32 3. A new S3
profile adds explicit leaf/control identities and declares its selected inventory;
it does not claim unselected/deferred historical roots executed. Keep a full
obligation inventory alongside its selected profile. No blind all11 rerun.

Future strict delta checks: normalize only the 22 planned assert spellings,
compare entire B lexical token stream to bd62 including all predicates/covers,
assumptions and source copies; verify fixed stub targets and cfg/PFC stacks,
runtime projection, source-copy correspondence, active model and exact hashes.
Current s2_policy.validate_source explicitly searches `assert!` and freezes old
oracle ordinals; a reviewed S3 adapter must recognize literal calls and rebind
oracles, not skip those gates or mutate the frozen legacy fixture. Hashes,
locations, request/workflow and maps all change explicitly. Add synthetic
wrong/missing/duplicate label, wrong ID/source/cfg, unrelated failing check,
unreachable check, placeholder, parser partial and bad model controls; require
rejection. Native intended failures and nonvacuity remain separately necessary.
