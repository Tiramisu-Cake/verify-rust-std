# C1-T2: received CI observations

Only coordinator-reported facts are recorded here; no run, evidence archive, full log or runtime artifact was inspected in this stage. These aggregates give no new independent proof credit.

| Run | Revision/context | Reported outcome | Mechanistic qualification |
| --- | --- | --- | --- |
| 43219870063 | baseline production 6134e42dd1c65dc980336e7d9455aba02d423edf plus C1-T 28e684cbae348130d559b87e030536d8f8a3c1ff; workflow-only checkout 172a7cfdbc02bd784873cfb4410d9b08fe51a9f1 | expected uninit 125 PASS / 1 FAIL / 2 ignored; sole FAIL existing maybe-uninit-initialized; all six C1-T matched goldens | Both origins, emitted/reached checks and hole failure sites UNKNOWN |
| 43222702257 | M1 5abdcf982da6aff65662e198af27a9c776830a89; current user supplied fact | Quick passed: expected uninit 130/0; maybe-uninit-initialized PASS; immutable-masks four PASS; promoted_* six PASS | Workflow checkout/ignored count not reported; actual mask/seed/check bindings UNKNOWN |

The original six C1-T already matched on baseline. Their legal SUCCESS/hole FAILURE cannot explain instrumentation or qualify D0's immutable RHS. M1's aggregate PASS remains separate from baseline and from unobserved per-property bindings.

All eight new C1-T2 selectors: baseline and M1 setup/compile/solver/harness/golden/MIR/property inspection NOT_RUN. They were not included in either reported run. No predicted baseline FAIL is recorded as observed.

D0-A at research ff5cabbfca records a distinct historical diagnostic: two [u8;4] legal harnesses, tracked left temporary setter already worked, immutable RHS started false. Its source/run identities and incomplete evidence limits remain in d0a; this stage neither re-audits nor upgrades them.
