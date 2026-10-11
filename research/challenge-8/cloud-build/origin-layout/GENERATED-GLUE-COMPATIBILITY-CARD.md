# B1 official-refiner compatibility controls

The Cloud-only runner `generated-glue-compatibility-controls.py` replays the
exact original/verified MIR exported during the official-refiner capture in the
same admission campaign. It uses a copied, SHA-checked official refiner and
argv-checked exporter shim. Raw and re-encoded positive baselines must pass.
Mutations affect only copied decoded messages; source files and proof posts
stay unchanged.

The selected ordinary `Drop::drop` body supplies the unit-return control. Both
exports have their final `_0 = ()` MIR assignment removed while retaining the
Return terminator. The expected exact refiner diagnostic is `Return local has no
value in the refinement environment`. The non-unit variant also changes both
the output and `_0` local type to `u64` and expects the same refusal. A
one-sided ordinary unit removal expects the earlier missing-value refusal;
it is **not** a generated `Some`/`None` return-comparison gate.

For a generated one-sided populated return, redirecting the verified glue call
destination from `_3` to `_0` must fail the generated shape gate before Return.
The official refiner requires exactly `_3` as destination, an empty return
block, and original/verified generated MIR equality. Therefore this control
records `PRE_RETURN_GENERATED_SHAPE_GATE` and grants no Return-comparison credit.
The intended `Some`/`None` comparison is unreachable under the current exact
generated admission shape; this is a qualification limit, not a reason to
change refiner semantics or weaken an existing gate.

The ordinary default-off control runs a tiny unannotated Rust `Drop` fixture
under Cloud with `SMALLSORT_ACTUAL_GLUE_BODY` absent. Its exporter/decode
receipt must show a real ordinary `Drop` terminator, no generated body and no
generated body key. The pinned verifier's dumped AST must contain an
`std::ptr::drop_in_place` call in `ordinary_drop`, with no generated call or
receiver rewrite there. A verifier proof failure on the unspecced fixture does
not supply proof credit; the intended observation is its frontend route.

A separate static source gate binds the exact tool refiner source SHA and built
refiner SHA and requires exactly two old synthetic `Drop` records, both with
explicit empty selected path/hash/guard and generated key plus false bare-local
and replace flags. This is source compatibility evidence only. The aggregate
may match when all executable gates reach their intended classifier; it never
claims a direct generated `Some`/`None` Return comparison.
