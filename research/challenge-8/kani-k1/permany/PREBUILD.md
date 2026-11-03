# PERMANY PRE-BUILD (G1 request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network, slug permany. Prepared 2026-11-03; T0 not started
(starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-permany-20261103`; base `e0fda080f5ea479d8f4fb801f4b42adde2b3259f` (library tree
  `d4ec476a7a001363e58f19948c188a9c2078e370`, v6); task commit `33895d18d7` (TASK-PERMANY.md sha256 11e19623…f289).
- Library commit **`b2cea32c407941c95199afb5a6f9393ca5710416`**: only `verify/network.rs` (+3, append
  `#[cfg(kani_smallsort_controls)] mod permany;`) and new `verify/network/permany.rs` (+61). Library diff vs base: 2 files,
  +64 −0. New library tree **`5e107678d01d8ec8a362f9b2719480104fde213d`**.
  network.rs blob 1a85a483 → a0b81b45 (sha256 dd3fb5c6…af8); the first bytes = whole base network.rs, byte-identical (`cmp`).
  permany.rs blob 1a086eb1 (sha256 ff2b6f10…13fe, 2490 B). smallsort.rs d1d7f552 unchanged; existing roots/helpers unchanged.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal tooling base e0fda080f5 (`git diff --stat` empty); `check-tooling BUILD
  e0fda080f5…` after the Build. Kissat only via `#[kani::solver(kissat)]`, as in PERMSOLVER (same image/setup).

## Route u64 N8 by source (smallsort.rs @ d1d7f552)
`<u64 as UnstableSmallSortTypeImpl>::small_sort` → FreezeMarker impl :90/:101 → `FreezeMarker + CopyMarker` impl :142 →
`has_efficient_in_place_swap::<u64>()` (size_of ≤ 8, :860) and 8·32 = 256 ≤ 4096 → `small_sort_network(v, is_less)` :164.
There len 8 ≥ 2, ≤ 32; `no_merge = len < 18` :330 true → region = whole v :333; region.len() 8 < 9 → presorted_len 1 →
`insertion_sort_shift_left(region, 1, is_less)` :349 → `if no_merge { return; }` :351. `bidirectional_merge` (:368, and
:286/:672 in other paths) is not reached, so `panic_on_ord_violation` (:832, only inside `bidirectional_merge`) is not on the
path. Insertion only moves elements by `insert_tail` gap copies, so the count claim must hold for every comparator answer.

## Source scope
`network::permany` is cfg-gated (opt-in only). `any_less(_a: &u64, _b: &u64) -> bool` returns a fresh `kani::any()` and
dereferences neither argument (read-only, no state; its two covers observe only the returned bool). Shared body
`permany_count_u64_n8::<const CORRUPT: bool>()`; roots `permany_u64_n8_default` (:45), `permany_u64_n8_kissat` (:52, + kissat),
`permany_u64_n8_value_loss_control` (:59, kissat, `CORRUPT = true` → `v[0] = v[1]` after the entry :30). All
`#[kani::proof] #[kani::unwind(25)]` = PERMSOLVER unwind (25 ≥ insert_tail/count loop bounds 7–8). No stub, summary, contract,
assume, `any_where`, width cut. Parent helpers `count_matching_values` (`==` on the full u64) / `prefix_unchanged` via `super::`,
private items of the parent are visible to the child → no visibility change.

## Body diff vs PERMSOLVER (`permany/body-diff.txt`, sha256 acaa85f1…c4d; `permany/body_diff.py`, reads git @a13389358a)
`permany_count_u64_n8` vs `posts::partposts_count_u64_n8` (= `solver::perm_arbitrary_kissat_u64_n8` minus solver/paths):
setup `v: [u64; 8] = any`, `pre = v`, `probe: u64 = any`, actual entry and the assert expression
`count(&pre, &probe) == count(&v, &probe)` are identical. Differences: proof attrs moved to the roots; `strict_less::<u64>` →
`any_less`; `if CORRUPT { v[0] = v[1]; }` before the assert; literal prefix `partposts` → `permany` (so the expect_check is
unique to this claim); + 2 probe covers. All 3 original covers kept. Pre-count is the count on the saved copy `pre`, as in
PERMSOLVER (not re-derived). Roots differ only by `#[kani::solver(kissat)]` (1 vs 2) and `::<true>` (3 vs 2).

## Asserts / covers (prefix `verify::network::permany::`)
Single assert :32 `permany: full-value count preserved`. Covers (7, gate 7/7 for rows 1–2): :16 `permany: comparator returned
true`, :17 `… returned false`, :36 `permany: probe hits the input` (count(pre) > 0), :37 `… probe misses the input` (= 0),
:38 `permany count: sort moves elements`, :39 `… sort returns normally at length 8`, :40 `… check reached the end`.
Control: v[0] = v[1] with probe = old v[0] ≠ v[1] drops count by one → only :32 can fail; covers are not gated for row 3.
Unexpected failure (UB, unwinding, other check) is not counted as intended-negative.

## Static (`cleanup/source_inventory.py` imported by a scratch script on base archive and HEAD; no report written)
- Ordinary 202 → 202, sorted-name sha256 d5d55502… at both. cfg-on 384 → 387. Exact delta +3 −0:
  `network::permany::{permany_u64_n8_default:45, permany_u64_n8_kissat:52, permany_u64_n8_value_loss_control:59}`, direct,
  gates [kani_smallsort_controls].
- PFC 36 unchanged: permany.rs has no `proof_for_contract` (text sites 27 = base); `integwrapfix/pfc_order.py` ordinary pfc
  sites 16 bad 0 at base and HEAD.
- rustfmt (TASK-DIRECT wrapper, `--edition 2024`, fmtcfg/rustfmt.toml) `--check` on network.rs, permany.rs: exit 0; no line
  > 100; `git diff --check` clean. All bindings used (`_a`/`_b` intentionally unused, `_`-prefixed); no new warnings expected.
  No local cargo/rustc/Kani/CBMC.

## Request (`kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`: 3 accepted)
`RUN-REQUEST.json` = `permany/g1.request.json`, request_id **permany-g1-anyless-u64n8-20261103**, sha256
**1b0ea6caaa87bda4920748d4eb31eadaedd6a2db1a3e97be04bc8ba292ba7cc3**. kind diagnostic, agent k1-network, gcb-e2-standard-4,
controls true (`--cfg kani_smallsort_controls`), kani_jobs 1, uninit off, 10 min/row; args `--exact --harness-timeout 10m
--jobs=1 --output-format=terse`. Rows: default SUCCESS, kissat SUCCESS, control FAILED expect_check
`permany: full-value count preserved`.

## Budget / slots / window (k1g.sh budget, 2026-11-03)
- Project: 209 builds, used $91.3380, reserved $0.0000, cap $98.96. + G1 reserve (3×10+30)×$0.0135 = **$0.810** →
  $92.148 ≤ $98.96. Own cap $0.90: one Build; no retry. One compile-error repair only if own spent + reserve ≤ $0.90.
- Slots: project ≤ 2 unfinished, k1-network ≤ 1 (CELLWRAP k1-merge may run). `k1g.sh budget` is re-run before dispatch.
- Window: T0 at dispatch; main 150 min, closeout 30 min.
