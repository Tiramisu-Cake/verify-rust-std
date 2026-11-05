# CITRIM — final closeout, partial runtime result

The two authorized primary builds are exhausted; no retry, repair or further dispatch.
Stage complete for review; the full runtime objective is **not achieved: 4/9 families resolved**.
Final library commit `f1ce831c2c9b7a3307a652248c467fb086b94ea5`.
Baseline library `4fa6151b6a9d0ae63261ab03eb86b65cec0a899e` (219 ordinary, 34 opt-in).
Only verify/network.rs differs from baseline: +36/-11 physical lines; runtime/tooling unchanged.
verify/merge.rs is byte-identical to baseline. All five failed original roots were restored,
including the original tail explicit frame; unused experimental merge/tail helpers/macros removed.

## Evidence and source identities

| Stage | Build | Approved source | Result |
| --- | --- | --- | --- |
| citrim-g1 | 76b1664d-a0bf-4268-92fc-3b69220d556f | bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a | COMPLETE, Cloud FAILURE, gate false, Kani exit1; 18 SUCCESS/7 TIMEOUT |
| citrim-g2 | bd623a0c-935a-4bcd-a5c1-5d6f148c6bec | 9cc449ccce74c6b3b8f96554b86308ff39a2b71f | COMPLETE, Cloud FAILURE, gate false, Kani exit1; 2 SUCCESS/13 TIMEOUT |

Both: standard4, jobs1, controls=false, inventory=false, 5 minutes per root;
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`. Each source/request hash and complete bounded
row page is checked by verify_g1.py / verify_g2.py. Both build-bound tooling checks pass against
`59893bff1fbb2af1a0c08862afd7e3bb87c19cdd` (8/8 each). Targeted verify/unused/dead-code scans
found no matches; G2 targeted scan also found no unwinding-assertion text. This is a bounded scan,
not a claim that timeout roots completed without unwinding failures.
No raw logs, caches, archives, credentials, competitor code, local proof tools or subagents read/run.
The original G1/G2 PREBUILD files and main expected lists are historical proposed packets,
not the final inventory. RUN-REQUEST.json is the consumed historical G2 request; do not dispatch it
against the reconciled final source. Current artifacts use the `final-` prefix.

## Decisions for all nine original domains

All final unions, selected measurements and rejected experimental rows are in final-check-report.json.

| Original verify:: family | Final decision | Final selector union |
| --- | --- | --- |
| merge::general_direct_u64_n9 | RESTORE ORIGINAL | identity; all G2 parts timed out |
| merge::stable_direct_u64_n9 | RESTORE ORIGINAL | identity; all G2 parts timed out |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | KEEP SPLIT | N15/N16/N17 × both routes |
| network::dispatch_safety_stable_unstable_bytes16_n32 | KEEP SPLIT | stable N32 ∪ unstable N32 |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | KEEP SPLIT | N15/N16/N17 × both routes |
| network::insert_tail_contract_u64_start1_tail2_to8 | RESTORE ORIGINAL | identity; both G2 parts timed out |
| network::insert_tail_contract_u64_start1_tail9_to12 | RESTORE ORIGINAL | identity; both G2 parts timed out |
| network::insert_tail_contract_u64_start1_tail13_to14 | RESTORE ORIGINAL | identity; G2 tail13 299.7872s, tail14 timed out |
| network::network_safety_unstable_u64_n30_to32 | KEEP SPLIT | N30 ∪ N31 ∪ N32 |

Restored bodies/attributes and all shared dependencies match baseline exactly. Do not replace them
with timed-out or >120s parts in the final submission. Their >200s Actions issue remains open;
future optimization needs a separately authorized task/budget. No root or input case is dropped.

The 11 kept parts comprise 10 G1 parts plus G2 unstable bytes16 N32 (118.51086s, 0/382, covers2/2).
Each is SUCCESS, zero failed checks, exact covers reached and <=120s. Combined covers **31/31**;
verification-time sum **989.115644s**, max **118.51086s**, margin to120 only **1.48914s**.
G1 N30/N31/N32 are also near the boundary (112.934250/116.823906/117.063560s).
The static checker compares final expanded bodies and attributes to their bound build source,
and requires all old shared items byte/token-identical. This supports carrying that bounded evidence
to final source; no new final-source build/full-suite proof is claimed.

Only retained unstable bytes16 N32 uses Kissat/unwind33; its G1 version with the same guard and unwind65 was 126.870476s
in G1, and the selected combined tuning is 118.51086s in G2. The two changes are confounded;
no solver-only or bound-only causal speedup is claimed. Other retained bounds/stubs are unchanged.

## Tail experiment and coverage-equivalence rationale

The coordinator-authorized G2 tail helper omitted only the explicit frame call and relied on checked
PFC modifies. With begin=base+1, tail_len=tail, the modified indices are [1,tail]. The former frame,
{0} union [tail+1,16], is exactly its complement in backing17; PFC checks that modifies guarantee.
The old helper's other inputs, assumptions, profile comparator/requires/ensures and covers remained.
Root docs at source9cc449c and archived static report record this argument and enumerate tail2..14.
The G2 variant kept Kissat/unwind18. Five tail parts timed out; tail13 succeeded at299.7872s.
Therefore none of the three tail families met the target, and all were restored to baseline,
including their original explicit frames. No isolated timing of frame removal was measured here.
Coordinator-reported TAILDIAG `59ada14d0a` (183 ->31s, ~5.85x) is a source claim for that other
experiment only; no neighboring branch/code/diff was inspected and no transfer of timing is claimed.

## Final inventory handoff

Source ordinary **226 =219 -4 +11 (+7)**; cfg-on **260 =226 +34**. There are **215** baseline
ordinary roots retained token-identically, including the five restored targets; all34 opt-in roots
unchanged. Every one of the original219 domains survives directly or as an exact union.
Current exact names: final-ordinary-expected.txt; cfg-on names: final-cfg-on-expected.txt.
Names SHA256 (newline-terminated, sorted full qualified names):
`5d67fd2609986d5ae017c7ab6833a8a93880bd5691d40a47afd184e5ccababea` (also in final-check-report.json).
This is a **source inventory**, not compiler output. No compiler inventory was requested in G1/G2.
Per coordinator instruction, a separate coordinator-owned/budgeted inventory build is still needed:

1. Bind its source/library exactly to the final library commit; any later change requires renewed
   comparison. Use the unchanged Kani pin/tooling, standard4 and controls=false.
2. Read only bounded k1g inventory pages; validate build/head/request/Kani and inventory hashes,
   continuation offsets and terminal next_offset=done.
3. Require exactly226 unique ordinary names equal to final-ordinary-expected.txt; all34 opt-in names
   absent. Do not compare to the historical235-name G2 proposed packet.
4. Save bounded report and state whether compiler inventory matches. Do not convert the source count
   or two diagnostic builds into full-suite proof credit.

Full-suite verification time before/after is unknown: only11 final parts were measured in these runs,
and the other215 final roots were not reverified in CITRIM. Supplied original Actions times sum
1804.5s Ubuntu/2126.0s macOS for nine roots, but paired original-root GCB data is unavailable in inherited
own reports. No measured platform multiplier or fair total speedup is available. At the task's
2x heuristic, max118.51s GCB is ~237.02s Actions, so Actions <=200s is not guaranteed.

## Budget and completion

G1 $1.1880, G2 $1.0935, total **$2.2815/$3.00**, reserved0, headroom$0.7185. Costs are from the
bounded two-build helper ledger (G2 derived by subtracting G1); 2/2 primary builds, 0 repairs/retries.
Both builds finished before main deadline16:00Z; closeout deadline16:30Z remains unchanged.
Finish by publishing the final research commit and REVIEW REQUEST / CITRIM ЗАВЕРШЁН marker.
This closes the assigned stage with five unresolved runtime blockers and inventory handed off.
