# NETNINE PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No build has been dispatched.
Review SHA is the published research/request commit carrying this packet.
Task: TASK-NETNINE.md, including all mandatory clarifications; one stage, one build, cap $0.75.
Branch: experiment/kani-k1-netnine-20261102.
Base: ed6e746bf8ec64043e7179be0a6eb631f106601b (task commit over e382287728).
Library commit: 24d9f1d3d8f1ff03f2c3dbe891d1e8f6f30a4d13.
Library tree: ac095c9d7bc9d6909f15015bea6ba692ee032f00.

## Full patch and claims

Full library diff: library.diff (52 insertions, 2 deletions, network.rs only).
Existing ordinary code is byte-identical after removing the two opt-in items and restoring
the two-line comment correction: structural argument plus separate leaf/suffix proofs,
without a full machine-checked N9 composition. Runtime bodies/signatures are unchanged.

Positive: network::netnine_full_value_count_u8_n9, unwind25, full any [u8;9], pre=v,
independent any u8 probe, sortedness and full-value count equality. No stubs or input assumptions.
F is the function-item type of strict_less::<u8>, inferred by let mut cmp (not a fn pointer).
Real UnstableSmallSortTypeImpl -> Freeze/Copy specialization -> small_sort_network:
u8 size1 <=8, scratch fits; N9 -> sort9_optimal -> insertion_sort_shift_left(start9), no merge.
Positive covers: sort moves, probe hits input, probe misses input, duplicates present.
Duplicates cover uses adjacent equality in the sorted output; full-value permutation is asserted.

Negative: network::netnine_full_value_count_u8_n9_negative, same real route and F, unwind25.
Fixed input=[0;9], probe=0; after return v[8]=1; sortedness remains true, count(0) goes9 ->8.
Before count: covers for normal return and corrupted count-check reachability.
Expected FAILED only at literal kani::assert "netnine negative: full-value count preserved",
network.rs:1005 (condition1006, literal1007). Sortedness assertion is network.rs:1003.
No impossible positive covers are copied into the narrow negative witness.

## Static validation

static_check.py / static-check.json: PASS. Exact ordinary200 unchanged; cfg-on382 +2 =384.
Preservation check compares all existing network bytes except the declared comment correction;
only this library file changed. Both additions carry kani_smallsort_controls; no stubs/assumes.
This is source-level validation, not native inventory or proof acceptance.
pfc_order.py: ordinary pfc sites16, bad0 (pfc-order.txt).
TASK-SPECFIX rustfmt wrapper --check: PASS (rustfmt-check.txt); diff whitespace check: PASS.
No local cargo/rustc/Kani/CBMC run, no Actions/CircleCI/macOS build, no competing PR code read.
Tooling/workflows/pin/checker flags/cap unchanged; protected-path comparison in tooling-static.txt.

## Exact G1 request and envelope

RUN-REQUEST.json equals g1.request.json; request_id netnine-g1-full-value-count-20261102.
SHA-256: 8cfb89050296377ebb752357659fd6f4eeac31b82e2a663b65a68e6235ddcafd.
kind measurement; controls:true; kani_jobs:1; uninit_checks:false; timeout10min per row.
Runner gcb-e2-standard-4 / k1-standard4, 4CPU/16GiB. Validator accepted both full harness paths.
Row1 expect SUCCESS; row2 expect FAILED with exact literal count expect_check above.
Generated selection/timeout flags: g1.args; runner: g1.runner. No third diagnostic row.
Kani pin9461e07af7ec929f050aa4192f29363c9be07779; nightly-2026-10-12; lane flags unchanged.
Envelope: 2*10+30=50min; reserve50*$0.0135=$0.675 <=$0.75.
Own UUIDs: none; spent/reserved $0/$0. Global snapshot: budget-prebuild.txt; cap $88.96 unchanged.
Refresh budget immediately before dispatch after GO. GO does not expand budget or scope.

## Continuation after GO

Dispatch this reviewed SHA once; record UUID/request/head/library identities and own reservation.
Use tools/k1g.sh watch UUID with CODEX_THREAD_ID and end the turn.
On wake: bounded status/summary/peaks, necessary log-grep/log-lines, tooling identity check.
Verify negative failure class/file:line/reason and no unrelated failed checks; record all covers.
If positive TIMEOUT, retain TIMEOUT, cap600s, available wall/RSS and VT UNKNOWN/None when absent.
No splitting/retry/third row without a separate explicit task change and GO.
RESULT-NETNINE.md <=35 lines: rows/status/VT/RSS/covers/failed checks, own costs, N9 conclusion;
N13/N18 remain estimates, not proven by N9. Measurement gate success is a separate field.
Evidence Brief / Select-Merge do not apply to K-1. Stop after final NETNINE ЗАВЕРШЁН.
