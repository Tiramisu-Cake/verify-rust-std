# UNSTABLEZST — PRE-BUILD packet (Runtime: Claude Code, one stage, one Build)

Task `TASK-UNSTABLEZST.md` @ 898c1b7baa. Branch `experiment/kani-k1-unstablezst-20261103` from 5fc77d446f (ZSTPROBE
result: v6 + tooling e8e238db9d + opt-in `network::zstprobe`). Owner k1-merge, slug unstablezst. Tooling base for
check-tooling: e8e238db9d. Locally only Git, Python and the rustfmt wrapper; no cargo/rustc/Kani/CBMC.

## Library delta (commit c6c78658f7, separate)

Only `verify/network/zstprobe.rs`: +9 lines (blank, 2 comment lines, 6 one-line invocations) right after the
`zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32` invocation. Nothing else in the file or the library changes:
existing roots, both `dispatch_safety_fixed`, `volatile_reading_less`, `comparators.rs`, `network.rs` are unchanged.
The new roots reuse ZSTPROBE's local `dispatch_safety_cases!` + `dispatch_safety_fixed` (comparator
`zst_aware_less::<T>` in both branches); the whole module is behind `#[cfg(kani_smallsort_controls)] mod zstprobe;`.

| # | Root (`verify::network::zstprobe::`) | Invocation | Covers | Expect |
|---|---|---|---:|---|
| 1 | `zst_unstable_dispatch_aware_n8_9_12_13_17` | `dispatch_safety_cases!(…, (), false, [8, 9, 12, 13, 17])` | 6 | SUCCESS |
| 2–6 | `zst_unstable_dispatch_aware_n8` / `_n9` / `_n12` / `_n13` / `_n17` | same with `[n]` | 2 each | SUCCESS |

Each root: stub `panic_on_ord_violation → assume_order_violation` (the parent's fns, one module deeper), unwind 65,
`len = any_where(matches!(l, …))`, `match len { n => dispatch_safety_fixed::<(), n, false>(), _ => {} }`, one cover
`dispatch route returns normally at n` per length + `dispatch safety family reached the end` — exactly the original's
covers for its length list. Actual `<() as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut zst_aware_less::<()>)`;
the unstable call takes no scratch (the stable branch, dead at `STABLE = false`, still builds its scratch as in the
original). No other stubs, assumptions or contracts.

## Root 1 semantic diff against `network::dispatch_safety_unstable_zst_n8_9_12_13_17` (`root1.diff`)

Compared: `dispatch_safety_fixed` + `macro_rules! dispatch_safety_cases` + the invocation (37 vs 33 lines).
Every hunk is classified by `check_unstablezst.py` (`root1_unexplained: []`):
1. **comparator** in the live unstable branch: `volatile_reading_less::<T>` → `zst_aware_less::<T>` — the only semantic
   change. For `T = ()` it differs from the original by `ptr::read` instead of `ptr::read_volatile` on both arguments
   and by the function type `F`; it still returns `kani::any()`. Same in the dead stable call (rustfmt joins it, −4 lines);
2. module depth: `use super::super::{…}` → `super::super::super::{…}` and stub
   `(super::super::panic_on_ord_violation, assume_order_violation)` → `(super::super::super::…, super::assume_order_violation)`
   — the same two functions;
3. root name. Type `()`, `false`, `[8, 9, 12, 13, 17]`, `any_where`, match arms, cover texts, unwind 65 identical.
   The original's `#[cfg(kani_smallsort_controls)]` on the invocation is inherited here from the `mod zstprobe` gate.
Roots 2–6 are root 1's invocation with the list narrowed to `[n]` (checked textually).

## Unstable route for `()` by source (`shared/smallsort.rs` in this tree)

- `() : Freeze + Copy` → `UnstableSmallSortTypeImpl` (FreezeMarker impl) → `UnstableSmallSortFreezeTypeImpl` for
  `FreezeMarker + CopyMarker`. `has_efficient_in_place_swap::<()>()` = `0 <= 8` and `0 * 32 <= 4096` → **`small_sort_network`**
  on every length (threshold 32; no general/fallback branch).
- `small_sort_network`: `len ≥ 2`, `len ≤ 32` (no abort); `no_merge = len < 18` is **true for all five lengths** → one
  pass with `region = v[..len]`, then `return` before `bidirectional_merge`: the `[MaybeUninit<()>; 32]` stack array is
  declared but never used. All comparator references point into `v` (a local `[(); N]`).

| len | presort | `insertion_sort_shift_left(region, offset)` | comparator calls (`swap_if_less` / `insert_tail`) |
|---:|---|---|---|
| 8 | none (`presorted_len = 1`) | offset 1: `insert_tail` for tails 1..7 | 0 / 7 tails, each 1..k calls |
| 9 | `sort9_optimal` (25 `swap_if_less`) | offset 9 = len: loop body never runs | 25 / 0 |
| 12 | `sort9_optimal` on `v[..12]` (sorts 0..8) | offset 9: tails 9..11 | 25 / 3 tails |
| 13 | `sort13_optimal` (45 `swap_if_less`) | offset 13 = len: none | 45 / 0 |
| 17 | `sort13_optimal` | offset 13: tails 13..16 | 45 / 4 tails |

`swap_if_less` (two `add`, one comparison, `select_unpredictable`, `ptr::read`, `ptr::copy`, `copy_nonoverlapping`) and
`insert_tail` (`tail.read()`, `CopyOnDrop` gap guard, `copy_nonoverlapping`) touch only `v`. With `add` the identity on a
ZST, every reference aliases `v`'s base. No `read_volatile` remains on these paths once the comparator is
`zst_aware_less` (for ZST it takes the `ptr::read` arm) — the ZSTPROBE class-(c) volatile failures cannot occur.
Expected cost driver: the `insert_tail` loops with `any` comparator results (len 8: up to 28 calls; 12: 25 + up to 30; 17: 45 + up to 58).

## Request, static checks, budget

- `RUN-REQUEST.json` = `unstablezst/request.json`, request_id `unstablezst-meas-zst-unstable-dispatch-aware-20261103`,
  sha256 0507b71351a78af507cee9fcf0fbde27b9e1fa473c6e8d9923f4262390c108dc. kind **measurement**, agent k1-merge,
  gcb-e2-standard-4, 6 rows × 10 min, controls on, kani_jobs 1, uninit off, all expect SUCCESS. `kani_k1.py validate`
  rc 0; args 6 × `--harness`, `--exact --harness-timeout 10m --jobs=1 --output-format=terse`, RUSTFLAGS
  `--cfg kani_smallsort_controls`.
- `check_unstablezst.py` → `static-check-prebuild.json` **PASS**: library delta vs 5fc77d446f = zstprobe.rs only, and
  zstprobe.rs = base + exactly the inserted block after the stable aware invocation; root-1 diff explained; name sets by
  the CLEANUP static source inventory (imported, base archive vs head): ordinary 202 → 202, identical; controls-on
  388 → 394, added exactly the 6 roots, removed none; original `dispatch_safety_unstable_zst_n8_9_12_13_17` still present.
  PFC 36 unchanged: every other library file is byte-identical to the base and zstprobe.rs has no `proof_for_contract`.
  Stubs only the existing pair; no `kani::assume`; lines ≤ 100. rustfmt `--check` (edition 2024 wrapper) rc 0 for
  zstprobe.rs and network.rs.
- Warnings: not compiled locally. The block adds only macro invocations already used in this module (with one-length
  lists `matches!(l, 8)` / `match len { 8 => …, _ => {} }`: no unreachable-pattern or unused item); the Build's compile
  output is the check.
- Hashes: zstprobe.rs sha256 `91ceefc21a0a51eec1fb8b930b17cd7591b6899e17700d5521932066115f7aaa`; network.rs blob `37d4da2bf9963a746afaa908e5e662104b9a8e34` (= base).
- Budget: reserve (6×10+30) × $0.0135 = **$1.215** ≤ own cap $1.30. `k1g.sh budget` before dispatch: builds 201, used
  $88.0575, reserved $0, unfinished 0; after reserve $89.2725 ≤ $93.96. Project ≤ 2 unfinished, ≤ 1 on k1-merge: holds
  (CELLSPLIT on k1-network may run in parallel). One Build; one compile-error repair only if own spent + reserve ≤ $1.30
  (i.e. the failed Build cost ≤ $0.085). Wait: `k1g.sh wait` in the background.

## Gate (after the Build)

Root SUCCESS, 0 failures, all covers. Root 1 → v7 candidate only with SUCCESS, 6/6 covers and VT ≤ 300 s; otherwise the
full set of successful per-length roots with the same threshold. The old volatile root stays TIMEOUT, counted apart.
