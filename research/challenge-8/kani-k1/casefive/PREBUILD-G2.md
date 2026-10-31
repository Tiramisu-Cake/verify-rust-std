# CASE5 G1 result and G2 PRE-BUILD REVIEW packet

## G1 (done)

Build `8c52a7a8-289e-4352-91ed-86d4f1bf5d26`, request `casefive-g1-20261101`, head `aa4469674a`,
library `18bb799795`; pin `9461e07af7`; COMPLETE, all 8 compiled and ran, Kani exit 1 (expected
failures), own cost $0.1215 (reserve $0.729 released); check-tooling vs `30f77e8599` ok; peak
RSS 1.59 GiB (kani-compiler), cbmc ≤ 0.05 GiB. Files: `g1.summary.md`, `g1.status.txt`,
`g1.peaks.txt`, `g1.tooling.txt`, `g1.cost.txt`, `g1.wait.txt`, `g1.dispatch.txt`.

| Row | Expect | Actual | Failed checks | Covers |
|---|---|---|---|---|
| R0 closure 17 | FAILED | FAILED | pos 0, pos 1 | 1/2 |
| R1 taken only | FAILED | FAILED | **pos 1 only** | 1/2 (reached; no path passes) |
| R2 not taken only | SUCCESS | **FAILED** | **pos 0 only** | 2/2 (some path passes) |
| R3 fn pointer | SUCCESS | **FAILED** | pos 0, pos 1 | 1/2 |
| R4 closure M=1 | FAILED | FAILED | pos 0, pos 1 | 1/2 |
| R5 single assert | FAILED `[taken]` | FAILED | **`[taken]` and `[not taken]`** | 2/2 |
| R6 snapshot | FAILED | FAILED | pos 0, pos 1 | 1/2 |
| R7 reference ptr::swap | SUCCESS | SUCCESS | — | 2/2 |

Reading (assert-assume: on each path only the first failing assert counts):
- Fixture/oracle sound: R7 passes on the same fixture and oracle. R6 = R0: not the snapshot.
- Both branches diverge (R5 2/2 covers, both labels fail). The lost cover in R0 is the
  assert-assume cascade, not an unreachable branch. My branch prediction (taken only) was wrong.
- Taken: position 0 never fails first, position 1 fails on every path (R1 cover after the loop
  unreachable). Not taken: position 0 fails on some paths, others pass every check (R2 2/2).
  This is exactly what "both positions hold the old `v[1]`" (y, y) predicts in both branches:
  taken (y, y) vs (y, x) fails pos 1 at byte 0; not taken (y, y) vs (x, y) fails pos 0 unless
  x == y. Consistent and simplest, not yet confirmed. G2B checks it step by step.
- Not closure-specific (R3 = R0), size-free (R4, M = 1, with 17/128/129).
- Open contradiction: `swap_contract_bytes17_n2` (same function, F = fn pointer, `[u8; 17]`) passed
  in P1-CLEAN G1. Its ensures compare arrays with `==` (KeyB17 model = whole array). Either the
  move differs in the contract harness, or `==` on `[u8; M]` cannot see the divergence. The second
  case would make the array-model swap PFCs (KeyB16/KeyB17) vacuous. The P1 negative full-value
  control (SPECFIX row 11) used `u8`, so no array `==` negative control exists. G2C decides this.
- Class so far: not harness (R7). Not shown to be the library: the source gives the correct move,
  and the u8 swap/network proofs pass. Kani model/pipeline is likely but the step is UNKNOWN.

## G2 (≤ 3 rows, needs a separate GO)

Library commit `849f1e6bd8` (library tree `ceb85757cb`): G1 rows unchanged; adds a byte-wise
`casefive_bytes_eq` helper and three opt-in rows. Gate `gate-g2.txt` PASS (diff scope, runtime
untouched, 11 harnesses, 54 unique messages, expect_check own-row). rustfmt clean, ≤ 100 columns.

| Row | Single change vs R0 | Expect | Prediction / reading |
|---|---|---|---|
| G2B `casefive_g2b_replica_steps_bytes17` | the call replaced by the statements of `swap_if_less` (same std calls and order), one assert after each: 1 decision, 2/3 selects, 4 `ptr::read` value, 5 pos 0 after `ptr::copy`, 6 pos 1 after `copy_nonoverlapping`. Byte-wise compare, no array `==` | FAILED `casefive G2B: step` | First failing step(s) localize the divergence. If (y, y) comes from the selects: step 2 fails on not-taken paths and step 3 on taken paths. The passing u8 proofs make an array-specific step 4–6 equally plausible. All steps pass → the divergence needs the real `swap_if_less` instance or call boundary |
| G2C `casefive_g2c_array_eq_only_bytes17` | component checks removed: only R0's array `==` oracle | FAILED `casefive G2C: array == oracle` | FAILED → `==` sound, and the P1 PFC pass means a context difference (OPEN). SUCCESS → `[u8; 17]` `==` misses the divergence, so the array-model PFC evidence is vacuous: a P1 finding |
| G2D `casefive_g2d_closure_u8` | element `u8` instead of `[u8; 17]` | SUCCESS | FAILED → harness-context divergence for scalars too, despite the passing u8 proofs |

Request `casefive-g2-20261101` (`g2.request.json` = `RUN-REQUEST.json`): diagnostic, 3 min,
controls true, kani_jobs 1, uninit false; validate accepted. Reserve 3×3 + 30 = 39 min ×
$0.0135 = $0.5265. Task reserve left $1.26 − $0.1215 = $1.1385. Budget: used $71.6010, reserved
$0 (`budget-after-g1.txt`). G2 is the last build allowed (≤ 2).
