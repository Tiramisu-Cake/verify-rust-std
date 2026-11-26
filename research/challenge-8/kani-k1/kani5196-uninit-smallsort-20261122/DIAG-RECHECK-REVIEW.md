# kani5196 · повтор ITER/SELECT · независимое ревью R1

**GO**, блокирующих замечаний нет · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · control `5ff3ce873558c80003b32851bc2223988f098ca4` (tree `e1791b8ff50ed9d6b486acfee8d2c687ee22d6a8`, parent `5b5aa3cb61`), review-trigger `1db313afad71517f56e1f91d6b552d2415582274` (тот же tree, sole parent `467af9cb8d`), handoff g0 `b9a0d3c28c`, CI-REQUEST SHA-256 `600e3015…0db3`.

## Неблокирующее

1. **Сопоставление assertion (вне буквального объёма задания, обосновано).** `diag_evidence.py:127-130` принимает `class=="panic"` с описанием `"assertion failed: "`. На пине `1c6e63b1` `assert!` идёт через `PanicAssert` → `PropertyClass::Panic` (`hooks.rs:187-210`, `assert.rs:64-81`); без правки все assertions фикстур дали бы `INCOMPLETE`. Множественное совпадение остаётся `INCOMPLETE`, тест с ложным panic на той же строке есть; мутации ловятся (5 и 2 падения). В разборе явно указать это как вынужденное инструментом отклонение и что классы assertion отличаются от run 45163409005.
2. `tool_attestation.py:165,175,290` берёт commit/tree из `tool_pin` запроса; обратно совместимо, новый тест отклоняет чужой commit и tree по отдельности.
3. `test_diagnostic.py:520`: лимиты теста таймаута инспектора 0,6/0,8 → 8/8,75 с, в handoff не объяснено; утверждения timeout и reap сохранены.
4. `evidence.py:15`: `STOCK_SOURCE_COMMIT` остаётся `bcdc1a0f` как источник валидатора; между пинами `schema_utils.rs` менялся только в unit-тестах. Не путать с tool commit.

## Проверено

- Дельта control — 8 файлов; workflow — только имя шага (gates, ref, attempt, runner прежние). Фикстуры побайтно прежние, пять SHA-256 совпадают. 8 корней в порядке задания; ON−OFF ровно `-Z uninit-checks`.
- Tool pin по git-объектам: `1c6e63b1`, tree `724e184d`, родители `cfcd2eb1`/`8c6dba59`, `rust-toolchain.toml` `864a9691…` (nightly-2026-11-23), `Cargo.lock`, gitlinks, CBMC 6.11.0, Kissat 4.0.1; 41 tool-file SHA-256 и 35 payload hashes.
- `finish` собирает пары по `pair`/`mode`; старая позиционная логика роняет 4 теста.
- Часы: 8×122 = 976 с, запас 1154 с, job 4500 с; caps прежние; ранний сбой → 8 `NOT_RUN`; harvest после timeout/reap.
- Тесты 26/26 + 28/28 + 14/14; YAML, `bash -n`, `git diff --check` чисты. Авторство Tiramisu-Cake, `[skip ci]`, без решётки перед цифрой.

Не проверено: regex исходников sysroot на rust-src 11-23 (несовпадение даёт `MISSING`/`AMBIGUOUS`, не фатально); поведение на runner.

Замечание координатора: пакет унаследовал gate прежнего kani5196 diag (repo/event/ref/attempt) без отдельной Actions-переменной trigger tree. Trigger создаёт координатор из проверенного tree; решение — за планером при GO.
