# Challenge 8: current status

Updated 2026-10-06 after explicit owner resumption, starting from instructions
commit `f50b237` on `challenge-8/research`.
This is the single current checkpoint; procedures live in
[AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), historical evidence in
[EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and stop state

**PHASE CLOSED: explicitly resumed and executed on 2026-10-06; NO-GO for expansion.**
Entry tree was clean; fork origin; fast-forward to instructions commit f50b237.
Source changes committed/pushed at f0f417ce9913f53a90591c89593b31b359b87032.
Both hosted runs completed; no active run. No tool semantic/patch changes and no
local compilation, verification or executable tests. Saved draft remains unapplied.

recover_single's actual conditional resource body now verifies through return
and leak-check (16 records). All five independent baseline controls pass both
minimal profile and unchanged release. Full ManuallyDrop caller gate is NOT
passed: immutable tmp exposes half storage, while full_borrow_content needs a
whole cell; both callers stop before actual reference/helper call. Original
RawPtr refinement failure remains, and draft's saved child-pointer substitution
has no established permission bridge. Missing-init negative is not reached.

The actual first false return/direct panic still have no established source-exact
full recovery route under allowed semantics. See [phase report](PREPARED-PHASE-2026-10-06.md).
The authorized phase stops here per owner's frozen trust boundary. Next action
requires the owner's architecture decision: separately review tool/refinement and
scope/unwind semantics, find another existing-semantics route, or choose a simpler
target. Do not begin callback integration, patch expansion or the next phase.

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

## Prepared phase after explicit resumption — limited feasibility gate

This bounded phase was explicitly authorized and has reached its stop boundary.
The following records its contract; it does not authorize another phase.
No new verifier semantics, callback integration or full insertion proof is part
of it. Autonomy covers routine fixture/spec/audit fixes and hosted iterations
within these boundaries, then stops for an architecture decision.

1. Review and isolate same-reference `recover_single` bookkeeping. Prove the
   coefficient/resource conditions; retain unrelated baseline controls without
   the new helper. State expected proof stage/predicate/location for each case.
2. Resolve the raw-pointer provenance/refinement blocker without weakening posts,
   bypassing the checker or changing the target's pointer semantics. If that
   requires changing tool semantics/support, STOP and present the decision.
3. Once statically justified, run the seven-case minimal ManuallyDrop gate on a
   NEW pushed SHA, inspect all evidence, and record only the established scope.
   Use the separate unchanged-release baseline control when relevant.
4. Document applicability to actual `insert_tail`: normal true path, false early
   return and first direct panic must have explicit full storage/ownership
   recovery routes. A natural-block fixture alone is insufficient. Close this
   phase with a go/no-go report; do not implement a new AST scope/routing feature.

Allowed tool profiles in this phase: unchanged pinned release 26.09
(`verifast_borrow_recovery`), and the EXISTING `manually_drop_only` profile
(`verifast_borrow_recovery_manually_drop`), with no patch expansion:

- VeriFast source `809de4596839b739dd999f9e462242c835e3af46`;
  Rust `nightly-2026-02-05`.
- Sole patch `verifast-manually-drop-ref.patch`, SHA-256
  `5500204aadd0ea0a2996d63d064160185457b6d337782aa4300c11272ab450cc`.
- Translator input SHA-256
  `7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803`;
  output `60ece6e90f4dd3c623a99ea31feebb3210359daa38850255332118b2316eac39`.
- Parser, kernel, prelude, memory model, exporter and refinement checker remain
  unchanged. Retain existing dependency/binary/source audits. The full historical
  patch chain is evidence, NOT a default fallback or phase permission.

## Architecture decision before expansion

The baseline fixture's natural block is absent around actual insert_tail's first
FnMut call; its first panic occurs before a guard exists. Direct unwind skips
trailing recovery statements. A proof-only translator AST block/label rewrite is
only a design candidate: unimplemented, unproved and NOT authorized here, even
if kernel-free. See [borrow design](BORROW-RECOVERY-DESIGN.md) and
[all-path ledger](INSERTION-RESOURCE-LEDGER.md).

Before further integration, justify source-exact normal/false/panic recovery and
the trust/admissibility of every semantic change. Then seek the owner's decision
on that route or a simpler target. Later roadmap: held tmp/guard provenance and
late panic → full generic insert_tail → actual outer loop → other safety targets,
specializations and three sorting contracts. Required UB checks and automation
remain separate completion gates. Do not silently advance into these later phases.
