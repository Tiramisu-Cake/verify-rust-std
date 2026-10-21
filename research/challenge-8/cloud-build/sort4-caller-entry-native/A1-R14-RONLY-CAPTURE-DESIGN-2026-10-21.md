# R14 design: fail-closed R-only structural AST capture

## Finding

The captured artifact can be useful as a structural reference even though its invocation exits 1, but the current collector does not establish that this particular exit was the known post-dump duplicate-prototype error. The current evidence therefore supports retaining the structural comparison only as **INCONCLUSIVE** until an exit/diagnostic gate is added. It does not support calling the nonzero stage successful verification or granting body/conformance/proof credit.

In the pinned VeriFast source, `vfconsole.ml` registers `-dump_ast_with_locs` as a dump request (`src/vfconsole/vfconsole.ml:629`), and its emitter callback serializes the complete parser-produced package list (`:670-679`). `CheckFile1` invokes that callback at module initialization (`src/verifast1.ml:1230-1234`) before its subsequent checking work. The duplicate-prototype error is raised later while iterating function declarations (`src/verify_expr.ml:505-535`, exact error branch at `:534`). Consequently, when that exact verifier error appears after this callback returns, the preverification package AST has already been handed to the writer and the intended P1 interface can still be checked structurally.

The writer is **not atomic**: `Ocaml_expr_formatter.print_ocaml_expr_to_file` uses `open_out`, prints directly, then closes (`src/frontend/ocaml_expr_formatter.ml:86-89`). A process interruption can leave a created but incomplete file. The collector protects against stale reuse by requiring a fresh destination (`a1-runner.py:1416-1419`), requires the AST file to exist (`:1441-1442`), hashes its bytes into the receipt (`:1448-1459`), and the AST parser requires a complete balanced package-list suffix (`a1-ast-gates.py:258-286`) before extracting the exact compiler-bound prototype and both original impls. Those checks reject missing, empty, truncated, or malformed AST. They do not establish why the process returned nonzero.

## Current defect and S5 observation

`collect_native_reference_baseline` records `stage.get("exit")` without checking terminal classification or accepted exit values, then proceeds to structural extraction (`a1-runner.py:1429-1468`). The consumer only requires `observed_exit` to be an `int` (`a1-ast-gates.py:991-1005`); it accepts `1`, `124`, and Python `bool` values. Thus an unrelated verifier error or a timeout after emitting enough AST can still produce `R_ONLY_NATIVE_INTERFACE_BASELINE_OBSERVED` if structural extraction succeeds.

Existing `test_a1_r10_r_only_source_pair.py` encodes the broad behavior: its fake stage always returns exit 1 and the test asserts that the baseline passes (`:51-59`, `:149-155`). It tests changed inputs and missing AST (`:157-167`) but not the reason for exit 1, timeout/missing/null/wrong-type exits, stale/truncated AST, or stage exceptions. That test should be revised to model the explicitly authorized expected duplicate-prototype path and add the missing/error cases.

The exact R13 S5 Brief evidence is bounded and identity-pinned:

- Build `ba7de205-b683-4517-a74f-cff4d53c482f`, archive SHA `913abb6620515ce61ed6111964cceb55f6fff5f599aa2899e1608f200dd9640b`, index SHA `dee2ee784e1e689e9eb984e44fdc532d25a7c2fec24d258b6aa80f78f78d6813`.
- Exact observation file `allprooflogs/cases/sort4-c1-current-recovery/a1-native-reference/P1/r-only-native-reference-observation.json`, file ID `85e62839079a4dde06bf04214d0cb4f97a4b714e76d17b2ff4864ac004473340`, SHA `e6b846af5e373b17719e6aaefb4d0917ee38131942d5e3c54e497dd9fbfa34c1`; targeted request ID `77ecc211e54658feb70328c162c9c9c7915502416629ec4f7e0b6867d75aed5b`. It records `observed_exit=1`, `proof_credit=false`, Build ID above, AST SHA `4d0120ee25ea61bb34432919e7be79a476d6b372cafbf640c8b116c8e7a11ddc`, and source-pair ID `2a0fca395c7324627fa28c61a2cdcec068ed84b12fe695956c47845fa1855906`.
- Exact stage file `.../a1-native-reference/P1/r-only-native-reference-stage.json`, file ID `7c0dbf5a600ce4f0b9537f76ff13446ba4ccf8b39cf56727b0a7317c1d16ca3b`, SHA `5dc7dd85f52d92e386d95b36ee79ffec11718205ac94f1b429e0f256bbf63082`; targeted request ID `b681839c53250778feea50a31347b5371e543de64d3c68aa1a2adbec5387f481`. It is `TERMINAL`, exit 1, 240-second timeout. The argv is the pinned R-only native-reference console with `-focus verified/lib.rs:0 -dump_ast_with_locs ... -rustc_args --edition 2021 verified/lib.rs` (request ID `7e618574d1c22d1a3587266cc8d4e776ab4e35fe956902965a403fc3c40fba17`).
- Targeted Brief locator for the stage log found exactly one expected diagnostic at line 28, `verified/lib.rs(32,8-28): error: Duplicate function prototype.` in `.../a1-native-reference/P1/r-only-native-reference.log`, file ID `be3dfcd08e58ba1ef6c68c29cb29e2b12605c57b62c9fdf12a0c9084aa00b216`, SHA `0fd042b148adff3bcf4c8d0f288e169c15127b1402ec8b836a16b10f4a757455`, request ID `090d58f57d87d8bccaf9f0019b372ed025fc7fa6cffe9835fc40665fe4d1ea6d`. Adjacent lines are two specialization warnings, then the duplicate-prototype diagnostic and source excerpt. This supports the specific known path for this Build; it does not imply every exit 1 is safe or establish causal completeness of other invocations.

The Brief classifies this as `SOURCE_OBSERVATIONS_NOT_PROOF`, `parser_input_binding=NOT_ESTABLISHED`, and `causal_status=UNKNOWN`. These evidence limits remain in force. The tool is the effective R13 chain based on `f76012fb518703b1d98e243ac4f487f16877cfcb`, profile SHA `d66d8d7890d528eed417e9c7088fa67f0bde70badd53733facfe2b645c512a58`; do not replace it with the base alone.

## Minimal fail-closed change for the main agent

Keep the collector's existing source-pair, binary, compiler inventory, structural identity, exact parser, and zero-credit checks. Before writing the observation receipt or calling `small_sort_native_baseline`, require:

1. Stage has `classification == "TERMINAL"` and `type(exit) is int`.
2. Exit `0` is accepted only with the complete exact AST checks already in place.
3. Exit `1` is accepted only if the stage log exists, `log_sha256` matches its bytes, and the log contains exactly one expected P1 `Duplicate function prototype.` diagnostic at the known `verified/lib.rs` span. Record the matched diagnostic (or its compact digest/location) and the stage-log SHA in the receipt. This is an explicit structural-capture exception, not a successful-verification claim.
4. Timeout `124`, signal exits, missing/null/wrong-type exit, unrecognized exit-1 diagnostic, absent/stale/mismatched log, stage exception, or AST missing/truncated/malformed must fail closed and yield no baseline. Do not translate these to `NOT_RUN`; retain the observed terminal/unknown status and report `INCONCLUSIVE`.

The R-only command uses a fresh evidence subdirectory, so stale paths are already excluded. Preserve that precondition. No AST producer change is needed for this bounded fix: the exact expected post-callback diagnostic proves the writer returned, while full AST parse and the existing P1 identity checks reject partial or unrelated serialization. If future evidence shows the same diagnostic can be printed before the callback completes, then require an atomic temp-file/rename writer or an explicit complete-dump marker before admitting exit 1.

## Required isolated controls before Cloud

Update the current R-only source-pair tests using synthetic stage/log fixtures, without running VeriFast locally:

- exit 0 + complete bound AST passes structural capture;
- exit 1 + exact unique expected diagnostic + complete AST passes structural capture, with `proof_credit=false` and `conformance_credit=false`;
- exit 1 with unrelated, absent, duplicated, or wrong-location diagnostic fails;
- exit 124, missing/null/bool/string exit and non-terminal stage fail;
- stage/log hash mismatch, stage exception, missing AST, stale destination, truncated AST, or source-pair mutation fails;
- preserve source/tool/profile/translator/schema/exporter identity controls.

Then keep native-interface admission `INCONCLUSIVE` until the updated exact route runs and all P1 producer/consumer predicates pass. Structural baseline is not body verification and cannot independently establish parser-input binding or proof credit.
