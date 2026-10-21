# N-false31 partial-status review

## Finding

The first bookkeeping fix only treated a non-mapping `expected_cases` value as
missing. The runner initializes `expected_cases_for_run` to `{}` and passes
that value to `draft_false31_pair_stage`, so the common default empty mapping
passed the shallow check. The later false31 alias-rebinding code then raised
`KeyError` after both own-pair body attempts, leaving the enclosing action with
an adapter error instead of the two body observations and separate caller /
receipt NOT_RUN states.

## Resolution

Receipt generation now requires the exact closed 26-case ID set with a mapping
row for every case. Empty, incomplete, extra-key, wrong-type, and malformed-row
manifests stop after the two same-pair body/conformance checks. The result
preserves both body records as executed, labels receipt and caller stages
NOT_RUN separately, emits no receipt path, and carries no proof credit. The
matrix classifier must retain this observation as INCONCLUSIVE.

Synthetic coverage exercises the caller's default `{}` input as well as
incomplete, null, wrong-type, and malformed-row inputs through the actual
false31 staging function, and verifies the external classifier outcome.

## Independent re-review

I confirm the revised predicate requires the exact `CASE_ORDER` key set, string
keys only, and mapping-valued rows. The new lifecycle test covers the default
empty mapping, incomplete, null, wrong-type, malformed-row, and extra-case
inputs; all preserve both body observations, mark receipt/caller `NOT_RUN`, and
classify as `INCONCLUSIVE` through both matrix and native-target classifiers.
The original NO-GO applies to the superseded candidate; **GO for this narrow
revised delta**, conditional on refreshing the active runner hash/profile pin
before execution.

Validation: `python -m unittest test_a1_false31_partial_lifecycle -v` passes
(2 tests), and `python -m py_compile a1-runner.py` passes. No compiler,
verifier, full runner, or Cloud Build was run for this review.
