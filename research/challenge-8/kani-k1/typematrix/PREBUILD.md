# TYPEMATRIX — PRE-BUILD packet (Runtime: Claude Code, one stage, one Build)

Task `TASK-TYPEMATRIX.md` @ 539ce4dc8d. Branch `experiment/kani-k1-typematrix-20261103` from e8e238db9d (v6 library tree
+ K-1 tooling + cap 93.96). Owner k1-merge, slug typematrix. Tooling base for check-tooling: e8e238db9d (lane files at
HEAD = base, `git diff --stat` empty). Locally only Git, Python and the rustfmt wrapper; no cargo/rustc/Kani/CBMC.

## Routes by source (`shared/smallsort.rs` in this tree)

All three types are `Freeze` (stable: `StableSmallSortTypeImpl` FreezeMarker impl → `small_sort_general_with_scratch`
with the harness's `[MaybeUninit<T>; 48]`) and `Copy` (unstable: FreezeMarker impl → `UnstableSmallSortFreezeTypeImpl`
for `FreezeMarker + CopyMarker`, lines 142-170). `has_efficient_in_place_swap` = `size_of <= 8` (line 858).

| Type | size / align | unstable condition | unstable route | general presort at len ≥ 16 |
|---|---|---|---|---|
| `(u8, u32)` | 8 / 4, 3 padding bytes | `8 <= 8` and `8 × 32 = 256 <= 4096` | `small_sort_network` | sort8 (8 ≤ 16) |
| `u128` | 16 / 16 | `16 > 8`; `16 × 48 = 768 <= 4096` | `small_sort_general` (stack `MaybeUninit<[u128; 48]>`) | sort8 (16 ≤ 16) |
| `[u8; 9]` | 9 / 1 | `9 > 8`; `9 × 48 = 432 <= 4096` | `small_sort_general` | sort8 (9 ≤ 16) |

Matches the task table. General (both routes but unstable `(u8, u32)`): len < 2 return; 2..7 presort 1; 8..15 sort4 ×2;
≥ 16 sort8 ×2; then `insert_tail` and `bidirectional_merge` from scratch. Network `(u8, u32)`: 2, 7, 8 insertion
offset 1; 9, 12 sort9 (+ tails); 13, 15, 16, 17 sort13 (+ tails); 18, 31, 32 halves (9/9, 15/16, 16/16) then merge
through the stack `MaybeUninit<[T; 32]>`. The module checks this layout and both route predicates with nine const
`assert!`s under `if cfg!(any(target_arch = "x86_64", target_arch = "aarch64"))` (no `#[cfg]`: the static source
inventory accepts only known cfg gates). `repr(Rust)` tuple layout is stated as target/toolchain fact, not language
guarantee; `[u8; 9]` is guaranteed.

## Library delta (separate commit)

- `network.rs`: +3 lines after the `use` block: `#[cfg(kani_smallsort_controls)]` / `mod typematrix;` / blank.
- New `verify/network/typematrix.rs` (133 lines): const assertions; `ArbitraryValue` for `(u8, u32)` =
  `(kani::any(), kani::any())` and `u128` = `kani::any()` (no zeroing, padding never read); `[u8; 9]` uses the parent's
  `impl<const M: usize> ArbitraryValue for [u8; M]`; copies of the two macros; 10 invocations.
- Parent macros cannot be invoked here: their stub path `super::super::panic_on_ord_violation` resolves at the call
  site (one module deeper it names `verify::panic_on_ord_violation`, which does not exist). Semantic diff
  (`macros.diff`, 49 vs 49 compared lines, classified by `check_typematrix.py`, `macro_unexplained: []`): the only
  changed line, twice, is the stub `(super::super::panic_on_ord_violation, assume_order_violation)` →
  `(super::super::super::panic_on_ord_violation, super::assume_order_violation)` — the same two functions (ZSTPROBE
  used this exact form). Body, covers, `any_where`, match arms, unwind 65 identical; the pair macro's doc line kept.
  The body calls the parent's `dispatch_safety_fixed` (imported, not copied): real `<T as Stable/UnstableSmallSortTypeImpl>
  ::small_sort`, scratch 48, `volatile_reading_less::<T>`. No summaries, contracts, assumptions or other stubs.

## Roots (`slice::sort::shared::smallsort::verify::network::typematrix::`), all expect SUCCESS

| # | Root | Macro | Type | Lengths | Covers |
|---:|---|---|---|---|---:|
| 1 | `dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8` | pair | `(u8, u32)` | 0,1,2,7,8 | 11 |
| 2 | `dispatch_safety_stable_unstable_u8u32_n15_16_17` | pair | `(u8, u32)` | 15,16,17 | 7 |
| 3 | `dispatch_safety_stable_unstable_u8u32_n31_32` | pair | `(u8, u32)` | 31,32 | 5 |
| 4 | `dispatch_safety_stable_unstable_u128_n0_1_2_7_8` | pair | `u128` | 0,1,2,7,8 | 11 |
| 5 | `dispatch_safety_stable_unstable_u128_n15_16_17` | pair | `u128` | 15,16,17 | 7 |
| 6 | `dispatch_safety_stable_unstable_u128_n31_32` | pair | `u128` | 31,32 | 5 |
| 7 | `dispatch_safety_stable_unstable_bytes9_n0_1_2_7_8` | pair | `[u8; 9]` | 0,1,2,7,8 | 11 |
| 8 | `dispatch_safety_stable_unstable_bytes9_n15_16_17` | pair | `[u8; 9]` | 15,16,17 | 7 |
| 9 | `dispatch_safety_stable_unstable_bytes9_n31_32` | pair | `[u8; 9]` | 31,32 | 5 |
| 10 | `dispatch_safety_unstable_u8u32_n9_12_13_18` | single, `false` | `(u8, u32)` | 9,12,13,18 | 5 |

Pair covers: `stable route normal return at n` + `unstable route normal return at n` per length + `dispatch family
reached the end`; single: `dispatch route returns normally at n` per length + `dispatch safety family reached the end`.
Total 74. Gate per root: SUCCESS, 0 failures, all covers. Family roots may TIMEOUT; no split after the result.

## Request, static checks, budget

- `RUN-REQUEST.json` = `typematrix/request.json`, request_id `typematrix-meas-dispatch-u8u32-u128-bytes9-20261103`,
  sha256 `b122e59d9848a77fdb78b33ad5336cd57d912782204a0dbb47697a6c8f3d0b5d`. measurement, k1-merge, gcb-e2-standard-4,
  10 rows × 10 min, controls on, kani_jobs 1, uninit off. `kani_k1.py validate` rc 0: 10 × `--harness`, `--exact
  --harness-timeout 10m --jobs=1 --output-format=terse`, RUSTFLAGS `--cfg kani_smallsort_controls`.
- `check_typematrix.py` → `static-check-prebuild.json` **PASS**: library delta = network.rs (+ exactly the gated mod
  line) and typematrix.rs; macro diff explained; roots/types/lengths/covers parsed; names by the CLEANUP static source
  inventory (imported, base archive vs head): ordinary 202 → 202 identical; controls-on 384 → 394, added exactly the
  10, removed none. PFC 36 unchanged: other files byte-identical, typematrix.rs has no `proof_for_contract`. No `#[cfg`,
  `kani::assume`, `stub_verified`, solver attribute; lines ≤ 100. rustfmt `--check` (edition 2024 wrapper, fmtcfg) rc 0
  for network.rs and typematrix.rs.
- Warnings: not compiled locally; the Build's compile output is the check (`log-grep '[-]> .*smallsort'`).
- Hashes: typematrix.rs sha256 `34b6e3790ea34a27aab3f59d8ba12e974a5525504a20f184efac54beb4b96a95`; network.rs sha256
  `33550fa79ccc8340f7201bf5d641248f1cce727c524d43ecebdca1672dd6f798` (base blob 1a85a483b1).
- Budget: reserve (10×10+30) × $0.0135 = **$1.755** ≤ own cap $1.80. `k1g.sh budget` now: builds 205, used $89.0700,
  reserved by unfinished $1.7550 (another owner's Build, one unfinished); + mine $92.5800 ≤ $93.96. Slots: mine makes
  2 ≤ 2; k1-merge has none per this stage (coordinator confirms owner of the unfinished one). The one compile-error repair
  is reachable only if the failed Build costs ≤ $0.045 (own spent + $1.755 ≤ $1.80): in practice no repair.
- Wait: `k1g.sh wait` in a background task; window main 150 + closeout 30 min from T0 (actual dispatch).
