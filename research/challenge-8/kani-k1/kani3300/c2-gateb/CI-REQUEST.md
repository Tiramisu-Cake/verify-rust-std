# Coordinator handoff — preparation only

Local branch ci/kani3300-c2-gateb-w15, parent frozen ad499e41dd2db9ccd432f89721638a1f3a0bbd44; exact one-commit overlay SHA in PACKAGE.json and INPUTS.json. No push or dispatch performed/authorized here. Coordinator owns review, publication of CI overlay and execution. No PR/issue.

Workflow .github/workflows/kani3300-replay.yml has push trigger restricted to ci/kani3300-c2-gateb-w15 and Tiramisu-Cake/kani guard. It checks out overlay beside exact C2 export, runs Python-only preflight, verifies source bindings, uses C2 .github/actions/setup (os ubuntu-24.04, kani_dir export), then builds export in CI. Std clone/apply runs only in CI using unchanged run4 URL, --destination and submodule initialization.

Exactly three ON rows in order raw merge, concrete profile merge, sort4. GitHub-hosted ubuntu-24.04 X64, fail-fast false, max-parallel 1, Kani --jobs 1. One attempt, no automatic retry; 2400 s/root, 60 min/job, 180 min total including setup/reporting. Full 3-row cap is a coordinator handoff configuration, not permission to execute in this session. Cloud budget $0. Phase/ledger remain unassigned; no coordinator or ledger edits.

Artifacts always uploaded per row, including fallback NOT_RUN if setup/build/preflight fails; original stdout/stderr/export, hashes/byte counts, receipts, effective argv/environment, original exit/signal/timeout/RSS, runtime identity inventory and full target artifacts retained by existing runner. Coordinator must preserve full failures/Unsupported and bind selected PFC target, useful ensures/checks/covers. Seven-day artifact retention; archive according to coordinator policy. UNKNOWN is never a PASS.
