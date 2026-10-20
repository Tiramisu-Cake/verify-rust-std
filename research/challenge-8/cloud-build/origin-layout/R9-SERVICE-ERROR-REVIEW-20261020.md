# R9 service error-path review — GO

Reviewed the source-pin setup change against `392278a3`. The control now
validates `source_record.source_sha256` inside the existing source/profile
setup `try` boundary, before entering the baseline gate. Invalid preparation
pins therefore produce the established `NOT_RUN` case receipts and persisted
aggregate instead of escaping `run()` and aborting the campaign. For valid
input, the existing strict gate still requires the exact original, verified,
and pinned `small_sort_source` hashes in both before/after maps, along with
unchanged-source, stage, exit, status, and event checks.

The synthetic test covers a missing pin, null, bool, integer, list, dict, and
malformed digest. Each case verifies that execution is not called, all five
controls remain `NOT_RUN`, and the aggregate is written. The existing valid
baseline/control cases continue to pass.

Validation: all 10 R9 control service tests passed; `git diff --check` passed
for both changed files. No compiler, proof, or Cloud Build was run for this
review. **GO for this localized service error-path fix.** No proof credit is
granted.
