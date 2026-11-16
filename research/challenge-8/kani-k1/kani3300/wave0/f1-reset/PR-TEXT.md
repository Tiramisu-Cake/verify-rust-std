# Initialize memory tracking for automatic harnesses

`kani autoharness -Z autoharness -Z uninit-checks main.rs` can report success for a function that reads an uninitialized padding byte through a raw pointer. Recognize automatic harnesses when setting up memory initialization state so their analysis checks these reads.

The regression runs automatic harnesses for two functions over a padded `#[repr(C)]` struct: one reads padding directly, and one writes the byte before reading it. It is expected to fail on `main`, which accepts the uninitialized read, and pass with this change by reporting that read as a failure while verifying the initialized read.

### Testing

- Static checks passed: shell syntax, copyright headers, and patch whitespace.
- Execution pending: run the standard workflows in [fork CI](FULL_FORK_CI_RUN_URL).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
