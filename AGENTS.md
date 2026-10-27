# Kani wave 2 worktree: W2-merge (Codex)

This worktree runs wave 2 of the Challenge 8 plan, revision 6 (Kani only). Agent: **W2-merge**, branch `experiment/kani-k1-wavemerge-20261026` (continuation of wave 1 on the same branch).

Read in this order before any action:
1. `research/challenge-8/kani-k1/R6-WAVE2.md` — all of it. It governs this work.
2. `research/challenge-8/kani-k1/TASK-w2-merge.md` — your task. Do priority 1 only; priority 2 waits for the coordinator.
3. `research/challenge-8/kani-k1/R5-WAVE1.md` — wave 1 rules and coordinator decisions CD-1…CD-4, still in force.
4. The plan: `git show origin/docs/evidence-brief-policy-20261017:research/challenge-8/CH8-MINIMAL-PLAN-R6-2026-10-26.md` §2–§3.
5. Your own wave 1 record: `research/challenge-8/kani-k1/RESULT-merge.md`, section «Волна 1».

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

Rules for this runtime:
- The only lane is `research/challenge-8/kani-k1/tools/k1.sh` (CircleCI). Do not run Kani, rustc or cargo locally. Python tool tests are allowed.
- Wait for jobs with `k1.sh watch <job>`, then end the turn. A queued message "k1 watch: job … status=…" wakes the thread. No Codex goal.
- Ask the owner nothing. Decide disputed points yourself and record them (R7).
- Lane files never change on this branch. No force-push.
- Write RESULT entries briefly and neutrally, in terms of Kani checks (harness, expected and actual status, failed check text and location).
- The SmallSort Select/Merge session flow (CORE, `smallsort-session`, Evidence Brief, Cloud Build lanes) does not apply here.
