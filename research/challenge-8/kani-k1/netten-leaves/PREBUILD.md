# NETTEN-LEAVES PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, no subagents. Task: TASK-NETTEN-LEAVES.md (commit4b2c94c1cc).
Review SHA is the published research commit carrying this packet.
Branch experiment/kani-k1-netten-20261102; base NETCOMP2 58d464ce1ce3d3ad7e60325e3297fdf07d38db4c.
Base library commit f4d3775dc505ef26e30158cfa7e78f120cd3c30e, library tree 3b6d2a51dae08e52464f4b2b82f5168d8ba9977b.
New library commit 23ba8cfddbce1cf0313ab402fd6376d157a0f845, library tree 74e42aaa191879280e8e7827c1e32a4ac65d5f18.
Request netten-leaves-swap9-backing10-insert-tail9-20261102, agent k1-merge.
Request SHA256 83e3a4719effb42fdfd0fabaa18fbc07541e1b9c97aed0413d9680291c6f8094; g1.request.json byte-equal.
Diffs: library.diff, request.diff (zero context). No competitor code/branches/diffs opened.

## Diff scope

- `verify/network/netcomp.rs`: only appended `mod netten;` (+comment) after all existing targets/roots.
- New `verify/network/netcomp/netten.rs`: 2 PFC roots + pure `sorted10`; inherits the
  `kani_smallsort_controls` gate of `network::netcomp`; uses parent-private swap_net9/U8Cmp and
  network-private StrictU8/count_matching_values/prefix_unchanged without visibility changes.
- Untouched (byte-identical, static_check.py): smallsort.rs runtime, network.rs, specfix.rs,
  ub_checks.rs, all other netcomp items/targets/contracts/roots, pin/tooling/workflows.
  DIRECTFOUR files (directfour.rs, mergestep.rs) not touched; no NET18/MERGESTEP/U64/v6 integration.

## Domain

| | Row 1 swap leaf | Row 2 insertion leaf |
|---|---|---|
| T / F / CMP | u8 / U8Cmp=fn(&u8,&u8)->bool / StrictU8::CMP=reified strict_less::<u8> | same |
| Model / order | full value / ordinary `<` | full value (StrictU8 identity) / `<` |
| Target | existing swap_net9 (unchanged) | existing insert_tail_profile::<StrictU8> (unchanged) |
| Real body | swap_if_less::<u8,U8Cmp> | insert_tail::<u8,U8Cmp> |
| Backing / offset / init | exact `[u8;10]=any`, base+0, fully initialized | exact `[u8;10]=any`, begin base+0 |
| Geometry | a,b any distinct <9 (prefix9) | tail base+9, tail_len10 = whole backing writable |
| Probe | independent `probe:u8=any`, by value | `StrictU8::set_probe(any)` before the array, static |
| Frame | 8 cells outside {a,b} unchanged, esp. v[9] | none outside: region = whole allocation |
| Snapshot | `pre=v` all10 before call | `pre=v` all10 + `pre_tail=pre[9]` before call |

Only restriction on values: row2's legitimate profile requires model_sorted(begin,9)
(assumed by proof_for_contract at the call); no manual assume/any_where on values, no sorting
constructor. Row1's only any_where are the distinct index choices a,b<9.
Old LtU8 insertion PFCs (x>>1, backing17) and the exact9 swap leaf do not cover these domains.

Requires vs executed: swap_net9 requires admit any allocation with readable/writable >=9 from v,
canonical cmp and distinct pair <9; executed domain is only base+0 of exact backing10.
insert_tail_profile requires admit any P, tail distance 1..31 in one allocation, sorted prefix;
executed domain is only StrictU8, begin0/tail9 of exact backing10. Credit is for executed domains.

## Roots and annotations (prefix slice::sort::shared::smallsort::verify::network::netcomp::netten::)

| Row | Full annotations | Stubs | Expect | Covers |
|---|---|---|---|---:|
| netten_swap_prefix9_backing10 | proof_for_contract(super::swap_net9), unwind(25) | none | SUCCESS | 8/8 |
| netten_insert_strict_u8_begin0_tail9 | proof_for_contract(super::super::super::merge::specfix::insert_tail_profile), unwind(25) | none | SUCCESS | 8/8 |

No stub/stub_verified/manual stubs, no new targets/wrappers/contracts. Unwinding assertions on.
Contract-side checks (from unchanged targets): row1 pair transfer, pair ordered, old/new count9,
modifies v+a,v+b only; row2 model_sorted(10), old/new model_count(10), modifies [begin,begin+10).

Harness post-checks (literal kani::assert, all expected to hold):
- Row1: `netten swap: pair transfer`, `pair ordered`, `active9 count preserved`,
  `backing10 count preserved`, `cells outside pair unchanged` (loop i<10, i∉{a,b}),
  `tail v[9] unchanged`.
- Row2 (pure typed, no callback): `netten insert: backing10 sorted`, `backing10 count preserved`
  (count(pre,probe)==count(post,probe)), `profile probe unchanged`.

Exact required covers (all after the target call, outside targets/ensures):
- Row1: taken=pre[b]<pre[a]; !taken; a==0&&b==8; a==8&&b==0; 0<a<8&&0<b<8;
  count(pre[..9],probe)>0; ==0; probe==pre[9]&&count(pre[..9],probe)==0 (untouched-tail-only hit).
- Row2: true (returned); pre[9]<pre[0]; pre[8]<=pre[9]; pre[0]<pre[9]&&pre[9]<pre[8];
  pre[9]==pre[4]; output!=pre (!prefix_unchanged); count(pre,probe)>0; ==0.
All reachable by source reasoning under sorted prefix9 (e.g. [0..8 ascending] with tail choices);
these are expectations, not executed facts.

## Source map of future actual N10 calls (n10-calls.tsv)

<u8 as UnstableSmallSortFreezeTypeImpl>::small_sort (smallsort.rs:101) -> Freeze+Copy efficient
swap -> small_sort_network (:164); len10: no_merge (:330), region=whole v (:333); sort9_optimal
(:343) makes 25 swap_if_less(v_base,a,b) calls (:435..459), all pairs in prefix9, v[9] untouched;
insertion_sort_shift_left(region,9) (:349) runs one insert_tail(v_base, v_base+9) (:596); return (:351).
No sort13/general/merge/scratch. Audit data, not executable input; no N10 caller composed here.
Future caller obligations (OPEN): establish prefix-sorted9 by the real network without assume;
initialize swap probe and StrictU8 probe to one chosen value before calls and keep their frame;
check raw swap/insert_tail -> summary binding with pre-failure-only witness covers.
Existing controls are not presented as checks of a future insert-tail hook.

## Static checks, identities, budget

static_check.py PASS (static-check.json): ordinary exact200; cfg-on 395 -> 397 (+2 netten names);
pfc_order.py: ordinary pfc sites20 bad0 (scanner ignores inherited module cfg; swap_net9 target
precedes `mod netten;`; insert_tail_profile in verify::merge precedes network). Static, not proof.
rustfmt wrapper --check on netcomp.rs+netten.rs and git diff --check PASS (rustfmt-check.txt).
Protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20; tooling-static.txt hashes
equal NETCOMP2. Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
Flags: measurement, controls:true, jobs1, uninit off, 10min/row, gcb-e2-standard-4 (k1-standard4,
4CPU/16GiB, swap off), organizer flags retained; validator accepted 2 rows (g1.args).
Reserve (2*10+30)*$0.0135=$0.675 <= stage cap$1.40; own spent0/reserved0, no UUIDs (runs.json).
Ledger 2026-11-02T15:27Z: builds168, used$79.0395, unfinished$0; +$0.675 = $79.7145;
+DIRECTFOUR $0.540 = $80.2545 <= $88.96. No slot acquired; refresh before dispatch after GO.
Gate: identities match; both rows SUCCESS, 0 unexpected failed checks, 8/8 covers each.
TIMEOUT/OOM/FAILED/coverage/UNKNOWN -> per-row facts, PARTIAL/FAIL, stop; G2 only after G1
compile error with new review/GO. No local cargo/rustc/Kani/CBMC, dispatch or deployment.
