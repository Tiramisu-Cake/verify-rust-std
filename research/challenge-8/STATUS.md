# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: [pointer ownership phase](SORT4-POINTER-OWNERSHIP-PHASE.md).**
Owner explicitly opened new phase from e0920ec; budget 0/5400 NEW job seconds,
<=1800/job, <=300/proof, one active run. No active run at entry.
[Results](SORT4-POINTER-OWNERSHIP-RESULTS.md); chosen definition/trust boundary
recorded before ownership edits. Model/constructor UNACCEPTED, actual callee NOT RUN.
Next permitted: implement narrow type-wide defined pointer ownership and full MIR
gate/matrix, hosted acceptance, then dependent actual callee. Prior budgets retired.

Previous checkpoint preserved below (historical authorization superseded):
**CLOSED: [composition/constructor phase](SORT4-COMPOSITION-CONSTRUCTOR-PHASE.md)**
at its authorized ownership boundary. [Final report](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md).
Entry85d82998e148394e5dbbb0a4ed8c326780130b75; new budget816/5400 summed
hosted job seconds=13m36s,8NEWruns. Remaining4584s retired. No active run.
C1/C2 pure composition accepted; C3 immutable layout full matrix PASS.
C8/37592506846/source53b64a780650f6bece661ad751429f628966a63a:
all8baselines/source/export/decode/refinement/translation gates PASS, then VF1
SAFE prototype check requires opaque MaybeUninit_own at10,75–102, BEFORE body.
Constructor body/value/resources/unwind NOT PROVEN. Translator-only patchcbf7b7da
UNACCEPTED; full MIR dataflow gate/constructor acceptance negatives and dependent
actual callee NOT RUN. Non-feasibility harness mode now fails closed.
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

No further implementation/dispatch under the PREVIOUS closed phase.
The owner has separately authorized the new pointer ownership phase above. The design committed
before semantic edits; safe source-local body and narrow representation/call
translation exist only as an UNACCEPTED separate experimental profile. No own
bridge, unsafe-constructor workaround, deleted safety template or old patch chain.
Next owner decision: checked ownership interpretation for pointer MaybeUninit,
then full MIR applicability/negative gate; [project](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md#minimal-next-project--not-implemented--not-authorized)
is NOT IMPLEMENTED / NOT AUTHORIZED. Actual callee follows only accepted constructor.
README/PLAN/current pointers reconciled; completed edits committed/pushed.
Runtime/general contract/pins/checks preserved. RAPx CLOSED/NO-GO; B/C NOT RUN.
