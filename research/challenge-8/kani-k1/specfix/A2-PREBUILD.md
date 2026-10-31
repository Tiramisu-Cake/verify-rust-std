# SPECFIX-A2 PRE-BUILD note

Task `TASK-SPECFIX-A2.md` (4768661430). Library unchanged since `3282e976b0`: library tree
`31997f7781bd893678bfbd9bbd067efb338cd7db` (final StageA, row 10 harness reverted, never built
cfg-on). No library delta in this package; research-only commit.

Request `specfix/a2.request.json` = `RUN-REQUEST.json` (sha256 `1010a363…5b33`),
`specfix-a2-20261031`: measurement, gcb-e2-standard-4, controls true, kani_jobs 1, uninit off,
timeout 10 min, 11 entries = `g1.request.json` minus row 10 (manifest `removed_after_g1`),
names/expect/expect_check byte-equal to G1 rows 1–9, 11, 12. `kani_k1.py validate` ok
(`--exact`, 11 harnesses).

Expected-FAILED literals rechecked on the final tree (`static-check-a2.json`, ok):
- row 11 `specfix full-value checker detects payload corruption`: unique, merge/specfix.rs:588
  (the preceding assert at :586, key order, must hold);
- row 12 `value probe supports at most 128 bytes per value`: unique, merge.rs:46, before first read.
Rows 1–9 expect SUCCESS.

Envelope 11×10 + 30 = 140 min × $0.0135 = $1.89 ≤ $2. Budget before
(`budget-before-a2.txt`): used $69.6030, reserved $0, cap $88.96 → ≤ $71.4930 after dispatch.
Risk: another kani-compiler error in the cfg-on tree (G1 showed only the first) = COMPILE_ERROR,
all NOT_RUN; no retry in this task.
