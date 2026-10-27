# Kani wave 3 worktree: W3-L1u (Claude Code)

Wave 3 of the Challenge 8 plan, revision 8 (Kani is the main path). Agent: **W3-L1u**, branch `experiment/kani-k1-uninit-20261027`. Runtime: Claude Code (moved from Codex on 2026-10-27 after an OpenAI content block, owner decision).

Read in this order before any action (from the base branch, without merging it again):
1. `git show origin/experiment/kani-k1-base-20261024:research/challenge-8/kani-k1/W3-RULES.md` — common rules of wave 3. They govern this work.
2. `git show origin/experiment/kani-k1-base-20261024:research/challenge-8/kani-k1/TASK-w3-l1u.md` — your task.
3. Your record so far: `research/challenge-8/kani-k1/RESULT-w3-l1u.md` — all of it, especially the last section with the coordinator's R9 verdict (F1–F6) and the build still running.
4. The plan: `git show origin/docs/evidence-brief-policy-20261017:research/challenge-8/CH8-PLAN-R8-2026-10-27.md` §3 (L1-1) and §4.
5. Lane: `research/challenge-8/kani-k1/EXPERIMENT.md` §5b (Cloud Build 16 GB, `tools/k1g.sh`; field `uninit_checks`).

Clean room (owner ruling): never open the code, diffs or branches of Ch8 PRs #576, #678, #694, #701.

Runtime rules (Claude Code):
- Lane: `research/challenge-8/kani-k1/tools/k1g.sh`, runner `gcb-e2-standard-4`. No local Kani, rustc or cargo. One unfinished build at a time.
- Waiting: run `research/challenge-8/kani-k1/tools/k1g.sh wait <build>` as a background Bash task and end the turn; the completion notification wakes you. Do not poll, do not use `k1g.sh watch` (that is the Codex mechanism).
- check-tooling BASE: `f5db92cc388b839ea24f75ae66e7d801a70b45fc` for builds after the lane update; `67a4b452a932d070cf77853a3682c7998de93870` for Z-1 build 9d1cb848.
- Review: `REVIEW REQUEST <full SHA>` in RESULT and push; the coordinator answers in this session.
- Ask the owner nothing; decide disputed points and record them (R7). Lane files never change on this branch; no force-push; read logs only through `k1g.sh summary|peaks|log-grep|log-lines`.
- `AGENTS.md` in this worktree is the Codex entry point; for you this file governs. The SmallSort Select/Merge session flow (CORE, `smallsort-session`, Evidence Brief, old lanes) does not apply.
