# REV2 · merge и нечётные центры N26–N31

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`

Один офлайн-пакет для Ubuntu, Item 2. В roster пять exact FIX3 pair Check N26–N30 и три odd-center Check N27/N29/N31. Для N31 pair используется исторический `M31-PAIR-FIXED` из run `45785063793`. Текущие нативные compile preflight, discovery и восемь измерений имеют статус `NOT_RUN`. Независимое ревью, отдельный GO и очередь определяются после сдачи с учётом пакета валидности. [Задание](REV2-N26-N31-MERGE-TASK.md) · [Допуск опор половин](REV2-N26-N31-HALVES-ADMISSION.md)

## Пины и входы

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n26-n31-merge-w15), `work/rev2-n26-n31-merge-w15` | `71953c45a9a38cff3538c8a5e413890efc896d70` | `f59ea89d61b25e34f06f9b14d61ad48694b86950` | `ea34c58ab95b4cbccd9acaa3080597b8b2517a87` |
| [Control](/root/kani-rev2-n26-n31-merge-control-w15), `work/rev2-n26-n31-merge-control-w15` | `108c45668b1c8aa41a6f0ae228697a639ad54933` | `e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7` | `302604ce810495c342282fba17cbdaea9aaf8cc5` |
| [Локальный detached review-trigger](/root/kani-rev2-n26-n31-merge-trigger-w15/control), ref `review/rev2-n26-n31-merge-trigger-w15` | `45a580e406244b83043f0b25c5caaef39012374c` | `e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std halves FIX1 имеет tree `75c4a374a0c906c989e2770a26990c7cdc6cdf83` и sole parent `8fe1b01f0a85ee60118d1813d6b74645e4594213`. Control halves FIX1 имеет tree `b235397dd83b5ee85a53d56ebe40e01f547e8403` и sole parent `fd941d949379ac437b9071cf9a1e636ae72aee5b`. Std CI-base для bundle — `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Author и committer каждого нового коммита — `Tiramisu-Cake <igkharin@gmail.com>`. Для Std, Control и trigger обе роли сверены через `git show -s --format='%an <%ae> | %cn <%ce>'` перед заморозкой пинов. Все новые коммиты используют `[skip ci]`.

Ожидаемый независимый Actions pin `CH8_REV2_N26_N31_MERGE_TRIGGER_TREE=e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7` передаётся как `REV2_N26_N31_MERGE_TRIGGER_TREE`. `pins`, `sources` и `finish` сверяют этот tree, `HEAD == GITHUB_SHA == payload.after`, единственный parent, чистый detached checkout, fork `Tiramisu-Cake/kani`, событие push на `refs/heads/uninit-ci/ch8-q-pilot-v1` и attempt 1. После `pins` также сверяется admission receipt. Compile preflight предшествует cfg-off/on discovery и записывает первые ошибки rustc. Ожидаемая дельта discovery — ровно восемь строк с указанными selector, kind, file и full target. Сохраняется весь cfg-off инвентарь, включая Check targets. Upload следует за допуском trigger, успешными `finish` и `upload-gate`. [Workflow](/root/kani-rev2-n26-n31-merge-trigger-w15/control/.github/workflows/ch8-q-pilot.yml)

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n26-n31-merge-control-w15/ch8-cal1/CI-REQUEST.json) | `013f4c377d46f0620fd4082bd2666b8faf716b40f89d72d9bc02e21a2802a9a9` |
| Roster, canonical JSON | `47cd94f3d07647f62ce26e0e0f1f8451545775e45d46f985a8f1759adbc059db` |
| [std-overlay.bundle](/root/kani-rev2-n26-n31-merge-control-w15/ch8-cal1/std-overlay.bundle), 52 888 байт | `6ccc000275fc9790184ee0b1bb04c130ac4955a927a786d7bf53eb46534e8ca6` |
| Source bindings, canonical JSON | `04b1c9ad8d84a83a3cfb6afee74d4a1af73b9e33f319f3ee200e59da56f70b0d` |

Canonical JSON использует сортировку ключей и разделители `(",", ":")`. `ch8-cal1/test_supervisor.py` в Control и trigger имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`.

## Roster и нативная привязка

Все восемь корней имеют вид `Check`. Полный selector и discovery target образуются добавлением префикса `slice::sort::shared::smallsort::verify::rev2_n26_n31_merge::` к соответствующему суффиксу. Оба объявлены в `core/src/slice/sort/shared/smallsort/verify/rev2_n26_n31_merge.rs`. Stock export должен содержать `ProofForContract.target_fn` с именем из столбца target и `contracted_function_name`, связанный с regular `single_top_level_call` и `no_recursive_call` точной специализации на строке `modifies`. Принимаются успешные regular ID, Location и Status и cover IDs с `SATISFIED` в stock export. Нативные IDs и символы восьми новых корней будут наблюдаться только в будущем запуске. [Std-модуль](/root/verify-rust-std-rev2-n26-n31-merge-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_n26_n31_merge.rs) · [Замороженные координаты и labels](/root/kani-rev2-n26-n31-merge-control-w15/ch8-cal1/CI-REQUEST.json)

| Слот | Selector suffix | Target | Exact source, записи | `modifies` | Latest start |
| --- | --- | --- | --- | --- | --- |
| `N26-PAIR-FIXED` | `n26_pair_fixed` | `actual_pair_step_n26` | `v[1..27]`, m=13, k=0–12, D[k] и D[25−k] | 14:1 | 55:00 |
| `N27-PAIR-FIXED` | `n27_pair_fixed` | `actual_pair_step_n27` | `v[1..28]`, m=13, k=0–12, D[k] и D[26−k] | 134:1 | 58:25 |
| `N28-PAIR-FIXED` | `n28_pair_fixed` | `actual_pair_step_n28` | `v[1..29]`, m=14, k=0–13, D[k] и D[27−k] | 254:1 | 61:50 |
| `N29-PAIR-FIXED` | `n29_pair_fixed` | `actual_pair_step_n29` | `v[1..30]`, m=14, k=0–13, D[k] и D[28−k] | 374:1 | 65:15 |
| `N30-PAIR-FIXED` | `n30_pair_fixed` | `actual_pair_step_n30` | `v[1..31]`, m=15, k=0–14, D[k] и D[29−k] | 494:1 | 68:40 |
| `N27-ODD-CENTER` | `n27_odd_center` | `actual_odd_center_n27` | `v[1..28]`, D[13], sentinel берёт S+26 | 616:1 | 72:05 |
| `N29-ODD-CENTER` | `n29_odd_center` | `actual_odd_center_n29` | `v[1..30]`, D[14], sentinel берёт S+28 | 728:1 | 75:30 |
| `N31-ODD-CENTER` | `n31_odd_center` | `actual_odd_center_n31` | `v[1..32]`, D[15], sentinel берёт S+30 | 840:1 | 78:55 |

Домен harness — произвольные инициализированные 34 байта, `S=&v[1]`, `u8/KeyLess<u8>` с числовым `<`, независимый `q: u8` и отдельный writable `MaybeUninit<[u8;32]>` для D. У pair wrapper проверяет только допустимые счётчики, readable source, writable D, disjoint и write set двух целей. Предположение порядка находится в fixture. При `b=k−a` и `d=k−c` обёртка вызывает actual `merge_up(S+a,S+m+b,D+k)` и `merge_down(S+m−1−c,S+N−1−d,D+N−1−k)`. Посты проверяют обе тройки курсоров, min/max, выбор слева при tie у up и справа при tie у down, exact bounds, q и frame всех 34 байтов source. Десять covers у каждой пары — actual comparator, k=0, k=m−1, useful return, обе стороны каждого вызова и оба ties. [Ревью формы FIX1](REV2-N22-N25-PROVIDERS-REVIEW.md#r2--fix1)

Odd wrapper транскрибирует `wrapping_add(1)`, `left < left_end`, выбор адреса, копирование одного байта в D[m] и продвижение выбранного курсора. Harness проверяет единственный остаток, exact bounds, выбранный адрес и значение, q и source frame, а также два равенства конца из actual guard. Четыре covers — левый и правый остаток, sentinel с c=m и точным S+N−1, post-copy. Все корни читают из D только свои записанные цели. Stubs, Replace, loop contracts и copy-back отсутствуют. Frozen `copy_back=false` проверяется для всех восьми строк.

| Слот | Координаты основных свойств в новом модуле |
| --- | --- |
| N26 pair | up/down cursors 32:9 / 40:9, min/max 115:5 / 116:5 |
| N27 pair | up/down cursors 152:9 / 160:9, min/max 235:5 / 236:5 |
| N28 pair | up/down cursors 272:9 / 280:9, min/max 355:5 / 356:5 |
| N29 pair | up/down cursors 392:9 / 400:9, min/max 475:5 / 476:5 |
| N30 pair | up/down cursors 512:9 / 520:9, min/max 595:5 / 596:5 |
| N27 center | source/value 698:5 / 699:5, end guard 700:5 / 704:5, sentinel 712:5, post-copy 719:5 |
| N29 center | source/value 810:5 / 811:5, end guard 812:5 / 816:5, sentinel 824:5, post-copy 831:5 |
| N31 center | source/value 922:5 / 923:5, end guard 924:5 / 928:5, sentinel 936:5, post-copy 943:5 |

`smallsort.rs:391–416` задаёт геометрию половин и actual S13 и вставки, `:424` передаёт точный срез merge, `:1014–1024` инициализирует и обновляет курсоры. Actual копии up/down находятся в `:885` и `:918`, нечётная ветка и guard в `:1027–1042`. Транскрипции center копируют на строках 636, 748 и 860 нового модуля. Компаратор проходит cover `cal1_model.rs:28:9` и выполняет `a < b` на `:29:9`. У каждого Check сохраняются `memcpy.assigns.1/.2` с builtin-координатами 46/47. Для `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14` принимаются ровно привязанные `.safety_check.1/.2` для alignment, `.arithmetic_overflow.1` для длины в байтах и `.precondition_instance.1/.2/.3` для disjoint/readable/writable. Группа применяется к обеим straight-line actual копиям пары по cursor assertions и useful-return cover, а у center к однобайтовому вызову по обоим branch covers и post-copy. Сверка успешных unwind свойств, exact write set и достижимости связывает grouped свойства с этими исполнениями. [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

| Исходник | Git blob в Std |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `rev2_n26_n31_halves.rs` | `92de2daf5b195e6340af59a8b9b7a1e0a22e8770` |
| `rev2_n26_n31_merge.rs` | `df670cd3a63cce01fe89f8a4fdf94353b849d805` |
| `rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |
| `verify.rs` / `core/Cargo.toml` | `56b129937f1043f5057066e1307de27c6eb0c94c` / `cceb09fc75ca0577eedc160a91c9fbd6148bd536` |

## Ранговые рёбра для N26–N31

Принятые посты половин дают numeric order, сохранение всех кратностей каждой половины, q и байтов вне активного среза. Левая половина использует B01, правая B14/B15/B16. Для вставок действуют принятые внешние переносы и индукция по actual итерациям. Вызов `smallsort.rs:424` передаёт то же S и N, поэтому обе половины удовлетворяют sorted fixture domain каждой пары. [Геометрии, основания и границы опор](REV2-N26-N31-HALVES-ADMISSION.md#привязка-полного-байтового-домена)

| N | Левая / правая геометрия и rel вставок | Pair-ребро | Завершение в D |
| --- | --- | --- | --- |
| 26 | B01 L13, B14 L14→L13 · ∅ / ∅ | новый N26, k=0–12 | границы сходятся после 13 пар |
| 27 | B01 L13, B14 L14 · ∅ / 13 | новый N27, k=0–12 | center D[13] |
| 28 | B01 L17→L14, B15 L15→L14 · 13 / 13 | новый N28, k=0–13 | границы сходятся после 14 пар |
| 29 | B01 L17→L14, B15 L15 · 13 / 13–14 | новый N29, k=0–13 | center D[14] |
| 30 | B01 L17→L15, B16 L16→L15 · 13–14 / 13–14 | новый N30, k=0–14 | границы сходятся после 15 пар |
| 31 | B01 L17→L15, B16 L16 · 13–14 / 13–15 | исторический M31, k=0–14 | center D[15] |

Упорядочим исходные позиции по `(byte, индекс в S после вставок)`. Внутри половины индекс разрешает равенства, между половинами минимум при равных байтах находится слева, максимум справа. Это ровно tie-правила actual up/down. Перед парой k уже извлечены k наименьших и k наибольших рангов. Из левой половины a ушло снизу и c сверху, из правой соответственно b и d, так что `a+b=c+d=k`. Изначально все четыре счётчика нулевые и D пуст. В непустой половине оставшиеся позиции образуют интервал между соответствующими курсорами. Кандидаты up и down — его крайние позиции.

Если половина длины r исчерпана, её нижний и верхний счётчики x,y удовлетворяют `x+y=r`. Перед каждой парой `x,y≤k<m≤r`, поэтому `x>0` и `y>0`. Кандидат up из исчерпанной половины находится в первой уже извлечённой сверху позиции x и больше всех оставшихся по рангу. Кандидат down из исчерпанной половины в позиции x−1 был извлечён снизу и меньше всех оставшихся. Они читаются в пределах своей половины и проигрывают сравнение с крайним кандидатом оставшейся половины. До каждой пары остаётся как минимум два разных ранга, поэтому up и down выбирают разные позиции, даже если байты равны и оба выбора лежат в одной половине. Цели различны, так как `k<m` даёт `k<N−1−k`. Оба actual вызова получают source-кандидаты из состояния перед парой, записывают только эти две ячейки и сдвигают ровно соответствующие курсоры. Предыдущие записи сохраняются. Так инвариант и точные цели охватывают все k фактического цикла, включая оба края.

После m пар у чётной длины оба остатка нулевые. Поэтому `a=m−c` и `m+b=N−d` непосредственно дают два равенства guard после `wrapping_add(1)`. У нечётной длины остатки `(m−a−c,m+1−b−d)` принадлежат `{(1,0),(0,1)}`. При левом остатке счётчики имеют вид `(i,m−i,m−1−i,i+1)` для `0≤i<m`, выбор есть S+i. При правом остатке вид `(i,m−i,m−i,i)` для `0≤i≤m`, выбор есть S+2m−i. Это ровно домен odd Check при k=m. В sentinel-случае `(0,m,m,0)` значение `left_rev=S−1` участвует только в `wrapping_add(1)`, дающем `left_end=S`. Адрес S−1 указывает на v[0], вне переданного среза. Читается правый S+N−1. Однобайтовый copy дописывает ранг m, выбранный курсор продвигается и оба равенства guard выполнены. Для каждого состояния есть sorted binary witness с i нулями слева и `m−i` либо `m+1−i` нулями справа.

Совместный пост даёт числовой порядок и полные кратности в D[0..N], q/source frame и границы записи. Заполненность scratch перед чтением следует внешне из покрытия различных ячеек всеми парами и нечётным центром при uninit OFF. Это аргумент для составного merge-графа с опорой на будущие принятые результаты восьми Check. Exact native copy-back/frame на `smallsort.rs:425` и различающий сквозной контроль каждой длины остаются открытыми. [Прецедент центров N23/N25](REV2-N22-N25-ADMISSION.md#нечётные-центры) · [Правило композиции](REV2-COMPOSITION-RULE.md)

## Проверка исторического M31-PAIR-FIXED

Run `45785063793`, attempt 1, Ubuntu X64. Std `f72f4303bacfff4706b20268a87b2a1031a8ee0b`, tree `03f9ce753b375729c2f8e53c18b2eaf7f3f07fc1`, trigger `a16071eefa002ee4cb885fde253a2f3c59cd8e1c`. Совпадают stock Kani, CBMC 6.11.0, solver CaDiCaL (в индексе 3.0.0), OB12, unwind36, jobs=1, `--no-assert-contracts` и профиль проверок. Индекс фиксирует `MEASURED`, `COMPLETE` final attestation и `proof_credit=NONE`. Слот имеет `VERIFIED`, exit 0, `MATCHED`, полный своевременный receipt, подтверждённые sampler/reap и 11/11 covers. VT 50,900 с, cold wall 84,343 с, sampled peak группы 2 224 500 KiB. Blobs actual `smallsort.rs`, `cal1_model.rs`, `ptr/mod.rs` и `rev2_merge_pair_fixed.rs` идентичны в историческом Std, halves base и новом Std. [Разбор run](REV2-MERGE-PAIR-FIXED-RESULTS-ANALYSIS.md#приёмка-run-45785063793) · [Исторический GO](REV2-MERGE-PAIR-FIXED-GO.md)

| Опубликованный член | Байт | SHA-256 |
| --- | ---: | --- |
| [index.json](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/index.json) | 27 578 | `ded8803087eab9aedcc2bfcda6dd1d5184fc6e6b640f796bd206a391fc313c06` |
| [receipt.json](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/slots/M31-PAIR-FIXED/receipt.json) | 83 459 | `e1e2e1842e37c1d1669ad322306ca72d4388759c86ac0fd308042bcf74f227a1` |
| [projection.json](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/slots/M31-PAIR-FIXED/projection.json) | 345 770 | `2a9c504abf5bba1fb27d2633a02de6912dd68f1469bccf9244711cebd60e2ca4` |

Размеры и SHA-256 receipt и projection совпали с индексом. Exact selector `slice::sort::shared::smallsort::verify::rev2_merge_pair_fixed::m31_pair_fixed`, target `actual_pair_step_n31`, домен V34[1..32], 15+16 sorted, scratch32 и `0≤a,c≤k<15`. Stock `ProofForContract` привязан к `_RNCNCNvNtNtNtNtNtNtCs2Yk8zB8usQS_4core5slice4sort6shared9smallsort6verify21rev2_merge_pair_fixed20actual_pair_step_n31s0_00Bh_`. У target с суффиксом `::{closure#2}::{closure#0}` свойства `.single_top_level_call.1` и `.no_recursive_call.1` имеют `SUCCESS` на `rev2_merge_pair_fixed.rs:387:1`, cursor assertions `.assertion.7/.10` на 413:9 и 423:9. Прямые строки `actual_pair_step_n31.assertion.7/.10` в regular имеют `UNREACHABLE`. Посты min/max, q и source frame находятся на 493–496, covers на 497–506 и `cal1_model.rs:28:9`. В `native_checks` сведены `memcpy.assigns.1/.2`, все шесть grouped свойств ptr и четыре `SUCCESS` unwind свойства. Covers фиксируют обе стороны up/down, up/down/both ties, края k и нормальный возврат после actual пары. Ребро относится к двум точным записям, связываемым с k=0–14 приведённой индукцией.

## Профиль и часы

Одна job `ubuntu-24.04` с пределом 120 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach включены. Uninit и validity выключены. Предел отбора VT 120 с, cold wall 180 с, cap группы 4 GiB, резерв 2 GiB. Linux RSS снимается выборочно, быстрые смены worker TID могут занижать наблюдаемый пик. Отдельные холодные CWD, Cargo/Kani targets, TMPDIR и exports на слот. [Лимиты](OWNER-DECISION-LIMITS-20261125.md)

| Граница от одного monotonic job epoch | Секунды / mm:ss | Внешний timeout |
| --- | --- | --- |
| Prepare, включая compile preflight и discovery | 3 240 / 54:00 | 56 мин |
| Входной gate / первый latest start | 3 300 / 55:00 | внутри measure |
| Конец окон / конец финальной аттестации | 4 940 / 82:20 и 5 060 / 84:20 | measure 32 мин |
| Общий cutoff finish / upload-gate | 5 355 / 89:15 | finish 6 мин |
| Конец upload | 5 780 / 96:20 | upload 7 мин |
| Конец плана с резервом / предел job | 6 320 / 105:20 и 7 200 / 120:00 | job 120 мин |

Каждое окно 205 с включает 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. `measure` ограничен 1 825 с от входа, включая 60 с gate, 8×205 с, 120 с аттестации и 5 с журнал. `finish` ограничен 300 с от входа и общим cutoff, после которого остаются 5 с на переход и 420 с upload. Setup увеличен на 5 мин с учётом измерения прежней ступени, где до отсечки оставалось 49,4 с. [Замер halves](REV2-N26-N31-HALVES-ADMISSION.md#run-45846512615)

Supervisor атомарно сохраняет checkpoint и подтверждает reap до проекции. Потеря подтверждения reap останавливает последующие слоты, а поздний receipt сохраняет наблюдение без допуска. Recovery использует ограниченный retry записи в пределах окна. Caps составляют 4 MiB для проекции и 96 MiB для артефакта. `PROVIDERS_WITHIN_PROFILE` требует все восемь `VERIFIED` с exit 0 и `MATCHED`, полные обязательные anchors и covers, своевременно записанные receipts, подтверждённые sampler/reap, наблюдённые ресурсные пределы и `COMPLETE` final attestation.

## Локальная проверка

- Rust-видимость, атрибуты и exact литералы проверены статически у всех восьми корней. Runtime `smallsort.rs`, компаратор, ptr, старые контракты и опоры совпадают с базой побайтно. Дельта Std состоит из одной cfg-декларации в manifest, регистрации под cfg и нового verification-only модуля. Удаление вставленных деклараций восстанавливает оба cfg-off blob. Прошли `rustfmt --check` закреплённым бинарником nightly-2026-11-19 с `use_small_heuristics=Max`, `git diff --check`, YAML без дубликатов ключей, `bash -n` для восьми shell-блоков и Python AST для 15 файлов.
- На чистой bare shallow Std базе depth 2 без alternates прошли `bundle verify/list-heads/unbundle`. Prerequisite — Std CI-base, единственный объявленный ref — `HEAD` кандидата. После unbundle сохранены HEAD, refs и shallow boundary. Сверены 18 троек commit/tree/sole-parent, 254 координаты source binding и 145 нативных label-координат.
- Перебор по ранговой модели на 1 399 sorted binary fixtures подтвердил выбор рангов, distinct D, оба сценария исчерпания половины и оба равенства end guard при каждой N. Для нечётных длин достигнуты все 27, 29 и 31 допустимых состояний счётчиков. Восемь синтетических replay на форме опубликованных структурированных проекций N22 pair и N23 center дали 8/8 `MATCHED`. При каждом отдельном сдвиге одной из 145 label-координат на +1 по столбцу mandatory anchors становились неполными. В replay сохранены Check closure и четыре builtin unwind ID из исторической формы. Новый exact-bounds пост центров добавлен в синтетику.
- На финальном detached trigger проверен точный shell-блок `pins` с синтетическим GitHub payload. Последовательно прошли 121/121 на обычной шкале и на свежих шкалах 1, 5 и 60 с. Время suite составило 35,470 / 31,713 / 31,911 / 32,900 с, весь блок занял 136,274 с. Синтетические `finish`, `upload-gate` и `upload-check` прошли. Индекс содержит восемь `NOT_STARTED` и 11 членов со сверенными размерами и SHA-256, итог `PROVIDERS_OPEN`.
- Синтетика отклоняет wrong tree/payload, неверный exact N, Check target/kind/file, смещение столбца или пропажу группового якоря и потерю sentinel cover у каждого центра. Проверены отказ при `copy_back=true` у всех восьми, native unwind evidence, поздний receipt, общий cutoff и остановка после неподтверждённого reap.
- Локальный объём ограничен статикой, Git, ранговой моделью и Python/shell синтетикой. Cargo, rustc, Kani, CBMC, CI и push не запускались. Actions variables не менялись.

## Следующий пакет

После независимого ревью и отдельного GO для текущего пакета сквозной этап измеряет actual network с exact copy-back/frame и post-return контролем на каждой длине. Первая пара positive/control для N31, затем N26 без вставок, затем N27 с нечётным центром и N28–N30. На каждом сохраняются первая CNF, фаза, group/CBMC RSS и PSS. При выходе широкого positive за 120 с VT или 4 GiB сохраняются наблюдение и отдельный контроль. Для составного допуска открытые exact native copy-back/frame рёбра закрываются коротким корнем по прецеденту N32. Для 12 сквозных слотов план с setup 55 мин составляет 119 мин с резервом 9 мин. [Ресурсный ориентир](REV2-N22-N25-ADMISSION.md#запас-памяти-для-n26n31) · [Прецедент N32](REV2-N32-ADMISSION.md#привязка-строки)
