# ROUTESCD PRE-BUILD (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-network, slug routescd. Prepared 2026-11-03T10:47Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-routescd-20261103`, clean before this commit; base ROUTESAB terminal
  `f02ba6c48b6a20d53494a0cf985fa533884b779e`; task commit `98bbf31775e666f5ae69aec34fc91a1f5c3586c4`
  (TASK-ROUTESCD.md sha256 6d8f0ad6…6c38e90). `git diff f02ba6c4 HEAD` touches only research/challenge-8/kani-k1 files.
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = base = Part1 v6 `d6b8caf7fe0e`
  (`git diff --quiet d6b8caf7fe0e HEAD -- library` true). No library commit. verify/merge.rs blob
  `12937938dbd93ae42e5000684dc1edb0d1c9289d` (sha256 b38f5ed8…6a94); smallsort.rs sha256 78fc8fe8…ed61 (same as ROUTESAB).
- All k1g.sh LANE_PATHS at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --quiet` true).
  Kani `9461e07af7ec929f050aa4192f29363c9be07779` (tool_config/kani-version.toml), channel nightly-2026-10-12.
  `check-tooling BUILD 30f77e85…` after each Build. Existing tool unit tests: 82 OK (python only; no cargo/rustc/Kani/CBMC).

## Requests (both: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`, rc 0)
| File | request_id | sha256 |
|---|---|---|
| routescd/g1.request.json = RUN-REQUEST.json (this commit) | routescd-g1-measure-allroutes-n18to21-20261103 | e75c0506236a31ff9aa66a3a080a35028a11f2fe17f6d39878d34c78b055e2bc |
| routescd/g2.request.json (copied to RUN-REQUEST.json only in the G2 commit) | routescd-g2-measure-allroutes-n22to25-20261103 | f52055e87ab357ee9c709a7998d790077b6170a82f69101b87d005eb134c868c |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 → k1-standard4 (4 vCPU/16 GiB, swap off), controls true,
kani_jobs 1, uninit_checks false, harness_timeout_minutes 10; 4 rows, each expect SUCCESS. Validator output:
4×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`;
rustflags `--cfg kani_smallsort_controls` (controls true). No highmem, resource kind, solver flags, instrumentation or list prep.

## Source inventory (verify/merge.rs at blob 12937938; paths relative to library/core/src/slice/sort/shared/smallsort/)
| Packet | Root (verify::merge::) | Line | cfg | Presort in general (halves) | insert_tail per half | Covers: 3 route returns + panic stub | Forecast |
|---|---|---:|---|---|---|---:|---:|
| G1 | route_safety_all_routes_n18 | 508-509 | kani_smallsort_controls | sort8_stable ×2 (9+9) | 1+1 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n19 | 510-511 | kani_smallsort_controls | sort8_stable ×2 (9+10) | 1+2 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n20 | 512-513 | kani_smallsort_controls | sort8_stable ×2 (10+10) | 2+2 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n21 | 514-515 | kani_smallsort_controls | sort8_stable ×2 (10+11) | 2+3 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n22 | 516-517 | kani_smallsort_controls | sort8_stable ×2 (11+11) | 3+3 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n23 | 518-519 | kani_smallsort_controls | sort8_stable ×2 (11+12) | 3+4 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n24 | 520-521 | kani_smallsort_controls | sort8_stable ×2 (12+12) | 4+4 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n25 | 522-523 | kani_smallsort_controls | sort8_stable ×2 (12+13) | 4+5 | 3+1 | 4/4 |

- Macro `define_route_safety_harness!` (470-482), read in pinned source: `#[kani::proof]`,
  `#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, abort_on_order_violation)]`,
  `#[kani::unwind(34)]`, body `all_upper_routes_safety_body::<N>()`. Each of the eight lines is preceded by
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
  In with_scratch: 48 ≥ N+16 for every N ≤ 32, so `abort_immediate` (231) is not taken; size_of u64 ≤ 16 and N ≥ 16 →
  `sort8_stable` (657) ×2 (each: sort4_stable ×2 + `bidirectional_merge` of 8) + `insert_tail` from 8 to the half length
  (table); then `bidirectional_merge` (754-836) of N back into v. Every bidirectional_merge calls stubbed
  `panic_on_ord_violation` (832) on inconsistent consumption. Real callees, no contracts/verified stubs. Same shape as N17.
- Reachable cover inventory: no `kani::cover` in library/core/src/slice/sort outside verify/ (grep: none); every other
  merge.rs cover (profile/sort4 harnesses, merge controls, safety control, …) is in a function these roots do not call.
  Total 4 per root = forecast = ROUTESAB measured 4/4 for N9..15,17 on the same tree; no discrepancy. Gate needs all 4,
  including the normal return of each of the three routes; the stub cover is not counted as a route return.
- Scope: bounded normal-return safety of exact any `[u64;N]` on three general/stable u64 routes; not correctness, not all
  T/F/impls, not Rust unwind cleanup; uninit checks off.
- None of the eight names is in macsplit/ordinary-expected.txt (202 rows; route roots there are n2..n8 and n16 only).
  Ordinary 202 / PFC 36 and static cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted).
- History, not a baseline (other trees/profiles, per task): N18 and N23 TIMEOUT on a 120 s screen, N21 SUCCESS 180 s;
  N19, N20, N22, N24, N25 unrecorded. ROUTESAB N17 121.7 s on this tree/profile.

## Budget / slots / window (k1g.sh budget, 2026-11-03T10:46Z)
- Project: 188 builds, used $83.9130, reserved by unfinished $0.5400 (one foreign unfinished build, not ours;
  COVERCOST k1-merge per task), cap $88.96. G1 reserve (4×10+30)×$0.0135 = $0.945 → used+reserved+G1 = $85.3980 ≤ $88.96.
  Own spent $0 + G1 $0.945 ≤ own cap $1.95; G1+G2 reserves $1.890 ≤ $1.95. G2 re-checked after G1 terminal/accounting.
- Slots: 1 unfinished in project (foreign); G1 makes 2 (≤ 2), k1-network 1 (≤ 1). Previous k1-network build f7be2377
  (ROUTESAB G2) terminal SUCCESS 10:40:05Z, accounted in RESULT-ROUTESAB.md. Foreign/ROUTESAB ledgers untouched.
- Window: main 150 min + closeout 30 min from T0; G1 timeout 70 min, then G2 70 min envelope; both fit inside main
  if G2 dispatches ≤ ~75 min after T0. Expected G1 wall well under timeout unless rows hit the 10 min/row limit.
- Compile-error repair (one per stage, new review/GO) only if own spent + its reserve ≤ $1.95.
