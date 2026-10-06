# Challenge 8: current status

Updated 2026-10-06 after the owner approved the sort4 contract-diagnostics and
generic-proof-route phase. Approval baseline:
`bea705d12062e515e69abc4ab4398944f9f82d65` on `challenge-8/research`.
This is the single current checkpoint; procedures live in
[AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), priorities in [PLAN.md](PLAN.md), and
historical evidence in [EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and execution state

**IN PROGRESS — the sort4 contract-diagnostics and architecture-proposal phase
is executing under owner approval commit `54485d632bfca9d69fee853bd6aa30bc330647c9`.** [SORT4-CONTRACT-PHASE.md](SORT4-CONTRACT-PHASE.md) defines its exact
scope, tool allowlist, deliverables and stop boundary. A continuation agent may
implement, commit, push, dispatch, inspect and fix its Kani diagnostics without
asking for the same start approval again. Check newer instructions, the branch
head and active runs at entry.

Entry audit: clean working tree, fast-forward to approval commit, fork origin and
research branch confirmed; main at `3d8c8c082a69dbb66c4ab566892e6be71d87a86d`.
No active research run observed. First hosted run [37464581019](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37464581019),
source `a082e0cf0c45d8bccf4c7df46eff9b84278a9f67`, selection
`sort4_contract_diagnostics`/90min. Card and isolated cases committed;
completed FAILURE: control and coincident copy negative accepted; shifted/witness
blocked by own array-equality memcmp unwind, correctly rejected as unrelated.
Routine proof-only element-equality fix prepared; NEW exact-SHA dispatch next.
The last successful proof remains run37459631500 below.

The new phase authorizes:

1. Actual-source Kani diagnostics for coincident buffers and shifted overlap,
   with the unchanged values harness as a positive control. Distinguish the
   expected copy-overlap safety failure from expected multiset failure.
2. Explicit safety/functionality/ownership/normal-and-panic contracts, mapped
   to actual callers and separated from any proposed contract strengthening.
3. Read-only review of historical VeriFast patches/evidence and one concrete
   generic-safety architecture proposal with a bounded future regression gate.

Executable work is Kani only, on GitHub-hosted Actions, at unchanged pin
`152c6a8c875d9886a67e229247b4826d6105ccfd`, Rust `nightly-2026-02-05`,
default checks and exact serial harness selection. No new VeriFast run,
patch application/build, semantic change or later target is authorized.
Historical patched profiles are evidence for the proposal only.

## Completed sort4 functional phase

[SORT4-PHASE.md](SORT4-PHASE.md) remains closed. Its results are retained in
[the closeout](SORT4-RESULTS.md), [contract/caller audit](SORT4-CONTRACT.md)
and [generic-safety assessment](SORT4-SAFETY-DECISION.md).
The actual std blob stays `e555fce440872898e47fd5114f32eb15401d07df`.
Harness/runner source is `1bc9cb718efc07315082334cded2d2362ecbbde1`;
[run 37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500)
completed SUCCESS (sort4_functional/90min; 11:55:16–11:59:55 UTC).
Values: 0/267 failed, 12/12 covers; tagged stability: 0/233 failed, 6/6 covers.
Full logs/artifacts/source/tool hashes were inspected. Workflow-only exposure
was 26a43be on research / 3d8c8c0 on main.

Both actual-body functional theorems are established for their concrete
types, separate initialized buffers and pure nonpanicking comparison.
Generic safety remains open. The phase found no new falsifiable route through
unchanged VeriFast and ran no generic diagnostic; that was a static feasibility
decision, not an executed generic failure. The current phase follows up on
the missing explicit overlap/ownership contract and the architecture question.

## Earlier insertion/ManuallyDrop phase remains closed

The ManuallyDrop/insert_tail feasibility phase reached NO-GO for integration.
The subsequent sort4 phases preserve that stop. Neither the completed
functional proof nor the new contract phase reopens insertion callback
integration, patch expansion or full insertion work.

The actual conditional `recover_single` body verifies through return and
leak-check (16 records), and five independent baseline controls pass. Both
ManuallyDrop callers still stop before the reference/helper call: immutable
tmp offers half storage where full borrow construction needs a whole cell.
Original RawPtr refinement failure and the draft's unproved child-pointer
permission bridge remain. The missing-init negative was not reached.
Source-exact first false return and direct panic recovery remain unestablished.
See the [preserved closeout and historical profile](PREPARED-PHASE-2026-10-06.md).

## Established milestones — not Challenge 8 completion

| Evidence | What passed | Boundary |
| --- | --- | --- |
| [37383583285](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37383583285) / Kani | Two actual swap harnesses, 5/5 covers | Four i32 cells, fixed positions 1/2; not generic safety |
| [37389298278](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37389298278) / Kani | Insertion adapter, research summary caller and direct actual outer function, 15/15 covers | Lengths/offsets 1..4, sorted prefix, unwind 6; not arbitrary-length modular proof |
| [37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500) / Kani | Actual sort4 sorted exact i32 multiset and separate tagged-item stability;18/18 covers | Complete four-element arity, full i32 range; fixed disjoint buffers, pure nonpanicking `<`, concrete Copy layouts; generic safety open |
| [37401540878](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401540878) / unchanged VeriFast 26.09 | Actual unrestricted generic size helper, exact size_of(T)<=8 on LP64 | Isolated function; dispatch callers/full-core integration open |
| [37419989766](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419989766) / experimental patched VeriFast | Actual generic CopyOnDrop::drop body, exact destination and ONE ownership sequence | Conditional source/destination resources, arbitrary valid len; not insertion |
| [37435525052](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37435525052) / experimental patched VeriFast | Actual Drop plus two one-cell callers (normal and FnMut() normal/unwind); 25 controls and 7 intended negatives | Local cleanup gate completed; not held &T provenance or actual insert_tail |
| [37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808) / unchanged VeriFast 26.09 | i32 and unrestricted T two-cell sharing/recovery, checked helper/callers, full current cells/T.own; 3 intended negatives | Natural Rust block, normal path only; no callback, panic, ManuallyDrop or std insertion |

Only the size helper has an isolated generic proof among the seven required
safety targets. The other six and all three sorting contracts remain incomplete.
See [coverage](coverage.md); do not equate a microfixture or patched-tool success
with whole-function proof, verifier soundness or upstream acceptance.

## Previous recovery evidence and preserved draft

- Diagnostic [37448257248](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448257248),
  source f0f417ce9913f53a90591c89593b31b359b87032, minimal profile/90min:
  completed/failure. Actual recover_single body passes; five baseline controls
  pass. Both MD callers fail full borrow construction with missing points_to<T>
  at tmp_addr before reference/helper call. Positive refinement still rejects
  original RawPtr. All seven exports/decodes, six refinements, exact source/tool
  audits pass. No full lifecycle or intended missing-init negative established.
- Unchanged-release baseline
  [37448682524](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37448682524),
  same source, verifast_borrow_recovery/90min: completed/success; both positives,
  three intended negatives, all five refinement/export/decode checks pass.
- Historical37441463201 remains evidence of the prior common-helper failure.
  Its new helper failure is superseded, its caller/pointer gate was never green.

[DRAFT-MD-RECOVERY-2026-10-06.patch](DRAFT-MD-RECOVERY-2026-10-06.patch) remains
UNAPPLIED and UNVERIFIED. Review rejected its absolute/relative fraction mixup
and unsupported permission transfer to a saved shared-reference-derived pointer.
Only independently designed access packaging was implemented. See experiment
log for exact costs, hashes, diagnostics and case counts.

## Next permitted action and stop boundary

Read the current phase, record IN PROGRESS at entry, and prepare the exact
experiment card. Implement isolated actual-source cases and fail-closed
expected-negative result classification before the first hosted dispatch.
Do not report the shifted-overlap multiset counterexample as an UB finding,
or treat any nonzero verifier exit as an accepted negative.

Refine the contract and use existing patch/source/regression evidence to
recommend one generic proof route. At closeout save observed cases, contract
delta, exact evidence boundaries and the proposed future experiment.
Implementation of that verifier capability remains a separate owner decision.
No automatic advancement to swap, networks, insertion or external publication.
