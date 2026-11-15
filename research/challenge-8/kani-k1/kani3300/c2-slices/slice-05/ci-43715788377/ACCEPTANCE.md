# Slice 05 CLOSURE — ACCEPTED (run 43715788377), mutation 4/4 with one coordinator review

2026-11-15, coordinator. Fork run [43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377),
branch `uninit-ci/c2-slices-05-w15`, overlay `ce56d3d467dd9aeec0fc7abc6a2444ee066e85f6` (CI-only `.github/`) on source
`96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` (parent slice 4 `345cedfd67`). ubuntu-24.04, ~19 min.

| Stage | Result |
|---|---|
| fmt / build-dev / clippy `-D warnings` | exit 0 |
| units: ActiveCalls / immutable / argument_size / marker_category / all compiler units | 9 / 9 / 1 / 1 / 68, 0 failed |
| kani | 50 / 0 / 3 ignored |
| expected | 362 / 0 / 6 ignored |
| ui / script-based-pre / json-handler / std-checks | 17 / 3 / 17 / 2 |

Totals 451 passed / 9 pre-existing ignores = CI-REQUEST (460 selectors). Every suite stage reviewed.

## S5 sensitivity mutations (`--force-rerun`, each on its selector)

| Mutation | Runner | Coordinator |
|---|---|---|
| positive-remove-useful-assertion | DETECTED_EXPECTED_MISMATCH | DETECTED |
| negative-extra-reached-failure | DETECTED_EXPECTED_MISMATCH | DETECTED |
| golden-invert-required-count | DETECTED_EXPECTED_MISMATCH | DETECTED |
| negative-repair-user-write | FAIL_OR_UNKNOWN ("permitted out-write check is missing") | **DETECTED** (manual) |

`negative-repair-user-write` on `maybe-uninit-contract-frame/main.rs` removes the forbidden `*outside` write. The mutant ran to
completion: native `** 0 of 331 failed (9 unreachable)`, `VERIFICATION:- SUCCESSFUL`; the golden requires
`Check that *var_7 is assignable` FAILURE and `VERIFICATION:- FAILED` → compiletest FAILED by the intended mismatch
(not compile error/timeout/early Unsupported). The runner's extra condition looked for the permitted out-write check under
its golden name `*var_8`; after removing the `outside` write the locals renumber and the same permitted `*out` write is
`Check 71 … Check that *var_7 is assignable — SUCCESS` (no `*var_8` exists). Name-binding artifact of the runner, not a
sensitivity gap. Same mutation was DETECTED on F (C2-S5 run 43641978948).

Obligations closed at 5: slice-1 head-5 (closure/contract/mode/root fixtures per CI-REQUEST), `generated-modifies-no-shadow`,
S5 mutations. Not Gate A, no proof credit. Next: stage 6 E1 on `96f5d5dc8d`.
