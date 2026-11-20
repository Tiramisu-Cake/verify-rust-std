<!-- Черновик follow-up PR к слитому kani#5159 (2026-11-20). Ветка Tiramisu-Cake:fix/volatile-zst-test-followup-main-v2, head 19f7c1af19 (один коммит на main fca73e1318). CI форка 44641742091 — все 12 задач зелёные. Публикуется всё ниже линии ---. Не публиковать без команды владельца. -->

---

Title: Read a local unit value in the volatile ZST test

Follow-up to the review of #5159. `read_volatile_unit_reference` read through `&()`, which rustc promotes to a static, so the test did not exercise the case from #5072. It now reads through a pointer to a local, as in the issue's reproducer. The uninhabited-ZST check in the `volatile_load` match guard moves into a small helper, and the two copies of its diagnostic share a constant; behavior is unchanged.

Testing: [CI in my fork](https://github.com/Tiramisu-Cake/kani/actions/runs/44641742091): regression on all five platforms, documentation, perf, benchcomp, LLBC, format, Clippy and Cargo Deny passed.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
