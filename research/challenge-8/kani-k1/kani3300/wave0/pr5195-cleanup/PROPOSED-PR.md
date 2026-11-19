With `cargo kani -Z ghost-state -Z uninit-checks`, harnesses that share a function can reuse delayed uninitialized-memory checks computed for a different harness. This can report an uninitialized read in a harness that initializes its value.

Each harness now gets a copy of its codegen unit's locally transformed bodies before delayed checks run. Runs without uninitialized-memory checks retain the shared cache. The regression compares each harness alone and paired under uninitialized-memory checking, preserves the unsafe-read and initialized-value checks, and checks ordinary paired runs for both call-path variants.

Testing for this cleanup: Python and shell syntax checks passed. Native regression and CI have not been run for this revision.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
