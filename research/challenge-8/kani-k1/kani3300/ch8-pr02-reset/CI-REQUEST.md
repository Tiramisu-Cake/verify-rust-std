# CI request — one paired matrix run

- Package commit `b4edbb18bc8a490197420aac0964a7d55b284380`, tree `a5a1c0b0b06c8af67ec132f107883222e2d220c1`, source fix `f695f653efaa1f7ac6774a079104de8cc0ff81fc`, CI parent `cbcffa8365b65c0373e6bf71c3bf2d638b327ef4`.
- Local CI worktree `/root/kani-fix-ch8-pr02-reset-ci-w15`, branch `work/ch8-pr02-reset-ci-w15`. Source-only worktree `/root/kani-fix-ch8-pr02-reset-w15` remains at its source fix.
- Source patch SHA256 `52173eb8126f00e7cc3285f4b7bd4941e42cec78a9e822588e7bc9cce23ec91a`; full pins, trees, artifact hashes and limits are in CI-REQUEST.json.
- Coordinator creates the same-tree non-skip child of the package and pushes it to `uninit-ci/ch8-pr02-reset-*`. First run attempt only; no automatic retry; one matrix-run = one dispatch. This worker performed no push/dispatch.

Arm A checks patched standalone PR-02: Rust fmt, build, workspace Clippy (`--tests -- -D warnings`), compiler binary unit tests, expected uninit/immutable and function-contract suites, script-based autoharness suites including all seven new fixtures. The unpatched PR-02 control runs the exact same source bytes and argv for all seven cases. Three seeded controls must produce exit 1 and the exact reset-absent fatal. The old uninitialized-tail outcome is observational (completed success or intended UB failure), recorded without proof credit; its new fixture requires the intended UB failure. Positive companions require successful completion.

Arm B checks SEL1 plus this exact source patch against the byte-exact A1 original #4854 autoharness and explicit companion. It requires a successful single selected function/harness in both regular and schema-validated JSON output, with source/tree/stage/target/name/file/automatic identity bindings.

Both arms use ubuntu-24.04, 120-minute job caps, matrix max-parallel 1, cargo jobs 2, Rust test threads 2; native B uses jobs 1 and 600-second invocation limits. Checkouts have depth 2; runner contexts occur only in step env. CI-only stock workflow deletions do not modify the separately pinned build sources. Sibling control/source/old checkouts and absolute Kani paths keep working-directory bindings explicit.

Offline checks passed: package/YAML plus embedded GITHUB_OUTPUT execution, source reset invariants, five synthetic runner-result tests, shell syntax, whitespace and full patch application to C2/SEL1. Rust/Kani/CBMC compilation, native regression results and emitted-model evidence are NOT_RUN. Source-level reset count/order/nondeterminism/OFF checks and reviewer inspection do not establish emitted-model proof or B1/B2 credit.
