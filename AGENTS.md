> **Автономность proof-агентов, 2026-10-20:** Select/Merge сами ставят задачи по миссии и плану; исправления inventory/binder/frontend и новые experimental profiles не требуют отдельного согласования каждого blocker при сохранении гарантий, review и controls. [Полномочия](research/challenge-8/PROOF-AGENT-AUTONOMY.md). Новые задания задают окно/бюджет; активные inputs/T0/явные границы и роль maintainer сохраняются.

> **Роли SmallSort:** Select/Merge разрабатывают патчи; VeriFast maintainer принимает готовые опубликованные патчи для review/регрессий/интеграции/upstream-пакета. Новый proof-blocker/model design ему автоматически не передаётся. [Границы роли](research/challenge-8/VERIFAST-ROLE.md). Только роли verifast разрешён GitHub Actions CI готовых tool-патчей в Tiramisu-Cake/verifast; Select/Merge сохраняют Cloud Build lanes.

> **Evidence v0.11 — приоритет:** [краткий guide](research/challenge-8/EVIDENCE-READER-GUIDE.md). Brief → catalogue → refresh/info → locate/fragment → нужные страницы по next_offset/next_value_start. Пожизненной16-квоты и прежних лексических WITHHELD больше нет; соседний контекст/argv/environment читаются как данные. Не выгружать автоматически всё. Proof scope, T0, окна/бюджеты и coordinator сохраняются.

> **Процесс итераций, 2026-10-19:** [ранние checks → целевой proof → полная матрица](research/challenge-8/ITERATION-PROCESS.md). Service error-path tests обязательны для затронутого runner; использовать существующий Cloud preflight. Принять на безопасной границе без изменения активных inputs/T0. Измерять закрытые proof obligations отдельно от setup-работы.

## Evidence Brief — решение владельца от 2026-10-17

Для всех SmallSort agents, worktrees и reviewers действует
[Evidence Brief policy](research/challenge-8/EVIDENCE-BRIEF.md), с приоритетом над
противоречащими указаниями ниже и в старых phase cards/runbooks. После terminal
Build использовать `smallsort-brief BUILD_UUID`. Полные Build/verifier logs,
raw evidence archives и Cloud Logging не читать и не скачивать, включая локальные
копии и обход через connectors. Если Brief недостаточен или отсутствует — сообщить
ограничение; без raw fallback и без повышения proof credit. Отдельный admin audit
требует явной авторизации. Coordinator, budgets, owners и deadlines сохраняются.

# Instructions for coding agents

## Project and first reads

This fork is Igor's original Challenge 8 (SmallSort) verification project.
Before acting, read:

1. [Current status and phase](research/challenge-8/STATUS.md).
2. [Approved roadmap](research/challenge-8/PLAN.md), the phase document linked
   from STATUS, and the [operating runbook](research/challenge-8/AGENT-RUNBOOK.md).
3. [Research index](research/challenge-8/README.md),
   [Challenge requirements](doc/src/challenges/0008-smallsort.md) and
   [general rules](doc/src/general-rules.md).
4. The actual SmallSort source, relevant specification and proof/runner files
   for the authorized task.

Work in `Tiramisu-Cake/verify-rust-std` on `challenge-8/research`. Inspect the
working tree, remotes, branch heads and Actions runs; recorded status is dated.
Preserve unrelated user changes. No force-push or destructive reset. Always use
explicit repository arguments so GitHub commands cannot target upstream.

## Authorization: autonomous within an agreed phase

The user's latest instruction takes precedence. `STATUS.md` is the single
current checkpoint; dated handoffs, reassessments and archived "next" instructions
are historical evidence, not standing authorization.

An explicit stop remains in force until the user resumes experiments or
explicitly approves a named next phase. A status check, documentation edit or
approval of operating rules alone is not that authorization. When STATUS records
a named phase as READY/approved, a continuation request can start that phase
without repeating the approval. Historical closed phases remain closed.
While paused, do only the requested read-only/documentation work: no proof
implementation, verifier changes or workflow dispatch.

After authorization, autonomously edit, commit, push, dispatch, inspect and
iterate WITHIN the phase and tool-profile allowlist linked from `STATUS.md`.
Do not ask the owner to click Run workflow or inspect routine failures.
A green fixture permits the next already-agreed step, not a new architecture,
tool extension or phase. At a phase boundary, unresolved material decision or
new trust requirement, checkpoint and ask the owner before expanding scope.

One relevant hosted experiment at a time. Keep `workflow_dispatch` as the only
research trigger; no push, pull_request or scheduled triggers, speculative jobs
or duplicate dispatches. No upstream PR, external comments, tool application or
bounty submission without separate user authorization.

## Hard rule: no verification or builds on the user's server

The server is an editing and orchestration machine only. ALL compilation,
verification and executable tests run on GitHub-hosted Actions runners.
Never run Kani, CBMC, VeriFast, Cargo builds/checks/tests, rustc, bootstrap/x.py,
research runners/extractors, scripts/run-kani.sh, or containers/remote subprocesses
that perform these tasks on the server. Do not install build/verifier dependencies,
run a "quick" compile check, use self-hosted runners or move to paid compute.

Local reading/editing, git/gh operations, reading compact evidence reports,
`git diff --check`, `bash -n` and lightweight non-executing document/YAML parsing
are allowed. GitHub failure is not permission to verify locally.

## Frozen trust boundary and proof integrity

Develop our own specifications/proofs; do not import other solutions' proof code.
Verify the actual repository std source without changing its runtime behavior,
algorithms or generic signatures. Keep experiments under `research/challenge-8`;
injection/exact-source extraction happens only in disposable Actions checkouts.
Do not commit generated/injected source, downloaded logs or build output.

Verifier pins, parser/translator semantics, kernel, memory/alias model, prelude
and refinement checker are frozen at the phase's explicitly named profile.
Existing experimental patches are NOT a blanket license to use or extend them.
New semantic changes or a different patch chain require a separate decision,
written rationale, trust/admissibility review and an explicit regression gate
BEFORE implementation. A "kernel-free", "frontend-only" or proof-only AST rewrite
still changes trusted semantics and is subject to this rule.

Before each experiment, record the actual std obligation, a falsifiable
hypothesis, exact domain and full target normal/unwind posts, tool profile,
expected positive/negative stage/predicate/location, and outcome-to-next-decision
mapping. Distinguish a deliberately partial diagnostic from the target contract.
Repeated failures without new evidence require reassessment, not more patches.

Do not obtain green results by weakening posts, deleting resources/assertions/
covers, adding Freeze/Copy/purity restrictions to unrestricted safety, assuming an
ownership bridge, hiding unsupported cases or disabling unwind, leak, dead-code,
uninitialized/validity or refinement checks. Safety and ordering premises are
separate. A pointer rewrite must preserve provenance/permissions and applicability
to the actual source; satisfying the refiner alone is not justification.

Verify an actual callee at the same source version before using its summary.
Isolate fixtures so an unrelated new helper cannot block baseline controls.
A negative counts only at its intended proof obligation; setup, frontend,
unsupported-operation and unrelated helper failures are not intended negatives.
Green microfixtures or regression counts prove neither a whole std function nor
the soundness/admissibility of a patched verifier. Use the Evidence Brief; do not inspect full logs or download artifacts.

## Evidence and continuity

Follow the runbook's exact-SHA dispatch/monitor loop. A changed source requires
a NEW run; rerunning an old run checks old code. After meaningful results, update
the compact `STATUS.md`, append evidence to `EXPERIMENT-LOG.md`, and update
`coverage.md`/the relevant design note when their claims change. Keep operating
instructions free of chronological run logs. Preserve failures, source/run/tool
identifiers and historical evidence; a documentation commit is not a proof run.

During an active authorized session, poll the specific run and continue routine
within-phase work; do not offload monitoring to the owner. Report concisely in
Russian. On stop or session limits, save a checkpoint with exact state, active
run ID (if any), draft status and the next permitted action. Do not promise work
after the session ends. Documentation-only changes require no verification run.
