# Офлайн-квалификация и допуск N20, N24, N25

**N20 допущен как bounded-результат в обычной полосе 6 GiB.** Положительная цепочка N24 функционально квалифицирована и укладывается в 6 GiB по имеющимся замерам. Её допуск ждёт exact q-post control из 21A. **N25 допущен как bounded-результат по измеренному fit в полосах 8 GiB для `MW-S13-R13` и 6 GiB для остальных корней цепочки.** [Задание](PILOT21-QUALIFICATION-TASK.md) · [Прецедент](ADMISSION-N13-N19-FINAL.md) · [Правило grouped properties](GROUPED-PROPERTY-DECISION.md#правило-допуска) · [Review](GROUPED-PROPERTY-REVIEW.md)

## Область и решения

Actual `small_sort_network`, `u8/KeyLess<u8>`, initialized V34, base1, произвольные байты и независимый `q:any::<u8>()`. Область результата охватывает нормальный возврат, полную пороговую маску по order-stat исходного среза, сохранение q и всех внешних байтов V34. Компаратор сравнивает полные байты независимо от q. Совпадение маски при каждом из 256 порогов определяет порядок и точное мультимножество. Check действует при requires своего контракта. Профиль fork normal OFF ограничивает допуск штатными проверками Kani, за пределами области остаются дополнительные проверки uninit/validity/permission.

Половины, footprints и scratch spans ниже полуоткрытые. Rel — индекс tail относительно базы вставки. В каждой строке указан максимум sampled child PGID RSS по доступной цепочке, включая применимый exact control.

| Длина | Exact consumer и Check → Replace | Контроль | Максимум RSS, KiB · nominal/effective cap корня | Решение |
| --- | --- | --- | --- | --- |
| **N20** | `COMPACT-N20-ACT-INSERT-OB11` (20), `v[1..21)`, 10+10. `MW-S9-L10`, `MW-S9-R10` (16) на `v[1..11)`, `v[11..21)`. Две actual вставки base1/11 rel9. `MW-MERGE-N20` (16), scratch `[0..10) + [10..20)`, actual copy-back 20 байтов. | `COMPACT-N20-ACT-INSERT-CORRUPT-OB11` (20), exact endpoint. | **4 588 580** · `MW-S9-L10` · 10/10 GiB | Функционально квалифицирован. **Допущен** по измеренному fit ≤6 GiB, запас 1 702 876 KiB. |
| **N24** | `COMPACT-N24-ACT-INSERT-OB11` (20), `v[1..25)`, 12+12. `MW-S9-L12` (16), `MW-S9-R-B13-L12-OB11` (20) на `v[1..13)`, `v[13..25)`. Шесть actual вставок base1/13 rel9–11. `MW-MERGE-N24-OB11` (20), scratch `[0..12) + [12..24)`, actual copy-back 24 байтов. | N20 проверяет чувствительность observer на своём маршруте. Exact `COMPACT-N24-ACT-INSERT-CORRUPT-OB11` запланирован в 21A. | **4 579 816** · `MW-S9-R-B13-L12-OB11` · 6/6 GiB | Positive и Check функционально квалифицированы, измеренный запас 1 711 640 KiB. **Допуск открыт до exact control и его замера**. |
| **N25** | `COMPACT-N25-ACT-INSERT-OB11` (20), `v[1..26)`, 12+13. `MW-S9-L12`, `MW-S13-R13` (16) на `v[1..13)`, `v[13..26)`. Три actual вставки base1 rel9–11. Справа offset=13 и пустой цикл. `MW-MERGE-N25` (16), scratch `[0..12) + {12} + [13..25)`, actual copy-back 25 байтов. | `COMPACT-N25-ACT-INSERT-CORRUPT-OB11` (20), exact endpoint. | **7 671 888** · `MW-S13-R13` · 10/10 GiB | Функционально квалифицирован. **Допущен** по измеренному fit ≤8 GiB для `MW-S13-R13`, запас 716 720 KiB, и fit ≤6 GiB для остальных корней цепочки. |

Исторические корни 16 завершились при nominal/effective cap 10/10 GiB, корни 20 при 6/6 GiB. Для корней 16 fit в более узкой полосе основан на замерах. Расширение полосы 8 GiB на все Check `sort13_optimal` в `1f0bb751f1` охватывает `MW-S13-R13` с геометрией (base13, len13). Его пик 7,32 GiB (875,349 с child при timeout 1 800 с) оставляет **716 720 KiB** запаса. Максимум остальных корней N25 составляет **4 538 852 KiB** (`MW-S9-L12`) при цели 6 GiB. [Расширение решения владельца](OWNER-DECISION-SORT13-8GIB.md#расширение-2026-11-21) · [План 21A и 21C](PILOT21-IMPL-TASK.md)

## Идентичность и native inventory

Вход g0 `d14b25c3f0252c9722b92cc1561890cd7d048e0b`, результаты 20 на `929baddca1`. Оба локальных артефакта относятся к `Tiramisu-Cake/kani`, attempt 1. Общий tool pin `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, Kani 0.68.0, CBMC 6.11.0, CaDiCaL, `x86_64-unknown-linux-gnu`. Все корни используют `merge_wide`, OB11, unwind36, `--exact --jobs=1 --no-assert-contracts`, regular + JSON export, обычные memory/bounds/overflow/unwind/undefined-function/reachability checks. Ordinary stubs пусты.

| Кампания · run/attempt | Std commit / tree | Control candidate → trigger / tree |
| --- | --- | --- |
| 16 · 44890498157/1 | `ed184d3f172def1b4d1bf6281a03ba2a0d5bb8f1` / `e2a757c2ca5659a83e70f3775ebce3e672dd0463` | `0578f584b650488cee98281961e8f699a82ab942` → `94e5fba7950bbc1941cafe01e069879b220c78d3` / `6e0f3a04555c4dfe90a5d3195610b86c541cc253` |
| 20 · 44913550779/1 | `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` / `3cc0e5aa1a8d5100c2812bef424291af9f83f630` | `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` → `97f552174eb15a06f726da390cfa7fbe5d981302` / `aba7ec3689b53644c105a138283f2efd7db4fcb6` |

Оба Control имеют parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Для std 20 таблица использует tree из Git, frozen request и raw index. В строке std-базы [плана 21](PILOT21-IMPL-TASK.md#scope-и-формы-корней) опечатка в tree.

| Кампания | SHA-256 frozen request | SHA-256 `q-pilot-raw.json` |
| --- | --- | --- |
| 16 | `11592b80dd83eb39aab8cfc5458a049660d4314ee93050fbdb7a6afb6770eeae` | `7722d45b7105d1f8bdfbba1a9e29fd980fc8c6af89aa4963dd228f8be336b783` |
| 20 | `6673e043738a687a0a47dabeb43f72f98a9dea8f6938be288c5e666658133033` | `60bc382276b2c66eef636ea86b84bf0fef411fb076ee6ce14b87d91f74aeffc9` |

Сверены request из Git blob, полные trees, pinned std/control file hashes, roster, invocation IDs, argv, RUSTFLAGS, resolved mode и verified stubs. SHA-256 и размеры 39 файлов stdout/stderr/export совпали с индексами и Git-артефактами на входном g0. Файлы сняты после reap без truncation. У 13 корней есть exact harness, непрерывные ordinals, полные `RESULTS` и `SUMMARY`, terminal verification, согласованные с export числа S/F/U, covers и детальные ID/status доступных buckets. У всех подтверждены child exit, cleanup/containment, identity PID/PGID и cap. RSS — sampled PGID VmRSS с шагом 50 мс. Максимум берётся по отдельным последовательным запускам. [Индекс 16](run-44890498157/raw/ch8-q-pilot-44890498157-1/q-pilot-raw.json) · [Индекс 20](run-44913550779/raw/ch8-q-pilot-44913550779-1/q-pilot-raw.json)

Использован тот же `native-inventory/1`, SHA-256 `2588eec19879eb774232a195e1b91bf920da310bc5806465db2371525595c255`. Синтетические проверки формата прошли. Три повторно извлечённых корня N20 совпали с прежними manifests и property rows с учётом provenance двух офлайн-сверок. Дополнение включает **10 root manifests, 7 331 свойство** (7 191 S, 2 F, 83 U, 55 covers). Всего в выбранных **13 exact roots** 9 275 свойств (9 096 S, 2 F, 102 U, 75 covers). Все 64 unsupported properties имеют статус `SUCCESS`. Display ID collisions и дубли записей отсутствуют. [Прежний inventory](NATIVE-INVENTORY-N13-N20.jsonl) · [Дополнение](NATIVE-INVENTORY-N20-N24-N25.jsonl)

S/F/U обозначают `SUCCESS` / `FAILURE` / `UNREACHABLE`. Все указанные covers имеют `SATISFIED`. Ссылки ведут к root manifest с полным invocation ID, checked argv и координатами stdout.

| Run | Exact root | S/F/U | Covers | Child PGID | RSS, KiB | Cap nom./eff., GiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 16 | [MW-S9-L10](NATIVE-INVENTORY-N13-N20.jsonl#L8647) | 610/0/5 | 7 | 9210 | 4 588 580 | 10/10 |
| 16 | [MW-S9-R10](NATIVE-INVENTORY-N13-N20.jsonl#L9270) | 610/0/5 | 7 | 9694 | 4 581 964 | 10/10 |
| 16 | [MW-MERGE-N20](NATIVE-INVENTORY-N13-N20.jsonl#L10664) | 685/0/9 | 6 | 11068 | 3 602 764 | 10/10 |
| 16 | [MW-S13-R13](NATIVE-INVENTORY-N20-N24-N25.jsonl#L1) | 610/0/5 | 7 | 11959 | 7 671 888 | 10/10 |
| 16 | [MW-S9-L12](NATIVE-INVENTORY-N20-N24-N25.jsonl#L624) | 610/0/5 | 7 | 12525 | 4 538 852 | 10/10 |
| 16 | [MW-MERGE-N25](NATIVE-INVENTORY-N20-N24-N25.jsonl#L1247) | 685/0/9 | 6 | 12986 | 4 523 700 | 10/10 |
| 20 | [COMPACT-N20-ACT-INSERT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L1948) | 755/0/10 | 6 | 9097 | 2 627 816 | 6/6 |
| 20 | [COMPACT-N20-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L2720) | 766/1/10 | 2 | 9546 | 2 556 432 | 6/6 |
| 20 | [COMPACT-N25-ACT-INSERT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L3500) | 852/0/10 | 6 | 9989 | 3 114 424 | 6/6 |
| 20 | [COMPACT-N25-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L4369) | 863/1/10 | 2 | 10514 | 2 670 188 | 6/6 |
| 20 | [MW-S9-R-B13-L12-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L5246) | 610/0/5 | 7 | 10963 | 4 579 816 | 6/6 |
| 20 | [MW-MERGE-N24-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L5869) | 685/0/9 | 6 | 11431 | 4 224 120 | 6/6 |
| 20 | [COMPACT-N24-ACT-INSERT-OB11](NATIVE-INVENTORY-N20-N24-N25.jsonl#L6570) | 755/0/10 | 6 | 11895 | 2 930 196 | 6/6 |

## Source и Check → Replace

S — `library/core/src/slice/sort/shared/smallsort.rs`, H — `smallsort/verify/sorting_q_merge.rs`, M — `smallsort/verify/sorting_q_merge_model.rs`. Координаты относятся к std 20, если указан только файл. `#n` — native `Check n` внутри exact root. Полный ID, class и Location хранятся в inventory.

- **Перенос 16 → 20.** В Git diff для `library/core` изменены только S, H и M. В S добавлена ветка q-only insert ensures под `kani_smallsort_q_no_merge_sort13`, которая выключена в обоих runs. Production bodies сети, presort, insert, merge, Up/Down, disjoint helper и copy-back совпадают. В M дополнительные presort-ветки требуют выключенных cfg `q_no_merge_sort13` и, для compact модели, `q_compact_presort13`. Существующие active geometry, numeric/q models и source-only merge capture совпадают. Шесть импортированных fixtures, макрос frame/covers и helper merge covers сохраняют тела. У merge fixtures N20 и N25 строки H:1428/1457 на 16 стали H:1498/1527 на 20. Новый правый Check N24 H:1301 и merge Check N24 H:1557 закреплены непосредственно на pin 20.
- **Presort.** Сеть S:339–381 дважды вызывает driver на фиксированных половинах. Wide geometry Pre S:549/624 проверяет exact type, readable срез и writable prefix с len 9–12 или 13–16 соответственно (M:470–495). `modifies` ограничивает запись первыми 9/13 байтами. `old` захватывает q и число байтов ниже q в префиксе до havoc. Ensures проверяет numeric order и это же число при неизменном q (S:534–555, S:609–630, M:497–556). Check исполняет 25/45 actual swaps. H:788–830 проверяет q и V34 вне префикса, включая хвост каждой половины. У L10/R10 сохраняются `v[10]`/`v[20]`, у L12 и R-B13-L12 — `v[10..13)`/`v[22..25)`. R13 пишет всю правую половину `v[13..26)`.
- **Actual insert.** На S:370 после presort вызывается `insertion_sort_shift_left`. Пары (base,rel) из таблицы следуют из `offset` и sentinel S:873–894. Каждая вставка допускает ранний возврат или сдвигает только `v[base..base+rel+1)`: sift стартует в tail−1, ограничен begin и write gap закрывает `CopyOnDrop` (S:826–860). Проверены grouped dereference/alignment native ID, guard offset и preconditions копирования. Числовой порядок исходного префикса задаёт presort, а единый numeric caller Pre merge проверяет обе полные половины после actual вставок. Insert идёт в Original, verified stubs есть только у presort и merge.
- **Whole merge.** Replace на S:389 проверяет шесть caller Pre из S:1194–1200 и S:1226–1248. Geometry включает exact type/len, readable source, writable scratch span и disjoint; отдельно проверяется numeric order обеих половин (M:562–591). В отдельном scratch32+0 actual Check выполняет S:1306–1309 (Up/Down с монотонными dst-курсорами), ровно один odd copy в N25 (S:1314–1324), затем cursor guard S:1326. У even N guard odd ветки ложен по длине. `modifies` ограничивает активный префикс scratch, q/source frame подтверждается fixture. `old(merge_capture)` читает только initialized source и q до havoc. Post проверяет все N байтов scratch по прежнему q (M:600–633). Две записи за шаг и odd slot покрывают весь префикс на нормальном возврате. Consumer затем исполняет actual `copy_nonoverlapping` S:390, где групповая тройка проверяет disjoint, readable и writable для всех вызовов этой операции, включая copy-back. Итоговая маска проверяется уже на исходном V34, по захвату до сети (H:2021,2045–2061). [Check lowering](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/check.rs:23) · [Replace lowering](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/replace.rs:101)

### Native-роли Check

Post presort — `sort{9,13}_optimal::<…>::{closure#2}.assertion.1` (S:534 либо S:609). Post merge — `bidirectional_merge::<…>::{closure#2}.assertion.1` (S:1202 на 16, S:1226 на 20). Таблица связывает выбранные assigns, safety и guard-проверки с телом в Check. Остальные свойства доступны по root manifests.

| Check | Ensures | DFCC `memcpy.assigns.1–2` / `memmove.assigns.1–2` | q/byte frame | Useful return, всего covers |
| --- | --- | --- | --- | --- |
| `MW-S9-L10` | #11 | #3–4 / #38–39 | #130–131 | #138, 7/7 |
| `MW-S9-R10` | #211 | #6–7 / #90–91 | #170–171 | #178, 7/7 |
| `MW-S9-L12` | #21 | #34–35 / #27–28 | #156–157 | #164, 7/7 |
| `MW-S13-R13` | #142 | #11–12 / #96–97 | #129–130 | #137, 7/7 |
| `MW-S9-R-B13-L12-OB11` | #107 | #5–6 / #1–2 | #115–116 | #123, 7/7 |
| `MW-MERGE-N20` | #144 | #39–40 | #42–43 | #44, 6/6 |
| `MW-MERGE-N24-OB11` | #148 | #46–47 | #59–60 | #61, 6/6 |
| `MW-MERGE-N25` | #27 | #32–33 | #9–10 | #11 odd return, 6/6 |

У трёх merge Check guard ведёт в `panic_on_ord_violation`, native `assertion.1` соответственно #249/#83/#61 со статусом `SUCCESS`. В N25 #362 привязывает pointer check к сравнению при odd выборе в actual Check wrapper на S:1292 pin 16, #260–262 проверяют `copy_nonoverlapping::<u8>.precondition_instance.1–3`, включая запись odd slot на S:1294 pin 16. Actual Up/Down в каждом merge Check проходят общие safety/DFCC assertions по двум потокам записей.

### Native-роли consumers и контролей

Все перечисленные Pre, safety и frame assertions имеют `SUCCESS`. Столбец q-post отмечает оба назначенных отказа. Общие presort Pre ID — `sort9_optimal::<…>::{closure#1}.assertion.1` и для N25 `sort13_optimal::<…>::{closure#1}.assertion.1`. Merge Pre — шесть `bidirectional_merge::<…>::{closure#1}.assertion.1–6` в порядке numeric, geometry, disjoint, writable, readable, len. Actual insert safety — `insert_tail::<…>.safety_check.1–6` на S:831/856 плюс abort guard `insertion_sort_shift_left::<…>.assertion.1` на S:875. Тройка copy Pre — `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3`, привязанная также к S:390.

| Root (20) | Presort Pre | Insert safety / offset guard | Merge Pre | Copy Pre | q-post / q-frame / outside | Covers |
| --- | --- | --- | --- | --- | --- | --- |
| N20 positive | #278 | #190–195 / #239 | #177–182 | #299–301 | #8 / #9 / #11 | #12–17 |
| N20 control | #100 | #199–204 / #115 | #6–11 | #299–301 | #263 F / #260 / #262 | #256, #259 |
| N24 positive | #135 | #144–149 / #214 | #265–270 | #299–301 | #73 / #74 / #76 | #77–82 |
| N25 positive | #109, #280 | #54–59 / #152 | #158–163 | #312–314 | #201 / #202 / #204 | #205–210 |
| N25 control | #206, #281 | #112–117 / #162 | #173–178 | #312–314 | #25 F / #22 / #24 | #18, #21 |

В каждом positive достигнуты mixed threshold, adjacent ties, q=0, q=255, q absent и useful return после всех вызовов сети. У обоих контролей тот же exact span и verified stub set, нулевой активный вход, q=1 и произвольные внешние байты. После полезного возврата `v[1] == 0` запись `v[1] = 255` меняет младший бит ожидаемой маски. Успешны capture и оба frame, достигнуты useful return и corruption path. Единственные `FAILURE` класса `assertion` следующие. [Контрольный макрос и invocations](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:2079)

| Root | Полный property ID | Description | Native Location |
| --- | --- | --- | --- |
| N20 control, #263 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n20_actual_insert_corrupt.assertion.9` | `COMPACT_N20_ACT_INSERT_CORRUPT_QPOST` | H:2123:1, раскрытие макроса |
| N25 control, #25 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n25_actual_insert_corrupt.assertion.9` | `COMPACT_N25_ACT_INSERT_CORRUPT_QPOST` | H:2127:1, раскрытие макроса |

### Развёртка и достижимость

Все **32 напечатанные unwind checks** имеют `SUCCESS`: по четыре DFCC unwind goals у восьми Check. У пяти consumers/control включены unwinding assertions, но отдельных unwind goals в `RESULTS` нет. В их regular stdout подтверждены unwind traces actual loops, без `Not unwinding`, с максимальными номерами итераций 20 для N20, 24 для N24 и 25 для N25. Source даёт два региона, не более трёх вставок в регионе, не более 11 шагов sift и не более 34 байтов на обход fixture. Полезный возврат достигается после fixed presort/insert/merge/copy route. Эти данные вместе с успешными terminal goals закрывают grouped Pre, helper safety/DFCC и copy-back для каждого обязательного исполнения. CBMC проверяет конъюнкцию экземпляров с общим property ID. [CBMC unwind decision](/root/cbmc-pr9487-slop-readonly-20261119/src/goto-checker/symex_bmc.cpp:127) · [Grouped-property правило](GROUPED-PROPERTY-DECISION.md#правило-допуска)

`UNREACHABLE` сохранены со своими native ID и coordinates. Во всех восьми roots с merge ролью (три Check и пять consumers/control) четыре U арифметики относятся к отдельному символу Original `bidirectional_merge`. Exact route выбирает Check wrapper у провайдера и Replace у вызывающего root. У Check арифметика исполняемого wrapper имеет `SUCCESS`. Остальные U приходятся на core helpers: `is_valid_allocation_size` делит только при size≠0 (`ub_checks.rs:147–149`), `usize::abs_diff` вычитает по ветке порядка (`uint_macros.rs:3215–3225`), `is_aligned_to` вычисляет align−1 после проверки power-of-two (`const_ptr.rs:1474–1479`). У consumers/control дополнительно `is_multiple_of` вычисляет остаток только при rhs≠0 (`uint_macros.rs:3913–3917`). U в `fmt::Arguments::from_str` относится к сдвигу на константу 1 при упаковке длины статического сообщения (`fmt/mod.rs:815–821`). Regular location общих helpers фиксирует декларацию, а точные стеки всех их вызовов в данном inventory недоступны. Обязательные свойства выбранных маршрутов опираются на указанные выше положительные статусы и fixed source path.

Для закрытия N24 нужен terminal regular/export и PGID замер exact control 21A с теми же geometry, width, cfg и verified stub set. Сверка должна подтвердить единственный отказ `COMPACT_N24_ACT_INSERT_CORRUPT_QPOST` с точным native ID/class/location, два достигнутых covers, q/outside frame и отсутствие иных failures. Запись устанавливает офлайн-допуск bounded-результатов N20 и N25. Исторический `proof_credit=NONE` и receipts сохранены. B1/B2 credit и dispatch вне области этой записи.
