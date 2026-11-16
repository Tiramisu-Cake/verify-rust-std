# S1-04 — offline acceptance, run 43830757263

Одна стадия `TASK-CH8-S1-04-ACCEPT-W11` завершена. **Qualified acceptance PENDING;
положительных obligations принято 0; proof credit NONE.** Это результат проверки
сохранённых наблюдений, не B1 independent acceptance или B2/general theorem.

Исходные 35 harness: 27 SUCCESS, 8 FAILURE. F1–F3 квалифицированы только как
`ACCEPTED_NEGATIVE_OBSERVATION`; F4–F6 совпали с заранее объявленными oracle,
но квалификация строк UNKNOWN. Два attachment mutants — `OBSERVED_UNQUALIFIED`.
Итого: 3 qualified negative observations, 30 UNKNOWN, 2 OBSERVED_UNQUALIFIED.
Исторические RESULT/ROWS/collected/receipts и ledgers не изменены.

Вход: intake g0 `149a94c8fa`; entry g0 `90e4c41b6f4e2dbe33c347afa7f5c286783c94a5`.
Control `205b0e98c771a7e6c6b8ec28414494868bcca4e0`, std
`5be85699b8826e3286c0bf89efb9affefac0acb5`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`. Request SHA256
`fce0e446f1506d0aebf4afc9929075843beed69c01a626391f119e18125850b7`.
Полные hashes, 14 group identities, исходные exits и per-row inventory — в
[ACCEPT.json](ACCEPT.json). Применена [ACCEPTANCE-POLICY-BATCH](../../../../../ACCEPTANCE-POLICY-BATCH.md),
подход Profiles accept-v2..v4: retained preflight + exact-property links + fail-closed role/binding gates.

Все 76 unsupported имеют SUCCESS и rich `PropertyExport` того же harness:
ID, class, description, file, line, status. Они связаны с pinned generator chain
`assert(false); assume(false)`: `assert.rs:129–145,214–231,278–324`,
`foreign_function.rs:256–261`, `intrinsic.rs:91–95`, `overrides/hooks.rs:228–240`;
exporter `schema_utils.rs:495–505,768–772`. Это недостижимость construct в данной
модели; сам непустой список не блокирует acceptance. Failed/reachable/unknown
unsupported отклоняются; unwind/undefined-function checks сохранены. Точные 76
same-row links перечислены, межстрочного или межзапускового заимствования нет.

**Оставшееся ограничение evidence:** stock export не сохраняет descriptions и
source locations для 413 UNREACHABLE checks; это списки строк ID. SUCCESS checks
даны счётчиком 9450, без их полного именованного inventory. 115 covers также
сохранены только как ID/status: 113 SATISFIED, 2 UNREACHABLE. Rich objects есть
лишь для 8 failures и 76 unsupported. Это подтверждается pinned
`schema_utils.rs:516–587,753–772`, не одним no-match.

Runner зафиксировал `--output-format=terse`; pinned `cbmc_property_renderer.rs:257–259`
не печатает property items. В каждом из 14 stdout выполнены только bounded rg
queries на rich record headers, harness markers и terse counts; rich records
не обнаружены. Точные selectors, SHA и проекции запросов — `bounded_output_audits`.
Полные raw logs не читались и не копировались; новых evidence-загрузок не было.

Поэтому роли всех 413 unreachable оставлены UNKNOWN с exact ID, функцией из ID
и явными null для недоступных file/line/description. Helper-name exemption и
угадывание source site по assertion ordinal не применялись. Нельзя установить,
что среди них нет обязательной post/frame/relation assertion. Подтверждённая
недостижимость обязательной проверки была бы blocker; это отдельно проверено тестом.
Не отменён blanket veto ради PASS: причиной UNKNOWN служит конкретный недостающий
source-site/role binding.

Таблица message → property ID хранится в `rows[].cover_message_table` для всех
113 required messages. Сейчас ID = null / UNKNOWN_DESCRIPTION_NOT_RETAINED:
export description отсутствует. ID/status каждого из 115 covers сохранены отдельно.
Даже ordinary-bridge с 12/12 SAT и без exceptions остаётся UNKNOWN. Источник
содержит 12 `concat!/stringify!` messages, но порядок `cover.N` не доказывает
их соответствия описаниям export. SAT не доказывает полноту domain.
127 required-success bindings также не восстановлены по одному счётчику SUCCESS;
часть `assert!` descriptions в stock вообще заменяется runtime-message placeholder.
Для 22 PFC rows exact source attribute/preflight сохранён, full check/modifies
wrapper и required post/frame property correlation остаются pending.

Patch worker13 проверен `git apply --check`, его bytes точно совпали с in-memory
request delta. Только offline classifier добавляет macro declaration line 29
`fn $name()` и сохраняет invocations 66/67/68, source SHA, selector/crate/file/mode.
Три model roots проходят source preflight и переходят к inventory/binding gates;
control и request на диске не менялись. 15 неверных selector/crate/mode/file/line
мутаций отклонены.

F1–F6 проверены по замороженным exact ID/file/line/class oracles и pinned source
assertion contexts, без подбора oracle по текущему FAILURE. Export description
для всех шести — stock runtime-message placeholder; он сохранён как факт,
а intended message проверен в исходном assertion context. Каждая строка имеет
ровно один требуемый FAILURE, без посторонних failures/unknown statuses.
F1–F3 не имеют unreachable, unsupported или required covers и квалифицированы
только как negative observations. F4–F6 имеют соответственно 8/1/11 unreachable;
count-corruption также требует непривязанную successful fixture assertion.
Все шесть остаются exact expected observations, но последние три не admitted.
Полный именованный SUCCESS inventory — gate positives, не новый gate F1–F3.

F7/F8 не засчитываются как DETECTED: request oracle = null до dispatch.
Две недостижимые mutant-return covers сохраняются как UNREACHABLE и не дают
positive vacuity credit. Точные наблюдённые failures:

- F7: `<cell::Cell<u8> as slice::sort::shared::smallsort::StableSmallSortTypeImpl>::small_sort::<slice::sort::shared::smallsort::verify::sorting_model::KeyLess<cell::Cell<u8>>>::{closure#2}.assertion.1`; `/home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort.rs`:41, assertion, FAILURE.
- F8: `<u8 as slice::sort::shared::smallsort::StableSmallSortTypeImpl>::small_sort::<slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::{closure#2}.assertion.2`; `/home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort.rs`:63, assertion, FAILURE.

`future_oracle_proposal` каждой mutant-строки предлагает эти exact IDs/description/
site и variant hashes **только для следующего пакета**: заранее freeze/review,
полный source/contract-wrapper binding, единственный разрешённый failure,
same-pin unmutated companion с достижимыми post-return covers. Это предложение
не меняет исторический oracle и не разрешает dispatch.

| Row | Qualification | Unreachable checks | Linked unsupported | Covers SAT/all |
|---|---|---:|---:|---:|
| stable_default_cell | UNKNOWN | 4 | 3 | 11/11 |
| unstable_default_cell | UNKNOWN | 4 | 3 | 11/11 |
| model_u8_n0_3 | UNKNOWN | 4 | 3 | 6/6 |
| model_cell_n0_3 | UNKNOWN | 4 | 3 | 6/6 |
| model_noncopy_n0_3 | UNKNOWN | 4 | 3 | 6/6 |
| inactive_pairs_read_free | UNKNOWN | 12 | 0 | 1/1 |
| activation_descending_rejected | qualified negative | 0 | 0 | 0/0 |
| activation_effectful_rejected | qualified negative | 0 | 0 | 0/0 |
| activation_unsupported_type_rejected | qualified negative | 0 | 0 | 0/0 |
| corruption_companion | UNKNOWN | 1 | 0 | 1/1 |
| order_corruption_rejected | UNKNOWN | 8 | 0 | 0/0 |
| count_corruption_rejected | UNKNOWN | 1 | 0 | 0/0 |
| snapshot_guards_companion | UNKNOWN | 2 | 1 | 1/1 |
| invalid_snapshot_rejected | UNKNOWN | 11 | 0 | 0/0 |
| stable_default_activation-legal | UNKNOWN | 4 | 3 | 1/1 |
| stable_freeze_activation-legal | UNKNOWN | 8 | 3 | 1/1 |
| activation-default | unqualified mutant | 15 | 3 | 0/1 |
| activation-override | unqualified mutant | 19 | 3 | 0/1 |
| ordinary-bridge | UNKNOWN | 0 | 0 | 12/12 |
| freeze_copy_u8_n0 | UNKNOWN | 27 | 3 | 2/2 |
| freeze_copy_u8_n1 | UNKNOWN | 26 | 3 | 2/2 |
| freeze_copy_u8_n2 | UNKNOWN | 22 | 3 | 5/5 |
| freeze_copy_u8_n3 | UNKNOWN | 22 | 3 | 5/5 |
| freeze_default_noncopy_n0 | UNKNOWN | 22 | 3 | 2/2 |
| freeze_default_noncopy_n1 | UNKNOWN | 21 | 3 | 2/2 |
| freeze_default_noncopy_n2 | UNKNOWN | 10 | 3 | 5/5 |
| freeze_default_noncopy_n3 | UNKNOWN | 10 | 3 | 5/5 |
| stable_freeze_u8_n0 | UNKNOWN | 23 | 3 | 2/2 |
| stable_freeze_u8_n1 | UNKNOWN | 22 | 3 | 2/2 |
| stable_freeze_u8_n2 | UNKNOWN | 9 | 3 | 5/5 |
| stable_freeze_u8_n3 | UNKNOWN | 9 | 3 | 5/5 |
| unstable_freeze_u8_n0 | UNKNOWN | 25 | 3 | 2/2 |
| unstable_freeze_u8_n1 | UNKNOWN | 24 | 3 | 2/2 |
| unstable_freeze_u8_n2 | UNKNOWN | 20 | 3 | 5/5 |
| unstable_freeze_u8_n3 | UNKNOWN | 20 | 3 | 5/5 |

Все четыре replacement unions PENDING / eligible_for_review=false. 16 exact-N
SUCCESS не закрывают исходные четыре symbolic obligations. Внутригрупповые
binary hashes и source snapshots согласованы; parser-input/AST/MIR binding и
GitHub ZIP digest независимо не установлены. Per-root RSS остаётся UNKNOWN;
из group peak нельзя вывести соблюдение per-root cap.

`intake.py` воспроизводит проверку без compiler/verifier; `test_intake.py` —
8 тестов на потерю inventory/status, unsupported ID/class/status/site, обязательные
unreachable, отсутствие cover descriptions, macro/selector binding и exact
negative oracle. `VALIDATION.json` и `REVIEW.json` сохраняют результат.
Независимый reviewer Luna HIGH подтвердил пробел evidence; его finding о F1–F3
исправлен отдельной квалификацией negative observation, без positive/proof credit.

Следующий пакет должен сохранять descriptions/locations для всех checks/covers
(regular property output либо проверенный structured exporter), required checks,
source/tool/config identities и заранее объявленные attachment oracles. Данные
нового запуска нельзя выдать за восстановленные facts run43830757263.
Push/CI/публикаций/ledger и локальных cargo/rustc/Kani/CBMC не было.
