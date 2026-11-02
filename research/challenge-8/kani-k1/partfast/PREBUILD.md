# PART2-FAST PRE-BUILD (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Owner k1-network. Prepared 2026-11-02T19:17Z; T0 not started
(starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-partfast-20261102`; base MACSPLIT `4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4`;
  task commit `cfac8c85c6d1ae97b723f6d37a5a754d0ed10c18` (TASK-PART2-FAST.md sha256 15a26a86…0dd5).
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = at MACSPLIT = at Part1 v6
  `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097` (git rev-parse). No library commit in this stage: `git diff 4f40345 HEAD`
  touches only research files. network.rs blob `1a85a483b16449485a02c4e1140033c8a22956fa`
  (sha256 d3d0047b…7f7a); smallsort.rs sha256 78fc8fe8…ed61.
- Lane files (k1g.sh LANE_PATHS) at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20`
  (`git diff --stat` empty). Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, channel nightly-2026-10-12
  (tool_config/kani-version.toml). `check-tooling BUILD 30f77e85…` after each Build.

## Requests (both validated by `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`)
| File | request_id | sha256 |
|---|---|---|
| partfast/g1.request.json = RUN-REQUEST.json (G1 commit) | partfast-g1-measure-u8net4-20261102 | 42df2ee0a8b720b661549d9bf4f373e52d91a9823e14b0a3e084719811fdbb59 |
| partfast/g2.request.json (copied to RUN-REQUEST.json only in the G2 commit) | partfast-g2-measure-u64net3-ins1-20261102 | e46f07c2bdf8f06749570d2c3a9cb1b7e1c20c1a5b99d2bee136d11b8a25a97a |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 (pool k1-standard4, 4 vCPU/16 GiB), controls true,
kani_jobs 1, uninit_checks false, harness_timeout_minutes 10, 4 rows, each expect SUCCESS. Validator args:
4×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`. No highmem,
resource kind, solver flags, instrumentation or list preparation. Existing tool unit tests: 82 OK (python only).

## Source inventory of the eight roots (network.rs, all gated by `#[cfg(kani_smallsort_controls)]`)
| Root | Line | Macro → body | Property | Covers |
|---|---:|---|---|---:|
| network_correctness_u8_n8 | 991 | network_correctness_cases → fixed::<u8,8> | sorted + count (N<9) | 3 |
| network_correctness_u8_n14 | 1208 | same, u8 14 | sorted only | 3 |
| network_correctness_u8_n15 | 1215 | same, u8 15 | sorted only | 3 |
| network_correctness_u8_n16 | 1224 | same, u8 16 | sorted only | 3 |
| network_correctness_u64_n10 | 1153 | same, u64 10 | sorted only | 3 |
| network_correctness_u64_n11 | 1190 | same, u64 11 | sorted only | 3 |
| network_correctness_u64_n12 | 1197 | same, u64 12 | sorted only | 3 |
| insertion_permutation_u8_n15 | 1219 | insertion_permutation_case → fixed::<u8,15> | full-value count | 2 |

- network_correctness_fixed (945-960): `v: [T;N] = kani::any()`, independent `probe: T = kani::any()`,
  `let mut cmp = strict_less::<T>` (function item, `a < b`, 941-943), `UnstableSmallSortTypeImpl::small_sort`;
  `assert!(is_sorted_by)`; count assert only `if N < 9`; cover "trivial input or sort moves elements". Macro (962-976):
  `#[kani::proof] #[kani::unwind(25)]`, single length, cover per length + "sort family reached the end" → 3/3.
  No stub, no assumed order, no fn-pointer coercion.
- Route (smallsort.rs 142-165, 311-349): u8/u64 → small_sort_network, len<18 no merge; N8 presorted 1 → insertion
  offset 1; N10..12 sort9 + insertion from 9; N14..16 sort13 + insertion from 13.
- insertion_permutation_fixed (1158-1172): any `[u8;15]`, independent any probe, `insertion_sort_shift_left(&mut v, 13,
  &mut volatile_reading_less::<T>)` (239-247: volatile reads, `kani::any()` bool), no sorted-prefix premise, count
  assert, cover "insertion preserves permutation and moves elements"; macro (1174-1183) unwind 25 + end cover → 2/2.
- Matches the task table exactly; no discrepancy. None of the eight names is in macsplit/ordinary-expected.txt (202).
- Ordinary 202 / PFC 36 and static cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted; no native
  inventory in this stage). Lane controls guard (gcb-k1.sh 52-57): no stray cfg outside verify/, verify.rs, Cargo.toml.

## Budget / slots (k1g.sh budget, 2026-11-02 ~19:15Z)
- Project: 179 builds, used $81.2535, reserved by unfinished $1.2150 (= INV2 reserve, not counted twice), cap $88.96.
- G1 reserve (4×10+30)×$0.0135 = $0.945 → used+reserved+G1 = $83.4135 ≤ $88.96. Own spent $0; own G1+G2 plan $1.890 ≤ $2.00.
- Slots: 1 unfinished in project now; G1 makes 2 (≤2), k1-network has none. Nightly ~$4 limit: coordinator check.
- Envelope: build timeout 70 min + finishing must fit main 180 min from T0; G2 only after G1 terminal/accounting.
- History, not a prediction: several of these roots were TIMEOUT under other profiles (c3b/c3c jobs>1 summaries).

## G2 PRE-BUILD (after G1 terminal/accounting, 2026-11-02 ~19:43Z)
- G1 5765f47e terminal SUCCESS, 4/4 rows accepted, cost $0.2835 (partfast/g1.result.md). No shared setup error.
- RUN-REQUEST.json := partfast/g2.request.json (sha256 e46f07c2bdf8f06749570d2c3a9cb1b7e1c20c1a5b99d2bee136d11b8a25a97a),
  re-validated; library tree d4ec476a and lane files unchanged (this commit touches only research files).
- Budget: project 180 builds, used $82.0635, reserved by unfinished $0.0000; + G2 $0.945 = $83.0085 ≤ $88.96.
  Own spent $0.2835 + G2 reserve $0.945 = $1.2285 ≤ $2.00; no further planned packet after G2.
- Slots: 0 unfinished in project; G2 makes 1. Window: T0 19:19:05Z, main ends 22:19Z; G2 70 min envelope from ~19:45Z
  ends ~20:55Z plus finishing, inside main.
