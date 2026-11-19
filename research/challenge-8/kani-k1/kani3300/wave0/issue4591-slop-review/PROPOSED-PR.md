Title: Support ordinary stubs of functions with contracts

Running `kani -Z function-contracts -Z stubbing tests/expected/function-contract/ordinary_stub_issue_4591.rs` exercises an ordinary `#[kani::stub(abs_val, stub_abs_val)]` of a function with a contract. At the base used for this change, the contract pass looks for the original function's generated closures in the replacement body and rejects compilation. This change makes the contract pass use the resolved replacement's attributes and closures.

A plain replacement supplies its behavior, and a replacement with a contract uses its own conditions by default. The regression expects compilation followed by a caller-overflow counterexample: the stub can return `i32::MAX`, and the caller adds one. The focused tests also cover ordinary stubs of requires-only, ensures-only and combined contracts, contract checking, verified replacements and `--no-assert-contracts`.

Resolves #4591.

Testing: [Full standard CI (pending)](PENDING_FULL_STANDARD_CI_URL).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
