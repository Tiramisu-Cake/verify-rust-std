# TASK — worker15: пакет «дефекты на main» F1–F4 (одна стадия, без dispatch)

Это верификация корректности, не security-работа. Отвечай кратко.

Цель: одним CI-прогоном на **stock upstream Kani `0aac16ef62`** показать (или опровергнуть) четыре дефекта `main`, которые
станут отдельными маленькими PR. Каждый — минимальный тест, без `MaybeUninit`, если это возможно. Правила: STYLE-UPSTREAM-RULES.md.

Кандидаты (из чтения кода на 0aac; проверить сами по исходникам):
- **F1 autoharness без reset.** `is_harness` (`kani-compiler/.../ptr_uninit/mod.rs`) распознаёт только `proof`/`proof_for_contract`;
  в `kani autoharness -Z uninit-checks` состояние инициализации не сбрасывается → чтение uninit (padding-байт `#[repr(C)]`
  через сырой указатель) не сообщается. Ожидание на main: верификация SUCCESS (дефект). Описание проверки в Kani содержит тип
  указателя (`*const u8`), не `u8` — в expected брать префикс без типа.
- **F2 смещения layout pattern-типов/enum.** `ty_layout.rs` (~337 на 0aac) считает data bytes pattern-типа от 0, а не от
  `current_offset` → неверная маска для структуры с `NonNull` не в нулевом смещении. Найти наблюдаемое следствие под
  `-Z uninit-checks` (ложная ошибка или пропуск) и тест на нём.
- **F3 рекурсия в delayed-UB анализе.** `points_to_analysis.rs` (~520) вызывает анализ для каждого вызова без защиты от повтора →
  рекурсивная функция, достижимая из harness с delayed-UB целью (приведение указателя к типу с другим padding, как
  `tests/expected/uninit/delayed-ub/delayed-ub.rs`), предположительно переполняет стек компилятора.
- **F4 утечка delayed-инструментации.** `delayed_ub/mod.rs` (~143) пишет инструментированное тело в кеш transformer → два
  harness в одном файле, проверки/результат зависят от порядка компиляции.

Сделать: тесты (формат upstream: `tests/expected/uninit/...` или `tests/script-based-pre/...`), control-ветку по образцу
наших quick-CI пакетов (`uninit-ci/**`, только нужные suites, artifacts — компактный вывод по каждому тесту), CI-REQUEST,
локальная валидация без cargo/Kani. Для каждого кандидата заранее записать ожидание «дефект есть» и «дефекта нет»,
чтобы прогон был однозначен. Исходники Kani: `/root/kani-fix-3300-c2-s5` (есть 0aac), свой worktree.

Выход: g0 `kani3300/wave0/confirm-main/`: тесты, PACKAGE.md, CI-REQUEST.json, HANDOFF.md. Коммит [skip ci], author
Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> <control SHA> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
