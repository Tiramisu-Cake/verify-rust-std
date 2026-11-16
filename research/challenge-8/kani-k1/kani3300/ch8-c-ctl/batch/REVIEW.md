# Independent C batch runner review

## Findings

No blocking static or synthetic finding remains in candidate `64ec781bc119279ccc4365aa831d2a9d0a792fee` (`33e95dc779cefde33132f8e265d9588b9d905b14`). The review compares it with baseline `cdd3c6d04112cc1b1e1a80a850389236647bc849` and includes the lifecycle and export-validation deltas after `f30f9851b842881743de273a1e64392d80e22dc7`.

The following review blockers found in intermediate `f30`/`c52` candidates are resolved in the final candidate:

- Group and batch receipts cannot claim complete on a cap, signal, termination, missing export row, or process exit inconsistent with the terminal harness outcomes. A nonzero exit remains valid when a selected harness reports a completed failure, as expected for the declared DETECTED row; the runner compares the exit against the full terminal harness inventory (`ch8-c-control/runner.py:972-1034,1205-1214`). Completed roots in a genuine `PARTIAL` export retain row diagnostics, while the aggregate remains `PARTIAL`.
- Compile boundaries require a fresh size-bounded INCOMPLETE marker with the pinned tool, target, timeout, and selector identity. The compile receipt keeps its marker digest and immutable bounded head/tail snapshots (`runner.py:309-365,405-430,534-551`). The pinned tool writes the marker after `std_project` compilation and target discovery, immediately before the harness checking loop (`kani-driver/src/main.rs:149-174,192-198`; `kani-driver/src/frontend/schema_utils.rs:54-65`).
- Post-spawn monitoring exceptions now terminate and reap the process group, join started readers, and preserve monitor, cleanup, signal, and exit details. Normal completion also kills remaining group members before returning (`runner.py:309-347,405-531`).
- Terminal JSON requires the exact top-level `outcome: {"kind":"COMPLETED"}` in the single-root parser, batch parser, and expected-exit derivation (`runner.py:571-580,773-798,972-1003`). Missing, null, wrong-type, NOT_RUN, and extra-field outcomes are covered by a synthetic mutation test.
- The parser binds each root to `core`, explicit/manual metadata, exact PFC target and contract shape, the frozen global target/timeout/check configuration, positive check inventory, and unique well-formed failed-property records (`runner.py:594-681`).
- The source-base receipt uses the frozen request value; offline inventory avoids a second Kani list/build. The frozen request rows, source file hashes, flags, source/tool pins, variants, and control supersession binding match baseline. Grouping remains seven unwind-8 roots plus one unwind-12 root, with 6,600 seconds total group allowance.

## Validation

- 33 isolated Python synthetic tests passed.
- `py_compile`, the workflow YAML package check, `actionlint`, and `git diff --check` passed.
- Independent static comparison confirmed frozen rows, source hashes, flags, and source/tool identities are unchanged; manifest entries, manifest digest, and payload hashes match.
- No Rust, Cargo, Kani, CBMC, CI, push, or ledger operation was run.

## Limitations and readiness

This is a package-preparation review only. All eight roots remain NOT_RUN and proof credit remains NONE. Actual proof/runtime compiler binding and resource behavior are unverified. Successful assertion labels and source-cover-description-to-export-ID correlation remain pending independent runtime review, as recorded in the unchanged C oracles.

The local skip-CI candidate is not the activation commit. The package `control` command requires a direct `0aac16ef62da9e9d5645782d458593e5d78143ba` parent; the eventual activation must use the documented same-tree sibling commit. This review does not authorize dispatch or activation.

**Decision:** static package review passes for preparation. Runtime/evidence review and separate dispatch authorization remain outstanding.
