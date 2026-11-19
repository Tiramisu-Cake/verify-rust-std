Title: Keep delayed UB instrumentation specific to each harness

With `cargo kani -Z ghost-state -Z uninit-checks`, harnesses that share a function can reuse delayed uninitialized-memory checks computed for a different harness. This can report an uninitialized read in a harness that initializes its value. The shared read in the regression receives an initialized u64 from one harness and storage containing padding from the other.

Each harness now gets a copy of its codegen unit's locally transformed bodies before delayed checks run. Runs without uninitialized-memory checks retain the shared cache. The regression compares each harness alone and paired under uninitialized-memory checking, checks that the unsafe read is still reported, and checks the ordinary paired runs for both call-path variants.

Testing: [Full standard CI (pending)](PENDING_FULL_STANDARD_CI_URL).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
