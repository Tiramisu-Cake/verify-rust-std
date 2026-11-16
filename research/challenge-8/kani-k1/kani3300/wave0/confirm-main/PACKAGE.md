# Проверка кандидатов на stock main

Пакет готовит один будущий CI-прогон Kani с исходниками компилятора и библиотеки из `0aac16ef62da9e9d5645782d458593e5d78143ba`.
В этой стадии выполнены только чтение исходников, подготовка тестов и статические/синтетические проверки. Результаты Kani: **NOT_RUN**.

| Кандидат | Различающий тест | Дефект есть | Дефекта нет на этом тесте |
|---|---|---|---|
| F1 | Автоматические harness для чтения data/padding `repr(C)` | Обе функции SUCCESS, native exit 0 | Data SUCCESS; padding FAILURE с `Undefined Behavior: Reading from an uninitialized pointer`, native exit 1 |
| F2 | `repr(C)` с инициализированным `u64` и неинициализированным `NonNull<u8>` на смещении 8 | Typed read SUCCESS, native exit 0 | Typed read FAILURE с тем же префиксом uninit, native exit 1 |
| F3 | Статически рекурсивный helper при глубине исполнения 0 и delayed-UB write/read | Компилятор сообщает `thread ... has overflowed its stack` до проверки harness; native exit ненулевой, export отсутствует | Завершённая проверка сообщает uninit FAILURE, native exit 1 |
| F4 | Два harness с общей функцией чтения: по отдельности и вместе в двух cfg-вариантах | У одного harness меняется результат либо число/состав проверок относительно его одиночного запуска | У обоих harness совпадают результаты и проверки с их одиночными запусками |

Все ожидания зафиксированы до CI. `DEFECT_ABSENT_FOR_TEST` относится к конкретному примеру; совпадение результатов без подтверждённого порядка компиляции не устанавливает независимость от любого порядка. Для F4 общий exit пары проверяется по результатам обоих harness. Он закономерно равен 1 при одном успешно проверенном и одном падающем harness.

Отдельный существующий explicit-proof тест `tests/expected/uninit/access-padding-uninit/access-padding-uninit.rs` должен дать uninit FAILURE. При его сбое выводы F1–F4 становятся INCONCLUSIVE. Timeout, неподдерживаемая операция, неполный/отсутствующий export и посторонняя ошибка не подтверждают кандидата.

## Основание в исходниках

- F1: `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs`, `is_harness`: только `proof` и `proof_for_contract`; `library/kani_core/src/mem_init.rs`: начальный tracked object 0, setup выбирает object/offset недетерминированно.
- F2: `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs`, ветвь `RigidTy::Pat`: вызов с offset 0. Перед pattern-полем теста целиком инициализированы первые восемь байт; неверная маска повторно включает их. Проверяется предположение, что pinned toolchain представляет поле `NonNull` через этот путь.
- F3: `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs`, `apply_regular_call_effect`: рекурсивный `PointsToAnalysis::run`. `#[inline(never)]` сохраняет helper; нулевая глубина исключает переполнение стека исполняемой программы.
- F4: `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs`: инструментированное тело записывается в transformer cache. `compiler_interface.rs` создаёт общий transformer для harness внутри codegen unit; `codegen_order.rs` сортирует по числу reachable items при наличии export workers. Фактический порядок и наблюдаемое следствие требуют CI.

## Состав и запуск

`tests/` содержит только новые upstream-тесты. `.github/` содержит CI-обработчик, его синтетические проверки и единственный workflow. `control.patch` воспроизводит control commit поверх stock main, включая удаление остальных workflow исключительно в control-ветке. Компилятор, библиотека, действующие тесты и проверки остаются stock.

Workflow строит Kani один раз и вызывает `.github/confirm-main/confirm.py run`. Обработчик запускает только перечисленные тесты форматов `expected` и `script-based-pre`, без полной regression matrix. Он сохраняет native argv/exit/termination, компактные выдержки, hashes export/output и результаты по harness. Полные native logs/export остаются временными; artifacts — компактные JSON. У F4 исходные результаты каждого запуска записываются отдельно в его компактный отчёт.

Control-коммит содержит `[skip ci]`. Для будущего push-запуска source gate допускает один пустой дочерний trigger-коммит с тем же tree; fetch depth равен 3. Подготовка и запуск trigger требуют отдельной авторизации. Синтетическая проверка принимает control и такого потомка и отвергает изменённый tree.

Зелёный workflow означает, что получены однозначные наблюдения, включая возможное подтверждение дефекта на main. Это не PASS исправлений. Существование всех четырёх дефектов заранее не утверждается.

Job env задаёт каталог evidence через `github.workspace`; upload использует `env.CONFIRM_EVIDENCE_DIR`. Все семь выражений проверены по документации GitHub и синтетической проверкой, отвергающей `runner.temp` в job env. Предыдущий запуск `43878357528` с нулём jobs зафиксирован как сообщение пользователя; результаты F1–F4 остаются **NOT_RUN**.

Точные SHA, команды, лимиты и локальная валидация: `CI-REQUEST.json`, `STATIC-VALIDATION.json`, `HANDOFF.md`. Публикация, dispatch, CI и ledger в этой стадии не выполняются.
