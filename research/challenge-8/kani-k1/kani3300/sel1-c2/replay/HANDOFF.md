# SEL1-C2 worker15 — B preparation READY, runtime NOT_RUN

Source FREEZE `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`.
CI-only package `fff42ed46992c7d00463a21561093cfde5dce330`, parent FREEZE, `[skip ci]`.
Ready-to-push trigger `1ce0b1e5b62660bdc5809318689eeea287af064c`, parent package, empty diff and no skip marker.
Both trees `6f118da84a311c0e28316fb80f4020122535592d`.
Worktree `/root/kani-fix-3300-sel1-c2-w15`, local branch `uninit-ci/sel1-c2-replay-w15`.
No local build/verifier, push or dispatch was performed. No Kani source/std-test/oracle edits were made.

Coordinator: first accept all three Gate A rows of run43744142824 on the same FREEZE; this preparation grants no early B run.
After review verify the exact trigger/package/source chain, identical trees and a fresh matching fork branch.
Push the exact trigger once to `https://github.com/Tiramisu-Cake/kani.git`, e.g. `uninit-ci/sel1-c2-replay-r1`.
Do not create another trigger or use workflow_dispatch; this trigger already has no skip marker.
Check remote head/run head equal1ce0b1e5b62660bdc5809318689eeea287af064c, expected replay workflow, run_attempt1,
six unique matrix rows, max-parallel1. No automatic retry or alternate run.

Wiring checklist:

1. Push branch `uninit-ci/sel1-c2-replay-*`; fork-only guard, concurrency cancellation disabled, run attempt1 enforced.
2. The only runner expression is in upload-step env RECEIPT_ROOT; with.path uses env.RECEIPT_ROOT.
3. Control/export checkout declarations both fetch-depth2 and persist-credentials false; exact control github.sha.
4. Siblings `control/` and `export/`, setup kani_dir export. Wrapper commands run at workspace parent, loading control scripts;
   actual replay child cwd is isolated RUNNER_TEMP std root, so `./library` resolves there. Binary is absolute export/scripts/kani.
   Output substitution uses the absolute receipt parent plus the exact row ID; target/export are outside both source checkouts.
   No structural comparison or path-normalization prefix is involved in this replay.
5. No checkout at the sibling parent, no Cargo.toml there; std is outside the source workspace. Control cannot enclose export/std.
6. This workflow targets ubuntu-24.04 only and installs no BASH_ENV observer hook; the macOS Bash3.2 guard is specific to Gate A.
7. check_workflow.py reuses A's YAML1.2/duplicate-key/context scanner, checks shell and inline Python syntax, paths/caps/flags,
   all source hashes and nested checksums, exact std patch/five files, and rejects four known wiring-error mutations.
   It is an offline targeted checker, not full upstream actionlint or runtime qualification.

Source570/7 binding regenerated; all548 uninit/json-handler files rediscovered.
Request roots/argv/environment/modes/unwinds/covers/flags match the prior six-row preparation exactly.
Std70ba + test-only6075 and the473526895d patch remain exact. Actual closures, preconditions and oracles unchanged.
The exact embedded test patch preserves historical whitespace; whitespace checks exclude that immutable patch only.

Localized runner fixes: sort4 parse review hint now requires SUCCESS and3/3 covers including return;
post-run std validation also checks HEAD/tree/library-tree (new drift controls). Existing failed/missing/null/wrong-type/
wrong-selector/partial/timeout/signal/exit/RSS/source-drift/postprocessing controls retained. Synthetic30/30 passed.
Independent static review PASS; exact identities and limits in REVIEW.md.

After CI, curate all six complete receipts plus stdout/stderr/export/runtime identities and selected PFC bodies.
Five legal rows require0 failures and covers5/2/3/6/2 respectively, with reached return/ensures/frame/readbacks.
Raw-negative must have exactly the intended uninitialized u64 source[1] read at the bound smallsort operation;
retain every failed property, original exit1 and source/name/location binding. Any other refusal/failure is unexpected.
Raw-negative execution intentionally remains nonzero; review the intended oracle separately from job infrastructure status.
Fallback/partial/UNKNOWN receipts require review. Compare inventories to C2 B-prime and old SEL1, explain added/removed checks
and unreachable; totals are references. Record exact CI run/head and actual tool/solver hashes. No claim for all SmallSort/T,N/#5104.
