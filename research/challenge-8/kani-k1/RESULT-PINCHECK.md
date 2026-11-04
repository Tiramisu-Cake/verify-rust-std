# RESULT PINCHECK — Kani cd355b0b: 8/8 controls fail on their check; CASE5 D1 still fails; uninit calibration NOT achieved
Kani `cd355b0bccd3…` / nightly-2026-10-22, evidence `pincheck/`; library `53ec52ed73` (tree `dc60cd2cd0` = v7 `32ce0c62f6` + opt-in
`verify/pincheck.rs`; ordinary 202 unchanged statically), packet `de0bd8ce5f` (GO). check-tooling vs eccc31f43b rc 0 ×2;
no smallsort warning. Own $0.243 ≤ $2.50; project $93.8895 / $98.96 (reserved $1.539 = other builds). Two Builds, no retry/repair.
## G1 `d7302cc6-30d7-478e-9a7e-7750f034b3e4` (k1-network, controls on, uninit off, 2 min): SUCCESS, gate True, 9/9 as expected
| Row (old = Kani 9461e07a) | Status | Failed check @ location | Time new / old s | Covers |
|---|---|---|---|---|
| specfix_full_value_checker_rejects_payload_change_u8 | FAILED = exp. | `specfix full-value checker detects payload corruption` @ specfix.rs:351 | 3.50 / 3.14 | 1/1 |
| wrap::rejects_payload_corruption | FAILED = exp. | `wrap full-value checker rejects payload corruption` @ wrap.rs:269 | 0.67 / 0.65 | 1/1 |
| wrap::rejects_always_true | FAILED = exp. | `wrap canonical comparator required` @ wrap.rs:61 | 0.44 / 0.43 | 3/3 |
| specfix_wrong_f_{sort4_u64, insert_u8, merge_u8} | FAILED = exp. ×3 | `specfix_canonical_comparator::<P>(cmp)` @ specfix.rs:241 / 277 / 315 | 0.33 / 0.29, 0.90 / 0.76, 0.72 / 0.68 | 1/1 ×3 |
| pincheck::casefive_d1_select_read_bytes1 | FAILED = exp. | `casefive D1: read through the selection` @ pincheck.rs:29 | 0.29 / 0.28 | 2/2 |
| pincheck::arrayfactor_f5_symbolic_indices_bytes1 / casefive_d2_select_read_u8 | SUCCESS = exp. ×2 | — (0/52, 0/26) | 0.59 / standalone; 0.17 / 0.17 | 4/4, 2/2 |
- **8 controls on the new pin:** with NEWPINCAL (reject_mutant_swap, wrong_f_swap) all 8 v7 controls FAIL with exactly
  one failed check, the named one at its location; covers all satisfied. Check totals equal the old pin except full_value
  (374 vs 389). Every row's failed-check count is 1. `kani::assert` literal messages still print on cd355b0b.
- **CASE5 caveat stands:** D1 still FAILED on its value check with both selection covers (x[0] != y[0]) satisfied; F5
  (symbolic indices) and D2 (u8) pass, as on the old pin. The array-select divergence is not fixed in cd355b0b; keep
  "model-trust OPEN (CASE5-2)" for the array-model PFCs. Which branch fails is not printed (terse).
## G2 `8f59f833-267f-456c-a0f3-c5f867faca39` (k1-merge, `-Z uninit-checks`, 5 min): FAILURE = gate False; 6/6 ran, no TIMEOUT
| Row | Status (exp.) | Failed check @ location → class | Checks, covers |
|---|---|---|---|
| 1 calibration, uninit slot, `assume_init` | FAILED (FAILED) | `Transmuting between types of incompatible layouts.` @ mem/mod.rs:1283 `transmute_neo::<MaybeUninit<u8>, u8>` → unsupported | 1/31, 3/3 |
| 2 calibration, `MaybeUninit::new(x)`, same read | FAILED (SUCCESS) | same check and location → unsupported | 1/32, 3/3 |
| 3 SPECDIAG `raw_uninit_read_sensitivity` | FAILED (FAILED) | `Interaction between raw pointers and unions is not yet supported.` @ pincheck.rs:106 (= old :322) → unsupported | 1/47, 0/3 |
| 4 `network::swap_contract_four_positions_u8` | FAILED (SUCCESS) | `Kani does not support memory initialization checks across calls through function pointers. …issues/3300.` @ ops/function.rs:166 → unsupported | 1/450, 2/5 |
| 5 `assembly::sorted_permutation_insert_tail_u8_n2` | SUCCESS (SUCCESS) | — | 0/174, 1/1 |
| 6 `assembly::permutation_merge_u8_n4` | FAILED (SUCCESS) | raw pointers + unions @ assembly.rs:83 (`dst.as_mut_ptr()`, `MaybeUninit<[u8; 4]>`) → unsupported | 1/235, 0/1 |
- **Calibration NOT achieved:** no uninit-check failure anywhere; both halves stop on the same transmute check and the
  uninit half still satisfies its post-read covers. On this toolchain `assume_init` is `transmute_neo`, which
  `-Z uninit-checks` rejects for `MaybeUninit<u8> → u8`. Rows 3–6 therefore do not count as uninit evidence.
- Outcomes: unsupported operation in 5 rows, 3 texts (transmute layouts; raw pointers + unions, unchanged from the old
  pin; calls through fn pointers, new for us, via the profile's fn-pointer comparator); row 5 SUCCESS without a working
  calibration (not a detection-capable PASS); no compile error, no TIMEOUT. cbmc ≤ 0.07 GiB.
- **Class "read of uninitialized memory":** on cd355b0b `-Z uninit-checks` still cannot check our code paths
  (`assume_init`, `MaybeUninit` raw pointers, fn-pointer comparators all hit unsupported checks before the target read).
  The class stays outside what the lane can check, as F09 on the old pin; no uninit claim for Part 1.
- **NOT_RUN:** sort4 under uninit checks (accepted at GO); a working uninit calibration (a fixture without `MaybeUninit`
  transmute/union pointers, e.g. padding read via a plain raw pointer — not tried); valid-value checks; heavy roots.
## PINCHECK ЗАВЕРШЁН
