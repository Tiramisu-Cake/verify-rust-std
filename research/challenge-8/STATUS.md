# Challenge 8: current status

Updated 2026-10-06 after the owner approved the revised roadmap and next phase.
Approval baseline: `25c590235c67107cffc92cf70b69568c388ac3ed` on
`challenge-8/research`. This is the single current checkpoint; procedures live
in [AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), priorities in [PLAN.md](PLAN.md), and
historical evidence in [EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and execution state

**READY — the bounded actual `sort4_stable` phase is approved.**
Its exact scope, tool allowlist, deliverables and stop conditions are in
[SORT4-PHASE.md](SORT4-PHASE.md). The continuation agent may implement, commit,
push, dispatch, inspect and fix routine issues within that phase without
asking the owner to approve its start again. Check for newer instructions,
branch changes and running jobs before acting.

The approval/documentation iteration has made no proof or runtime changes
and dispatched no workflow. No sort4 harness, runner selection or proof result
is established yet. No active research run was observed at this checkpoint;
the last proof runs below are unchanged.

The approved phase covers:

1. Full target contract and actual caller/aliasing/resource audit.
2. Actual-body Kani sortedness and multiset preservation for four arbitrary
   i32 inputs in separate fixed buffers, with a pure `<` comparator.
3. Separate actual-body tagged-item proof of stability.
4. Existing-evidence-first generic-safety feasibility assessment, followed by
   at most one justified unchanged-release diagnostic route and a closeout.

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
| [37401540878](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401540878) / unchanged VeriFast 26.09 | Actual unrestricted generic size helper, exact size_of(T)<=8 on LP64 | Isolated function; dispatch callers/full-core integration open |
| [37419989766](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37419989766) / experimental patched VeriFast | Actual generic CopyOnDrop::drop body, exact destination and ONE ownership sequence | Conditional source/destination resources, arbitrary valid len; not insertion |
| [37435525052](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37435525052) / experimental patched VeriFast | Actual Drop plus two one-cell callers (normal and FnMut() normal/unwind); 25 controls and 7 intended negatives | Local cleanup gate completed; not held &T provenance or actual insert_tail |
| [37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808) / unchanged VeriFast 26.09 | i32 and unrestricted T two-cell sharing/recovery, checked helper/callers, full current cells/T.own; 3 intended negatives | Natural Rust block, normal path only; no callback, panic, ManuallyDrop or std insertion |

Only the size helper has an isolated generic proof among the seven required
safety targets. The other six and all three sorting contracts remain incomplete.
See [coverage](coverage.md); do not equate a microfixture or patched-tool success
with whole-function proof, verifier soundness or upstream acceptance.

## Latest evidence and preserved draft

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

Read AGENTS, this checkpoint, PLAN, SORT4-PHASE and the runbook. Audit the
actual sort4 body/callers, record the contract and first experiment card, then
implement and execute the functional harnesses through a new hosted selection.
The full generic target and the concrete functional domain must remain separate.

Use existing tuple/HRTB/borrow/unwind evidence before any generic-safety probe.
A required semantic extension ends that route and becomes a documented
architecture decision. Complete independent authorized functional work when
possible; do not treat the generic blocker as a reason to abandon it.

At phase closeout, update this checkpoint and coverage, preserve run evidence,
and present the next decision. Later roadmap stages, verifier semantic changes
and external publication still require separate owner approval.
