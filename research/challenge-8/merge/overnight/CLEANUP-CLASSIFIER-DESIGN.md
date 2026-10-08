# Cleanup fixture classifier design

This note records the classification boundary for the cleanup fixture from
hosted run `37711781188` before extending `pointer-prove.py`.

The positive case keeps the existing full gate: all four stages succeed, the
expected checked body is visited and executed, return and leak checks occur,
the source remains unchanged, and VeriFast reports zero errors. Its gate is not
weakened by negative-case handling.

Negative cleanup controls have two different outcomes. A proof rejection is
an exact, predeclared VeriFast proof error after exporter/decode/refinement
succeed, the source is unchanged, and the case's checked body has executed.
This covers the false unwind post, absent input owners, the missing reference
fraction, and the escaped typed reference reported by the function leak check.
The result remains a proof rejection; an error in a shared specification is
acceptable only when its exact file, location, columns, and message match the
recorded oracle and the marked case body ran.

An admission rejection is an exact cleanup-protocol diagnostic emitted before
the checked body is entered. The classifier records a separate
`EXPECTED_ADMISSION_REJECTION` status and requires that no body execution was
reported. It does not invent execution, return, or leak records. This applies
to the wrong marker, local predicate type, physical lifetime, and predicate
operand controls. These results test admission validation and do not count as
proof negatives.

Both negative outcomes require exact stage codes `0/0/1/0`, exact source
integrity, one exact error, an exact `TARGET` anchor inside the sole checked
body, and fail-closed mutations for stage, diagnostic, target, source, and
execution evidence. Historical `INCONCLUSIVE` labels in earlier evidence
remain historical; this source change does not reclassify or rewrite them.

The new `frontend_admission` and `leak_check` kinds name these distinct
diagnostic classes. They add no verifier behavior or semantic rule. The
classifier only interprets saved stage output and metadata.
