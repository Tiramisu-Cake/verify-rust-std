# A1 R/C/G checkpoint — 2026-10-17, NO-GO / NOT_RUN

Source commit `bc2af77223428df14b61300a81eb99541c49723e`; owner `select-sort4`; branch
`research/night-select-sort4-cloud-2026-10-09`; worktree
`/root/verify-rust-std-select-night`.

Сессия 00:28:49Z–01:46:25Z. Основной deadline 02:28:49Z, finish-only 02:58:49Z
не исчерпаны: остановка по инженерному NO-GO, а не по якобы истёкшему времени.
Владелец прямо разрешил checkpoint без расхода Build, если безопасный кандидат
не подготовлен. Решение не выдаёт частичный набор проверок за первую матрицу.

## Результат и первый blocker

**Первый установленный blocker запуска:** P1 gate пока не связывает полные
required/impl signatures, scoped `Self,F`/regions/clauses с actual AST исходного
`small_sort` и не сравнивает целиком native pre, returning и unwind subtrees
под явной positional alpha map. Threshold-only gate и проверка arity/callee не
подтверждают этот обязательный интерфейс. Body small_sort не доказывался.

Также не завершены полный 26-row execution/admission и N-false31 lifecycle.
False31 меняет verified bytes: ему нужны оба threshold body/conformance proofs
для **его собственной** verified/original пары перед receipt. Receipt исходного
positive использовать нельзя. Повторяемый полный paired export/refinement для
каждого focus ещё не обоснован по 900s deadline; reviewed exact-pair/tool/Build
cache не реализован. `run(a)` намеренно только закрытый preflight. Coordinator,
lane launcher и recipe не подключены к новому эксперименту.

Следующий шаг: сначала реализовать полный P1 native-interface observation gate
на уже экспортируемых compiler tables/types и actual AST; сравнивать все native
subtrees, без name-only/resource-count сокращений. Затем закончить все строки,
N-false31 exact-pair body proofs, classifier provenance и бюджетную оценку;
провести независимый review и закрепить proof/infra/recipe pins до нового
разрешённого Cloud запуска. Никакой автоматический второй или отложенный Build
этой записью не разрешён.

## Что подготовлено — только source-reported

- R opt-in exporter/schema/decoder/translator: compiler identities, method F,
  отдельные scoped aliases/owners, полные clauses, порядок Self/F/late regions.
- C/G: native envelope с returning-only `16<=result<=32`, distinct actual impl
  aliases/prototypes, исходный common trait call, отказ legacy redirect.
- Focus связан с actual `Body.span.lo`; `fnSigSpan.lo` отдельно связывает native
  diagnostic. Caller focus проверяется до receipt, полная impl inventory/IDs —
  до любой body/call translation. Observer не может consume small_sort summary.
- Source constructor, bounded synthetic MIR mutations/transport, paired compiler
  inventory, MIR/AST binding, native threshold AST gate, classifier/admission и
  source/tool/Build-bound receipt; staged runner остаётся draft, UNRUN.
- Независимый [review](A1-RCG-INDEPENDENT-REVIEW-2026-10-17.md) закрыл локальные
  source findings, но не подтверждает компиляцию, API compatibility или proof.

Есть условный source-риск: global Body.inputs encoder смешивает distinct
same-depth `ReBound(Anon)` IDs. Как именно lowered actual сигнатуры, **не
установлено** без paired export. Distinct-region gate должен отказать при
потере IDs. Это не наблюдённый SmallSort failure; global encoder не расширялся.

## Точные source pins

| Компонент | SHA256 / commit |
| --- | --- |
| VeriFast base | `f76012fb518703b1d98e243ac4f487f16877cfcb` |
| Selected translator base | `e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64` |
| R patch | `4c0a43a10d5e023af7c190ed801546cf9877448d8dde65b39a773d68707f5a5e` |
| C/G patch | `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e` |
| Result translator | `4e1c7e12dc67f3ea9f6305ea495f9503c170ad624612d0839dc8e8f00ae3a00d` |
| Source profile | `fbdb28dc43582b9b9bb695929f0b8200148761ed66c2c7b78def0df1da7b75d0` |
| Frozen kernel | `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c` |
| Compiler | `nightly-2026-09-25` / `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f` |

[Profile](A1-RCG-PROFILE-2026-10-17.json) содержит before/after hashes трёх
изменяемых tool files, четыре frozen focus-semantics pins, 12 helper hashes,
std source pins и все 26 NOT_RUN. `proof_sha=null`, `infra_sha=null`,
`profile_accepted=false`, `cloud_build_enabled=false`: это **не** run-ready pins.
Kernel, memory/alias/layout, prelude, refiner и runtime std не изменены.

## Проверки, evidence и accounting

96 изолированных синтетических tests восьми parser/classifier modules — PASS.
Imports/entrypoints просмотрены; compiler/exporter/proof функции локально не
вызывались. Python AST parse и exact R→C patch application/result SHA checks —
PASS. Whitespace cleanup после tests подтверждён равенством Python AST.
Эти результаты ничего не доказывают о actual threshold bodies или интерфейсе.

| Первая матрица | Фактический статус |
| --- | --- |
| OFF; P0a/P0b/P0c/P-dispatch/P1 | NOT_RUN |
| Все 13 N-* controls, включая representation-only alpha-valid | NOT_RUN |
| Свежие R1–R7 | NOT_RUN |

Builds **0/1**, Cloud charge **0/960 s**; queued/running Build отсутствует у
этой сессии, request/token/slot не создавались. [Ledger](BUDGET-A1-TRAIT-CONTRACT-2026-10-17.json)
закрыт без расходов, 960 unspent retired без переноса. Старые ledgers/evidence
не изменялись; `download_verified` не устанавливался. Brief отсутствует, потому
что Build не запускался; **никаких gates, подтверждённых Brief, нет**. Full logs,
Cloud Logging и raw archives, включая локальные копии, не читались/скачивались.

Threshold/interface hypothesis не подтверждена. A1/A2 NOT ACHIEVED, index 15%,
experimental profile UNACCEPTED. Для полного A1 нужен отдельный последующий
actual small_sort→helper proof; дальнейшие P2/A2/ZST/resources/copies/sort8 не
получают credit или разрешение этим checkpoint.

## Сохранённые инструкции

Pre-existing Evidence Brief изменения оставлены локально вне commits:
AGENTS.md, AGENT-RUNBOOK.md, INFRASTRUCTURE-TASK.md, PROGRESS-REVIEW.md,
WORK-POLICY.md, cloud-build/PARALLEL-BUILDS.md, cloud-build/README.md и новый
EVIDENCE-BRIEF.md. Проверены неизменные hashes AGENTS
`5ce177461ab8a964d3e530d8b0b49edb48021117a9c6e35ec5c7bb74f34c01d1`
и EVIDENCE-BRIEF
`f9a04c1c8bd940c79c0f07eda421a7cb03a28f44ad33cb8407d4f0de3d51f170`.
Предыдущий STATUS сохранён [без изменения claims](STATUS-BEFORE-A1-TRAIT-CONTRACT-2026-10-17.md).
