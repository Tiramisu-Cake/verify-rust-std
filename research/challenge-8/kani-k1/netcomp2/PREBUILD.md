# NETCOMP2 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No NETCOMP2 Build submitted; compile/proof/covers NOT_RUN.
Review SHA is the published research/request commit carrying this packet.
Task: TASK-NETCOMP2.md including Уточнения, with TASK-NETCOMP.md mechanism/domain restrictions.
One jointly submitted packet is explicitly authorized by NETCOMP2; it does not resume old G2.
Branch: experiment/kani-k1-netcomp-20261102. Pre-edit head: b57bf76f699d77fc774f54cceba1c64d78340c22.
Library commit: f4d3775dc505ef26e30158cfa7e78f120cd3c30e.
Library tree: 3b6d2a51dae08e52464f4b2b82f5168d8ba9977b.
Request: netcomp2-n9-cover-n13-pair-frame-count-20261102.
Request SHA256: 69646d5b669310254328a92ea9d35d7d0b2a99c0708cd94f4605e04422723311.
Full source/request diffs: library.diff and request.diff (zero-context, no whitespace artifacts).

## Scope and retained G1 evidence

N9: move ONLY the complete-hit cover from check_context9 to netcomp_composed_u8_n9,
immediately after positive9(true), using context9().hits==25. All assertions stay in place;
run9 still calls check_context9 when composed. No validator/threshold/cover waiver.
Four N13 harnesses are added separately, without refactoring N9 targets or shared assertions.
network.rs registration remains byte-identical; no runtime or other library file changes.
Ordinary exact200 and prior domains/controls remain unchanged. Opt-in kani_smallsort_controls only.
No competitor code/branches/diffs read; own bridge at assigned8cbb267500 read for mechanism.

G1 b3e257d1-eaf9-4323-a8f1-f4648798cbd9 remains PARTIAL: A9 covers4/5.
Historical leaf9 SUCCESS7/7 and wrong-cmp9 intended FAILED2/2 are reused, not new Build rows.
reuse-dependencies.md and static-check.json prove source preservation of their dependency closure
against G1 source0944189023c0c53620ed74a45bb2d2efef4c53cd, including targets/roots/annotations,
T/F/value/probe/backing/frame/runtime/pin/flags. Those rows do not reach changed check_context9.
Count-negative9 DOES reach that helper, so is included afresh with expected3/3 covers.
Old4/5 is never treated as a full-cover gate. Old38.205% is observation under failed measurement.

## Domain and actual call binding

T=u8, F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>.
The function-item comparator from NETNINE/NETTHIRTEEN is a different monomorphization;
no proof or matching timing transfer to it is claimed. N13 has no matching direct fn-pointer baseline.
Each positive uses unrestricted full any [u8;N] with independent any u8 probe, exact initialized
backingN/offset0. Each leaf uses the same domain with arbitrary distinct in-range indices.
Wrong comparator alone uses always_true_u8; count controls alone use fixed [0;N]/probe0 witnesses.
Requires admit some wider backings/offsets; independent leaf credit is restricted to exact backingN.

| Actual consumer | Raw replacement | Checked summary | Independent real-body leaf |
|---|---|---|---|
| trait entry -> Freeze/Copy -> sort9, 25 raw calls | adapter9<T,F> -> sole SwapBridge9<U8Cmp> for u8 | swap_net9(actual v/a/b/*is_less/ctx.probe) | historical netcomp_leaf_u8_n9; no stubs |
| trait entry -> Freeze/Copy -> sort13, 45 raw calls | adapter13<T,F> -> sole SwapBridge13<U8Cmp> for u8 | swap_net13(actual v/a/b/*is_less/ctx.probe) | new netcomp_leaf_u8_n13; no stubs |

actual-calls.tsv lists all25+45 source calls with ordered argument pairs, source lines435..459
and484..528, checked against unchanged runtime source. This is audit data, never executable input.
Real small_sort_network receives full regionN at lenN<18; sortN then insertion at full prefixN
does zero insertions and returns without merge. No other std helper/network is replaced.
Concrete target body only binds actual:U8Cmp=cmp and calls the real raw swap with received args.
Requires: received canonical cmp, nonnull/aligned full readable initialized/writable regionN,
one allocation and distinct in-range pair with valid geometry. No manual assumed premises.
Modifies exactly v[a],v[b]; ensures pure pre-pair branch transfer, ordered post-pair,
old scalar countN(v,probe)==post countN(v,probe). Specs never call the callback.
Leaf has no manual stub or stub_verified and checks contract/assigns plus explicit unchanged
other values, pair transfer/order and full count. Historical leaf9 is not a substitute for leaf13.
Pin contract modes: explicit PFC Check and stub_verified Replace precede Assert selection,
so retained --no-assert-contracts does not disable them (pinned contracts.rs lines565ff):
https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/transform/contracts.rs#L565

## Context lifecycle and frame

registerN runs before the real entry, outside PFC: assign actual root pointer, independent
by-value probe, computed initial scalar count, hits=0. No setter/ghost write is inside target.
Closed adapter asserts actual root equality, pair distinct/in range, canonical RECEIVED cmp.
Invalid cmp returns before summary. Valid calls forward actual v/a/b/*is_less and ctx.probe;
replacement must check all memory premises from actual state, with no assumes.
After each summary, only dedicated CONTEXTN.hits increments outside the target write set,
then countN(actual_base,ctx.probe)==ctx.initial_count is asserted. Base/probe/count stay readonly.
Caller checks hits25/45, base/probe/initial-count frame, canonical cmp unchanged, sortedness
and full independent-probe count against pre-state snapshot. Context pointer is used only while
the caller's exact array lives; every composed entry registers afresh. No mutable trace is havoced.
check_context13 has assertions only. Complete-hit covers are in B roots, never shared helpers.

## Exact seven rows and full annotations

Names have prefix slice::sort::shared::smallsort::verify::network::netcomp::.
Every row has unwind(25), with unwinding assertions enabled. No direct N13 row is requested.

| Row suffix | Full Kani annotations | Expected | Covers |
|---|---|---|---:|
| netcomp_direct_u8_n9 | proof, unwind(25) | SUCCESS | 4/4 |
| netcomp_composed_u8_n9 | proof, stub(swap_if_less,adapter9), stub_verified(swap_net9), unwind(25) | SUCCESS | 6/6 |
| netcomp_count_negative_u8_n9 | proof, stub(swap_if_less,adapter9), stub_verified(swap_net9), unwind(25) | FAILED count only | 3/3 |
| netcomp_leaf_u8_n13 | proof_for_contract(swap_net13), unwind(25) | SUCCESS | 7/7 |
| netcomp_composed_u8_n13 | proof, stub(swap_if_less,adapter13), stub_verified(swap_net13), unwind(25) | SUCCESS | 6/6 |
| netcomp_wrong_cmp_u8_n13 | proof, stub(swap_if_less,adapter13), stub_verified(swap_net13), unwind(25) | FAILED guard only | 2/2 |
| netcomp_count_negative_u8_n13 | proof, stub(swap_if_less,adapter13), stub_verified(swap_net13), unwind(25) | FAILED count only | 3/3 |

g1.manifest.json gives EVERY exact cover literal per row and all annotations; reachable sets:
- A9: sort moves elements; probe hits input; probe misses input; duplicates present.
- B9: A9 four plus adapter entered and all actual exchanges intercepted.
- Count9: adapter entered; sort returned before corruption; corrupted count check reached.
- Leaf13: swap taken; swap not taken; first to last; last to first; interior pair;
  probe hits input; probe misses input. All arbitrary pair directions have witnesses.
- B13: adapter entered; sort moves elements; probe hits input; probe misses input;
  duplicates present; all actual exchanges intercepted. All-zero input witnesses duplicates;
  inversion witnesses movement; independent probe permits both hit and miss.
- Wrong13: actual entry reached; adapter entered. No summary-return/hit-count cover.
- Count13: adapter entered; sort returned before corruption; corrupted count check reached.
All are source reachability expectations, not executed cover facts. Require all positives' covers.

Only allowed failed literals (real kani::assert sites in netcomp.rs):
- Count9: `netcomp N9 negative: full-value count preserved`, line244.
- Wrong13: `netcomp canonical comparator required`, line354 (N9 counterpart unchanged at122).
- Count13: `netcomp N13 negative: full-value count preserved`, line461.
Each expect_check matches exactly. Wrong13 uses the SAME actual adapter as B13 before summary,
checks entry/adapter reachability, and makes no sorted/count result assertion. Repeated guard
failures across actual exchanges allowed; no unrelated failed check is accepted.
Count controls first pass canonical B with hits25/45, invariant and frame; after return v[N-1]=1,
check sortedness, cover count-check arrival, then fail unique count literal: count(0) N->N-1.
UB/geometry/root/frame/hit/unwind/unsupported/ERROR/OOM/TIMEOUT are not intended failures.

## Static checks and resource boundary

static_check.py PASS: ordinary exact200; cfg-on391+4=395; N9 exact bytes except cover move;
all other library bytes and protected tooling preserved; exact request/annotations/domain checks.
Counts are static composition checks, not native inventory or proof. pfc_order.py:18 sites/bad0;
its simple scanner does not inherit module cfg. Actual targets precede respective PFCs:
swap_net9 line42 before PFC48; swap_net13 line274 before PFC280. Ordinary inventory stays200.
Assigned rustfmt wrapper --check on changed .rs and git diff --check PASS.
Independent Luna High source review: source-review.txt; this is not proof or coordinator GO.
No local Cargo/rustc/Kani/CBMC/proof, runner/model/compiler/validator change or build submission.
Protected lane paths match30f77e859903df14b442ff9294d4fbbd44827f20; tooling-static.txt hashes.
Kani9461e07af7ec929f050aa4192f29363c9be07779 / nightly-2026-10-12 unchanged.
Retain organizer flags including --no-assert-contracts/object-bits12, uninit off, jobs1,
controls:true, measurement,600s per row, unwind25/unwinding assertions, k1-standard4/4CPU/16GiB.
Request validator accepted exact7, g1.request.json byte-equals RUN-REQUEST.json.

One Build only, no retry. Full envelope=(7*10+30)=100min; reserve=$1.350 <=stage cap$1.40.
This explicitly replaces old six-row/$1.215 staging arithmetic. NETCOMP2 own spent0/reserved0,
UUIDs none (runs.json); no old NETCOMP spend is presented as new-stage spend.
Ledger snapshot:163 builds, used$77.6355, unfinished reserve$0, project cap$88.96;
with proposed reserve=$78.9855. budget-prebuild.txt records read-only observation, not a slot grant.
No active reservation observed in this snapshot; no slot acquired. Refresh budget/slots and
check published exact source/request immediately before dispatch AFTER coordinator GO.
Old NETCOMP G2 remains stopped; no conditional retry, packet substitution or threshold change.

## Joint gate and result obligations

One joint Build does not guarantee N9 acceptance before N13 execution. Full gate requires matching
source/request/library/pin/tooling; new A9 SUCCESS4/4 and B9 SUCCESS6/6; preserved historical
leaf9/binding evidence; current Count9 intended FAILED3/3; new Leaf13 SUCCESS7/7 and B13 SUCCESS6/6;
both N13 controls intended FAILED with their complete reachable cover sets and no unrelated failures.
Cloud COMPLETE/SUCCESS is distinct from task gate. If incomplete, retain per-row facts and stop.
RESULT-NETCOMP2.md <=45 lines after authorized Build: identities/F/domain/trace, each row status,
VT/CBMC RSS/failed-total/unreachable/covers, gate and open obligations; G1 PARTIAL kept separate.
Compare current VT(A9_new),VT(B9_new); label B9_new+leaf9_old as mixed-run estimate, never same-build.
CBMC max(B,leaf), not sum; compiler/driver/process-sum RSS, command wall and Build cost separate.
No N13 speedup without matching direct fn-pointer baseline; no old function-item transfer.
TIMEOUT cap600s with VT UNKNOWN unless printed; OOM separate. No broader backing/T/F/N18,
stability/init-detection/full alias-validity/unwind, trait-PFC, ordinary200 or Part1/v6 credit.
After GO use existing k1g dispatch and watch UUID with CODEX_THREAD_ID, then end turn.
At final result mark NETCOMP2 ЗАВЕРШЁН and stop after this one stage.
