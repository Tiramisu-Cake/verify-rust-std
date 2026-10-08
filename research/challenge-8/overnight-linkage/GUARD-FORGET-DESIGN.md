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

## Generic nested `Drop` must verify too: source-level architecture

The nested `<select_unpredictable::DropOnPanic<T> as Drop>::drop` body is a
separate MIR body in O7's export. The stock Rust frontend filters only
closures by default (`vf_mir_translator.ml:8091–8121`);
`skip_specless_fns` is false for Rust (`frontend/verifast0.ml:335`). It will
verify this generic method even if the outer pointer-specialized helper's
live-guard cleanup is later proved unreachable. Skipping it or making its
precondition contradictory would hide a generic case and cannot justify an
actual-helper PASS.

For SAFE `Drop`, `translate_body` selects `gen_drop_contract` as the template
(`vf_mir_translator.ml:5109–5152`). A user annotation does not freely replace
that template: `verify_expr.ml:194–295` produces the generated pre before
consuming the user pre, then produces the user post and consumes the generated
post with a leak check. Therefore a source annotation requiring an extra
selected-slot chunk would fail safety compatibility, and one returning an
extra uninitialized chunk would fail the post compatibility leak check.

The generated `DropOnPanic_full_borrow_content` combines the guard's `inner`
field points-to, padding and nominal `DropOnPanic.own`
(`vf_mir_translator.ml:5272–5384`). A truthful nominal own can state an
initialized target-cell invariant, schematically
`DropOnPanic<T>.own(t,g) = *g.inner |-> ?v &*& <T>.own(t,v)` plus pointer
validity. It must be **constructed** by transferring the selected wrapper
slot's real cell right to the guard; the unselected slot remains independent.
For `T=*const Element`, the `<T>.own` part is the accepted empty raw-pointer
value ownership and supplies no `Element` pointee right. The predicate is not
`true` and is satisfiable whenever the caller owns that initialized slot.

Opening this own from the generated borrow pre gives the actual generic
destructor its unsafe call pre. The generic call in its MIR is
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place<T>`, not the pointer-only
specialization used by the outer helper. The stock free
`std::ptr::drop_in_place<T>` contract (`std/lib.rsspec:597–600`) consumes
`*slot |-> v &*& <T>.own(t,v)` and returns `*slot |-> _` with thread on
normal **and unwind**. A new same-source-verified generic method adapter for
the exact `mut_ptr.rs` body must bridge this method call to that free
contract. It cannot claim false unwind or preservation of an initialized
cell for arbitrary `T`; those are valid only for the pointer-specialized O3
component.

The stock generated `Drop` post returns guard `inner` field/padding/thread
but omits the now-uninitialized target slot. That leftover chunk is a real
leak-check obstacle, even after the method call is supported. A narrowly
reviewed nominal `gen_drop_contract` extension must expose the target slot
as uninitialized in both normal and unwind posts, while preserving the
ordinary field/padding/thread posts. It must be gated on the exact guard ADT,
field type, source body and generic method MIR; ordinary `Drop` types retain
their stock contracts. This is a contract-shape repair, not an axiom: the
generic actual body must prove it from the truthful own pre and the verified
generic pointer-drop callee. Negative controls need initialized-slot absence,
wrong target, wrong post state, false unwind, source/MIR changes and a
nonvacuous caller that constructs the guard from a real initialized slot.

On the outer helper's normal path, exact nominal `forget` must consume the
guard value **without** invoking Drop and return the initialized selected
slot from the opened guard own. This is an ownership transfer, not a duplicate:
the selected slot leaves the caller at guard construction and returns once
on disarm. A typed unsafe adapter with the exact source body
`let _ = ManuallyDrop::new(t);` can expose this stronger post; its current G1
direct-body frame proof is only supporting evidence. Generic SAFE
`forget<T>` still has the ordinary own-consuming post and cannot be weakened
globally. The actual SAFE call needs a source/typed-MIR-certified, nominal
single-call redirect to the proven adapter. If the source exactness gate
cannot admit the necessary ghost type predicate and body annotations, that
requires its own reviewed overlay; the accepted S6 gate must not be relaxed
silently.

The frontend already supports user-provided `.own` definitions for a
**private-field local struct** (`vf_mir_translator.ml:6310–6362`), whereas it
rejects user own definitions for public-field structs. The exact nested
`DropOnPanic` has a private `inner` field, so this is a plausible source
annotation mechanism; the qualified nested type syntax and exporter binding
still need a hosted capture. The existing S6 intrinsic actual-body gate
rejects extra body ghost-declaration blocks, so the owner predicate must be
admitted through a reviewed top-level ghost declaration or a separate exact
gate overlay. The `Drop` trait itself contributes no extra impl prototype in
the translator (`vf_mir_translator.ml:7719–7723`); the generated SAFE Drop
template and function body are the operative checks.
