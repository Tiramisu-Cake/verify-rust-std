# ROUTESEF PRE-BUILD (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-network, slug routesef. Prepared 2026-11-03T11:36Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-routesef-20261103`, clean before this commit; base `7ef2f27a81af39cbe84361bd07bd510c35092c71`
  (ROUTESCD terminal c165e6b1 + cherry-pick of cap commit e8e238db); task commit `c5dbc40f2d1071756c5bb5db6546b13b8ede6df5`
  (TASK-ROUTESEF.md sha256 cf69b7e5…86bb0). `git diff 7ef2f27a HEAD` touches only research/challenge-8/kani-k1 files.
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = base = Part1 v6 `d6b8caf7fe0e`
  (`git diff --quiet d6b8caf7fe0e HEAD -- library` true). No library commit. verify/merge.rs blob
  `12937938dbd93ae42e5000684dc1edb0d1c9289d` (sha256 b38f5ed8…6a94); smallsort.rs sha256 78fc8fe8…ed61 (= ROUTESAB/ROUTESCD).
- Tooling base `e8e238db9d87323fa4da011a1a8b37fb76ec91c0`: all k1g.sh LANE_PATHS at HEAD equal it (`git diff --quiet` true).
  Its lane diff vs frozen `30f77e85` is only tools/k1g.sh CAP_USD 88.96 → 93.96 (+ comment), +3/−2 lines; HEAD lane files
  therefore differ from 30f77e85 by exactly that. `check-tooling BUILD e8e238db…` after each Build.
  Kani `9461e07af7ec929f050aa4192f29363c9be07779` (tool_config/kani-version.toml), channel nightly-2026-10-12.
  Existing tool unit tests: 70 + 12 = 82 OK (python only; no cargo/rustc/Kani/CBMC).

## Requests (both: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`, rc 0)
| File | request_id | sha256 |
|---|---|---|
| routesef/g1.request.json = RUN-REQUEST.json (this commit) | routesef-g1-measure-allroutes-n26to29-20261103 | 7cba0f023c62d0816f4c8f2790497b4e33fc1d7388b4204c14706836cffbf49b |
| routesef/g2.request.json (copied to RUN-REQUEST.json only in the G2 commit) | routesef-g2-measure-allroutes-n30to32-20261103 | 76ca39b82807b2f12deee9e280ddc94671d7a232b5f4da238125df7206801c14 |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 → k1-standard4 (4 vCPU/16 GiB, swap off), controls true,
kani_jobs 1, uninit_checks false, harness_timeout_minutes 10; G1 4 rows, G2 3 rows, each expect SUCCESS. Validator output:
N×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`;
rustflags `--cfg kani_smallsort_controls` (controls true). No highmem, resource kind, solver flags, instrumentation or list prep.
Requests differ from ROUTESCD g1 only in request_id, purpose text and harness names.

## Source inventory (verify/merge.rs at blob 12937938; paths relative to library/core/src/slice/sort/shared/smallsort/)
| Packet | Root (verify::merge::) | Line | cfg | Presort in general (halves) | insert_tail per half | Covers: 3 route returns + panic stub | Forecast |
|---|---|---:|---|---|---|---:|---:|
| G1 (E) | route_safety_all_routes_n26 | 524-525 | kani_smallsort_controls | sort8_stable ×2 (13+13) | 5+5 | 3+1 | 4/4 |
| G1 (E) | route_safety_all_routes_n27 | 526-527 | kani_smallsort_controls | sort8_stable ×2 (13+14) | 5+6 | 3+1 | 4/4 |
| G1 (E) | route_safety_all_routes_n28 | 528-529 | kani_smallsort_controls | sort8_stable ×2 (14+14) | 6+6 | 3+1 | 4/4 |
| G1 (E) | route_safety_all_routes_n29 | 530-531 | kani_smallsort_controls | sort8_stable ×2 (14+15) | 6+7 | 3+1 | 4/4 |
| G2 (F) | route_safety_all_routes_n30 | 532-533 | kani_smallsort_controls | sort8_stable ×2 (15+15) | 7+7 | 3+1 | 4/4 |
| G2 (F) | route_safety_all_routes_n31 | 534-535 | kani_smallsort_controls | sort8_stable ×2 (15+16) | 7+8 | 3+1 | 4/4 |
| G2 (F) | route_safety_all_routes_n32 | 536-537 | kani_smallsort_controls | sort8_stable ×2 (16+16) | 8+8 | 3+1 | 4/4 |

- Macro `define_route_safety_harness!` (470-482), read in pinned source: `#[kani::proof]`,
  `#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, abort_on_order_violation)]`,
  `#[kani::unwind(34)]`, body `all_upper_routes_safety_body::<N>()`. Each of the seven lines is preceded by
  `#[cfg(kani_smallsort_controls)]` (opt-in). N16 (505) and N2..8 have no cfg (ordinary).
- Body `all_upper_routes_safety_body` (370-377): `route: u8 = kani::any()`; 0 → `unstable_general_u64_safety_body`
  (348-352: any `[u64;N]`, direct `small_sort_general`, cover "general u64 safety: normal return reachable");
  1 → `noncopy_general_u64_safety_body` (354-359: any `[u64;N]` payload mapped to `#[repr(transparent)] WrappedU64`
  (337), `<WrappedU64 as UnstableSmallSortTypeImpl>::small_sort` with `arbitrary_wrapped_u64_order`, cover "non-Copy u64
  route safety: normal return reachable"); any other value → `stable_general_u64_safety_body` (361-366: any `[u64;N]`,
  `[MaybeUninit<u64>; SMALL_SORT_GENERAL_SCRATCH_LEN]` = 32+16 = 48, `<u64 as StableSmallSortTypeImpl>::small_sort`,
  cover "stable u64 route safety: normal return reachable"). Payload/routes full, no assumed order, no assert.
- Comparators: `arbitrary_u64_order` (256-263) and `arbitrary_wrapped_u64_order` (339-346): function items, volatile
  reads of both arguments, return `kani::any()` bool.
- Panic stub `abort_on_order_violation` (265-269): `cover(true, "order violation panic path is reachable")`,
  `assume(false)`. Non-generic, one instance → one cover per root; it is a panic witness, never a route return.
- Actual routes (smallsort.rs): route 0 → `small_sort_general` (205-218, internal 48-element stack scratch) →
  `small_sort_general_with_scratch` (220-293). Route 1: WrappedU64 is Freeze, not Copy → `UnstableSmallSortTypeImpl` Freeze
  impl (90-103) → `UnstableSmallSortFreezeTypeImpl` default (113-134): 8×48 ≤ 4096 → `small_sort_general`. Route 2:
  `StableSmallSortTypeImpl` Freeze impl (49-63) → `small_sort_general_with_scratch` with the caller's 48 scratch.
  In with_scratch: 48 ≥ N+16 for every N ≤ 32 (N32 is the exact boundary 48 = 32+16), so `abort_immediate` (231) is not
  taken; size_of u64 ≤ 16 and N ≥ 16 → `sort8_stable` (657) ×2 (second at scratch+len+8, end len+16 ≤ 48) + `insert_tail`
  from 8 to the half length (table); then `bidirectional_merge` (754-836) of N back into v. Every bidirectional_merge calls
  stubbed `panic_on_ord_violation` (832) on inconsistent consumption. Real callees, no contracts/verified stubs. Same shape
  as N17..25.
- Reachable cover inventory: no `kani::cover` in library/core/src/slice/sort outside verify/ (grep: none); every other
  merge.rs cover is in a function these roots do not call. Total 4 per root = forecast = ROUTESAB/ROUTESCD measured 4/4 for
  N9..25 (exc. 16) on the same tree; no discrepancy. Gate needs all 4, including the normal return of each of the three
  routes; the stub cover is not counted as a route return.
- Scope: bounded normal-return safety of exact any `[u64;N]` on three general/stable u64 routes; not correctness, not all
  T/F/impls, not Rust unwind cleanup; uninit checks off.
- None of the seven names is in macsplit/ordinary-expected.txt (202 rows; grep count 0). Ordinary 202 / PFC 36 and static
  cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted).
- History, not a baseline (other trees/profiles, per task): N29/N31/N32 TIMEOUT on a 120 s screen; others unrecorded.
  ROUTESCD N25 189 s on this tree/profile; task forecast E 190–250 s, F 250–300 s per row.

## Budget / slots / window (k1g.sh budget, 2026-11-03T11:35Z)
- Project: 191 builds, used $84.9255, reserved by unfinished $0.0000, cap $93.96. G1 reserve (4×10+30)×$0.0135 = $0.945
  → used+reserved+G1 = $85.8705 ≤ $93.96. G2 reserve (3×10+30)×$0.0135 = $0.810.
  Own spent $0 + G1 $0.945 ≤ own cap $1.80; G1+G2 reserves $1.755 ≤ $1.80. G2 re-checked after G1 terminal/accounting.
- Slots: 0 unfinished in project now; G1 makes ≤ 2 (re-checked at dispatch; PERMSOLVER/WRAPMORE are k1-merge),
  k1-network 1 (≤ 1). Previous k1-network build (ROUTESCD G2) terminal and accounted in RESULT-ROUTESCD.md.
  Foreign/ROUTESCD ledgers untouched.
- Window: main 150 min + closeout 30 min from T0; G1 timeout 70 min, then G2 60 min envelope; both fit inside main
  if G2 dispatches ≤ ~85 min after T0. A row at the 10 min limit is a bounded TIMEOUT fact, no retry.
- Compile-error repair (one per stage, new review/GO) only if own spent + its reserve ≤ $1.80.

## G2 dispatch record (coordinator pre-approved G2 in the G1 GO; after G1 terminal/accounting, 2026-11-03T12:06Z)
- G1 6515c8ee terminal SUCCESS, 4/4 rows accepted, cost $0.3375 (routesef/g1.result.md). No shared setup/compile error.
- RUN-REQUEST.json := routesef/g2.request.json (sha256 76ca39b82807b2f12deee9e280ddc94671d7a232b5f4da238125df7206801c14),
  unchanged since 604e01b4 (`git diff --quiet 604e01b4 HEAD` true before this commit); library tree d4ec476a and lane files
  unchanged (this commit touches only research files).
- Budget: project 194 builds, used $85.4520, reserved by unfinished $1.0800 (one foreign build of 80 min; WRAPMORE G1's 60 min
  = $0.81 plus any second build ≥ 40 min = $0.54 would exceed $1.08, so exactly one unfinished, not ours);
  + G2 $0.810 = $87.3420 ≤ $93.96. Own spent $0.3375 + G2 reserve $0.810 = $1.1475 ≤ $1.80.
- Slots: 1 unfinished in project (foreign); G2 makes 2 (≤ 2), k1-network 1 (≤ 1). Window: T0 11:38:06Z, main ends
  14:08Z; G2 60 min envelope from ~12:07Z ends ~13:07Z, inside main.
