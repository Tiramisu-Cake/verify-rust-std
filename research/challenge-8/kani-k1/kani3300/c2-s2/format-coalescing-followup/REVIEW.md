# S2 follow-up — review and permitted checks

Entry source f96ad419bcae4e920708ff4bffe2b28d310f422e. Separate formatting commit 3c2af5d5e54ebd15784e34b46e53fd54d7090c4e changes only the two unit-test expressions named by CI. Comparison after removing whitespace confirms no token-content change. The authorized rustfmt wrapper was run with `--edition 2024 --config-path rustfmt.toml <file>`; a second pass was byte-idempotent. This is actual local format-tool execution under the user's explicit exception, not a build or a new CI format-stage result.

The subsequent bf8170b28afb682f8dd55a94199caa247736d8fa adds only two Rust/expected pairs. Each has one proof harness, the same three own value/equality assertions, zero failed properties, final SUCCESSFUL and one-harness summary. They use existing --edition 2021/-D warnings/-Z uninit-checks/regular flags. The same authorized formatter was applied to both files and a second pass was byte-idempotent. The four previous control/oracle pairs are byte-identical to the tested f96 candidate.

Operand/type review: both initializer forms produce `[&'static u8;1]`; &5 is inferred as &u8, the named static is immutable/Sync, const helper execution is CTFE, T[0] copies a valid shared reference, volatile reads coerce &u8 to *const u8 and read initialized u8. No by-value union/nested MaybeUninit, pointer equality, assumptions, raw address fabrication or new qualification rule is introduced.

Production body (including qualification, admission, registration, target/seal/binding/reset and diagnostics) is unchanged from f96 except test whitespace. Existing semantic independent review is therefore still applicable; tests-only additions do not weaken any existing controls. Bounded Luna HIGH read-only investigation supplied compiler allocation-ID and body-conversion references with the explicit nearby-version/unknown-lowering limits preserved in TRACE.md. It did not compile or verify any source candidate.

Git diff/check, exact commit chain, authored identity, clean source, preservation of previous test blobs and temporary-index application of baseline-new-controls.patch are recorded in STATIC-CHECKS.json. No cargo/rustc/Kani/CBMC/Miri/build, push, CI or Cloud operation was performed. Research is uncommitted; unrelated g0/SEL1 updates are preserved.

Prior coordinator CI remains source-reported evidence for f96 only: unit9/0 and existing 4 controls PASS, build/clippy PASS; format FAIL and composition FAIL. No new head is declared all-PASS. New source controls, numeric key/symbol binding and new head CI are NOT_RUN/UNKNOWN.
