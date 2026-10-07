# Callback frontend profile for VeriFast 26.10

This is the proposed M2a frontend profile for the callback typing dependency
described in [CALLBACK-DESIGN.md](CALLBACK-DESIGN.md). It is separate from W1;
the wrapping patch is not included or implied. A hosted run must apply this
patch alone to the pinned source below, keep the pinned exporter/refiner, and
record the new frontend markers. Static applicability does not establish that
the generated program is accepted or that callback resources are proved.

## Exact inputs

- VeriFast source: `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Source patch: `callback.patch`, SHA-256
  `57cfb07a2a09afe71517ae50c8b5443d51b4201fbcd42053215c7198f2fd5975`.
- Source design: `CALLBACK-DESIGN.md`, SHA-256
  `df0d790e284ada2f55a995d3953ac67abc2bcd12cabf7b9d9698a8ac21bf461d`.
- Parser input/output SHA-256:
  `b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622` →
  `0b3269978355161e48cdf4e7b705a43e57239ead163806c16f33aaa6bf4e3dac`.
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

For the exact generated nominal `std_tuple_2_<T1, T2>` declaration, the parser
defines its existing `own` predicate as the separating conjunction of the
thread-owned field predicates for fields `0` and `1`. The parser's other
generated tuple arities and other generic ADTs retain their existing opaque
ownership behavior. This is a structural expansion of the generated two-field
tuple predicate; it adds no ownership axiom or proof assumption.

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

## Static review

The patch was generated from a private checkout of the exact pinned commit.
`git apply --check` passed against the read-only baseline checkout, and
`git diff --check` passed in the private working copy. No compilation, parser
execution, verifier, research runner, or executable test was run locally.
