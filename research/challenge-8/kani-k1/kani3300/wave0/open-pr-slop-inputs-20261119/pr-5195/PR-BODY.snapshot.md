On `main`, `cargo kani -Z uninit-checks` can fail an initialized read when two harnesses reach the same function. The delayed UB pass instruments function bodies for the analysis targets of the harness being compiled, and the result enters the body cache shared by all harnesses in the codegen unit. A later harness that reaches the same function reuses that body. In the regression test, `initialized_control_harness` reads an initialized `u64`: on `main`, it verifies alone and fails when paired with `delayed_harness`, which writes a padded struct through a pointer cast and calls the same read function.

With `-Z uninit-checks`, this change gives each harness its own copy of the unit's body cache, so the delayed UB pass and codegen of one harness never see bodies instrumented for another. Without the flag, harnesses keep sharing the cache as before, so other runs pay nothing extra. The new `script-based-pre/delayed-shared-body` test verifies each harness alone and both together, through two shared call chains, with and without `-Z uninit-checks`, and checks that the uninitialized read is still reported.

Testing: [CI in my fork](https://github.com/Tiramisu-Cake/kani/actions/runs/44295027834): regression on Linux x86_64, Linux Arm and macOS Intel, documentation, perf, benchcomp, LLBC, format and Clippy passed. The macOS arm64 job did not get a runner. Cargo Deny fails on the new `chrono` advisory (RUSTSEC-2026-0543); this change does not touch dependencies.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
