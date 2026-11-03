# TYPESPLIT — PRE-BUILD packet (Runtime: Claude Code, one stage, one Build)

Task `TASK-TYPESPLIT.md` @ 18226e9c6e. Branch `experiment/kani-k1-typesplit-20261103` from 0d33d29f0e (TYPEMATRIX result:
v6 + tooling e8e238db9d + opt-in `network::typematrix`). Owner k1-network, slug typesplit. Tooling base for check-tooling:
e8e238db9d (lane files at HEAD = base). Locally only Git, Python and the rustfmt wrapper; no cargo/rustc/Kani/CBMC.

## Library delta (commit d0589867b9, separate)

Only `verify/network/typematrix.rs`: 17 lines appended after its 133 lines (comment + 12 invocations of the existing
local `dispatch_safety_cases!`). The first 133 lines — 10 roots, both macros, `ArbitraryValue`, const asserts — are
byte-identical (checked as a prefix). Every new root: single route, one length, same stub
`(super::super::super::panic_on_ord_violation, super::assume_order_violation)`, unwind 65, parent's
`dispatch_safety_fixed` (scratch 48, `volatile_reading_less`). No new macro/impl/attribute/assume/contract.
typematrix.rs sha256 `80ee35d1fde33a342cb596df5f7032ec24748238aa2d87a0d9a9e1b22978cf24` (base blob e8a693a869, 133 → 150
lines); network.rs and all other library files unchanged vs 0d33d29f0e.

## Cell correspondence (type × route × length)

| Pair root (TYPEMATRIX, unchanged) | VT s | Cells | Split roots (`dispatch_safety_…`) |
|---|---:|---|---|
| `stable_unstable_u8u32_n31_32` | 538.3 | stable·31, unstable·31, stable·32, unstable·32 | `stable_u8u32_n31`, `stable_u8u32_n32`, `unstable_u8u32_n31`, `unstable_u8u32_n32` |
| `stable_unstable_u128_n31_32` | 452.5 | same four | `stable_u128_n31`, `_n32`, `unstable_u128_n31`, `_n32` |
| `stable_unstable_bytes9_n31_32` | 532.8 | same four | `stable_bytes9_n31`, `_n32`, `unstable_bytes9_n31`, `_n32` |

Per type the four split roots cover exactly the pair root's four cells, each once (`cell_correspondence`, all
`equal_cells: true`). Routes as in TYPEMATRIX (const asserts): stable → `small_sort_general_with_scratch`; unstable →
`small_sort_network` for `(u8, u32)`, `small_sort_general` for u128 and `[u8; 9]`.

Covers. Pair root (5): `stable route normal return at 31`, `unstable … at 31`, `stable … at 32`, `unstable … at 32`
(per route: the `stable` bool selects the route) + `dispatch family reached the end`. Split root (2): `dispatch route
returns normally at N` (per length; the route is fixed by the `$stable` literal, so the cover is on `len == N`) +
`dispatch safety family reached the end`. 12 × 2 = 24 covers; with one length `len == N` is the only allowed value, so
both covers just witness that the single route's normal return is reachable. Gate per root: SUCCESS, 0 failures, 2/2.

## Request, static checks, budget

- `RUN-REQUEST.json` = `typesplit/request.json`, request_id `typesplit-meas-dispatch-n31-n32-route-split-20261103`,
  sha256 `2f5b88dc980dcdb033d090c8dbd71110c9d8dc89bb0f3c88490897c8ab294390`. measurement, k1-network, gcb-e2-standard-4,
  12 rows × 10 min, controls on, kani_jobs 1, uninit off, all expect SUCCESS. `kani_k1.py validate` rc 0: 12 ×
  `--harness`, `--exact --harness-timeout 10m --jobs=1 --output-format=terse`, RUSTFLAGS `--cfg kani_smallsort_controls`.
- `check_typesplit.py` → `static-check-prebuild.json` **PASS**: library delta vs 0d33d29f0e = typematrix.rs only, old
  text a prefix, appended part has no macro/impl/assert/attribute/`fn`/`use`/assume/PFC; old 10 invocations unchanged,
  new 12 = expected (name, type, literal, [len]); names by the CLEANUP static source inventory (base archive vs head):
  ordinary 202 → 202 identical; controls-on 394 → 406, added exactly the 12, removed none; PFC 36 unchanged (other files
  byte-identical, no `proof_for_contract`); lines ≤ 100; rustfmt `--check` (edition 2024 wrapper, fmtcfg) rc 0; lane
  files = e8e238db9d. Negative mutations (a wrong length; unwind 65 → 64 in an old line) make it FAIL.
- Warnings: not compiled locally; checked in the Build's compile output (`log-grep '[-]> .*smallsort'`).
- Budget (`budget-prebuild.txt`): builds 208, used $90.1365, reserved by unfinished $0.9450 (one unfinished, not mine;
  WRAPEIGHT k1-merge expected — coordinator confirms owner). Reserve (12×10+30) × $0.0135 = **$2.025** ≤ own cap $2.05;
  90.1365 + 0.945 + 2.025 = **$93.1065 ≤ $93.96**. Slots: with mine 2 ≤ 2 unfinished, k1-network 1 ≤ 1. Re-checked
  before dispatch; if it no longer fits — stop, no reduced packet. Compile-error repair only if the failed Build cost
  ≤ $0.025 (own spent + $2.025 ≤ $2.05): in practice no repair.
- Wait: `k1g.sh wait` in a background task; window main 150 + closeout 30 min from T0 (actual dispatch).
