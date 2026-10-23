# R23 generated-glue compatibility pin — design note (2026-10-24)

## Defect and applicability

The generated-glue compatibility runner verifies that the checked-in pair of legacy synthetic Drop constructors and the copied refiner source match the selected public profile. Its exact R11 entry still requires refiner-source digest `48d02bf4…` (the R20 baseline), so it rejects the exact R23 diagnostic profile 3fec, whose R22 owned-NLL refiner source digest is `11a0ff90…`. This blocks later caller/capture execution after the tool compiled successfully. The change applies only when the runner is given the exact registered profile file through `SMALLSORT_MERGE_PROFILE`.

## Invariants

- Every legacy profile retains its current exact expected refiner source pin. The legacy synthetic Drop source must still contain exactly two `kind=Drop` cases and exactly two complete unqualified-default constructors.
- The new exception is exact and optional: profile file bytes hash to `3fec93b5237d534b69eb3be59d11ea4abde3588f07c6e9437b1c09bf8533ac88`; parsed profile is public `experimental-merge-label-storage-r11-v1`; effective tool commit is `fc0208d4f53583d458670cd07bd0370636d4b2eb`; the owned-NLL registration is the complete expected registration; and the refiner source hash is `11a0ff9057e6da92a684c20b1cda1e4825d986ea6d80980a7a967f236f0c9db8`.
- No public profile name or prior pin is replaced. Missing, unreadable, malformed, partial, null, wrong-type, wrong-profile, wrong-field, wrong-hash, or wrong-source profile data fails closed. An unregistered R11 source remains rejected.
- Copied verifier bytes, capture receipts, source snapshots, replay commands, controls, and no-proof-credit classification are unchanged. A compatibility match only permits the existing diagnostic campaign to continue.

## Distinguishing controls

- Keep the existing synthetic service tests for all legacy pins, exact two/count-two constructor checks, and source mutation failures.
- Add exact registered profile3fec acceptance with refiner digest `11a0ff90…`, plus wrong bytes/registration/profile/tool/source/hash cases that must fail.
- Exercise missing/null/wrong-type/unreadable profile binding through the helper's optional `profile_path`; the production runner must pass `SMALLSORT_MERGE_PROFILE` explicitly so it cannot use the test-only legacy-compatible default to admit a changed source.
- Retain runner failure-path behavior: prerequisite/receipt mismatches and source-stage inconsistencies remain errors or inconclusive outcomes and do not yield proof credit.
