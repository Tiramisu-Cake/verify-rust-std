# MERGESTEP PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No MERGESTEP Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, no subagents. Task TASK-MERGESTEP.md @e547e6dca1f0c5f6fb68b4959cf2a6aeff5442b7.
Branch experiment/kani-k1-mergestep-20261102 (slug letters only; no alias needed).
Base NET18-LEAVES 7d8b21728b, base library commit 4eb7e81259f843da6517a8de97c68e23b584eb76,
base library tree 1fa41b3a5f101ee3981787f71588bfc22e2aae5b.
Library commit 91d4d9f77a5a6e7f27b151839e6ac42114523a89; library tree dc7c79bb9b2a779a6db2977f6142adfea835441b.
Request mergestep-up-down-steps-merge4-calibration-20261102; SHA256 fa2a217facff573af3576489d5b4aac29ad7885a388740105cada62703bc679f.
Review SHA = the research commit carrying this packet. Full diffs: library.diff (U3), request.diff (U0).
No competitor PR code/branches/diffs (#576/#678/#694/#701) opened. No local cargo/rustc/Kani/CBMC run.

## Change scope

New file verify/network/netcomp/mergestep.rs (child `network::netcomp::mergestep`, inherits netcomp's
`cfg(kani_smallsort_controls)` gate); netcomp.rs gains ONLY a trailing comment + `mod mergestep;`.
static_check.py asserts byte equality vs base of smallsort.rs (runtime, merge_up/down inline(always)),
network.rs, specfix.rs (merge_profile, profiles, model), neteighteen.rs (N9/N13/NET18 targets/roots) and
lane/tooling. No visibility change, no new profile/comparator, no generic framework, no flags/pin change.
Not touched: U64-N9 worktree / network.rs sibling. Merge18 TIMEOUT not repeated; no N18/N32 caller.

## Step contract (concrete targets, declared before their PFCs)

`up_step_u8 / down_step_u8(left:*const u8, right:*const u8, dst:*mut u8, cmp:U8Cmp) -> bool take_left`.
Requires: canonical(cmp) (= specfix_canonical_comparator::<StrictU8>); left/right non-null, aligned,
can_dereference, same_allocation(left,right), left!=right; dst non-null, aligned, can_write,
!same_allocation(left,dst). down additionally: same_allocation(dst, dst.wrapping_sub(1)) and
can_write(dst.wrapping_sub(1)) - writable, NOT required initialized; allocation-start dst is outside.
Modifies: `dst` only. Ensures (pure, full u8 values, no callback call): up take_left == old(*l <= *r);
down take_left == old(*r < *l) (up ties left, down ties right); *dst == old(selected full value).
Pre-dst value is never read. Target reads no probe/context, writes nothing else.
Body: saves (lv, rv), `let mut actual: U8Cmp = cmp`, calls the REAL merge_up/merge_down, take_left from
saved pre-values, then `kani::assert(same_step(raw, decode(left,right,dst,take_left)))` ("mergestep
up|down step: actual raw tuple equals decoder") - decoder vs the helper's actual returned tuple.
Shared pure decoder (also used by adapters): up (L.wrapping_add(t as usize), R.wrapping_add((!t) as
usize), D.wrapping_add(1)); down (L.wrapping_sub(t as usize), R.wrapping_sub((!t) as usize),
D.wrapping_sub(1)). Returned source pointers are opaque (may be one-past / one-before); never read.
Encoding is a choice: bool return, not a claim that Kani havocs pointer tuples.

## Leaves - rows 1/2 (PFC, no stub/stub_verified, unwind34)

Source `[u8;18]=any`, i!=j<18 any_where, cmp=StrictU8::CMP. Destination separate
`MaybeUninit<[u8;32]>`: up k<32, down 1<=k<32; mask:[bool;32]=any and init:[u8;32]=any; only mask cells
written before the call (partial_dst32). Root + indices passed as s.add(i), s.add(j), base.add(k).
Post (fixture, outside target): take_left relation; written cell == selected pre-value; probe(any)
indicator out==probe <=> selected==probe; every c!=k with mask[c] still == init[c]; source18 all
unchanged. Never reads mask=false cells or the backing as [u8;32]. Loops <=32 (33 heads) <= 34.
Covers up (11): left selected; right selected; tie; probe hits/misses written value; source cells
0 and 17; source cells 17 and 0; destination cell 0; destination cell 31; written cell was
uninitialized; written cell was initialized. Down (12): same with destination cell 1 (not 0) plus
predecessor uninitialized. All reachable by arbitrary i/j/k/mask/values.

## Composed merge4 - row 3

PFC existing merge_profile (unchanged requires/modifies dst[..4]/ensures sorted + model_count).
Fixture: StrictU8::set_probe(any); source [u8;18]=any; dst scratch32 uninit offset0; register(...) THEN
merge_profile::<StrictU8>(&src[..4], dst, StrictU8::CMP). Sorted halves2 only via target requires.
Annotations: stub(merge_up, up_adapter), stub(merge_down, down_adapter), stub_verified(up_step_u8),
stub_verified(down_step_u8), unwind(34). NOT stubbed: bidirectional_merge, merge_profile,
panic_on_ord_violation - the real loop, odd check and consumption check run.
Adapters: same-signature generic `up_adapter/down_adapter<T: MergeStepBridge<F>, F: FnMut>` forward to
the sole closed impl `MergeStepBridge<U8Cmp> for u8` (no blanket/fallback). Impl: unconditional entered
cover; binding guard assert; canonical(*is_less) assert; geometry assert via index_in (same_allocation
and pointer range BEFORE offset_from): l in src[0..2), r in src[2..4), d in dst[0..4) (down dst[1..4)),
active_len==4; calls the verified step with the ACTUAL pointers and received `*is_less` (never
replaced by the canonical const); returns decoder(actual args, take_left); then ledger assertions.
Up ledger: forward endpoints in src[0..=2], src[2..=4], dst[0..=4]; count(probe) of written
dst[0..D') == count(src[0..L')) + count(src[2..R')). Down ledger: endpoints first wrapping_add(1),
then range-checked: count dst[Dr'+1..4) == count src[Lr'+1..2) + count src[Rr'+1..4); front prefix
length = 4-(Dr'+1) (from the current dst offset: the actual loop runs one merge_up before each
merge_down, source map line 812/813); asserts front<=back start, front prefix sorted, back suffix
sorted, front_last <= back_first. Reads: only written dst cells and source prefix4 cells.
Overlap of the two ledgers is not assumed away; final std consumption check gives the partition.
Readonly context `STEP_CONTEXT` {src18 base, dst32 base, active_len4, probe, fail_up, fail_down}: one
write site (register), before the outer target; no hit counters/ghost writes in adapters/target, so the
outer destination-only modifies is not widened. Post: StrictU8 probe unchanged; context unchanged;
source18 unchanged; dst prefix4 sorted (ordinary <); count_matching_values(src[..4]) == dst[..4].
Covers (8): returned; left first (src0<src2); right first; equal first values; probe hits/misses
source prefix4; mergestep actual up adapter entered; mergestep actual down adapter entered.

## Negative controls - rows 4/5/6 (plain proofs, same 4 substitutions, unwind34)

Setup control_merge4: source18=[0;18], set_probe(0), dst32 uninit, canonical U8Cmp, valid sorted halves.
4 up binding: fail_up=true, fail_down=false. Guard in the SAME up adapter before the verified step:
`kani::assert(!ctx.fail_up, "mergestep actual up adapter binding control")`, then legal step/decoder.
5 down binding: fail_up=false, fail_down=true; `mergestep actual down adapter binding control`.
6 count: flags false; check_merge4 (positive post checks) passes; dst[3]=1 -> [0,0,0,1] sorted,
count0 4->3; `mergestep calibration negative: full-value count preserved` (same count_matching_values).
Covers: 4/5 (4): control: actual entry reached; control: merge returned; up adapter entered; down
adapter entered. 6 (6): those 4 + returned before corruption + corrupted count check reached.
Each literal appears once in source. Expected: FAILED only on its literal; any panic/assigns/UB/
unwind/unsupported/geometry failure is NOT an intended negative. Missing interception would show as
SUCCESS of 4/5 (guard unreachable) plus unreachable adapter covers -> gate fails, STOP (no patch).

## Raw-call map and hypotheses (actual-calls.tsv)

N4: len_div_2=2; it1 up(src+0,src+2,dst+0), down(src+1,src+3,dst+3); it2 up(L in {0,1},R in {2,3},
dst+1), down(Lr in {1,0}, Rr in {3,2}, dst+2); left_rev may end at src-1 (before source18 start);
left_end=wrapping_add(1); even -> odd tail skipped; consumption check must not panic.
Up d idx {0,1} subset 0..31; down d idx {3,2} subset 1..31; sources distinct cells of source18.
H1 (task-named): stubbing #[inline(always)] merge_up/down is a real hypothesis on pin 9461e07af7;
rows 4/5 and adapter-entered covers decide it. H2: first suite use of stub + stub_verified on a
proof_for_contract root (NETCOMP used plain roots); a compile/unsupported outcome is reported as is.

## Exact rows (prefix slice::sort::shared::smallsort::verify::network::netcomp::mergestep::)

| Row | Annotations | Expect | Covers |
|---|---|---|---|
| mergestep_up_leaf_u8 | proof_for_contract(up_step_u8), unwind(34) | SUCCESS | 11 |
| mergestep_down_leaf_u8 | proof_for_contract(down_step_u8), unwind(34) | SUCCESS | 12 |
| mergestep_composed_merge4_u8 | PFC(super::super::super::merge::specfix::merge_profile) + 4 subst, unwind(34) | SUCCESS | 8 |
| mergestep_up_binding_negative_u8 | proof + 4 subst, unwind(34) | FAILED: mergestep actual up adapter binding control | 4 |
| mergestep_down_binding_negative_u8 | proof + 4 subst, unwind(34) | FAILED: mergestep actual down adapter binding control | 4 |
| mergestep_count_negative_u8 | proof + 4 subst, unwind(34) | FAILED: mergestep calibration negative: full-value count preserved | 6 |

Exact cover/check literals per row: g1.manifest.json. allowed_failed_checks: none.

## Static checks (not proofs)

static_check.py PASS (static-check.json): ordinary exact200 unchanged; cfg-on 398+6=404, the 6 names
exact; library diff = new file + registration; listed files byte-equal base; annotations per root;
no assume/cfg/pub, no stub of panic/bidirectional_merge/merge_profile; one context write site;
request == RUN-REQUEST.json. pfc_order.py: 24 sites / bad0 (21 + 3 PFCs); up/down_step_u8 precede
their leaves in mergestep.rs; merge_profile (verify::merge) is visited before verify::network.
rustfmt-check.txt: assigned wrapper --check edition2024/fmtcfg PASS both .rs; git diff --check PASS.
tooling-static.txt: lane paths == 30f77e859903df14b442ff9294d4fbbd44827f20; bound hashes == NET18-LEAVES
/NETCOMP2; Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12.
kani_k1.py validate: 6 accepted; g1.args = 6x --harness, --exact, --harness-timeout 10m, --jobs=1, terse.

## Build / budget

G1 measurement, controls:true, jobs1, uninit off, 10min/row, gcb-e2-standard-4 -> k1-standard4 4CPU/16GiB,
swap off, prior pool/pin/flags; unwind34, unwinding assertions on. Owner agent k1-network.
Reserve (6*10+30)*$0.0135=$1.215 <= stage cap$2.50. budget-prebuild.txt: 166 builds, used$78.4185,
unfinished$0, cap$88.96 -> with reserve $79.6335. Own spent0/reserved0. Slot: <=2 project, <=1 owner;
refresh ledger/slots after GO. G2 only after a G1 compile error, same 6 rows/encoding/domains/
mechanism/flags, new review/GO, own spent+reserve <= $2.50 (two reserves $2.430). No G2 after
resource/semantic/coverage failure; no G3. Row order is not an early-stop guarantee; the consumer
row gets no credit without both leaf proofs. After GO: k1g.sh dispatch, `k1g.sh wait BUILD` in background.
