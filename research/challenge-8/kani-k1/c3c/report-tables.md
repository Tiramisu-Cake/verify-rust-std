# Таблицы bounded-результатов C3c

Сформировано по bounded summary pages, exports строк, peaks/process summaries, metadata сессии и входным TSV времени. Полные verifier logs не читались; proof/build команды не запускались.

## Сборки и время

Стоимость — расчёт по Cloud wall при ставке `$0.0135/min`, если в derived measurements нет готового ledger value; резерв показан отдельно. `NA` означает, что bounded evidence отсутствует.

| Запуск | Build ID | Source SHA | Статус Cloud | Статус Kani | Gate | Cloud wall, с | Kani wall | Расчётная стоимость, USD | Резерв, USD | Evidence |
|---|---|---|---|---|---|---:|---|---:|---:|---|
| [baseline](evidence/) | ba81d888-90db-49c7-a04d-d6dbb9108fac | 7b6bf1ede05d5a8369fdc0dc455b340c79a7ef03 | FAILURE | INCONSISTENT | False | 1369.5 | 16:27.83 | 0.3105 | 1.2960 | [папка evidence](evidence/) |
| [candidate-setup-failed](evidence/) | dfada6fc-2f83-4c2e-abf5-2ce45c6e3e81 | af406030589a1d733709a3376b5b1fa1bb1dfc2e | FAILURE | RUNNER_ERROR | False | 401.0 | NA | 0.0945 | 2.4300 | [папка evidence](evidence/) |
| [candidate](evidence/) | fa7d2d00-8470-40e3-be55-c96f0eaa76dc | 66a7ad1fae733121cde66cc6dcf2e0ebf8b2122f | FAILURE | INCONSISTENT | False | 1553.5 | 19:39.31 | 0.3510 | 2.4300 | [папка evidence](evidence/) |
| [autoharness](evidence/) | be070a8b-f0ca-4d6c-8f86-f8aff7915cbd | 2cc4a5871bf6da42d23137208247c0cf8dacb44c | FAILURE | PARTIAL | False | 17703.8 | NA | 3.9960 | 4.0500 | [папка evidence](evidence/) |
| [baseline-memory](evidence/) | e358163c-9006-4ea0-a402-c12a5a009747 | f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 | FAILURE | COMPLETE | False | 2219.0 | 29:38.32 | 0.4995 | 2.1600 | [папка evidence](evidence/) |
| [candidate-memory-1](evidence/) | 5ae76959-e306-4b33-9506-402bc9909768 | 1216fc2884f01af67d6328fd927edce418933af9 | FAILURE | COMPLETE | False | 1686.0 | 21:23.49 | 0.3915 | 2.4300 | [папка evidence](evidence/) |
| [candidate-memory-2](evidence/) | 4722df9d-7a70-46d1-b761-deef420bb1f2 | eefb512a3fe8e30c31645eb63141f2a5179e39d8 | SUCCESS | COMPLETE | True | 838.3 | 8:44.83 | 0.1890 | 2.0250 | [папка evidence](evidence/) |
| [controls](evidence/) | 0b2482ba-6db6-4125-8aa1-2503a7a8ccf4 | 34c3cf02580266542d2122707bc4d955527d0641 | FAILURE | COMPLETE | False | 781.9 | 6:32.83 | 0.1890 | 0.8100 | [папка evidence](evidence/) |

## Память процессов

HWM — независимый максимум каждого процесса; одновременные RSS максимумы измерены совместно и указаны со временем. Независимые HWM не складываются как общая RAM.

| Запуск | HWM driver KiB @с | HWM CBMC KiB @с | HWM solver | Одновременный RSS CBMC KiB @с | Одновременный RSS driver KiB @с | Суммарный sampled RSS KiB @с | Источник |
|---|---:|---:|---|---:|---:|---:|---|
| baseline | 1913392@317 | 4125308@674 | NA | 8287232@620 | 1813648@315 | 9819292@620 | [peaks/process summaries](evidence/) |
| candidate-setup-failed | NA | NA | NA | NA | NA | NA | [peaks/process summaries](evidence/) |
| candidate | 5263720@533 | 2576084@253 | NA | 4322320@180 | 5263720@533 | 8482016@523 | [peaks/process summaries](evidence/) |
| autoharness | 8453412@12331 | 4552300@10708 | kissat:first_s:2079; hwm_kb:44852; last_s:2594; peak_s:2089 | 8785312@10754 | 8453412@12331 | 14198868@10754 | [peaks/process summaries](evidence/) |
| baseline-memory | 5799796@392 | 4324924@1206 | NA | 7303540@912 | 5785276@390 | 11560520@912 | [peaks/process summaries](evidence/) |
| candidate-memory-1 | 860568@1094 | 2607828@682 | NA | 5214240@543 | 860568@1094 | 5715232@567 | [peaks/process summaries](evidence/) |
| candidate-memory-2 | 5661708@429 | 1286420@385 | NA | 2784984@96 | 5661708@429 | 6718016@427 | [peaks/process summaries](evidence/) |
| controls | 6419416@392 | 1414408@96 | NA | 3404276@201 | 6419416@392 | 7088568@213 | [peaks/process summaries](evidence/) |

## P6 Mac CI: известные VT и сравнение с C3c autoharness

Сравнительные метрики P6 — предоставленные Verification Time counts/sums/share. Для P6 нет whole-job wall, RAM или стоимости. Три task-заданных Mac timeout по 600s показаны отдельно и не входят в TSV-суммы.

| Запуск | Все гармоники: строки / VT, с | SmallSort: строки / VT, с | Доля SmallSort | Cloud wall | Пик памяти | Стоимость |
|---|---:|---:|---:|---:|---:|---:|
| P6 Mac TSV, run 40748125754 | 2313 / 28518.6 | 322 / 25367.5 | 89.0% | NA | NA | NA |
| C3c autoharness | 1959 / 25773.944 | 238 / 18045.638 | NA | 17703.8s | 14198868 KiB | 3.996 USD |

Mac timeout names: merge::merge_contract_u64_n16, network::insertion_permutation_u64_n12, network::insert_tail_contract_u64_start1. C3c request limit is 270 min work plus 30 min build overhead; это бюджет текущего build, не метрика P6. Без полного baseline autoharness нельзя утверждать измеренное улучшение полного задания или причину исторического завершения Ubuntu.

## Калибровка по типизированным группам моделей

Отношение — Mac/GCB Verification Time. Точечная оценка требует timed Mac и успешного timed GCB. При Mac timeout 600s и GCB success приводится нижняя граница; при GCB timeout и Mac success — верхняя. Dual-censored наблюдение не задаёт конечную границу. Калибровка не является приёмкой.

| Группа моделей | Точечных | Цензурированных | Медиана | P90 | Максимум точек | Нижние границы | Верхние границы | Дважды цензурировано | ID источников |
|---|---:|---:|---:|---:|---:|---|---|---:|---|
| assembly.primitive_witness | 3 | 0 | 0.510 | 0.576 | 0.576 | NA | NA | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| assembly.zst | 5 | 0 | 0.481 | 0.584 | 0.584 | NA | NA | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| correct.fallback.u64 | 1 | 0 | 0.404 | 0.404 | 0.404 | NA | NA | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| correct.general_stable.u8 | 1 | 0 | 0.440 | 0.440 | 0.440 | NA | NA | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| merge.contract.u64 | 1 | 3 | 0.343 | 0.343 | 0.343 | NA | 1.401, 1.350 | 1 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| merge.general_stable.u64 | 1 | 0 | 0.302 | 0.302 | 0.302 | NA | NA | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| merge.upper_route_safety | 0 | 2 | NA | NA | NA | NA | 1.400, 1.685 | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| network.correctness.u64 | 2 | 2 | 0.407 | 0.514 | 0.514 | NA | 1.597, 1.560 | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| network.correctness.u8 | 0 | 2 | NA | NA | NA | NA | 1.500, 1.358 | 0 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| network.insertion_permutation.u64 | 0 | 1 | NA | NA | NA | NA | NA | 1 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |
| network.tail_contract.u64 | 0 | 2 | NA | NA | NA | NA | 1.950 | 1 | 40748125754, 6cfc76cb211d088aebaff8a449bcac953e97f942, e358163c-9006-4ea0-a402-c12a5a009747, e96555151df91080fa0ccc106f60ee38a919c50e, f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810 |

## Память по отдельным harnesses

Подробности: [per-harness-memory.tsv](per-harness-memory.tsv), 80 строк. Проверка прямой атрибуции: baseline-memory: 26 rows / 26 однозначных CBMC harnesses (AVAILABLE); candidate-memory-1: 30 rows / 30 однозначных CBMC harnesses (AVAILABLE); candidate-memory-2: 24 rows / 23 однозначных CBMC harnesses (AVAILABLE). Если прямой привязки нет, поле остаётся `NA`; active-set не связывает пик CBMC с отдельным harness. Solver HWM приписывается harness только через точный CBMC parent PID.

## Старые домены и все successor-модели

Выбрана серия **memory-5m**, cutoff **5 min**. Серии 3m и 5m не смешиваются. Пятиминутная серия полная: **true**; трёхминутная серия полная: **true**. Проверка inputs: baseline-memory 26/26 rows, cutoff 5m; candidate-memory-1 30/30 rows, cutoff 5m; candidate-memory-2 24/24 rows, cutoff 5m; baseline 22/22 rows, cutoff 3m; candidate 50/50 rows, cutoff 3m. Если серия 5m неполна, отсутствующие rows/pages/builds показаны как `NA`, а парное сравнение использует целиком 3m серию либо `NA`. Candidate суммы содержат только наблюдавшиеся VT; timeout/untimed successors остаются censored и считаются отдельно. Build IDs показаны как source IDs.

| Семейство | Старых доменов | Строк successor | Наблюдаемая сумма VT, с | Максимум VT, с | Цензурировано/нет данных | ID источников |
|---|---:|---:|---:|---:|---:|---|
| correct | 2 | 3 | 291.528 | 142.251 | 0 | 4722df9d-7a70-46d1-b761-deef420bb1f2 |
| merge | 7 | 11 | 567.684 | 105.073 | 3 | 4722df9d-7a70-46d1-b761-deef420bb1f2, 5ae76959-e306-4b33-9506-402bc9909768 |
| network | 9 | 32 | 645.902 | 58.325 | 5 | 4722df9d-7a70-46d1-b761-deef420bb1f2, 5ae76959-e306-4b33-9506-402bc9909768 |

Полные per-domain/per-successor данные находятся в `report-metrics.json`.

## Аудит controls

| Сборка | Harness | Статус | Covers satisfied/total | Gate | Аудит cover |
|---|---|---|---:|---|---|
| controls | slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u64_n8 | SUCCESS | 1/1 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::correct::contract_insert_tail_u8_prefix | TIMEOUT | NA | False | FAIL |
| controls | slice::sort::shared::smallsort::verify::merge::merge_contract_u64_n5 | SUCCESS | 1/1 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n2 | SUCCESS | 2/2 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::network::swap_contract_u8_n2 | SUCCESS | 5/5 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail2 | SUCCESS | 3/3 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_bytes16_n15 | SUCCESS | 1/1 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::network::mutating_route_permutation_cell_n2 | SUCCESS | 7/7 | False | PASS |
| controls | slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_u8_n14 | SUCCESS | 1/2 | False | FAIL |
| controls | slice::sort::shared::smallsort::verify::correct::sorted_permutation_stable_u8_n14 | SUCCESS | 1/2 | False | FAIL |
Выборочный covers-аудит: FAIL / INCOMPLETE. Полнота request names и COMPLETE summary проверены.
Строки controls проверяются на SUCCESS и covers `satisfied == total > 0`; это не автоматическая приёмка.

## Реестр риска ordinary inventory

Строк, привязанных к inventory: **421**; реестр **доступен**. См. [risk-register.tsv](risk-register.tsv). Сначала идут TIMEOUT/FAILURE/пропущенные результаты, затем числовые прогнозы. Source-predicted inventory не считается завершённым remote inventory.

| Harness | Статус | GCB VT, с | Точечный прогноз Mac, с | Перенос наблюдённого хвоста, с | Флаги |
|---|---|---:|---:|---:|---|
| slice::sort::shared::smallsort::verify::correct::sorted_permutation_fallback_u64_n10 | MISSING_RESULT | NA | NA | NA | RUN_PARTIAL, MISSING_RESULT, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_drop_count_n2 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_drop_count_n4 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_drop_count_n8 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_tag_permutation_n2 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_tag_permutation_n4 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_fallback_tag_permutation_n8 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_drop_count_n16 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_drop_count_n2 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_drop_count_n4 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_drop_count_n8 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_tag_permutation_n16 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_tag_permutation_n2 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_tag_permutation_n4 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |
| slice::sort::shared::smallsort::verify::merge::drop_general_tag_permutation_n8 | NO_RESULT_ROW | NA | NA | NA | RUN_PARTIAL, NO_RESULT_ROW, NO_MAC_POINT_FORECAST |

## Ограничения

- Нет полного baseline-autoharness запуска: нельзя утверждать измеренное улучшение полного задания или причину исторического завершения Ubuntu.
- Три точных Ubuntu harnesses, активных при остановке, не определяются по предоставленному TSV; имена не угадываются.
- Суммы VT P6 не являются wall time, памятью или стоимостью задания; бюджет текущего C3c build задаётся отдельно.
- В Mac TSV нет RAM или wall-time; суммы включают только строки со временем, без трёх timeout по 600 секунд.
- Время — Verification Time. Сумма split successors — наблюдаемая сумма VT, не wall time и не время одного harness.
- Отдельные максимумы HWM по процессам не складываются как RAM; для общей нагрузки используйте одновременный RSS с временем измерения.
- Censor bounds не являются точечными коэффициентами; перенос к изменённым моделям — прогноз, не приёмка.

Вход генератора: `measurements.json`, schema `c3c-analysis-v1`; session и bounded pages находятся в `evidence/`. Отсутствующие данные отмечаются `NA`, а не восстанавливаются догадками.
