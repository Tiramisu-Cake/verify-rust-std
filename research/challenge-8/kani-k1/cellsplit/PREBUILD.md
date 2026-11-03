# CELLSPLIT PRE-BUILD G1 (G1/G2/G3 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network, slug cellsplit. Prepared 2026-11-03 ~16:10Z; T0 not
started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-cellsplit-20261103`; base = tooling base `e8e238db9d87323fa4da011a1a8b37fb76ec91c0`;
  task commit `ea89483576ec80e0f13fa62c4d31279def3b4a71` (TASK-CELLSPLIT.md sha256 2dc13113…1b96).
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = at e8e238db (v6). No library commit in this stage:
  `git diff e8e238db HEAD` touches only research files (task + cellsplit/ + RUN-REQUEST.json).
  network.rs blob `1a85a483b16449485a02c4e1140033c8a22956fa` (sha256 d3d0047b…7f7a); smallsort.rs sha256 78fc8fe8…ed61.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal tooling base e8e238db (`git diff --stat` empty). Kani
  `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12. `check-tooling BUILD e8e238db9d87…` after each Build.

## Requests (all three validated: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`)
| File | request_id | rows | sha256 |
|---|---|---:|---|
| cellsplit/g1.request.json = RUN-REQUEST.json (this commit) | cellsplit-g1-measure-cell-n11-15-split7-20261103 | 7 | 6abdc9befbfdc7dcc19d605c80e3ea0224354bee878b5c82913144d0f896b79a |
| cellsplit/g2.request.json (to RUN-REQUEST.json only in the G2 commit) | cellsplit-g2-measure-cell-n16-17-split9-20261103 | 9 | 4c1e9ce6829a7cc9ff7b9ead8f04fd61b8bbdc3ac09d0f5b76212e8b6937a998 |
| cellsplit/g3.request.json (to RUN-REQUEST.json only in the G3 commit) | cellsplit-g3-measure-cell-n18-19-split10-20261103 | 10 | 61b78853f42661e9c8a823be3e03f51b5b46ae63323734f59df9b27de6cd5ee7 |

All: kind measurement, agent k1-network, runner gcb-e2-standard-4 (pool k1-standard4, 4 vCPU/16 GiB, swap off), controls
true (rustflags `--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false, harness_timeout_minutes 10, each row
expect SUCCESS. Validator args: N×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`,
`--output-format=terse`. Names exactly as the task table (prefix `slice::sort::shared::smallsort::verify::network::`).
No highmem/resource kind/solver flags/instrumentation/list preparation. Tool unit tests 82 OK (python only).
Not taken (per task): `*_offset1` singles, `n13_to15`, `n15`, wide `n11_to15`/`n16_to20`.

## Source inventory (network.rs; all 26 roots gated `#[cfg(kani_smallsort_controls)]`; `verify` is `#[cfg(kani)]`)
| Pkt | Root (cell_…) | Line | Macro | Lengths | Offsets | unwind | Required covers |
|---|---|---:|---|---|---|---:|---:|
| G1 | n11_to12 | 637 | mutating_insertion_cases (602) | 11,12 | any 1..=N | 35 | 8 |
| G1 | n13 / n14 | 646 / 648 | same | 13 / 14 | any 1..=N | 35 | 5 / 5 |
| G1 | n15_offsets1_to4, 5_to8, 9_to12, 13_to15 | 750-771 | insertion_offset_group_cases (714, cell arm 731) | 15 | 4,4,4,3 listed | 35 | 6,6,6,5 |
| G2 | n16_offsets1_to4, 5_to8, 9_to12, 13_to16 | 778-799 | same | 16 | 4,4,4,4 | 35 | 6,6,6,6 |
| G2 | n17_offsets1_to4, 5_to8, 9_to12, 13_to15, 16_to17 | 806-834 | same | 17 | 4,4,4,3,2 | 35 | 6,6,6,5,4 |
| G3 | n18_offsets1_to4, 5_to8, 9_to12, 13_to16, 17_to18 | 841-869 | same | 18 | 4,4,4,4,2 | 35 | 6,6,6,6,4 |
| G3 | n19_offsets1_to4, 5_to8, 9_to12, 13_to16, 17_to19 | 876-904 | same | 19 | 4,4,4,4,3 | 35 | 6,6,6,6,5 |

Partition (parsed from source, all group cell arms carry `#[cfg(kani_smallsort_controls)]`): for each N∈{15..19} the listed
offset groups are disjoint and their union is exactly 1..=N — no gap, no overlap. N11..14 come from mutating_insertion_cases
roots with the full `any_where(1 <= o <= N)` offset domain. Together the 26 rows cover every (N, offset) with N∈11..19.

Shared semantics with the wide root `mutating_insertion_safety_cell_n11_to15` (629) / `n16_to20` (631), unchanged:
`tagged_values::<N>()` (549: `[Cell<TaggedKey>; N]`, each key and tag `kani::any()`), comparator `&mut mutating_key_order`
(534-547: volatile reads of both Cells, writes arbitrary new keys keeping tags, returns `kani::any()`), call
`insertion_at::<_, _, O>` (466) = `insertion_sort_shift_left(v, O, cmp)` with constant O, `#[kani::unwind(35)]`. No stub,
no assumed order, no sorted-prefix premise, no fn-pointer coercion; same type and backing.
Expected differences (listed, not discrepancies):
- n11_to12/n13/n14: same macro and `mutating_insertion_fixed` body (594-600) as the wide root, fewer lengths. Covers: per
  length + family end + per length "offset one"/"final offset" + comparator → 2+1+4+1 = 8; 1+1+2+1 = 5.
- Offset groups: single fixed N; `const { assert!(1 <= o <= N) }`; offset `any_where(matches!(o, listed))`; match arm per
  listed offset, `_ => unreachable!()` (excluded by the assumption; wide root has `_ => {}` with `if N >= k` guards). Covers:
  one per listed offset ("mutating insertion offset k") + "mutating insertion offset group returns normally" + comparator
  "mutating comparator changes both keys" → k+2. No per-length or "offset one/final offset" covers; offsets 1 and N appear as
  per-offset covers of their groups.
- Comparator cover is non-generic (one instance per root). History, not a baseline: n11_to12 8/8 in c3b/heavy6-before-j3
  (earlier source, jobs3, 210.4 s); n14, n16_offsets1_to4, n17_offsets5_to8, n18_offsets9_to12 SUCCESS in c3b ordinary
  timings (earlier source afea78b3). No current-tree GCB data for any of the 26.

## Ordinary preservation
None of the 26 names is in macsplit/ordinary-expected.txt (202; it has Cell n1_to5 and five n20 offset groups). Ordinary 202 /
PFC 36, static cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted). Library, harnesses, covers,
workflows, tooling unchanged.

## Budget / slots / window (k1g.sh budget, 2026-11-03 ~16:05Z)
- Project: 201 builds, used $88.0575, reserved by unfinished $0.0000, cap $93.96.
- G1 reserve (7×10+30)×$0.0135 = $1.350 → $88.0575+$0+$1.350 = $89.4075 ≤ $93.96. Own spent $0 + $1.350 ≤ own cap $3.60.
  G2 $1.620 / G3 $1.755 rechecked before each dispatch against actual G1/G2 accounting (sum of max reserves $4.725 > $3.60).
- Slots: 0 unfinished in project now; G1 makes project 1 (≤2), k1-network 1 (≤1). UNSTABLEZST (k1-merge) may run in parallel.
- Window: T0 at G1 dispatch; main 300 min + closeout 30. G2 needs ≥ 110 min left of main, G3 ≥ 120 min; otherwise not run.
- No retry; only the one compile-error repair exception per stage with new review/GO. Status 6 on ≥ 4/7 G1 rows → stop
  before G2 and report.

## G2 PRE-BUILD (after G1 terminal/accounting, 2026-11-03 ~16:35Z)
- G1 37bbcae6 terminal SUCCESS, 7/7 rows accepted, cost $0.2430 (cellsplit/g1.result.md). No status 6, no compile/setup error.
- RUN-REQUEST.json := cellsplit/g2.request.json (sha256 4c1e9ce6829a7cc9ff7b9ead8f04fd61b8bbdc3ac09d0f5b76212e8b6937a998),
  re-validated (9 rows); library tree d4ec476a and lane files unchanged since 24c93e8d (only research files change).
- Required covers G2 (from source inventory above): n16 groups 6,6,6,6; n17 groups 6,6,6,5,4.
- Budget: project 203 builds, used $88.3005, reserved by unfinished $1.2150 (another owner's build) → + G2 $1.620 =
  $91.1355 ≤ $93.96. Own spent $0.2430 + G2 reserve $1.620 = $1.863 ≤ $3.60 (G3 $1.755 rechecked after G2 accounting).
- Slots: 1 unfinished in project (not k1-network); G2 makes 2 (≤2), k1-network 1 (≤1).
- Window: T0 16:11:14Z, main ends 21:11Z; ~276 min left ≥ 9×10+20 = 110 min.

## G3 PRE-BUILD (after G2 terminal/accounting, 2026-11-03 ~16:56Z)
- G2 f77274f7 terminal SUCCESS, 9/9 rows accepted, cost $0.2295 (cellsplit/g2.result.md). No status 6, no setup error.
- RUN-REQUEST.json := cellsplit/g3.request.json (sha256 61b78853f42661e9c8a823be3e03f51b5b46ae63323734f59df9b27de6cd5ee7),
  re-validated (10 rows); library tree d4ec476a and lane files unchanged since d3a639c2 (only research files change).
- Required covers G3 (source inventory above): n18 groups 6,6,6,6,4; n19 groups 6,6,6,6,5.
- Budget: project 204 builds, used $88.5300, reserved by unfinished $1.2150 (UNSTABLEZST, k1-merge) → + G3 $1.755 =
  $91.5000 ≤ $93.96. Own spent $0.2430 + $0.2295 = $0.4725 + G3 reserve $1.755 = $2.2275 ≤ $3.60. G3 is the last packet.
- Slots: 1 unfinished in project (k1-merge); G3 makes 2 (≤2), k1-network 1 (≤1).
- Window: T0 16:11:14Z, main ends 21:11Z; ~255 min left ≥ 10×10+20 = 120 min.
