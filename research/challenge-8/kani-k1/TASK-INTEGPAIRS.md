# INTEGPAIRS — четыре пары leaf + consumer на интегрированном дереве, same-Build (2 × 8 строк)

**Выдано координатором 2026-11-03; каждый dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-integpairs**, ветка **experiment/kani-k1-integpairs-20261103** от **415044485b599f6337387650f0dfdefea8d5fb42**:
  терминальный коммит PARTTREE-INV2 `6ff24c756c` плюс cherry-pick cap-коммита `e8e238db9d`. Integrated library commit
  `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`, library tree `a45388ac593c809405558ea0c27599f487b17e4e`; inventory 438
  подтверждён INV2. Library **не менять**.
- Slug **integpairs**, stable owner **k1-merge**. Dispatch только после terminal/accounting WRAPMORE G2 (тот же owner).
  Новые stage/ledger/UUID/request_id `integpairs-*`.
- Project cap **$93.96**, свой cap **$3.00**. Два плановых Build, retry нет. Один compile-error repair на стадию — только
  если own spent + reserve ≤ cap и project ≤ cap.
- Tooling base для check-tooling: **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (= frozen 30f77e85, изменён только
  CAP_USD в k1g.sh).
- Окно: main 240 мин + closeout 30 мин.

## Цель

Впервые прогнать на интегрированном дереве четыре композиции так, чтобы leaf и consumer каждой пары прошли **в одном
Build** — на одном source/tree/profile. Это проверка интеграции и частичное закрытие «integrated proof matrix NOT_RUN»
([parttwotree/PROOF-MATRIX.md](research/challenge-8/kani-k1/parttwotree/PROOF-MATRIX.md),
`parttwotree/proof-matrix.tsv`). Это **не** перевод в ordinary.

## Exact rows

Префикс `slice::sort::shared::smallsort::verify::`. Перед GO сверить каждое имя с proof-matrix.tsv и cfg-on inventory
дерева. Если имя расходится — стоп и ко мне.

| Build | Пара | Leaf | Consumer | Контроли / baseline (expect) |
|---|---|---|---|---|
| G1 | network u8 N9 | `network::netcomp::netcomp_leaf_u8_n9` | `network::netcomp::netcomp_composed_u8_n9` | `netcomp_wrong_cmp_u8_n9`, `netcomp_count_negative_u8_n9` (FAILED, literal из matrix) |
| G1 | network u64 N9 | `network::u64nine::u64nine_leaf_u64_n9` | `network::u64nine::u64nine_composed_u64_n9` | `u64nine_wrong_cmp_u64_n9`, `u64nine_count_negative_u64_n9` (FAILED, literal из matrix) |
| G2 | general u8 N9 через merge-контракт | `merge::merge_scratch48_contract_u8_n9` | `bridge::bridgenine_caller_u8_n9` | `bridge::bridgenine_direct_u8_n9` (baseline SUCCESS), `bridge::bridgenine_payload_flip_u8_n9` (FAILED, literal) |
| G2 | network u8 N13 | `network::netcomp::netcomp_leaf_u8_n13` | `network::netcomp::netcomp_composed_u8_n13` | `netcomp_wrong_cmp_u8_n13`, `netcomp_count_negative_u8_n13` (FAILED, literal) |

Expectations, literals и `expect_check` брать из proof-matrix.tsv и исходных RESULT (NETCOMP2, U64-N9, BRIDGENINE); в
PREBUILD — таблица со ссылками. Unwind — из source каждого root.

## Профиль и бюджет

- measurement, gcb-e2-standard-4, controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani 9461e07a.

Резерв каждого Build **(8×10+30)×$0.0135 = $1.485**; оба — $2.970 ≤ cap $3.00. Project ≤ 2 unfinished, ≤ 1 на k1-merge;
global spent + reserves ≤ $93.96.

**Порядок.**
1. PRE-BUILD G1 → GO → dispatch → `k1g.sh wait BUILD` в фоне.
2. После terminal/accounting G1 — PRE-BUILD G2 → GO.

G2 запускается при любом proof-исходе G1, кроме общего compile-blocker. OOM в G1 — факт: составы не меняем, строки не
дробим.

**PRE-BUILD каждого Build:**
- identities и tree;
- tooling diff против e8e238db9d;
- name check против inventory;
- для каждой пары leaf/consumer: T, категория F (fn-pointer или function-item), значение CMP, домен пробы и её передача,
  backing/offset, prefix/scratch/init/frame, цепочка binding actual call → adapter → summary;
- covers и literal table;
- budget/slots.

Коммиты research — `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, затем стоп до GO.

## Gate и RESULT

**Gate.**
- Положительные строки: SUCCESS, 0 failed checks, все declared covers.
- Отрицательные: FAILED только по точному literal/requires из matrix, со своими covers.
- Пара засчитывается только при обоих положительных (leaf и consumer) в одном Build.

Общего «всё SUCCESS» нет.

**RESULT-INTEGPAIRS.md**, ≤ 50 строк.

По каждой строке:
- status, failed/total checks, unreachable, covers, VT;
- пик CBMC по строке;
- **driver**: пакетный пик плюс то, что можно привязать по времени при jobs1 (отметки «Checking harness» и series
  driver ~30 с), с явной погрешностью; неизмеренное — UNKNOWN.

По каждой паре — таблица доменных полей leaf/consumer, перечисленных выше.

Разделить положительные строки и намеренные FAILED-контроли. Матрица после стадии — PARTIAL: 16 строк, остальные 39 —
NOT_RUN.

**Без интерпретации.** Не утверждать «наклон GiB/consumer» как константу и не переносить на macOS: в RESULT только
измеренная динамика.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **INTEGPAIRS ЗАВЕРШЁН**, одна стадия, затем стоп.
