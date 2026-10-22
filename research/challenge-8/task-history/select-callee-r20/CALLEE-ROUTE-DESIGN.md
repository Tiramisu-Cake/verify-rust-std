# R20: actual `select_unpredictable` callee — current state and route (design, unverified)

## Correction of the starting assumption

R20 started from "forget guard-own at `std/lib.rsspec:420`" (the S6/S7 GitHub-hosted record). The later Cloud record supersedes it. NIGHT-CLOUD-4 (Build `6c560082-2359-4444-85ec-8bb247aea7ae`, proof `61034fd5`, o26 lane, pinned tool `f76012fb`, translator `0862e635`; `EXPERIMENT-LOG.md` ≈ line 5555) used the **nine-body owned-forget unit**:
- seven checked prefix callees: `MaybeUninit::new`, `as_mut_ptr`, pointer and generic drop, the A1 `assume_init` and transmute adapters, and `checked_forget_owned`;
- the actual `select_unpredictable` (`T = *const Element`) and the actual nested `DropOnPanic::drop`.

In that unit all seven prefix callees verify their returns and leak checks, and the actual body passes:
- the truthful nominal guard close;
- the unselected-guard `Drop`;
- the SAFE `forget(guard)`.

It then stops at the final `select_unpredictable(condition, true_val, false_val).assume_init()`, where the S6-patched `lib.rsspec(462,47-48)` rejects an absent `MaybeUninit_pointer_own<Element>(t, MaybeUninit::new(payload))`. Which payload (selected or unselected) is UNKNOWN: Brief has no index for that Build (HTTP 404).

## Guard ownership (already the accepted design; no gate exemption, no guard-own=true)

- `pred<T> <select_unpredictable::DropOnPanic<T>>.own(t, g) = *g.inner |-> ?payload &*& <T>.own(t, payload);` This is consistent with the actual `Drop`, which opens it before `drop_in_place`.
- It is closed truthfully at `DropOnPanic { inner: guard }` from the selected cell.
- The SAFE `crate::mem::forget(guard)` is linked to `checked_forget_owned<T>`. That component was accepted locally in O22; its body is byte-exactly std `mem::forget` (`let _ = ManuallyDrop::new(t);`) and its contract is owner-preserving: req/ens `<T>.own(tid, t)`, `on_unwind_ens false`. The redirect is `Sort4ActualForgetOwn`, which certifies the same-unit spans and the std `mem/mod.rs` body.
- The guard's own is re-opened after the call to recover the selected cell.

This route relies on the existing TRUSTED ManuallyDrop representation, as recorded in the S7 design.

## Candidate repair for the recorded blocker (to verify in Cloud)

For `T = *const Element`, `MaybeUninit_pointer_own<Element>(t, MaybeUninit::new(p))` is built from `raw_ptr_own<Element>(t, p)`, which is `true` (`rust_belt/general.rsspec:109`). Two cases:
- **Unselected wrapper.** After its `drop_in_place`, the wrapper's pointer bits are unchanged. Re-closing `raw_ptr_own` and then `MaybeUninit_pointer_own` over the recovered `*ptr |-> p` creates no ownership. That makes it a checked ghost step, not a bridge.
- **Selected wrapper.** It is the same step after the post-forget guard re-open.

Each close must be justified by the exact points-to chunk. A control must show that omitting each close fails at the same site. This is a proof/annotation repair within the accepted method.

The S6 spec patch already provides this as a checked lemma: `close_MaybeUninit_pointer_own<Element>(t, v)`, req `true`, ens `MaybeUninit_pointer_own<Element>()(t, v)`, proved by cases on `MaybeUninit::inner(v)` with `raw_ptr_own` = `true` (`overnight-s6/verifast-s6-26.10-candidate.patch`, lines 18–28). The repair is therefore one ghost call of that lemma for the wrapper value demanded at the final select. `select_MaybeUninit_pointer_own` (lines 32ff.) then gives the selected wrapper's ownership for A1 `assume_init`. Verified definitions: `raw_ptr_own` is `true` at `general.rsspec:109` (pinned `f76012fb`); `MaybeUninit_pointer_own` matches `inner` with `none => true`, `some(p) => raw_ptr_own(t, p)`.

## Port to the authorized lane (next implementation cycle)

Only `o26-sort4-c1-current-recovery` is authorized. All nine activation hooks exist in the R17-chain translator base (`6c04f608`), verified statically by grep:
- `SORT4_ACTUAL_OWNER_REPO_ROOT`
- `SORT4_ACTUAL_OWNER_ADMISSION`
- `SORT4_ACTUAL_OWNER_NINE_ADMISSION`
- `SORT4_ACTUAL_NESTED_H2_REPO_ROOT`
- `SORT4_ACTUAL_FORGET_OWN_REPO_ROOT`
- `SORT4_A1_NINE_REPO_ROOT`
- `SORT4_MAYBEUNINIT_REPO_ROOT`
- `SORT4_SELECT_INTRINSIC_REPO_ROOT`
- `SORT4_POINTER_DROP_REPO_ROOT`

The current std sources match the translator's pinned digests (intrinsics `c286…`, hint `3623…`, mem `86cc…`, maybe_uninit `40db…`).

Implementation plan:
1. A new body action `select-callee-nine-diagnostic`, run by a separately pinned module `a1-select-callee-r20.py` that the R17 body adapter loads only for that action.
2. Unit generation reuses the o26 precedent (`o26-recipe.py` `OVERLAYS`/`GUARD_VARIANTS`): the five preparers get their GitHub-hosted guard replaced by the Cloud provider check under pinned overlay SHAs, then run in the Cloud work root. Alternatively, commit a generated source pair whose provenance (preparer SHAs plus std SHAs) is checked in Cloud.
3. Verification on the reconstructed R17-chain tool with the activation set above, through the existing `run_case` gates (source pair, refinement, single target, leak/dead-code unchanged).
4. Required controls: the O22 owner negatives, an omitted-guard-close control, an omitted-repair-close control (it must fail at the final select), and pin/source refusals.
5. Transport. The lane is at 191/191 chunks with 538 bytes spare after the R20 pruning (`d67636a6`). The nine-body preparers and fixtures add several KB. A further closure decision is needed: prune more closed-route items with an inventory, or the owner raises the cap.

## Scope limits

- The result is pointer-specialized (`T = *const Element`, sort4). `*mut T` for `swap_if_less` (Network) needs the same unit at `*mut` or a generic proof. The generic-T gap (two `<T>.own` transfers, ZST aliasing) is in `overnight-assume-actual/ACTUAL-GENERIC-SELECT-GAP-2026-10-09.md`.
- No credit. Callee acceptance also needs normal, unwind and nested-Drop completion and the matrix. Only after that can the sort4 route use it (opt-in redirect with source/MIR certification), followed by Cloud c5 (`34e37669`), the selectors and the copies.

## Review finding: certificate pins (R20 review NO_GO #2)

Under `SORT4_ACTUAL_OWNER_NINE_ADMISSION`/`SORT4_A1_NINE_REPO_ROOT` the pinned 20+2 translator certifies the nine-body unit exactly. The owner admission rebuilds the actual body together with its injected ghost and requires the exact ordered ghost-statement list. The nine-admission and A1 nine patches, as refreshed by the two O26 literal refresh patches, pin the `verified/lib.rs` SHA-256 (`1798132f…`). Any ghost-repaired copy is therefore refused at the certificate before the final select.

The repair consequently needs a separately reviewed certificate-refresh tool patch: new source pin and ghost list, with the repair ghost included and the controls preserved. The first R20 callee Build is baseline-only: a fresh reproduction of the recorded blocker, with exact message and location in Brief, on the current commit and closure.
