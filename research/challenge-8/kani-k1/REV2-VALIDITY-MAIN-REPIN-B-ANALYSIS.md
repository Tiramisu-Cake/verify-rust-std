# REV2 валидность · разбор фазы B run 45870184232

**ANALYSIS_READY** · `proof_credit=NONE` · ledger **Item 2** · исполнитель w11 · [Задание](REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS-TASK.md) · [Handoff](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md) · [GO FIX4](REV2-VALIDITY-MAIN-REPIN-FIX4-GO.md)

Разбор офлайновый: читались только опубликованные receipts из `/root/ch8-artifacts/run-45870184232/`, исходники кандидата Kani `4caf097d84` (= main `8c6dba5935`, merge kani#5205), overlay Std `bc866f8dfa` и исходники CBMC, сверенные с тегом `cbmc-6.11.0`. Cargo, rustc, Kani и CBMC не запускались. CI, push, изменений Actions variables и публикаций не было. Выводы, которые не подтверждены прогоном, помечены как гипотезы.

## Итог

1. **`swap_bool_n02` — это не kani#5104 и не дефект fixture-логики. Наиболее вероятная причина — кодирование `<` для `bool`.** Kani понижает `bool` в CBMC-тип `c_bool` и строит `c_bool < c_bool`. В CBMC 6.11.0 `convert_bv_rel` не обрабатывает `c_bool` и уходит в `convert_rest`. Тот подставляет свободную пропозициональную переменную и печатает `warning: ignoring`. Поэтому любое сравнение `<`/`>`/`<=`/`>=` двух символьных `bool` недетерминировано. Это объясняет все наблюдения: сортированность падает и в OFF, и в ON, а multiset (`==`) держится. Чтобы подтвердить вывод, достаточно маленьких probe-слотов в FIX5.
2. **`mutable cast` в network ON** — остаточное ограничение после kani#5205. Оно срабатывает на приведении `*mut [T; 32]` → `*mut T` в `smallsort.rs:423`. Валидность массива разложена по 32 смещениям, валидность элемента — по одному, поэтому `dest_validity != src_validity` (`check_values.rs:1114-1119`). Всякий network-маршрут с merge (len ≥ 18) на нишевом типе обрезается на этом месте. Дубликатов в model-checking/kani не нашёл; upstream issue оправдан после минимального repro.
3. **TIMEOUT.** Во всех char-слотах OFF symex и первый solve укладываются в 7 с. Всё остальное время, 137–142 с, уходит на последний, финальный UNSAT по функциональным проверкам над 32-битными `char`. В network n19 OFF один symex занимает 37 с. Меньшее N не помогает: `sort8` без stable-обвязки уже минимален и тоже упал в TIMEOUT. Главный рычаг — ранговый домен ключей, у отрицательного контроля функциональная проверка не нужна вовсе.
4. **Скрытый дефект FIX4, обнаруженный по receipts.** Чтение вида `*values.as_ptr()` порождает на строке не два свойства, а 2 + N. N свойств `[T; N]` на столбце 27 даёт autoref `&values`. Для отрицательного `vv_stable_char_n09_corrupt` ON гейт FIX4 дал бы MISMATCH и без таймаута. В FIX5 указатель нужно брать до порчи, как в фазе A.

## 1. `vv_swap_bool_n02`: OFF и ON — FAILURE на сортированности

### Наблюдения (receipts)

| Слот | Terminal | Exit | Failure | Multiset `assertion.2` | Covers |
| --- | --- | --- | --- | --- | --- |
| OFF | `VERIFICATION:- FAILED` | 1 | только `check_sorted_and_full_multiset::<bool, 2>.assertion.1` «normal return is sorted», `validity_main.rs:29:9` | SUCCESS | 3/3 SATISFIED |
| ON | `VERIFICATION:- FAILED` | 1 | то же одно свойство | SUCCESS | 3/3 SATISFIED |

В ON все validity-свойства в SUCCESS, в том числе пары `bool` в `smallsort.rs:483:35`/`:42` и чтение `ManuallyDrop<bool>` в `:498:36`. Status counts OFF: FAILURE 1, SUCCESS 373, UNREACHABLE 9; ON: FAILURE 1, SUCCESS 938, UNREACHABLE 21. CBMC OFF: 6285 steps, 651 VCC, 70 после упрощения, VT 0,71 с.

### Почему не kani#5104

kani#5104 описывает чтение через условно выбранный указатель, которое возвращает **чужой** элемент. Для `swap_if_less` на `[u8; 17]`/`[u8; 1]` такие сбои ломают значения на обеих позициях (комментарий 2026-11-03 в issue). Здесь при n = 2 чтение не того элемента в `ptr::read(v_b_swap)` (`smallsort.rs:496`) дало бы дубликат:
- при `should_swap`: `v_a ← b` (`:497`), `v_b ← tmp = b`, итог `[b, b]`;
- при `!should_swap`: итог `[a, a]`.

Когда `a ≠ b`, это ломает счётчик multiset, а `a ≠ b` достижимо: cover «swap path» SATISFIED. Но `assertion.2` в SUCCESS на всех путях. Значит, на этом корне чтение чужого элемента не наблюдается. Выход всегда перестановка входа, неверен только порядок.

### Как кодируется `select_unpredictable` на кандидате

- `core::hint::select_unpredictable` (`library/core/src/hint.rs:838-886`) оборачивает аргументы в `MaybeUninit`. Затем она вызывает интринсик `crate::intrinsics::select_unpredictable` на указателях (`:871-872`) и на значениях (`:885`).
- У интринсика есть fallback-тело `if b { forget(false_val); true_val } else { … }` (`library/core/src/intrinsics/mod.rs:755-763`, `#[rustc_intrinsic]`, без `must_be_overridden`).
- В `4caf097d84` `uses_kani_model` (`kani-compiler/src/intrinsics.rs:864-882`) возвращает `false` для интринсика с телом, если это не generic float. Своей модели `select_unpredictable` в Kani нет: `git grep select_unpredictable 4caf097d84 -- kani-compiler library` пуст. SEL1-функция `select_unpredictable_fallback` из [KANI5104-RECON](KANI5104-RECON.md) в кандидат не входит.
- Итог: обычный MIR `SwitchInt` → GOTO-ветвление с двумя присваиваниями указателя. Специального CBMC-выражения (`if_exprt`/select) нет. После слияния у указателя value set {`&v[0]`, `&v[1]`}, и CBMC разыменовывает его через case split по этому value set.

### Механизм: `<` на `bool`

1. **Rust.** `bool_less` (`validity_main.rs:12-14`) и проверка (`:29`) сравнивают `bool` через `<`. В core это `partial_ord_methods_primitive_impl!`, `fn lt(&self, other) { *self < *other }` (`library/core/src/cmp.rs:2199-2208`, `impl PartialOrd for bool` в `:2260-2267`). В MIR это `BinOp::Lt` над двумя `bool`.
2. **Kani.**
   - `ty::Bool => Type::c_bool()` (`kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs:604`).
   - `Type::c_bool()` — это `CInteger(CIntType::Bool)` (`cprover_bindings/src/goto_program/typ.rs:1021-1023`); `is_integer()` для него `true` (`:599-605`). Поэтому проверка `typecheck_binop_args` для `Lt` проходит (`cprover_bindings/src/goto_program/expr.rs:1276-1278`).
   - `comparison_expr` строит `left.lt(right)` без приведения (`kani-compiler/src/codegen_cprover_gotoc/codegen/rvalue.rs:1838-1855`, вызов из `:37-45` и `:401-407`). Для `bool` нет особой ветки.
   - В irep тип уходит как `ID_c_bool` шириной 8 (`cprover_bindings/src/irep/to_irep.rs:800-803`).
3. **CBMC 6.11.0.**
   - `boolbvt::convert_bool` отправляет `ID_lt/gt/le/ge` в `convert_bv_rel` (`src/solvers/flattening/boolbv.cpp:362-365`).
   - `convert_bv_rel` обрабатывает float, signed, unsigned, fixed, range и verilog, но не `IS_C_BOOL` (`src/solvers/flattening/boolbv_bv_rel.cpp:31-97`). `get_bvtype(c_bool) = IS_C_BOOL` (`boolbv_type.cpp:19-20`).
   - Поэтому вызывается `SUB::convert_rest(expr)` → `prop_conv_solvert::convert_rest`: `ignoring(expr); return prop.new_variable();` (`src/solvers/prop/prop_conv_solver.cpp:314-319`). `ignoring` печатает `warning: ignoring <expr>` (`:432-437`).
   - `simplify_inequality` вычисляет сравнение, только когда **оба** операнда константы (`src/util/simplify_expr_int.cpp:1435-1441`). При символьных `bool` выражение доходит до решателя.
   - Сверено по тегу: в `cbmc-6.11.0` `boolbv_bv_rel.cpp` не содержит `IS_C_BOOL`, а `simplify_expr_int.cpp` — `c_bool`. Diff рабочего checkout к тегу по этим файлам не затрагивает эти ветви.
4. **Следствия.**
   - `should_swap` (`smallsort.rs:483`) и `sorted[1] < sorted[0]` (`validity_main.rs:29`) — свободные литералы. Assertion сортированности падает даже при идеальном обмене.
   - Обмен остаётся перестановкой при любом решении, поэтому multiset держится.
   - Оба cover по `original[1] < original[0]` SATISFIED. Они могут быть ложно удовлетворены, и как свидетельство их использовать нельзя.
   - OFF/ON не важен: это не valid-value pass.
5. **Почему pr752 проверяет ту же функцию для `u8`/`u64`.**
   - Функциональные проверки `swap_if_less` в pr752 используют только целые типы: `sorted_permutation_swap_u8_n2` (`verify/fixed_inputs.rs:111-116`) и `swap_contract_four_positions_{u8,i32,u64}` с `ensures` `swap_transfer`/`swap_ordered` (`verify/network.rs:88-118`, `verify/merge/profiles.rs:192-226`).
   - Это `unsignedbv`/`signedbv`, и `convert_bv_rel` их кодирует.
   - `swap_safety_bytes17_backing4` проверяет только frame (`verify/helper_contracts.rs:30-66`). Значения на позициях `a`/`b` там не сравниваются, и kani#5104 этот harness не задевает.
6. **Масштаб.**
   - Задеты любые `<`/`>`/`<=`/`>=` и `Ord::cmp` на символьных `bool`. `Cmp` строится как `(l > r) - (l < r)` (`rvalue.rs:1865-1867`), а `Ord for bool` идёт через `three_way_compare`.
   - Значит, `slice::sort` и `min`/`max` на `bool` дают ложные контрпримеры и ложно удовлетворённые covers.
   - Ложного SUCCESS для assertions этот механизм не даёт: свободный литерал только расширяет множество поведений.
   - Ни `char` (`unsignedbv 32`), ни `NonZero<u8>` не задеты.
   - Дубликатов не нашёл. Поиск в model-checking/kani: `bool comparison`, `c_bool`, `bool less than`, `PartialOrd bool`, `ignoring lt`, `comparing booleans`. Поиск в diffblue/cbmc: `c_bool relational/less/comparison`, `convert_bv_rel`. Эвристический grep тестов Kani на `4caf097d84` не находит сравнений символьных `bool` через `<`.

**Уверенность.** По исходникам высокая, но receipts публикуют только префикс stdout, и строки `warning: ignoring` в них нет. Прогоном это не подтверждено.

### Минимальная проверка (в составе FIX5, не отдельный пакет)

Standalone probes в `validity_fixture.rs` (фаза A, слоты дешёвые). Код предлагается, а не собран:

```rust
/// Symbolic bool ordering against its truth table.
#[kani::proof]
pub fn bool_order_probe() {
    let a: bool = kani::any();
    let b: bool = kani::any();
    kani::cover!(a != b, "bool_order_probe:distinct");
    assert_eq!(a < b, !a && b);
}

/// The same table through u8 keys.
#[kani::proof]
pub fn bool_order_u8_control() {
    let a: bool = kani::any();
    let b: bool = kani::any();
    kani::cover!(a != b, "bool_order_u8_control:distinct");
    assert_eq!((a as u8) < (b as u8), !a && b);
}
```

Ожидания по гипотезе:
- `bool_order_probe` OFF/ON — FAILURE ровно на одном assertion;
- `bool_order_u8_control` OFF/ON — SUCCESS.

Дополнительно предлагаю non-gating маркер в `native_metrics`: число строк stdout с подстрокой `warning: ignoring` и координата первой (только данные, без текста выражения). Для probe ожидается ≥ 1, для control 0. Трасса контрпримера (`--concrete-playback=print`) не нужна. Таблица истинности различает гипотезы сама, и argv-политику пакета расширять не придётся.

Отдельная проверка kani#5104 (`[u8; 1]` через `select_unpredictable`) к `bool` не относится. Если координатор захочет узнать, исправлен ли kani#5104 на main, её можно добавить слотом с ожиданием `OBSERVE`, но в основной roster я её не включаю.

## 2. `vv_network_nonzero_n19` ON: `mutable cast`

### Где и почему

- **Источник.** `smallsort.rs:423:28` в ветке merge `small_sort_network`: `let scratch_base = stack_array.as_mut_ptr() as *mut T;`, где `stack_array: MaybeUninit<[T; SMALL_SORT_NETWORK_SCRATCH_LEN]>` (`:383`, длина 32). `MaybeUninit::as_mut_ptr` даёт `*mut [T; 32]`, затем идёт `PtrToPtr` в `*mut T`.
- **Kani.** `visit_rvalue`, `CastKind::PtrToPtr` (`kani-compiler/src/kani_middle/transform/check_values.rs:1063-1133`):
  - ранний выход, если валидность целевого pointee пуста (`:1088-1096`), это правило добавил kani#5205;
  - для непустых требований `ty_validity_per_offset(src) != ty_validity_per_offset(dest)` даёт `SourceOp::UnsupportedCheck { check: "mutable cast", ty: src_ty }` (`:1107-1119`);
  - для массива требования разворачиваются по каждому элементу (`FieldsShape::Array`, `:1508-1528`): у `[NonZero<u8>; 32]` 32 записи, у `NonZero<u8>` одна. Список не совпадает, хотя тип элемента тот же.
- **Свойство.** `small_sort_network::<NonZero<u8>, …nonzero_less…>.unsupported_construct.1`, status **FAILURE**, описание «Kani currently doesn't support checking validity of `mutable cast` for `*mut [num::nonzero::NonZero<u8>; 32]`». `assert(false); assume(false)` обрезает путь. Поэтому cover «both sort9 halves, odd merge, copy-back returned» UNREACHABLE, а слот завершился за 85 с (VT 47,5 с), тогда как OFF ушёл в TIMEOUT.
- **Другие приведения в `smallsort.rs`** не задеты:
  - `:268` — `*mut [T; 32]` → `*mut MaybeUninit<T>`: валидность цели пуста;
  - `:295` — `*mut MaybeUninit<T>` → `*mut T`: валидность источника пуста, `:1110`.
- **Когда достижимо.** Только при len ≥ 18 (`no_merge = len < 18`, `:386`) и только для типов с нишей: `bool`, `char`, `NonZero*`, enum. Для `u8`/`u64` срабатывает ранний выход.

### Формулировка для описания pr752 (EN)

> Under `-Z valid-value-checks` (Kani main `8c6dba5935`), `small_sort_network` on an element type with a niche (e.g. `NonZero<u8>`) and a length of at least 18 reaches the cast `stack_array.as_mut_ptr() as *mut T` before the merge. Kani reports this cast as an unsupported construct, so value validity on the merge and copy-back path of the network route is not checked for such types. Shorter lengths (sort9/sort13 plus insertion) do not reach the cast and are checked.

### Поиск дубликатов (model-checking/kani)

Запросы: `"mutable cast"`, `mutable cast validity`, `valid-value-checks cast array`, `doesn't support checking validity`, `UnsupportedCheck mutable`, `validity array element pointer cast`. Близкие результаты:

| № | Состояние | Суть | Отношение |
| --- | --- | --- | --- |
| kani#5205 (PR) | merged 2026-11-25 = наш pin | «mutable casts to other pointee types were reported as unsupported» — исправлено для целей **без** требований валидности | Остаток: цели с требованиями, отличными от источника |
| kani#3762 | closed (by kani#5205) | `copy`/`copy_nonoverlapping` | Другой механизм |
| kani#5021 | closed (by kani#5205) | `*mut bool → *mut u8` round-trip не ловился | Обратное направление |
| kani#5056 | closed | Упоминает существующий `mutable cast` (`*mut bool` → `*mut u8`) как вне scope | Не массив → элемент |
| kani#3332 (PR) | closed | Отказ от mutable cast при несовместимом padding (uninit) | Другой pass |
| kani#5069 (PR) | open | Enum discriminants | Не связано |

Отдельного issue о приведении «массив → свой элемент» (`*mut [T; N] as *mut T`) нет.

### Нужен ли upstream issue

**Да, после минимального repro.**
- Случай частый: это реальный путь `core` на всех нишевых типах при len ≥ 18.
- Корректность понятна: запись через `*mut T` в `[T; N]` — типизированная запись `T`. Требования источника, суженные на `[0, size_of::<T>())`, совпадают с требованиями цели.
- Направление исправления: сравнивать валидность цели с валидностью источника на диапазоне цели, а не целиком.

Repro для FIX5 (фаза A, дёшево):

```rust
/// Array-to-element mutable cast, the shape of smallsort.rs:423.
#[kani::proof]
pub fn array_elem_cast_nonzero() {
    let mut storage = core::mem::MaybeUninit::<[core::num::NonZeroU8; 4]>::uninit();
    let element = storage.as_mut_ptr() as *mut core::num::NonZeroU8;
    unsafe { element.write(core::num::NonZeroU8::MIN) };
    kani::cover!(true, "array_elem_cast_nonzero:write_complete");
}

/// Control: same cast with a u8 element (no validity requirements).
#[kani::proof]
pub fn array_elem_cast_u8_control() {
    let mut storage = core::mem::MaybeUninit::<[u8; 4]>::uninit();
    let element = storage.as_mut_ptr() as *mut u8;
    unsafe { element.write(1) };
    kani::cover!(true, "array_elem_cast_u8_control:write_complete");
}
```

Ожидания:
- `array_elem_cast_nonzero`: OFF — SUCCESS; ON — ровно одно `unsupported_construct` FAILURE «… `mutable cast` for `*mut [num::nonzero::NonZero<u8>; 4]`» на строке приведения, cover UNREACHABLE;
- `array_elem_cast_u8_control`: OFF и ON — SUCCESS.

Текст issue и решение о публикации остаются за владельцем: сначала показ текста и проверка LLM-политики проекта. Ничего не публиковалось.

## 3. TIMEOUT: фаза отсечки, CNF, RSS

CBMC стартует через 35–37,5 с после начала слота: холодная сборка `core` идёт в каждом слоте. Значит, у CBMC остаётся около 145 с wall, и предел VT 120 с жёстче. Все семь слотов отсечены в фазе `cbmc` (exit −15).

| Слот | CBMC wall | Symex | Steps | Первая CNF (vars / clauses) | Решения завершены | Остаток последнего solve | CBMC / group peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stable_char_n09 OFF | 144,7 | 1,9 | 69 366 | 403 953 / 1 124 783 | 2 (4,7 + 0,03 с) | ≥ 137,6 | 0,80 / 1,97 GiB |
| stable_char_n09 ON | 142,8 | 6,2 | 256 299 | 1 077 789 / 4 492 478 | ≥ 6 (первое 27,9 с) | ≤ 92,4 | 2,43 / 2,44 GiB |
| stable_char_n09_corrupt OFF | 144,4 | 2,0 | 69 492 | 404 505 / 1 125 382 | 2 (5,0 с) | ≥ 137,0 | 0,80 / 1,97 GiB |
| stable_char_n09_corrupt ON | 142,8 | 6,3 | 256 851 | 1 079 058 / 4 508 536 | ≥ 6 (первое 27,8 с) | ≤ 92,6 | 2,44 / 2,45 GiB |
| sort8_char_n08 OFF | 145,0 | 1,5 | 60 589 | 314 258 / 760 512 | 2 (1,5 с) | ≥ 141,6 | 0,43 / 1,96 GiB |
| sort8_char_n08 ON | 144,6 | 5,0 | 215 778 | 841 828 / 3 113 491 | ≥ 6 (первое 14,7 с) | ≤ 117,4 | 1,35 / 2,08 GiB |
| network_nonzero_n19 OFF | 145,2 | **37,2** | 269 160 | 1 063 935 / 1 966 971 | 3 (1,6 + 4,0 с) | ≥ 101,1 | 1,36 / 1,97 GiB |

Пояснения к таблице:
- Остаток = CBMC wall − symex − SSA − сумма завершённых решений.
- В ON маркеры обрезаны bounded publish (`markers_omitted` 12–36), поэтому число решений занижено, а остаток — верхняя граница.
- Эффективный cap RSS — 4 GiB. Память не была ограничителем.

Выводы:
- **Время уходит в финальный UNSAT по функциональной проверке, а не в symex или кодирование.** В OFF первый solve за 1,5–5 с находит модели для covers, следующий удовлетворяет оставшиеся, а последний доказывает недостижимость нарушений сортированности и multiset над 32-битными `char`. Его не хватает 137–142 с.
- `check_sorted_and_full_multiset` даёт N − 1 сравнение `<` и N² равенств на 32-битных ключах. Для n9 это 8 + 81 на выходе после реального маршрута.
- Меньшее N само по себе не спасает: `sort8_char_n08` — уже минимальный отдельный `sort8` (8 элементов, без stable-обвязки), и он упал так же.
- В ON добавляется инструментирование. CNF больше в 2,7–3,6 раза по переменным и в 4,0 раза по клаузам, первый solve 15–28 с.
- **Отрицательному контролю функциональная проверка не нужна.** Его смысл — сбой на типизированном чтении после реального маршрута. Сейчас `stable_char_n09_body::<true>` делает полную проверку (`validity_main.rs:88`) до порчи, и именно она держит слот.
- **Ранговый домен.** Компаратор `char_less` — чистый total order, маршруты видят только его ответы и переносят байты целиком. Поэтому поведение на любом входе совпадает с поведением на его ранговом образе. N значений `< N` покрывают все слабые порядки длины N, включая равенства. Это тот же аргумент, что в пункте 5 [ревью-входа 2026-11-23](PLAN-CH8-NEXT-REVIEW-INPUT-20261123.md), и Kani его не проверяет. Ограничение `kani::assume((c as u32) < N as u32)` на элементы `kani::any::<char>()` сохраняет тип и генерацию `char`, но сужает эффективную ширину ключа с 21 значимого бита до 4.
- **Network.** Merge-маршрут на нишевом типе в ON всегда обрезается (п. 2), а OFF n19 тратит 37 с на один symex. Положительный network-корень стоит перевести на no-merge длину: n10 = `sort9_optimal` + один `insert_tail` (`smallsort.rs:395-405`: ветка `region.len() >= 9`). Merge-путь лучше оставить отдельным ON-слотом с закреплённым unsupported.

**Оценка.** Сколько займёт ранговый UNSAT, по этим receipts честно оценить нельзя: каждый финальный solve в них не завершился. Ожидаю выигрыш на порядки, но это гипотеза. Если FIX5 снова даст TIMEOUT в положительных ON-слотах, следующий шаг — разделить корни на validity-only (без функциональной проверки) и функциональные OFF.

## 4. Предложение FIX5 (пакет не собирался)

### Fixture overlay (`validity_main.rs`)

- **Все чтения B** переводятся в форму фазы A. Указатель берётся отдельной строкой **до** порчи и до чтения: `let values_ptr = values.as_ptr();` … `let first = unsafe { *values_ptr };`. Тогда на строке чтения остаётся только пара `T` (`UntypedRead` + `DerefValidity`), без N проверок `[T; N]` от autoref `&values`.
  - Основание: в ON receipts на строке `*values.as_ptr()` есть N + 2 свойства, столбец 27 для `[T; N]` и столбец 26 для `T`: `vv_swap_bool_n02` `:54` — 2 + 2, `vv_fallback_nonzero_n03` `:70` — 3 + 2, `vv_network_nonzero_n19` `:179` — 19 + 2.
  - Для `vv_stable_char_n09_corrupt` ON на `:111` было бы 9 + 2, и порченный элемент провалил бы и свою проверку `[char; 9]`. Правило FIX4 «failure set = ровно пара `char`» дало бы MISMATCH.
- **`bool`.** `bool_less(a, b) = (*a as u8) < (*b as u8)`. `check_sorted_and_full_multiset` получает параметр `less: fn(&T, &T) -> bool` и сравнивает тем же порядком, что сортировка. Covers `vv_swap_bool_n02` переводятся на `u8`-ключи.
- **`char`.** Ранговый домен для `vv_stable_char_n09` (< 9), `vv_stable_char_n09_corrupt` (< 9) и `vv_sort8_char_n08` (< 8).
- **`vv_stable_char_n09_corrupt`** — без функциональной проверки: только covers, порча и чтение.
- **Network.** `vv_network_nonzero_n19` заменяется на `vv_network_nonzero_n10` (no-merge, ранги 1..=10) и `vv_network_nonzero_n18` (merge, только ON).

### Roster B (13 слотов)

| Корень | Режим | Ожидание | Гейт |
| --- | --- | --- | --- |
| `vv_swap_bool_n02` | OFF / ON | SUCCESS / SUCCESS | read structure `bool`, count 2 |
| `vv_fallback_nonzero_n03` | OFF / ON | SUCCESS / SUCCESS | read structure `num::nonzero::NonZero<u8>`, count 2 |
| `vv_stable_char_n09` | OFF / ON | SUCCESS / SUCCESS | read structure `char`, count 2 |
| `vv_stable_char_n09_corrupt` | OFF / ON | SUCCESS / **FAILURE** | ON: failure set = пара `char` на строке чтения |
| `vv_sort8_char_n08` | OFF / ON | SUCCESS / SUCCESS | read structure `char`, count 2 (столбец `:153`-формы) |
| `vv_network_nonzero_n10` | OFF / ON | SUCCESS / SUCCESS | read structure `NonZero<u8>`, count 2 |
| `vv_network_nonzero_n18` | ON | **UNSUPPORTED_PINNED** | см. ниже |

Худший случай — 13 × 195 с = 2535 с, а окно B — 2400 с (`phase-B.json`: 1249,9 → 3649,9). Варианты: расширить окно B на 195 с с переносом последующих дедлайнов или убрать `vv_sort8_char_n08` OFF (12 слотов). Рекомендую расширить окно: пара OFF/ON у `sort8` нужна как положительный контроль отдельного маршрута.

### Roster A (+8 слотов, standalone)

`bool_order_probe`, `bool_order_u8_control`, `array_elem_cast_nonzero`, `array_elem_cast_u8_control` — каждый OFF/ON, ожидания из пп. 1 и 2. Существующие 18 слотов не меняются, реплей 18/18 должен остаться байт-идентичным.

### Изменения гейта

1. **Новые классы ожидания.**
   - `ASSERTION_FAILURE_PINNED`: failure set = ровно одно assertion с закреплёнными файлом, строкой, столбцом, функцией и описанием; covers SATISFIED; terminal FAILED; exit 1. Для `bool_order_probe`.
   - `UNSUPPORTED_PINNED`: failure set = ровно одно `unsupported_construct` с закреплёнными описанием и типом, координатой (`smallsort.rs:423:28`; для fixture — строка приведения) и префиксом функции (`small_sort_network::<num::nonzero::NonZero<u8>`). Все прочие `unsupported_construct` — только из установленных семейств и не FAILURE. Закреплённый пост-cast cover обязан быть UNREACHABLE. Terminal FAILED, exit 1. Такой слот даёт `MATCH_KNOWN_LIMITATION`, а не validity-кредит.
2. **Общее правило unsupported** не ослабляется: FAILURE у `unsupported_construct` допустим только в слотах `UNSUPPORTED_PINNED` и только для закреплённого свойства.
3. **`read_structures` для всех корней B.** Тип описания задаётся точной строкой (`bool`, `char`, `num::nonzero::NonZero<u8>`). Строки и столбцы перепиновываются по новому тексту overlay, `check_coordinates` сверяет их в шаге `sources`. Для положительных слотов `read_binding` должен стать OBSERVED.
4. **Non-gating маркер** `cbmc_ignoring_warnings` (число и первая координата) в `native_metrics`.
5. **Часы.** Окно B +195 с (или 12 слотов, см. выше). Пределы слота 180 с cold wall и 120 с VT не меняются.
6. **Без изменений:** профиль CBMC (`--unwind`, `--no-self-loops-to-assumptions`, список запрещённых флагов FIX4), порядок решений FIX4, правило single/pinned/structural.

### Что FIX5 покажет при каждом исходе

- `bool_order_probe` FAILURE и `vv_swap_bool_n02` MATCH: механизм подтверждён, бага swap нет. Готовим upstream-текст для Kani: приводить операнды `c_bool` к `unsignedbv` перед `Lt`/`Le`/`Gt`/`Ge`/`Cmp`.
- `bool_order_probe` SUCCESS, а `vv_swap_bool_n02` снова FAILURE: гипотеза неверна. Нужен отдельный диагностический пакет (swap `bool`/`u8`/`[u8; 1]`, трасса).
- Char-слоты снова в TIMEOUT: разделить validity-only и функциональные корни (см. п. 3).
