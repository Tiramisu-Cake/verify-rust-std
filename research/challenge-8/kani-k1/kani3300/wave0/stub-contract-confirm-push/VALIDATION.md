# Static and synthetic validation

PASS: full validate.py, 71 inherited counted mutation cases and 63 new push identity/final-head gate cases. The suite retains synthetic process success/nonzero/signal/timeout/RSS/output/spawn controls; build failure, missing/partial target, diagnostic/export strictness, independent slots, setup/finalization and rich result integrity. No compiler, Kani, CBMC, MIR, expansion or actual CI execution occurred.

The adapter tests reject missing context; workflow_dispatch/schedule and wrong repository/head/ref; empty/tag/invalid branches; event ref/head/repository mismatches; legacy environment identities and payload inputs; wrong creation/force/deletion/before topology; wrong/partial/malformed head payload; stock/profile mutation; untracked source and depth1 source/control. Each runtime negative is paired with a mock that would fail if build execute were reached.

Final-head tests cover exact no-skip candidate and a direct same-tree sibling; SHA-only input, wrong head/tree/parent/profile/request/ref, stale candidate request, merge/multi-commit topology and all GitHub skip directive forms. The sibling runtime snapshot must match the independently computed final-head request. Gate reads leave HEAD/worktree unchanged. The real stock/control preflight is read-only with a synthetic GitHub event, establishing local identity admission only.

INVARIANCE.json checks exact projected snapshot-only runner change; all other 16 functions unchanged by AST, byte-identical fixture/service/workflow-context checker/schema/oracles, identical source maps/caps/argv/env and equal workflow jobs after removing dispatch inputs. Full source/compiler/build/setup/library/docs/tree boundaries and both patch replay checks pass. Frozen prior packet/control/review/GO identities remain unchanged.

One initial disposable-Git test failed because its sibling object had not reached the depth2 clone. The corrected test fetches each exact sibling at depth2 before checkout; the final suite passes. No real source/runtime failure was observed.

Reproduce with PYTHONDONTWRITEBYTECODE=1 python3 validate.py. After the report/manifest are sealed, use validate.py --verify-only for final identity/manifest/invariance verification. VALIDATION.json and MANIFEST.json are immutable evidence in the containing g0 commit. Native confirmation remains NOT_RUN and independent credit NONE.
