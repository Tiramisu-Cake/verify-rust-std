# Handoff — PR-02 entry reset

Source candidate is committed in `/root/kani-fix-ch8-pr02-reset-w15` on `work/ch8-pr02-reset-w15`: `f695f653efaa1f7ac6774a079104de8cc0ff81fc` (tree `ae00c4f05316e1129d7ce911417c627fda1dc9ea`). Source patch and full C2/SEL1 apply-check identities are included here. No rebase/force/push was performed.

Independent source and final-package review are complete (GO for review scope); reports and exact bindings are recorded in REVIEW.md and CI-REQUEST.json. Final CI package: `b4edbb18bc8a490197420aac0964a7d55b284380`, tree `a5a1c0b0b06c8af67ec132f107883222e2d220c1`, branch `work/ch8-pr02-reset-ci-w15`, worktree `/root/kani-fix-ch8-pr02-reset-ci-w15`. This stage prepares the requested single matrix run and does not authorize or execute it.

Coordinator next action: inspect the final CI-REQUEST.json and REVIEW.md; create a non-skip child of the exact CI package commit with an identical Git tree, then push that child to a unique `uninit-ci/ch8-pr02-reset-*` branch. The package parent is `[skip ci]`. Do not push an unreviewed changed tree or use a second dispatch/retry under this request. One matrix run has arms A/B, each capped at 120 minutes, max-parallel 1.

Arm A is the standalone PR-02 fix plus fmt/build/clippy/compiler units, new fixtures, affected suites, and the exact same fixture/flags old PR-02 controls. Arm B is cumulative SEL1 plus the same source patch and the exact original #4854 autoharness/explicit companion from A1. C2/SEL1 apply checks do not rewrite their existing branches.

All native outcomes are NOT_RUN. Source inspection/review and isolated Git apply checks establish source properties, not compilation, emitted-model evidence, proof acceptance, or independent B1/B2 credit. After CI, the coordinator evaluates the matched results, emitted-reset evidence and complete controls before updating PR-02 text or rebuilding later stack identities. Historical ledgers/evidence and PR text remain untouched.

The g0 input was ea3cec4078a2b1598d4d4f5d3bd62db9c1a13dde. Other sessions advanced the shared g0 during execution; this handoff commits only its own `kani3300/ch8-pr02-reset/` directory on the current shared head and preserves other changes.
