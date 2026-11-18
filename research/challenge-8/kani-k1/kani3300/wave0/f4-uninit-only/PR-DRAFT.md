Title: Keep delayed uninitialized-memory instrumentation specific to each harness

`cargo kani -Z uninit-checks` can report an uninitialized read in a harness that reads a fully initialized value when another harness shares its read function. The initialized harness succeeds on its own and fails when verified together with a harness that writes a padded value through a pointer cast.

Give each harness a copy of the codegen unit's body transformations when uninitialized-memory checks are enabled, and use the shared transformer otherwise. This keeps the cached bodies, pass state and loop metadata together. The regression compares singleton and paired checks through both call paths with the checks enabled and disabled. It rejects the observed initialized-harness failure on main, preserves the intended uninitialized-memory failures with the checks enabled, and expects the initialized harness to succeed with the fix; execution of this revision is pending CI.

Testing: Python oracle fixtures, shell syntax and static patch checks pass. Compiler build, the two-mode regression and performance validation are pending the full native push CI on this revision.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
