# R10 prefix/caller bridge source investigation

This is a source-only investigation. It does not establish parser-input
identity, successful verification, or proof credit. No compiler, extraction,
proof, or Cloud run was performed for this note.

## Nearest source-bound obligation

The exporter currently erases the pointer-coercion subtype:
`src/rust_frontend/vf_mir_exporter/src/lib.rs`,
`translate_rvalue` (around line 2724) maps every
`mir::CastKind::PointerCoercion { .. }` to the unit
`CastKind.pointerCoercion`. The schema
`src/rust_frontend/vf_mir/vf_mir.capnp` (`CastKind`, lines 598–610) carries no
`Unsize` discriminator.

The narrow translator admission point is
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`:
`translate_statement_kind` handles `Assign` before calling the generic
`translate_rvalue` (around lines 4096–4114). `translate_statement` saves the
original MIR span as `mir_loc`, then may narrow `loc` for generated ghost
statements (lines 4289–4304). A future admission must bind the original
`mir_loc`, exact body identity/hash/phase/fingerprint and source identity,
decoded local declarations, and the exact bare assignment shape. The
diagnosed bridge shape is the `b2_three_from_local` assignment `_4 = move _5`,
with no projections and source/target types `&'erased mut [u64; 3]` and
`&'erased mut [u64]`. Keep all other `PointerCoercion` cases on the existing
unsupported path. This source-binding step is implementable without changing
storage or the Rocq model, but by itself does not implement the cast.

## Resource boundary

The current translator cannot express the required mutable-reference resource
through its existing type interpretations:

- `translate_array_ty` (around lines 1807–1846) returns errors for array
  `own` and `full_bor_content`.
- `translate_slice_ty` (around lines 1848–1879) returns errors for slice
  `own` and `full_bor_content`.
- For mutable references, `translate_ref_ty` builds `own` by invoking the
  pointee full-borrow content (`ptee_fbc`, around lines 1570–1622). The
  `&mut [T]` special case in `slice_ref_ty_info` (around lines 1259–1361)
  also uses `slice_full_borrow_content` for reference ownership, but its
  reference `full_bor_content` callback is unsupported.

Existing helpers do not fill this gap. `Array_to_array<T, N>` in
`bin/rust/prelude_core.rsspec` (around lines 333–340) converts an existing
whole-array `points_to` permission into a slice-range `points_to` permission.
`slice_full_borrow_content` (lines 462–469) requires an array predicate and
element ownership. `slice_from_raw_parts_mut` in `bin/rust/std/lib.rsspec`
(around lines 642–645) establishes data-pointer and length equalities only;
it grants no ownership, mutable-reference authority, or lifetime token.

Therefore source-bound subtype/span admission is a useful verifiable bridge
obligation, but proof-bearing cast lowering is blocked unless the exact live
local already supplies the required checked resources. Do not add a
supplemental `Unsize` tag or special cast route as if that alone closes the
bridge. If the resources cannot be derived with the unchanged prelude and
current interpretations, stop for a separate model decision; this note
proposes no new storage interpretation, Rocq model, lemma, assumption, or
authority.
