# Support ordinary stubs of functions with contracts

Running `kani file.rs -Z function-contracts -Z stubbing` with an ordinary stub of a contracted target fails on main while looking for the target's generated contract closures in the replacement body. This change lets the contract pass use the resolved replacement body and its contract attributes after ordinary stubbing succeeds. Plain replacements supply their behavior; contracted replacements retain their contract instrumentation.

The regressions exercise ordinary replacements alongside `proof_for_contract` and `stub_verified` controls for the same functions. Caller-contract tests use a single checked call with an ordinary replacement inside the caller body; a negative test requires a false replacement postcondition to fail. The safe replacement is expected to verify with the change. The verbatim issue reproducer is expected to report a caller overflow because its replacement admits `i32::MAX` before the caller adds one.

Resolves #4591.

Testing: the published candidate failed the [standard Kani run](https://github.com/Tiramisu-Cake/kani/actions/runs/44399789701) on the single-top-level-call assertion; Format and Deny passed. This follow-up repairs both affected positive and negative fixtures. Offline source, oracle and patch-replay checks pass. Native validation of this repair is pending independent review and a separately authorized full standard CI run.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
