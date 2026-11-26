# REV2 · сквозные проверки N22–N25 с контролями

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`

Пакет готов к независимому ревью. Четыре positive и четыре различающих контроля заморожены в одном Ubuntu job. Нативные compile preflight, discovery и измерения consumer остаются открыты до отдельного GO. Основание переноса на полные байты изложено ниже. Наблюдения по опорам относятся к их собственным запускам. [Задание](REV2-N22-N25-CONSUMER-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md) · [Результаты FIX1](REV2-N22-N25-PROVIDERS-RESULTS-ANALYSIS.md)

Актуальный кандидат и результаты повторных проверок приведены в разделе [FIX1](#fix1). Ревью R1 признало содержание пакета корректным и остановило допуск из-за авторства трёх коммитов. [Ревью R1](REV2-N22-N25-CONSUMER-REVIEW.md) · [Задание FIX1](REV2-N22-N25-CONSUMER-FIX1-TASK.md)

## Пины R1

Исторические пины первого кандидата. Ссылки на worktrees ведут к текущему FIX1.

| Роль и worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Std, `work/rev2-n22-n25-consumer-w14` | `2f73485a5d6115b1611b68f9e814fde6c9669f93` | `f754c01d0ed26cb8d4e28c81efe8467cdf97d034` | `b076d2ff4ed720930e2de62d70c0bbd1bb0308d5` |
| Control, `work/rev2-n22-n25-consumer-control-w14` | `e3dcce70bedf47755df650c8f4458864fde9e9cb` | `a5aab1d9c4f10794dcf8eb6e5d92926cac1ed850` | `279c2200a8ecab1ee0e9057c86d771ff6e6c963e` |
| Локальный detached review-trigger, ref `review/rev2-n22-n25-consumer-trigger-w14` | `1e5b5b397cf882b9fb067ecb17c45ce1bd530988` | `a5aab1d9c4f10794dcf8eb6e5d92926cac1ed850` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

[Std](/root/verify-rust-std-rev2-n22-n25-consumer-w14) · [Control](/root/kani-rev2-n22-n25-consumer-control-w14) · [Review-trigger](/root/kani-rev2-n22-n25-consumer-trigger-w14/control) · [Workflow](/root/kani-rev2-n22-n25-consumer-trigger-w14/control/.github/workflows/ch8-q-pilot.yml)

Задание прочитано на g0 `f4aebba4e6b8f6bf1edf7d8d21d17eb2c03c8f0b`. На входе g0 был `ea438b437aea5ac9e5ad194d6109a2c82758d5d0` с поправкой единицы RSS в ledger. Пакет основан на Std FIX1 tree `33cd29a7756b24febf399932f86d8d09892653f7` и Control FIX1 tree `ac6176ac55522c8a78d9cd9418077fe8bd62a391`. Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`. [Пины FIX1](REV2-N22-N25-PROVIDERS-HANDOFF.md#fix1)

| Замороженный вход | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `05bd0697a8113d0f72a323b4ec411149dab7ceefbcf72faff3dfb8cbb65128b7` |
| Roster, canonical JSON с сортировкой ключей и разделителями `(",", ":")` | `ccc8db596f3e9b61299057b4c23f9747af4dc85d62b70456e1bfcaf30ad76bf6` |
| `std-overlay.bundle`, 45 627 байт, только HEAD с prerequisite Std CI-base | `44440bc5a6734404eb04a0341dac42eef4d61e262222a0a3a68b01291842c305` |
| Source bindings, canonical JSON | `6fb605dd5ad65f9e61a67b21e82e6aaa90cd762fccf47f54f1e94ad9f92bbb4b` |

[Frozen request](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/CI-REQUEST.json) · [Bundle](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/std-overlay.bundle)

В R1 независимый pin `CH8_REV2_N22_N25_CONSUMER_TRIGGER_TREE=a5aab1d9c4f10794dcf8eb6e5d92926cac1ed850` передавался в runner как `REV2_N22_N25_CONSUMER_TRIGGER_TREE`. `pins`, `sources` и `finish` требуют clean detached checkout, точный tree, sole parent, репозиторий `Tiramisu-Cake/kani`, push `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и равенство HEAD, `GITHUB_SHA` и payload `after`. Последующие стадии сверяют trigger receipt. `sources` проверяет цепочку overlay и координаты. `finish` повторяет сверку пинов и координат при полном source receipt. [Trigger gates](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/run.py:731)

## Рёбра для полного байтового домена

Все целевые рёбра относятся к Std consumer FIX1. Вход на каждом N — actual `small_sort_network::<u8, KeyLess<u8>>` на инициализированном V34, активный `v[1..1+N]`, независимый `q: u8`. `KeyLess<u8>::call_mut` читает два значения, возвращает числовое `a < b` и сохраняет q. Обозначения S и D означают начало активного среза и начало отдельной scratch32. Итоговый пост на нормальном возврате — порядок по числовому значению, полное мультимножество активных байтов и frame `q, v[0], v[1+N..34]`.

| Файл | Blob на Std consumer | Actual координаты |
| --- | --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` | scratch `383:27`, split `385:5, 391:31, 416:27`, sort13/sort9 `396:13, 399:13`, insertion `405:9`, merge `424:9`, copy-back `425:9` |
| `cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` | comparator cover `28:9` и числовое сравнение `29:9` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` | grouped copy `587:14`, overlapping copy из swap `682:9` |
| `rev2_n22_n25_providers.rs` | `3d83992d8fda0a78cb8b388f54db81bc90e751a7` | опоры FIX1 ниже |
| `rev2_n22_n25_consumer.rs` | `2a27d0465485781ee462df9218b0fa990069462e` | actual call N25/N24/N23/N22 `73:5, 101:5, 123:5, 151:5` |

Первые три blobs совпадают с FIX1 и всеми тремя историческими Std-пинами в таблице опор. Исторические модули `rev2_provider_cost.rs`, `rev2_s13_geometries.rs`, `rev2_n18_n19_providers.rs` также сверены на своих пинах и на consumer. Их blobs соответственно `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de`, `c403b343270752fb03fc087a101b55d8dc20a7ab`, `9f5f22527656fd0b9b6afa879d7b8bb7574ff5c3`. [Actual сеть](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:374) · [Координаты и blobs в request](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/CI-REQUEST.json)

| N | Левая половина | Правая половина | Merge и copy-back |
| ---: | --- | --- | --- |
| 22 | `v[1..12]`. `S9-B01-L09-BITS` + `S13-SWAP-LEAF` на B01 с L09→L11. `INSERT-B01-L12-BYTES` с L12→L11, rel9–10. | `v[12..23]`. `S9-B12-L12-BITS` с L12→L11 + `S9-B12-SWAP`. `INSERT-B12-L12-BYTES` с L12→L11, rel9–10. | `N22-PAIR-FIXED`, 11 пар D[k]/D[21−k], затем 22 байта. |
| 23 | `v[1..12]`. Те же опоры и переносы на B01/L11, rel9–10. | `v[12..24]`. Exact `S9-B12-L12-BITS` + `S9-B12-SWAP`, exact `INSERT-B12-L12-BYTES`, rel9–11. | `N23-PAIR-FIXED`, 11 пар D[k]/D[22−k], `N23-ODD-CENTER` в D[11], затем 23 байта. |
| 24 | `v[1..13]`. `S9-B01-L09-BITS` + `S13-SWAP-LEAF` на B01 с L09→L12. Exact `INSERT-B01-L12-BYTES`, rel9–11. | `v[13..25]`. Exact `S9-B13-L12-BITS` + `S13-B13-L13-SWAP` на B13 с парами rel0–8. Exact `INSERT-B13-L12-BYTES`, rel9–11. | `N24-PAIR-FIXED`, 12 пар D[k]/D[23−k], затем 24 байта. |
| 25 | `v[1..13]`. Те же опоры и перенос на B01/L12, rel9–11. | `v[13..26]`. Exact `S13-B13-L13-BITS` + `S13-B13-L13-SWAP` для всех 45 пар. При offset 13 driver имеет `tail == v_end`. | `N25-PAIR-FIXED`, 12 пар D[k]/D[24−k], `N25-ODD-CENTER` в D[12], затем 25 байтов. |

### Presort и вставки

Actual split на `smallsort.rs:391:31/416:27` даёт живые непересекающиеся половины. Затем `396:13/399:13` выбирает S13/S9 по длине и `405:9` запускает driver на том же регионе. В исторических harnesses actual calls стоят в `rev2_n18_n19_providers.rs:55` для S9/B01, `rev2_provider_cost.rs:157` для B01 swap, `rev2_s13_geometries.rs:51/85` для S13/B13 и его swap. В FIX1 `rev2_n22_n25_providers.rs:23/58/89` закрепляют S9/B12, swap/B12 и S9/B13. Лист на `smallsort.rs:488:1` получает два различных адреса по своему base и проверенным относительным индексам. Он сохраняет остальной V34 и q и выставляет min/max. B01 и B13 Check используют `0 ≤ a < b < 13`, B12 Check использует `b < 9`. В S9 все 25 пар ограничены rel0–8. Guard `len >= 9`, base, порядок пар и живость обоих адресов сохраняются при same-base L09→L11/L12 и L12→L11. Хвост за rel8 в write set не входит. Для S13/B13 тот же вывод о pre/post относится к exact L13 с guard `len >= 13` и 45 парами rel0–12. [Расписание S9](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:538) · [Расписание S13](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:597)

Для каждого порога t отображение `P_t(x) = [x ≥ t]` переводит min/max в AND/OR. Поднимаем проверенный битовый пост вдоль того же расписания. Любое нарушение числового порядка дало бы инверсию на некотором пороге. Сохранённые количества единиц для всех t дают все кратности через разности соседних пороговых счётчиков. Границы берутся из длины префикса и максимального порога 255. Получаем числовой порядок, полные кратности префикса и сохранение исходного хвоста.

FIX1 byte driver calls на `rev2_n22_n25_providers.rs:823/859/895` предполагают порядок первых девяти байтов. Для exact L12 непосредственно применимы порядок полного среза, `C(q)=count(byte<q)`, q/frame и normal return. При фиксированном входе компаратор независим от q. Кратность b для b<255 равна `C(b+1)−C(b)`, а для 255 равна `L−C(255)`.

Для L11 дополнительно применяется индукция до своего end. Перед шагом rel=r обработанный `[0,r)` упорядочен и имеет исходные кратности, `[r,L)` содержит исходный хвост. На `smallsort.rs:706:9` при уже упорядоченной границе вставка сразу возвращается. Иначе `715:9` сохраняет tail в отдельный tmp. Копия на `722:13` переносит байт из соседнего initialized адреса в дыру, `725:13` защищает нижнюю границу, `731:13` останавливается у первого predecessor, не большего tmp. `CopyOnDrop` на `362:13` заполняет последнюю дыру из tmp. Чтения и записи ограничены `[0,r]`, источники и назначения каждой копии различны. Это сохраняет инвариант и frame снаружи региона. Actual driver `759:9–767:13` на L11 делает rel9 и rel10 и после продвижения достигает base+11. L12 делает ещё rel11. У N25 справа offset=13 даёт `tail == v_end == B13+13` уже до первого шага, поэтому число вызовов `insert_tail` равно нулю. На входе merge обе половины целиком численно упорядочены и сохраняют свои кратности. [Actual вставка](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:701) · [Driver](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:742)

### Ранги merge

Пусть `m=floor(N/2)`. Ранг — лексикографический `(byte, индекс в S после вставок)`. Перед итерацией k уже записаны ранги `[0,k)` в `D[0..k]` и `[N−k,N)` в `D[N−k..N]`. Пусть a,b — числа взятых снизу из левой и правой половин, c,d — числа взятых сверху. Тогда `a+b=c+d=k`. Actual инициализация на `1014:9–1020:9` устанавливает это при k=0. На `1023:34` up получает `(S+a,S+m+b,D+k)`, на `1024:46` down получает `(S+m−1−c,S+N−1−d,D+N−1−k)`. При `k<m` каждый счётчик ≤k, поэтому даже при исчерпании одной половины все четыре читаемых адреса ещё лежат внутри своих инициализированных половин. Scratch32 жива, writable, отделена от S, цели различны, так как `k<N−1−k<N`.

На непустой половине прямой и обратный курсоры указывают на крайние оставшиеся ранги. Если половина исчерпана, её прямой кандидат принадлежит уже выбранным верхним рангам, обратный — уже выбранным нижним. Действительно, при `k<m` исчерпание возможно лишь при положительном числе выборов с обеих сторон этой половины. Поэтому такой кандидат проигрывает сравнение за нужный экстремум. Up выбирает меньший ранг с tie-left. Down выбирает больший с tie-right. Это ровно правила `883:9` и `916:9` при равных байтах и индексах из разных половин. Перед парой осталось как минимум два различных ранга, поэтому выборы различны даже при совпадении значений и при одном живом байте в половине.

| N | FIX1 Check и actual up/down в wrapper | Selected `.assertion.7/.10` в `actual_pair_step_nN::{closure#2}::{closure#0}` | Точный write set |
| ---: | --- | --- | --- |
| 22 | `actual_pair_step_n22` · строки 141/149 | `143:9 / 151:9` | `D[k], D[21−k]`, (0 ≤ k < 11) |
| 23 | `actual_pair_step_n23` · 261/269 | `263:9 / 271:9` | `D[k], D[22−k]`, (0 ≤ k < 11) |
| 24 | `actual_pair_step_n24` · 488/496 | `490:9 / 498:9` | `D[k], D[23−k]`, (0 ≤ k < 12) |
| 25 | `actual_pair_step_n25` · 608/616 | `610:9 / 618:9` | `D[k], D[24−k]`, (0 ≤ k < 12) |

В каждой FIX1 projection сверены stock `ProofForContract` своего Check, selected cursor anchors, min/max, source/q frame, `memcpy.assigns.1/.2`, шесть grouped copy properties и covers. Нативная опора использует предпосылку числового порядка половин в harness. Индукция применяет тот же шаг к actual паре, сохраняет S, q и ранее записанные цели D. Это заполняет два следующих ранга и продвигает соответствующие курсоры. По окончании чётного merge `a+c=b+d=m`, оба прямых курсора равны границам `*_rev.wrapping_add(1)`. Записаны все N байтов D. [Actual цикл](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:1014) · [FIX1 Check](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n22_n25_providers.rs:126)

### Нечётный центр N23 и N25

После m пар `a+b=c+d=m`. Из общей длины `2m+1` и инварианта остатков следует `(m−a−c,m+1−b−d) ∈ {(1,0),(0,1)}`. Для левого остатка `(a,b,c,d)=(i,m−i,m−1−i,i+1)` при `0≤i<m`, и выбран `S+i`. Для правого `(i,m−i,m−i,i)` при `0≤i≤m`, и выбран `S+2m−i`. Канонические свидетели — исходно отсортированные половины с i нулями слева и соответственно m−i или m+1−i справа. В первом случае перед центром ровно m нулей, во втором в центре расположен последний из m+1 нулей. Tie-left и tie-right дают указанные счётчики.

Actual `smallsort.rs:1027:24–1036:13` получает обе границы через wrapping, выбирает `left` при `left<left_end` и `right` иначе, копирует единственный остаток в `D[m]` и продвигает выбранный курсор. Эта последовательность операций и адресов транскрибирована в FIX1 `actual_odd_center_n23` и `actual_odd_center_n25` с соответствующими константами. Selected source `SUCCESS` на `rev2_n22_n25_providers.rs:447:5/794:5`, оба равенства границ, write set только D[m], source/frame и grouped свойства подтверждены. Внешняя привязка подставляет курсоры из индукции. После однобайтового шага обе границы сходятся, проверка на `1042:9` проходит и merge возвращается.

| N | Левый остаток, i и источник | Правый остаток, i и источник | Sentinel positive |
| ---: | --- | --- | --- |
| 23, m=11 | `0..=10`, `S+i` → D[11] | `0..=11`, `S+22−i` → D[11] | `0x0000_07ff`, `(0,11,11,0)`, `S+22` |
| 25, m=12 | `0..=11`, `S+i` → D[12] | `0..=12`, `S+24−i` → D[12] | `0x0000_0fff`, `(0,12,12,0)`, `S+24` |

В обеих sentinel геометриях `c=m` и `left_rev=S−1` участвует только в `wrapping_add(1)` с результатом `left_end=S`. Левый прямой курсор равен S, поэтому выбрана последняя правая ячейка `S+N−1`. После copy `right=S+N` и `right_end=S+N`. На противоположных концах диапазонов i=0 и i=m−1 для левого остатка адрес остаётся в левой половине. При i=m для правого остатка адрес `S+m` есть начало правой половины, `left=left_end=S+m`, после copy `right=right_end=S+m+1`. [Actual ветка](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort.rs:1027) · [Прецедент N21](REV2-N20-N21-ADMISSION.md#нечётный-центр-n21)

### Copy-back и открытые обязательства

Последний actual вызов `ptr::copy_nonoverlapping(scratch_base, v_base, len)` стоит на `smallsort.rs:425:9` сразу после нормального возврата merge. `len=N` получен из активного среза на `374:5`, назначения writable, scratch32 отдельна от V34 и жива до копии. `size_of::<u8>()=align_of::<u8>()=1`, значит размер ровно N байтов и умножение не переполняется. Ранговая индукция и odd center устанавливают запись всей `D[0..N]` до чтения. Это внешний вывод об инициализации при uninit OFF. После copy та же последовательность рангов находится в `v[1..1+N]`, а записи merge и copy-back сохраняют `v[0]`, `v[1+N..34]` и q.

| Обязательство | Нативная часть и текущий статус | Внешняя привязка для ревью |
| --- | --- | --- |
| Presort и driver | 4 исторических и 6 FIX1 слотов presort/insert из таблицы ниже для соответствующих B/L и leaf scope. | Scope каждого листа, пороговый подъём, frame, exact L12 и индукция L11 по двум итерациям. |
| Actual merge и odd | 4 exact pair и 2 exact odd Check FIX1. | Ранговый инвариант, применение Check к каждому actual шагу, две odd ветки и sentinel в каждом N. |
| Последняя копия, N22/N23/N24/N25 | На каждом positive запрошены `SUCCESS` у `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14` для `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` и `SATISFIED` у своего `AFTER_COPY_BACK`. Статус consumer anchors **OPEN**, ожидают CI. | Grouped ID покрывает группу. Последняя копия привязана к straight-line actual call, exact N, раздельным областям, записи всех N байтов ранговым выводом и post-return cover. Те же размер, адресная геометрия и disjoint действуют на полном байтовом домене. |
| Числовой пост, чувствительность и frame всего вызова | 8 consumer projections и receipts, сопоставление regular/stock и своевременная аттестация **OPEN**. | Независимая проверка составного переноса, включая q и frame. Положительный битовый oracle и контроль каждой длины должны совпасть с замороженным ожиданием. |

[Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) · [Проверка anchors](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/results.py:247)

## Исторические и FIX1 опоры

Сверены четыре индекса структурированных результатов GitHub Actions и SHA-256/размеры 32 членов receipt/projection по индексам. Для всех 16 слотов подтверждены tool/solver/OB/unwind, exact selector и kind, `VERIFIED` exit 0, complete projection, sampler/reap и COMPLETE аттестация. Для 15 слотов проекции имеют `MATCHED` и полные mandatory anchors. Для раннего FIX3 `S13-SWAP-LEAF` доступен stock `COMPLETED/SUCCESS` с `ProofForContract(swap_if_less)`. Run 45813207026 имеет attempt 1, trigger `667a0d09b124734e8a68f6a614c248dc75d8db2a` с FIX1 Control tree и ожидаемым sole parent. `proof_credit=NONE` у всех четырёх индексов. [FIX1 GO](REV2-N22-N25-PROVIDERS-GO.md) · [Сверка FIX1](REV2-N22-N25-PROVIDERS-RESULTS-ANALYSIS.md#сверка-45813207026)

| Run | Std commit / tree | SHA-256 index |
| --- | --- | --- |
| 45661535099 | `32129c149a15fb1b60a7314e738f3cb466d076e5` / `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| 45688753097 | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` / `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| 45749463113 | `86ea7aa5b773888e52f9fb78fda38d5cbff9ea61` / `63b199cc33052d6390fd0fdaa2b5c36962545fc4` | `065a9d8c2738117b36101eb7f3dcb5c8e568506c79b90b7953d561ae49d39504` |
| 45813207026 | `b076d2ff4ed720930e2de62d70c0bbd1bb0308d5` / `33cd29a7756b24febf399932f86d8d09892653f7` | `8abc7333bab330acaf9ad6d11fbe6421e5af60357b7d31ffd5f86ab1246e08f1` |

| Слот и run | SHA-256 receipt | SHA-256 projection |
| --- | --- | --- |
| `S13-SWAP-LEAF` · 45661535099 | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S13-B13-L13-SWAP` · 45688753097 | `e936c63e821f880d80527a7ce22ed78842e100bb11f6d9178fda0f4501b8982a` | `17f8dda9bf3f7199f7142fadadfdd6d31aef7030f480f164a888d982999240b8` |
| `S13-B13-L13-BITS` · 45688753097 | `f672c1152444500e7e80d233dfc3401c2ea9eabd25bb5f9a54fd759163efcd94` | `9a888efb0e5c88aa685743bed8de273eeb2457b03e270af5a62a59a3f270eb2b` |
| `S9-B01-L09-BITS` · 45749463113 | `41e3435e50904c0cd683a7503a05d4428418557b3bfeddee95242d97c59551e3` | `46478975751c93569d9d1d0c681a9d623b2414db7129a1668e4ba05962649e48` |
| `S9-B12-L12-BITS` · 45813207026 | `58bb23852cb8c533b525b87a559c253af22a17890407018c19e7bd0360068ae9` | `3955ada4b9d665eee216996606cdb2d326b5e42f42633374b60fec697cc5bcd1` |
| `S9-B12-SWAP` · 45813207026 | `6a5abb83a372056e997dc8da130c4e3405cfe7eb833b3da6c5026a17f79b82b6` | `ee371f753e808094cf15f1e4f15eeceabc42f22edeb94eb60cf484a08f8a93c0` |
| `S9-B13-L12-BITS` · 45813207026 | `c7e353769567513988226dd1edc3d1afbc3defbe98bd7e0d9e5d8c679cda52a1` | `697f9c39a224924cc2388f1a38c3ef86df75293bf48da006c7d04995890e42da` |
| `N22-PAIR-FIXED` · 45813207026 | `d36c54c50559c4623c7ba13e0c1784d4ddc315d459ce0786a04c022cafc68e5d` | `ff27004a400b6f49449a0049c6007a066af7c298bfc034abbd702a2bdd14ef21` |
| `N23-PAIR-FIXED` · 45813207026 | `114329565aaadd1a6589b9875b18d2991d293d181396ef2531cab4d5bbfffb3c` | `7df02d51c4017d76a3fb58aac4d95f50f96d194d265d5a5d7cf55fafc34ccf54` |
| `N23-ODD-CENTER` · 45813207026 | `af5171cf61daf9ba17fb79de6641b9d0de784c168733d7440cc681a3d17c2853` | `151f650636584906d619c66854282d4e8dc8187339d102824613950cbb360e4a` |
| `N24-PAIR-FIXED` · 45813207026 | `7cade55e86302ee30b1340b9ad9feaf7b660d90a2d93948f590633cc2f819bae` | `b8ab41d46686b4bfef67bd54496edd56004df9cda3ee38a4322692b0ecd436c5` |
| `N25-PAIR-FIXED` · 45813207026 | `1e5ff270ef640ee81e11a50d430bf4ec61ec4ff38256400ef0717ac39a747138` | `fb77c89a59800692f0074cace58510196074c57542364693d464bc41df9251fb` |
| `N25-ODD-CENTER` · 45813207026 | `40b40ea09ac2470b4a809f63517407258e1f3410b6b85e3f2da263e8f72e46d8` | `3138673bd0930ada350f165145924cb6181cdd43f2802fa149bef1acdb948a5c` |
| `INSERT-B01-L12-BYTES` · 45813207026 | `5663ebe3ce6d23f43b1920db25241b43ef2e2053ede242cb8c41f379017e854a` | `12c55e775f2000b129a19d4a73f105ca9be7e4d29d57e4c7a633d5feeb860b09` |
| `INSERT-B12-L12-BYTES` · 45813207026 | `b46a8af6f4b30e3c53aa4a08211eef3252409edbcd8261ad30233b1f947dbf4a` | `167c509fe4364c1248fdaa21f4d9d1f6b53945ec4aab01b37a658b3fddbcf3d7` |
| `INSERT-B13-L12-BYTES` · 45813207026 | `2cb69fbca815aeab612c1b247684af5621da01dc40940dffcdc3a2b341959522` | `c5fcf6c1597c77c339721011dba7221d3300df157f8052d921b10481123082d5` |

[Индекс FIX3](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) · [Индекс S13](/root/ch8-artifacts/run-45688753097/ch8-rev2-s13-geometries-Linux-X64-45688753097-1/index.json) · [Индекс N18/N19](/root/ch8-artifacts/run-45749463113/ch8-rev2-n18-n19-providers-Linux-X64-45749463113-1/index.json) · [Индекс FIX1](/root/ch8-artifacts/run-45813207026/ch8-rev2-n22-n25-providers-Linux-X64-45813207026-1/index.json)

## Exact roster и контрольные пути

Общий префикс selector `slice::sort::shared::smallsort::verify::rev2_n22_n25_consumer::`. Все восемь корней имеют `#[kani::proof]` и `#[kani::unwind(36)]`. У каждой пары один `check_nN::<CORRUPT>` с одним actual вызовом и одинаковыми assertions. Positive покрывает каждую комбинацию N независимых битов. q и внешние байты произвольны у обоих корней. Actual сеть работает с исходным срезом без предположения о порядке половин, stubs, Replace и loop contracts. После actual возврата и covers контроль выполняет `v[1] ^= 1`. Общий oracle требует каноничность всех байтов и маску с исходным popcount, в которой единицы сгруппированы в старших битах. q/frame проверяются отдельно.

| № | Slot | Suffix | Root строка | Ожидаемый исход | Covers | Latest start |
| ---: | --- | --- | ---: | --- | ---: | ---: |
| 1 | `N25-ACTUAL-BITS` | `n25_actual_bits` | 20 | `VERIFIED`, 0 | 7 | 50:00 |
| 2 | `N25-WITNESS-CORRUPT` | `n25_witness_corrupt` | 26 | `FAILED`, 1 | 6 | 53:25 |
| 3 | `N24-ACTUAL-BITS` | `n24_actual_bits` | 32 | `VERIFIED`, 0 | 5 | 56:50 |
| 4 | `N24-WITNESS-CORRUPT` | `n24_witness_corrupt` | 38 | `FAILED`, 1 | 5 | 60:15 |
| 5 | `N23-ACTUAL-BITS` | `n23_actual_bits` | 44 | `VERIFIED`, 0 | 7 | 63:40 |
| 6 | `N23-WITNESS-CORRUPT` | `n23_witness_corrupt` | 50 | `FAILED`, 1 | 6 | 67:05 |
| 7 | `N22-ACTUAL-BITS` | `n22_actual_bits` | 56 | `VERIFIED`, 0 | 5 | 70:30 |
| 8 | `N22-WITNESS-CORRUPT` | `n22_witness_corrupt` | 62 | `FAILED`, 1 | 5 | 73:55 |

Для всех восьми `CAL1 q actual comparator executed` закреплён на `cal1_model.rs:28:9` в `<KeyLess<u8> as FnMut<(&u8, &u8)>>::call_mut` с полным путём из request. Метки из следующей таблицы имеют префикс `REV2_Nxx_ACTUAL_`, точный instance `check_nN::<false>` или `check_nN::<true>` и координаты в `rev2_n22_n25_consumer.rs`. У правого sentinel только positive instance.

| Suffix метки | N25 | N24 | N23 | N22 |
| --- | --- | --- | --- | --- |
| `AFTER_COPY_BACK` | 75:5 | 103:5 | 125:5 | 153:5 |
| `MIXED_INPUT` | 76:5 | 104:5 | 126:5 | 154:5 |
| `LEFT_ALL_TAIL_SHIFTS` | 77:5 | 105:5 | 127:5 | 155:5 |
| `RIGHT_ALL_TAIL_SHIFTS` | — | 106:5 | 128:5 | 156:5 |
| `RIGHT_S13_PREFIX13_INVERSION` | 79:5 | — | — | — |
| `ODD_LEFT_REMAINDER` | 80:5 | — | 130:5 | — |
| `ODD_RIGHT_REMAINDER_LEFT_REVERSE_SENTINEL` | 83:9 | — | 133:9 | — |
| `Q_FRAME` | 88:5 | 110:5 | 138:5 | 160:5 |
| `V34_FRAME` | 89:5 | 111:5 | 139:5 | 161:5 |
| `CANONICAL_SORTED_POPCOUNT` | 91:5 | 113:5 | 141:5 | 163:5 |

Контрольный `FAILED` допускает ровно одну ошибку `REV2_Nxx_ACTUAL_CANONICAL_SORTED_POPCOUNT`. Regular и stock должны согласовать native ID, класс assertion, метку и fail location. Regular дополнительно привязывает столбец и exact instance. Stock RFC 0015 отдаёт для failed property файл и строку. Остальные обязательные assertions должны быть `SUCCESS`, включая q/frame. Для safety, overflow и unwind итоговая сверка сохраняет успешные проверки на достигнутых путях и отклоняет посторонние failures. `MATCHED` требует также всех обязательных covers и согласования regular/stock. [Rust roots](/root/verify-rust-std-rev2-n22-n25-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n22_n25_consumer.rs:18) · [Разбор результата](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/results.py:289)

| N | Witness → правильный результат → XOR после возврата | Сдвиги в каждой S9 половине | Центр на witness |
| ---: | --- | --- | --- |
| 25 | `0x00ff_f1ff` → `0x01ff_fff0` → `0x01ff_fff1` | Слева 9+9+9. Справа S13, пустой driver. | Левый, `(11,1,0,12)`, `S+11` |
| 24 | `0x001f_f1ff` → `0x00ff_ffc0` → `0x00ff_ffc1` | 9+9+9 с каждой стороны | — |
| 23 | `0x000f_f9ff` → `0x007f_ffe0` → `0x007f_ffe1` | Слева 9+9, справа 9+9+9 | Левый, `(8,3,2,9)`, `S+8` |
| 22 | `0x000f_f9ff` → `0x003f_fff0` → `0x003f_fff1` | 9+9 с каждой стороны | — |

Covers `LEFT_ALL_TAIL_SHIFTS`, `RIGHT_ALL_TAIL_SHIFTS`, `RIGHT_S13_PREFIX13_INVERSION` и `ODD_*_REMAINDER` проверяют предикаты входной маски после actual возврата. Сам путь внутри сети привязан офлайн по actual расписанию, сдвигам и ранговому ходу курсоров.

У каждой S9 половины первые девять байтов witness — единицы, хвост — нули. Первая вставка сравнивает 0 с 1 и сдвигает девять единиц до начала. Следующие проходят те же девять единиц и останавливаются у уже вставленного нуля, восстанавливая дыру после нулевого префикса. У N25 справа двенадцать единиц и один конечный ноль дают исходную инверсию префикса13 и actual S13 перед пустым driver. Контрольные маски дают левый остаток на нечётных N. Sentinel-маски из таблицы нечётного центра дают правый остаток только в обязательном наборе positive. Офлайн сверка прочитала 25/45 пар из фактического исходника, повторила сдвиги, результаты и все 23/25 терминальных сигнатур нечётных N на канонических отсортированных половинах.

## Профиль и окна

Ubuntu 24.04, одна job с пределом 120 мин. Stock Kani по пину выше, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Штатные safety, overflow, unwind, undefined-function и assertion-reach включены. Uninit и validity выключены. Для каждого слота отдельные cold CWD, Cargo/Kani targets, TMPDIR и export. Cold wall ≤180 с, reap 10 с, receipt 5 с, launch headroom 10 с. VT ≤120 с, group RSS ≤4 GiB и машинный резерв 2 GiB. Linux RSS группы может быть занижен при смене worker TID.

| Стадия | Граница от нового monotonic epoch | Внешний timeout |
| --- | --- | ---: |
| Setup, включая source pins, ранний compile preflight и exact discovery | 49:00. Preflight до 180 с с сохранением первых rustc diagnostics при отказе. | `prepare` 51 мин |
| `measure` input gate | До 50:00 и ≤60 с от входа. | В составе `measure` |
| Восемь слотов и финальная аттестация | 77:20 и 79:20 соответственно. `measure` ≤30:25 от входа. | 32 мин |
| `finish` и `upload-gate` | Общий cutoff 84:15. `finish` ≤5:00 от входа. | 6 мин и 1 мин |
| Upload и резерв | Абсолютный конец upload 91:20, оставлены 5 с перехода. Резерв плана до 100:20. | Upload 7 мин |

Сохраняются атомарная запись disposition/reap до projection, ограниченные receipt/retry, 4 MiB на projection и 96 MiB на artifact. После неподтверждённого reap следующие слоты получают `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED`. Приёмка `CONSUMER_PAIRS_WITHIN_PROFILE` требует восемь exact `MATCHED`, полные anchors и covers, timely receipts, подтверждённые sampler/reap, лимиты каждого слота и своевременную финальную аттестацию. `proof_credit=NONE` сохраняется и при диагностическом успехе. [Часы](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/run.py:99) · [Приёмка](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/report.py:108)

## Локальная валидация R1

- Вручную проверены Rust-видимость actual функции через `super::super`, доступность `KeyLess<u8>::with_q/q` и корневой `cfg(kani)`. Std delta ограничена новым модулем, регистрацией под всей унаследованной цепочкой cfg и декларацией check-cfg. При снятии добавлений восстанавливаются исходные blobs registry/manifest. Runtime, существующие контракты и provider-модули побайтно совпали. `rustfmt --check` прошёл установленным nightly-2026-11-19 с `--edition 2024 --config use_small_heuristics=Max,skip_children=true,reorder_modules=false`. `git diff --check`, YAML с уникальными ключами, `bash -n` для восьми shell-блоков и Python AST прошли.
- Bare shallow Std depth 2 получен по локальному Git transport без alternates. `bundle verify/list-heads/unbundle` прошли. Для проверки bare-импорта вместо рабочих копий и submodules использованы прямые проверки local base и объектов. Сверены 16 commit/tree/sole-parent, cfg-off blobs, 85 source координат и 70 native label координат с учётом специализаций. Каждый отдельный сдвиг столбца на +1 отклонён. HEAD, refs и shallow boundary сохранились.
- На финальном detached trigger точный workflow block `pins` завершился за 100,463 с. Последовательно прошли по 116 тестов на обычной шкале и свежих шкалах 1/5/60 с. Время suite 24,217 / 24,435 / 24,231 / 25,187 с. Blob `ch8-cal1/test_supervisor.py` в Control и trigger — `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- Синтетика проверила exact cfg-off/on delta из восьми plain Proof с сохранением унаследованного inventory, ранний staged preflight, foreign geometry/instance, неверный столбец, потерю copy-back и odd cover, посторонний failure, поздний receipt и latch после потери reap. `finish` и `upload-gate` прошли ровно на общем cutoff с переходом 5 с до upload и отказом после сдвига на 0,01 с. На detached trigger также отклонены 32 мутации gate, payload, tree и admission receipt. Synthetic finish дал 8 `NOT_STARTED`, 4 `OPEN` пары и 12 членов индекса с совпавшими размерами и SHA-256.

CI, push, изменение Actions variables и локальные запуски cargo, rustc, Kani и CBMC не выполнялись. Локальные коммиты Std, Control, review-trigger и handoff R1 помечены `[skip ci]`. Независимое ревью и GO остаются отдельными решениями.

## FIX1

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`

Автор и коммиттер Std, Control и локального review-trigger — `Tiramisu-Cake <igkharin@gmail.com>`. Tree Std совпадает с R1. Работа выполнена поверх задания g0 `44221a04536055efa1dd143b764aad96b904fc90`. Handoff R1 `ca3e7862f2749e23a9684e094921a341a659fa5b` сохранён в истории g0. [Задание FIX1](REV2-N22-N25-CONSUMER-FIX1-TASK.md)

| Роль и worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n22-n25-consumer-w14), `work/rev2-n22-n25-consumer-w14` | `8fe1b01f0a85ee60118d1813d6b74645e4594213` | `f754c01d0ed26cb8d4e28c81efe8467cdf97d034` | `b076d2ff4ed720930e2de62d70c0bbd1bb0308d5` |
| [Control](/root/kani-rev2-n22-n25-consumer-control-w14), `work/rev2-n22-n25-consumer-control-w14` | `fd941d949379ac437b9071cf9a1e636ae72aee5b` | `f4d42df994425e251022feeedcfd89e608b3d17a` | `279c2200a8ecab1ee0e9057c86d771ff6e6c963e` |
| [Detached review-trigger](/root/kani-rev2-n22-n25-consumer-trigger-w14/control), ref `review/rev2-n22-n25-consumer-trigger-w14` | `8a8bddf892308c1556b723d7540e378ad49badcf` | `f4d42df994425e251022feeedcfd89e608b3d17a` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Ожидаемое значение независимого pin — `CH8_REV2_N22_N25_CONSUMER_TRIGGER_TREE=f4d42df994425e251022feeedcfd89e608b3d17a`. Runner получает его как `REV2_N22_N25_CONSUMER_TRIGGER_TREE` для `pins`, `sources` и `finish`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/CI-REQUEST.json) | `a21b91c9de484d6400a241c495b95791172d031f4a2cee49e2219fb594a07d2d` |
| Roster, canonical JSON | `ccc8db596f3e9b61299057b4c23f9747af4dc85d62b70456e1bfcaf30ad76bf6` |
| [std-overlay.bundle](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/std-overlay.bundle), 45 631 байт | `7768ed33b33812682e393222079e1a199eb2cde27bedd58f82d23cbf2be88dee` |
| Source bindings, canonical JSON | `6fb605dd5ad65f9e61a67b21e82e6aaa90cd762fccf47f54f1e94ad9f92bbb4b` |

### Дельта от R1

- Std пересоздан с исправленным авторством. `git diff` между двумя Std-коммитами пуст. Пины roster, source bindings, восемь root selectors, координаты, actual runtime, контракты и опоры совпадают побайтно.
- В Control изменены четыре файла. Пересобран `std-overlay.bundle`, его SHA-256 и Std commit обновлены в `request.py` и `CI-REQUEST.json`. Source gate требует ключ `historical_blobs` и выдаёт явную ошибку при его отсутствии до чтения Git. Добавлен тест этого отказа в `test_run.py`. Профиль и часы совпадают с R1. [Source gate](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/request.py:448) · [Тест](/root/kani-rev2-n22-n25-consumer-control-w14/ch8-cal1/test_run.py:223)
- В описании covers путей отмечены предикаты входной маски и офлайн-привязка каждого пути. [Exact roster и контрольные пути](#exact-roster-и-контрольные-пути)

### Повторная локальная валидация

- `rustfmt --check` на новом модуле и registry, `git diff --check`, YAML с уникальными ключами, `bash -n` для восьми shell-блоков и Python AST прошли. Видимость Rust, cfg и побайтное совпадение Std с R1 сверены. Blob `test_supervisor.py` в Control и trigger равен `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- Bundle импортирован в свежий bare shallow depth 2 без alternates. Проверены единственный заявленный HEAD, prerequisite, 16 пар commit/tree с sole parent, cfg-off blobs, исторические blobs и 85 source координат. Все 70 native координат прошли проверку, каждый отдельный сдвиг столбца на +1 отклонён. HEAD, refs и shallow boundary сохранились.
- Офлайн повторно сверены контрольные маски, сдвиги, оба нечётных центра и sentinel. Хэши четырёх исторических индексов и 32 членов receipt/projection совпали.
- Точный workflow block `pins` на финальном detached trigger прошёл за 156,821 с. По 117/117 тестов прошли последовательно на обычной и свежих шкалах 1/5/60 с. Время suite 28,423 / 43,811 / 41,043 / 36,292 с. Сценарии включают отсутствие `historical_blobs`, чужую геометрию, сдвиг столбца, потерю copy-back или odd cover, лишний failure, поздний receipt, потерю reap и общий cutoff finish/upload с 5 с на переход.
- В синтетике `pins`, `sources` и `finish` отклонили поданный tree R1. Всего проверены 35 отказов для trigger, payload и admission receipt. Синтетический finish дал 8 `NOT_STARTED`, 4 `OPEN` пары и 12 членов индекса со сверенными размерами и SHA-256.

CI, push, изменения Actions variables и локальные запуски cargo, rustc, Kani и CBMC не выполнялись. Нативный preflight, discovery и измерения ожидают отдельного GO.
