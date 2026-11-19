`kani autoharness -Z uninit-checks` can report success for a function that reads an uninitialized padding byte because its generated entry point lacks memory initialization setup. This change initializes memory tracking at automatic harness entry, using the setup for manual proof harnesses.

The compiler recognizes the generated wrapper through its automatic-harness marker. The regression selects a padding-byte read and a control that writes the byte before reading it. Separate invocations require failure for the uninitialized read and success for the initialized control, with both target names in the expected output.

Testing for this cleanup: static source and output-matcher checks passed. Native regression and CI have not been run for this revision.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
