# INTEGCHECK — интеграционная проверка очищенного дерева Part 1: 13 контролей, пары leaf/consumer, cfg-on inventory

**Выдано координатором 2026-11-06, решение владельца.** Последняя GCB-проверка перед финальным коммитом и полным CI
организаторов. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-integcheck**, ветка **experiment/kani-k1-integcheck-20261106** от
  **bbdc1aac23** (RENAMEMODS PASS: library `85ced7f8a8, tree def2d65ddc`; 233 ordinary + 13 контролей, cfg-on 246).
- Slug **integcheck**, stable owner **k1-merge**. Request_id/stage/ledger `integcheck-*`.
- Project cap **$118.96**, свой cap **$2.00**. **До двух сборок**: G1 (proof rows), G2 (cfg-on inventory) — G2
  можно отправить сразу после G1 в том же пакете GO, если пул позволяет; иначе последовательно. Retry нет.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 300 + closeout 30 мин.

## Цель

Library **не менять** (ни одного library-коммита). Проверить на итоговом дереве то, что до сих пор проверялось
только на деревьях отдельных этапов:

1. **Все 13 отрицательных контролей** падают ровно на своей назначенной проверке. Источники ожидаемых проверок —
   только наши RESULT (имена там старые; соответствие старых и новых имён —
   `renamemods/name-map.tsv`): PINCHECK `690bdea1c7` (8 исходных контролей), REALCONTRACTS `d648179493` и
   REALCONTRACTSTWO `588c002998` (три нарушения `requires`), PERMTAGS `6542b3c4ba` (дубль тега), TIDYDOCS
   `01c090dc1d` (write set счётчика). Для каждого контроля в пакете: ожидаемая проверка (описание и место),
   ожидаемое `expect_check`. Принимать контроль, только если **все** упавшие проверки — назначенные; любой
   посторонний отказ — контроль не откалиброван.
2. **Четыре пары leaf/consumer** на итоговом дереве, каждая `expect: SUCCESS` с прежним числом covers:
   `helper_contracts::swap_safety_u8_backing9` + `helper_contracts::unstable_network_safety_u8_n9_stubbed`;
   `helper_contracts::swap_safety_u8_backing13` + `helper_contracts::unstable_network_safety_u8_n13_stubbed`;
   `helper_contracts_wide::swap_safety_u8_backing32` + `helper_contracts_wide::unstable_network_safety_u8_n32_stubbed`;
   `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` +
   `helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed`.
3. **Cfg-on compiler inventory**: ровно 246 ожидаемых новых имён (`renamemods/cfg-on-expected.txt`), без новых
   предупреждений в `smallsort/verify`.

## Сборки

- **G1:** kind diagnostic, `controls: true`, `inventory: false`, jobs 1, standard4. 21 строка: 13 контролей
  (`expect: FAILED` + `expect_check`) и 8 строк пар. Лимит на корень — по самым длинным строкам пар с запасом
  (прежние времена — наши RESULT VEIGHTROWS/VEIGHTMAX/REALCONTRACTSTWO); лимит сборки — компиляция cfg-on + строки
  × лимит + запас.
- **G2:** kind inventory, `controls: true`, без строк; лимит — по OPTINMOVE/RENAMEMODS (~42–47 мин компиляции с
  inventory) с запасом.

## RESULT

**RESULT-INTEGCHECK.md**, ≤ 40 строк: identities (library SHA/tree, равенство tree с RENAMEMODS); таблица 13
контролей (status, упавшие проверки — полный состав, совпадение с назначенной); таблица 8 строк пар (status,
время, covers, прежнее время); cfg-on inventory (число, SHA256 sorted, совпадение); warnings; расход.

## Коммиты

- Только research-коммиты `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Library, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **INTEGCHECK ЗАВЕРШЁН**, одна стадия, затем стоп.
