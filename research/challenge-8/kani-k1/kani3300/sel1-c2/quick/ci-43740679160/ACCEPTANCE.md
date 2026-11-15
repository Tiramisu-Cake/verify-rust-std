# SEL1-C2 Quick — ACCEPTED (run 43740679160); FREEZE 14bc57fdb9

2026-11-15, coordinator. Fork run [43740679160](https://github.com/Tiramisu-Cake/kani/actions/runs/43740679160),
branch `uninit-ci/sel1-c2-quick-w15-r6`, CI-only overlay `568f10ed6540bc46046e3571044e10a262a14b42` on source
**`14bc57fdb99960240c4944845a3d985c8af4dcf7`** (parent C2 `8e299aa624`; tree `1efb6e4dfa69d346df8e23741d11839b1932403d`).

fmt/build/clippy/LLBC exit 0; units ActiveCalls 9, immutable 9, argument_size 1, marker_category 1, delayed_cache 6, delayed_scope 2,
all compiler 76 — 0 failed; kani 50/0/3; expected 402/0/6 (373 C2 + **29/29 select-unpredictable controls ok**); ui 17; script 3;
json 17; std-checks 2. S5 mutations 4/4 PASS. Structural `PASS_EXACT_FRESH_MIXED_VS_OWN_ISOLATED`: 11 invocations, 18 exact
comparisons; exit-1 runs are the intended negatives / cycle Unsupported (`expected_exit` 1).

Overlay repairs before this run (CI-only, worker15 package `4ef74e822b` + coordinator commits; no source/test change):
- `a8dad427d3`: push trigger (fork `workflow_dispatch` cannot reach non-default-branch workflows); `${{ runner.temp }}` removed from
  workflow-level `env` (invalid context → workflow rejected, run 43736056775/43736186940); source checkout `fetch-depth: 2` for the
  `HEAD^` parent check (run 43736186940).
- `0e2888a686` + `568f10ed65`: structural runs executed from the control/export parent with that parent as normalization prefix,
  expected input `control/.github/c2-slices/structural-mixed.rs` (Kani renders the input relative to cwd; runs 43736295143,
  43738530114 stopped at "selected root came from wrong input" before any comparison).

FREEZE: source `14bc57fdb9` for Gate A (3 platforms) and the six-row SmallSort replay. Any source/test/docs change → new head.
