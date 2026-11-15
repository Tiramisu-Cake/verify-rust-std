# Slice 07 F7 — ACCEPTED (run 43723531871); C2 slicing complete, final tree = freeze

2026-11-15, coordinator. Fork run [43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871),
branch `uninit-ci/c2-slices-07-w15`, overlay `8288537e7c57b04d2462ff0c5bf1af38ab9d4451` (CI-only `.github/`) on source
`8e299aa6243bc5f06a29c51e98aafa9564478220` (parent slice 6 `3f5242bb15`). Job success.

**Exact recomposition (coordinator-checked locally):** `git rev-parse 8e299aa624^{tree}` =
`9829702c1aa0ecb73c860fc0ad5451757917d6cb` (= freeze `ad499e41dd` tree); `git diff ad499e41dd 8e299aa624` empty.

fmt/build/clippy/LLBC build exit 0; units: ActiveCalls 9, immutable 9, argument_size 1, marker_category 1, delayed_cache 6,
delayed_scope 2, all compiler 76 — 0 failed; kani 50/0/3; expected 373/0/6; ui 17; script 3; json 17; std-checks 2.
S5 mutations 4/4 DETECTED. Structural isolation: `PASS_EXACT_FRESH_MIXED_VS_OWN_ISOLATED` — 11 completed invocations,
18 exact mixed-vs-own-isolated comparisons; the five exit-1 runs are the intended negatives / cycle Unsupported
(`expected_exit` 1 in summary), not failures.

## Final stack on U `0aac16ef62` + B1 `6fe484b300` (kani#5172)

| # | Commit | Subject | Qualification run |
|---|---|---|---|
| 1 | `d82752c8bc` | Analyze selected contract bodies and detect active call cycles | 43696666260 (NO_REGRESSION; integration closed at 4/5) |
| 2 | `932fb8395a` | Seed exact immutable allocation masks and coalesce qualified aliases | 43701587141 |
| 3 | `5ca51679e3` | Check raw equality byte extents and preserve nested layout offsets | 43706759714 (NO_REGRESSION; integration closed at 4) |
| 4 | `345cedfd67` | Track MaybeUninit storage and pair shadow transfers across calls | 43710024495 |
| 5 | `96f5d5dc8d` | Compute initialization masks for closure environments | 43715788377 (S5 4/4) |
| 6 | `3f5242bb15` | Qualify initialization edge cases and document experimental limits | 43720042056 |
| 7 | `8e299aa624` | Isolate delayed instrumentation within each model codegen scope | 43723531871 |

Gate A (43665002636) and Gate B′ replay (43683557088) qualify the final tree (identical to freeze); intermediate heads are
qualified by their own fork Quick runs. Next (separate stage): PR texts / stack publication — owner decides.
