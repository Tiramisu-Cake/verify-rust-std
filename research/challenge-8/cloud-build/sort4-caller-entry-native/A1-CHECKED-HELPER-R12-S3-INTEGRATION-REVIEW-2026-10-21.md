# R12 S3 partial-observation review

**Decision: GO for this bounded runner delta.** The body-entry change moves the exact alias/body-line note check back inside `body_entry_context`, where it is reachable. It retains the unique exact first-error requirement and requires exactly one post-error `Verifying function '<alias>'` frame at the compiler-bound body line. The default and Freeze aliases pass; missing, header-only, prior-note, duplicate, wrong-alias, wrong-line, multiple-error, and wrong-metadata cases refuse the attestation. This produces a non-credit execution/conformance observation only for the intended body-stage failure; positive body-proof acceptance conditions are unchanged.

For false31, after the two same-pair body/conformance checks and the existing own-pair receipt issuance, the new early return handles the checked-helper-blocked/no-structure caller result before boundary analysis. It preserves the body pair, caller helper result, source-pair identity, and issued receipt path/order; it marks caller verification and boundary unavailable, with no proof credit. The matrix classifier maps only the new partial label to `INCONCLUSIVE` with no record or matrix gate. The successful canonical path still proceeds through the existing boundary checks and exact completed classification; unrelated exceptions retain the existing action error path. Focused synthetic tests cover the helper-blocked branch, kept body rows, classifier result, no boundary call, and the existing body-entry edge cases.

Validation run for this review: body-entry, false31 partial lifecycle, and matrix-classifier tests pass (24 total); profile-binding tests pass (11); `py_compile` and `git diff --check` pass. No compiler, verifier, full runner, or Cloud Build was run. The refreshed R12 profile binding remains current.

One non-blocking reporting ambiguity remains: the partial record sets `caller_stage.execution_started=true` because the outer caller collection/helper-gate invocation started, while `caller_verification_status` is explicitly `NOT_RUN_CHECKED_HELPER_PREREQUISITE` and `proof_attempted=false`. An explicit `caller_verification_started=false` field could make that distinction easier to read. Also, the generic missing-structure arm shares the helper-blocked top-level classification, so the classifier's fixed reason mentions the helper prerequisite even when the local reason says structure unavailable. Both cases remain conservative `INCONCLUSIVE` with no record or proof credit; these are diagnostic-precision suggestions, not acceptance defects.

## Precision follow-up

Both reporting suggestions are resolved in the current delta. The explicit
helper-blocked path now records `caller_verification_started=false` and
`proof_attempted=false`. A generic no-structure result has a distinct
`FALSE31_OWN_PAIR_RECEIPT_ISSUED_CALLER_STRUCTURE_UNAVAILABLE` label and
classifier reason; those execution/proof fields remain `null` because that
stage's exact cause is not established. New lifecycle tests exercise both
paths through the matrix and native-target classifiers, confirming
`INCONCLUSIVE`, no record, no matrix pass, and no proof credit. The focused
false31 lifecycle tests pass (4); the refreshed profile-binding tests pass
(11); compilation and diff checks pass. **GO remains unchanged.**
