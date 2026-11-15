# S1 batch — Kani host, preparation only

Control: `36db70978a16144624abf94d480a593dae684451`, tree `f3d36d51f58bf7937f6f8778260e3e2816996b48`; single parent `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Repository `Tiramisu-Cake/kani`, branch `uninit-ci/ch8-s1k-w13`.
Only `.github/workflows/` and `ch8-s1-control/` differ from parent; all 16 stock workflows removed, only `ch8-s1.yml` remains.

Production std: `Tiramisu-Cake/verify-rust-std@75a4d1ea6eb60c63c27c1b18e662740d93bafb08`, tree `6d1b90bc11440762c9b65889fc538ba3071b0d9d`; depth 2, submodules true.
Stock tool: `model-checking/kani@0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`; depth 2.
Control uses github.sha, depth 2. Layout: control/export/tool are siblings. Build tool, epoch and receipt paths are normalized from step cwd; runner is unchanged.

SHA256 manifest: `MANIFEST.sha256`, digest `e6daee66ba73a15f393d4f2fdfb70c9abb2bd22d3859efb46ba5ed5de2ecad52`. Entries are relative to `/root/kani-ch8-s1k-w13` and include the complete in-control request. Request SHA256 `ba0e2e57be25502d47cc9223e05a324afddeb60a8280d3cf2b0081c0fe045d89`.
`CI-REQUEST.json` records the full changed-path inventory and immutable identities; `BATCH-IDENTITY.json` records byte equality with original std control `f88bf3f0ea0ef1f87ca01ba5da11b57be574adf1`.

All 23 rows, oracles, variants, source hashes, flags and resource caps match the original request. Runner, original runner tests and both patches are byte-identical. Only request payload/path inventories changed. The checker delta changes host binding and validates explicit checkout repositories; additional synthetic tests exercise the migrated binding and unchanged failure handling.

One 120min job, max-parallel 1, existing setup/phase/reserve and row/output/RSS caps unchanged. No push, CI, publication or ledger operations performed. All proof rows NOT_RUN; credit NONE. Coordinator authorization remains required for dispatch and any duplicate-run cancellation.

The control message contains `[skip ci]` as requested. A future push of this exact commit suppresses Actions; activation requires a separately authorized same-tree sibling commit without the skip marker, still with parent tool0aac, and recording its new SHA. Do not append a child commit: the single-parent exact-tool check would reject it. No activation was performed here.
