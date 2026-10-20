# R9 prefix Unsize bridge investigation

This is a source-only design note. It does not establish parser-input identity,
successful verification, or proof credit. The retained R8 obligation report
keeps the prefix open because the compiler's `PointerCoercion` subtype is lost,
and the mutable `[u64; 3]` to mutable `[u64]` coercion needs both a length-3
metadata bridge and a checked borrow/lifetime binding.

## Existing path and narrow admission point

The exporter currently maps every `mir::CastKind::PointerCoercion { .. }` to
the same unit `CastKind.pointerCoercion` at
[`lib.rs`](</root/verifast-merge-actual-glue/src/rust_frontend/vf_mir_exporter/src/lib.rs:2721>).
The schema therefore has no `Unsize` discriminator
([`vf_mir.capnp`](</root/verifast-merge-actual-glue/src/rust_frontend/vf_mir/vf_mir.capnp:598>)).
The translator prints that generic tag and lowers all cast kinds through the
ordinary typed `CastExpr` path at
[`vf_mir_translator.ml`](</root/verifast-merge-actual-glue/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:3983>).

The narrow interception point is the `Assign` case in
`translate_statement_kind`, before generic `translate_rvalue` lowering. The
statement translator retains both the MIR statement span and translated source
span; admission should bind the **original** MIR span (`mir_loc`) as well as
the body identity, not the narrowed AST location used to place ghost commands.
The concrete source/MIR shape recorded by prior diagnosis is `b2_three_from_local`,
`lhs _4 = move _5`, no projections, with `_5 : &'erased mut [u64; 3]` and
`_4 : &'erased mut [u64]`.

Keep ordinary `PointerCoercion` handling rejected. Add a supplemental schema
field for the pointer-coercion subtype (rather than changing the existing
generic Rocq `CastKind` constructor), and have the pinned exporter populate it
only for the compiler's actual `Unsize` variant. Before writing the Rust match,
inspect the enum definition from pinned `nightly-2026-09-25`; do not guess its
field/pattern spelling. The translator may take the special route only when all
of these hold:

- subtype is exactly `Unsize`; source and target are mutable references to
  `[u64; 3]` and `[u64]`, respectively, with the same explicitly bound
  non-static lifetime;
- body is the exact `b2_three_from_local` MIR body under its pinned body hash,
  MIR fingerprint/phase and source identity; statement span is the bound
  coercion span;
- assignment is exactly the bare `_4` destination from `Move(_5)`, with no
  source or destination projections, no other cast/operand form, and the
  decoded local declarations agree with both cast types;
- the explicit lifetime binder encloses the live source local from its
  `StorageLive` through the coercion and is ended on every normal and unwind
  return. The binder only names the checked borrow; it cannot create a token,
  owner, reference fraction or source permission.

All failed checks should take the existing unsupported-cast error path. Do not
match only by source/target type, line number, or erased lifetime; those do not
recover the erased compiler subtype or bind the compiler assignment.

## Resource bridge candidate and current limit

There is a promising existing-model conversion, but its applicability to this
actual mutable borrow must be proved before implementation:

1. `Array_to_array::<u64, 3>(p)` in
   [`prelude_core.rsspec`](</root/verifast-merge-actual-glue/bin/rust/prelude_core.rsspec:337>)
   converts the existing array object's `points_to` permission into the
   three-element slice-range points-to view. The existing
   `int_of_const_of_int` fact can discharge the type-level length `3`.
2. Fold the existing `array::<u64>(p, 3, values)` representation and
   `foreach(values, own::<u64>(t))` required by
   `slice_full_borrow_content` (same file, lines 467–469). For `u64`, the
   translator's `own` interpretation is `true`; it still must be produced by
   checked commands, not assumed.
3. Construct/bind the fat-pointer representation through the existing
   `slice_from_raw_parts_mut(data, 3)` specification in
   [`std/lib.rsspec`](</root/verifast-merge-actual-glue/bin/rust/std/lib.rsspec:642>):
   it establishes `result as *u64 == data` and `result.len() == 3`. Use those
   equalities to connect the array data pointer and metadata. Numeric address
   equality alone grants no ownership or reference authority.
4. Use the existing mutable-reference `full_borrow` representation with that
   exact slice full-borrow content and the already established source
   lifetime. Return the same lifetime token/fraction and all source array
   resources on both exits; preserve the wrapper's CURRENT and comparator
   posts.

There is a real gap to resolve here: `translate_array_ty` currently reports
that array full-borrow content is unsupported, and `translate_slice_ty` reports
that slice full-borrow content is unsupported; only `slice_ref_ty_info` has
the specialized `pointee_fbc` expansion. The raw slice constructor supplies
pointer metadata but explicitly does not authorize creation of a mutable
reference. Thus the existing lemmas suggest a checked path from an array
`points_to` owner to slice contents, but this source inspection does **not**
show the necessary end-to-end conversion of the actual `_5` mutable borrow,
its lifetime token and its return obligations. First test this derivation as a
small checked ghost proof using the unmodified prelude and exact live local. If
it cannot be expressed without adding a static-array/slice interpretation or a
new lemma, stop for a separate, explicit model decision; do not hide that gap
inside cast typing or add an assumption.

The bridge must be placed at the exact assignment and scoped to the bound
lifetime. It must preserve the source borrow on normal and unwind paths, with
no residual synthetic lifetime, local slice loan, or missing array owner.
The ordinary cast path stays unchanged for every other cast. No broad
`StaticArrayTypeExpr`/`SliceTypeExpr` interpretation, prelude/model change,
kernel rule, `CURRENT18` matcher change, or profile qualification is proposed
by this note.
