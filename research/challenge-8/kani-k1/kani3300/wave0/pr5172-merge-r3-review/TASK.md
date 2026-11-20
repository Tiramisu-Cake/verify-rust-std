# TASK — independent review of the #5172 re-merge with main (2026-11-20)

One stage. Read-only on Kani code: do not edit, commit, push, run cargo/rustc/Kani/CBMC, or post anything. Write only `HANDOFF.md` in this directory, then stop.

## Inputs
- Worktree: `/root/kani-pr5172-copilot-w15`, branch `fix/pr5172-merge-main-20261120`, HEAD `88fec3b3979bc409ed714e992c66d30ad6ee9e58`.
- Merge parents: `7e53bc6539` (our tested #5172 candidate) and upstream main `0601bc57f00a5b7f4d8fb4dd76acd6ec9355227a`.
- The only textual conflict was in `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` (main side from #5184, recursive-call check with `active_calls`).
- Coordinator's resolution: imports `use rustc_span::Spanned;` + `use std::cell::RefCell;` (dropped `DUMMY_SP`, unused on our side); in the regular-call branch: main's `active_calls` recursion check first, then our `let Some(body) = body else { return };`, then `apply_regular_call_effect(state, instance, body, args, destination)`.
- Fork CI is already running on this head (Kani CI 44756041900); you do not need to watch it.

## Check
1. Reproduce the merge yourself in a scratch way that does not touch the worktree (for example `git merge-tree --write-tree 7e53bc6539 0601bc57f0`) and compare the conflict hunks with HEAD.
2. Is the resolution semantically right? In particular: ordering of the recursion check vs the body guard; whether `body == None` (intrinsics/foreign items) could ever bypass a needed recursion error; `active_calls` push/pop still balanced with our body-passing `apply_regular_call_effect`; no leftover unused import or dead code.
3. Auto-merged files (`uninit_visitor.rs`, `ptr_uninit/mod.rs`, `check_uninit/mod.rs`, delayed_ub files): any semantic clash between #5183/#5184/#5195 on main and our `resolve_call` / `try_resolve_instance` / shim-guard changes (callers, signatures, duplicate logic).
4. Maintainer's inline suggestion on #5172 proposes `field.ty(tcx, *args).skip_normalization()` at `uninit_visitor.rs:787`. Our code has `field.ty(tcx, *args)` without it. Determine from the toolchain sources/usages in the tree (rust-toolchain.toml, other call sites, the `inspect` signature) whether ours compiles and whether `.skip_normalization()` is needed or harmless. Verify findings against code before reporting; say UNKNOWN if you cannot.

## Output
`HANDOFF.md`: verdict APPROVE / REQUEST_CHANGES, numbered findings with file:line and evidence, and the answer to item 4.
