# NET18-LEAVES PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No NET18-LEAVES Build submitted; compile/proof/covers NOT_RUN.
Review SHA is the published research/request commit carrying this packet (Runtime: Claude Code).
Task: TASK-NET18-LEAVES.md @3c9e00b9e1a3b66220f9032e113bf8a0f5450626, with retained TASK-NETCOMP/NETCOMP2 limits.
Branch experiment/kani-k1-net18leaves-20261102. Base NETCOMP2 58d464ce1ce3d3ad7e60325e3297fdf07d38db4c,
base library commit f4d3775dc505ef26e30158cfa7e78f120cd3c30e, base library tree 3b6d2a51dae08e52464f4b2b82f5168d8ba9977b.
Library commit 4eb7e81259f843da6517a8de97c68e23b584eb76; library tree 1fa41b3a5f101ee3981787f71588bfc22e2aae5b.
Request net18-leaves-swap18-merge18-scratch32-20261102; SHA256 bee157bfce2eba6fb13f4d8882b04e2033bbbe4699252858c06a68d153e3459d.
Full diffs: library.diff, request.diff (zero context). MACSPLIT/v6/DOMSIX/other pilots not integrated.
No competitor PR code/branches/diffs (#576/#678/#694/#701) opened. No subagent executors.

## Change scope

New file verify/network/netcomp/neteighteen.rs (child `network::netcomp::neteighteen`); netcomp.rs gains ONLY
the trailing `mod neteighteen;` registration plus one comment, after every existing target/root.
The child inherits netcomp's `#[cfg(kani_smallsort_controls)]` gate (network.rs:15-16, unchanged) and sees the
private ancestor items swap_net9/U8Cmp/StrictU8/count_matching_values without any visibility change.
Unchanged bytes: all prior targets/contracts/PFCs/controls, Context9/13/bridges, specfix.rs, network.rs,
runtime smallsort.rs, tooling/workflows/flags/pin (static_check.py asserts file equality against base).
No new profile tags/comparators, no model/count/write-set change, no stubs/stub_verified, no assumes,
no caller/adapter18, no network copy, no raw-call binding bypass. Old negative controls not repeated.

## Domain record (each leaf independently unrestricted)

T=u8; F=U8Cmp=fn(&u8,&u8)->bool; value StrictU8::CMP = reified strict_less::<u8> (explicit `let cmp: U8Cmp`).
Same explicit fn-pointer domain as NETCOMP2, not the earlier function-item F. Order: ordinary `<`, full-byte counts.

| Row | Target (unchanged) | Arguments actually passed | Backing / init / frame checked |
|---|---|---|---|
| net18_swap_left_backing18 | swap_net9 (netcomp.rs:42) | v.as_mut_ptr()+0, local a!=b<9 (any_where), cmp, by-value probe:any | [u8;18]=any fully initialized; active9=global0..8; whole-18 frame |
| net18_swap_right_backing18 | swap_net9 | v.as_mut_ptr()+9, same | same backing18; active9=global9..17; whole-18 frame |
| net18_merge_strict_scratch32 | merge_profile::<StrictU8> (specfix.rs:322) | &src[..18], dst=scratch32 as *mut u8 offset0, cmp | src [u8;18]=any after set_probe(any); dst MaybeUninit<[u8;32]>, prefix18 only |

Offsets are concrete per harness (const generic 0 vs 9); no symbolic offset, union or match of placements.
No second [u8;9] stands in for backing18. Swap requires/ensures/modifies are swap_net9's own (canonical cmp,
region9 incl. same_allocation(v,v+8) - satisfied at base+9 since 9+8<18 -, modifies v[a],v[b], pair transfer,
ordered pair, old count9==count9 of the by-value probe). Real swap_if_less runs; no stubs.
Swap post-checks (fixture, outside target): pair transfer/order at global OFF+a/OFF+b; active9 count of the
same probe; whole backing18 count; every backing18 value outside {OFF+a,OFF+b} unchanged (crosses the half boundary).
Merge: requires are exactly merge_profile's: canonical cmp, merge_regions (len 2..=32, readable source,
writable dst[..18], disjoint) and merge_halves_sorted (half=9: both halves9 StrictU8-model-sorted). These are
legitimate PFC requires that limit the admitted leaf input; no manual assume/source sorting/probe correlation.
Body is the generic forwarder: `let mut is_less = cmp; bidirectional_merge::<u8,U8Cmp>(v, dst, &mut is_less)`.
Merge post-checks: global probe unchanged; source all18 unchanged vs snapshot; dst prefix18 sorted by `<`;
full-value count src vs prefix18 for StrictU8::probe(). Destination-only modifies unchanged (dst[..18]).
Tail 18..32 is never read, snapshotted or initialized (static_check asserts no other 32/index use). This
checks the real write frame via modifies; it is not uninit-read detection (uninit checks off).
Probe passports differ: swap uses its by-value probe, merge uses Profile::probe; each leaf keeps its own
unrestricted and unchanged. A future caller must choose one value and assign it to both before the calls.

## Unwind sufficiency (no bound change by trial Builds)

Swap rows unwind(25), unwinding assertions on: deepest loops are fixture count over18 (19 heads) and frame
loop 0..18 (19); count9 in the contract 10; swap_if_less has no loop (ptr::copy/copy_nonoverlapping count1).
Merge row unwind(34) as all existing merge PFCs: bidirectional_merge `for _ in 0..len_div_2` = 9 iterations
(10 heads); len18 even so the odd tail branch is not taken; merge_up/merge_down loop-free; model_sorted and
model_count are macro-unrolled (loop-free); merge_regions predicates loop-free. Fixture source-check loop
0..18 (19), sorted loop 1..18 (18), count_matching_values over 18 (19). All <= 34; under-unwinding would be
reported by unwinding assertions, not hidden.

## Future call geometry source map

actual-calls.tsv: Unstable entry -> Freeze/Copy -> small_sort_network(len18) (smallsort.rs:311): no_merge=false,
len_div_2=9; sort9_optimal on v[0..9] (25 swap_if_less, lines435..459, base v_base+0, globals = locals) and on
v[9..18] (same 25 calls, base v_base+9, globals 9+local); insertion_sort_shift_left offset9 on len9 (line349)
makes zero insert_tail calls; bidirectional_merge(v[0..18], stack_array MaybeUninit<[u8;32]> base) line368;
copy_nonoverlapping(scratch, v_base, 18) line369. sort13/sort4/sort8 are not called. Audit data only.
Leaf coverage per geometry: left/right swap placements -> rows1/2; merge src/dst geometry -> row3. Copy-back,
raw->summary binding, half-count invariants and merge premises (halves sorted, canonical cmp from &mut F)
remain obligations for a separate NET18-CALLER; leaf requires do not prove that sort9 establishes them.

## Exact rows, annotations, covers

Prefix slice::sort::shared::smallsort::verify::network::netcomp::neteighteen::; all expect SUCCESS, no expect_check.

| Row | Annotations | Required covers (all must be SATISFIED) |
|---|---|---|
| net18_swap_left_backing18 | proof_for_contract(super::swap_net9), unwind(25) | 7: swap taken; swap not taken; first to last; last to first; interior pair; probe hits active9; probe misses active9 |
| net18_swap_right_backing18 | proof_for_contract(super::swap_net9), unwind(25) | same 7 |
| net18_merge_strict_scratch32 | proof_for_contract(super::super::super::merge::specfix::merge_profile), unwind(34) | 6: returned; left first; right first; equal first values; probe hits source18; probe misses source18 |

Exact literals per row: g1.manifest.json. All covers are in the uncontracted fixture, outside targets.
Reachability (source expectation, not executed fact): arbitrary distinct a/b give all directions/edges; any
backing gives taken/not-taken; independent probe gives hit/miss; sorted halves admit src[0]<src[9],
src[9]<src[0] and src[0]==src[9]. No cover on the uninit tail. Allowed failed checks: none.
PFC attribute paths use the precedented relative `super::` form (network.rs uses super::merge::specfix::...).

## Static checks

static_check.py PASS (static-check.json): ordinary exact200 unchanged; cfg-on 395+3=398, the 3 new names exact;
library diff = new file + registration only; specfix.rs/old netcomp.rs bytes equal base; no assume/stub/cfg/pub;
request byte-equals RUN-REQUEST.json. Static composition, not native inventory or proof.
pfc_order.py: 21 sites / bad0 (18 before + 3; its scanner does not inherit module cfg). Target ordering:
swap_net9 (netcomp.rs:42) precedes `mod neteighteen;` (netcomp.rs:466); merge_profile in verify::merge is
visited before verify::network (existing network PFCs on specfix targets already rely on this).
rustfmt-check.txt: assigned wrapper --check (edition2024, assigned fmtcfg) PASS on both .rs; git diff --check PASS.
tooling-static.txt: protected lane paths equal 30f77e859903df14b442ff9294d4fbbd44827f20; bound-file hashes equal
NETCOMP2; Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
kani_k1.py validate: 3 harnesses accepted; g1.args = --exact, --harness-timeout 10m, --jobs=1, terse.
No local cargo/rustc/Kani/CBMC/proof run, workflow dispatch or deployment.

## Build / budget

G1 measurement, controls:true, jobs1, uninit off, timeout10min/row, gcb-e2-standard-4 -> k1-standard4 4CPU/16GiB,
swap off, prior pool/pin/flags. Reserve (3*10+30)*$0.0135=$0.810 <= stage cap$1.70. Own spent0/reserved0, no UUIDs.
Ledger (budget-prebuild.txt, read-only): 164 builds, used$77.9325, unfinished reserve$0, cap$88.96;
with proposed reserve $78.7425. No slot acquired. Refresh ledger and published source/request after GO.
G2 only after a G1 compile error: same 3 rows/mechanism/domains/flags, new review/GO, full $0.810 reserve,
own fact_spent+reserve <= $1.70 (two-attempt reserve <= $1.620). No G2 after resource/semantic/coverage failure; no G3.
Any TIMEOUT/OOM/FAILED/UNKNOWN -> stage PARTIAL/FAIL, proved rows retained, stop. No narrowing of input/probe.

## Result obligations

RESULT-NET18-LEAVES.md <=35 lines: reviewed/build/library/request identities; F/value/geometry per leaf;
rows status/VT/CBMC RSS/failed-total/unreachable/covers; overall gate; own spent/reserved; compiler/driver peaks
separately. TIMEOUT cap600 with VT UNKNOWN unless printed; OOM separately. With 3 SUCCESS and full covers only
matching leaf credit for the two named swap placements and the merge geometry; actual N18 composition NOT
established. No arbitrary backing/offset/T/FnMut/function-item F/N32, tie stability, init detection,
full alias-validity/unwind or ordinary/Part1-v6 credit. After GO: k1g.sh dispatch, `k1g.sh wait BUILD` in background.
