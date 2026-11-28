# REV2 · пилот general Wide и stable u64 на N32

**READY_FOR_REVIEW (FIX1 по ревью R1) · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Подготовлена одна Ubuntu job из семи последовательных singleton на штатном pipe (`STOCK_PIPE`). Пакет измеряет крайние локальные опоры N32. Это actual правый S8 FULL для stable `u64`, правый fill rel15 для `u64` и `Wide` и четыре exact stock Check фактических `merge_up` и `merge_down` в геометрии `16+16`, отдельно для каждого типа. Сквозных контролей нет, relay не обслуживает ни одну стадию. Даже полный итог даёт только локальные опоры, а не строку допуска N32. Исполнитель стадии — Claude Code, pane 11. Нативная компиляция и результаты ожидают независимого ревью и отдельного GO координатора. [Задание](REV2-GEN-STABLE-N32-PILOT-TASK.md) · [План N32](REV2-GEN-STABLE-WIDE-N12-N14-ADMISSION.md#следующий-пакет) · [Прецедент exact Check](REV2-GEN-STABLE-WIDE-N12-N14-HANDOFF.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std N32](/root/verify-rust-std-rev2-gen-stable-n32-pilot-w11) | `88d05a138c4bca054de4ec1215ceb7f54087c3df` | `7dd117f5257b790fcd07f21826e6a8adecf75cc2` | `93d0c4a18d2f9e13c366a51c6f15e61c209a32d3` |
| [Control N32 FIX1](/root/kani-rev2-gen-stable-n32-pilot-control-w11) | `79a5ec2fb89f643559e44bdab0f534d6e827ec08` | `c1bbb6dbe41ce69c93a65b42fb45655d78da2aac` | `ec27bc206c745ac6babd6acd4862f7ac9282fea5` |
| [Review-trigger FIX1, detached](/root/kani-rev2-gen-stable-n32-pilot-trigger-w11/control) | `e9206385e8d02e62af407ce568db253683ce4215` | `c1bbb6dbe41ce69c93a65b42fb45655d78da2aac` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n32-pilot-control-w11/ch8-cal1/CI-REQUEST.json) | `eddd1856a5b7cb27913f4624637ce699d0825dd799a562861c82810c3d968c0c` |
| Exact roster из семи строк, канонический JSON | `5845e394a29f51aa9145a0510826d4a277b826e893825ba7f591713725821310` |
| Source bindings, канонический JSON | `623ae996fdc6b1610ee28cdc341e5df86865649c6aeb13e3d8a4d79a1dbda16f` |
| [Std bundle](/root/kani-rev2-gen-stable-n32-pilot-control-w11/ch8-cal1/std-overlay.bundle), 98 035 байт | `c806269c65c141d1eec04e9c78bed16c8f1ff734b3c02223b45f1e26d937ce21` |
| `ch8-cal1/cbmc_relay.py`, байты не менялись | `c8b4c070dbd12a8acafa4b23df0b74833b600333f539b66fc9d27eccee3613b7` |

Tree variable — `CH8_REV2_GEN_STABLE_N32_PILOT_TRIGGER_TREE=c1bbb6dbe41ce69c93a65b42fb45655d78da2aac`. Control FIX1 — fast-forward поверх R1-коммита `ec27bc206c`, R1 tree `9fda6b9c8e…` и R1 trigger `df269de443` заменены; pins отклоняет прежний tree. Четыре хэша входов и байты relay не изменились. Сохранены fork `Tiramisu-Cake/kani`, push и ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и payload guards. Bundle объявляет один `HEAD` и связывает 37 последовательных overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`. Upload-gate сверяет индекс `smallsort-rev2-gen-stable-n32-pilot-artifact-v1` с четырьмя хэшами, хэшем relay и инвентарём. Worktree прошлых пакетов не изменялись.

## FIX1 по ревью R1

[Ревью R1](REV2-GEN-STABLE-N32-PILOT-REVIEW.md) (`af8b8d2c59`) — GO_WITH_NITS, GO отложен до правок. Control `79a5ec2fb8` меняет три файла: `test_relay.py`, `request.py`, `ch8-q-pilot.yml`. Std, CI-REQUEST, bundle, roster, bindings, `cbmc_relay.py` и лимиты на корень прежние.

- **Nit 3, первый прогон suite.** Причина — свободное место на диске хоста, а не первый прогон как таковой. Relay перед каждой установкой (`stdout_relay.install`) и каждым spill (`cbmc_relay.relay`) требует реального свободного места `spill_cap_bytes + disk_reserve_bytes`. Тестовая фикстура `RelayFixture` задавала cap 64 MiB, то есть 65 MiB на каждую проверку, при потоке до 21,2 MiB в тесте large JSON. Корень сервера заполнен на 100 %, свободно 40–170 MiB, и объём колеблется из-за соседних процессов. Свежий clone занимает место, и первый прогон попадает под порог. Поэтому следующие прогоны того же clone проходили. На свежем clone R1 trigger воспроизведено `FAILED (errors=2)` с `stdout_relay.RelayError: spill disk has 59428864 bytes, 68157440 required`. Детерминированно воспроизведено на ext4-образе 100 MiB под `TMPDIR`. При 62,7 MiB свободно R1 trigger даёт `FAILED (failures=1, errors=25)`: те же `RelayError` в relay-тестах и один FAIL `test_rss_stop_keeps_census_and_full_spill_prefix_inside_the_real_receipt_window`. При 87 MiB — 181/181. Это тот же тип сбоя, что у ревьюера (`failures=1, errors=12`). Исправление: cap фикстуры 24 MiB, чуть больше крупнейшего синтетического потока, требование одной проверки 25 MiB. На том же образе FIX1 проходит 181/181 при 62,7 и 50 MiB свободно. При 44 MiB `errors=5` — это собственный объём файлов suite, пиковое потребление около 43 MiB. Боевой `STDOUT_RELAY` (4 GiB cap, 2 GiB резерв) не изменён. Relay в N32 выключен. На раннере Ubuntu свободного места обычно гигабайты, так что в CI этот порог маловероятен, но FIX1 снимает зависимость с запасом. Других зависимостей suite от состояния хоста при первом прогоне не найдено.
- **Nit 2.** Timeout шага pins `ch8-q-pilot.yml:46` — 10 мин вместо 8. Prepare по-прежнему ограничен дедлайном 54:00 от epoch, план часов не меняется.
- **Nit 1.** Цикл `for p in range(16): for j in range(16)` удалён из `check_n32_pilot_source`. Вместо него — комментарий: границы индексов поста rel15 — инвариант рендера, закреплённого побайтным совпадением, а не проверка источника. Самопроверка рендера `fill.count(...)` осталась.
- **Nit 4.** Исправлены три формулировки: фикстура, импорты `wide_n12_n14`, координата `:35:5`.

Проверка FIX1. Три свежих depth-2 clone trigger `e920638`, первый прогон как в CI (`PYTHONDONTWRITEBYTECODE=1`, лимит 150 с, `TMPDIR` на корне при 40–43 MiB свободно): 181/181 за 86,6 / 86,4 / 86,6 с. Ещё один свежий clone прошёл полный шаг pins на четырёх шкалах подряд: обычная 93,1 с, старт с 1 с 89,2 с, с 5 с 90,1 с, с 60 с 84,4 с, всего 361 с из 10 мин. На точном trigger прошли `pins`, `sources`, `finish` с семью `NOT_STARTED` и `OPEN`, `upload-gate` и `upload-check`. Pins отклонил R1 tree `9fda6b9c8e`, tree N12/N14 `e10399474a` и чужой payload `90fa5b778b`.

## Std: модуль `n32_pilot`

Модуль дописан в конец `rev2_gen_stable_n16_pilot.rs` под `#[cfg(kani_smallsort_rev2_gen_stable_n32_pilot)]` на `:1943` и закрывает файл. Check-cfg добавлен на `core/Cargo.toml:82`. Дельта Std от `93d0c4a18d` — эти два места. Файл N12/N14 — побайтный префикс нового, `wide_n12_n14` и все прежние root не изменены. Runtime, контракты и blob `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` не изменены. Blob модуля `16c8b85861018a6ce3cb75c57e706ca47ce6cf42`, `core/Cargo.toml` `1bf4829481ac60b15a5f551006a301bd01240a04`. Модуль импортирует только `super::*`. У `wide_n12_n14` есть ещё `use super::super::super::UnstableSmallSortTypeImpl` (`:1499`), N32 он не нужен. Из `super::*` приходят `Wide`, `any_wide`, `same_wide`, `wide_less`, `u64_less`, `sort8_stable`, `insert_tail`, `merge_up`, `merge_down`, `MaybeUninit`, `ptr`, `ub_checks` и `kani`. Трейты не нужны, вызовы идут напрямую в приватные функции родительского `smallsort`. [Модуль](/root/verify-rust-std-rev2-gen-stable-n32-pilot-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs:1943)

Все selectors и Check targets начинаются с `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::n32_pilot::`. Roster заморожен в порядке задания.

| Слот / selector | Роль, target (`cfg_attr`) | Ключевые координаты | Typed copy и copy sites |
| --- | --- | --- | --- |
| `GEN-N32-U64-S8-R48-FULL` / `gen_n32_u64_s8_r48_full` | plain Proof, target пуст | вызов `:2031`, посты `:2074–2079`, covers `:2080–2082` и `rev2_u64_n13.rs:9:5` | `<u64>`, `smallsort.rs:832–835`, `:885`, `:918` |
| `GEN-N32-U64-FILL-R48-REL15` / `gen_n32_u64_fill_r48_rel15` | plain Proof, target пуст | assume `:2108`, копия `:2122:13`, `insert_tail` `:2123`, посты `:2154–2156`, covers `:2157–2160` | `<u64>`, локальная `:2122:13` → `smallsort.rs:329:17`, `:722:13`, `:362:13` |
| `GEN-N32-WIDE-FILL-R48-REL15` / `gen_n32_wide_fill_r48_rel15` | plain Proof, target пуст | assume `:2186`, копия `:2200:13`, `insert_tail` `:2201`, посты `:2234–2236`, covers `:2237–2240` и `rev2_gen_stable_n16_pilot.rs:35:5` (`GEN_N16_WIDE_COMPARATOR_CALLED`) | `<…::Wide>`, локальная `:2200:13` → `:329:17`, `:722:13`, `:362:13` |
| `GEN-N32-U64-MERGE-UP` / `gen_n32_u64_merge_up` | Check `actual_merge_up_u64_n32`, `:2243:5` | `modifies(s.wrapping_add(k))` | `<u64>`, `smallsort.rs:885:9` |
| `GEN-N32-U64-MERGE-DOWN` / `gen_n32_u64_merge_down` | Check `actual_merge_down_u64_n32`, `:2329:5` | `modifies(s.wrapping_add(31 - k))` | `<u64>`, `:918:9` |
| `GEN-N32-WIDE-MERGE-UP` / `gen_n32_wide_merge_up` | Check `actual_merge_up_wide_n32`, `:2415:5` | `modifies(s.wrapping_add(k))` | `<…::Wide>`, `:885:9` |
| `GEN-N32-WIDE-MERGE-DOWN` / `gen_n32_wide_merge_down` | Check `actual_merge_down_wide_n32`, `:2504:5` | `modifies(s.wrapping_add(31 - k))` | `<…::Wide>`, `:918:9` |

Общая геометрия: `S = v[1..33].as_mut_ptr()` в живой инициализированной V34, `D` — база отдельной живой D48. Канарейки `v[0]`, `v[33]` произвольны. Все проверки V34 идут двумя проходами `0..17` и `17..34`, D48 — проходами внутри `0..32` и `32..48`. Самый длинный цикл в тексте модуля — 32 итерации, unwind 36. Произвольный `[u64; 34]` строит `kani::any()` библиотеки Kani, как `[u64; 18]` в прецедентах. `memcmp`, сравнений срезов и равенства массивов нет.

- **Правый S8 FULL.** Actual `sort8_stable(s.add(16), d.add(16), d.add(40), &mut less)`, как на `smallsort.rs:300–305` при `len=32`. Это `v_base.add(len_div_2)`, `scratch_base.add(len_div_2)`, `scratch_base.add(len + 8)`. Чтение — ровно `S[16..24] = v[17..25]` (наблюдатели `before[17 + i]`, `i<8`). Выход `D[16..24]` — [128, 192) байт, tmp `D[40..48]` — [320, 384) байт. Оба блока изначально uninit и раздельны. `D[0..16]` и `D[24..40]` произвольны и инициализированы для frame. На `:850–851` два actual S4 заполняют `D[40..44]` и `D[44..48]` до чтения на `:857`. Посты: порядок восьми результатов, кратность независимого произвольного полного `u64` probe, порядок обеих tmp-четвёрок, весь V34, D вне двух write-областей. Covers 4/4: `MIXED_INVERSION`, `EQUAL_INPUT`, `RETURNED` после постов, компаратор `REV2_U64_N13_COMPARATOR_CALLED`.
- **Fill rel15, `u64` и `Wide`.** Инициализированы `D[0..31]` и `D[32..48]`, `D[31]` остаётся uninit. `x = before[32] = S[31]` — произвольная полная запись. Снимок `old` — ровно 15 записей `scratch[16 + i]`, `i<15`, `D[31]` не читается. Единственный `kani::assume` — неубывание ключей `old` (`for i in 1..15`). Затем локальная копия `ptr::copy_nonoverlapping(s.add(31), d.add(31), 1)` транскрибирует `smallsort.rs:329:17` при `offset=16`, `i=15`. Потом actual `insert_tail(d.add(16), d.add(31), &mut less)` по `:330`. `pos = #{old.key ≤ x.key} ∈ 0..=15`. Для каждого `j<16` пост сверяет `old[j]` при `j<pos`, `x` при `j==pos`, `old[j−1]` при `j>pos`. У `u64` сравнивается полное слово, у `Wide` все три поля (`same_wide`). Это exact upper bound, включая вставку после равных. Границы индексов — инвариант текста поста, а не отдельный gate: `j<pos ≤ 15 ⇒ j<15`, `j>pos ≥ 0 ⇒ 1 ≤ j` и `j−1 ≤ 14`. Текст закреплён побайтным рендером, выход за массив снимка поймали бы bounds checks Kani. Худший шаг `insert_tail` сдвигает 15 записей. Frame — весь V34 и D вне `D[16..32]`, то есть `0..16` и `32..48`. Covers 5/5: компаратор, `NO_SHIFT` (`pos == 15`), `SHIFT` (`pos < 15`), `EQUAL_KEY` у `u64` или `EQUAL_DISTINCT` у `Wide` (равный ключ, другая метка), `RETURNED`. Предпосылку rel15 в полной композиции даст rel14, здесь он не измеряется.

### Четыре exact Check merge

Форма повторяет раздельные Wide Check N12/N14 с `m=16`. Отличия только в типе (`u64`/`u64_less` или `Wide`/`wide_less`) и в двухпроходных V34-frame. `ProofForContract` на scoped обёртке, Replace нет.

| Направление | Кандидаты → цель | Выбор | Следующий курсор |
| --- | --- | --- | --- |
| Up, actual `smallsort.rs:885:9` | `D[a]`, `D[16+b]` → `S[k]` | левый при `left ≤ right` по ключу | `S[k+1]` |
| Down, actual `smallsort.rs:918:9` | `D[15−c]`, `D[31−d_count]` → `S[31−k]` | левый при `left > right`, правый при равенстве | `S[30−k]` |

- **Контракт.** `k<16`, `a<=k` или `c<=k`, `b=k−a`, `d_count=k−c`. Также `can_dereference(slice_from_raw_parts(d, 32))`, `can_write(slice_from_raw_parts_mut(s, 32))` и `!same_allocation(d, s)`. Выравнивание по типу входит в оба предиката, как в прецеденте. Scoped `modifies` — одна запись `s.wrapping_add(k)` или `s.wrapping_add(31 - k)`.
- **Обёртка.** `_READ`, `_WRITE`, `_DISJOINT` проверяют нативные чтение, запись и раздельность. `_CURSORS` сверяет обе исходные позиции после выбора и следующий курсор записи. Down обновляет исходные курсоры через `wrapping_sub`. Указатель перед `D` при исчерпании левой половины только сравнивается. Up на последнем шаге может вернуть one-past своей половины. У `u64` выбор на tie различается только курсором.
- **Корень.** Символические `u8` для `k` и счётчика, единственный `kani::assume` равен `requires`. Все записи V34 и D48 произвольны, условий sorted или tie нет. `D[32..48]` заполнен только для frame. `_VALUE` сверяет полное слово или все поля Wide в `v[1+k]` или `v[32−k]`. `_V_FRAME` — V34 кроме этой позиции. `_SCRATCH_FRAME` — весь D48.
- **Covers 7/7.** `TAKES_LEFT`, `TAKES_RIGHT`, `TIE` (у `u64` равные слова, у Wide равные ключи и разные метки), `K_ZERO`, `K_LAST` (`k == 15`), `RETURNED`, компаратор (`rev2_u64_n13.rs:9:5` у `u64` или `rev2_gen_stable_n16_pilot.rs:35:5` у Wide).
- **Приёмка.** Exact stock target `ProofForContract` на строке `cfg_attr`, колонка 5. Нужны `single_top_level_call`, `no_recursive_call`, scoped `memcpy.assigns.1/.2` и шесть grouped typed-copy свойств своего типа на `ptr/mod.rs:587:14`. Actual copy site — одна строка своего направления, тело обёртки вызывает ровно один `merge_*` и не копирует само. В regular и stock сверяются требуемые свойства и covers, все выведенные unwind требуют `SUCCESS`. Ожидается `VERIFIED/MATCHED`, exit 0.

### Источник: гейт по геометрии

`request.check_n32_pilot_source` рендерит весь модуль от объявления до конца файла из типа и роли каждого слота (`n32_module_text`) и требует побайтного совпадения. Так закреплены все литеральные смещения S8 (`s.add(16)`, `d.add(16)`, `d.add(40)`), окна `17..25`, tmp-блоки `40..44`/`44..48`, длина снимка 15, циклы `0..15`, `1..15`, `0..16`, копия `S+31 → D+31`, база `insert_tail` `D+16` и uninit `D[31]`. Также закреплены смещения merge `16`, `15`, `31`, `30`, границы `k<16`, длины срезов 32, scoped `modifies`, tie-правила, `wrapping_sub` и единственный `assume` каждого корня. Любой хвост после модуля отклоняется. Рендер прошёл rustfmt без изменений, и фикстура `n32_pilot_module.fixture` равна срезу blob `16c8b858…` от `:1943` (строка cfg модуля) до конца файла. Гейт copy sites отдельно сверяет две локальные копии и их `insert_tail`, S4 и merge длины 8 у S8 и единственный направленный site каждого Check.

## Профиль, argv и часы

Одна Ubuntu 24.04 X64 job до 110 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`, CBMC 6.11.0/CaDiCaL 3.0.0, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, прежние `-Z`, regular и stock export. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit и validity выключены. На корень 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Все семь строк используют 34 флага cfg, cfg-off опускает последний.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Тест сверяет argv всех семи строк с argv Check `GEN-N12-WIDE-MERGE-UP` пакета `46121678583/1` с точностью до selector и каталога слота. `RUSTFLAGS` сверяется с вектором из 33 флагов плюс `kani_smallsort_rev2_gen_stable_n32_pilot`. PATH всех стадий штатный. Ранний cfg-on compile preflight идёт до обоих discovery list, первые rustc diagnostics сохраняются. Ориентир — Wide N12/N14: 60,5–68,1 с VT и до 2 665 820 KiB на Check. У N32 больше адресные диапазоны (V34 вместо V14/V16) и есть fill rel15. Ресурсы всех семи корней предстоит измерить.

| Стадия | Дедлайн от начала job | Лимит |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Identity gate и latest start `GEN-N32-U64-S8-R48-FULL` | 55:00 | До 60 с с начала measure |
| Latest start `GEN-N32-U64-FILL-R48-REL15` | 58:25 | Окна по 205 с |
| Latest start `GEN-N32-WIDE-FILL-R48-REL15` | 61:50 | |
| Latest start `GEN-N32-U64-MERGE-UP` | 65:15 | |
| Latest start `GEN-N32-U64-MERGE-DOWN` | 68:40 | |
| Latest start `GEN-N32-WIDE-MERGE-UP` | 72:05 | |
| Latest start `GEN-N32-WIDE-MERGE-DOWN` | 75:30 | |
| Конец окон | 78:55 | `slots_seconds=1435` |
| Финальная аттестация | 80:55 | Measure 27:00 внутренний, 29 мин внешний |
| Finish и upload-gate | 85:50 | 5 с запаса на запуск upload |
| Upload | 92:55 | Внешние 7 мин |
| План с резервом | 98:55 | Job 110 мин |

Сохранены caps публикации 4/96 MiB, checkpoint перед проекцией, дедлайн receipt, reap до следующего слота и финальная проверка индекса. Если слот не подтвердил reap, следующие не запускаются. При cutoff receipt сохраняет исход, census и по роли первую CNF, фазу, VT/cold, RSS группы и CBMC и PSS с оговоркой Linux TID. `slot_diagnoses` оценивает каждый слот. `type_diagnoses` даёт `STABLE_U64` по S8, u64 fill и двум u64 Check, `GENERAL_WIDE` — по Wide fill и двум Wide Check. Общий `GEN_STABLE_N32_PILOT_WITHIN_PROFILE` требует все 7 `VERIFIED/MATCHED`, полные timely receipts и attestation `COMPLETE`. Иначе итог `GEN_STABLE_N32_PILOT_OPEN`, а успешные слоты сохраняют свои измерения.

### Stdout delivery

Каждая строка roster несёт `stdout_delivery=STOCK_PIPE`. `load()` требует этого у всех семи строк и `STDOUT_RELAY.slot=None`. Сам блок relay, его режим `SPILL_THEN_REPLAY` и байты `cbmc_relay.py` заморожены без изменений для будущих контролей. `measure_slot` отказывает слоту `STOCK_PIPE`, если конфигурация relay назовёт его. В этом случае receipt `NOT_STARTED/STDOUT_DELIVERY_CONFLICT`, relay не устанавливается и child не запускается. Профиль слота требует `STOCK_PIPE` и в замороженном корне, и в receipt, а также отсутствия записи `stdout_relay`. Иначе слот `OPEN` с колонкой `NOT_STOCK_PIPE`. Prepare, discovery и version attestation не получают PATH-префикса, это проверяет тест setup. Автоматического повтора или переключения при `RSS_LIMIT` нет. Машинерия relay по-прежнему тестируется на историческом корне N14 с тестовой конфигурацией.

## Discovery

Cfg-off содержит 186 исторических записей, включая пять корней Wide N12/N14. Cfg-on добавляет три plain Proof с пустыми targets и четыре `ProofForContract` с exact targets `n32_pilot::actual_merge_{up,down}_{u64,wide}_n32`, всего 193. Активны только семь строк в порядке таблицы. Discovery отклоняет исторический корень на месте новой строки, plain на месте Check и Check на месте plain, перестановку, неполный или удвоенный roster, чужой target и contract target у standard harness. Отклоняется и потеря исторического корня, включая N14 witness и Check N12/N14. Исторический roster N12/N14 закреплён digest `2cb3104a…` и сверяется на своей ревизии `93d0c4a18d`. Прежние roster сохраняют свои digest.

## Валидация

- **Std.** Rustfmt `nightly-2026-11-19` (`style_edition=2024`, `use_small_heuristics=Max`) прошёл для нового и прежнего blob модуля. Прежний файл — побайтный префикс, TOML разобран, `git diff --check` пройден. Независимая Python-модель `insert_tail` по `smallsort.rs:701–735` на 20 000 случайных упорядоченных префиксах с повторами подтвердила exact post rel15 и неизменность `D` вне `[16, 32)`. Tie-правила `:883–888`, `:916–921` совпадают с выбором в Check.
- **Source gate на реальном Std.** `check_overlay_layout`, `check_source_bindings` и все `check_native_coordinates` прошли на рабочем Std и на точном trigger со свежим depth-2 Std. Сверены 37 commit/tree/parent, append-only слои до `wide_n12_n14` и `n32_pilot` и 1 471 литеральная координата, из них 152 новые. Совпали native coordinates всех исторических roster и семи новых строк, рендер модуля и copy sites.
- **Синтетика, источник.** Гейт геометрии отклонил 45 мутаций модуля и два изменения помощников. Среди них tmp `D+32` вместо `D+40`, сдвиг источника S8, окно чтения `16..24`, tmp-блок, frame D, размер scratch, диапазон `v[0..32]`, ослабленный probe. У rel15 отклонены лишняя итерация и чтение `D[31]`, снимок из 16 записей, смещённый снимок, ослабленный sorted guard, `<` вместо `≤`, неверная копия и база `insert_tail`, инициализированный `D[31]`, чужой `x`, cover `pos == 14`, добавочный `assume` и неполное сравнение Wide. В merge отклонены смещения `16/15/31/30`, `k<17`, длина среза 31, tie-правила, курсоры, `sub` вместо `wrapping_sub`, `merge_down` в Up, чужой target, снятый `same_allocation` и добавленный sorted guard. Хвост после модуля и потерянное объявление тоже отклоняются. Гейт координат отклоняет подмену modifies, строки и колонки `cfg_attr`, target, copy sites всех трёх plain, строки поста, функции и лишний labelled call.
- **Синтетика, проекция.** `results` отклоняет подмену target, definition, selector, Check, колонки, copy type другого типа, scoped assigns, typed-copy свойства, copy sites, неполные wrapper assertions и неуспешный unwind. У plain отклоняются чужой selector, роль Check, ожидаемый `FAILED`, потерянные посты, `RETURNED`, typed-copy свойство и unwind. Перекрёстная подмена между `u64` и Wide отклоняется.
- **Профиль.** Relay на любом из семи слотов, receipt не `STOCK_PIPE` или корень не `STOCK_PIPE` снимают слот. Потеря `STOCK_PIPE` в корне меняет digest roster и открывает все слоты. Просроченный или отложенный receipt, превышение VT, cold или RSS, неверный exit, неполная проекция и неподтверждённый reap оставляют слот `OPEN`. Изоляция типов проверена: Wide-мутации оставляют `STABLE_U64` в профиле, u64-мутации — `GENERAL_WIDE`.
- **Trigger.** На точном detached trigger R1 прошли `pins`, `sources`, `finish` с семью `NOT_STARTED` и диагнозом `OPEN`, `upload-gate` и `upload-check`. Отклонены tree N12/N14 `e10399474a`, чужой payload N12/N14 trigger `90fa5b778b`, подмена индекса и receipt, поздние upload-gate и upload-check. Std-checkout сохранил HEAD `dab03cf510`, shallow boundary и отсутствие refs. YAML разобран с проверкой уникальных ключей: job 110 мин, measure 29 мин. Восемь блоков прошли `bash -n`, `git diff --check` пройден.
- **Suite.** 181 тест, последовательно на точном trigger с лимитом 150 с. Обычная шкала 181/181 за 83,642 с, старт с 1 с 181/181 за 88,149 с, с 5 с 181/181 за 81,873 с, с 60 с 181/181 за 77,768 с. Четыре прогона занимают около 5,5 мин. Timeout шага с FIX1 — 10 мин, на свежем clone FIX1 шаг занял 361 с, см. FIX1.
- Локальная стадия обошлась без Cargo, rustc, Kani, CBMC, CI, push в Kani и изменений Actions variables. Коммиты Std, Control и trigger имеют `[skip ci]` и author/committer `Tiramisu-Cake <igkharin@gmail.com>`, в сообщениях нет решётки перед цифрой.

## Измерено и что остаётся

| Измеряет пакет (локальные опоры) | Остаётся для строк N32 |
| --- | --- |
| Правый stable S8 FULL `S+16 → D+16`, tmp `D+40` | Левый S8 или доказанный перенос в `D[0..8]` с tmp `D[32..40]` |
| Fill rel15 правой половины для `u64` и Wide | Wide S4 в геометрии V34/D48, все промежуточные fill (stable rel8–14, Wide rel4–14), применимость rel15 по посту rel14 |
| Exact Up/Down `16+16` для `u64` и Wide на произвольных записях и всех допустимых счётчиках | Ранговая композиция 16 пар и собственный различающий нативный контроль каждого фактического входа |

Для stable `u64` заявляем порядок и кратности полных слов. У Wide различимые равные записи требуют отдельного поста устойчивости. N31 с геометрией `15+16` и нечётным центром остаётся следующей стадией.

## Ограничения

- Компиляция модуля локально не проверялась. Ранний cfg-on preflight остановит пакет до discovery, если rustc отклонит модуль. Форма Check повторяет скомпилированные `wide_n12_n14`, форма S8 и fill — `pilot` и `close`. Новые элементы — `[0u64; 15]`, `[Wide { .. }; 15]`, двухпроходные циклы и `u64_scratch48`.
- Ресурсы N32 не измерялись. Опора на Wide N12/N14 даёт только ориентир, при `RSS_LIMIT` или `TIMEOUT` слот остаётся `OPEN` со своими измерениями.
- Все семь корней — локальные опоры. Ни полный итог, ни отдельный слот не дают строку допуска N32 без рёбер из таблицы выше.

## Дальше

Независимое ревью пакета, затем отдельный GO координатора на установку tree variable `c1bbb6dbe4…` и новый trigger с этим tree и sole parent `467af9cb8d`.
