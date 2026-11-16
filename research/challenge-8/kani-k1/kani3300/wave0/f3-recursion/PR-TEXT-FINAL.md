<!-- PR F3 в model-checking/kani (2026-11-16). Голова f99713506f (b69f484e8c + фикс заголовка edition; база 0aac16ef62), ветка fork fix/delayed-ub-recursion. Основа — PR-TEXT w14 (g0 a70737e1ab), переписан координатором по STYLE-UPSTREAM-RULES.
Факты: тот же тест (кроме doc-комментария) на main даёт переполнение стека rustc — run 43882466907 (research, не ссылаем). CI стандартных workflow на голове — run 43920609175 (идёт; 43912461616 упал на заголовке edition).
Публикуется всё ниже линии ---. Title — отдельно. -->

Title: Report recursive calls in delayed UB analysis instead of overflowing the stack

---

With `-Z uninit-checks`, the points-to analysis for delayed UB analyzes the body of every function a harness calls, with no check for calls that are already being analyzed. When a harness with delayed UB targets reaches a recursive function, the compiler overflows its stack.

The analysis now keeps track of the functions in progress and reports a recursive call at its call site: "Kani does not support memory initialization checks across recursive calls."

### Testing

`tests/expected/uninit/recursive-delayed/recursive-delayed.rs` reaches a recursive helper from a harness where a pointer cast creates a delayed UB target. On `main` the compiler overflows its stack; with this change it reports the error above. `repeated-calls.rs` calls a helper twice in a row: an uninitialized read is still reported, and the initialized case verifies.

Standard workflows on this head in my fork: [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43920609175). The macOS 15 job did not get a runner and the perf job lost its runner, both also after a rerun.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
