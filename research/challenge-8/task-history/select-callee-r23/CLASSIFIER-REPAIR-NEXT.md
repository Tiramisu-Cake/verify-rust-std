# Next exact classifier repair (NO_GO path remains unqualified)

Independent review of a7f7a67b found two coupled data-binding defects. A current
matrix log has fresh elapsed timestamps, so its complete-file hash cannot be
required to equal the prior observation's log hash. The prior observation's
Build/file/index/archive/request identities must also not be copied into a
record describing the current stage log.

Repair contract for the next implementation:

1. Keep each prior target observation immutable: original Build, full log
   artifact SHA, Brief identities and request IDs, source/tool hashes, exact
   target file/line/column/full message. This validates the pinned diagnostic
   proposal and its provenance, not the current execution.
2. Separately record the current stage's genuine Cloud Build ID, exact case/
   variant, verified/original source hashes, actual argv and stdout/stderr
   paths, real exit/status/gates, current log hash and pre/post physical
   snapshot checks. Preserve the existing R20 binding. Compute the current log
   hash from the current bytes; do not synthesize it from the prior map.
3. Match exactly the sole current diagnostic (full file, location and message)
   to the pinned prior target. Reject additional diagnostics/fatals, target
   drift, source/tool drift, missing provenance or an invalid stage. Timestamp
   differences in unrelated trace lines must change the current hash without
   changing this diagnostic relation. Do not strip failing assertions/errors.
4. Audit the distinct prior-target/current-stage records and their relation,
   including raw and canonical target-map hashes. Default no-map execution
   remains incomplete/TARGET_UNPINNED. A positive exit1/dead-code case can never
   complete the matrix.

Distinguishing synthetic controls: two valid logs with equal sole diagnostics
and different elapsed timestamps; changed sole message or extra diagnostic;
wrong current Build/variant/source/log path/content hash; prior provenance
unchanged and never relabeled current; missing/null/wrong types; real nonzero
or timeout stage must not be promoted. Re-review the complete delta before any
Cloud matrix qualification. No local actual proof tools are needed for this
metadata repair.
