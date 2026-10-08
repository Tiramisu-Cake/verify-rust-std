## Текущий результат STOCK-26.10-BASELINE — 2026-10-08

## Current owner authorization: OVERNIGHT-SELECT-SORT4-26.10

2026-10-08 CI window EXPIRED at09:30MSK/06:30UTC;3094/21600 hosted
jobseconds used throughO17. Analysis/preparation authorized; new CI extension pending. [Phase](OVERNIGHT-SELECT-SORT4-26.10.md) supersedes historical stage
stops: CFG26.10 → S6 transfer → actual helper → actual sort4 → profile reduction/
dependent components. Semantic changes authorized after written rationale/trust/gates
and self-review; no owner wait between these stages. Runtime/check integrity preserved.
[STATUS](STATUS.md) remains the current compact checkpoint. Old budgets and results
below are historical and do not constrain this authorized phase.

## Historical roadmap and phase checkpoints (preserved)


Владелец отдельно возобновил stock26.10 phase с новым бюджетом1800s.
[Отчёт / новая карта переноса](STOCK-26.10-BASELINE.md): proofa0cfd30e,
run37694000195, stock chain PASS на независимых u32/raw/unwind controls;
exact generic forget INCONCLUSIVE на dead-code gate, физический ключ UNKNOWN.
Фаза CLOSED,99/1800used(1701remaining), old5306/5400(94) untouched/S7c UNACCEPTED.
Ни один semantic patch не переносился; следующие scoped diagnosis/transfer gates
требуют отдельного решения. Исторические ограничения/оценки ниже сохранены.

## Переходный checkpoint — Git sync, повторная приёмка НЕ ВЫПОЛНЕНА

2026-10-08. В этой ветке напрямую влит закреплённый upstream cd371e03.
[UPSTREAM-SYNC](UPSTREAM-SYNC.md) фиксирует parents/SHA, исходниковые изменения,
бюджеты и два следующих задания. CI budget этой фазы0; исследования отложены.
Старые принятые результаты ниже относятся только к прежним proof SHA/tool profiles.
Новым std/nightly/VF необходима повторная проверка. S7c UNACCEPTED (пять admission
контролей незавершены); G2/A/B и девять Rust projections сохраняют прежние условные
границы в исходных ветках. Бюджеты5306/5400(94) и512/1800(1288) не сброшены.
Git merge не доказывает actual helper/merge/Challenge. Подготовленные задания
НЕ разрешают их выполнение в этой CI0-фазе.

# Challenge 8 research

Our own specifications and proofs for the actual Rust SmallSort implementation.
Other solutions may inform requirements/review concerns, but their proof code is
not imported. Runtime algorithms and generic signatures must remain unchanged.

## Start here

Current S7c: the exact autonomous generic body passes full verifier exit0 on
`experimental-manuallydrop-new-cfg-v1`; **the profile is NOT ACCEPTED** because
five pointer-drop admission controls remain unverified. Physical residual loc52
is established as the orphan cleanup return. Ordinary unwind and genuine shared
cleanup, false normal/unwind posts and contradictory-precondition dead-code gates
are checked. Actual linkage/redirect NOT RUN; full helper/sort4 NOT PROVEN.
[Results and exact proof SHAs](SORT4-SELECT-FORGET-RESULTS.md),
[design](SORT4-SELECT-FORGET-DESIGN.md), [checkpoint](STATUS.md).
Budget5306/5400 summed hosted job seconds used;94remain/noreset/noactive.
Iteration STOP at incomplete acceptance; no more dispatch. Migration26.10 is
source analysis/plan only, with no rebase, profile switch or migration CI.
[Migration assessment](VERIFAST-26.10-MIGRATION.md).

Historical S7b: **auxiliary generic body NOT ACCEPTED; actual linkage NOT ACCEPTED;
no S7 actual advancement.** [Report](SORT4-SELECT-FORGET-RESULTS.md),
[design/trust](SORT4-SELECT-FORGET-DESIGN.md), [current checkpoint](STATUS.md).
Standalone run37675513854/source `c9c59a85807da0135a8192b1912b15d510c68028`
checks the whole minimal generic unit without focus/select/macros/guard. All seven
predeclared functions execute, return and leak-check; full verifier exits1 with
sole adapter-span dead-code diagnostic. NORMAL/readonly/decode/refinement exit0;
source hashes PASS. Existing ManuallyDrop correspondence remains TRUSTED.
Separate immutable replay37676357686/processor
`dd4b0493b8411d92f61f525a3c7ef6ec0429d021` preserves all nine original classes;
new separate map has two INCONCLUSIVE positives and seven intended negatives.
Dead-code exit1 never becomes PASS. Full S7 thread/cell/frame/borrow/admission/
mutation controls and new-profile regressions remain NOT RUN; no actual redirect.
S6v4 remains accepted. Last actual run37656621026 still stops at forget63,
std/lib.rsspec420 requiring absent nominal guard-own; assume_init is not reached.
Full helper/sort4 NOT PROVEN. Latest [AST diagnostic37678089113](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113),
source `a6f077a5aa89ad25df94295320cdbe18ebe4b9d9`, confirms an orphan translated
cleanup return; full VF remains exit1, with source/MIR/tool identity retained.
STOP at frozen translation/dead-code acceptance; no pruning/exemptions/model change.
Physical loc-key attribution remains an explicit diagnostic limit in the report.
Budget **4752/5400 summed hosted job seconds used; 648 remain**, no reset/no active
run. Historical budgets and instructions below do not reopen phases.

Historical S6 closeout: **COMPONENT_ACCEPTED (v4); actual integration STOPPED at forget guard-own.**
[Fresh run37656621026](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026), proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, profile
`experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Constructor/as_mut_ptr/typed intrinsics/narrow pointer drop matrices and14baselines
PASS freshly; S6 has2positive+11proofnegative+22source/MIR/pin negatives, all on
intended obligations. All19 independent NORMAL controls reject exactly beforeproof,
including oldreceiver26→23. Full source/typed method+actual MIR/runtime/normal-unwind
CFG correspondence preserved; diagnostic37649244205 is not a proof. Five extra
stock ghost locals/blocks and every annotation coordinate are in the design table.

Actual baseline still lacks initialized payloadcell. Stock-projected actual enters
proof after full36/19 admission and checkedmethod redirect. Both stock opens, proof
condition split, retained runtime drop at verified/lib.rs60 and both closes61/62
pass in the recorded prefix. Next blocker: verified/lib.rs63 `mem::forget(guard)`,
frozen std/lib.rsspec420:41–42 requires nominal
`<DropOnPanic<*const Element>>.own(t, guard)`, absent. No guard/forget extension;
STOP at this exact obligation. Current classifier stays INCONCLUSIVE with heuristic
kind intrinsic_select; rawlog establishes the forget guard-own failure separately.
Finalreturn/leak/fullnormal-unwind posts not reached; wholehelper/sort4 NOT PROVEN.

Checked method and ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence and frozen stock frontend ghost substitution.
Existing initializedcell/fullpointervalue/thread/independentframes required, no
Element rights. Recursive free stub is not a runtime-body theorem. Runtime std,
signatures/targetcontract unchanged; broader04d67f4b/Drop/guard/forget/assume_init/
union/refiner/kernel/memory/alias/provenance stay frozen. Further semantic work
requires a separate owner decision; no additional dispatch authorized at this stop.
Budget **3954/5400 summed hosted jobseconds used;1446remain**, same budget/noreset,
noactive. Last two proof orchestration jobs:37654585346=184s,37656621026=202s.

The following pointer-ownership closeout is historical.

**Previous: [pointer ownership phase](SORT4-POINTER-OWNERSHIP-PHASE.md), CLOSED.**
[Final report](SORT4-POINTER-OWNERSHIP-RESULTS.md): O4/37601511894 at proofSHA182ddf29
accepts experimental defined pointer-value ownership and SAFE MaybeUninit::new,
full source/HIR/MIR criterion and intended controls. [Actual select](SORT4-SELECT-CALLEE.md)
RUN/INCONCLUSIVE: both constructor calls pass; first blocker as_mut_ptr at adapter38.
518/5400jobseconds,4NEWruns,noactive;remaining4882s retired. No broader storage/
borrow/union/copy/FnMut/Drop/unwind model; full Rust sort4 NOT PROVEN.
[STATUS](STATUS.md) is authoritative; [PLAN](PLAN.md) and
[runbook](AGENT-RUNBOOK.md) define execution boundaries. Next capability requires
a new phase decision. RAPx CLOSED/NO-GO; B/C NOT RUN.

Previous [composition/constructor phase](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md)
is historical CLOSED: C1/C2 pure SWO composition and C3 full exact fieldless layout
matrix accepted; C8 translator-only constructor stopped before body on opaque
ownership. The new separately pinned profile supersedes that constructor boundary,
without combining patches. [Night report](SORT4-NIGHT-RESULTS.md) preserves stock
index/rank/SWO/range components and earlier layout evidence. No generic Copy bound.
Entries below describe historical phases.

**Historical CLOSED at6/6 NEW runs: stock generic H_align PASS; experimental layout acceptance INCONCLUSIVE.**
[Stock run37540829027/source968c073](SORT4-ALIGNMENT-RESULTS.md#stock-generic-baseline-and-experimental-fieldless-layout--2026-10-07)
proves const/mut independently on unchanged VeriFast26.09 with all old gates.
[Final run37544574703/sourcee472aa2](SORT4-ALIGNMENT-RESULTS.md#fieldless-layout-prototype-closeout)
builds the separate fieldless Rust layout profile and verifies Z0/8, const/mutadd,
generic calls Z/u64 and intended false assertions. Full acceptance remains
INCONCLUSIVE: metadata absent/span evidence-processing gates and new C/C++ annotation
parse errors; existing regressions pass both profiles. Budget653s jobs including
build/setup, no active run, STOP at6/6. [Patch/provenance](verifast-rust-fieldless-layout.md),
[current checkpoint](STATUS.md), [history](STATUS-HISTORY-2026-10-07.md).
No full model/automatic-copy UB/whole-sort4 theorem. RAPx CLOSED/NO-GO; B/C NOT RUN.
Next narrowly proposed harness/annotation check is NOT AUTHORIZED / NOT RUN.
Prior phases below remain historical.

**Historical generic completion/layout review CLOSED at2-run limit; generic INCONCLUSIVE.**
[Runs37537448952/37537868053](SORT4-ALIGNMENT-RESULTS.md#generic-completion-and-layout-review--two-new-runs),
2/2 NEW,85s total jobs/setup. Checked order splits derive i==0 and original residual
posts; impossible guard assertions fail the unchanged dead-code gate. No accepted
generic whole-unit proof or classifier/check change. Prior raw evidence preserved.
[Layout review](SORT4-ALIGNMENT-MODEL-BOUNDARY.md#follow-up-layout-model-review-documentation-only-2026-10-07)
confirms upstream26.10/master boundary and recommends limited compiler-backed Rust
struct layout facts with a Rust-only nonnegative bound; exact generic ADTs remain
separate scope. Kani concrete Z candidate is calibration, no proven all-types bridge.
Future regression design NOT RUN; no tool patch, further proof run or publication.
RAPx CLOSED / NO-GO; B/C NOT RUN; ZST retained in adopted contract. No active run.

**Historical bounded no-patch H_align continuation CLOSED at a concrete ZST model boundary.**
[Run37535499783/sourceea635ea](SORT4-ALIGNMENT-RESULTS.md),1/3 NEW runs,38s summed
jobs/setup: classifier historical replay3 groups/30 mutants and intended negatives
PASS. Generic helper/local bounds and i=1,2,3 branches pass; residual alignment post
keeps whole geometry INCONCLUSIVE. Original ZST layout/add remains unproved;
[pinned model trace](SORT4-ALIGNMENT-MODEL-BOUNDARY.md) identifies incompatible
positive struct size and missing repr alignment. No patch/axiom/domain change.
Historical raw evidence remains unchanged. STOP, no active run; unused slots retired.
No automatic-copy UB/full-sort4 proof; RAPx NO-GO, B/C NOT RUN.

**Historical H_align syntax-only continuation CLOSED / INCONCLUSIVE,1/1 used.**
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
historical. That historical phase authorized no further experiment or external contact.

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
