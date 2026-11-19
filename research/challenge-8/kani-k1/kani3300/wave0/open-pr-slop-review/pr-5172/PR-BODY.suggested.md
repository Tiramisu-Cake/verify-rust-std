Refs #3300

With `-Z uninit-checks`, Kani retains checks for call operands and function-entry union argument loads when it reports an unsupported call through a function pointer or trait object. On `main`, the local visitor returns before recording these operations, so an uninitialized read in a call operand can be missing from the results. The call-operand and initialized/partially initialized argument regressions check that the safety properties appear with the expected results alongside the unsupported-call diagnostic.

The local visitor records the collected checks before the unsupported-call check. It shares fallible call resolution with the points-to analysis and uses the MIR body of the resolved instance for generated shims. Shims that need union initialization state transfer remain unsupported and receive a diagnostic before that transfer.

### Testing

Standard-workflow CI: pending a run on the revision prepared for publication.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
