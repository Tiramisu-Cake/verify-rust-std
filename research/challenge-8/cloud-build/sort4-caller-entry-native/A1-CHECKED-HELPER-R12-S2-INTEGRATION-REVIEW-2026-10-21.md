# R12 S2 syntax/body split review

**Decision: NO-GO pending one diagnostic-matching correction.** The split preserves the proof boundary: syntax preflight records `body_verified=false`, `proof_credit=false`, and `caller_receipt=false`; the core requires the AST-selected manual helper plus either a zero-exit mini unit explicitly marked as noncanonical or the observed body-leak case; canonical fresh helper prerequisites remain unchanged. The stop path reports every first-matrix row `NOT_RUN` for full-matrix mode and creates no admission record.

The leak exception is broader than the rationale and requested contract. `a1-ghost-grammar.py:160–171` requires a single diagnostic at the certified helper closing line and checks that the known marker occurs anywhere in the diagnostic string. The core receipt validator at `a1-runner.py:272–287` repeats the same substring condition. Therefore a line such as `verified/lib.rs(12,1): error: unrelated failure; Function leaks heap chunks: own(ref_typeid(...)` is accepted as `KNOWN_BODY_LEAK_OBSERVED`, even though the error is not the observed body leak. Anchor the exact diagnostic immediately after `: error: ` and constrain the remainder to the known form; add a synthetic unrelated-error-with-marker negative.

The existing controls cover exact known leak, wrong source line, arbitrary unrelated error without the marker, missing AST, and malformed/partial stages. The combined focused synthetic suite passed (32 tests), but it does not cover an unrelated diagnostic containing the marker. No compiler, verifier, full runner, or Cloud Build was run for this review. The earlier false31 partial-status delta remains independently reviewed GO, conditional on its profile pin refresh.

## Follow-up correction

The NO-GO finding is addressed in the working tree: both grammar-module and
core validation now require a full-line match whose text immediately after
`: error: ` is exactly the S1 leak expression family. Synthetic module and
core cases with an unrelated-error prefix followed by the leak marker are
rejected. The R12 registration assertions now reflect the authorized
full-matrix timeout/work budget and validate the live ledger's accounting
invariants instead of assuming its pre-build state. Focused grammar, core,
coordinator-budget, and transport tests pass. Profile source pins still need
the coordinating refresh before the registration pin test can pass.
