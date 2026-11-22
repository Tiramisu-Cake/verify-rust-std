# #752. Локальный кандидат с прямыми контрактами SmallSort

| Поле | Значение |
| --- | --- |
| Worktree | `/root/verify-rust-std-pr752-trait-contracts` |
| Локальная ветка | `experiment/pr752-trait-contracts` |
| Кандидат | `152f11556ab19c6dcfa21b5a0f1096603530ce67` |
| Tree | `08c6c08235035dbca44715c4b4822f5c34c041f6` |
| Parent | `5402b33188d51d4c30e1302af710a27c7a60d831` |
| Parent tree | `7ad88a0e11e10ab253f1140ac6701cd95f3e5fc2` |
| Kani pin | `9834c96ce90ff57d8495416530b080dc3d52ce25` |
| Workflow и baseline | `.github/workflows/kani.yml`, run `44946596047`, 16 успешных jobs, 235 SmallSort roots, критический шард macOS partition 2 за 77 мин |
| Предложенный fork ref для отдельного GO | `Tiramisu-Cake/verify-rust-std:ci/ch8-pr752-trait-contracts-20261122`, expected head и tree как у кандидата |

Кандидат состоит из одного локального коммита с `[skip ci]`. Автор и коммитер — `Tiramisu-Cake <igkharin@gmail.com>`. Рабочее дерево чистое. Статус кандидата — исходники и формат проверены. Публикация предложенного ref, native compile, inventory и verifier evidence для этого SHA ожидают отдельного GO координатора.

## Исходники и локальная сверка

Изменены четыре файла относительно `library/core/src/slice/sort/shared/`.

- `smallsort.rs` добавляет шесть пар `cfg_attr(kani, ...)` непосредственно к impl methods.
- `smallsort/verify.rs` описывает границы гарантий и подключает два Kani-модуля.
- `smallsort/verify/trait_model.rs` задаёт закрытые специализации модели и проверяет порядок и кратности.
- `smallsort/verify/trait_contracts.rs` содержит десять обычных roots и пять opt-in roots.

`git diff --check` прошёл. После удаления шести новых блоков атрибутов `smallsort.rs` побайтно совпадает с базой, включая все тела, сигнатуры, объявления trait, specialization, thresholds и прежние атрибуты. Новых `safety::requires` нет. Существующие helper и forwarding modules, harnesses, controls, `tool_config/kani-version.toml`, `.github/workflows/kani.yml` и `scripts/run-kani.sh` сверены по Git. У прежних модулей сохраняется подключение с теми же cfg. Статическая сверка exact-имён и атрибутов даёт ожидаемую ordinary дельту SmallSort **235 → 245**. Из десяти добавленных имён семь совпали с исходным manifest G3, ещё три соответствуют default Check. Пять opt-in roots в этот набор не входят.

`/root/rustfmt-toolchains/bin/kani-fmt-check.sh` выдал **FMT_OK** для всех четырёх Rust-файлов кандидата. Первый прямой вызов дал `FMT_DIFF`, так как скрипт ищет `rustfmt.toml` в корне коммита и перешёл на настройки по умолчанию. Проверка с рабочей конфигурацией использовала тот же скрипт и SHA во временном Git-репозитории с локальным `git replace`. В дереве для проверки добавлен только `rustfmt.toml` из g0 `research/challenge-8/kani-k1/codefix/rustfmt.toml` (blob `1850dc92020011c4918146aa42cd002854a015b6`, конфигурация проверки G3). Сравнение деревьев подтвердило идентичность всех остальных файлов и тот же parent. Конфигурация отсутствует в сдаваемом дереве. Других локальных инструментов компиляции и верификации не запускали.

## Реализации, домены и write sets

В каждом impl один `ensures` с формой `!old(enabled(entry, is_less, v.len())) || sort_postcondition(old(snapshot(v.as_ptr(), v.len())), v.as_ptr(), v.len())`. В `old` захватываются значения `bool` и `SortSnapshot: Clone + Copy`. Generic fallback возвращает выключенный guard и снимок без чтений. Exact снимки проверяют длину до чтения и получают только initialized active slice, в том числе если `old(snapshot(...))` вычисляется при выключенном guard. `Cell::get` и поле `NonCopyKey.0` дают полный байт. Проверка использует числовой порядок и полные кратности значений. Она обходится без вызова компаратора.

| Impl в `smallsort.rs` | Exact Check target | Домен на normal return | Footprint |
| --- | --- | --- | --- |
| Stable `impl<T>`, default | `<Cell<u8> as StableSmallSortTypeImpl>::small_sort` | `CellCmp` / `canonical_less_cell`, N2, `backing[1..3]` из 4, insertion | `v`; отдельная caller scratch из 2 слотов, slot 0 с произвольным sentinel, slot 1 uninit |
| Stable `T: FreezeMarker`, specialized | `<u64 as StableSmallSortTypeImpl>::small_sort` | `U64Cmp` / `canonical_less_u64`, N2 и N3, отдельный весь массив, actual general | `v, scratch`; отдельная caller `MaybeUninit<u64>` scratch длиной N+16 |
| Unstable `impl<T>`, default | `<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort` | `CellCmp` / `canonical_less_cell`, N2, `backing[1..3]` из 4, actual fallback | `v` |
| Unstable `T: FreezeMarker`, specialized | `<u64 as UnstableSmallSortTypeImpl>::small_sort` | `U64Cmp` / `canonical_less_u64`, N2 и N3, `backing[1..N+1]` из N+2, actual forwarding с matched Freeze Replace | `v` |
| Freeze `T: FreezeMarker`, default | `<NonCopyKey as UnstableSmallSortFreezeTypeImpl>::small_sort` | `NonCopyCmp` / `canonical_less_noncopy`, N2, `backing[1..3]` из 4, actual general | `v`; private stack scratch |
| Freeze `T: FreezeMarker + CopyMarker`, specialized | `<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort` | `U64Cmp` / `canonical_less_u64`, N2 и N3, `backing[1..N+1]` из N+2, actual network entry | `v`; private stack scratch |

Каждый `*Cmp` — точный `fn(&T, &T) -> bool` с указанной read-only функцией. Её `true` означает числовое `<` на полном значении. Компараторы не пишут через аргументы или вовне. Interior fixtures после вызова проверяют оба внешних canary. Stable default дополнительно читает после возврата только initialized sentinel. Выбор Stable и Unstable defaults следует из `Cell<u8>: !Freeze`. `NonCopyKey` — приватная обёртка `#[repr(transparent)]` над `u8` с `Freeze`, без `Copy` и пользовательского `Drop`. Условие `1 * SMALL_SORT_GENERAL_SCRATCH_LEN (48) <= MAX_STACK_ARRAY_SIZE (4096)` выбирает Freeze general.

`unwind(32)` следует профилю G3. В Stable и Unstable default при N2 вставка с offset 1 имеет один проход, а `insert_tail` при сдвиге достигает начала после одного прохода. Freeze default при N2 копирует два singleton, обходит два offset без итераций удлинения и один раз исполняет парный merge шаг. В модели снимок N2 читает два элемента и проверка использует две перестановки пары без циклов. Успешные native unwinding assertions остаются условием приёмки.

## Ordinary roots и ожидаемое evidence

Во всех таблицах селектор для `--harness <full-name> --exact` образуется добавлением суффикса к `slice::sort::shared::smallsort::verify::trait_contracts::`. Строки исходника относятся к `smallsort/verify/trait_contracts.rs` кандидата. Все десять roots ожидаются `SUCCESS` с пятью `SATISFIED` covers `sort model enabled before call`, `ascending input returns`, `descending input returns`, `duplicate input returns`, `trait small_sort returns`. Guard отдельно утверждается перед вызовом. Для каждого Check ожидаются native `ensures`, DFCC/frame и успешные unwind assertions на exact impl. Для каждого Replace ожидается native привязка к соответствующему Freeze target.

| Селектор, суффикс | Строка | Native режим и связь с fixture | VT, с |
| --- | ---: | --- | ---: |
| `stable_sorts_permutation_u64_len2` | 25 | Stable specialized Check, actual general, N2, scratch 18 | 112 |
| `stable_sorts_permutation_u64_len3` | 41 | Stable specialized Check, actual general, N3, scratch 19 | 170 |
| `freeze_sorts_permutation_u64_backing4` | 57 | Freeze Copy-specialized Check, actual network entry, N2, `backing[1..3]` | 29 |
| `freeze_sorts_permutation_u64_backing5` | 75 | Freeze Copy-specialized Check, actual network entry, N3, `backing[1..4]` | 68 |
| `unstable_sorts_permutation_u64_backing4` | 94 | Unstable specialized Check, Freeze Replace с fixture строки 57 | 83 |
| `unstable_sorts_permutation_u64_backing5` | 113 | Unstable specialized Check, Freeze Replace с fixture строки 75 | 128 |
| `verified_forwarding_sorts_permutation_u64_backing5` | 132 | Plain proof, real Unstable, Freeze Replace с fixture строки 75, отдельные sortedness, multiplicities и frame | 6 |
| `stable_default_sorts_permutation_cell_u8_backing4` | 167 | Stable default Check, actual insertion, N2, отдельная scratch и sentinel frame | 15–60 |
| `unstable_default_sorts_permutation_cell_u8_backing4` | 188 | Unstable default Check, actual fallback, N2 | 15–60 |
| `freeze_default_sorts_permutation_noncopy_u8_backing4` | 204 | Freeze default Check, actual general, N2 | 30–120 |

Проверка default binding на новом пине должна связать каждый exact target из таблицы impl с его `default fn small_sort<F>` и выведенным из вызова `F`. Все три default Check вызывают тот же UFCS, который указан в атрибуте, без stubs. В случае сбоя frontend нужно сохранить exact target, сгенерированный Check/Replace, диагностику разрешения specialization или `old` и координаты. До этой сверки здесь зафиксировано только соответствие на уровне исходников. Предыдущий G3 PASS относится к ограниченным доказательствам на прежнем пине. [Результаты G3](/root/verify-rust-std-kani3300-gateb-prime/research/challenge-8/kani-k1/RESULT-TRAITPFC-G3.md)

## Opt-in roots

Ожидания относятся к раздельным exact прогонам с `cfg(kani_smallsort_controls)`. Для каждого негатива ожидается одна `assertion` со статусом `FAILURE` и один указанный `SATISFIED` cover. Source ID задаёт пара «exact root, сообщение `kani::assert`». В таблице указаны строки вызовов в candidate source. Нативные property IDs, class и фактические locations сверяются и записываются по удалённой выдаче на этом SHA.

| Селектор, суффикс | Expected assertion и строка | SATISFIED cover | VT G3, с |
| --- | --- | --- | ---: |
| `rejects_high_bit_corruption_u64_len3` | `high-bit corruption preserves sorted full values`, 234 | `sorted high-bit corruption reached` | 1,91 |
| `rejects_changed_multiplicities_u64_len3` | `same set preserves full multiplicities`, 254 | `sorted multiplicity corruption reached` | 0,55 |
| `rejects_reverse_pointer_sorted_u64_backing5` | `reverse pointer output is sorted`, 280 | `guard-disabled reverse pointer can return unsorted` | 2,21 |
| `rejects_function_item_sorted_u64_backing5` | `function item output is sorted`, 315 | `guard-disabled function item can return unsorted` | 2,05 |
| `freeze_frame_function_item_u64_backing5` | `SUCCESS`, actual Freeze Check, guard off и оба canary, root 321 | `descending input returns`, `non-descending input returns`, `trait small_sort returns` | 35,95 |

Первый негатив включает верхний бит максимума в `[0, 1, 2]` и сохраняет порядок. Второй меняет `[a, a, b]` на `[a, b, b]` при `a < b`. Третий и четвёртый выполняют real Unstable forwarding на `backing[1..4]` с диагностическим Freeze Replace и проверяют внешний frame перед ожидаемым провалом sortedness. Третий передаёт `U64Cmp` со значением `reverse_less`. Четвёртый и frame witness используют один и тот же function item `trait_less_u64` и generic lookup guard. W1 ограничен frame при выключенной модели. Эти контроли калибруют границы модели.

## Бюджет и границы дальнейшей проверки

Семь исходных roots суммарно занимали 596,7 с native VT в G3. Три новых default Check предварительно добавляют 60–240 с. Суммарный новый serial VT оценивается в 11–14 мин. Для 77-минутного baseline критического verifier shard план использует ориентир +5 мин. Оценка размещения предварительная. Точный упорядоченный полный std inventory для кандидата отсутствует, а `run-kani.sh` объединяет standard/contract entries и режет весь std набор на четыре последовательных куска по `ceil(count/4)`. Числа 235 и 245 относятся к SmallSort. План приёмки связывает восемь verifier cells и весь набор из 16 jobs с точным SHA и пином. [GO и приёмка](PLAN.md#go-на-один-dispatch-fork-ci)

Границы исходных утверждений — normal return, указанные exact типы и функции с полным числовым порядком, длины и allocation layouts. Вне области остаются произвольные типы, длины и компараторы, effectful `FnMut`, stability для различимых равных ключей, unwinding, aliasing, ZST и panic cases, а также uninitialized-memory, value-validity и immutable-byte permission checks. Сдача фиксирует подготовленный локальный кандидат. Fork CI, GCB, controls-on и публикация требуют предусмотренных планом решений координатора или владельца.
