# Current-owner duplicate-resource proof negative

The existing `current_owner_transposition_double_owner_calibration` case
retains its name for evidence continuity. Its ghost body first transfers the
current destination owner list using the verified transposition helper, opens
the resulting destination `foreach`, and then asks for the same singleton
`T.own` resource twice. It adds no physical memory or ownership assumption.
The required result is a proof-stage rejection at the second resource request,
not a source/parser/setup failure or a positive theorem. All original
preconditions, full postconditions, helper bodies, assertions, resources,
source-integrity checks and refinement remain in force.

Fresh source metadata must predeclare exactly one `// TARGET` on that
assertion and one `// EXPECT_REJECTION` with kind `memory_permission`, file
`verified/lib.rs`, `error_line=TARGET`, columns `95–102`, and exact message:

`No matching heap chunks: foreach<T>(cons(head(transposition_values(T_typeid, vs, i, j)), nil), own0(T_typeid, t))`

The retained pointer harness must observe exporter/decode/refinement exit 0,
VeriFast exit 1, a unique exact error, no dead-code records, unchanged source,
execution of the marked line, entry into the target and all five helper
bodies, and successful classifier fail-closed mutations. The outer audit
independently binds the fixture metadata, case row, first failure, full stage
exits, body-entry records, and error line. Any mismatch remains
`INCONCLUSIVE`; it is never credited as an intended negative.

Cloud run `a643d1e1-48e4-4b24-bc6e-90e8c1bc11e7` at proof commit
`20184556bc04ff33185fb4922617077a0326a383` observed this exact error
under both experimental and stock tools, with target execution, all five
helper bodies, and no dead records. Its fixture had no predeclared oracle and
its result remains historical `INCONCLUSIVE`; this card does not reclassify
it. A new Cloud run on the changed fixture is required before reporting
`EXPECTED_REJECTION`.

This negative establishes only that this proof state cannot duplicate that
specific current owner `foreach` chunk. It does not make generic `T.own`
universally physically unique, prove a caller ownership bridge, or accept the
combined patched verifier profile.
