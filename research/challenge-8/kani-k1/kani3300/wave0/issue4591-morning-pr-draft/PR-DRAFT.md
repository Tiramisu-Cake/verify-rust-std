# Support ordinary stubs of functions with contracts

With `kani file.rs -Z function-contracts -Z stubbing`, an ordinary stub of a contracted function uses the replacement's behavior and contract attributes. The contract pass follows the resolved replacement body, so a plain replacement supplies its behavior and a contracted replacement keeps its own contract checks. Explicit `proof_for_contract` and `stub_verified` selections retain their selected target.

The regression tests cover requires-only, ensures-only, and combined contracts, with ordinary-stub, `proof_for_contract`, and `stub_verified` controls. Caller-contract tests make a single checked call with an ordinary replacement inside the caller; the negative case satisfies the caller's postcondition while violating the replacement's postcondition. The safe examples are intended to verify. The verbatim issue reproducer is intended to produce a caller-overflow counterexample when the replacement returns `i32::MAX` and the caller adds one.

Resolves #4591.

Testing: Full standard CI run pending (link to be added).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
