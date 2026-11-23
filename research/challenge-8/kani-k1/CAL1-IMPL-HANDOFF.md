# CAL1 · пакет диагностики pr752, FIX3

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. После `SAMPLER_ERROR` в прогоне 45268412731 FIX3 пропускает исчезнувшую запись PID целиком и считает такие пропуски отдельно при измерении и cleanup. Control `5dd6140e7aa9225d4c1014b957bb2c65bba6c7aa`, tree `4cf6be61fff1988b22bf7f504e553361352f55d9`, единственный parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Discovery и результаты harnesses на FIX3 имеют статус `UNKNOWN`. [Задание FIX3](CAL1-FIX3-TASK.md) · [Аудит и проверки FIX3](CAL1-FIX3-HANDOFF.md)

Linux-стресс завершился за 182,43 с с 643 потомками, `EXITED`, exit 0, 608 валидными сэмплами и нулём пропущенных сэмплов. Зафиксированы 143 пропуска PID-записей при измерении и один при cleanup. Пик RSS 85 876 KiB при cap 163 840 KiB. Отдельный `RSS_LIMIT` сработал при 66 656 KiB и cap 24 576 KiB. В обоих сценариях `reaped=true` и `remaining_processes=[]`. Прошли 58 Python-тестов. Darwin проверен синтетически. [Результаты прогонов](CAL1-FIX3-HANDOFF.md#локальные-проверки)

## Пакет FIX2

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. В прогоне 45262099662 ранняя компиляция overlay прошла за 34,88 с. Cfg-on discovery завершился через 987,86 с с `LIVE_MEMORY_PRESSURE` в `goto-cc` при `full avg10=0.18`, `MemAvailable=15 308 756 KiB` и пике RSS 5,56 GiB. GO четвёртого раунда относился к этому диагностическому запуску. [Задание FIX2](CAL1-FIX2-TASK.md) · [Ревью раунда 4](CAL1-REVIEW.md#четвёртый-раунд--2026-11-23) · [Setup receipt](/root/ch8-artifacts/run-45262099662/ch8-cal1-Linux-X64-45262099662-1/setup.json) · [Error receipt](/root/ch8-artifacts/run-45262099662/ch8-cal1-Linux-X64-45262099662-1/error.json)

| Control FIX2 | SHA |
| --- | --- |
| Commit | `c93b068fcc2bc7e1e9b723d6d4ad72743e520ddc` |
| Tree | `b455c846b09cc0a669e3a2fa853438745a233a37` |
| Единственный parent | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Диапазон diff | `bba444231c320a41a9add48bb7caad56b268dbee..c93b068fcc2bc7e1e9b723d6d4ad72743e520ddc` |

В diff входят два файла. На Linux допуск процесса и batch классифицируют снимок по `full avg10 >= 5.0%`. При работе `LIVE_MEMORY_PRESSURE` требует не менее трёх последовательных высоких сэмплов за интервал не менее 2,0 с по монотонным часам. Низкий сэмпл сбрасывает серию. Receipt сохраняет `pressure_avg10`, а при подтверждённом стопе также `pressure_high_samples` и `pressure_high_seconds`. Предел RSS, резерв памяти и ошибки PSI-пробы срабатывают сразу. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Синтетические тесты](/root/kani-cal1-control-w11/ch8-cal1/test_supervisor.py)

Прошли 48 локальных Python-тестов (`python3 -m unittest discover -v`), включая синтетические сценарии Linux и macOS, и `git diff --check`. Сверены overlay `080a0104159fd04b6764a24f8538a97588f6612e`, SHA-256 frozen request и bundle. FIX2 подготовлен локально. Discovery и результаты harnesses для FIX2 остаются `UNKNOWN`.

## Пакет раунда 4

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Раунд 4 устраняет блокер из ревью `5cc886b894`. В `cal1.rs` четыре функции SmallSort импортируются через `super::super`. Пакет сохраняет feature gate `fn_traits`, раннюю пробу cfg-on `core` перед полным discovery и сохранение первых ошибок обоих потоков. [Ревью третьего раунда](CAL1-REVIEW.md#третий-раунд--2026-11-23) · [Задание](CAL1-FIX-TASK.md) · [Handoff предыдущего исправления](CAL1-FIX-HANDOFF.md) · [Frozen request](/root/kani-cal1-control-w11/ch8-cal1/CI-REQUEST.json)

## Идентичность и trigger раунда 4

| Объект | Commit | Tree | Parent |
| --- | --- | --- | --- |
| std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| std overlay раунда 4 | `080a0104159fd04b6764a24f8538a97588f6612e` | `96f95b8082983b57f203b0e3e12151552dba0f76` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| std overlay прогона 45249887979 | `6e5b28070d72adefae7c259c6f33ffcebcd9a314` | `d4ab1d4f0749019d9f5568bfc4c62e54066de4a2` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Kani stock | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |
| Control CAL1 раунда 4 | `bba444231c320a41a9add48bb7caad56b268dbee` | `e1b1a7e80ceb1d69c96540abbdf7806b36c6b8a6` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Control CAL1 прогона 45249887979 | `496851502d6fa6c773472ddc1981b62c9d948f3a` | `f85bab20a00b5651050733c1e2d5aedff24d140e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| g0 задания на исправление | `d8667dc7c3a8471cf612d2edd1ef5cc3ef8262d3` | `69fb1a850bd3642f0a85709d16e43df77167566f` | `8bfe740b784742d0a920c6aff47f7406481c1270` |

- Оба checkout detached. Workflow проверяет SHA-256 bundle, импортирует объекты overlay без ref и сверяет commit/tree и единственного parent. После пробы и полного cfg-on discovery выполняется cfg-off inventory. Перед замерами runner восстанавливает точный detached overlay. [Std](/root/verify-rust-std-cal1-w11) · [Control](/root/kani-cal1-control-w11) · [Bundle](/root/kani-cal1-control-w11/ch8-cal1/std-overlay.bundle)
- Целевой fork `Tiramisu-Cake/kani`, событие `push`, единственный ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. В прогоне 45262099662 trigger `d3461349bdc357f030efdbcfceda272088485ff3` использовал tree `e1b1a7e80ceb1d69c96540abbdf7806b36c6b8a6` и единственного родителя `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Workflow на обоих jobs проверяет fork, event и полный ref. Runner сверяет push SHA и единственного родителя. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml) · [Source receipt](/root/ch8-artifacts/run-45262099662/ch8-cal1-Linux-X64-45262099662-1/source.json)
- Receipt прогона 45249887979 зафиксировал предыдущий trigger `4b7e292777412a5a239d7afbf283ad08bac8e75a` с тем же родителем. [Source receipt](/root/ch8-artifacts/run-45249887979/ch8-cal1-Linux-X64-45249887979-1/source.json)

| SHA-256 | Пакет раунда 4 | Пакет прогона 45249887979 |
| --- | --- | --- |
| Frozen request | `bd375fc094fc0c63f913efcc05278ea45fa0851b4285f367a5403ce77e078647` | `de9d0586b681c86cfb85aff85eec8c5450e3d3caaad2a3101f2af60bdb9a4cfc` |
| Std bundle | `27cb6c5fc420ba32f1b9266d3c7d66451e176a63a0ba2ba70a74405c39472d61` | `4de024a3b2f844c186be8271c24ef757d402d94098c3e1b07b12a7e22dc610e8` |

## Статическая сверка путей раунда 4

В таблицах `smallsort` обозначает `crate::slice::sort::shared::smallsort`, `verify` — `smallsort::verify`, а `merge_wide` — `verify::cal1_q_merge_model::merge_wide`. Под `cfg(kani)` файл `smallsort.rs` объявляет `verify`. Под `cfg(kani_smallsort_cal1)` файл `verify.rs` объявляет четыре соседних модуля `cal1`, `cal1_direct`, `cal1_model` и `cal1_q_merge_model`. В первых двух модулях `super` ведёт в `verify`, а `super::super` — в `smallsort`. Частные функции `smallsort` видимы его потомкам. У `cal1_q_merge_model` объявление `pub(super)` открывает его для `smallsort`, а `pub(in crate::slice::sort::shared::smallsort)` внутри модели ограничивает видимость этой веткой. [Объявление `smallsort`](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/mod.rs:6) · [Объявление `verify`](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort.rs:1055) · [Объявления CAL1](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify.rs:79)

### Импорты

| Файл и строка | Путь `use` | Разрешение |
| --- | --- | --- |
| `cal1.rs:4` | `super::cal1_model::KeyLess` | `verify::cal1_model::KeyLess`. Методы `with_q` и `q` имеют `pub(super)` и доступны в ветке `verify`. |
| `cal1.rs:5` | `super::cal1_q_merge_model as merge_model` | `verify::cal1_q_merge_model` под локальным именем `merge_model`. |
| `cal1.rs:6` | `super::super::bidirectional_merge` | `smallsort::bidirectional_merge` (`smallsort.rs:945`). |
| `cal1.rs:6` | `super::super::small_sort_network` | `smallsort::small_sort_network` (`smallsort.rs:367`). |
| `cal1.rs:6` | `super::super::sort9_optimal` | `smallsort::sort9_optimal` (`smallsort.rs:518`). |
| `cal1.rs:6` | `super::super::sort13_optimal` | `smallsort::sort13_optimal` (`smallsort.rs:577`). |
| `cal1.rs:7` | `crate::kani` | `core::kani` из `kani_core::kani_lib!(core)` в `core/src/lib.rs:367`. |
| `cal1.rs:7` | `crate::mem::MaybeUninit` | Реэкспорт `crate::mem::maybe_uninit::MaybeUninit` из `core/src/mem/mod.rs:55`. |
| `cal1_direct.rs:4` | `super::super::small_sort_general` | `smallsort::small_sort_general` (`smallsort.rs:261`). |
| `cal1_direct.rs:4` | `super::super::small_sort_network` | `smallsort::small_sort_network` (`smallsort.rs:367`). |
| `cal1_direct.rs:5` | `crate::kani` | Тот же `core::kani` из `kani_lib!(core)`. |
| `cal1_direct.rs:6` | `crate::mem::size_of` | Функция `size_of` из `core/src/mem/mod.rs:379`. |
| `cal1_direct.rs:7` | `crate::slice::sort::shared::FreezeMarker` | Trait `FreezeMarker` в `shared/mod.rs:11`. |
| `cal1_model.rs:3` | `crate::marker::PhantomData` | Тип `PhantomData` в `core/src/marker.rs:813`. |
| `cal1_q_merge_model.rs:3` | `super::cal1_model::KeyLess` | `verify::cal1_model::KeyLess`. |
| `cal1_q_merge_model.rs:38` | `super::ByteModel` | Частный trait `verify::cal1_q_merge_model::ByteModel`, видимый дочернему `merge_wide`. |
| `cal1_q_merge_model.rs:38` | `super::numeric_order` | `verify::cal1_q_merge_model::numeric_order`. |
| `cal1_q_merge_model.rs:39` | `crate::slice::sort::shared::smallsort::merge_contract_regions_disjoint` | Частная функция `smallsort::merge_contract_regions_disjoint` (`smallsort.rs:908`), видимая дочернему `merge_wide`. |
| `cal1_q_merge_model.rs:40` | `crate::ptr` | Модуль `core::ptr` (`core/src/lib.rs:284`). |
| `cal1_q_merge_model.rs:40` | `crate::ub_checks` | Модуль `core::ub_checks` (`core/src/lib.rs:286`). |

### Цели контрактных атрибутов

Все цели находятся в `cal1.rs`. На пине `9834c96ce9` Kani разбирает аргумент атрибута относительно родительского модуля harness. Резолвер `resolve_relative` проходит вложенные ветви группового `use` и берёт DefId из уже разрешённого Rust-импорта. Поэтому простые имена атрибутов ведут к тем же определениям `smallsort`, что и вызовы по этим именам. [Разбор атрибута на пине](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/kani_middle/attributes.rs#L832-L851) · [Резолвер на пине](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/kani_middle/resolve.rs#L573-L649)

| Строка `cal1.rs` | Путь в атрибуте | Harness | Разрешение |
| --- | --- | --- | --- |
| 22, раскрытие на 59 | `proof_for_contract(sort13_optimal)` | `nm_sort13_left_len13` | `smallsort::sort13_optimal` |
| 22, раскрытие на 60 | `proof_for_contract(sort13_optimal)` | `nm_sort13_left_len17` | `smallsort::sort13_optimal` |
| 22, раскрытие на 61 | `proof_for_contract(sort13_optimal)` | `mw_sort13_right_b17_len16` | `smallsort::sort13_optimal` |
| 65 | `proof_for_contract(sort9_optimal)` | `cal1_provider_sort9_n12` | `smallsort::sort9_optimal` |
| 78 | `proof_for_contract(bidirectional_merge)` | `cal1_provider_merge_n25` | `smallsort::bidirectional_merge` |
| 94 | `proof_for_contract(bidirectional_merge)` | `mw_merge_n32` | `smallsort::bidirectional_merge` |
| 123 | `stub_verified(sort9_optimal)` | `compact_network_n25_actual_insert` | `smallsort::sort9_optimal` |
| 124 | `stub_verified(sort13_optimal)` | `compact_network_n25_actual_insert` | `smallsort::sort13_optimal` |
| 125 | `stub_verified(bidirectional_merge)` | `compact_network_n25_actual_insert` | `smallsort::bidirectional_merge` |

В `cal1_direct.rs` все шесть harness используют `kani::proof` и `kani::unwind` без целевых функций. `cal1_model.rs` и `cal1_q_merge_model.rs` содержат только вспомогательную модель. [Q harnesses](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs) · [Direct harnesses](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_direct.rs)

### Остальные квалифицированные пути

| Место | Пути и разрешение |
| --- | --- |
| `cal1.rs`, `cal1_direct.rs`, `cal1_model.rs` | `kani::any`, `kani::assert`, `kani::assume`, `kani::cover` и `crate::kani::cover` ведут к API `core::kani`. `kani::proof`, `kani::unwind`, `kani::proof_for_contract` и `kani::stub_verified` ведут через `kani_core` к макросам `kani_macros`. |
| `cal1.rs:28,46,49,85` и повторы | `KeyLess::<u8>::with_q` ведёт к `verify::cal1_model::KeyLess<u8>::with_q`. `u8::MAX` — константа целочисленного примитива `u8`. `merge_model::numeric_order` ведёт к `verify::cal1_q_merge_model::numeric_order`. `MaybeUninit::<[u8; 32]>::uninit` ведёт к методу импортированного `MaybeUninit` в `core/src/mem/maybe_uninit.rs:433`. |
| `cal1.rs:86,103,131,159` | `merge_model::merge_wide::merge_halves_numeric_order`, `merge_model::merge_wide::merge_capture` и `merge_model::merge_wide::merge_q_post` ведут к одноимённым функциям `merge_wide` на строках 122, 178 и 193. |
| `cal1_direct.rs:111,116,132,140,212,226,291` | `crate::array::from_fn` ведёт к `core/src/array/mod.rs:109`. |
| `cal1_model.rs:5`, `cal1_q_merge_model.rs:29,33,37,43,57,72,81,111,122,132,178,193` | `pub(in crate::slice::sort::shared::smallsort)` указывает на общий модуль-предок `smallsort`. |
| `cal1_q_merge_model.rs:30,54,77,87,101,115,183,198` | `super::active` из `merge_wide` ведёт к обёртке внешней модели на строке 29. `<() as ByteModel<T, F>>::active` и `<() as ByteModel<T, F>>::threshold` ведут к методам локального trait `ByteModel` с общей реализацией на строке 9 и специализацией `u8, KeyLess<u8>` на строке 19. |
| `cal1_q_merge_model.rs:54,61,103,117,118,202` | `ub_checks::can_dereference` и `ub_checks::can_write` при `cfg(kani)` реэкспортируются из `crate::kani::mem` через `ub_checks::predicates`. |
| `cal1_q_merge_model.rs:69,108,118,201` | `crate::slice::from_raw_parts` — реэкспорт `crate::slice::raw::from_raw_parts`. `ptr::slice_from_raw_parts_mut` и `ptr::slice_from_raw_parts` объявлены в `core/src/ptr/mod.rs:1292` и `:1246` соответственно. |
| `cal1_q_merge_model.rs:154,162,172,186,188,209,210` | `u32::from` и `u8::from` используют реализации `From<bool>`, `usize::from` — `From<u8>` из `core/src/convert/num.rs`. `MergeTarget::Below` и `MergeTarget::Mask` — варианты локального `merge_wide::MergeTarget` на строках 141 и 140. |
| `smallsort.rs:510,512,513,569,571,572` | `verify::cal1_q_merge_model::merge_wide::presort_geometry`, `verify::cal1_q_merge_model::merge_wide::presort_post`, `verify::cal1_q_merge_model::merge_wide::presort_capture` ведут к `merge_wide:57,81,72` для префиксов 9 и 13. |
| `smallsort.rs:937,938,939,940` | `verify::cal1_q_merge_model::merge_wide::merge_geometry`, `verify::cal1_q_merge_model::merge_wide::merge_halves_numeric_order`, `verify::cal1_q_merge_model::merge_wide::merge_q_post`, `verify::cal1_q_merge_model::merge_wide::merge_capture` ведут к `merge_wide:111,122,193,178`. |

В добавленных блоках `smallsort.rs` атрибуты `crate::kani::requires`, `crate::kani::modifies` и `crate::kani::ensures` также реэкспортированы из `kani_macros`. Выражения `old(...)` обрабатывает макрос `ensures`. Под cfg-on и модули, и ссылающиеся на них атрибуты доступны вместе. [Контракт sort9](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort.rs:508) · [Контракт sort13](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort.rs:567) · [Контракт merge](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort.rs:935) · [Модель](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs)

## Overlay и frozen roster

Guard восстанавливает исходные `smallsort.rs`, `verify.rs` и `core/Cargo.toml` удалением добавленных опциональных атрибутов, деклараций четырёх модулей и записи `check-cfg`. В `core/src/lib.rs` он требует единственную строку `#![cfg_attr(all(kani, kani_smallsort_cal1), feature(fn_traits))]` и проверяет, что её удаление восстанавливает исходный blob побайтно. Все 11 строк roster используют `RUSTFLAGS=--cfg=kani_smallsort_cal1`. [Guard](/root/kani-cal1-control-w11/ch8-cal1/request.py) · [Feature gate](/root/verify-rust-std-cal1-w11/library/core/src/lib.rs)

Полный префикс каждого селектора — `slice::sort::shared::smallsort::verify::`. Исходные cover labels зафиксированы в roster.

| ID | Суффикс селектора | Роль | Unwind | Слот, с |
| --- | --- | --- | ---: | ---: |
| NET-U8-N08 | `cal1_direct::cal1_net_u8_n08` | Original, вставки | 40 | 300 |
| NET-U8-N09 | `cal1_direct::cal1_net_u8_n09` | Original, sort9 | 40 | 300 |
| S13-N13 | `cal1::nm_sort13_left_len13` | Check `sort13_optimal` | 36 | 1080 |
| S13-N17 | `cal1::nm_sort13_left_len17` | Check `sort13_optimal` | 36 | 1080 |
| S13-N32-R | `cal1::mw_sort13_right_b17_len16` | Check `sort13_optimal` | 36 | 1080 |
| MERGE-N32 | `cal1::mw_merge_n32` | Check `bidirectional_merge` | 36 | 780 |
| NET-N25 | `cal1::compact_network_n25_actual_insert` | Replace `sort9_optimal`, `sort13_optimal`, `bidirectional_merge` | 36 | 480 |
| NET-U64-N13 | `cal1_direct::cal1_net_u64_n13` | Original, sort13 | 40 | 720 |
| NET-U64-N32 | `cal1_direct::cal1_net_u64_n32` | Original, sort13, вставки, merge, copy-back | 96 | 1080 |
| GEN-N16-SMALL | `cal1_direct::cal1_gen_u64_n16_small` | Original, general scratch48 и два sort8 | 96 | 720 |
| GEN-N16-WIDE | `cal1_direct::cal1_gen_wide_n16` | Original, general scratch48 и два sort4 | 96 | 720 |

- S13 переносит q-post и запись в первые 13 элементов для `V34/base1/len13`, `V34/base1/len17` и `V34/base17/len16` из `3fff6aa0db` и `e2bd3c6adc`. Check выполняет реальные swaps. N32 merge сохраняет две численно упорядоченные половины 16+16, отдельный writable scratch32, исходный frame и observer `54123e752d`. Observer считает входы `<q` в `u8` и сверяет предикат на каждой из 32 позиций.
- N25 переносит `bfa60b19cc`, включая ветку insertion на левой половине длины 12 и реальный copy-back. Для N25 сохранена исходная маска q, компактный observer применяется при длине 32. Зарегистрированы два дополнительных Check для sort9 и merge N25. Они участвуют в discovery и исключены из 11 измерительных слотов и сценария партиций. N25 измеряется условно на Replace до отдельных точных повторов провайдеров на этом пине.
- Direct roots проверяют сортировку и кратности полных значений плюс внешний frame. Wide — `repr(C)` с тремя `u64` и проверкой размера 24, ключ задаёт порядок, оба payload участвуют в равенстве. Covers наблюдают сравнения внутри реальных тел, равные ключи, восходящие и нисходящие пары и нормальный возврат фиксированного маршрута. [Q roots](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs) · [Observer](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs) · [Direct roots](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_direct.rs)

## Команды, бюджет и сравнение

```text
{tool}/scripts/kani list -Z function-contracts -Z mem-predicates -Z float-lib
  -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing {std}/library --std --format json

{tool}/scripts/kani verify-std -Z unstable-options -Z function-contracts
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
  -Z stubbing --no-assert-contracts --no-codegen --only-codegen --quiet
  --target-dir {preflight}/kani-target {std}/library

{tool}/scripts/kani verify-std -Z unstable-options -Z function-contracts
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
  -Z stubbing --no-assert-contracts --harness {selector} --exact --jobs=1
  --output-format=regular -Z export-json --export-json {slot}/export.json
  --verbose --target-dir {slot}/kani-target {std}/library --cbmc-args --object-bits 12
```

Проба `OVERLAY_COMPILE_PREFLIGHT` получает до 180 с внутри setup-дедлайна, отдельный target и `CARGO_TERM_VERBOSE=true` для записи команды компилятора. Успех требует exit 0, подтверждённого reap, наблюдения `kani-compiler` с `--crate-name core`, обоими cfg и `-Z no-codegen`, а также нуля наблюдавшихся verifier children. После пробы runner сверяет exact selector/kind по cfg-on списку, затем снимает cfg-off список и возвращает точный overlay. `common_ready` публикуется после обоих списков и сверки. [Порядок фаз и привязка к пину](CAL1-FIX-HANDOFF.md)

Проба, оба списка и каждый измерительный слот получают отдельный `CARGO_TARGET_DIR`. Runner очищает inherited `RUSTFLAGS` и `CARGO_ENCODED_RUSTFLAGS` перед установкой cfg. Stock checks, reachability, unwind и CaDiCaL остаются штатными. Uninit и validity выключены. Export сверяет exact selectors, Check/Replace, resolved unwind, solver, OB12 и включённые проверки.

Batch содержит ровно `NET-U8-N08` и `NET-U8-N09` в этом порядке. Допуск требует завершённых singleton-терминалов с полными receipts, сумму wall с запасом 30 с в 600 с, и сумму изолированных пиков ≤80% начального доступного batch cap данной платформы. При недопуске batch получает `NOT_RUN`, список корней сохраняется. На Ubuntu команда использует `KANI_JOBS=2` и `--jobs=2`. В одном macOS job команды идут последовательно с незаданным `KANI_JOBS` и `-j`, затем с `KANI_JOBS=1` и `--jobs=1`. Каждая команда использует повторённый `--harness` и общий `--exact`. Все batch-варианты используют `terse` и stock export. Pinned Kani требует `terse` при многопоточном `--jobs`. Совпадение составов и наличия результата фиксируется отдельно. [Сбор argv](/root/kani-cal1-control-w11/ch8-cal1/run.py)

Оба job ограничены 225 мин. В окне 45 мин идут source/deps setup, одна сборка stock Kani и discovery. Успешный Linux discovery даёт допуск macOS job. Лимиты одиночных слотов суммарно составляют 139 мин, каждый batch получает до 600 с. Latest-start требует полного окна слота и 10 с headroom до 202-й минуты. Поздние слоты получают `NOT_STARTED`, если окно уже не помещается. Версионные пробы и повторные проверки обоих checkout делят до 120 с с общим дедлайном на 204-й минуте. Дальше выделены 5 мин на финализацию, 7 мин на upload и 9 мин резерва. После таймаута аттестации сохранённые слоты и `attestation.json` входят в частичный артефакт. Внутри слота зарезервированы 5 с на фиксацию результата и 10 с на TERM/KILL/wait. После проверенной очистки следующие независимые слоты продолжаются.

| Платформа | Singleton cap | Batch cap | Резерв |
| --- | ---: | ---: | ---: |
| Ubuntu | 10 GiB | 12 GiB | 2 GiB |
| macOS | 5,5 GiB | 5,5 GiB | 1,25 GiB |

Supervisor проверяет доступную память и давление при допуске и во время работы. Linux читает `/proc` и PSI. Darwin наблюдает RSS через `ps`, оценивает доступную память через `hw.memsize` и `memory_pressure -Q`, а уровень получает из `kern.memorystatus_vm_pressure_level`. Warning и critical блокируют допуск или останавливают запуск даже при достаточном резерве. Receipt сохраняет свободный процент, уровень и ошибки проб. RSS — сумма KiB по выбранной process group и обнаруженным потомкам в одном сэмпле. Общие страницы могут учитываться несколько раз. Receipt фиксирует cadence, пропуски, stop/reap и эффективный предел. Batch timeline сохраняет изменения набора наблюдавшихся CBMC PID. Индивидуальный RSS batch-корня остаётся неизвестным. [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py) · [Коды давления XNU](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/event_private.h#L276-L278)

## Артефакт и локальные проверки

- `index.json` связывает run/attempt, trigger, source/checkouts, версии, frozen request, размеры и SHA-256 members и все ожидаемые слоты. Setup receipt связывает launcher, pinned nightly, CBMC, goto-cc/goto-instrument, установленный Kissat и чистоту Kani до/после. Версия используемой CaDiCaL берётся из native solver banner при наличии. Первые строки version probes сохраняются даже при отклонённом пине. [Баннер goto-cc](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-cc/gcc_mode.cpp#L323-L333) · [Версия CaDiCaL](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/sat/satcheck_cadical.cpp#L38-L41)
- При ошибке сборки Kani, ранней пробы или discovery `setup.json` сохраняет отдельные первые ошибки stdout и stderr, до 80 строк и 16 KiB на поток. При отсутствии заголовка сохраняется помеченный префикс. Итог Cargo доступен в отдельном хвосте stderr. В `error.json` есть фаза, указатель на запись и распознанное первичное сообщение. [Проекция диагностик](/root/kani-cal1-control-w11/ch8-cal1/setup_diagnostics.py)
- На слот сохраняются `receipt.json`, bounded `projection.json` и для batch `timeline.json`. Singleton содержит native checks/covers с ID, status, description и location плюс stock totals. Batch содержит stock totals и идентификаторы, метки отдельных свойств при terse остаются `UNKNOWN`. Receipt хранит отдельно фазу stdout с доступным native timestamp и фазу sampler с временем monotonic. В частичном итоге с нетаймированной строкой stdout отображается наблюдение sampler с его временем. Compile/symex/SSA/SAT записываются при наблюдаемом источнике. Окно под projection — до 4 MiB, суммарно до 96 MiB на job. Index, summary и receipts сохраняются при усечении.
- `VERIFIED` и `FAILED` описывают наблюдаемые согласованные терминалы Kani. `TIMEOUT`, `RSS_LIMIT`, pressure/cleanup, сигнал, setup failure, `NOT_STARTED`, `NOT_RUN` и `INCOMPLETE` сохраняют причины и доступные частичные сведения. Отсечённые длительности остаются censored. `SUMMARY.md/json` сравнивают по каждой ОС standard + contract в штатном порядке, `ceil(total/4)`, перемещения и вклад выбранных корней. Отдельно приведены холодная компиляция, native verifier work/span, полный wall и наблюдённый batch. Для каждой метрики с выбранными корнями `UNKNOWN` означает отсутствие завершённых значений. Частичный агрегат показывает долю замеров и ID недоступных и отсечённых корней. Абсолютный прогноз и stock baseline macOS jobs=1 имеют статус `UNKNOWN`. Замер macOS p2 от 45173593629 закреплён в request. [Штатный run](https://github.com/model-checking/verify-rust-std/actions/runs/45173593629)
- В раунде 4 прошли 43 offline-теста Python, `git diff --check`, разбор workflow через PyYAML и `bash -n` для 12 shell-шагов обоих jobs. Проверен SHA-256 bundle по frozen request. На отдельной shallow std base `git bundle verify` и `unbundle` прошли без создания refs. Сверены единственный advertised `HEAD`, tree, единственный родитель overlay и layout. Синтетический exact push для итогового control прошёл guard, несовпадающий SHA отклонён. В overlay относительно третьего раунда изменён один импорт. В control обновлены bundle и три значения frozen request — commit, tree и SHA-256 bundle.
- Раунд 4 завершён локальными коммитами. CI, push и локальные Cargo, rustc, Kani и CBMC не запускались. Compile PASS и результаты harnesses остаются неизвестными. [Проверки предыдущего исправления](CAL1-FIX-HANDOFF.md)
