# U64-N9 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No U64-N9 Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, executor alone (no subagents). Review SHA = the research commit carrying this file.
Task: TASK-U64-N9.md (2cfb24ab4f) incl. coordinator clarification: stable owner `k1-merge`.
Branch experiment/kani-k1-u64nine-20261102; base 58d464ce1ce3d3ad7e60325e3297fdf07d38db4c (NETCOMP2),
base library commit f4d3775dc505ef26e30158cfa7e78f120cd3c30e, tree 3b6d2a51dae08e52464f4b2b82f5168d8ba9977b.
New library commit fddf308321046a8cd8f5526622a5e2353d79830e, library tree d22566ab5a685df2608ddb756714e51ad288f08d.
Request u64nine-n9-leaf-composition-controls-20261102, SHA256
7a0dcbf7cc987602d0d5f309098a7f2c99adf6221b6f136ac0d76f3b2931fead (g1.request.json byte-equals RUN-REQUEST.json).
Full diffs: library.diff, request.diff (zero context). Competitor PRs/branches/diffs not opened.

## Diff scope

New file verify/network/u64nine.rs (sibling `network::u64nine`, 239 lines). network.rs: ONLY appended
`#[cfg(kani_smallsort_controls)] mod u64nine;` at the end (static_check: network.rs == base + 3 lines).
netcomp.rs, runtime smallsort.rs, u8 roots/targets, ordinary cases, Cargo/flags/tooling/workflows/pin unchanged.
No visibility change: private StrictU64, count_matching_values, is_sorted_by, prefix_unchanged are parent items.
No u8 target/context/summary imported; no shared u8/u64 framework. NET18-LEAVES registers in netcomp.rs: disjoint.

## Domain

T=u64 (Copy+Freeze, size8; 8*32=256<=4096 and has_efficient_in_place_swap) -> real Unstable entry
`<u64 as UnstableSmallSortTypeImpl>::small_sort` -> Freeze/Copy impl -> small_sort_network (not general).
len9<18: no_merge, region=full 9 -> sort9_optimal (25 raw swap_if_less) -> insertion_sort_shift_left(offset9)
with zero insertions (no comparator call) -> return; no merge/scratch transfer.
F = `type U64Cmp = fn(&u64,&u64)->bool`, value StrictU64::CMP = reified strict_less::<u64> (ordinary `<`).
Not u8 summaries, not LtU64 (`x>>1`), not function-item F. New typed domain; no transfer claimed.
Backing exact initialized [u64;9], offset0; every positive/leaf input and probe full `kani::any::<u64>`;
no casts/truncation/range restriction (only `u8::MAX as u64` widening inside the high-bit cover).
Leaf pair: arbitrary distinct a,b<9 (only any_where uses). No kani::assume anywhere.

## Target / leaf (independent, no substitutions)

swap_u64_net9(v:*mut u64,a,b,cmp:U64Cmp,probe:u64), line43, before its PFC line49.
requires canonical(cmp); region9_u64: a,b<9, nonnull, aligned, can_dereference+can_write full 9,
same_allocation(v,v+8), swap_geometry (a!=b, same alloc, readable/writable pair).
modifies v+a, v+b only. ensures swap_transfer::<StrictU64>(old(pair_models)) (pure pre-pair `<` branch,
full u64 values), swap_ordered, old(count9_u64(v,probe))==count9_u64(v,probe). Old snapshots are scalars/pair
values. Specs never call the callback. Body: `let mut actual: U64Cmp = cmp; swap_if_less(v,a,b,&mut actual)`.
u64nine_leaf_u64_n9: proof_for_contract(swap_u64_net9), unwind25; no stub/stub_verified; reads no context.
Explicit post asserts: pair transfer, pair ordered, full-value count, other7 unchanged.
Existing swap_contract_u64_n9 (swap_profile<StrictU64>) is design precedent only, not proof of this target.

## Actual call map -> adapter -> summary (actual-calls.tsv)

All25 sort9_optimal calls, smallsort.rs lines435..459, args (v_base,a,b,is_less) unchanged; identical site list
to NETCOMP2 N9 map. Each: raw swap_if_less::<u64,U64Cmp> --kani::stub--> adapter_u64nine<T,F> (same params/
return/two generics) -> sole impl SwapBridgeU64Nine<U64Cmp> for u64 (no blanket/fallback) -> asserts base==
registered root, a/b distinct in range, canonical(*is_less) [guard literal]; on false return w/o summary ->
swap_u64_net9(v,a,b,*is_less,ctx.probe) --stub_verified--> summary; leaf = u64nine_leaf_u64_n9.
The received comparator is forwarded; canonical is never substituted. No other std helper/network replaced.
Pin contract modes: explicit PFC Check / stub_verified Replace precede Assert (contracts.rs#L565 at pin).

## Context lifecycle / ghost boundary

ContextU64Nine{base:*mut u64, probe:u64, initial_count:usize, hits:usize}; static CONTEXT_U64_NINE, own.
register(): plain assignment before the real entry, outside PFC (actual root, by-value probe, computed count,
hits0). Only writes: one register store, one hits+=1 in adapter after summary (outside target write set).
Target/leaf never read/write context. After each summary: assert count9_u64(actual base,ctx.probe)==initial.
run9 on return: canonical cmp unchanged; check_context: hits==25, base/probe/initial-count frame.
Helpers run9/check_context/register carry assertions only; no covers. Context reused only by own roots.

## Rows (prefix slice::sort::shared::smallsort::verify::network::u64nine::)

| Row | Annotations | Expected | Required covers |
|---|---|---|---:|
| u64nine_leaf_u64_n9 | proof_for_contract(swap_u64_net9), unwind(25) | SUCCESS | 7 |
| u64nine_composed_u64_n9 | proof, stub(swap_if_less,adapter_u64nine), stub_verified(swap_u64_net9), unwind(25) | SUCCESS | 7 |
| u64nine_wrong_cmp_u64_n9 | same three as composed + unwind(25) | FAILED guard only | 2 |
| u64nine_count_negative_u64_n9 | same three as composed + unwind(25) | FAILED count only | 3 |

- Leaf: swap taken; swap not taken; first to last; last to first; interior pair; probe hits; probe misses.
- Composed: adapter entered (adapter); all actual exchanges intercepted (root, after run9); sort moves elements;
  probe hits input; probe misses input; duplicates present; high-bit probe hits input (probe>255 && count>0).
- Wrong-cmp: wrong comparator actual entry reached; adapter entered. No sorted/count/hits assertion in root.
- Count-negative: adapter entered; sort returned before corruption; corrupted count check reached.
Exact literals per row in static-check.json `covers_required`. Source reachability expectations, NOT_RUN.
Expected failed literals (unique kani::assert sites in u64nine.rs):
- wrong-cmp: `u64nine canonical comparator required`, line123 (repeats across raw calls allowed).
- count-negative: `u64nine N9 negative: full-value count preserved`, line237.
Count control: [P;9], probe P=1<<40, canonical composed path; hits25/invariant/frame must pass; then
v[8]=1<<41 (>P, low32 bits equal 0 in both), sortedness asserted and passes, count(P) 9->8 fails only there.
UB/unwind/geometry/root/frame/hits/unsupported/ERROR/OOM/TIMEOUT are never intended failures.

## Static checks (static_check.py -> static-check.json PASS; not proof)

Ordinary exact200 (integwrapfix/ordinary-expected.txt); cfg-on exact 395+4=399 by source_inventory.
pfc_order.py: 19 sites, bad0 (+1 = new leaf; scanner does not inherit module cfg). Target line43 < PFC49.
rustfmt wrapper --check on both changed .rs exit0; git diff --check PASS; <=100 cols.
Protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20; tooling-static.txt hashes = NETCOMP2.
Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12. kani_k1.py validate: 4 accepted (g1.args).
measurement, controls:true, jobs1, uninit off, 10min/row, unwind25 + unwinding assertions, gcb-e2-standard-4
(k1-standard4 4CPU/16GiB, swap off), organizer flags unchanged. No local cargo/rustc/Kani/CBMC run.

## Budget, slots, dispatch

Reserve (4*10+30)*$0.0135=$0.945 <= stage cap$2.00; own spent0/reserved0, no UUIDs (runs.json).
Ledger (budget-prebuild.txt): builds165, used$78.2295, unfinished$0; +proposal=$79.1745; +NET18 plan
$0.810=$79.9845<=$88.96. Slots/global ledger: coordinator to confirm (<=2 project, one per owner) before GO.
Dispatch after GO: k1g.sh regex forbids digits in branch name, so per coordinator push non-force alias
experiment/kani-k1-usixtyfournine-20261102 at the reviewed SHA, record it in u64nine/g1.dispatch.txt,
then `k1g.sh wait BUILD` as a Claude Code background task. One Build; G2 only after compile error + new GO.
