# Кампания 14. Handoff Check sort9 и потребителей N18/N19

Локально подготовлены три exact Check фактического `sort9_optimal`, два plain proof фактического `small_sort_network` и один литеральный контроль порчи q-post. Request имеет статусы `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. Запуск требует независимого review и отдельного GO. [Задание Pilot 14](PILOT14-IMPL-TASK.md) · [Handoff Pilot 13](PILOT13-IMPL-HANDOFF.md)

## Pins и хэши

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `d02d5872c70e64ec912523b093d8359ba057c689` | `6faa236898be8b22e90179e00bbb8499b148d38c` |
| Control | `/root/kani-ch8-q-pilot-control-v12`, `experiment/ch8-q-pilot-control-v14` | `8794a0215d7bbbd61350a290be43328b55e72fb7` | `d45c212b5cf9db491d1966a3753584e5f8775f8f` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `b7cea7f60a6a8a928c9cf3a60f043ce58a71c009`, tree `b7d5c17fec426174c0984c8206b154b9efe47fae`. Дельта добавляет атрибуты к `sort9_optimal` и определения в двух verification-модулях. Побайтная сверка подтвердила идентичность runtime-тел и сигнатур, компаратора, clauses A/B, корней C13 и `CAP=17`.

Единственный parent control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. База содержимого v13 — `65a35d901fc6110f90a84c225c03bdf5289595c2`, tree `1f8541a233cf45ea0e1ce06294d8c81654cc6264`. В дельте к v13 только roster, новый cfg, std pin/tree, хэши и тестовые fixtures. Побайтно сохранён workflow с event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` и историческим именем шага `Run seven q-pilot roots`. Число запусков задаёт roster из шести строк. [Request](/root/kani-ch8-q-pilot-control-v12/ch8-q-pilot-control/CI-REQUEST.json)

| Control-файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `beaddb914204df0ec7be42247585632e6badcddf9c443bfa4370384c9cc71b3d` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `8063d1e40064b01fc58950bc3b8e1650af908a5dcca07bf3ea26db7163a0aaab` |
| `ch8-q-pilot-control/test_run.py` | `e51ede4c67e71631d34ff426e634e988c97553b9996e563ed4f3d336f971e2c4` |

| Std-файл относительно `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `f5aa0d038d8348b4c4f6f6fa62cc86fe0fb6f12b6fde3ec26f0985a08e7c9ce2` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `85b744c980a2357ccdada2e3d1907d440860a18dcc3a5f0d9759f1b69a19c760` |
| `smallsort/verify/sorting_q_merge_model.rs` | `01798c187deed6e2417ad0140d971508b32946eed309ffdc756343ff36f43bc3` |

## Exact roster и профиль

Префикс селекторов — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Для всех строк задан `merge_c_sort9`, ordinary stubs пусты, unwind36. Исходы в таблице ожидаемые.

| № | Root ID | Суффикс selector | Режим и вход | Verified stubs | Child, с | Ожидание |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | MD-SORT9-L1 | `md_sort9_left_b01_len09` | Check sort9, `v[1..10]` | `swap_if_less` | 600 | SUCCESS |
| 2 | MD-SORT9-R9 | `md_sort9_right_b10_len09` | Check sort9, `v[10..19]` | `swap_if_less` | 600 | SUCCESS |
| 3 | MD-SORT9-R10 | `md_sort9_right_b10_len10` | Check sort9, `v[10..20]` | `swap_if_less` | 600 | SUCCESS |
| 4 | MD-NETWORK-N18 | `md_network_n18_b01` | Proof, `v[1..19]` | `sort9_optimal`, `bidirectional_merge` | 600 | SUCCESS |
| 5 | MD-NETWORK-N19 | `md_network_n19_b01` | Proof, `v[1..20]` | `sort9_optimal`, `insert_tail`, `bidirectional_merge` | 600 | SUCCESS |
| 6 | MD-N19-QPOST-CORRUPT | `md_network_n19_corrupt_literal` | Proof, `v[1..20]` | `sort9_optimal`, `insert_tail`, `bidirectional_merge` | 600 | Одна FAILURE `MD_N19_CORRUPT_QPOST` |

`merge_c_sort9` добавляет `--cfg=kani_smallsort_q_merge_sort9` к `merge_b` с его normal guards. S2, q-mutant и bad-tie исключены. На заданном pin профиль использует CaDiCaL, 12 object bits, `--exact --jobs=1 --no-assert-contracts`, OFF, отдельные target dirs и пустые extra CBMC args. Обычные memory, bounds, overflow и unwind checks входят в OFF. Native uninit/validity требуют отдельной matched ON-проверки.

Шесть последовательных child по 600 с дают 3 600 с child budget. Setup/build один, до 1 800 с. Job 180 мин с резервом финализации 540 с. Latest start за 630 с до supervisor cutoff. Номинальный child cap 10 GiB, outer 12 GiB, резерв 2 GiB. Effective child cap берётся как минимум local cap и доступного process-group budget. Capture caps stdout/stderr/export составляют 16/1/8 MiB, суммарно 256 MiB. Bounded-наблюдения, cleanup, первопричина cutoff и `NOT_RUN` сохраняются по runner v13.

## Привязка Check к Replace

Каждый Check выбирает независимые initialized V34 и q через `kani::any()`, строит `KeyLess::<u8>::with_q(q)` и передаёт литеральный mutable slice без ограничений порядка. Native Pre проверяет пару `u8/KeyLess<u8>`, длину 9 или 10, читаемость всего span и возможность записи массива из первых девяти элементов. Allocation/base выбирает fixture, соответствие actual call site устанавливается отдельно по каждому маршруту. [Контракт](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:511) · [Модель](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:384)

Один `modifies(v.as_mut_ptr().cast::<[T; 9]>())` задаёт `v[0..9]` в координатах аргумента для Check и Replace. На pin thin lowering задаёт assigns на разыменованный массив и havoc через `ptr::write(pointer, T::any())`. Check дополнительно проверяет q и все байты V34 за пределами footprint. Для правого len10 outside frame включает `v[19]` до вызова `insert_tail`. Реальные native assigns на девяти байтах и эффект thin lowering на GOTO/DFCC остаются открытыми. [Lowering assigns](/root/kani-upstream-ch8-s1/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs:173) · [Модель havoc](/root/kani-upstream-ch8-s1/library/kani_core/src/lib.rs:711)

Два native post проверяют полный числовой порядок и сохранение q и `count(byte < q)` на первых девяти байтах. Упорядоченный префикс содержит все байты ниже q в начальном отрезке, поэтому его длина задаёт исходную пороговую маску. Один `old` хранит `Option<Snapshot>` с q и count, `Snapshot` имеет `Clone + Copy`. Чтение префикса проверяет тип, компаратор и длину до доступа к данным. Каждый Check покрывает mixed threshold, ties, q=0, q=255, отсутствие q, исходную числовую инверсию и полезный возврат. Covers относятся к исходным девяти байтам. [Frame и covers](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:775)

| Участок | Требуемый провайдер | Source binding и native obligations |
| --- | --- | --- |
| 25 swap в каждом Check sort9 | 11, `MA-SWAP-BYTE-Q` | Базы V34 1 и 10. Все фактические пары, включая повторы, удовлетворяют `a < b < 9`. Сверить native caller Pre каждого вызова, q AND/OR, min/max полных байтов и assigns пары внутри девяти. |
| Два вызова sort9 в N18 | MD-SORT9-L1 и MD-SORT9-R9 | Actual loop вызывает тот же helper сначала на `v[1..10]`, затем на `v[10..19]`. Сверить обе инстанциации native Pre и те же два post и assigns в Replace. Оба прохода insertion loop имеют пустой хвост. |
| Два вызова sort9 в N19 и контроле | MD-SORT9-L1 и MD-SORT9-R10 | Actual loop вызывает helper на `v[1..10]` и `v[10..20]`. Сверить native Pre, обе сводки и сохранение исходного `v[19]` до вставки. |
| Правая вставка N19 и контроля | 11, `MA-INSERT-RIGHT` | Actual вызов `insert_tail(v+10,v+19)`, relative 9. Числовой post sort9 влечёт q-монотонный префикс. Сверить native pointer Pre, q-pre, q-post и условный numeric post для десяти байтов. |
| Whole merge в N18 или N19 | 12b, `MB-MERGE-N18` или `MB-MERGE-N19` | Source `v[1..19]` или `v[1..20]`, split 9+9 или 9+10. Сверить native numeric Pre обеих половин и readable source / writable disjoint scratch32. B Replace пишет первые N слотов scratch. Actual copy-back читает ровно эти слоты и пишет активный срез. |

Сводки 11 и 12b фиксируют source-reported SUCCESS. Перенос требует сверки pins, профиля, активных clauses и native inventory. При cutoff одного из Check результаты зависимых consumers остаются условными наблюдениями. [Сводка 11](run-44872078840/SUMMARY.md) · [Сводка 12b](run-44876372471/SUMMARY.md) · [Actual network](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332)

Оба positive consumer берут B capture на полном исходном срезе до actual вызова. После copy-back проверяют q/order-stat относительно этого snapshot, q-frame, equality всех V34 байтов вне активного среза и шесть covers C13. На маршрутах N18/N19 происходит соответственно 3/4 динамических Replace. [N18](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:888) · [N19](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:940)

В контроле при q=1 активные 19 байтов исходно нулевые, остальные байты V34 произвольны. Набор Replace совпадает с positive N19. После actual возврата cover проверяет `v[1]==0`, затем запись `v[1]=255` и второй cover фиксируют порчу. Целевой mask равен 0, порча поднимает бит 0. Квалификация требует двух достигнутых covers, q/outside frame и единственной FAILURE с native ID/class/location, привязанными к `MD_N19_CORRUPT_QPOST`. [Контроль](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:992) · [Целевое утверждение](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1018)

## Локальная проверка и открытые результаты

- `rustfmt 1.11.0-nightly (7189d39d9c 2026-10-22) --edition 2024 --check` прошёл на участке `sort9_optimal` и целиком на двух изменённых verification-модулях. `git diff --check` прошёл для std/control. Статически сверены побайтная сохранность, шесть selectors/guards/roles, 38 уникальных source-меток, геометрия V34 и scratch32, 25 пар сети на трёх точных срезах, все 512 бинарных входов и их пороговые маски, actual правый insert и witness порчи.
- `validate` с синтетическими GitHub metadata подтвердил control commit/tree/parent, event/ref/attempt и payload SHA-256. `check-source` подтвердил чистые std/tool checkout, commits/trees и все восемь std SHA-256. `python3 -m unittest -v test_run.py` прошёл 14/14 на синтетических Python-процессах. Проверены шесть последовательных запусков, exact argv, child budget 3 600 с, cap 10 GiB и нижний effective cap, latest start, capture caps, cleanup, drift и error paths.
- Cargo, rustc, Kani, CBMC, CI и push в этой стадии не выполнялись. Компиляция и все native outcomes открыты. При qualification сверить IDs/classes/locations, complete safety inventory, обе post и assigns каждого Check, caller Pre и применённые clauses каждой Replace, covers и обоснования U. Native uninit/validity остаются за отдельным ON-профилем. [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)
- Основной риск — DFCC и память Check sort9 с 25 swap. Сохранить для каждого Check и consumer последнюю фазу, первую CNF, VT и child time, nominal/effective cap и PGID/component RSS. При ограничении thin lowering зафиксировать точную причину. Эквивалентный fat span потребует отдельной сверки footprint и активных clauses. Переносимость в CI определяется самым тяжёлым корнем всей цепочки, включая провайдеров, на matched профиле. [Порядок разбора](PILOT14-IMPL-TASK.md) · [Cutoff кампании 13](run-44878875303/SUMMARY.md)
