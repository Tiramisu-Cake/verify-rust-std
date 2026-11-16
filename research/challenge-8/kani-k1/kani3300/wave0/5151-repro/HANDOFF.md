# #5151 reproduction handoff

State: prepared for a future authorized CI stage. Runtime **NOT_RUN**.
The source comparison and success criteria are in `PACKAGE.md`;
`CI-REQUEST.json` binds the final control commit, tree and payload hashes.
The task input is g0 `18743fb816465180215fcd86410ecfd46763b0ed`.

Control commit `5725e5ca3df9d793c01f8ba45745c6ed133c3201`, tree
`4f9984d35c4caf019f041854a68bb65ffa70b81d`. Author `Tiramisu-Cake <igkharin@gmail.com>`;
message `[skip ci] Pass Rust 2021 compiler flags to issue 5151 harnesses`.

Control worktree: `/root/kani-ch8-5151-edition-w13`, branch
`uninit-ci/ch8-5151-edition-w13`. Its source parent is stock Kani `0aac16ef62`.
The control contains a dedicated workflow, runner, tests and pinned request.
The workflow uses separate tool checkouts for the two exact pins.
`CONTROL.patch` reconstructs the control tree from its stock parent; the
test files under this directory are identical copies for review.

The prepared commit carries `[skip ci]`. Future activation uses a same-tree
child of that commit in the dedicated branch family, first attempt, after
coordinator authorization. The workflow checks those activation identities
before setup. Existing workflow files are removed in the control overlay.
Publication and activation are pending a separate assignment.

Part 1 compares the initialized element-0 case, the unchanged element-1 issue
example and a destructor with an actual byte read. The original empty
destructor has a diagnostic completion oracle; successful verification there
leaves its invalid-drop detection open. `PACKAGE.md` declares the required
positive and byte-read negative outcomes before execution.

Part 2 has a compatible nightly pin and 56 source-inferred candidates,
including 19 using `PointerGenerator`. The historical 77 failing names remain
unconfirmed, and the static full inventory has 393 names against the reported
394. The missing mapping is explicit in `CHALLENGE2.md`; compilation/listing
and calibration precede any performance estimate or complete 77-case run.
The proposed 20/20/20/17 split reserves the entire confirmed inventory.

Artifacts and limits: see `CI-REQUEST.json`. Process errors, incomplete
verification and unstarted rows retain distinct states. Runtime outcomes and
proof credit remain pending; preparation closes zero proof obligations.

Static validation passed: 18 Python synthetic checks, frozen payload checks,
actionlint, whitespace checks and exact patch-to-tree reconstruction.
`validate.py` repeats the Git/hash/source inventory checks without compiling;
`VALIDATION.json` records the result. Review identities and scope are recorded
in `REVIEW.json`.

Pushes, CI dispatches, publications, ledger writes and local
Cargo/rustc/Kani/CBMC invocations: **0**. Concurrent g0 changes outside this
directory are preserved.

Edition follow-up: the owner reports all six rows in run 43878900159
(trigger dbfb4d8bd8) as UNKNOWN, with E0433 under Rust 2015 before verification.
The corrected candidate uses `// compile-flags: --edition 2021` in each test
and `RUSTFLAGS="--edition 2021"` in every standalone process, following the
upstream compiletest transport. The issue body and expected verification
outcomes are preserved. New synthetic checks cover the actual subprocess
environment and source headers, missing-edition rejection, and E0433 as UNKNOWN.
The new edition test fails on all three original fixture headers.

This replacement control is a new commit with the same sole stock parent,
preserving the workflow activation guard. The earlier published control and
trigger are retained. The new control and g0 revision are prepared locally;
new runtime outcomes remain NOT_RUN. The recorded prior run is user-reported,
and preparation adds zero CI dispatches or ledger changes.
