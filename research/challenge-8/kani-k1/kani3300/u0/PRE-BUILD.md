# KANI3300 U0 PRE-BUILD

Пакет подготовлен для exact-packet review координатора по TASK-KANI3300-U0.md и всем пяти пунктам U0-REVIEW-FIXES.md.

- Worktree `/root/verify-rust-std-kani3300`, branch `experiment/kani-k1-kani3300-20261111`.
- Stage `kani3300-u0`, owner `k1-merge`, request `kani3300-u0-uninit-20261111-01`.
- Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`.
- Library commit `c96175dab23c69825ba654d5e4fc45e920baf0a2`.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`, `kani_patch` отсутствует.
- Request SHA-256 `0dbce45f0859d38e56817b53e1861e4d028853418f6826caa73293adfb966056`.
- `RUN-REQUEST.json` в этом каталоге побайтно совпадает с активным request в `kani-k1/`.
- `kind=diagnostic`, standard4, jobs1, controls on, inventory off, `-Z uninit-checks`, timeout каждого harness 3 минуты.
- Резерв по формуле dispatcher `(8 × 3 + 30) × $0.0135 = $0.7290`, собственный cap $0.80.
- Снимок общего ledger в `budget-prebuild.txt` показывает used $112.5330, reserved $0.0000 при cap $118.96. С данным резервом получится $113.2620, итоговый ledger проверяется dispatcher перед submit.
- Окно main 240 + closeout 30 минут. Общий лимит задания проекта $6.40 учитывается вместе с координатором.

Все имена таблицы находятся в `slice::sort::shared::smallsort::verify::uninit_probe::`.

| Row | Harness | Expect | Unwind | Проверяемый путь |
|---|---|---|---|---|
| U1 | `pincheck_calibration_uninit_read_u8` | FAILED | прежний default | невыписанный слот через `assume_init` |
| U2 | `pincheck_calibration_init_read_u8` | SUCCESS | прежний default | записанный слот через тот же helper |
| U3 | `raw_uninit_read_sensitivity` | FAILED | прежний default | volatile read через `MaybeUninit<u8>::as_ptr` |
| U4 | `swap_contract_four_positions_u8` | SUCCESS | прежний default | PFC `merge::profiles::swap_profile::<LtU8>`, fn pointer |
| U5 | `sorted_permutation_insert_tail_u8_n2` | SUCCESS | 17 | реальный `insert_tail`, item `strict_less`, N2 |
| U6 | `permutation_merge_u8_n4` | SUCCESS | 17 | реальный `bidirectional_merge`, item `arbitrary_less`, N4 |
| U7 | `swap_contract_four_positions_u8_function_item` | SUCCESS | прежний default | PFC локального `swap_profile_function_item`, item `lt_u8` |
| U8 | `small_sort_general_with_scratch_u8_n4` | SUCCESS | 17 | реальный general scratch sort, item `strict_less`, N4 |

## Перенос и различия пакетов

Исторические fixtures прочитаны из `690bdea1c7e2c919161e0b3ef16c206122e885b5`, результаты cd355b0b из раздела 2 `kani-pin-check.md` в `fc72b711781e2c0effb3fc1d33dfad55785bd5b2` и исторического `pincheck/g2.summary.md`.
U1–U3 и их read-helper перенесены дословно вместе со всеми asserts/covers. U4 сохраняет исторический generic helper, LtU8, четыре позиции, canonical fn pointer и пять covers. Его PFC target переименован вместе с существующим модулем `merge::specfix` → `merge::profiles`, реальный target остаётся `swap_if_less`.
U5/U6 сохраняют тела helpers, T/F/N, assertions/covers и stub `panic_on_ord_violation` → `cut_ord_violation`. Старый macro `original_case!` развёрнут в те же proof/unwind/stub атрибуты двух harness. Исторический `assembly` в текущем дереве заменён `fixed_inputs`, нужные функции скопированы в opt-in модуль.
Между историческим деревом и tooling base в `smallsort.rs` добавлено 107 строк contracts, геометрических helpers и сопровождающих imports/comments. В частности, `swap_if_less`, `insert_tail` и `bidirectional_merge` получили requires/modifies. Исполняемые тела этих алгоритмов сохранены. Изменились также Kani pin и nightly toolchain.
Сравнение результатов характеризует два полных пакета. Изолированный эффект смены пина этим сравнением не устанавливается.

U7 имеет отдельный PFC target `uninit_probe::swap_profile_function_item` вместо `merge::profiles::swap_profile`. Он фиксирует `lt_u8` в теле и вызывает реальный `swap_if_less` с function item. Сохраняются `swap_geometry`, `swap_transfer` и `swap_ordered` на LtU8, footprint двух позиций, символические различные индексы и все пять covers. Canonical fn-address guard становится избыточен, поскольку callback-аргумента у нового target нет. Covers вызывают `lt_u8` напрямую, `P::CMP` в пути U7 не используется.

U6 выделяет merge output как `MaybeUninit<[u8; 4]>`, передаёт `as_mut_ptr().cast()` и читает результат через `assume_init`. U8 выделяет отдельный массив `[MaybeUninit<u8>; 20]`, передаёт его как срез scratch и наблюдает initialized `v` после реального вызова. Для U8 проверяются полная sortedness и количество произвольного байта, есть cover нормального возврата. Формы scratch различаются, препятствия могут отличаться. U8 использует тот же узкий panic stub, что U5/U6.

В `verify.rs` добавлена ровно одна строка `mod uninit_probe;`. Весь новый модуль исключён внутренним атрибутом `#![cfg(kani_smallsort_controls)]`. Такая запись обеспечивает однострочное подключение и штатное форматирование.

## Статика и приёмка разведки

`static-check.json` фиксирует 24 успешных проверки, identity исходников/request, точность исторических helpers и scope. `request-validation.txt`, `kani.args`, `rustflags.txt` фиксируют принятые восемь selectors и настройки runner. Rustfmt через заданную обёртку, edition 2024, проектный config, `--check` на двух изменённых Rust-файлах даёт exit 0 и ноль diff. `skip_children=true` ограничивает проверку этими файлами. Скомпилировать и проверить harness предстоит в Cloud Build после GO.

Приёмка требует COMPLETE, binding head/request/pin без patch, `check-tooling BUILD c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` PASS и ручную классификацию всех восьми строк. Для U1/U3 `expect_check` равен `Reading from an uninitialized`. Классы сохраняют unsupported, ожидаемый uninit-FAILED, ложный отказ, SUCCESS и TIMEOUT. Gate false допустим для разведки при выполненных остальных критериях. Covers после unsupported сами по себе не устанавливают чувствительность к uninit-чтению.

Из bounded `k1g.sh summary BUILD` и страниц строк будут сохранены failed/total и доступные failed checks дословно с локациями. При ограничении списка/длины будет явно записана неполнота и доступные checks. Порядок строк summary используется для идентификации строк, порядок исполнения им не устанавливается.

Первое препятствие определяется по пути в U6/U8, при отсутствии такового рассматривается первый unsupported. После evidence будет подготовлен standalone repro ≤30 строк, edition 2021, в этом каталоге и указан отвергающий участок `check_uninit/` с файлом и строкой. До отдельного запуска repro получает обозначение кандидата, его связь с препятствием обосновывается трассировкой исходного пути. RESULT-KANI3300-U0.md ≤35 строк будет содержать identities, все восемь классификаций, сравнение пакетов, кандидат repro, исходную локацию, расход и вывод для U1.

После exact-packet GO применяется `k1g.sh dispatch experiment/kani-k1-kani3300-20261111`, затем `k1g.sh watch BUILD` и конец хода. Dispatch требует опубликованного SHA из маркера PRE-BUILD REVIEW. Каждый repair требует факта отказа, расчёта факт + новый резерв ≤$0.80 и нового exact-packet GO.
