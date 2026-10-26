# Kani wave 1 worktree: W1-merge (Codex)

This worktree runs only wave 1 of the Challenge 8 plan, revision 5 (Kani only). Agent: **W1-merge**, branch `experiment/kani-k1-wavemerge-20261026`.

Read in this order before any action:
1. `research/challenge-8/kani-k1/R5-WAVE1.md` — all of it. It governs this work; the K-1 criterion and STOP counters of EXPERIMENT.md §2 do not apply.
2. `research/challenge-8/kani-k1/TASK-w1-merge.md` — your task.
3. `research/challenge-8/kani-k1/EXPERIMENT.md` §5 (CircleCI lane) and §6 (rules R1–R12, as amended by R5-WAVE1).
4. The plan: `git show origin/docs/evidence-brief-policy-20261017:research/challenge-8/CH8-MINIMAL-PLAN-R5-2026-10-26.md` §2–§4.1, and `…-R4-2026-10-26.md` §4.

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

Rules for this runtime:
- The only lane is `research/challenge-8/kani-k1/tools/k1.sh` (CircleCI). Do not run Kani, rustc or cargo locally. Python tool tests are allowed.
- Wait for jobs with `k1.sh watch <job>`, then end the turn. A queued message "k1 watch: job … status=…" wakes the thread. No Codex goal.
- Ask the owner nothing. Decide disputed points yourself and record them (R7).
- Lane files never change on this branch. No force-push.
- The SmallSort Select/Merge session flow (CORE, `smallsort-session`, Evidence Brief, Cloud Build lanes) does not apply here.
