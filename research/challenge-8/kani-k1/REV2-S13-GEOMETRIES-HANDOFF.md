# REV2 · три опорные геометрии sort13

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

Локальный пакет содержит одну Ubuntu job и шесть замороженных слотов. Задание сверено с g0 `a7e5a01d5f`, handoff добавлен поверх текущей g0. Следующий шаг — независимое diff-ревью и отдельный GO. Компиляция на пине, нативный discovery, новые ID, вердикты и ресурсы ожидают будущего допуска. [Задание](REV2-S13-GEOMETRIES-TASK.md) · [Разбор exact S13/base1](REV2-S13-BINDING-RESULTS-ANALYSIS.md)

## Идентичности

| Объект | Локальный worktree и ref | Commit | Tree | Единственный parent |
| --- | --- | --- | --- | --- |
| Std | `/root/verify-rust-std-rev2-s13-geometries-w14`, `work/rev2-s13-geometries-std-w14` | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` | `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `32c2857f4b7137601de54ea42a02610c8fd29ed9` |
| Control | `/root/kani-rev2-s13-geometries-control-w14`, `work/rev2-s13-geometries-control-w14` | `7eb91451d891bfdd802591b30b065f941c51b019` | `7665875a528b2de2e8df5dc50f9a7637bf1a7808` | `4beae2f1b03f6e88abd8dc673eb5a37b835f2dd3` |
| Review-trigger | `/root/kani-rev2-s13-geometries-trigger-w14`, detached sparse checkout, локальный ref `local/rev2-s13-geometries-trigger-review` | `7e8cf4c0e3eac78d6a7f0fad61d9d84a580ef8d7` | `7665875a528b2de2e8df5dc50f9a7637bf1a7808` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

| Вход | SHA-256 |
| --- | --- |
| `CI-REQUEST.json` | `f60a71e65ad2f9c595db00321fa8e9570f839ef3df27725f19d7c7a5d9d869e8` |
| Canonical roster | `6f22724a84cd44811834005ba5c2300395e2f64b31e3631cc93c6c8c90f386f5` |
| `std-overlay.bundle` | `922639b173b623e69c97013a8be83c993efd4d73c04135146e227ea689b0fc16` |

Canonical roster — UTF-8 от упорядоченного JSON-массива `roster` с сортировкой ключей и разделителями `(",", ":")`. Пакетный bundle объявляет только Std overlay `HEAD`, его prereq — shallow checkout Std `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Проверяется цепочка CAL1 → CAL2 → FIX3 → S13-binding → S13-geometries, включая tree и единственного родителя каждого коммита. [Request](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/CI-REQUEST.json) · [Bundle](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/std-overlay.bundle) · [Layout guard](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/request.py)

`pins` и `finish` независимо вычисляют `HEAD^{tree}` и сверяют поле из `CH8_REV2_S13_GEOMETRIES_TRIGGER_TREE`. При отдельном GO координатор задаёт это значение по ревью дерева `7665875a528b2de2e8df5dc50f9a7637bf1a7808`. Gate проверяет fork `Tiramisu-Cake/kani`, push в `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact SHA в окружении и payload `after`, единственного родителя из таблицы и чистый detached checkout. После `pins` сохраняется начальный receipt допуска. `finish` сравнивает его с повторной проверкой. Upload требует успешных `pins` и `finish`. Actions variables не менялись. [Workflow](/root/kani-rev2-s13-geometries-control-w14/.github/workflows/ch8-q-pilot.yml) · [Gate](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/request.py:137)

## Замороженные слоты

Интервалы полуоткрытые. Latest start измеряется в секундах от epoch первого шага job.

| Слот | Exact selector | Геометрия | Роль и ожидание | Latest start |
| --- | --- | --- | --- | ---: |
| `S13-B01-L17-BITS` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b01_l17_bits` | Base 1, срез [1,18), префикс [1,14), no-merge N17 | Proof, VERIFIED | 2700 |
| `S13-B13-L13-SWAP` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b13_l13_swap` | Base 13, цели в [13,26) | Check `swap_if_less`, VERIFIED | 2905 |
| `S13-B13-L13-BITS` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b13_l13_bits` | Base 13, срез и префикс [13,26), правая половина N25 | Proof, VERIFIED | 3110 |
| `S13-B17-L16-SWAP` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b17_l16_swap` | Base 17, цели в [17,30) | Check `swap_if_less`, VERIFIED | 3315 |
| `S13-B17-L16-BITS` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b17_l16_bits` | Base 17, срез [17,33), префикс [17,30), правая половина N32 | Proof, VERIFIED | 3520 |
| `S13-B17-L16-CORRUPT-MASK` | `slice::sort::shared::smallsort::verify::rev2_s13_geometries::s13_b17_l16_corrupt_mask` | Та же геометрия, инверсия одного бита наблюдения после actual вызова и проверок frame/canonical | Proof, FAILED с единственным ожидаемым отказом | 3725 |

На всех строках `replace=[]`, unwind 36. Bit-корни исполняют actual сеть с actual swap. Первые 13 элементов берутся из независимых битов, прочие 21 байт V34 и q произвольны. Срез передаётся целиком, а frame охватывает и хвост среза. Посты `REV2_S13_GEOMETRIES_{Q_FRAME,V34_FRAME,CANONICAL_OUTPUT,SORTED_POPCOUNT}`. Covers `REV2_S13_GEOMETRIES_{MIXED_INPUT,INPUT_INVERSION,REACHED_POST}` и `CAL1 q actual comparator executed`. Эти covers обязательны и на контроле. [Bit-корни](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs:13)

Байтовые Check используют `REV2_S13_SWAP_LEAF_{Q_FRAME,MIN_MAX,BYTE_FRAME}` и `REV2_S13_SWAP_LEAF_{SWAP,NO_SWAP,EQUAL_BYTES_DISTINCT_POSITIONS,MIXED_Q,NORMAL_RETURN}` плюс cover actual компаратора. Frame проверяет все позиции кроме двух целей. Если native вывод содержит несколько ID этого frame-поста после развёртки цикла, все его наблюдавшиеся экземпляры должны быть `SUCCESS`. [Байтовые корни](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs:72)

Контрольная метка `REV2_S13_GEOMETRIES_SORTED_POPCOUNT`, `library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs:69:5`. Положительный исход требует `VERIFIED` и exit 0. Для контроля требуется `FAILED` и exit 1, ровно один `FAILURE` класса `assertion` на этой метке и строке в regular и stock export, колонка 5 при её наличии в regular, совпадающий property ID, успешные q/V34 frame и canonical, штатные safety/overflow/unwind. Контрольный ID новой мономорфизации пока `UNKNOWN`. Прежний `check_s13_base1::<true>.assertion.9` относится к историческому корню. Stock экспортирует file/line для отказа и ID/status групп cover. Успешные ID и координаты постов берутся из regular, количество успешных checks сверяется с stock. [Точка assert](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_geometries.rs:69) · [Разбор результатов](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/results.py)

## Профиль, часы и диагностика

Одна job `ubuntu-24.04`, stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`. CBMC 6.11.0, CaDiCaL, OB12, unwind 36, `--exact --jobs=1 --no-assert-contracts`, штатные safety/overflow/unwind, uninit/validity OFF. На слот отдельные `kani-target`, `cargo-target`, `export.json` и `tmp`. Preflight в пределах 180 с setup проверяет witness компиляции `core` со всеми пятью флагами и сохраняет первые rustc diagnostics при отказе. Единственный cfg-on discovery требует 6 новых селекторов с 4 Proof и 2 Check, а также 6 неизменных наследуемых селекторов в двух REV2 модулях. Из discovery в исполнение селекторы не переносятся. [Runner](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/run.py)

| Участок | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup | 45:00 | 45:00 |
| Шесть слотов | 20:30 | 65:30 |
| Заключительная аттестация | 2:00 | 67:30 |
| Finish и upload | 12:00, из них до 5:00 и 7:00 соответственно | 79:30 |
| Резерв | 9:00 | 88:30 |
| Внешний job limit | 90:00 | 90:00 |

Каждый слот имеет 180 с cold wall, 10 с reap, 5 с receipt и 10 с запаса для расчёта latest start. Пик группы ограничен 4 GiB с резервом 2 GiB. Порог отбора VT ≤120 с. Часы читаются от epoch первого шага, включая финализацию. Фактический исход процесса, exit, argv, фаза, дедлайны и reap попадают в атомарный checkpoint до проекции. Дедлайн receipt равен более ранней из двух отсечек, 5 с после возврата supervisor или конец окна слота. Проекция прерывается за 1 с до дедлайна receipt. Наблюдавшийся вердикт и полнота свидетельства хранятся в разных полях. Задержанная запись сохраняет snapshot результата и проходит retry в `finish` вне окон слотов. После неподтверждённого reap оставшиеся слоты получают `NOT_STARTED` с причиной. При подтверждённом reap следующий запуск зависит от своего latest start и состояния supervisor. [Окна в request](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/CI-REQUEST.json) · [Receipt и финализация](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/run.py:446)

Receipts сохраняют VT, RSS группы и CBMC, наблюдения фазы, первую CNF и компактные обязательные anchors независимо от опционального timeline и детальной проекции. Предел проекции 4 MiB, артефакта 96 MiB. Сводка различает результат `FAILED`, совпадение с ожиданием и приёмку пары. Timeout, RSS-отсечка, неполный профиль, невалидный sampler, ошибка проекции, поздний receipt и посторонний отказ исключают приёмку пары. `PAIR_WITHIN_PROFILE` относится к двум слотам B17/L16 с бинарным входом, а `roster_within_profile` требует попадания всех шести слотов в профиль. Сохраняется оговорка supervisor о возможном недоучёте RSS на Linux. [Отчёт](/root/kani-rev2-s13-geometries-control-w14/ch8-cal1/report.py)

## Разрешение Rust-имён и cfg

| Место | Разрешение и минимальная видимость |
| --- | --- |
| Путь всех шести корней | `crate::slice` и `slice::sort` объявлены `pub`, `sort::shared` и `shared::smallsort` — `pub(crate)`. `smallsort::verify` приватен у `smallsort` и открыт его потомкам при `cfg(kani)`. `verify::rev2_s13_geometries` приватен у `verify` и имеет пять условий CAL1, CAL2 merge mask, FIX3 provider cost, S13 binding и S13 geometries. Шесть корней, `BACKING`, `LOW_BITS`, `check_bits` и `assert_swap_post` приватны у нового модуля, локальные переменные и const-параметры имеют область своих функций. |
| Импорт и actual вызов `sort13_optimal` | В новом модуле `super::super` — предок `smallsort`. Приватная функция предка доступна потомку. На вызове `check_bits:51` выводятся `T=u8, F=KeyLess<u8>` из `&mut [u8]` и `&mut less`. `BASE, LEN: usize` и `CORRUPT_MASK: bool` подставляются только из четырёх явных корней. Длины 17, 13 и 16 покрывают guard `len >= 13`, все `BASE+LEN <= 34`. |
| Импорт, атрибут и actual вызовы `swap_if_less` | Та же видимость приватной функции предка. Имя в `proof_for_contract(swap_if_less)` разрешается в области harness с этим импортом. Kani раскрывает атрибут в `kanitool::proof_for_contract` со строковым путём и вызовы публичных `kani::internal::{reset_contract_clause_depth, init_contracts}`. В harness на строках 85 и 103 передаются `*mut u8, usize, usize, &mut KeyLess<u8>`. Тип `BASE: usize` в `assert_swap_post` фиксирует индексы 13 или 17. |
| `super::cal1_model::KeyLess`, `with_q`, `q` и вызовы компаратора | `cal1_model` приватен у общего предка `verify`, доступен потомку при CAL1. `KeyLess` ограничен `pub(in crate::slice::sort::shared::smallsort)`, методы `with_q` и `q` имеют `pub(super)` до `verify`. Поле q приватно в `cal1_model`. Реализации `FnOnce` и `FnMut` для `KeyLess<u8>` используют публичные trait-методы, встроенный ABI `rust-call` и `PhantomData` из публичного `crate::marker`. CAL1 включает `fn_traits` только вместе с `kani`. На actual пути `FnMut::call_mut` испускает cover и сравнивает `a < b`. |
| `crate::kani`, атрибуты и intrinsics harness | `kani_core::kani_lib!(core)` при `cfg(kani)` создаёт публичный нестабильный модуль `crate::kani`. Re-export `pub use kani_core::*` и публичный re-export `kani_macros` открывают `proof`, `proof_for_contract`, `unwind`, `requires`, `ensures`, `modifies`. `proof` и `unwind` используют metadata `kanitool`. Макрос intrinsics создаёт публичные `any/assume/assert/cover`, а `generate_arbitrary!` даёт `Arbitrary` для `u8`, `u16`, `usize` и массивов. |
| Атрибуты `sort13_optimal` и `swap_if_less` в `smallsort.rs` | На sort13 под `all(kani, kani_smallsort_cal1)` приватный `verify` доступен в его родителе, `cal1_q_merge_model` имеет `pub(super)`, `merge_wide`, `presort_geometry/capture/post` и `PrefixSnapshot` видимы до `smallsort`. Const-параметр атрибутов — 13, `modifies` получает `*mut [T; 13]`. На swap под FIX3 `verify::rev2_provider_cost` имеет `pub(super)`, `swap_leaf_geometry/capture/post` и `SwapCapture` ограничены `smallsort`. `old` обрабатывается Kani в `ensures`. `modifies` под `kani` перечисляет два `*mut T` через `wrapping_add`. Штатные `safety::requires` используют `size_of` из prelude, публичный `crate::ptr` и его `pub(crate) byte_offset_does_not_wrap`, `crate::ub_checks` с публичными re-export предикатов из `kani::mem` при Kani и обычными реализациями при cfg-off. |
| Индексы, срезы, маски и байты | `as_mut_ptr`, `iter/iter_mut`, `len`, `*mut u8::add` и `cast` — публичные inherent методы срезов и указателей. Индексация и `enumerate` идут через публичные `Index/IndexMut` и `Iterator`. `u16::from(u8)` — публичный `From` из prelude, `u16::count_ones` — публичный примитивный метод с `ctpop`. Для low mask проходы и сдвиги в пределах 0–12, popcount 0–13. Обе стороны `min/max` — `Ord` для `u8` из prelude. |

Без `kani` выключены весь `verify` и Kani facade. При Kani и выключенном новом cfg четыре наследуемых флага оставляют S13-binding и лист FIX3 доступными. Удаление новой регистрации и строки check-cfg восстанавливает точные blobs Std-базы. `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`, `cal1_model.rs` `236394dcfb1ff571ee6f816391f7b2e00cc9e630` и `rev2_provider_cost.rs` `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` совпадают у FIX3, S13-binding и нового overlay. [Реестр Std](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify.rs:97) · [Kani facade](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/lib.rs:366) · [FIX3 Check](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:88)

## Привязка байтового листа и пороговый перенос

Для Base1/len17 используется `S13-SWAP-LEAF` из run `45661535099`, exact `slice::sort::shared::smallsort::verify::rev2_provider_cost::s13_swap_leaf`, `VERIFIED`, exit 0, 6/6 covers, VT 32,66 с, cold wall 59,74 с, пик группы 2 046 696 KiB. SHA-256 receipt `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c`. Профили совпадают по stock Kani, CBMC, CaDiCaL, OB12, unwind36, exact singleton, `--no-assert-contracts`, uninit/validity OFF и actual FIX3 Check. Два новых cfg добавляют только корни. [Готовый receipt](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/slots/S13-SWAP-LEAF/receipt.json) · [Разбор FIX3](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

В лист Base1 передаётся `V34.as_mut_ptr().add(1)`. В `sort13_optimal(&mut V34[1..18], …)` указатель `v.as_mut_ptr()` имеет ту же базу адреса и ту же доступную префиксную область для двух targets. Длина обёртки в `swap_if_less` не передаётся. Для всех трёх геометрий V34 полностью инициализирован, q независим. При `0 ≤ a < b < 13` адреса выровнены для `u8`, принадлежат одному живому массиву, доступны на чтение и запись через эксклюзивный `&mut` и адресуют непересекающиеся байты. Оба результата actual swap — инициализированные байты `min/max`, остальные 32 байта и q сохраняются. Это поддерживает предпосылки следующего вызова. Для Base13 и Base17 нативные листы из пакета проверяют эту же связь на своих адресах. [Actual swap](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:440) · [Домен листа](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:144)

`sort13_optimal` проверяет `v.len() < 13`, берёт один `v_base` и выполняет следующие 45 вызовов подряд. Пары в точном порядке сверены с FIX3 `SWAP_PAIRS`. Каждый столбец абсолютных адресов привязан к соответствующему байтовому листу. [Guard и расписание](/root/verify-rust-std-rev2-s13-geometries-w14/library/core/src/slice/sort/shared/smallsort.rs:597)

| Вызов | Аргументы листа `(a,b)` | Base 1 абсолютные цели | Base 13 абсолютные цели | Base 17 абсолютные цели |
|---:|---:|---:|---:|---:|
| 01 | (0,12) | (1,13) | (13,25) | (17,29) |
| 02 | (1,10) | (2,11) | (14,23) | (18,27) |
| 03 | (2,9) | (3,10) | (15,22) | (19,26) |
| 04 | (3,7) | (4,8) | (16,20) | (20,24) |
| 05 | (5,11) | (6,12) | (18,24) | (22,28) |
| 06 | (6,8) | (7,9) | (19,21) | (23,25) |
| 07 | (1,6) | (2,7) | (14,19) | (18,23) |
| 08 | (2,3) | (3,4) | (15,16) | (19,20) |
| 09 | (4,11) | (5,12) | (17,24) | (21,28) |
| 10 | (7,9) | (8,10) | (20,22) | (24,26) |
| 11 | (8,10) | (9,11) | (21,23) | (25,27) |
| 12 | (0,4) | (1,5) | (13,17) | (17,21) |
| 13 | (1,2) | (2,3) | (14,15) | (18,19) |
| 14 | (3,6) | (4,7) | (16,19) | (20,23) |
| 15 | (7,8) | (8,9) | (20,21) | (24,25) |
| 16 | (9,10) | (10,11) | (22,23) | (26,27) |
| 17 | (11,12) | (12,13) | (24,25) | (28,29) |
| 18 | (4,6) | (5,7) | (17,19) | (21,23) |
| 19 | (5,9) | (6,10) | (18,22) | (22,26) |
| 20 | (8,11) | (9,12) | (21,24) | (25,28) |
| 21 | (10,12) | (11,13) | (23,25) | (27,29) |
| 22 | (0,5) | (1,6) | (13,18) | (17,22) |
| 23 | (3,8) | (4,9) | (16,21) | (20,25) |
| 24 | (4,7) | (5,8) | (17,20) | (21,24) |
| 25 | (6,11) | (7,12) | (19,24) | (23,28) |
| 26 | (9,10) | (10,11) | (22,23) | (26,27) |
| 27 | (0,1) | (1,2) | (13,14) | (17,18) |
| 28 | (2,5) | (3,6) | (15,18) | (19,22) |
| 29 | (6,9) | (7,10) | (19,22) | (23,26) |
| 30 | (7,8) | (8,9) | (20,21) | (24,25) |
| 31 | (10,11) | (11,12) | (23,24) | (27,28) |
| 32 | (1,3) | (2,4) | (14,16) | (18,20) |
| 33 | (2,4) | (3,5) | (15,17) | (19,21) |
| 34 | (5,6) | (6,7) | (18,19) | (22,23) |
| 35 | (9,10) | (10,11) | (22,23) | (26,27) |
| 36 | (1,2) | (2,3) | (14,15) | (18,19) |
| 37 | (3,4) | (4,5) | (16,17) | (20,21) |
| 38 | (5,7) | (6,8) | (18,20) | (22,24) |
| 39 | (6,8) | (7,9) | (19,21) | (23,25) |
| 40 | (2,3) | (3,4) | (15,16) | (19,20) |
| 41 | (4,5) | (5,6) | (17,18) | (21,22) |
| 42 | (6,7) | (7,8) | (19,20) | (23,24) |
| 43 | (8,9) | (9,10) | (21,22) | (25,26) |
| 44 | (3,4) | (4,5) | (16,17) | (20,21) |
| 45 | (5,6) | (6,7) | (18,19) | (22,23) |

Для порога t отображение `Pₜ(x)=[x ≥ t]` переводит `min` в AND, `max` в OR и сохраняет случай равных байтов. Расписание компараторов и наблюдательное q не зависят от t. После каждого из 45 вызовов проекция байтового состояния равна состоянию сети, запущенной на его бинарной проекции. При успешных битовом корне и листе это даёт порядок для произвольных байтов каждой геометрии, поскольку инверсия `x>y` видна при `t=x`. Popcount выходных проекций сохраняет все пороговые счётчики одного байтового выхода. Разности счётчиков при t и t+1 дают кратности 0–254, счётчик при t=255 — кратность 255. Локальные frames сохраняют q и все позиции за префиксом, включая 4, 0 или 3 байта хвоста переданного среза. Перенос соответствует принятому внешнему аргументу exact S13/base1. Для `stub_verified(sort13_optimal)` остаётся нужен свой нативный Check либо отдельно проверенная композиция. [Пороговый перенос](REV2-S13-BINDING-DESIGN.md#перенос-на-произвольные-байты) · [Граница native Replace](REV2-S13-BINDING-REVIEW.md#допуск-и-native-replace)

## Локальная валидация

- `rustfmt --check` на двух затронутых Rust-файлах прошёл. Использован `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max --config skip_children=true,reorder_modules=false`.
- Отдельный `git diff --check` прошёл на Std, control, дереве локального trigger относительно его родителя и handoff. Сравнение по трём исходным blobs подтверждает отсутствие runtime diff и совпадение листа/компаратора. Статический cfg-off восстанавливает исходные manifest и registry побайтно.
- Python извлёк из actual тела все 45 пар в порядке FIX3, сверил каждую строку карты и адреса для всех трёх баз. Перебраны 8 192 бинарные маски и 65 536 пар байтов на границах смены порога. Проверены формула sorted-popcount, изменение popcount от порчи и тождества min/max → AND/OR.
- В полном Python unittest suite прошло 98 тестов в обычной шкале. Те же 98 прошли с переустановкой monotonic на 60,000003 с независимо от аптайма. Все связанные чтения в тестах с синтетическим временем, включая `finish`, использовали ту же шкалу.
- Синтетика проверила точный список Proof/Check, неверную категорию, лишний селектор и неверный файл. Preflight проверен до discovery, с witness `core` и с первыми диагностическими строками при отказе компилятора. Проверены пустой, старый и чужой pin у `pins` и `finish`, подмена дерева с согласованными SHA payload и trailer и несовпадение начального receipt. Дополнительно локальный sparse trigger прошёл gate с синтетическим событием и ожидаемым tree.
- Проверены прерывание медленной проекции после checkpoint, поздняя запись и deferred retry с сохранением фактического `FAILED`, допуск последнего слота точно на границе, ранний отказ и блокировка дальнейших слотов после неподтверждённого reap. Проверены посторонний отказ контроля, несовпадающая колонка, предел проекции с сохранением anchors и отдельно профильные причины отказа в приёмке.
- YAML загружен в режиме запрета дублирующихся ключей. `bash -n` прошёл для всех шести `run`-блоков. Подтверждены одна Ubuntu job, 90 мин внешнего лимита и обе зависимости upload.
- Пакетный bundle проверен с `bundle verify` и `unbundle` на отдельном depth-1 checkout точной CI-базы `dab03cf510`. Единственный advertised ref — overlay `HEAD`, все tree/parent и layout guard совпали. HEAD, существующие refs и shallow boundary сохранились. Дополнительная временная проверка инкрементального delta `32c2857f4b..overlay` на точной depth-1 S13-binding базе дала те же гарантии refs и parent. В пакет входит один bundle.

Cargo, rustc, Kani и CBMC локально не запускались. Пакет остался локальным, без push, CI и публикации. Все три пакетных коммита и handoff используют `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`.
