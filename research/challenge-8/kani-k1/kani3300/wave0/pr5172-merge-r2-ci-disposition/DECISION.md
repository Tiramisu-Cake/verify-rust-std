# #5172 merge r2 — owner package disposition

**AGREE**: prepare the owner push package for exact `7e53bc65394dd1af675545c428ca2ff29e7a6a27`. No further fork CI is required for this handoff. This accepts explicitly partial evidence for owner review; it does not declare green CI or authorize an open-PR push.

Run [44633285784](https://github.com/Tiramisu-Cake/kani/actions/runs/44633285784), attempt1, is natively FAILURE: ubuntu24 passes; arm64 regression fails; ubuntu22, macos15-intel **and macos15** are cancelled. Perf/docs/LLBC/benchcomp pass. Format/Clippy and Deny pass on the exact head. Source consent and exact diff/merge checks remain bound to `e1f093d1200551a1faa46cefa7a464c9c54cd703`. Cache module and fixture are unchanged from the merged-in PR head.

The coordinator reports the sole arm failure as `codegen_cache: FAIL: no cache statistics were printed` and the same marker in upstream queue runs 44590803353 and 44605372437. Native metadata confirms those upstream regression failures (ubuntu22 and macos15-intel). Exact check-summary routes are unavailable; no raw logs acquired. An intermittent upstream test/statistics-output failure is a reasonable working classification. Its root cause remains UNKNOWN. TLS destructor, profile/env, cache initialization and output capture are hypotheses. Recurrence across unrelated heads supports stopping fork retries for this owner handoff; it does not prove branch effects impossible.

Current PR head remains `d91aeeea94a8a4a697f9416fafbe6cf0f8816801`, auto-merge disabled. **Release Bundle remains queued**. Prepare now; actual publication waits for upstream terminal/idle, a fresh exact-head/auto-merge check, and owner command. Keep cancelled platforms cancelled and earlier head passes historical. No force, automatic retry or new CI authorized.

#5206 attempt2 remains natively FAILURE: eight successful Kani jobs, macos15 cancelled without a runner. Say previously failing regressions passed on retry, macos15 not validated; do not call all platforms or the workflow green. Successful old non-regression executions retain their original timestamps.

Seven duplicate searches found no matching issue; unrelated historic hits recorded. ISSUE-DRAFT.md is a symptom-based English draft. Publication requires owner command. No source/native/CI/push/publication/accounting performed.
