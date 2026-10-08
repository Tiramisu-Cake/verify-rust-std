## Actual callee conditional checkpoint — 2026-10-08 Moscow

Run37711781188/proof5bbd2ef: unchanged actual merge_up/down full normal/unwind
posts and source/export/decode/refinement/body/return/leak/dead gates PASS.
Domain: positive stride, distinct source owned cells, initialized-or-uninitialized
valid destination option cell, explicit aligned bounded disjoint C1 domain.
Current source values/T.own and comparator state/F.own survive both outcomes;
normal copies the selected current value, advances exact cursors; callback panic
leaves destination untouched. No destination T.own duplication or entry snapshot.
New strict cleanup kernel/frontend remains experimental pending exact6proof+
4admission controls. Full caller pointer trace and actual bidirectional OPEN.
Night2894/21600 job seconds; historical603/1800 separate.

## Overnight W1d checkpoint — 2026-10-08 Moscow

W1d proof8d97b6bc/run37700424582:22 bounded wrapping primitive/projection
positives,5 intended negatives,9 terminal/source bridge cases and full G2/A/B
compatibility checked. Primitive contracts TRUSTED; wrapper machine bodies,
full pointer trace, actual merges and resource/unwind composition OPEN. Full
profile acceptance still requires separate baseline/unwind/C++ controls.
Night467/21600 seconds; historical603/1800 separate.

## MERGE-STOCK-26.10 closeout — 2026-10-08

G2/A/B and nine conditional Rust projections reaccepted on official stock26.10.
Both exact const-pointer wrapping methods unsupported; semantic properties OPEN.
[New report/table](STOCK-26.10-RESULTS.md), [current status](STATUS.md),
[separate profile](stock-26.10/PROFILE.md). Proof1be9c131/run37694164542;
603/1800hosted seconds used1197remain. No actual merge/Challenge theorem.
Older sections below preserve historical26.09 and CI0sync states; their stops,
proof SHAs and budgets are not relabelled as new results/authorization.

# Independent merge coverage

G2accepted:8lemma bodies/88statements/17return-leak, all3negatives/21controls.
Checked proofSHA b1ed0c22dafec350a64e83675d55350806d77208. Actual Rust OPEN.

| Obligation | Established mathematical evidence | Boundary |
| --- | --- | --- |
| Exact active Rust schedule | Full-source SHA32574f..., active operation certificate for three functions | Hosted admission accepted; no Rust AST/MIR/refinement proof |
| merge_up access/advance | Both reference reads, selected copy source/write BEFORE right/left/dst add; arbitrary normal Boolean | Pure integer positions only |
| merge_down access/advance | Both reads/copy/write BEFORE right/left wrapping_sub and ordinary dst.sub | Requires dst>=1 for ordinary sub; the mathematical bidirectional caller proves this |
| Arbitrary-length paired loop | Count invariant and structural induction over arbitrary decision list of length n/2 | Accepted structural induction, no bounded enumeration/SWO |
| Odd residual/endpoints | Both sources readable, dst=n/2, selection/advancement and terminal boundary guards | Arbitrary residual Boolean handles ZST comparison uncertainty geometrically |
| Destination geometry | Forward/reverse disjoint intervals, odd gap, exactly n writes | No physical write/initialization/resource theorem |
| Scalar final checks | Even a=d; odd a+h=d, exact scalar h=a<d supplemental | Not automatically pointer equality/order, particularly ZST |
| Negative controls | Read at n, invalid advance, exact proof predicate/location controls | Concrete witnesses calibrate classifier, not universal proof |
| Actual Rust memory/unwind/functionality | None | Provenance/overflow/ZST/permissions/initialized T/ownership/FnMut/panic and actual Rust sorting OPEN |

Networks proof/budget ledger is frozen separately; no transfer of its remaining
seconds or status to this phase. Current own [STATUS](STATUS.md), [plan](PLAN.md),
[source map](SOURCE-MAP.md), [integration obligations](INTEGRATION.md).

The complete trace fixes destinations k andn-1-k at every inductionstep;
mg_destination_regions separately proves crossinterval separation. Exact n
writecount alone is not a destination uniqueness theorem. Traceequations and
these bounds yield full evencoverage / oddsolegapm as mathematicalcorollaries.
Actualinitializeddestination/Townership afterpanic is NOT established.
Original geometry closeout:25/1800jobseconds,1775unspent; current total below.

## Authorized functional stage

| Obligation | Status / checked evidence | Boundary |
| --- | --- | --- |
| Exact chronological ID writes / natural output | A2 accepted SHAfc4d03d31f92c6d3f3566b0baa506d0a6dec6805/run37677079473 | Scalar mathematical events; actual copy/memory OPEN |
| Every destination exactly once | Arbitrary p: count1 iff0<=p<n; tracevalue equals output nth | Full arbitrary-length induction; no physical init theorem |
| Every original occurrence exactly once | Arbitrary q: count1 iff0<=q<n under only scalar guard | Arbitrary comparator and odd choice, no SWO/sortedness |
| Duplicate/loss negative without guard | n2 output[0,0], intended multiplicity assert and7controls accepted | Guard is necessary; panic/copy ownership OPEN |
| Fixed SWO sorting/stability/guard | B7 accepted SHA4e546ec150cf655681516be727aa1a79f525fc56/run37681190236;65bodies/505statements/197return-leak | Immutable keys, faithful normal answers, sorted original halves and scalar residual only in B |
| Tie / wrong comparator negatives | Both exact assertions274cols39-41/31-33 accepted with14controls; duplicate218 adds7 | Guard/permutation pass; stability/key order respectively fail |

Latest functional ledger in RESULTS/STATUS supersedes initial geometry budget
checkpoint above; original G2 proof/source/results retained byte-for-byte.

B7 also rechecks the original generic finite SWO predecessor-count bridge and
constructively translates every comparison and original-half sortedness; no
rank correspondence axiom. Forward-left/backward-right tie selection checked
in separate bodies. All mathematical A/B targets closed; actual Rust remains
OPEN. Functional-completion budget330/1800,1470remaining is historical; the
same cumulative budget continues below without reset.

## Stock Rust pointer/index stage — 2026-10-08 Moscow

P3 proof1c318453efa4e3a774b2edd791a5298d76132eb0/run37686627140:
9positive units,12own bodies,102own execution records,25return/leak paths,
2intended negatives,128strict classifier controls accepted. Full export/decode/
verifier/refinement/source/dead-code gates, stock26.09; fixture refinement only.

| Obligation | Status | Boundary |
| --- | --- | --- |
| Caller/ZST applicability | Audit COMPLETE | Public stable/unstable entry returns cover callers; direct generic Challenge retains ZST |
| Direct network ZST | Semantic audit: short return / long same-address loop | Does not reach merge normally; no stock layout/termination proof |
| Local G2 step/terminal formulas in Rust | Checked bodies PASS | Full C-to-Rust trace/composition not assumed |
| Exact generic const/mut add; Boolean add steps; destination sub | PASS with result/provenance/limits posts | Nonzero size, explicit count/byte/provenance-limit premises; caller resource proof OPEN |
| left<left_end and final pointer OR guard | PASS conditional on pointer/index associations; stride lemmas checked | Terminal wrapping associations not derived |
| Wrong cursor / address-only index restoration | Intended TARGET assertions rejected,20controls | No earlier-stage failures counted |
| Exact wrapping_sub / wrapping_add | UNSUPPORTED, P2 No such function | Wrapping/provenance/re-entry composition STOP; no later rerun |
| Reading intermediate -1 | INCONCLUSIVE before read in P2; corrected draft NOT RUN | No read detector claim; -1 never declared readable |
| Actual copies, memory, initialization, ownership, FnMut, unwind | OPEN | No whole merge/Challenge safety or functionality theorem |

Positive-size premise remains component-local. G2/A/B and their premises/results
preserved. Same budget **512/1800 used,1288remaining**,182newseconds including
setup/evidence. No active run, tool patch, network/exactN13 work, budget transfer
or first-agent-tree change. P1/P2 failures remain recorded in RESULTS/journal.
