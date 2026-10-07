# Current phase: MERGE-STOCK-26.10

Owner resumed on2026-10-08. [Phase contract](STOCK-26.10-PHASE.md),
[current checkpoint](STATUS.md). Historical sections below remain closed;
new stock rechecks do not reopen integration or tool changes.

## Переходный checkpoint — Git sync, повторная приёмка НЕ ВЫПОЛНЕНА

2026-10-08. В этой ветке напрямую влит закреплённый upstream cd371e03.
[UPSTREAM-SYNC](../UPSTREAM-SYNC.md) фиксирует parents/SHA, исходниковые изменения,
бюджеты и два следующих задания. CI budget этой фазы0; исследования отложены.
Старые принятые результаты ниже относятся только к прежним proof SHA/tool profiles.
Новым std/nightly/VF необходима повторная проверка. S7c UNACCEPTED (пять admission
контролей незавершены); G2/A/B и девять Rust projections сохраняют прежние условные
границы в исходных ветках. Бюджеты5306/5400(94) и512/1800(1288) не сброшены.
Git merge не доказывает actual helper/merge/Challenge. Подготовленные задания
НЕ разрешают их выполнение в этой CI0-фазе.

# Current checkpoint: supported stock Rust components accepted; wrapping STOP

Owner continuation from documentation HEAD
`7d27ce106d27208bcd1156fe5675f70f8f9bf1aa` accepts completed G2/A/B.
New stage follows [POINTER-DESIGN](POINTER-DESIGN.md), including caller audit,
nonzero-size component, exact operator support, meaningful controls and preserved
export/decode/refinement/full verifier gates. Entry budget330/1800,1470 remain;
final512/1800 used1288remain (P1111+P236+P335), no reset/transfer.
Audit is completed before dispatch. No ZST exclusion in Challenge contracts,
no tool semantic changes, memory/copy/FnMut/unwind expansion or network work.
Own branch only; one hosted run at a time. Unsupported wrapping -> stop that
composition; independently supported components can complete. Mathematical
proof bodies, premises, source/proof SHAs and historical results below unchanged.

P3/run37686627140/proof1c318453efa4e3a774b2edd791a5298d76132eb0 accepts
nine supported Rust projections and two intended negatives, all128 classifier
controls. Exact pointer wrapping_add/sub has no stock function (P2), so the
next terminal wrapping/index/provenance composition is STOPPED. All ordinary
operator/local G2/order/guard targets of this bounded projection stage complete;
no new run is needed for documentation. New wrapping semantics/specs/tool
profile would need a separate decision and are outside this authorization.
FnMut/memory/copy/ownership/unwind/whole-source refinement remain separate OPEN
obligations, not scheduled next steps. No active run; excluded wrapping draft
corrections NOT RUN. [Final results](RESULTS.md).

# Completed functional stage: goals and acceptance

Owner continuation from067fb584018760259841210d2cc6c227117798ce, SAME1800jobsecond
merge budget25spent/1775remaining, no reset or networktransfer. Stock unchanged
VF26.09 and existing strict classifier. Original acceptedgeometryplan follows.

A. Model exact output occurrence IDs0..n-1 from current source cursor before
its movement; each pairwrites upwardat k then downwardat n-1-k, and odd
residualat m. AllcomparisonBooleanpairs and residualchoices arbitrary. For every
n>=2, assumeONLY final scalar-index equalities; prove destinationcoverage/no
repeatwrites/outputlengthn and exact arbitrary-q multiplicity equal original
IDs. Build structural induction/invariant, no bounded inputenumeration/SWO.
Export full reusable theorem posts; identify existingG2calls before use.

B. Add ONLY functional premises: two original halves sorted by ONE fixed finite
SWO on immutable keys, faithful normallyreturning comparator and odd scalar
sourcechoice left<left_end. Derive forwardleft/backwardright tie rules, prove
scalarfinalguardpasses, sortedout, occurrencepermutation and stableIDordering
for every equivalent key pair. Rechecked constructiveSWO-rankbridge allowed;
no assumed correspondence. If reference stablemerge is introduced, both its
correctness and exactourbidirectional schedule correspondence need bodies.
Do not count an ordinary one-direction merge theorem as B acceptance.

Acceptance: same fullpinnedsource3bodyadmission, expected==visited ownbodies,
allfullnormalpost/return/leak/sourceintegrity/0error gates; no omitted deadbody,
assumed lemma/ownershipbridge or disabledchecks. Explicit inductive arbitrary
length domain. GeometryG2 original proof/source/profile/results remain intact.
Three new meaningful negatives: lossy/duplicate output withoutfinalguard,
wrongtie selection violatesstability, incorrectcomparison violates sortedness.
Eachisolatedfalseassert mustreach predeclaredpredicate/stage/line/column; strict
7wrongresultcontrols each. Parser/setup/timeout/unrelatedfailure is inconclusive.

ProceedA thenB through relevant successful stages; failures require evidence-
based annotation/context/lemma fixes, preservecounterexampleifany. Material
unproved obligation/budgetboundary -> exact checkpoint, no silent stronger
premises/weakerposts. One own manualhostedjob<=remainingbudget, no local
proof/generator/build/test, no tool/runtime/signature/memory patch. Updatecards
beforeeachnew experiment. Final ownRESULTS/STATUS/coverage/log/cost,commit/push.

Functional theorem is conditional puremath only: scalar guard doesnot identify
actual pointerguards/ZST; provenance/usize-byteoverflow/memorypermissions/
initialization/ownership/FnMut/unwind and actualRust remain OPEN. No public
Challenge/fullactualmerge completion. No otheragent worktree/branch/commondocs
or networkruns/merges. G2originalproofSHA b1ed0c22dafec350a64e83675d55350806d77208.

---

# Authorized merge geometry phase

1. Admit full pinned SmallSort bytes and exact active bodies/operation order of
   merge_up, merge_down and bidirectional_merge, including odd residual/guards.
2. Check pure access/advance helpers before using them. For n=2m+e, m>=1,
   e=0 or1, arbitrary independent comparison decisions, prove an invariant for
   every k=0..m and induction on an arbitrary m-long decision list.
3. Check every reference read/copy-source/destination BEFORE cursor changes;
   distinguish readable [0,n) from wrapping intermediate -1 and boundaries n.
4. Prove final odd source/destination and updates for BOTH possible branch
   outcomes; separate arithmetic scalar guard behavior from pointer comparisons.
5. Calibrate boundary/progression negative assertions with isolated cases and
   fail-closed exact predicate/location/stage/source controls.
6. Inspect full hosted evidence; update own checkpoint, commit/push; no merge.

Stock official VeriFast26.09 source809de4596839b739dd999f9e462242c835e3af46,
archive SHA256da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
console SHA256dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
No parser/kernel/prelude/memory/refiner or historical profile changes. Own C
mathematical ghost bodies, not C replacements for Rust. Every abstract callee
checked in same unit; no assumed pointer/rank bridge, bounded enumeration or
sortedness premise. Frozen accepted networks classifier may be reused byte-
identically for pure full-body/return/leak/integrity/exact-negative evidence.

Budget1800 summed hosted job seconds, cold setup/evidence included. workflow_dispatch
only, ubuntu hosted, one relevant job/run at a time on this branch; never verify,
compile, execute proof/generator/tests locally. Routine within-profile proof
fixes authorized; failures need new evidence/card, no blind retry. Source/tool/
trust boundary change or insufficient budget -> exact checkpoint.

## Phase checkpoint

Steps1–6 completed as mathematical geometry/sourceadmission, G2accepted.
All8body/fullpost/source/return/leak gates,3intendednegatives and21classifier
controls accepted. Budget25/1800,1775unspent, no active run. Actual Rust
transfer/fullmerge safety/functionality remain separate OPEN obligations.
No further tests for documentation-only closeout. See RESULTS/STATUS/journal.

## Functional stage completed

Goals A and B and every acceptance gate completed. A2 accepted at
fc4d03d31f92c6d3f3566b0baa506d0a6dec6805; full B7 at
4e546ec150cf655681516be727aa1a79f525fc56. Both arbitrary-length inductive;
all G2/A/general SWO/application bodies checked, exact source admission retained,
full posts/return/leak/dead-code/integrity and intended negatives accepted.
No reference merge introduced; rank correspondence constructively derived.
All actual Rust transfer obligations remain OPEN, described in INTEGRATION.
At functional closeout330/1800 job seconds spent,1470 unspent, no active run. The25/1775
checkpoint above records geometry completion/stage entry, not a budget reset.
Only documentation closeout remains; no more runs for this completed stage.
Networks/exactN13 remain closed/OPEN respectively with unchanged prior budgets.
