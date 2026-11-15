# Slice 03 LAYOUT-RAW — ACCEPTED as NO_REGRESSION (run 43706759714)

2026-11-15, coordinator. Fork run [43706759714](https://github.com/Tiramisu-Cake/kani/actions/runs/43706759714),
branch `uninit-ci/c2-slices-03-w15-r2`, overlay `34b8008f12ac909d53803ddb1a4da956c498c19f` (CI-only `.github/`) on source
`5ca51679e3f433718807a2e44add0d5abac128e7` (parent slice 2 `932fb8395a`). Supersedes `d0345ddf4f` (run 43704461635:
18 fixture pairs needing MaybeUninit arrays / raw-pointer+union support; moved to slice 4, production unchanged).

fmt/build/clippy exit 0; ActiveCalls 9/0/0; immutable 9/0/0; kani 50/0/3; expected 220/0/6; ui 17; script 3; json 17;
std-checks 2. Totals 309 passed / 9 pre-existing ignores = CI-REQUEST (318 selectors). Every stage reviewed.

Qualification **NO_REGRESSION**; slice-3 integration (nested Pat/enum, raw-eq-uninit multi-root, and the 18 moved
fixture pairs) is **PENDING on slice 4**. Slice-1 obligations PENDING on 4/5. Next: stage 4 STORAGE on `5ca51679e3`.
