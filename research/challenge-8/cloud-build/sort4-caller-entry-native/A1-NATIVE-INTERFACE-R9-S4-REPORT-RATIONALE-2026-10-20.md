# R9 S4 lossless report serialization rationale

## Evidence and boundary

The R9 lifecycle result stores each case observation both in
`observed_rows[].observation` and in `observation_details[case_id]`. Keeping both
copies in the emitted final JSON can duplicate large observations. This is a
representation change only; it does not address or explain the S3 terminal
failure (`execute=SUCCESS`, package upload exit 1, Brief/catalogue HTTP 404,
sizes unknown), and it grants no proof credit.

## Pointer contract

Only the final disk view for the literal R9 authorization ID
`SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9` may compact rows. The older
runner-wide authorization constant is not the eligibility gate, so changing
that constant for another lane cannot opt R6/R7/R8 reports into this
representation. A row is replaced only when it has a unique string `case_id`, both its
inline observation and the same-key `observation_details` value are non-null
mappings, and their JSON-shaped values match recursively with type-sensitive
equality. The reference uses schema `a1-observation-ref-v1` and an RFC 6901
pointer to the retained map entry. Root `report_serialization` records
`kind=row-pointer-v1`, `lossless=true`, and `proof_credit=false` only when at
least one row is replaced.

The full `observation_details` mapping is retained, including entries outside
the matrix. Root flags, case status, row order/IDs/statuses, source and unit
IDs, events, errors, partial data, `NOT_RUN`, nulls, and artifact-path shapes
remain present. Missing map keys and null/wrong-shaped observations stay
inline. A conflicting value or duplicate/malformed row identity makes the
operation a no-op for the whole report. No pointer is invented for absent
observations, and no status or acceptance field is changed. The in-memory result
and progress snapshots are not transformed; only terminal disk JSON uses this
view. Existing metadata limits, source bytes, and packaging behavior are
unchanged.

## Validation limits

AST-extracted synthetic tests exercise the pure disk-view function without
importing the runner or running preparation/proof. They expand emitted JSON by
following each pointer and compare the reconstructed complete value with the
original, including 26 rows, escaped Unicode/slash/tilde IDs, non-matrix
observations, large repeated payloads, a 128-bit integer, errors, partials,
`NOT_RUN`, nulls, and absent artifact paths. They also cover older R6/R7/R8
authorization IDs, malformed, missing, duplicate, and conflicting inputs.
These tests establish serialization
round-trip behavior only; they do not establish S3 causality or verifier
acceptance.
