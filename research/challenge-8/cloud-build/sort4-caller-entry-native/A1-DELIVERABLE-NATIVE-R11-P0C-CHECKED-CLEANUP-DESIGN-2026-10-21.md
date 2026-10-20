# R11 P0c observer cleanup: checked-route design and applicability boundary

## Finding

R10's bounded P0c observation identifies a resource leak in the generated
diagnostic body `a1_guard_observer` at `verified/lib.rs:139`: the verifier still
owns `Option_own(...)(_t, left_ancestor_pivot)` when the body returns. This is a
generated-observer proof failure, not evidence that the actual stable quicksort
has a runtime heap leak.

The fixture builder's `_observer` in `a1-fixtures.py` (around lines 245–259)
keeps the actual quicksort signature and guard prefix and appends the diagnostic
assertions and early return. The parameter is the actual, arbitrary
`mut left_ancestor_pivot: Option<&T>` from
`library/core/src/slice/sort/stable/quicksort.rs`. Before the generated return,
the prefix has not reached the later assignment `left_ancestor_pivot = None`
at source line 72. Neither the source nor the current proof establishes that the
parameter is `None`; both `None` and `Some(&T)` remain in scope.

## Minimal checked cleanup candidate

The smallest checked ghost candidate is variant-aware elimination of the
existing `Option_own` chunk: open it using the symbolic parameter value, then
match `None` and `Some(r)` so the `Some` field is handled only on that branch.
The pinned VeriFast source audit recorded in the R10 backlog says
`rust_parser.ml::own_pred_decls_for_enum` (995–1019) generates enum ownership
from the fields: `None` contributes `Emp`; `Some(r)` exposes the field's
`<&T>.own`. This preserves arbitrary input and is sound as an unfold/match step;
it does not itself dispose of the `Some` field permission.

Two existing checked directions must be considered for that field. First,
`std::mem::drop<T>` in the pinned `lib.rsspec` (R10 source lines 414–416)
requires `thread_token(t) &*& <T>.own(t, value)` and returns the thread token
on normal and unwind exits. A call on the `Some` field may consume that field,
but the caller still must prove that its Option local was moved or otherwise
discharged. Second, `end_ref_Option_None/Some` in the same source (1536–1542)
is variant-aware, but the R10 audit identifies its interface as operating on a
reference place/end token; it is not directly the contract for a by-value
Option parameter.

This route is **not established** for the current candidate. `Option<&T>` is
`Copy`, so Rust evaluates a by-value use as a copy and leaves the original
local available. A checked callee contract consuming ownership of the copied
argument alone does not show that the caller's original `Option_own` is
discharged. The R10 profile pins selected base `lib.rsspec` SHA
`d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf` and the
proof source `library/core/src/mem/mod.rs` SHA
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`; R11's
effective Cloud reconstruction is not available in this worktree. R10's
source-only audit explicitly leaves the Copy-lowering and effective-overlay
compatibility questions open.

The project proof source illustrates both the positive construction and the
missing end condition. In
`verifast-proofs/alloc/collections/linked_list.rs/verified/linked_list.rs:2798–2801`,
`Iter::next` obtains reference share permission, calls `close_ref_own`, then
closes `Option_own(Some(elem_ref))` to return the option. It returns the
reference permission rather than discarding it. Its `end_ref_Option_NonNull`
lemma at lines 632–645 requires `ref_initialized`, an
`ref_end_token_Option_NonNull`, and a fractional points-to chunk for the
referenced Option place; on `Some`, it invokes `std::option::end_ref_Option_Some`
and `std::ptr::end_ref_NonNull`. Those place/token resources are not established
for the by-value `left_ancestor_pivot` local. Applying this lemma by analogy
would be unsound until its exact precondition is proved from the active caller
and lifetime.

Assigning `None` is a separate falsifiable lowering candidate, not an assumed
cleanup: it must consume the old arbitrary variant's resource exactly once and
must not synthesize an end-of-lifetime token for a still-live caller reference.
Matching the value establishes which field exists but likewise does not consume
that field. For `Some(&T)`, any `end_ref` use must prove the exact borrow
origin, lifetime-dead/end token, and restoration behavior; merely opening or
dropping the field cannot stand in for those facts.

## Decision and controls

The selected first Cloud hypothesis is the explicit existing checked contract
call `core::mem::drop(left_ancestor_pivot)` immediately before both P0c
observer returns. It preserves the arbitrary parameter and source guard. The
same call is placed only in the P1 caller's separately labeled synthetic tail,
after the exact source prefix, so the P1 body can reveal whether its diagnostic
cut has the same cleanup requirement. No source quicksort return is rewritten.
The exact question is whether the active Copy/MIR lowering and effective
`proof_std` let that call consume the observer's local `Option_own` without
leaving or duplicating it. A verifier failure there means P0c remains open and
proof credit stays zero; it does not establish a runtime leak. No ghost
unfold/match is included in this candidate, so its result will not be confused
with a separate variant-aware model experiment.

The R10 `a1-tool.py` reconstruction statically checks the selected baseline's
`critical`, `effective_rsspec`, `proof_std`, and modified-file maps before
building, and checks that effective spec/source identity is unchanged after
each overlay (around lines 290–301 and 459–485). That supports a fail-closed
Cloud identity check, but cannot establish R11's final maps locally because
the pinned tool source commit is not present in this worktree. Do not widen
scope to alter the active model or runtime std to make the diagnostic pass.

The implementation changes only generated diagnostic tails in
`a1-fixtures.py`: the P0c and N-false31 observers each call checked `drop` at
both early returns; the P1 source prefix is byte-for-byte retained and the
candidate call appears only after a labeled diagnostic-cut comment. Two small
import-inert synthetic tests check generated source shape, both observer
variants/returns, exact source-prefix preservation, and the P1 tail boundary.
They pass locally. These tests establish generation only; Cloud must verify the
Copy/MIR contract correspondence, None and Some behavior, and all required
posts/receipts. No proof credit or profile acceptance follows from the static
and synthetic results. The distinguishing controls must preserve arbitrary
inputs and reject:

- `None`-only behavior masquerading as the general observer proof;
- a `Some(&T)` path that leaks or duplicates the reference ownership;
- cleanup that consumes the caller's unrelated resources or changes the
  comparator/guard obligations;
- missing or altered `drop`/end-ref contract, wrong owner, or unsupported
  lowering, without treating setup failure as an intended negative.

Static review establishes source applicability and the `Copy` concern only. It
provides no verifier result, exact-pair receipt, proof credit, or acceptance of
the experimental profile.
