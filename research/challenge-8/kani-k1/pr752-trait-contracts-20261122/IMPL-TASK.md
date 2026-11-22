# #752. Задание воркеру на прямые контракты `small_sort`

В отдельном std worktree подготовить локальный кандидат поверх `5402b33188d51d4c30e1302af710a27c7a60d831` (tree `7ad88a0e11e10ab253f1140ac6701cd95f3e5fc2`). Tool pin `9834c96ce90ff57d8495416530b080dc3d52ce25`. Исходная форма модели, harnesses и атрибутов зафиксирована в G3 `70ba5befc617627073738e26cb1466bd4fb76e41`. На базе перенести смысловую дельту вручную. [Бриф](COORDINATOR-BRIEF.md) · [Патч G3](/root/verify-rust-std-kani3300-gateb-prime/research/challenge-8/kani-k1/traitpfc/g3/build2/library.patch) · [Атрибуты G3](/root/verify-rust-std-kani3300-gateb-prime/research/challenge-8/kani-k1/traitpfc/g3/build2/contracts.json)

## Код и границы

- В `library/core/src/slice/sort/shared/smallsort.rs` аннотировать шесть **impl methods** `small_sort`. Поставить `#[cfg_attr(kani, ...)]` также на каждую существующую `default fn`. Сохранить trait declarations, сигнатуры, specialization, тела, threshold и все имеющиеся аннотации базы. Из G3 перенести Kani-модель и footprint. Унаследованные от экспериментальной базы G3 дополнительные `#[safety::requires]` на trait methods сюда не переносить. Существующие helper/forwarding contracts, harnesses, controls, tool pin и workflow сохранить.
- Для каждого impl — один `ensures` в форме `!old(enabled(entry, is_less, v.len())) || sort_postcondition(old(snapshot(v.as_ptr(), v.len())), v.as_ptr(), v.len())`. Захватить by-value bool и `Clone + Copy` снимок; `old` без ссылки на `&mut` после вызова. Условие домена на входе проверяется через отдельные assert и cover у каждого positive. Один общий `SortModel<T,F>` с закрытыми специализациями, в generic fallback `enabled=false` и безопасный снимок без чтений. `old` может вычислять снимок независимо от short circuit, поэтому snapshot читает только поддерживаемый размер initialized `v` и никогда scratch. Проверка использует чистый логический порядок и полные кратности без вызова компаратора.
- Сохранить `u64` и точный canonical read-only `fn(&u64, &u64) -> bool` для всех трёх специализированных методов при N2 и N3. Добавить exact специализации для `Cell<u8>` и приватного `NonCopyKey(u8)` под `cfg(kani)`. У `Cell` модель включена только для Stable/Unstable на N2 с конкретным read-only fn pointer, проекция `Cell::get`. У `NonCopyKey` модель включена только для Freeze на N2 с конкретным read-only fn pointer, проекция полного байта. `NonCopyKey` без `Copy`, внутренней мутабельности и пользовательского `Drop`. Явно типизировать fn pointers в roots. Возврат true от cmp означает числовое `<` для целого логического значения. Guard связывает точный тип и каноническую функцию лишь в данном proof domain.
- `modifies(v)` у Stable default, обеих реализаций Unstable и обеих реализаций Freeze. `modifies(v, scratch)` только у Stable specialized. Для footprint учитывать `FnMut` с ровно тем read-only callback, что в harness. `stub_verified` в ordinary только на паре доказанных `u64` Freeze calls с совпадающей геометрией. Scratch Stable specialized отдельный `MaybeUninit`, размер `N+16`. Stable default имеет отдельный scratch из двух слотов с произвольным initialized sentinel и uninit tail. Проверить sentinel после вызова без чтения tail.
- Обновить карту и bounded Limitations в `smallsort/verify.rs` и добавить `verify/trait_model.rs`, `verify/trait_contracts.rs`. Зафиксировать exact тип, компаратор, длину, specialized/default, normal return и геометрию для каждого вывода. Неподдержанные типы, `FnMut` с эффектами, произвольные длины, stability для различимых равных ключей, unwind и ранее перечисленные UB-классы остаются за границей новых claims.

## Обычные harnesses

Prefix `slice::sort::shared::smallsort::verify::trait_contracts::`. Точные UFCS targets `<T as Trait>::small_sort` в `proof_for_contract`, совпадающий вызов из fixture и inference `F` от explicit comparator type. Проверять actual impl, а не forwarding contract из соседнего модуля. Во всех десяти roots ожидаются SUCCESS и пять covers — enabled, ascending, descending, duplicate и normal return. Входные значения произвольные на полной ширине. У interior fixtures сравнить оба внешних canary. `unwind(32)` по G3, тот же профиль организаторов. Пояснить, почему развёртка достаточна для новых N2 roots.

| Root suffix | Exact тип и реализация | Fixture и stubs | VT, с |
| --- | --- | --- | ---: |
| `stable_sorts_permutation_u64_len2` | Stable specialized Check, u64 | N2, scratch 18, actual | 112 |
| `stable_sorts_permutation_u64_len3` | Stable specialized Check, u64 | N3, scratch 19, actual | 170 |
| `freeze_sorts_permutation_u64_backing4` | Freeze Copy-specialized Check, u64 | `backing[1..3]`, actual network entry | 29 |
| `freeze_sorts_permutation_u64_backing5` | Freeze Copy-specialized Check, u64 | `backing[1..4]`, actual network entry | 68 |
| `unstable_sorts_permutation_u64_backing4` | Unstable Freeze-specialized Check, u64 | `backing[1..3]`, только matched Freeze Replace N2 | 83 |
| `unstable_sorts_permutation_u64_backing5` | Unstable Freeze-specialized Check, u64 | `backing[1..4]`, только matched Freeze Replace N3 | 128 |
| `verified_forwarding_sorts_permutation_u64_backing5` | Plain, real Unstable entry, u64 | `backing[1..4]`, matched Freeze Replace N3, независимые sortedness, multiplicities и frame | 6 |
| `stable_default_sorts_permutation_cell_u8_backing4` | Stable default Check, `Cell<u8>` | `backing[1..3]`, actual insertion, отдельный scratch и frame | 15–60 |
| `unstable_default_sorts_permutation_cell_u8_backing4` | Unstable default Check, `Cell<u8>` | `backing[1..3]`, actual fallback, без stubs | 15–60 |
| `freeze_default_sorts_permutation_noncopy_u8_backing4` | Freeze default Check, `NonCopyKey` | `backing[1..3]`, actual general, private scratch, без stubs | 30–120 |

Первые семь VT — ориентиры по округлённым замерам G3 на старом пине, последние три — предварительные оценки. Для новых default rows зафиксировать выбор через `Cell<u8>: !Freeze` и Freeze/non-Copy свойства `NonCopyKey`. `size_of::<NonCopyKey>() * SMALL_SORT_GENERAL_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE` выбирает general. Сверить, что у actual Check нативно выполнены ensures и DFCC/frame на нужном теле с успешными unwind assertions. Общая ordinary дельта только эти десять имён, **235 → 245**. [Времена G3](/root/verify-rust-std-kani3300-gateb-prime/research/challenge-8/kani-k1/RESULT-TRAITPFC-G3.md)

## Opt-in контроли

`cfg(kani_smallsort_controls)` выключен в обычном CI. Перенести четыре negative roots и положительный function-item frame witness W1. Сохранить ожидаемые ID/class/location в handoff после удалённого прогона. Каждый негатив запускается exact и должен дать одну назначенную assertion FAILURE с cover достижимости порчи или guard-disabled пути. Контроли проверяют границы модели и не дают proof credit для unsupported T/F.

| Root suffix | Ожидаемый результат | Исторический VT, с |
| --- | --- | ---: |
| `rejects_high_bit_corruption_u64_len3` | `high-bit corruption preserves sorted full values`. Литеральный `[0,1,2]`, high bit включается у максимума, порядок сохраняется | 1,91 |
| `rejects_changed_multiplicities_u64_len3` | `same set preserves full multiplicities`. `[a,a,b]` → `[a,b,b]`, `a<b`, порядок сохраняется | 0,55 |
| `rejects_reverse_pointer_sorted_u64_backing5` | `reverse pointer output is sorted`. Assert guard off, диагностический Freeze Replace, проверить frame перед failing sortedness | 2,21 |
| `rejects_function_item_sorted_u64_backing5` | `function item output is sorted`. Не приводить item к pointer, guard через generic lookup helper G3, диагностический Freeze Replace, frame перед failing sortedness | 2,05 |
| `freeze_frame_function_item_u64_backing5` | SUCCESS, guard off, actual Freeze Check, outside frame и три W1 covers | 35,95 |

## Локальная сдача

Сдать один reviewable std commit с `[skip ci]`, SHA/tree/parent, списком изменённых файлов, таблицей impl → target → domain → footprint и evidence ожиданий для всех roots. Только статическая сверка (`git diff --check`, сравнение runtime, области исходников, expected inventory и selectors) и `/root/rustfmt-toolchains/bin/kani-fmt-check.sh <repo> <commit>` (`FMT_OK`). Локальные cargo/rustc/Kani/CBMC и локальное получение нативного списка harnesses запрещены. Если blocker относится к макросам или разрешению default impl, в handoff указать exact target и форму, сохранив эту развилку для удалённой проверки. Fork CI и GCB запускает координатор по отдельному GO. Push в `submission/ch8-smallsort` требует решения владельца. [GO и приёмка](PLAN.md#go-на-один-dispatch-fork-ci)
