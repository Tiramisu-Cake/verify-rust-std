# ROUTESAB PRE-BUILD (G1 and G2 requests prepared; nothing dispatched)

Runtime Claude Code, executor alone, no subagents. Stable owner k1-network, slug routesab. Prepared 2026-11-03T10:12Z;
T0 not started (starts at the actual G1 dispatch after coordinator GO). This file registers no phase and grants no dispatch.

## Identities
- Branch `experiment/kani-k1-routesab-20261103`, clean before this commit; base SAFETYNET terminal
  `969c94f8591d2aff08f671e53911e325b5cf529d`; task commit `afa9aefd5c5db401b665bc6dbba625cba2df196c`
  (TASK-ROUTESAB.md sha256 d41b4142…43ed). `git diff 969c94f8 HEAD` touches only research/challenge-8/kani-k1 files.
- `library` tree `d4ec476a7a001363e58f19948c188a9c2078e370` at HEAD = base = Part1 v6 `d6b8caf7fe0e`
  (`git diff --quiet` true for both). No library commit. verify/merge.rs blob `12937938dbd93ae42e5000684dc1edb0d1c9289d`
  (sha256 b38f5ed8…6a94); smallsort.rs sha256 78fc8fe8…ed61.
- All k1g.sh LANE_PATHS at HEAD equal frozen tooling `30f77e859903df14b442ff9294d4fbbd44827f20` (`git diff --quiet` true).
  Kani `9461e07af7ec929f050aa4192f29363c9be07779` (tool_config/kani-version.toml), rust-toolchain nightly-2026-10-12.
  `check-tooling BUILD 30f77e85…` after each Build. Existing tool unit tests: 82 OK (python only).

## Requests (both: `kani_k1.py validate --require-runner gcb-e2-standard-4 --max-total-minutes 720`, rc 0)
| File | request_id | sha256 |
|---|---|---|
| routesab/g1.request.json = RUN-REQUEST.json (this commit) | routesab-g1-measure-allroutes-n9to12-20261103 | cc730f7e08b308b112e82d4acbd01a083c6cf7ab32bb33c454313b635ac3155e |
| routesab/g2.request.json (copied to RUN-REQUEST.json only in the G2 commit) | routesab-g2-measure-allroutes-n13to15-n17-20261103 | b606895376bb051940a25717e3a128bc7a3910d7a2bb5666bf97700c139f3e00 |

Both: kind measurement, agent k1-network, runner gcb-e2-standard-4 → k1-standard4 (4 vCPU/16 GiB, swap off), controls true,
kani_jobs 1, uninit_checks false, harness_timeout_minutes 10; 4 rows, each expect SUCCESS. Validator output:
4×`--harness <full name>`, `--exact`, `--harness-timeout 10m`, `--jobs=1`, `--output-format=terse`;
rustflags `--cfg kani_smallsort_controls`. No highmem, resource kind, solver flags, instrumentation or list preparation.

## Source inventory (verify/merge.rs at blob 12937938; paths relative to library/core/src/slice/sort/shared/smallsort/)
| Packet | Root (verify::merge::) | Line | cfg | Presort in general | Covers: 3 route returns + panic stub | Forecast |
|---|---|---:|---|---|---:|---:|
| G1 | route_safety_all_routes_n9 | 491-492 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n10 | 493-494 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n11 | 495-496 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G1 | route_safety_all_routes_n12 | 497-498 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n13 | 499-500 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n14 | 501-502 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n15 | 503-504 | kani_smallsort_controls | sort4_stable ×2 | 3+1 | 4/4 |
| G2 | route_safety_all_routes_n17 | 506-507 | kani_smallsort_controls | sort8_stable ×2 (each merges 8) | 3+1 | 4/4 |

- Macro `define_route_safety_harness!` (470-482): `#[kani::proof]`,
  `#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, abort_on_order_violation)]`,
  `#[kani::unwind(34)]`, body `all_upper_routes_safety_body::<N>()`. N16 (505) and N2..8 have no cfg (ordinary).
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
  In with_scratch: 48 ≥ N+16 for every N here, so `abort_immediate` is not taken; N9..15 → `sort4_stable` ×2 + `insert_tail`
  from 4; N17 → `sort8_stable` ×2 (sort4_stable ×2 + `bidirectional_merge` of 8 each) + `insert_tail` from 8; then
  `bidirectional_merge` (754-836) back into v, which calls stubbed `panic_on_ord_violation` (832) on inconsistent
  consumption. Real callees, no contracts/verified stubs.
- Reachable cover inventory: no `kani::cover` in library/core/src/slice/sort outside verify/; every other merge.rs cover
  (158/170/185/213 profile/sort4 harnesses, 286/316/331 merge controls, 390 safety control, …) is in a function these roots
  do not call. Total 4 per root = forecast; no discrepancy. Historical c3b light60-before rows (other tree) also show 4/4
  for n2..n10. Gate needs all 4, including the normal return of each of the three routes.
- Scope: bounded normal-return safety of exact any `[u64;N]` on three general/stable u64 routes; not correctness, not all
  T/F/impls, not Rust unwind cleanup; uninit checks off.
- None of the eight names is in macsplit/ordinary-expected.txt (202 rows; route roots there are n2..n8 and n16 only).
  Ordinary 202 / PFC 36 and static cfg-on 384 / opt-in 182 preserved by library-tree identity (not recounted).
- History, not a baseline: N9 33.7 s, N10 41.0 s (c3b light60-before, other tree/profile); task also cites N12 43 s,
  N14 65 s; N11, N13, N15, N17 unrecorded.

## Budget / slots / window (k1g.sh budget, 2026-11-03T10:08:43Z)
- Project: 185 builds, used $83.0895, reserved by unfinished $1.0800 (foreign, not ours; PERMPROBE k1-merge per task), cap $88.96.
  G1 reserve (4×10+30)×$0.0135 = $0.945 → used+reserved+G1 = $85.1145 ≤ $88.96. Own spent $0 + G1 $0.945 ≤ own cap
  $1.95; G1+G2 reserves $1.890 ≤ $1.95. G2 re-checked after G1 terminal/accounting.
- Slots: 1 unfinished in project (foreign); G1 makes 2 (≤ 2), k1-network 1 (≤ 1). Previous k1-network build 19a9e92a
  (SAFETYNET) terminal SUCCESS 2026-11-03T10:00:39Z, accounted in RESULT-SAFETYNET.md. Foreign ledgers untouched.
- Window: main 150 min + closeout 30 min from T0; G1 timeout 70 min, then G2 70 min envelope; both fit inside main
  only if G2 dispatches ≤ ~75 min after T0 (G1 expected ~20–30 min wall).

## G2 dispatch record (coordinator pre-approved G2 in the G1 GO; after G1 terminal/accounting, 2026-11-03T10:26Z)
- G1 c6bc3a65 terminal SUCCESS, 4/4 rows accepted, cost $0.1350 (routesab/g1.result.md). No shared setup/compile error.
- RUN-REQUEST.json := routesab/g2.request.json (sha256 b606895376bb051940a25717e3a128bc7a3910d7a2bb5666bf97700c139f3e00),
  unchanged since e9e70271; library tree d4ec476a and lane files unchanged (this commit touches only research files).
- Budget: project 186 builds, used $83.2245, reserved by unfinished $1.0800 (PERMPROBE 87487311, foreign); + G2 $0.945 =
  $85.2495 ≤ $88.96. Own spent $0.1350 + G2 reserve $0.945 = $1.0800 ≤ $1.95.
- Slots: 1 unfinished in project (foreign); G2 makes 2 (≤ 2), k1-network 1 (≤ 1). Window: T0 10:12:15Z, main ends
  12:42Z; G2 70 min envelope from ~10:27Z ends ~11:37Z plus finishing, inside main.
