# INSERTPFC — доказательство контракта `insertion_sort_shift_left` в обычном наборе

**Выдано координатором 2026-11-07, решение владельца (вариант C).** Последнее изменение library перед финальным
коммитом. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-insertpfc**, ветка **experiment/kani-k1-insertpfc-20261107** от
  **4f52065504** (INTEGCHECK PASS: library tree `def2d65ddc`; 233 ordinary + 13 контролей, cfg-on 246).
- Slug **insertpfc**, stable owner **k1-merge**. Request_id/stage/ledger `insertpfc-*`.
- Project cap **$118.96**, свой cap **$2.00**. **До двух сборок**: G1 (proof rows), G2 (cfg-on inventory); G2 можно
  отправить в том же пакете GO. Retry нет. Один compile-error repair, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 300 + closeout 30 мин.

## Цель

Контракт на `insertion_sort_shift_left` (`smallsort.rs`, `requires`/`modifies`) сейчас не доказан ни одним
обычным харнессом. Вернуть в обычный набор два доказательства контракта, которые уже проходили:
`realcontracts::insertion_safety_u64_len2` и `_len3` из **44b972435a** (`verify/realcontracts.rs:106–130`,
`exercise_insertion_fixed`; SUCCESS 81.03 с / 105.38 с, covers 6/6, RESULT-REALCONTRACTS `d648179493`).

Library-изменения (только они):
1. `verify/helper_contracts.rs`: импорт `insertion_sort_shift_left` без cfg; функция `exercise_insertion_fixed<const N>`
   и два корня `insertion_safety_u64_len2`, `insertion_safety_u64_len3` (`proof_for_contract(insertion_sort_shift_left)`,
   `unwind(8)`, без `cfg`). Тело, домен (u64, `[u64; N]`, произвольный `offset` с `offset != 0 && offset <= N`),
   компаратор `arbitrary_less::<u64>` и covers — как в 44b972435a. Тексты covers — в стиле файла
   («helper contract insertion …»), без кодовых имён этапов. Комментарий над функцией — одна-две строки по сути
   (фиксированная длина, любой допустимый offset), без истории этапов. Разместить рядом с PFC `insert_tail`.
2. `verify.rs`, карта модулей: в список доменов `helper_contracts` добавить u64 insertion sort двух и трёх
   элементов с любым допустимым offset. Остальной текст карты не менять («five real helper write sets» остаётся
   верным).

**Нельзя:** менять `smallsort.rs`, другие корни, их тела, атрибуты, covers, сообщения; делить/объединять файлы.

## Статические проверки (скрипт в `research/challenge-8/kani-k1/insertpfc/`)

Переиспользовать лексер/expander из `renamemods/`.
- Ordinary = 233 прежних + 2 новых = **235**; cfg-on = **248**; файлы `ordinary-expected.txt`, `cfg-on-expected.txt`.
- Раскрытые items всех 246 прежних корней и их замыкания **токен-идентичны** INTEGCHECK-дереву `def2d65ddc`.
- Два новых корня после обратной замены текстов covers токен-идентичны корням 44b972435a.
- `smallsort.rs` байт-идентичен; `rustfmt --check` (обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
  research/challenge-8/kani-k1/codefix/rustfmt.toml` на изменённых файлах) — ноль diff; строк > 100 нет;
  запрещённая лексика TIDYDOCS и кодовые имена этапов в изменённых строках — пусто.

## Сборки

- **G1:** kind diagnostic, `controls: true`, `inventory: false`, jobs 1, standard4. 15 строк: 2 новых PFC
  (`expect: SUCCESS`, covers 6/6) и 13 контролей (`expect: FAILED` + `expect_check`; ожидания — из пакета
  INTEGCHECK `integcheck/controls-expected.json`, с пересчётом строк, если файл helper_contracts.rs сдвинулся).
  Контроль принимать, только если **все** упавшие проверки — назначенные. Лимит на корень 5 мин; лимит сборки —
  компиляция cfg-on + строки × лимит + запас.
- **G2:** kind inventory, `controls: true`, без строк: ровно 248 имён = `cfg-on-expected.txt`, без новых
  предупреждений в `smallsort/verify` и `smallsort.rs`. Лимит — по INTEGCHECK G2 с запасом.

## RESULT

**RESULT-INSERTPFC.md**, ≤ 40 строк: identities (library SHA/tree, diff к `def2d65ddc` — только два файла);
статика; две строки PFC (status, время, covers, прежнее время); таблица 13 контролей (status, упавшие проверки —
полный состав, совпадение с назначенной); cfg-on inventory (число, SHA256 sorted, совпадение); warnings; расход.

## Коммиты

- Library-коммит отдельно от research-коммитов, все `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC (rustfmt разрешён), Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **INSERTPFC ЗАВЕРШЁН**, одна стадия, затем стоп.
