# Reject ordinary stubs of contract targets

Reject `#[kani::stub]` when its original function is also the same harness's `proof_for_contract` or `stub_verified` target. Report the conflicting attributes and function during harness stub resolution, before MIR transformation. Repeated verified targets produce one conflict diagnostic per target.

These combinations replace the body containing the contract instrumentation and otherwise fail while looking for a generated contract closure. Comparing resolved function identities catches qualified paths too and preserves stubbing of different functions.

Resolves #5206.

Testing: TODO — run the compile-error cases and positive controls for different targets and reverse-direction stubs under both contract attributes; native tests and CI were not run during offline implementation or revision. Static diff and fixture consistency checks passed.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
