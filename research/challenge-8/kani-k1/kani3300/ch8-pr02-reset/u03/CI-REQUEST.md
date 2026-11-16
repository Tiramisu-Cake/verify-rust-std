# U-03 arm A request

Local preparation only. Source `f7e89f1942fa6f671f20ec45fde98d9d736dc122`
directly on PR02 `932fb8395a58f8c86c0d702ba2cae835823b2962`; CI package
`80d0d98529445088db2fd2941fe9370ba6c0eaa6`, tree
`4237f7d2c8d86f28655a88824480da2e7c911b6b`, on U-02 package `952ea771be`.
Exact source/pin/tree/patch identities and worktrees are in CI-REQUEST.json.

Arm A keeps fmt, build, clippy, compiler binary units, compiletest build,
expected uninit/function-contract, all seven reset fixtures, generic autoharness
and matched old PR02 controls. A failed gate accumulates failure and preserves
its receipt's original exit. Once the patched source builds, every later gate
runs, including after compiletest-build or reset-fixture failure. A failed source
build leaves dependent gates NOT_RUN. Workflow A execution is independent of
earlier structure/test/old-build failure after successful patched apply/setup;
the job still retains all earlier failures. Finalization/upload remain always.

The negative reads byte 1 of `#[repr(C)] Bytes { a: u8, b: u32 }` on the pinned
`x86_64-unknown-linux-gnu` target. The companion writes byte 1 in place and then
reads it. Expected negative: uninitialized-u8 FAILURE; companion: SUCCESS.
All expected outputs and the other five fixtures are unchanged.

Arm B is omitted; retain the task-reported U-01 success. Compiler diff SHA256
`f7beb5f9fc63e3a0a63536c44b922f07937d91829ecb551a3cbea3d517f232da`
matches U-01/U-02/U-03; B runner and its exact issue inputs also match.

After reading REVIEW.md, a separately authorized coordinator can create one
same-tree non-skip child of this exact skip-CI package and push it to a unique
`uninit-ci/ch8-pr02-reset-*` branch. The existing first-attempt/equal-tree gate,
one A job, 120-minute limit, max-parallel 1, Cargo jobs 2/test threads 2 and no
retry remain. A changed package tree is outside this handoff.

No push, CI, publication, ledger mutation or local native tools were performed.
Static/synthetic preparation supplies no new runtime/model/proof credit.
