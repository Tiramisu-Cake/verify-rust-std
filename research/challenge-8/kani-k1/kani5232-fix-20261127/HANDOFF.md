# Kani 5232 fix handoff

The candidate is local at `/root/kani-5232-fix-w14` on `fix/bool-ordering-comparison`. It is one commit above the fetched upstream `main`. The handoff goes on the current g0 branch tip, which advanced after the task was assigned.

| Identity | SHA |
| --- | --- |
| Commit | `ce44753241dbb7df05ed72a245a7a92aff0def06` |
| Tree | `7a2cf02954d4b8c91db908c8c433b528dbd58f5c` |
| Parent | `8c6dba5935e8b37a905145c57572d1b67489bae2` |

Author and committer are `Tiramisu-Cake <igkharin@gmail.com>`.

## Diff summary

- `rvalue.rs` casts both `c_bool` operands to unsigned 8-bit values for `Lt`, `Le`, `Gt`, `Ge`, and `Cmp`. This preserves the ordering of the valid Rust `bool` values `0` and `1` and uses the same type as the issue's explicit `u8` control. The cast is scoped to ordering operations. [Issue 5232](https://github.com/model-checking/kani/issues/5232)
- `utils.rs` provides the `cast_bool_for_ordering` helper used by MIR comparison lowering.
- `tests/kani/Bool-BoolOperators/ordering.rs` retains both issue harnesses and adds truth-table assertions for `<=`, `>`, `>=`, `Ord::cmp`, `min`, and `max`. The separate expected-output test checks `SATISFIED` for `a < b` and `UNSATISFIABLE` for `a < b && b < a`. I used the expected suite because the ordinary Kani suite checks the exit code, which can be successful with either cover status.

## Relational codegen audit

- `rvalue.rs` routes scalar ordering and `Cmp` through `comparison_expr`. Its fat-pointer callers order data pointers and slice lengths. The other direct comparisons use integer shift distances, integer discriminants, or float-cast bounds. The MIR generators for validity and automatic niche checks already compare unsigned values.
- The pinned rustc lowers `three_way_compare` to MIR `BinOp::Cmp` before Kani codegen. The intrinsic documents integer and character operands, so the regression uses the supported `Ord::cmp` API for `bool`. On this toolchain, `bool::cmp` subtracts two `i8` casts and Boolean `min` and `max` use bitwise operations. These assertions cover the library behavior while the relational truth tables exercise the reported defect. [Rust intrinsic lowering](https://github.com/rust-lang/rust/blob/137d1d49458b73b7b85d2c1599d8730886d65e47/compiler/rustc_mir_transform/src/lower_intrinsics.rs#L117-L153) · [Intrinsic contract](https://github.com/rust-lang/rust/blob/137d1d49458b73b7b85d2c1599d8730886d65e47/library/core/src/intrinsics/mod.rs#L1923-L1933) · [Boolean `Ord` implementation](https://github.com/rust-lang/rust/blob/137d1d49458b73b7b85d2c1599d8730886d65e47/library/core/src/cmp.rs#L2357-L2386)
- The `SliceValidityAssume` hook compares raw unsigned bytes and `usize` indices. The experimental `forall!` and `exists!` range hook in `hooks.rs` remains a known direct emitter of `c_bool` relations when the typed macro arms receive `bool` bounds. It is outside this patch's scope because the regression tests exercise scalar ordering and solver support for Boolean quantifier bounds is unverified.
- `intrinsic.rs` uses integer operands for layout, shift and count checks, and pointer operands for swap overlap checks. SIMD ordering uses vector operations with numeric lane representations, and SIMD min/max reductions require integral lanes. Atomic min/max reaches the binding-level `Expr::min` and `Expr::max` helpers through signed and unsigned integer intrinsics. I kept out-of-contract raw atomic `bool` instantiations outside this fix. [Rust atomic intrinsic type checks](https://github.com/rust-lang/rust/blob/137d1d49458b73b7b85d2c1599d8730886d65e47/compiler/rustc_codegen_ssa/src/mir/intrinsic.rs#L463-L509)
- The binding sign helpers are used for numeric shift distances and arithmetic. The IREP conversion serializes the relational operators it receives. The LLBC path emits Charon operations without CBMC types.

## Validation

`git diff --check` against the parent and `kani-fmt-check.sh` on the final commit passed. Compilation and proof execution are pending coordinator fork CI.

## Draft PR

**Fix ordering comparisons on symbolic booleans**

Cast Boolean ordering operands to `u8` before emitting comparisons so CBMC can encode `false < true`. Add a regression for the ordering truth tables and cover outcomes.

Resolves #5232

Testing: [pending fork CI]

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
