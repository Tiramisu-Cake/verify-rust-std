# Q — шаблон, NOT_RUN / PENDING_PORT_ACCEPTANCE

Принятый slice-07 Quick run43723531871, overlay8288537e7c57b04d2462ff0c5bf1af38ab9d4451.
Observer и artifacts вне source checkout: sibling control/export, source не патчится для обычных suites.
S5 — отдельные намеренные test/golden mutations с проверкой input/patch hash и восстановлением bytes/mode;
production не мутируется. Существующий accepted mutation protocol сохранён.

Прежние471 selectors/directives/ignores сохранены; добавлены все29 из corrected39a6521bf1:
12 intended SUCCESS,17 intended FAILURE/Unsupported. Proposed totals500: expected408 (402 passed/6 existing ignored),
kani53 (50/3), ui17, script3, json17, std-checks2. Новые результаты NOT_RUN.
Сохранены fmt/build/clippy(-D warnings)/LLBC, ActiveCalls9, immutable9, argument_size1, marker_category1,
delayed_cache6, delayed_scope2, all compiler76 (native names сверить с accepted candidate), все original mode boundaries.
S5 требуется4/4 DETECTED; F7 —11 invocations и18 exact mixed-vs-own-isolated comparisons;
пять verifier exit1 intended negative/cycle roots не ошибки suite.
Нет JSON DRIFT exemptions и новых ignores/filters. 29/0 compiletest не равно29 доказанных legal harnesses.
Nested refusal — general UnionAsField при создании Nested до select; select-specific branch этим не проверяется.
Absent/overridden fallback/unsized T — static-only review, не runtime controls.

Фактические limits исходного recipe без повышения: job120min, RUST_TEST_THREADS2,
compiletest2400s/test, S5 process timeout2400s/variant, structural180s/invocation, retention14d.
Общие fmt/build/clippy/LLBC ограничены job timeout; дополнительного RSS/artifact-byte cap в принятом Quick нет.
Original exit/termination сохраняются; ненулевой exit/timeout/OOM/setup loss не становится PASS по подстроке.
Сначала принятие P и candidate binding Q, затем coordinator один запуск Q; только после приёмки Q — freeze.
