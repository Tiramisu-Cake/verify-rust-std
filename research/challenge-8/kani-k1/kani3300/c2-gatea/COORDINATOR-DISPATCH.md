# C2 Gate A — coordinator dispatch notes

Frozen export ad499e41dd2db9ccd432f89721638a1f3a0bbd44 (remote fix/kani-3300-c2-s6 and freeze/kani-3300-c2 verified equal before push).
Worker15 overlay e795403859 (26 synthetic tests re-run locally by coordinator: OK; self-test PASS on Linux bash 5).

1. **Trigger.** `workflow_dispatch` cannot reach a workflow absent from the fork default branch, and the fork main is not synced.
   Coordinator commit c7be548c6b switches the trigger to `push` on the single branch `ci/kani3300-c2-gatea-w15`
   (same model as the C1b gate). Nothing else changed.
   → run **43661248113** (ubuntu-24.04, ubuntu-24.04-arm, macos-15), one push.
2. **macos-15 row failed before regression**: observer self-test "synthetic success/child shell event observation failed".
   Diagnostics 43661512006 / 43661594596 (macos-15, no Kani): `/bin/bash` is 3.2.57; while reading `BASH_ENV`
   bash 3.2 sets `$0` to `bash`, so the hook guard `$0 == scripts/kani-regression.sh` never installed the traps (0 events).
   printf NUL/\036 and DEBUG/EXIT traps work on 3.2.
3. **Observer fix** f6eca52d32 (on c7be): top-level shell identified only by `KANI_GATE_OWNER_PID` (the observer starts the
   regression shell directly; children inherit the exported owner variable and are not instrumented). Local: 26 tests OK, self-test PASS.
4. **macos-15 row rerun**: 8d4a36667b (on f6eca52d32) — matrix `[macos-15]`, branch `ci/kani3300-c2-gatea-w15-macos`,
   separate concurrency group → run **43661668298**. Self-test PASS on macOS, regression started.
   Same frozen export; only CI overlay differs. Linux rows of 43661248113 ran with the original hook (bash 5, self-test PASS).
   The aggregate summary job of each run will mark the other rows missing; the 3-platform verdict is assembled by the coordinator.

## Run 1 result — INFRASTRUCTURE FAILURE (not a C2 result)

43661248113 (ubuntu-24.04, ubuntu-24.04-arm) and 43661668298 (macos-15): on all three platforms stages 1–17
(cbmc … suite:ui) completed with exit 0 (units 42/76/215/4/0/2/6/7; kani, expected, ui suites 0 failed), then
`suite:std-checks` failed 5/5 in 0.1 s: `cargo metadata` — "current package believes it's in a workspace when it's not:
current export/tests/std-checks/core/Cargo.toml, workspace /home/runner/work/kani/kani/Cargo.toml". The control (overlay)
checkout sat at the workspace root and its Kani `Cargo.toml` enclosed `export/`. Script stopped (errexit); stages 19–33 NOT_RUN.
Receipts: `run1-infra/`. C1b passed std-checks 5/5 with a different layout.

Fix 39bcdd7ad5 (on f6eca52d32): control checkout at `control/` beside `export/`; observer/lifecycle steps run with
`working-directory: control`, `--source-dir ../export`; regression still runs in `export/`. Three-platform matrix restored,
trigger branch `ci/kani3300-c2-gatea-w15-r2` → run **43665002636**.
