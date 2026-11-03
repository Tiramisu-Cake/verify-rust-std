# PANICPROBE PRE-BUILD (one diagnostic request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network. Prepared 2026-11-03T18:25Z; T0 not started
(starts at the actual dispatch after coordinator GO). This file registers no phase and grants no dispatch.
Locally only Git, Python and the rustfmt wrapper; no cargo/rustc/Kani/CBMC.

## Identities
- Branch `experiment/kani-k1-panicprobe-20261103`; base `e8e238db9d87323fa4da011a1a8b37fb76ec91c0`; task commit
  `30126453c91551a7af282bfb185a60f0bbded560` (TASK-PANICPROBE.md sha256 0ff5f629…0ee9).
- Library commit `4bd0da5ac09ca6f09abbc64742687cad5437edc4`: `library` tree d4ec476a → `b2d54f08c64960a836da293efc99112e37176850`.
  Only two files: `verify/network.rs` (+3 lines at 14: blank, `#[cfg(kani_smallsort_controls)]`, `mod panicprobe;`;
  sha256 137a897d…2da1) and new `verify/network/panicprobe.rs` (blob 8f54025c, sha256 9daf5e74…6af7).
  smallsort.rs unchanged (sha256 78fc8fe8…ed61). No existing root, stub or comparator touched.
- Lane files (k1g.sh LANE_PATHS) equal base e8e238db9d (`git diff --stat` empty); Kani pin 9461e07a, nightly-2026-10-12.
  `check-tooling BUILD e8e238db9d` after the Build. Tool unit tests test_kani_k1: 70 OK (python only).

## Roots (`…::verify::network::panicprobe::`, all `#[kani::proof]` + `#[kani::unwind(65)]`, no `kani::stub`)
Unwind 65 = the dispatch roots (`dispatch_safety_cases!`, network.rs 267-268). Comparator `any_less(_: &u8, _: &u8)
-> bool { kani::any() }`: function item, reads nothing, mutates nothing. One cover per root (normal return).
| # | Root | should_panic | Body / route (smallsort.rs) | Expect, expect_check |
|---|---|---|---|---|
| 1 | panic_control_plain | yes | `if any { panic!("panicprobe control") }` | SUCCESS |
| 2 | panic_control_ub | yes | `if any { panic! }`; independent `if any { *local.as_ptr().wrapping_add(4) }` on `[u8;4]`, value → `hint::black_box` | FAILED, `pointer outside object bounds` |
| 3 | panic_network_u8_n18_should_panic | yes | `network_u8_n18()` | SUCCESS |
| 4 | panic_network_u8_n18_plain | no | same helper | FAILED, `does not correctly implement a total order` |
| 5 | panic_general_u8_n16_should_panic | yes | `general_u8_n16()` | SUCCESS |
| 6 | panic_general_u8_n16_plain | no | same helper | FAILED, same |

- `network_u8_n18`: any `[u8;18]`, `<u8 as UnstableSmallSortTypeImpl>::small_sort`. u8 is Freeze+Copy, size 1 ≤ 8,
  1×32 ≤ 4096 → `small_sort_network` (311). len 18 → `no_merge` false (330), regions 9+9: `sort9_optimal` (343) each,
  `insertion_sort_shift_left(region, 9)` (349, no iteration), then **one** `bidirectional_merge` of 18 (368).
- `general_u8_n16`: any `[u8;16]`, scratch `[MaybeUninit<u8>;48]`, `<u8 as StableSmallSortTypeImpl>::small_sort` →
  `small_sort_general_with_scratch` (220; scratch 48 ≥ 16+16). size ≤ 16 and len ≥ 16 → two `sort8_stable` (243-244),
  each 2×`sort4_stable` + `bidirectional_merge` of 8 (672); presorted 8 = desired 8, no `insert_tail`; then
  `bidirectional_merge` of 16 (286) under `CopyOnDrop`. **Three** merge calls, each can reach the guard (832 →
  `panic_on_ord_violation` 839, `panic!` at 854). Plain/should_panic pairs share one helper, so bodies are identical.
- Pin semantics read in Kani 9461e07a source (kani-driver/src/call_cbmc.rs 716-757): with `should_panic`, SUCCESS iff ≥ 1
  failed property and all failed are class `assertion` (panic!/assert!); none failed or any other class → FAILED. So
  rows 3/5 SUCCESS also needs the guard panic to be reached; an unwinding or pointer failure there makes them FAILED.
- Message risk: Kani `codegen_panic` (codegen/assert.rs 236-242) uses the constant message if it can extract it, else
  `This is a placeholder message; …`; core `assert!` gave the placeholder in DIRECT/ASSEMBLY. If the guard prints the
  placeholder, rows 4/6 do not meet the frozen lane gate (`_row_meets` matches description of located checks); the
  diagnostic classification then needs a log-grep `File:` line in `slice::sort::shared::smallsort::panic_on_ord_violation`
  for every failed check, else UNKNOWN. Expectations are not changed to SUCCESS or to the placeholder.

## Static (`check_panicprobe.py` → `static-check-prebuild.json` PASS)
Library delta exactly the two files; network.rs = base + the gated `mod` only. CLEANUP static source inventory
(imported, base archive vs head): ordinary 202 → 202 identical; controls-on 384 → 390, added exactly the six names,
removed none. PFC 36 unchanged (no `proof_for_contract`, other files byte-identical). No `kani::stub`/`kani::assume`/
`#[cfg` in panicprobe.rs; lines ≤ 100. rustfmt `--check` (edition 2024 wrapper) rc 0 for both files
(`rustfmt-check.txt`). Warnings: not compiled locally; the Build's compile output (`[-]> .*smallsort`) is the check.

## Request
`panicprobe/request.json` = `RUN-REQUEST.json`, sha256 d1dccfe467d7662408718abd91f9ce51e0228075e16f56aa27f6640c090dbe6b,
request_id `panicprobe-e1-diag-6roots-20261103`; kind diagnostic, agent k1-network, gcb-e2-standard-4 (k1-standard4),
controls true, kani_jobs 1, uninit_checks false, 10 min/row. `kani_k1.py validate --require-runner gcb-e2-standard-4
--max-total-minutes 720` rc 0: 6×`--harness`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`;
RUSTFLAGS `--cfg kani_smallsort_controls`.

## Budget / slots (`k1g.sh budget`, 2026-11-03T18:24Z, `budget-prebuild.txt`)
- Project: 206 builds, used $89.9475, reserved by unfinished $0.0000, cap $93.96.
- Reserve (6×10+30)×$0.0135 = $1.215 → used+reserve = $91.1625 ≤ $93.96. Own spent $0; $1.215 ≤ own cap $1.30.
  Compile-error repair only if own spent + reserve ≤ $1.30 (not possible after a full-envelope Build).
- Slots: 0 unfinished in project, none on k1-network; this Build makes 1 (WRAPEIGHT k1-merge may add 1, ≤ 2).
- Window: main 150 + closeout 30 min from T0; 90 min envelope fits main.
