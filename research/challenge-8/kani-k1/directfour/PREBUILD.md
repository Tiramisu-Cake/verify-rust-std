# DIRECTFOUR PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No DIRECTFOUR Build submitted; compile/proof/covers NOT_RUN.
Runtime: Claude Code, no subagents. Task TASK-DIRECTFOUR.md @8505b3b2882cf2e18f0b7771b54f4239135ccfd5.
Branch experiment/kani-k1-directfour-20261102 (slug letters only; no alias). Base MERGESTEP 97a252bea7,
base library commit 91d4d9f77a5a6e7f27b151839e6ac42114523a89, tree dc7c79bb9b2a779a6db2977f6142adfea835441b.
Library commit 813a03db4a0ae11fbe8e00418b17556ae5171758; library tree 334b3a2912259c4b75193c465fdbd0d776cdc7b7.
Request directfour-direct-merge4-baseline-20261102; SHA256 82bc61a1959b25ff2cd8a9eb7cac3300449f11bbd1f9379f91178e372e85d5fb.
Review SHA = the research commit carrying this packet. Full diffs: library.diff (U3), request.diff (U0).
No competitor PR code/branches/diffs (#576/#678/#694/#701) opened. No local cargo/rustc/Kani/CBMC run.
NETTEN files/worktree (netcomp.rs, its child) not touched or integrated.

## Change scope

New file verify/network/netcomp/mergestep/directfour.rs = child `network::netcomp::mergestep::directfour`
(inherits network.rs `cfg(kani_smallsort_controls)` gate on netcomp). mergestep.rs gains ONLY a trailing
comment + `mod directfour;` after all existing items (sha256 2ae7e36d…; base 2552bd3c…). Old MERGESTEP
targets/roots/helpers/controls/RESULT unchanged; no refactoring, no visibility change (child uses parent
private items ACTIVE4/register/check_merge4 and parent imports StrictU8/U8Cmp/count_matching_values).
static_check.py asserts byte equality vs base of smallsort.rs, network.rs, netcomp.rs, specfix.rs,
neteighteen.rs, and lane/tooling == 30f77e8599. Runtime smallsort.rs / inline(always) unchanged.

## Annotation table (no substitutions)

| Root | Annotations | Expect | Covers |
|---|---|---|---|
| mergestep_composed_merge4_u8 (old, unchanged) | PFC(super^3::merge::specfix::merge_profile), stub(merge_up,up_adapter), stub(merge_down,down_adapter), stub_verified(up_step_u8), stub_verified(down_step_u8), unwind(34) | (TIMEOUT600) | 6 post + 2 adapter-entered |
| directfour_merge4_u8 (new) | PFC(super^4::merge::specfix::merge_profile), unwind(34) | SUCCESS | 6 post only |

Path: directfour is one module deeper, so super^4 resolves to the same `verify::merge::specfix::merge_profile`.
No stub/stub_verified/assume/cfg/static/adapter/step/ledger code in the new file (static check on code
without comments). Real in the proof graph: merge_profile body, bidirectional_merge, merge_up/merge_down
(inline(always), not intercepted), StrictU8::CMP = reified strict_less::<u8>, panic_on_ord_violation (NOT
stubbed; must be unreachable under canonical cmp + sorted halves, else it surfaces as a failure).

## Domain / init / call: identical to the old composed root

static_check.py: every non-comment, non-cover statement of the new body equals, in order, the old
mergestep_composed_merge4_u8 body (statement list equality), and cover positions in the sequence match.
1 `StrictU8::set_probe(kani::any())`; 2 `let probe = StrictU8::probe()`; 3 `let src: [u8;18] = kani::any()`;
4 `let pre = src`; 5 `MaybeUninit::<[u8;32]>::uninit()`; 6 `dst = scratch.as_mut_ptr() as *mut u8` (offset 0);
7 `register(&src, dst, probe, false, false)`; 8 `let cmp: U8Cmp = StrictU8::CMP`;
9 `merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp)`, ACTIVE4=4 (not a merge copy);
10 `check_merge4(&src, &pre, dst, probe, (false, false))`; 11 `hits = count_matching_values(&pre[..4], &probe)`.
Sorted halves2 + canonical cmp + regions only via merge_profile requires; no manual assume, no sorting
constructor, no probe/input correlation. Scratch tail 4..32 stays uninit and is never read (check_merge4
views only dst[..4]). Probe independent: set before source:any.
register writes the parent's readonly STEP_CONTEXT before the call (outside the target, as in the old
root); nothing inside the direct target reads it (no adapters); only check_merge4 reads it afterwards.

## Oracle old vs new

Inner: unchanged merge_profile contract — modifies slice dst[..4] only; ensures model_sorted(dst,4) and
model_count(v,4)==model_count(dst,4). Outer (fixture): unchanged parent check_merge4 — StrictU8 probe
unchanged; readonly context (src/dst/active_len/probe/flags) unchanged; source18 unchanged (all 18);
dst prefix4 sorted (ordinary <); count_matching_values(pre[..4],probe)==count(dst[..4],probe). Same
assert literals ("mergestep merge4: …") since the helper is shared, not copied.

## Covers: 6 required (labels mergestep→directfour prefix; predicates identical)

| Old label (mergestep merge4: …) | New label | Predicate | Position |
|---|---|---|---|
| returned | directfour merge4: returned | true | after merge, before check_merge4 |
| left first | directfour merge4: left first | src[0] < src[2] | after check_merge4 |
| right first | directfour merge4: right first | src[2] < src[0] | after |
| equal first values | directfour merge4: equal first values | src[0] == src[2] | after |
| probe hits source prefix4 | directfour merge4: probe hits source prefix4 | hits > 0 | after |
| probe misses source prefix4 | directfour merge4: probe misses source prefix4 | hits == 0 | after |

The two old "mergestep actual up/down adapter entered" covers are absent: no adapter in the direct graph.
No other covers, sentinels, or negatives. Prefixed labels keep log attribution distinct from MERGESTEP.

## Raw-call map (direct; source audit, not executed fact)

merge_profile (SF:322) -> bidirectional_merge(v,dst,&mut is_less) (S:754) len4, len_div_2=2; 2 loop
iterations each real merge_up (S:812) then merge_down (S:813); up d idx 0,1; down d idx 3,2; left_rev may
end at src-1 (wrapping, opaque); even -> odd tail skipped; consumption check (S:831-832) must not panic.

## Static checks (not proofs)

static_check.py PASS (static-check.json): library diff = new child + registration; listed files byte-equal
base; ordinary exact200 unchanged; cfg-on 404+1=405 (the 1 new name exact; the 6 MERGESTEP names kept);
request == RUN-REQUEST.json, 1 row SUCCESS, k1-network, measurement/controls/jobs1/uninit off/10min/
gcb-e2-standard-4. pfc_order.py: 25 sites / bad0 (24 + 1); merge_profile (verify::merge) visited before
verify::network. rustfmt-check.txt: assigned wrapper --check edition2024/fmtcfg PASS both .rs; git diff
--check PASS; lines <=100. tooling-static.txt: lane paths == 30f77e8599; bound hashes == MERGESTEP;
Kani 9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12. kani_k1.py validate: 1 accepted;
g1.args = 1x --harness, --exact, --harness-timeout 10m, --jobs=1, --output-format=terse.

## Build / budget

G1 one exact row: measurement, controls:true, jobs1, uninit off, 10min, gcb-e2-standard-4 -> k1-standard4
4CPU/16GiB, swap off; unwind34, unwinding assertions on; pin/tooling/organizer flags as MERGESTEP.
Owner agent k1-network (MERGESTEP terminal). Reserve (1*10+30)*$0.0135=$0.540 <= stage cap$1.10.
budget-prebuild.txt: 168 builds, used$79.0395, unfinished$0, cap$88.96 -> with reserve $79.5795;
with NETTEN G1 $0.675 (other stage/owner) $80.2545. Slots: <=2 project, <=1 per owner; refresh after GO.
G2 only after a G1 compile error: same fixture/1 row/flags, new review/GO, own spent+reserve <= $1.10
(two reserves $1.080). TIMEOUT/OOM/FAILED/coverage/UNKNOWN: record and STOP; no narrowing, no removal
of outer post/frame, no limit/machine change; no G3. After GO: k1g.sh dispatch, `k1g.sh wait BUILD`
as a background task.
Scope of a PASS: direct merge4 on this fixture only; separates composition bundle cost from direct, not
ledgers from pointer/havoc/assigns; no N18/32, other CMP/F/backing/probe, generic T/FnMut, uninit/alias/
unwind, Part1/ordinary credit. A TIMEOUT does not let the composed problem be attributed to composition.
