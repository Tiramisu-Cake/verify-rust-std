# A1 ARRAYFACTOR — PRE-BUILD REVIEW

Task `TASK-ARRAYFACTOR.md`, task/base `db9583a0b9` (CASE5-2 result `a1e56b61cd`).
Worktree `/root/verify-rust-std-kani-arrayfactor`, branch
`experiment/kani-k1-arrayfactor-20261101`. One diagnostic build, coordinator GO required.

## Patch and scope

Library commit `56387d72342b9f3bd6fd17c919130a412639bde4`, library tree
`894ee6d862e0b1f29a06dd9877123cce14da4312`. Only
`library/core/src/slice/sort/shared/smallsort/verify/merge/casefive.rs`: append six plain proof rows,
all unwind 180. The complete old file is a byte-identical prefix, including D1/D2 bodies,
messages and order. F0/F1 request those existing harnesses directly, with no wrappers.
The module remains gated by its existing `kani_smallsort_controls` declaration; merge.rs is
unchanged. Production bodies, profiles, ordinary 197 source membership and selected P2 source
membership are unchanged. No new native inventory or proof acceptance is claimed.
CASE5-2 is the runtime/profile baseline; this does not validate a new Part 1 candidate or WRAP.

F2–F7 use independent x/y pre-values (concrete distinct values for F7), compute all oracle
booleans before the first assert, and put every cover before asserts. F5's oracle indexes
`[x, y]`, not the memory read through the selected pointer. F7 has one executable assert per
branch, so a failure on c does not remove !c paths. All new checks are literal `kani::assert`
calls with unique messages and separate source lines. No extra runs of R0–R7/G2/CASE5-2.

## Exact rows and predictions

Namespace for every name below: `slice::sort::shared::smallsort::verify::merge::casefive::`.
`expect` is a prediction; a mismatch does not prevent a diagnostic COMPLETE result.

| Row | Harness | Single factor vs D1 | Expect | expect_check / predicted failure | Covers prediction |
|---|---|---|---|---|---|
| F0 | `casefive_d1_select_read_bytes1` | unchanged D1 | FAILED | `casefive D1: read through the selection` | 2/2 |
| F1 | `casefive_d2_select_read_u8` | unchanged D2, scalar u8 | SUCCESS | — | 2/2 |
| F2 | `arrayfactor_f2_if_bytes1` | explicit if instead of select | FAILED | `arrayfactor F2: read through if selection` | 2/2 |
| F3 | `arrayfactor_f3_deref_bytes1` | `*s` instead of ptr::read | FAILED | `arrayfactor F3: copy through dereference` | 2/2 |
| F4 | `arrayfactor_f4_from_fn_bytes1` | from_fn instead of literal construction | FAILED | `arrayfactor F4: read from from_fn selection` | 2/2 |
| F5 | `arrayfactor_f5_symbolic_indices_bytes1` | symbolic (i,j) instead of (0,1) | SUCCESS | — | 4/4 |
| F6 | `arrayfactor_f6_address_bytes1` | add address oracle | FAILED | `arrayfactor F6: read through the selection` | 4/5; wrong address unsatisfied |
| F7 | `arrayfactor_f7_witness_bytes1` | x=[1], y=[2], branch checks | FAILED | `arrayfactor F7: first selected value` | 2/2 |

Predictions follow the CASE5-2 working hypothesis: symbolic positions spare the array read,
whereas construction and read spelling alone do not. Low confidence: CASE5-2 did not separate
these factors. ptr::read uses read_via_copy; its source comments describe dereference-like MIR,
which motivates the F3 prediction but does not establish pinned Kani behavior. F2 distinguishes
the select path from the initialized aggregate fixture. For F7, predict the first-selected check
fails and the second holds, consistent with a possible read of y; this is an unproven hypothesis,
not a recovered counterexample. SUCCESS means only this concrete witness did not reproduce.

F6 predicts address PASS and value FAILED. Its covers are c/!c with differing values plus
`addr_ok && !value_ok`, `!addr_ok`, `addr_ok && value_ok`, all before asserts. If address fails,
the second assertion is evaluated only on surviving paths: silence does not establish value PASS
on cut paths. The three outcome covers provide pre-assert evidence independently of that cut.
An unsatisfied `!addr_ok` cover is predicted and must be reported, not hidden as a coverage PASS.

## Validation and local package

`check_arrayfactor.py db9583a0b9 56387d7234 RUN-REQUEST.json` → `gate.txt`.
GATE PASS; `validation.txt` records formatting, preserved lane and package checks; exact source,
request, reproducer and pin-file hashes are in `source-identity.json`.
Read-only Git/source and Python validation only; project rustfmt wrapper checks changed Rust
files, Rust/comments <=100 columns, git diff --check. No local cargo/rustc/Kani/CBMC runs.
The Cloud Build would be the first compile of F2–F7; compile failure is a reported limitation
and consumes the only build slot. `a1.request.json` equals the root `RUN-REQUEST.json`.
`reproducer.rs` is an exact D1/D2 module fragment; `REPRODUCER.md` supplies pin/flags and scope.

## Request, budget and next boundary

`arrayfactor-a1-20261101`, kind diagnostic, runner gcb-e2-standard-4 (4 CPU / 16 GiB),
controls true, kani_jobs 1, uninit_checks false, harness timeout 3 min, exactly 8 harnesses.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12; tools, workflows,
toolchain, checker flags and backend unchanged. Validator accepts the exact request; generated
arguments/runner/RUSTFLAGS are in `a1.args.txt`, `a1.runner.txt`, `a1.rustflags.txt`.
Build timeout/reserve: 8×3 + 30 = 54 min × $0.0135 = $0.729 <= $0.75. No second build.
`budget-before-a1.txt`: project used $73.2480, reserved $0, cap $88.96; envelope after submit
at that snapshot $73.9770. Own request/UUID ledger: no submitted UUIDs; spent $0, reserved $0.
Re-read `k1g.sh budget` after GO, before dispatch; account only own UUIDs for task costs.

STOP at PRE-BUILD REVIEW; await coordinator GO. After GO, dispatch this published branch,
record UUID and call `k1g.sh watch UUID` with CODEX_THREAD_ID, then end the turn. After wakeup:
bounded status/summary/peaks and check-tooling against
`30f77e859903df14b442ff9294d4fbbd44827f20`. No raw logs/trace/playback workaround, no external
publication or issue. Record per-row failed checks/covers and remaining UNKNOWN in the
<=35-line A1 ARRAYFACTOR result section. Evidence Brief/Select-Merge phases do not apply to K-1.
