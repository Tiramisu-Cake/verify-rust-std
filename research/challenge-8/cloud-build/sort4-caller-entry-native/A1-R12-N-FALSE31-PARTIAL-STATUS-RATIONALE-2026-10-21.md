# R12 N-false31 partial lifecycle status

When both N-false31 threshold-body and native-conformance observations have
completed but the complete expected-case manifest is unavailable, the runner
must stop before publishing an own-pair receipt or invoking the caller. The
existing return marked the entire N-false31 observation `not_run` with
`execution_started=false`, despite two actual focused body attempts.

The external matrix classifier treats any top-level `not_run=true` as an
immediate `NOT_RUN` result. The partial path will instead report that the
body pair was observed, set top-level `execution_started=true`, and store the
two exact body observations. It will describe receipt and caller stages as
separate `NOT_RUN` children, with no receipt path, no success classification,
and no proof credit. The external classifier will therefore retain the row as
`INCONCLUSIVE` rather than suppressing the attempted bodies as `NOT_RUN`.

This changes only lifecycle reporting for the missing-manifest branch. It
does not issue the receipt, relax same-pair/default+Freeze conformance checks,
consume a helper summary, or invoke the false31 caller. Synthetic coverage
will exercise the real runner function with two successful body observations
and pass its result to the current matrix classifier, confirming that the
attempts remain visible while the matrix outcome stays conservative.
