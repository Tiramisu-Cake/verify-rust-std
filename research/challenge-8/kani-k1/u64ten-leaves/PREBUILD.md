# U64-TEN-LEAVES PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, executor alone (no subagents). Task: TASK-U64-TEN-LEAVES.md (commit 422f12b98c).
Review SHA is the published research commit carrying this packet.
Branch experiment/kani-k1-usixtyfourten-20261102; base U64-N9 record 9ab925b1578b9102e3009c0ec940c5c9cc0280cb.
Base library commit fddf308321046a8cd8f5526622a5e2353d79830e, library tree d22566ab5a685df2608ddb756714e51ad288f08d.
New library commit e4c696648a5a4ff4f92dbe1ec7ed145afea25ee8, library tree 3c600416e508b037ebdfe817f6dc93d0314c9b21.
Not based on U64-N13; its PARTIAL stage is not resumed. Stable owner k1-network.
Request usixtyfourten-swap9-backing10-insert-tail9-20261102, agent k1-network.
Request SHA256 251b71d59b1df1f160d1b84c8d4a839cfb5f58cd41582a6074910dcfe5d4da42; g1.request.json byte-equal.
Diffs: library.diff, request.diff (zero context). No competitor PR code/branches/diffs opened.

## Diff scope

- `verify/network/u64nine.rs`: only appended comment + `mod tenleaves;` after all existing items
  (static_check: file == base + registration, byte-exact).
- New `verify/network/u64nine/tenleaves.rs` (child `network::u64nine::tenleaves`, 102 lines): 2 PFC roots
  + pure `sorted10_u64`. Inherits the `kani_smallsort_controls` gate of `network::u64nine`. Uses
  parent-private swap_u64_net9/U64Cmp and ancestor-private StrictU64/count_matching_values/
  prefix_unchanged without visibility changes; count9_u64 not needed (counts via count_matching_values,
  result usize, payload/probe u64).
- Untouched (byte-identical, static_check.py): smallsort.rs runtime, network.rs, specfix.rs, ub_checks.rs,
  all u64nine items/targets/contracts/roots, pin/tooling/workflows/flags. No v6/U64-N13/Part 2
  integration, no shared u8/u64 framework, no caller/adapter/context/summary/stub.

## Domain

| | Row 1 swap leaf | Row 2 insertion leaf |
|---|---|---|
| T / F / CMP | u64 / U64Cmp=fn(&u64,&u64)->bool / StrictU64::CMP=reified strict_less::<u64> | same |
| Model / order | full value / ordinary `<` | full value (StrictU64 identity) / `<` |
| Target | existing swap_u64_net9 (unchanged) | existing insert_tail_profile::<StrictU64> (unchanged) |
| Real body | swap_if_less::<u64,U64Cmp> | insert_tail::<u64,U64Cmp> |
| Backing / offset / init | exact `[u64;10]=any`, base+0, fully initialized | exact `[u64;10]=any`, begin base+0 |
| Geometry | a,b any distinct <9 (prefix9) | tail base+9, tail_len10 = whole backing10 writable |
| Probe | independent `probe:u64=any`, by value, after `pre` | `StrictU64::set_probe(any)` before the array, static |
| Frame | 8 cells outside {a,b} unchanged, incl. v[9]==pre[9] | none outside: region = whole allocation |
| Snapshot | `pre=v` all10 before call | `pre=v` all10 before call; covers use pre only |

Value restrictions: none beyond row2's legitimate profile requires model_sorted(begin,9) (assumed by
proof_for_contract at the call). No kani::assume, no manual any_where on values, no sorting constructor,
no sentinel/backing12, no casts/u8/u32/small-value/distinct-value restriction. Row1's only any_where are
the distinct index choices a,b<9. High-bit covers show reachability only, not a domain restriction.
Old exact9 u64 swap leaf (backing9) and LtU64 insertion PFCs (x>>1, other backing/offset) do not cover these.

Requires vs executed: swap_u64_net9 requires canonical cmp, region9_u64 (nonnull, aligned, readable/
writable 9 from v, same_allocation(v,v+8), distinct pair <9); executed domain only base+0 of exact backing10.
insert_tail_profile requires any P, tail distance 1..31 in one allocation, sorted prefix; executed domain
only StrictU64, begin0/tail9 of exact backing10. Credit only for executed domains.

## Roots and annotations (prefix slice::sort::shared::smallsort::verify::network::u64nine::tenleaves::)

| Row | Full annotations | Stubs | Expect | Covers |
|---|---|---|---|---:|
| u64ten_swap_prefix9_backing10 | proof_for_contract(super::swap_u64_net9), unwind(25) | none | SUCCESS | 9/9 |
| u64ten_insert_strict_u64_begin0_tail9 | proof_for_contract(super::super::super::merge::specfix::insert_tail_profile), unwind(25) | none | SUCCESS | 9/9 |

No stub/stub_verified/manual stubs, no new targets/wrappers/contracts. Unwinding assertions on (lane).
Contract-side checks (unchanged targets): row1 swap_transfer (pure pre-pair `<`), swap_ordered,
old/new count9_u64(v,probe), modifies v+a,v+b only; row2 model_sorted(10), old/new model_count(10),
modifies [begin,begin+10) (region-only assigns).

Harness post-checks (literal kani::assert, all expected to hold):
- Row1: `u64ten swap: pair transfer`, `pair ordered`, `active9 count preserved` (count(pre[..9])==count(v[..9])),
  `backing10 count preserved` (same probe), `cells outside pair unchanged` (i<10, i∉{a,b}), `tail v[9] unchanged`.
- Row2 (pure typed, no callback): `u64ten insert: backing10 sorted` (sorted10_u64), `backing10 count preserved`
  (count(pre,probe)==count(post,probe)), `profile probe unchanged`.

Exact required covers, all after the target call, outside targets/ensures (static_check `cover_predicates`):
- Row1 (9): taken=pre[b]<pre[a]; !taken; a==0&&b==8; a==8&&b==0; 0<a<8&&0<b<8; count(pre[..9],probe)>0;
  ==0; probe==pre[9]&&count(pre[..9],probe)==0; probe>=(1u64<<40)&&count(pre,probe)>0.
- Row2 (9): true (returned); pre[9]<pre[0]; pre[8]<=pre[9]; pre[0]<pre[9]&&pre[9]<pre[8]; pre[9]==pre[4];
  !prefix_unchanged(v,pre,0) (output differs); count(pre,probe)>0; ==0; probe>=(1u64<<40)&&count(pre,probe)>0.
All predicates are over pre-state (`pre`, `taken`, hits computed from `pre`), not reread mutated memory,
except "output differs", which compares post v to pre by design. Reachability is source reasoning only.

## Source map of future actual N10 calls (n10-calls.tsv)

<u64 as UnstableSmallSortTypeImpl> -> Freeze impl (smallsort.rs:101); u64 Copy, size8 <= 8 efficient swap,
8*SMALL_SORT_NETWORK_SCRATCH_LEN within stack limit -> small_sort_network (:164); len10: no_merge (:330),
region=whole v (:333); sort9_optimal (:343) makes 25 swap_if_less(v_base,a,b) (:435..459), all pairs
in prefix9 (pair list rechecked against source), v[9] untouched; insertion_sort_shift_left(region,9) (:349)
runs one insert_tail(v_base, v_base+9) (:596); return (:351). No sort13/general/merge/scratch.
Audit data, not executable input; no N10 caller composed here.
Future caller obligations (OPEN): establish prefix-sorted9 by the real network without assume; bind the
swap by-value probe and the StrictU64 static probe to one value before entry and keep their frame;
check raw swap/insert_tail -> summary binding. NETTEN-CALLER needed driver ~14GiB: consider highmem early.

## Static checks, identities, budget

static_check.py PASS (static-check.json): ordinary exact200 unchanged; cfg-on 399 -> 401, exact name-set
delta = the 2 tenleaves names. Static source inventory, not native inventory or proof.
pfc_order.py: ordinary pfc sites 19 -> 21, bad0 (scanner ignores inherited module cfg; swap_u64_net9 at
u64nine.rs:43 precedes `mod tenleaves;` :242; insert_tail_profile specfix.rs:290 in verify::merge precedes
network). Target ordering is a separate fact from the cfg inventory counts.
rustfmt wrapper --check on u64nine.rs + tenleaves.rs exit0; git diff --check PASS; lines <=100.
Protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20; tooling-static.txt hashes equal
NETTEN-LEAVES. Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
Flags: measurement, controls:true, jobs1, uninit off, 10min/row, gcb-e2-standard-4 (k1-standard4,
4CPU/16GiB, swap off), organizer flags retained; kani_k1.py validate accepted 2 rows (g1.args).
Reserve (2*10+30)*$0.0135=$0.675 <= stage cap $1.40; own spent0/reserved0, no UUIDs (runs.json).
Ledger 2026-11-02T16:53:42Z: builds172, used$79.7415, unfinished$0; +$0.675 = $80.4165;
+PARTTWO-TREE G1 $0.675 = $81.0915 <= $88.96. No slot acquired; refresh budget/slots after GO.
Gate: identities match; both real-body PFC SUCCESS, 0 unintended failed checks, 9/9 covers each.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN -> per-row facts, PARTIAL/FAIL, stop; G2 only after G1 compile error
with new review/GO. No local cargo/rustc/Kani/CBMC, dispatch or deployment before GO.
