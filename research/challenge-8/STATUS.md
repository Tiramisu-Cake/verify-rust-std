# Challenge 8: current checkpoint

2026-10-08. **STOCK-26.10-BASELINE CLOSED**: independent stock chain operational;
exact generic forget **INCONCLUSIVE at mandatory dead-code gate**. No active run
or semantic draft. [Phase report / BEFORE / transfer map](STOCK-26.10-BASELINE.md).
Own branch `research/stock-26.10-baseline`, from sync/research a06cfb9d,
std/upstream `cd371e035c7e573760c43bf934d53e8118ee3e7d`.

Stock26.10 VF source `f76012fb518703b1d98e243ac4f487f16877cfcb`,
nightly2026-09-25/rustc f7575a9da; effective patches NONE.
[Proof run37694000195](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694000195),
SHA `a0cfd30e066acbaf1b5406cd9773f54388cc45be`: all11 export pairs/22decodes/
11refinement PASS;4whole-unit positives (u32/raw/ordinary unwind/shared cleanup),
4intended false-post negatives,2separate intended contradictory-pre dead-code
controls. Forget executes normal return/leak then sole3:1–16:2 dead code.
New MIR4locals/3blocks and AST show orphan label2 unwind return after stock MD
identity+normalGoto; physical residual key/object remains UNKNOWN, not old52.
Run37693718508/SHA4baed189 is37s setup failure, not a proof.

Actual source audit: MD/MaybeUninit/SmallSort match nightly rust-src; mem/ptr
full-file hashes differ due repository annotations/cfg additions/docs, relevant
forget/drop bodies unchanged. This is an adapter/sysroot baseline, not repository
std build or safe generic-forget theorem. S6 source-linked matrices NOT_RUN on26.10;
source map explains constructor/asptr/intrinsics/new drop_glue transfer gates.
Refiner unwind TODOs and stock MD correspondence remain explicit trust limits.

Separate phase account **99/1800 hosted jobseconds used,1701remaining**
(37setup+62full baseline/artifacts). Old account **5306/5400,94remaining** untouched;
old S7c **UNACCEPTED** and its5missing admission controls remain unchanged.
Documentation closeout HEAD is later than proof SHA; no verification on docs.
No actual redirect/guard/assume_init/memory-unwind/tool semantic changes.
Original branches/main fixed; no upstream PR/messages/submission.

Next decision: separately authorize narrowly scoped CFG26.10 physical-loc
**diagnosis** before semantic transfer/trust review; no identical semantic rerun.
Plan only, not authorization for overlays or broader FnCallResult/model changes.

---

## Preserved previous checkpoint (historical authorization)

# Challenge 8: upstream synchronization checkpoint

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

# Challenge 8: current checkpoint

Updated2026-10-08 (experiment timestamps are UTC2026-10-07). **S7c iteration STOP; experimental CFG profile NOT ACCEPTED.**
Owner authorization from070b9236 was limited to MD::new CFG/standalone body;
actual linkage/redirect remains NOT RUN. No active run or semantic draft.
[Results](SORT4-SELECT-FORGET-RESULTS.md), [design/BEFORE cards](SORT4-SELECT-FORGET-DESIGN.md),
[runbook](AGENT-RUNBOOK.md), [roadmap](PLAN.md).

Physical-loc diagnosis[37681688627](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37681688627),
checked32d909a7b1015a9417b882676d349bab5c80481f: residualid52 is orphan label2
ReturnStmt(unwinding), registered1/executed0/residual1. Normalid53 executes.
Old plain and instrumented S6v4 fullVF1 solely dead-code; exact source/MIR/AST match.

Narrow separate overlay89b0d80b over unchangedS6v4c7cc08a9 changes only existing
MD::new identity lowering successors for FnCallResult+normalGoto. Acceptance build
has no trace; kernel/dead-code/exporter/refiner/spec/runtime unchanged.
[Acceptance37683136287](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37683136287),
checked7185d8bae4a25fa2be278424fa9f5c6a80b93956: exact autonomous generic unit
fullVF0, all7bodies/return/leak, dead-code gate completes. All other5stages0,
sourcepair and both completeMIR unchanged, exportedcleanup2 retained.
Constructor16+9MIR+14baselines, asptr9+17admission, intrinsics16+40admission PASS.
Pointerdrop2positive+11proofnegative and8source+9MIRadmission PASS before timeout.

[Focused37684590509](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37684590509),
checked6b63670c21bfa57d2531c4be57ac098df6111c5f: autonomous VF0 repeated;
ordinary potentially-panicking call normal+unwind verified, sharedcleanup3 retained
and executed from another real predecessor. False normalpost9:27–32, false
unwindpost23:15–20 and contradictory-precondition dead-code failures are intended.
Earlier parse failures37683136287 do not count as negative controls.
[Immutable replay37685560355](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37685560355),
processor7eea51399d570b0eba895605c5d05d0de9cf3ed1: preserves original aggregate
INCONCLUSIVE bytes; new separate map confirms intended false-unwind rejection.
Six classifier controls PASS; no new proof or verifier run in replay.

**Mandatory unverified tail:** pointer-drop `mir_cfg_unwind` (partial timeout),
`mir_extra_operation`, `mir_contract`, `method_source_pin`, `glue_source_pin`.
Profile remains UNACCEPTED; autonomous positive is conditional on this experimental
profile, not accepted actual-forget summary or safe generic-forget theorem.
ManuallyDrop representation/destructor/no-unwind correspondence remains TRUSTED.

**Budget5306/5400 summed hosted job seconds used;94remain**, no reset:
entry4752+diagnosis132+acceptance283+focused131+replay8. No further dispatch:
a full rebuild, missing tail and artifacts have no established bound within94s.
All executable checks hosted, one active direction at a time. Final documentation
HEAD is not a proof SHA; source inventory/results retain all prior evidence.

Actual remains lastS6v4 at forget63/stdspec420 missing nominal guard-own;
full helper/sort4 NOT PROVEN. No guard/Drop/assume_init/memory/exporter/refiner/kernel
expansion. Broad FnCallResult repair is only a separate future proposal.
Owner supplement authorizes only source comparison/transfer plan for upstream
cd371e03 and VF26.10f76012fb; [assessment](VERIFAST-26.10-MIGRATION.md).
No rebase/merge/profile switch or migration CI; old proofs/budget retain old pins.

S6v4 component acceptance remains run37656621026/proofsource
75681fbc57bda633f59096cdc28f0c1aa61daef8, patchc7cc08a9. Historical S7b
failures/replay/AST evidence and prior budgets remain in [RESULTS](SORT4-SELECT-FORGET-RESULTS.md)
and [EXPERIMENT-LOG](EXPERIMENT-LOG.md); they are not reclassified as new positives.
S5j RawPtr/normal preprocessing limitations retained; RAPx CLOSED/NO-GO, B/C NOTRUN.
No upstream PR, external messages or submission. Next permitted work is source-only
migration review; further proof experiments/tool expansion require a separate decision.
