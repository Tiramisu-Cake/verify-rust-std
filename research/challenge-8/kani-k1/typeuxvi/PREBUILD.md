# TYPEUXVI — PRE-BUILD packet (Runtime: Claude Code, one stage, one Build)

Task `TASK-TYPEUXVI.md` @ 940c761cdb. Branch `experiment/kani-k1-typeuxvi-20261104` from b1ff545720 (TYPESPLIT result:
v6 + `network::typematrix`, 22 roots) + cherry-pick 0cafef19cc of e0fda080f5 (cap $98.96, `k1g.sh` only). Owner
**k1-network**, slug typeuxvi. Tooling base for check-tooling: e0fda080f5 (lane files at HEAD = base). Locally only Git,
Python and the rustfmt wrapper; no cargo/rustc/Kani/CBMC.

## Library delta (commit bc38309fe9, separate)

Only `verify/network/typematrix.rs`: 29 lines appended after its 150 lines; the first 150 lines (22 roots, both macros,
`ArbitraryValue` impls, const asserts) are byte-identical (checked as a prefix). Appended, in order:
- a comment and a second `const _` block (x86_64/aarch64, as the existing one): `size_of::<u16>() == 2 &&
  align_of::<u16>() == 2`, `has_efficient_in_place_swap::<u16>()`, and `size_of::<u16>() *
  SMALL_SORT_NETWORK_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE` — the second condition of the network branch in
  `UnstableSmallSortFreezeTypeImpl for T: FreezeMarker + CopyMarker` (same pair as the `(u8, u32)` asserts), so the
  unstable route is `small_sort_network`; stable is `small_sort_general_with_scratch` (`T: FreezeMarker`);
- `impl ArbitraryValue for u16 { kani::any() }` (full domain; no other u16 impl in verify/);
- 7 invocations of the existing local macros, same stub `(super::super::super::panic_on_ord_violation,
  super::assume_order_violation)`, unwind 65, parent's `dispatch_safety_fixed` (scratch 48, `volatile_reading_less`).

No new macro/attribute/assume/contract/unsafe. typematrix.rs sha256
`7c9ad5b60afee5d4dc9626e534880d11d8ddbfebde49232b028b6fced196ddc8` (blob 84104dec55; base blob d0b31e14a9, 150 → 179
lines); network.rs and all other library files unchanged vs b1ff545720.

## Cells (type × route × length): u16 gets exactly the seven `(u8, u32)` v7-candidate shapes

| u16 root (`network::typematrix::…`) | Macro | Route | Lengths | Covers | `(u8, u32)` counterpart |
|---|---|---|---|---:|---|
| `dispatch_safety_stable_unstable_u16_n0_1_2_7_8` | pair | both | 0, 1, 2, 7, 8 | 11 | `…_u8u32_n0_1_2_7_8` |
| `dispatch_safety_stable_unstable_u16_n15_16_17` | pair | both | 15, 16, 17 | 7 | `…_u8u32_n15_16_17` |
| `dispatch_safety_unstable_u16_n9_12_13_18` | single | unstable | 9, 12, 13, 18 | 5 | `…_unstable_u8u32_n9_12_13_18` |
| `dispatch_safety_stable_u16_n31` / `_n32` | single | stable | 31 / 32 | 2 + 2 | `…_stable_u8u32_n31` / `_n32` |
| `dispatch_safety_unstable_u16_n31` / `_n32` | single | unstable | 31 / 32 | 2 + 2 | `…_unstable_u8u32_n31` / `_n32` |

24 distinct cells, each once: stable {0, 1, 2, 7, 8, 15, 16, 17, 31, 32}, unstable {0, 1, 2, 7, 8, 9, 12, 13, 15, 16, 17,
18, 31, 32} = the `(u8, u32)` candidates' cells (`cell_correspondence`, all `same_shape: true`). Covers: pair root =
`stable/unstable route normal return at N` per length + `dispatch family reached the end`; single root = `dispatch route
returns normally at N` per length + `dispatch safety family reached the end`. Total 31. Gate per root: SUCCESS, 0
failures, all covers (11, 7, 5, 2, 2, 2, 2). Scope as TYPEMATRIX: safety and normal return only, no sortedness/permutation.

## Request, static checks, budget

- `RUN-REQUEST.json` = `typeuxvi/request.json`, request_id `typeuxvi-meas-dispatch-u16-20261104`, sha256
  `8d2d6de9e47438e7940539171ea16a2d87d3ffe6bb172122df572b306ab9da9a`. measurement, k1-network, gcb-e2-standard-4,
  7 rows × 10 min, controls on, kani_jobs 1, uninit off, all expect SUCCESS. `kani_k1.py validate` rc 0: 7 × `--harness`,
  `--exact --harness-timeout 10m --jobs=1 --output-format=terse`, RUSTFLAGS `--cfg kani_smallsort_controls`.
- `check_typeuxvi.py` → `static-check-prebuild.json` **PASS**: library delta vs b1ff545720 = typematrix.rs only, old
  text a prefix; appended non-root text equals the expected const block + impl byte for byte; no
  macro_rules/`#[`/assume/PFC/unsafe; old 22 invocations unchanged, new 7 = expected (macro, name, type, literal,
  lengths); names by the CLEANUP static source inventory (base archive vs head): ordinary 202 → 202 identical;
  controls-on 406 → 413, added exactly the 7, removed none; PFC 36 unchanged (other files byte-identical, no
  `proof_for_contract`); lines ≤ 100; rustfmt `--check` (edition 2024 wrapper, fmtcfg) rc 0; lane files = e0fda080f5.
  Negative mutations (length 31 → 30; unwind 65 → 64 in an old line; align `==` → `>=`; `any_where` in the impl) FAIL.
- Warnings: not compiled locally; checked in the Build's compile output (`log-grep '[-]> .*smallsort'`).
- Budget (`budget-prebuild.txt`): builds 213, used $92.2830, reserved by unfinished $0.8100 (one unfinished build, not
  mine; owner not shown by `k1g.sh budget`). Reserve (7×10+30) × $0.0135 = **$1.350** ≤ own cap $1.40;
  92.283 + 0.81 + 1.35 = **$94.443 ≤ $98.96**. Re-checked before dispatch; if it no longer fits — stop, no reduced packet.
  Compile-error repair only if own spent + $1.350 ≤ $1.40, i.e. the failed Build cost ≤ $0.05.
- Wait: `k1g.sh wait` in a background task; window main 150 + closeout 30 min from T0 (actual dispatch).
