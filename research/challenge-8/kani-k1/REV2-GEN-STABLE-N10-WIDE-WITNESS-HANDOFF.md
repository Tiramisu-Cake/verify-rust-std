# REV2 · Wide N10 stability witness

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Подготовлен один Ubuntu-слот `GEN-N10-WIDE-WITNESS-LITERAL-CORRUPT` на литеральном V12. Выбрана геометрия **N10**. Статическая подготовка не нашла риска развёртки, который требовал бы перехода на N8. Слот проверяет, что пост устойчивости реагирует на одну перестановку равных ключей после фактического unstable trait на Wide. Составной допуск N16 рассматривается отдельно. Его Wide N16 witness остаётся `OPEN / RSS_LIMIT`. Нативная компиляция cfg-on и результат слота ожидают независимого ревью и отдельного GO координатора. Исполнитель стадии — Claude Code, pane 11, вместо w13. [Задание](REV2-GEN-STABLE-N10-WIDE-WITNESS-TASK.md) · [Черновик допуска N16](REV2-GEN-STABLE-N16-ADMISSION.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std N10](/root/verify-rust-std-rev2-gen-stable-n10-wide-witness-w11) | `bec3b6ee805fd3640da34e20482a3de647b3c865` | `7ba43a3e1930dcd881a044fb9f87eb2208d9399b` | `cebdba9913d72c892eb6701d9a989bb2a9830768` |
| [Control N10](/root/kani-rev2-gen-stable-n10-wide-witness-control-w11) | `e54fde9f4c9c8e24085c6953f25c0d036c586a30` | `6d353bd8a1e1f587dc772a7a2958edc55ee78d9e` | `274370cb7b6692543e2d7d3400951724e236108a` |
| [Review-trigger, detached](/root/kani-rev2-gen-stable-n10-wide-witness-trigger-w11/control) | `5652a9c5d4e836a678eba48766ea5dad98debadd` | `6d353bd8a1e1f587dc772a7a2958edc55ee78d9e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n10-wide-witness-trigger-w11/control/ch8-cal1/CI-REQUEST.json) | `da2a7c1423432f217cfafe450a60df0cc34d1eb215392973f58582ace6298f16` |
| Exact roster, канонический JSON | `528906a5c447b5ebfb68646a5a5ff7073efdf83e8f046e9bf915008ae228a2e7` |
| Source bindings, канонический JSON | `2fb54e89d652773fd9d111cddf0d4f4ce09a648f0a508b72965ecaf7fc983a3c` |
| [Std bundle](/root/kani-rev2-gen-stable-n10-wide-witness-trigger-w11/control/ch8-cal1/std-overlay.bundle), 89 404 байт | `ea5805026c1419bbb1fad80dc2af11b352d83953634096ec05a5a8c3a245f914` |

Независимый pin — `CH8_REV2_GEN_STABLE_N10_WIDE_WITNESS_TRIGGER_TREE=6d353bd8a1e1f587dc772a7a2958edc55ee78d9e`. Repo `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и payload guards сохранены. Bundle объявляет один `HEAD` и связывает 34 последовательных overlay-коммита поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`. Upload-gate сверяет admission и индекс `smallsort-rev2-gen-stable-n10-wide-witness-artifact-v1` с четырьмя хэшами и инвентарём. Worktree w13 не изменялись.

## Слот и ожидаемый отказ

Exact selector `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::n10_wide_witness::gen_n10_wide_witness_literal_corrupt`. Это plain Proof с пустыми targets и Replace, `copy_back=false`, unwind36, OB12. Модуль добавлен в конец `rev2_gen_stable_n16_pilot.rs` под `kani_smallsort_rev2_gen_stable_n10_wide_witness`, check-cfg на `core/Cargo.toml:79`. Байтовый префикс файла FIX2 сохранён. Дельта Std состоит из этих двух мест. Runtime, контракты и blob `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` не изменены. [Std](/root/verify-rust-std-rev2-gen-stable-n10-wide-witness-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:1327)

Ожидается `FAILED/MATCHED`, exit 1 и ровно один `FAILURE` класса `assertion` на `GEN_N10_WIDE_STABLE_EQUAL_KEYS` в `rev2_gen_stable_n16_pilot.rs:1407:9`. Regular и stock export должны совпасть по ID, классу, файлу, строке и метке. Остальные восемь assertions требуют `SUCCESS`.

### Вход и маршрут

Переиспользованы `Wide` (24 байта, align 8, Copy+Freeze, три `u64`), `wide_less` с полным `key < key` и скалярный `same_wide`. Константы родительского модуля фиксируют `!has_efficient_in_place_swap::<Wide>()`, `SMALL_SORT_GENERAL_SCRATCH_LEN == 48` и размер scratch не больше `MAX_STACK_ARRAY_SIZE`. В `v[1..11]` обе пятёрки имеют ключи `[1,0,1,0,0]`, метки 0–9 и payload `0x8000_0000_0000_0100+tag`. Канарейки `v[0]=(2,16,0x1111_2222_3333_4444)` и `v[11]=(3,17,0xaaaa_bbbb_cccc_dddd)` сравниваются по всем полям.

Вызов `<Wide as UnstableSmallSortTypeImpl>::small_sort(&mut v[1..11], &mut less)` на `:1383` идёт через `smallsort.rs:134–139` и `:213–224` к private general со своим scratch48 (`:261–273`). При `len=10` и `size_of::<Wide>()=24` ветка S8 закрыта, работают два actual S4 (`:308–313`). Затем по одному fill rel4 в каждой половине (`:321–331`). В каждом fill ключ 0 сдвигает две единицы и встаёт после равных нулей. Merge выполняет пять actual пар сразу в V (`:342–347`, `:1014–1044`). При чётной длине копия `:1034` не исполняется. Тело не содержит `assume`, `kani::any()`, stubs и Check.

### Обе перестановки

Ожидаемые записи берутся из `INPUT` по константным индексам. Один скалярный проход `observe` с литеральными границами сверяет первую позицию напрямую. Затем цикл `1..10` проверяет все три поля по позиции, порядок ключей и возрастание меток при равных ключах. `memcmp` и поиск по меткам отсутствуют. Максимальный индекс 10 в V12 и 9 в expected10.

| Фаза | Метки по позициям `v[1..11]` | Assertions |
| --- | --- | --- |
| До обмена | `[1,3,4,6,8,9,0,2,5,7]` | `GEN_N10_WIDE_BEFORE_ORDER` :1387, `_RECORDS_BY_TAG` :1388, `_STABLE_EQUAL_KEYS` :1389, `_SWAP_PAIR` :1390, `_FRAME` :1394 |
| После обмена целых `v[3]`, `v[4]` | `[1,3,6,4,8,9,0,2,5,7]` | `GEN_N10_WIDE_AFTER_ORDER` :1404, `_RECORDS_BY_TAG` :1405, `_FRAME` :1406 |
| Последняя проверка | — | `GEN_N10_WIDE_STABLE_EQUAL_KEYS` :1407, ожидаемый `FAILURE` |

Перед обменом у `v[3]` и `v[4]` ключ 0, метка 4 из левой половины и метка 6 из правой. Обмен сохраняет порядок ключей и кратность каждой полной записи. Он создаёт ровно одну инверсию меток внутри группы равных ключей. Все координаты имеют колонку 9 и функцию exact selector.

| Cover | Координаты |
| --- | --- |
| `GEN_N16_WIDE_COMPARATOR_CALLED`, фактический компаратор из `wide_less` | `:35:5`, функция `rev2_gen_stable_n16_pilot::wide_less` |
| `AFTER_WIDE_N10_RETURN` | `:1384:9` |
| `GEN_N10_WIDE_WITNESS_CROSS_HALF_TIE`, пара до обмена | `:1395:9` |

Требуются 3/3 covers. Typed-copy инстанс `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>` сохраняет шесть групп свойств на `ptr/mod.rs:587:14`. Actual sites S4 `:832–835`, fill `:329`, gap `:722`, guard `:362` и merge `:885`, `:918` совпадают с N16 witness. Все полученные unwind properties требуют `SUCCESS`.

### Границы циклов и unwind36

| Цикл | Итераций на N10 |
| --- | ---: |
| `observe`, `for i in 1..10` | 9 |
| `for offset in [0, len_div_2]` | 2 |
| fill `for i in 4..5` в каждой половине | 1 |
| `insert_tail`, `loop` | не больше 4, на входе 2 сдвига |
| `bidirectional_merge`, `for _ in 0..5` | 5 |

Все границы меньше 36. Control восстанавливает границы из исходника и отклоняет расхождение с длинами массивов и unwind.

## Оценка CNF

До замера ожидаю первую CNF порядка 2–4 млн переменных и 10–19 млн дизъюнктов против 4,96 млн / 25,52 млн у литерального N16. Два S4 и scratch48 остаются. Число fill падает с восьми до двух, число пар merge с восьми до пяти. Это грубый диапазон по числу копий и выборов адресов. Затраты кодировки и групповой RSS не масштабируются линейно, поэтому риск `RSS_LIMIT` остаётся. Оценка одного job с setup 50–65 мин, hard timeout 90 мин. При `RSS_LIMIT` фиксируется остановка выбранного корня, второго слота и автоматического повтора нет. [Receipt N16 FIX2](/root/ch8-artifacts/run-46081825138/ch8-rev2-gen-stable-n16-close-wide-witness-Linux-X64-46081825138-1/slots/GEN-N16-WIDE-WITNESS-LITERAL-CORRUPT/receipt.json)

## Профиль и часы

Одна Ubuntu 24.04 X64 job до 90 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL, OB12, unwind36. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. Лимиты 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Cfg-on имеет 31 флаг, cfg-off опускает последний.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Ранний cfg-on compile preflight до обоих discovery list использует те же verify `-Z` без export-json, `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir "$preflight/kani-target" "$std/library"` и предел 180 с. Первые rustc diagnostics сохраняются. Discovery вызывает `"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json` в обоих cfg. Target и export холодные и единственные.

| Стадия | Дедлайн от начала job | Лимит |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Identity gate и latest start | 55:00 | До 60 с с начала measure |
| Единственное окно | 58:25 | 205 с |
| Финальная аттестация | 60:25 | Measure 6:30 внутренний, 9 мин внешний |
| Finish и upload-gate | 65:20 | 5 с запаса на запуск upload |
| Upload | 72:25 | Внешние 7 мин |
| План с резервом | 78:25 | Job 90 мин |

`GEN_STABLE_N10_WIDE_WITNESS_WITHIN_PROFILE` требует одного своевременного `FAILED/MATCHED` с exit 1, полного receipt и projection, трёх достигнутых covers, sampler/reap, лимитов и своевременной аттестации `COMPLETE`. Caps 4/96 MiB, supervisor, checkpoint исхода, подтверждение reap до проекции и ограничение повтора receipt дедлайном сохранены. Receipt содержит первую CNF, стадии, VT/cold, group и CBMC RSS, PSS и оговорку о неатомарной выборке Linux при смене TID. Для отсутствующего маркера или замера сохраняется причина.

## Discovery и исторические опоры

Cfg-off содержит 179 исторических записей: 178 прежних и N16 FIX2 witness. Cfg-on добавляет один plain Proof с пустым target. Активный roster содержит только N10. Исторические roster N16 CLOSE, FIX1, pilot и N16 witness закреплены своими digest, их координаты сверяются на собственных ревизиях. N16 witness `9241da11…` проверяется на `cebdba9913`. Исправленные bounds rel5–7 проверяются на CLOSE FIX1. Точное сообщение `standard harness has a contract target` проверено для CLOSE, N16 witness и N10. В отчёте внешние обязательства фиксируют, что N16 witness из run 46081825138 остаётся `RSS_LIMIT`. Маршрут, канарейки и наблюдение N10 не переносятся на N16 и на произвольные входы.

## Валидация

- Control заново вычисляет обе перестановки из литерального `INPUT` в исходнике. Он сверяет ключи, метки, payload, канарейки, точную пару обмена, единственную инверсию после него, границы циклов, unwind36, диапазон вызова и индексы frame. Синтетика отклонила 17 мутаций: две границы цикла, unwind, диапазон вызова, длину и ключ входа, канарейку, payload, оба порядка, индексы observer, пару в `SWAP_PAIR`, tie cover, обменную пару, индекс frame, пару из одной половины и отсутствие модуля.
- Source gate на Std N10 прошёл: append-only слои FIX2 и N10, 34 commit/tree/parent, 30 текущих blobs и 1 192 литеральные координаты, из них 21 новая. Совпали native coordinates всех исторических и нового roster и actual typed-copy sites. Видимость `super::super::super::UnstableSmallSortTypeImpl` и унаследованных `Wide`, `kani`, `same_wide`, `wide_less` та же, что в FIX2.
- Rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max` и `style_edition=2024` прошёл для нового и прежнего blob модуля. Проверены TOML, YAML с уникальными ключами, восемь блоков `bash -n` и `git diff --check` обеих дельт.
- Depth-2 Std checkout без alternates принял bundle. Исходный HEAD, shallow boundary и отсутствие refs сохранены. На точном detached trigger прошли `pins`, `sources`, `finish`, `upload-gate` и `upload-check`. Локальная проверка submodules заменена чистыми detached Std и tool с точными commit/tree. `finish` сформировал один `NOT_STARTED` receipt. Отклонены tree FIX2, чужой payload, подмена индекса и индексированного receipt, поздний upload.
- Синтетика suite проверила исчезновение исторических CLOSE и N16 witness, активный N16 вместо N10, проекцию N16 witness против N10, перенос координаты и метки отказа N16, потерю каждой предпроверки, cover tie и return, чужой и второй failure, неполный receipt, превышение VT и RSS, просроченный receipt, потерю reap и аттестации.
- Blob `test_supervisor.py` равен `df63a457c3adf648d360f3d559d5d40ef00a9427`. Полный suite Python 3.12.3 прошёл последовательно на точном trigger. Обычная шкала 143/143 за 56,990 с, старт с 1 с 143/143 за 55,678 с, с 5 с 143/143 за 57,778 с, с 60 с 143/143 за 57,945 с.
- Локальная стадия обошлась без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Std, Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## Дальше

Независимое ревью пакета, затем отдельный GO координатора на установку tree variable и push review-trigger.
