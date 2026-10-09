# Strict CUT matrix and false-post Cloud lane

The earlier `o26-strict-cut-controls` Build reached pinned relocation and
strict-control preflight, then stopped at an audit-record `classification`
lookup before the seventeen-case matrix ran. This lane is the first actual
same-Build matrix plus two target false-post controls. It retains the frozen
O26 baseline, `d557` strict CUT, callback relocation and translated-ID patch
chain. It does not include the actual-sort4 scope TEST or source-only capture.

The lane requests only `CUT_RELOCATE=1`, `STRICT_CUT_CONTROLS=1`, and
`STRICT_CUT_FALSE_POSTS=1`. The baseline must satisfy its original source,
MIR, refinement and prefix proof gates. Relocation must reach the mapped-ID
callback fixture with exact source, full normal/readonly MIR, direct unwind
and a full diagnostic verifier exit zero. All seventeen matrix cases must
have the intended source/MIR/first-error or full-positive verdict, including
the no-opt-in rejection. The two false-post mutants change only the target
normal or unwind post of their already positive parent case and must fail at
their respective first false-post obligation after successful support stages.
The exact raw files and component audits remain in one Cloud archive.

The compound result is `STRICT_CUT_FALSE_POSTS_DISCOVERY_COMPLETE` only when
all three distinct components and the baseline gates complete. It is a
diagnostic result with `verification_accepted=false` and
`actual_sort4_proved=false`. Any setup, source, MIR, earlier proof or resource
failure is inconclusive. False-post first locations remain predictions until
the Cloud archive is inspected; no actual-sort4 source, liveness, alias,
heap/bound or no-cut/S6 acceptance follows from this lane.
