# Офлайн-квалификация и допуск N26–N31

**N26, N27, N28, N29, N30 и N31 функционально квалифицированы и допущены как bounded-результаты.** Для обоих Check `sort13_optimal` каждой цепочки действует серийная полоса 8 GiB на корень. Consumer, merge Check и matched control каждой длины проходят в обычной полосе 6 GiB. Для N27 правый Check из 21C закрывает зависимость, оставшуюся после отсечения по RSS в 20. Все обязательные корни для шести длин найдены. [Решение владельца](OWNER-DECISION-SORT13-8GIB.md#расширение-2026-11-21) · [Правило grouped properties](GROUPED-PROPERTY-DECISION.md#правило-допуска) · [Прецедент N21–N24](ADMISSION-N21-N24.md)

## Строки допуска

Область охватывает actual `small_sort_network` для exact длин, `u8/KeyLess<u8>`, initialized V34, base1, произвольные входные байты и независимый q по всем `u8`, `merge_wide`, normal fork OFF, OB11 и unwind36. На нормальном возврате проверены полная q/order-stat маска по snapshot до сети, q-frame и побайтовый frame за пределами активного среза. Scratch выделяется отдельно как `MaybeUninit<[u8; 32]>` с base+0. Интервалы полуоткрытые. Относительные индексы вставок включают обе границы.

| Длина и exact consumer | Presort Check и actual вставки | Whole merge Check и copy-back | Matched control | Максимум цепочки, KiB | Решение |
| --- | --- | --- | --- | ---: | --- |
| **N26**, `COMPACT-N26-ACT-INSERT-OB11` (21B), `v[1..27)` | `NM-S13-L13` (17A), `v[1..14)`, ∅ · `MW-S13-R-B14-L13-OB11` (21C), `v[14..27)`, ∅ | `MW-MERGE-N26-OB11` (21B), 13+13, scratch `[0..13) + [13..26)`, copy-back 26 байтов | `COMPACT-N26-ACT-INSERT-CORRUPT-OB11` (21B) | **7 709 744** · `NM-S13-L13` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 678 864 KiB. |
| **N27**, `COMPACT-N27-ACT-INSERT-OB11` (20), `v[1..28)` | `NM-S13-L13` (17A), `v[1..14)`, ∅ · `MW-S13-R-B14-L14-OB11` (21C), `v[14..28)`, rel13 | `MW-MERGE-N27-OB11` (20), 13+14, scratch `[0..13) + {13} + [14..27)`, copy-back 27 байтов | `COMPACT-N27-ACT-INSERT-CORRUPT-OB11` (21A) | **7 709 744** · `NM-S13-L13` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 678 864 KiB. |
| **N28**, `COMPACT-N28-ACT-INSERT-OB11` (21B), `v[1..29)` | `NM-S13-L14` (17A), `v[1..15)`, rel13 · `MW-S13-R-B15-L14-OB11` (21C), `v[15..29)`, rel13 | `MW-MERGE-N28-OB11` (21B), 14+14, scratch `[0..14) + [14..28)`, copy-back 28 байтов | `COMPACT-N28-ACT-INSERT-CORRUPT-OB11` (21B) | **7 708 696** · `NM-S13-L14` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 679 912 KiB. |
| **N29**, `COMPACT-N29-ACT-INSERT-OB11` (21B), `v[1..30)` | `NM-S13-L14` (17A), `v[1..15)`, rel13 · `MW-S13-R-B15-L15-OB11` (21C), `v[15..30)`, rel13–14 | `MW-MERGE-N29-OB11` (21B), 14+15, scratch `[0..14) + {14} + [15..29)`, copy-back 29 байтов | `COMPACT-N29-ACT-INSERT-CORRUPT-OB11` (21B) | **7 708 696** · `NM-S13-L14` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 679 912 KiB. |
| **N30**, `COMPACT-N30-ACT-INSERT-OB11` (21B), `v[1..31)` | `NM-S13-L15` (17A), `v[1..16)`, rel13–14 · `MW-S13-R-B16-L15-OB11` (21C), `v[16..31)`, rel13–14 | `MW-MERGE-N30-OB11` (21B), 15+15, scratch `[0..15) + [15..30)`, copy-back 30 байтов | `COMPACT-N30-ACT-INSERT-CORRUPT-OB11` (21B) | **7 709 832** · `NM-S13-L15` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 678 776 KiB. |
| **N31**, `COMPACT-N31-ACT-INSERT-OB11` (21B), `v[1..32)` | `NM-S13-L15` (17A), `v[1..16)`, rel13–14 · `MW-S13-R-B16-L16-OB11` (21C), `v[16..32)`, rel13–15 | `MW-MERGE-N31-OB11` (21B), 15+16, scratch `[0..15) + {15} + [16..31)`, copy-back 31 байт | `COMPACT-N31-ACT-INSERT-CORRUPT-OB11` (21B) | **7 709 832** · `NM-S13-L15` | Допущен. 8 GiB для sort13 Check, 6 GiB для остальных. Запас максимума 678 776 KiB. |

Максимум цепочки берётся по пяти обязательным корням, включая matched control. Измерение — sampled child PGID VmRSS с шагом 50 мс. Для правых Check установлен nominal/effective cap 8/8 GiB (8 388 608 KiB). Левые Check 17A выполнены под 10/10 GiB, их допуск в 8 GiB основан на измеренном fit. Корни 20/21A/21B завершились под 6/6 GiB (6 291 456 KiB). Максимум обычной полосы у каждой длины даёт её merge Check. В порядке N26–N31 пики составляют 4 702 544, 4 863 100, 5 048 264, 5 202 476, 5 316 272 и 5 527 296 KiB. Минимальный запас в этой полосе 764 160 KiB у N31. [Решение о серийной полосе](OWNER-DECISION-SORT13-8GIB.md)

## Идентичность и inventory

Входной g0 `f7d10a67d34efc2a0dd1c8a2a5dddc0ff85392f3`. Артефакты `Tiramisu-Cake/kani`, attempt 1. Общий tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, Kani 0.68.0, CBMC 6.11.0, CaDiCaL, `x86_64-unknown-linux-gnu`. Exact invocation использует `--exact --jobs=1 --no-assert-contracts`, regular + JSON export, включённые memory/bounds/overflow/unwind/undefined-function/reachability checks и пустые ordinary stubs.

| Кампания · run | Std commit / tree | Control candidate → trigger / tree |
| --- | --- | --- |
| 17A · 44896810040 | `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` / `a41b4c4822ab9df70db698ce576b3112a670ba80` | `cb81adc41d7bce501d8a93c4e90bb236a27b550f` → `22a6422e6d6a24779fa2b76c1443f5ce17ccb843` / `647b4bf6a9c749e5983159181216565467de46a4` |
| 20 · 44913550779 | `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` / `3cc0e5aa1a8d5100c2812bef424291af9f83f630` | `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` → `97f552174eb15a06f726da390cfa7fbe5d981302` / `aba7ec3689b53644c105a138283f2efd7db4fcb6` |
| 21A · 44919576152 | `e2bd3c6adc870729794a6b2fe44eece988402d8f` / `7e62553ab80d6178ce8f01c8212e084b2186e308` | `2fa3734008c1e5e3e46cd7f72f8bbc891ae99080` → `2ffd91183ebd4cb6c2f1adc96a5de5ff622c7f20` / `3174f86fd3aa6b30a4a70158156f955f8f54267f` |
| 21B · 44919643424 | `e2bd3c6adc870729794a6b2fe44eece988402d8f` / `7e62553ab80d6178ce8f01c8212e084b2186e308` | `d62b75ddd9cbc4e4fa5366f1ae225833d71f52f3` → `74e03c59559f07006d276e297b3c4193837f4bdb` / `324123d4ea2c0c961b3bab36987de147913ade90` |
| 21C · 44923999242 | `e2bd3c6adc870729794a6b2fe44eece988402d8f` / `7e62553ab80d6178ce8f01c8212e084b2186e308` | `5eef2b48617a8f2583fb5e587af0e071b9288366` → `86bd362993cd0020ec0312e86fda3be8ab1d53e7` / `83bf55935e34a1a86b7ce02f52be0be79e1e315e` |

Control parent всех пяти кампаний `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. SHA-256 индексов и frozen requests сверены с закоммиченными индексами и Git blobs trigger соответственно. Полные digests приведены для каждого корня в inventory. [Индекс 17A](run-44896810040/raw/ch8-q-pilot-44896810040-1/q-pilot-raw.json) · [Индекс 20](run-44913550779/raw/ch8-q-pilot-44913550779-1/q-pilot-raw.json) · [Индекс 21A](run-44919576152/raw/ch8-q-pilot-44919576152-1/q-pilot-raw.json) · [Индекс 21B](run-44919643424/raw/ch8-q-pilot-44919643424-1/q-pilot-raw.json) · [Индекс 21C](run-44923999242/raw/ch8-q-pilot-44923999242-1/q-pilot-raw.json)

Для 27 exact roots сверены Git trees, pinned file hashes, frozen requests, roster, selector, invocation ID, argv, RUSTFLAGS, resolved mode и verified stubs. Размеры и SHA-256 всех 81 stdout/stderr/export совпали с индексами и Git blobs входного g0. Проверены snapshot after reap, отсутствие truncation и timeout, исходный child exit, cleanup/containment, привязка PID/PGID и серийное выполнение. Regular содержит непрерывные ordinals, полные `RESULTS` / `SUMMARY` и terminal verdict. Export совпадает по exact harness, итогу, числам и статусам, ID доступных buckets, классу и location отказов.

Применён extractor `native-inventory/1` с SHA-256 `2588eec19879eb774232a195e1b91bf920da310bc5806465db2371525595c255`. Синтетические проверки формата прошли. Три root manifests 17A и их свойства совпали с прежним inventory с учётом provenance входного g0. Дополнение содержит **24 root manifests и 17 232 свойства** (16 896 S, 6 F, 204 U и 126 covers), SHA-256 `6a24198d11aba23aeb4dc67c8e00c134b9319304792992aed20094a0daeddaf8`. По всем 27 корням сверены 19 098 свойств (18 726 S, 6 F, 219 U и 147 covers). Все 129 unsupported checks имеют `SUCCESS`. Коллизий display ID и дубликатов нет. [Дополнение inventory](NATIVE-INVENTORY-N26-N31.jsonl) · [Прежний inventory 17A](NATIVE-INVENTORY-N13-N20.jsonl#L13998)

S/F/U — `SUCCESS` / `FAILURE` / `UNREACHABLE`. Все covers имеют `SATISFIED`.

| Кампания | Exact root | S/F/U | Covers | Child PGID | RSS, KiB | Cap nom./eff., GiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 17A | [NM-S13-L13](NATIVE-INVENTORY-N13-N20.jsonl#L13998) | 610/0/5 | 7 | 10962 | 7 709 744 | 10/10 |
| 17A | [NM-S13-L14](NATIVE-INVENTORY-N13-N20.jsonl#L14621) | 610/0/5 | 7 | 11457 | 7 708 696 | 10/10 |
| 17A | [NM-S13-L15](NATIVE-INVENTORY-N13-N20.jsonl#L15244) | 610/0/5 | 7 | 12000 | 7 709 832 | 10/10 |
| 20 | [MW-MERGE-N27-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L1) | 685/0/9 | 6 | 12840 | 4 863 100 | 6/6 |
| 20 | [COMPACT-N27-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L702) | 755/0/10 | 6 | 13306 | 2 918 380 | 6/6 |
| 21A | [COMPACT-N27-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L1474) | 766/1/10 | 2 | 15674 | 2 580 388 | 6/6 |
| 21B | [MW-MERGE-N26-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L2254) | 685/0/9 | 6 | 9221 | 4 702 544 | 6/6 |
| 21B | [COMPACT-N26-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L2955) | 755/0/10 | 6 | 9703 | 2 841 328 | 6/6 |
| 21B | [COMPACT-N26-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L3727) | 766/1/10 | 2 | 10145 | 2 734 068 | 6/6 |
| 21B | [MW-MERGE-N28-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L4507) | 685/0/9 | 6 | 10586 | 5 048 264 | 6/6 |
| 21B | [COMPACT-N28-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L5208) | 755/0/10 | 6 | 11058 | 3 188 096 | 6/6 |
| 21B | [COMPACT-N28-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L5980) | 766/1/10 | 2 | 11500 | 2 550 268 | 6/6 |
| 21B | [MW-MERGE-N29-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L6760) | 685/0/9 | 6 | 11943 | 5 202 476 | 6/6 |
| 21B | [COMPACT-N29-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L7461) | 755/0/10 | 6 | 12411 | 3 370 396 | 6/6 |
| 21B | [COMPACT-N29-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L8233) | 766/1/10 | 2 | 12856 | 2 629 488 | 6/6 |
| 21B | [MW-MERGE-N30-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L9013) | 685/0/9 | 6 | 13298 | 5 316 272 | 6/6 |
| 21B | [COMPACT-N30-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L9714) | 755/0/10 | 6 | 13830 | 3 566 156 | 6/6 |
| 21B | [COMPACT-N30-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L10486) | 766/1/10 | 2 | 14275 | 2 623 644 | 6/6 |
| 21B | [MW-MERGE-N31-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L11266) | 685/0/9 | 6 | 14717 | 5 527 296 | 6/6 |
| 21B | [COMPACT-N31-ACT-INSERT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L11967) | 755/0/10 | 6 | 15179 | 3 720 748 | 6/6 |
| 21B | [COMPACT-N31-ACT-INSERT-CORRUPT-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L12739) | 766/1/10 | 2 | 15623 | 3 065 852 | 6/6 |
| 21C | [MW-S13-R-B14-L13-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L13519) | 610/0/5 | 7 | 9125 | 7 635 752 | 8/8 |
| 21C | [MW-S13-R-B14-L14-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L14142) | 610/0/5 | 7 | 9697 | 7 649 492 | 8/8 |
| 21C | [MW-S13-R-B15-L14-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L14765) | 610/0/5 | 7 | 10283 | 7 635 016 | 8/8 |
| 21C | [MW-S13-R-B15-L15-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L15388) | 610/0/5 | 7 | 10794 | 7 636 380 | 8/8 |
| 21C | [MW-S13-R-B16-L15-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L16011) | 610/0/5 | 7 | 11388 | 7 638 084 | 8/8 |
| 21C | [MW-S13-R-B16-L16-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L16634) | 610/0/5 | 7 | 11895 | 7 648 532 | 8/8 |

## Source и Check → Replace

S — `library/core/src/slice/sort/shared/smallsort.rs`, H — `smallsort/verify/sorting_q_merge.rs`, M — `smallsort/verify/sorting_q_merge_model.rs` относительно `sort/shared/`. Координаты даны по Std 21, если явно не указан другой pin. `#n` — native `Check n` внутри exact root. Полные IDs, class и location приведены в inventory.

- **Перенос 17A → 20/21.** Тела S и компаратор сохранились. Для левых длин 13, 14 и 15 развёрнутый predicate `presort_readable` даёт одинаковые условия в `no_merge_sort13` (13–17) и `merge_wide` (13–16). Обе конфигурации активируют один и тот же wide-контракт S:609–631, включая `presort_geometry`, writable prefix 13, тонкий `modifies`, `old` и numeric/q post. Новые ветви в M:510–519 и M:533–551 требуют `q_compact_presort13`, выключенный в обеих конфигурациях. 17A fixture вызывает Check на base1 с литеральными концами 14/15/16, frame ограничен `v[1..14)` (H:1683–1694, 1759–1764 по 17A). Перенос применяется к левым Check точных геометрий. [Исходная квалификация 17A](ADMISSION-N13-N19-FINAL.md#native-роли-и-контроли) · [Пины и сверка профилей](PILOT21-IMPL-HANDOFF.md#зависимости-и-границы-допуска)
- **Перенос 20 → 21 для N27.** Std 21 добавляет строки только в H. Сохранены whole merge N27, правый Check b14/14, общий positive macro и exact positive N27. Consumer из 20 и контроль из 21A вызывают actual сеть на `v[1..28)` с одинаковыми `u8/KeyLess<u8>`, cfg, OB11, unwind36 и verified stubs `sort13_optimal` / `bidirectional_merge`. Отдельный merge Check в 20 использует тот же source span и scratch32+0 (H:1586–1601 по 20). Правый Check брался из завершившегося 21C на тех же active clauses. [Кампания 20](run-44913550779/SUMMARY.md) · [Кампания 21C](run-44923999242/SUMMARY.md)
- **Presort.** S:339–381 задаёт две половины, слева `floor(N/2)`, справа остаток. Обе длины ≥13, поэтому на каждой половине выполняется один sort13 Replace. Check проверяет 45 actual `swap_if_less` (S:632–693), numeric order и число байтов ниже прежнего q на первых 13 байтах. Fixture проверяет неизменность q и всех V34 байтов вне write prefix, включая хвост самой половины. Левый prefix `v[1..14)`, правый `v[b..b+13)`. Правые fixture anchors для N26–N31 идут по H:1426, 1342, 1436, 1446, 1456, 1466. Общий frame и useful-return cover следуют за Check. [Прецедент thin modifies и frame](ADMISSION-N21-N24.md#source-и-check--replace)
- **Actual вставки.** В каждой половине S:370 передаёт offset 13 в original `insertion_sort_shift_left`. Для длины 13 `tail == v_end` при первой проверке S:884–890. Поэтому в N26 происходят два вызова драйвера и ноль вызовов `insert_tail`, у N27 вставка есть только справа. В остальных полупроходах literal route задаёт ровно rel из таблицы. При каждом rel=r original `insert_tail` (S:826–860) выполняет ранний возврат либо сдвиг в `v[b..b+r+1)` с закрытием gap через `CopyOnDrop` (S:323–328). Numeric merge Pre проверяет обе полные половины после проходов.
- **Whole merge.** Consumer Replace после вставок проверяет все шесть merge Pre (S:1194–1200, 1226–1248, M:562–591). Отдельный exact merge Check (H:1754–1770 и инстанциации H:1781–1789 для 21B) выполняет actual Up/Down (S:1306–1309). У N27/N29/N31 константная чётность ведёт к одному actual odd copy (S:1315–1320). У N26/N28/N30 два потока заполняют весь span. После потоков и odd slot проверяется cursor guard (S:1326–1327). `modifies` задаёт активные N байтов назначения. `old(merge_capture)` захватывает initialized source и q до havoc, post проверяет весь активный scratch при неизменном q, fixture проверяет q и весь source V34. Затем actual `copy_nonoverlapping` в consumer на S:390 переносит N байтов в `v[1..1+N)`. Итоговая проверка использует исходный snapshot (H:2209, 2233–2249).
- **Сверка с N21–N24.** `NATIVE-INVENTORY-N21-N24.jsonl` и соответствующий допуск дают тот же whole-merge ID, состав шести caller Pre, copy-back preconditions и q/frame роли positive/control. Для N26–N31 привязка сделана заново к своим roots и ordinals, с presort ID `sort13_optimal` и offset 13. [Inventory N21–N24](NATIVE-INVENTORY-N21-N24.jsonl#L2493) · [Native-роли N21–N24](ADMISSION-N21-N24.md#native-роли-consumers-и-контролей)

### Native-роли Check

Presort post — `sort13_optimal::<…>::{closure#2}.assertion.1` (S:609). Merge post — `bidirectional_merge::<…>::{closure#2}.assertion.1` (S:1226). DFCC — `memcpy.assigns.1–2` и для presort также `memmove.assigns.1–2`. Frame означает q и V34 вне presort prefix либо q и весь source V34 у merge.

| Exact Check | Ensures | DFCC memcpy / memmove | q / byte frame | Useful return | Cursor guard |
| --- | --- | --- | --- | --- | --- |
| [NM-S13-L13](NATIVE-INVENTORY-N13-N20.jsonl#L13998) | #188 | #117–118 / #31–32 | #97 / #98 | #105 | — |
| [NM-S13-L14](NATIVE-INVENTORY-N13-N20.jsonl#L14621) | #183 | #33–34 / #21–22 | #11 / #12 | #19 | — |
| [NM-S13-L15](NATIVE-INVENTORY-N13-N20.jsonl#L15244) | #177 | #51–52 / #47–48 | #136 / #137 | #144 | — |
| [MW-MERGE-N27-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L1) | #230 | #50–51 | #145 / #146 | #147 odd | #245 |
| [MW-MERGE-N26-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L2254) | #151 | #89–90 | #145 / #146 | #147 | #250 |
| [MW-MERGE-N28-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L4507) | #128 | #7–8 | #131 / #132 | #133 | #83 |
| [MW-MERGE-N29-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L6760) | #171 | #19–20 | #25 / #26 | #27 odd | #238 |
| [MW-MERGE-N30-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L9013) | #187 | #99–100 | #131 / #132 | #133 | #104 |
| [MW-MERGE-N31-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L11266) | #12 | #78–79 | #150 / #151 | #152 odd | #76 |
| [MW-S13-R-B14-L13-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L13519) | #183 | #63–64 / #46–47 | #136 / #137 | #144 | — |
| [MW-S13-R-B14-L14-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L14142) | #5 | #26–27 / #34–35 | #157 / #158 | #165 | — |
| [MW-S13-R-B15-L14-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L14765) | #183 | #72–73 / #76–77 | #40 / #41 | #48 | — |
| [MW-S13-R-B15-L15-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L15388) | #186 | #64–65 / #72–73 | #77 / #78 | #85 | — |
| [MW-S13-R-B16-L15-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L16011) | #173 | #48–49 / #24–25 | #73 / #74 | #81 | — |
| [MW-S13-R-B16-L16-OB11](NATIVE-INVENTORY-N26-N31.jsonl#L16634) | #181 | #54–55 / #35–36 | #198 / #199 | #206 | — |

У всех presort Check по семь covers для mixed threshold, ties, q=0, q=255, q absent, input inversion и полезного возврата. У всех merge Check по шесть covers для split q, cross-half tie, q=0, q=255, q absent и полезного возврата. Для N27/N29/N31 useful-return cover достигается после odd write. В Check wrapper для всех трёх нечётных длин проходит свойство сравнения указателей #362 на S:1316. Группа `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3` (#260–262) имеет `SUCCESS` и включает disjoint, readable и writable для actual odd write. Actual Up/Down проходят grouped DFCC и safety на обоих потоках записи.

### Native-роли consumers и контролей

Presort Pre — `sort13_optimal::<…>::{closure#1}.assertion.1` (S:624), общий для обеих половин. Merge Pre — `bidirectional_merge::<…>::{closure#1}.assertion.1–6` в порядке numeric, geometry, disjoint, writable, readable, len. Insert safety — `insert_tail::<…>.safety_check.1–6` (S:831/856), offset guard — `insertion_sort_shift_left::<…>.assertion.1` (S:875). Copy Pre — `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3`, в том числе для copy-back S:390. Все Pre, safety, guard и frame в таблице имеют `SUCCESS`.

| Root | Presort Pre | Insert safety / offset guard | Merge Pre | Copy Pre | q-post / q-frame / outside | Covers |
| --- | --- | --- | --- | --- | --- | --- |
| N26 positive | #266 | ∅ / #208 | #229–234 | #299–301 | #103 / #104 / #106 | #107–112 |
| N26 control | #260 | ∅ / #250 | #126–131 | #299–301 | #40 F / #37 / #39 | #33, #36 |
| N27 positive | #262 | #218–223 / #246 | #179–184 | #299–301 | #21 / #22 / #24 | #25–30 |
| N27 control | #256 | #184–189 / #165 | #155–160 | #299–301 | #252 F / #249 / #251 | #245, #248 |
| N28 positive | #270 | #102–107 / #69 | #205–210 | #299–301 | #47 / #48 / #50 | #51–56 |
| N28 control | #255 | #121–126 / #131 | #170–175 | #299–301 | #221 F / #218 / #220 | #214, #217 |
| N29 positive | #251 | #127–132 / #224 | #60–65 | #299–301 | #29 / #30 / #32 | #33–38 |
| N29 control | #265 | #80–85 / #197 | #165–170 | #299–301 | #128 F / #125 / #127 | #121, #124 |
| N30 positive | #234 | #128–133 / #218 | #151–156 | #299–301 | #275 / #276 / #278 | #279–284 |
| N30 control | #259 | #139–144 / #233 | #221–226 | #299–301 | #114 F / #111 / #113 | #107, #110 |
| N31 positive | #264 | #276–281 / #255 | #7–12 | #299–301 | #234 / #235 / #237 | #238–243 |
| N31 control | #265 | #253–258 / #274 | #4–9 | #299–301 | #209 F / #206 / #208 | #202, #205 |

Для N26 напечатанные свойства `insert_tail` (#139–144 positive и #241–246 control) имеют `SUCCESS`. Два пустых цикла при offset 13 установлены по exact source и подтверждаются regular trace, где нет развёртки `insert_tail` или цикла insertion driver. Эти ordinals сохраняются в inventory как свойства символа.

Каждый positive достигает mixed threshold, adjacent ties, q=0, q=255, q absent и useful return после всей сети. Каждый matched control оставляет внешние байты произвольными, обнуляет активный срез и задаёт q=1. После useful-return cover `v[1] == 0` выполняется `v[1] = 255`. Это меняет младший бит наблюдаемой маски и достигает corruption cover. Capture и оба frame имеют `SUCCESS`. Единственная terminal `FAILURE` у каждого контрола относится к native классу `assertion`.

| Root | Полный property ID | Description | Native Location | Capture |
| --- | --- | --- | --- | --- |
| N26 control #40 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n26_actual_insert_corrupt.assertion.9` | `COMPACT_N26_ACT_INSERT_CORRUPT_QPOST` | H:2355:1 | #31 |
| N27 control #252 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n27_actual_insert_corrupt.assertion.9` | `COMPACT_N27_ACT_INSERT_CORRUPT_QPOST` | H:2359:1 | #243 |
| N28 control #221 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n28_actual_insert_corrupt.assertion.9` | `COMPACT_N28_ACT_INSERT_CORRUPT_QPOST` | H:2363:1 | #212 |
| N29 control #128 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n29_actual_insert_corrupt.assertion.9` | `COMPACT_N29_ACT_INSERT_CORRUPT_QPOST` | H:2367:1 | #119 |
| N30 control #114 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n30_actual_insert_corrupt.assertion.9` | `COMPACT_N30_ACT_INSERT_CORRUPT_QPOST` | H:2371:1 | #105 |
| N31 control #209 | `slice::sort::shared::smallsort::verify::sorting_q_merge::compact_network_n31_actual_insert_corrupt.assertion.9` | `COMPACT_N31_ACT_INSERT_CORRUPT_QPOST` | H:2375:1 | #200 |

### Развёртка и достижимость

Все **60 напечатанных unwind checks** имеют `SUCCESS`, по четыре у каждого из 15 Check. У 12 consumers/control unwinding assertions включены и отдельных unwind goals в `RESULTS` нет. Regular traces показывают развёртку двух регионов, actual inserts для N27–N31 и проходов fixtures. Максимальные напечатанные номера итераций для N26–N31 соответственно 26/27/28/29/30/31. В regular traces этих 12 корней отсутствуют сообщения `Not unwinding`. Source bound охватывает до трёх вставок на половину, sift до rel15 и обходы V34. Фиксированный маршрут и достигнутый useful-return cover связывают нужные исполнения с Check или Replace. Успех общего ID закрывает конъюнкцию его экземпляров на достижимых путях. [Правило grouped properties](GROUPED-PROPERTY-DECISION.md#правило-допуска) · [Review семантики](GROUPED-PROPERTY-REVIEW.md)

Каждый merge-bearing root содержит четыре `UNREACHABLE` для арифметики в отдельном Original-символе `bidirectional_merge` на S:1286, 1302, 1303, 1304. Provider исполняет Check wrapper, в котором соответствующие arithmetic/pointer checks имеют `SUCCESS`. Consumer/control вызывают Replace. Остальные U относятся к guard-ветвям core helpers, уже описанным для N21–N24: allocation-size divide, две ветви `abs_diff`, `is_aligned_to`, static-message `fmt::Arguments::from_str`, а у consumers/control также `is_multiple_of`. Native статусы и source locations сохранены в inventory. [Разбор U в прецеденте](ADMISSION-N21-N24.md#развёртка-и-достижимость)

Запись устанавливает офлайн-допуск bounded-результатов для указанных шести exact длин. Исторические receipts сохраняют `proof_credit=NONE`. Независимый B1/B2 proof credit и dispatch находятся вне области этой записи.
