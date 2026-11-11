# KANI3300 T1a — PRE-BUILD packet

PREPARED; A Cloud NOT_RUN, proof credit NONE. Runtime Codex; one diagnostic stage.
Task: `research/challenge-8/kani-k1/TASK-KANI3300-T1A.md` (read in full).
Planner: exact copy `PLANNER-T0-REVIEW-ANSWER.md` (read in full); T1a only, no T1b implementation.
Worktree `/root/verify-rust-std-kani3300-t0`, branch `experiment/kani-k1-kani3300t0-20261111`.
Task base `2cc5c79ea5d2aeb5b131e11a0fb895b3086d7aac`; slug `kani3300`, stage `kani3300-t1a`, owner `k1-merge`.
Only this directory and active lane-root `research/challenge-8/kani-k1/RUN-REQUEST.json` change.
No phase activation, live-ledger modification, reservation, dispatch or watcher during preparation.
Independent review is recorded separately; exact final published SHA requires coordinator GO.

## Same-library baseline B

Reuse CMP4-B build `d137507f-c7de-432a-85dc-62fa03d1adaf`, dispatch head
`c8967c5a44e8f95b19f31761e55313d8488faea5`, as a **source-reported bounded diagnostic** baseline.
Library tree A/B/planner-reference `2121ff2d08d50d412c834760af925b202a1d8c01`:
`919cc3e2dc5fb19ea6e7f7be761914b949160a41`. No library edits in T1a.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`.
Immutable production CMP2 patch `research/challenge-8/kani-k1/kani3300/u4/kani-uninit.patch`:
SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, 100977 bytes.
B reported applied tree and A expected tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`.
Protected lane/recipe/pin paths at A and B equal KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
Both: diagnostic, uninit/controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`,
RUSTFLAGS `--cfg kani_smallsort_controls`. Valid-value request field remains absent (B reports off).
`check_t1a.py`, `static-check.json` and `BASELINE-COMPARISON.json` bind exact inputs and preserved receipt hashes.

B: Cloud SUCCESS, summary COMPLETE, gate PASS, Kani exit1. Three positives SUCCESS:
literal IndexRange 0/20 cover1/1, runtime IndexRange 0/26 cover1/1, ManuallyDrop 0/84 cover2/2.
U1 expected FAILED 1/30 cover3/3: ``Undefined Behavior: Reading from an uninitialized pointer of type `u8` ``
at `/workspace/src/library/core/src/mem/mod.rs:1283`. Native report unavailable; Brief HTTP404.
Actual argv/MIR remain UNKNOWN. Preserved bounded receipts are hash-checked, not independent proof credit.
Recipe comparability is established from published requests and unchanged tooling, not observed native argv.
B has no step2/3 or U2 root: direct A/B comparison is available for step1 and shared step4/U1;
A steps2/3 and U2 must be reported on their own. No automatic B repetition; a real input mismatch means stop
with `Координатор, вопрос`, not a separate Build.

## Request A and observations required after GO

`kani3300-t1a-uninit-20261111-01`; `RUN-REQUEST.json` snapshot equals the active lane-root request.
SHA256 is recorded in `static-check.json` and `CHECKPOINT.json`.
Every request field except request_id/purpose equals original CMP3. Generated `kani.args` equals CMP3 bytes.
No diagnostic patch delta, `--emit`, `--trace`, `--no-slice-formula`, new env or tooling changes.
All existing library roots remain present; only the original CMP3 nine roots are selected.
Selected order is request order only; it does not establish actual codegen order.
Prefix `slice::sort::shared::smallsort::verify::uninit_probe::`:

| Step | Root suffix | Expectation / observation |
|---|---|---|
| 1 | cmp3_index_range_len | SUCCESS requested; check original usize uninit at ops/index_range.rs:57 |
| 2 | cmp3_polymorphic_sized_len | SUCCESS requested; report separately from step1 |
| 3 | cmp3_polymorphic_unsized_len | SUCCESS requested; report separately from step1 |
| 4 | cmp3_manually_drop_unsized_len | SUCCESS requested; compare shared B root |
| 5 | cmp3_into_iter_len | SUCCESS requested; retain all len/Drop failures |
| 6 | cmp3_into_iter_next | SUCCESS requested; retain all next/Drop failures |
| 7 / U8 | small_sort_general_with_scratch_u8_n4 | SUCCESS requested; integration probe |
| 8 / U1 | pincheck_calibration_uninit_read_u8 | FAILED, `Reading from an uninitialized`; preserve exact checks/location |
| 9 / U2 | pincheck_calibration_init_read_u8 | SUCCESS; positive calibration |

For every root: status, failed/total, covers, verbatim Failed Checks with location and omissions.
Verify A head/request/pin/patch/applied-tree/tooling/control identities before classification.
Use `smallsort-brief BUILD` first, then authorized bounded `k1g.sh summary/native/native-field` and rows
(`k1g.sh summary BUILD 0 9`); status/budget/tooling checks retain existing gates. No raw logs/archives/credentials.
Missing Brief/native or incomplete bindings stay explicit UNKNOWN; no raw fallback.

## Budget, classification and stop

One attempt, no repair/retry. Envelope `(9*3+30)=57min`; reserve `57*$0.0135=$0.7695` <=cap `$0.80`.
Spend `$0`, submitted reserve `$0`, attempts0/1. No new B; historic B cost is not a T1a charge.
Coordinator/client checks live slots, project budget, deadline and exact remote SHA before GO/dispatch.
Runner unchanged; no new service tests required. Static validator/identity checks and diff whitespace checked.
No local cargo/rustc/Kani/CBMC, Actions/PR/issue, other-worktree writes or model/trusted changes.

A FAIL on steps1–3 with matching original located uninit and comparable B SUCCESS: same-library contrast,
not mechanism or deterministic dependence only on root set. Only step1 is directly shared with B.
A SUCCESS: non-reproduction, no constant-seed fix; old CMP3 blocker remains unresolved.
Partial reproduction, broken controls/identities, Unsupported and timeout are distinct outcomes.
Post-build `RESULT-KANI3300-T1A.md` <=30 lines: A/B identities, B check, per-root table, class, expense,
limitations and proposed next step. T1b is a proposal only; it requires a separately reviewed/authorized task.
After exact coordinator GO only: one `k1g.sh dispatch experiment/kani-k1-kani3300t0-20261111`,
then `k1g.sh watch BUILD` and end turn. Task explicitly uses this lane watcher; generic watcher not armed
(thread cwd `/root` differs from worktree). After results close the single stage; no next-stage execution.
Publish reviewed packet; final response ends `PRE-BUILD REVIEW <full published SHA>`, then stop until GO.
