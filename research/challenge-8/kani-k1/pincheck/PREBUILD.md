# PINCHECK PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No PINCHECK Build submitted; compile/proof NOT_RUN.
Runtime Claude Code, one stage, no subagents. Task `TASK-PINCHECK.md` @ b08c94a164. Branch
`experiment/kani-k1-pincheck-20261104` from 50b3abfe9b. Review SHA = the published commit carrying this packet.
No competitor code/branches/diffs read; no local cargo/rustc/Kani/CBMC; no credentials read.

## Identities

| Item | Value |
|---|---|
| Upstream / tooling base | `233f96f66a` / `eccc31f43b1a4e2765323192d1f511c9e44c7d4b` |
| Library base | `e470652790` (tree `32ce0c62f6` = TRIMPART = Part 1 v7) |
| Library commit | `53ec52ed73` (library tree `dc60cd2cd0`): only new `verify/pincheck.rs` + 2 lines in `verify.rs` |
| Kani / toolchain (tree) | `cd355b0bccd32300713bc2ce4f765dafa1510607` / `nightly-2026-10-22` |
| G1 request | `pincheck-g1-controls-case5-20261104`, `g1.request.json` SHA256 `2a3be745…b485f678` (= `RUN-REQUEST.json` here) |
| G2 request | `pincheck-g2-uninit-pilot-20261104`, `g2.request.json` SHA256 `8b043682…575005ea9` |

## Static checks (no compiler)

- `test_kani_k1.py`: 70 tests OK (`test-kani-k1.txt`). Lane files (k1g.sh LANE_PATHS) equal to eccc31f43b
  (`git diff --quiet`); `check-tooling BUILD eccc31f43b…` runs per build after it ends.
- `check_pincheck.py --head 53ec52ed73` → `static-check.json`, ok: library diff vs e470652790 = `A verify/pincheck.rs`,
  `M verify.rs` (+`#[cfg(kani_smallsort_controls)]` `mod pincheck;` only). Ordinary roots (cfg off) 202 = base =
  TRIMPART `ordinary-expected.txt`; cfg-on 210 → 216, +6 `pincheck::*`, none removed (TRIMPART source model).
  Copies verbatim: D1+D2 (casefive.rs @ d558b986c6 l.638–674), SPECDIAG `raw_uninit_read_sensitivity`
  (specdiag.rs @ 4da5ec554a l.320–328), F5 (standalone lib.rs @ 42ead2dba6 l.62–80, de-indented 4). rustfmt
  --check and `git diff --check` clean. Controls cfg only in verify/ (gcb-k1.sh stray check passes).
- Note: the kickoff says "existing v7 files unchanged"; the task allows the cfg registration, which needs the
  2-line `verify.rs` edit. Nothing else in v7 files changed.

## G1 — k1-network, diagnostic, controls on, uninit off, jobs 1, 2 min/row, 9 rows

Prefix `slice::sort::shared::smallsort::verify::`. Old pin = Kani 9461e07a (RESULT/summary given).

| # | Root | Expect | expect_check (source line now) | Old pin |
|---|---|---|---|---|
| 1 | `merge::specfix::specfix_full_value_checker_rejects_payload_change_u8` | FAILED | `specfix full-value checker detects payload corruption` (`kani::assert`, specfix.rs:351) | FAILED 3.1 s @ :588 (specfix a2) |
| 2 | `wrap::rejects_payload_corruption` | FAILED | `wrap full-value checker rejects payload corruption` (wrap.rs:269) | FAILED 0.65 s @ :269 (INTEGWRAP G1) |
| 3 | `wrap::rejects_always_true` | FAILED | `wrap canonical comparator required` (`canonical_guard`, wrap.rs:61) | FAILED 0.43 s @ :61, covers 3/3 |
| 4 | `merge::specfix::specfix_wrong_f_sort4_rejected_u64` | FAILED | `specfix_canonical_comparator::<P>(cmp)` (requires, specfix.rs:241) | FAILED 0.29 s @ :243 (PONECLEAN G1) |
| 5 | `merge::specfix::specfix_wrong_f_insert_rejected_u8` | FAILED | same text (specfix.rs:277) | FAILED 0.76 s @ :279 |
| 6 | `merge::specfix::specfix_wrong_f_merge_rejected_u8` | FAILED | same text (specfix.rs:315) | FAILED 0.68 s @ :317 |
| 7 | `pincheck::casefive_d1_select_read_bytes1` | FAILED | `casefive D1: read through the selection` (pincheck.rs:29) | FAILED 0.28 s, 1/40, covers 2/2 (CASE5-2) |
| 8 | `pincheck::arrayfactor_f5_symbolic_indices_bytes1` | SUCCESS | — | SUCCESS 0/42, covers 4/4 (standalone, pin and main) |
| 9 | `pincheck::casefive_d2_select_read_u8` | SUCCESS | — | SUCCESS 0.17 s, covers 2/2 |

- Rows 4–6 share one text; RESULT attributes them by location (241/277/315), as NEWPINCAL row 4 (216).
- CASE5 choice (≤ 3): D1 is the minimal in-tree fixture with the impossible counterexample on the old pin
  (RESULT-CASEFIVE CASE5-2; ARRAYREPRO playback x=[255], y=[127], c=true, read y). Its known passing variant is
  F5 (same `[u8; 1]` read through `select_unpredictable`, symbolic indices; SUCCESS on pin and main in
  ARRAYREPRO); D2 is D1 on `u8`, the scalar control. Expectations = old behaviour; a change is a fact.
- Risk: no `kani::assert` message row has run on cd355b0b yet (NEWPINCAL rows used `assert!` and a requires).
  If the description format changed, rows 1–3/7 miss the gate; RESULT records the actual text and location.
- Timeout 2 min: every row ≤ 3.1 s on the old pin, NEWPINCAL light rows ≈ old times.

## G2 — k1-merge, diagnostic, controls on, `uninit_checks: true`, jobs 1, 5 min/row, 6 rows

| # | Root | Target | Expect | expect_check |
|---|---|---|---|---|
| 1 | `pincheck::pincheck_calibration_uninit_read_u8` | calibration: `MaybeUninit::<u8>::uninit()` read by `assume_init` | FAILED | `uninitialized` |
| 2 | `pincheck::pincheck_calibration_init_read_u8` | same read, slot built by `MaybeUninit::new(x)`, assert value == x | SUCCESS | — |
| 3 | `pincheck::raw_uninit_read_sensitivity` | SPECDIAG #17: `read_volatile(slot.as_ptr())` of uninit u8 | FAILED | `Interaction between raw pointers and unions is not yet supported` (old pin @ specdiag.rs:322 = `let slot = …uninit()`, now pincheck.rs:106) |
| 4 | `network::swap_contract_four_positions_u8` | scalar PFC `swap_profile` → real `swap_if_less` (covers 5) | SUCCESS | — |
| 5 | `assembly::sorted_permutation_insert_tail_u8_n2` | real `insert_tail`, initialized `[u8; 2]` (cover 1) | SUCCESS | — |
| 6 | `assembly::permutation_merge_u8_n4` | real `bidirectional_merge` N4 into `MaybeUninit<[u8; 4]>`, then `assume_init` (cover 1) | SUCCESS | — |

- Calibration rows share `pincheck_read_slot` (`slot.assume_init()`); only the slot construction differs.
  `uninitialized` is a substring choice: I could not confirm the exact uninit-check text from Kani docs. It
  excludes both old unsupported texts ("Checking memory initialization of type … is not supported",
  "Interaction between raw pointers and unions …"). RESULT classifies every row by the actual description and
  location as SUCCESS / FAILED on the uninit check / unsupported operation (exact text) / compile error /
  TIMEOUT; the lane gate is not the task gate. Rows 3–6 count only if row 1 fails on an uninit check and row 2
  passes.
- Row 3 expectation = old-pin behaviour (unsupported); row 1 is the by-value union read, row 3 the raw-pointer one.
- Rows 4–6 expect SUCCESS (correct code); old-pin evidence for this class: `select_unpredictable` (used by
  `swap_if_less`) hit the raw-pointer/union unsupported check (SPECDIAG #11, hint.rs:844).
- **Choice to review:** the task lists four helpers (swap, sort4, insert_tail, merge) but caps G2 at 6 rows
  with 3 taken by calibration and SPECDIAG. I dropped **sort4** (NOT_RUN): it uses the same
  `select_unpredictable` as swap and the same `MaybeUninit<[T; 4]>` destination as row 6. insert_tail and merge
  rows are the small real-body assembly roots (0.2 s / 1.1 s in v7 CI ubuntu); PFC versions are 126 s / 51 s.
  Swap keeps the scalar PFC (8.4 s v7 CI, 12.8 s NEWPINCAL). If sort4 should replace a row, say which.
- Timeout 5 min: uninit instrumentation cost on these roots is unknown; ≥ 20× the uninit-off times.

## Budget, slots, dispatch

- Reserves: G1 (9×2 + 30) × $0.0135 = **$0.648**; G2 (6×5 + 30) × $0.0135 = **$0.810**; sum $1.458 ≤ own cap
  $2.50 (a compile-error repair of either still fits). Project before (`budget-prebuild.txt`): used $93.6465,
  reserved 0, 215 builds → at most $95.1045 ≤ $98.96. Unfinished 0 (≤ 2 per project, ≤ 1 per owner).
- After GO: dispatch G1 from the review SHA (RUN-REQUEST.json = g1.request.json). Then one research commit sets
  RUN-REQUEST.json byte-equal to g2.request.json, push, dispatch G2 (different SHA; parallel, other owner).
  `k1g.sh wait` in background for each. No retry; one compile-error repair per build only within cap.
