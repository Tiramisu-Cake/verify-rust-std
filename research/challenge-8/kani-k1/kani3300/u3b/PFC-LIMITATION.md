# PFC/uninit — known limitation U3B

На проверенном v2 и standard4 оба изолированных proof_for_contract root с `modifies(out)` и `-Z uninit-checks`
завершаются с **Kani-reported OOM**. Те же bodies/contracts/DFCC при выключенном uninit-checks проходят.
Это наблюдение ограничено двумя fixtures и данным runner; полный класс PFC, конкретный write set MEM_INIT_STATE
или механизм расхода памяти этим сравнением не установлен. Полная U3/PFC приёмка не выполнена.

## Точные воспроизведения

Полный test-коммит `0ab9cc703aed799f6f73d826b60281a4632ab585`, parent `81dd85bfce67226e283fdd9a156932e32ece080b`.
Production — прежний U3 repair1. Build от полного pin `f046b70644e113be0df9c22c2e6ea44a65a57566`
с build-патчем `d9417e68ec3ee9c8c27bb8e7ac829e2af712c4d124ac59078416ab34feebd85c`;
applied tree `4de67d7ead14bdc4060d2b08060e7ee7651625bb`.
Kani 0.68.0 standalone / CBMC 6.11.0; gcb-e2-standard-4, 4 CPU, summary-reported container memory15.6GiB.

| root | source под tests/expected/uninit/ | on: selector wall / test s | matched off: selector wall / test s |
|---|---|---|---|
|contracted_roundtrip_harness|maybe-uninit-buffer-u3b-pfc-positive/main.rs|OOM:50.284 /50.10|SUCCESS:5.400 /3.03|
|contracted_uninit_read_harness|maybe-uninit-buffer-u3b-pfc-negative/main.rs|OOM:51.350 /51.08|SUCCESS:5.107 /2.81|

Каждый source — 29 строк, один exact root и только нужные два relay helpers + modifies-target.
Пути контрольных копий отличаются суффиксом `-no-uninit` у directory; сами файлы отличаются только удалением
`-Z uninit-checks`. Никаких дополнительных assumptions/stubs, иных contracts, DFCC flags или тела контроля.
Положительный root сохраняет discard незаполненного значения, затем чтение результата с полностью заполненными inputs;
отрицательный читает незаполненный второй аргумент после nested return. Golden on-negative всё ещё требует actual uninit FAILURE u16.
Список всех исходников/goldens и проверенное равенство файлов полному test-коммиту — BUILD-PATCH-INVENTORY.json / STATIC-CHECKS.json.
Полный набор исходных тестов оставлен в fix/kani-3300-v2 и полном test-патче.

Параметры воспроизведения (описание native invocation; локально не запускалось):

```text
kani tests/expected/uninit/maybe-uninit-buffer-u3b-pfc-positive/main.rs -Z uninit-checks -Z function-contracts --output-format=terse --harness contracted_roundtrip_harness --exact
kani tests/expected/uninit/maybe-uninit-buffer-u3b-pfc-negative/main.rs -Z uninit-checks -Z function-contracts --output-format=terse --harness contracted_uninit_read_harness --exact
```

Native manifest использует expected suite/mode с edition2021 из source; require-success=true у positive и обеих off-копий,
selector timeout150s, общий native budget10min. Cloud Build9f964706-4b89-4340-a1ee-022aa23ecbe9; exact source a3e082da37f65095f85ebf998170775d7b75db9c.
Дальнейший запуск/уменьшение repro/смена runner требуют отдельного задания/GO; эта стадия не разрешает repair.

## Причина и пределы evidence

В `native-field ... 0 output_excerpt` и `... 2 output_excerpt` сохранены unclipped `kani_stdout:7`:
`CBMC appears to have run out of memory.` и `kani_stdout:10` с именем соответствующего root.
Оба имеют Complete0SUCCESS/1failure/1total; native compiletest FAILED, exit1; producer validation VALIDATED.
Это явное сообщение инструмента. RSS по root, RSS всего run и kernel/cgroup kill confirmation недоступны;
whole-run RSS/wall — MISSING, memory cap не tracked. Поэтому аппаратный OOM независимо не подтверждён.
`wall_s` — время selector wrapper; `time_s` — время native test, оба не являются solver-only time.
В собственных объектах native0–3 нет per-root memory fields; bounded records/metadata сохранены целиком в страницах.

В negative excerpt `compiletest_stdout:10` печатает отсутствующую expected golden строку Failed Checks.
В `kani_stdout`/`kani_stderr` required_substring_found=false; только compiletest_stdout=true,
но он не участвует в gate diagnostic. Нельзя считать эту строку наблюдённым uninit property FAILURE.
Положительный off и отрицательный off PASS с require-success и golden1SUCCESS; producer не сохранил literal success excerpt.
Off-negative содержит UB по исходнику, поэтому его SUCCESS служит диагностическим контролем и не даёт correctness credit.

Frame negative с усиленным golden passes: assigns FAILURE *var_7 и source file/line22:5; wrap7, review7,
plain u16 negative и U1T overwrite-copy negative проходят. Здесь property/count привязаны к exact golden и validated native PASS;
отдельных excerpt для прошедших selectors producer не сохраняет. Полная PFC-пара с uninit остаётся непроходящей.

Предложение координатору: **known limitation с малыми repro** для сочетания PFC+modifies+uninit на standard4;
любую формулировку ready-for-review v2 ограничить этим фактом и не заявлять полную U3/PFC compatibility.
OOM не является контрпримером soundness; unexpected SUCCESS on-negative не наблюдался.
Фикс конкретной production-механики пока не обоснован. Новых Builds/patches в рамках завершённой стадии нет.

Evidence — POST-BUILD-OBSERVATIONS.json, TOOLING-CHECK.json и bounded files в evidence/native-9f964706/;
full/raw logs/archives не читались, general/independent proof credit не установлен.
