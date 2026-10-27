# Kani wave 3 worktree: W3-L1 (Codex)

Wave 3 of the Challenge 8 plan, revision 8 (Kani is the main path). Agent: **W3-L1**, branch `experiment/kani-k1-assembly-20261027`.

Read in this order before any action (from the base branch, without merging it):
1. `git show origin/experiment/kani-k1-base-20261024:research/challenge-8/kani-k1/W3-RULES.md` — common rules of wave 3. They govern this work.
2. `git show origin/experiment/kani-k1-base-20261024:research/challenge-8/kani-k1/TASK-w3-l1.md` — your task.
3. The plan: `git show origin/docs/evidence-brief-policy-20261017:research/challenge-8/CH8-PLAN-R8-2026-10-27.md`.
4. Lane: `research/challenge-8/kani-k1/EXPERIMENT.md` §5b (Cloud Build 16 GB, `tools/k1g.sh`).

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

Runtime rules: the lane is `tools/k1g.sh` with runner `gcb-e2-standard-4`; no local Kani, rustc or cargo; wait with `k1g.sh watch <build>` and end the turn; no Codex goal; ask the owner nothing, decide and record (R7); lane files never change on this branch; no force-push. The SmallSort Select/Merge session flow (CORE, `smallsort-session`, Evidence Brief, old Cloud Build lanes) does not apply here. The previous AGENTS.md of this worktree (W2-merge) is obsolete.
