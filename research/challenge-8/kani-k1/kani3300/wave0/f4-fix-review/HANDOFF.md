# READY — CHANGES_REQUIRED

Review task `7b829344c9cdd8c25ec59294bb9015201638a879` is complete for package
`7485bbb27a72dd463d4a9628c8627689d30e7e56`, source
`cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, direct frozen-main parent
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.

Verdict **CHANGES_REQUIRED**. One blocking CI-plan finding F4-R14-1 for original15;
no source-code finding or author code/package edit by review.
Static and synthetic validation PASS; observed-main oracle FAIL → synthetic expected-fixed
oracle PASS. Actual fixed compiler/runtime/new-test main/full CI remain NOT_RUN.
Compilation order and runtime causality UNKNOWN; proof credit NONE.

Original15 must include `release.yml` in the full-standard-CI plan: four bundle builds
and both five-OS bundle/toolchain test matrices run on PR, while release and dependent
Docker publication intentionally skip. Update the exact package and return its delta
to this review; preserve source cab66681/tree8585336e and all standard workflows.

After APPROVE of the corrected package, coordinator prepares the separate GO request
for item1 final full standard CI 28/28, incorporating REVIEW.md's exact PR-HEAD/tree
versus merge-ref binding, skip-ci
push-range/head handling, both benchmark labels/native events, and complete job/matrix
coverage. Standard performance/compiler benchmarks must assess clone overhead.
Missing/red/cancelled required checks require a concrete handoff.

Owner publication command and separate CI authorization/accounting are still required.
This review performs no CI/push/PR/ledger/reservation or external message action.
Supplied item1 27/28 reference and S2 ledger/accounting are unchanged. Model+/fast
unchanged; no subagents or local compiler. S2 review e40 is outside this review.

Review output is solely `kani3300/wave0/f4-fix-review/`. The enclosing commit is the
review g0 identity; resolve it with `git log -1 --format=%H --` this HANDOFF path.
