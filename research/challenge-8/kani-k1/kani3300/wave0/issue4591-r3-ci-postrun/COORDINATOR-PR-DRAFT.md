<!-- Черновик PR в model-checking/kani для #4591 (2026-11-19). Ветка Tiramisu-Cake:fix/stub-contracted-function, head 031fc085cd (2 коммита поверх main 969f464898).
Основа — черновик w15 (g0 issue4591-morning-pr-draft), переписан координатором. Ссылка Testing — после CI r3 (Kani CI 44461123962). Публикуется всё ниже линии ---. Не публиковать без команды владельца. -->

---

Title: Support ordinary stubs of functions with contracts

`#[kani::stub(f, g)]` failed to compile when `f` has a contract: the stubbing pass replaced `f`'s body with `g`'s, and the contract pass then looked for `f`'s generated closures in the replaced body (`Failed to find contract closure __kani_recursion_check_f`).

The contract pass now follows the resolved replacement. A plain replacement simply supplies its behavior, and a replacement that has its own contract keeps its own checks. Harnesses that select `f` explicitly with `proof_for_contract` or `stub_verified` are unchanged.

The new tests cover `requires`-only, `ensures`-only and combined contracts, each with ordinary-stub, `proof_for_contract` and `stub_verified` harnesses, plus caller contracts that call an ordinary replacement once. The reproducer from #4591 now compiles; its harness reports an overflow, because the stub may return `i32::MAX` and the caller adds one.

Resolves #4591.

Testing: [CI in my fork](https://github.com/Tiramisu-Cake/kani/actions/runs/44461123962).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
