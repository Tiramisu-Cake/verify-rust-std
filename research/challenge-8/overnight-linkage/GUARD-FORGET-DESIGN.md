# Actual guard and `forget` linkage: static review, no proof claim

This note follows O7 actual source/MIR evidence, run `37705052264`, on std
`cd371e03` and the combined experimental VF26.10 console. It refines
`../OVERNIGHT-GUARD-DESIGN.md`; it does not replace that note or historical
S6/S7c status. O8 intrinsic/pointer-drop linkage is pending. No model patch
or hosted verification is supplied here.

## Concrete actual path

The unchanged `library/core/src/hint.rs` builds two initialized
`MaybeUninit<*const Element>` local slots. After two pointer selects it
constructs `DropOnPanic<*const Element> { inner: S }`, where `S` is the
selected local slot address and the other slot address is `D`. Its only
potentially unwinding operation while the guard is live is
`D.drop_in_place()`. The actual NORMAL and readonly MIR preserve:

- block 6: pointer-drop call, normal successor 7, unwind to common cleanup
  block 13;
- block 7: clear guard drop flag `_30`, move `_20` to `_25`, call typed
  `std::mem::forget<DropOnPanic<*const Element>>`, normal successor 8 and
  unwind to block 13;
- block 9: `MaybeUninit<*const Element>::assume_init`, normal successor 10,
  unwind to block 13;
- cleanup 13: switch `_30`, either resume in block 11 or run the guard Drop
  in block 12, then resume. No source or fixture may erase block 13.

The actual runtime body hash in O7 linkage cases is
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613`.
O7 reached the first intrinsic call after proving local constructor and
as_mut_ptr adapters; it has not checked the guard path or `forget` call.

## Current VeriFast resource interfaces

`/tmp/verifast-review-26.10/bin/rust/std/lib.rsspec:419` declares SAFE
generic `forget<T>` with pre `thread_token(t) &*& <T>.own(t, value)`, post
`thread_token(t)` and false unwind. Its source body is exactly
`let _ = ManuallyDrop::new(t);` in `library/core/src/mem/mod.rs`; the updated
`ManuallyDrop` contains a direct `T` field. `default_struct_own` in
`vf_mir_translator.ml:6125` builds public fields' ownership, but for this
private-field nominal guard `:6690-6698` emits `own=false`. The actual SAFE
call therefore cannot satisfy generic `forget` under the stock ownership
model. G1's exact-body, framed direct probe proves a value/frame property;
its positive path neither calls a SAFE generic callee nor links the actual
nominal guard.

For `DropOnPanic::drop`, `gen_drop_contract` at `vf_mir_translator.ml:4408`
uses `DropOnPanic_full_borrow_content` plus thread as its SAFE pre and
returns field points-to/own. The field's raw-pointer own is empty for this
specialization. The contract does not contain the pointed-to initialized
selected slot `*S |-> p` required by the unsafe
`self.inner.drop_in_place()` call. A verifier pass obtained from a
contradictory guard predicate would be vacuous; the body needs a separate
nonempty initialized-slot precondition.

Weakening SAFE generic `forget<T>` to thread-only for arbitrary `T` would
make moved-value ownership disappear from the model. Defining
`DropOnPanic.own=true` would not supply the selected slot to its Drop body.
Making guard own exclusively contain `*S |-> p` supplies Drop, but ordinary
forget consumes and leaks that own; the normal continuation then lacks the
slot needed to close the selected wrapper. Copying the slot chunk or granting
`Element` pointee permission from a raw pointer is unsound.

## Narrow, conditional pointer-specialized route

First establish the typed `D.drop_in_place()` no-unwind result and preservation
of the initialized pointer cell; O3 proved its local method, while O8 must
check the actual callsite redirect. Then the full MIR/translated CFG must
show no reachable guard destructor while `_30` is true. A different unwind
from block 6 while `_30=true` invalidates this route. Later unwind from
`forget` or `assume_init` must either be excluded by pinned false-unwind
callee contracts or accounted for with `_30=false` and no guard Drop. The
shared cleanup block stays in the graph and in evidence.

Only under that path invariant is a nominal callsite rule plausible:
specialize the exact source `forget<DropOnPanic<*const Element>>` to the
single typed call in block 7. The rule consumes the guard **value and drop
obligation**, returns thread and leaves separately owned selected and
unselected slot cells untouched, and cannot unwind. Its source/MIR
certificate must pin `mem::forget`, `ManuallyDrop::new`, the guard ADT and
field type, `_20 → _25` move, `_30=false`, typed FnDef/substs, normal and
cleanup successors, and all other actual operations. A trusted correspondence
remains: `ManuallyDrop` construction suppresses destruction of this moved
guard. The ordinary framed slot preservation is a separation-logic proof
obligation, not an added ownership axiom. Any identity lowering must repair
emitted successor inventory narrowly, as the accepted CFG component does,
without deleting MIR cleanup 13 or its other predecessors.

Separately prove a source-equivalent pointer-specialized `DropOnPanic::drop`
body under a **satisfiable** pre `thread_token(t) &*& guard.inner == S &*&
*S |-> p` (plus actual mutable guard-borrow structure), using the accepted
pointer-drop method rule and returning the pointer slot unchanged/no unwind.
This would document what the destructor needs if it runs. It cannot be used
as the whole actual generic Drop theorem without an exact specialization
certificate and a legitimate SAFE contract. If the guard destructor remains
reachable while live, replace the no-Drop path argument with a recoverable
loan/invariant protocol whose forget transition returns the selected slot
right; do not make the missing right an assumption.

Source mutants should change guard field/identity, forget operand/type,
drop-flag order, and one cleanup edge; they must reject at source/MIR
admission. Proof negatives should lose/duplicate/change either slot or
thread, or demand false normal/unwind post, and fail at those obligations.
All normal and readonly exports, refinement, full verifier leak/dead-code
checks, and exact actual body hash remain mandatory. This component's
success would still leave wrapper selection and updated `assume_init`
conversion to prove before claiming the helper's conditional pointer result.
