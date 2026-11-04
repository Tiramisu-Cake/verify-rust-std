# VALIDVALTWO — `bool` на реальном маршруте под `-Z valid-value-checks`

**Выдано координатором 2026-11-04 (ночь) после RESULT-VALIDVAL (`1de1e13ade`).** Dispatch только после exact-packet
PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-validvaltwo**, ветка **experiment/kani-k1-validvaltwo-20261104** от
  **1de1e13ade**. В ветке уже есть VALIDVAL: модуль `verify/validval.rs`, калибровка и RESULT.
- Slug **validvaltwo**; stable owner — свободный на момент dispatch (указать в PRE-BUILD). Новые request_id
  `validvaltwo-*`.
- Project cap **$118.96**, свой cap **$0.80**. **Одна сборка**, retry нет. Tooling base: **59893bff1f**.
- Окно: main 90 + closeout 20 мин.

## Цель

VALIDVAL установил:
- калибровка `bool`/`char` работает;
- `char` и `NonZeroU8` на реальных маршрутах упираются в «doesn't support checking validity of
  `copy_nonoverlapping`»;
- `bool` N4..8 дал TIMEOUT при лимите 2 мин.

Нужно узнать, что происходит с `bool` на реальном маршруте при нормальном лимите. Варианты: SUCCESS, то же
неподдержанное `copy_nonoverlapping`, реальный invalid-value отказ или TIMEOUT.

## Что сделать

- В `verify/validval.rs` добавить отдельные корни `bool` через Unstable entry по одной длине: N2 и N4 (при запасе N8).
  Тот же компаратор и covers, что в `unstable_bool_n4_to8`. Существующие корни не менять.
- Сборка: kind diagnostic, `controls: true`, `valid_value_checks: true`, jobs 1, `harness_timeout_minutes` 10.
  Строки: новые корни и `accepts_bool_byte_0_or_1` как позитивный контроль профиля. Не больше 4 строк.

## Коммиты, ожидание, RESULT

- Коммиты `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-VALIDVALTWO.md**, ≤ 20 строк: таблица строк с точным текстом и location; вывод для класса «невалидные
  значения» вместе с VALIDVAL.

## Запреты

Как в TASK-VALIDVAL:
- только bounded evidence;
- без raw logs и credentials;
- без локальных cargo/rustc/Kani/CBMC и Actions;
- чужие PR не открывать;
- runtime, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **VALIDVALTWO ЗАВЕРШЁН**, затем стоп.
