# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: [composition/constructor phase](SORT4-COMPOSITION-CONSTRUCTOR-PHASE.md)**,
new owner authorization from85d82998e148394e5dbbb0a4ed8c326780130b75.
New budget248/5400 summed hosted job seconds; job<=30min, pure fixture<=300s,
one relevant run. Active C4/37590641832/sourceac6dfcf246a72f4e9066041b0e31b810553d117d,
constructor feasibility only, dispatched07:57:56UTC; budget pending completion.
C1/C2 pure composition accepted; C3/37586921301
immutable layout full matrix PASS179s. C4 constructor feasibility diagnostic ready:
source-linked translator-only patch047b92a8; building, not accepted. Full MIR
dataflow gate/acceptance negatives/dependent actual callee are NOT RUN in C4.
Entry tree clean, research HEAD/remote match.
The [night](SORT4-NIGHT-PHASE.md) remains CLOSED at12/12 NEW,2697jobseconds;
[report](SORT4-NIGHT-RESULTS.md). All historical budgets remain closed.

**Accepted components, not a full Rust sort4 theorem:**

- Existing stock generic H_align const/mut: run37540829027/source968c073,
  full integrity/refinement/dead-code gates intact; not rerun this night.
- Exact experimental fieldless layout profile d4a12525: N2/37547890530,
  source3f5c9e3,historical N2 retained; C3/37586921301/source3844c5f full matrix PASS,
  valid distinct (7,0)..(7,12) binding mismatch calibrated and41 span/classifier checks. Patch remains SHA256
  d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14.
  Narrow original-fieldless nongeneric Sized reprRust/C+optional-align profile,
  not full-model soundness or automatic operation-UB coverage.
- Stock index permutation: N4/37548475221/sourcefa74d92,arbitrary5independent
  Booleans,bounds/distinctness/everyIDonce. N5 saved replay accepts intended
  duplicate-index failure without repeating verifier or altering raw evidence.
- Stock integer-rank sortedness/stability: N5/37548811698/source6a12b4e,
  39statements,fixed/preserved arbitrary ranks and original tie IDs; negative17.
- Stock finite-SWO rank bridge: N11/37553933186/source3c3f0f3,104statements,
  relation16/all4diagonal+64triple laws,counts0..3,less iff rank<,equiv iff rank=;
  all named bodies/leak checks and intended tied-rank negative19 accepted.
- Stock scalar range composition: N8/37549955948/source9b25c41,24statements,
  exact selected source IDs to dst0..3,containment/separation for stride>=0,
  including0. No pointer/resource/overflow/initialization/operation theorem.

**Accepted pure SWO composition:** C1/37585795831/source0383012,
stock s4_swo_choice_network and all components pass194statements/leak checks,
full index permutation and three adjacent sorted/stable steps for fixed SWO.
C2/37586573468/source4e7ee10 audits saved bytes/profile/source binding and accepts
intended negative21,42–44 plus3 classifier mutants, without verifier rerun.
[Audit](SORT4-SWO-COMPOSITION-AUDIT.md). This is pure mathematics; actual Rust,
callback/value preservation, memory/resources and unwind remain separate.

**Model/callee boundaries:** N6/37549040942/sourceaed1d97 retains exact actual
pointer-callee body; export/decode/refinement/integrity0,first VF error at adapter21:
`No such function: std::mem::MaybeUninit::<T>::new`. Selection/provenance/permissions/
frame/no-unwind posts unproved. See [callee](SORT4-SELECT-CALLEE.md).
[Memory note](SORT4-MEMORY-OPERATIONS.md): initialized-dst specs do not bridge raw
scratch; reference/copy automatic alignment coverage unmeasured. Current callback
resources/effects and all five full panic posts remain open. Logical ZST IDs can
share addresses; Copy/Freeze/purity restrictions were not added to general safety.

Current permitted actions: stock pure composition/negative, bounded span-control
repair/full unchanged-layout matrix, and separately designed minimal runtime
MaybeUninit::new support for MaybeUninit<*const Element> over stock26.09.
Constructor design/trust/gates must precede semantic edits; experimental profile
is not automatically accepted. Stop extension before general union/alias/ownership/
copy/FnMut/Drop support. No historical patch chain or general-model expansion.
README/PLAN point to this phase. Runtime/general contract/pins/checks preserved.
RAPx CLOSED/NO-GO; B/C NOT RUN. Constructor design reviewed before semantic edits: source-linked local body/active-value
translation only, no opaque ownership bridge; implementation in separate profile.
Next: hosted C4 safe-body feasibility; retain generated safety contracts and stop
before a new ownership bridge. Even green C4 cannot accept this partial profile.
