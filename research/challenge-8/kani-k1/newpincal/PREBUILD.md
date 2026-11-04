# NEWPINCAL PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No NEWPINCAL Build submitted; compile/inventory/proof NOT_RUN.
Runtime Claude Code, one stage, no subagents. Task `TASK-NEWPINCAL.md` @ bc1138e73d. Branch
`experiment/kani-k1-newpincal-20261104`. Review SHA = the published commit carrying this packet.
No competitor code/branches/diffs read; no local cargo/rustc/Kani/CBMC; no credentials read.

## Identities

| Item | Value |
|---|---|
| Upstream | `233f96f66ab3785881cead133817ed5db4c76b09` |
| Tooling base | `eccc31f43b1a4e2765323192d1f511c9e44c7d4b` (upstream + K-1 lane tooling) |
| Library commit | `e470652790` = cherry-pick of TRIMPART `bd7fb8196e` |
| Library tree | `32ce0c62f6c28d8ae0df8cef6b75e8557b34174a` at HEAD, `e470652790`, `bd7fb8196e` (all equal) |
| Kani (tree) | `tool_config/kani-version.toml` commit = `cd355b0bccd32300713bc2ce4f765dafa1510607` |
| Toolchain (tree) | `rust-toolchain.toml` channel = `nightly-2026-10-22` |
| Request | `newpincal-diag-inv-ctl-4rows-20261104`, SHA256 `9d8b8b11de08b3f00b59463ef7d8bc9bbc9aef38324077dbbe50a6884f950f34` |

## Static checks (no compiler)

- `test_kani_k1.py`: 70 tests OK, incl. `test_controls_cfg` (check-cfg `cfg(kani_smallsort_controls)` now in
  `library/core/Cargo.toml`); output `test-kani-k1.txt`.
- Lane files (`k1g.sh` LANE_PATHS) `git diff --quiet eccc31f43b HEAD`: equal. `check-tooling BUILD eccc31f43b…`
  runs after the Build (needs the build id).
- `git diff 233f96f66a..HEAD -- library` byte-equal to `git diff 233f96f66a..bd7fb8196e -- library`.
- Controls cfg: `git grep kani_smallsort_controls -- library` outside verify/, verify.rs, core/Cargo.toml,
  smallsort.rs: none (gcb-k1.sh stray check passes).
- `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`: accepted, 4 harnesses;
  args `g1.args` (`--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`), runner `g1.runner`.

## Request

kind diagnostic, `inventory: true`, `controls: true`, gcb-e2-standard-4, kani_jobs 1, uninit_checks false,
10 min per row. Agent k1-network. Prefix `slice::sort::shared::smallsort::verify::`.

| # | Root | Expect | expect_check | Source of the check | Covers | Old pin (RESULT) |
|---|---|---|---|---|---|---|
| 1 | `network::swap_contract_four_positions_u8` | SUCCESS | — | PFC `swap_profile::<LtU8>` | 5 | predecessor `swap_profile_four_positions_u8` 15.4 s (RESULT-SPECFIX) |
| 2 | `network::dispatch_safety_stable_u8_n0_1_2_7_8` | SUCCESS | — | real `small_sort` stable u8 | 6 | none in RESULT |
| 3 | `assembly::reject_mutant_swap_u8_n2` | FAILED | `assertion failed: v[0] <= v[1]` | `assert!(v[0] <= v[1])` assembly.rs:25 (`check_swap`) | 1 | none in RESULT |
| 4 | `merge::specfix::specfix_wrong_f_swap_rejected_u8` | FAILED | `specfix_canonical_comparator::<P>(cmp)` | `#[kani::requires(...)]` specfix.rs:216 (`swap_profile`) | 1 | 0.1 s (RESULT-PONECLEAN G1, `specfix.rs:218` then) |

expect_check sources: row 4 uses the literal requires expression, the exact description PONECLEAN G1 got on
Kani 9461e07a (`specfix_canonical_comparator::<P>(cmp) @ …specfix.rs:218`; line now 216 after TRIMPART
removed the lines above it). Row 3: core `assert!(cond)` without a message was reported as
`assertion failed: <cond>` on 9461e07a (PERM12 summary, commit e493f8d978, network.rs:1518); the shared
placeholder applies to `panic!`/`assert!` with a message literal (PANICPROBE). The mutant negates the
exchange decision, so for distinct values it returns them reversed: only line 25 can fail (line 26 permutation
holds). `check_insert` (line 34) has the same text but is not reachable from this root; RESULT will record
the location. If the new pin changes either description format, the row gate is not met and that is a
calibration fact (no retry).

## Inventory gate

Expected 210 = `ordinary-expected.txt` (202, sha256 78c4c050…) ∪ `controls-expected.txt` (8, 931ee925…) from
TRIMPART `120e443536`, union `expected-210.txt` (5171a7b6…). Rows 1–2 in ordinary, 3–4 in controls.

## Budget and slots

Reserve (4×10 + 30) min × $0.0135 = **$0.945** ≤ own cap $1.00. Project before dispatch (`budget-prebuild.txt`):
used $93.0120, reserved $0.0000, 214 builds; after submit at most $93.957 ≤ $98.96. Unfinished builds: 0
(≤ 2 per project, ≤ 1 on k1-network). One Build, no retry; compile-error repair only with coordinator consent.
