# `MaybeUninit::assume_init` storage-permission diagnostic

Design prepared 2026-10-07 before any semantic implementation. This note
defines a hosted diagnostic for the remaining pointer-specialized helper
dependency. It does **not** declare a semantic stop or accept the operation.
No local build, verifier, or executable check is part of this design step.

## Question and falsifiable hypothesis

The actual source-linked helper calls
`MaybeUninit::<*const Element>::assume_init` after selecting one complete
wrapper value. The intended input fact is that the selected wrapper has
`inner == some(p)`. The central question is whether the frozen Rust memory
rules can derive the read permission required by the pinned body from the
existing `MaybeUninit` storage/open rules, without assuming a new resource.

Hypothesis: after exact source/MIR admission and the existing storage open
operation, the checked body reaches its typed `const_ptr::read` dereference.
If the existing rules are sufficient, it proves that the loaded value is the
same complete modeled pointer `p`, preserves `raw_ptr_own(p)`, and returns the
thread token without unwind. If they are insufficient, the positive diagnostic
must fail at the read's missing points-to permission. A source, export, type,
or MIR-gate failure is inconclusive and must be repaired before interpreting
the resource result.

The test is limited to `T = *const Element`. It adds no `Element: Copy`,
`Freeze`, pointee ownership, validity, non-nullness, alignment, or aliasing
assumption. The object being read is the initialized pointer slot inside the
local `MaybeUninit` value; it is not the `Element` pointee.

## Pinned source and modeled pointer path

The body to bind is the repository implementation in
`library/core/src/mem/maybe_uninit.rs`, the `assume_init` method whose runtime
body is:

```rust
unsafe {
    intrinsics::assert_inhabited::<T>();
    (&raw const self.value).cast::<T>().read()
}
```

The repository file hash and exact signature/attributes/body bytes must be
recorded from the selected hosted checkout. The adapter is a source-local,
pointer-specialized copy of this body. Its only source substitutions are
`self` to its by-value parameter and `T` to `*const Element`; it may omit the
original `const` qualifier if the pinned fixture cannot express it, but it
must remain a Rust `unsafe fn`. It must use the certified local copy of the
two-field `MaybeUninit` union already checked against the standard-library
source. The actual helper's external `assume_init::<*const Element>` call is
redirected only after that adapter and callsite pass exact typed admission.
This verifies a source-linked body copy, not a claim that the compiler
intrinsic `assert_inhabited` itself has a Rust body theorem.

The MIR gate must require the following value/dataflow chain, including all
locals and CFG edges:

1. One `assert_inhabited::<*const Element>` call, with its exact typed
   function identity and permitted no-unwind edge.
2. A raw immutable address of `self.value`, with the certified union DefId,
   field index 1, and exact `ManuallyDrop<*const Element>` field type.
3. A pointer cast from that address to `*const *const Element`; the operand
   must be the address from step 2.
4. A `const_ptr::read` call on that exact pointer, returning
   `*const Element`.
5. The read result flows to `_0` and then the sole normal return. Reject extra
   operations, altered operands/types, alternate returns, cleanup/unwind
   edges, and unknown MIR forms.

The original method source bytes, adapter source bytes, adapter MIR and spans,
full helper source/MIR, export/decode/refinement evidence, and mutation records
must be kept as one hosted evidence set. A call count or name-only redirect is
not sufficient. The source check must bind the method's original unsafe
signature and item path as well as its body; the adapter contract and exported
annotations must bind their own spans and exact text. Changes to the source,
field order/privacy, generic type, method identity, or adapter/callsite MIR
reject applicability before the proof runs.

## Existing rules and the exact permission question

The current pointer profile defines `MaybeUninit_pointer_own<Element>` over
the **value** `MaybeUninit<*const Element>`; its initialized case contains
`raw_ptr_own<Element>(t, p)`. It deliberately carries no memory permission
for `Element` at `p`. Existing `open_MaybeUninit<T>` in `std/lib.rsspec`
opens an outer wrapper cell into an optional inner cell at the cast address
`self as *T`; it preserves `none` versus `some(value)`.

Rust union-field address translation has a different modeled pointer path.
`&raw const self.value` is represented by
`union_variant_ptr(self, unionTypeId, 1)`. The prelude definition preserves
the address but applies `union_variant_ptr_provenance`; this is a complete
pointer term, not an address-only equality. The Rust verifier does not enable
the C-only `union_variant_ptr_eq_ptr` assumption. The existing union typing
rule relates `has_type` facts but does not transfer heap chunks. The stock
`const_ptr::read` translation lowers to a typed dereference, which requires a
readable cell at the exact pointer term produced by the field-address path.

Therefore the hosted positive must attempt only the existing route:

1. Establish the adapter's local initialized wrapper value and its strict
   `inner(storage) == some(p)` precondition from the caller's selected wrapper.
2. Invoke the existing `open_MaybeUninit` storage operation for the adapter's
   actual local storage pointer, without adding a new union lemma or assuming
   field/cast pointer equality.
3. Execute the pinned address/cast/read chain through ordinary translation.
4. Require `read` to consume the points-to permission at the exact
   `union_variant_ptr`-derived `*const *const Element`, then return that value
   and the existing pointer-value ownership.

If step 2 yields only permission at `self as *T`, while step 4 requires
permission at the differently-provenanced union variant pointer, the resulting
missing-cell failure is the intended resource diagnostic. Do not insert a
points-to chunk at the union pointer in translator code, infer it from equal
numeric addresses, turn the option into an always-initialized value, or add an
axiom/summary that supplies the read resource. Existing generic full-borrow
generation explicitly lacks Rust union support, so it cannot be cited as that
transfer. The experiment must preserve the exact failure so a later boundary
decision has a causal reproducer.

## Contracts and outcome classification

The adapter is Rust-unsafe, matching the source method's safety boundary. Its
proof precondition must include the ordinary thread token, the strict wrapper
initialization fact `MaybeUninit::inner(storage) == some(p)`, and the accepted
pointer-value ownership for `p`. The local body proof must still obtain its
read-cell permission through the existing storage rules; the contract may not
postulate a points-to chunk at the union variant pointer. Its normal post must
preserve the thread token, return the full modeled pointer `p`, and transfer
the pointer-value ownership to the result. `on_unwind_ens false` is allowed
only after the exact pointer specialization proves the `assert_inhabited`
step and the reached operations' no-unwind behavior. No cleanup/unwind edge
may be discarded to obtain this result.

For the *first* hosted run, this is a deliberately partial diagnostic: it
checks source binding, adapter contract compatibility, body execution, and
whether the current storage rules reach the expected read permission. It does
not claim component acceptance if the read permission is missing. The run
must classify outcomes as follows:

| Observation | Classification |
|---|---|
| Source/hash/span/type/MIR admission rejects the adapter or callsite | Applicability failure; repair the gate/fixture, no semantic conclusion. |
| Unsupported operation prevents translation before the typed read is emitted | Frontend/translation inconclusive; add only an exact operation lowering that preserves the pointer term, then rerun. |
| Exact body reaches `read` and fails for missing points-to at the `union_variant_ptr`-derived address | Target resource diagnostic; retain log and expression. This is not yet the final phase stop. |
| Exact body proves, but result, pointer ownership, token, frame, or no-unwind post fails | Proof failure at that named obligation; fix only within the authorized pointer specialization. |
| Exact body proves all posts using existing checked rules and without injected permissions | Positive evidence that the current model suffices; continue the component acceptance matrix. |

In all outcomes, an uninitialized control must not produce a readable cell or
result. A false return/postcondition control must reach the named post proof.
An independent caller resource must remain framed, and duplicated resource
controls must fail at their intended ownership check. For any negative, retain
its exact expected predicate/location and verify that it reaches that target;
gate rejection is not a proof negative.

## Source/MIR and mutation controls

Once the base diagnostic reaches the body proof, the admission matrix must
include mutations for: wrong `assert_inhabited` type; wrong union identity,
field index or field type; replacing/removing the raw address; wrong cast
source/target or const/mutability; wrong read operand/result; returning a
different local; extra call/assignment/drop; changed normal or unwind graph;
changed source body/signature/field declaration; and altered actual helper
call binding. Each admission mutation must reject before the semantic read
proof. Separate proof mutations preserve the admitted source/MIR while adding
an incorrect result, false postcondition, false assertion, duplicated or lost
resource, or `inner == none`; these must reach the corresponding verifier
obligation. Keep source-integrity, exporter/decode/refinement, and SAFE/unsafe
contract checks active for every admitted control.

The positive state matrix includes the actual `some(p)` result from the
selected wrapper and symbolic pointer provenance, including null or otherwise
unconstrained raw-pointer values where the model permits them. It must not add
a condition on the pointee. The `none` case is expected to fail before
extraction. `Element: Copy` is not introduced; the only copied/read value is
the raw pointer type itself, exactly as the pinned body specifies.

## Narrow translator implementation that exposes, but does not solve, the read

If existing translation cannot expose the intended obligation, the proposed
first code change is limited to these gates/lowerings in the experimental
translator profile:

* Extend the existing certified-local-MaybeUninit applicability gate to admit
  exactly the source-linked assume-init adapter, without enabling arbitrary
  union translation or changing other specializations.
* Preserve union field-address identity as
  `union_variant_ptr(base, MaybeUninitTypeId, 1)` through MIR-to-AST lowering.
  Do not rewrite it to `base`, `self as *T`, or an integer/address expression.
* Add the missing `*const T` pointer cast dispatch only for the exact typed
  `ptr.cast` operation found in this adapter. The lowering must retain the
  complete operand pointer term; it changes pointee type only.
* Keep the existing `const_ptr::read` lowering to a dereference, so VeriFast
  itself checks the exact cell permission. Do not replace the read with
  `MaybeUninit::inner`, an extraction summary, or a direct result expression.
* Add a raw-pointer-only, exact-type `assert_inhabited` rule if the pinned
  compiler intrinsic is otherwise unsupported. Its documented obligation is
  only that `*const Element` is inhabited and the intrinsic has no unwind;
  it gives no storage permission and says nothing about `Element`.

These are applicability/operation-translation changes, not a resolution of the
resource gap. In particular, no translator branch may manufacture
`*union_variant_ptr(...) |-> p` from `inner == some(p)`.

## Diagnostic fallback if the full source adapter cannot be exported

If exporter limitations prevent the adapter body from reaching VeriFast, use a
separate minimal ghost-only diagnostic in a hosted fixture. Its precondition
supplies an ordinary initialized `MaybeUninit<*const Element>` storage cell
and `inner == some(p)`. It invokes only the existing `open_MaybeUninit`
operation, then asks for the exact readable cell at the Rust
`union_variant_ptr(storage, MaybeUninitTypeId, 1)` term. The expected failure
is the missing points-to permission after the open operation. This isolates
the old kernel/specification permission question from adapter parsing and
method-body translation.

This fallback is strictly **diagnostic**, not proof of the actual method,
source-link evidence, or component acceptance. It must not assume the desired
union-field points-to chunk, use C-only union rules, or substitute pointer
address equality. Preserve the failed obligation and return to the
source-linked adapter as soon as exporter support permits. A passing ghost
fixture alone cannot establish the body or the actual helper call.

## Decision boundary after the diagnostic

Do not stop on an unsupported function name or on source/MIR-gate rejection.
First make the exact adapter and MIR check reach the typed read obligation.
If the ordinary read then fails because the model cannot relate the existing
MaybeUninit storage resource to the full-provenance union variant location,
record the exact term, required permission, available permission, source hash,
profile, run URL and artifact. A follow-up design must determine whether an
ordinary checked lemma can derive that permission from existing storage and
layout predicates. If no such checked derivation exists and progress requires
translator-created permission, an unverified resource bridge, or a general
union/provenance/memory change, that is the point to stop and request a
separate semantic decision. This diagnostic does not make that decision in
advance.

The phase remains pointer-specialized and does not include general union
support, aliasing/borrowing changes, arbitrary copy, `FnMut`, arbitrary `Drop`,
or full `sort4`. The accepted constructor/as_mut_ptr profiles remain
regressions only; all controls for this new rule must execute with its exact
gate active. No runtime std source or signature is changed.
