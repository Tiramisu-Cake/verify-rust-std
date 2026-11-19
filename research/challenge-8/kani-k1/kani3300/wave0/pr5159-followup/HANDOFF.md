# HANDOFF — offline follow-up to Kani #5159

Status: requested single preparation stage complete; STOP WITH HANDOFF. No push, PR mutation, CI dispatch, compiler invocation, or verification run is authorized by this handoff.

## Exact candidate

- Worktree: `/root/kani-5159-followup-w11`.
- Branch: `fix/volatile-zst-test-followup`.
- Base fetched from `https://github.com/model-checking/kani.git refs/pull/5159/head`: `d0ba1c2cb381965c215f4cb7b2e32d028ee7e088` (matches the requested head).
- Follow-up commit: `a197a690e44c5e997f967757ab9f86a55ee6b0f7`.
- Commit subject: `Exercise local ZST volatile reads and simplify load diagnostics`.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`; no skip-CI marker or Co-Authored-By trailer.
- Exactly one commit above the base; two source files changed, 14 insertions and 9 deletions. Candidate worktree clean after commit.
- Protected PR #5159 and `Tiramisu-Cake:fix/volatile-zst-5072` were not modified. Fetch and review/issue reads were the only GitHub operations. No local checkout or write to the protected branch.

## Review and reproducer checked

Read `gh api repos/model-checking/kani/pulls/5159/reviews`. Maintainer `feliperodri` submitted [APPROVED review 5981054730](https://github.com/model-checking/kani/pull/5159#pullrequestreview-5981054730) at `2026-11-19T18:37:26Z`, for base `d0ba1c2cb381965c215f4cb7b2e32d028ee7e088`.

The review says `&()` is promoted to a static and the original harness also passes on main. It requests the issue's local form and optionally a helper/constant extraction. Its reported main-versus-PR verification results are maintainer-reported evidence, not independently rerun here.

Read [issue #5072](https://github.com/model-checking/kani/issues/5072) through the GitHub connector. Its failing harness is:

```rust
let x = ();
unsafe { core::ptr::read_volatile(&x) };
```

The issue reports four dereference failures (NULL, invalid pointer, outside object bounds, invalid integer address), while the matching `ptr::read` harness succeeds. These are issue-reported results; no local or remote rerun was performed for this task.

## Why the replacement exercises the fixed path

Static source trace at base `d0ba1c2cb381965c215f4cb7b2e32d028ee7e088`:

1. `codegen/rvalue.rs:788` handles `Rvalue::Ref` through `codegen_place_ref_stable`. `codegen/place.rs:385` represents an ordinary local by a symbol; `is_zst_object` at line 670 recognizes a zero-sized symbol.
2. `codegen/place.rs:684` / lines 702–730 model a reference to that ZST local using a nondeterministic numeric address, constrained nonzero and properly aligned, then cast to a pointer. There need not be an allocated memory object behind it. This is the relevant local-reference path avoided by the promoted-literal harness.
3. `src/intrinsics.rs:496` maps `volatile_load` to `Intrinsic::VolatileLoad`; `codegen/intrinsic.rs:735` routes it to `codegen_volatile_load`.
4. In the pre-fix main snapshot `0997d11c14cb2da0824efc34e2c4001e53ac0faf` (the main-side parent of the requested PR head), `codegen/intrinsic.rs:1902` / line 1918 unconditionally execute `let expr = src.dereference();` after checking alignment. Thus the local ZST pointer can encounter precisely the invalid memory checks reported in #5072. `codegen/statement.rs:1152` emits the expression as a statement even for a unit destination; discarding the unit value does not remove this lowering step.
5. At the requested PR head, `codegen/intrinsic.rs:1931–1945` instead recognizes the inhabited ZST and builds `Expr::init_unit` without dereferencing the source. Alignment and uninhabited-value checks remain. The follow-up leaves this path unchanged, apart from substituting the identical diagnostic constant.

All compiler paths above are relative to `kani-compiler/`; `codegen/` abbreviates `src/codegen_cprover_gotoc/codegen/`. Coordinates in this trace refer to the base unless the pre-fix snapshot is explicitly named. The pre-fix failure conclusion is supported by the source trace, the exact local-borrow reproducer, and the maintainer's reported comparison; it is not a new measured verification result or independent proof credit.

## Changes and complete harness audit

`tests/kani/Intrinsics/Volatile/load_zst.rs:15` now declares `let x = ();` and calls `ptr::read_volatile(&x)`, retaining the unit assertion. A short comment explains why the local matters.

| Harness | Pointer supplied to the load | Promotion finding |
| --- | --- | --- |
| `read_volatile_unit_reference` | `&x`, with local `let x = ();` | Fixed; no literal temporary borrow |
| `read_volatile_dangling_unit` | `NonNull::<()>::dangling().as_ptr()` | No literal borrow |
| `read_volatile_overaligned_zst` | `NonNull::<Z>::dangling().as_ptr()` | No literal borrow |
| `read_volatile_null_zsts` | `ptr::null::<()>()` and `ptr::null::<Z>()` | No literal borrow |
| `intrinsic_volatile_load_zsts` | Dangling `Z` pointer and null unit pointer | No literal borrow |
| `read_volatile_aggregate_zsts` | Dangling aggregate pointer | No literal borrow |

Expected values in assertions, including `()`, `Z`, `[Z, Z]`, and `[]`, are not load-source pointers. The other five harnesses are byte-for-byte unchanged.

Optional cleanup included in `codegen/intrinsic.rs`: private `returns_uninhabited_zst(&self, instance: Instance)` contains exactly the former guard body, retaining the same output-type query and short-circuit order. `VOLATILE_LOAD_UNINHABITED` stores the identical diagnostic bytes for the two existing sites. Property classes, spans/locations, target/no-target dispatch, alignment, ZST handling, non-ZST dereferencing, and control flow are unchanged.

## Validation and limits

- `git diff --check` passed before commit and for `HEAD^..HEAD` after commit.
- An ad hoc Python static check inlined the helper and constant, then compared Rust token streams with the exact base: identical. Both former message occurrences resolve to the original bytes.
- The same check confirmed the entire test file equals the base with only the intended harness replacement; all six harnesses were audited and no load argument directly borrows a literal tuple.
- Inspected the pre-fix main snapshot's unconditional dereference and the fixed source path above.
- Confirmed one follow-up commit, exact parent, author/committer, commit message, and clean candidate worktree.
- Cargo, rustc, rustfmt, Kani, CBMC, builds, native tests, verification, push, CI, and PR writes: NOT RUN. No runtime or proof acceptance is claimed.

## PR draft and next authorized stage

Title: **Use a local unit value in the volatile ZST regression test**

Body: [PR-BODY.md](PR-BODY.md), with two descriptive sentences referencing #5159 review and #5072, a Testing placeholder, license declaration, and the requested AI disclosure.

After #5159 merges, a separately authorized stage should rebase this single follow-up commit onto the then-current main, check that the main version contains #5159's fix, and record the new base/candidate SHAs. Before publication, validate the local-reference harness against fixed and pre-fix code through an authorized test lane, run the relevant Volatile and uninhabited/alignment expected regressions and required checks, and replace the Testing placeholder with actual results. This handoff does not authorize those actions or change the existing PR's auto-merge setting.

The documentation commit containing this file and PR-BODY.md uses `[skip ci]`; its resulting SHA is reported separately because a commit cannot contain its own SHA.
