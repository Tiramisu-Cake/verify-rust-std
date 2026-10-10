# Native opaque resource diagnostics: separate Cloud session

Owner `select-sort4`; worktree `/root/verify-rust-std-select-night`; branch
`research/night-select-sort4-cloud-2026-10-09`. Start **2026-10-10 19:27:14 UTC**;
main deadline **21:27:14 UTC**; finish-only absolute deadline **21:57:14 UTC**.
Fresh ceiling **3600 Cloud Build seconds**, no carry from closed C4. One own
queued/running/unresolved Build and at most two project-wide under v2. Reviewed
lane `o26-sort4-c1-current-recovery` only. No Research Actions or local proof
execution. Policy revision read: `c7ca8c467aecf10a4b53039372ee97714f854ee3`
(adoption commit `6726a08d30b37d6d0f4ae65c3d8c2861615d249a`).

The actual obligation is the native resources from
`small_sort_general_with_scratch` in the pinned SmallSort std source, which
must eventually supply the first `sort4_stable` call in the `len >= 8` branch.
That edge and the full native caller are **NOT_PROVED**. The unchanged C4
theorem is conditional on separately supplied raw T source/owner, F cell/owner,
current thread, types, positive size, and optional destination resources.
The caller's scratch is `&mut [MaybeUninit<T>]`; the proposed opaque frame
diagnostic tests whether it can remain in that native form through a small
resource step without claiming a raw T destination bridge.

## Exact diagnostic batch

Use one frozen C4 tool: HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`,
translator SHA-256
`1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`,
kernel SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
`../sort4-native-c4/FROZEN-C4-SNAPSHOT.json` and its prior fresh C4/admission
evidence pin the tool and previous controls. Reuse the prior fresh admission
refusal only as evidence of the **same unchanged gate**; it gives no new proof
credit. The new `profile.json` and `cases.rs` are separate exact inputs.

1. The pointer-expression component uses the source-linked
   `self as *mut [T] as *mut T` expression from `slice/mod.rs:778`, with a
   syntactically corrected assertion. If paired source/MIR/refinement and VF
   succeed, it establishes only this expression in the isolated fixture. A
   parser, refinement, or verifier refusal identifies that first stage.
2. The early-return component checks the actual `len < 2` return and native
   source/F/thread/MU resource restoration under full generated normal and
   unwind contracts. The expected positive is closure at the return; an
   intended failure is the first exact missing resource, never an unrelated
   setup or unsupported-operation refusal.
3. The safe `usize + 16` reproducer isolates the guard overflow obligation.
   A verifier refusal at the addition confirms the previously seen arithmetic
   blocker. This diagnostic is deliberately partial: no bound is assumed and
   it does not prove the caller guard, abort, or inline-const branch.
4. The opaque MU frame component tests whether current native
   `MaybeUninit<T>` ownership can pass through a small checked frame operation
   and return unchanged. It may not add an assumed inverse, raw-T owner,
   positive-size premise, or an implicit callee summary.

All supplied fixtures must preserve their **full generated normal and unwind
posts**, return ownership and leak obligations. The intended domain remains
generic `T: FreezeMarker` and `F: FnMut(&T, &T) -> bool`, arbitrary legal native
slice lengths and `MaybeUninit<T>` scratch; no `Copy`, narrower ZST, or purity
premise is added. These isolated cases do not establish composition or a new
std theorem. A separate narrow source/MIR/AST binding is authorized by the user with independent review and fresh capture. General VeriFast changes remain peer-owned. No native alias overlay, strict-cut draft,
selector profile, C5/select/copy expansion, or unnecessary matrix rerun is authorized.

## Decision and closure

Before dispatch, pin published proof/infra SHAs and inspect the exact recipe,
profile, case blocks, source correspondence, Cloud slots and account. A
source/profile change needs its own fresh Build. After terminal evidence,
record first causal stage and location for every case, exact artifact hashes,
Build IDs, charged seconds and whether a useful interface remains. PASS of a
component permits only the next already agreed within-phase step; a semantic
gap or new trusted rule requires an owner decision. At the main deadline no
new experiment begins. The extra 30 minutes finish the current step, evidence,
accounting and checkpoint only.
