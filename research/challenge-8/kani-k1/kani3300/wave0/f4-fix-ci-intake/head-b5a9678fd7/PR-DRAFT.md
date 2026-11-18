Title: Keep uninitialized-memory instrumentation specific to each harness

`cargo kani -Z uninit-checks` can report an uninitialized read in a harness that reads a fully initialized value when another harness shares its read function. The initialized harness succeeds on its own and fails when verified together with a harness that writes a padded value through a pointer cast.

Give each harness a copy of the codegen unit's cached local transformations so global passes and codegen use bodies instrumented for that harness's analysis targets. The regression rejects the observed result on `main`; the fork's script-based-pre suite was reported successful with this change. It checks initialized reads and the intended uninitialized-memory failures across singleton and paired harnesses with both feature configurations.

Testing: [Fork push CI](https://github.com/Tiramisu-Cake/kani/actions/runs/44274306776) completed with Linux and macOS Intel regression, documentation, benchcomp, LLBC and perf jobs successful; Format/Clippy passed separately. Kani CI remains failed because macOS arm64 could not acquire a runner and never executed. Cargo Deny failed on the external chrono advisory with unchanged dependencies. macOS arm64 coverage, release bundles, std verification and benchmark comparisons await upstream PR CI.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
