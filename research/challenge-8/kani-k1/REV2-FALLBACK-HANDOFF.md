# REV2 · fallback · передача воркера 11

`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`

Статический admission после FIX относится к трём строкам первого диагностического roster. Нативные discovery, binding, свойства, covers, resolved unwind и замеры имеют статус `UNKNOWN`. [FIX](REV2-FALLBACK-IMPL-TASK.md#fix-после-первого-ревью) · [Первое независимое ревью](REV2-FALLBACK-REVIEW.md)

## Исходники

| Поле | Значение для каждой строки roster |
| --- | --- |
| Std worktree | `/root/verify-rust-std-rev2-fallback-w11` |
| Ветка | `work/rev2-fallback-w11` |
| Опубликованная база | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Tree базы | `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Первый кандидат и единственный parent FIX | `dfdc70f8ccce6365f88fa489968508fa326ec60f` |
| Tree первого кандидата | `9f967855a6e6b71a7f81ecbc81e45a4d388443aa` |
| Локальный source commit FIX | `fb82da3c788c0e705cd598abee723200c0f28c42` |
| Tree source FIX | `4329b593bdb0d4f3972452648396170f94adea8e` |
| Cfg | `kani` и `kani_smallsort_fallback_rev2`. Второй флаг включает новый модуль и расширение модели Cell |

Diff FIX и полный diff доступны в общем Git object store. Оба source-коммита и коммит handoff имеют маркер `[skip ci]` и автора `Tiramisu-Cake <igkharin@gmail.com>`.

```sh
git -C /root/verify-rust-std-rev2-fallback-w11 diff dfdc70f8ccce6365f88fa489968508fa326ec60f fb82da3c788c0e705cd598abee723200c0f28c42
git -C /root/verify-rust-std-rev2-fallback-w11 diff dab03cf510df5c35141cde49f1368b1242f5035e fb82da3c788c0e705cd598abee723200c0f28c42
```

FIX меняет только `fallback_rev2.rs`. Все 20 примитивных корней используют опубликованные `merge::lt_u8` и `merge::lt_u64` для сортировки, oracle и covers порядка. Отношение порядка совпадает с опубликованными N0–N6 и определяется ключом `value >> 1`. Полные значения сохраняются в произвольных входах, счётчиках кратностей и cover дубликатов. Cell сохраняет числовой порядок байтов в Check и covers. Полный diff от базы также включает opt-in cfg в `verify.rs` и `library/core/Cargo.toml`, opt-in снимок и post в `trait_model.rs` и видимость существующего oracle в `merge.rs`. [Опубликованные компараторы](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:114) · [Вызовы и covers примитивов](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs:69)

## Exact selectors

| Selector | Диагностический roster |
| --- | --- |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n05` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n06` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n07` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n08` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n09` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n10` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n11` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n12` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n13` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n14` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n15` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::cell_unstable_n16` | **Первый** |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n07` | **Первый** |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n08` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n09` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n10` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n11` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n12` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n13` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n14` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n15` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u8_n16` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n07` | **Первый** |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n08` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n09` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n10` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n11` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n12` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n13` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n14` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n15` | — |
| `slice::sort::shared::smallsort::verify::fallback_rev2::u64_n16` | — |

Во всех длинах общие return covers — `sorted input returns`, `strictly descending input returns`, `duplicate input returns` и `fallback useful return`. В таблице указаны порядок для первых двух covers и дополнительный cover каждого семейства. Дубликат всегда означает равенство полных значений.

| Все длины семейства | T/F | Порядок в covers | Дополнительный cover |
| --- | --- | --- | --- |
| `cell_unstable_n05`–`cell_unstable_n16` | `Cell<u8>` / `CellCmp` со значением `canonical_less_cell` | Числовой `<` по логическому байту сохранённого входа | `sort model enabled before call` перед Check |
| `u8_n07`–`u8_n16` | `u8` / function item `merge::lt_u8` | `<` по ключу `value >> 1` | `distinct inputs with equal keys return` |
| `u64_n07`–`u64_n16` | `u64` / function item `merge::lt_u64` | `<` по ключу `value >> 1` | `distinct inputs with equal keys return` |

## Карта первого roster

Путь `smallsort.rs` отсчитывается от `library/core/src/slice/sort/shared/`. `fallback_rev2.rs`, `trait_model.rs` и `merge.rs` находятся в `smallsort/verify/`. Номера строк относятся к source tree из таблицы выше. Во всех трёх строках `small_sort_fallback` выбирает `insertion_sort_shift_left(v, 1, ...)` при `N >= 2`. Цикл идёт по tail offsets `1..=N−1` от начала **активного среза** и вызывает настоящий `insert_tail`. В ветке сдвига `CopyOnDrop::drop` заполняет последний разрыв через `copy_nonoverlapping`. [Fallback](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:255) · [Shift loop](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:718) · [Insert tail](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:661) · [Drop](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:357)

| Роль | `cell_unstable_n16` | `u8_n07` | `u64_n07` |
| --- | --- | --- | --- |
| T/F | `Cell<u8>` / `CellCmp = fn(&Cell<u8>, &Cell<u8>) -> bool` со значением `canonical_less_cell` (`trait_model.rs:16,27`) | `u8` / function item `merge::lt_u8` (`merge.rs:116–118`) | `u64` / function item `merge::lt_u64` (`merge.rs:124–126`) |
| N и backing | 16 из `[Cell<u8>; 34]`, `backing[1..17]`, base 1, 34 независимых байта инициализируют каждый слот (`fallback_rev2.rs:31–36,67`) | 7 из `[u8; 7]`, весь initialized backing, base 0 (`fallback_rev2.rs:73–76,100`) | 7 из `[u64; 7]`, весь initialized backing, base 0 (`fallback_rev2.rs:73–76,110`) |
| Режим и вызов | Check `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort` (`fallback_rev2.rs:28,45`) → default Unstable (`smallsort.rs:95,111–116`) → fallback → shift → insert tail → Drop на ветке сдвига | Original `kani::proof` (`fallback_rev2.rs:90–100`) → `primitive_fallback::<u8, _, 7>` → прямой fallback (`fallback_rev2.rs:76`) → shift → insert tail → Drop на ветке сдвига | Original `kani::proof` (`fallback_rev2.rs:90–98,110`) → `primitive_fallback::<u64, _, 7>` → прямой fallback (`fallback_rev2.rs:76`) → shift → insert tail → Drop на ветке сдвига |
| Порядок | Сравнение соседей по полному логическому байту (`trait_model.rs:130–134`) внутри post | `output is sorted` (`merge.rs:347–348`), `<` по ключу `u8 >> 1` | `output is sorted` (`merge.rs:347–348`), `<` по ключу `u64 >> 1` |
| Кратности | `old` сохраняет собственные значения. Проверки диапазона и снимок (`trait_model.rs:7–13,42–49,187–197`), одинаковая длина и детерминированные счётчики для каждого исходного значения (`trait_model.rs:125–148,206–212`) | `input value counts are preserved` (`merge.rs:350–353`). Независимый probe до вызова (`fallback_rev2.rs:73`), равенство полного `u8` (`merge.rs:24–71,91–105`) | Та же проверка. `matches_value_probe` сравнивает все 8 байт одним `read_unaligned` слова `u64` (`merge.rs:24–71,91–105`) |
| Внешний frame | `outside slice unchanged` (`fallback_rev2.rs:46–49`), через `Cell::get` для слотов 0 и 17–33 | Active занимает всю `[u8; 7]`. За её пределами действуют штатные pointer/bounds checks (`smallsort.rs:661–695,718–727,357–363`) | Active занимает всю `[u64; 7]`. За её пределами действуют те же pointer/bounds checks |
| Активация | Unstable, N5–16 и точное значение fn pointer (`trait_model.rs:176–184`). Assertion и cover `sort model enabled before call` до вызова (`fallback_rev2.rs:37–45`) | Original вызывает helper напрямую, guard trait модели отсутствует | Original вызывает helper напрямую, guard trait модели отсутствует |
| `ensures` и write set | `old(enabled(Unstable, …))` и `old(snapshot(…))` в собственном `ensures` default Unstable, `modifies(v)` (`smallsort.rs:101–109`). Нативная проекция должна подтвердить активный post и DFCC | Прямой `small_sort_fallback` (`smallsort.rs:255–259`) без контракта. Здесь действуют прямые assertions и штатные проверки тела. Trait `ensures` и DFCC trait write set не имеют роли в этой строке | Тот же Original helper и та же область применимости |
| Covers возврата | Четыре общих cover с числовым `<` на байтах (`fallback_rev2.rs:8–24,51`), плюс активация в строке 44 | Четыре общих cover с `merge::lt_u8` для порядка (`fallback_rev2.rs:8–24,78`) и cover пары разных значений с равным ключом (`fallback_rev2.rs:80–87`) | Четыре общих cover с `merge::lt_u64` для порядка (`fallback_rev2.rs:8–24,78`) и тот же отдельный cover равного ключа (`fallback_rev2.rs:80–87`) |
| Стартовый unwind | `36` (`fallback_rev2.rs:29`) | `34` (`fallback_rev2.rs:93`) | `34` (`fallback_rev2.rs:93`) |

`Cell<u8>` использует default Unstable из-за `!Freeze`. Снимок читает `0..len` от указателя активного среза после проверки длины. Совпадение кратностей всех исходных байтов при совпадающей длине исчерпывает длину результата. Pre и post обходятся без недетерминированного probe и без вызова компаратора. Три компаратора только читают аргументы. Для примитивов весь инициализированный массив и независимый probe квантифицируются через отдельные `kani::any()`. При проверке кратностей сравниваются полные значения. `u8` и `u64` в Unstable trait dispatch удовлетворяют `FreezeMarker + CopyMarker` и условию сети (`size_of::<T>() <= 8` и `size_of::<T>() * 32 <= 4096`). В Stable у них специализация `FreezeMarker` с `small_sort_general_with_scratch`. [Default и Freeze](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:95) · [Freeze + Copy](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:189) · [Stable Freeze](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:60)

Входные классы определены по сохранённому входу и покрываются после полезного возврата. На неубывающем входе по своему компаратору каждый tail проходит ранний возврат в `insert_tail` (строки 665–668). При строго убывающем входе по тому же компаратору каждый новый tail меньше всего отсортированного префикса, поэтому сдвиг достигает `begin` (строки 678–692), а `Drop` закрывает разрыв. Cover дубликатов требует любую равную пару полных значений и допускает, например, константный массив. [Общие условия covers](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs:8)

Дополнительный primitive cover ищет любую пару `a != b`, для которой `cmp(a, b)` и `cmp(b, a)` обе ложны. Например, начало `[1, 0, 2, 4, …]` имеет неубывающие ключи, и первая хвостовая вставка возвращается сразу на равном ключе `1 >> 1 == 0 >> 1`. При сравнении `u64` биты 1–63 участвуют через ключ, а все 64 бита участвуют в равенстве полных значений и кратностях. То же различие ключа и полного значения действует для `u8`. Будущая проекция связывает пять return covers каждого примитивного корня и четыре Cell covers со своими exact селекторами. [Cover равного ключа](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/fallback_rev2.rs:80)

Cell N16 воспроизводит геометрию V34/base1 и берёт верхнюю границу fallback. Исторический S4 использовал вызов helper с `KeyLess<Cell<u8>>`; здесь вход в Check идёт через default Unstable с `CellCmp`. Два N7 начинают новые примитивные диапазоны с одинаковой длины. Остальные 29 строк подготовлены для последующего отбора. [S4 N0–N4](kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md) · [Верхняя граница S4](kani3300/ch8-s4/s4-full-lengths-next-plan/LOOP-COST.md)

## Границы циклов и область проверки

| Цикл по исходнику | Cell N16, максимум тел | Каждый примитив N7, максимум тел |
| --- | ---: | ---: |
| Инициализация Cell и отдельный внешний frame, каждый | 34 | — |
| Снимок `old` и отдельный снимок результата, каждый | 16 | — |
| Проверка соседнего порядка | 15 | 6 |
| Счётчики Cell, внешний цикл и отдельный внутренний цикл | 16 / 16 | Oracle содержит 32 развёрнутых позиции без цикла, из них N активны |
| Входные классы, смежные пары и внутренний поиск равного элемента | 15 / 15 | 6 / 6 |
| Отдельный cover разных значений с равным ключом, внешний и внутренний циклы | — | 6 / 6 |
| `insertion_sort_shift_left` и наибольший `insert_tail` | 15 / 15 | 6 / 6 |

Для tail со смещением `p` первое сравнение и до `p−1` последующих дают максимум `p` сравнений. N16 имеет 15 хвостовых вставок и сумму `1 + … + 15 = 120`, N7 имеет 6 вставок и сумму 21. Границы относятся к работе исходного алгоритма. Стартовые 36 оставляют запас над циклами длины 34, а 34 следуют опубликованной схеме oracle до 32 позиций и превышают явные циклы примитивов до N16. В обоих случаях будущий запуск должен подтвердить resolved unwind, успешные unwinding assertions, reachability и штатные safety, overflow и bounds. Преобразования компилятора, `Arbitrary`, memory predicates и DFCC требуют нативной сверки. В новых корнях отсутствуют ordinary/verified stubs. [Опубликованная схема unwind](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:537)

- Stable default `Cell` идёт напрямую в `insertion_sort_shift_left(v, 1, ...)` через отдельный `ensures` и `modifies(v)`. Он принимает caller scratch, которую тело игнорирует. Для этой ветви нужен отдельный Check с активацией Stable на целевой длине, внешним frame и проверкой frame scratch на инициализированных sentinel-значениях. Текущий guard Stable поддерживает действующий N2. [Stable default](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:32) · [Короткий Check со scratch](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:164)
- Большой `Freeze` в default Freeze-type выбирает fallback при `size_of::<T>() * SMALL_SORT_GENERAL_SCRATCH_LEN > MAX_STACK_ARRAY_SIZE`, то есть `size_of::<T>() * 48 > 4096`. Для специализации `FreezeMarker + CopyMarker` также должен быть ложным первый сетевой предикат `has_efficient_in_place_swap::<T>() && size_of::<T>() * 32 <= 4096`. Full-value домен большого типа пока не подготовлен. [Freeze fallback](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:171) · [Copy dispatch](/root/verify-rust-std-rev2-fallback-w11/library/core/src/slice/sort/shared/smallsort.rs:213)
- Вне трёх строк остаются отдельная вставка с другим offset, паника, стабильность равных payload, generic `T/F`, uninit/validity и права записи immutable bytes.

## Предложение для будущего диагностического запуска

Три exact singleton последовательно на Ubuntu в порядке таблицы. Один stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, stock CBMC 6.11.0 и CaDiCaL. Семантические флаги штатного CAL2 профиля перечислены ниже. Очистить наследуемые `RUSTFLAGS` и `CARGO_ENCODED_RUSTFLAGS`, задать только `RUSTFLAGS=--cfg=kani_smallsort_fallback_rev2` для новых корней. У каждого selector свои свежие cwd, Cargo/Kani target, output и JSON export. Uninit и validity OFF. [Профиль CAL2](CAL2-HANDOFF.md#геометрия-и-профиль)

```text
verify-std -Z unstable-options -Z function-contracts -Z mem-predicates
  -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing
  --no-assert-contracts --harness <exact-selector> --exact --jobs=1
  --output-format=regular -Z export-json --export-json <root-export>
  --verbose --target-dir <root-target> <std>/library --cbmc-args --object-bits 12
```

Предложенный внешний потолок на singleton — 600 с cold wall и 6 GiB (6 291 456 KiB) sampled group RSS с резервом 2 GiB (2 097 152 KiB). Записать номинальный и effective cap после учёта available и резерва. Cold wall включает compile, verification и выдачу результатов. Сохранить отдельно VT, пик группы с фазой и временем сэмпла, exit/reap, причину и фазу отсечки с пометкой censoring и число CNF variables/clauses с источником при наличии. Ориентиры **120 с VT** и **4 GiB на новый корень** диагностические. Исход и пригодность по ресурсам открыты. [Рабочие ориентиры](CAL2-RESULTS-ANALYSIS.md#материал-к-решению-о-лимитах-и-следующий-шаг-rev2)

## Данные будущей приёмки

1. Привязать run/attempt и запрос к точным base/source/tool SHA и tree, stock зависимостям, argv/env, cfg, selector, результату discovery, OB12, jobs и resolved unwind. Требуется ровно одна exact регистрация на singleton с cfg on, а список с cfg off должен исключать новые регистрации. Сохранить данные о завершении и ресурсах. Для Cloud Build использовать Evidence Brief и сохранить координаты сопоставленных записей.
2. Сверить полный regular `RESULTS`/`SUMMARY`, stock export и terminal exit. Сохранить native ID, ordinal, class, полное описание, location и status, включая успешно выполненные assertions, safety, overflow, bounds, unwind, reachability и все covers. Привязать роли из карты к фактическим строкам, включая оба primitive oracle assertions, пять covers возврата на каждый примитив и четыре covers возврата плюс активацию для Cell. Сопоставлять свойства по источнику и роли, поскольку сообщения `assert!` могут иметь общее описание. Фиксировать пропуски, неоднозначность, ошибки и отсечки.
3. В Cell Check соединить `attributes.kind.target_fn`, непустое `contract.contracted_function_name`, вызов `goto-instrument --enforce-contract` и проекцию той же подготовленной программы, которую проверил solver. Подтвердить `F = CellCmp` со значением `canonical_less_cell`, binding к default Unstable, активный `old(enabled)`, снимок и post `ensures`, DFCC `modifies(v)`, явный внешний frame и реальный путь до `insert_tail`/`CopyOnDrop` на ветке сдвига. Для примитивов нужны Original helper и полные свойства тела по карте.
4. Оставить ненайденную или непривязанную обязательную роль `UNKNOWN`. Исторический допуск S4 N0–N4 и его исключение для missing location ограничены тем запуском. Раздельно зафиксировать три результата. На остальные 29 корней их область не распространяется. [Нативная приёмка и binding](pr752-trait-contracts-20261122/BINDING-CHECK-PLAN.md#offline-acceptance) · [Границы S4](kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md)

## Локальные проверки

`git diff --check` и статическая сверка ниже прошли. Сверка проверяет цепочку source-коммитов, неизменность 32 деклараций и точной тройки, литералы `N`, типы, опубликованные function items и передачу одного компаратора в сортировку, oracle и covers порядка. Отдельно сверены cover равного ключа и сохранение числового порядка в covers Cell. FIX ограничен одним файлом. Полный diff содержит пять ожидаемых файлов. Восстановлена токенная проекция исходной модели при cfg off и проверены два уровня cfg. Байт-в-байт сверены `smallsort.rs`, действующие атрибуты контрактов, штатные harnesses, профиль, tool pin и workflow. Для `merge.rs` сравнение с базой исключает только видимость существующего oracle. Стадия выполнена локально через Git и Python. Native inventory, компиляция и верификация остаются открыты.

```sh
python3 -B - <<'PY'
from collections import Counter
from pathlib import Path
import re
import subprocess

std = Path('/root/verify-rust-std-rev2-fallback-w11')
g0 = Path('/root/verify-rust-std-kani3300-g0')
report = (g0 / 'research/challenge-8/kani-k1/REV2-FALLBACK-HANDOFF.md').read_text()
base, base_tree, previous, previous_tree, source, source_tree = re.findall(r'\| `([a-f0-9]{40})` \|', report)[:6]
cfg = 'kani_smallsort_fallback_rev2'
prefix = 'slice::sort::shared::smallsort::verify::fallback_rev2::'
kernel = 'library/core/src/slice/sort/shared/smallsort'
verify = f'{kernel}/verify'
new = f'{verify}/fallback_rev2.rs'

def git(*args):
    return subprocess.check_output(['git', '-C', str(std), *args], text=True)

def blob(rev, path):
    return git('show', f'{rev}:{path}')

assert git('rev-list', '--parents', '-n1', source).split() == [source, previous]
assert git('rev-list', '--parents', '-n1', previous).split() == [previous, base]
for rev, tree in ((base, base_tree), (previous, previous_tree), (source, source_tree)):
    assert git('rev-parse', f'{rev}^{{tree}}').strip() == tree
assert git('diff', '--name-only', previous, source).splitlines() == [new]
assert set(git('diff', '--name-only', base, source).splitlines()) == {
    'library/core/Cargo.toml', f'{kernel}/verify.rs', new,
    f'{verify}/merge.rs', f'{verify}/trait_model.rs',
}
git('diff', '--check', base, source)
git('diff', '--check', previous, source)

roots = blob(source, new)
old_roots = blob(previous, new)
decl = re.compile(r'^(?:cell|primitive)_harness!.*$', re.M)
assert decl.findall(roots) == decl.findall(old_roots)
cell_rows = re.findall(r'^cell_harness!\((\w+), (\d+)\);$', roots, re.M)
primitive_rows = re.findall(r'^primitive_harness!\((\w+), (\w+), (\w+), (\d+)\);$', roots, re.M)
assert len(re.findall(r'\bcell_harness\s*!', roots)) == len(cell_rows)
assert len(re.findall(r'\bprimitive_harness\s*!', roots)) == len(primitive_rows)
assert Counter(cell_rows) == Counter((f'cell_unstable_n{n:02}', str(n)) for n in range(5, 17))
assert Counter(primitive_rows) == Counter(
    (f'{ty}_n{n:02}', ty, f'lt_{ty}', str(n)) for ty in ('u8', 'u64') for n in range(7, 17)
)
assert [int(n) for n in re.findall(r'#\[kani::unwind\((\d+)\)\]', roots)] == [36, 34]
assert '#[kani::proof_for_contract(<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort)]' in roots
assert roots.count('#[kani::proof') == 2 and '#[kani::proof]' in roots
assert 'primitive_fallback::<$ty, _, $n>($cmp);' in roots and 'backing[1..$n + 1]' in roots
cell_code = re.compile(r'^macro_rules! cell_harness \{\n.*?^\}', re.M | re.S)
cell_before = 'cover_input_classes(&input[1..$n + 1]);'
cell_after = 'cover_input_classes(&input[1..$n + 1], |a, b| a < b);'
assert cell_before in cell_code.search(old_roots)[0]
assert cell_code.search(roots)[0] == cell_code.search(old_roots)[0].replace(cell_before, cell_after)
assert not re.search(r'^fn lt_u(?:8|64)\(', roots, re.M)
assert 'use super::merge::{assert_sorted_and_probe_preserved, lt_u8, lt_u64, set_value_probe};' in roots
flow = (
    'set_value_probe::<T>();', 'let mut active: [T; N] = kani::any();',
    'let input = active;', 'small_sort_fallback(&mut active, &mut cmp);',
    'assert_sorted_and_probe_preserved(&input, &active, &mut cmp);',
    'cover_input_classes(&input, &mut cmp);',
    'distinct_equal_keys |= a != b && !cmp(a, b) && !cmp(b, a);',
    'kani::cover(distinct_equal_keys, "distinct inputs with equal keys return");',
)
offsets = [roots.index(item) for item in flow]
assert offsets == sorted(offsets)
assert 'let decreases = is_less(&input[i], &input[i - 1]);' in roots
assert 'sorted &= !decreases;' in roots and 'descending &= decreases;' in roots
assert 'duplicate |= input[j] == input[i];' in roots
assert not re.search(r'kani::(?:assume|any_where|stub|stub_verified)\b', roots)
table = re.findall(r'^\| `' + re.escape(prefix) + r'(\w+)` \| (\*\*Первый\*\*|—) \|$', report, re.M)
assert report.count('`' + prefix) == len(table)
assert Counter(name for name, _ in table) == Counter(row[0] for row in cell_rows + primitive_rows)
assert [name for name, mark in table if mark == '**Первый**'] == ['cell_unstable_n16', 'u8_n07', 'u64_n07']

module = f'{kernel}/verify.rs'
gate = f'#[cfg({cfg})]\nmod fallback_rev2;\n'
module_source = blob(source, module)
assert module_source.count(gate) == 1 and module_source.replace(gate, '') == blob(base, module)
assert '#[cfg(kani)]\n#[unstable(feature = "kani", issue = "none")]\nmod verify;' in blob(source, f'{kernel}.rs')
cargo = 'library/core/Cargo.toml'
lint = f"    'cfg({cfg})',\n"
assert blob(source, cargo).count(lint) == 1 and blob(source, cargo).replace(lint, '') == blob(base, cargo)
merge = f'{verify}/merge.rs'
published = blob(source, merge)
for ty in ('u8', 'u64'):
    assert f'fn lt_{ty}(a: &{ty}, b: &{ty}) -> bool {{\n    (*a >> 1) < (*b >> 1)\n}}' in published
assert published.replace('pub(super) fn assert_sorted_and_probe_preserved',
                         'fn assert_sorted_and_probe_preserved', 1) == blob(base, merge)

# Project only the new cfg constructs, then compare the remaining model tokens.
model = f'{verify}/trait_model.rs'
cfg_item = re.compile(r'^([ ]*)#\[cfg\(' + cfg + r'\)\]\n\1'
                      r'(?:(?:const|cell_vals:) [^\n]+\n|(?:fn|if) [^\n]+\{\n.*?^\1\}\n)', re.M | re.S)
model_off, removed = cfg_item.subn('', blob(source, model))
def normalized(text):
    return re.sub(r'\s+', '', text).replace(',}', '}')

assert removed == 9 and normalized(model_off) == normalized(blob(base, model))
print('PASS: 32 exact declarations, three roster rows, comparator/cover flow, cfg-off source projection, pinned FIX')
PY
```

Пакет передаётся отдельному ревьюеру. Для независимой сверки подготовлены все литеральные длины, три строки admission, dispatch, компараторы, кратности и cfg isolation. CI, push, trigger, ledger и CAL2 macOS/control находятся вне этой стадии.
