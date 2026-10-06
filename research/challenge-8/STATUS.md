# Challenge 8: current status

Updated 2026-10-06 from stopped checkpoint
`126e23d35c26bb336ca5e975f0ec696ef1fa88d0` on `challenge-8/research`.
This is the single current checkpoint; procedures live in
[AGENT-RUNBOOK.md](AGENT-RUNBOOK.md), historical evidence in
[EXPERIMENT-LOG.md](EXPERIMENT-LOG.md).

## Authorization and stop state

**PAUSED by the owner's explicit request. No active research run at this review.**
Only instruction/documentation changes are authorized now. They do not resume
proof work, apply the draft, authorize verifier changes or dispatch a workflow.
A future agent must inspect live branch/run state without interpreting activity
or an old "resumed" note as permission. Resume requires an explicit owner request.

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

## Last experiment and preserved draft

Latest run: [37441463201](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37441463201),
source `d198907e7eec57f8bcd880304fa1345b97b0ef53`,
`verifast_borrow_recovery_manually_drop`, 90-minute budget; completed/failure.

- Minimal `manually_drop_only` profile builds; all seven exports/decodes and
  source/ghost-strip audits pass.
- All seven verifier cases stop in the common new `recover_single` helper:
  missing `[first_fraction]ref_initialized<T>(tmp_ref)` at its first close.
  No caller is reached; neither new positives nor intended negatives pass.
- The ManuallyDrop positive separately fails refinement: `RawPtr: not yet supported`
  for `addr_of!(tmp)`; six other refinements pass. An identical operation dump
  does not substitute for a successful refinement check.
- Existing `recover_pair` still checks. The unchanged release profile excludes
  the new helper and retains its five controls; the prior baseline success is
  not invalidated by the experimental profile's common-helper failure.

[DRAFT-MD-RECOVERY-2026-10-06.patch](DRAFT-MD-RECOVERY-2026-10-06.patch) is preserved,
UNAPPLIED and UNVERIFIED. Its fractional split/coefficient constraints need
review; saving a shared-reference-derived raw pointer may not convey the full
permission recovered at the original tmp location. Source-line/MIR audits are
unfinished. Do not apply/dispatch it wholesale or treat it as a prepared fix.

## Prepared phase after explicit resumption — limited feasibility gate

This is the next bounded phase, NOT permission to start while paused.
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
