# Pilot 21. Локальный handoff actual вставок на OB11

Три frozen пакета используют один std pin и содержат 40 exact строк. Во всех request `status=READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакеты остаются `RESEARCH_ONLY`. Для dispatch нужны review и отдельный GO. Для 21C также нужно решение владельца о полосе 8 GiB для семи перечисленных правых Check. [Задание](PILOT21-IMPL-TASK.md) · [Действующий допуск](OWNER-DECISION-SORT13-8GIB.md)

## Пины и деревья

| Объект | Commit | Tree |
| --- | --- | --- |
| g0 задания | `f6678f7acd85851f2a27baeb86a4435ce472b5a8` | `f1cb3a728951a7d2832f07ac2488cd598d1edff5` |
| Std 21 | `e2bd3c6adc870729794a6b2fe44eece988402d8f` | `7e62553ab80d6178ce8f01c8212e084b2186e308` |
| Единственный parent Std 21 | `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` | `3cc0e5aa1a8d5100c2812bef424291af9f83f630` |
| Control 21A | `2fa3734008c1e5e3e46cd7f72f8bbc891ae99080` | `3174f86fd3aa6b30a4a70158156f955f8f54267f` |
| Control 21B | `d62b75ddd9cbc4e4fa5366f1ae225833d71f52f3` | `324123d4ea2c0c961b3bab36987de147913ade90` |
| Control 21C | `5eef2b48617a8f2583fb5e587af0e071b9288366` | `83bf55935e34a1a86b7ce02f52be0be79e1e315e` |
| Единственный parent всех трёх Control | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` | `53b372008b70704b15a404275f81fa078ed50034` |
| База содержимого Control 20 | `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` | `aba7ec3689b53644c105a138283f2efd7db4fcb6` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Std 16 | `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1` | `e2a757c2ca5659a83e70f3775ebce3e672dd0463` |
| Std 17A | `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` | `a41b4c4822ab9df70db698ce576b3112a670ba80` |

Std находится в `/root/verify-rust-std-ch8-q-pilot-v1`, ветка `experiment/ch8-q-pilot-v1`. Коммит добавляет 252 строки только в `verify/sorting_q_merge.rs` под `library/core/src/slice/sort/shared/smallsort/`. Это 38 новых roots, ещё две строки roster используют прежние `mw_merge_n32` и `mw_sort13_right_b14_len14`. В задании опечатка в tree базы std (`…91af5f630`). Таблица, request и локальная сверка используют tree точного коммита `bfa60b19cc`, также записанный в handoff 20. [Handoff 20](PILOT20-IMPL-HANDOFF.md)

- 21A, `/root/kani-ch8-q-pilot-control-v21a`, ветка `experiment/ch8-q-pilot-control-v21a`. [Frozen request](/root/kani-ch8-q-pilot-control-v21a/ch8-q-pilot-control/CI-REQUEST.json)
- 21B, `/root/kani-ch8-q-pilot-control-v21b`, ветка `experiment/ch8-q-pilot-control-v21b`. [Frozen request](/root/kani-ch8-q-pilot-control-v21b/ch8-q-pilot-control/CI-REQUEST.json)
- 21C, `/root/kani-ch8-q-pilot-control-v21c`, ветка `experiment/ch8-q-pilot-control-v21c`. [Frozen request](/root/kani-ch8-q-pilot-control-v21c/ch8-q-pilot-control/CI-REQUEST.json)

Дельта каждого Control к 20 содержит `CI-REQUEST.json`, `run.py` и `test_run.py`. Workflow побайтно совпадает с 20, event ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. Шаг с названием «Run seven q-pilot roots» унаследован из 20. Фактическое число и порядок строк задают frozen request и runner. Строгая проверка списка файлов Control относительно parent проходит для всех кандидатов.

| Control | SHA-256 request | SHA-256 run.py | SHA-256 test_run.py |
| --- | --- | --- | --- |
| 21A | `102561420c20400b4323a33a0af31e2af9f440f694cfbc266c051b314a88dd50` | `dcc8123fb2e1f3cbc90799fdef222e3aab39bfb66fceb55f1f9d05a77c291d14` | `f8ccac2bd7cfee4b4c8c03953aa651e10e16291f8fcb7d138b212580d32190b6` |
| 21B | `352e05dba3cadd417be31834348a44958c7f169e8cd401380cf36f4b876670d7` | `50373622d1ddc22e63dcfdf9489880279b52d01e8bf6d52188ff388a91b578b1` | `d6b30ce0ef288efdf407e9b004ac32eee860589e73b141552f665240bbbdad07` |
| 21C | `5532a3b0eee54b8348f6cc9fc049b413f5668c65787350168158bf1692aec410` | `71c12729bf3f47f4eef5aedb4f6ceafa2b7bf3647854a9ec7f967bb02fbf931d` | `dca046058112671b1b8205e465d9a80fde2dc58550069329fd035a771e29c96f` |

SHA-256 общего workflow `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f`.
| Файл std относительно `library/core/src/slice/sort/shared/` | SHA-256 |
| --- | --- |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `smallsort/verify.rs` | `b4ecd70c29b636f918c0916718ed6a79349932fe1e9713911d0a0c8e3e62e210` |
| `smallsort/verify/sorting_model.rs` | `dec45747dde28e0861becf4c0c089d2a9899ad035db30e9967d0a0041845fb88` |
| `smallsort/verify/sorting_q_controls.rs` | `0ee56705b083f7610b764bc8bc164a81eae94de9229b33baf0169f6c7b8df9ff` |
| `smallsort/verify/sorting_q_model.rs` | `5e5eac5ad26d1352df52b659a12eb5396ef23872f724c1b460441eb6a37520f0` |
| `smallsort/verify/sorting_q_pilot.rs` | `ac755d455d7a0f5fbd706c90bb6bae02ffd4a4c41125db7e5fb28833da55a8b6` |
| `smallsort/verify/sorting_q_merge.rs` | `66cd68162631ae26eb7068e03d505d3648bdaf7c529a323d6cbce785e367e284` |
| `smallsort/verify/sorting_q_merge_model.rs` | `d7a7fea7ac679b5adf611aee8cb714d6bec59e13b4493d610e0eacea958ffd9f` |

## Frozen roster и ожидаемые результаты

Exact selector prefix `slice::sort::shared::smallsort::verify::sorting_q_merge::`. Все строки используют `merge_wide`, `u8/KeyLess<u8>`, OB11, normal OFF, unwind36 и пустые ordinary stubs. Check исполняют реальное тело с пустыми verified stubs. Replace у consumer/control суммаризирует указанный presort и `bidirectional_merge`. Для Check и Proof ожидается `SUCCESS`. Каждый Control ожидает одну `FAILURE` класса `assertion` с меткой `COMPACT_N{N}_ACT_INSERT_CORRUPT_QPOST` и covers `COMPACT_N{N}_ACT_INSERT_CORRUPT_USEFUL_RETURN` и `COMPACT_N{N}_ACT_INSERT_CORRUPT_PATH`.

### 21A

| № | Root ID | Exact selector suffix | Native роль | Child, с | Covers |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | `MW-S9-L-B01-L11-OB11` | `mw_sort9_left_b01_len11` | Check sort9 | 600 | 7 |
| 2 | `MW-S9-R-B11-L11-OB11` | `mw_sort9_right_b11_len11` | Check sort9 | 600 | 7 |
| 3 | `MW-S9-R-B12-L11-OB11` | `mw_sort9_right_b12_len11` | Check sort9 | 600 | 7 |
| 4 | `MW-S9-R-B12-L12-OB11` | `mw_sort9_right_b12_len12` | Check sort9 | 600 | 7 |
| 5 | `MW-MERGE-N21-OB11` | `mw_merge_n21` | Check merge | 600 | 6 |
| 6 | `MW-MERGE-N22-OB11` | `mw_merge_n22` | Check merge | 600 | 6 |
| 7 | `MW-MERGE-N23-OB11` | `mw_merge_n23` | Check merge | 600 | 6 |
| 8 | `COMPACT-N21-ACT-INSERT-OB11` | `compact_network_n21_actual_insert` | Proof, Replace sort9, merge | 450 | 6 |
| 9 | `COMPACT-N21-ACT-INSERT-CORRUPT-OB11` | `compact_network_n21_actual_insert_corrupt` | Control, Replace sort9, merge | 300 | 2 |
| 10 | `COMPACT-N22-ACT-INSERT-OB11` | `compact_network_n22_actual_insert` | Proof, Replace sort9, merge | 450 | 6 |
| 11 | `COMPACT-N22-ACT-INSERT-CORRUPT-OB11` | `compact_network_n22_actual_insert_corrupt` | Control, Replace sort9, merge | 300 | 2 |
| 12 | `COMPACT-N23-ACT-INSERT-OB11` | `compact_network_n23_actual_insert` | Proof, Replace sort9, merge | 450 | 6 |
| 13 | `COMPACT-N23-ACT-INSERT-CORRUPT-OB11` | `compact_network_n23_actual_insert_corrupt` | Control, Replace sort9, merge | 300 | 2 |
| 14 | `COMPACT-N24-ACT-INSERT-CORRUPT-OB11` | `compact_network_n24_actual_insert_corrupt` | Control, Replace sort9, merge | 300 | 2 |
| 15 | `COMPACT-N27-ACT-INSERT-CORRUPT-OB11` | `compact_network_n27_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |

### 21B

| № | Root ID | Exact selector suffix | Native роль | Child, с | Covers |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | `MW-MERGE-N26-OB11` | `mw_merge_n26` | Check merge | 600 | 6 |
| 2 | `COMPACT-N26-ACT-INSERT-OB11` | `compact_network_n26_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 3 | `COMPACT-N26-ACT-INSERT-CORRUPT-OB11` | `compact_network_n26_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |
| 4 | `MW-MERGE-N28-OB11` | `mw_merge_n28` | Check merge | 600 | 6 |
| 5 | `COMPACT-N28-ACT-INSERT-OB11` | `compact_network_n28_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 6 | `COMPACT-N28-ACT-INSERT-CORRUPT-OB11` | `compact_network_n28_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |
| 7 | `MW-MERGE-N29-OB11` | `mw_merge_n29` | Check merge | 600 | 6 |
| 8 | `COMPACT-N29-ACT-INSERT-OB11` | `compact_network_n29_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 9 | `COMPACT-N29-ACT-INSERT-CORRUPT-OB11` | `compact_network_n29_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |
| 10 | `MW-MERGE-N30-OB11` | `mw_merge_n30` | Check merge | 600 | 6 |
| 11 | `COMPACT-N30-ACT-INSERT-OB11` | `compact_network_n30_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 12 | `COMPACT-N30-ACT-INSERT-CORRUPT-OB11` | `compact_network_n30_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |
| 13 | `MW-MERGE-N31-OB11` | `mw_merge_n31` | Check merge | 600 | 6 |
| 14 | `COMPACT-N31-ACT-INSERT-OB11` | `compact_network_n31_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 15 | `COMPACT-N31-ACT-INSERT-CORRUPT-OB11` | `compact_network_n31_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |
| 16 | `MW-MERGE-N32-OB11` | `mw_merge_n32` | Check merge | 600 | 8 |
| 17 | `COMPACT-N32-ACT-INSERT-OB11` | `compact_network_n32_actual_insert` | Proof, Replace sort13, merge | 450 | 6 |
| 18 | `COMPACT-N32-ACT-INSERT-CORRUPT-OB11` | `compact_network_n32_actual_insert_corrupt` | Control, Replace sort13, merge | 300 | 2 |

### 21C

| № | Root ID | Exact selector suffix | Native роль | Child, с | Covers |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | `MW-S13-R-B14-L13-OB11` | `mw_sort13_right_b14_len13` | Check sort13 | 1100 | 7 |
| 2 | `MW-S13-R-B14-L14-OB11` | `mw_sort13_right_b14_len14` | Check sort13 | 1100 | 7 |
| 3 | `MW-S13-R-B15-L14-OB11` | `mw_sort13_right_b15_len14` | Check sort13 | 1100 | 7 |
| 4 | `MW-S13-R-B15-L15-OB11` | `mw_sort13_right_b15_len15` | Check sort13 | 1100 | 7 |
| 5 | `MW-S13-R-B16-L15-OB11` | `mw_sort13_right_b16_len15` | Check sort13 | 1100 | 7 |
| 6 | `MW-S13-R-B16-L16-OB11` | `mw_sort13_right_b16_len16` | Check sort13 | 1100 | 7 |
| 7 | `MW-S13-R-B17-L16-OB11` | `mw_sort13_right_b17_len16` | Check sort13 | 1100 | 7 |

## Геометрии и контракты

- У positives initialized V34, произвольные байты и независимый произвольный q. Presort Check использует exact аргумент из таблицы ниже, actual 25/45 swaps, thin writes первых 9/13 байтов. Active post требует numeric order, тот же q и то же число байтов ниже q в префиксе. Общий helper проверяет q-frame и V34 вне префикса записи, включая хвост аргумента. Семь covers проверяют mixed threshold, tie, q=0, q=max, q absent, инверсию и полезный возврат. [Геометрии Check](PILOT21-IMPL-TASK.md)
- Каждый whole merge Check берёт `v[1..1+N]`. Split после `floor(N/2)`, назначение `MaybeUninit<[u8; 32]>` в отдельной allocation с base+0. При `k = floor(N/2)` actual up/down пишут `dst[0..k]` и `dst[N-k..N]`. При нечётном N actual odd copy пишет `dst[k]`. Guard проверяет курсоры. `modifies` охватывает `dst[0..N]`, whole-merge `old` захватывает только snapshot источника и q. q-post читает весь записанный префикс. Fixture проверяет q и весь source V34, пять covers входа и полезный возврат. Прежний N32 также покрывает ниже q все 32 и ни одного, то есть целевые маски 0 и `u32::MAX`.
- Consumer вызывает real `small_sort_network`. После presort Replace выполняется actual `insertion_sort_shift_left` с обычными memory/bounds/overflow/unwind проверками. Native merge Pre применяется после обеих вставок и включает length, readable/writable/disjoint, wide geometry и numeric order обеих половин. Следом выполняется actual copy-back из scratch32. Positive проверяет исходный q/order-stat на всём срезе, q-frame и все внешние байты, включая `v[0]`. Шесть covers отмечают mixed threshold, tie, q=0, q=max, q absent и полезный возврат. N32 заполняет scratch целиком. Его wide oracle считает `((1_u64 << len) - (1_u64 << below)) as u32`, включая оба крайних значения для длины 32.
- Каждый контроль использует геометрию и verified stubs своего positive. Активный вход обнулён, внешние байты произвольны, q=1. Полезный возврат `v[1] == 0` покрывается после actual сети. Следом идут `v[1] = 255`, cover порчи, q/frame assertions и назначенный q-post. При q=1 все байты с нулевой threshold-маской равны нулю, а порча меняет её младший бит.
- Сверены сохранённые active clauses. У `sort9_optimal`, `sort13_optimal`, `insert_tail`, `merge_up`, `merge_down` и `bidirectional_merge` по одному active `ensures` в `merge_wide` при захвате через `old` с `&mut` аргументом. `Clone` реализуют `Option<PrefixSnapshot>`, tuple `(Snapshot, Option<bool>)` у insert, `Option<StepSnapshot>` и `Option<MergeSnapshot>`. `swap_if_less` имеет один active `ensures` со snapshot пары байтов без захвата `&mut`. Actual helpers идут в Original.

Под `v[a..b]` указаны полуоткрытые срезы. Диапазоны actual tails относительны к своей половине и включают обе границы.

| N | Presort | Аргумент L | Аргумент R | Tails L / R | Whole merge source | Odd dst slot |
| ---: | --- | --- | --- | --- | --- | ---: |
| 21 | sort9 | `v[1..11]` | `v[11..22]` | 9 / 9–10 | `v[1..22]` | 10 |
| 22 | sort9 | `v[1..12]` | `v[12..23]` | 9–10 / 9–10 | `v[1..23]` | — |
| 23 | sort9 | `v[1..12]` | `v[12..24]` | 9–10 / 9–11 | `v[1..24]` | 11 |
| 24 | sort9 | `v[1..13]` | `v[13..25]` | 9–11 / 9–11 | `v[1..25]` | — |
| 26 | sort13 | `v[1..14]` | `v[14..27]` | ∅ / ∅ | `v[1..27]` | — |
| 27 | sort13 | `v[1..14]` | `v[14..28]` | ∅ / 13 | `v[1..28]` | 13 |
| 28 | sort13 | `v[1..15]` | `v[15..29]` | 13 / 13 | `v[1..29]` | — |
| 29 | sort13 | `v[1..15]` | `v[15..30]` | 13 / 13–14 | `v[1..30]` | 14 |
| 30 | sort13 | `v[1..16]` | `v[16..31]` | 13–14 / 13–14 | `v[1..31]` | — |
| 31 | sort13 | `v[1..16]` | `v[16..32]` | 13–14 / 13–15 | `v[1..32]` | 15 |
| 32 | sort13 | `v[1..17]` | `v[17..33]` | 13–15 / 13–15 | `v[1..33]` | — |

В N26 сеть дважды входит в `insertion_sort_shift_left` с `offset=13` на отдельных половинах длины 13. В обоих случаях `tail == v_end` до проверки цикла, поэтому `insert_tail` вызывается ноль раз. Этот маршрут сверён по коду.

## Зависимости и границы допуска

| Consumer / Control | Left Check | Right Check | Whole merge Check |
| --- | --- | --- | --- |
| N21 | 16 `MW-S9-L10` | 21A `MW-S9-R-B11-L11-OB11` | 21A N21 |
| N22 | 21A `MW-S9-L-B01-L11-OB11` | 21A `MW-S9-R-B12-L11-OB11` | 21A N22 |
| N23 | 21A `MW-S9-L-B01-L11-OB11` | 21A `MW-S9-R-B12-L12-OB11` | 21A N23 |
| N24, Proof в 20 и Control в 21A | 16 `MW-S9-L12` | 20 `MW-S9-R-B13-L12-OB11` | 20 N24 |
| N26 | 17A `NM-S13-L13` | 21C `MW-S13-R-B14-L13-OB11` | 21B N26 |
| N27, Proof в 20 и Control в 21A | 17A `NM-S13-L13` | 21C `MW-S13-R-B14-L14-OB11` | 20 N27 |
| N28 | 17A `NM-S13-L14` | 21C `MW-S13-R-B15-L14-OB11` | 21B N28 |
| N29 | 17A `NM-S13-L14` | 21C `MW-S13-R-B15-L15-OB11` | 21B N29 |
| N30 | 17A `NM-S13-L15` | 21C `MW-S13-R-B16-L15-OB11` | 21B N30 |
| N31 | 17A `NM-S13-L15` | 21C `MW-S13-R-B16-L16-OB11` | 21B N31 |
| N32 | 17A `NM-S13-L16` | 21C `MW-S13-R-B17-L16-OB11` | 16 N32, 21B exact повтор при 6 GiB |

- `MW-S9-L10` из 16 совпадает с left N21 по входу `v[1..11]`, footprint `v[1..10]`, type/q, active contract, роли Check и OB11. Сводка 16 указывает `SUCCESS`, 7/7 covers, 243 с child, 4,38 GiB. Left N24 `MW-S9-L12` из 16, right и whole merge из 20 имеют source-reported `SUCCESS` на OB11. Consumer N24 в 20 имел `SUCCESS`, 6/6, 2,79 GiB. Control 21A даёт отдельную проверку чувствительности N24. [16](run-44890498157/SUMMARY.md) · [20](run-44913550779/SUMMARY.md) · [Задание qualification](PILOT21-QUALIFICATION-TASK.md)
- Left `NM-S13-L13`…`L16` из 17A применимы по сверке source/cfg. В обоих профилях действуют те же guards wide-контракта, тот же actual sort13 с 45 swaps и тонким `modifies` первых 13, те же `old`, numeric и q-post и то же native `presort_geometry` для Check и caller Pre. Exact входы `v[1..14]`…`v[1..17]`, пишется `v[1..14]`. Обе стороны OB11. `no_merge_sort13` был включён в 17A и расширял допустимую длину до 17, поэтому на длинах 13–16 предикат совпадает с `merge_wide`. `compact_presort13` выключен с обеих сторон. Q-only insert clause в 17A относится к другому callee, а wide inserts идут в Original. Сверка поддерживает reuse левых Check без отдельного matched root и сохраняет исторический ресурсный профиль.
- Сводка 17A сообщает `SUCCESS`, 0/615 failed, 7/7 covers и 25,5 млн clauses у всех четырёх левых Check. У L13/L14/L15/L16 соответственно 826/830/821/813 с child и 784,2/786,5/779,7/772,1 с VT, sampled peak у всех 7,35 GiB. Решение владельца распространяется на прежние exact roots 17A в их профиле. [17A](run-44896810040/SUMMARY.md) · [Scope решения](OWNER-DECISION-SORT13-8GIB.md)
- N27 whole merge и consumer переиспользуются из 20 с source-reported `SUCCESS`. Exact right Check R14 в 20 остановился во время solve после 25,5 млн clauses, 833 с child, sampled peak 6,02 GiB. Control N27 в 21A проверяет чувствительность. Whole-chain qualification ждёт right R14 в 21C. N25 R13 из 16 достиг `SUCCESS` с 7,32 GiB и 875 с child. Его применимость в полосе 8 GiB требует отдельной записи владельца по этому root. В roster 21C входят R14–R17 с точными длинами из таблицы. [20](run-44913550779/SUMMARY.md) · [16](run-44890498157/SUMMARY.md)
- N32 whole merge в 16 имел source-reported `SUCCESS`, 8/8 covers, 482 с child, 6,04 GiB при OB11. В 21B тот же source selector проверяет fit при 6 GiB. Cutoff оставит fit открытым и сохранит исторический функциональный результат в его профиле. [16](run-44890498157/SUMMARY.md)
- При открытом matched provider результат consumer условен. До закрытия sort13 результаты 21B и его controls имеют диагностический статус. При последующем допуске для grouped property требуются native `SUCCESS`, успешные unwinding assertions, достижимость нужного пути по `SATISFIED` cover или прямому exact source и соответствующая роль Check/Replace. Исторические сводки передают source-reported результаты. Независимый proof credit для Pilot 21 отсутствует. [Правило допуска](GROUPED-PROPERTY-DECISION.md#правило-допуска)

## Ресурсный профиль

| Пакет | Roots | Local cap | Child, с | Остаток, с | Capture members, MiB | Aggregate, MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 21A | 15 | 6 GiB | 7 050 | 1 410 | 375 | 384 |
| 21B | 18 | 6 GiB | 8 100 | 360 | 450 | 512 |
| 21C | 7 | 8 GiB | 7 700 | 760 | 175 | 384 |

- Общий job 10 800 с, setup/build до 1 800 с, финализация 540 с, allowance child 8 460 с. Latest start считается от supervisor cutoff с запасом timeout + 30 с. Окна для 600/450/300/1 100 с child равны 630/480/330/1 130 с.
- Outer 12 GiB, reserve 2 GiB, local 6 291 456 / 6 291 456 / 8 388 608 KiB. Перекрывающиеся sampled RSS peaks имеют разные scope. Per-root capture stdout/stderr/export 16/1/8 MiB. Общий cap включает members и index.
- Один setup/build, CaDiCaL по default pinned tool, `--exact --jobs=1 --no-assert-contracts`, unwind36, regular + JSON export, отдельные Cargo и Kani target dirs. Extra CBMC args пусты. Bounded runner сохраняет original exit/exception, effective cap, sampled process identity с PGID при наблюдении, outer и component RSS, child timing, ограниченные stdout/stderr/export и первопричину cutoff. При последующем dispatch из них фиксируются capacity/CNF/solve, VT/child и terminal native inventory либо причина отсутствия.

## Локальная валидация

- Статическая сверка task/source/request прошла для 40/40 строк. Проверены порядок, exact литеральные срезы, ширина, activated cfg, Check/Replace, stubs, labels, зависимости и наличие q/frame/cover проверок.
- `git diff --check` прошёл для Std и каждого Control относительно parent и базы содержимого. 21A/21B/21C прошли `validate` с синтетическими GitHub metadata и `check-source` на чистых exact std и tool, включая восемь SHA-256 std.
- `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18)` с `--check --edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на четырёх добавленных блоках. Проверка полного файла возвращает прежние 30 замечаний, совпадающие с base после нормализации путей и строк. Изменения форматирования базы отсутствуют.
- `python3 -m unittest -v test_run.py` прошёл по 14/14 для 21A, 21B и 21C. Синтетические тесты проверяют roster, exact argv, заявленный и effective cap, captures и artifact bounds, отдельные target dirs, окна latest start и cutoff. Error paths покрывают drift, failed preparation, read error, unconfirmed cleanup, timeout и RSS cutoff с последующим root после reap, отсутствующий/частичный/повреждённый export, неожиданный тип и explicit `NOT_RUN`.

Формальная компиляция, native outcomes и resource fit Pilot 21 остаются открытыми. Push, CI и операции с trigger ref в этой стадии отсутствуют.
