# CASE5 PRE-BUILD REVIEW packet (G1)

Task `TASK-CASEFIVE.md` (`a7f1e5b722`). Base `f000cb484e` (P1-CLEAN result, library tree
`73e902bec8`); cap 88.96 inherited, history unchanged. Pin Kani `9461e07af7`, nightly-2026-10-12;
tools/workflows/flags/toolchain untouched. No local cargo/rustc/Kani: G1 is the first compile.

## Patch (library commit `18bb799795`, `library` tree `2da33e5c84`, separate from research)

- New `verify/merge/casefive.rs` (8 harnesses, no ordinary item); `merge.rs` +2 lines
  `#[cfg(kani_smallsort_controls)] mod casefive;` placed before `specdiag` (rustfmt module
  order), no existing declaration moved. Runtime library and P1 ordinary 197 untouched: the module
  exists only with controls on (static, `gate.txt`); cfg-on set becomes 377 + 8 = 385 (not run).
- rustfmt (`--edition 2024`, project config) clean on both files; lines <= 100 columns.

## Matrix (M = 17 unless noted; arbitrary `kani::any()` x, y; unwind 140 as in case5)

| Row | Harness `…::merge::casefive::` | Single change vs R0 |
|---|---|---|
| R0 | `casefive_r0_closure_bytes17` | none: specfix case5 body, own messages |
| R1 | `casefive_r1_taken_only_bytes17` | `assume(taken)` before the call; cover after the call before any assert (R0's taken cover kept after the loop) |
| R2 | `casefive_r2_not_taken_only_bytes17` | same with `assume(!taken)` (equal keys included) |
| R3 | `casefive_r3_fn_pointer_bytes17` | `let mut cmp: fn(&[u8;17],&[u8;17])->bool = case5_key_less_b17` |
| R4 | `casefive_r4_closure_bytes1` | M = 1 (same macro as R0) |
| R5 | `casefive_r5_single_assert_bytes17` | components folded into `ok_taken`/`ok_not_taken` (no assert), both covers, then one assert per path: `[taken]` / `[not taken]` |
| R6 | `casefive_r6_snapshot_oracle_bytes17` | `let pre = v;` decision and expectation from `pre` |
| R7 | `casefive_r7_reference_move_bytes17` | `if taken { ptr::swap(base, base.add(1)) }` instead of `swap_if_less` |

Messages are literal or `concat!` of literals, all 39 unique; `[taken]` is not a substring of
`[not taken]`. Each expect_check matches only its own row (`gate.txt`).

## Prediction (= request expect; COMPLETE does not need every match)

Reading of R0 under assert-assume: a single deterministic wrong permutation in one branch fails
only position 0 (the keys differ at byte 0); a duplicate `(y, y)` fails only position 1. Both
failing with one unreachable cover needs at least two different wrong outcomes on the failing
branch's paths. The failing branch is most likely *taken*: for x == y every permutation is
correct, so the not-taken cover could only be unreachable with a value outside {x, y}.

| Row | Expect | expect_check | Predicted failed checks / covers |
|---|---|---|---|
| R0 | FAILED | `casefive R0: component oracle position` | pos 0 + pos 1, `==` not listed; 1/2 |
| R1 | FAILED | `casefive R1 taken: component oracle position` | pos 0 + pos 1; 1/2 (reached, none passes) |
| R2 | SUCCESS | — | none; 2/2 |
| R3 | SUCCESS | — | none; 2/2 (same pointer route as passed `swap_contract_bytes17_n2`) |
| R4 | FAILED | `casefive R4: component oracle position` | as R0; 1/2 |
| R5 | FAILED | `casefive R5: single oracle [taken]` | only `[taken]`; 2/2 (no assume before covers) |
| R6 | FAILED | `casefive R6: component oracle position` | as R0; 1/2 |
| R7 | SUCCESS | — | none; 2/2 |

## Discrimination (one build)

- Branch: R1/R2 and R5 message. R1 covers: 2/2 = some taken path correct, 1/2 = reached but
  every path fails, 0/2 = call unreachable under taken. R5 2/2 + one message = the R0 lost cover
  is the assert-assume cascade, not an unreachable branch.
- Oracle/fixture: R7 FAIL (with R0 FAIL) → harness class; R7 PASS → difference is in the move.
- Comparator form: R0 FAIL + R3 PASS → closure-specific execution of the real body in the
  pinned pipeline (the library source gives `is_less(&*v_b, &*v_a) = y[0] < x[0] = taken`);
  R3 FAIL → not closure-specific, and the passed contract harness differs from R3 only by
  wrapper/requires/old-model/arbitrary_value → UNKNOWN, G2 needed.
- Size: R4 PASS → depends on M (multi-byte element); R4 FAIL → size-free (with 17/128/129).
- Encoding: R6 PASS while R0 FAILS → expectation copies of x/y differ from the array (snapshot
  /MIR copy); R6 = R0 → not the snapshot.
- Library class requires R7 PASS, R3 FAIL and a source-level path to the wrong move; Kani/model
  class requires R7 PASS and a pure-comparator form split (R0 vs R3) the source cannot explain.
  Without a trace the step inside the pipeline (kani-compiler vs rustc MIR of the closure
  instance) stays UNKNOWN; timeout/compile error is not a result.

## G2 candidates (≤ 3 rows, only with a separate GO after G1)

1. Decision observer: closure `|a, b| { let r = a[0] < b[0]; seen = r; r }`, assert
   `seen == taken` separately from the move (decision vs move localization).
2. Function item `let mut cmp = case5_key_less_b17` (if R0 and R3 split).
3. Split not taken into `x[0] < y[0]` and `x[0] == y[0]` (if R2 fails).

## Request and budget

`RUN-REQUEST.json` = `casefive/g1.request.json`, request_id `casefive-g1-20261101`, kind
diagnostic, runner gcb-e2-standard-4, timeout 3, controls true, kani_jobs 1, uninit_checks false,
8 harnesses; `kani_k1.py validate` accepted (args `--exact --harness-timeout 3m --jobs=1
--output-format=terse`, RUSTFLAGS `--cfg kani_smallsort_controls`). Reserve 8×3 + 30 = 54 min ×
$0.0135 = $0.729 ≤ $1.26. Budget now: used $71.4795, reserved $0, cap $88.96
(`budget-before-g1.txt`) → at most $72.2085 after submit. G2 39 min / $0.5265 not reserved.
After the terminal status: summary, peaks, `check-tooling UUID 30f77e8599`, bounded
log-grep/log-lines only; no raw logs/archives.
