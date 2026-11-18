Title: Keep delayed UB instrumentation specific to each harness

On `main`, `cargo kani -Z uninit-checks` can fail an initialized read when two harnesses reach the same function. The delayed UB pass instruments function bodies for the analysis targets of the harness being compiled, and the result enters the body cache shared by all harnesses in the codegen unit. A later harness that reaches the same function reuses that body. In the regression test, `initialized_control_harness` reads an initialized `u64`: on `main`, it verifies alone and fails when paired with `delayed_harness`, which writes a padded struct through a pointer cast and calls the same read function.

With `-Z uninit-checks`, this change gives each harness its own copy of the unit's body cache for delayed UB instrumentation and codegen. Other runs reuse the shared unit transformer. When harness ordering warms the cache through reachability analysis, each harness starts from those cached local transformations. The regression test checks singleton and paired harnesses through both shared call chains, with and without uninitialized-memory checks, including the initialized assertion and the expected uninitialized-read failures.

Testing: [CI in my fork](https://github.com/Tiramisu-Cake/kani/actions/runs/44295027834) passed the executed regression suites, documentation build, full performance tests, benchcomp, LLBC, formatting and Clippy. Kani CI concluded with failure; the macOS arm64 job was cancelled without a runner. Cargo Deny failed on an external advisory. Per-harness results for both checking modes are unavailable in the CI summaries.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
