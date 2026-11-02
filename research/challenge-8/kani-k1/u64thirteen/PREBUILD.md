# U64-N13 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No U64-N13 Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, executor alone (no subagents). Review SHA = the research commit carrying this file.
Task: TASK-U64-N13.md (4ddef5b62a). Stable owner `k1-merge`; U64-N9 terminal, not part of this stage.
Branch experiment/kani-k1-usixtyfourthirteen-20261102 (matches k1g.sh dispatch regex; no alias needed).
Base 9ab925b1578b9102e3009c0ec940c5c9cc0280cb (U64-N9 record), base library commit
fddf308321046a8cd8f5526622a5e2353d79830e, base tree d22566ab5a685df2608ddb756714e51ad288f08d.
New library commit 497077c6cd14fdbcc439807c0cdc186860cb00ce, library tree 90a3889318f1db39163e8fe9e382da39d9cf5e85.
Request u64thirteen-n13-leaf-composition-controls-20261102, SHA256
cf8693f597c243b5e084dcc96e877084e7fa48e98e1b5977cacad57493991e67 (g1.request.json byte-equals RUN-REQUEST.json).
Full diffs: library.diff, request.diff (zero context). Competitor PRs/branches/diffs not opened.

## Diff scope

New file verify/network/u64nine/uthirteen.rs (child `network::u64nine::uthirteen`, 242 lines; inherits
the parent's `#[cfg(kani_smallsort_controls)]`). u64nine.rs: ONLY appended a comment + `mod uthirteen;`
after all existing targets/roots (static_check: u64nine.rs == base + 3 lines). network.rs, netcomp.rs
(MERGESTEP area), runtime smallsort.rs, all N9/u8 roots/targets/contracts/ContextU64Nine/counters,
ordinary cases, Cargo/flags/tooling/workflows/pin unchanged. No visibility change: imported from parent
private U64Cmp/canonical/always_true_u64 (pure), from network private StrictU64/count_matching_values/
is_sorted_by/prefix_unchanged. No N9 target/count9/run9/adapter/context is called (static_check asserts
absence of every N9 item name and of literals 9/8/7). NET18/MERGESTEP/MACSPLIT/v6/DOMSIX not integrated.

## Domain

T=u64 (Copy+Freeze, size8; 8*32=256<=4096, has_efficient_in_place_swap) -> real Unstable entry
`<u64 as UnstableSmallSortTypeImpl>::small_sort` -> Freeze/Copy impl -> small_sort_network (not general).
len13<18: no_merge, region=full13 -> region.len()>=13 -> sort13_optimal (45 raw swap_if_less) ->
insertion_sort_shift_left(region,13): tail==v_end, zero insert_tail/comparator calls -> return.
No sort9/sort25, no N18 halves, no merge/scratch transfer.
F = `type U64Cmp = fn(&u64,&u64)->bool`, value StrictU64::CMP = reified strict_less::<u64> (default `<`).
Not u8 summaries, not N9 summary/PFC, not LtU64, not function-item F, not arbitrary FnMut.
Backing exact initialized [u64;13], offset0; every positive/leaf input and probe full `kani::any::<u64>`;
no casts/truncation/range restriction/presort (only `u8::MAX as u64` widening inside the high-bit cover).
Leaf pair: arbitrary distinct a,b<13 (the only two any_where). No kani::assume anywhere.

## Target / leaf (row1, independent, no substitutions)

swap_u64_net13(v:*mut u64,a,b,cmp:U64Cmp,probe:u64), line41, before its PFC line47.
requires canonical(cmp) [received cmp]; region13_u64: a,b<13, nonnull, aligned, can_dereference+can_write
full 13, same_allocation(v,v+12), swap_geometry (a!=b, same alloc, readable/writable pair).
modifies v+a, v+b only. ensures swap_transfer::<StrictU64>(old(pair_models)) (pure pre-pair `<` branch,
full u64 values), swap_ordered, old(count13_u64(v,probe))==count13_u64(v,probe). Old = scalar count /
pair values, no pointer snapshot. Specs never call the callback; no context/probe-global reads or ghost
writes in target. Body: `let mut actual: U64Cmp = cmp; swap_if_less(v,a,b,&mut actual)`; no stubs.
u64thirteen_leaf_u64_n13: proof_for_contract(swap_u64_net13), unwind25; no stub/stub_verified; no context.
Full any [u64;13], independent any u64 probe, canonical U64Cmp. Explicit post asserts: pair transfer,
pair ordered, full-value count, other11 unchanged (loop over 13, skip a/b).

## Actual call map -> adapter -> summary (actual-calls.tsv, 45 rows)

All45 sort13_optimal calls, smallsort.rs lines484..528 (fn469..530), args (v_base,a,b,is_less) unchanged:
484(0,12) 485(1,10) 486(2,9) 487(3,7) 488(5,11) 489(6,8) 490(1,6) 491(2,3) 492(4,11) 493(7,9)
494(8,10) 495(0,4) 496(1,2) 497(3,6) 498(7,8) 499(9,10) 500(11,12) 501(4,6) 502(5,9) 503(8,11)
504(10,12) 505(0,5) 506(3,8) 507(4,7) 508(6,11) 509(9,10) 510(0,1) 511(2,5) 512(6,9) 513(7,8)
514(10,11) 515(1,3) 516(2,4) 517(5,6) 518(9,10) 519(1,2) 520(3,4) 521(5,7) 522(6,8) 523(2,3)
524(4,5) 525(6,7) 526(8,9) 527(3,4) 528(5,6). Same site list as NETCOMP2 N13 map (runtime unchanged);
static_check re-derives it from source and checks each pair distinct/<13. Single caller line340.
Each edge: raw swap_if_less::<u64,U64Cmp> --kani::stub--> adapter_u64thirteen<T,F> (line144; same params/
return/two generics) -> sole impl SwapBridgeU64Thirteen<U64Cmp> for u64 (line117; no blanket/fallback) ->
asserts base==registered root, a/b distinct <13, canonical(*is_less) [guard literal line127]; on false
return w/o summary -> swap_u64_net13(v,a,b,*is_less,ctx.probe) --stub_verified--> summary;
leaf = u64thirteen_leaf_u64_n13. Received comparator forwarded; canonical never substituted.
No other std helper/network/insertion body replaced.

## Context lifecycle / ghost boundary

ContextU64Thirteen{base:*mut u64, probe:u64, initial_count:usize, hits:usize}; own static
CONTEXT_U64_THIRTEEN (CONTEXT_U64_NINE untouched). register13(): one plain assignment of the full
struct (actual root, by-value probe, computed count, hits0) before the real entry, outside PFC.
Only writes: line109 register store, line135 hits+=1 in adapter after summary (outside target write set).
After each summary: assert count13_u64(actual base,ctx.probe)==initial_count. run13 on return:
canonical cmp unchanged; check_context13: hits==45, base/probe/initial-count frame.
Helpers run13/check_context13/register13 carry assertions only; no covers.

## Rows (prefix slice::sort::shared::smallsort::verify::network::u64nine::uthirteen::)

| Row | Annotations | Expected | Required covers |
|---|---|---|---:|
| u64thirteen_leaf_u64_n13 | proof_for_contract(swap_u64_net13), unwind(25) | SUCCESS | 7 |
| u64thirteen_composed_u64_n13 | proof, stub(swap_if_less,adapter_u64thirteen), stub_verified(swap_u64_net13), unwind(25) | SUCCESS | 7 |
| u64thirteen_wrong_cmp_u64_n13 | same four as composed | FAILED guard only | 2 |
| u64thirteen_count_negative_u64_n13 | same four as composed | FAILED count only | 3 |

Full annotation list in file: target 2 requires/1 modifies/3 ensures; leaf 2; three roots x4 = 20 total.
- Leaf: swap taken; swap not taken; first to last (0,12); last to first (12,0); interior pair; probe hits; probe misses.
- Composed: adapter entered (adapter); all actual exchanges intercepted (root, after return, hits==45);
  sort moves elements; probe hits input; probe misses input; duplicates present; high-bit probe hits input.
- Wrong-cmp: wrong comparator actual entry reached; adapter entered. No sorted/count/hits assertion in root.
- Count-negative: adapter entered; sort returned before corruption; corrupted count check reached.
Exact literals per row in static-check.json `covers_required`. Reachability expectations, NOT_RUN.
Expected failed literals (unique kani::assert sites, absent from u64nine.rs/netcomp.rs/network.rs):
- wrong-cmp: `u64thirteen canonical comparator required`, line127 (repeats across 45 raw calls allowed).
- count-negative: `u64thirteen N13 negative: full-value count preserved`, line240.
Count control: [P;13], probe P=1<<40, canonical composed path; hits45/invariant/frame must pass; then
v[12]=1<<41 (>P, low32 bits both 0), sortedness asserted and passes, count(P) 13->12 fails only there.
UB/unwind/geometry/root/frame/hits/unsupported/setup/ERROR/OOM/TIMEOUT are never intended failures.

## Static checks (static_check.py -> static-check.json PASS; not proof)

Ordinary exact200 (integwrapfix/ordinary-expected.txt); cfg-on exact 399+4=403 by source_inventory.
pfc_order.py: 20 sites, bad0 (+1 = new leaf; scanner does not inherit module cfg). Target line41 < PFC47.
rustfmt wrapper --check on both changed .rs exit0; git diff --check PASS; <=100 cols.
Protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20; tooling-static.txt hashes = U64-N9.
Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12. kani_k1.py validate: 4 accepted (g1.args).
measurement, controls:true, jobs1, uninit off, 10min/row, unwind25 + unwinding assertions, gcb-e2-standard-4
(k1-standard4 4CPU/16GiB, swap off), organizer flags unchanged. No local cargo/rustc/Kani/CBMC run.
Resource note: u8 B13 driver reached ~8GiB; u64 N13 cost is not predicted linearly from u8 B13/u64 B9.

## Budget, slots, dispatch

Reserve (4*10+30)*$0.0135=$0.945 <= stage cap$2.00; own spent0/reserved0, no UUIDs (runs.json).
Ledger (budget-prebuild.txt): builds167, used$78.4185, unfinished$1.2150 (MERGESTEP G1-sized, k1-network);
+proposal=$80.5785<=$88.96. Coordinator to confirm both slot states (<=2 project, <=1 per owner) before GO.
After GO: refresh budget, `k1g.sh dispatch experiment/kani-k1-usixtyfourthirteen-20261102` at the reviewed
SHA, record g1.dispatch.txt, then `k1g.sh wait BUILD` as a Claude Code background task. One Build;
G2 only after compile error + new review/GO.
