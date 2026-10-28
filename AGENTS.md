# EXT X0 worktree (Codex)

Extended plan EXT R2, stage X0 — integrator, paper only. Branch `experiment/kani-ext-x0-20261028`, based on `b6b480cc` (W3-L1 stage D).

Read before any action:
1. `research/challenge-8/kani-k1/TASK-ext-x0.md` — your task. It governs this session.
2. The plan, by sections named in the task: `git show origin/docs/evidence-brief-policy-20261017:research/challenge-8/CH8-PLAN-EXT-R2-2026-10-28.md`.
3. Common wave-3 rules for anything the task does not say: `git show origin/experiment/kani-k1-base-20261024:research/challenge-8/kani-k1/W3-RULES.md`.

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

No builds of any kind (Cloud Build, Actions, CircleCI), no local Kani/rustc/cargo/CBMC. No force-push. Ask the owner nothing; decide disputed points and record them. Finish with `REVIEW REQUEST <sha>` and the line `W3-X0 ЗАВЕРШЁН`, then stop.

The SmallSort Select/Merge session flow from the global instructions (CORE, `smallsort-session`, Evidence Brief / `smallsort-brief`) does not apply to the Kani lane: its builds are not served by the Brief reader. Do not add Brief rules to documents or tasks here; the lane interface is `k1g.sh` as in W3-RULES.
