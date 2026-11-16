# Report recursion in delayed UB analysis as unsupported instead of overflowing the stack

`kani -Z ghost-state -Z uninit-checks tests/expected/uninit/recursive-delayed/recursive-delayed.rs` can overflow the compiler stack when a harness reaches a recursive function. Track the function instances currently undergoing points-to analysis and report an unsupported recursive call at its source location.

The regression reaches a recursive helper from a harness with a pointer cast that triggers delayed UB analysis. It is expected to fail on `main` with a compiler stack overflow and pass with this change by producing the recursion diagnostic. A companion checks repeated calls to a helper, including an uninitialized read and a read after initialization.

### Testing

- Patch whitespace and copyright checks passed; execution is pending.
- Run the standard workflows in [fork CI](FULL_FORK_CI_RUN_URL).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
