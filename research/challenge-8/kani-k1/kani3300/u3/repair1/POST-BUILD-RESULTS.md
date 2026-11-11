# U3 repair 1 — actual bounded results and limits

Build `45287677-98cb-4dc4-b98d-7ccae4782f5f`, head `6308e4b9fb3dcc81584d3227a7c1701db855a643`.
Request SHA256 `2def1eb2642fe4f707dd659208c0af7ff55b2a3feba5f3ed7cc9fb99b7dcca7e`.
Patch SHA256 `f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c`.
Applied tree `c5b24f0b0da999d1deb9758215790382fe5e3be4`; Kani0.68.0/CBMC6.11.0, Kani build265s, compiletest17s.
check-tooling against `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` PASS for pool/lane/bound tooling/request/patch/tree.
Summary SHA256 `373f5d6bc76ad07131d07f1f7339bc2aaca5065640f7a28a29b0fc2e4a0223a8`.
Source: bounded k1g.sh summary, native0/1, native-field output_excerpt and diagnostic pages only. No raw fallback.
Native17 PASS/3 ERROR; Cloud FAILURE, summary TOOL_ERROR/gatefalse. This is not full U3 acceptance.

## Empty harness and passed controls

wrap-u3-positive native PASS, exit0, errors[], argv --require-success. Its exact source has7 proof harnesses and golden7 successes.
That validates empty_harness as SUCCESS together with scalar/usize-array/empty-array/ZST/padded Move/Copy controls.
Binding is explicit in EMPTY-HARNESS-OBSERVATION.json; no literal empty_harness result line was retained by the producer.
review-positive also native PASS under require-success and its7-success golden, including both written-slot overlap controls.
All five amended U1T negatives are native PASS and their own diagnostic field actually begins Failed Checks: uninit with expected T.
Plain negative, clause plain/PFC negatives, padding/source-read and partial-copy/reset/MU→T/no-MIR controls passed expected goldens.
These establish finite native test outcomes, not general std theorem/B2 credit.

## Actual retained Failed Checks

For frame-negative offset9, kani_stdout lines177–180 and850–851:
Check19: frame_target::{closure#2}::{closure#0}.assigns.1 — Status FAILURE.
Failed Checks: Check that *var_7 is assignable
File tests/expected/uninit/maybe-uninit-buffer-u3-frame-negative/main.rs, line22, in frame_target::{closure#2}::{closure#0}.
Line22 is the user `*outside = ...` write under modifies(out). Thus the user frame violation is detected.
The golden asks for *outside instead of MIR's *var_7; its native ERROR is a naming mismatch, not evidence of a weakened frame.
KT2 failed_check_line_count12 counts duplicated compiletest/kani contexts; omitted_failed0, all failed context unclipped.
For the five passing U1T selectors, own diagnostic pages return these first matching actual lines:
- argument-return: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16`
- overwrite-copy: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]`
- overlap-copy: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8`
- repeat-local: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64`
- reset-zst: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64`
Overlap's two failed harnesses are required by its passing golden; separate complete Failed Checks lists for each are not retained.
No extra unreachable/foreign FAILURE is established from these first matching lines; absence of extra failures is UNKNOWN.

## Remaining PFC failures

Offset6 pfc-negative kani_stdout24 says: CBMC appears to have run out of memory. You may want to rerun your proof in an
 environment with additional memory or use stubbing to reduce the size of the code the verifier reasons about.
It names contracted_uninit_read_harness failed, Complete0success/1failure/1total. KT2 recognized failed-check count0, omitted0.
This is Kani-reported OOM, not independently measured memory exhaustion and not the required uninit property failure.
Offset4 buffer-positive names contracted_roundtrip_harness failed, Complete3success/1failure/4total. Recognized failed-check
count0, omitted0; the excerpt does not retain a concrete failure reason. Do not infer OOM there merely from offset6.
No new repair, memory-model/contract weakening, timeout reduction or Cloud retry was performed.

## Reporting limitation for every native PASS

run_native attaches output_sources/output_excerpt only if native_status==FAILED or request.expect==fail
(kani_k1.py472–480). For each of the17 native PASS records, native-field output_excerpt returns unknown native field.
Only one matching own diagnostic string is retained. This prevents listing ALL actual Failed Checks for those selectors,
including both overlap harnesses; no reader pagination can recover a field the producer did not save.
SELECTOR-OBSERVATIONS.json lists the actual available line(s), missing-list coverage and source per selector.
Description-only diagnostic fields are not relabelled as Failed Checks. Positive SUCCESS is based on require-success/golden,
not on a missing excerpt. Complete negative failing-property lists would need a separately authorized reporting change/data.
All field-string continuations used returned next_start, identical build/head/request/summary identities; bounded pages are saved.

## IntoIter and next bounded scope

IntoIter selector is native PASS under its expected Unsupported golden. The retained diagnostic names
std::array::iter::iter_inner::PolymorphicIter<[std::mem::MaybeUninit<usize>;2]> containing MU as a field.
The compound-storage Unsupported family is confirmed by the golden, but full failing-wrapper order/list is unavailable.
U8/U9 and select remain open; compound InnerSized/PolymorphicIter/ManuallyDrop support needs a later stage.
Next U3 work: preserve this evidence; separate the frame golden naming fix from PFC resource/error isolation;
retain all5 U1T negatives, empty harness and user frame controls. New builds require a new explicit task/GO: the one repair is used.
Build1 actual$0.1080 + repair$0.1755 = U3$0.2835, reserve$0, cap$0.90. Historical evidence/ledger/download_verified unchanged.
No native PASS of full U3, upstream acceptance or independent proof credit asserted.
