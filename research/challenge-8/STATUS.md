# Challenge 8: current status

Updated 2026-10-06 after completion of the explicitly resumed sort4 phase.
Approval commit: `68fcc98b79fc69b717d3e2ed42605cae8b4ffc05` on
`challenge-8/research`. This is the single current checkpoint; procedures live
in [AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), priorities in [PLAN.md](PLAN.md), and
historical evidence in [EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and execution state

**PHASE CLOSED — both functional proofs passed; generic safety remains open.**
All deliverables from [SORT4-PHASE.md](SORT4-PHASE.md) are saved in
[the closeout](SORT4-RESULTS.md), [contract/caller audit](SORT4-CONTRACT.md)
and [generic-safety decision](SORT4-SAFETY-DECISION.md). No new tool semantics,
patched VeriFast profile or later roadmap phase was implemented. The next
phase or architectural capability needs the owner's separate decision.

Entry: clean tree, fork origin, fast-forward from d436977 to approval 68fcc98;
no newer remote instructions and no active/queued Actions runs. The actual std
blob remains e555fce440872898e47fd5114f32eb15401d07df. The owner explicitly
requested autonomous execution of this phase. Actual-body harness/runner are at
1bc9cb718efc07315082334cded2d2362ecbbde1. Hosted run
[37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500)
completed SUCCESS (sort4_functional/90min; 11:55:16–11:59:55 UTC).
Values: 0/267 failed,12/12 covers; tagged stability: 0/233 failed,6/6 covers.
Full logs/artifacts/source/tool hashes inspected; no active research run.
Workflow-only exposure is 26a43be on research / 3d8c8c0 on main.
Saved insertion draft stays unapplied.

The completed phase delivered:

1. Full target contract and actual caller/aliasing/resource audit.
2. Actual-body Kani sortedness and multiset preservation for four arbitrary
   i32 inputs in separate fixed buffers, with a pure `<` comparator.
3. Separate actual-body tagged-item proof of stability.
4. Existing-evidence-first generic-safety assessment and closeout. No new
   falsifiable unchanged-release route was found, so no generic probe was run.

Kani stays at `152c6a8c875d9886a67e229247b4826d6105ccfd`;
VeriFast stays at unchanged 26.09, source
`809de4596839b739dd999f9e462242c835e3af46`, Rust `nightly-2026-02-05`.
No historical experimental patches are authorized in this phase.
All executable work stays on GitHub-hosted Actions.

## Previous phase remains closed

The ManuallyDrop/insert_tail feasibility phase reached NO-GO for integration.
The owner has now selected the simpler sort4 target; this supersedes the old
wait-for-a-target-decision checkpoint only for the named new phase. It does
not reopen callback integration, patch expansion or full insertion work.

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

The authorized sort4 work is complete. No repeat proof run is needed for the
documentation-only closeout; harness, runner, source and tool pins are unchanged
from the successful SHA. Generic normal/unwind ownership, comparator effects,
allocation/provenance/ZST and all four UB categories remain open beyond the
specific default-check functional domain. Source analysis identifies a missing
non-overlap/ownership policy in the short SAFETY comment; caller separation is
not silently promoted to a universal target precondition.

Recommended next decision: review source-derived tuple-2 ownership/HRTB Output
support together with a full normal/direct-unwind recovery route, explicit
overlap/ownership contract and trust/admissibility regression gate BEFORE
implementation. This assessment does not prove all unchanged-tool routes
impossible. Alternatively approve a separate later roadmap phase, retaining
its own generic blockers. Do not begin either route or external publication
without that decision. No active run; saved insertion draft stays unapplied.
