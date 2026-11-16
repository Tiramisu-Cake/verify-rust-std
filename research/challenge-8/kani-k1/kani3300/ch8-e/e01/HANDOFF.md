# E-01 — одна intake стадия завершена

Вход: g0 `56b4134b5a62b9fba6461afcc94afe6a41c650a3`,
`TASK-CH8-E01-INTAKE-W15.md`. Результат: **STOP E текущего encoding**,
intake пакет готов. [RESULT.md](RESULT.md): классификация всех 40 строк,
причины 10 missing exports, exact source chain U/S, issues и границы claims.
[EVIDENCE.json](EVIDENCE.json): производные факты с hashes/member coordinates.
[MRE](MRE/README.md): 10 exact single-file fixtures, отдельный NOT_RUN primitive
candidate и [неопубликованный issue draft](MRE/ISSUE-DRAFT.md).

- E-Q ON: intended frontend refusal; OFF: ignored exists даже в isolated positive.
  Base failure false mutant не чистый oracle. SMT workaround не проверен.
- E-H S ON: shadow-field assigns при достаточном user frame; loop frame включает
  explicit targets/generated locals, а shadow allowance есть только в function
  contract path. Доказано source/diagnostic соответствие; transformed GOTO не связан.
  Оба negative также дают intended uninit-read, но с assigns failures.
  U ON останавливается на отдельном unsupported union/layout check.
- E-S: setup E0425; source fix namespace `kani::arbitrary::...`, затем новая
  калибровка. Нельзя выводить невозможность uncapped storage из compile error.
- Scalar ON SUCCESS имеет 3 предупреждения arity/nondet injected init helper;
  source-level init invariant этим не установлен (related upstream #4796).

Следующее отдельное задание: E-S namespace; primitive H positive/no-write/OFF
и fix private loop bookkeeping с сохранением init relation/false bits; отдельно
scalar helper lowering. Q — только согласованная solver/encoding калибровка с
true/false controls. Полный insertion и arbitrary-length E остаются STOP до gates.
Не расширять user frame на shadow/все payload bytes и не ослаблять checks.

Проверки: zip digests, 40 receipt identities/fixture hashes, 30 complete exports
и 10 exact bounded-tail diagnostics, pins source ranges, static JSON/Markdown
и `git diff --cached --check` — PASS.
Исходные exports/receipts/ledgers не изменены; proof credit NONE, B2 нет.
Новых runs, push, CI, публикаций, ledger операций или локальных
cargo/rustc/Kani/CBMC не выполнено. Незакоммиченные чужие ch8-b/ch8-c-ctl не затронуты.
