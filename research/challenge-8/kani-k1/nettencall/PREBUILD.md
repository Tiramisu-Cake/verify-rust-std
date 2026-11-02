# NETTEN-CALLER PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, no subagents. Task: TASK-NETTEN-CALLER.md (commit 844ce8c0c9).
Review SHA is the published research commit carrying this packet.
Branch experiment/kani-k1-nettencall-20261102; base NETTEN-LEAVES 9835bd00dc4bf386e68e5f7885964a17d0dda240.
Base library commit 23ba8cfddbce1cf0313ab402fd6376d157a0f845, tree 74e42aaa191879280e8e7827c1e32a4ac65d5f18.
New library commit 2ebda13e1445186f53a12b69a4419aafe4f17e1b, tree 40d3b22c82551eafb6d55510bf0bba2bcfbebf74.
Request nettencall-u8-n10-swap9-insert-tail-caller-20261102, agent k1-merge.
Request SHA256 799bc58aa4ce933436fb11f6d0854dd2347f60f80479bfcebd4a42c180d34dab; g1.request.json byte-equal.
Files: library.diff, request.diff (zero context), n10-call-map.tsv, reuse-dependencies.md,
static_check.py/static-check.json. No competitor code/branches/diffs opened.

## Diff scope

- `verify/network/netcomp/netten.rs`: only appended `mod caller;` (+comment) after all items.
- New `verify/network/netcomp/netten/caller.rs` (324 lines): ContextTen, register10, two closed
  bridges + same-signature adapters, check_context10/run10/check_final10, 4 plain `#[kani::proof]`
  roots. Inherits the `kani_smallsort_controls` gate of `network::netcomp`. Uses ancestor-private
  swap_net9/U8Cmp/canonical/count9, netten-private sorted10, network-private StrictU8/
  count_matching_values; specfix pub(crate) Profile/insert_tail_profile/model_sorted/model_count.
  No visibility widened, no new contracts/targets/requires/ensures/modifies/assume/any_where.
- Byte-identical (static_check.py): smallsort.rs runtime, network.rs, netcomp.rs, specfix.rs,
  ub_checks.rs, both NETTEN leaf roots/targets; pin/tooling/workflows/runner. DIRECTFOUR files
  (directfour.rs, mergestep.rs) untouched; no NET18/MERGESTEP/U64/v6/DOMSIX integration.

## Typed domain and actual route

T=u8; F=U8Cmp=fn(&u8,&u8)->bool (the actual F of `small_sort(v, &mut cmp)`); value
StrictU8::CMP = reified strict_less::<u8>; full-value model, ordinary `<`.
Positive: `v: [u8;10] = any`, `probe: u8 = any` independent; exact initialized backing10, root
= v.as_mut_ptr() (offset0); no requires/assume linking probe and input. Controls: [0;10], probe0.
Route (n10-call-map.tsv, unchanged smallsort.rs): <u8 as UnstableSmallSortTypeImpl>::small_sort
-> Freeze+Copy efficient swap -> small_sort_network; len10 no_merge, region=whole v;
sort9_optimal (:343) -> 25 raw swap_if_less(v_base,a,b) :435..459, all pairs <9;
insertion_sort_shift_left(region,9) (:349) -> one raw insert_tail(v_base, v_base+9) (:596); return.
Network and insertion_sort_shift_left run unchanged; only the two raw helpers are stubbed.

## Roots and annotations (prefix ...::verify::network::netcomp::netten::caller::)

All 4 roots carry exactly: `#[kani::proof]`,
`#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]`,
`#[kani::stub_verified(super::super::swap_net9)]`,
`#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]`,
`#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]`,
`#[kani::unwind(25)]` (unwinding assertions on in the lane).

| Raw (typed instance reached) | Stub | Closed impl | Forwards to (typed) | Replaced by |
|---|---|---|---|---|
| swap_if_less::<u8,U8Cmp> | swap_adapter10::<u8,U8Cmp> | SwapBridge10<U8Cmp> for u8 | swap_net9(v,a,b,*is_less,ctx.probe) | swap_net9 contract (stub_verified) |
| insert_tail::<u8,U8Cmp> | insert_adapter10::<u8,U8Cmp> | InsertBridge10<U8Cmp> for u8 | insert_tail_profile::<StrictU8>(begin,tail,*is_less) | profile contract (stub_verified) |

No recursion/self-proof: the targets' own bodies (which call the raw helpers) are never executed in
these roots; the replacement checks requires, havocs the modifies set, assumes ensures. The targets
are proven only by the separate old no-stub PFC leaves (no stubs there). Not stubbed: trait entry,
small_sort_network, sort9_optimal, insertion_sort_shift_left, final checkers. No blanket/fallback
bridge impl: any other T/F instance would fail to compile, not silently bypass.
Target order: swap_net9 (netcomp.rs) precedes `mod netten;`; insert_tail_profile (verify::merge)
precedes network; both precede `mod caller;`. pfc_order.py ordinary 20 bad 0 (no new PFC).

## Adapter guards (all literal kani::assert; failing assert cuts the path)

Swap adapter (caller.rs:92): v==ctx.root; a<9&&b<9&&a!=b; canonical(*is_less); backing10(v)
(non-null, aligned, can_dereference/can_write 10, same_allocation v..v+9); StrictU8::probe()==ctx.probe;
ctx.insert_hits==0; marker `!fail_swap` (:101) -> swap_net9 (:104, its requires also checked) ->
swap_hits+=1 -> count9(v,probe)==initial_prefix_count9; *v.add(9)==initial_tail (read via checked base).
Insert adapter (:133): begin==ctx.root; tail==begin.wrapping_add(9); canonical(*is_less);
swap_hits==25; insert_hits==0; backing10(begin); StrictU8::probe()==ctx.probe;
model_sorted<StrictU8>(begin,9) (:146, real network must prove it); count9==initial_prefix_count9;
*tail==initial_tail; model_count<StrictU8>(begin,10)==initial_count10; marker `!fail_insert` (:162)
-> insert_tail_profile (:164) -> insert_hits+=1 -> model_sorted(begin,10), model_count(10)==
initial_count10, probe frame. After insertion tail/prefix9-count are NOT asserted (may change).
Ghost counters are written only here, outside the targets' write sets; statics never in modifies.

## Context phase/counter audit (ContextTen, single static CONTEXT_TEN)

Fields root/probe/initial_prefix_count9/initial_count10/initial_tail/swap_hits/insert_hits/
fail_swap/fail_insert. Written: register10 (once, before entry, outside targets; counters 0) and the
two `+= 1` lines. Phases: swaps require insert_hits==0; insert requires swap_hits==25, insert_hits==0.
After return (check_context10): swap_hits==25, insert_hits==1, root/probe/snapshots/flags equal the
registered value, root==v, probe==root probe, StrictU8::probe()==probe; run10 also asserts canonical
outer cmp unchanged. Count algebra and single-probe setup: reuse-dependencies.md.

## Rows, controls and covers (no kani::cover in any helper/adapter; static_check asserts)

| Row | Input | Flags | Expect | expect_check (literal, line) | Covers |
|---|---|---|---|---|---:|
| nettencall_positive_u8_n10 | any [u8;10], any probe | F/F | SUCCESS | - | 8 |
| nettencall_swap_binding_negative_u8_n10 | [0;10], 0 | T/F | FAILED | `nettencall actual swap adapter binding control` :101 | 1 |
| nettencall_insert_binding_negative_u8_n10 | [0;10], 0 | F/T | FAILED | `nettencall actual insert adapter binding control` :162 | 1 |
| nettencall_count_negative_u8_n10 | [0;10], 0 | F/F | FAILED | `nettencall negative: full-value count preserved` :322 | 2 |

Positive covers, all after run10 + check_final10 (sorted10, full count), predicates over pre/probe:
returned (true); descending adjacent pair in pre; probe hits pre10; probe misses pre10; duplicate
value in pre10; probe==pre[9] && count(pre[..9])==0; swap_hits==25&&insert_hits==1; pre[9]<all
pre[0..9]. Each reachable for unrestricted input (e.g. [9,8,..,0]/probe 0 or 200; [1,1,..]).
Swap control: cover `nettencall swap control: actual entry reached` before entry; the first raw
swap passes all guards on [0;10], fails only the marker; no post-return obligations.
Insert control: cover `nettencall insert control: actual entry reached` before entry; 25 swaps pass,
insert guards incl. prefix-sorted/counts pass, marker fails; nothing after entry.
Count control: run10 (all phases/hits/frames) + check_final10 pass; cover `returned before
corruption`; v[9]=1; assert sorted10 `nettencall negative: sorted after corruption` holds; cover
`count check reached`; count(0) 10->9 fails only the designated literal (same typed checker).
Any other failed check (canonical/geometry/probe/prefix-sorted/hit/frame/UB/unwinding/unsupported)
= FAIL stage. Checks after an expected failing marker may be unreachable; not post-guard witnesses.

## Static checks, identities, budget

static_check.py PASS (static-check.json): ordinary exact200; cfg-on 397 -> 401 (+4 caller names);
library diff = registration + caller.rs only; leaves and all dependencies byte-identical to reviewed
1914e42274; 25 swap edges (<9, distinct) + single insert_tail call extracted from runtime source.
Static, not native proof inventory. rustfmt wrapper --check and git diff --check PASS.
Protected lane paths equal 30f77e8599; tooling-static.txt hashes equal NETTEN-LEAVES/NETCOMP2.
Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
Flags: measurement, controls:true, jobs1, uninit off, 10min/row, gcb-e2-standard-4 (k1-standard4,
4CPU/16GiB, swap off), organizer flags retained; validator accepted 4 rows (g1.args).
Reserve (4*10+30)*$0.0135=$0.945 <= stage cap$2.00; own spent0/reserved0 (runs.json).
Ledger 2026-11-02T16:08Z: builds171, used$79.4580, unfinished$0; +$0.945=$80.403;
+DIRECTFOUR G2 $0.540=$80.943 <= $88.96. No slot acquired; refresh before dispatch after GO.
Gate: identities/domain/reuse match; positive SUCCESS 0 unintended failed and 8/8 covers; controls
FAILED only designated literals with 1/1, 1/1, 2/2 covers; both old leaves and source integrity kept.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN -> per-row facts, PARTIAL/FAIL, stop. G2 only after G1 compile
error (same 4 rows/flags, new review/GO, reserve$0.945). No local cargo/rustc/Kani/CBMC/dispatch.
