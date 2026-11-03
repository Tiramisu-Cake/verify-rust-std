# SAFETYNET PRE-BUILD (single G1 request prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-network, slug safetynet. Prepared 2026-11-03T09:35Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-safetynet-20261103`, clean before this commit; base PART2-FAST
  `2104e7a596fabb058a99c8bcdf0e3f487d9a7753`; task commit `a64fecc570cf47ec305b9a7a973721a64c8e830c`
  (TASK-SAFETYNET.md sha256 76a3b4c3…cb1cb). `git diff 2104e7a5 HEAD` touches only research/challenge-8/kani-k1 files.
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = base = Part1 v6 `d6b8caf7fe0e`
  (`git diff --quiet d6b8caf7 HEAD -- library` true). No library commit. network.rs blob
  `1a85a483b16449485a02c4e1140033c8a22956fa` (sha256 d3d0047b…7f7a); smallsort.rs sha256 78fc8fe8…ed61.
- All k1g.sh LANE_PATHS at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --quiet` true).
  Kani `9461e07af7ec929f050aa4192f29363c9be07779` (tool_config/kani-version.toml), rust-toolchain nightly-2026-10-12.
  `check-tooling BUILD 30f77e85…` after the Build. Existing tool unit tests: 82 OK (python only).

## Request (validated: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`, rc 0)
- safetynet/g1.request.json = RUN-REQUEST.json, request_id `safetynet-g1-measure-u64netsafety4-n18to29-20261103`,
  sha256 `aa2e18fa5365148a90a0f4dcabe8a0049d7fa8c888f71429b6a72e5780c3e7a6`.
- kind measurement, agent k1-network, runner gcb-e2-standard-4 → k1-standard4 (4 vCPU/16 GiB, swap off), controls true,
  kani_jobs 1, uninit_checks false, harness_timeout_minutes 10; 4 rows, each expect SUCCESS. Validator output:
  4×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`;
  rustflags `--cfg kani_smallsort_controls`. No highmem, resource kind, solver flags, instrumentation or list preparation.

## Source inventory (verify/network.rs at blob 1a85a483; paths relative to library/core/src/slice/sort/shared/smallsort/)
| Root (verify::network::) | Line | cfg | Lengths | Covers: lengths + family end + panic stub | Forecast |
|---|---:|---|---|---:|---:|
| network_safety_unstable_u64_n18_to21 | 212 | kani_smallsort_controls | 18,19,20,21 | 4+1+1 = 6 | 6/6 |
| network_safety_unstable_u64_n22_to25 | 214 | kani_smallsort_controls | 22,23,24,25 | 4+1+1 = 6 | 6/6 |
| network_safety_unstable_u64_n26_to27 | 216 | kani_smallsort_controls | 26,27 | 2+1+1 = 4 | 4/4 |
| network_safety_unstable_u64_n28_to29 | 218 | kani_smallsort_controls | 28,29 | 2+1+1 = 4 | 4/4 |

- Macro `unstable_dispatch_network_cases` (191-209): `#[kani::proof]`,
  `#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]`, `#[kani::unwind(35)]`;
  `len = any_where(matches!(l, N..))`, match arm per N → `unstable_dispatch_network_fixed::<N>()`, then one
  `cover(len == N, "unstable network normal return at N")` per N and `cover(true, "unstable network family reached the end")`.
- `unstable_dispatch_network_fixed` (185-189): `v: [u64; N] = kani::any()` (exact initialized array, offset 0, all 64 bits),
  `<u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less_u64)`. No assumed order/prefix, no assert.
- F `volatile_reading_less_u64` (62-69): function item, `read_volatile` of both arguments, returns `kani::any()` bool.
- Panic stub `cut_order_violation_panic` (152-155): `cover(true, "order-violation panic stub reached")` then
  `assume_order_violation` (157-160: `assume(false)`). Non-generic, one instance → one cover per root.
- Reachable cover inventory: grep finds no `kani::cover` in library/core/src/slice/sort outside verify/; every other
  network.rs cover (e.g. 25-32 swap profile, 170/182/290 controls, 275-279 dispatch_safety, later correctness macros) is
  in a function these roots do not call. Totals match the forecast exactly; no discrepancy. Gate needs all covers satisfied, incl. per-length returns.
- Actual route (smallsort.rs): UnstableSmallSortTypeImpl for Freeze u64 (90-103) → UnstableSmallSortFreezeTypeImpl for
  Freeze+Copy (142-171): `has_efficient_in_place_swap` (size 8 ≤ 8) and 8×32 ≤ 4096 → `small_sort_network` (311-371).
  len 18..29 ≥ 18 → merge path: halves 9..15 → sort9_optimal (9..12) or sort13_optimal (13..15) + insertion_sort_shift_left
  from 9/13; then `bidirectional_merge` (754-836) into internal `stack_array: MaybeUninit<[u64; 32]>` scratch, which calls
  `panic_on_ord_violation` (stubbed) on inconsistent consumption; then copy_nonoverlapping back. Real callees, no contracts.
- Scope: normal-return safety of this u64 Unstable network domain only; no correctness, not all T/F, not general/Stable;
  not Rust unwind cleanup; uninit checks off. Panic witness covers the stub only, never a per-length normal return.
- None of the four names is in macsplit/ordinary-expected.txt (202 rows; it holds n0_to17 and n30_to32 only). Ordinary
  202 / PFC 36 and static cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted; no inventory here).
- History, not a prediction: n18_to21 SUCCESS 116.9 s on earlier source afea78b3 (c3b/ordinary-timings.tsv,
  build 45a0dd0c); n22_to25, n26_to27, n28_to29 UNMEASURED there.

## Budget / slots / window (k1g.sh budget, 2026-11-03T09:34:51Z)
- Project: 183 builds, used $82.7925, reserved by unfinished $0.0000, cap $88.96.
  G1 reserve (4×10+30)×$0.0135 = $0.945 → used+reserved+G1 = $83.7375 ≤ $88.96. Own spent $0 + $0.945 ≤ own cap $1.00.
  One Build only; no retry/G2. Night envelope: coordinator check.
- Slots: 0 unfinished in project; G1 makes 1 (≤ 2), k1-network 1 (≤ 1). Previous k1-network build 38ec4914 (PART2-FAST G2)
  terminal SUCCESS 2026-11-02T20:01:52Z and accounted in RESULT-PART2-FAST.md. Foreign reservations/ledgers untouched.
- Window: main 120 min + closeout 30 min from T0; Build timeout 70 min (4200 s) + finishing fits inside main.
