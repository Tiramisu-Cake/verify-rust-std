# Separate cell timing comparison

Raw stock verification_time_s only; all source/request/control/profile differences
are retained in TIMING-CELL.json (complete request field deltas and control changed
paths once per baseline, plus per-root row/config/argv differences). The old35pairs
comparison remains immutable. Qualification PENDING_OFFLINE; proof NONE.

| Root | S1-07 600s | S1-08 diagnostic 600s | Retry 1200s | Retry/S1-07 completed ratio | Retry/diagnostic completed ratio |
|---|---:|---:|---:|---:|---:|
|stable_default_cell|367.259887864 SUCCESS|600.031112420 TIMEOUT|617.990161140 SUCCESS|1.682705304|CENSORED|
|unstable_default_cell|368.802323945 SUCCESS|594.575884753 SUCCESS|485.289873459 SUCCESS|1.315853621|0.816195015|

Completed ratios are descriptive across different profiles. Stable diagnostic TIMEOUT
is a right-censored completion time at600s (reported elapsed600.031112420s), so it
has no exact retry/diagnostic completed ratio. Retry stable617.990s cannot establish
fit600. Limits600→1200, changed scheduling and source5be→99e (S1-07 comparison),
request/control/label/contract-interface coordinate differences are disclosed.
Tool0aac is common. No causal label effect, same-profile slowdown, aggregate
composite runtime or organizer-CI budget fit is established.

Group elapsed1147.782s and sampled RSS8174308KiB are shared-process observations.
Per-root process wall/RSS/exit are UNKNOWN. Raw verifier time is not process wall.
