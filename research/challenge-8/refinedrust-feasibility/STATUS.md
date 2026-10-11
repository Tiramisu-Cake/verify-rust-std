# RefinedRust feasibility — G1 PREPARATION CLOSED / docs-only

2026-10-11, Europe/Moscow. **READY FOR TECHNICAL REVIEW / NOT DISPATCH READY / NOT_RUN.** Cloud budget/charge **0/0**; own registered lanes, active/unresolved Build/token **NONE**. No compilation/extraction/proof/install/infra/coordinator changes.

- Worktree /root/verify-rust-std-refinedrust-feasibility-20261011; branch research/refinedrust-feasibility-20261011; origin https://github.com/Tiramisu-Cake/verify-rust-std.git.
- Separate index /root/verify-rust-std/.git/worktrees/verify-rust-std-refinedrust-feasibility-20261011/index; starting HEAD/G0 `60272e31ae4d1780dea05da525c345b0c6534799`; no new worktree.
- Fixed source/base and read policy snapshot `c7ca8c467aecf10a4b53039372ee97714f854ee3`; policy-change `5bf53668a4afa51c302e599be91a2dbc4b24042d` (AGENTS/WORK-POLICY/runbooks).
- SmallSort blob `e555fce440872898e47fd5114f32eb15401d07df`; RR `332d945fafa14bf55c0c8390cb35ec4b0c012cff`; compiler nightly-2026-08-28/full SHA `e457a7b0d326d67b4322ef0d11bd715cfaeda48f`.

Results: [G1-CLOUD-PREPARATION](G1-CLOUD-PREPARATION.md), [G1-EXECUTION-PLAN](G1-EXECUTION-PLAN.md). Previous [G0](G0-RESOURCE-REVIEW.md), [feasibility](FEASIBILITY-REPORT.md) and [plan](EXPERIMENT-PLAN.md) retained. Generic CURRENT recovery remains PROOF REQUIRED/UNKNOWN. Latest read [merge checkpoint at `d74a50c886a8e5a19289c577a9b41fadca760630`](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d74a50c886a8e5a19289c577a9b41fadca760630/research/challenge-8/cloud-build/origin-layout/FINAL-CHECKPOINT.md): actual glue session closed, final exporter compile failed, generic recovery unproved; peer evidence neither replayed nor changed.

Main risk: pinned core (repo nightly-2026-02-05) versus RR nightly-2026-08-28; frontend translates crate/scans ADT Drop glues. Actual callee/cleanup admission unobserved. Submission blockers: no confirmed image digest or executable harness/proof and registered infra/recipe SHAs. Proposed warm timeout/reservation 1200/1260 s; separate cold frontend setup 1740/1800 s only if approved. Foundational Rocq replay explicitly deferred, not PASS. New G1 caps supersede old 3600/7200 s proposals; none are authorized.

Validation: static source/document/config/pin/link and Git diff checks; only two G1 docs/compact STATUS changed. Ordinary own-branch commit/push [skip ci]; exact commit is branch tip/final report. No PR/merge/Tool Application/Cloud Build.

**STOP after publication.** Owner next reviews design, separately authorizes harness/image/lane implementation and freezes inputs, then decides budget/session. Preparation grants no execution/G2 permission.
