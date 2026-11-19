# HANDOFF — independent review of the #5159 follow-up

Verdict: **APPROVE**. No required candidate or PR-draft changes found. This is a source-only review of the exact candidate below, not a verification result or authorization to publish/run CI. Requested single review stage complete; **STOP WITH HANDOFF**.

## Identities and scope

- Candidate worktree: `/root/kani-5159-followup-w11`, branch `fix/volatile-zst-test-followup`, clean before and after review.
- Reviewed commit: `a197a690e44c5e997f967757ab9f86a55ee6b0f7`.
- Its sole parent / #5159 head: `d0ba1c2cb381965c215f4cb7b2e32d028ee7e088`. Read-only GitHub head check matched.
- Pre-fix comparison: `0997d11c14cb2da0824efc34e2c4001e53ac0faf`, the main-side parent of that PR head.
- Package: [preparation HANDOFF](../pr5159-followup/HANDOFF.md) and [PR body](../pr5159-followup/PR-BODY.md); title reviewed from the HANDOFF.
- Independently inspected the actual diff, compiler implementation, pinned rustc sources, [#5072](https://github.com/model-checking/kani/issues/5072), and `gh api repos/model-checking/kani/pulls/5159/reviews`. Maintainer [review 5981054730](https://github.com/model-checking/kani/pull/5159#pullrequestreview-5981054730), by `feliperodri`, is APPROVED at the exact base above.

## 1. Local unit borrow and regression sensitivity

**PASS for the pinned compiler path.** `load_zst.rs:15–18` now uses `let x = (); ptr::read_volatile(&x)`, exactly the local-borrow form in #5072. The surrounding unit assertion does not replace the volatile call with an ordinary read. Its constant expected value is not the source pointer.

The distinction is the address computation, not whether the unit value itself is constant. A unit value can be folded and its unused assignment/storage markers can disappear without turning the borrow of its local place into a promoted allocation. A ZST local does not require real stack storage, either.

To check this beyond the preparation author's explanation, inspected Rust sources for the candidate's `nightly-2026-11-18`. The public dated [distribution manifest](https://static.rust-lang.org/dist/2026-11-18/channel-rust-nightly.toml) identifies rustc `1.102.0-nightly`, commit `59cbdee2e7b3ee50e44b460561c43c9e3023d9f0`:

- [`promote_consts.rs:103`](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_mir_transform/src/promote_consts.rs#L103): the collector explicitly skips `is_user_variable()` locals. They remain `Undefined`; candidate validation requires `TempState::Defined` (lines 201–203, 240–243). Thus the named `x` is excluded from temporary promotion even though its type is zero-sized. `&()` borrows an eligible temporary instead.
- [`gvn.rs:483`](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_mir_transform/src/gvn.rs#L483): a direct local borrow is represented by `AddressBase::Local`; constant evaluation explicitly returns `None` for that base at lines 672–678 ("We have no stack to point to"). Folding a ZST value does not fold its local address into a static pointer.
- [`dataflow_const_prop.rs:427`](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_mir_transform/src/dataflow_const_prop.rs#L427): reference/raw-pointer rvalues produce unknown (`TOP`), rather than an evaluated local address. [`remove_zsts.rs:108`](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/compiler/rustc_mir_transform/src/remove_zsts.rs#L108) replaces ZST-valued operands; the reference/raw pointer itself is pointer-sized, and a borrowed place is not a ZST-valued operand. This pass does not remove the volatile call terminator.
- [`ptr/mod.rs:2157`](https://github.com/rust-lang/rust/blob/59cbdee2e7b3ee50e44b460561c43c9e3023d9f0/library/core/src/ptr/mod.rs#L2157): `read_volatile` checks alignment and calls `intrinsics::volatile_load(src)` without an early ZST return. Kani lowers MIR through its own backend, before LLVM could discard a zero-byte operation.

The checked Rust Git blob IDs are respectively `5be8a1b8523c8485da16d051af986d8c227447fa`, `426d262c1e851e8668f51aa358fd42187ca7d40e`, `4efa985af319530b2d27e4d64444f0c7f6239fb1`, `11d5ad6221d34740e7dd2bb3824eac2d55415dbd`, and `443b518284e87a351f88a692a0f1baa9ed3f9b2f`.

Kani source trace (coordinates at the candidate; paths below `kani-compiler/src/`):

1. `codegen_cprover_gotoc/codegen/rvalue.rs:788` sends `Rvalue::Ref` / `AddressOf` to `codegen_place_ref_stable`. `place.rs:385` represents the ordinary local as a symbol; `place.rs:670` identifies that symbol as a ZST object.
2. `place.rs:702–726` models the ZST reference using a nondeterministic numeric address constrained nonzero and aligned, then casts it to a pointer. These constraints do not establish a readable allocated object. This is the path missed by the promoted-literal version.
3. `intrinsics.rs:496` recognizes `volatile_load`; `codegen_cprover_gotoc/codegen/intrinsic.rs:738` dispatches to `codegen_volatile_load`.
4. The pre-fix file at `0997d11c…`, lines 1902–1920, unconditionally builds `src.dereference()` after alignment checking. `statement.rs:1158–1159` emits a unit result expression as a statement, so ignoring/folding the returned unit does not bypass that dereference lowering.
5. The candidate at `intrinsic.rs:1934–1951` constructs inhabited ZST results with `Expr::init_unit`, retaining alignment and uninhabited checks; only non-ZSTs reach `src.dereference()`.

**Conclusion:** the new harness exercises the changed lowering and is expected to fail with the pre-fix backend. The maintainer independently reports four pre-fix dereference failures for the identical local-borrow reproducer (NULL, invalid pointer, outside object bounds, invalid integer address). Those four measured failures are maintainer/issue evidence, not a run performed by this reviewer. Static inspection establishes regression sensitivity for the inspected pipeline; it is not a language-level promise about all future rustc optimizers, nor a freshly observed MIR/CBMC result for this candidate. No `black_box`, artificial mutation, or additional compiler flag is needed for the reviewed source change.

## 2. Helper, diagnostic, and style

**PASS.** Private `returns_uninhabited_zst(&self, instance: Instance) -> bool` at `intrinsic.rs:110` contains the original output-type query and exactly the original `self.is_zst_stable(ret_ty) && self.layout_of_stable(ret_ty).is_uninhabited()` expression, preserving short-circuit order. It is called only in the original `"volatile_load"` no-target guard. Placement immediately after its caller in the existing `GotocCtx` implementation, snake_case naming, and private visibility fit the surrounding methods.

The private module constant sits after imports, before type declarations, and uses normal SCREAMING_SNAKE_CASE naming. Its exact value is `volatile load of an uninhabited type has undefined behavior`. Both original diagnostic sites now use it: no-target fatal error at lines 96–100 and target-bearing assertion at lines 1938–1942. The latter correctly keeps its existing pointee-type test; it does not need the return-type helper. Property classes, spans/locations, alignment checks, dispatch, and control flow are unchanged.

An independent static check reversed only the helper/constant extraction and recovered the entire base compiler file modulo whitespace. It also confirmed exactly two diagnostic use sites and one helper call. No behavioral difference found. Source formatting is consistent by inspection with the repository's `rustfmt.toml`; rustfmt was not executed.

## 3. Remaining harnesses

**PASS.** All five other harnesses are byte-for-byte unchanged. None gets its source pointer from a borrowed literal or temporary:

| Harness | Load-source pointer | Finding |
| --- | --- | --- |
| `read_volatile_dangling_unit` | `NonNull::<()>::dangling().as_ptr()` | Integer/dangling address; no promoted allocation |
| `read_volatile_overaligned_zst` | `NonNull::<Z>::dangling().as_ptr()` | Same, with alignment 8 |
| `read_volatile_null_zsts` | `ptr::null::<()>()`, `ptr::null::<Z>()` | Null constants; no allocation |
| `intrinsic_volatile_load_zsts` | Dangling `Z` pointer and null unit pointer | Direct intrinsic still exercises lowering |
| `read_volatile_aggregate_zsts` | `NonNull::<([Z; 2], [u8; 0])>::dangling().as_ptr()` | No borrowed aggregate |

Constant folding these address constructors does not create valid backing storage or remove the intrinsic. `()`, `Z`, `[Z, Z]`, and `[]` used for expected-value assertions are harmless. The independent file comparison confirmed the local-reference harness replacement is the only test-file edit and all six proof harnesses remain.

## 4. PR draft and licensing

**PASS.** The title is focused and the two-sentence body accurately explains both the local-reference regression improvement and optional diagnostic cleanup, with #5159/#5072 context. The Testing TODO truthfully states that tests/CI were not run and is appropriate for this offline preparation stage; actual results must replace it in a separately authorized publication stage. The draft claims no new verification success.

Both changed source files retain the exact existing copyright/SPDX headers. The PR license line matches `.github/PULL_REQUEST_TEMPLATE.md` byte-for-byte, and the requested disclosure occurs exactly once as a standalone line:

```text
By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
```

## Validation and handoff boundary

- `git diff --check` passed for the exact base/candidate diff; independent static equivalence, unchanged-harness, license, and disclosure checks passed.
- No candidate edits, Cargo/rustc/rustfmt/Kani/CBMC execution, Cloud Build, push, CI dispatch, or GitHub writes. #5159 and its auto-merge configuration were untouched.
- No raw CI evidence/logs/archives were accessed. No new runtime, B1/B2, formal-proof, or independent proof credit is claimed.
- Follow-on execution/publication remains a separate stage as described in the preparation HANDOFF. This report does not start it.
- Only this review HANDOFF is to be committed in the documentation worktree, with `[skip ci]` and author/committer `Tiramisu-Cake <igkharin@gmail.com>`. The resulting report commit SHA is returned separately.
