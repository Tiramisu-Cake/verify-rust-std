# Challenge 8: current checkpoint

Updated2026-10-07. **CLOSED: [autonomous night phase](SORT4-NIGHT-PHASE.md)**;
NEW-run budget exhausted before09:00MSK. [Morning report](SORT4-NIGHT-RESULTS.md).
12/12 NEW,2697/10800jobseconds(44m57s),layout repair2/2. No active run.
Branch challenge-8/research in Tiramisu-Cake/verify-rust-std; completed changes
committed/pushed. Final proof-attempt source1803ad0be54a41d97059ad28a0400a7cf851aed3;
subsequent closeout/harness correction is NOT a proof run. Historical budgets closed.

**Accepted components, not a full Rust sort4 theorem:**

- Existing stock generic H_align const/mut: run37540829027/source968c073,
  full integrity/refinement/dead-code gates intact; not rerun this night.
- Exact experimental fieldless layout profile d4a12525: N2/37547890530,
  source3f5c9e3,full original/18extra/7metadata/10native/31classifier-span matrix
  and artifact audit PASS. Patch remains SHA256
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

**Unverified draft:** pure SWO/network composition and relation stability control
in sort4-swo-composition*.c. FINAL N12/37554258065 failed BEFORE VeriFast because
harness requested wrong file names; composition AND negative NOT RUN. Confirmed
one-line wiring repair is committed but UNRECHECKED. No13th run. N9/N10 arithmetic
timeouts retained; isolated checked arithmetic repairs passed in N11.

**Model/callee boundaries:** N6/37549040942/sourceaed1d97 retains exact actual
pointer-callee body; export/decode/refinement/integrity0,first VF error at adapter21:
`No such function: std::mem::MaybeUninit::<T>::new`. Selection/provenance/permissions/
frame/no-unwind posts unproved. See [callee](SORT4-SELECT-CALLEE.md).
[Memory note](SORT4-MEMORY-OPERATIONS.md): initialized-dst specs do not bridge raw
scratch; reference/copy automatic alignment coverage unmeasured. Current callback
resources/effects and all five full panic posts remain open. Logical ZST IDs can
share addresses; Copy/Freeze/purity restrictions were not added to general safety.

Next permitted action: read-only/documentation review of report/designs. A stock
proof-only composition retry needs a separately approved new budget/phase; any
constructor/union/raw-copy/ownership capability requires prior explicit trust/
admissibility review and regression gate. No historical FnMut/Drop/tuple chain,
new axiom/spec/model/verifier or publication authorized. Main4771dd9 changes only
minimal manual workflow exposure, no research-history merge. RAPx CLOSED/NO-GO;
B/C NOT RUN. Evidence in /tmp only; exact run/tool/artifact IDs in journal.
