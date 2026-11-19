# Suggested title

Fix reconstruction of arrays with zero-width elements

# Suggested body

A typed read of constant bytes into a struct containing an array of GNU C empty structs can abort in `bits2expr`. The regression in `regression/cbmc/byte_extract_empty_struct_array` exercises this with `cbmc main.c` and checks the bytes on both sides of the array. The related Rust failure is reported in [model-checking/kani#5085](https://github.com/model-checking/kani/issues/5085).

Allow known zero-width elements in the array branch. The existing loop recursively reconstructs each element from an empty bit string, preserving the element count and array type. Unit tests check empty and nested arrays, tagged elements, surrounding values and reconstruction inside a union.

## Testing

The regression targets the former positive-element-width invariant. Standard CI for the final cleanup revision: pending; replace this sentence with one standard workflow run link when available. Native validation of that revision remains pending.

- [x] Each commit message has a non-empty body, explaining why the change was made.
- [x] Methods or procedures I have added are documented, following the guidelines provided in CODING_STANDARD.md.
- [x] The feature or user visible behaviour I have added or modified has been documented in the User Guide in doc/cprover-manual/
- [x] Regression or unit tests are included, or existing tests cover the modified code (in this case I have detailed which ones those are in the commit message).
- [x] My commit message includes data points confirming performance improvements (if claimed).
- [x] My PR is restricted to a single feature or bugfix.
- [x] White-space or formatting changes outside the feature-related changed lines are in commits of their own.

This bug fix uses the existing API and command-line interface. New-method documentation, new-feature guide changes and performance measurements are not applicable.

*Disclosure: this change and description were prepared with the help of AI assistants.*
