# REV2 · составной consumer u64 N22–N25

**`WAITING_FOR_PROVIDER_RESULT` · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Пакет содержит четыре контроля фактической сети с порчей после возврата и четыре локальных корня copy-back/frame. Кандидат на исследовательский допуск связывает для каждого активного `v[1..1+N]` в инициализированном `V=[u64;34]` нативные опоры и внешний вывод о полном числовом порядке, сохранении всех кратностей и скалярном frame внешних слов на нормальном возврате `small_sort_network::<u64, _>(…, &mut u64_less)`. Запуск требует независимого ревью, отдельного GO координатора и свободной ветки. [Задание](REV2-U64-N22-N25-CONSUMER-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Локальные пины пакета

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15) · `work/rev2-u64-n22-n25-consumer-std-w15` | `26ce90b1924a3a85dd2b2d8667d32673c9afcfbe` | `be0379100eb8864eb70f96a065b46c5c975355b7` | `a1335f8e11960150afda1d00d60c72b4362e3cec` |
| [Control](/root/kani-rev2-u64-n22-n25-consumer-control-w15) · `work/rev2-u64-n22-n25-consumer-control-w15` | `45501496bc6e9aff5cfc80ba39f6ded22d4c6856` | `427855f50583254169533be7a0957237183b9ee5` | `9e95965f30f40a4dea9532bd04330b0d68537769` |
| [Review-trigger](/root/kani-rev2-u64-n22-n25-consumer-trigger-w15/control) · detached · `review/rev2-u64-n22-n25-consumer-trigger-w15` | `7afbade1a2f5e17e2472d7e1a509ff73cfad13f2` | `427855f50583254169533be7a0957237183b9ee5` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Задание закреплено на g0 `c254479b9a25ef25f0e30ff346ce56b79636ecea`. Деревья баз Std и Control providers — `a04025df1dddb1668c12219307c943a23ee9382a` и `6b9a8245426143527186a7095e8fbf5623578527`. Bundle объявляет один `HEAD` и содержит 27 overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n22-n25-consumer-trigger-w15/control/ch8-cal1/CI-REQUEST.json) | `f22a8f97cc44fc369c1d6c808d2f32108c721a9c7075fd8f24e8f6f7923e9508` |
| Exact roster, канонический JSON | `9255a3c071abc8e01e97e8350e49c994d40a8e0528ecc27ecab2d002e92ab2d8` |
| Source bindings, канонический JSON | `e0887f281334bd3bc85314d8070886c81d57c2b8101e46ff478207084a3dad5d` |
| [Std bundle](/root/kani-rev2-u64-n22-n25-consumer-trigger-w15/control/ch8-cal1/std-overlay.bundle), 74 288 байтов | `32d68dc7bc11e87f056dfc06115b6d66af1b4e68b5aa47489f0b74154cff9352` |
| [Workflow](/root/kani-rev2-u64-n22-n25-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) | `20020118d37a5437ba9cad33cda180108c67ed8c5d1b162c775a5ab61054c4a2` |

Независимый tree pin `CH8_REV2_U64_N22_N25_CONSUMER_TRIGGER_TREE` получает дерево review-trigger после GO. `pins`, `sources`, `finish` и `upload-gate` требуют `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, чистый detached HEAD с единственным ожидаемым parent, совпадение HEAD, payload `after` и `GITHUB_SHA`. Admission receipt сверяется при sources, prepare, measure, finish и upload-gate. Схема индекса `smallsort-rev2-u64-n22-n25-consumer-artifact-v1` связывает четыре хэша входов, trigger, request и полный инвентарь.

## Exact roster и точки привязки

Префикс selector `slice::sort::shared::smallsort::verify::rev2_u64_n22_n25_consumer::`. После включения `kani_smallsort_rev2_u64_n22_n25_consumer` discovery требует сохранения всех 131 унаследованных записей в управляемом roster с kind/source/targets и ровно восемь добавлений `standard-harnesses` с `targets=[]`. Полный cfg-off/cfg-on multiset контролирует остальные записи Kani list. Общие параметры — plain Proof, unwind36, `copy_back=true`, без Check, Replace и stubs. Колонка root указывает начало атрибута proof. [Корни](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n22_n25_consumer.rs:13)

| Слот | Суффикс selector | Root | Ожидаемый исход | Latest start |
| --- | --- | --- | --- | --- |
| `U64-N25-WITNESS-CORRUPT` | `u64_n25_witness_corrupt` | 13:1 | FAILED, exit 1 | 55:00 |
| `U64-N24-WITNESS-CORRUPT` | `u64_n24_witness_corrupt` | 19:1 | FAILED, exit 1 | 58:25 |
| `U64-N23-WITNESS-CORRUPT` | `u64_n23_witness_corrupt` | 25:1 | FAILED, exit 1 | 61:50 |
| `U64-N22-WITNESS-CORRUPT` | `u64_n22_witness_corrupt` | 31:1 | FAILED, exit 1 | 65:15 |
| `U64-N25-COPY-BACK-FRAME` | `u64_n25_copy_back_frame` | 37:1 | VERIFIED, exit 0 | 68:40 |
| `U64-N24-COPY-BACK-FRAME` | `u64_n24_copy_back_frame` | 43:1 | VERIFIED, exit 0 | 72:05 |
| `U64-N23-COPY-BACK-FRAME` | `u64_n23_copy_back_frame` | 49:1 | VERIFIED, exit 0 | 75:30 |
| `U64-N22-COPY-BACK-FRAME` | `u64_n22_copy_back_frame` | 55:1 | VERIFIED, exit 0 | 78:55 |

| Нативная привязка | Координаты |
| --- | --- |
| Shared comparator `REV2_U64_N13_COMPARATOR_CALLED` | `rev2_u64_n13.rs:9:5`, `u64_less`. |
| Witness mixed input / actual call / after return | `69:5` / `72:5` / `73:5`, `check_witness_corrupt::<N>`. |
| Witness canonical / sorted-popcount до порчи | `75:5` / `76:5`, тот же instance. |
| Порча, внешний frame / canonical после порчи | `78:5`, `80:5` / `82:5`, тот же instance. |
| Единственный failure `REV2_U64_Nxx_ACTUAL_SORTED_POPCOUNT` | N22 `84:9`, N23 `86:9`, N24 `88:9`, N25 `90:9`, класс `assertion`. Regular и stock сверяются по ID, описанию, классу и источнику. |
| Локальная typed copy | `130:14` в `check_copy_back::<N>`, `ptr::copy_nonoverlapping::<u64>(scratch_base, dest, N)`. |
| Локальные `DEST_EQUALS_SOURCE`, `SOURCE_PREFIX_FRAME`, `V34_FRAME`, `AFTER_COPY_BACK_FRAME` | `139:5`, `140:5`, `143:5`, `144:5` в `check_copy_back::<N>`. |
| Grouped typed copy | Шесть SUCCESS `ptr::copy_nonoverlapping::<u64>` в `ptr/mod.rs:587:14` с regular/stock ID. Все выведенные unwind checks SUCCESS при stock unwinding ON. |

У actual вызова `smallsort.rs:425:9` копируются N слов из отдельного scratch32 в `v[1..1+N]`. Покрытие `AFTER_COPY_BACK` идёт после обычного возврата, actual тело прошло безусловную копию `:425:9`, а grouped ID относится к семейству typed копий `u64`, общему для нескольких вызовов. Source blob с безусловным call и достижение возврата связывают grouped evidence с этим маршрутом. У локального корня один typed call с теми же type/count, 8-байтовым выравниванием и раздельными живыми объектами. Scratch-префикс инициализируется независимыми полными `u64`, остаток scratch находится вне чтений. Посты локального корня вместе с внешним аргументом об инициализации объединяют полный домен префикса и скалярный frame. [Actual копия](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:425)

## Опоры

Исторические B01/S9 и B01/rel9 используются на всех левых половинах. B11/rel9 и B11/rel10 из N20/N21 дополнительно подтверждают форму вставки на второй базе. Допуск каждого нового правого ребра остаётся предметом внешнего переноса.

| Run/attempt, слот | Exact Proof selector без общего префикса `slice::sort::shared::smallsort::verify::` | Посты и covers | SHA-256 receipt / projection |
| --- | --- | --- | --- |
| `45919454859/1`, U64-N13-SWAP | `rev2_u64_n13::u64_n13_swap` | 35:5, 36:5, 42:5 · 5/5 | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| `45938919685/1`, U64-S9-B01-L09-BITS | `rev2_u64_n18_n19::u64_s9_b01_l09_bits` | `check_sort9_bits::<1, 9>`, 389:5, 390:5, 395:5 · 4/4 | `f7d5bf7f80cf4eca3f1f000f4f92a5e760ca4c036cfee1e68a426b66fbc9f4b1` / `417dd157952fb184de5affd6dc2a4f5a2732615955253c10234464bf0c01959f` |
| `45946532451/1`, U64-B01-INSERT-REL9 | `rev2_u64_n20_n21::u64_b01_insert_rel9` | `check_insert::<1, 9>`, 132:5, 141:5 · 6/6 | `2bbaf726683c45083a304ef9c63286b315a71381568d4ed652b1af081bafb668` / `3b3ed2f328bd7e0a13a3eccd1387913e27ff6b3e83febad94394a5d6cc825cee` |
| `45946532451/1`, U64-B11-INSERT-REL9 | `rev2_u64_n20_n21::u64_b11_insert_rel9` | `check_insert::<11, 9>`, 132:5, 141:5 · 6/6 | `b75cabbd682c71556ef02073a68680e5ea57461643bb104188ab75fecb1776a2` / `fb4d448ec979f980c3a9c246b08bb5b11c197983034a500a5ba079e9ecec4a45` |
| `45946532451/1`, U64-B11-INSERT-REL10 | `rev2_u64_n20_n21::u64_b11_insert_rel10` | `check_insert::<11, 10>`, 132:5, 141:5 · 6/6 | `28abbf68a45a302c446e7e6342036220e118656b1068832a7fe7acbc81a0a511` / `87abe31094d26c4a10c5b01cb255597648486e6f5262a80065859ba2d943fd95` |

Индексы SHA-256 по порядку run — `6d7e603aa2fe26dd62c0f41725d664bf726be89836c16c35efbe641f3a0661f9`, `7b1e589aaf491a38f2e5232411ee734793e73f79e08d5e6c956d9669544fc202`, `e9ed86f4712bb3d6307b4b8be309bd8c3fb934d8a0457a2c26155bc6a1199410`. В исторических и текущем Std совпадают actual `smallsort.rs` blob `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` и `ptr/mod.rs` blob `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6`. Исторический N13 blob `6658b28d64647aa6e11c5bee3c71a135f09b2a6c` отличается от используемого `47c129a11d6cd0d0adce0be450b91eca84a25c0c` видимостью `pub(super)` на том же определении `u64_less`. Остальные применяемые blobs — `4ea168fc664f9f4733a80082af9cdd441f06a2ed` (N18/N19), `5af7b8f629e6b218c5c4ccb7672aa5754fb9fecb` (N20/N21), `e5b3d622a4d2b873df49368cb1e49e060d6a85f5` (providers N22–N25). [Исходные привязки providers](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md#roster-и-нативные-якоря)

Все пять исторических projections сверены с regular/stock и receipt по индексам. В каждом случае `VERIFIED/MATCHED`, exit 0, полный набор anchors/covers, sampler/reap, своевременные receipt и аттестация `COMPLETE`. VT 3,612–33,798 с, cold wall 34,827–73,852 с и пик группового RSS 2,133–2,440 GiB.

Ожидается итог `45967622962/1` от координатора. Таблица задаёт привязку к исходникам из закреплённого source roster. Нативный результат каждой новой строки пока `OPEN`.

| Нативная опора | Exact корень и тип | Root / Check target | Зависимые N |
| --- | --- | --- | --- |
| B12 S9 L12 bits | `u64_s9_b12_l12_bits`, Proof | 111:1 | 22, 23 |
| B12 full-width swap | `u64_s9_b12_swap`, Proof | 144:1 | 22, 23 |
| B13 S9 L12 bits | `u64_s9_b13_l12_bits`, Proof | 78:1 | 24 |
| B13 S13 L13 bits | `u64_s13_b13_l13_bits`, Proof | 16:1 | 25 |
| B13 full-width swap | `u64_s13_b13_swap`, Proof | 49:1 | 24, 25 |
| B01 rel10 | `u64_b01_insert_rel10`, Proof | 173:1 | 22, 23, 24, 25 |
| B01 rel11 | `u64_b01_insert_rel11`, Proof | 179:1 | 23, 24, 25 |
| Pair N22 | `u64_n22_pair_step`, Check | 288:1 / `actual_pair_step_n22` 241:1 | 22 |
| Pair N23 | `u64_n23_pair_step`, Check | 391:1 / `actual_pair_step_n23` 344:1 | 23 |
| Pair N24 | `u64_n24_pair_step`, Check | 494:1 / `actual_pair_step_n24` 447:1 | 24 |
| Pair N25 | `u64_n25_pair_step`, Check | 597:1 / `actual_pair_step_n25` 550:1 | 25 |
| Odd center N23 | `u64_n23_odd_center`, Check | 687:1 / `actual_odd_center_n23` 653:1 | 23 |
| Odd center N25 | `u64_n25_odd_center`, Check | 773:1 / `actual_odd_center_n25` 739:1 | 25 |

Общий префикс provider selector `slice::sort::shared::smallsort::verify::rev2_u64_n22_n25_providers::`. Связывание Check требует свойств `single_top_level_call` и `no_recursive_call` на атрибуте цели, scoped `memcpy.assigns.1/.2` на builtin 46/47, typed copy `u64` на `ptr/mod.rs:587:14` и успешных выведенных unwind checks. Парные проверки курсоров стоят на 269:9/279:9, 372:9/382:9, 475:9/485:9 и 578:9/588:9. Actual typed copy пары в `smallsort.rs:885:9` и `918:9`. Центры воспроизводят `smallsort.rs:1034:13` на 680:9 и 766:9 с covers левой, правой стороны и sentinel. При дорогой форме пары первый запасной вариант из R1 разделяет up/down. [R1](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-U64-N22-N25-PROVIDERS-REVIEW.md)

| N | Исторические опоры | Новые опоры | Actual witness | Local copy-back | Внешнее ребро |
| --- | --- | --- | --- | --- | --- |
| 22 | B01 swap, S9 L09, rel9 сверены | B12 S9/swap, B01 rel10, pair N22 ожидают итог | OPEN, слот ожидает запуска | OPEN, слот ожидает запуска | Переносы по длине, B12 rel9/10, ранги и копия ожидают ревью |
| 23 | B01 swap, S9 L09, rel9 сверены | B12 S9/swap, B01 rel10/11, pair и odd N23 ожидают итог | OPEN, слот ожидает запуска | OPEN, слот ожидает запуска | Переносы по длине, B12 rel9/10/11, ранги и копия ожидают ревью |
| 24 | B01 swap, S9 L09, rel9 сверены | B13 S9/B13 swap, B01 rel10/11, pair N24 ожидают итог | OPEN, слот ожидает запуска | OPEN, слот ожидает запуска | Перенос по длине, B13 rel9/10/11, ранги и копия ожидают ревью |
| 25 | B01 swap, S9 L09, rel9 сверены | B13 S13/B13 swap, B01 rel10/11, pair и odd N25 ожидают итог | OPEN, слот ожидает запуска | OPEN, слот ожидает запуска | Перенос по длине, нулевой правый driver, ранги и копия ожидают ревью |

## Половины и правые вставки

Цикл `smallsort.rs:394–417` обходит две области из таблицы. `S=v+1`, `m=N/2`, правая база `S+m`. Переносы B01 S9 L09→L11/L12 и B12 S9 L12→L11 сохраняют guard на `:538`, базу, девять доступных ячеек, адреса всех 25 пар и frame хвоста. Actual S13 на B13 имеет 45 фиксированных пар. Full-width swap с `b<13` покрывает S13 и S9 на B13, у S9 также выполнено `b<9`. Exact расписания извлечены из тел `sort9_optimal` и `sort13_optimal` и сверяются при source gate. [Расписания](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:538)

Зафиксируем порог `t:u64` и проецируем слово в `word > t`. Скалярные min/max проецируются в AND/OR. Каждая позиция полного выхода совпадает по этой проекции с проверенным битовым выходом сети. Для инверсии `x>y` с x перед y порог `t=y` дал бы битовую инверсию. Min/max сохраняют мультимножество пары и все остальные слова. Это даёт числовой порядок, точные кратности и frame каждого presort. Драйвер использует отсортированный префикс как предпосылку следующей вставки. Пост relR сохраняет порядок и кратности по точному отображению позиций, а его frame сохраняет вход rel(R+1) и соседнюю половину.

| N | Левая половина | Правая половина | Merge и последняя копия |
| --- | --- | --- | --- |
| 22 | `v[1..12]`, B01 S9 → L11, rel9,10 | `v[12..23]`, B12 S9 L12→L11, rel9,10 | 11 пар, 176 байтов в `v[1..23]` |
| 23 | `v[1..12]`, B01 S9 → L11, rel9,10 | `v[12..24]`, B12 S9 L12, rel9,10,11 | 11 пар, центр D[11], 184 байта в `v[1..24]` |
| 24 | `v[1..13]`, B01 S9 → L12, rel9,10,11 | `v[13..25]`, B13 S9 L12, rel9,10,11 | 12 пар, 192 байта в `v[1..25]` |
| 25 | `v[1..13]`, B01 S9 → L12, rel9,10,11 | `v[13..26]`, B13 S13 L13, `offset=13`, `tail==end` | 12 пар, центр D[12], 200 байтов в `v[1..26]` |

Для каждого relR и каждой правой базы отображение `1+j ↔ B+j` при `0≤j≤R` действует внутри одной живой V34. Перенос на B12 равен 88 байтам, на B13 — 96 байтам. Все адреса 8-байтово выровнены. Сканирование от `tail−1` использует те же полные строгие сравнения `x < word`, поэтому равные остаются перед вставляемым x. Проверка `sift==begin` срабатывает при том же `j=0`. При сдвиге `B+j → B+j+1` два диапазона по восемь байтов смежны и раздельны. Отдельный tmp `CopyOnDrop` держит x при любом логическом gap и при выходе записывает его ровно в gap. Ранний возврат оставляет регион прежним. Совпадение относительных чтений, сравнений, шагов и записей сохраняет точное отображение префикса и все слова за tail, включая следующий вход. [Actual insert и driver](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:677)

Независимому ревьюеру нужен отдельный вердикт по каждому из шести рёбер.

| Ребро | Занятые индексы B01 ↔ B | Зависимые N | Запасной exact plain Proof для отдельного малого пакета |
| --- | --- | --- | --- |
| B12 rel9 | 1…10 ↔ 12…21 | 22, 23 | `u64_b12_insert_rel9`, B=12, R=9 |
| B12 rel10 | 1…11 ↔ 12…22 | 22, 23 | `u64_b12_insert_rel10`, B=12, R=10 |
| B12 rel11 | 1…12 ↔ 12…23 | 23 | `u64_b12_insert_rel11`, B=12, R=11 |
| B13 rel9 | 1…10 ↔ 13…22 | 24 | `u64_b13_insert_rel9`, B=13, R=9 |
| B13 rel10 | 1…11 ↔ 13…23 | 24 | `u64_b13_insert_rel10`, B=13, R=10 |
| B13 rel11 | 1…12 ↔ 13…24 | 24 | `u64_b13_insert_rel11`, B=13, R=11 |

Запасной корень — plain Proof `check_insert::<B,R>` с инициализированной произвольной V34, отсортированной предпосылкой и скалярными exact mapping/frame/covers. Для правого rel11 основание состоит из B01/rel11 и показанного переноса. Отклонение любого ребра оставляет указанные длины открытыми.

## Merge, заполнение D и frame

Для actual цикла `smallsort.rs:1022–1025` фиксируем порядок позиций `(полное слово, индекс после вставок)`. Up при равенстве берёт слева, down берёт справа. Пусть перед парой k up уже потребил a слева и b=k−a справа, down потребил c слева и d=k−c справа, `0≤a,c≤k<m`. Тогда обе головы и оба конца читаемы, поскольку каждый обход по отдельности использовал максимум k< m на каждую половину. Actual адреса относительно S — `a`, `m+b`, `m−1−c`, `N−1−d`. Совпадение встречных адресов допустимо для чтения. Up выбирает ранг k, down — отдельный ранг N−1−k. Они записываются в D[k] и D[N−1−k], чьи диапазоны разнесены минимум на слово. Frame pair сохраняет источник для обеих операций и остальные D-ячейки.

При чётных N22/N24 после m пар `a+c=m` и `b+d=m`. Получаем `S+a = S+(m−1−c)+1` и `S+m+b = S+(N−1−d)+1`, обе проверки `:1042`. У нечётных N23/N25 остатки `(m−a−c,m+1−b−d)` равны `(1,0)` или `(0,1)`. Сравнение `left<left_end` берёт соответствующий forward cursor. При левом остатке добавляется единица к a, при правом — к b. В обоих случаях после центра `a'+c=m` и `b'+d=m+1`, поэтому выполняются оба равенства forward и reverse ends. При `c=m` reverse left — wrapping sentinel `S−1`. `wrapping_add(1)` даёт S, чтение sentinel отсутствует. `:1027–1036` записывает одно typed слово в `D[m]`, ранг m, и продвигает один выбранный курсор. [Actual merge](/root/verify-rust-std-rev2-u64-n22-n25-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:1022)

Раздельные записи пар и нечётная запись заполняют весь D[0..N] до копии, что следует из внешнего рангового аргумента при uninit OFF. Поскольку каждая позиция источника представлена ровно одним рангом, merge сохраняет все кратности и числовой порядок. Записи половин лежат внутри активного диапазона V, merge пишет в D, а последняя копия меняет только активный диапазон. Объединение трёх областей записи сохраняет `v[0]` и `v[1+N..34]`.

## Трассы различающего контроля

Вход ставит единицы в `S+0` и `S+m`. Actual S9 двигает единицу по rel0 → rel3 → rel8. Каждая последующая вставка с нулём сдвигает это одно слово на одну ячейку вправо. Actual S13 в правой половине N25 ставит единицу на rel12. Обе половины заканчиваются одной единицей. Up и down ниже перечисляют фактически выбранные читаемые слова относительно S.

| N | Вход | Up | Down | Центр и курсоры | До / после порчи |
| --- | --- | --- | --- | --- | --- |
| 22 | `0x0000_0801` | 0…9, 11 | 21, 10, 20…12 | `(a,b,c,d)=(10,1,1,10)`. Обе стороны совпадают на `S+10,S+12`. | `0x0030_0000 / 0x0030_0001` |
| 23 | `0x0000_0801` | 0…9, 11 | 22, 10, 21…13 | `(10,1,1,10)`. Forward `S+10,S+12`, ends `S+10,S+13`. Центр читает `S+12`. | `0x0060_0000 / 0x0060_0001` |
| 24 | `0x0000_1001` | 0…10, 12 | 23, 11, 22…13 | `(11,1,1,11)`. Обе стороны совпадают на `S+11,S+13`. | `0x00c0_0000 / 0x00c0_0001` |
| 25 | `0x0000_1001` | 0…10, 12 | 24, 11, 23…14 | `(11,1,1,11)`. Forward `S+11,S+13`, ends `S+11,S+14`. Центр читает `S+13`. | `0x0180_0000 / 0x0180_0001` |

Каждый свидетель запускает actual сеть на одном фиксированном активном входе с произвольными внешними словами. До порчи проходят каноничность и expected sorted-popcount. `v[1] ^= 1u64` сохраняет каноничность и frame, меняет только младший бит маски и различает общий оракул по ожидаемому assertion. Обе стороны нечётного центра и sentinel проверяются отдельными опорами. Полный домен здесь дают нативные локальные опоры и внешнее связывание.

## Unwind и профиль

| Вычисление | Максимум итераций на длину N22 / N23 / N24 / N25 |
| --- | --- |
| Инициализация маски, каждый из двух вызовов `observe_bits`, write/read scratch prefix | 22 / 23 / 24 / 25. Каждый обход отдельно, не больше 26 проверок диапазона. |
| `outside_unchanged` | 34 на вызов, 35 проверок диапазона. Внешних скалярных сравнений 12 / 11 / 10 / 9. |
| Actual обход регионов | 2 / 2 / 2 / 2. S9 и S13 содержат 25 и 45 прямых вызовов, без циклов. |
| Insertion driver, слева / справа | 2/2, 2/3, 3/3, 3/0. Сканирование `insert_tail` ≤R для R=9,10,11 на вызов, с явной веткой при begin. |
| Actual merge | 11 / 11 / 12 / 12 пар. Up/down, нечётный центр и copy-back выполняют typed copies без добавочного Rust цикла. |
| Произвольные массивы и popcount | `u64::any_array` использует raw array specialization stock Kani. `u32::count_ones` — intrinsic. |

Снимки копируют значения массивов. Посты используют интервалы индексов и скалярные `u64` сравнения. Сравнения массивов/срезов и скрытый `memcmp` отсутствуют. Наибольшая граница — 34 итерации и 35 проверок диапазона, в пределах unwind36. Успех выведенных native unwind assertions остаётся условием приёмки.

Одна job `ubuntu-24.04` X64, предел 110 минут. CBMC 6.11.0/CaDiCaL, OB12, unwind36, safety, overflow, unwinding, undefined-function и assertion-reach ON, uninit/validity OFF. На слот 120 с VT, 4 GiB группового RSS, 180 с cold wall и 2 GiB резерва ОС. Каждый слот использует отдельные холодные CWD, Cargo/Kani targets, tmp и export. `KANI_JOBS=1`. В roster закреплён порядок 25 cfg.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare собирает закреплённый tool, запускает cfg-on compile preflight с теми же verify `-Z` без export-json и с `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir "$preflight/kani-target" "$std/library"` в отдельном каталоге с пределом 180 с. При отказе сохраняет первые rustc diagnostics до двух list. Discovery отдельно вызывает `"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json` с consumer cfg off/on.

| Стадия | Граница от начала job | Окно |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Measure identity gate | 55:00 | До 60 с от входа в measure |
| Восемь слотов | 82:20 | По 205 с с cold 180 с, reap 10 с, receipt 5 с и запасом старта 10 с |
| Финальная аттестация | 84:20 | Measure 30:25 внутренний и 32 мин внешний |
| Finish и upload-gate | 89:15 | 6 и 1 мин внешние, с 5 с резерва запуска upload |
| Upload | 96:20 | 7 мин |
| План с 6 мин резерва | 102:20 | Job 110 мин |

`U64_N22_N25_COMPOSITE_WITHIN_PROFILE` требует 8/8 `MATCHED`, полных своевременных receipts/projections, штатных covers, sampler/reap, трёх лимитов и `COMPLETE` аттестации в её окне. Report сохраняет VT, cold wall, group/CBMC RSS, доступный PSS, фазу и первую CNF. Linux RSS суммируется неатомарно, разделяемые страницы могут учитываться дважды, а смена TID может редко дать недоучёт. Checkpoint исхода и reap сохраняется атомарно до проекции. При неподтверждённом reap следующие слоты пропускаются. Ограниченный повтор receipt сохраняет статус опоздания. Caps — 4 MiB на projection и 96 MiB на артефакт. По каждой длине report показывает отдельно witness и local copy-back.

## Локальная валидация

- Rustfmt `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max` применён до извлечения координат. SHA-256 бинарника `0cb21861860ae07c03b7097b099ea3e28dfb3857a9b09acce0df6b165f25cc70`. Проверены видимость, cfg, побайтное восстановление registry/manifest после снятия добавлений, побайтное совпадение runtime и контрактов, TOML, YAML, восемь блоков `bash -n`, Python syntax и `git diff --check`.
- Из actual тел извлечены 25/45 обменов, модель прошла все 512 S9 и 8192 S13 битовых входов. Проверены четыре фиксированные трассы, по одному сдвигу в каждой непустой вставке, оба равенства конечных курсоров и копия в точный диапазон. Отдельно сверены 506/506/650/650 pair-геометрий, 23/25 геометрий нечётного центра и 66 позиций вставки на шести правых рёбрах.
- Shallow bundle проверен без alternates на depth 2. Распаковка сохранила HEAD, refs и shallow boundary. Source gate сверил 27 commit/tree/parent, 28 текущих blobs, 840 координат и определения exact Proof/Check. Подстановка в тесте затрагивала только локальные checkout identities Std/stock без рекурсивных submodules. Exact detached review-trigger выпустил восемь `NOT_STARTED` receipts и пропустил синтетические `pins/sources/finish/upload-gate/upload-check`. Подмены tree/payload, admission receipt и запуск после отсечек +5355,01/+5780,01 с были отклонены.
- Синтетика на exact review-trigger выполнена последовательно. Штатная шкала 129/129 за 50,924 с, свежий старт 1 с 129/129 за 50,915 с, старт 5 с 129/129 за 49,788 с, старт 60 с 129/129 за 50,962 с. Проверены чужие selectors/kinds/targets, потеря typed/post/return anchors и unwind, второй или чужой failure, выход за профиль, late receipt, потеря reap и аттестации, подмена схемы/инвентаря и поздняя публикация.
- Std, Control, review-trigger и g0 записаны от `Tiramisu-Cake <igkharin@gmail.com>` с `[skip ci]`. Blob `test_supervisor.py` в Control и review-trigger — `df63a457c3adf648d360f3d559d5d40ef00a9427`. Локальная подготовка прошла без Cargo, rustc, Kani, CBMC, CI, push и изменения Actions variables.
