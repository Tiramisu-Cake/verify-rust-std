# Challenge 8 research

Our own specifications and proofs for the actual Rust SmallSort implementation.
Other solutions may inform requirements/review concerns, but their proof code is
not imported. Runtime algorithms and generic signatures must remain unchanged.

## Start here

**The bounded actual `sort4_stable` phase is approved and ready to start.**
The [approved roadmap](PLAN.md) records the revised priorities, and
[SORT4-PHASE.md](SORT4-PHASE.md) defines the executable scope. No sort4 proof run
has been made at this approval checkpoint. The previous ManuallyDrop/insert_tail
phase remains closed. [STATUS.md](STATUS.md) is the single current checkpoint.

1. [Root agent instructions](../../AGENTS.md).
2. [Current status](STATUS.md), [roadmap](PLAN.md), [phase](SORT4-PHASE.md)
   and [operating runbook](AGENT-RUNBOOK.md).
3. [Coverage ledger](coverage.md), [Challenge 8](../../doc/src/challenges/0008-smallsort.md)
   and [general rules](../../doc/src/general-rules.md).
4. The relevant design/proof note and actual source before implementation.

The owner's server is for editing/orchestration only. All compilation,
verification and executable tests run on GitHub-hosted Actions. See STATUS for
both completed hosted runs and their evidence boundaries.

## Specifications and proof boundaries

- [Bounded insertion contract](insertion-contract.md): i32, lengths 1..4;
  verified adapter, research composition and separate direct outer proof.
- [All-path insertion resource ledger](INSERTION-RESOURCE-LEDGER.md): full
  normal/unwind target, ownership, actual MIR cleanup and trust boundaries.
- [Prepared-phase feasibility report](PREPARED-PHASE-2026-10-06.md): checked
  same-reference helper, unresolved immutable tmp storage/provenance/refinement
  and exact first-false/first-panic routes.
- [Borrow recovery design](BORROW-RECOVERY-DESIGN.md) and
  [baseline/minimal-profile fixture](verifast-borrow-recovery.md): normal
  baseline success versus unresolved source applicability and panic recovery.
- [Actual Drop body](verifast-drop-gate.md) and
  [local cleanup callers](verifast-local-drop-call.md): conditional results on
  experimental patched tools, not completed generic insertion.
- [UB checks](ub-checks.md) and [outer invariant diagnostic](outer-invariant-diagnostic.md):
  measured limitations, not a complete safety proof.
- [Upstream candidates](VERIFAST-UPSTREAM-CANDIDATES.md): technical ideas only;
  no external publication or new semantic extension is authorized by that note.

## External verification research

The [C verification survey](C-VERIFICATION-SURVEY.md) records the 2026-10-06
comparison of all seven targets with C proof developments, transfer candidates
and Rust-specific limits. The [artifact catalog](C-VERIFICATION-ARTIFACTS.md)
pins source files, contracts, published results, papers and relevant tool
references. [Sorting-model observations](SORTING-MODEL-OBSERVATIONS.md) preserve
the earlier finite-enumeration report and a reconstruction specification, with
its missing run provenance made explicit.

These are reference materials, not new proof evidence. Their implications for
the next steps are now recorded in the separately approved [roadmap](PLAN.md).
Use STATUS and the linked phase for current authorization.

## Run log

[EXPERIMENT-LOG.md](EXPERIMENT-LOG.md) preserves the former README, all run
evidence and future experiment cards/results. The former operational log is
preserved in [AGENT-RUNBOOK-ARCHIVE-2026-10-06.md](AGENT-RUNBOOK-ARCHIVE-2026-10-06.md).

[HANDOFF-2026-10-06.md](HANDOFF-2026-10-06.md) and
[REASSESSMENT-2026-10-06.md](REASSESSMENT-2026-10-06.md) are historical snapshots.
Their old "resumed", "next" and "pending" statements do not override STATUS.
Use the runbook for exact-SHA dispatch/inspection within the currently approved
phase; historical proposed experiments do not expand that scope.
