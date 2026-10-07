# OVERNIGHT-SELECT-SORT4-26.10: guard and extraction design

Source review on 2026-10-08; **design only, no hosted proof or accepted profile**.
This note concerns the unchanged actual `core::hint::select_unpredictable` body at
`library/core/src/hint.rs:838–880`, specialized to `T = *const Element` with
unrestricted `Element`. It does not update historical S6/S7c evidence. The
working source is the updated repository std; VeriFast source inspected at
`/tmp/verifast-review-26.10`, release commit
`f76012fb518703b1d98e243ac4f487f16877cfcb`.

## Actual obligation and resource accounting

The intended pointer-specialized helper contract is the old adapter's full
post: current `thread_token(t)` in, same token and the **complete** result
pointer `condition ? true_val : false_val` out, `on_unwind_ens false`. This is
a specialization of the actual generic Rust body, not a generic helper theorem.
Neither argument grants access to an `Element` pointee. The two local
`MaybeUninit<*const Element>` wrappers each hold an initialized **pointer
value**. Their addresses are distinct local slots. The first two typed
intrinsics select respectively the selected slot `S` and the other slot `D`,
including provenance; they grant no storage permission by selecting a pointer.

The source constructs `DropOnPanic { inner: S }`, drops the pointer value at
`D`, moves the guard to `mem::forget`, then selects one of the two wrappers and
calls `assume_init`. The old source-linked prefix in run 37656621026 reaches
the call to `forget`: both wrapper opens, split, typed pointer drop, and both
wrapper closes pass. That is evidence for a prefix on the **old** profile only.
At `std/lib.rsspec:420`, generic `forget<T>` requires `<T>.own(t,value)`.
VF26.10's `default_struct_own` builds field ownership, but for a struct with
private fields its generated own predicate is `false`
(`vf_mir_translator.ml:6125–6145,6690–6698`). The local private-field
`DropOnPanic` therefore cannot satisfy this generic precondition. Its inner
raw pointer `.own` would carry no slot permission even if the nominal own
were changed to that conjunction.

There is a real resource conflict in the obvious stronger model. A guard own
that exclusively owns `*S |-> p` permits its `Drop` to call
`S.drop_in_place()`, but ordinary `forget` consumes and leaks the guard own.
The normal continuation needs the selected initialized slot to close its
`MaybeUninit` wrapper and obtain the selected pointer value. It cannot both
leak and retain the same exclusive slot. Conversely, defining guard own as
mere pointer bits makes the `Drop` proof unable to dereference `S`.
`guard.own = true`, an invented second slot chunk, or extracting pointee
`Element` rights from pointer bits would mask this conflict.

## Minimal candidate: prove the guard cannot run in this specialization

For `T = *const Element`, the exact guard lifetime has only one potentially
panicking call while it is live: `D.drop_in_place()`. The narrow checked
pointer drop/glue rule must establish `on_unwind_ens false` for the actual new
std body (`ptr/mod.rs:843–864` calls compiler `drop_glue`) and preserve the
initialized raw-pointer slot, thread, and unrelated frame. The exact
source-linked `forget` operation must also be no-unwind; its body remains
`let _ = ManuallyDrop::new(t)`. Then the guard is moved to `forget` on every
reachable continuation and its drop flag clears. No reachable cleanup may
invoke `DropOnPanic::drop`; this must be shown from the full **new** typed MIR
and translated CFG, not inferred from source order or an isolated fixture.
The third pointer-wrapper intrinsic and `assume_init` must each be no-unwind
as well, for the helper's own unwind post.

Under that path proof, a narrowly source-linked, nominally and callsite-bound
forget adapter can consume the guard value while **framing both local slot
chunks**. The old autonomous generic forget body theorem is useful evidence
for the `ManuallyDrop::new` identity/dead-code repair, but is not itself an
actual-call redirect. A new adapter's pre/post should explicitly carry the
thread token and independent `*S |-> pS`, `*D |-> pD` (or their opened wrapper
resources), return those same chunks, and have `on_unwind_ens false`.
The body must be byte-exact to new `mem::forget`, with a checked nominal
`select_unpredictable::DropOnPanic<*const Element>` type and callsite. The
semantic claim is: moving this valid guard into a no-destructor
`ManuallyDrop` performs no read/drop of either pointed-to slot and does not
invalidate a separately held slot permission. This is a trusted Rust/MIR to
model correspondence unless a lower-level ownership proof establishes it.
It is **not** a general safe `forget<T>` contract or a claim that private
`DropOnPanic.own` is true. The emitted actual call and every cleanup edge
must still be checked; a token-only surrogate with no actual linkage is only
an auxiliary body result.

Separately check the actual `DropOnPanic<*const Element>::drop` body under an
explicit initialized-slot precondition (borrowed `&mut` guard, `inner=S`,
`*S |-> p`, token) and prove the appropriate pointer-drop post and no-unwind.
Do not count VF's default `own=false` SAFE Drop compatibility as a body proof:
that would be vacuous, and a contradictory-precondition/dead-code control
should reject it. This separate body result documents what a reachable guard
destructor would require; the actual helper's proof relies on its destructor
being unreachable while live. If the new MIR has a reachable unwind from
`D.drop_in_place` or another operation while the guard is live, this route
fails and must be replaced by a genuine recoverable borrow/invariant protocol
for the selected slot. Such a protocol must explain how the slot permission
returns after `forget`, and prove the SAFE Drop call under its own predicate.

## New `assume_init` and the remaining value obligation

The previous raw union-field read proposal is stale. In updated
`maybe_uninit.rs:722–730`, `assume_init(self)` calls
`assert_inhabited::<T>()` and `transmute_neo(self)`. The latter in
`mem/mod.rs:1278–1283` checks equal sizes in a const assertion and invokes
compiler `transmute_unchecked`. Updated `ManuallyDrop<T>` directly contains
`T` (`manually_drop.rs:154–158,180–182`); old `MaybeDangling` field/MIR
certificates cannot be reused.

For the exact `T = *const Element`, the desired consuming rule is:
`MaybeUninit::inner(wrapper) = some(p)` plus the existing pointer-wrapper
ownership and current thread yields the same **complete pointer** `p`, raw
pointer ownership, same thread, and no unwind. The rule must fail for `none`
and for arbitrary `T`; it grants no `Element` cell/borrow and may not replace
provenance-bearing equality with numeric address equality. The equal
size/alignment and valid initialized-pointer representation facts come from
the actual `MaybeUninit` union and transparent `ManuallyDrop` layout and pinned
compiler behavior; these are trusted correspondence unless independently
proved by the frontend. `transmute_unchecked` itself has no Rust body theorem.
`assert_inhabited` for a raw pointer is a separate compiler specialization.
Source, typed MIR and call graph must show the exact move from the selected
wrapper through `transmute_neo` to the returned pointer, with no extra copy,
read or drop. A generic transmute rule would be much broader than needed.

## Proposed gates and next decisions

1. Re-pin new std method/guard/forget/`assume_init`/`transmute_neo` sources,
   adapter ghost-strip identity, nominal DefIds, fields, generics, callsites,
   complete NORMAL and readonly MIR including all cleanup successors. Old
   certificates must fail closed against changed layout or body.
2. Isolate the typed raw-pointer drop and generic forget transfer controls
   before actual linkage. Positive controls must execute body, return, leak and
   dead-code gates; negative controls must fail at false normal/unwind posts,
   wrong source/MIR identity, wrong receiver or extra operation. Preserve an
   ordinary reachable unwind and a cleanup shared with another predecessor.
3. Check a source-linked exact-guard forget adapter with independent selected
   and unselected slot frames; require false frame-loss, frame-duplication,
   wrong-value and false-post controls at their intended proof obligations.
   Separately prove the typed destructor under a non-vacuous slot precondition.
   A failure at `guard.own` in the *stock* SAFE `forget` call is expected until
   exact actual linkage is established, not evidence of helper correctness.
4. Add the new pointer-only `assume_init`/`transmute_neo` conversion with
   source and full typed MIR gates. Positive symbolic pointer values and
   true/false branch cases must preserve complete value and frames; negatives
   include `none`, wrong returned pointer/provenance, wrong type/layout,
   source/MIR mutation, and false post. An unsupported frontend/refiner
   failure is inconclusive, not an intended negative.
5. Run the unchanged actual helper with all three intrinsic calls, both
   wrappers, guard construction/move, pointer drop, forget, and extraction.
   Accept only full normal return/leak/dead-code/refinement and the stated
   no-unwind post, with a certified absence of reachable guard cleanup and
   same-profile regressions. If cleanup is reachable, stop the no-guard-own
   route and implement/review a recoverable guard borrow protocol before
   claiming full actual safety.

Current evidence proves none of these new gates on VF26.10. The principal
trust boundary is compiler-backed raw-pointer drop glue, exact intrinsic
selection, `ManuallyDrop` destructor suppression, and pointer-only
`transmute_neo` representation. Resource equalities, frame preservation,
branch selection and wrapper state transitions remain proof obligations.
