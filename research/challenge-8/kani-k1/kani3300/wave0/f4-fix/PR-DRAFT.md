Title: Keep delayed uninitialized-memory instrumentation specific to each harness

`cargo kani -Z uninit-checks` can report an uninitialized read in a harness that reads a fully initialized value when another harness shares its read function. The initialized harness succeeds on its own and fails when verified together with a harness that writes a padded value through a pointer cast.

Give each harness a copy of the codegen unit's cached local transformations so global passes and codegen use bodies instrumented for that harness's analysis targets. The regression compares singleton and paired check inventories for both call paths, requires the initialized harness to succeed, and preserves the delayed and independent uninitialized-memory failures. It rejects the observed results from main; passing execution with the fix is pending CI.

Testing: Python oracle fixtures and shell syntax checks pass. Compiler build and regression execution are pending the full standard PR CI.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
