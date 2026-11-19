Refs #3300

With `-Z uninit-checks`, retain call-operand checks and function-entry union argument loads when reporting an unsupported function-pointer or trait-object call. The local visitor records these operations before the unsupported-call check, preserving safety properties that its early return could discard.

The visitor and points-to analysis share fallible call resolution and use the resolved instance's MIR body for generated shims. Shims requiring union initialization state transfer remain unsupported. Regression fixtures keep plain and byte-copy variants in separate compilations, including call-operand reads, initialized/partially initialized entry arguments and direct/generated-call controls.

### Testing

Static checks confirm the retained harnesses, flags, helper operations and expected-output bytes after fixture deduplication. Native regression tests and CI have not been run for this cleanup revision.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
