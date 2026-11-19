`ptr::read_volatile(&())` can fail pointer checks on `main` because Kani lowers the zero-sized result to a memory dereference. This change constructs an inhabited zero-sized value after checking alignment, allowing aligned reference, dangling and null pointers for these loads.

Loads of uninhabited zero-sized types produce a safety diagnostic, including calls without a MIR return target. The regressions cover the original unit-reference case, over-aligned and aggregate values, direct intrinsics, and the specific alignment and uninhabited-value failures.

### Testing

Standard-workflow CI: pending on the reviewed merged revision.

Resolves #5072

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
