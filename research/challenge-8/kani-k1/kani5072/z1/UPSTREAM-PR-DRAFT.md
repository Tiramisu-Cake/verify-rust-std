Avoid dereferencing pointers when lowering volatile loads of zero-sized types.

Kani emits a spurious memory access for `ptr::read_volatile(&())`, causing pointer failures (#5072).
For inhabited ZSTs, generate a typed ZST value while retaining alignment checks; reject uninhabited ZSTs explicitly.
The non-ZST load path is unchanged. Add reference, dangling, over-aligned, null, aggregate and negative regression cases.
Validation: rustfmt/fresh-pin apply/tree checks pass; all 8 selected native compiletest cases PASS on nightly-2026-10-23.
Negative alignment/uninhabited/bounds cases matched failing-check goldens; full upstream CI has not been run.

Resolves #5072

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
