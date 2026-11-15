# Slice 01 ANALYSIS — ACCEPTED as NO_REGRESSION (run 43696666260)

2026-11-15, coordinator. Fork run [43696666260](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260),
branch `uninit-ci/c2-slices-01-w15`, overlay `4f5dc3732c8fbaa94c814c41d184534148a1d312` (CI-only: `.github/workflows`,
`.github/c2-slices`) on source `d82752c8bc878398e672bffaa631ca6a28430acc` / tree `c7024fb95c`, parent B1 `6fe484b300`.
ubuntu-24.04, ~10 min. Job and every step success.

| Stage | Result |
|---|---|
| fmt / build-dev / clippy `-D warnings` | exit 0 |
| ActiveCalls units | 9 passed / 0 failed / 0 ignored (exactly 9) |
| kani | 50 / 0 / 3 ignored |
| expected | 213 / 0 / 6 ignored |
| ui | 17 / 0 / 0 |
| script-based-pre | 3 / 0 / 0 |
| json-handler | 17 / 0 / 0 |
| std-checks | 2 / 0 / 0 |

Totals 302 passed / 9 ignored = CI-REQUEST static expectation (311 selectors); runner reports
`EXIT_ZERO_COUNTS_MATCH_REQUIRES_REVIEW` for every stage, reviewed here. Ignores are pre-existing upstream ones.
Source identities before/after: same source/tree/overlay, clean porcelain, 3878 entries; only difference — submodules
`charon`, `firecracker`, `tests/perf/s2n-quic` initialized by setup at their pinned SHAs.

Qualification kind **NO_REGRESSION** (variant C). Integration obligations of this slice remain **PENDING** on heads 4/5
(`slice-01/DEFERRED-OBLIGATIONS.json`). Not Gate A, no proof credit. Next: stage 2 IMMUTABLE on top of `d82752c8bc`.
