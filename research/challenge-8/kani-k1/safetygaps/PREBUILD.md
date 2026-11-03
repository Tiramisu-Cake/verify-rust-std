# SAFETYGAPS PRE-BUILD G1 (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network, slug safetygaps. Prepared 2026-11-03; T0 not started
(starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.
G1 dispatch additionally waits for terminal/accounting of DIRECTBOUNDS (same owner k1-network).

## Identities
- Branch `experiment/kani-k1-safetygaps-20261103`; base = tooling base `e8e238db9d87323fa4da011a1a8b37fb76ec91c0`;
  task commit `972d8c0b098d1d4bfc87b0ab2e33cd5851f668d5` (TASK-SAFETYGAPS.md sha256 24bd5b84…0fe0c).
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = at e8e238db = at MACSPLIT 4f403452 (v6).
  No library commit in this stage: `git diff e8e238db HEAD` touches only research files (task + safetygaps/ + RUN-REQUEST.json).
  network.rs blob `1a85a483b16449485a02c4e1140033c8a22956fa` (sha256 d3d0047b…7f7a); smallsort.rs sha256 78fc8fe8…ed61.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal tooling base e8e238db (`git diff --stat` empty); e8e238db vs frozen
  30f77e85 differs only in k1g.sh CAP_USD 88.96→93.96 (+comment). Kani `9461e07af7ec929f050aa4192f29363c9be07779`,
  nightly-2026-10-12 (tool_config/kani-version.toml). `check-tooling BUILD e8e238db9d87…` after each Build.

## Requests (both validated: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`)
| File | request_id | sha256 |
|---|---|---|
| safetygaps/g1.request.json = RUN-REQUEST.json (this commit) | safetygaps-g1-measure-dispatch-bytes85-zst-20261103 | d0bd35e51f8cdb6aaec5f0b9513719505f63a4d2817f141e7b3e33be41d9436d |
| safetygaps/g2.request.json (to RUN-REQUEST.json only in the G2 commit) | safetygaps-g2-measure-cell-insertion-n6-20-20261103 | 7caeb8f1e90edbde31d68a0de416491864edd580055831e53415d99943f23dc2 |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 (pool k1-standard4, 4 vCPU/16 GiB, swap off),
controls true (rustflags `--cfg kani_smallsort_controls`), kani_jobs 1, uninit_checks false, harness_timeout_minutes 10,
3 rows each, expect SUCCESS. Validator args: 3×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`,
`--output-format=terse`. No highmem/resource kind/solver flags/instrumentation/list preparation. Tool unit tests 82 OK.

## Source inventory (network.rs; all six roots gated `#[cfg(kani_smallsort_controls)]`; `verify` is `#[cfg(kani)]`)
| Pkt | Root | Line | Macro (line) | cfg | stub | unwind | Required covers |
|---|---|---:|---|---|---|---:|---:|
| G1 | dispatch_safety_stable_unstable_bytes85_n31 | 454 | dispatch_pair_safety_cases (312) | controls | panic_on_ord_violation→assume_order_violation | 65 | 3 |
| G1 | dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32 | 296-301 | dispatch_safety_cases (264) | controls | same | 65 | 11 |
| G1 | dispatch_safety_unstable_zst_n8_9_12_13_17 | 303 | dispatch_safety_cases (264) | controls | same | 65 | 6 |
| G2 | mutating_insertion_safety_cell_n6_to10 | 627 | mutating_insertion_cases (602) | controls | none | 35 | 17 |
| G2 | mutating_insertion_safety_cell_n11_to15 | 629 | same | controls | none | 35 | 17 |
| G2 | mutating_insertion_safety_cell_n16_to20 | 631 | same | controls | none | 35 | 17 |

Cover inventory (reachable `kani::cover` sites; none in library sort bodies, `grep` outside verify/ empty; Kani counts
one cover per monomorphized instance — consistent with the measured 8/8 of `mutating_insertion_safety_cell_n11_to12`
in c3b/heavy3-before-j1 at ff40dd99, whose mutating_key_order / mutating_insertion_fixed / macro bodies equal HEAD):
- bytes85_n31: "stable route normal return at 31", "unstable route normal return at 31", family end → 3.
- stable ZST: "dispatch route returns normally at N" for N∈{0,1,2,7,8,15,16,17,31,32} (10) + end → 11.
- unstable ZST: same per N∈{8,9,12,13,17} (5) + end → 6. dispatch_safety_fixed/volatile_reading_less/assume_order_violation
  have no covers (cut_order_violation_panic, which has one, is not used by these roots).
- Cell N6..10 / N11..15 / N16..20: per length 5 + end 1 + mutating_insertion_fixed::<N> "offset one" and "final offset"
  2×5 + mutating_key_order "mutating comparator changes both keys" 1 (non-generic, one instance) → 17 each.

Bodies: dispatch_safety_fixed (249-262): `[T;N]` via `T::arbitrary_value()` (u8 arrays: full `kani::any()` [u8;85] (369);
`()` (227)); stable: scratch `[MaybeUninit<T>; 48]` + `StableSmallSortTypeImpl::small_sort`; unstable:
`UnstableSmallSortTypeImpl::small_sort`; comparator function item `volatile_reading_less::<T>` (239: volatile reads,
`kani::any()` bool). Pair macro: any len from the list × any `stable: bool`; single-route macro fixes STABLE.
mutating_insertion_fixed (594-600): `tagged_values::<N>()` (549: any key, any tag per `Cell<TaggedKey>`), any offset
1..=N, `insertion_at_any_offset!` (470-496: constant offset per arm → `insertion_sort_shift_left(v, O, cmp)`), comparator
`mutating_key_order` (534-547: volatile reads of both Cells, writes arbitrary new keys keeping tags, returns `kani::any()`).
No sorted-prefix premise, no assumed order, no fn-pointer coercion. Task table matches source exactly; no discrepancy.

## Route map and scratch (smallsort.rs 30-172, 199-262, 311-351, 574)
- [u8;85] (Freeze+Copy, 85 B): stable → `small_sort_general_with_scratch` with the harness scratch 48 ≥ 31+16;
  size>16 → presort `sort4_stable` ×2 + insert_tail + `bidirectional_merge`. Unstable → `has_efficient_in_place_swap` false
  (85>8), 85×48=4080 ≤ 4096 → `small_sort_general` (stack `[T;48]`), same body. (bytes86 is the fallback boundary.)
- `()` stable → `small_sort_general_with_scratch`, scratch 48 ≥ len+16 for all N≤32; len<2 early return; len≥16 sort8_stable.
- `()` unstable → size 0 ≤ 8, 0×32 ≤ 4096 → `small_sort_network` (stack `[T;32]`); N8 insertion offset 1, N9/12 sort9,
  N13/17 sort13, all no_merge (len<18).
- Three dispatch routes, each with normal-return covers in G1: stable general_with_scratch (bytes85 stable, ZST stable),
  unstable small_sort_general (bytes85 unstable), unstable small_sort_network (ZST unstable).
- `Cell<TaggedKey>` G2: direct `insertion_sort_shift_left` at every offset 1..=N (no dispatch, no scratch).

## Ordinary preservation
None of the six names is in macsplit/ordinary-expected.txt (202). Ordinary already has bytes85 N{0,1,2,7,8},{15,16,17},{32},
Cell insertion N1..5 and N20 offsets 1..20; no ZST root. Ordinary 202 / PFC 36, static cfg-on 384 / opt-in 182 preserved by
library-tree identity (not recounted; no native inventory here). Library, harnesses, covers, workflows, tooling unchanged.

## Budget / slots / window (k1g.sh budget, 2026-11-03)
- Project: 197 builds, used $86.2350, reserved by unfinished $2.4300, cap $93.96.
- G1 reserve (3×10+30)×$0.0135 = $0.810 → $86.2350+$2.4300+$0.810 = $89.475 ≤ $93.96. Own spent $0; own G1+G2 plan
  $1.620 ≤ own cap $1.65. No retry; only the one compile-error repair exception with new review/GO.
- Slots: 2 unfinished now (DIRECTBOUNDS on k1-network, INTEGPAIRS on k1-merge) → G1 only after DIRECTBOUNDS is
  terminal/accounted; then G1 makes project 2 (≤2), k1-network 1 (≤1).
- Window: T0 at G1 dispatch; main 150 min + closeout 30. G1 60 min envelope, G2 60 min after G1 terminal → ≤ 120 min + finishing.
- History, not a prediction: bytes85_n31 has a historical macOS 109.8 s point (c3c-inputs/mac-times.tsv, not a GCB baseline); ZST and Cell N11..20 roots unmeasured on GCB/v6.
