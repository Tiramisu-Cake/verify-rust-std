# REV2 · полноширинные опоры сети u64 N20/N21

**`READY_FOR_REVIEW` · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.** Заморожен один Ubuntu-пакет из трёх Check слияния и пяти plain Proof для sort9, swap и вставок. Локальные статические и синтетические проверки завершены. Нативные исходы N20/N21, независимое ревью и отдельный GO открыты. [Задание](REV2-U64-N20-N21-TASK.md)

## Исход N18/N19 и выбор формы

Run `45938919685`, attempt 1, локально сверён по опубликованным bounded receipts и summary координатора. Trigger `aa538f575425fdad8546449ef15bf8fbff1aee34`, tree `74f90d62acda5157906272454ec9d6c4bb9819db` и четыре хэша FIX1 совпали с пинами. Размеры и SHA-256 сводки и семи receipts совпали с индексом. Диагноз `U64_N18_N19_PROVIDERS_WITHIN_PROFILE`, 7/7 `VERIFIED/MATCHED`, полные проекции, все ожидаемые covers, валидный sampler, reap и аттестация `COMPLETE`. У обоих pair и центра подтверждены два scoped `memcpy.assigns` и шесть свойств типизированной копии полного `u64`. [Ledger, g0 `378788216e`](CH8-DISPATCH-LEDGER.md#L311) · [Summary](/root/ch8-artifacts/run-45938919685/ch8-rev2-u64-n18-n19-Linux-X64-45938919685-1/SUMMARY.json) · [Index](/root/ch8-artifacts/run-45938919685/ch8-rev2-u64-n18-n19-Linux-X64-45938919685-1/index.json)

| Предыдущий слот | VT, с | Cold wall, с | CBMC RSS, KiB |
| --- | ---: | ---: | ---: |
| N18 pair | 69,50 | 114,07 | 921 480 |
| N19 pair | 68,67 | 113,17 | 912 116 |
| N19 odd center | 13,94 | 57,65 | |
| N19 insert right | 4,39 | 44,44 | |
| S9 B01/L09 bits | 33,80 | 73,85 | 1 444 352 |
| S9 B10/L10 bits | 40,81 | 80,76 | 1 426 956 |
| S9 B10 swap | 4,68 | 44,15 | |

У более дорогой пары остаётся 50,50 с до лимита VT и 65,93 с до лимита cold wall. Выбраны отдельные литеральные N20 и N21 Check той же формы с символическими `k,a,c`. Дополнительное значение k увеличивает число состояний с 285 до 385. Каждый Check по-прежнему выполняет два actual шага с четырьмя адресами чтения и двумя адресами записи для полных u64. До измерения стоимость N20/N21 открыта. При отсечке receipts сохраняют достигнутую фазу, CNF, память и reap для решения о границах k или разделении up/down.

Левый `U64-S9-B01-L09-BITS` имеет `VERIFIED/MATCHED`, четыре covers и полные нативные якоря. Его перенос на B01/L10 использует общий guard и тот же граф 25 пар. Полноширинный swap-лист B01 из N13 связывает эту геометрию с числовым сравнением `u64_less`. B10 из N19 сохраняет собственную геометрию. [Левый receipt](/root/ch8-artifacts/run-45938919685/ch8-rev2-u64-n18-n19-Linux-X64-45938919685-1/slots/U64-S9-B01-L09-BITS/receipt.json) · [Лист N13](REV2-U64-N13-ADMISSION.md#нативная-сверка)

## Worktrees и замороженные входы

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n20-n21-w13), `work/rev2-u64-n20-n21-std-w13` | `b09c6f22bfbd1ce8eb6afccf96df6b9a2ad3c54b` | `a784a8d12b2d7439233385ffa25f512e4f2c623b` | `c8eefae4c8073cff31e5576b372d5105b52797a1` |
| [Control](/root/kani-rev2-u64-n20-n21-control-w13), `work/rev2-u64-n20-n21-control-w13` | `c4da71875efe80ebcfe78094afe6889a902d2da5` | `0d0857a039e5ffa263414952de49b716e3371c25` | `44aa6a2273588502083e47e204730dd67e0fba51` |
| [Review-trigger](/root/kani-rev2-u64-n20-n21-trigger-w13/control), detached, ref `review/rev2-u64-n20-n21-trigger-w13` | `3ef1c394934f8917c687568381cadaaeaa5d7c59` | `0d0857a039e5ffa263414952de49b716e3371c25` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std база FIX1 имеет tree `4f9687a4edccf69ef86ee8b4c2e01de9b3517539`, Control база FIX1 — `74f90d62acda5157906272454ec9d6c4bb9819db`. Bundle объявляет только `HEAD`, prerequisite CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655` и 25 последовательных overlay-коммитов. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `48f143cc26c31c0d08feda5ea38ff7323ce531bb6b734c4cc68b8046f7843a6c` |
| Exact roster, канонический JSON | `efe927152ff12c20ecb150ed7a04353dc68e500ae6b83158f91974742551bbb8` |
| Source bindings, канонический JSON | `80fa49500d68fd1488bbd2ea133950cc60cfb4899d7d32eaa9f1bf478c616a8e` |
| [std-overlay.bundle](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/std-overlay.bundle), 69 520 байт | `02e9cbbdc2d2528f0e15dbdb3b1448ca90289ad5e095cc16be31bfe9705ef1ef` |
| [Workflow](/root/kani-rev2-u64-n20-n21-trigger-w13/control/.github/workflows/ch8-q-pilot.yml) | `4b244fe5fbbb685c580f16790266877f7b50023fd9af3def51406d0dcd9c29f7` |

Git blobs `smallsort.rs` — `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`, `ptr/mod.rs` — `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6`, новый модуль — `5af7b8f629e6b218c5c4ccb7672aa5754fb9fecb`, реестр — `58fdf01ac881ffcd424f8d55df52049d4e97dce7`, `core/Cargo.toml` — `3352dde8a37775ee4eae790d90e678f93d3b5cd8`. Регистрация внутри `cfg(kani)` требует `kani_smallsort_rev2_u64_n13` и `kani_smallsort_rev2_u64_n20_n21`. Удаление добавленных строк регистрации и check-cfg побайтно восстанавливает файлы базы. Runtime, контракты и старые модули совпадают по байтам.

## Roster и нативные координаты

Exact selector prefix — `slice::sort::shared::smallsort::verify::rev2_u64_n20_n21::`. Все строки ожидают exit 0, `VERIFIED`, `copy_back=false` и покрытие всех covers. Discovery при включении нового cfg добавляет пять plain Proof и три Check к 110 историческим REV2-записям. Сопоставляются вид, selector, файл и targets. Stock Check привязан к одной точной цели. У plain targets пусты. Существующие функции идут в Original с `--no-assert-contracts`. [Std-модуль](/root/verify-rust-std-rev2-u64-n20-n21-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n20_n21.rs) · [Frozen roster](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/CI-REQUEST.json)

| Слот | Суффикс selector, root | Check target, `cfg_attr` / `modifies` | Посты / covers | Latest start |
| --- | --- | --- | ---: | --- |
| `U64-N20-PAIR-STEP` | `u64_n20_pair_step`, 202:1 | `actual_pair_step_n20`, 153:1 / 159:5 | 8 / 10 | 55:00 |
| `U64-N21-PAIR-STEP` | `u64_n21_pair_step`, 305:1 | `actual_pair_step_n21`, 256:1 / 262:5 | 8 / 10 | 58:25 |
| `U64-N21-ODD-CENTER` | `u64_n21_odd_center`, 395:1 | `actual_odd_center_n21`, 359:1 / 365:5 | 8 / 4 | 61:50 |
| `U64-S9-B11-L11-BITS` | `u64_s9_b11_l11_bits`, 16:1 | Plain | 3 / 4 | 65:15 |
| `U64-S9-B11-SWAP` | `u64_s9_b11_swap`, 49:1 | Plain | 3 / 5 | 68:40 |
| `U64-B01-INSERT-REL9` | `u64_b01_insert_rel9`, 78:1 | Plain | 2 / 6 | 72:05 |
| `U64-B11-INSERT-REL9` | `u64_b11_insert_rel9`, 84:1 | Plain | 2 / 6 | 75:30 |
| `U64-B11-INSERT-REL10` | `u64_b11_insert_rel10`, 90:1 | Plain | 2 / 6 | 78:55 |

| Якорь | Координаты |
| --- | --- |
| Общий `N13_COMPARATOR_CALLED` | `rev2_u64_n13::u64_less`, 9:5, все строки кроме odd center |
| Pair N20 и N21, `UP_CURSORS` / `DOWN_CURSORS` | 181:9 / 191:9 и 284:9 / 294:9 внутри соответствующего Check target |
| Pair N20 и N21, read / write / disjoint / up / down / frame | 209/213/217/242/243/244 и 312/316/320/345/346/347, столбец 5 |
| Pair N20 и N21, up left/right, down left/right, up/down tie, k=0/9, return | 245–253 и 348–356, столбец 5 |
| Odd center, read / write / disjoint / selected source / value / left end / right end / frame | 402/406/410/428/429/430/434/438, столбец 5 |
| Odd center, left/right/sentinel/return | 439–442, столбец 5 |
| Bits B11, canonical / sorted popcount / frame и mixed / inversion / return | 37/38/43 и 25/26/44, столбец 5 |
| Swap B11, min / max / frame и greater / less / equal / return | 66/67/72 и 57/58/59/73, столбец 5 |
| Вставки, exact mapping / frame и no shift / max shift / interior / after equal / return | 132/141 и 111/112/113/114/142, столбец 5, `check_insert::<1, 9>`, `::<11, 9>`, `::<11, 10>` соответственно |

Пары используют actual копии `smallsort.rs:885:9` и `:918:9`. Транскрипция центра копирует на `rev2_u64_n20_n21.rs:386:9` по форме `smallsort.rs:1034:13`. Каждый Check требует `single_top_level_call` и `no_recursive_call` на своём атрибуте, scoped `memcpy.assigns.1/.2` на builtin 46/47 и шесть успешных grouped `ptr::copy_nonoverlapping::<u64>` на `ptr/mod.rs:587:14`. Курсоры пары привязаны к closure того же target. Regular сохраняет отдельные ID, координаты и статусы. Stock даёт exact target, проверки, terminal и cover ID для сопоставления. Все выведенные unwind свойства должны иметь `SUCCESS` при stock `unwinding=ON`. [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Геометрия половин и sort9

Вход — живая `[u64; 34]`, `S = &v[1]`. N20 использует `v[1..21]` и половины `v[1..11]`, `v[11..21]`. N21 использует `v[1..22]` и половины `v[1..11]`, `v[11..22]`. На Ubuntu x86_64 размер и выравнивание слова равны 8 байтам. Активный источник занимает 160/168 байт. Отдельная живая `MaybeUninit<[u64; 32]>` даёт записываемую область `D` в 256 байт.

Actual `sort9_optimal` в `smallsort.rs:538` проверяет `len >= 9` и вызывает 25 упорядоченных пар на rel0…8. Левый перенос с B01/len9 на B01/len10 сохраняет базу, guard, все адреса листа и добавляет в frame произвольное слово `v[10]`. Правый перенос с B11/len11 на B11/len10 сохраняет базу и те же пары на `v[11..20]`. Корень len11 проверяет frame и для произвольных `v[20]` и `v[21]`. B10/len10 из N19 остаётся на B10.

Для полного числового порядка каждому порогу `t` сопоставляем бит `word > t`. Проекция min/max на биты равна AND/OR. По каждой из 25 фактических пар это переносит битовый пост на проекции полных слов. Инверсия `x > y` дала бы инверсию битов порога `t=y`. Swap-лист сохраняет пару как мультимножество и все слова во frame, поэтому сохраняются кратности исходных полных слов. Для левой базы адресно подходящий лист — полноширинный B01 из N13 с `0 ≤ a < b < 13`, ограниченный до `b < 9`. Для правой базы — новый B11 swap с `0 ≤ a < b < 9`. Источники и координаты для левого листа закреплены в допуске N13. [N13](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-U64-N13-ADMISSION.md) · [N18/N19](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-U64-N18-N19-HANDOFF.md)

## Вставки

| Корень | Actual begin / tail | Участок, включая tail | Frame |
| --- | --- | --- | --- |
| `u64_b01_insert_rel9` | `S / S+9` | `v[1..11]` | `v[0]`, `v[11..34]` |
| `u64_b11_insert_rel9` | `S+10 / S+19` | `v[11..21]` | `v[0..11]`, `v[21..34]` |
| `u64_b11_insert_rel10` | `S+10 / S+20` | `v[11..22]` | `v[0..11]`, `v[22..34]` |

В каждом корне B и R заданы литералами. Для отсортированного префикса элементы `≤x` образуют начальный отрезок, его длина даёт единственный `p` для `x=before[B+R]`. Точный пост сохраняет `before[B+j]` при `j<p`, пишет `x` на `p` и `before[B+j−1]` при `p<j≤R`. Равные предшественники остаются слева от `x`. Covers проверяют `p=R`, `p=0`, `0<p<R`, остановку после равного внутри, actual компаратор и возврат после постов.

В actual driver начальный offset равен 9. Первый правый шаг N21 и единственный правый шаг N20 имеют одинаковые begin/tail и одну живую область. Пост rel9 сохраняет `v[21]` и устанавливает порядок в `v[11..21]`. Эти факты дают pre для rel10 в N21. Слева один rel9 на обеих длинах. По `smallsort.rs:722:13` каждый сдвиг копирует 8 байт из `B+j-1` в соседнее слово `B+j`. По `:362:13` Drop заполняет конечный зазор из отдельного инициализированного `tmp` в `v[B+p]`. Оба места используют `ptr::copy_nonoverlapping::<u64>` с типизированными проверками на `ptr/mod.rs:587:14`. Нужны шесть общих свойств wrapper, caller ID сохраняются при точной координате. [Форма FIX1](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-U64-N14-N17-FIX1-HANDOFF.md#полноширинные-предпосылки-посты-и-границы-циклов)

## Адреса и композиция слияния по исходнику

В каждой строке `k∈0..=9`, `a,c∈0..=k`, `b=k−a`, `d=k−c`. До вызовов границы ниже включительны. Каждая копия с `count=1` читает и пишет ровно 8 байт, с интервалом `[8i,8i+8)` относительно базы соответствующего объекта. Предпосылка отсортированных половин нужна внешнему выводу о рангах. Границы адресов локального шага следуют из счётчиков.

| Длина | Входы up относительно S | Входы down относительно S | Выходы относительно D |
| --- | --- | --- | --- |
| 20 | `a=0..9`, `10+b=10..19` | `9−c=0..9`, `19−d=10..19` | `k=0..9`, `19−k=10..19` |
| 21 | `a=0..9`, `10+b=10..19` | `9−c=0..9`, `20−d=11..20` | `k=0..9`, `20−k=11..20` |

Up advance может дать левый `S+10` и правый `S+20` (one-past у N20), forward dst `D+1..D+10`. Down advance может дать левый sentinel `S−1` через wrapping, правый `S+9` у N20 или `S+10` у N21, reverse dst `D+9..D+18` у N20 и `D+10..D+19` у N21. Эти курсоры сами по себе адрес чтения не устанавливают. Для следующей пары счётчики вновь ограничены её `k≤9`.

Ранг — лексикографический `(значение, индекс после вставок)`. Внутри каждой половины ранги строго возрастают. Up выбирает меньший ранг, при равном значении — левый. Down выбирает больший, при равном значении — правый. Каждый поток последовательно выбирает экстремум среди элементов, оставшихся именно в его собственном обходе. До завершения десятого вызова ни одна половина в таком обходе не исчерпана, так как каждый содержит не менее десяти слов, а поток потребил не более девяти. Up пишет первые десять глобальных рангов, down — последние десять в обратном порядке. Эти ранговые множества раздельны. Поэтому хотя курсоры могут смотреть на значения, уже выбранные противоположным потоком, такие значения повторно не выбираются. Это также покрывает исчерпание половины после последней пары. У N20 выходные интервалы покрывают `D[0..20]`, а по каждой половине `a+c=10` и `b+d=10` дают оба равенства guard `smallsort.rs:1042`.

После десяти пар N21 возможны только два остатка. Если остаётся левый, `0≤a≤9`, `b=10−a`, `c=9−a`, `d=1+a` и копируется `S+a`. Если остаётся правый, `0≤a≤10`, `b=c=10−a`, `d=a` и копируется `S+20−a`. При `a=0,c=10` левый reverse sentinel `S−1` продвигается до `S` через `wrapping_add(1)` без разыменования. В обоих случаях центр пишет ровно `D[10]`, затем forward с выбранной стороны совпадает с соответствующим reverse end. Это устанавливает обе части `:1042` и инициализацию `D[0..21]` по фактическим записям при uninit OFF. Копия `:425` на 160/168 байт, итоговый frame и сквозные контроли относятся к следующему пакету.

## Циклы и скрытые развёртки при unwind36

| Место | Граница |
| --- | --- |
| S9 setup, каноничность/маска, frame | `0..9`, `0..9`, `0..34`, то есть 9/9/34. `u16::count_ones` — ctpop ширины 16. |
| B11 swap frame | `0..34`, два символических индекса выбирают исключения. |
| `check_insert::<1,9>` | Порядок 8, разбиение 9, отображение 10, frame 1 и 23. |
| `check_insert::<11,9>` | Порядок 8, разбиение 9, отображение 10, frame 11 и 13. |
| `check_insert::<11,10>` | Порядок 9, разбиение 10, отображение 11, frame 11 и 12. |
| Actual `insert_tail` | До 9/10 итераций по геометрии, `p` влияет только на число совершённых сдвигов. При no shift возврат до цикла. |
| Actual S9, swap, Drop, up, down, транскрипция центра | 25 вызовов swap развёрнуты в исходнике. В остальных телах циклов нет. Копии переносят одно слово; builtin memcpy использует array_copy/array_replace. |
| Range, индексирование, input и snapshot | `Range::next` — скалярный шаг внутри явного цикла, `contains` — границы без обхода. `any_array` для `u64` специализируется на прямой генерации массива. Snapshot — фиксированные 272 байта; посты используют скалярные сравнения. |
| Pair/center source frame | `0..34` при применении формы Check. Указатели строятся напрямую из ограниченных счётчиков. |
| DFCC write-set assignment/deallocation | Сканируется `contract_assigns.max_elems`; pair имеет два targets, center один. Пустой окружающий set тоже возможен. При кодогенерации учитывается unwind36, фактические выведенные свойства должны быть SUCCESS. Эти циклы относятся к Check. |
| Caller и merge в композиции | Две итерации presort driver, 1+1 / 1+2 вызовов вставки, 10 пар, в N21 одна прямая ветвь центра. Циклы driver и общего merge относятся к внешнему выводу. |

## Ubuntu job и абсолютные границы

Одна job `ubuntu-24.04` X64, 110 мин. CBMC 6.11.0/CaDiCaL, OB12, unwind36, safety/overflow/unwinding/undefined-function/assertion-reach ON, uninit/validity OFF. RUSTFLAGS содержат 23 cfg в порядке frozen roster, последним `--cfg=kani_smallsort_rev2_u64_n20_n21`. На singleton используются отдельные холодные CWD, cargo target, Kani target, tmp и export, `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, `TMPDIR=TMP=TEMP=$slot/tmp`.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare запускает cfg-on compile preflight после сборки stock Kani и checkout overlay, до discovery. Preflight имеет предел 180 с, `--no-codegen --only-codegen --quiet`, отдельный target и запись первых rustc diagnostics при отказе. Discovery выполняет cfg-off и cfg-on list. Сопоставление проверяет 110 исторических записей и дельту до 118. [Раннер](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/run.py)

| Стадия | Абсолютная граница | Внешнее окно |
| --- | --- | --- |
| Prepare | 54:00 | 56 мин |
| Measure identity gate | до 55:00, до 60 с от входа | в measure |
| Восемь слотов по 205 с | 82:20 | measure 32 мин, внутренний 30:25 |
| Итоговая аттестация | 84:20 | в measure |
| Finish и upload-gate | 89:15 | 6 и 1 мин |
| Конец upload | 96:20 | 7 мин |
| План с резервом 6 мин | 102:20 | job 110 мин |

На слот 120 с VT, 4 GiB RSS группы, 180 с cold wall, 10 с на reap, 5 с на receipt и 10 с запаса старта. Резерв ОС 2 GiB. Checkpoint сохраняет исход процесса и reap перед проекцией. Последующие слоты блокируются при отсутствии подтверждения reap. Ограниченный повтор записи в finish сохраняет отметку об опоздании. Caps проекции и артефакта 4/96 MiB. Отчёт сохраняет фазу, первую CNF, VT, cold wall, RSS/PSS группы и CBMC и открытые опоры для каждой длины. Linux sampler может недоучесть RSS при смене TID. Для `U64_N20_N21_PROVIDERS_WITHIN_PROFILE` нужны восемь `VERIFIED/MATCHED`, полные своевременные проекции и receipts, лимиты, sampler/reap и своевременная аттестация `COMPLETE`. [Профиль](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/report.py)

У `pins/sources/finish` независимый `CH8_REV2_U64_N20_N21_TRIGGER_TREE` с ожидаемым tree `0d0857a039e5ffa263414952de49b716e3371c25`. Гейты требуют `Tiramisu-Cake/kani`, событие push attempt 1 на `refs/heads/uninit-ci/ch8-q-pilot-v1`, совпадение detached HEAD с payload и `GITHUB_SHA`, чистое дерево и единственный parent из таблицы. Перед публикацией повторно сверяется admission receipt. [Trigger gate](/root/kani-rev2-u64-n20-n21-trigger-w13/control/ch8-cal1/request.py)

## Офлайн-валидация

- Закреплённый rustfmt `nightly-2026-11-19 --edition 2024 --config use_small_heuristics=Max` применён до вычисления координат. Форматирование реестра сверено с его форматированной базой при отключённом обходе дочерних модулей. Граница cfg, Rust-видимость, побайтный runtime diff, TOML, YAML, восемь блоков `bash -n` и `git diff --check` проверены.
- Сверены 25 фактических пар и по 512 масок на четырёх геометриях B01/L09, B01/L10, B11/L11, B11/L10. Модель сдвигов прошла 12 012 случаев для каждой rel9 и 18 018 для rel10 с шестью значениями, включая края `u64` и значения по обе стороны `2^63`. Сверены по 385 адресных состояний, 21 состояние нечётного центра и 184 756/352 716 ранговых чередований N20/N21. Модели служат офлайн-проверкой адресов и композиции.
- Проверка frozen inputs привязала source blobs, расписания, исторические и новые координаты постов, covers и exact Check definition/modifies. Shallow checkout CI-base глубины 2 проверил bundle, распаковал 25 overlay-коммитов и сверил цепочку tree/parent.
- Detached review-trigger принял `pins` при +2 с, `sources` при +30 с, `finish` при +5100 с, `upload-gate` при +5150 с и `upload-check` при +5775 с. Подменённые дерево и payload SHA отклонены в трёх гейтах, изменённый admission receipt — в `sources/finish`, публикация после +5780,01 с — в `upload-check`. Тестовый индекс сохранил восемь `NOT_STARTED`. Синтетические локальные std/tool прошли detached identity; рекурсивная инициализация submodules исключена из этой симуляции.
- На замороженном detached review-trigger последовательно прошли 128/128 тестов на обычной шкале и каждой из свежих шкал 1/5/60 с. Время suite 80,176 / 59,834 / 50,503 / 81,673 с. Синтетика покрыла exact roster, Check targets и scoped anchors, типизированные копии, профили, receipt/reap/attestation и cutoff. Blob `test_supervisor.py` в Control и trigger равен `df63a457c3adf648d360f3d559d5d40ef00a9427`.
- Std, Control и review-trigger имеют author и committer `Tiramisu-Cake <igkharin@gmail.com>`. Работа выполнена офлайн через Git, rustfmt, статическую сверку и синтетику. Нативный compile preflight, discovery и восемь исходов остаются задачами следующего этапа после GO. Сквозные positive/control и copy-back остаются отдельным пакетом.
