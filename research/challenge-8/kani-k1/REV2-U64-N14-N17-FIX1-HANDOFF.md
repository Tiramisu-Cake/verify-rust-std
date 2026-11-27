# REV2 `u64` N14–N17 · FIX1 для шага вставки

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE` · Item 2.** FIX1 готовит один Ubuntu-пакет из четырёх полноширинных проверок actual `insert_tail`, по одной на фиксированный `R=13..16`. Сквозной битовый N17 и четыре контроля переиспользуются из run `45926757103`. Новый compile preflight, discovery, нативные результаты и замеры ожидают независимого ревью и отдельного GO. [Задание FIX1](REV2-U64-N14-N17-FIX1-TASK.md) · [Ревью R1](REV2-U64-N14-N17-REVIEW.md) · [Исходный handoff](REV2-U64-N14-N17-HANDOFF.md)

## Worktrees и пины

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1), `work/rev2-u64-n14-n17-std-w13-fix1` | `fe8444d175ec1630155b886d54ce527ebbb6c415` | `fe97d2dd54b5c1ec27479b6332e0285bfe267588` | `53e733666ede6b256c84498a6dd350f1e84dddfb` |
| [Control](/root/kani-rev2-u64-n14-n17-control-w13-fix1), `work/rev2-u64-n14-n17-control-w13-fix1` | `087843c161d70ec36f6533ba8dd39742bae922c4` | `b4bf21f6578d30d40f66fd296af4258b6b0bc390` | `e51c10547ddd19f1f63ec324cd1ee31fbf0c57c9` |
| [Review-trigger](/root/kani-rev2-u64-n14-n17-trigger-w13-fix1/control), чистый detached, ref `review/rev2-u64-n14-n17-trigger-w13-fix1` | `3570969428b44ecb6d87015c4559f6322ee4411b` | `b4bf21f6578d30d40f66fd296af4258b6b0bc390` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std base tree `b1d2c899753acd6e137e9c10e153270f30a65846`, Control base tree `fe9dfbd9a9670cc435190210578d68fa7e363f4e`. Bundle загружается с `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`, объявляет один `HEAD` Std FIX1. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/CI-REQUEST.json) | `a70f7208f517fc165079ef582b2af780dcfdf539cb9afced669f90bd1f168f8a` |
| Exact roster, канонический JSON | `a6eb6158a63b01689f3b49bdb52f7cfc90a517954d21ee3ef7743ffd1532648f` |
| Source bindings, канонический JSON | `90bcab91b75b8fc80adf2e51202e2c4d3f3aacc1d38808755e23ee1a8adb8dc7` |
| [std-overlay.bundle](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/std-overlay.bundle), 61 679 байт | `b3752a87ff9c22b73cbd9d1c7725a920904d3891c7e681552cddeb254527f504` |

Std-дельта состоит из нового модуля (blob `6ef2b2b503347f2e31532bdd2e79d7e82bb02ffe`), строки check-cfg в `core/Cargo.toml` (blob `bceb3fb2ccd589b9e613ec5d8199db07e5bbb136`) и двух строк регистрации в `smallsort/verify.rs` (blob `c6d157ce2154889fcd30ad81718910abac747a05`). Новый модуль требует opt-in `kani_smallsort_rev2_u64_n14_n17_fix1` и `kani_smallsort_rev2_u64_n13` в области `cfg(kani)`. Прежний N14–N17 модуль сохраняет свой отдельный флаг и все шесть регистраций. Удаление новых деклараций из registry и manifest восстанавливает базовые blobs побайтно. Runtime, контракты и прежние verification-модули побайтно совпадают с базой. [Гейт исходников](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/request.py)

## Отсечка исходной формы и ресурсная гипотеза

Исходный `U64-N14-N17-INSERT-STEP` остановлен по `RSS_LIMIT` на 90,650 с cold wall. Первая SAT CNF — 2 708 984 переменных и 13 149 479 дизъюнктов. В момент отсечки 4 234 588 KiB из 4 242 916 KiB группы занимал CBMC при cap 4 194 304 KiB. Ближайший PSS CBMC — 3 825 986 KiB за 0,30 с до пика. Sampler и reap подтверждены. В проекции есть завершение первого вызова решателя и начало следующей пропозициональной редукции. Конкретная операция пика, terminal verdict, итоговый VT и covers остались неизвестны. [Receipt исходного шага](/root/ch8-artifacts/run-45926757103/ch8-rev2-u64-n14-n17-Linux-X64-45926757103-1/slots/U64-N14-N17-INSERT-STEP/receipt.json)

Четыре мономорфизации убирают символический выбор геометрии в адресе `x`, срезе, tail и границах циклов fixture. Символический `p` сохраняет все положения вставки. Число проходов actual `insert_tail` зависит от слов, поэтому фиксированная верхняя граница сама по себе не устанавливает нативную развёртку и размер CNF. Роль rel16 идёт первой как максимальная фиксированная геометрия. Сравнение четырёх слотов с исходным receipt использует фазу, первую CNF, VT, cold wall, group и CBMC RSS, PSS с привязкой к сэмплу и нативные якоря при том же профиле. Память и время FIX1 пока не измерены. [Риск R1.2](REV2-U64-N14-N17-REVIEW.md#r1)

## Полноширинные предпосылки, посты и границы циклов

У каждого корня произвольный инициализированный `[u64; 34]`, `S=&v[1]`, `x=before[1+R]` и символический `p∈0..=R`. `before[1..1+R]` отсортирован. При `j<p` проверяется `before[1+j]≤x`, при `p≤j<R` проверяется `x<before[1+j]`. В отсортированном префиксе значения `≤x` образуют начальный отрезок. Его длина даёт единственный `p` для каждого полного слова `x`, включая все дубликаты и оба края. Cover равенства вычисляет тот же факт о предшественнике через `j+1==p` и `before[1+j]==x` в проходе `0..R`. Это сохраняет условие исходного cover и убирает доступ по `before[p]`. [Предпосылки и covers](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17_fix1.rs:31)

Actual `insert_tail::<u64,_>` получает `v[1..2+R].as_mut_ptr()` и `base.add(R)` внутри одной живой области. На относительных индексах `j<p` остаётся прежний `j`, на `p` стоит `x`, при `p<j≤R` стоит прежний `j−1`. Разбиение и этот пост дают полный порядок и точные кратности. Frame сверяет `v[0]` и каждое слово с абсолютного индекса `2+R` до 33. Все сравнения слов скалярные. [Actual вызов и посты](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n14_n17_fix1.rs:53)

| R | Actual срез и tail | Порядок, `1..R` | Разбиение и equality cover, `0..R` | Отображение, `0..=R` | Цикл frame, плюс `v[0]` отдельно | Максимум сдвигов actual |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 16 | `v[1..18]`, `v[17]` | 15 | 16 | 17 | 16 | 16 |
| 13 | `v[1..15]`, `v[14]` | 12 | 13 | 14 | 19 | 13 |
| 14 | `v[1..16]`, `v[15]` | 13 | 14 | 15 | 18 | 14 |
| 15 | `v[1..17]`, `v[16]` | 14 | 15 | 16 | 17 | 15 |

Для `p=R` ветка `smallsort.rs:706–707` возвращается после вызова компаратора без сдвига. Для `0<p<R` цикл совершает `R−p` сдвигов и останавливается на предшественнике `≤x` на `:731`. Внутренний equality cover выбирает случай с предшественником `==x`. Для `p=0` сделаны все `R` сдвигов, включая сдвиг из `begin`, после которого срабатывает `:725`. Вызов компаратора отмечен в том же function item, возврат — после обоих постов. [Actual тело](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1/library/core/src/slice/sort/shared/smallsort.rs:701)

На `smallsort.rs:722:13` переносится одно `u64` из `sift` в соседний зазор. Элементы выровнены, их области длиной 8 байт не пересекаются. На `:362:13` `CopyOnDrop<u64>` заполняет конечный зазор из отдельного `tmp`, прочитанного на `:715`. Сдвиг каждый раз читает инициализированного предшественника, а последний зазор заполняется инициализированным `tmp`. Это исходный аргумент при `uninit=OFF`. Оба места связываются с одним типизированным wrapper `ptr::copy_nonoverlapping::<u64>` на `core/src/ptr/mod.rs:587:14`. [Заполнение зазора](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1/library/core/src/slice/sort/shared/smallsort.rs:362) · [Intrinsic](/root/verify-rust-std-rev2-u64-n14-n17-w13-fix1/library/core/src/ptr/mod.rs:587)

У каждого корня гейт требует `SUCCESS` для обязательных групп на координате wrapper. Это проверки выравнивания src и dst (`safety_check`), размера в байтах (`arithmetic_overflow`), непересечения, читаемости src и записываемости dst (`precondition_instance`). Regular сохраняет фактические ID, классы, статусы и координаты. Наблюдения с точной caller-координатой входят в списки `shift` или `gap_fill`, wrapper ID атрибутируются общей обёртке. Stock сопоставляется по terminal, счётчикам и доступным ID/status. Все выведенные unwind checks требуют `SUCCESS` при stock `unwinding=ON`. Таблица фиксирует семантические границы циклов, нативный результат проверяется по прогону. [Native гейт](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/results.py) · [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Exact roster и native anchors

Префикс exact selector и новых функций — `slice::sort::shared::smallsort::verify::rev2_u64_n14_n17_fix1::`. Все корни plain Proof, `copy_back=false`, `unwind(36)`, без Check, Replace, stubs и loop contracts. Каждый ожидает `VERIFIED`, exit 0, `MATCHED`.

| Слот | Суффикс selector | Root и мономорфизация | Latest start |
| --- | --- | --- | --- |
| `U64-INSERT-REL16` | `u64_insert_rel16` | `9:1` → `check_insert::<16>` | 55:00 |
| `U64-INSERT-REL13` | `u64_insert_rel13` | `15:1` → `check_insert::<13>` | 58:25 |
| `U64-INSERT-REL14` | `u64_insert_rel14` | `21:1` → `check_insert::<14>` | 61:50 |
| `U64-INSERT-REL15` | `u64_insert_rel15` | `27:1` → `check_insert::<15>` | 65:15 |

| Native label | Класс и ожидаемый статус | Line:column | File и function |
| --- | --- | --- | --- |
| `REV2_U64_N13_COMPARATOR_CALLED` | cover, `SATISFIED` | `9:5` | `rev2_u64_n13.rs`, `rev2_u64_n13::u64_less` |
| `REV2_U64_INSERT_FIX1_NO_SHIFT` | cover, `SATISFIED` | `48:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_INTERIOR` | cover, `SATISFIED` | `49:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_MAX_SHIFT` | cover, `SATISFIED` | `50:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_AFTER_EQUAL` | cover, `SATISFIED` | `51:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_EXACT_MAPPING` | assertion, `SUCCESS` | `69:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_V34_FRAME` | assertion, `SUCCESS` | `75:5` | FIX1 helper |
| `REV2_U64_INSERT_FIX1_RETURNED_AFTER_POSTS` | cover, `SATISFIED` | `76:5` | FIX1 helper |

Оба файла находятся в `core/src/slice/sort/shared/smallsort/verify/`. FIX1 helper означает `rev2_u64_n14_n17_fix1.rs` и полный префикс выше с `check_insert::<R>` своей строки roster. У компаратора полный путь `slice::sort::shared::smallsort::verify::rev2_u64_n13::u64_less`. [Замороженные координаты](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/CI-REQUEST.json)

## Переиспользуемые слоты и граф

Структурированный индекс run `45926757103` attempt 1 имеет SHA-256 `53452e1bbf74a33eefe28a16ed4908d519111ac1fb31e26b9f6f34b6085ad1f5`, аттестация `COMPLETE`. Для пяти переносимых слотов фактические размер и SHA-256 receipt и projection совпали с индексом. У всех пяти `MATCHED`, проекция `COMPLETE`, covers 5/5, подтверждены sampler и reap и выдержан профиль. Positive N17 прошёл за 81,224 с VT и 112,263 с cold wall при RSS группы 2,57 GiB и CBMC 2,29 GiB. У контролей VT 10,780–12,375 с и единственный отказ класса `assertion` в regular и stock. [Индекс](/root/ch8-artifacts/run-45926757103/ch8-rev2-u64-n14-n17-Linux-X64-45926757103-1/index.json)

| Слот | Исход и назначенный нативный отказ | Receipt SHA-256 | Projection SHA-256 |
| --- | --- | --- | --- |
| `U64-N17-ACTUAL-BITS` | `VERIFIED`, exit 0 | `23b1396f97295e3dfe352fbb417f68e701c7d72fcba15219d649bfda4468d6d5` | `4ab299cdb27ff9aef6dc336ba2463c67dc8d1e28baf909cbb3d183bb20d91b92` |
| `U64-N17-WITNESS-CORRUPT` | `FAILED`, exit 1, `check_network::<17>.assertion.15`, `138:13` | `ef1b536f29639160535b90de9c4e291c817db31e84dd610ada3f367a575d2873` | `86c38e0df38bc3d0defd9d53c4f3118f7c41aefe94f3a4f8946cf6cceb118ef2` |
| `U64-N14-WITNESS-CORRUPT` | `FAILED`, exit 1, `check_network::<14>.assertion.18`, `129:13` | `2a2cf84a12fdfa6e2f28e85e62c1d87767dab66f8f3b3def760f1e61f6601c8a` | `fe48c1dab19466c2f172ae11976681370d6c0b0e37fdca0c9a03e24c5d4277ac` |
| `U64-N15-WITNESS-CORRUPT` | `FAILED`, exit 1, `check_network::<15>.assertion.17`, `132:13` | `45df41e3e8008f944034778c29ae2bc286adc8be2ef5410be86ee24dcda3384b` | `082e202579bee07f7426eff1396e9a6c00dfb6202be5458b3cefc1f6053c33ba` |
| `U64-N16-WITNESS-CORRUPT` | `FAILED`, exit 1, `check_network::<16>.assertion.16`, `135:13` | `e6dae2a7e8902a7d09c2eeb1ef6cbc7d4c2b7562e451f2b41930377c860ca7f3` | `cb6e1593a8598d3fbfe87915cd16c4f0300e139759a0a3f73de640bf410a5039` |

У контролей метка `REV2_U64_Nxx_ACTUAL_SORTED_POPCOUNT` соответствует длине. Blob `rev2_u64_n14_n17.rs` `0a23131ac174f4f7b6793823e49336c69397091f` сохраняет эти корни, `check_network`, пост и порчу. Blob компаратора `rev2_u64_n13.rs` `47c129a11d6cd0d0adce0be450b91eca84a25c0c` сохраняет `u64_less` и cover. Blob runtime `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` сохраняет actual `small_sort_network` на `:367`, S13 на `:597`, `insert_tail` на `:701` и driver на `:742`. Blob `ptr/mod.rs` `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` сохраняет wrapper. Старый roster с этими координатами проверяется как историческая привязка, а все шесть исходных ролей остаются в discovery. Четыре новых слота составляют весь измерительный roster FIX1. [Исторические привязки](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/CI-REQUEST.json)

Общие зависимости каждой длины — принятые `U64-N13-SWAP` и `U64-N13-S13-BITS`, прежняя source-привязка base B01, guard `len≥13`, 45 пар и тот же числовой компаратор. После S13 первый префикс отсортирован, хвост сохранён. Каждый применимый FIX1-шаг расширяет отсортированный префикс на одно слово, сохраняет кратности и оставляет ещё не обработанный хвост и внешний frame прежними. Driver стартует с rel13 и заканчивает при `tail==v_end=S.add(N)`. При `len<18` сеть возвращается на `smallsort.rs:407–408`. [Допуск N13](REV2-U64-N13-ADMISSION.md) · [Привязка композиции](REV2-U64-N14-N17-HANDOFF.md#композиция-на-четырёх-длинах)

| Длина | Последовательный набор полноширинных опор | Прежний точный контроль | Конечный порядок и кратности, внешний frame |
| --- | --- | --- | --- |
| N14 | rel13 | N14, `0x2000 → 0x2001` | `v[1..15]`, сохранены `v[0]` и `v[15..34]` |
| N15 | rel13 → rel14 | N15, `0x4000 → 0x4001` | `v[1..16]`, сохранены `v[0]` и `v[16..34]` |
| N16 | rel13 → rel14 → rel15 | N16, `0x8000 → 0x8001` | `v[1..17]`, сохранены `v[0]` и `v[17..34]` |
| N17 | rel13 → rel14 → rel15 → rel16 | N17, `0x10000 → 0x10001`, плюс битовый N17 | `v[1..18]`, сохранены `v[0]` и `v[18..34]` |

Например, успешные rel13, rel15 и rel16 при отсечке rel14 дают последовательную опору только N14. В отчёте `insert_support_by_length` вычисляет префикс по подтверждённым в профиле слотам FIX1. Это поле описывает наличие опор вставки. Соединение с N13 и пятью историческими ролями остаётся предметом отдельной приёмки.

## Control, профиль и часы

Один job `ubuntu-24.04`, 90 мин. CBMC 6.11.0/CaDiCaL, OB12, unwind36. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. Каждый слот имеет отдельные CWD, Cargo/Kani targets, tmp и stock export. `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, `TMPDIR=TMP=TEMP=$slot/tmp`. `RUSTFLAGS` строится в порядке frozen roster. Последний флаг `--cfg=kani_smallsort_rev2_u64_n14_n17_fix1`.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Prepare после сборки и аттестации tool выполняет cfg-on compile preflight с теми же `-Z` и `--no-assert-contracts` и с `--no-codegen --only-codegen --quiet`. Предел 180 с, первые структурированные rustc diagnostics сохраняются при отказе. Discovery требует 103 исторических REV2 harnesses при cfg-off и ровно четыре дополнительных plain Proof при cfg-on. Сохраняются kind, selector, file и targets исторических записей, прежние Check targets и пустые targets у plain. [Workflow](/root/kani-rev2-u64-n14-n17-control-w13-fix1/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/run.py)

| Стадия | Абсолютная граница от monotonic epoch | Внешний timeout |
| --- | --- | --- |
| Prepare | 54:00 | 56 мин |
| Входной gate | до 55:00 и до 60 с от входа | в measure |
| Четыре окна по 205 с | latest starts из roster, конец 68:40 | measure 18 мин, внутренний 16:45 |
| Финальная аттестация | 70:40 | в measure |
| Finish и upload-gate | cutoff 75:35, finish до 5 мин от входа | 6 мин и 1 мин |
| Upload | до 82:40 | 7 мин |
| План с резервом 6 мин | 88:40 | job 90 мин |

На слот 120 с VT, 4 GiB group RSS, 180 с cold wall, системный резерв 2 GiB, 10 с reap, 5 с receipt, 10 с launch headroom. Ранний вход в measure может сдвинуть effective latest starts раньше, сохраняя абсолютные верхние границы. Исход процесса и reap закрепляются до проекции. При отсечке следующий слот допускается с подтверждённым reap и в своём окне. Deferred receipt повторно пишется в ограниченном окне finish с признаком опоздания. Caps 4/96 MiB. Linux group sampler может недоучитывать RSS при смене TID после выхода главного потока.

`CH8_REV2_U64_N14_N17_FIX1_TRIGGER_TREE` ожидает Control tree `b4bf21f6578d30d40f66fd296af4258b6b0bc390`. `pins/sources/finish` проверяют fork `Tiramisu-Cake/kani`, push, ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, SHA из HEAD, `GITHUB_SHA` и `event.after`, единственный parent и чистый detached checkout. `sources` и `finish` сверяют admission receipt от `pins`. Публикация допускается после успешного finish и до cutoff. Review-trigger локальный и содержит `[skip ci]`.

`U64_N14_N17_FIX1_WITHIN_PROFILE` требует четыре `VERIFIED` с exit 0, `MATCHED`, все обязательные properties и covers, полные опубликованные проекции, своевременные receipts, sampler/reap, соблюдение лимитов и своевременную аттестацию `COMPLETE`. Отсечка, неполная проекция и поздний receipt оставляют роль `OPEN`. Подтверждённый нативный terminal при неполной проекции хранится отдельно как наблюдение. При повторной отсечке фиксированного R нужно разобрать фазу и стоимость, затем отдельно решать о диагностике по `p`. [Отчёт FIX1](/root/kani-rev2-u64-n14-n17-control-w13-fix1/ch8-cal1/report.py)

## Локальная сверка

- Проверены visibility, cfg, область runtime/contract diff и прежние blobs. Закреплённый `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` (`1.12.0-nightly 65ce8611fe`) с `--edition 2024 --config use_small_heuristics=Max` прошёл на новом и обоих исходных модулях `u64`. У registry форматированный diff порядка прежних `mod` побайтно совпадает с diff базы после удаления новой регистрации. Исторический порядок сохранён. TOML, YAML с уникальными ключами, восемь `bash -n`, 15 Python AST и `git diff --check` прошли.
- Модель фактического сдвига сверила 12 100 сочетаний отсортированных префиксов и вставляемых значений из `{0,1,2^63,u64::MAX}`. Во всех четырёх геометриях проверены оба края `p`, внутреннее равенство, эквивалентность equality cover, пост, кратности и frame.
- Shallow depth 2 без alternates прошёл `bundle verify/list-heads/unbundle` с сохранением HEAD, refs и shallow boundary. Проверены 23 ребра commit/tree/parent, 25 текущих blobs с историческими привязками, 445 текстовых и 372 нативных якоря. Локальный smoke `sources` выполнил реальные проверки Git-пинов и bundle с пропуском проверки подмодулей в синтетическом вызове.
- Синтетический detached trigger прошёл `pins` при +2 с, `sources` при +30 с, `finish` при +4500 с, `upload-gate` при +4535 с и `upload-check` при +4960 с. Отклонены чужое дерево, payload, fork/ref/attempt, подменённый admission receipt, 32/32 сдвига столбца новых якорей и опоздания +0,01 с. Сверены SHA-256 и размеры восьми членов синтетического индекса.
- `test_supervisor.py` в Control и review-trigger сохранил blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. На чистом detached review-trigger последовательно прошли 128/128 тестов на обычной и на каждой из свежих шкал 1/5/60 с. Время 36,252 / 41,256 / 39,840 / 38,405 с соответственно. Синтетика покрывает exact roster, extra selector/target, отсутствие каждой typed copy-группы или cover, сдвиги якорей, неверный exit и unwind, ресурсные отсечки, late receipt, reap/attestation, последовательность опор и предел публикации.
- Std, Control и review-trigger имеют author и committer `Tiramisu-Cake <igkharin@gmail.com>`. Локальный объём — Git, форматирование, статическая проверка и синтетика. Cargo, rustc, Kani, CBMC, CI, push и изменение Actions variables отсутствуют.
