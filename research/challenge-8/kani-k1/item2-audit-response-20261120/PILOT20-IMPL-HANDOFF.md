# Кампания 20. Handoff actual вставок на OB11

Локальный пакет содержит десять последовательных exact roots для `merge_wide`, OB11 и local cap 6 GiB. Frozen request имеет `status=READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. Для dispatch требуются review и отдельный GO. Кампания 19 продолжает свой замороженный roster. [Задание 20](PILOT20-IMPL-TASK.md)

## Пины и хэши

| Объект | Commit | Tree |
| --- | --- | --- |
| Std 20 | `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` | `3cc0e5aa1a8d5100c2812bef424291af9f83f630` |
| Parent std 20, он же std 18 | `a9e7dba799a22b49f4bad3be1579c08d9e0763a3` | `78079cf6e72d4cc56f77876c4ba61e98fe689dbf` |
| Control 20 | `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` | `aba7ec3689b53644c105a138283f2efd7db4fcb6` |
| Единственный parent Control 20 | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` | `53b372008b70704b15a404275f81fa078ed50034` |
| База содержимого Control 19 | `400b54a57cc1b1de2ebeca3060e95cf5954ec69c` | `e548edece4474ec5412c29e359b3959fa2716095` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Std 16 | `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1` | `e2a757c2ca5659a83e70f3775ebce3e672dd0463` |
| Std 17A | `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` | `a41b4c4822ab9df70db698ce576b3112a670ba80` |
| g0 задания | `4c9b5fd96acb3de4887bc603bacf0cb931b16a0b` | `8e9641faf0e419234a498e778c7c2ea174cff308` |
| g0 native inventory | `2547412124d253c44c97ec3e28391866f49d4cb9` | `21633f444c48aca7a16eb4cecbfb9f761e417daa` |

Std находится в `/root/verify-rust-std-ch8-q-pilot-v1`, ветка `experiment/ch8-q-pilot-v1`. В коммите только добавления в `verify/sorting_q_merge.rs`. Control находится в `/root/kani-ch8-q-pilot-control-v20`, ветка `experiment/ch8-q-pilot-control-v20`. Дельта от содержимого 19 затрагивает roster в `run.py`, pins, hashes и roster в request, а также тесты. Workflow и event ref `refs/heads/uninit-ci/ch8-q-pilot-v1` взяты побайтно из 19. Унаследованное имя шага содержит «seven», фактический состав задают десять строк request. [Frozen request](/root/kani-ch8-q-pilot-control-v20/ch8-q-pilot-control/CI-REQUEST.json)

| Файл Control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `6673e043738a687a0a47dabeb43f72f98a9dea8f6938be288c5e666658133033` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `2045763a42a5d09d3adb2d009eb3fd4c05baac7aa226a2bdd5494737f757abcd` |
| `ch8-q-pilot-control/test_run.py` | `9787a946bae78e76cb009d113c44f7cde478cda445b5c2ae8f6fe509b448f6ea` |

| Файл std из `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `b28019641694703cc0dee6a7f934dc125fdf418d0bbee6824de1dc0e1664eea9` |
| `smallsort/verify/sorting_q_merge_model.rs` | `d7a7fea7ac679b5adf611aee8cb714d6bec59e13b4493d610e0eacea958ffd9f` |

## Frozen roster

Префикс selector — `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Ordinary stubs и extra CBMC args пусты. Check исполняют actual функцию с пустым набором verified stubs. В колонке Replace указаны `sort9_optimal`, `sort13_optimal` и `bidirectional_merge` как sort9, sort13 и merge. У восьми positives ожидается `SUCCESS`. У двух контролей ожидается по одной назначенной `FAILURE` класса `assertion`.

| № | Root ID | Exact selector suffix | Check или Replace | Child, с | Covers |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | COMPACT-N20-ACT-INSERT-OB11 | `compact_network_n20_actual_insert` | Replace sort9, merge | 600 | 6 |
| 2 | COMPACT-N20-ACT-INSERT-CORRUPT-OB11 | `compact_network_n20_actual_insert_corrupt` | Replace sort9, merge | 300 | 2 |
| 3 | COMPACT-N25-ACT-INSERT-OB11 | `compact_network_n25_actual_insert` | Replace sort9, sort13, merge | 600 | 6 |
| 4 | COMPACT-N25-ACT-INSERT-CORRUPT-OB11 | `compact_network_n25_actual_insert_corrupt` | Replace sort9, sort13, merge | 300 | 2 |
| 5 | MW-S9-R-B13-L12-OB11 | `mw_sort9_right_b13_len12` | Check sort9 | 600 | 7 |
| 6 | MW-MERGE-N24-OB11 | `mw_merge_n24` | Check merge | 600 | 6 |
| 7 | COMPACT-N24-ACT-INSERT-OB11 | `compact_network_n24_actual_insert` | Replace sort9, merge | 600 | 6 |
| 8 | MW-S13-R-B14-L14-OB11 | `mw_sort13_right_b14_len14` | Check sort13 | 1 200 | 7 |
| 9 | MW-MERGE-N27-OB11 | `mw_merge_n27` | Check merge | 600 | 6 |
| 10 | COMPACT-N27-ACT-INSERT-OB11 | `compact_network_n27_actual_insert` | Replace sort13, merge | 600 | 6 |

## Exact геометрии и роли

Все positives используют произвольный initialized V34 и независимый q для точного `u8/KeyLess<u8>`. Compact consumers получают q-target из исходного активного среза, проверяют q-post, q-frame и каждый внешний байт через `v[0]` и компактный снимок хвоста. Сеть выполняет выбор и обработку обеих половин, реальные циклы вставок и copy-back из отдельного scratch32. Native Replace Pre merge проверяются на состоянии после обеих половин. Они включают numeric order половин, model geometry и отдельные length/readable/writable/disjoint. Рёбра к Check insert в этих четырёх маршрутах отсутствуют. [Сеть и copy-back](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332) · [Compact positives](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:2002) · [Native роли, в том числе Pre merge](NATIVE-INVENTORY-N13-N20.md)

| N | Presort, точные срезы | Actual insert, base/rel | Whole merge source и записи в scratch32+0 |
| ---: | --- | --- | --- |
| 20 | sort9 `v[1..11]` и `v[11..21]` | 1/9 и 11/9 | `v[1..21]`, `[0..10) + [10..20)` |
| 25 | sort9 `v[1..13]`, sort13 `v[13..26]` | 1/9–11, справа пусто | `v[1..26]`, `[0..12) + {12} + [13..25)` |
| 24 | sort9 `v[1..13]` и `v[13..25]` | 1/9–11 и 13/9–11 | `v[1..25]`, `[0..12) + [12..24)` |
| 27 | sort13 `v[1..14]` и `v[14..28]` | слева пусто, 14/13 | `v[1..28]`, `[0..13) + {13} + [14..27)` |

- **Check presort.** Правый N24 выполняет 25 actual swaps и проверяет frame вне `v[13..22]`. Правый N27 выполняет 45 actual swaps и проверяет frame вне `v[14..27]`, включая `v[27]`. Prefix modifies и numeric/q-post действуют в Check. Обе fixtures проверяют q-frame и семь covers из `define_presort_frame_and_covers!`. [Check N24](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1301) · [Check N27](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1336)
- **Check merge.** N24 и N27 исполняют actual up/down, курсоры и финальный guard. N27 выполняет odd copy в slot 13. `modifies` ограничивает записи активным префиксом отдельного `MaybeUninit<[u8; 32]>`. Контрактный q-post проходит по всем байтам этого префикса после normal return. Fixture проверяет весь source V34, q-frame и шесть covers. Отдельные uninit/validity проверки входят в отключённую часть профиля OFF. Обычные bounds, memory, overflow и unwind проверки сохранены. [Check N24](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1557) · [Check N27](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1586) · [Actual merge](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:1249)
- **Форма контрактов.** Новые roots используют прежние active clauses. В `merge_wide` у соответствующих `sort9_optimal`, `sort13_optimal`, `insert_tail` и `bidirectional_merge` по одному активному `ensures` с `old` на захвате. Результаты захвата реализуют `Clone`, включая элементы tuple для wide insert. Consumer исполняет insert в Original, с обычными проверками тела. [Wide insert clauses](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:770) · [Модели wide](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:465)

В обоих контролях q=1, активный вход нулевой, внешние байты произвольны. Cover полезного возврата проверяет `v[1] == 0`. Затем запись `v[1] = 255` меняет младший бит нулевой маски. Cover отмечает порчу, после него проверяются q-frame, внешний frame и назначенный q-post. Native Location для обоих ожидается в раскрытии общего макроса. [Контроль и обе invocations](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:2079)

| N | Единственная ожидаемая failure | Оба ожидаемых covers |
| ---: | --- | --- |
| 20 | `COMPACT_N20_ACT_INSERT_CORRUPT_QPOST` | `COMPACT_N20_ACT_INSERT_CORRUPT_USEFUL_RETURN`, `COMPACT_N20_ACT_INSERT_CORRUPT_PATH` |
| 25 | `COMPACT_N25_ACT_INSERT_CORRUPT_QPOST` | `COMPACT_N25_ACT_INSERT_CORRUPT_USEFUL_RETURN`, `COMPACT_N25_ACT_INSERT_CORRUPT_PATH` |

## Провайдеры для qualification

| Consumer | Требуемые Check на OB11 | Исторический sampled RSS, GiB |
| --- | --- | --- |
| N20 и контроль | 16 `MW-S9-L10`, `MW-S9-R10`, `MW-MERGE-N20` | 4,38 / 4,37 / 3,44 |
| N25 и контроль | 16 `MW-S9-L12`, `MW-S13-R13`, `MW-MERGE-N25` | 4,33 / **7,32** / 4,31 |
| N24 | 16 `MW-S9-L12`, 20 `MW-S9-R-B13-L12-OB11`, `MW-MERGE-N24-OB11` | 4,33 / открыто / открыто |
| N27 | 17A `NM-S13-L13`, 20 `MW-S13-R-B14-L14-OB11`, `MW-MERGE-N27-OB11` | **7,35** / открыто / открыто |

Шесть импортируемых результатов 16 имеют source-reported `SUCCESS` и все covers при `merge_wide`, OB11 и том же tool. Сверены exact type/domain, вход и footprint каждого Check, активные contracts/models и тела sort9, sort13, whole merge и actual helpers. Поздние ветви моделей под `no_merge_sort13` и `compact_presort13` не активируются в этом профиле. У 17A `NM-S13-L13` на `v[1..14]` был `SUCCESS` с 7/7 covers, 826 с child, 784,2 с VT и 7,35 GiB. Активные предикаты presort при len13 совпадают. Расширение допустимой длины до 17 под `no_merge_sort13` сохраняет этот случай. Q-only insert clause относится к другому callee. В левом N27 после sort13 цикл вставок пуст. Правый N27 выполняет одну actual вставку. [Провайдеры 16](run-44890498157/SUMMARY.md) · [Провайдеры 17A](run-44896810040/SUMMARY.md) · [Native роли Check и Replace](NATIVE-INVENTORY-N13-N20.md#привязки-к-source-и-lowering)

Для qualification сверить точные invocation, pins и source/tree/hashes, native property ID, класс, Location, ordinal, S/F/U и coverage. Особенно нужны Pre merge после actual вставок, все назначения из таблицы и привязка повторных presort/insert/DFCC/copy instances к их paths. Исторический inventory даёт ориентиры для N20 и `NM-S13-L13`. Успешный consumer при открытом provider остаётся диагностическим результатом. Для N24/N27 требуется собственная контрольная привязка. Максимальный RSS считать по всей цепочке. Исторические провайдеры sort13 для N25 и N27 превышают 6 GiB. [Критерии qualification](PILOT18-QUALIFICATION-TASK.md) · [Матрица wide](MERGE-WIDE-PLAN.md)

N20 actual positive OB12 из 18 и строка 1 используют один и тот же harness и набор verified stubs. Исторические 2,49 GiB, 68 с child, 33,6 с VT и 0,61 млн clauses относятся к OB12. При capacity cutoff на OB11 следующий matched вариант — actual пара N20 и три exact Check на OB12 с отдельной оценкой fit. Для N25 прежние capacity на OB12 и RSS на OB13 относятся к Replace insert. При capacity cutoff actual пары N25 отдельное измерение на OB12 требует своего matched плана. Capacity, RSS, timeout и property outcome фиксируются отдельно. [A/B и отсечения 18](run-44907708573/SUMMARY.md)

### Узкая полоса sort13 на решение владельца

Отдельный serial пакет на cap 8 GiB только для `NM-S13-L13`, `NM-S13-L14`, `NM-S13-L15`, `NM-S13-L16`, `NM-S13-L17` в таком порядке. Пин std 17A из таблицы, текущий tool, `no_merge_sort13`, OB11, OFF, actual swaps, jobs=1 и 1 200 с на child. Суммарно 6 000 с child. С теми же job 180 мин, setup 1 800 с и финализацией 540 с запас составит 2 460 с. Исторический пик 7,35 GiB оставляет около 0,65 GiB до cap 8 GiB. Требуются калибровка, результаты 19, native привязка и решение владельца. Этот вариант описан для отдельного допуска. R13 N25 и новый R14 N27 оцениваются по своим измерениям. [Результаты 17A](run-44896810040/SUMMARY.md) · [Анализ DFCC](PILOT-RUN5-ANALYSIS.md)

## Лимиты и локальная валидация

- Один setup/build, CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, regular, unwind36, OFF, JSON export и отдельные Kani/Cargo target dirs. 6 000 с child, setup/build до 1 800 с, финализация 540 с, job 10 800 с, запас 2 460 с. Latest starts за 330, 630 и 1 230 с до supervisor cutoff для 300, 600 и 1 200 с child соответственно.
- Local cap 6 291 456 KiB, outer 12 582 912 KiB, reserve 2 097 152 KiB. Capture 16/1/8 MiB на stdout/stderr/export, 384 MiB aggregate. При запуске сохранить effective cap, PGID, outer и component peaks, capacity/CNF/solve, VT/child, native inventory или первопричину cutoff.
- `git diff --check` прошёл для std и Control. Для Control сверены дельты к 19 и единственному parent. Статическая сверка task/source/request подтвердила 10/10 строк, exact slices, Check/Replace, verified stubs и labels контролей.
- Check-only `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18)` с `--edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на добавленных блоках. Полная проверка файла вернула те же 30 замечаний, что и база, с побайтно одинаковыми правками после нормализации путей и номеров строк отчёта.
- `validate` прошёл на чистом Control с синтетическими GitHub metadata. `check-source` прошёл на чистых std и tool и подтвердил commits, trees и восемь std SHA-256.
- `python3 -m unittest -v test_run.py` прошёл 14/14. Синтетические процессы проверили frozen roster, два ожидаемых nonzero exit, exact argv, local/effective cap, все три окна latest start, запуск следующего root после штатного reap при RSS cutoff и timeout, сохранение причин и error paths. Покрыты drift, failed preparation, read error, unconfirmed cleanup, отсутствующий и частичный export, неправильный тип и явный `NOT_RUN`.

Формальная компиляция, native outcomes кампании 20, resource fit и proof credit остаются открытыми. Push, CI и операции с триггером в этой стадии не выполнялись.
