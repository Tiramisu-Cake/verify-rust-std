# Challenge 8 research

Our own specifications and proofs for the actual Rust SmallSort implementation.
Other solutions may inform requirements/review concerns, but their proof code is
not imported. Runtime algorithms and generic signatures must remain unchanged.

## Start here

Read [WORK-POLICY](WORK-POLICY.md), the branch-local [STATUS](STATUS.md),
[AGENT-RUNBOOK](AGENT-RUNBOOK.md), [Cloud procedure](cloud-build/README.md)
and [COMPLETION-PLAN](COMPLETION-PLAN.md). Latest select checkpoint:
[caller bridge](cloud-build/sort4-c1-caller-bridge/END-CHECKPOINT-2026-10-09.md).
Prior operating text and status are retained in the
[branch archive](archive/select-adoption-2026-10-10/README.md); dated research
results below are evidence within their original identities, not authorization.

## Specifications and proof boundaries

- [Independent alignment phase](SORT4-ALIGNMENT-PHASE.md): one-run no-patch
  H_align scope, full-target versus partial fixture domain/posts, intended controls
  and automatic-operation/model boundary; all scopes closed, latest2/2 at run limit.
- [Independent alignment results](SORT4-ALIGNMENT-RESULTS.md): six fixture parse
  failures, export/refinement evidence, no proof gain, initial syntax
  failure, corrected-run blockers, checked residual-post progress/dead-code failure
  and separate replay evidence.
- [Concrete ZST model boundary](SORT4-ALIGNMENT-MODEL-BOUNDARY.md): pinned exporter,
  schema, translator and engine trace; necessary faithful layout correction versus
  independent generic arithmetic, upstream/release review, minimum compiler-backed
  implementation scope and future acceptance matrix (no patch implementation).
- [Joint sort4 composition assessment](SORT4-COMPOSITION-ASSESSMENT.md): exact
  obligation/tool/evidence/gap/dependency matrix; common source/domain/premises,
  acyclic responsibilities, restricted RAPx role, independent ZST route, necessary
  versus optional VF capabilities and one proposed bounded alignment gate.
- [Sort4 admissibility review](SORT4-ADMISSIBILITY-REVIEW.md): assumption ledger,
  local copy safety vs sufficient separation/preservation, raw scratch/ownership,
  legal comparator effects and five panic posts; official clarification limits,
  historical runner interface limitation, superseded inquiry recommendation and
  deferred unsent question. The later owner decision adopts the explicit domain.
- [RAPx applicability results](RAPX-APPLICABILITY-RESULTS.md): NO-GO for pinned
  ZST alignment detection, six actual controls and corrected automatic replay,
  processor/source/artifact identities, preserved manual/JSON history and stop.
- [RAPx applicability phase](RAPX-APPLICABILITY-PHASE.md): approved bounded
  diagnostics, exact profile, ordered gates, run budget and mandatory stop;
  no full sort4 proof or tool patch authorized.
- [Remaining-tools assessment](ALTERNATIVE-TOOLS-ASSESSMENT.md): immutable
  integration/source references, comparison, observed/inferred/unknown
  distinctions, ZST alignment and callback/panic coverage concerns.
- [No-patch phase](SORT4-NO-PATCH-PHASE.md) and
  [assessment](SORT4-NO-PATCH-ASSESSMENT.md): completed source/evidence comparison,
  no experiment, no generic coverage gain; its historical contract-review
  recommendation led to the analysis and subsequent domain adoption above.
- [Completed contract phase](SORT4-CONTRACT-PHASE.md): coincident/shifted-overlap
  diagnostics, precise contract and one proposed generic proof route; see
  [observed results](SORT4-CONTRACT-RESULTS.md). Verifier implementation remains
  a separate owner decision.
- [Sort4 contract and callers](SORT4-CONTRACT.md): adopted research memory/aliasing,
  single-ownership, comparator effects and all five panic sites, separated from
  the four-cell functional domain in [the actual-body harnesses](sort4.rs) and
  [overlap diagnostics](sort4-contract-diagnostics.rs).
- [Sort4 phase result](SORT4-RESULTS.md): exact i32 multiset and separate tagged
  stability proofs,18/18 covers; [generic-safety assessment](SORT4-SAFETY-DECISION.md)
  and next architecture question; no new verifier semantics implemented.
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
references, and distinguishes their scholarly/institutional/tool-artifact
authority. [Sorting-model observations](SORTING-MODEL-OBSERVATIONS.md) preserve
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
