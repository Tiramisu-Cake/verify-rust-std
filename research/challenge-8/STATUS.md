# Challenge 8: компактное состояние команды

Snapshot 2026-10-10, Europe/Moscow. **Docs-only; новых proof-фаз/бюджетов нет.**
Миссии сохраняются по [WORK-POLICY](WORK-POLICY.md); более свежие конкретные
поручения/checkpoint собственных веток приоритетнее этой сводки. Полный Challenge,
whole sort4, insertion и общий merge не квалифицированы. Статус profile отдельный.

| Миссия/owner | Последнее проверенное обязательство | Первый blocker | Следующий шаг после отдельного возобновления |
| --- | --- | --- | --- |
| select/sort4 (`select-sort4`): full actual sort4/callers, затем sort8 | C1 caller bridge достиг source/MIR/AST entry boundary; actual sort4 invocation и whole caller NOT_RUN. Никакая supplied C1 premise не устранена полной admitted теоремой | Strict selected-path admission/dead code; затем generic/ZST/MU ownership и identity. Experimental slice projection не accepted | Sound exact path correspondence и admission controls, затем тот же C1 bridge |
| merge/insert_tail (`merge`): actual insert_tail, guard/Drop/CURRENT recovery, затем общий merge | Новее lifetime NO-GO: incoming-origin v3, local draft evidence. Build 6cf7f205 terminal FAILURE; часть scalar span controls выполнена, origin/affected-path gates неполны; actual generic rerun NOT_RUN | Origin admission/correlation и generic runtime extent, включая unit/ZST; full Drop/comparator/recovery не закрыты | Закрыть точные origin/affected-path gates и обосновать runtime extent в разрешённом tool scope |
| VeriFast (`verifast`): review, интеграция, подготовка подачи | Latest RESULT: full Linux make test PASS; внешний Build FAILURE из-за collector, saved-data service replay PASS, READY_FOR_USER_REVIEW | Приёмка/integration tool profile и применимость consumer proofs остаются отдельными от suite PASS | Review пакета и integration gates; upstream publication только по отдельному поручению |

Proof sessions: select CLOSED (934/3600, 2666 retired); merge-origin deadline
2026-10-09 21:46:40 UTC истёк (394/3600, ledger ещё AUTHORIZED, 3206 не являются
доступным бюджетом). VeriFast fullmake CLOSED (950/3600, 2650 retired).
По прочитанным записям active_build отсутствует; это не live API/coordinator audit.
Чужие ledgers/worktrees этой документационной задачей не изменены.

Evidence/checkpoints и точные прочитанные revisions —
[датированный snapshot](checkpoints/TEAM-DOCS-2026-10-10.md).
Он сохраняет расхождения STATUS/ledger и различие raw Build/replay/result.
Технический baseline COMPLETION-PLAN на 11:00 МСК 9 октября — история, не
последнее состояние. Main ведёт индекс; рабочие ветки держат свой компактный
STATUS и историю отдельно по [runbook](AGENT-RUNBOOK.md#компактный-status-и-существующая-отчётность).

Следующее разрешённое действие в этой ветке — review documentation draft PR.
Принятие общих docs всеми тремя агентами — по [ADOPTION](ADOPTION.md), на безопасной
границе без чужой research history. [Инфраструктурная работа](INFRASTRUCTURE-TASK.md)
только поставлена; ни cache, ни filters, ни slots здесь не реализуются.
