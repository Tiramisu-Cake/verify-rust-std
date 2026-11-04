# TRIMPART — Part 1 v7: только ordinary + 8 контролей, на текущем upstream

**Выдано координатором 2026-11-04 по решению владельца.** Runtime **Claude Code**, одна стадия, без субагентов.
**Без Cloud Build и Actions**: только git, Python и rustfmt.

## Рабочее место

- Worktree **/root/verify-rust-std-kani-trimpart**, ветка **experiment/kani-k1-trimpart-20261104** от upstream
  **233f96f66ab3785881cead133817ed5db4c76b09** (Kani `cd355b0b`, nightly-2026-10-22).
- Источник кода — Part 1 v6 **d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097** (library tree `d4ec476a7a`). Runtime `smallsort.rs`
  между `c0bd09c354` и `233f96f66a` не менялся — проверить и записать.
- Окно 180 мин.

## Цель

Part 1 v6 — 4 445 строк, из них ~1 290 — opt-in (`cfg(kani_smallsort_controls)`), который CI не запускает. Владелец решил:
- в Part 1 оставить ordinary-набор и минимальные контроли;
- остальной opt-in уходит в Part 2. Part 2 будет **добавлять** код, а не снимать cfg.

## Состав

**Ordinary — без изменений.** 202 корня, 36 PFC. Тела, атрибуты, stubs, unwind, covers и раскрытие макросов
совпадают с v6. Также совпадают транзитивные helpers, модели, контракты, T/F/CMP/probe, backing/frame.

**Opt-in — ровно 8 negative controls** (за `cfg(kani_smallsort_controls)`, check-cfg в `library/core/Cargo.toml`
сохранить):

1. `assembly::reject_mutant_swap_u8_n2` — из mutants оставить только нужный `mutant_swap_if_less`.
2. `merge::specfix::specfix_full_value_checker_rejects_payload_change_u8`.
3. `wrap::rejects_payload_corruption`.
4. `wrap::rejects_always_true`.
5. `merge::specfix::specfix_wrong_f_swap_rejected_u8`.
6. `merge::specfix::specfix_wrong_f_sort4_rejected_u64`.
7. `merge::specfix::specfix_wrong_f_insert_rejected_u8`.
8. `merge::specfix::specfix_wrong_f_merge_rejected_u8`.

Если реальные имена в v6 отличаются от перечисленных — сверить по смыслу, записать соответствие и спросить меня до
удаления.

**Удалить физически:** все остальные opt-in корни, `specdiag.rs`, неиспользуемые mutants и их mod-декларации. Должен
получиться cfg-on набор = **210** (202 + 8). Если корень опирается на `paired_case`-макрос, его можно разделить на
позитивную генерацию и выбранный негатив, сохранив раскрытие позитива байт-в-байт.

**Не делать:**
- не превращать intentional failures в ordinary через `should_panic`;
- не маскировать осиротевшие helpers широким `allow(dead_code)` — удалить их;
- общие checkers не переписывать.

**`verify.rs` doc** переписать под фактический состав:
- убрать описание полного `mutations`/`specdiag`/исследовательских корней;
- назвать восемь контролей и отдельный Part 2;
- сохранить домены профилей и ограничения: uninit, validity, permissions (immutable bytes), unwind;
- фразу «permutation beyond N8 uses a structural argument» заменить на: ordinary network утверждает count только при
  N < 9, более длинная композиция относится к отдельным research-результатам;
- команды сверить с `scripts/run-kani.sh` на новой базе: обычный запуск без cfg и отдельный exact-select контролей с
  cfg. Не писать «проверить все cfg-on roots как SUCCESS».

## Проверки (статические; компиляция — следующей стадией на новом pin)

1. ordinary name-set (cfg-off) = v6, ровно 202. Раскрытые тела и атрибуты каждого ordinary-корня и их транзитивные
   зависимости совпадают с v6 побайтно или с объяснённой нормализацией (пути/импорты).
2. cfg-on name-set = 202 + ровно эти 8.
3. Нет ссылок на удалённые модули и функции; нет осиротевших helpers и imports в cfg-off и cfg-on (статически, по
   использованию).
4. rustfmt `--check` по всем файлам verify, `git diff --check`, строки ≤ 100.
5. Diff против `233f96f66a`: только `smallsort/verify*`, регистрация `mod verify;` в `smallsort.rs`, check-cfg в
   `Cargo.toml`. Runtime-строк в diff нет.
6. Итог в строках: total / ordinary-код / opt-in-код / комментарии, тем же способом, что для v6 (4 445 → ?).

Скрипт проверок — в `research/challenge-8/kani-k1/trimpart/`.

## Коммиты

- **Library** — одним коммитом `[skip ci]` (это кандидат в Part 1 v7).
- **Research** — отдельным.

Push без force.

## RESULT

**RESULT-TRIMPART.md**, ≤ 40 строк:
- base/head SHA, library tree;
- таблица «было v6 → стало» по файлам и строкам;
- список 8 контролей с привязкой к механизму;
- что удалено и куда (Part 2);
- результаты 6 проверок;
- что не проверено без компиляции.

## Запреты

- Никаких локальных cargo/rustc/Kani/CBMC, Cloud Build, Actions, PR/issue.
- Credentials не читать.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **TRIMPART ЗАВЕРШЁН**, одна стадия, затем стоп.
