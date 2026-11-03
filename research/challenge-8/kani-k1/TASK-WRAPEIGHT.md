# WRAPEIGHT — фаза D1: контракты-обёртки на N8/N9 там, где N4 был дешёвым

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-wrapeight**, ветка **experiment/kani-k1-wrapeight-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library tree + K-1 tooling + cap 93.96).
- Первым library-коммитом перенести WRAPMORE: `git cherry-pick 0bf64c1c32 716e094b61`. Это только `verify/wrap.rs` и
  `verify/wrap/more.rs`. Проверить, что tooling и прочие файлы не затронуты, и записать в PRE-BUILD tree-hash.
- Slug **wrapeight**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `wrapeight-*`.
- Project cap **$93.96**, свой cap **$1.00**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Окно: main 150 + closeout 30 мин.

## Контекст

WRAPMORE
([RESULT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/0f034ceb09/research/challenge-8/kani-k1/RESULT-WRAPMORE.md)):
обёртки на всех пяти доменах при N2 и N4. Время при N4:

| Путь | N4 |
|---|---|
| Stable Cell | 152 с |
| Unstable Cell | 84 с |
| Unstable u8 network | 91 с |
| Stable Freeze general | 511 с |
| NonCopy general | 402 с |

General на N8 не проверяем: N4 там уже дорогой. Пробуем, как далеко идут дешёвые пути.

## Source scope

Только `verify/wrap/more.rs`. N4 targets жёстко задают длину 4 и для новых harnesses не подходят. Поэтому добавить
четыре новые fixed-N контрактные функции и четыре PFC-root по образцу `*_n4_backing6`:
- full any backing `N + 2`, active span `1..N+1`, оба sentinel-frame; для Stable Cell — scratch-frame как в N4;
- requires region и canonical fn pointer;
- modifies;
- ensures key-order и full-value count `old(count) == count` с независимой full-u8 пробой;
- исходный unwind 16 с unwinding assertions.

Старые targets, helpers, roots и guard не менять.

| # | Root | Путь |
|---|---|---|
| 1 | `stable_cell_n8_backing10` | Stable blanket → insertion |
| 2 | `unstable_cell_n8_backing10` | Unstable blanket → fallback insertion |
| 3 | `unstable_byte_n8_backing10` | Unstable Freeze Copy u8 → network, insert_tail |
| 4 | `unstable_byte_n9_backing11` | то же, ветка sort9_optimal |

Ожидание каждой строки — SUCCESS. TIMEOUT допустим как измерение.

Static:
- ordinary 202 и ordinary-PFC 36 неизменны;
- cfg-on: 392 после переноса WRAPMORE, 396 после четырёх новых roots; общий opt-in/PFC состав считать отдельно, не
  прибавлять к ordinary 36;
- exact name-set delta;
- rustfmt;
- без warnings.

## Пакет

4 строки, measurement:
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (4×10+30)×$0.0135 = **$0.945**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge. Параллельно может идти PANICPROBE (k1-network).

PRE-BUILD содержит:
- semantic diff новых roots против `*_n4_backing6` (отличаются N и backing);
- маршрут u8 N8/N9 по source;
- hashes, budget.

Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в
фоне.

## Gate и RESULT

**Gate root.** PFC SUCCESS, 0 failures, все covers (covers описывают полный N). TIMEOUT/FAILED — bounded facts, без retry. Настоящий
counterexample — немедленно мне.

**RESULT-WRAPEIGHT.md**, ≤ 30 строк:
- таблица 4 строк: status, VT, checks, covers, CBMC RSS;
- обновлённая матрица «impl × N» для обёрток;
- кандидаты в v7: только SUCCESS, все covers и ≤ 300 с, затем fork-CI.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **WRAPEIGHT ЗАВЕРШЁН**, одна стадия, затем стоп.
