# HANDOFF — reviewed #5159 follow-up ported onto upstream main

Status: requested single coordinator stage complete; **STOP WITH HANDOFF**. Source-only port and static validation passed. No compiler, native test, verification, push, or CI execution was performed.

## Exact identities

- Upstream fetch: `git fetch --no-tags https://github.com/model-checking/kani.git refs/heads/main`.
- Exact fetched main / new candidate's sole parent: `fca73e13186782e62d286ef89c43d2fcc4bb3a51`. This is the requested minimum tip itself.
- Merged #5159 squash: `7227d72887ca832460872c4b53f3ed26241d99e0`; confirmed ancestor of fetched main.
- Reviewed follow-up: `a197a690e44c5e997f967757ab9f86a55ee6b0f7`, with parent `d0ba1c2cb381965c215f4cb7b2e32d028ee7e088`, in `/root/kani-5159-followup-w11`.
- Existing independent review: [APPROVE](../pr5159-followup-review/HANDOFF.md), for that exact follow-up.
- New worktree: `/root/kani-5159-followup-main`.
- New branch: `fix/volatile-zst-test-followup-main`.
- New source commit: `73edbdd8aec2608fae63338cc4a9df7a7c792cbb`.
- Exactly one commit above fetched main, created with `git cherry-pick a197a690e44c5e997f967757ab9f86a55ee6b0f7`; no conflict or resolution edits.
- Exact preserved message: `Exercise local ZST volatile reads and simplify load diagnostics`.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`. Original author date preserved: `2026-11-19T22:05:59+03:00`; new committer date: `2026-11-20T01:41:29+03:00`.
- Source commit has no skip-CI marker and no Co-Authored-By trailer. The original follow-up branch/worktree was left unchanged.

## Upstream contents and clean application

Both complete touched files are byte-for-byte identical at the reviewed parent, the #5159 squash, and fetched main. Thus this checks more than the affected code fragments. Git blob identities:

| Path | Reviewed parent = #5159 squash = fetched main | Reviewed follow-up = new follow-up |
| --- | --- | --- |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` | `8c353711e61b42479aa47ba7cbeb77a2da16d07e` | `7f8cc8bcaa8b3fcf7b7b40f2f8c16653edfa3fc0` |
| `tests/kani/Intrinsics/Volatile/load_zst.rs` | `48c976602ee1ee2f22935473499557ca0bdba0be` | `dbf5592b69db9672fad1a004ab0a98d9b065ad7e` |

For each path, `git log --full-history --format=%H 7227d72887ca832460872c4b53f3ed26241d99e0..fca73e13186782e62d286ef89c43d2fcc4bb3a51 -- PATH` returned no commits: there have been no upstream edits since the squash.

Before cherry-picking, `git apply --check` accepted the reviewed full-index binary-capable diff against the clean main worktree. The cherry-pick then completed successfully. No unmerged index entries remain.

## Reviewed and ported diffs

Reviewed (`a197a690^..a197a690`):

```text
 .../src/codegen_cprover_gotoc/codegen/intrinsic.rs    | 19 +++++++++++--------
 tests/kani/Intrinsics/Volatile/load_zst.rs            |  4 +++-
 2 files changed, 14 insertions(+), 9 deletions(-)
```

Ported (`73edbdd8^..73edbdd8`):

```text
 .../src/codegen_cprover_gotoc/codegen/intrinsic.rs    | 19 +++++++++++--------
 tests/kani/Intrinsics/Volatile/load_zst.rs            |  4 +++-
 2 files changed, 14 insertions(+), 9 deletions(-)
```

Python compared the complete bytes produced by `git diff --binary --full-index --no-ext-diff --no-renames COMMIT^ COMMIT` for both commits: **identical**, including hunk offsets. Equality modulo line offsets therefore also passes. SHA-256 of each complete diff:

```text
dd82bf1c34192c2a96f51c96e02c584ee186ba680c042874386250bd3d281a68
```

Both resulting source files were also independently compared byte-for-byte with their reviewed versions. All indentation, spacing, line breaks, and rustfmt-sensitive layout are unchanged. In particular, the constant remains split after `=`, the `volatile_load` match guard remains on one line, and the helper's return expression and local-unit harness retain their reviewed layout. No formatter was invoked.

`git diff --check` passed for both reviewed and new commit ranges. Parent/count, exact changed-path list, branch, author/committer, original author date, full commit-message equality, prohibited-marker absence, empty unmerged index, and clean candidate worktree checks all passed.

## PR draft and boundary

Title: **Use a local unit value in the volatile ZST regression test**

Updated body: [PR-BODY.md](PR-BODY.md). It now refers to merged #5159 and retains a Testing TODO for the later publication stage. License declaration and AI disclosure remain unchanged. The historical preparation and independent review packages were preserved.

No Cargo, rustc, rustfmt, Kani, CBMC, builds, native tests, proof runs, push, CI dispatch, PR mutation, or external messages. No CI evidence/log/archive access. No new runtime, B1/B2, formal-verification, or independent proof credit is claimed. Only Git fetch, local Git operations, static byte/hash checks, and local documentation updates were performed; Git hooks were disabled for worktree creation and cherry-pick to prevent incidental execution.

This HANDOFF and its PR body are committed together in the documentation repository with `[skip ci]`, using `Tiramisu-Cake <igkharin@gmail.com>`. That documentation commit's SHA is reported separately. No publication or testing stage is started by this handoff.
