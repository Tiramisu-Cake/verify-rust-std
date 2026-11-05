# CITRIM — exact G2 pre-build packet

PRE_BUILD_REVIEW_PENDING. G2 has not been dispatched; fresh exact-packet GO required.
Task TASK-CITRIM.md, owner k1-merge; worktree `/root/verify-rust-std-kani-citrim`;
branch `experiment/kani-k1-citrim-20261105`. This is the second/final primary build, no retry.
G1 approved packet `bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a`, library `d866f287bb844b788ea853d0bb2fe829ddbf7292`.
G2 library commits `26d5083990bf5c5996376a061aa4a06389aa4568` and
`57bf69b29046d515091dda662f180dba64cea041` (separate [skip ci] commits).
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` unchanged; runtime unchanged.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`; nightly 2026-10-22.

## G1 evidence and acceptance

Build `76b1664d-a0bf-4268-92fc-3b69220d556f`, exact approved source, standard4,
COMPLETE, Cloud FAILURE, Kani exit 1, gate/expectation false. This is not a setup/compile error.
Tooling: all 8 checks pass. Bounded targeted verify/unused/dead-code warning scan: no match.
All 25 requested rows are present with exact request/build/head bindings, next_offset=done.
18 SUCCESS, 7 TIMEOUT; of the 18 successes only 10 satisfy <=120 seconds.
Completed roots have 57/57 covers; 7 timed-out roots have unknown cover/proof results.
Do not call the result 64/64 or count timeout rows as proven. Unreachable non-cover checks
are not unreachable covers. Full root timings are in g1-evidence/rows.txt and summary.md.
Completed verification-time sum 2597.189200 s; full 25-root verification-time sum unknown.
Runner wall 1:20:29 including compile/instrumentation; Cloud start..finish about 87 min.
No OOM seen; runner max RSS 2993108 KiB. Cost **$1.1880**, outstanding reservation $0.
`verify_g1.py` validates bounded saved evidence: consistency PASS, task acceptance FAIL.
No raw log/cache/archive inspection, local proof tools or subagents were used.

| Group | G1 evidence, seconds per part | G2 action |
| --- | --- | --- |
| general N9 | ge_ge/ge_lt/lt_ge TIMEOUT; lt_lt 298.004330 | new four first-comparison partitions, Kissat, unwind10 |
| stable N9 | four TIMEOUT | same four partitions, Kissat, unwind10 |
| bytes16 N15/N16/N17 | 57.527676 / 63.919994 / 64.923390 | carry unchanged |
| bytes17 N15/N16/N17 | 62.401028 / 70.842450 / 95.443690 | carry unchanged |
| bytes16 N32 stable/unstable | 108.724840 / 126.870476 | carry stable; unstable Kissat/unwind33 |
| tail2..5 / 6..8 | 210.270110 / 229.835190 | checked modifies frame, Kissat/unwind18 |
| tail9..10 / 11..12 | 193.222260 / 199.784850 | checked modifies frame, Kissat/unwind18 |
| tail13 / 14 | 231.391420 / 237.205780 | checked modifies frame, Kissat/unwind18 |
| network N30/N31/N32 | 112.934250 / 116.823906 / 117.063560 | carry unchanged; small margin disclosed |

## Exact domains, source checks and unwind argument

The nine original domains still equal the disjoint unions recorded in check-report.json.
Eight merge parts now choose the first comparison of the first sort4 in each half:
`(lt_u64(&v[1], &v[0]), lt_u64(&v[5], &v[4]))`. The comparator uses the original `x >> 1` keys,
so the partitions expose actual runtime branch outcomes. Each pair of booleans appears once;
false includes equal keys (and equal full values). All [u64;9] inputs and the entire independent
128-byte probe domain remain. Both half inputs are unchanged when their sort4 comparisons run.
New names use swap0/keep0 and swap4/keep4 to distinguish them from the old G1 input partitions.
No G1 merge proof credit is transferred to these differently partitioned roots.

The helper bodies project exactly to the original N9 helpers after deleting only the two
partition assumptions and normalizing the helper/generic names. Assertions, oracle, allocations,
comparator and cover labels are unchanged. Other network splits remain exactly as approved in G1:
N15/N16/N17, N32 stable/unstable, tails [2,5]∪[6,8], [9,10]∪[11,12], {13}∪{14}, N30/N31/N32.

## Coordinator-authorized frame correction for the six tail parts

The 2026-11-05 coordinator instruction authorizes replacing the explicit post-call frame
with the profile's checked modifies guarantee. New helper `insert_tail_group_value_modifies_frame`
is exactly the original helper with only `insert_tail_start1_frame::<START>(&v, &pre, tail)`
omitted. The original helper and frame function remain unchanged for tail15..16.
Root doc comments state the justification. All six tail domains, backing arrays, input/probe,
comparator, requires, sortedness/permutation ensures, covers and movement-cover pre-copy remain.
No new assumption or stub is introduced. The other nine G2 parts are unchanged from packet
`7e382c4a1c7075245b3202939c0d931e199e4025`; all 10 carried G1 parts are unchanged as well.

For START=1, begin=base+1 and end=base+tail, so tail_len=tail and the profile's modifies slice
is exactly the inclusive element interval [1,tail]. In backing indices [0,16], the prior frame
is {0} union [tail+1,16], exactly its complement (and therefore a subset of the complement).
`proof_for_contract(insert_tail_profile)` checks that modifies guarantee on the real callee;
the unchanged modifies attribute is
`ptr::slice_from_raw_parts_mut(begin, tail_len::<P::Elem>(begin, tail))`.
Thus the PFC still checks out-of-region preservation; duplicate post-call comparisons add
no independent frame obligation. The static checker enumerates this complement for every
tail2..14, verifies the helper projection and unchanged profile contract, and freezes other roots.
This is a source argument for coverage equivalence; G2 success is still required.

Coordinator-reported motivation: TAILDIAG `59ada14d0a`, branch
`experiment/kani-k1-taildiag-20261105`, RESULT-TAILDIAG: 183 ->31s (~5.85x) after removing an
explicit post-call frame while retaining PFC modifies. This is supplied evidence, not an
independently inspected result or a CITRIM timing prediction. No neighboring code/diff was read.
Final selected variant keeps **Kissat/unwind18** for all six tail parts.

Only the 15 problem parts gain `#[kani::solver(kissat)]` and lower unwind. Solver selection
changes the verification backend, not the program/domain. The existing runner already checks
Kissat installation/version. This is an experiment; no speedup is asserted before G2.
[Kani attributes documentation](https://model-checking.github.io/kani/reference/attributes.html)
documents solver selection and failing unwinding assertions for insufficient bounds.

| Parts | Old -> new unwind | Source bound rationale |
| --- | --- | --- |
| 8 merge N9 | 34 -> 10 | exact array N9; sortedness loop8, merge loop4, half-extension loops <=1, insertion loop<=4; 10 covers a 9-iteration array loop plus exit |
| 6 insert-tail | 25 -> 18 | backing17; full prefix_unchanged scan <=17 plus exit; real insertion <=13; duplicate frame scans omitted; model_count/model_sorted are loop-free |
| unstable bytes16 N32 | 65 -> 33 | from_fn exact32 plus exit; general sort halves/extensions and merge loops <=16; sort8 merges4, insertion <=15 |

These are source arguments, not a preclaimed compiler/proof result. No unwinding assertion is
removed or disabled; any insufficient bound in G2 is a failure, never accepted as coverage.
`check_citrim.py`: PASS_SOURCE_ONLY; 210 original retained ordinary roots and all 34 opt-in
roots token-identical to base, all old shared helpers/macros retained verbatim, runtime/tooling
unchanged. All 10 carried G1 roots are also token-identical to their successful G1 expansions;
their old shared dependencies are unchanged. Compiler inventory is still outstanding.
Ordinary **235 = 219 - 9 + 25**, cfg-on **269 = 235 + 34**; exact expected lists are alongside.

## Exact G2 request and budget

Request `citrim-g2-20261105-02`: diagnostic, standard4, k1-merge, jobs1,
controls=false, **inventory=false**, 15 SUCCESS roots, 5 minutes each. Full exact root names:
RUN-REQUEST.json; request SHA256 in RUN-LEDGER.json and check-report.json.
Require each <=120s and **35/35 covers** with exact per-root totals in expected-g2-covers.json.
Carry 10 unchanged G1 parts with **29/29** covers (carried-g1.txt); combined target **64/64**.
Acceptance of the new root set requires all G2 rows and covers, not merely a green runner gate.

Maximum 75 harness-minutes +30 overhead = **105 min**, reserve **$1.4175**.
Own spent $1.1880 + proposed reserve $1.4175 = **$2.6055 <= $3.00**; headroom $0.3945.
One compile-error repair per build only if separately permitted by remaining own cap/window;
G1 used no repair, and its failure is not eligible as a compile-error repair. No retry or G3.
Window anchored 11:00Z: main deadline 16:00Z, closeout 16:30Z. Recheck exact remaining time
before dispatch; a 105-minute maximum G2 must fit the remaining main window.
Project snapshot: 243 builds, used $104.1495, reserved $0; with G2 max $105.5670 <=$118.96.
Request SHA256: `7822880947beb888d1a7a3103b2f8e9c2b942269536565ee3363e1884d2d7616`.
Latest full105-minute dispatch is 14:15Z; no window extension is implied. Recheck at dispatch.

Inventory is explicitly handed off per coordinator instruction: if it does not fit, report
and run separately. Existing gcb-k1.sh documents about 49 min for the complete std kani-list
preparation; its budget is consumed before verification and is not added by inventory=true.
49 min inventory +75 min of full root allowances +setup/instrument/upload would exceed105 min.
Even 49+75+8=132 min costs $1.782; with G1 this is $2.970 and leaves only ~$0.03 margin, but the
unchanged dispatcher cannot request a 132-minute timeout for this 15x5 packet: it fixes105 min.
No padding roots, tooling changes or premature inventory success claims are introduced.
A separate coordinator inventory build must bind its source/library to the final CITRIM commit,
controls=false, exact ordinary names and count (currently235; update if final fallback changes).
It is outside the two CITRIM primary builds and needs its own authorized budget/owner.

## Execution after fresh exact-packet GO

Confirm approved pushed source, free owner slot, project/own cap and window; dispatch once.
Record source/request/build UUID and reserve, run `k1g.sh watch BUILD`, then end the turn.
On wake: bounded summary/rows, tooling, warnings, covers, cost; do not poll status in a loop.
Keep measured GCB times distinct from supplied Actions baselines; no paired original-root GCB
measurements are available in inherited own reports, so no empirical Actions scaling factor.
If a family still cannot meet the runtime goal, restore that original family unchanged and
report its unresolved >200s issue as TASK-CITRIM.md requires; do not delete its cases/checks.
Publish final RESULT-CITRIM.md <=45 lines, review marker, then stop. Inventory remains a disclosed
coordinator closeout item until bounded, source-bound evidence for the final library is supplied.
