# UNSTABLEZST — unstable ZST dispatch safety с `zst_aware_less`

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-unstablezst**, ветка **experiment/kani-k1-unstablezst-20261103** от
  **5fc77d446f** (ZSTPROBE: v6 + tooling e8e238db9d + opt-in `network::zstprobe`).
- Slug **unstablezst**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `unstablezst-*`.
- Project cap **$93.96**, свой cap **$1.30**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e8e238db9d.
- Окно: main 150 + closeout 30 мин.

## Контекст

- **SAFETYGAPS:** `dispatch_safety_unstable_zst_n8_9_12_13_17` (компаратор `volatile_reading_less::<()>`) — TIMEOUT
  > 600 с, CBMC ≥ 7.97 GiB.
- **ZSTPROBE**
  ([RESULT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/5fc77d446f/research/challenge-8/kani-k1/RESULT-ZSTPROBE.md)):
  - в трёх проверенных in-core фикстурах на этом пине `read_volatile::<()>` дало pointer-check failures (standalone
    и другие ZST не проверены, причина не установлена);
  - тот же stable ZST-root с `comparators::zst_aware_less` — SUCCESS 194.8 с против 345.9 с с volatile.

Проверяем, что unstable ZST с тем же исправлением укладывается в 600 с.

## Source scope

Только `verify/network/zstprobe.rs`: дописать roots рядом с `zst_stable_dispatch_aware_*`. Существующие roots,
`dispatch_safety_fixed`, компараторы и `network.rs` не менять.

Roots, `#[kani::proof]`. Тело — копия смысла `dispatch_safety_fixed::<(), N, false>` в том виде, как root 1 ZSTPROBE
копирует stable-вариант:
- actual `<() as UnstableSmallSortTypeImpl>::small_sort`;
- тот же panic stub (`panic_on_ord_violation → assume_order_violation`), unwind 65 и covers, что у исходного unstable
  root; scratch unstable-вызову не нужен;
- по смыслу отличается только компаратор `comparators::zst_aware_less::<()>` (any bool, но другой тип F и `ptr::read`
  вместо `read_volatile`). Новые имена/пути helper допустимы.

| # | Root | Длины |
|---|---|---|
| 1 | `zst_unstable_dispatch_aware_n8_9_12_13_17` | 8, 9, 12, 13, 17 |
| 2–6 | `zst_unstable_dispatch_aware_n8`, `_n9`, `_n12`, `_n13`, `_n17` | по одной |

Covers каждой длины и family end — как у исходного root.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+6);
- rustfmt;
- без warnings.

## Пакет

6 строк, measurement (expect SUCCESS):
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (6×10+30)×$0.0135 = **$1.215**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge. Параллельно может идти CELLSPLIT (k1-network).

PRE-BUILD содержит:
- semantic diff root 1 против исходного `dispatch_safety_unstable_zst_n8_9_12_13_17` (по смыслу — только компаратор);
- маршрут unstable для `()` по source: какая ветка `small_sort` берётся на каждой длине;
- hashes, budget.

Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в
фоне.

## Gate и RESULT

**Gate root.** SUCCESS, 0 failures, все covers. Root 1 — кандидат в v7 только при SUCCESS, всех covers и VT ≤ 300 с;
иначе рассматривается полный набор успешных per-length roots с тем же порогом. Финальный допуск — после fork-CI v7.
Старый volatile-root остаётся TIMEOUT; новый результат учитывается отдельно.

TIMEOUT/FAILED — bounded facts. Для FAILED — bounded `k1g.sh log-grep`. Настоящий counterexample — немедленно мне.

**RESULT-UNSTABLEZST.md**, ≤ 30 строк:
- таблица 6 строк: status, VT, checks, unreachable, covers, CBMC RSS;
- вывод: закрыт ли unstable ZST-домен и каким root;
- кандидат в v7 (≤ 300 с).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **UNSTABLEZST ЗАВЕРШЁН**, одна стадия, затем стоп.
