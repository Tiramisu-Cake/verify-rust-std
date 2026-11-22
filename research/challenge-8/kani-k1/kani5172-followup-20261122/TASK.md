# Worker task: follow-up PR to merged kani#5172 (three non-blocking review remarks)

kani#5172 ("Preserve memory initialization checks at unresolved calls") merged 2026-11-21. The maintainer's approving review listed three non-blocking follow-ups (quoted verbatim):

> - `try_resolve_instance` in the visitor now calls `checked_body` for every resolved call, which builds the callee's stable MIR and discards it. Availability doesn't need the body (`Item` with `has_body()` or any `Shim`), so the visitor could skip building it and leave fetching the body to points-to, where caching it per instance would also help the dataflow iterations.
> - `unsupported_call_reason` is defined twice with the same message; one shared copy would avoid drift.
> - `let Some(body) = body else { return };` in points-to cannot fail, since the resolver always returns a body for non-foreign items. An `expect` with that invariant (or a comment) would keep a future change from silently dropping the call effect.

Files: `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`, `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` (and the shared resolver module, wherever 5172 put it).

## Do

1. Fresh worktree `/root/kani-5172-followup-w11` on upstream `model-checking/kani` main (fetch from GitHub; current head `87c87010ed`). Branch `fix/uninit-resolver-followup`.
2. Implement the three remarks with minimal, behavior-preserving changes. Per-instance body caching in points-to only if it stays small and clearly correct; otherwise leave it out and say why in the handoff. No unrelated refactors, no test churn. Behavior must be unchanged: existing `tests/expected/uninit`, `tests/kani/Uninit` and the `unresolved-calls` tests are the regression net; add a test only if a remark changes an observable path.
3. Check overlap with open kani#5196 (feliperodri, `uninit-nested-unions`, head bcdc1a0f8d), which edits the same `visit_terminator` call handling: list the hunks that would conflict and keep ours away from them where possible.
4. Local checks allowed: `git diff --check` and local rustfmt via `/root/rustfmt-toolchains/bin/kani-fmt-check.sh`. No local cargo/rustc/Kani/CBMC. Do not push anywhere; the coordinator runs fork quick CI.
5. One commit, author and committer `Tiramisu-Cake <igkharin@gmail.com>`, no Co-Authored-By, conventional Kani commit message style.
6. Write `HANDOFF.md` next to this file: commit SHA/tree/parent, diff summary per remark, 5196 overlap, and a draft PR title and body in the style of kani#5210 (short, plain, "Follow-up to the review of #5172", Testing line placeholder, license line, then a final line `*Disclosure: this change and description were prepared with the help of AI assistants.*`). Commit the handoff to g0 with `[skip ci]`, push g0, stop and report the SHA.
