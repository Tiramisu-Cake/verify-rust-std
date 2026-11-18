# Support ordinary stubs of functions with contracts

Running `kani file.rs -Z function-contracts -Z stubbing` with an ordinary stub of a contracted target currently fails while looking for the target's generated contract closures in the replacement body. This change lets the contract pass use the resolved replacement body and its contract attributes after ordinary stubbing succeeds. Plain replacements supply their own behavior; contracted replacements keep their own contract instrumentation.

The regressions cover requires-only, ensures-only and combined contracts, recursive and generic targets, and PFC and verified-stub controls. The bounded `u8` replacement is expected to verify where main reports a missing closure. The verbatim #4591 reproducer is expected to reach verification and report an overflow counterexample because its replacement admits `i32::MAX` before the caller adds one. Explicit PFC or verified-stub selection of the same ordinary-stubbed target retains its current error behavior.

Resolves #4591.

Testing: static source, patch-replay and fixture checks completed. Native verification is pending the full standard push-CI run.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
