# U-02 — one arm A run prepared

Package `952ea771be3827a495a9c9f29ad6a015bd796fc7` (tree `6635864584be3049f96e146cb548b348101b0064`), source `09a6d1cb2cba63e67e60aeefbd909d1f64849b76` directly on PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962`. Exact pins, patch hashes and worktrees are in CI-REQUEST.json. The new source commit replaces U-01's source candidate locally; no published branch was rebased or forced.

All seven regression directories are now `tests/script-based-pre/autoharness_entry_reset_<case>/`. Their 28 files and modes are identical to U-01, including all expected outputs. The fixture filter and old-control/static lookup paths were updated. `COMPATIBILITY.json` records every byte identity and isolated PR-02/SEL1 patch application tree.

Only A is in the U-02 matrix. Compiler diff SHA256 is `f7beb5f9fc63e3a0a63536c44b922f07937d91829ecb551a3cbea3d517f232da`, identical to U-01; B runner and exact original/companion inputs are unchanged. Retain U-01 B SUCCESS as reported by the coordinator task, without a new B run or new proof credit; see RESULT-U01.md.

A retains fmt, build, workspace/test Clippy with `-D warnings`, compiler binary units, compiletest build, affected uninit/function-contract suites, seven reset fixtures, existing autoharness suite, and seven matched old PR-02 controls. The three seeded old controls must exit 1 with the exact reset-absent fatal. The old uninitialized-read observation retains its earlier permitted outcomes; new negative expected bytes are unchanged.

A now streams each native gate through a bounded recorder: original process exit plus at most 16,384 output bytes per gate, with explicit error/timeout/partial states. Gate timeout is 6,900 seconds under the unchanged 120-minute job cap; compiletest still uses 600 seconds. Always-finalize records request identities, action outcomes and NOT_RUN for unstarted gates; always-upload publishes `ch8-pr02-reset-a-${run_id}-${attempt}`, retention 7 days. Artifact contains receipts and bounded tails only. No observed-model binding or proof acceptance is inferred from those receipts. Initial control-checkout failure or runner loss can prevent artifact creation.

Coordinator: after review, create one non-skip child of the exact package with the identical Git tree and push to a unique `uninit-ci/ch8-pr02-reset-*` branch. Existing first-attempt/same-tree/repository gates, ubuntu-24.04, max-parallel 1, cargo jobs 2, Rust test threads 2 and no automatic retry remain. No dispatch is performed or authorized by this preparation stage.

Static package/source checks and seven isolated synthetic tests passed. Native compile/regressions/verifier/model and U-02 CI are NOT_RUN. No push, publications or ledger changes.
