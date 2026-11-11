Avoid dereferencing pointers when lowering volatile loads of zero-sized types.

Kani currently emits a memory access for `ptr::read_volatile(&())`, producing spurious pointer failures (#5072).
For inhabited ZSTs, generate a typed ZST value while retaining alignment checks; reject uninhabited values.
The non-ZST load path is unchanged. Add reference, dangling, over-aligned, null, aggregate and negative regression cases.
Validation: rustfmt and fresh-pin patch/tree checks pass. Native Kani subset is pending authorized Cloud execution.

Resolves #5072

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
