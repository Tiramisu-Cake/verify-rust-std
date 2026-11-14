# C2-S3 controls v2 — coordinator CI (2026-11-14)

Baseline bf8170b28 + controls-v2/baseline-tests.patch (tree 1356cb0048, matches expected) + CI-only 8cf1626b30, run 43614612145:
- moved-from-source: **VERIFICATION SUCCESSFUL, 0 of 183 failed** (false success) → test FAILED as intended.
- repeated-destination: **VERIFICATION SUCCESSFUL, 0 of 189 failed** (false success) → test FAILED as intended.
- reinit-companion: ok.

Candidate 5ca3cbf2e9 + CI-only 1b9be0f53b, run 43614615441: SUCCESS — format PASS, build PASS, clippy PASS,
nested-aggregate-reset 3/3 ok (negatives: exactly 1 failure, "Reading from an uninitialized pointer of type `*const u8`").

Earlier full uninit Quick on 86428e9313 (run 43611509452): kani 24/0, expected 210 ok (only the 3 old-form controls failed),
ui 17/0, script 2/0; composition FAIL = S5 debt. Production unchanged since 86428e9313; only test files changed.

=> F6: both paths reproduced on baseline (false SUCCESS) and fixed by the candidate. Docs narrowing now allowed per task §5.
