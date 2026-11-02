# NETCOMP G1 PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO. No build submitted; compile/proof/covers NOT_RUN.
Review SHA is the published research/request commit carrying this packet.
Task: TASK-NETCOMP.md; G1/N9 calibration only, exactly five rows.
Branch: experiment/kani-k1-netcomp-20261102, from NETTHIRTEEN 23751ff775.
Pre-edit task head: a76671d5c4ef08e50bbad371e2353a2f1e0220b4.
Library commit: 47ed440a23641545fba1eedd279a0ebabe6edf02.
Library tree: f9fa2945d6fd31f042b66926aad098f906f4abca.
Request: netcomp-g1-n9-pair-frame-count-20261102.
Request SHA256: e7afc8c7cb631569289b751c103892302c736191f28153e95216f24c41dc312a.

## Scope, full diff, domain

Full library diff: library.diff (2 files, 249 additions, no removed runtime code).
The complete patch uses zero context to avoid trailing-space context lines inside the diff artifact.
Full request diff: request.diff. Whole packet is reviewable via git diff from pre-edit task head.
network.rs changes only by cfg-gated child registration; removing it restores exact base bytes.
All existing harnesses, domains/controls/targets and runtime smallsort.rs are byte-identical.
The only new code is network::netcomp, opt-in through kani_smallsort_controls.
No competitor source/diff was opened; B1/B2 bridge was read at the explicitly assigned 8cbb267500.

T=u8; F=U8Cmp = fn(&u8,&u8)->bool; received value StrictU8::CMP, reified strict_less::<u8>.
This is a new monomorphization, distinct from prior NETNINE/NETTHIRTEEN function-item F.
No backwards transfer to that F or matching timing comparison with its old results is claimed.
Positive callers: arbitrary full [u8;9], exact initialized backing9/offset0, independent any u8 probe.
Leaf: same backing/domain/F/value/probe; arbitrary distinct in-range indices in either order.
Declared requires additionally admit geometries beyond this leaf; those backings/offsets are unproved.
Pure full-u8 transfer/order models are inherited from StrictU8; count9 uses plain full-u8 equality.
No callback is called from requires/ensures. old saves full pair values and scalar pre-count.
No sortedness/count assumption is introduced. Leaf any_where restricts only the two valid indices.
Full domain, annotations, cover labels and negative literals/lines: g1.manifest.json.

## Actual call -> adapter -> summary -> independent leaf

| Actual consumer | Adapter | Summary target | Independent real-body PFC |
|---|---|---|---|
| actual trait -> Freeze/Copy -> sort9, all 25 raw swap_if_less<u8,U8Cmp> calls | adapter9<T,F> -> sole SwapBridge9<U8Cmp> for u8 | swap_net9(v,a,b,*is_less,ctx.probe) | netcomp_leaf_u8_n9, no substitutions |

Actual call sites and ordered arguments: actual-calls.tsv, N9 lines435..459, 25 entries.
It also records all 45 sort13 source calls (lines484..528) as required audit data only;
N13 adapters/targets/leaves/request are DEFERRED, no G2 setup/proof claim yet.
The map is never read by verification code; no network algorithm is copied for execution.
Actual u8 entry is UnstableSmallSortTypeImpl -> Freeze specialization -> Copy specialization
-> small_sort_network: len9<18, full initial region9, sort9_optimal, insertion with prefix9,
then return. Empty insertion suffix; no merge. Only raw swap_if_less is manually replaced.

swap_net9 body only binds actual:U8Cmp=cmp and calls real swap_if_less with actual arguments.
Requires: received cmp canonical; a,b<9; nonnull/aligned full nine-element readable/initialized
and writable region, one allocation, pair distinct/readable/writable geometry.
Modifies: exactly v[a],v[b]. Ensures: branch-sensitive pure full pair transfer, ordered pair,
and old(count9(v,probe))==count9(v,probe). No context/counter/probe/trace writes are authorized.
Leaf executes real helper and checks all contract clauses/assigns plus explicit untouched values,
pair transfer/order and full count. Previous swap_profile leaves do not discharge this new target.

Pin contract-mode selection was checked at the assigned source:
[contracts.rs on 9461e07](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/transform/contracts.rs#L565).
Explicit proof_for_contract Check and stub_verified Replace precede Assert-mode selection.
--no-assert-contracts therefore keeps those explicit modes; normal calls alone supply no PFC credit.
Adapter/summary acceptance and the raw binding remain hypotheses for G1 to test.

## Context lifecycle and ghost-write boundary

Before actual entry, register9 assigns actual root pointer, independent probe, computed scalar
initial count and hits=0. No setter runs in the leaf/target. A direct uses the same caller/oracle
with composed=false; B changes only declared proof instrumentation and its two root substitutions.
Adapter's sole closed u8/U8Cmp implementation reads context, asserts literal root equality,
distinct in-range pair, then canonical received comparator; invalid cmp returns before summary.
It forwards actual v/a/b/*is_less and by-value ctx.probe. All summary memory requires must follow
from actual caller state and be checked by replacement; no manually assumed premises.
After summary it increments only CONTEXT9.hits, outside target modifies, then asserts actual
count9(v,ctx.probe)==ctx.initial_count after every actual exchange. Probe/base/count stay readonly.
On return B checks hits==25, root/probe/initial-count frame and canonical cmp unchanged, followed
by the common sortedness/count oracle against pre-state snapshot. A uses the same unrestricted input,
fn-pointer, oracle, flags and unwind25. Context pointer is only dereferenced while caller array lives;
every composed entry re-registers it; no later read is used to extend backing/lifetime claims.

## Exact roots, annotations, covers and negatives

All roots inherit cfg(kani_smallsort_controls), and all retain unwind25.
Names below are under slice::sort::shared::smallsort::verify::network::netcomp::.

| Root | Full Kani annotations | Expected |
|---|---|---|
| netcomp_leaf_u8_n9 | proof_for_contract(swap_net9), unwind(25) | SUCCESS |
| netcomp_direct_u8_n9 (A9) | proof, unwind(25) | SUCCESS |
| netcomp_composed_u8_n9 (B9) | proof, stub(swap_if_less,adapter9), stub_verified(swap_net9), unwind(25) | SUCCESS |
| netcomp_wrong_cmp_u8_n9 | proof, stub(swap_if_less,adapter9), stub_verified(swap_net9), unwind(25) | FAILED only guard |
| netcomp_count_negative_u8_n9 | proof, stub(swap_if_less,adapter9), stub_verified(swap_net9), unwind(25) | FAILED only count |

Leaf seven source cover labels: taken/not taken, first->last/last->first, interior pair, hit/miss.
A four labels: sort moves, probe hit/miss, duplicates. B adds adapter entry and complete hit count.
Covers are in uncontracted harness/adapter/caller, never ensures or PFC target/generated closures.
All required cover properties of each positive must be SATISFIED; source labels are not backend counts.

Wrong cmp uses actual trait entry and same B annotations/context, U8Cmp value always_true_u8;
requires entry/adapter reachability; no sorted/count output assertions and no summary on guard failure.
Only allowed failed literal: `netcomp canonical comparator required`, netcomp.rs:122.
Repeated failures of this same guard across actual raw calls are allowed; no other failure is allowed.
Count sensitivity uses canonical B, [0;9]/probe0, all25 hits/invariants/frame must pass first.
After return v[8]=1, assert sortedness, cover reaching count-check, then require sole failure:
`netcomp N9 negative: full-value count preserved`, netcomp.rs:244.
count(0) changes9->8 while order holds; fixed witness does not narrow either positive input/probe.
Unsupported/unwind/UB/geometry/root/hit/frame/setup failures, OOM/TIMEOUT/UNKNOWN are not controls.
Keep and inspect every unexpected failed check; runner and exit status are not masked.

## Static validation and identities

static_check.py/static-check.json PASS: exact ordinary200 unchanged; cfg-on386+5=391.
Exact set comparison covers existing cleanup baseline plus both NETNINE/NETTHIRTEEN pairs and new5.
These are source forecasts; native compilation/inventory/verification has not run.
pfc_order.py: prints ordinary pfc sites17/bad0 (pfc-order.txt). Its simple scanner does not inherit
module cfg: the additional17th site is opt-in netcomp leaf, not a new ordinary PFC.
Separately checked actual ordering: swap_net9 line42 before PFC attribute
line48; existing sources unchanged, accurate cfg traversal still ordinary200.
Rustfmt wrapper --check on both changed .rs and git diff --check PASS; Rust/comments<=100 columns.
Read-only Luna High source review found no concrete source blocker (source-review.txt).
No cargo/rustc/Kani/CBMC, local proof/build, Actions/CircleCI/macOS or external dispatch was run.
Protected lane paths byte-identical to tooling base 30f77e859903df14b442ff9294d4fbbd44827f20.
Bound-file SHA256s in tooling-static.txt; Kani9461e07af7ec929f050aa4192f29363c9be07779,
nightly-2026-10-12. Preserve organizer solver/checker flags, --no-assert-contracts/object-bits12,
controls:true, jobs1, uninit off, unwinding assertions; no new profiles or model/compiler changes.
Validator PASS; g1.request.json byte-equals RUN-REQUEST.json; g1.args has only these five exact names.

## Reserve, slot and gate

measurement, timeout10min/row; gcb-e2-standard-4 / k1-standard4, 4CPU/16GiB, swap off.
Envelope (5*10+30)=80min; reserve80*$0.0135=$1.080. Own UUIDs none, spent0/reserved0 (runs.json).
Task cap$2.50, <=2 builds; planned G1+G2 reserve$2.025, compile-only retry alternative$2.160.
Ledger snapshot budget-prebuild.txt: 162 builds, used$77.4060, unfinished reserve$0,
plus proposed G1=$78.4860 <=global cap$88.96. Snapshot recorded in snapshot.json; this is not a slot grant.
No slot claimed/acquired and no submission before coordinator GO for this exact published packet.
Refresh ledger and check active slot immediately before authorized dispatch; reserve current full envelope.
No reinterpretation of $11.55 approximate task-start remainder as spend authorization.

G1 gate needs source/request/pin/tooling identity match, all three positives SUCCESS with required
covers, both controls FAILED solely on intended checks, correct geometry/frame/hits and ordinary200.
Cloud COMPLETE/SUCCESS is distinct from this gate. If any positive times out/OOM/fails/is UNKNOWN,
stop with per-row facts and do not start N13. Only compile error may use G2 to retry same five rows
with mechanism/domain/flags unchanged, after new exact review/GO and own-spent+reserve<=cap.
G2/N13 requires G1 gate plus a new PRE-BUILD GO; no automatic dispatch. There is no G3.
After GO, dispatch only exact reviewed packet, register tools/k1g.sh watch UUID using CODEX_THREAD_ID,
then end turn. Task-specific K-1 evidence access remains bounded summaries/rows/peaks and targeted
check context; full/raw evidence and credentials/hidden configs were not read or downloaded.

## Result obligations after authorized build

RESULT-NETCOMP.md<=45 lines must bind source/request/build/library/pin identities and actual F/value,
trace/binding, per-row status/VT/CBMC RSS/failed-total/unreachable/covers and task gate/next step.
Compare VT(B9)+VT(leaf9) to VT(A9); jobs1 CBMC memory=max(B9,leaf9), never their sum.
Compiler/process-sum RSS, whole-command wall and cost are separate; no speed comparison to old F-item.
TIMEOUT means cap600s with available wall/RSS, VT UNKNOWN unless printed; classify OOM separately.
Only a passing G1 can establish exact N9 u8/U8Cmp canonical, initialized backing9/offset0 composition.
It does not establish old F-item, arbitrary T/FnMut/backings/offsets, N13/N18, tie stability,
initialization detection/full validity/alias/unwind scope, or a PFC contract for the trait method.
Ordinary200/Part1/v6 claims are unchanged. After final authorized gate record PASS/PARTIAL/FAIL,
exact open obligations and NETCOMP ЗАВЕРШЁН; no replacement project on blocker.
