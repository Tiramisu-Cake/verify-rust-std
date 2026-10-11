# Caller-derived bound session (2026-10-11)

Owner select-sort4; checkpoint 64922e1e5978b7204a6664e33a9f202aa6eea920.
Policy read c7ca8c467aecf10a4b53039372ee97714f854ee3 (origin/main fetched).
Start 16:25:01 UTC; main 18:25:01; finish-only 18:55:01.
Separate phase SORT4-CALLER-DERIVED-BOUND-CLOUD-2026-10-11 and ledger
BUDGET-CALLER-BOUND-2026-10-11.json; new3600 conservative seconds/no carry.
Existing lane and v2 coordinator/max2/one per owner-ledger unchanged.

## First experiment, rationale before execution

Actual obligation: unstable::sort first T::IS_ZST guard establishes nonzero
size on continuation, preserves native v/F/thread/lifetime/type resources,
full generated normal/unwind posts and cleanup. Prefix cuts before v.len;
no public-to-helper transfer claim. Exact same source/body and frozen model.
Hypothesis: existing fully qualified ghost std::mem::size_of::<T>() resolves
where Rust import alias did not. No size/frontend/model repair. Positive
assert >0; false-zero continuation semantic assertion rejection at its exact
line/predicate; reachable ZST-arm assert false intended rejection. Both
negatives require paired MIR/refinement; lookup failures give no credit.
All three execute on post-slice-binding translator21ca026a (same further
consumer profile), not pre-binding66e266d3. Existing canonical pointer gates,
default-off/source/phase refusals and authority/MU negatives remain separate.
Source template pin and classifier tokens change together; runtime ghost-strip
bytes unchanged. Tool/model/profile experimental/unaccepted. Component PASS
allows source-specific caller investigation, never implicit helper nonzero.
Expected failure keeps typed audit Booleans; setup collector errors too.

## Minimal transition map (read-only, not proof credit)

stable/quicksort.rs:23–28: len=v.len; len<=T::small_sort_threshold();
T::small_sort(v,scratch,is_less); return. Same source owners cross call.
smallsort.rs:49–62 selected T:FreezeMarker impl: threshold actual body returns
SMALL_SORT_GENERAL_THRESHOLD; small_sort calls helper with same slices/F.
smallsort.rs:176: constant32. General fallback constant16 (not32).
FreezeMarker: shared/mod.rs marker impl T:Freeze. Generic quicksort signature
unchanged; only explicitly selected Freeze theorem may use this impl.
No whole quicksort/public sort/driftsort/scratch allocation credit.
Bound<=32 does not imply nonzero. Helper must retain len<2, len+16/abort,
v pointer, division, scratch pointer/cast, actual branch and first call order.
Threshold/body compiler identity binding and native transfer remain OPEN.
