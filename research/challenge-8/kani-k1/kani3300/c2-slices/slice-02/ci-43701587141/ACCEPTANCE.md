# Slice 02 IMMUTABLE — ACCEPTED (run 43701587141)

2026-11-15, coordinator. Fork run [43701587141](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141),
branch `uninit-ci/c2-slices-02-w15-r2`, overlay `536f1d20d127987cdd860bc6367acc9fff90c5cb` (CI-only `.github/`) on source
`932fb8395a58f8c86c0d702ba2cae835823b2962` (parent slice 1 `d82752c8bc`). Supersedes candidate `b0a5a4fff9`
(run 43699468860, E0726 split impl hunk; fix = one line, `impl MirVisitor for InitialTargetVisitor<'_>`; static
compile-seam check added, `slice-02/COMPILE-SEAMS.md`). ubuntu-24.04, ~12 min, every step success.

| Stage | Result |
|---|---|
| fmt / build-dev / clippy `-D warnings` | exit 0 |
| ActiveCalls units | 9 / 0 / 0 |
| immutable_allocations units | 9 / 0 / 0 |
| kani | 50 / 0 / 3 ignored |
| expected | 219 / 0 / 6 ignored |
| ui / script-based-pre / json-handler / std-checks | 17 / 3 / 17 / 2, all 0 failed |

Totals 308 passed / 9 pre-existing ignores = CI-REQUEST (317 selectors). Every stage
`EXIT_ZERO_COUNTS_MATCH_REQUIRES_REVIEW`, reviewed here. Fixtures needing slices 3/4/5 are deferred per `slice-02/SLICE.json`;
slice 1 integration obligations remain PENDING on 4/5. Not Gate A, no proof credit. Next: stage 3 LAYOUT-RAW on `932fb8395a`.
