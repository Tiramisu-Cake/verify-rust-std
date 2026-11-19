`ptr::read_volatile(&())` can fail pointer checks because Kani lowers the zero-sized result to a memory dereference. Construct an inhabited zero-sized value after checking alignment, allowing aligned reference, dangling and null pointers.

Reject loads of uninhabited zero-sized types with a safety diagnostic, including calls without a MIR return target. Eight regression harnesses cover the original reproducer, over-aligned and aggregate values, direct intrinsics, and the alignment and uninhabited-value failures. The negative expected files also require their named harness and completed failure summary.

Validation: static checks passed; native tests and standard-workflow CI for this cleanup are pending.

Resolves #5072

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
