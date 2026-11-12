# CBMC ZST-BITS2EXPR — STOP
Status: SOURCE_AND_CI_PACKAGE_READY / NOT_COMPILED.
Base: 107a1e504cd69a2f3483717c8bcfcfa59814c557 (upstream develop unchanged).
Source: c0850c029faed04f8666de7f89045b5f04d246e1, branch fix/zst-bits2expr.
CI-only: 64a077ab6767c7a91fc9141bfac08423d5424bf7, branch ci/zst-bits2expr-20261113.
Source parent is exact develop; CI-only parent is clean source.
Fix: allow known zero element width only in bits2expr array guard.
13 independent GNU C cases; 3 focused public util unit cases; nonzero bytes preserved by oracles.
Literal owner and Kani-like C fixtures included separately; no actual Kani replay.
One Luna High static review complete; Low pre-existing invalid-count edge documented.
Static type/signature audit, diff checks, test-only overlay tree check and workflow inventory complete.
6 isolated synthetic Python runner checks PASS; no compiler/verifier executed.
Baseline with test-only overlay differs from source tree only in simplify_utils.cpp.
CI-only removes all 21 inherited workflow-directory files; exactly one new workflow remains.
Build/unit/regression/CBMC/formatter/CI: NOT_RUN. Develop crash remains unmeasured.
Push/dispatch/issue/PR: none. Cloud $0. No reset/stash/force or foreign file removal.
Coordinator receives CI-MANIFEST.json, separate source/CI patches and CI-REQUEST.md.
Next: coordinator-only paired C CI; if develop does not reproduce, STOP without historical proof credit.
No Kani#5085/case B closure; B3 workaround unchanged; planner/history preserved.
READY c0850c029faed04f8666de7f89045b5f04d246e1
