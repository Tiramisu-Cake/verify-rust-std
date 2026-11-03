# LOOPINV — фаза E2: loop invariant внешнего цикла `insertion_sort_shift_left` (диагностический пилот)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-loopinv**, ветка **experiment/kani-k1-loopinv-20261103** от
  **e0fda080f5ea479d8f4fb801f4b42adde2b3259f** (v6 library tree + K-1 tooling + cap 98.96).
- Slug **loopinv**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `loopinv-*`.
- Project cap **$98.96**, свой cap **$0.90**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e0fda080f5.
- Окно: main 150 + closeout 30 мин.

## Контекст

Challenge требует safety для любой длины. У нас все доказательства bounded: unwind по фиксированному N. Loop
contracts (`-Z loop-contracts`) уже включены во флагах организаторов (`scripts/run-kani.sh:87`), и в `core` они
используются через `#[cfg_attr(kani, kani::loop_invariant(...))]` (например, `num/imp/dec2flt/decimal_seq.rs:105`).

Пилот проверяет, работает ли этот механизм на внешнем pointer-цикле `insertion_sort_shift_left` (`smallsort.rs`
около 584). Unbounded safety не заявляем ни при каком исходе.

## Source scope

1. **Аннотация реального цикла.** `#[cfg_attr(all(kani, kani_smallsort_controls), kani::loop_invariant(...))]` на
   `while tail != v_end` в `insertion_sort_shift_left`. Gate на controls обязателен, чтобы ordinary-набор не менялся.
   Инвариант — только safety: `v_base <= tail <= v_end`, оба в одной аллокации, и т. п. Если нужен
   `loop_modifies`, явно обосновать его для вызова `insert_tail`. Недоказанную summary `insert_tail` не подставлять.
   Это **единственное** изменение в `smallsort.rs`, атрибут под cfg. Runtime-логика не меняется. Показать diff.
2. **Новый opt-in child** `network::loopinv`, файл `verify/network/loopinv.rs`; в `network.rs` — только
   `#[cfg(kani_smallsort_controls)] mod loopinv;`.

Ровно 3 roots:

| # | Root | Тело | Ожидание |
|---|---|---|---|
| 1 | `loopinv_insertion_u64_n2_offset1` | actual `insertion_sort_shift_left` на `[u64; 2]`, offset 1, read-only компаратор, с аннотированным циклом | SUCCESS |
| 2 | `loopinv_copy_true` | локальная копия того же внешнего pointer-цикла (тело — no-op или запись по `tail`) с тем же инвариантом | SUCCESS |
| 3 | `loopinv_copy_false_control` | та же копия с заведомо ложным инвариантом | FAILED на проверке инварианта |

Копия (2, 3) — только контроль инструмента, не доказательство реального helper.

Если на пине атрибут на этом цикле не компилируется или CBMC даёт TOOL_ERROR/OOM — это отдельный непринятый исход,
записать с bounded log-grep. Старый OOM и внутренний цикл `insert_tail` остаются риском.

Static:
- ordinary 202 / PFC 36 неизменны;
- ordinary-набор не затронут атрибутом: cfg-gate показать;
- exact name-set delta (+3);
- rustfmt;
- без warnings.

## Пакет

3 строки, kind diagnostic (1–2 expect SUCCESS, 3 expect FAILED + expect_check; сверить с `kani_k1.py`):
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (3×10+30)×$0.0135 = **$0.810**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge.

PRE-BUILD: diff `smallsort.rs`, инвариант и обоснование modifies, hashes, budget. Коммиты library/research отдельно,
`[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в фоне.

## Gate и RESULT

Засчитываем как работающий механизм, если:
- 1 и 2 SUCCESS;
- 3 FAILED ровно на invariant-check (описание + location).

Lane gate и ручной вердикт разделять.

**RESULT-LOOPINV.md**, ≤ 30 строк:
- таблица 3 строк;
- вывод: применим ли loop contract к внешнему циклу на пине;
- что дальше потребовалось бы для unbounded safety: внутренний цикл `insert_tail`, контракт `insert_tail`, другие
  циклы.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **LOOPINV ЗАВЕРШЁН**, одна стадия, затем стоп.
