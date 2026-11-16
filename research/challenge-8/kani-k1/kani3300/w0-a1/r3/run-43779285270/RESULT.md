# A1-R3 run 43779285270 — coordinator intake (bounded artifacts only)

Это верификация корректности, не security-работа. Trigger `efddfd120b` (pkg `e3e9f138b7`), attempt 1.
Artifacts: std `ch8-a1-r3-std-43779285270-1` (14188217680), native SEL1 (14187941242), native baseline (14187608266).
Read: sequence-summary, receipts, export.json, stdout tail (bounded). No raw job logs.

## Std rows — Kani SEL1 `14bc57fdb9`, std `70ba5befc6` + A1 overlay (import fixed), `-Z uninit-checks`

Std compiles now (R1 blocker was the `super` import). Serial, fail-fast after watchdog.

| Row | Exit | Verify time | Max RSS | Export verdict | Failed properties |
|---|---|---|---|---|---|
| stable_freeze_u64_n32 | 1 | 255.8 s (row 303.5 s) | 2.90 GiB | FAILURE, 895 props | **1**: `array::iter::iter_inner::PolymorphicIter::<[MaybeUninit<usize>; 2]>::new_unchecked.unsupported_construct.1` — "Checking memory initialization of type PolymorphicIter<[MaybeUninit<usize>; 2]> is not supported. Cannot determine layout for a type that contains union of type MaybeUninit<usize> as a field" (core/src/array/iter/iter_inner.rs:96) |
| unstable_general_nocopy_u64_n32 | 1 | 194.3 s (row 240.1 s) | 2.82 GiB | FAILURE, 907 props | **1**: same PolymorphicIter unsupported construct |
| unstable_network_u64_n32 | SIGTERM | — | backend 13.57 GB | INCOMPLETE | RSS watchdog (group 13 579 075 584 B > threshold 13 575 032 832 B = avail 15.72 GB − 2 GiB reserve); symex 141.7 s, 143 434 VCCs (59 525 after simplification) |
| stable_freeze_u64_n8/n16, unstable_general_nocopy_u64_n8/n16, unstable_network_u64_n18 | — | — | — | NOT_RUN | fail-fast after watchdog |

Reachable source of the unsupported construct: `smallsort.rs:307` in `small_sort_general_with_scratch`
(`[usize; 2].into_iter()` → `array::IntoIter<usize, 2>`), also reported (status SUCCESS = unreachable/other
instances) for `ManuallyDrop<PolymorphicIter<…>>::{new,drop}`, `drop_in_place`, `IntoIterator for [usize; 2]`.
Other unsupported constructs listed with status SUCCESS (caller_location, abort_immediate, cold_path, foreign
rust_begin_unwind, same_allocation) did not fail.

So: on SEL1 the two N32 scratch roots are **one property away** from SUCCESS; the remaining blocker is uninit
layout for a **struct containing an array of MaybeUninit** (array::IntoIter / PolymorphicIter), not covered by C2.
Network N32 with uninit ON exceeds the memory budget (>13.5 GB; S target ≤6 GiB/root).

## Native #5151 fixtures (edition-fixed), `-Z uninit-checks`

| Pin | Fixture | Verdict | Props/failed | Failed property |
|---|---|---|---|---|
| upstream 0aac (baseline) | empty-drop negative | FAILURE | 43/1 | unsupported: `[MaybeUninit<D>; 2]` layout (the #5151 symptom) |
| upstream 0aac (baseline) | initialized-slot companion | FAILURE | 44/1 | same unsupported construct |
| SEL1 | empty-drop negative | FAILURE (intended) | 141/1 | `drop_in_place::<D>.safety_check.1` — UB: reading from an uninitialized pointer of type `*mut D` |
| SEL1 | initialized-slot companion | **SUCCESS** | 142/0 | — |

So the C2 stack **fixes #5151** (matched negative/companion), while `PolymorphicIter<[MaybeUninit<T>; N]>`
(array inside a struct) is still unsupported on SEL1.

Job conclusions are `failure` because rows did not all PASS; that is the expected native negative plus the
unsupported construct and watchdog above, not infrastructure. Proof credit: none (diagnostic A1).
