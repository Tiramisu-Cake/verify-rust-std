# A — READY for worker14/coordinator review; Gate A NOT_RUN

FREEZE source `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`.
Quick acceptance: `../quick/ci-43740679160/ACCEPTANCE.md` (run 43740679160).
CI-only overlay `b69a040ded46d5ee7edf35b8eb727b66e5838930`, parent exact FREEZE;
local branch `uninit-ci/sel1-c2-gatea-w15`, assigned worktree `/root/kani-fix-3300-sel1-c2-w15`.
Adapted from accepted c2-gatea run 43665002636 / working overlay `39bcdd7ad51dc169f75a9974e43717205553bad0`,
through the existing worker15 preparation package. No source/tests/docs/dependency changes.

Push trigger only: `uninit-ci/sel1-c2-gatea-*`; fork workflow_dispatch is unavailable.
All runner expressions occur in step env; all checkouts use depth2. The regression job checks out sibling
`control/` and `export/`; there is no checkout/Cargo.toml at their parent. Setup uses the frozen export action,
`kani_dir: export`; observer and lifecycle live in control, source checks use `../export`, regression cwd is export.
This Gate A has no structural JSON path normalization; those Quick commands were not copied.
The accepted Bash3.2 owner guard remains unchanged. Source identity is checked before setup, after setup and after regression.

Matrix exactly ubuntu-24.04 / ubuntu-24.04-arm / macos-15; fail-fast false, max-parallel3, one attempt, no retry.
Full unchanged `bash scripts/kani-regression.sh`, 33 ordered stages, all suites; no filters/new ignores/check disables/RSS-watchdog.
Job360min, regression≤20400s, reserve600s; compiletest2400s/test. Events256MiB, metadata16MiB,
artifacts384MiB/platform, retention14d. Process-group timeout preserves original exit/signal;
artifacts always, fallback partial receipts, aggregate missing/failed-row checks remain intact.
Exact binding covers22 files/9 subtrees/3 submodule pins/10 symlink targets. Setup/toolchain/dependency pins come from FREEZE.

Local checks: targeted offline YAML/context/shell/binding checker, four known-error mutations rejected,
26 synthetic observer/lifecycle tests, Linux shell self-test PASS. No native build or verification run.
Worker14 must review before coordinator launches; see HANDOFF.md for publication details.
Complete three-platform receipts and coordinator acceptance are still required. UNKNOWN/truncation/lost rows never imply PASS.
Explain counter differences from C2 by SEL1 additions; do not transfer historical totals or acceptance.
Formal proof credit NOT_ESTABLISHED.
