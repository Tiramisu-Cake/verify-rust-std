# CASE5-2 PRE-BUILD REVIEW packet (one diagnostic build)

Task `TASK-CASEFIVETWO.md` (`0b63fbdaac`). Base = task commit `0b63fbdaac` (CASE5 result
`8f934ca826` + task); pin Kani `9461e07af7`, nightly-2026-10-12; cap 88.96. Tools, workflows, flags,
toolchain untouched. No local cargo/rustc/Kani: the build is the first compile.

## Patch (library commit `d558b986c6`, `library` tree `50c243e332`, separate from research)

Only `verify/merge/casefive.rs` (already opt-in via `#[cfg(kani_smallsort_controls)] mod casefive;`;
`merge.rs` unchanged). Module doc +3 lines, import block extended, G1/G2 rows byte-identical, new
section appended. Runtime library and ordinary 197 untouched; cfg-on set grows by 8 (not run).
Gate `gate.txt` PASS (diff scope, old rows identical, 8 rows in order with unwind 180, twin
contracts textually equal to `swap_profile`/`sort4_profile`, C1 body without select/swap_if_less,
94 unique messages, expect_check own-row). rustfmt (project config) clean, <= 100 columns.

## Rows (full names `slice::sort::shared::smallsort::verify::merge::casefive::…`, unwind 180)

| Row | Harness | Form |
|---|---|---|
| A1 | `casefive_a1_plain_profile_bytes17` | `#[kani::proof]`: `v = array::from_fn(\|_\| any)`, `pre = v`, `reverse`, `taken = KeyB17::CMP(&pre[b], &pre[a])`; plain `swap_profile::<KeyB17>(.., a, b, KeyB17::CMP)` (contract not targeted → body runs as `Original`); `eq_ok` (array `==`), `bytes_ok` (byte loop) at a, b; 7 covers; then `assert(eq_ok == bytes_ok)`, `assert(bytes_ok)` |
| A2 | `casefive_a2_raw_call_bytes17` | A1 with `let mut is_less = KeyB17::CMP; swap_if_less(v, a, b, &mut is_less)` (the call `swap_profile` makes) |
| P17 | `casefive_p17_checked_contract_bytes17` | PFC of `swap_profile_checked::<KeyB17>` (fixture = `swap_contract_fixed`) |
| P16 | `casefive_p16_checked_contract_bytes16` | same, `KeyB16` |
| S4 | `casefive_s4_checked_contract_bytes16` | PFC of `sort4_profile_checked::<Sort4ReadB16>` (fixture = `sort4_length_body`) |
| C1 | `casefive_c1_bad_body_contract_bytes17` | PFC of `bad_swap_profile::<KeyB17>`: same contract, body writes `old_b` into a and b (`ptr::read` + 2× `copy_nonoverlapping`) |
| D1 | `casefive_d1_select_read_bytes1` | `x, y: [u8; 1]`, `v = [x, y]`, `c`, `s = select_unpredictable(c, base, base.add(1))`, `assert(ptr::read(s)[0] == if c {x[0]} else {y[0]})` |
| D2 | `casefive_d2_select_read_u8` | D1 on `u8` |

Twins (`swap_profile_checked`, `sort4_profile_checked`): generic in `P: Profile` like the originals,
the same requires/modifies/ensures attribute lines, the same real call (`swap_if_less(v, a, b, &mut
is_less)` / `sort4_stable(src, dst, &mut is_less)`). Inside the target: before the call, the pre-state is
copied byte by byte (`*const u8` reads) into local `[u8; 32]` / `[u8; 64]` buffers and, for the swap,
also read typed (`ptr::read`, no selected pointer); `taken` from the profile model of the typed copy.
After the call: covers (reached, a > b, a < b, taken, not taken with different values, equal keys
with different values; sort4: reached, unsorted input, adjacent equal keys with different values),
then the asserts: snapshots match the slots (pre), byte-wise transfer at a and at b, snapshots
unchanged (swap); source unchanged, every output equals some input, byte counts kept for every
output and input value, keys ordered by the profile model (sort4). Then the PFC ensures run.

Deviations, stated: (1) D1/D2 take both candidates from one `base = v.as_mut_ptr()` (as
`swap_if_less` does) instead of two `v.as_mut_ptr()` calls: same values, no second `&mut` reborrow.
(2) The fixtures call `kani::any()` in the `from_fn` closure; `ArbitraryValue for [u8; M]` (private to
network.rs) is exactly `kani::any()`. (3) S4 runs at unwind 180 (the P1 harness: 34); sort4 and
the ensures helpers are loop-free, only the twin's byte loops (<= 65 iterations) use it. (4) The twin's
extra typed reads and checks change the MIR of the target; a twin PASS is about the twin.

## Prediction (= request expect; COMPLETE does not need every match)

| Row | Expect | expect_check / predicted failed checks | Covers |
|---|---|---|---|
| A1 | SUCCESS | — | 7/7 |
| A2 | SUCCESS | — | 7/7 |
| P17 | SUCCESS | — | 6/6 twin + fixture end |
| P16 | SUCCESS | — | same |
| S4 | SUCCESS | — (risk: runtime unknown, timeout = OPEN) | 3/3 twin + 1 |
| C1 | FAILED | `swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b)` only (ordered holds for (b, b)) | 3/3 before call + body cover |
| D1 | FAILED | `casefive D1: read through the selection` | 2/2 (covers before the assert) |
| D2 | SUCCESS | — | 2/2 |

Basis: every CASE5 failure used constant positions (0, 1); the PFC fixture uses `reverse`, so a, b
(and both select candidates) are symbolic on each path. Working hypothesis: that spares it, so
A1/A2/P17/P16 pass and the constant-position D1 fails like G2B step 4 / R4. Low confidence;
from_fn construction or the contract context are the alternatives the rows separate.

## Verdict mapping (TASK criterion, per profile)

- KeyB17: A1, A2, P17 SUCCESS with all covers + C1 FAILED only on transfer → local consistency
  (not general faithfulness). A1/A2 FAILED while P17 SUCCESS → the contract context changes the
  outcome → model-trust OPEN. P17 internal check FAILED (P1 PFC passed) or C1 SUCCESS → NOT TRUSTED.
- KeyB16: P17's rule with P16 (+ C1). Sort4ReadB16: S4 (+ C1, which tests the swap contract only;
  stated as such). Missing covers, compile error or timeout → OPEN.
- D1 SUCCESS → minimal form not reproduced; the run reproducer stays G2B. D2 FAILED → scalar too.
- A1 `eq_ok != bytes_ok` → array `==` divergence in this context (P1 finding).

## Request and budget

`RUN-REQUEST.json` = `casefivetwo/g1.request.json`, `casefivetwo-g1-20261101`, diagnostic,
gcb-e2-standard-4, 3 min, controls true, kani_jobs 1, uninit false, 8 harnesses; `kani_k1.py
validate` accepted (`--exact --harness-timeout 3m --jobs=1 --output-format=terse`). Reserve 8×3 + 30
= 54 min × $0.0135 = $0.729 <= $0.75. Budget now: used $71.7225, reserved $0, cap $88.96
(`budget-before-g1.txt`) → at most $72.4515 after submit. One build; no second.
Risk: a compile error in the new section fails all 8 rows (would be reported, not retried).
After the terminal status: summary, peaks, `check-tooling UUID 30f77e8599`, bounded log-grep/lines.
