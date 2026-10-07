# A1 frontend review before pointer-only semantic edit

2026-10-08 source and O4 canonical MIR review. This is a design and
self-review, not an accepted proof. The only target is
`MaybeUninit<*const Element>::assume_init` as used by the unchanged actual
`hint::select_unpredictable<*const Element>` helper. `Element` is unrestricted.

## Observed stock entry points

* VF26.10 `vf_mir_translator.ml:2323–2379,2390–2655` handles unknown typed
  FnDefs through `translate_regular_fn_call`, producing `FnCallOutcome`.
  Neither `assert_inhabited`, `transmute_neo` nor `transmute_unchecked` has a
  stock special case or relevant stock std spec. An unresolved external call
  is the expected first proof blocker, subject to O4 evidence.
* Call translation at `:2680–2799` builds a normal assignment/goto and also
  records unwind successors. A typed no-unwind primitive must account for
  translated CFG successor inventory as well as its postcondition. Reuse the
  already accepted narrow CFG rationale only after the O4 MIR/AST identifies
  an orphan; preserve cleanup reached from another real predecessor.
* The exporter at `vf_mir_exporter/src/lib.rs:2273–2290` serializes MIR
  `Rvalue::Cast(CastKind::Transmute, ...)`. It also serializes
  `BoxDerefTransmute` to the *same* wire `transmute` tag. The stock translator
  at `vf_mir_translator.ml:3320–3390` prints that tag and then translates
  all ordinary cast kinds to `Ast.CastExpr`; it does not apply a typed
  `MaybeUninit` representation rule. Because the wire kind is merged, any
  candidate must require the complete operand type/shape and reject
  `Copy(local.BoxAsNonNull)` or any Box projection. If that cannot be proved
  from the serialized data, split the two exporter/schema variants instead
  of accepting a name-only transmute hook.
* Stock `general.rsspec:109,153` defines raw pointer own as `true`. The S6
  candidate defines `MaybeUninit_pointer_own<Element>` by a `some(p)`
  branch containing that pointer own. Stock `std/lib.rsspec:478–485`
  relates `size_of` and `align_of` of `MaybeUninit<T>` and `T`; the model's
  abstract `MaybeUninit::inner` is not itself a compiler layout theorem.

## Proposed exact semantics and dependency chain

1. For exactly `assert_inhabited::<*const Element>()`, after source attributes
   `#[rustc_intrinsic]` and `#[rustc_nounwind]` and full typed call/MIR check,
   return unit without unwind or heap change. Raw pointers are inhabited.
   Do not generalize to arbitrary T or infer that an arbitrary pointer is
   dereferenceable.
2. For exactly `transmute_unchecked::<MaybeUninit<*const Element>,
   *const Element>(src)` in the certified `transmute_neo` body, consume the
   initialized wrapper model `inner(src)=some(p)` and its pointer-only own;
   return the **same complete pointer p**, its raw-pointer own and the thread.
   The rule is undefined/unavailable for `none`, unknown inner, different
   source/destination types, layout mismatch or Box cast operand. This is
   trusted compiler-to-model correspondence for a type-specific primitive,
   not a proof that arbitrary transmute is safe. It never creates
   `*p |-> Element` or any `Element.own` resource.
3. Prove the exact local source copy of `transmute_neo` with its const size
   check and compiler intrinsic call under that rule. Pin complete NORMAL and
   readonly typed MIR, including generic args, operand move, destination,
   const assert, CFG and unwind. Only then redirect the exact public
   `std::mem::transmute_neo` call inside the exact local `assume_init` copy.
4. Prove the exact local `assume_init` body, including step 1 and the checked
   `transmute_neo` summary. Its pre is current thread, initialized
   `MaybeUninit_pointer_own`, and `inner(storage)=some(p)`; post is same
   thread, result exactly p, raw-pointer own and false unwind. Then certify
   exact actual helper callsite and redirect to this checked method summary.
   No method body or compiler intrinsic may be skipped merely because its
   name matches.

The representation obligation is deliberately visible: source pins must bind
`MaybeUninit`'s `uninit: ()`/`value: ManuallyDrop<T>` union, new direct-field
transparent `ManuallyDrop<T>`, `transmute_neo`'s equal-size check and its
`transmute_unchecked` invocation, plus typed MIR for the chosen specialization.
The resulting p equality is over the model's complete pointer value, including
provenance. An `as usize` equality would be inadequate. Size/alignment lemmas
and source attributes support applicability; the correspondence between
initialized union bytes and abstract `inner=some(p)` is trusted unless a more
detailed verified memory model is supplied. This assumption must be listed in
the accepted profile if the primitive rule is used.

## Controls and self-review

Positive cases: symbolic p (including null and provenance-distinct pointers
if representable), independent mutable slot and fractional frame, both actual
select branches, exact source/ghost-strip identity, complete NORMAL/readonly
MIR, refinement, full body/return/leak/dead-code and false unwind. A direct
compiler rule test does not suffice for source-linked method acceptance.

Proof negatives must reach named obligations: `none` and unknown inner fail
the primitive/method precondition; false/wrong pointer post fails equality;
lost or duplicated thread/frame fails leak/post. Admission negatives must
reject changed std source, union/direct-field layout, type arguments, cast
kind/operand/destination, `BoxAsNonNull` projection, const size check,
extra MIR operation, swapped return, altered normal/unwind successor or
actual callsite. A source/export/decode/refinement failure is inconclusive.
Relevant S6 component matrices and ordinary shared cleanup/false unwind
controls must pass on the cumulative profile before actual integration.

Self-review risk: a raw `CastKind.Transmute` rule based only on the wire tag
would also admit `BoxDerefTransmute`; a rule based only on the callee name
would admit unrelated generic substitutions; a contract returning a pointer
without `inner=some(p)` would assert the very validity to be proved. The
candidate must reject all three. The O4 capture decides the actual MIR form
and the minimal edit point. No semantic patch is authored before that review.

## O4 canonical capture and independent review

Hosted run 37702049156, proof SHA 86e84ace, captured complete NORMAL MIR
records for the exact method fixture (SHA-256
`ed78895c20f1a8ea3b1c63a55a96f996a9c5158861861786a2cdb5a6bda46de7`)
and the exact local `transmute_neo` fixture (SHA-256
`743990d692c78f43b786768f777ea4b7063178732ac8fec119e6e2d26d44d9ea`).
The former has `assert_inhabited::<*const Element>()` with `unwind=unreachable`,
then a one-argument move call to
`transmute_neo::<MaybeUninit<*const Element>,*const Element>` with
`unwind=continue`. The latter has one plain-local `Move(_3)`
`CastKind::Transmute` to `*const Element`; `_3` is a copy of the incoming
`MaybeUninit<*const Element>`, and the const size assertion is a unit
statement in this specialization. There is no Box projection in either
record. The method's first full-verifier error is missing
`assert_inhabited`; the transmute body's first is a source/destination type
mismatch at the cast. NORMAL and readonly export/decode plus refinement pass.

Self-review result: the source and destination types must both be checked
and the operand must be a plain-local Move with no projection. The minimal
patch checks the destination as `*const Element`, looks up the plain Move
local's exact decoded MIR declaration, and requires its source type to be
`MaybeUninit<*const same Element>`. It then emits a call to a **typed**
primitive with that exact argument type. The explicit MIR lookup matters
because VeriFast's raw-pointer type translation erases const versus mut;
ordinary call typechecking alone could accept a `*mut Element` wrapper.
Other generic const-pointer transmutes fail closed at the translator's
explicit admission check; the existing BoxAsNonNull special case runs first.
This conservative rejection is an experimental policy pending the hosted
wrong-source, mutable-source, Copy and projection controls. The component
patch is based on the S6 translator overlay and must be applied after S6.
Call typechecking remains an independent fail-closed backstop: a Box source
or a wrapper with another pointee cannot satisfy it. Although
the existing exporter conflates `Transmute` and `BoxDerefTransmute`, this
typed argument check and plain Move rule reject the Box case, without
changing the wire format. A compiler-to-model primitive then consumes
initialized `MaybeUninit_pointer_own` and returns the exact complete pointer;
it has no right to any `Element` cell. A separate typed
`assert_inhabited` rule accepts only `*const Element`, after the source pin
checks the compiler's `rustc_nounwind` attribute. Neither rule suppresses
an actual cleanup edge. The method still needs a separately proved
`transmute_neo` call linkage; this patch alone cannot close it.

The trusted primitive is declared as an ordinary Rust-spec function, so the
Rust parser gives it `fn_outcome<*Element>`, even though the MIR cast produces
`*Element`. The cast translation uses the existing `result_of_outcome`
projection. Its `unwinding` case is made impossible by the primitive's
`on_unwind_ens false`; no unconditional result cast or branch suppression is
introduced. This is the same projection used by other rvalue helpers in the
stock translator. The direct-body matrix must still validate it on-host.
