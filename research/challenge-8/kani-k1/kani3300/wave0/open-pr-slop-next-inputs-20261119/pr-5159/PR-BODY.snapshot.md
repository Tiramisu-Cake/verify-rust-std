`ptr::read_volatile` on an inhabited zero-sized type can fail pointer checks even for `read_volatile(&())`. `codegen_volatile_load` lowers it to a dereference although no memory is accessed. Construct the ZST value directly instead, preserving the alignment check and adding no non-null requirement. Non-ZST loads are unchanged.

Reject volatile loads of uninhabited ZSTs with a safety check, including calls without a MIR return target.

Regression tests cover the reproducer, dangling and null pointers, over-aligned and aggregate ZSTs, and direct intrinsic calls. Expected-output tests check misalignment and an uninhabited ZST.

The regression suites passed in [fork CI](https://github.com/Tiramisu-Cake/kani/actions/runs/42947192933) at `70d9288` on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM, and macOS 15 Intel; the macOS 14 job was cancelled because its runner was unavailable.

Resolves #5072

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
