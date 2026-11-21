# Кампания 13. Handoff merge-пакета C

Локально подготовлены два plain proof фактического `small_sort_network` для N18/N19 и один литеральный контроль N19. Request имеет статусы `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. Для запуска нужны отдельные review и GO. [Задание Pilot 13](PILOT13-IMPL-TASK.md) · [Merge-план](MERGE-PLAN.md) · [Handoff Pilot 12](PILOT12-IMPL-HANDOFF.md)

## Идентичности

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `b7cea7f60a6a8a928c9cf3a60f043ce58a71c009` | `b7d5c17fec426174c0984c8206b154b9efe47fae` |
| Control | `/root/kani-ch8-q-pilot-control-v12`, `experiment/ch8-q-pilot-control-v13` | `65a35d901fc6110f90a84c225c03bdf5289595c2` | `1f8541a233cf45ea0e1ce06294d8c81654cc6264` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Цепочка std от A к C идёт через `2dc2afe895679773f443642685fabaab049d80bd` → `4707a7354a2f3240493d030dfae7d618706f8a1a` → `8ae402976537da81229392ba72bfa48b4d798260` → кандидат C. Единственный parent C имеет tree `df16bb43dca10bd8873b89ae3f90e6abfd2efe62`. Дельта C состоит из добавлений в `sorting_q_merge.rs`. Runtime, comparator, существующие clauses и корни сохранены побайтно. В прежнем oracle сохранён `CAP=17`, в oracle B сохранён `MergeSnapshot: Clone + Copy`.

У control единственный parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. База содержимого 12b — `38ef437cb85def0736150ae12509349c2f176dc0`, tree `288cf434a379a8d06dff4a21e732cb6e081481e0`. От неё изменены roster, std pin/tree, хэши и тестовые fixtures. Workflow сохранён побайтно, включая event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` и историческое имя шага `Run seven q-pilot roots`. Число запусков задаёт roster из трёх строк. `merge_a` остаётся в таблице профилей для синтетических тестов runner. В frozen roster все строки используют `merge_b`. [Request кандидата](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json)

| Control-файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `f2d58cfa721bffe9f22d2d6913e3713cfc9c90cfb7e0f308ca8d9298273a65fa` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `ddbefc55bcc071e51c7cf9c961c6358205976c8897ce625fae84c3063fd9af0e` |
| `ch8-q-pilot-control/test_run.py` | `e812677b2e8ea09b889eb342a9f41d2a3b9d15511e564f3380a5a5c312d0237a` |

| Std-файл относительно `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `9adbedd4ee038ea711f9c82546b6080578adcee27a0617d304bd2453b737f8d4` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `ae7fc39b86f5cbade2fd8a62f9b6493636144478a84acee9776a7a85a12e634d` |
| `smallsort/verify/sorting_q_merge_model.rs` | `1435cbd9b8ab0b42623314dcb5e821b3343ac7a231f591ec04026614e3d7d08d` |

## Exact roster и профиль

Префикс селекторов — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Все три корня имеют `#[kani::proof]` и `#[kani::unwind(36)]`. Ordinary stubs пусты. Итоги в таблице ожидаемые.

| № | Root ID | Суффикс selector | Verified stubs | Child, с | Ожидание |
| ---: | --- | --- | --- | ---: | --- |
| 1 | MC-NETWORK-N18 | `mc_network_n18_b01` | `swap_if_less`, `bidirectional_merge` | 600 | SUCCESS |
| 2 | MC-NETWORK-N19 | `mc_network_n19_b01` | `swap_if_less`, `insert_tail`, `bidirectional_merge` | 600 | SUCCESS |
| 3 | MC-N19-QPOST-CORRUPT | `mc_network_n19_corrupt_literal` | `swap_if_less`, `insert_tail`, `bidirectional_merge` | 600 | Одна FAILURE `MC_N19_CORRUPT_QPOST` |

`merge_b` задаёт `kani_smallsort_sorting`, `kani_smallsort_q_pilot`, `kani_smallsort_q_merge` и `kani_smallsort_q_merge_b`. S2, q-mutant и bad-tie выключены. Tool pin использует CaDiCaL по умолчанию. Сохранены 12 object bits, `--exact --jobs=1 --no-assert-contracts`, unwind36, OFF, отдельные target dirs и пустые дополнительные CBMC args. В OFF остаются обычные memory, bounds, overflow и unwind checks. Native uninit/validity требуют отдельного ON-прогона. [Выбор solver на tool pin](/root/kani-upstream-ch8-s1/kani-driver/src/call_cbmc.rs:103)

Один setup/build до 1 800 с, три последовательных child по 600 с, job 180 мин и резерв финализации 540 с. Latest start каждого корня за 630 с до supervisor cutoff. Nominal RSS cap 10 GiB, outer 12 GiB, резерв 2 GiB. Effective child cap берётся как минимум local cap и доступного process-group budget. Capture caps stdout/stderr/export составляют 16/1/8 MiB, суммарно 256 MiB. Cleanup, сбор bounded наблюдений и сохранение первопричины, в том числе `NOT_RUN` у невыполненной строки, унаследованы от 12b.

## Привязка Check и Replace

Результаты провайдеров ниже взяты из сводок координатора. Сверка исходников и профилей локальная. Native inventory, перенос сводок и допуск требуют отдельной qualification. [Сводка 11](run-44872078840/SUMMARY.md) · [Сводка 12b](run-44876372471/SUMMARY.md) · [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)

| Replace в C | Check и зафиксированный итог | Геометрия и обязательство consumer |
| --- | --- | --- |
| `swap_if_less`, все три корня | 11, `MA-SWAP-BYTE-Q`, SUCCESS, 0/614 failures, 9/9 covers | `u8/KeyLess<u8>`, инициализированный V34, произвольные байты и q, base 1 или 10 и `a < b < 9`. У каждой сети 25 фактических пар, всего 50 вызовов на корень. Posts задают AND/OR для q и min/max полных байтов, footprint состоит из двух байтов. |
| `insert_tail`, оба N19 | 11, `MA-INSERT-RIGHT`, SUCCESS, 0/746 failures, 7/7 covers | V34, begin `v+10`, tail `v+19`, relative 9. Caller проверяет native pointer Pre и q-монотонность старых девяти байтов. Полный числовой порядок старого префикса через условный numeric post даёт числовой порядок всех десяти байтов. Footprint `v[10..20]`. |
| `bidirectional_merge`, N18 | 12b, `MB-MERGE-N18`, SUCCESS, 0/692 failures, 6/6 covers | `&v[1..19]`, split 9+9, отдельный scratch32, dst+0. Consumer устанавливает native `merge_halves_numeric_order` и `merge_geometry` у фактического вызова. |
| `bidirectional_merge`, оба N19 | 12b, `MB-MERGE-N19`, SUCCESS, 0/692 failures, 6/6 covers | `&v[1..20]`, split 9+10, отдельный scratch32, dst+0. Те же native Pre, девять пар записей и фактический odd copy в slot 9 у Check. |

- **Переход A → C.** Сверены байты actual swap и insert, их clauses, comparator и используемая часть моделей. Между A и 12b в `smallsort.rs` добавлен только guarded B-блок у whole merge. Определения A сохранены, включая обычную q-сводку swap и условную numeric-сводку insert. Добавленный cfg `kani_smallsort_q_merge_b` не меняет clauses листьев при выключенных S2, q-mutant и bad-tie. Tool commit/tree, argv, object bits и режим проверок совпадают по локальным request A/12b/C. Пробы `MA-H9-L1`, `MA-H9-R10` и `MA-H10-R10` из 11 дают сверку маршрута и стоимости. В C обе `sort9_optimal` и оба прохода insertion loop сохраняют actual тела. N18 не вызывает вставку. N19 вызывает одну правую вставку. Harness не добавляет assumptions о порядке. [Actual network](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Провайдеры A](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:52)
- **Переход 12b → C.** Whole-merge Replace возвращает `()` и использует точный B Check для длины. Pre требует initialized readable source после presort, writable disjoint dst и полный числовой порядок обеих половин. Вход capture у контракта — source, без old-read dst. `modifies` ограничивает запись первыми N байтами scratch и сохраняет source и q вне footprint. В actual Check две последовательности copy пишут offsets 0–8 и 9–17 для N18 либо 0–8 и 10–18 для N19. Фактический odd copy закрывает offset 9 у N19 перед guard. На normal return это покрывает все N слотов. C получает этот участок через whole-merge Replace, затем фактический `copy_nonoverlapping` переносит ровно N байтов из scratch в исходный активный срез. Хвост scratch остаётся за пределами чтения и записи. [B-clauses](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1029) · [Actual записи и guard](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1107) · [Oracle B](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:295)
- **Plain post и frame.** Каждый positive независимо выбирает initialized V34 и q, проверяет активацию byte/q-моделей, сохраняет `before=v` и вычисляет B capture на исходном активном срезе. После actual copy-back `merge_q_post` проверяет пороговую маску в том же срезе. q-frame и равенство префикса `[..1]` и суффикса `[1+N..]` проверяются отдельно. Шесть covers включают mixed threshold, соседние равные байты, q=0, q=255, отсутствие q в исходном активном срезе и useful return после постпроверок. [N18](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:632) · [N19](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:683)
- **Контроль N19.** При q=1 весь `v[1..20]` заполнен нулями до snapshot и вызова. Остальные байты произвольны. Та же Replace-цепочка проходит actual network, после которого `MC_N19_CORRUPT_USEFUL_RETURN` покрывает `v[1]==0`. Без развилки присваивается `v[1]=255`, и `MC_N19_CORRUPT_PATH` покрывает это состояние. Сохраняются q-frame и outside frame. Ожидаемый target 0 расходится с маской после порчи, где бит 0 равен 1. Назначенное утверждение находится в `mc_network_n19_corrupt_literal`. Native ID, class и location для фактического отказа остаются открытыми до прогона и сверки двух covers и единственной FAILURE. [Контроль](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:734) · [Исходная метка отказа](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:762)

## Локальные проверки и открытые обязательства

- Прошли `rustfmt 1.11.0-nightly (7189d39d9c 2026-10-22) --edition 2024 --check` на verification-модуле и `git diff --check` для дельт. Статически сверены три guards/selector/Replace, 29 уникальных меток, порядок capture/call/post, actual call-site и scratch geometry. Из исходника извлечены 25 пар sort9, проверены обе базы в каждом маршруте и все 512 бинарных входов девятиэлементной сети. Отдельно сверены формула пороговой маски и literal witness.
- `validate` с синтетическими GitHub metadata подтвердил control commit/tree/parent, событие, ref, попытку и хэши. `check-source` подтвердил чистые std/tool checkout, commit/tree и все восемь std SHA-256. `python3 -m unittest -v test_run.py` прошёл 14/14 на синтетических Python-процессах. Проверены exact argv/roster, 10 GiB и нижний effective cap, 630 с latest start, лимиты capture, cleanup, drift и унаследованные error paths.
- Cargo, rustc, Kani, CBMC и CI не запускались. Пушей не было. Компиляция, исходы root, native caller Pre для insert и merge, полнота safety/inventory/covers и применимость сводок к наблюдаемым property IDs остаются открытыми. При cutoff сохранять исходную причину, последнюю фазу, наличие и размер первой CNF, effective cap, PGID/component RSS, VT и child time. Риск памяти остаётся высоким у N18 и выше у N19 с правой H10. [Порядок действий при cutoff](PILOT13-IMPL-TASK.md)
