# Overnight helper components — BEFORE card

2026-10-08, own scope `research/challenge-8/overnight-helper/`; no proof run yet.
All runtime source is the updated repository std, pinned by SHA-256 in generated
certificates. The hosted tool baseline is VF26.10 source
`f76012fb518703b1d98e243ac4f487f16877cfcb`, nightly2026-09-25. The accepted
CFG result is run 37698481357 / proof SHA `e6c02f22`; S6 transfer is a separate
unaccepted dependency until its own controls pass. This card precedes edits to
the fixture/certificate code.

## G1: source-exact generic forget with frames

Actual obligation: `core::mem::forget<T>` at `library/core/src/mem/mod.rs`,
body `let _ = ManuallyDrop::new(t);`. Hypothesis: with the accepted exact
`ManuallyDrop::new` CFG repair, a **non-SAFE** source-linked generic adapter
consumes its by-value argument and preserves a symbolic initialized raw-pointer
slot and unrelated fractional frame by separation. Its pre requires current
thread token; post returns it; unwind post is false. A probe holds
`*slot |-> p`, `[f]*frame |-> flag`, thread, and calls the adapter, requiring
all three unchanged. No `Element` pointee rights or nominal guard own occur.
This is a component and does not yet justify redirecting actual SAFE forget.

Expected positives: exact full source pair, NORMAL/readonly export+decode,
refinement, full body/return/leak/dead-code verifier for generic adapter and
symbolic frame probe. Expected negatives: false post, lost/duplicated frame,
wrong frame value, lost/duplicated slot, wrong slot value, lost/duplicated
thread, absent slot and absent thread; all must fail at the named proof/leak
obligation rather than setup/frontend. A contradictory precondition is a
separate dead-code negative. Source and typed MIR mutations must fail admission.
`ManuallyDrop` identity/destructor suppression is trusted correspondence;
ownership/frame preservation is checked.

## A1: pointer-only updated assume_init

Actual obligation: `MaybeUninit::<*const Element>::assume_init` at
`library/core/src/mem/maybe_uninit.rs:722–730` calls
`assert_inhabited::<*const Element>()`, then
`transmute_neo::<MaybeUninit<*const Element>, *const Element>(self)`.
`transmute_neo` at `mem/mod.rs:1278–1283` checks equal sizes then calls
compiler `transmute_unchecked`. Hypothesis: an exact type-specific rule
consumes `MaybeUninit_pointer_own<Element>(t,storage)` and
`storage.inner() == some(p)`, returning the **complete** pointer `p`,
`raw_ptr_own<Element>(t,p)` and thread, with no unwind. The predicate is
defined in the separate S6 profile; no ownership of `Element` is inferred.
`none` or unknown initialization cannot pass. This is an unsafe method with
the caller's initialized-value obligation; it is not a generic transmute rule.

Trusted boundary: compiler intrinsic `transmute_unchecked` and raw-pointer
`assert_inhabited`, plus representation of the updated union and direct-field
`ManuallyDrop`. The equal-size/layout and no-drop/no-copy source/MIR chain
must be pinned; the pointer value, provenance, ownership transfer, thread,
frames and no-unwind are proof obligations. Old raw-field-read certificates
must reject the updated method. Proposed positives include symbolic pointer
and independent frame; negatives include `none`, unknown, wrong selected
value/provenance, false post, lost/duplicated frame/thread, changed method/
transmute source, wrong nominal type/generic arguments, extra MIR operation,
wrong operand/destination and changed CFG/unwind. A first hosted capture may
refine concrete block IDs/locals; until then a certificate must fail closed.

## H1: actual linkage boundary

Only after G1/A1 and S6 pass may an exact nominal
`select_unpredictable::DropOnPanic<*const Element>` forget redirect be
considered. The helper has the full pointer-value result post and false
unwind post. While the guard is live, typed pointer drop must be proven
no-unwind. The full exported and translated helper CFG must show no reachable
guard destructor before its move into no-drop `ManuallyDrop`. Separately prove
the actual `Drop` body under an explicit initialized selected-slot right; a
private-field `own=false` vacuous SAFE compatibility is not that proof. If
the guard destructor is reachable, a recoverable borrow/invariant protocol
is required. There is no `guard.own=true`, no extra slot right, and no
Element right.

Main agent owns hosted workflow, acceptance, integration and checkpoints.
This directory supplies isolated candidates/certificates only. No local
compilation, verifier or executable tests are authorized.
