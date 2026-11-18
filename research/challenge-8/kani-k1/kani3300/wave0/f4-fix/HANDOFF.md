# READY_FOR_REVIEW — W15 standalone F4 fix

Task `task7b829344c9cdd8c25ec59294bb9015201638a879` was explicitly issued by the user;
the task file's earlier PREPARED_NOT_ISSUED marker is superseded by that GO.

- Isolated source: `/root/kani-f4-fix-w15`, branch `w15/f4-fix-main`.
- Source commit: `cab66681c912a3e5ee01a106faaeee5237ca0232`.
- Source tree: `8585336ed35a14fe0fc157a7ca4e0d52075c0e49`.
- Direct parent/frozen main: `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.
- Base tree: `09b828b47c93e90e140e8c41f9048109a2f4a786`.
- Exact nine-file patch and SHA-256/source/blob/workflow inventory: `fix.patch` / `MANIFEST.json`.
- Source author: Tiramisu-Cake <igkharin@gmail.com>; commit includes `[skip ci]`.
- Source Git objects are shared with the existing Kani repository; no remote source published.

Compiler change: clone the warmed unit transformer for each harness before global passes and
codegen, preserving pass configuration and the body/loop metadata relationship. See
SOURCE-LIFECYCLE.md for applicability, invariant, alternatives and allocation/performance risk.
The compact upstream regression retains the exact observed fixture, both cfg variants and
independent unsafe control; no confirmation workflow/profile/runner is copied into PR source.
All 16 standard workflows and all scripts are unchanged against frozen main; no deletions.

Static validation PASS (`VALIDATION.json`, repeatable `validate.py`); patch replay reproduces
the committed tree. Main's observed compact results FAIL the new oracle. Synthetic expected-fixed
inventories PASS. Actual new-test main execution, fixed compiler build/runtime and standard CI
are NOT_RUN. Compilation order UNKNOWN; bounded reproduction carries no general proof credit.
The immutable intake/review inputs and hashes are recorded in MANIFEST.json.

Next: coordinator hands the exact committed g0 package plus exact source SHA/tree to review14.
Reviewer should inspect code/cache lifecycle, cloned pass/loop metadata consistency, regression
admission and unchanged controls, and full-CI/performance plan. Review14 remains pending; this
READY makes no review/CI/publication authorization claim. Fix concrete findings before any
owner-authorized publication or CI. No review message has been sent by this stage.

PR-DRAFT.md is prepared, unpublished; pending Testing wording must become actual full-CI
wording/link after authorization and execution. CI-REQUEST.md/json requests the complete future
standard PR workflows/matrices plus applicable label-gated benchmarks. Owner publication command
and separate full-CI GO are still required. Item1 remains reference 27/28; attempt28/28 unspent;
S2 accounting ledger4076 untouched. No local compiler/rustfmt/full runner, CI/rerun/cancel,
push/PR/message/reservation/ledger edit, subagent or model/fast change was performed.

Upstream main was checked read-only and matched frozen main (MAIN-CHECK.json). Fork main is
an older ancestor and is not the upstream PR base. Recheck upstream before publication;
relevant drift requires explicit handoff, never silent rebase. The source `[skip ci]` commit
needs a separately authorized same-tree trigger for future CI; this stage creates none.

The g0 package identity is the enclosing commit containing this HANDOFF; resolve with
`git log -1 --format=%H -- research/challenge-8/kani-k1/kani3300/wave0/f4-fix/HANDOFF.md`.
