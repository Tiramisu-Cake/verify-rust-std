# Select R13 phase and route registration rationale

R13 opens a new authorized Select window after the R12 account closed. It uses the fresh `SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13` phase and its already-created 3600-second ledger, while retaining the established A1 experiment protocol phase, lane, source restoration, and v3 shared coordinator capacity/accounting rules. The registration does not mutate R12/R11 ledgers, profiles, routes, or evidence.

The R13 entry and runner adapters are copied from the reviewed R12 adapter route and bind a distinct R13 authorization phase to the same existing protocol. This keeps the phase distinction explicit while reusing the same underlying source reconstruction and runner contract. Profile hashes that depend on in-flight R13 runner integration are provisional and must be refreshed by the integrating owner before publication.

The profile remains `execution_mode: full-matrix`, `profile_accepted: false`, `proof_credit: false`, and `first_matrix_status: NOT_RUN`. No new diagnostic mode is registered in this change, and no matrix cases or admission criteria are relaxed. Existing target/diagnostic support can be added only with its own fail-closed profile and runner checks.

The R13 account registration mirrors R12's sequential-build phase constraints: exact owner, lane, T0/main/absolute deadlines, 3600-second ceiling, no fixed Build-count limit, and 1200-second maximum timeout. It keeps the existing 240-second report reserve and does not alter coordinator/IAM code or capacity policy. The existing R12 local two-slot historical guard remains unchanged; R13 uses the current coordinator protocol.

Regression expectations: the coordinator must accept only the exact R13 ledger/profile binding and preserve the existing R12 registration; the lane routes only R13 authorization to the R13 entry; the profile keeps the A1 protocol phase and full matrix admission state; adapter pins fail closed when stale. Validation is limited to small synthetic registration tests and static parsing. No compiler, preparation pipeline, verifier, full runner, or Cloud Build is run here.
