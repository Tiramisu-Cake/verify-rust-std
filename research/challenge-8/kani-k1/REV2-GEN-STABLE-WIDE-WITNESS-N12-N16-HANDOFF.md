# REV2 · Wide N12 и N16 · контроли устойчивости

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Действующие пины пакета находятся в разделе [FIX2](#fix2--поиск-cnf-по-всему-префиксу-spill). Таблицы ниже фиксируют пакет R1, раздел FIX1 — первый раунд исправлений. [Ревью R1](REV2-GEN-STABLE-WIDE-WITNESS-N12-N16-REVIEW.md)

Подготовлен один Ubuntu-пакет из двух последовательных singleton. Первым идёт stock N12 `GEN-N12-WIDE-WITNESS-LITERAL-CORRUPT`. Вторым идёт exact FIX2 N16 `GEN-N16-WIDE-WITNESS-LITERAL-CORRUPT` за отложенным relay stdout CBMC. Relay стоит в PATH только у дочернего процесса N16. N12 даёт контроль для будущей строки допуска N12. N16 измеряет, снимает ли разнесение работы CBMC и разбора его JSON превышение 4 GiB. Допуск N16 по-прежнему требует завершённого нативного `FAILED/MATCHED` на N16. Исторический `RSS_LIMIT` run 46081825138 остаётся в ledger. Нативная компиляция и результаты ожидают независимого ревью и отдельного GO координатора. Исполнитель стадии — Claude Code, pane 11. [Задание](REV2-GEN-STABLE-WIDE-WITNESS-N12-N16-TASK.md) · [Допуск N16](REV2-GEN-STABLE-N16-ADMISSION.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std N12](/root/verify-rust-std-rev2-gen-stable-wide-witness-n12-n16-w11) | `b465318cc95001c651011c2e5579bba12669b467` | `9d4c78baf73fae2b15f29c2c81730399e1a2d9fa` | `bec3b6ee805fd3640da34e20482a3de647b3c865` |
| [Control N12/N16](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11) | `507a01258faac8d748dbdcbea9aa82a16f4467fc` | `a128c58ffe71e577d50ae0f2b2620cba3094fcd2` | `e54fde9f4c9c8e24085c6953f25c0d036c586a30` |
| [Review-trigger, detached](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control) | `f7db388ba89a0b8a22529ceb30ee96e5b8779fa5` | `a128c58ffe71e577d50ae0f2b2620cba3094fcd2` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control/ch8-cal1/CI-REQUEST.json) | `a5a5d1c1f0f561432d3d96d3300e82d8817432d6a99b0e625755bfad77870fe8` |
| Exact roster, канонический JSON | `7f4ae44e4063234934ed4cbcb3cec182a8ebe15cbba0e4845262acdcc8bea9cb` |
| Source bindings, канонический JSON | `8df3d8ed069a47ecbb993a86a864cde54c111a45c7bce06ef8870f4ede597929` |
| [Std bundle](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control/ch8-cal1/std-overlay.bundle), 92 368 байт | `45dfe97fa55e311f7a9a8f99fa0c32042c64e51cc02850ca5af77f356ebe8711` |

Независимый pin — `CH8_REV2_GEN_STABLE_WIDE_WITNESS_N12_N16_TRIGGER_TREE=a128c58ffe71e577d50ae0f2b2620cba3094fcd2`. Сохранены repo `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и payload guards. Bundle объявляет один `HEAD` и связывает 35 последовательных overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`. Frozen request дополнительно связывает режим relay и SHA-256 его исходника `ch8-cal1/cbmc_relay.py`: `5c9fed472325c3f38a278bbe87c4cf83cbea246dc15167b6f9b573495f1e64cf`. Upload-gate сверяет индекс `smallsort-rev2-gen-stable-wide-witness-n12-n16-artifact-v1` с четырьмя хэшами, хэшем relay и инвентарём. Worktree N10 и w13 не изменялись.

## Слот 1 · N12 на штатном PATH

Exact selector `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::n12_wide_witness::gen_n12_wide_witness_literal_corrupt`. Это plain Proof с пустыми targets и Replace, `copy_back=false`, unwind36, OB12. Модуль дописан в конец `rev2_gen_stable_n16_pilot.rs` под `kani_smallsort_rev2_gen_stable_n12_wide_witness`, check-cfg добавлен на `core/Cargo.toml:80`. Байтовый префикс файла N10 сохранён. Дельта Std состоит из этих двух мест. Runtime, контракты и blob `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` не изменены. Blob модуля `4acfe853df43589701d54d6d971767092502e043`, `core/Cargo.toml` `6d0794422c2fd077c379abe9398fe64cccd426ce`. [Std](/root/verify-rust-std-rev2-gen-stable-wide-witness-n12-n16-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:1411)

Ожидается `FAILED/MATCHED`, exit 1 и ровно один `FAILURE` класса `assertion`: `GEN_N12_WIDE_STABLE_EQUAL_KEYS` на `rev2_gen_stable_n16_pilot.rs:1493:9`. Regular и stock export должны совпасть по ID, классу, файлу, строке и метке. Остальные восемь assertions требуют `SUCCESS`.

### Вход и маршрут

Переиспользованы `Wide` (24 байта, align 8, Copy+Freeze, три `u64`), `wide_less` с полным `key < key` и скалярный `same_wide`. Литеральный V14 содержит внешние записи N10: `v[0]=(2,16,0x1111_2222_3333_4444)` и `v[13]=(3,17,0xaaaa_bbbb_cccc_dddd)`. В `v[1..13]` обе шестёрки имеют ключи `[1,0,1,0,0,0]`, метки 0–11 по исходной позиции и `payload=0x8000_0000_0000_0100+tag`.

Вызов `<Wide as UnstableSmallSortTypeImpl>::small_sort(&mut v[1..13], &mut less)` на `:1469` идёт через `smallsort.rs:134–139` и `:213–224` к private general со своим scratch48 (`:261–273`). При `len=12` ветка S8 на `:297` закрыта размером 24, работают два actual S4 (`:308–313`). Затем по два fill `4..6` в каждой половине (`:321–331`). Каждый ключ 0 сдвигает две единицы и встаёт после равных нулей. Merge выполняет шесть actual пар сразу в V (`:342–347`, `:1014–1044`). При чётной длине копия `:1034` не исполняется. Тело не содержит `assume`, `kani::any()`, stubs и Check.

### Обе перестановки

`EXPECTED` и `CORRUPTED` берут полные записи из `INPUT` по константным индексам. Один скалярный проход `observe` с литеральной границей `1..12` сверяет все три поля по позиции, порядок ключей и возрастание меток при равных ключах. `memcmp` и поиск по меткам отсутствуют. Максимальный индекс 12 в V14 и 11 в expected12. Control проверяет, что первый `observe` получает `&EXPECTED` после вызова, а второй — `&CORRUPTED` после обмена. Это закрывает замечание 1 ревью N10.

| Фаза | Метки по позициям `v[1..13]` | Assertions |
| --- | --- | --- |
| До обмена | `[1,3,4,5,7,9,10,11,0,2,6,8]` | `GEN_N12_WIDE_BEFORE_ORDER` :1473, `_RECORDS_BY_TAG` :1474, `_STABLE_EQUAL_KEYS` :1475, `_SWAP_PAIR` :1476, `_FRAME` :1480 |
| После обмена целых `v[4]`, `v[5]` | `[1,3,4,7,5,9,10,11,0,2,6,8]` | `GEN_N12_WIDE_AFTER_ORDER` :1490, `_RECORDS_BY_TAG` :1491, `_FRAME` :1492 |
| Последняя проверка | — | `GEN_N12_WIDE_STABLE_EQUAL_KEYS` :1493, ожидаемый `FAILURE` |

Перед обменом у `v[4]` и `v[5]` ключ 0. Метка 5 приходит из левой половины, метка 7 из правой. Обмен сохраняет порядок ключей и кратность каждой полной записи. Он создаёт ровно одну инверсию меток внутри группы равных ключей. Все координаты имеют колонку 9 и функцию exact selector.

| Cover | Координаты |
| --- | --- |
| `GEN_N16_WIDE_COMPARATOR_CALLED`, фактический компаратор из `wide_less` | `:35:5`, функция `rev2_gen_stable_n16_pilot::wide_less` |
| `AFTER_WIDE_N12_RETURN` | `:1470:9` |
| `GEN_N12_WIDE_WITNESS_CROSS_HALF_TIE`, пара до обмена | `:1481:9` |

Требуются 3/3 covers. Typed-copy инстанс `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>` сохраняет шесть групп свойств на `ptr/mod.rs:587:14`. Actual sites S4 `:832–835`, fill `:329`, gap `:722`, guard `:362` и merge `:885`, `:918` совпадают с N10 и N16. Все полученные unwind properties требуют `SUCCESS`.

| Цикл | Итераций на N12 |
| --- | ---: |
| `observe`, `for i in 1..12` | 11 |
| `for offset in [0, len_div_2]` | 2 |
| fill `for i in 4..6` в каждой половине | 2 |
| `insert_tail`, `loop` | не больше 5, на входе по 2 сдвига |
| `bidirectional_merge`, `for _ in 0..6` | 6 |

Все границы меньше 36. Ориентир первой CNF 15–16 млн дизъюнктов получен интерполяцией N10 → N16. Попадание в 4 GiB проверит запуск. Успех покрывает один вход N12. Функциональные рёбра этой длины нужны отдельно.

## Слот 2 · exact FIX2 N16 за relay

Selector `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::close_witness_fix1::gen_n16_wide_witness_literal_corrupt` и вся строка roster байт в байт равны исторической строке FIX2. Digest `9241da1124f35a1ce9ade90d3ab7eddcb457a5df5c4627fba0ae1463f559a38f` сохранён. Сохранены cfg-вектор FIX2 из 30 флагов без N10 и N12, V18/D48, пять предпроверок, три постпроверки, точка обмена, три covers, typed/unwind и единственный `FAILURE` `GEN_N16_WIDE_STABLE_EQUAL_KEYS` на `:1323:9`. Координаты сверяются на собственной ревизии `cebdba9913`. Цепочка append-only FIX2 → N10 → N12 доказывает, что эти байты на текущем overlay не изменились. Тест сравнивает argv и `RUSTFLAGS` с receipt FIX2 из run 46081825138. Отличается только имя каталога состояния. Профиль и аргументы CBMC те же. Новый receipt отличается способом передачи stdout, фазами измерения и пинами пакета. [FIX2 handoff](REV2-GEN-STABLE-N16-CLOSE-HANDOFF.md#fix2--wide-witness-на-литеральном-входе)

### Relay stdout CBMC

Stock Kani `9834c96ce9` в режиме `regular` запускает `cbmc` через PATH с `--json-ui` (`kani-driver/src/call_cbmc.rs:178`, `:191`) и читает pipe до EOF, затем ждёт процесс. Разбор буферизует JSON-объект результатов целиком. Relay откладывает этот разбор до завершения CBMC без правок бинарей и фильтрации stdout. [Relay](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11/ch8-cal1/cbmc_relay.py) · [Сторона runner](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11/ch8-cal1/stdout_relay.py)

1. **Область PATH.** Только `measure_slot` для `GEN-N16-WIDE-WITNESS-LITERAL-CORRUPT` ставит `$slot/relay/bin` первым в PATH дочернего Kani. В `prepare`, discovery и N12 PATH штатный, тест проверяет `path_prefix=None` для N12. До подстановки `resolve_real` находит `cbmc` на штатном PATH, разрешает путь и сверяет путь, размер, SHA-256 и первую строку версии 6.11.0 с аттестацией `setup.json`. Relay получает абсолютный путь и `(dev, inode, size, mtime_ns)` и перед каждым вызовом проверяет, что файл не подменён. Иначе слот `NOT_STARTED / STDOUT_RELAY_UNAVAILABLE` без запуска Kani.
2. **Установка.** `relay/bin/cbmc` создаётся эксклюзивно с режимом `0700`. Это строка `#!<python3 runner> -I` и байты frozen `cbmc_relay.py`. Конфиг `0600` лежит рядом. Журналы и spill находятся в `relay/journal` и `relay/spill` (`0700`). До запуска проверяется свободное место: 4 GiB spill плюс 2 GiB резерва.
3. **Вызовы.** `--version` и прочие вызовы без `--json-ui` замещаются реальным бинарём через `execve` с исходным argv-хвостом и исходным окружением. Вызов с `--json-ui` запускает реальный CBMC с `argv[0]="cbmc"`, исходным argv-хвостом, cwd, stdin, stderr и окружением. Окружение берётся байт в байт из `/proc/self/environ` relay, поэтому коррекция локали интерпретатором его не меняет. Relay и CBMC остаются в сессии и группе Kani без нового PGID.
4. **Spill и replay.** Stdout CBMC читается блоками 64 KiB через pipe и пишется в `spill-<pid>.bin` (`O_EXCL|O_NOFOLLOW`, `0600`). Используются обычный диск, без mmap и без чтения целиком. Короткие записи дописываются. После `wait` и reap CBMC все байты читаются тем же блоком и передаются в исходном порядке в pipe Kani. Затем relay закрывает stdout, удаляет spill и возвращает исходный код. Если CBMC убит сигналом, relay после полного replay завершается тем же сигналом. Журнал фиксирует объём и SHA-256 записанных и переданных байтов, PID/start ID/PGID/SID, хэш argv, хэш окружения, пик RSS relay и монотонные отметки `CBMC start`, `wait done`, `replay first byte`, `replay end`.
5. **Сбои.** Превышение 4 GiB даёт `SPILL_LIMIT`. Ошибка записи даёт `SPILL_WRITE_ERROR`, нехватка диска — `SPILL_DISK_UNAVAILABLE`. В этих случаях relay посылает живому CBMC `SIGTERM`, через 2 с `SIGKILL`, подтверждает reap, не передаёт ни байта и выходит с кодом 125. Обрыв или расхождение replay дают `REPLAY_INCOMPLETE`. CBMC к этому моменту уже reaped. Часть байтов успела уйти в Kani, остаток не передаётся, spill остаётся, код выхода 125. Kani получает неполный JSON, а доставка помечается `INCOMPLETE`. Исправлено в FIX1. `SIGTERM`/`SIGINT`/`SIGHUP` группы дают `CANCELLED` с тем же порядком остановки. Штатный внешний дедлайн supervisor охватывает всю группу, `--harness-timeout` не используется. Штатный VT Kani включает replay.
6. **Приёмка доставки** (`stdout_relay.collect`) идёт после checkpoint и до проекции, в окне receipt. Требуется ровно один relay-вызов `--json-ui` с исходом `COMPLETE`. Остальные вызовы допускаются только как `--version`. Argv-хвост должен совпасть с frozen профилем stock `cbmc_flags`, где меняется только goto-файл внутри каталога слота, и с verbose-строкой `[Kani] Running: \`cbmc ...\`` из stdout.log. Профиль: `--no-malloc-may-fail --no-undefined-shift-check --no-signed-overflow-check --nan-check --no-self-loops-to-assumptions --no-pointer-primitive-check --unwind 36 --sat-solver cadical --slice-formula --object-bits 12 <goto> --verbosity 9 --json-ui`. Он совпадает с наблюдённой stock-командой из run 45077134698, где отличался только `--unwind 32`. Также требуются равные объём и SHA-256 spill и replay, `wait done < replay first byte`, отметки внутри наблюдения supervisor, общие PGID/SID, нормальный код CBMC и удалённый spill. Census должен видеть PID реального CBMC и не считать relay процессом CBMC. Relay запускается интерпретатором, поэтому его образ `python3`. Любое отклонение даёт `stdout_delivery=INCOMPLETE`, и слот остаётся `OPEN`. Доставка только запрещает match: `MATCHED` по-прежнему выдаёт обычная regular/stock проекция.
7. **Стоп до replay.** После подтверждённого supervisor reap runner читает до 16 MiB префикса оставшегося spill, извлекает `messageText` и прогоняет штатный разбор маркеров. Начиная с FIX1 это происходит после проекции и в отдельном ограниченном окне. Так сохраняются первая CNF, SAT-маркеры и терминальные маркеры. Затем spill удаляется. При отсутствии маркера записывается `NO_RECOGNIZED_NATIVE_MARKER_IN_PREFIX`, при неподтверждённом reap spill сохраняется с `REAP_UNCONFIRMED_SPILL_KEPT`. Эти наблюдения не заменяют regular/stock приёмку.

### Census группы

Телеметрия обоих слотов публикует `group_census` из того же census, что и RSS-guard. Ключевые сэмплы: пик группы, последний сэмпл перед стопом или завершением, и для N16 пики до `wait done`, во время replay и после replay. Фаза relay читается из его журнала на каждом сэмпле. В каждом ключевом сэмпле сохраняются до 64 процессов по убыванию RSS: PID, PPID, start ID, образ, RSS и признак CBMC. Также записываются монотонное время, групповой RSS, RSS CBMC, PSS CBMC при наличии, число строк, опущенных лимитом 64, и число PID, пропущенных при чтении `/proc`. Если в сэмпле есть пропуски, `attribution_complete=false`. Измеритель, порог 4 GiB, критерий остановки и оговорка Linux RSS прежние.

## Профиль и часы

Одна Ubuntu 24.04 X64 job до 90 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. На каждый корень 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Cfg-on имеет 32 флага, cfg-off опускает последний. Строка N16 использует 30 флагов FIX2.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Для N16 окружение Kani отличается только префиксом `PATH=$slot/relay/bin:…`. Ранний cfg-on compile preflight до обоих discovery list и сохранение первых rustc diagnostics не изменились.

| Стадия | Дедлайн от начала job | Лимит |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Identity gate и latest start N12 | 55:00 | До 60 с с начала measure |
| Latest start N16 | 58:25 | Окно N12 205 с |
| Конец окон | 61:50 | Окно N16 205 с |
| Финальная аттестация | 63:50 | Measure 9:55 внутренний, 13 мин внешний |
| Finish и upload-gate | 68:45 | 5 с запаса на запуск upload |
| Upload | 75:50 | Внешние 7 мин |
| План с резервом | 81:50 | Job 90 мин |

При полном исходе каждый слот оценивается отдельно (`slot_diagnoses`). Нужны своевременный `FAILED/MATCHED` с exit 1, полный receipt и проекция, 3/3 covers, sampler/reap, лимиты профиля и своевременная аттестация `COMPLETE`. Для N16 дополнительно нужна доставка `COMPLETE`. Общий диагноз `GEN_STABLE_WIDE_WITNESS_N12_N16_WITHIN_PROFILE` требует обоих. Сохранены caps 4/96 MiB, checkpoint перед проекцией, ограничение повтора receipt дедлайном, reap до следующего слота и финальная аттестация. Если N12 не подтвердил reap, N16 не запускается.

## Discovery и исторические опоры

Cfg-off содержит 180 исторических записей: 178 прежних, N16 FIX2 и N10. Cfg-on добавляет ровно один plain Proof N12 с пустым target. Активный roster выбирает N12 и исторический N16 FIX2. Discovery считает добавлением только N12. Активный N10 или переименованный N16 на месте N12 отклоняются. Точное сообщение `standard harness has a contract target` проверено для CLOSE, N16, N10 и N12. Исторические roster N10 `528906a5…`, N16 witness `9241da11…`, CLOSE, FIX1 и pilot закреплены своими digest. Их координаты сверяются на собственных ревизиях. Bounds rel5–7 проверяются на CLOSE FIX1.

## Валидация

- **Std.** Rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max` и `style_edition=2024` прошёл для нового и прежнего blob модуля. Файл N10 — побайтный префикс нового. Проверены TOML и `git diff --check`. Независимая Python-модель трассы (S4, `insert_tail`, `merge_up/down` по `smallsort.rs`) дала `[1,3,4,5,7,9,10,11,0,2,6,8]` и устойчивость на всех 3^12 шаблонах ключей. После обмена порядок ключей сохраняется и появляется единственная инверсия на позиции 3. Модель не использует `sorted` как оракул, это отвечает на замечание 2 ревью N10.
- **Source gate на Std N12.** Пройдены append-only слои FIX2, N10 и N12, 35 commit/tree/parent, 30 текущих blobs и 1 213 литеральных координат, из них 21 новая. Совпали native coordinates всех исторических roster и N12, actual typed-copy sites и видимость `super::super::super::UnstableSmallSortTypeImpl`. Gate пересчитывает обе перестановки N12 из литерального `INPUT` и сверяет ключи, метки, payload, канарейки, пару обмена, единственную инверсию, границы циклов, unwind36, диапазон вызова, индексы frame и массив каждого `observe`. Синтетика отклонила 20 мутаций N12, включая канарейку и перестановку `EXPECTED`/`CORRUPTED` между наблюдателями. Gate N10 останавливается на следующем opt-in модуле.
- **Эквивалентность транспорта**, синтетика без верификатора (`test_relay.py`). Синтетический CBMC выдаёт JSON-UI объёмом 22 260 535 байт с полным фикстуром проекции N16: все свойства, covers и единственный failure. Прямой pipe и relay дают одинаковые байты, SHA-256 и коды 10 и 0. В обоих случаях штатная проекция даёт `MATCHED` с единственным `GEN_N16_WIDE_STABLE_EQUAL_KEYS` и 3/3 covers. Без relay первый байт приходит до выхода дочернего процесса, через relay — только после него и после `wait done`. Хэш окружения, argv, cwd, PGID и SID у relay и реального CBMC совпадают. Пик RSS relay не зависит от объёма потока: 17 344 KiB на 22,3 МБ против 17 244 KiB на 43 КБ. Тест требует разницы меньше 4 МиБ.
- **Сбои, синтетика.** Проверены `--version` passthrough и сигнал CBMC с полным replay и тем же сигналом. Переполнение spill даёт `SPILL_LIMIT` без единого байта на выходе. Короткие записи replay сохраняют порядок и хэш. Ошибка записи spill (`ENOSPC`) и нехватка диска проверены до установки и до spill. Остановка группы через production supervisor дала `CANCELLED`, reap CBMC и пустой stdout. После reap runner извлёк первую CNF 4 956 964 / 25 517 502 из префикса spill и удалил его. Сквозной `measure_slot` ставит relay только для N16, сверяет реальный бинарь, строит census и оценивает доставку. Недоступный relay не запускает N16. Census не считает интерпретатор relay процессом CBMC. Приёмка отклоняет 21 нарушенную привязку. Среди них исход relay, хэши и объёмы, ранний replay и пропущенные отметки, отметки вне наблюдения supervisor, профиль argv и его хэш, verbose-команда Kani, cwd, PGID/SID, сигнал CBMC, выход за cap, ноль или два relay-вызова, чужой passthrough, остаток spill, goto вне слота, учёт relay как CBMC и невидимый census PID CBMC.
- **Trigger.** Depth-2 Std checkout без alternates принял bundle. HEAD, shallow boundary и отсутствие refs сохранены. На точном detached trigger прошли `pins`, `sources`, `finish`, `upload-gate` и `upload-check`. Проверка submodules заменена чистыми detached Std и tool с точными commit/tree. `finish` сформировал два `NOT_STARTED` receipt и диагноз `OPEN`. Отклонены tree N10, чужой payload N10 trigger, подмена индекса и receipt, поздний upload. Проверены YAML с уникальными ключами, восемь блоков `bash -n` и `git diff --check`. Runtime и tool diff отсутствуют.
- **Suite.** Blob `test_supervisor.py` равен `df63a457c3adf648d360f3d559d5d40ef00a9427`, production RSS-guard сохранён. Supervisor лишь дописывает в сэмпл число пропущенных PID. Полный suite Python 3.12.3 прошёл последовательно на точном trigger с лимитом 90 с: обычная шкала 164/164 за 66,207 с, старт с 1 с 164/164 за 67,084 с, с 5 с 164/164 за 65,925 с, с 60 с 164/164 за 66,323 с. Межпроцессные тесты relay сравнивают отметки по ядерному `CLOCK_MONOTONIC`, потому что relay и синтетический CBMC живут в других процессах.
- Локальная стадия обошлась без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Std, Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## Ограничения

- Relay не исполнялся с настоящими Kani и CBMC. Эквивалентность показана на синтетических дочерних процессах и штатной проекции фикстура. Профиль argv выведен из stock `cbmc_flags` и наблюдённой stock-командой с другим unwind. Если реальная команда отличится, N16 получит `INCOMPLETE` доставки, а не ложный match.
- Объём JSON-вывода CBMC на N16 неизвестен. Запись на диск и повторное чтение добавляют время в VT и cold wall и нагружают файловый кеш. Большой поток грязных страниц может временно снизить `MemAvailable` и вызвать штатный `LIVE_MEMORY_RESERVE`. Это относится к измерителю, а не к relay.
- Разнесение снимает одновременность позднего буфера Kani и живого CBMC. Пик каждой стадии отдельно ещё не измерен. При RSS CBMC около 3,33 GiB запас остаётся малым. Если N16 снова упрётся в лимит до replay, receipt даст census и CNF из префикса spill.
- Census фиксирует RSS каждого процесса, а не PSS группы. PSS читается только для CBMC. Оговорка Linux о смене TID и двойном учёте общих страниц сохраняется.
- Если ревью не подтвердит эквивалентность relay, предлагаю нести в запуск только N12, а N14 готовить для его собственной строки. N16 с одним PID-снимком к запуску не готовить.

## FIX1 · окно разбора spill и замечания R1

**READY_FOR_REVIEW · `go=NOT_GRANTED` · `proof_credit=NONE`.** Основание — ревью R1 (g0 `bec49a4d6f`), GO_WITH_NITS, GO отложен до п. 1. Лимиты, Std, roster и bindings не изменены. Control получил новый коммит поверх R1 без force. Review-trigger новый, с тем же sole parent.

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Std N12, без изменений | `b465318cc95001c651011c2e5579bba12669b467` | `9d4c78baf73fae2b15f29c2c81730399e1a2d9fa` | `bec3b6ee805fd3640da34e20482a3de647b3c865` |
| [Control FIX1](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11) | `b5e6c89c0e06cc55e264c4d297086e3ae629300a` | `4d4e7f5b3b4ccb6fc112eb5b93645d8052c801e0` | `507a01258faac8d748dbdcbea9aa82a16f4467fc` |
| [Review-trigger FIX1, detached](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control) | `60650bf250f7021623eac6e54993f66e98b05608` | `4d4e7f5b3b4ccb6fc112eb5b93645d8052c801e0` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control/ch8-cal1/CI-REQUEST.json) | `1247e9e65a6be3fe41862b3559f6996284024d1d3ee3e03bbaf9546ecd4ba3f9` |
| Exact roster, канонический JSON, без изменений | `7f4ae44e4063234934ed4cbcb3cec182a8ebe15cbba0e4845262acdcc8bea9cb` |
| Source bindings, канонический JSON, без изменений | `8df3d8ed069a47ecbb993a86a864cde54c111a45c7bce06ef8870f4ede597929` |
| Std bundle, 92 368 байт, без изменений | `45dfe97fa55e311f7a9a8f99fa0c32042c64e51cc02850ca5af77f356ebe8711` |
| `cbmc_relay.py`, связан с frozen request | `c8b4c070dbd12a8acafa4b23df0b74833b600333f539b66fc9d27eccee3613b7` |

Независимый pin — `CH8_REV2_GEN_STABLE_WIDE_WITNESS_N12_N16_TRIGGER_TREE=4d4e7f5b3b4ccb6fc112eb5b93645d8052c801e0`. Хэш CI-REQUEST изменился только из-за нового SHA-256 relay в `stdout_relay.source_sha256`.

1. **Окно разбора spill (п. 1).** Census и сводка памяти теперь пишутся в receipt до checkpoint, как только supervisor подтвердил reap. Поэтому `memory_telemetry.group_census` попадает в receipt и при `RSS_LIMIT`, даже если позднее истечёт окно разбора. `stdout_relay.collect` в окне проекции оценивает только журналы, verbose-строку Kani и наличие spill. Префикс spill читает `drain_spill` после `slot_projection`. У него своё окно до `receipt_deadline − 1 с`, общий бюджет receipt не меняется. Скан стал однопроходным и выполняется на уровне C: развёрнутый шаблон JSON-строки по 16 MiB, остановка на 16 384 сообщениях или 1 MiB текста, остаток считается через `bytes.count`. Учитываются `messages`, `messages_parsed` и `messages_omitted`. Худший префикс из 16 MiB коротких сообщений разбирается за 0,39–0,52 с, прежний построчный разбор занимал 6,5 с. Префикс без сообщений занимает 0,05 с. Если окно всё же истечёт, receipt получает `SPILL_PREFIX_DEADLINE`, а spill удаляется после записи receipt. [Run](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11/ch8-cal1/run.py:771) · [Скан](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11/ch8-cal1/stdout_relay.py:195)
2. **Новый тест п. 1.** Тест проходит через `measure_slot` с реальным `receipt_window`: остановка N16 по `RSS_LIMIT` до replay, spill 17 MiB. В нём 16 MiB худших сообщений, первая CNF 4 956 964 / 25 517 502 и census из трёх процессов. Весь путь укладывается в 4 с. В receipt есть CNF префикса, `prefix_bytes_read=16 MiB`, census с группой 5 094 309 KiB, удалённый spill и `projection_status` не `DEADLINE`. Отдельный тест подтверждает запись `SPILL_PREFIX_DEADLINE` и удаление spill.
3. **`REPLAY_INCOMPLETE` (п. 2).** Текст §5 исправлен. Новый тест с настоящим потребителем закрывает pipe после 128 KiB из 2 MiB. Relay получает `BrokenPipeError`, выходит с кодом 125, пишет `replay_bytes` меньше `spill_bytes`, оставляет spill. Доставка `INCOMPLETE`.
4. **Сигналы при остановке (п. 3).** Перед `stop_child` после любого сбоя, а также перед финальной записью журнала при `RelayFailure` и внутренней ошибке relay ставит SIG_IGN для SIGTERM, SIGINT и SIGHUP. Тест фиксирует это состояние в момент `stop_child`. Тестовый fixture восстанавливает обработчики, потому что игнорирование наследуется через exec.
5. **Доставка рядом с результатом (п. 4).** Receipt содержит `stdout_delivery` (`STOCK_PIPE` для N12, статус relay для N16), а `expected_result` дублирует его в поле `stdout_delivery`. В SUMMARY.md колонка «Stdout delivery» стоит сразу после «Expected result». Тест сверяет заголовок, разделитель и значения `STOCK_PIPE` и `INCOMPLETE`.
6. **tmpfs (п. 5, сделано).** Установка relay определяет тип ФС каталога spill по самой длинной точке монтирования в `/proc/self/mounts`. Spill на `tmpfs` и `ramfs` отклоняется, и N16 получает `NOT_STARTED / STDOUT_RELAY_UNAVAILABLE`. Тип ФС пишется в receipt. Здесь `/root` и `/tmp` на xfs, `/dev/shm` на tmpfs.
7. **Self-test (п. 6, оставлен).** Лимит 90 с на прогон не менялся. Запас на этой машине около 20 с. Отказ по времени дешёвый и случается в `pins`, до измерений.

Валидация FIX1: 169 тестов, из них 23 в `test_relay.py`. На точном detached trigger повторены `pins`, `sources`, `finish` с двумя `NOT_STARTED`, `upload-gate` и `upload-check`. Отклонены tree и payload trigger R1, подмена индекса и receipt, поздний upload. Std-checkout сохранил HEAD `dab03cf510`, shallow boundary и отсутствие refs. `git diff --check` пройден. Blob `test_supervisor.py` по-прежнему `df63a457c3adf648d360f3d559d5d40ef00a9427`. Полный suite прошёл последовательно на trigger с лимитом 90 с: обычная шкала 169/169 за 69,189 с, старт с 1 с 169/169 за 68,531 с, с 5 с 169/169 за 68,012 с, с 60 с 169/169 за 72,010 с. Без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## FIX2 · поиск CNF по всему префиксу spill

**READY_FOR_REVIEW · `go=NOT_GRANTED` · `proof_credit=NONE`.** Основание — delta-ревью R2 (g0 `1590a213d5`), GO_WITH_NITS, до dispatch исправить (a) и (b). Proof-лимиты, Std, roster, bindings, bundle, relay и CI-REQUEST не изменены. Control получил новый коммит поверх FIX1 без force. Review-trigger новый, с тем же sole parent.

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Std N12, без изменений | `b465318cc95001c651011c2e5579bba12669b467` | `9d4c78baf73fae2b15f29c2c81730399e1a2d9fa` | `bec3b6ee805fd3640da34e20482a3de647b3c865` |
| [Control FIX2](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11) | `588fc98143a3321d58d58407c916da621b70cccb` | `664f75885c8aafa7b4df8d82e9c8b7e0eb102593` | `b5e6c89c0e06cc55e264c4d297086e3ae629300a` |
| [Review-trigger FIX2, detached](/root/kani-rev2-gen-stable-wide-witness-n12-n16-trigger-w11/control) | `f0f51bd6de4ce617eeef205b897c4489f9b58201` | `664f75885c8aafa7b4df8d82e9c8b7e0eb102593` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| CI-REQUEST.json, без изменений | `1247e9e65a6be3fe41862b3559f6996284024d1d3ee3e03bbaf9546ecd4ba3f9` |
| Exact roster, канонический JSON | `7f4ae44e4063234934ed4cbcb3cec182a8ebe15cbba0e4845262acdcc8bea9cb` |
| Source bindings, канонический JSON | `8df3d8ed069a47ecbb993a86a864cde54c111a45c7bce06ef8870f4ede597929` |
| Std bundle, 92 368 байт | `45dfe97fa55e311f7a9a8f99fa0c32042c64e51cc02850ca5af77f356ebe8711` |
| `cbmc_relay.py` | `c8b4c070dbd12a8acafa4b23df0b74833b600333f539b66fc9d27eccee3613b7` |

Независимый pin — `CH8_REV2_GEN_STABLE_WIDE_WITNESS_N12_N16_TRIGGER_TREE=664f75885c8aafa7b4df8d82e9c8b7e0eb102593`. Дельта Control затрагивает `stdout_relay.py`, `run.py`, `test_relay.py` и шаг `pins` в workflow.

1. **(a) CNF по всему префиксу.** Общий разбор сообщений с лимитами 16 384 сообщения и 1 MiB текста убран. Вместо него один целевой regex идёт по всем 16 MiB префикса. Он принимает только нативные сообщения размера и фазы: CNF, `Starting Bounded Model Checking`, `Runtime Symex/Convert SSA/Solver/decision procedure`, `size of program expression`, `Generated … VCC(s)`, `converting SSA`, `Running propositional reduction`, `Solving with …`, cover/reachability и `VERIFICATION:-`. Обычные сообщения вроде `Unwinding loop …` отбрасываются на первом байте, поэтому бюджет не расходуют. Найденные маркеры в исходном порядке идут в штатный `stream_metrics`, и контекст `INITIAL_SOLVE` сохраняется. Предел скана — 4 096 нативных сообщений. Причина отсутствия CNF теперь различается: `CNF_NOT_FOUND_BEFORE_MARKER_SCAN_LIMIT` при достигнутом пределе, `NO_RECOGNIZED_NATIVE_MARKER_IN_PREFIX` при отсутствии любых нативных маркеров, иначе `NO_CNF_IN_PREFIX`. В receipt пишутся `messages`, `native_messages`, `marker_scan_limit_reached` и `prefix_complete`. [Скан](/root/kani-rev2-gen-stable-wide-witness-n12-n16-control-w11/ch8-cal1/stdout_relay.py:212)
2. **Тест (a).** Spill на 17 MiB: версия CBMC, `Starting Bounded Model Checking`, 8 000 реалистичных строк `Unwinding loop … insert_tail …` (больше 2 MiB текста), затем symex, VCC, SSA, propositional reduction, CaDiCaL и CNF 4 956 964 / 25 517 502, дальше трасса. Под реальным окном `receipt_seconds − 1 с` `drain_spill` находит CNF с `INITIAL_SOLVE`, все восемь маркеров по порядку и 8 010 сообщений, причины нет. На реализации FIX1 тот же тест падает: CNF не найден. Отдельный тест проверяет все три причины. Время скана 16 MiB: 0,21 с для сплошных `Unwinding loop`, 0,07 с для 16 MiB нативных сообщений до предела, 0,10 с для трассы без сообщений. Прежний тест худшего случая через `measure_slot` и `RSS_LIMIT` проходит в новой форме: CNF найден, предел скана отмечен.
3. **(b) Таймаут self-test.** В шаге `pins` оба `timeout --kill-after=5s` подняты с 90 с до 150 с. Внешний timeout шага 8 мин и все proof-лимиты не менялись. При наблюдённых 69–78 с на прогон четыре прогона занимают около 5 мин и укладываются в шаг. Только если все прогоны одновременно подойдут к 150 с, раньше сработает timeout шага. Это всё ещё дешёвый отказ до измерений.
4. **(c) Сделано.** Если relay установлен, но доставка не оценивалась, receipt пишет `stdout_delivery=NOT_JUDGED`, а не `INSTALLED`. Вердикт по-прежнему требует `COMPLETE` от `collect`.

Валидация FIX2: 171 тест, из них 25 в `test_relay.py`. На точном detached trigger повторены `pins`, `sources`, `finish`, `upload-gate` и `upload-check`. Отклонены tree и payload trigger FIX1, подмена индекса и receipt, поздний upload. Std-checkout сохранил HEAD `dab03cf510` и отсутствие refs. `git diff --check` пройден. Blob `test_supervisor.py` равен `df63a457c3adf648d360f3d559d5d40ef00a9427`. Полный suite прошёл последовательно на trigger с лимитом 150 с: обычная шкала 171/171 за 69,023 с, старт с 1 с 171/171 за 71,458 с, с 5 с 171/171 за 77,714 с, с 60 с 171/171 за 75,158 с. Без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`.

## Дальше

Delta-ревью FIX2 тем же reviewer, затем отдельный GO координатора на установку tree variable `664f75885c…` и push review-trigger `f0f51bd6de`.
