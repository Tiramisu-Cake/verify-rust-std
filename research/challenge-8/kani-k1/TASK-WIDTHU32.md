# WIDTHU32 — точка ширины: перестановка u32 N8 на реальном unstable-маршруте

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-widthuthirtytwo**, ветка **experiment/kani-k1-widthuthirtytwo-20261103** от
  **e0fda080f5ea479d8f4fb801f4b42adde2b3259f** (v6 library tree + K-1 tooling + cap 98.96).
- Slug **widthuthirtytwo**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `widthuthirtytwo-*`.
- Project cap **$98.96**, свой cap **$0.90**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e0fda080f5.
- Окно: main 150 + closeout 30 мин.

## Контекст

Перестановка при N8 упирается в ширину элемента:
- u8 — ordinary;
- u64 — только kissat, 449 с (PERMSOLVER, a13389358a; worktree `/root/verify-rust-std-kani-permsolver`).

Аудитор предложил промежуточную точку u32: где проходит граница. Это измерение ширины, не перенос доказательства между
типами.

## Source scope

Новый opt-in child `network::widthu32`, файл `verify/network/widthu32.rs`; в `network.rs` — только
`#[cfg(kani_smallsort_controls)] mod widthu32;`.

Тело — клон arbitrary-probe варианта PERMSOLVER:
- full input `[u32; 8]`, независимая проба `u32`;
- actual `<u32 as UnstableSmallSortTypeImpl>::small_sort`;
- компаратор FnItem `strict_less::<u32>`;
- full-value count до и после.

Показать diff против PERMSOLVER: меняется только тип.

Ровно 3 roots:

| # | Root | Отличие | Ожидание |
|---|---|---|---|
| 1 | `widthu32_perm_n8_default` | default solver | SUCCESS или TIMEOUT (измерение) |
| 2 | `widthu32_perm_n8_kissat` | `#[kani::solver(kissat)]` | SUCCESS |
| 3 | `widthu32_perm_n8_value_loss_control` | `v[0] = v[1]` после сортировки, kissat | FAILED на assert count |

Covers — как у PERMSOLVER плюс проба попадает и не попадает.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+3);
- rustfmt;
- без warnings.

## Пакет

3 строки, kind diagnostic (1–2 expect SUCCESS, 3 expect FAILED + expect_check):
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв **$0.810**.

Project ≤ 2 unfinished, ≤ 1 на k1-network.

PRE-BUILD: diff против PERMSOLVER, hashes, budget. Коммиты library/research отдельно, `[skip ci]`, push без force.
`PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в фоне.

## Gate и RESULT

Засчитываем, если:
- 2 SUCCESS со всеми covers;
- 3 FAILED на assert count.

1 — измерение.

**RESULT-WIDTHU32.md**, ≤ 25 строк:
- таблица;
- сравнение VT с u8 и u64 при N8 (ссылки на записи);
- вывод о ширине без обобщения.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **WIDTHU32 ЗАВЕРШЁН**, одна стадия, затем стоп.
