# VALIDVAL — пилот `-Z valid-value-checks` на новом pin

**Выдано координатором 2026-11-04 (ночь), решение владельца: valid-value делаем.** **Dispatch только после
exact-packet PRE-BUILD review/GO координатора.** Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-validval**, ветка **experiment/kani-k1-validval-20261104** от
  **59893bff1f**: upstream `233f96f66a` (Kani `cd355b0b`), library Part 1 v7, тулинг K-1 с новым ключом запроса
  `valid_value_checks` (передаёт `-Z valid-value-checks`, только kind diagnostic на gcb-e2-standard-4).
- Slug **validval**. Stable owner — тот, чей слот свободен на момент dispatch (k1-network или k1-merge); указать в
  PRE-BUILD, координатор подтвердит. Новые stage/ledger/UUID/request_id `validval-*`.
- Project cap **$118.96**, свой cap **$1.30**. **Одна сборка**, retry нет. Один compile-error repair, если own spent
  + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**.
- Окно: main 150 + closeout 30 мин.

## Цель

Challenge требует автоматически проверять создание невалидных значений. До сих пор это было NOT_RUN. Нужно получить
факт на текущем pin:
- ловит ли флаг заведомо невалидное значение;
- не даёт ли он ложных срабатываний на валидных путях;
- что он говорит на настоящих маршрутах SmallSort для типов с инвариантом представления.

## Что сделать

Новый opt-in модуль `verify/validval.rs` под `cfg(kani_smallsort_controls)`. Существующие файлы v7 не менять,
кроме одной регистрации модуля в `verify.rs`. ≤ 7 корней.

1. **Калибровка (обязательна, без неё строки 3+ не засчитываются):**
   - negative: из байта `2u8` создаётся `bool` (через `transmute` или `ptr::read` из байтового буфера). Ожидается
     FAILED на valid-value-проверке;
   - positive: тот же путь с байтом из `{0, 1}` (`kani::any()` + assume). Ожидается SUCCESS;
   - при запасе: такая же пара для `char` (суррогат `0xD800` против валидного скаляра).
2. **Реальные маршруты** на типах с инвариантом, валидно построенные входы, компаратор — строгий порядок:
   - `bool` через Unstable entry (Freeze + Copy, size 1 → network), N4..8;
   - `char` через Stable entry со scratch, N4;
   - при запасе `NonZeroU8` или `Option<NonZeroU8>` через Unstable, N4.

   Covers на достижение маршрута. Проверка — отсутствие отказов (safety + valid-value), без утверждений о
   корректности.

Исходы различать: SUCCESS, FAILED на valid-value-проверке (с location), неподдержанная операция (точный текст),
compile error, TIMEOUT.

## Сборка

Kind diagnostic, `controls: true`, `valid_value_checks: true`, `uninit_checks: false`, jobs 1. Строк ≤ 7,
`harness_timeout_minutes` минимальный разумный.

## Коммиты

- Library-research коммит (новый модуль) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-VALIDVAL.md**, ≤ 30 строк:
- identities;
- калибровка;
- таблица строк с классификацией исходов;
- что это значит для класса «невалидные значения»: что проверено и где, что нет;
- что осталось NOT_RUN.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **VALIDVAL ЗАВЕРШЁН**, одна стадия, затем стоп.
