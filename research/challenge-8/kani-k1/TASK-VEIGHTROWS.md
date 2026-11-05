# VEIGHTROWS — догон пяти строк VEIGHTMAX без inventory

**Выдано координатором 2026-11-05, в рамках решения владельца по VEIGHTMAX.** Dispatch только после exact-packet
PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-veightrows**, ветка **experiment/kani-k1-veightrows-20261105** от
  **ab99e39380** (VEIGHTMAX: library `d3982a6240`, кандидат v8c, 233 ordinary).
- Slug **veightrows**, stable owner **k1-merge**. Request_id/stage/ledger `veightrows-*`.
- Project cap **$118.96**, свой cap **$1.00**. **Одна сборка**, retry нет, repair нет.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 120 + closeout 20 мин.

## Контекст

VEIGHTMAX (`RESULT-VEIGHTMAX.md`, build `daf1045c`): inventory PASS, ровно 233 ожидаемых имени; merge8 и sort8
SUCCESS. Остальные пять строк не успели: компиляция с inventory заняла 2851 с из 58-минутного лимита сборки. Это
ошибка расчёта лимита координатором, не отказ корней.

## Что сделать

Library не менять (ни одного library-коммита). Новый RUN-REQUEST на `d3982a6240` без изменений кода:

- kind diagnostic, `controls: false`, **`inventory: false`**, jobs 1, gcb-e2-standard-4, 4 мин/корень;
- строки — ровно пять, каждая `expect: SUCCESS`:
  `allocationcontracts::swap_safety_u8_backing32`, `allocationcontracts::swap_safety_u64_backing32`,
  `allocationcontracts::unstable_network_safety_u8_n32_stubbed`,
  `tailcontracts::insert_tail_safety_u64_backing17_tail1_to7`,
  `tailcontracts::insert_tail_safety_u64_backing17_tail8_to15` (полные имена `slice::sort::shared::smallsort::verify::…`).
- В пакете проверить, что library tree дерева сборки побайтно равен `d3982a6240`, и что ожидаемые covers
  (9+9+5+5+5 = 33) взяты из VEIGHTMAX-пакета.

Если расчётный лимит сборки не оставляет на verify хотя бы 5×4 мин после компиляции без inventory (оценить по
прошлым diagnostic-сборкам с `inventory: false`), написать `Координатор, вопрос: ...` и остановиться.

## Коммиты

- Только research-коммит `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.

## RESULT

**RESULT-VEIGHTROWS.md**, ≤ 20 строк: identities; таблица пяти строк (status, время, covers); сводка по всем семи
перенесённым корням вместе с merge8/sort8 из VEIGHTMAX (сумма времени, covers из 42).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Library, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **VEIGHTROWS ЗАВЕРШЁН**, одна стадия, затем стоп.
