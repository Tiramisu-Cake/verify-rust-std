Title: Reset memory initialization state in automatic harnesses

`kani autoharness -Z uninit-checks` can report success for a function that reads an uninitialized padding byte because the generated entry point lacks memory initialization setup. This change initializes tracking when an automatic harness starts, matching the setup used for manual proof harnesses.

The generated wrapper is recognized through its automatic-harness marker and uses the existing setup code. The regression selects a function that reads a padding byte and a control that writes the byte before reading it. Separate invocations require a verification failure for the uninitialized read and success for the initialized control.

Testing: [Full standard CI (pending)](PENDING_FULL_STANDARD_CI_URL). Prior CI reported a macOS Intel `cargo_autoharness_multichareq_searcher` failure (#5162) and fail-fast cancellation.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
