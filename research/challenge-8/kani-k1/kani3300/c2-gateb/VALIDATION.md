# Preparation validation

27/27 Python-only wrapper tests PASS. Original 20 retained; seven C2-specific tests added. Coverage includes original exit/signal/timeout/exec error and atomic receipt preservation; missing/partial/null/wrong-type/wrong-selector export; request/cap/hash validation; C1/wrong HEAD/tree/dirty binding rejection; three mocked C2 argv executions with source/std validation and UNKNOWN/no-credit behavior. No Rust, Cargo, Kani, CBMC or build executed. Details: VALIDATION.json.

Exact C2 verify-source PASS: ad499e41dd2db9ccd432f89721638a1f3a0bbd44 / 9829702c1aa0ecb73c860fc0ad5451757917d6cb, 504 file SHA-256 and 6 subtree IDs. Source setup chain identical to C1 and current driver declarations inspected for replay flags. Setup and observer compatibility are static preparation checks, not runtime qualification.

Reproducible static package check: PYTHONDONTWRITEBYTECODE=1 python3 validate_package.py (run from this package or by absolute path). Checks every PACKAGE and nested manifest checksum/copy, exact one-commit C2 parent, CI-only changed paths, original source worktree cleanliness, std base/overlay trees, all four patched file hashes and exact unchanged patch bytes against C1, and semantic row/profile equality. The immutable C2 source is checked through its read-only worktree. git diff --check required on both commits.

Original C2/std/SEL1 worktrees keep their entry HEAD/tree and clean status; INPUTS.json records before/after. Std patch SHA-256 af2d6e7bce1d628ab7b56363578e9aa1393aa1e02be72786ae277d34a43892a5. Kani overlay delta consists only of its own workflow and scripts/kani3300-replay files; Kani source under it is unchanged. No target/artifact copies, local builds, push, CI dispatch, external publication, or coordinator state edits. Review is explicitly pending coordinator, as assigned by this task. No independent review claimed.

All replay rows NOT_RUN; receipt outcomes remain UNKNOWN until explicit coordinator review. Formal proof credit NOT_ESTABLISHED. Preparation readiness does not establish the C2 row oracles.
