# TASK — inventory of working copies under /root for disk cleanup (2026-11-20)

One stage. **Read-only. Do not delete, move, `git worktree remove/prune`, fetch into, checkout, reset, stash or commit in any inspected directory.** Only write the outputs below in this directory, commit them to g0 with `[skip ci]` as Tiramisu-Cake <igkharin@gmail.com>, push origin, stop. Disk is at 90 %: do not create large temporary files; keep any scratch under 50 MB.

## Goal
Disk is tight (5 GB free of 50 GB). `/root` has ~132 `kani*` directories (3.2 GB) and ~57 `verify-rust-std*` directories (4.9 GB), plus other git checkouts (cbmc, verifast, etc.). Classify every git working copy directly under `/root` (depth 1; include linked worktrees and standalone clones) so the coordinator can later delete only the safe ones.

## Never candidates (mark KEEP_PROTECTED, do not even analyse deeply)
- `/root/ozon-warehouse*` and anything Ozon-related.
- `/root/verify-rust-std-evidence-brief`, `/root/verify-rust-std-kani3300-g0`, `/root/smallsort-pr-drafts`, `/root/rustfmt-toolchains`, `/root/Ch8_audit`.
- Main repositories that other worktrees are linked from (the `.git` common dir owner) — deleting them breaks the linked worktrees. Identify them via `git rev-parse --git-common-dir`.
- Working copies for open/active upstream work: kani#5172 (`/root/kani-pr5172-copilot-w15` and the PR's own branch `fix/kani-uninit-unresolved-call-v3` wherever checked out), kani#5176, the #5206 fix (`/root/kani-fix-5206-w13`), kani#5210 / #5159 follow-up (`/root/kani-5159-followup-main`, `/root/kani-5159-followup-w11`), verify-rust-std#752 (its head branch), diffblue/cbmc#9487.

## Per directory, collect (cheap commands only)
- path, size (`du -sx`), last modification time of the tree (newest file mtime is fine, or dir mtime if cheaper), kind (linked worktree / standalone clone / main repo with N linked worktrees), git common dir.
- HEAD sha, current branch, `git status --porcelain` count (tracked changes + untracked, separately). Untracked files that look like results (`*.md`, `*.json`, logs) must be listed by name (up to 10).
- Local branches whose tip is not known to GitHub. Get GitHub tips once with `git ls-remote` for `https://github.com/Tiramisu-Cake/kani.git`, `https://github.com/model-checking/kani.git`, `https://github.com/Tiramisu-Cake/verify-rust-std.git`, `https://github.com/model-checking/verify-rust-std.git` (and cbmc/verifast forks if relevant). A local commit X counts as published if X equals a GitHub tip, or `git merge-base --is-ancestor X T` succeeds for some GitHub tip T whose object already exists locally (do not fetch). Otherwise UNPUBLISHED (list sha + subject).
- Whether the path or its branch is referenced by currently active work: grep the path in g0 `research/` files modified in the last 3 days, in `/root/smallsort-pr-drafts/TODO.md`, and in current tmux pane cwds (`tmux list-panes -a -F '#{pane_current_path}'`). Also whether any running process has its cwd inside it (`ls -l /proc/*/cwd`).

## Classification
- `SAFE_DELETE`: clean (no tracked changes; untracked only build/scratch noise), every local branch tip and HEAD published, not referenced by active work, no process inside, not a main repo with linked worktrees, untouched for ≥ 2 days.
- `ASK`: anything uncertain — unpublished commits, untracked result-like files, recent activity, referenced by recent docs.
- `KEEP`: active work or protected.
For each SAFE_DELETE give the exact removal command the coordinator should use (`git -C <main> worktree remove <path>` for linked worktrees, otherwise `rm -rf <literal absolute path>`), but do not run it.

## Output
- `INVENTORY.json`: one record per directory with all fields above.
- `SUMMARY.md`: totals (count and GB) per class; table of SAFE_DELETE sorted by size; list of ASK with the one-line reason; anything surprising. Verify a sample of 5 SAFE_DELETE records by re-running the checks before finishing.
