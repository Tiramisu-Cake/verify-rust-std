# KANI3300 CMP3 — PRE-BUILD packet

PREPARED, Cloud NOT_RUN, proof credit NONE. Runtime Codex; one diagnostic stage.
Task: `research/challenge-8/kani-k1/TASK-KANI3300-CMP3.md`; normative planner copy: `PLANNER-CMP3-ANSWER.md`.
Worktree `/root/verify-rust-std-kani3300-cmp3`; branch `experiment/kani-k1-kani3300cmp3-20261111`.
Slug `kani3300`, stage `kani3300-cmp3`, owner `k1-merge`; task base `b557178a8bf10cb5e984d73f1c6efaadd2ccdb87`.
Library commit `a5a66cc6e1f6b2d77c1ba46150b0d296a2f55df0` is separate from research.
No phase activation, reservation, dispatch or watcher during preparation. Exact final published SHA needs coordinator GO.
Thread cwd is `/root`, not the assigned worktree; a later Build runtime must satisfy watcher entry rules before dispatch.

## Pinned inputs

Request `kani3300-cmp3-uninit-20261111-01`; root request equals `RUN-REQUEST.json` snapshot.
Request SHA256 `2fcfec5e616561e62bdddb894ab3378974a020c03ea6fc1871f668571a90cf7a`.
Kani patch reused in place: `research/challenge-8/kani-k1/kani3300/u4/kani-uninit.patch`.
SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, 100977 bytes, eight production paths, no tests.
Patch bytes equal U4 and all production sections of immutable CMP2 build patch SHA256
`17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`.
Full CMP2 candidate `b1f0105c0390fb55081e3d186fa286d23867b585`; inherited U4 static expected applied tree
`d356238999ab436ddc1dd7ffa845b0db214aa53e` (actual Cloud tree NOT_RUN; see U4 `PATCH-BINDING.json`).
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`, unchanged.
Protected lane/tooling paths equal KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; no tooling edits.
CMP2 acceptance FAIL is the motivation for this diagnostic, not a prerequisite PASS for CMP3. U4 remains held.

## Nine selected roots and acceptance

Prefix: `slice::sort::shared::smallsort::verify::uninit_probe::`.
All observations, actual argv, counts, covers, failure locations and first failing step remain NOT_RUN.
The request asks SUCCESS for diagnostic positives to detect failures; U8 is an integration probe, not an established PASS control.

| Step | Root suffix | Operation / required observation |
|---|---|---|
| 1 | cmp3_index_range_len | actual core IndexRange::zero_to(2).len() == 2, post-operation cover |
| 2 | cmp3_polymorphic_sized_len | initialized PolymorphicIter, native sized len() == 2, covers |
| 3 | cmp3_polymorphic_unsized_len | coerce reference to PolymorphicIter<[MaybeUninit<usize>]>, native len() == 2, covers |
| 4 | cmp3_manually_drop_unsized_len | ManuallyDrop -> explicit Deref -> unsize -> native len() == 2, covers |
| 5 | cmp3_into_iter_len | IntoIterator::into_iter([a,b]), len() == 2, cover before Drop |
| 6 | cmp3_into_iter_next | Some(a), Some(b), None, post-operation covers before Drop |
| 7 / U8 | small_sort_general_with_scratch_u8_n4 | unchanged real scratch path, sorted/count assertions, normal-return cover |
| 8 / U1 | pincheck_calibration_uninit_read_u8 | FAILED on uninit read; inspect exact failure count/location and each cover |
| 9 / U2 | pincheck_calibration_init_read_u8 | SUCCESS, written byte assertion and covers |

All nine existing proof roots and all preceding source bytes in uninit_probe.rs are preserved.
Six new roots remain behind its existing opt-in controls gate. Three minimal adapters are inside iter_inner under cfg(kani),
with crate-visible re-exports only. Real methods, signatures, visibility, types and production code remain unchanged.
Steps 2–4 construct alive=0..2 and [MaybeUninit::new(a), MaybeUninit::new(b)] with arbitrary usize inputs.
No raw-read/AddressOf instrumentation precedes len. Adapter covers immediately follow len, before sized/unsized Drop;
root covers follow adapter return. Step 4 naturally suppresses Drop through ManuallyDrop. Count Drop failures separately.
Covers aid localization only: assertion reachability does not establish MIR identity or causality. No isolated alive.len shortcut.
All adapter comparisons share an extra call boundary; inlining, unsizing and Drop can change the instrumentation context.

## Controls, budget, evidence and stop

Exactly one diagnostic build, standard4/jobs1, 3m per root, controls/uninit on, inventory off; no retries.
Envelope 9*3+30 = 57 minutes; reserve 57*$0.0135 = $0.7695 <= cap $0.80. Spend $0, submitted reserve $0.
Generated kani.args/rustflags prove intent only. Static request validation and scope/identity checks PASS (`static-check.json`).
No local cargo/rustc/Kani/CBMC or preparation/extraction; no Actions/PR/issue. Runner unchanged; no service tests rerun.
Independent Luna HIGH review PASS (`INDEPENDENT-REVIEW.md`), candidate `e8712286a092ff417a6cc7651e679f1d7598d3f0`;
spec SHA256 `f0f7f1e42c224fbfcc381f3a018facc60d964090d633aee32c342cd7205250ad`,
packet SHA256 `d15a2cbc0abf2e259fff54a3fad7a67b9c9fc56169ee87d37ad50c17e7afea96`. Review does not authorize dispatch.
Coordinator must check exact published head/request, slots, phase, deadline envelope and project/nightly accounting before GO.
After GO only: existing k1g.sh dispatch for this branch, then k1g.sh watch BUILD and end turn (watcher runtime entry required).
After terminal: permitted Brief and bounded k1g.sh summary/native/native-field/rows; status, budget, check-tooling against KT2.
Bind build/head/request/pin/toolchain/patch/actual applied tree and actual -Z uninit-checks; retain exact/complete/omitted fields.
Do not read raw/full logs, archives, credentials or bypass the bounded interface. Partial Failed Checks are not a complete list.
Write RESULT-KANI3300-CMP3.md here, <=30 lines: nine rows with status, failed/total, covers, verbatim located Failed Checks,
omitted counts, first failed step, limits of localization, linked transfer/delayed-get facts or reason UNKNOWN, next step and cost.
Needed causal binding: concrete function instance/MIR-place/type/base object+offset, R ranges/values before/after transfer,
points-to targets and Set/Copy/Get ordering. Same span alone does not identify the object. If absent, cause UNKNOWN;
propose a separately authorized bounded nonmutating trace. If all steps pass and U8 fails, localization is incomplete.
U4 remains blocked until original gates and separate exact-packet GO. No repair, total pointee initialization or extra Build here.
Preparation ends at PRE-BUILD REVIEW <full final SHA>, then stop until coordinator GO.
