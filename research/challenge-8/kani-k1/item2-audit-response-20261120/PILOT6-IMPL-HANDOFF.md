# Кампания 6 q-пилота — handoff реализации

Локальный control-кандидат для A/B `--refine-arrays` подготовлен. Режим `RESEARCH_ONLY`, request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Слоевая декомпозиция sort13 отложена по решению координатора. [Задание](PILOT6-IMPL-TASK.md) · [Анализ кампании 5](PILOT-RUN5-ANALYSIS.md)

## Пины

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| Control | `/root/kani-ch8-q-pilot-control-v1`, `experiment/ch8-q-pilot-control-v6` | `87c9919ffa3de7d63e6d4cf15f29209ec30ba821` | `a84a1eb9ec12561c62afe49edc2f793e5a6e71e9` |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `c8b703918a40c03d5b889d3018d8d818a70c233f` | `7ebee5d0bf4a1b1b0fb53c21f30e41c49294aed5` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Ветка control создана из v5 `d453bb80a574ffbfd09a6f9d8dcdc08d118ea9a1`. У кандидата единственный parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Относительно v5 изменены только request, runner и его тесты. Frozen event ref — `refs/heads/uninit-ci/ch8-q-pilot-v1`.

| Файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `0941c91a81d9fda3989c5f37b7bd83873cc4d4f042e56004563de059a478336c` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `ef2d23bfba0dfac3053c24868fc9946309d3b0fce9f8109caa1a26642e4a6819` |
| `ch8-q-pilot-control/test_run.py` | `477e162ea12853acb0febd4cdb384a661b7c3f5bf8d63ccad8550431a649adcc` |

## Roster

| Порядок | Корень | Суффикс exact selector | Object bits | Дополнительные аргументы CBMC | Таймаут child, с |
| ---: | --- | --- | ---: | --- | ---: |
| 1 | `P17-STATS` | `d13_check_p17` | 12 | `[]` | 180 |
| 2 | `P17-REFINE` | `d13_check_p17` | 12 | `--refine-arrays` | 180 |
| 3 | `P-2b-OB11-REFINE` | `p2b_sort13_u8_b01_len17_q_any_actual_swaps` | 11 | `--refine-arrays` | 600 |
| 4 | `P-2-OB11-REFINE` | `p2_sort13_u8_b01_len17_q_any` | 11 | `--refine-arrays` | 600 |

Префикс всех селекторов — `slice::sort::shared::smallsort::verify::sorting_q_pilot::`. P-2b исполняет реальные swap. P-2 использует `stub_verified(swap_if_less)` на 45 вызовах. Корни идут последовательно с `normal` cfg, unwind 36, `--no-assert-contracts`, `--jobs=1` и CaDiCaL по умолчанию tool. Локальный cap 6 GiB, outer 12 GiB, резерв 2 GiB. Сумма child timeouts — 1 560 с, окно setup/build — 1 800 с.

Runner сверяет упорядоченный roster целиком, включая списки `cbmc_args`. Он добавляет эти аргументы после `--cbmc-args --object-bits <N>` и пишет их в `roots[].cbmc_args` и `roots[].invocation.cbmc_args` при наличии подготовленного запуска. Для начавшихся запусков raw index содержит полный `roots[].argv`. Таймаут строки задаёт `--harness-timeout` и таймаут дочернего процесса. Latest start вычисляется из общего cutoff за вычетом таймаута строки и 30 с на запуск.

## Совместимость флагов по исходникам

- `kani-dependencies` на пине tool задаёт CBMC 6.11.0, локальный тег `cbmc-6.11.0` соответствует `820ff0f555b43fb78e0cd9332e498461bd14244b`. CBMC регистрирует оба флага в `src/cbmc/cbmc_parse_options.h` и `src/goto-checker/solver_factory.h`. Kani принимает их в хвосте `--cbmc-args` и копирует в backend argv в `call_cbmc.rs:301`. `--refine-arrays` включает bit-vector refinement, который использует тот же выбор SAT solver. См. `solver_factory.cpp:112–123,416–438,782–786`.
- `--show-array-constraints` исключён из обоих P17. Kani с `--output-format=regular` уже добавляет `--json-ui`, как требует CBMC. По завершении eager conversion обычный solver выдаёт отдельный JSON-элемент с `arrayConstraints` и `numOfConstraints`. `ParserItem` на пине Kani не содержит такого варианта, а `parse_item` вызывает `unwrap()` при ошибке разбора. Если CBMC дойдёт до вывода статистики, этот элемент сломает поток Kani. См. `cbmc_parse_options.cpp:543–551`, `arrays.h:42–47`, `arrays.cpp:921–943`, `message.cpp:161–170`, `ui_message.cpp:239–260` и `cbmc_output_parser.rs:44–61,450–465,492–520`.
- Refinement использует отдельную фабрику, которая не передаёт параметр счётчиков в `bv_pointerst`. Поэтому `P17-REFINE` всё равно не дал бы статистику массивов. ID `P17-STATS` сохранён для соответствия заданию и обозначает базовый замер P17. В фактическом A/B единственная разница в настройке CBMC между корнями P17 — `--refine-arrays`. Сравнимы фазы, первая CNF, RSS и статус завершения. При чтении первой CNF refinement нужно учитывать последующие итерации, которые могут добавлять ограничения. См. `solver_factory.cpp:355–369,416–438` и `bv_refinement_loop.cpp:13–48`.

## Локальная проверка

- `run.py validate` на коммите control с синтетическими метаданными GitHub прошёл и подтвердил commit, tree, parent и хэши payload.
- `run.py check-source` подтвердил commit и tree чистых checkout std и tool и хэши шести файлов std. Все селекторы найдены в закреплённом `sorting_q_pilot.rs`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` прошёл 14 из 14 тестов. Проверены roster, exact selectors, argv, отклонение незакреплённых аргументов, запись аргументов в raw index, лимиты RSS, child timeout, latest start и очистка синтетических процессов. `git diff --check` прошёл.

Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Результаты A/B и статус формальной проверки открыты.
