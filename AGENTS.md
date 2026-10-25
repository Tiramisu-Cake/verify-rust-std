# Kani K-1 experiment worktree (Codex)

This worktree runs only the Kani K-1 experiment of the SmallSort Challenge 8 minimal plan. Since phase 7 (2026-10-26) the K1-merge agent runs in Codex.

Read `research/challenge-8/kani-k1/EXPERIMENT.md` first: all of it, with §5a (32 GB resource lane on Cloud Build) in full. Then read `research/challenge-8/kani-k1/TASK-merge.md`: the header and the section «Фаза 7». Then read `research/challenge-8/kani-k1/RESULT-merge.md`: «Фаза 6» and «Фаза 5».

EXPERIMENT.md governs this experiment where it differs from `/root/AGENTS.md` or the SmallSort CORE (lane, owners, evidence reading). Their other rules still apply. In this experiment:
- no smallsort-session task, no Evidence Brief, no smallsort-ci Cloud Build lanes;
- the only lane is `research/challenge-8/kani-k1/tools/k1g.sh`;
- R9 review is not part of phase 7.

The rules for Claude Code in `CLAUDE.md` (the smallsort-reviewer subagent, background waits) do not apply to Codex. Wait for builds with a foreground `k1g.sh wait`, as TASK-merge.md «Фаза 7» says.
