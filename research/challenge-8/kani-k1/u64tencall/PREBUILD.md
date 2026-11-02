# U64-TEN-CALLER PRE-BUILD REVIEW — G1 (positive)

Status: WAITING FOR COORDINATOR GO for G1. No Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, executor alone (no subagents). Task: TASK-U64-TEN-CALLER.md (commit c80444e8c6).
Review SHA is the published research commit carrying this packet.
Branch experiment/kani-k1-usixtyfourtencall-20261102; base U64-TEN-LEAVES f057b7e4ebebd2050861976ee8bb0ee0172703c2.
Base library commit e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8, tree 3c600416e508b037ebdfe817f6dc93d0314c9b21.
New library commit a6010df7b451da55d4227ad5960b0c93992f10f0, tree 514c6f841cf2af3b27f6d9aa8f27c86e24c562af.
Stable owner k1-network. Package G1 request usixtyfourtencall-g1-positive-u64-n10-20261102,
SHA256 628c4bfe8d913102a420513fa87698faf97f9bf2af7fa786c568cb2e43db536d; RUN-REQUEST.json byte-equal g1.request.json.
Planned G2 (own PRE-BUILD later): usixtyfourtencall-g2-controls-u64-n10-20261102, SHA256 2344a3b8...e8091862.
Files: library.diff, request.diff (zero context), n10-call-map.tsv, reuse-dependencies.md,
static_check.py/static-check.json, tooling-static.txt, rustfmt-check.txt, budget-prebuild.txt.
NETTEN-CALLER @61cfba69c3 used as phase/control template only (no u8 target/context reused).
No competitor PR code/branches/diffs opened; PARTTWO-TREE files/branch/requests untouched.

## Diff scope

- `verify/network/u64nine/tenleaves.rs`: only appended comment + `mod caller;` after all items.
- New `verify/network/u64nine/tenleaves/caller.rs` (341 lines, child `network::u64nine::tenleaves::caller`):
  ContextU64Ten/CONTEXT_U64_TEN, register_u64ten, backing10_u64, count10_preserved_u64, two closed
  bridges + same-signature adapters, check_context_u64ten/run_u64ten/check_final_u64ten, 4 plain
  `#[kani::proof]` roots. Inherits the `kani_smallsort_controls` gate of `network::u64nine`. Uses
  u64nine-private swap_u64_net9/U64Cmp/canonical/count9_u64, tenleaves-private sorted10_u64,
  network-private StrictU64/count_matching_values; specfix pub(crate) Profile/insert_tail_profile/
  model_sorted/model_count. No visibility widened; no new contracts/targets/requires/ensures/
  modifies/assume/any_where; dedicated context (not CONTEXT_U64_NINE).
- Byte-identical to leaves source 9009451c82 (static_check.py): smallsort.rs runtime, network.rs,
  u64nine.rs, merge.rs, specfix.rs, ub_checks.rs, both leaf roots/targets; pin/tooling/workflows/runner.
  No v6/U64-N13/PARTTWO integration, no generic framework change.

## Typed domain and actual route

T=u64; F=U64Cmp=fn(&u64,&u64)->bool (the actual F of `small_sort(v, &mut cmp)`); value
StrictU64::CMP = reified strict_less::<u64>; full-value model, ordinary `<`.
Positive: `v: [u64;10] = any`, `pre = v`, then `probe: u64 = any` independent; exact initialized
backing10, root = v.as_mut_ptr() (offset0); no requires/assume/any_where; no mask/cast/narrowing.
Route (n10-call-map.tsv from unchanged smallsort.rs): <u64 as UnstableSmallSortTypeImpl>::small_sort
(:101 Freeze) -> Copy, size8 efficient swap -> small_sort_network (:164); len10 no_merge (:330),
region = whole v (:333); sort9_optimal (:343) -> 25 raw swap_if_less(v_base,a,b) :435..459, all pairs
<9 distinct; insertion_sort_shift_left(region,9) (:349) -> one raw insert_tail(v_base, v_base+9)
(:596); return (:351). No sort13/general/merge/scratch. Only the two raw helpers are stubbed.

## Roots and annotations (prefix ...::verify::network::u64nine::tenleaves::caller::)

All 4 roots carry exactly: `#[kani::proof]`,
`#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]`,
`#[kani::stub_verified(super::super::swap_u64_net9)]`,
`#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]`,
`#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]`,
`#[kani::unwind(25)]` (unwinding assertions on in the lane).

| Raw (typed instance reached) | Stub | Closed impl | Forwards to (typed) | Replaced by | Independent leaf (old Build) |
|---|---|---|---|---|---|
| swap_if_less::<u64,U64Cmp> | swap_adapter_u64ten::<u64,U64Cmp> | SwapBridgeU64Ten<U64Cmp> for u64 | swap_u64_net9(v,a,b,*is_less,ctx.probe) | contract (stub_verified) | u64ten_swap_prefix9_backing10, no stubs |
| insert_tail::<u64,U64Cmp> | insert_adapter_u64ten::<u64,U64Cmp> | InsertBridgeU64Ten<U64Cmp> for u64 | insert_tail_profile::<StrictU64>(begin,tail,*is_less) | contract (stub_verified) | u64ten_insert_strict_u64_begin0_tail9, no stubs |

No recursion/self-proof: the targets' bodies (which call the raw helpers) never execute in these
roots; the replacement checks requires, havocs modifies, assumes ensures. Targets are proven only by
the old no-stub PFC leaves. Not stubbed: trait entry, small_sort_network, sort9_optimal,
insertion_sort_shift_left, final checkers. No blanket/fallback impl: any other T/F would not compile.
Target order: swap_u64_net9 (u64nine.rs:43) precedes `mod tenleaves;`; insert_tail_profile
(verify::merge) precedes network; both precede `mod caller;`. pfc_order.py ordinary 21 bad 0 (no new PFC).

## Adapter guards (literal kani::assert; a failing assert cuts the path)

Swap (caller.rs:102): v==ctx.root; a<9&&b<9&&a!=b; canonical(*is_less); backing10_u64(v) (non-null,
aligned, can_dereference/can_write 10, same_allocation v..v+9); StrictU64::probe()==ctx.probe;
insert_hits==0; marker `!fail_swap` (:111) -> swap_u64_net9 (:114, its requires checked) ->
swap_hits+=1 (:116) -> count9_u64(v,probe)==initial_prefix_count9; *v.add(9)==initial_tail (checked base).
Insert (:143): begin==ctx.root; tail==begin.wrapping_add(9); canonical(*is_less); swap_hits==25;
insert_hits==0; backing10_u64(begin); StrictU64::probe()==ctx.probe; ASSERT model_sorted<StrictU64>
(begin,9) (:156); count9_u64==initial_prefix_count9; *tail==initial_tail; model_count<StrictU64>
(begin,10)==initial_count10; marker `!fail_insert` (:172) -> insert_tail_profile (:174, requires incl.
tail_region and sorted prefix checked) -> insert_hits+=1 (:176) -> model_sorted(begin,10),
model_count(10)==initial_count10, probe frame. After insertion tail/prefix9 count are NOT asserted.

## Context phase/counter audit (ContextU64Ten, single static CONTEXT_U64_TEN)

Fields root:*mut u64, probe:u64, initial_prefix_count9, initial_count10, initial_tail:u64,
swap_hits, insert_hits, fail_swap, fail_insert. Written only by register_u64ten (once, before entry,
outside targets; counters 0; :91 StrictU64::set_probe(probe) with the same probe) and the two `+= 1`
lines (static_check: exactly 3 addr_of_mut sites). Phases: swaps need insert_hits==0; insert needs
swap_hits==25 and insert_hits==0. After return (check_context_u64ten :198): swap_hits==25,
insert_hits==1, root/probe/snapshots/flags == registered, root==v, StrictU64::probe()==probe;
run_u64ten also asserts canonical outer cmp unchanged. Count algebra/probe: reuse-dependencies.md.

## Rows and covers (no kani::cover outside root bodies; static_check asserts)

| Pkg | Row | Input | Flags | Expect | expect_check (literal, line) | Covers |
|---|---|---|---|---|---|---:|
| G1 | u64tencall_positive_u64_n10 | any [u64;10], any u64 probe | F/F | SUCCESS | - | 9 |
| G2 | u64tencall_swap_binding_negative_u64_n10 | [0;10], 0 | T/F | FAILED | `u64tencall actual swap adapter binding control` :111 | 1 |
| G2 | u64tencall_insert_binding_negative_u64_n10 | [0;10], 0 | F/T | FAILED | `u64tencall actual insert adapter binding control` :172 | 1 |
| G2 | u64tencall_count_negative_u64_n10 | [2^40;10], 2^40 | F/F | FAILED | `u64tencall negative: full-value count preserved` :339 | 2 |

Positive covers, all after run_u64ten + check_final_u64ten (sorted10_u64, count10_preserved_u64),
predicates over pre/probe, not assumptions: returned (true); descending adjacent pair in pre; probe hits
pre10; probe misses pre10; duplicate in pre10; probe==pre[9]&&count(pre[..9])==0; swap_hits==25&&
insert_hits==1; pre[9]<all pre[0..9]; probe>=(1u64<<40)&&count(pre,probe)>0. Each reachable for
unrestricted input (e.g. descending values with probe at/above 2^40, equal pairs). Consumer-model
reachability only, not leaf evidence.
G2 (reviewed now, dispatched only after own GO): swap control cover before entry, first raw swap passes
all guards on [0;10], fails only the marker; insert control cover before entry, 25 swaps and all insert
premises pass, marker fails; count control: run_u64ten + check_final pass, cover returned-before-
corruption, v[9]=Q=2^41 (same low 32 bits as P), sorted10 holds, cover count-check-reached, the same
count10_preserved_u64 fails only the designated literal (count(P) 10->9). Any other failed check
(canonical/geometry/probe/prefix/hits/frame/UB/unwinding/unsupported) = FAIL, not intended negative.

## Static checks, identities, frozen profile

static_check.py PASS (static-check.json): ordinary exact200; cfg-on 401 -> 405, exact name-set delta =
the 4 caller names; library diff = registration + caller.rs; leaves/dependencies byte-identical to
9009451c82; 25 swap edges (<9 distinct) + single insert_tail call extracted from runtime source; both
requests' rows/expect/expect_check/flags; each expect_check matches exactly one literal.
Static source inventory, not native inventory/proof credit. rustfmt wrapper --check and git diff --check
PASS, lines <=100. Protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20;
tooling-static.txt hashes equal U64-TEN-LEAVES. Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
Both packages: measurement, controls:true, jobs1, uninit off, 10min/row, gcb-e2-standard-4 ->
k1-standard4 (4CPU/16GiB, swap off, $0.0135/min); validator accepted G1 1 row, G2 3 rows (g1.args/g2.args).
G1<->G2: same library commit/tree; only RUN-REQUEST.json and research metadata change between them.
Memory: G1 positive runs in a fresh driver process (no controls); u8 NETTEN driver peak 14.10GiB was a
4-row process; single u64 positive peak unknown. OOM/TIMEOUT G1 -> positive OPEN, G2 still runs.

## Budget and gate

G1 reserve (1*10+30)*$0.0135=$0.540; G2 $0.810; with G1R/G2R $2.700 <= own cap $2.80.
Ledger 2026-11-02T17:26Z: builds173, used$79.8900, unfinished$0; +G1 $0.540 = $80.4300;
+G2 = $81.2400; +PARTTWO-TREE planned $0.675 = $81.9150 <= $88.96 (worst case all four $83.2650).
Own spent0/reserved0, no UUIDs (runs.json). No slot acquired; refresh ledger/slots/deadline after GO.
G1 gate: positive SUCCESS, 0 unintended failed checks, 9/9 covers. G2 gate: 3 controls FAILED only
designated literals, covers 1/1, 1/1, 2/2. Stage PASS needs both plus reuse/identity match; positive
OOM/TIMEOUT/NOT_RUN -> PARTIAL. Compile error -> one repair G1R/G2R with new review/GO.
No local cargo/rustc/Kani/CBMC, Actions dispatch or deployment before GO.
