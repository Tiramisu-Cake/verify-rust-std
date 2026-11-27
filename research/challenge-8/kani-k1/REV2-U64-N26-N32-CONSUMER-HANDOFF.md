# REV2 · составной consumer u64 N26–N32

**`READY_FOR_REVIEW` · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Одна Ubuntu job содержит семь контролей с порчей после возврата фактической сети и семь локальных copy-back/frame. У контроля на каждую длину один фиксированный активный вход. Локальная копия принимает произвольные полные слова scratch-префикса и V34. Связь с полным доменом сети требует нативных опор и внешних шагов ниже. Запуск требует независимого ревью, отдельного GO и очереди координатора. [Задание](REV2-U64-N26-N32-CONSUMER-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md) · [Допуск N22–N25](REV2-U64-N22-N25-ADMISSION.md)

## Пины пакета

| Роль и checkout | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15) | `727137f7efd6f5feb05eb7b3db4f3875c8699675` | `50089d49d2be1058df3f271abef7d0bfc9ee57d4` | `72bb79d26dd495d0461c6e6d3c05d21c2d1b1878` |
| [Control](/root/kani-rev2-u64-n26-n32-consumer-control-w15) | `5d58830f278d18a9080c61b4d791f94101e0c4c4` | `4e4a20091835954aa9ff6847b11b7a572c9fc277` | `f50d86dffac4c1265797189511feaec8bba9d09b` |
| [Review-trigger](/root/kani-rev2-u64-n26-n32-consumer-trigger-w15/control), detached | `1b7c50edeec64700a81160ceb8c869ddf7c21cf2` | `4e4a20091835954aa9ff6847b11b7a572c9fc277` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Задание на g0 `b5524a234e22bb3f6088f66eb62da9c667c5a34c`. Деревья баз Std и Control FIX1 `c513d0ec1a137457add28b2b9ee9c47ac23642d3` и `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`. Bundle объявляет единственный `HEAD` и несёт 28 последовательных overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n26-n32-consumer-trigger-w15/control/ch8-cal1/CI-REQUEST.json) | `146a55a545430a8d3ad5980f35026bf2230d773b28e2aea57f420e523807ad63` |
| Exact roster, канонический JSON | `98a0b9778547cc039fd3364e273d2d52657bb361a40972ca5de7bae37a440e25` |
| Source bindings, канонический JSON | `b02f99ad69480beca5a963a91b0fa48acef42f28f9299eb6a92d4aac1ff5db9f` |
| [Std bundle](/root/kani-rev2-u64-n26-n32-consumer-trigger-w15/control/ch8-cal1/std-overlay.bundle), 76 830 байтов | `b7292e6c50cf0562dec5669b909878d543ba145afd11794745998e34554f53f6` |
| [Workflow](/root/kani-rev2-u64-n26-n32-consumer-trigger-w15/control/.github/workflows/ch8-q-pilot.yml) | `d99fc9f50fe334e7cc37bea003978bf29d10aa0f8b7f3233f676fc2db9cd223c` |

Независимый pin `CH8_REV2_U64_N26_N32_CONSUMER_TRIGGER_TREE` связывает `pins`, `sources`, `finish` и `upload-gate` с деревом Control. Входы требуют `Tiramisu-Cake/kani`, событие push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, чистый detached HEAD, совпадение HEAD, payload `after` и `GITHUB_SHA`, точный единственный parent. Перед prepare, measure, finish и upload-gate сверяется admission receipt. Индекс `smallsort-rev2-u64-n26-n32-consumer-artifact-v1` фиксирует четыре хэша входов, trigger и полный инвентарь. Upload-gate перепроверяет содержимое индекса и request.

## Exact roster и исходные координаты

Префикс `slice::sort::shared::smallsort::verify::rev2_u64_n26_n32_consumer::`. Cfg-on сохраняет 149 исторических записей управляемого roster с kind, source и Check targets и добавляет ровно 14 `standard-harnesses` с пустыми targets. Полный multiset cfg-off/cfg-on покрывает остальные записи discovery. Все 14 слотов — plain Proof, unwind36, `copy_back=true`, без Check, Replace и stubs. Колонка Root содержит координату атрибута proof. [Модуль consumer](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n26_n32_consumer.rs)

| Слот | Суффикс selector | Root | Ожидаемый исход | Latest start |
| --- | --- | --- | --- | --- |
| `U64-N32-WITNESS-CORRUPT` | `u64_n32_witness_corrupt` | 13:1 | FAILED, exit 1 | 55:00 |
| `U64-N31-WITNESS-CORRUPT` | `u64_n31_witness_corrupt` | 19:1 | FAILED, exit 1 | 58:25 |
| `U64-N30-WITNESS-CORRUPT` | `u64_n30_witness_corrupt` | 25:1 | FAILED, exit 1 | 61:50 |
| `U64-N29-WITNESS-CORRUPT` | `u64_n29_witness_corrupt` | 31:1 | FAILED, exit 1 | 65:15 |
| `U64-N28-WITNESS-CORRUPT` | `u64_n28_witness_corrupt` | 37:1 | FAILED, exit 1 | 68:40 |
| `U64-N27-WITNESS-CORRUPT` | `u64_n27_witness_corrupt` | 43:1 | FAILED, exit 1 | 72:05 |
| `U64-N26-WITNESS-CORRUPT` | `u64_n26_witness_corrupt` | 49:1 | FAILED, exit 1 | 75:30 |
| `U64-N32-COPY-BACK-FRAME` | `u64_n32_copy_back_frame` | 55:1 | VERIFIED, exit 0 | 78:55 |
| `U64-N31-COPY-BACK-FRAME` | `u64_n31_copy_back_frame` | 61:1 | VERIFIED, exit 0 | 82:20 |
| `U64-N30-COPY-BACK-FRAME` | `u64_n30_copy_back_frame` | 67:1 | VERIFIED, exit 0 | 85:45 |
| `U64-N29-COPY-BACK-FRAME` | `u64_n29_copy_back_frame` | 73:1 | VERIFIED, exit 0 | 89:10 |
| `U64-N28-COPY-BACK-FRAME` | `u64_n28_copy_back_frame` | 79:1 | VERIFIED, exit 0 | 92:35 |
| `U64-N27-COPY-BACK-FRAME` | `u64_n27_copy_back_frame` | 85:1 | VERIFIED, exit 0 | 96:00 |
| `U64-N26-COPY-BACK-FRAME` | `u64_n26_copy_back_frame` | 91:1 | VERIFIED, exit 0 | 99:25 |

| Нативная привязка | Координаты |
| --- | --- |
| Общий cover компаратора `REV2_U64_N13_COMPARATOR_CALLED` | `rev2_u64_n13.rs:9:5`, `u64_less`. |
| Контроль: mixed / actual network / `AFTER_COPY_BACK` | `105:5` / `108:5` / `109:5`, `check_witness_corrupt::<N>`. |
| Контроль: canonical / expected mask до порчи | `111:5` / `112:5`, тот же instance. |
| Контроль: порча / V34 frame / canonical после порчи | `114:5` / `116:5` / `118:5`, тот же instance. |
| Контроль: `REV2_U64_Nxx_ACTUAL_SORTED_POPCOUNT` | N26 `120:9`, N27 `122:9`, N28 `124:9`, N29 `126:9`, N30 `128:9`, N31 `130:9`, N32 `132:9`. Требуется единственный `FAILURE` класса `assertion` с одним ID, меткой, файлом и строкой в regular и stock. |
| Локальный typed copy | `172:14`, `check_copy_back::<N>`. Actual runtime copy на `smallsort.rs:425:9`. |
| Локальные посты `DEST_EQUALS_SOURCE`, `SOURCE_PREFIX_FRAME`, `V34_FRAME` и cover `AFTER_COPY_BACK_FRAME` | `181:5`, `182:5`, `185:5`, `186:5` того же instance. |
| Grouped typed copy | Во всех 14 слотах требуются шесть `SUCCESS` для `ptr::copy_nonoverlapping::<u64>` на `ptr/mod.rs:587:14` и `SUCCESS` у всех выведенных unwind checks при stock unwinding ON. |

Actual blobs `smallsort.rs` и `ptr/mod.rs` совпадают с FIX1, соответственно `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` и `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6`. Новый модуль `991235d9e4e921ebc48d9d196f5359480595e4fe`. Registry `fb20a9974eaddb538ebd26f75e5eb08a0401eb03` добавляет две строки под `cfg(kani)` с зависимостью от cfg `u64_less` в `verify.rs:313–314`. Manifest `729a3d9c3d782794829891c3c7525315f8b7ea96` добавляет только check-cfg на строке 74. Побайтное вычитание этих строк восстанавливает оба старых файла.

## Полный домен и внешние шаги

Домен для каждой N — эксклюзивный `v[1..1+N]` живого инициализированного `V=[u64;34]`. Пусть `S=&v[1]`, `m=N/2`, `D` — база отдельного живого scratch32. Компаратор `u64_less` реализует полный непаникующий числовой `<`. Пост нормального возврата — неубывающий числовой порядок, сохранение каждой входной кратности и неизменность `v[0]` и `v[1+N..34]`.

| N | Левая половина и rel вставок | Правая половина и rel вставок | Merge и copy-back |
| --- | --- | --- | --- |
| 26 | `v[1..14]`, ∅ | `v[14..27]`, ∅ | 13 пар, 208 байтов |
| 27 | `v[1..14]`, ∅ | `v[14..28]`, 13 | 13 пар, `D[13]`, 216 байтов |
| 28 | `v[1..15]`, 13 | `v[15..29]`, 13 | 14 пар, 224 байта |
| 29 | `v[1..15]`, 13 | `v[15..30]`, 13–14 | 14 пар, `D[14]`, 232 байта |
| 30 | `v[1..16]`, 13–14 | `v[16..31]`, 13–14 | 15 пар, 240 байтов |
| 31 | `v[1..16]`, 13–14 | `v[16..32]`, 13–15 | 15 пар, `D[15]`, 248 байтов |
| 32 | `v[1..17]`, 13–15 | `v[17..33]`, 13–15 | 16 пар, 256 байтов |

1. **Регионы и S13.** Во всём диапазоне `no_merge=false`. Actual `smallsort.rs:394–417` проходит сначала длину m, затем N−m. Оба региона удовлетворяют `len>=13` и проходят те же 45 литеральных сравнений `sort13_optimal`. Слева используются B01 bits/swap и переносы L13→L14/L15/L16. Справа по таблицам ролей используются B14, B15, B16, B17 bits/swap, а для укороченных регионов B14 L14→L13, B15 L15→L14 и B16 L16→L15. У каждого переноса сохраняются база, guard, 45 пар в первых 13 словах и скалярный frame хвоста. Для каждого порога t проекция `x>t` переводит min/max в AND/OR. Любая инверсия x>y дала бы битовую инверсию при t=y. Полноширинные min/max сохраняют кратности входной пары, а frame сохраняет остальные слова. [Actual цикл](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:394)
2. **Драйвер и вставки.** Actual `smallsort.rs:742–769` стартует с `tail=base+13`, `end=base+len`. На длине 13 `tail==end` на входе. На остальных длинах берутся смещения из таблицы, по одному в порядке возрастания. S13 инициализирует предпосылку упорядоченности первых 13 слов. Перед relR префикс `[0,R)` отсортирован, а слово tail произвольно и инициализировано. Пост relR расширяет отсортированный префикс, сохраняет кратности и оставляет следующее слово неизменным. Слева применяются B01 REL13/14/15. Справа применяются девять переносов ниже. [Actual драйвер](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:742)
3. **Merge pair.** После вставок упорядочим позиции по `(слово, индекс после вставок)`. Up при равенстве берёт слева, down справа. В паре k, где `0≤k<m`, up уже потребил a слева и b=k−a справа, down потребил c слева и d=k−c справа. Относительные адреса кандидатов равны `a`, `m+b`, `m−1−c`, `N−1−d`. Все читаемы, поскольку каждый обход по отдельности потребил не больше k на половину. По индукции up и down выбирают ранги k и N−1−k. Пара записывает их в разные слова `D[k]` и `D[N−1−k]`, сохраняя источник и остальные D-ячейки. Exact N-специализация связывает два нативных site actual `smallsort.rs:885:9` и `:918:9` с этим шагом. [Actual merge](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:1022)
4. **Курсоры и центр.** При чётном N после m пар `a+c=m`, `b+d=m`, и обе пары курсоров достигают равенств в `smallsort.rs:1042`. При нечётном N остатки `(m−a−c, m+1−b−d)` равны (1,0) или (0,1). Условие `left<left_end` выбирает forward cursor стороны с остатком. Копируется одно слово ранга m в `D[m]`. Выбранный курсор продвигается, после чего `a'+c=m`, `b'+d=m+1` и выполнены оба равенства. При c=m reverse left образует wrapping sentinel `S−1`, его `wrapping_add(1)` даёт S. Чтение происходит только из выбранного forward cursor. Для N27, N29 и N31 собственные нативные copy sites находятся на `rev2_u64_n26_n32_providers.rs:1018:9`, `:1104:9`, `:1190:9`. Каждому соответствует внешнее `transcribes: smallsort.rs:1034:13`. [Координаты опор](REV2-U64-N26-N32-PROVIDERS-HANDOFF.md#exact-roster-и-нативные-якоря)
5. **Инициализация scratch, копия и frame.** Записи пар и нечётная запись покрывают ровно ранги 0…N−1, поэтому `D[0..N]` записан до чтения. Это внешний вывод при uninit OFF. Actual `smallsort.rs:425:9` выполняется после нормального возврата merge. Его `scratch_base`, `v_base` и `len` определяются размещением и длиной без зависимости от слов. Отдельные живые объекты размером 256/272 байта и выравнивание 8 дают точный диапазон `D[0,8N) → V[8,8+8N)`. Локальная копия использует то же количество полных слов, а её посты проверяют destination, scratch prefix и V34 frame. В контроле cover возврата проходит через безусловную actual copy, соотнесённую с общими grouped ID typed copy. Итоговый frame следует из того, что половины пишут в активный срез, merge пишет в D, а copy-back пишет в активный срез. Упорядоченность и кратности следуют из состава S13, вставок, записи по рангам и точной копии. [Actual copy-back](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:425)

### Девять переносов вставок

R1 принял эти рёбра по исходнику при выполнении предпосылок. В каждом ребре `v[1+j] → v[B+j]` при `0≤j≤R` остаётся внутри живой половины на базе V34. Сдвиг кратен 8 байтам. Actual `insert_tail` начинает с `sift=tail−1`, сравнивает те же относительные слова полным строгим `<` и останавливается на `sift==begin` или при найденном месте вставки. Копии сдвигают слово между соседними непересекающимися ячейками. Отдельный tmp и `CopyOnDrop` заполняют зазор и сохраняют все прочие слова. На максимальном B17/rel15 диапазон `v[17..33]`, tail `v[32]`, end `v+33`. [Вердикт R1](REV2-U64-N26-N32-PROVIDERS-REVIEW.md#r1) · [Actual insert_tail](/root/verify-rust-std-rev2-u64-n26-n32-consumer-w15/library/core/src/slice/sort/shared/smallsort.rs:701)

| Ребро из B01 | Сдвиг, байты | Слова V источника → цель, включительно | N |
| --- | --- | --- | --- |
| rel13 → B14/rel13 | +104 | 1…14 → 14…27 | 27 |
| rel13 → B15/rel13 | +112 | 1…14 → 15…28 | 28, 29 |
| rel14 → B15/rel14 | +112 | 1…15 → 15…29 | 29 |
| rel13 → B16/rel13 | +120 | 1…14 → 16…29 | 30, 31 |
| rel14 → B16/rel14 | +120 | 1…15 → 16…30 | 30, 31 |
| rel15 → B16/rel15 | +120 | 1…16 → 16…31 | 31 |
| rel13 → B17/rel13 | +128 | 1…14 → 17…30 | 32 |
| rel14 → B17/rel14 | +128 | 1…15 → 17…31 | 32 |
| rel15 → B17/rel15 | +128 | 1…16 → 17…32 | 32 |

## Трассы контролей

На входе единицы в `S+0` и `S+m`, остальные активные слова нули. Actual S13 переносит единицу с rel0 на rel12 первым обменом 0–12. Остальные обмены оставляют её на rel12. Каждая непустая итерация драйвера вставляет очередной ноль, сдвигая ровно одну единицу на следующее слово. Так обе половины заканчиваются одной единицей. Индексы up/down ниже даны относительно S.

| N | Входная маска | Up | Down | Центр | До → после порчи |
| --- | --- | --- | --- | --- | --- |
| 26 | `0x0000_2001` | `0…11,13` | `25,12,24…14` | ∅ | `0x0300_0000 → 0x0300_0001` |
| 27 | `0x0000_2001` | `0…11,13` | `26,12,25…15` | `S+14` | `0x0600_0000 → 0x0600_0001` |
| 28 | `0x0000_4001` | `0…12,14` | `27,13,26…15` | ∅ | `0x0c00_0000 → 0x0c00_0001` |
| 29 | `0x0000_4001` | `0…12,14` | `28,13,27…16` | `S+15` | `0x1800_0000 → 0x1800_0001` |
| 30 | `0x0000_8001` | `0…13,15` | `29,14,28…16` | ∅ | `0x3000_0000 → 0x3000_0001` |
| 31 | `0x0000_8001` | `0…13,15` | `30,14,29…17` | `S+16` | `0x6000_0000 → 0x6000_0001` |
| 32 | `0x0001_0001` | `0…14,16` | `31,15,30…17` | ∅ | `0xc000_0000 → 0xc000_0001` |

Первые m−1 шагов up берут левые нули при равенстве. Последний шаг up берёт правый первый ноль. Down сначала берёт правую единицу при равенстве, затем левую единицу над правым нулём, затем правые нули при равенстве. Поэтому после m пар `(a,b,c,d)=(m−1,1,1,m−1)`. Для N27/29/31 left достигает left_end, и центр читает правый остаток `S+m+1`. Для N26/28/30/32 обе стороны уже достигли своих ends. Оракул вычисляет исходный popcount и ожидаемую скалярную маску с `low=(1u64 << N) - 1`. Операция `v[1] ^= 1u64` меняет только младший бит при сохранении каноничности и frame.

## Границы циклов

| Цикл или этап | Максимум на экземпляр |
| --- | --- |
| Инициализация контроля, каждый из двух `observe_bits` | Каждый отдельно N≤32 итераций и до 33 проверок диапазона. |
| Scratch prefix write / read и сравнение destination | Два последовательных прохода по N≤32 итераций. |
| `outside_unchanged` | 34 итерации, 35 проверок диапазона, от 2 до 8 внешних скалярных сравнений. |
| Actual обход регионов и S13 | Два региона. В S13 45 прямых вызовов без цикла. |
| Actual insertion driver, слева/справа | N26 0/0, N27 0/1, N28 1/1, N29 1/2, N30 2/2, N31 2/3, N32 3/3. `insert_tail` имеет до R≤15 итераций для одного вызова. |
| Actual merge и copy-back | m≤16 пар. Up/down, нечётный центр и copy-back используют typed copy без дополнительного Rust-цикла. |
| Произвольные массивы и popcount | Stock Kani специализирует `u64::any_array` через raw array nondet. `u64::count_ones` вызывает intrinsic. |

Максимум составляет 34 итерации и 35 проверок диапазона при unwind36. Снимки копируют значения массивов. Проверки данных сравнивают отдельные `u64` и скалярные маски без сравнений массива/среза и скрытого `memcmp`.

## Нативные опоры по длинам

B01 bits/swap взяты из `45919454859/1`, B01 REL13/14/15 из `45933888115/1`. У обеих попыток сверены индексы `6d7e603aa2fe26dd62c0f41725d664bf726be89836c16c35efbe641f3a0661f9` и `50ba454bc3106f76ea6cb83717280fb6f13cb4c5d6b67ad6d41bdfa3a0ea14e3`. Все пять bounded receipts и projections совпали с индексами по размерам и SHA-256. У них `VERIFIED/MATCHED`, exit 0, полные нативные якоря и covers, штатный профиль, своевременный receipt, sampler/reap и аттестация `COMPLETE`. B01 bits использует посты `79:5, 86:5, 87:5`, swap — `35:5, 36:5, 42:5`. Каждый REL использует посты `69:5, 75:5` в `check_insert::<R>`. В текущем Std actual runtime и typed-copy blobs совпадают с историческими. Отличие исторического и текущего N13 blobs — видимость `pub(super)` у того же компаратора. [Допуск B01 S13](REV2-U64-N13-ADMISSION.md) · [Допуск B01 REL13/14/15](REV2-U64-N14-N17-ADMISSION.md)

`45985715566/1` · Ubuntu X64 · job `success` · диагноз публикации `U64_N26_N32_PROVIDERS_WITHIN_PROFILE` · SHA-256 индекса `90d30f581460d473d8913b0901ae0be2e5c493852d01fb80c587e70f05a487e5`. Trigger `59958991f8f64dae4e9bfaed67e3035415b0ab52`, tree `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Std `72bb79d26dd495d0461c6e6d3c05d21c2d1b1878` / `c513d0ec1a137457add28b2b9ee9c47ac23642d3`, stock tool и метаданные source/discovery/attestation совпали с FIX1. Request `3d97d7898abc2e77cbeb9f5431672aa2b361f6e90cef65b1ca2d74f643699043`, roster `5b12d12a4d8c131a1477c2e083444473fba248bae26ecc4aa38e0d153ddf0ae3`, bundle `d9b308422fdb10153ea07b4a953b46467edccca5b2b208e8ee1799412919a38f`, bindings `9fd4a201951ab0fd799474fe935e20300fac5478d78c2b52ad67d03e1ff71b95`. [FIX1](REV2-U64-N26-N32-PROVIDERS-HANDOFF.md#fix1) · [Опубликованный индекс](/root/ch8-artifacts/run-45985715566/ch8-rev2-u64-n26-n32-providers-Linux-X64-45985715566-1/index.json)

Инвентарь содержит 62 опубликованных структурированных члена общим размером 7 875 315 байтов. Сверены имена, размеры и SHA-256 всех членов, включая 18 receipts, 18 projections и 18 timelines. Все 18 слотов дали `VERIFIED/MATCHED`, exit 0. Сверены exact Proof/Check target, regular и stock, нативные посты и covers, профиль, sampler/reap и своевременная запись. Заключительная аттестация `COMPLETE` уложилась в своё окно. Подтверждены чистые Std и stock checkouts, рекурсивные submodules и повторная сверка runtime identity. Наблюдались CBMC 6.11.0, CaDiCaL 3.0.0, OB12 и unwind36 со штатными safety, overflow, unwinding, undefined-function и assertion-reach ON и uninit/validity OFF. [Сводка](/root/ch8-artifacts/run-45985715566/ch8-rev2-u64-n26-n32-providers-Linux-X64-45985715566-1/SUMMARY.json) · [Аттестация](/root/ch8-artifacts/run-45985715566/ch8-rev2-u64-n26-n32-providers-Linux-X64-45985715566-1/attestation.json)

Для каждой пары и каждого центра подтверждены scoped `memcpy.assigns.1/.2`, шесть typed-copy properties и четыре успешных unwind. У трёх центров `checked_write_set.copy_sites` содержит собственные вызовы и `transcribes: smallsort.rs:1034:13`. У восьми bits/swap проверены обе typed-copy группы и включённый stock unwind. Выведенных unwind assertions в этих восьми проекциях не было.

| Роли | Слоты | VT, с | Cold wall, с | Пик RSS группы / CBMC, GiB |
| --- | ---: | ---: | ---: | ---: |
| PAIR-STEP | 7 | 56,14–65,48 | 92,15–100,25 | 2,179–2,551 / 0,869–0,883 |
| ODD-CENTER | 3 | 10,93–11,44 | 46,84–48,33 | 2,177–2,515 / 0,311–0,339 |
| S13 bits | 4 | 39,92–44,06 | 70,54–76,24 | 2,230–2,473 / 2,222–2,234 |
| S13 swap | 4 | 4,44–5,35 | 35,43–36,33 | 2,154–2,591 / 0,233–0,238 |

### N26

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B14-L14-BITS` · 4/4 covers | `2f0b11329ea97e8ba6a5967ec3dd5f1b8c06331769b9dc3975b87de11d918c6b` / `f2b4b95d2296cf5d39d01e682930c2cdd570ad1cf4fc8ee87149e84ac96f7e87` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B14-SWAP` · 5/5 covers | `f00920a303a4350492d33f0ca6704379efaaa7676fe07a3b1440ce46d235bc6f` / `7c78fcdd9caa966166d6694bd4777471781cfc9297331b5e13fbfb36faa02851` |
| Пара merge | `45985715566/1` · `U64-N26-PAIR-STEP` · 10/10 covers | `1fb1ae31b7bddca5b96a6386921237d5d01833dd2d4fc7fb8ba4ad3760659fb1` / `09f9e03535278316d3f320f33f8e868c48e2d50110452531fa6565ca1290184b` |
| Copy-back / различающий контроль | `U64-N26-COPY-BACK-FRAME` / `U64-N26-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 13 и B14 S13 к правым 13 словам.
2. Передать префиксы драйверу offset 13. Слева tail==end, справа tail==end.
3. Применить exact N26 pair в 13 ранговых шагах. Курсоры достигают ends после пар.
4. После заполнения `D[0..26]` связать локальную и actual копии на 208 байтов и вывести frame.

### N27

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B14-L14-BITS` · 4/4 covers | `2f0b11329ea97e8ba6a5967ec3dd5f1b8c06331769b9dc3975b87de11d918c6b` / `f2b4b95d2296cf5d39d01e682930c2cdd570ad1cf4fc8ee87149e84ac96f7e87` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B14-SWAP` · 5/5 covers | `f00920a303a4350492d33f0ca6704379efaaa7676fe07a3b1440ce46d235bc6f` / `7c78fcdd9caa966166d6694bd4777471781cfc9297331b5e13fbfb36faa02851` |
| REL13, исторический B01 для переноса на B14 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| Пара merge | `45985715566/1` · `U64-N27-PAIR-STEP` · 10/10 covers | `86989634626f78de334dd50f6a01980e496cb2071a6639d5bd036a6694db9b1b` / `8fb5e9e68638ee5692b28be8e7e18bae91c258576932840f466f00b552ee2d9d` |
| Нечётный центр | `45985715566/1` · `U64-N27-ODD-CENTER` · 4/4 covers | `6b1e612b1bf6d01bd20e3f60ea7b0ff91cec46756b9cf9d9e0d553988ab97528` / `07c5121030d2a38962c1173c6fd033ae7f0ff3c78009c1ee7fee3c674be7d064` |
| Copy-back / различающий контроль | `U64-N27-COPY-BACK-FRAME` / `U64-N27-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 13 и B14 S13 к правым 14 словам.
2. Передать префиксы драйверу offset 13. Слева tail==end, справа переносы rel 13.
3. Применить exact N27 pair в 13 ранговых шагах. Затем нативный центр заполняет `D[13]`.
4. После заполнения `D[0..27]` связать локальную и actual копии на 216 байтов и вывести frame.

### N28

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B15-L15-BITS` · 4/4 covers | `fb38dbf891438c82e48b69bd4cfcfb98bef179b37ab17b4fef852267ca3145f8` / `b9a6cd63bb0a04f7abca7a4fca3c3de28b75d2509e588f83b5ad9e44e7fcb64f` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B15-SWAP` · 5/5 covers | `b789918e780600c4e0776086408b87fd937d425016ff9a4e56fe5f145bece1fb` / `ca56b8e901fa8ccbc01f54580c10b6428419b040646f052861998c12b801648f` |
| REL13, левая B01 и основание переноса на B15 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| Пара merge | `45985715566/1` · `U64-N28-PAIR-STEP` · 10/10 covers | `c4172b928b1d75282ef30545e8239ee6e69afbb73da30e24deed836481f32253` / `68987cb4ab8c21d71936ed258b3815486e241c02ffbc8bb997308fc962edc309` |
| Copy-back / различающий контроль | `U64-N28-COPY-BACK-FRAME` / `U64-N28-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 14 и B15 S13 к правым 14 словам.
2. Передать префиксы драйверу offset 13. Слева rel 13, справа переносы rel 13.
3. Применить exact N28 pair в 14 ранговых шагах. Курсоры достигают ends после пар.
4. После заполнения `D[0..28]` связать локальную и actual копии на 224 байтов и вывести frame.

### N29

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B15-L15-BITS` · 4/4 covers | `fb38dbf891438c82e48b69bd4cfcfb98bef179b37ab17b4fef852267ca3145f8` / `b9a6cd63bb0a04f7abca7a4fca3c3de28b75d2509e588f83b5ad9e44e7fcb64f` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B15-SWAP` · 5/5 covers | `b789918e780600c4e0776086408b87fd937d425016ff9a4e56fe5f145bece1fb` / `ca56b8e901fa8ccbc01f54580c10b6428419b040646f052861998c12b801648f` |
| REL13, левая B01 и основание переноса на B15 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| REL14, исторический B01 для переноса на B15 | `45933888115/1` · `U64-INSERT-REL14` · 6/6 covers | `edf1a43b5daba77d9d3ebd1066041ca5112f5cedb7333cbbee935b19afac9100` / `53bf38c78c2314fb11a7429f30b6286b489e00759a8f0033c947ccd5e5ff4a5c` |
| Пара merge | `45985715566/1` · `U64-N29-PAIR-STEP` · 10/10 covers | `bc6e057d627c28bed11c78b64144534bb590a53b54c22a89e162802b38fd1927` / `7931a076f9638894b60b412e2c66bc75b6a14fc785319238b3a68822001057c5` |
| Нечётный центр | `45985715566/1` · `U64-N29-ODD-CENTER` · 4/4 covers | `ee4c6bce18563c44a4f42d92ae5fa79c9b7e0350f2e44cb7dfe3a80aae3844e3` / `f187f9fde6fce447bccbe3d038a054db1d6cfc2ec017d1179880a0ad404a6199` |
| Copy-back / различающий контроль | `U64-N29-COPY-BACK-FRAME` / `U64-N29-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 14 и B15 S13 к правым 15 словам.
2. Передать префиксы драйверу offset 13. Слева rel 13, справа переносы rel 13, 14.
3. Применить exact N29 pair в 14 ранговых шагах. Затем нативный центр заполняет `D[14]`.
4. После заполнения `D[0..29]` связать локальную и actual копии на 232 байтов и вывести frame.

### N30

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B16-L16-BITS` · 4/4 covers | `4a49b3af629e9412a55fd55053af7d6b923bf274a5190b3c80a6d616b2ec9720` / `5b34328b0d7cbb8d90ee836f2bc7ccc3774a33309255a5cfbf22d9189a32869d` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B16-SWAP` · 5/5 covers | `3606082c7edce6e880faf96d572a771267bb6ef935033bb43b084b9a9907c58f` / `96cc39c790de369ec3c1b5f9b0c742adf4abddbd05a92bea319603882daea6dc` |
| REL13, левая B01 и основание переноса на B16 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| REL14, левая B01 и основание переноса на B16 | `45933888115/1` · `U64-INSERT-REL14` · 6/6 covers | `edf1a43b5daba77d9d3ebd1066041ca5112f5cedb7333cbbee935b19afac9100` / `53bf38c78c2314fb11a7429f30b6286b489e00759a8f0033c947ccd5e5ff4a5c` |
| Пара merge | `45985715566/1` · `U64-N30-PAIR-STEP` · 10/10 covers | `ff7fc9e670046607ee313957fed0f8a0b718a9982936bfa9d2df8e66efb96e30` / `10df314fa93c7ddb06bc51c4078cb346b17db522db615ed4916dd487cf77bcba` |
| Copy-back / различающий контроль | `U64-N30-COPY-BACK-FRAME` / `U64-N30-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 15 и B16 S13 к правым 15 словам.
2. Передать префиксы драйверу offset 13. Слева rel 13, 14, справа переносы rel 13, 14.
3. Применить exact N30 pair в 15 ранговых шагах. Курсоры достигают ends после пар.
4. После заполнения `D[0..30]` связать локальную и actual копии на 240 байтов и вывести frame.

### N31

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B16-L16-BITS` · 4/4 covers | `4a49b3af629e9412a55fd55053af7d6b923bf274a5190b3c80a6d616b2ec9720` / `5b34328b0d7cbb8d90ee836f2bc7ccc3774a33309255a5cfbf22d9189a32869d` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B16-SWAP` · 5/5 covers | `3606082c7edce6e880faf96d572a771267bb6ef935033bb43b084b9a9907c58f` / `96cc39c790de369ec3c1b5f9b0c742adf4abddbd05a92bea319603882daea6dc` |
| REL13, левая B01 и основание переноса на B16 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| REL14, левая B01 и основание переноса на B16 | `45933888115/1` · `U64-INSERT-REL14` · 6/6 covers | `edf1a43b5daba77d9d3ebd1066041ca5112f5cedb7333cbbee935b19afac9100` / `53bf38c78c2314fb11a7429f30b6286b489e00759a8f0033c947ccd5e5ff4a5c` |
| REL15, исторический B01 для переноса на B16 | `45933888115/1` · `U64-INSERT-REL15` · 6/6 covers | `e123a1f34f425a157eb977801e43781417fca28f37b60bd7bc3c0d701c314933` / `4148c468785e207f323bbe0e3778c2bb369a4a4f98e922116c5737cb6ecfc552` |
| Пара merge | `45985715566/1` · `U64-N31-PAIR-STEP` · 10/10 covers | `ff82b7ca659141b22c3f3a0f8855910e2cc65204ae96a25a3e3d234fa9995929` / `05a22ba38e82a1b0441d237bbe44dcd0727875c2c92a6cb24478f98b843b0009` |
| Нечётный центр | `45985715566/1` · `U64-N31-ODD-CENTER` · 4/4 covers | `48257f5c46d1fd0997e9642a5b33422efbb7972294581fa4fd608904eef440da` / `6cc9c8da10f4ac20d392b1f839e21f4e1b794e0284cf6440dc890780a79203d4` |
| Copy-back / различающий контроль | `U64-N31-COPY-BACK-FRAME` / `U64-N31-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 15 и B16 S13 к правым 16 словам.
2. Передать префиксы драйверу offset 13. Слева rel 13, 14, справа переносы rel 13, 14, 15.
3. Применить exact N31 pair в 15 ранговых шагах. Затем нативный центр заполняет `D[15]`.
4. После заполнения `D[0..31]` связать локальную и actual копии на 248 байтов и вывести frame.

### N32

| Роль | Run/attempt · exact slot | SHA-256 receipt / projection |
| --- | --- | --- |
| Левая S13 bits | `45919454859/1` · `U64-N13-S13-BITS` · 4/4 covers | `c3ca8085ba45dc01aed62164c46e46ca7d307b3c5544a150c5b72ce63f5bf560` / `9eca670c5f5854ff679a613e2c374df929c0a86e4dd9d5fbcbe05155958d1da5` |
| Левая полноширинная swap | `45919454859/1` · `U64-N13-SWAP` · 5/5 covers | `91947328f3ea3d2fac94785b058317c8eb7de31b3cbcd72905e07043573bec11` / `48eddb1e4074f2efa334f76b0c6d554fbeb06dea21a196055ccc5148cd8650fc` |
| Правая S13 bits | `45985715566/1` · `U64-S13-B17-L16-BITS` · 4/4 covers | `6204462eec88a7e08eaf3f68654ff48f2b19d80c950acdcb3482faa9f941a0ff` / `bd470b24cf629e15c92ba0cbc4c5b92f4d46f40bc1c56c0449490f93272d4ea5` |
| Правая полноширинная swap | `45985715566/1` · `U64-S13-B17-SWAP` · 5/5 covers | `f57bcf13793b0f8f102b3d2e71d82d7c3be4e17386a7cbcf207f0d44c14031df` / `3e2158f3cefb56c1d10e7351584d9fb0f68fb90eb7e94258574a6dd4523cd8e7` |
| REL13, левая B01 и основание переноса на B17 | `45933888115/1` · `U64-INSERT-REL13` · 6/6 covers | `fecb9cbd6806997e1fe122a1ae744b507b5739e6441e142c5c4d6bea3b002099` / `eb991572a24721ec4fc05312872ceeeca3ea5080c2ff684f1340b7cac86f3db8` |
| REL14, левая B01 и основание переноса на B17 | `45933888115/1` · `U64-INSERT-REL14` · 6/6 covers | `edf1a43b5daba77d9d3ebd1066041ca5112f5cedb7333cbbee935b19afac9100` / `53bf38c78c2314fb11a7429f30b6286b489e00759a8f0033c947ccd5e5ff4a5c` |
| REL15, левая B01 и основание переноса на B17 | `45933888115/1` · `U64-INSERT-REL15` · 6/6 covers | `e123a1f34f425a157eb977801e43781417fca28f37b60bd7bc3c0d701c314933` / `4148c468785e207f323bbe0e3778c2bb369a4a4f98e922116c5737cb6ecfc552` |
| Пара merge | `45985715566/1` · `U64-N32-PAIR-STEP` · 10/10 covers | `31e64e4ace154d0ece93b771976849ef8e704f5f0d72991b9a6d79a65e35d39d` / `3212a0d82b25934ebcf7d2160e51c8a4899b72466f32209c82fd7f950358a378` |
| Copy-back / различающий контроль | `U64-N32-COPY-BACK-FRAME` / `U64-N32-WITNESS-CORRUPT` | Корни consumer, запланированы |

1. Применить B01 S13 к левым 16 и B17 S13 к правым 16 словам.
2. Передать префиксы драйверу offset 13. Слева rel 13, 14, 15, справа переносы rel 13, 14, 15.
3. Применить exact N32 pair в 16 ранговых шагах. Курсоры достигают ends после пар.
4. После заполнения `D[0..32]` связать локальную и actual копии на 256 байтов и вывести frame.

Индекс, нативная привязка и профиль подтверждены для всех требуемых рёбер провайдеров. Copy-back и контроль каждой длины ожидают собственный запуск consumer.

## Профиль запуска

Одна job `ubuntu-24.04` X64 с пределом 130 мин. На слот 120 с VT, 180 с cold wall, 4 GiB группового RSS и 2 GiB резерва ОС. Stock CBMC 6.11.0/CaDiCaL, OB12, unwind36. Safety, overflow, unwinding, undefined-function и assertion-reach ON, uninit/validity OFF. Cold CWD, Cargo/Kani targets, tmp и export раздельны на слот. `KANI_JOBS=1`. В request закреплён порядок 26 cfg. До измерения ориентиры составляют 20–60 с VT для контролей и 2–4 с VT для локальных копий. Предыдущий N25 дал 21,2 с VT и 2,59 GiB. N32 измеряется первым с двумя S13, 3+3 вставками, 16 парами и копией 256 байтов. [Ориентир N25](REV2-U64-N22-N25-ADMISSION.md)

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare собирает stock tool и выполняет cfg-on compile preflight с теми же verify `-Z` без export-json и с `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir "$preflight/kani-target" "$std/library"` до 180 с. При ошибке сохраняются первые rustc diagnostics до двух списков discovery. Discovery вызывает `"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json` с двумя наборами cfg из request.

| Стадия | Граница от начала job | Окно |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Measure identity gate | 55:00 | До 60 с от входа в measure |
| 14 слотов | 102:50 | По 205 с: 180 с cold, 10 с reap, 5 с receipt, 10 с запаса старта |
| Финальная аттестация | 104:50 | Measure 50:55 внутренний, 53 мин внешний |
| Finish и upload-gate | 109:45 | 6 и 1 мин внешние, 5 с резерва запуска upload |
| Upload | 116:50 | 7 мин |
| План с 6 мин резерва | 122:50 | Job 130 мин |

`U64_N26_N32_COMPOSITE_WITHIN_PROFILE` требует 14/14 `MATCHED`, своевременных полных receipts/projections, covers, sampler/reap, соблюдения трёх лимитов и аттестации `COMPLETE` в её окне. Report показывает VT, cold wall, group/CBMC RSS, доступный PSS, последнюю фазу и первую CNF. При смене Linux TID возможен недоучёт RSS в неатомарной выборке. Checkpoint исхода и reap сохраняется до проекции. При неподтверждённом reap последующие слоты блокируются. Ограниченный повтор записи сохраняет статус опоздания. Caps составляют 4 MiB на проекцию и 96 MiB на публикацию.

## Локальная валидация

- Новый Rust-модуль отформатирован `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max` до снятия координат и прошёл `--check`. SHA-256 бинарника `0cb21861860ae07c03b7097b099ea3e28dfb3857a9b09acce0df6b165f25cc70`. Проверены TOML, cfg, видимость Rust-имён, 14 proof roots, runtime diff и побайтное совпадение прежних модулей и контрактов.
- Модель извлекла 45 сравнений actual S13 и проверила все 8192 битовых входа на каждой длине региона 13–16, frame хвоста и семь трасс свидетелей. Сверены 819/819/1015/1015/1240/1240/1496 pair-геометрий, 27/29/31 геометрий нечётных центров и девять переносов вставок.
- На exact review-trigger прошли последовательно штатная 134/134 за 61,405 с, старт 1 с 134/134 за 58,795 с, старт 5 с 134/134 за 56,985 с, старт 60 с 134/134 за 53,763 с. Синтетика проверила неверный промежуточный layout, лишний selector, чужой Check target, потерю typed/post/return anchors и unwind, чужой или второй failure, late receipt, потерю reap/attestation. Подмены результата дают `MISMATCHED`. Проверены YAML, восемь блоков `bash -n`, Python syntax и `git diff --check`.
- Depth-2 checkout без alternates принял bundle, сохранив базовый HEAD, единственный заявленный overlay HEAD и shallow boundary. Source gate проверил 28 commit/tree/parent, 29 текущих blobs, 1060 координат и нативные определения. В синтетике рекурсивные submodules Std и tool заменены проверкой чистых detached checkout и точных commit/tree. Точный detached trigger сформировал 14 `NOT_STARTED` receipts. Пройдены `pins/sources/finish/upload-gate/upload-check`. Отклонены чужой tree, payload, admission receipt, подмена индексированного receipt и просроченные upload-gate и upload-check.
- Std, Control, review-trigger и g0 записаны от `Tiramisu-Cake <igkharin@gmail.com>` с `[skip ci]`. `test_supervisor.py` имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Подготовка выполнена локально без Cargo, rustc, Kani, CBMC, CI, push и изменения Actions variables.
