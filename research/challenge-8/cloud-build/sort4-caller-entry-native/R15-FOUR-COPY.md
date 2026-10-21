# R15 four-copy resource component

`a1-actual-four-copy.rs` adds a generic identity-route resource fixture around
four explicit `ptr::copy_nonoverlapping` calls. The source is represented by
`src[..4] |-> values` and one `foreach(values, own::<T>(t))`; the destination
starts as four optional uninitialized cells and ends as the initialized raw
representation `dst[..4] |-> values`. The source owner is kept once, and all
four primitive calls have `on_unwind_ens false`.

The fixture uses the stock `array_split` / `array_join` operations to expose
each slot and checked source and optional-destination interior-pointer lemmas
to derive bounds from their respective four-element array invariants. It does
not claim that the actual sort4 indices are the identity route, prove a
permutation, bind any pointer to `sort4_stable`, or establish callback and
unwind behavior for that function. It is a representation-copy component
only. The duplicate-owner negative repeats the primitive body and asks for a
second `foreach(..., own::<T>(t))` in its normal postcondition, without relying
on another fixture case's summary.

No compiler, verifier, extraction, or build was run for this addition. The
fixture still needs its authorized runner check; pointer arithmetic,
destination `array_` splitting, and list reconstruction remain unconfirmed.
The model's ZST address/slot geometry is also open and receives no credit here.
