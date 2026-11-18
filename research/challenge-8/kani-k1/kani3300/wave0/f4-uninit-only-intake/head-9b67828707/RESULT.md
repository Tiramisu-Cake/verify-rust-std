# F4-A final push intake — PARTIAL_INFRASTRUCTURE

Intake and STYLE PR draft are READY for owner review. This packet binds only final head `9b67828707f8d7d5e691484896a82475dcf34d28`, tree `baedd51d92073ecb2b96991bae7dc562ee8f58a2`, parent `b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`. Local Git objects and the existing static identity/skip gate match the reviewed candidate tree. All 16 workflow files match the frozen inventory and dispatch main.

| Native run / attempt | Identity | Native result | Accounted jobs |
| --- | --- | --- | --- |
| Kani CI 44295027834 / 1 | MATCH | FAILURE | 8 SUCCESS; regression (macos-15) CANCELLED |
| Kani Format Check 44295027924 / 1 | MATCH | SUCCESS | format-check and clippy-check SUCCESS |
| Cargo Deny 44295028060 / 1 | MATCH | FAILURE | audit FAILURE |

Every run is completed, repository `Tiramisu-Cake/kani`, event `push`, branch `fix/per-harness-global-transforms`, exact final head. All 12 jobs and every exposed native step are retained in GITHUB-SUMMARIES.json, with source URLs, observation times and complete attempt-1 pagination (9/9, 2/2, 1/1). RESULT.json lists each job separately.

Four regression entries succeeded: ubuntu-22.04, ubuntu-24.04, ubuntu-24.04-arm and macos-15-intel. The new macos-15 job 134769741845 has runner_id=0, empty runner name and no steps: NOT_RUN, matching the new coordinator no-runner report. This required gap determines PARTIAL_INFRASTRUCTURE. No old-head cancellation decision is transferred.

Deny job 134769742186 failed at step 4, Run EmbarkStudios/cargo-deny-action@v2 (starts 2026-11-18T11:29:03Z). Its EXTERNAL_ADVISORY classification comes from the new owner/coordinator report for this head. The current advisory ID/diagnostic text is UNKNOWN; the prior chrono diagnostic is not substituted. Native FAILURE remains recorded.

Documentation build, benchcomp, LLBC and full native perf succeeded. Documentation publication alone was SKIPPED by its frozen main-only condition. C formatting retains continue-on-error=true, with native SUCCESS; Clippy statistics retains its masked shell status. Perf retains retry@v4/max_attempts=2, but internal retry attempts/outcomes and numerical time/RSS/speedup comparisons are UNKNOWN.

The exact-head source routes native regression discovery through scripts/kani-regression.sh -> script-based-pre exec -> config.yml -> test.sh -> check.py. Its oracle checks both uninit modes, both cfg call paths, singleton/paired initialized and delayed harnesses, and the independent unsafe control. With uninit checks, initialized controls must succeed and intended unsafe reads must fail; without the flag, ordinary checking must succeed through the shared transformer path. These are source expectations.

The new coordinator report states script-based-pre 103/103 on this head. Its report text and digest are preserved separately in PROVENANCE.json; OS/job attribution and individual two-mode exports were not supplied. Native regression job success and that aggregate support suite-level acceptance. Named per-harness verdicts, property inventories/counts, measured checkout SHA/tree, actual compilation order and runtime cache causality remain UNKNOWN. Historical main reproducer evidence supplies only the main defect observation; old b5 CI supplies no new-head credit.

The connector rejects the macOS and Deny check-run diagnostic endpoints; exact errors are retained. Coordinator follow-up needs the missing bounded diagnostics/individual exports listed in RESULT.json, not a new execution or raw archive. Missing detail does not prevent this completed intake.

Compiler/e2e PR comparisons, release bundles, verify-std-check and PR metadata/labels remain DEFERRED_TO_UPSTREAM_PR. No all-green, five-OS or independent formal-proof claim is made. Current accounting reference is 29/29 + 9/14 = 38/43, Fast OFF, no accounting changes.

PR-DRAFT.md contains two substance paragraphs, a short Testing section with the sole required current run link, standard license and exact AI disclosure. The external draft is unchanged. No compiler, verifier, runner, CI, retry, cancellation, push, PR, source, ledger, budget or label action occurred.
