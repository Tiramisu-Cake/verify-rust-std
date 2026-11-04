# PINCHECK — перепроверка имеющегося на новом pin: контроли, CASE5, uninit-пилот

**Выдано координатором 2026-11-04 по решению владельца** (сначала перепроверка на новом pin, потом новые
доказательства). **Dispatch только после exact-packet PRE-BUILD review/GO координатора.** Runtime **Claude Code**,
одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-pincheck**, ветка **experiment/kani-k1-pincheck-20261104** от
  **50b3abfe9b**. Это upstream `233f96f66a` (Kani `cd355b0b`, nightly-2026-10-22), K-1 tooling, library Part 1 v7
  (tree `32ce0c62f6`) и research NEWPINCAL/v7ci.
- Slug **pincheck**. Owners: G1 — **k1-network**, G2 — **k1-merge**; они могут идти параллельно. Новые
  stage/ledger/UUID/request_id `pincheck-*`.
- Project cap **$98.96**, свой cap **$2.50** на обе сборки. **Две сборки**, retry нет. Исключение — один
  compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **eccc31f43b**. Tooling не менять.
- Окно: main 180 + closeout 30 мин.

## Контекст

Part 1 v7 (`d1283ff22a`) прошёл CI организаторов на новом pin. Не перепроверены там:
- 6 из 8 negative-контролей;
- оговорка CASE5;
- статус uninit-проверок.

Всё остальное из прошлых исследований получено на старом pin `9461e07a`. Цель этапа — для каждого пункта получить
факт на новом pin. Новые доказательства и расширение доменов в этот этап не входят.

Источники (читать их RESULT и код, всё — наше):
- RESULT-NEWPINCAL (`732c4e25b2`): формат запроса с контролями и формат `expect_check`;
- CASE5-2: `a1e56b61cd` и коммиты перед ним — фикстуры A1/A2/P16/P17/S4/C1/D1/D2. Standalone-репро
  array-select — `5f5f99c9e4`, `42ead2dba6`;
- SPECDIAG (`e417249e66`): uninit-фикстуры и неподдержанные операции на старом pin.

## G1 — 6 контролей и CASE5 (k1-network, kind diagnostic, controls: true)

**Строки 1–6** — оставшиеся контроли Part 1 v7, каждый с `expect: FAILED` и `expect_check` по фактическому тексту
проверки в source:
- `merge::specfix::specfix_full_value_checker_rejects_payload_change_u8`;
- `wrap::rejects_payload_corruption`;
- `wrap::rejects_always_true`;
- `merge::specfix::specfix_wrong_f_{sort4_rejected_u64, insert_rejected_u8, merge_rejected_u8}`.

**Строки CASE5** — не больше 3:
- минимальная фикстура, которая на старом pin давала невозможный контрпример;
- её известный проходящий вариант;
- scalar-контроль.

Фикстуры перенести из CASE5-2 в отдельный opt-in модуль под `cfg(kani_smallsort_controls)`, отдельным
research-library коммитом. Существующие файлы v7 не менять. Ожидания поставить по старому поведению, расхождение
записать как факт.

Строк ≤ 9. `harness_timeout_minutes` выбрать минимальным разумным, резерв по формуле lane. Ordinary-корни не
запускать: они уже прошли в CI v7.

## G2 — uninit-пилот (k1-merge, `uninit_checks: true`)

По одной цели за раз, ≤ 6 строк:
1. **Калибровка.** Собственная пара фикстур: чтение неинициализированного `MaybeUninit` должно упасть на
   uninit-проверке, тот же код с инициализацией — пройти. Без калибровки результаты строк 3–6 не засчитываются.
2. **Старая фикстура SPECDIAG**, которая на старом pin упиралась в неподдержанную операцию.
3. **Реальные хелперы**, маленькие существующие корни Part 1: scalar PFC `swap_if_less`, `sort4`, `insert_tail`,
   `merge` на малом N. Пары с covers выбрать в PRE-BUILD.

Исходы различать: SUCCESS, FAILED на uninit-проверке (с location), неподдержанная операция (точный текст), compile
error, TIMEOUT. Valid-value в этот этап не входит: в lane нет такого профиля.

## До PRE-BUILD

- `test_kani_k1.py` OK. `check-tooling` против eccc31f43b.
- Diff library против `e470652790`: только новый opt-in модуль (CASE5 и uninit-фикстуры) и его регистрация под cfg.
  Ordinary 202 не меняется, статически.
- Requests проходят validate. Budget и slots: ≤ 2 unfinished на проект, ≤ 1 на owner.

PRE-BUILD: identities, обе request, expect/expect_check, budget. Коммиты library-research и research отдельно,
`[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в фоне.

## RESULT

**RESULT-PINCHECK.md**, ≤ 40 строк:
- identities;
- G1: таблица строк (status, failed check и location, время), вывод по 8 контролям на новом pin, статус CASE5 на
  новом pin;
- G2: результат калибровки, таблица строк и классификация исходов, что это значит для класса «чтение
  неинициализированной памяти»;
- что осталось NOT_RUN.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наши исходники, RESULT и документация Kani. Чужие PR, их код и ветки не открывать.

Маркеры `REVIEW REQUEST <sha>` / **PINCHECK ЗАВЕРШЁН**, одна стадия, затем стоп.
