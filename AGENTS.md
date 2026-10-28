# Submission review worktree П-1/П-2 (Codex)

R8 submission addendum, items П-1 and П-2 only — paper, no builds. Branch `experiment/kani-sub-p12-20261028`, based on `661a5a1a` (accepted EXT X0).

Read before any action:
1. `research/challenge-8/kani-k1/TASK-sub-p12.md` — your task. It governs this session.
2. The addendum: `git show a03f8c3a:research/challenge-8/CH8-PLAN-R8-ADDENDUM-SUBMISSION-2026-10-28.md`.
3. The X0 harness registry: `research/challenge-8/kani-k1/EXT-X0-BASELINE-2026-10-28.md` (in this checkout).

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

No builds of any kind (Cloud Build, Actions, CircleCI), no local Kani/rustc/cargo/CBMC. Do not change `library/`. No force-push. Ask the owner nothing; decide disputed points and record them. Finish with `REVIEW REQUEST <sha>` and the line `W3-SUB ЗАВЕРШЁН`, then stop.

The SmallSort Select/Merge session flow from the global instructions (CORE, `smallsort-session`, Evidence Brief / `smallsort-brief`) does not apply to the Kani lane: its builds are not served by the Brief reader. Do not add Brief rules to documents or tasks here; the lane interface is `k1g.sh` as in W3-RULES.
