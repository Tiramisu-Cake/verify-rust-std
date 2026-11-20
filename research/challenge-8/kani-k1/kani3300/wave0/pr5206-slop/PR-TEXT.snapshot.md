<!-- Черновик PR в model-checking/kani для #5206 (2026-11-20). Ветка Tiramisu-Cake:fix/stub-contract-target-conflict-v2, head a65ffdbdcc (один коммит на main 0997d11c14; merge-tree с main 5d80a641d чистый). CI форка 44616139446: attempt 1 — codegen_cache флейк на ubuntu-22.04, attempt 2 — зелёный. Публикуется всё ниже линии ---. Не публиковать без команды владельца. -->

---

Title: Reject ordinary stubs of contract targets

`#[kani::stub(f, g)]` failed with the internal error `Failed to find contract closure __kani_recursion_check_f` when the same harness also had `#[kani::proof_for_contract(f)]` or `#[kani::stub_verified(f)]`: the stub replaces the body that carries `f`'s contract instrumentation. Both combinations are configuration mistakes, so Kani now rejects them while resolving the harness's stubs, with an error that names the function and the conflicting attributes. Stubbing other functions, or stubbing in the other direction, is unaffected.

Resolves #5206.

Testing: `tests/ui/function-contracts/ordinary_stub_target_conflict` checks both errors, and `tests/expected/function-contract/ordinary_stub_different_target` covers a stub of another function and a reverse-direction stub under each attribute. [CI in my fork](https://github.com/Tiramisu-Cake/kani/actions/runs/44616139446): regression on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM and macOS 15 Intel, documentation, perf, benchcomp, LLBC, format, Clippy and Cargo Deny passed. The macOS 15 job did not get a runner, and the Ubuntu 22.04 job passed on a rerun after an unrelated `codegen_cache` failure.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
