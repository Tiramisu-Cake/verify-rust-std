# Challenge 8: компактное состояние команды

Snapshot 2026-10-10, Europe/Moscow; merge-origin повторно прочитан
2026-10-09T21:25:00Z–21:25:17Z. **Docs-only; новых proof-фаз/бюджетов нет.**
Миссии сохраняются по [WORK-POLICY](WORK-POLICY.md); более свежие конкретные
поручения/checkpoint собственных веток приоритетнее этой сводки. Полный Challenge,
whole sort4, insertion и общий merge не квалифицированы. Статус profile отдельный.

| Миссия/owner | Последнее проверенное обязательство | Первый blocker | Следующий шаг после отдельного возобновления |
| --- | --- | --- | --- |
| select/sort4 (`select-sort4`): full actual sort4/callers, затем sort8 | C1 caller bridge достиг source/MIR/AST entry boundary; actual sort4 invocation и whole caller NOT_RUN. Никакая supplied C1 premise не устранена полной admitted теоремой | Strict selected-path admission/dead code; затем generic/ZST/MU ownership и identity. Experimental slice projection не accepted | Sound exact path correspondence и admission controls, затем тот же C1 bridge |
| merge/insert_tail (`merge`): actual insert_tail, guard/Drop/CURRENT recovery, затем общий merge | Опубликованный incoming-origin closeout `9da02971`: два terminal Builds, свежие шесть span controls совпали; origin/normal-unwind gates OPEN, actual generic rerun NOT_RUN, candidate NOT_FOR_INTEGRATION | Origin admission/correlation и generic runtime extent, включая unit/ZST; full Drop/comparator/recovery не закрыты | Закрыть точные origin/affected-path gates и обосновать runtime extent в разрешённом tool scope |
| VeriFast (`verifast`): review, интеграция, подготовка подачи | Latest RESULT: full Linux make test PASS; внешний Build FAILURE из-за collector, saved-data service replay PASS, READY_FOR_USER_REVIEW | Приёмка/integration tool profile и применимость consumer proofs остаются отдельными от suite PASS | Review пакета и integration gates; upstream publication только по отдельному поручению |

Proof sessions: select CLOSED (934/3600, 2666 retired); VeriFast fullmake CLOSED
(950/3600, 2650 retired). Merge-origin: main deadline **21:16:40Z** 9 октября;
после него только завершение начатого, до absolute deadline **21:46:40Z**.
При создании PR в **21:15:52Z** основное окно ещё шло: вывод об истечении был
ошибочным. При повторном наблюдении в **21:25:17Z** absolute deadline ещё не
наступил, но опубликованный ledger владельца уже CLOSED с
**21:18:12.966107Z**: 774/3600, 2826 закрыты без переноса. Основание закрытия —
[closeout на точном SHA](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9da02971a162468cd06602585a0dcd4a1e8d67a1/research/challenge-8/cloud-build/incoming-origin/BUDGET.json),
а не окончание основного часа. AUTHORIZED в окне завершения сам по себе не stale.
По прочитанным записям active_build отсутствует; это не live API/coordinator audit.
Чужие ledgers/worktrees этой документационной задачей не изменены.

Evidence/checkpoints и точные прочитанные revisions —
[датированный snapshot](checkpoints/TEAM-DOCS-2026-10-10.md).
Он сохраняет первоначальные наблюдавшиеся факты, уточнение времени и более
свежий опубликованный closeout; raw Build/replay/result различаются.
Технический baseline COMPLETION-PLAN на 11:00 МСК 9 октября — история, не
последнее состояние. Main ведёт индекс; рабочие ветки держат свой компактный
STATUS и историю отдельно по [runbook](AGENT-RUNBOOK.md#компактный-status-и-существующая-отчётность).

Следующее разрешённое действие в этой ветке — review documentation draft PR.
Принятие общих docs всеми тремя агентами — по [ADOPTION](ADOPTION.md), на безопасной
границе без чужой research history. [Инфраструктурная работа](INFRASTRUCTURE-TASK.md)
только поставлена; ни cache, ни filters, ни slots здесь не реализуются.
