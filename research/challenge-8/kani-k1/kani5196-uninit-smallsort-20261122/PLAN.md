# SmallSort uninit experiment on Kani #5196

Run one targeted fork Actions job after the pending #752 binding check releases the shared lane. Use the exact #5196 head `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` (tree `15816aaf3b6dfa4855452e34825073db8ca6760f`) as published. GitHub metadata at planning time reports this head as open and conflicting with main. Its pinned `nightly-2026-11-19` and CBMC 6.11.0 match the accepted std candidate's tool generation. An integration merge would add changes to the instrumenter and make the tested source a local variant. Use one harness per Kani process and fresh directories because this head predates main's per-harness delayed UB isolation. Record the experiment against the whole tested tool commit. [Task and owner GO](TASK.md) · [Kani #5196](https://github.com/model-checking/kani/pull/5196) · [Worker task](IMPL-TASK.md)

#5196 changes initialization tracking for unions inside non-union aggregates and behind raw pointers, including copies and reads from `MaybeUninit`. Unions nested inside unions and transmutes into unions remain unsupported. The reported 10–25 GB cost in #5199 concerns union values crossing contract calls. Selected SmallSort scratch is passed by slices or pointers. Generated contract code can still make its own copies. #5199 reports the peak during SSA-to-SAT conversion, so retain phase and CNF markers as well as peak RSS. [Kani #5151](https://github.com/model-checking/kani/issues/5151) · [Kani #5196](https://github.com/model-checking/kani/pull/5196) · [Kani #5199](https://github.com/model-checking/kani/issues/5199)

## Std pins and matched roster

| Pin | Commit and tree | Scope |
| --- | --- | --- |
| Candidate | `152f11556ab19c6dcfa21b5a0f1096603530ce67` / `08c6c08235035dbca44715c4b4822f5c34c041f6` | All seven SmallSort rows. The organizer OFF matrix on Kani `9834c96ce9` is context. The campaign collects its own matched OFF observations |
| PR head | `872d5a43380752786415bc00d2a12ce0e930cb37` / `384023c2f80a04d0618aa7ce971b1419494b062b` | Five shared rows. GitHub #752 still points to this head. This checkout declares `nightly-2026-10-22`. Test it verbatim using the compiler from the #5196 build |

For each selected std row run OFF then ON, with the same source, tool, harness, effective solver, unwind, cfg, and allocation. The two trait contract roots exist only on the candidate. The five shared harness modules and `smallsort` bodies match across the two trees, but the std versions and trait annotations differ. Interpret each pair within its own pin. [#752 head](https://github.com/model-checking/verify-rust-std/pull/752) · [Candidate organizer baseline](../pr752-trait-contracts-20261122/RUN-45018616243-SUMMARY.md)

Prefix every std selector with `slice::sort::shared::smallsort::verify::`. "Plain" permits the root's existing order-violation panic stub, where present. Every row runs at 8 GiB local. Durations are `--harness-timeout` / whole-child wall, in seconds.

| ID | Exact selector suffix | Pins | Mode and scratch | Unwind | Seconds |
| --- | --- | --- | --- | ---: | ---: |
| S2 | `scratch_geometry::stable_u64_min_scratch_n2` | Both | Plain actual Stable, two `u64`, disjoint scratch18 | 34 | 240 / 300 |
| UF2 | `merge::route_safety_all_routes_n2` | Both | Plain direct general plus real Stable and Unstable→Freeze default via non-Copy `WrappedU64`, scratch48. Keep all three return covers | 34 | 240 / 300 |
| N18 | `network::dispatch_reachability_network_u8_n18` | Both | Plain actual Unstable→Freeze Copy network, two sort9 halves, actual bidirectional merge and copy-back from private scratch32 | 65 | 360 / 420 |
| M8-C | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | Both | Real `bidirectional_merge` Check on scratch48, initialized `[32..40)`, destination `[0..8)`, source frame | 34 | 240 / 300 |
| M8-R | `helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | Both | Real sort8 and sort4 calls, `bidirectional_merge` Replace with M8-C geometry. Check initialization up to the call and caller frame on return | 34 | 240 / 300 |
| S2-C | `trait_contracts::stable_sorts_permutation_u64_len2` | Candidate | Direct Stable specialized Check, scratch18 through `&mut [MaybeUninit<u64>]`, writes to `v,scratch` | 32 | 240 / 300 |
| F2-C | `trait_contracts::freeze_default_sorts_permutation_noncopy_u8_backing4` | Candidate | Direct Freeze `default fn` Check, `backing[1..3]`, `NonCopyKey`, private scratch48, writes to `v` | 32 | 240 / 300 |

[S2](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort/verify/scratch_geometry.rs:26) · [UF2](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:249) · [N18](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort/verify/network.rs:356) · [M8 pair](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts_wide.rs:100) · [Direct trait contract fixtures](../pr752-trait-contracts-20261122/IMPL-HANDOFF.md#ordinary-roots-и-ожидаемое-evidence)

Run two ON-only instrumentation controls first, copying the pinned `tests/expected/uninit/nested-unions/main.rs` verbatim into each root's private target area.

| Exact standalone selector | Expected result on #5196 |
| --- | --- |
| `buffer_written_then_read_ok` | `SUCCESS` with no failed or unsupported construct. Writes all `[MaybeUninit<u32>;4]` elements before a raw read at an arbitrary in-bounds index |
| `buffer_partly_written_ub` | `FAILURE` on the two pinned uninitialized-read checks, for `*const u32` and `u32`, at the raw read of slot 2 after writing slot 0. Match the native IDs and read site, with no other failure or unsupported construct |

Both controls have default unwind 8, 90 s harness / 120 s whole-child. A control mismatch leaves the run uncalibrated. Stop early for a confirmed shared launch, compiler or flag fault and preserve available data. Otherwise continue capturing independent roots. Run all candidate pairs before the older PR-head pairs. S2 OFF on the older pin also probes compiler compatibility. A confirmed tree-wide compile or link incompatibility marks the rest of that pin `NOT_RUN` with the exact diagnostic, leaving the candidate observations intact. [Pinned control source](https://github.com/model-checking/kani/blob/bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a/tests/expected/uninit/nested-unions/main.rs#L34-L53) · [Pinned expected outcomes](https://github.com/model-checking/kani/blob/bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a/tests/expected/uninit/nested-unions/expected)

## Invocation and budget

Use one Ubuntu 24.04 serial job with one #5196 tool build. For std, invoke the pinned launcher directly and retain the organizer flags. Append `-Z uninit-checks` only for ON. Kani's stock CaDiCaL and the root's unwind attribute remain in force. Keep memory/bounds/overflow/unwind/reachability checks and the original contract and panic stub modes. `RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS` and host `RUSTUP_TOOLCHAIN` overrides are unset. Record the actual compiler for both std trees.

```bash
"$TOOL/scripts/kani" verify-std -Z unstable-options -Z function-contracts -Z mem-predicates \
  -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts \
  "${uninit_flags[@]}" --harness "$selector" --exact --jobs=1 --output-format=regular \
  --harness-timeout "${harness_seconds}s" -Z export-json --export-json "$root_export" \
  --verbose --target-dir "$root_target" "$STD/library" --cbmc-args --object-bits 12
```

For the standalone controls use the same launcher with the copied `main.rs` as the input instead of `verify-std`. Use `-Z unstable-options -Z uninit-checks -Z export-json`, `--harness <name> --exact --jobs=1 --default-unwind 8 --harness-timeout 90s --output-format=regular --verbose --export-json <fresh-file>` and `--cbmc-args --object-bits 12`. Run from the private directory containing the copy.

26 invocations maximum. Twenty std invocations × 300 s, four N18 × 420 s and two controls × 120 s give 7,920 child seconds (132 min). A 180-minute job leaves 30 min for setup, 9 min for finalization and 9 min spare. Refuse launches that lack the whole-child window plus 30 s before verification cutoff. Apply an 8 GiB child PGID ceiling, 12 GiB outer owned-tree ceiling and 2 GiB runner-memory reserve. Record the lower effective cap and reap before starting another root. Earlier OFF observations for S2, M8-C/M8-R and S2-C were roughly 4–6, 94/7 and 112 s native VT on earlier pins. Treat those as sizing anchors. ON remains unmeasured. [Helper timings](../RESULT-INTEGCHECK.md) · [Trait Check timings](../pr752-trait-contracts-20261122/IMPL-HANDOFF.md#ordinary-roots-и-ожидаемое-evidence)

Fork uses one existing control slot and $0 GCB. A comparable standard-4 GCB build would reserve 132 + 30 = 162 min, about **$2.19** at $0.0135/min, assuming an adapted single-build controller. The stock `k1g.sh` path would need changes for mixed source trees, per-case limits and the enforced 8 GiB cap. If split into two otherwise comparable builds, setup reserve alone raises the estimate to **$2.59**. Any GCB switch needs a new reservation under the shared $10 item-2 ceiling and confirmation of Evidence Brief access, plus coordinator review. Schedule this fork job behind the binding check. [GCB rate and accounting](../tools/k1g.sh)

## Offline results and item 1

- Use an exact per-root native property inventory from regular output and reconcile it with stock export and terminal status. Record commit/tree, tool/dependency identity, compiler and actual argv, selector, flags, contract mode, solver, unwind, exit, summaries, required covers and uninit instrumentation evidence. Record IDs, class, status, description and source coordinates for unsupported constructs, including any marked UNREACHABLE. Name the concrete type/layout or operation and mapped source path where the evidence permits. Keep missing identity or coverage explicit.
- Report each row as completed with no unsupported construct and covered native uninit reads, completed with unsupported construct, uninit-read failure pending triage, other property failure, compile/link failure, or timed out/RSS-limited/otherwise incomplete. Distinguish a reported but unreachable construct from zero reported constructs. A clean result requires evidence that uninit instrumentation covers the relevant actual reads, satisfied route/return covers where present and valid unwinding. For M8-R bind the actual caller and Replace mode. The stub provides a write set for the destination, and this harness does not observe destination initialization.
- Compare ON/OFF native VT, compile/child wall and sampled child PGID peak with compiler/backend attribution where available. Show deltas or ratios for completed pairs. A cutoff is a censored observation and does not identify #5199 as its cause. Capture the phase and exact checked counters. Retain unsupported and uninit-read evidence separately if both are reported. For any suspected uninitialized read, trace the initialized spans, writes/copies, read width and whether it occurred in the real body, model or harness. Keep both real defect and model imprecision open until a minimal reproducer distinguishes them. A version shift from `9834c96ce9` to this full PR stack means the run establishes behavior on the tested tool, with no isolated attribution to one patch.
- Before item 1 claims uninit coverage, qualify the merged or otherwise accepted organizer pin with matched ON controls and native mode binding. Expand coverage to every fixture/domain named in the claim, resolving unsupported layouts, resource failures and reproduced alarms. If a harness change is justified, qualify the exact changed fixture with matched ON/OFF and preserve its original obligation. Bound the statement by type, length, comparator, allocation and panic-cut scope. Value validity, immutable-memory checks, unwinding and wider inputs remain separate obligations.
