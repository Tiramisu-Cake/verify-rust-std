# NEWPINCAL — Part 1 v7 на новом pin: inventory и калибровка

**Выдано координатором 2026-11-04 по плану, одобренному владельцем. Dispatch только после exact-packet PRE-BUILD
review/GO координатора.** Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-newpincal**, ветка **experiment/kani-k1-newpincal-20261104**.
- База: **eccc31f43b** — upstream `233f96f66a` (Kani `cd355b0b`, nightly-2026-10-22) плюс K-1 lane tooling без
  изменений. Сверху cherry-pick library-коммита TRIMPART `bd7fb8196e` → **e470652790**, library tree
  **32ce0c62f6** (тот же, что в `bd7fb8196e`).
- Slug **newpincal**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `newpincal-*`.
- Project cap **$98.96**, свой cap **$1.00**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap. Repair library-кода — только с согласия координатора.
- Tooling base для check-tooling: **eccc31f43b**.
- Окно: main 150 + closeout 30 мин.

## Контекст

Part 1 v7 — это 202 ordinary-корня и 8 opt-in negative-контролей (RESULT-TRIMPART в ветке
`experiment/kani-k1-trimpart-20261104`, коммит `120e443536`). Все прежние результаты получены на Kani `9461e07a`,
nightly-2026-10-12. Этот Build — первый на новом pin. Lane соберёт Kani по `tool_config/kani-version.toml` из дерева.

## Пакет

Один request, 4 строки: **kind diagnostic**, `inventory: true`, `controls: true`, gcb-e2-standard-4, kani_jobs 1, uninit off,
10 мин на строку. Резерв (4×10+30)×$0.0135 = **$0.945**.

| # | Root (`slice::sort::shared::smallsort::verify::…`) | Что калибрует | Ожидание |
|---|---|---|---|
| 1 | `network::swap_contract_four_positions_u8` | scalar PFC | SUCCESS, все covers |
| 2 | `network::dispatch_safety_stable_u8_n0_1_2_7_8` | реальный вход `small_sort` | SUCCESS, все covers |
| 3 | `assembly::reject_mutant_swap_u8_n2` | negative control мутанта | FAILED на своей проверке |
| 4 | `merge::specfix::specfix_wrong_f_swap_rejected_u8` | negative control контракта | FAILED на guard компаратора |

Для строк 3 и 4 указать `expect_check` по фактическому тексту проверки в source. Формат сверить с `kani_k1.py`.

## До PRE-BUILD (статически)

- `python3 -B research/challenge-8/kani-k1/tools/test_kani_k1.py`: все тесты проходят. На голой `eccc31f43b`
  `test_controls_cfg` падал, потому что не было check-cfg; теперь он должен пройти.
- `k1g.sh check-tooling` против `eccc31f43b`: lane не изменён.
- Library tree = `32ce0c62f6`. Diff `233f96f66a..HEAD -- library` совпадает с TRIMPART.
- Request validation, budget и slots (≤ 2 unfinished на проект, ≤ 1 на k1-network).

PRE-BUILD: identities (head, tree, Kani commit и toolchain из дерева), request, expect_check, budget. Коммиты research
отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` — в фоновом Bash.

## Gate и RESULT

1. **Inventory** (`k1g.sh inventory`): ровно 210 имён = `ordinary-expected.txt` ∪ `controls-expected.txt` из
   `research/challenge-8/kani-k1/trimpart/` (взять из коммита `120e443536`). Расхождение — факт, без исправлений.
2. **Строки**: 1–2 SUCCESS, 0 failures, все covers. 3–4 FAILED ровно на назначенной проверке (описание и location).
   Время каждой строки записать рядом с временем на старом pin, если оно есть в прежних RESULT.

Compile error, TIMEOUT или иной исход — bounded facts, без retry. Если ошибка в verify-коде из-за нового pin,
записать точное место и сообщение и остановиться. Repair не делать до решения координатора.

**RESULT-NEWPINCAL.md**, ≤ 30 строк:
- identities;
- inventory (count, совпадение);
- таблица 4 строк со временем;
- выводы для полного прогона CI на новом pin.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **NEWPINCAL ЗАВЕРШЁН**, одна стадия, затем стоп.
