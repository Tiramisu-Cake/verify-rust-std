# Challenge 8 research

Our own specifications and proofs for the actual Rust SmallSort implementation.
Other solutions may inform requirements/review concerns, but their proof code is
not imported. Runtime algorithms and generic signatures must remain unchanged.

## Start here

**Bounded no-patch H_align proof/reclassification phase IN PROGRESS.**
[Current card](SORT4-ALIGNMENT-PHASE.md) authorizes <=3 NEW hosted manual jobs,
summed setup/job time<=90min. Classifier replay uses both original artifacts and
separate derived outputs. Generic local bound proofs preserve the outer contract;
original ZST layout model is traced without assumptions/patches/type replacement.
Historical results below remain preserved; only this narrow continuation authorized.

**H_align syntax-only continuation CLOSED / INCONCLUSIVE,1/1 used.**
[Run37532204465/source9474453 closeout](SORT4-ALIGNMENT-RESULTS.md): syntax parsed,
export/decode/refinement6/6; generic nonnegativity, ZST size/layout and pointer
limits remain unproved. Both negatives reject their intended assertion manually;
raw automatic all-six INCONCLUSIVE due missed source-prefixed headers. No active
run or further proof correction/dispatch authority. Original37529855468 remains
historical INCONCLUSIVE. No geometry/layout/automatic-UB coverage; RAPx NO-GO,
B/C NOT RUN. [Closed scope](SORT4-ALIGNMENT-PHASE.md).

**Joint proof-route assessment complete; no generic composition yet.**
[RAPx / VeriFast / Kani matrix and compatibility analysis](SORT4-COMPOSITION-ASSESSMENT.md)
assign exact obligations without a single-tool requirement. RAPx presently
contributes diagnostics; any selected future fact needs independent qualification.
ZST remains in scope with A NO-GO and B/C NOT RUN. One independent no-patch VF
alignment geometry gate was proposed there; its separate phase and syntax-only continuation closed INCONCLUSIVE
without a completed positive proof. Arithmetic success alone would not establish automatic operation
coverage or full sort4 safety.

**Explicit sort4 research contract adopted; C-source authority checked.**
The [adopted domain](SORT4-CONTRACT.md#adopted-domain-and-caller-obligations)
states full source/output separation and the effect-aware scratch/resource
protocol, with caller-precondition proofs required for composition. The
[authority assessment](C-VERIFICATION-ARTIFACTS.md#authority-and-separation-precedents)
supports this specification choice; it supplies no new Rust proof or committee
acceptance. Organizer clarification is deferred and no longer blocks planning.
The [earlier review and unsent question](SORT4-ADMISSIBILITY-REVIEW.md) remain
historical. No further experiment or external contact is currently authorized.

**CLOSED / NO-GO: RAPx gate A reproduces a ZST alignment detector miss.**
Two of four new hosted runs used under the [bounded continuation](RAPX-APPLICABILITY-PHASE.md#current-gate-a-continuation).
All six controls were analyzed; both misaligned alignment-eight ZST copies get
SOUND/Align ProvedByRule. Original manual contracts/diagnostics/MIR evidence
is now reproduced by the separately authorized saved-data replay37513897141,
processor1c0b517. All six authentic pairs parse and nine mutation/replay test
groups pass; two valid controls, two SOUND_MISS and two intended Align failures
with other Failed/Unknown retained. The original unmapped JSONs remain historical.
The prior two setup failures remain historical INCONCLUSIVE in
[results](RAPX-APPLICABILITY-RESULTS.md). Pins/std/contracts unchanged; B/C
NOT RUN, no generic proof gain. Current checkpoint: [STATUS](STATUS.md).

The closed [no-patch assessment](SORT4-NO-PATCH-ASSESSMENT.md) preserves the
official VeriFast26.09/26.10 and Kani review; it found no new full-resource
first-callback candidate and ran no experiment. Earlier phases remain closed.
[Contract closeout](SORT4-CONTRACT-RESULTS.md) and
[functional closeout](SORT4-RESULTS.md) preserve earlier results.
[STATUS.md](STATUS.md) is the current checkpoint; [PLAN.md](PLAN.md) the roadmap.

1. [Root agent instructions](../../AGENTS.md).
2. [Current status](STATUS.md), [roadmap](PLAN.md),
   [adopted contract](SORT4-CONTRACT.md),
   [admissibility analysis](SORT4-ADMISSIBILITY-REVIEW.md),
   [closed RAPx phase](RAPX-APPLICABILITY-PHASE.md)
   and [operating runbook](AGENT-RUNBOOK.md).
3. [Coverage ledger](coverage.md), [Challenge 8](../../doc/src/challenges/0008-smallsort.md)
   and [general rules](../../doc/src/general-rules.md).
4. The relevant design/proof note and actual source before implementation.

The owner's server is for editing/orchestration only. All compilation,
verification and executable tests run on GitHub-hosted Actions. See STATUS for
both completed hosted runs and their evidence boundaries.

## Specifications and proof boundaries

- [Independent alignment phase](SORT4-ALIGNMENT-PHASE.md): one-run no-patch
  H_align scope, full-target versus partial fixture domain/posts, intended controls
  and automatic-operation/model boundary; CLOSED at1/1 runs.
- [Independent alignment results](SORT4-ALIGNMENT-RESULTS.md): six fixture parse
  failures, export/refinement evidence, no proof gain, initial syntax
  failure, corrected-run blockers and manual versus automatic control evidence.
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
