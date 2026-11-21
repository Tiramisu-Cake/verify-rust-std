# Офлайн-квалификация и допуск N21–N24

**N21, N22, N23 и N24 функционально квалифицированы и допущены как bounded-результаты в обычной полосе 6 GiB.** Для каждой длины сверены exact Check → Replace, actual вставки и copy-back, useful return и свой q-post control. Контроль N24 из 21A закрывает условие допуска, оставленное в предыдущей записи. [Допуск N20/N25 и условие N24](ADMISSION-N20-N24-N25.md) · [Правило grouped properties](GROUPED-PROPERTY-DECISION.md#правило-допуска) · [Review](GROUPED-PROPERTY-REVIEW.md)

## Строки допуска

Область — actual `small_sort_network`, `u8/KeyLess<u8>`, initialized V34, base1, произвольные входные байты и независимый q по всем `u8`, exact длины, `merge_wide`, normal fork OFF, OB11, unwind36. На нормальном возврате проверены q/order-stat маска по snapshot до сети, q-frame и побайтовый frame за пределами активного среза. Scratch — отдельный `MaybeUninit<[u8; 32]>` с base+0. Интервалы полуоткрытые. Относительные индексы вставок включают обе границы.

| Длина и exact маршрут | Presort Check и actual вставки | Whole merge Check и copy-back | Matched контроль (21A) | Максимум цепочки, KiB | Решение |
| --- | --- | --- | --- | ---: | --- |
| **N21**, `COMPACT-N21-ACT-INSERT-OB11` (21A), `v[1..22)` | `MW-S9-L10` (16), `v[1..11)`, rel9 · `MW-S9-R-B11-L11-OB11` (21A), `v[11..22)`, rel9–10 | `MW-MERGE-N21-OB11` (21A), scratch `[0..10) + {10} + [11..21)`, copy-back 21 байта | `COMPACT-N21-ACT-INSERT-CORRUPT-OB11` | **4 588 580** · `MW-S9-L10` | Квалифицирован и допущен при ≤6 GiB по измеренному fit. Запас 1 702 876 KiB. |
| **N22**, `COMPACT-N22-ACT-INSERT-OB11` (21A), `v[1..23)` | `MW-S9-L-B01-L11-OB11`, `v[1..12)`, rel9–10 · `MW-S9-R-B12-L11-OB11`, `v[12..23)`, rel9–10 (оба 21A) | `MW-MERGE-N22-OB11` (21A), scratch `[0..11) + [11..22)`, copy-back 22 байта | `COMPACT-N22-ACT-INSERT-CORRUPT-OB11` | **4 583 904** · `MW-S9-L-B01-L11-OB11` | Квалифицирован и допущен при ≤6 GiB. Запас 1 707 552 KiB. |
| **N23**, `COMPACT-N23-ACT-INSERT-OB11` (21A), `v[1..24)` | `MW-S9-L-B01-L11-OB11`, `v[1..12)`, rel9–10 · `MW-S9-R-B12-L12-OB11`, `v[12..24)`, rel9–11 (оба 21A) | `MW-MERGE-N23-OB11` (21A), scratch `[0..11) + {11} + [12..23)`, copy-back 23 байта | `COMPACT-N23-ACT-INSERT-CORRUPT-OB11` | **4 583 904** · `MW-S9-L-B01-L11-OB11` | Квалифицирован и допущен при ≤6 GiB. Запас 1 707 552 KiB. |
| **N24**, `COMPACT-N24-ACT-INSERT-OB11` (20), `v[1..25)` | `MW-S9-L12` (16), `v[1..13)`, rel9–11 · `MW-S9-R-B13-L12-OB11` (20), `v[13..25)`, rel9–11 | `MW-MERGE-N24-OB11` (20), scratch `[0..12) + [12..24)`, copy-back 24 байта | `COMPACT-N24-ACT-INSERT-CORRUPT-OB11` | **4 579 816** · `MW-S9-R-B13-L12-OB11` | Квалифицирован и допущен при ≤6 GiB. Запас 1 711 640 KiB. |

Цель 6 GiB соответствует 6 291 456 KiB. Корни 20 и 21A завершились при nominal/effective cap 6/6 GiB. Два используемых Check из 16 завершились при 10/10 GiB, их fit установлен по измеренным пикам. Максимум каждой цепочки включает consumer, оба presort Check, merge Check и matched control. RSS — sampled child PGID VmRSS с шагом 50 мс.

## Идентичность и inventory

Входной g0 `71c52e368c93393ae618f04a35f035cfa95619ad`. Артефакты `Tiramisu-Cake/kani`, attempt 1. Общий tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, Kani 0.68.0, CBMC 6.11.0, CaDiCaL, `x86_64-unknown-linux-gnu`. Во всех корнях `--exact --jobs=1 --no-assert-contracts`, regular + JSON export, обычные memory/bounds/overflow/unwind/undefined-function/reachability checks и пустые ordinary stubs.

| Кампания · run | Std commit / tree | Control candidate → trigger / tree |
| --- | --- | --- |
| 16 · 44890498157 | `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1` / `e2a757c2ca5659a83e70f3775ebce3e672dd0463` | `0578f584b650488cee98281961e8f699a82ab942` → `94e5fba7950bbc1941cafe01e069879b220c78d3` / `6e0f3a04555c4dfe90a5d3195610b86c541cc253` |
| 20 · 44913550779 | `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` / `3cc0e5aa1a8d5100c2812bef424291af9f83f630` | `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` → `97f552174eb15a06f726da390cfa7fbe5d981302` / `aba7ec3689b53644c105a138283f2efd7db4fcb6` |
| 21A · 44919576152 | `e2bd3c6adc870729794a6b2fe44eece988402d8f` / `7e62553ab80d6178ce8f01c8212e084b2186e308` | `2fa3734008c1e5e3e46cd7f72f8bbc891ae99080` → `2ffd91183ebd4cb6c2f1adc96a5de5ff622c7f20` / `3174f86fd3aa6b30a4a70158156f955f8f54267f` |

Control parent у всех трёх кампаний `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. SHA-256 frozen request 21A `102561420c20400b4323a33a0af31e2af9f440f694cfbc266c051b314a88dd50`, индекса 21A `5745590493f746232940212624968e8de7fba49d5d100f975148da568846ab78`. Digests для 16/20 повторно сверены с предыдущим допуском. [Индекс 16](run-44890498157/raw/ch8-q-pilot-44890498157-1/q-pilot-raw.json) · [Индекс 20](run-44913550779/raw/ch8-q-pilot-44913550779-1/q-pilot-raw.json) · [Индекс 21A](run-44919576152/raw/ch8-q-pilot-44919576152-1/q-pilot-raw.json) · [Digests 16/20](ADMISSION-N20-N24-N25.md#идентичность-и-native-inventory)

Для 19 exact roots сверены Git trees и pinned file hashes, frozen requests, roster, invocation, argv, RUSTFLAGS, resolved mode и verified stubs. Размеры и SHA-256 всех 57 stdout/stderr/export совпали с индексами и Git blobs входного g0. Проверены snapshot after reap, отсутствие truncation, child exit, cleanup/containment и привязка PID/PGID. Regular содержит непрерывные ordinals, полные `RESULTS` / `SUMMARY` и terminal verdict; JSON export совпадает по exact harness, итогу, числам, статусам и ID доступных buckets, классу и location отказов.

Использован тот же extractor `native-inventory/1` с SHA-256 `2588eec19879eb774232a195e1b91bf920da310bc5806465db2371525595c255`. Синтетические проверки формата прошли. Пять ранее извлечённых корней совпали с прежними inventory с учётом provenance входного g0. Дополнение содержит **14 root manifests и 10 017 свойств** (9 824 S, 4 F, 117 U и 72 covers), его SHA-256 `eacf4118958c77c952c34dd47d508d88f21000611598a05b29e1498a82b0f5d6`. По всем 19 корням — 13 354 свойства (13 094 S, 4 F, 151 U и 105 covers), все 91 unsupported checks имеют `SUCCESS`. Коллизий display ID и дублей нет. [Новый inventory](NATIVE-INVENTORY-N21-N24.jsonl) · [Inventory MW-S9-L10](NATIVE-INVENTORY-N13-N20.jsonl#L8647) · [Inventory N24 positive и Check](NATIVE-INVENTORY-N20-N24-N25.jsonl#L624)

S/F/U — `SUCCESS` / `FAILURE` / `UNREACHABLE`. Все covers имеют `SATISFIED`.

| Кампания | Exact root | S/F/U | Covers | Child PGID | RSS, KiB | Cap nom./eff., GiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 16 | [MW-S9-L10](NATIVE-INVENTORY-N13-N20.jsonl#L8647) | 610/0/5 | 7 | 9210 | 4 588 580 | 10/10 |
| 16 | [MW-S9-L12](NATIVE-INVENTORY-N20-N24-N25.jsonl#L624) | 610/0/5 | 7 | 12525 | 4 538 852 | 10/10 |
| 20 | [MW-S9-R-B13-L12-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L5246) | 610/0/5 | 7 | 10963 | 4 579 816 | 6/6 |
| 20 | [MW-MERGE-N24-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L5869) | 685/0/9 | 6 | 11431 | 4 224 120 | 6/6 |
| 20 | [COMPACT-N24-ACT-INSERT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L6570) | 755/0/10 | 6 | 11895 | 2 930 196 | 6/6 |
| 21A | [MW-S9-L-B01-L11-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L1) | 610/0/5 | 7 | 9205 | 4 583 904 | 6/6 |
| 21A | [MW-S9-R-B11-L11-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L624) | 610/0/5 | 7 | 9750 | 4 566 868 | 6/6 |
| 21A | [MW-S9-R-B12-L11-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L1247) | 610/0/5 | 7 | 10214 | 4 569 264 | 6/6 |
| 21A | [MW-S9-R-B12-L12-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L1870) | 610/0/5 | 7 | 10680 | 4 573 188 | 6/6 |
| 21A | [MW-MERGE-N21-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L2493) | 685/0/9 | 6 | 11145 | 3 830 608 | 6/6 |
| 21A | [MW-MERGE-N22-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L3194) | 685/0/9 | 6 | 11603 | 3 885 188 | 6/6 |
| 21A | [MW-MERGE-N23-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L3895) | 685/0/9 | 6 | 12060 | 4 217 484 | 6/6 |
| 21A | [COMPACT-N21-ACT-INSERT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L4596) | 755/0/10 | 6 | 12526 | 2 620 620 | 6/6 |
| 21A | [COMPACT-N21-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L5368) | 766/1/10 | 2 | 12967 | 2 750 596 | 6/6 |
| 21A | [COMPACT-N22-ACT-INSERT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L6148) | 755/0/10 | 6 | 13409 | 2 653 340 | 6/6 |
| 21A | [COMPACT-N22-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L6920) | 766/1/10 | 2 | 13853 | 2 626 968 | 6/6 |
| 21A | [COMPACT-N23-ACT-INSERT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L7700) | 755/0/10 | 6 | 14293 | 2 785 088 | 6/6 |
| 21A | [COMPACT-N23-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L8472) | 766/1/10 | 2 | 14732 | 2 549 760 | 6/6 |
| 21A | [COMPACT-N24-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N21-N24.jsonl#L9252) | 766/1/10 | 2 | 15234 | 2 603 496 | 6/6 |

## Source и Check → Replace

S — `library/core/src/slice/sort/shared/smallsort.rs`, H — `smallsort/verify/sorting_q_merge.rs`, M — `smallsort/verify/sorting_q_merge_model.rs` относительно `sort/shared/`. Координаты относятся к Std 21A, кроме явно помеченных. `#n` — native `Check n` внутри exact root. Полные IDs, class и location есть в inventory.

- **Перенос 16 → 20 → 21A.** В переходе 16 → 20 модели и контракт вставки получили ветви под выключенными `q_no_merge_sort13` и `q_compact_presort13`. Active `merge_wide` clauses, comparator, production bodies и fixtures левых L10/L12 сохранились. Std 21A добавляет строки только в H. Тела и active contracts S/M, общий presort frame, positive macro и существующий positive N24 сохранены. Поэтому L10 и L12 применимы к exact левым половинам N21/N24, а positive и Check N24 из 20 образуют matched цепочку с контролем 21A. У N24 positive и control одинаковые `v[1..25)`, 12+12, `u8/KeyLess<u8>`, cfg, OB11, unwind36 и verified stubs `sort9_optimal` / `bidirectional_merge`. [Переход 16 → 20](ADMISSION-N20-N24-N25.md#source-и-check--replace) · [Пины и зависимости 21A](PILOT21-IMPL-HANDOFF.md)
- **Presort.** В S:339–381 длина задаёт ровно две половины и по одному вызову sort9 на каждой. Geometry Pre проверяет exact type, readable срез и writable prefix. Check проходит 25 actual swaps, ограничивает запись первыми девятью байтами и устанавливает numeric order и число байтов ниже прежнего q. Fixture проверяет q и V34 вне prefix, включая хвост half, а useful-return cover следует за телом. Source вызовы новых Check на H:1379 и invocations H:1386/1396/1406/1416 связывают exact span и конец записи `10/20/21/21` соответственно. [Прежние active clauses](ADMISSION-N20-N24-N25.md#source-и-check--replace)
- **Actual вставки.** В S:370 offset=9, индексы заданы двумя длинами половин и sentinel в S:873–894. Тело S:826–860 использует ранний возврат или сдвиг в пределах `v[base..base+rel+1)` с закрытием gap через `CopyOnDrop`. Insert остаётся в Original, presort и whole merge работают в Replace. После вставок numeric Pre merge проверяет обе полные половины.
- **Whole merge.** Replace на S:389 проверяет шесть caller Pre, включая numeric order, exact geometry, disjoint, writable scratch, readable source и len (S:1194–1200, 1226–1248; M:562–591). Отдельный actual Check (H:1754–1770) использует тот же span и scratch. Up/Down в S:1306–1309 записывают два потока. При нечётных N21/N23 S:1315–1320 выбирает оставшийся элемент и записывает ровно один odd slot на S:1318. Для N22/N24 ветка исключена константной чётностью. Cursor guard следует на S:1326–1327. `modifies` охватывает активные N байтов назначения. `old(merge_capture)` читает initialized source и q до havoc, post проверяет весь scratch при неизменном q, fixture проверяет q и полный source V34. Consumer исполняет actual `copy_nonoverlapping` на S:390 и проверяет итог на исходном V34 (H:2209, 2233–2249).

### Native-роли Check

Post presort — `sort9_optimal::<…>::{closure#2}.assertion.1`, S:534. Post merge — `bidirectional_merge::<…>::{closure#2}.assertion.1`, S:1226. Для DFCC приведены `memcpy.assigns.1–2` и, у presort, `memmove.assigns.1–2`.

| Exact Check | Ensures | DFCC memcpy / memmove | q / byte frame | Useful return |
| --- | --- | --- | --- | --- |
| MW-S9-L10 | #11 | #3–4 / #38–39 | #130–131 | #138 |
| MW-S9-L12 | #21 | #34–35 / #27–28 | #156–157 | #164 |
| MW-S9-R-B13-L12-OB11 | #107 | #5–6 / #1–2 | #115–116 | #123 |
| MW-S9-L-B01-L11-OB11 | #3 | #52–53 / #6–7 | #133–134 | #141 |
| MW-S9-R-B11-L11-OB11 | #7 | #5–6 / #1–2 | #140–141 | #148 |
| MW-S9-R-B12-L11-OB11 | #56 | #30–31 / #1–2 | #35–36 | #43 |
| MW-S9-R-B12-L12-OB11 | #41 | #24–25 / #43–44 | #107–108 | #115 |
| MW-MERGE-N21-OB11 | #146 | #79–80 | #39–40 | #41 odd |
| MW-MERGE-N22-OB11 | #65 | #112–113 | #10–11 | #12 |
| MW-MERGE-N23-OB11 | #256 | #43–44 | #130–131 | #132 odd |
| MW-MERGE-N24-OB11 | #148 | #46–47 | #59–60 | #61 |

В merge Check N21/N22/N23/N24 `panic_on_ord_violation.assertion.1` проходит в #137/#246/#247/#83 соответственно. У обоих odd Check pointer goal #362 привязан к сравнению на S:1316 в Check wrapper. Группа `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3` (#260–262) покрывает disjoint, readable и writable, включая odd copy на S:1318. Actual Up/Down проходят grouped DFCC и safety на обоих потоках записей.

### Native-роли consumers и контролей

Все Pre, safety, guard и frame в таблице имеют `SUCCESS`. Presort Pre — `sort9_optimal::<…>::{closure#1}.assertion.1` (S:549), общий для обоих вызовов. Merge Pre — `bidirectional_merge::<…>::{closure#1}.assertion.1–6` в порядке numeric, geometry, disjoint, writable, readable, len. Insert safety — `insert_tail::<…>.safety_check.1–6` (S:831/856), offset guard — `insertion_sort_shift_left::<…>.assertion.1` (S:875). Copy Pre — та же тройка `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3`, в том числе для copy-back (S:390).

| Root | Presort Pre | Insert safety / guard | Merge Pre | Copy Pre | q-post / q-frame / outside | Covers |
| --- | --- | --- | --- | --- | --- | --- |
| N21 positive | #116 | #243–248 / #237 | #4–9 | #299–301 | #88 / #89 / #91 | #92–97 |
| N21 control | #123 | #238–243 / #229 | #133–138 | #299–301 | #113 F / #110 / #112 | #106, #109 |
| N22 positive | #197 | #229–234 / #143 | #184–189 | #299–301 | #268 / #269 / #271 | #272–277 |
| N22 control | #279 | #179–184 / #62 | #7–12 | #299–301 | #234 F / #231 / #233 | #227, #230 |
| N23 positive | #137 | #144–149 / #234 | #2–7 | #299–301 | #25 / #26 / #28 | #29–34 |
| N23 control | #253 | #127–132 / #44 | #157–162 | #299–301 | #175 F / #172 / #174 | #168, #171 |
| N24 positive (20) | #135 | #144–149 / #214 | #265–270 | #299–301 | #73 / #74 / #76 | #77–82 |
| N24 control | #6 | #124–129 / #209 | #238–243 | #299–301 | #150 F / #147 / #149 | #143, #146 |

Каждый positive достигает mixed threshold, adjacent ties, q=0, q=255, q absent и useful return после всей сети. Каждый control обнуляет тот же активный вход, задаёт q=1 и сохраняет произвольные внешние байты. После useful-return cover `v[1] == 0` запись `v[1] = 255` меняет младший бит маски, затем достигается corruption cover. Capture (#104/#225/#166/#141 соответственно) и оба frame проходят. В каждом control ровно один terminal `FAILURE` класса `assertion` со следующим native ID и location (раскрытие H:2339/2343/2347/2351).

| Root | Полный property ID | Description | Native Location |
| --- | --- | --- | --- |
| N21 control #113 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n21_actual_insert_corrupt.assertion.9` | `COMPACT_N21_ACT_INSERT_CORRUPT_QPOST` | H:2339:1 |
| N22 control #234 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n22_actual_insert_corrupt.assertion.9` | `COMPACT_N22_ACT_INSERT_CORRUPT_QPOST` | H:2343:1 |
| N23 control #175 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n23_actual_insert_corrupt.assertion.9` | `COMPACT_N23_ACT_INSERT_CORRUPT_QPOST` | H:2347:1 |
| N24 control #150 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n24_actual_insert_corrupt.assertion.9` | `COMPACT_N24_ACT_INSERT_CORRUPT_QPOST` | H:2351:1 |

### Развёртка и достижимость

Все **44 напечатанные unwind checks** имеют `SUCCESS`, по четыре у каждого из 11 Check. У восьми consumers/control включены unwinding assertions, отдельных unwind goals в `RESULTS` нет. Regular traces показывают развёртку двух регионов, actual insert и проходов fixture. Максимальные напечатанные номера итераций для N21/N22/N23/N24 — 21/22/23/24, сообщений `Not unwinding` нет. Source bound охватывает до трёх вставок на половину, до 11 шагов sift и обходы не более 34 байтов. Fixed route и достигнутый useful-return cover в каждом root связывают обязательные исполнения с активным Check либо Replace. Терминальный `SUCCESS` закрывает конъюнкцию экземпляров общего ID в соответствующем root. [Grouped-property правило](GROUPED-PROPERTY-DECISION.md#правило-допуска) · [Review семантики](GROUPED-PROPERTY-REVIEW.md)

У `UNREACHABLE` сохранены native статусы и координаты. Четыре U в каждом merge-bearing root относятся к арифметике отдельного символа Original `bidirectional_merge`. У providers исполняемый Check wrapper имеет успешные arithmetic и pointer checks, у consumers/control выбирается Replace. Остальные U относятся к тем же guarded core helpers, что и в допуске N20/N25: allocation-size divide, `abs_diff`, `is_aligned_to`, `is_multiple_of` у consumers/control и сдвиг для статического сообщения в `fmt::Arguments::from_str`. Regular location общих helpers указывает декларацию. Обязательные native роли на exact маршрутах опираются на положительные статусы и source binding. [Разбор U в прецеденте](ADMISSION-N20-N24-N25.md#развёртка-и-достижимость)

Эта запись устанавливает офлайн-допуск bounded-результатов для четырёх exact длин. Исторические receipts сохраняют `proof_credit=NONE`. B1/B2 proof credit и dispatch вне области допуска.
