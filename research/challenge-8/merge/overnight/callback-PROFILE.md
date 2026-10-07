# Callback frontend profile for VeriFast 26.10

This is the proposed M2a frontend profile for the callback typing dependency
described in [CALLBACK-DESIGN.md](CALLBACK-DESIGN.md). It is separate from W1;
the wrapping patch is not included or implied. The diagnostic combined profile
applies the separately pinned W1 patch followed by this patch, checks their
joint path allowlist and keeps the pinned exporter/refiner. A hosted run must
record the new frontend markers. Static applicability does not establish that
the generated program is accepted or that callback resources are proved.

## Exact inputs

- VeriFast source: `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Source patch: `callback.patch`, SHA-256
  `0a006df94f04d6425d70280967d6652bdd33ccb88ead4a44f02a2e36775aaa5e`.
- Source design: `CALLBACK-DESIGN.md`, SHA-256
  `df0d790e284ada2f55a995d3953ac67abc2bcd12cabf7b9d9698a8ac21bf461d`.
- Parser input/output SHA-256:
  `b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622` →
  `8ed673086183323058aac5e0e21399e4532d1e74b97c5d41105827e8643107bd`.
- Translator input/output SHA-256:
  `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445` →
  `697693e05705b56b2410d9db1cde5f4f7afe5849c20394158400520b737df12d`.
- The only modified source paths are
  `src/rust_frontend/vf_mir_translator/rust_parser.ml` and
  `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`.

The patch does not modify the kernel (`src/verifast.ml`, SHA-256
`adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`), the
Rust MIR exporter source (`src/rust_frontend/vf_mir_exporter/src/lib.rs`, SHA-256
`11f1e10bb8e52a4950611f874b1123c11e2c87cbb1378c3f5060992f74425f00`), or any
refinement-checker source (pinned-tree manifest SHA-256
`14e7566e4727855ab762c70d2ae665c2fd6f328fee8223507b357d15614a737c`).

## Change and limits

The pinned local Rust prelude is `bin/rust/prelude.rsspec`, SHA-256
`d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5`; it
declares `std_tuple_2_<T1, T2>(T1, T2)`. For this exact generated nominal
declaration, the parser defines its existing `own` predicate as the separating
conjunction of the thread-owned field predicates for fields `0` and `1`.

The specialization checks the parsed body as well as the name and parameters:
it requires an ordinary tuple body with exactly two fields, `T1` named `0` and
`T2` named `1`, each an instance field, public, nonvolatile, and without an
initializer. A declaration named `std_tuple_2_` with different generic
parameters or any other parsed body shape raises a parser error instead of
receiving the expansion. Other generated tuple arities and generic ADTs retain
their stock opaque ownership behavior. This is a structural expansion of the
generated two-field tuple predicate; it adds no ownership axiom or proof
assumption.

The translator retains only a narrow compiler-origin bound when one function
body's decoded clauses contain both (a) an `FnMut<F, (&'r1 T, &'r2 T)>` trait
clause and (b) `FnOnce::Output` equal to `bool` for the same `F`, shared
reference tuple and `T`, with two distinct bound regions that match the
projection arguments. It records this as an eligible `(F, T)` pair and emits a
`#register_type_projection_equality` only while translating an actual
`std::ops::FnMut::call_mut` whose source substitutions and ghost substitutions
both have the expected three-argument form. The matcher requires identical
source and ghost `F` and `T`, identical shared-reference field types, and equal
nonempty reference lifetimes that also match the method lifetime. An unmatched
call receives no equality registration.

The bound gate reads the typed decoder path: `D.decode_clause` is mapped to the
translator's `decode_clause`, whose input is explicitly `D.clause`; the
`Projection` case carries the decoder's projection record. The `FnMut` clause
must have the canonical source trait name and generic arguments structurally
equal to the decoded projection arguments. The projection must have the
canonical `FnOnce::Output` item name and a decoded `Ty` RHS equal to `Bool`.
This is a static source inspection of the pinned decoder interface and
translator annotations; it has not been compile-checked in this phase.

The translator emits `MERGE_HRTB_BOUND` for recognized source clauses and
`MERGE_HRTB_CALL registered=1|0` for each recognized `FnMut::call_mut` call.
These messages are admission evidence only; they do not change proof outcomes.

The new semantic dependency is limited to this tuple ownership definition and
the bound instantiation rule above. It does not relax safety, callback unwind,
leak, return, or dead-code checks and does not add `Copy`, `Freeze`, purity, or
ownership assumptions. It does not support other outputs, tuple shapes, trait
methods, or substitution forms. Resource recovery, mutation effects, panic
posts, and actual `merge_up` proof obligations remain open for separate hosted
evidence.

Tuple negative admission cases must retain the same `std_tuple_2_` name while
changing one shape element at a time: wrong parameter names/count, wrong field
type, field order, field name, mutability/field kind, visibility, volatility,
initializer, missing field, or extra field. Each must be rejected at parsing;
they must not enter the two-field ownership expansion. Unrelated tuple arities
and other generic struct names remain the stock opaque controls.

## Static review

The patch was generated from a private checkout of the exact pinned commit.
`git apply --check` passed against the read-only baseline checkout, and
`git diff --check` passed in the private working copy. No compilation, parser
execution, verifier, research runner, or executable test was run locally.
