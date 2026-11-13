# CC2 controls — all verifier outcomes NOT_RUN

| Source / root | Intended discriminating observation |
| --- | --- |
| positive.rs / scalar_parameters_true_false | Both entry reads before address creation and true/false covers reached; normal returns consumed; no failures |
| positive.rs / reference_copy_move_return | Reference Copy operand before address creation, supported padded wrapper argument/Move/normal return, useful assertions/covers reached; no failures |
| positive.rs / capture_free_ordinary | Zero-upvar ordinary contract body actually runs scalar/ref helpers and returns true; useful body/ensures/outer checks reached SUCCESS |
| positive.rs / capture_free_simple_check | Same isolation in SimpleCheck; no reached Unsupported counts as initialization success |
| payload.rs / initialized_payloads | Paired reference/raw callee reads return42; pointer-slot and byte checks succeed, useful outer assertions/covers reached |
| payload.rs / reference_slot_preserves_hole | Valid &MU slot; body cover immediately before actual u8 payload read reached; bound read Check/CheckRef fails, no slot/ref/bool/protocol/Unsupported failure |
| payload.rs / raw_slot_preserves_hole | Valid raw pointer slot; callee cover/read reached; only bound u8 payload read failure(s), never initialization of pointed-to storage |
| payload.rs / entry_does_not_hide_caller_read | Actual bad u8 read in caller fails before consume_byte entry can seed its parameter; no invalid typed bool/reference constructed first |
| padding.rs / ordinary_parameter_does_not_bless_padding | Valid repr(C) typed value, initialized fields, padding byte1; callee reaches raw padding read and rejects it; data-only entry mask preserves false |
| positive.rs and payload.rs / mixed all roots | Complete per-root inventories match exact singleton results, including successful assertions and reached covers; establish actual starting_items grouping/order |
| Original replace.rs / replace_ordinary, replace_simple_check | Unchanged input, retain all outcomes; entry fix may remove bool failures but nonzero closure copy/entry layout still CC3. Any remaining bool failure needs bound producer analysis |
| Original recursive.rs / recursive_check, recursive_ordinary, recursive_simple_check | Separate complete executions; preserve CC1 targeted cycle Unsupported without crash. Ordinary recursive Unsupported remains release BLOCKED; no general mode qualification |
| Existing closure-zst/scalar-pfc-legal.rs / postcondition_reads_initialized_return | Existing P1 exact oracle, no extra failures |

Expected-suite substrings are preliminary regression expectations. They do not
accept a negative by matching any failure: CI must retain the complete inventory
and bind the required payload checks, with no unrelated failures. Exact new
property IDs and multiplicities are UNKNOWN until selected model binding, not
inferred from descriptions. Positive checks/covers must actually be reached;
negative outer consumers may be unreachable. A reached Unsupported, invalid
value, collection crash, missing export, timeout or signal is not negative PASS.

All8 strong JSON oracle inputs/expectations, P1/PFC/lawful-modifies, P2 read pair,
frame-negative user *outside, C03 and S3 left/right holes are byte-identical.
Their common-head gate remains required after the stages, with one Quick and
then separate M3/full/platform/SmallSort gates. Fixed oracles must not be relaxed
if instrumentation changes actual identities. Replace's prior complete5-failure
observation is unchanged; the two u8 havoc-domain checks are not declared false.
Actual two-order mixed-root coverage remains UNKNOWN if CI exposes only one
ordering. Source declaration order is not evidence of starting_items order.
