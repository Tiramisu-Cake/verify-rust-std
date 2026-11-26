# REV2 · сквозные проверки N26–N31 с post-return контролями

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Item 2, w15. Один офлайн-пакет из 12 exact singleton, первая пара N31. Нативные результаты новых корней ожидаются после независимого ревью и отдельного GO. Validity остаётся отдельным пакетом. [Задание](REV2-N26-N31-CONSUMER-TASK.md) · [Допуск половин](REV2-N26-N31-HALVES-ADMISSION.md) · [Допуск merge](REV2-N26-N31-MERGE-ADMISSION.md)

## Пины и worktrees

| Роль и worktree | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n26-n31-consumer-w15), `work/rev2-n26-n31-consumer-std-w15` | `50609bb850c64080aedd74c00c9865dcae1ce74b` | `c2e93c566512c45179ab015b55835167eefc6191` | `71953c45a9a38cff3538c8a5e413890efc896d70` |
| [Control](/root/kani-rev2-n26-n31-consumer-control-w15), `work/rev2-n26-n31-consumer-control-w15` | `a02a710c0c1206459d924c7467c9092b6921c674` | `7a92427bc3e81e99016536ee6ef87dd761eb7f3a` | `108c45668b1c8aa41a6f0ae228697a639ad54933` |
| [Локальный detached review-trigger](/root/kani-rev2-n26-n31-consumer-trigger-w15/control), ref `review/rev2-n26-n31-consumer-trigger-w15` | `1d33084054113a4f1f319788e88ba4eda9d04047` | `7a92427bc3e81e99016536ee6ef87dd761eb7f3a` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Handoff находится в [g0 worktree](/root/verify-rust-std-rev2-n26-n31-consumer-g0-w15) на `work/rev2-n26-n31-consumer-g0-w15` от `3bae1ed0079aed021718efeaaaaddc8a8a46f815`. Std CI-base для bundle `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Author и committer Std, Control и trigger перед заморозкой сверены через `git show -s --format='%an <%ae> | %cn <%ce>'`. Обе роли во всех новых коммитах `Tiramisu-Cake <igkharin@gmail.com>`. Все новые commit messages содержат `[skip ci]`.

`pins`, `sources` и `finish` читают независимое значение Actions `CH8_REV2_N26_N31_CONSUMER_TRIGGER_TREE=7a92427bc3e81e99016536ee6ef87dd761eb7f3a` через `REV2_N26_N31_CONSUMER_TRIGGER_TREE`. Gate требует `HEAD == GITHUB_SHA == payload.after`, `payload.deleted == false`, exact tree и sole parent из таблицы, чистый detached checkout, fork `Tiramisu-Cake/kani`, событие push на `refs/heads/uninit-ci/ch8-q-pilot-v1` и attempt 1. После `pins` сверяется также admission receipt. [Workflow](/root/kani-rev2-n26-n31-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/request.py:305)

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/CI-REQUEST.json) | `6ab5d9e821fa55710be3cda6202bf147aed7d6c2db364ee9cef5688665fa8e02` |
| Roster, canonical JSON | `b6709c5d920e4ac4621fc10e6a4a3056a7fa7c52ca6b9ff8d399eb04e45129dc` |
| [std-overlay.bundle](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/std-overlay.bundle), 55 091 байт | `d7c197c2e3c2fda043720970fc37a57fb249fb2bb6df4c48eb3416115b683ff6` |
| Source bindings, canonical JSON | `e808404160a4d5451d0b2ab52775abc4e8d77d18dd64d7ce47f4b6192e63c5e6` |

Canonical JSON использует сортировку ключей и разделители `(",", ":")`. Вложенный historical merge roster сохраняет digest `47cd94f3d07647f62ce26e0e0f1f8451545775e45d46f985a8f1759adbc059db`. `ch8-cal1/test_supervisor.py` в Control и trigger имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`.

| Исходник | Git blob в Std |
| --- | --- |
| `rev2_n26_n31_consumer.rs` | `6d407f1df0f9d0d36f8cc3205a7c041a4c5bd4d5` |
| `smallsort/verify.rs` | `10054e550c65a4cfbd5e1c4f4159c54fcab05e7e` |
| `core/Cargo.toml` | `067c8d62dc443e80ad401f188985b8d12c12e588` |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `rev2_n26_n31_halves.rs` | `92de2daf5b195e6340af59a8b9b7a1e0a22e8770` |
| `rev2_n26_n31_merge.rs` | `df670cd3a63cce01fe89f8a4fdf94353b849d805` |
| `rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |

В `cfg-on` добавлен `kani_smallsort_rev2_n26_n31_consumer` поверх 17 унаследованных cfg под `cfg(kani)`. Registry и manifest восстанавливаются до прежних blobs удалением только новых деклараций. Discovery требует дельту ровно из 12 `standard-harnesses` с exact selector и source file. Проверка `not targets` действует для standard вне карт `*_CHECKS`. В обеих выборках проверяются прежние карты с `MERGE_CHECKS`, target и file, а полный `cfg-off` инвентарь сравнивается с частью `cfg-on` по kind, selector, file и targets. [Гейт discovery](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/run.py:243)

## Exact roster и native anchors

Префикс selector `slice::sort::shared::smallsort::verify::rev2_n26_n31_consumer::`. Все корни `#[kani::proof]` и `#[kani::unwind(36)]`, `copy_back=true`. У пары один helper `check_nN::<false/true>` с одинаковым actual вызовом и каноническим sorted-popcount oracle. Маска positive задаёт N независимых битов. На обоих входах произвольны `q`, `v[0]` и `v[1+N..34]`. Контроль выполняет `v[1] ^= 1` после actual возврата и covers. Оракул проверяет, что каждый активный байт — 0 или 1, а маска содержит исходное число единиц в старших позициях. Отдельные q и V34 assertions выполняются после ветки порчи. [Исходник корней](/root/verify-rust-std-rev2-n26-n31-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_n26_n31_consumer.rs:9)

| Slot | Selector suffix | Строка root | Ожидание | Covers | Latest start |
| --- | --- | ---: | --- | ---: | ---: |
| `N31-ACTUAL-BITS` | `n31_actual_bits` | 11 | `VERIFIED`, exit 0 | 7 | 55:00 |
| `N31-WITNESS-CORRUPT` | `n31_witness_corrupt` | 17 | `FAILED`, exit 1 | 6 | 58:25 |
| `N26-ACTUAL-BITS` | `n26_actual_bits` | 73 | `VERIFIED`, exit 0 | 5 | 61:50 |
| `N26-WITNESS-CORRUPT` | `n26_witness_corrupt` | 79 | `FAILED`, exit 1 | 5 | 65:15 |
| `N27-ACTUAL-BITS` | `n27_actual_bits` | 126 | `VERIFIED`, exit 0 | 7 | 68:40 |
| `N27-WITNESS-CORRUPT` | `n27_witness_corrupt` | 132 | `FAILED`, exit 1 | 6 | 72:05 |
| `N28-ACTUAL-BITS` | `n28_actual_bits` | 188 | `VERIFIED`, exit 0 | 5 | 75:30 |
| `N28-WITNESS-CORRUPT` | `n28_witness_corrupt` | 194 | `FAILED`, exit 1 | 5 | 78:55 |
| `N29-ACTUAL-BITS` | `n29_actual_bits` | 241 | `VERIFIED`, exit 0 | 7 | 82:20 |
| `N29-WITNESS-CORRUPT` | `n29_witness_corrupt` | 247 | `FAILED`, exit 1 | 6 | 85:45 |
| `N30-ACTUAL-BITS` | `n30_actual_bits` | 303 | `VERIFIED`, exit 0 | 5 | 89:10 |
| `N30-WITNESS-CORRUPT` | `n30_witness_corrupt` | 309 | `FAILED`, exit 1 | 5 | 92:35 |

Координаты actual вызова и native properties в `rev2_n26_n31_consumer.rs`. Метки имеют префикс `REV2_Nxx_ACTUAL_`.

| Координата или суффикс метки | N31 | N26 | N27 | N28 | N29 | N30 |
| --- | --- | --- | --- | --- | --- | --- |
| Actual `small_sort_network` | 33:5 | 95:5 | 148:5 | 210:5 | 263:5 | 325:5 |
| `AFTER_COPY_BACK` | 35:5 | 97:5 | 150:5 | 212:5 | 265:5 | 327:5 |
| `MIXED_INPUT` | 36:5 | 98:5 | 151:5 | 213:5 | 266:5 | 328:5 |
| `LEFT_S13_REL0_ONE_ZERO_TAIL` | 37:5 | 99:5 | 152:5 | 214:5 | 267:5 | 329:5 |
| `RIGHT_S13_REL0_ONE_ZERO_TAIL` | 41:5 | 103:5 | 156:5 | 218:5 | 271:5 | 333:5 |
| `ODD_LEFT_REMAINDER` | 48:9 | — | 163:9 | — | 278:9 | — |
| `ODD_RIGHT_REMAINDER_LEFT_REVERSE_SENTINEL` | 49:9 | — | 164:9 | — | 279:9 | — |
| `ODD_CONTROL_RIGHT_REMAINDER` | 46:9 | — | 161:9 | — | 276:9 | — |
| `Q_FRAME` | 57:5 | 110:5 | 172:5 | 225:5 | 287:5 | 340:5 |
| `V34_FRAME` | 58:5 | 111:5 | 173:5 | 226:5 | 288:5 | 341:5 |
| `CANONICAL_SORTED_POPCOUNT` | 68:5 | 121:5 | 183:5 | 236:5 | 298:5 | 351:5 |

В обоих корнях каждой пары native comparator cover `CAL1 q actual comparator executed` привязан к `cal1_model.rs:28:9` и `KeyLess<u8>` `FnMut<(&u8, &u8)>::call_mut`. Все остальные native coordinates выше имеют exact instance `check_nN::<false>` либо `::<true>`. У контроля допускается единственный `FAILURE` класса `assertion` с меткой `REV2_Nxx_ACTUAL_CANONICAL_SORTED_POPCOUNT`. Gate сверяет полный regular ID с RFC 0015 stock ID и exact инстанс по regex, а также сравнивает класс, метку, файл и строку. Regular дополнительно сверяет столбец. Числовой суффикс ID будет получен из нативного исхода. У положительного корня все обязательные anchors имеют `SUCCESS` или `SATISFIED` по своей роли. Контроль требует того же для обязательных свойств за пределами канонического отказа. Unwind включён в stock configuration, все выданные unwind assertions должны быть `SUCCESS`. Из режима plain Proof возможен исход без отдельных unwind ID, как в сквозном прецеденте N22–N25. [Гейт результата](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/results.py:311) · [Прецедент](REV2-N22-N25-ADMISSION.md#сверка-сквозного-пакета)

| N | Контроль, правильная маска → после XOR | Positive odd left / right sentinel | Covers + / контроль |
| ---: | --- | --- | ---: |
| 31 | `0x0000_8001`, `0x6000_0000` → `0x6000_0001` | `0x4000_7fff` / `0x0000_7fff` | 7 / 6 |
| 26 | `0x0000_2001`, `0x0300_0000` → `0x0300_0001` | — | 5 / 5 |
| 27 | `0x0000_2001`, `0x0600_0000` → `0x0600_0001` | `0x0400_1fff` / `0x0000_1fff` | 7 / 6 |
| 28 | `0x0000_4001`, `0x0c00_0000` → `0x0c00_0001` | — | 5 / 5 |
| 29 | `0x0000_4001`, `0x1800_0000` → `0x1800_0001` | `0x1000_3fff` / `0x0000_3fff` | 7 / 6 |
| 30 | `0x0000_8001`, `0x3000_0000` → `0x3000_0001` | — | 5 / 5 |

`LEFT_S13_REL0_ONE_ZERO_TAIL` и `RIGHT_S13_REL0_ONE_ZERO_TAIL` проверяют полный входной регион своей половины с единицей на rel0. В каждой контрольной маске оба предиката выполнены, обе половины содержат инверсию, S13 перемещает единицу на rel12, а каждый нулевой хвостовой байт сдвигает её ещё на один rel. У N26 оба driver пусты. Odd covers после actual возврата проверяют входные предикаты. Связь предиката с центром следует из офлайн-трассировки ниже. В каждом контроле `MIXED_INPUT` и `AFTER_COPY_BACK` предшествуют XOR.

## Составные рёбра N26–N31

Домен композиции — живой V34 с произвольными инициализированными u8, `S=&v[1]`, активный `v[1..1+N]` и независимый `q: u8`. Все actual вызовы `small_sort_network`, `sort13_optimal`, `swap_if_less`, `insertion_sort_shift_left`, `insert_tail`, `bidirectional_merge`, `merge_up` и `merge_down` специализируются на `<u8, KeyLess<u8>>`. `KeyLess::call_mut` использует числовой `a < b` на `cal1_model.rs:29:9`. Стандартные исходники этих операций совпадают с пинами исторических корней. [Правило композиции](REV2-COMPOSITION-RULE.md) · [Actual сеть](/root/verify-rust-std-rev2-n26-n31-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:375)

`smallsort.rs:385:5` вычисляет `m=N/2`. Срезы заданы на `:391:31` и `:416:27`. Обе половины проходят guard `len≥13` на `:395` и вызов S13 на `:396:13`. Вставка на `:405:9` получает offset 13. End в таблице — индекс one-past-end относительно V34.

| N | Actual левая половина, S13, вставка и end | Actual правая половина, S13, вставка и end | Exact Check для merge | Copy-back |
| ---: | --- | --- | --- | ---: |
| 31 | `v[1..16]`, B01 L17→L15, rel13–14, end 16 | `v[16..32]`, exact B16/L16, rel13–15, end 32 | `M31-PAIR-FIXED`, 15 пар, `N31-ODD-CENTER` пишет D[15] | 31 |
| 26 | `v[1..14]`, exact B01/L13, пусто, `tail=end=14` | `v[14..27]`, B14 L14→L13, пусто, `tail=end=27` | `N26-PAIR-FIXED`, 13 пар | 26 |
| 27 | `v[1..14]`, exact B01/L13, пусто, `tail=end=14` | `v[14..28]`, exact B14/L14, rel13, end 28 | `N27-PAIR-FIXED`, 13 пар, `N27-ODD-CENTER` пишет D[13] | 27 |
| 28 | `v[1..15]`, B01 L17→L14, rel13, end 15 | `v[15..29]`, B15 L15→L14, rel13, end 29 | `N28-PAIR-FIXED`, 14 пар | 28 |
| 29 | `v[1..15]`, B01 L17→L14, rel13, end 15 | `v[15..30]`, exact B15/L15, rel13–14, end 30 | `N29-PAIR-FIXED`, 14 пар, `N29-ODD-CENTER` пишет D[14] | 29 |
| 30 | `v[1..16]`, B01 L17→L15, rel13–14, end 16 | `v[16..31]`, B16 L16→L15, rel13–14, end 31 | `N30-PAIR-FIXED`, 15 пар | 30 |

**S13.** В `smallsort.rs:601:5` проверяется длина, на `:605:18` берётся base, `:612–656` задаёт 45 пар. У каждой `0≤a<b<13`, адреса внутри своей живой половины. Укорочение меняет только метаданные длины и сохраняет guard, base и все обращения. B01 опирается на `S13-SWAP-LEAF` и `S13-BASE1-BITS` либо `S13-B01-L17-BITS`. Для B14/B15/B16 stock `ProofForContract(swap_if_less)` в каждом своём Check покрывает 78 пар полных байтов и привязан к `smallsort.rs:467:1`, post `:468:1`. Actual leaf calls находятся на строках 23, 47 и 71 в `rev2_n26_n31_halves.rs`. У `check_bits::<14,14>`, `::<15,15>` и `::<16,16>` actual S13 начинается на `:96:5`, post anchors `:98:5`, `:99:5`, `:109:5` и `:111:5`. У B01 actual bit calls `rev2_s13_binding.rs:35:5` и `rev2_s13_geometries.rs:51:5`. Swap Check даёт min/max, q и byte frame. Битовые корни дают канонический порядок, popcount и frame префикса. Для всех порогов `P_t(x)=[x≥t]` каждая из 45 min/max операций проецируется в AND/OR. Если бы в результате осталась инверсия `x_i>x_j`, её обнаружил бы порог `x_j+1`. Совпадение всех пороговых счётчиков даёт полные кратности байтов. Хвост до вставок сохранён. [Опоры и расписание](REV2-N26-N31-HALVES-HANDOFF.md#все-45-вызовов-s13)

**Вставки.** Слева берётся префикс исторического B01/L16, справа внешний перенос B17→B14/B15/B16 и первые шаги actual цикла до собственного end. Historical insert roots исполняют `rev2_n32_consumer.rs:84:5` на своём пине, текущие драйверы имеют тот же байтовый блок на `:90:5`. Их посты дают порядок, `count(<q)`, q/frame и возврат. Для фиксированных данных поведение независимо от q, поэтому разности соседних счётчиков и `L−count(<255)` дают полные кратности. `smallsort.rs:759–764` сравнивает tail с one-past-end и вызывает `insert_tail::<u8, KeyLess<u8>>`. До шага r префикс `[0,r)` упорядочен, хвост и frame сохранены. При сдвиге `:715` читает tail в отдельный tmp, `:722` копирует инициализированный байт из `sift` в соседнюю дыру, а `:725–732` ограничивает продвижение `begin`. `CopyOnDrop` копирует tmp в дыру на `:362:13`. Все записи в `[0,r]`, шаг сохраняет кратности и даёт упорядоченный `[0,r+1)`. Инициализация source и tmp следует из фактических записей при `uninit OFF`. Исторический cover относится к rel13. Свидетель с тринадцатью тройками и хвостом `2,1,0` даёт 13, 14 и 15 последовательных сдвигов на соответствующих поздних rel. Самостоятельные insert roots B14–B16 имеют статус `NOT_RUN`. [Драйверы и перенос](REV2-N26-N31-HALVES-HANDOFF.md#actual-вставки-и-решение-по-roster)

**Merge.** Actual `:424:9` получает две упорядоченные половины и отдельный writable D. Инициализация курсоров начинается на `:1014`, pair calls на `:1023/:1024` привязаны к helper copies `:885/:918`. Check каждого N покрывает `0≤a,c≤k<m`, `a+b=c+d=k` и две цели D[k], D[N−1−k]. Up выбирает левый элемент на tie, down выбирает правый. Внешняя индукция по `(byte, индекс в S после вставок)` даёт до пары k уже записанные k нижних и k верхних рангов. При `k<m` все четыре адреса находятся в половинах. У исчерпанной половины прямой кандидат уже взят сверху, обратный уже взят снизу и оба проигрывают выбор очередного экстремума. Две actual копии берут различные оставшиеся ранги и пишут в разные цели. После m пар при чётном N заполнены все D[0..N] и оба равенства guard выполнены. Pair Check даёт min/max, изменения курсоров, exact bounds, q/source frame и write set. Stock `ProofForContract` target/symbol, frozen regex по `target_instance` для `single_top_level_call` и `no_recursive_call`, строка `modifies` и столбец 1 дают независимые якоря. Имя функции из ID дополнительно сверяет согласованность двух полей regular. [Допуск merge](REV2-N26-N31-MERGE-ADMISSION.md#привязка-нативных-опор-к-actual-циклу) · [Комментарий гейта](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/results.py:219)

| N | Pair target | `modifies` | Up/down cursors | Native ID суффиксы cursor checks |
| ---: | --- | ---: | --- | --- |
| 26 | `actual_pair_step_n26` | 14:1 | 32:9 / 40:9 | `.assertion.7/.10` |
| 27 | `actual_pair_step_n27` | 134:1 | 152:9 / 160:9 | `.assertion.7/.10` |
| 28 | `actual_pair_step_n28` | 254:1 | 272:9 / 280:9 | `.assertion.7/.10` |
| 29 | `actual_pair_step_n29` | 374:1 | 392:9 / 400:9 | `.assertion.7/.10` |
| 30 | `actual_pair_step_n30` | 494:1 | 512:9 / 520:9 | `.assertion.7/.10` |
| 31 | `actual_pair_step_n31` в `rev2_merge_pair_fixed.rs` | 387:1 | 413:9 / 423:9 | `.assertion.7/.10` |

**Нечётный центр.** Остатки `(m−a−c,m+1−b−d)` после m пар равны `(1,0)` или `(0,1)`. Транскрипция `smallsort.rs:1027–1036` выбирает единственный ранг m для D[m], копирует на `:1034` и продвигает выбранный курсор. Оба равенства actual guard на `:1042` проверяются в harness отдельно. Левый witness даёт `(0,m,m−1,1)` и источник S, правый sentinel даёт `(0,m,m,0)` и источник `S+N−1`. При `c=m` `left_rev=S−1` участвует только в `wrapping_add(1)`, который даёт `left_end=S`. Контрольный правый остаток даёт `(m−1,1,1,m−1)` и источник `S+m+1`. В odd fixture `less` остаётся вне вызова wrapper, поэтому его локальный `Q_FRAME` относится только к fixture. Actual q-frame центра следует из отсутствия вызовов компаратора в ветке. До допуска каждой строки нужен native whole-network `less.q()==q`. [Нечётные опоры](REV2-N26-N31-MERGE-HANDOFF.md#roster-и-нативная-привязка) · [Ревью Q_FRAME](REV2-N26-N31-MERGE-REVIEW.md#неблокирующее)

| N | Selected source / value | Два конечных equality anchors | Sentinel / post-copy |
| ---: | --- | --- | --- |
| 27 | 698:5 / 699:5 | 700:5 / 704:5 | 712:5 / 719:5 |
| 29 | 810:5 / 811:5 | 812:5 / 816:5 | 824:5 / 831:5 |
| 31 | 922:5 / 923:5 | 924:5 / 928:5 | 936:5 / 943:5 |

Координаты центров и pair N26–N30 относятся к `rev2_n26_n31_merge.rs`. Exact pair и odd Checks имеют успешные scoped `memcpy.assigns.1/.2`, шесть grouped свойств `ptr::copy_nonoverlapping::<u8>` и четыре unwind ID. Source и read/write bounds связывают group с обоими actual вызовами пары или с однобайтовым вызовом центра. Различные целевые адреса и ранговая индукция дают полную запись D[0..N] до чтения при `uninit OFF`. [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

**Copy-back и открытые обязательства.** Actual `ptr::copy_nonoverlapping::<u8>(scratch_base,v_base,N)` на `smallsort.rs:425:9` следует сразу за merge. Scratch32 и V34 раздельны, size/alignment u8 равны 1, место назначения writable, первые N scratch-байтов записаны по рангам. Это связывает exact N и размещение областей на всём байтовом домене с grouped ID `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14`. У всех 12 корней gate требует `SUCCESS` для `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` и `SATISFIED` для `AFTER_COPY_BACK`. Ожидаемый конечный пост даёт числовой порядок, полное исходное мультимножество и сохранение `q`, `v[0]`, `v[1+N..34]`. Открыты нативные результаты последнего copy-back, whole-network q/frame и отличающий контроль каждой длины. Полнота записи scratch при `uninit OFF` и переносы на полные байты остаются внешними шагами. Доказательный зачёт `NONE`, `stub_verified` целевых контрактов и допуск в pr752 за пределами этого пакета. [Copy-back прецедент](REV2-N22-N25-ADMISSION.md#привязка-к-полным-байтам)

## Исторические нативные опоры

Таблица задаёт суффиксы regular IDs и member SHA-256 из опубликованных структурированных индексов. Сверены SHA-256 семи индексов, размеры и SHA-256 40 членов receipt/projection. Stock и regular привязки промежуточных корней сохраняют прежние пины и координаты. Результаты ниже относятся к соответствующим exact опорам. [Исторические пины половин](REV2-N26-N31-HALVES-HANDOFF.md#blobs-и-исторические-свидетельства) · [Пин M31](REV2-N26-N31-MERGE-HANDOFF.md#проверка-исторического-m31-pair-fixed)

| Ребро / слот | Native ID-якорь | Receipt SHA-256 | Projection SHA-256 |
| --- | --- | --- | --- |
| `S13-SWAP-LEAF` | `s13_swap_leaf.assertion.1–3`, `.cover.1–5`, `call_mut.cover.1` | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |
| `S13-BASE1-BITS` | `check_s13_base1::<false>.assertion.3/.6/.8/.9`, `.cover.1–3`, `call_mut.cover.1` | `66fbadf4bb9ef514bb367f35d50da6e2f421c17266aa3ca03f3228af12fd7ddd` | `33875cb4ad55dfa468410b6083fc3c92f50bf2b0359fe903c4013a62380a2bf2` |
| `S13-B01-L17-BITS` | `check_bits::<1,17,false>.assertion.5/.8/.11/.12`, `.cover.1–3`, `call_mut.cover.1` | `119b822970d1386f3d15e5edefefaf847d4ee63a5358610f0bd9e22880c63c79` | `6c37276170ebe94470fa4a1d17b92bc09e05e5ac6b66d22aadd21508f255696a` |
| `N32-INSERT-LEFT-BYTES` | `check_insertions::<1>.assertion.3–6`, `.cover.1–2`, `call_mut.cover.1` | `7cac457115063a8ffb3f46ff207c23f0361523a93c7d73395f6b7115639c4f4e` | `6b407b8d1f9e6ffa67786e07e06fd1a91e373f72527df8dd93bc9afbae0d3f40` |
| `N32-INSERT-RIGHT-BYTES` | `check_insertions::<17>.assertion.3–6`, `.cover.1–2`, `call_mut.cover.1` | `3bcb3d314501ddb8d35bfc01396bfba094b2a65cd8ade7e54f4763ceac1b6a84` | `0a7a7f482845d9f4609b9a83b1856b12cc81489146693e39ab48dc7cc2946c25` |
| `S13-B14-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<14>.assertion.1` | `5df30e8896b69fb8131e34b1a6863bca4d60d34988c5def0e1c484c4f5a235b7` | `2108accffc6dff8117c1eac6cd615eba1c01095cf20a354de94fd89788d161a3` |
| `S13-B14-L14-BITS` | `check_bits::<14,14>.assertion.5/.8/.11/.12`, `.cover.1–3` | `390bbc1fd2f2660e48656ff54522f5fc5ab0d4738f50f44f4b2b1f14e640bb7e` | `833eab67b3aab06fb333fd2bd7c1817045df2122b22a8c58f981dcb0cd3bdd5a` |
| `S13-B15-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<15>.assertion.1` | `17e49991b94b7e913ecb78b45035be07bb277d9fdd2361684c309f80004c38f1` | `a745ac861dfe32ee6242539a14aa5b3acb4d2e0be85b17b35675827168b18828` |
| `S13-B15-L15-BITS` | `check_bits::<15,15>.assertion.5/.8/.11/.12`, `.cover.1–3` | `d5861a93d0fbc65e1bc8e9c0206a9a5b0753dc4672bb80651fc22d8d14895f5b` | `1be1248b7de5ce66bc3687a50cae84e3f367189ceb289cc983b0ec75dc8b53a3` |
| `S13-B16-SWAP` | `swap_if_less::<u8,KeyLess<u8>>::{closure#2}.assertion.1`, `assert_swap_post::<16>.assertion.1` | `f80cfd703e427643364deecd187898f3a123bf9aaa2f42b204e9f2751723b5a9` | `d5dc5e926e13ae3dfbb29c2eff1c81bd3b51bd8607c32b5e27be20542ab38ed3` |
| `S13-B16-L16-BITS` | `check_bits::<16,16>.assertion.5/.8/.11/.12`, `.cover.1–3` | `97a7ed5967be72aeef86b59b79db2f491f818cfaff72240042f6fb0cd5bac48a` | `f1043e658ca2ecaadffa83eb5d1733fd4dd10230d8bc17104e5adb54a28d4254` |
| `N26-PAIR-FIXED` | `n26_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `0ee400de2eb10b6ab63a855aaf52ca4d087511238777e5301f48c5db85353814` | `7701d3c6bc41f35e6d612059845bbb7327bcc4372360a0b2e0bc2c705446496f` |
| `N27-PAIR-FIXED` | `n27_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `7791ceedba14562ceb01ba350793d06fec1a5716c5be7eae97047dfb6f2c4c38` | `9c3240db539bfdab83a5aff041a3d012035d9a5375edd65f79b1c641a057a94c` |
| `N28-PAIR-FIXED` | `n28_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `d9c027132b5fbd734f59bac0c3c5bc745d34324a52e5517ea3dba8c9d7f0d85d` | `1fcd354bdf746646c1e359d653cd045317931704f7f01e741b3d50eda1edecfd` |
| `N29-PAIR-FIXED` | `n29_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `7c9f6678b8b6ba98677ceb505d7b40fdb325b78f24a7751979ab7549436614df` | `858440f4422ed5b43cea473e630dc680bab1f72dad36dc2af6a1f734cd2d9a5e` |
| `N30-PAIR-FIXED` | `n30_pair_fixed.assertion.1/.2/.3/.10/.15–18`, `.cover.1–10` | `b040533d768b474b127edf64429db83b6b85e6aa91536be7077619ce9bd244a5` | `bfc36ef774cdfeb7f8e7f508c146f923dca48d00fc2f17052a2002d789a4e400` |
| `N27-ODD-CENTER` | `n27_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `219482289b26d670581a9bed774745c01039a873ed3240ae65c3cd27647a73a8` | `c396f50813f1d9f4ffeb111a585ce5dbcc49c1c6dc0c07c9784b3b6ec9c79490` |
| `N29-ODD-CENTER` | `n29_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `a5e54adbfc95a7dfa3974030da1bea6d492ecd41451fc696928126843fce6a46` | `afdbf8c0f1cdaacbf68c3e8151078ff13134652a82f66cad97a1107a2bd2d167` |
| `N31-ODD-CENTER` | `n31_odd_center.assertion.1/.2/.3/.13/.15/.18–23`, `.cover.1–4` | `898d35ebfe8f0ad52595c4dbfc7fe82e5c6ab37d1fc37ad5622945319e00f4c5` | `b5bad24884bf427be3eac32405f4ceb610c5b9c70492eb4b2980e017fa76d417` |
| `M31-PAIR-FIXED` | `m31_pair_fixed.assertion.1/.2/.3/.14–17`, `.cover.1–10`, actual cursor closure `.assertion.7/.10` | `e1e2e1842e37c1d1669ad322306ca72d4388759c86ac0fd308042bcf74f227a1` | `2a9c504abf5bba1fb27d2633a02de6912dd68f1469bccf9244711cebd60e2ca4` |

| Run / attempt | Опора | SHA-256 индекса |
| --- | --- | --- |
| [45846512615/1](/root/ch8-artifacts/run-45846512615/ch8-rev2-n26-n31-halves-Linux-X64-45846512615-1/index.json) | halves | `452059d4c406b9f75455ae00cdc1e68709f28874890a254374b35f5550a57d79` |
| [45861423438/1](/root/ch8-artifacts/run-45861423438/ch8-rev2-n26-n31-merge-Linux-X64-45861423438-1/index.json) | merge | `28799cedd217692c009f36282bf31d8ca2fc9c2ec15f29f86d822a1a5bc22222` |
| [45785063793/1](/root/ch8-artifacts/run-45785063793/ch8-rev2-merge-pair-fixed-Linux-X64-45785063793-1/index.json) | M31 pair | `ded8803087eab9aedcc2bfcda6dd1d5184fc6e6b640f796bd206a391fc313c06` |
| [45661535099/1](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) | B01 swap leaf | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` |
| [45676394046/1](/root/ch8-artifacts/run-45676394046/ch8-rev2-s13-binding-Linux-X64-45676394046-1/index.json) | B01/L13 bits | `bcb05483715c3b6067586c26059f2b341f84b6c3a6b5ba7018db0395258f89d6` |
| [45688753097/1](/root/ch8-artifacts/run-45688753097/ch8-rev2-s13-geometries-Linux-X64-45688753097-1/index.json) | B01/L17 bits | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` |
| [45710831239/1](/root/ch8-artifacts/run-45710831239/ch8-rev2-n32-consumer-Linux-X64-45710831239-1/index.json) | N32 insertion drivers | `9145808434de22a0cc31f8f15630c7510e723dd870862cb06d59d5624ce7bfa6` |

## Профиль и часы

Одна job на `ubuntu-24.04` с пределом 120 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach включены. Uninit и validity выключены. Stubs, Replace и loop contracts отсутствуют во всех 12 корнях. У каждого слота собственные cold CWD, Cargo/Kani targets, TMPDIR и export. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [Runner](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/run.py:438)

| Стадия | Граница от monotonic epoch | Внешний timeout |
| --- | --- | --- |
| Setup с ранним compile preflight и discovery | 54:00. До 180 с на preflight с сохранением первых rustc diagnostics при отказе. | Prepare 56 мин |
| Входной gate measure | До 55:00 и ≤60 с от входа | В составе measure |
| 12 слотов и финальная аттестация | Конец слотов 96:00, конец аттестации 98:00, `measure` ≤44:05 от входа | Measure 46 мин |
| `finish` и `upload-gate` | Общий cutoff 102:55, `finish` ≤5:00 от входа | 6 мин и 1 мин |
| Upload, резерв и job | Переход 5 с, абсолютный конец upload 110:00, план 119:00 с резервом 9 мин | Upload 7 мин, job 120 мин |

Каждое окно 205 с включает 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. Измерение ограничено ≤120 с VT, ≤4 GiB группы, резервом 2 GiB. Linux RSS группы может быть занижен при смене worker TID. Проекция ограничена 4 MiB, артефакт — 96 MiB. Checkpoint исхода и подтверждение reap сохраняются до проекции. Отложенная запись повторяется в ограниченном окне `finish`, а оригинальный late receipt остаётся вне профиля. Ретрай и задержка receipt не пересчитывают latest starts. При раннем входе внутренние 44:05 дополнительно ограничивают весь шаг measure. [Часы и checkpoint](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/run.py:100)

`CONSUMER_PAIRS_WITHIN_PROFILE` требует 12 `MATCHED`, ожидаемые exit codes, полные timely anchors и receipts, подтверждённые sampler/reap, ресурсные пределы и своевременную аттестацию `COMPLETE`. Если N31 positive упрётся в cap, его receipt сохранит наблюдённый native исход и phase/CNF, group/CBMC RSS и PSS в пределах имеющейся телеметрии. При подтверждённом reap отдельный N31 контроль и последующие слоты остаются в очереди со своими окнами. Без подтверждения reap следующие слоты получают `PROCESS_CLEANUP_COULD_NOT_BE_VERIFIED`. Составной вариант с отдельным exact copy-back/frame root остаётся за анализом такого исхода. [Приёмка](/root/kani-rev2-n26-n31-consumer-control-w15/ch8-cal1/report.py:108) · [Ресурсный ориентир N31](REV2-N22-N25-ADMISSION.md#запас-памяти-для-n26n31)

## Проверки перед сдачей

- Вручную сверены доступность `small_sort_network` через `super::super`, видимость `KeyLess<u8>::with_q/q`, корневой `cfg(kani)`, цепочка из 18 opt-in cfg, exact срезы и типы обеих специализаций. Runtime, старые контракты и опоры побайтно совпадают с Std merge. Дельта состоит из нового модуля, его регистрации и check-cfg декларации. Пин rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max`, `git diff --check`, YAML без дубликатов, `bash -n` для 8 shell-блоков и AST всех 15 Python файлов прошли.
- Bare shallow Std depth 2 на локальном Git transport без alternates прошёл `bundle verify/list-heads/unbundle`. Единственный объявленный ref — HEAD кандидата. Prerequisite — Std CI-base. HEAD, refs и shallow boundary сохранены. Сверены 19 троек commit/tree/sole-parent, 20 текущих source blobs и historical mappings, 280 текстовых координат и 250 native label координат с учётом exact instances. Любой одиночный сдвиг столбца на +1 отклонён.
- Офлайн-модель прочитала 45 actual пар S13, сверила их порядок с `SWAP_PAIRS` и перебрала 8192 входа S13 на битах. 1399 пар отсортированных половин дали distinct ранги, полный D и оба равенства guard, включая все 27, 29 и 31 допустимых терминальных состояния нечётных N. Сверены шесть контрольных масок и XOR, сдвиги единицы в хвостах, все девять odd состояний из witness/control masks и источники центра. Для поздних rel подтверждены сдвиги на хвосте `2,1,0`.
- На структурированном historical discovery run 45861423438 приняты 78 унаследованных REV2 записей, включая все 8 exact `MERGE_CHECKS`. Добавление 12 синтетических plain Proof даёт ожидаемую дельту. Синтетика отклоняет contract target при верных selector/kind/file у standard, чужие Check target/file, смещение native координаты, потерю copy anchor, after-copy-back или odd cover и дополнительный failure. Отдельно проверены late receipt, потеря reap, exact payload/tree и общий finish/upload cutoff.
- На финальном detached review-trigger точный локальный блок `pins` прошёл за 133,707 с. Suite последовательно дал 122/122 на обычной шкале и на свежих шкалах 1, 5 и 60 с за 33,527 / 32,192 / 31,189 / 33,434 с. Синтетические `finish`, `upload-gate` и `upload-check` прошли. Индекс содержит 12 `NOT_STARTED`, 6 `OPEN` пар и 15 членов с совпавшими размерами и SHA-256. Итог синтетики `CONSUMER_PAIRS_OPEN`.

Локальная валидация ограничена статикой, Git, моделью и Python/shell синтетикой. Cargo, rustc, Kani, CBMC, CI и push не запускались. Actions variables не менялись. Для нативного запуска нужны независимое ревью и отдельный GO координатора.
