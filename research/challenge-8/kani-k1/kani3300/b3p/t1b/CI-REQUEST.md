# B3 T1b — coordinator handoff (NOT RUN)

- Parent Kani CI: `cfa4b0c5296b1f7735b0d4a138d339431dfbf93d`.
- Task research base: `b2737f00565bfa73649290cecd31ac42c4097598`.
- Candidate Kani CI SHA: `1a8faa3b60ee9a19534cdb57315e8887f5666301`.
- Authorized coordinator trigger: `uninit-ci/b3-t1b**`, workflow `b3-t1b.yml`.
- One ubuntu-24.04 job, at most 60 minutes, attempt 1 only. No automatic retry.
- Input: `Tiramisu-Cake/kani` run 43701550489, artifact
  `b3-t1-43701550489-1` (T1 retention: 14 days; missing artifact is INVALID).
- No rebuild, model generation or SAT. Only identical 6.11.0 display tool.
- Expected upload: `b3-t1b-<run_id>-1`, RESULT.json, INDEX.json, command logs,
  tool/install/version evidence, raw/normalized dumps and unified diffs.
- Preparation did not push, dispatch CI, create PR/issue or invoke a local backend.

Coordinator checks RESULT stage COMPLETE, input/tool identities, all command exits,
three raw-repeat determinism checks in both modes, A/A count (131 final models),
AA_DIFF, B_DIFF and B_PAIR_DIFFS, exact positive-control structural gate and diffs.
INVALID/INVALID_CONTROL and INCONCLUSIVE_AA admit no B3 conclusion. Auxiliary
wrapper classifications require review; zero width is not automatically harmless.
See DESIGN.md and the unchanged `../t1/RESULT-template.md` for scope limits.
