# PART2-FAST — измерить восемь исходных opt-in roots на v6 library

**Dispatch только после exact-packet GO координатора.**
Runtime: **Claude Code**, tmux4, исполнитель сам, **без субагентов**. Одна стадия на сессию.
Worktree `/root/verify-rust-std-kani-partfast`, ветка `experiment/kani-k1-partfast-20261102`; owner **k1-network**, новая стадия/UUIDs/request_id
`partfast-*`. U64-TEN-CALLER terminal; не возобновлять его ledger и не брать его library за базу.
База **MACSPLIT `4f4034527d3e3a26e4cd94e12ba6922e2b5e80e4`** с K-1 tooling;
library tree **d4ec476a7a001363e58f19948c188a9c2078e370** = Part1 v6
`d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`. Голый submission v6 dispatch не поддерживает.
Не merge PARTTWO-TREE/SPLIT31/U64/research changes: вопрос о восьми прежних roots неизменённого v6.
Project cap$88.96, **свой cap$2.00, ровно два плановых Build, повторов нет**.
Wall window main180min+closeout30min; T0 при фактическом старте. Каждый полный70min envelope плюс finishing
должен помещаться в действующий deadline. Metadata preparation не регистрирует phase и не даёт dispatch GO.

## Цель и точный состав пакетов

Установить current-tree GCB results для восьми уже существующих положительных opt-in roots;
это screen для будущего решения о v7, **не** перенос в ordinary и не изменение самих proof obligations.
Все имена ниже относительно `slice::sort::shared::smallsort::verify::`; request names — полные с этим prefix.

| Пакет | Exact root | Свойство исходного harness | Required covers |
|---|---|---|---:|
|G1|network::network_correctness_u8_n8|sortedness + full-value count|3/3|
|G1|network::network_correctness_u8_n14|sortedness|3/3|
|G1|network::network_correctness_u8_n15|sortedness|3/3|
|G1|network::network_correctness_u8_n16|sortedness|3/3|
|G2|network::network_correctness_u64_n10|sortedness|3/3|
|G2|network::network_correctness_u64_n11|sortedness|3/3|
|G2|network::network_correctness_u64_n12|sortedness|3/3|
|G2|network::insertion_permutation_u8_n15|full-value count of actual insertion suffix|2/2|

Read pinned `library/core/src/slice/sort/shared/smallsort/verify/network.rs`: network_correctness_fixed/cases,
strict_less, insertion_permutation_fixed/case, volatile_reading_less, count/prefix helpers, actual routes;
MACSPLIT native ordinary reference и существующий request/preflight workflow. Не выводить covers из одного имени:
сверить exact source inventory до GO; расхождение — blocker, не исправление source/covers в этой стадии.

Network roots: full any exact `[u8;N]`/`[u64;N]`, independent any typed probe, inferred **function-item F
strict_less::<T>**, ordinary `<`; без fn-pointer coercion, stubs или assumed input order.
N8 идёт через insertion offset1; N14..16 — sort13 +tail insertion; N10..12 — sort9 +tail insertion; merge нет.
При N≥9 исходный network harness **не утверждает whole-route count**, его не добавлять и не приписывать PASS.
3 covers — sort moves, fixed length returns, family end. N8 count остаётся исходным, full-width.

Insertion-permutation u8 N15: full any backing15/independent any u8 probe, offset13, actual insertion body,
прежний function-item volatile-reading comparator с arbitrary boolean results. **Нет sorted-prefix premise**:
вход включает произвольные исходные15 значений, а не только реальные network outputs. Sortedness не утверждается.
2 covers — insertion moves/preserves count и check reached end. Ordered StrictU8 summary здесь не подстановка.

## Неизменяемое и requests

**Library/runtime/harnesses/annotations/covers/tooling/workflows не менять.** Разрешены только собственные task,
PREBUILD/request/research reports/receipts. Ordinary202/PFC36 и static cfg-on384/opt-in182 сохраняются;
native inventory в этой стадии не запускать. Исходный name-set/domain source зафиксировать до submit.
Не брать новые wrappers/composed callers/full-count experiments вместо перечисленных roots.

Два отдельных4-row **measurement** requests: G1 и G2 ровно по таблице, expect SUCCESS для каждой строки.
Runner gcb-e2-standard-4 →k1-standard4,4CPU/16GiB/swap off; controls:true, kani_jobs:1,
uninit_checks:false, harness_timeout_minutes:10/600s per row, исходный unwind25/unwinding assertions.
Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12,
frozen tooling **30f77e859903df14b442ff9294d4fbbd44827f20**; check-tooling против него обязателен.
Никаких highmem/resource kind/solver flags/new instrumentation или отдельного list preparation.

Каждый reserve **(4×10+30)×$0.0135=$0.945**, общий план **$1.890≤cap$2.00**.
До каждого GO: own fact_spent+reserve следующего Build+резерв ещё не отправленного планового пакета≤cap;
актуальные global used/reserved/slots и **общий ночной лимит около$4** допускают действие.
INV2 имеет отдельный reserve$1.215/cap$1.25: не учитывать его дважды и не расходовать его резерв.
Project≤2 queued/running/unresolved, ≤1 на stable owner; unknown submit сначала разрешить через coordinator.

Сначала G1, затем G2 после terminal/accounting G1. G2 не зависит от proof SUCCESS G1: TIMEOUT/OOM/coverage
отдельных u8 roots не лишает смысла измерение u64/insertion rows. Общую compile/setup ошибку сначала классифицировать;
если она заведомо блокирует G2 с тем же source, не посылать такой пакет, записать NOT_RUN/HANDOFF.
Нет G1R/G2R, compiler repairs/code fixes, resource/semantic retries или новых фаз автоматически.
Ошибку preparation/request устранить до submit; после платного неуспеха — per-row facts и следующая разрешённая
независимая работа, без молчаливого увеличения caps/window. Полный envelope каждого dispatch должен помещаться в main.

PRE-BUILD: exact source/library/tree and tool/request hashes, root names/cfg/annotations/cover table,
неизменность обоих domains/F и ordinary202, existing validator/preflight, бюджеты/slots/deadline.
Metadata commits `[skip ci]`, publish без force. Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD`
в фоновом Bash task Claude Code; без Codex watch/CODEX_THREAD_ID, polling-субагентов/новых сессий.

## Gate и итог

По каждой строке: matching identities/profile, SUCCESS/0 unintended failures, все исходные covers.
G1/G2 gates отдельно; overall FAST PASS только при8/8 принятых строках. Timeout/OOM/UNKNOWN/missing row
оставляет её OPEN; неожиданный counterexample/UB/coverage failure сохраняется как failure, не expected negative.
Не принимать общий Cloud SUCCESS вместо per-row gate. Не приписывать memory peak каждой строке по агрегату:
CBMC row RSS и compiler/driver/process-sum **по Build** отдельно, missing поля UNKNOWN.

`RESULT-PART2-FAST.md` ≤40 строк: reviewed/source/library/tree/request/build/pin/tooling identities,
8-row table status/VT/checks/covers/CBMC RSS, отдельно packet memory peaks и gates, own spent/reserved.
Исторические organizer partition timings не считать новым Mac baseline. GCB SUCCESS≤600s — bounded result;
macOS/jobs3/600s с запасом400–450s пока OPEN, conversion factor не установлен.
Составить список кандидатов для audit report; FAIL/PARTIAL строки не удалять. Ни включения в ordinary,
ни v7/full organizer CI/PR submission здесь нет. Source unchanged: измерение не называть ускорением кода.

Evidence только bounded K-1 summaries/rows/peaks/targeted excerpts; Evidence Brief/Select-Merge к K-1 не относятся.
Raw archives/full logs/Cloud Logging/credentials/hidden configs/competing code не читать/скачивать.
Нет local cargo/rustc/Kani/proofs/deploy. Historical results/ledgers сохраняются.
Маркеры `REVIEW REQUEST <sha>` / `PART2-FAST ЗАВЕРШЁН`; одна стадия, затем стоп.
