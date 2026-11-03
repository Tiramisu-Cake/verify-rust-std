# PERMANY — перестановка u64 N8 с произвольным read-only компаратором

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-permany**, ветка **experiment/kani-k1-permany-20261103** от
  **e0fda080f5ea479d8f4fb801f4b42adde2b3259f** (v6 library tree + K-1 tooling + cap 98.96).
- Slug **permany**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `permany-*`.
- Project cap **$98.96**, свой cap **$0.90**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e0fda080f5.
- Окно: main 150 + closeout 30 мин.

## Контекст

Перестановка u64 N8 доказана только с канонической строгой сортировкой: PERMSOLVER, arbitrary probe + kissat,
449 с. Аудитор спросил, держится ли перестановка, если компаратор не задаёт порядок. При N8 на маршруте u64 network
есть только insertion и нет merge, а значит и нет guard `panic_on_ord_violation`. Поэтому перестановка должна
выполняться при любом ответе компаратора.

## Source scope

Новый opt-in child `network::permany`, файл `verify/network/permany.rs`. В `network.rs` — только
`#[cfg(kani_smallsort_controls)] mod permany;`. Существующие roots не менять.

Общее тело:
- `let mut v: [u64; 8] = kani::any();`
- независимая проба `probe: u64 = kani::any()`;
- pre-count по `==` на полном значении;
- actual `<u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut any_less)`, где `any_less` возвращает
  `kani::any()` и не читает память;
- post-count, затем `assert!(pre == post)`.

Без stubs, summaries и assumptions. Тело pre/post-count взять из PERMSOLVER (arbitrary-probe вариант; ветка
`experiment/kani-k1-permsolver-20261103`, RESULT a13389358a, worktree `/root/verify-rust-std-kani-permsolver`), а не
писать заново. Сверить и показать diff.

Ровно 3 roots:

| # | Root | Отличие | Ожидание |
|---|---|---|---|
| 1 | `permany_u64_n8_default` | default solver | SUCCESS или TIMEOUT (измерение) |
| 2 | `permany_u64_n8_kissat` | `#[kani::solver(kissat)]` | SUCCESS |
| 3 | `permany_u64_n8_value_loss_control` | после сортировки `v[0] = v[1]`, kissat | FAILED на assert перестановки |

Unwind — как у PERMSOLVER, сверить. Covers:
- проба попадает и не попадает;
- компаратор вернул true и false хотя бы раз;
- нормальный возврат.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+3);
- rustfmt;
- без warnings.

## Пакет

3 строки, kind diagnostic (1–2 expect SUCCESS, 3 expect FAILED + expect_check; сверить с `kani_k1.py`):
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (3×10+30)×$0.0135 = **$0.810**.

Project ≤ 2 unfinished, ≤ 1 на k1-network. Параллельно может идти CELLWRAP (k1-merge).

PRE-BUILD: маршрут u64 N8 по source (network → insertion, merge нет), diff тела count против PERMSOLVER, hashes,
budget. Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO.
`k1g.sh wait` в фоне.

## Gate и RESULT

Засчитываем, если:
- 2 SUCCESS со всеми covers;
- 3 FAILED ровно на assert перестановки (описание + location).

1 — измерение: SUCCESS — плюс, TIMEOUT — факт.

**RESULT-PERMANY.md**, ≤ 30 строк:
- таблица 3 строк: status, VT, checks, covers, CBMC RSS;
- вывод: перестановка u64 N8 на реальном unstable-маршруте при любом read-only bool-компараторе — доказана или нет;
- что не доказано: мутирующий компаратор, N ≥ 9, другие типы, CI-fit (> 300 с).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **PERMANY ЗАВЕРШЁН**, одна стадия, затем стоп.
