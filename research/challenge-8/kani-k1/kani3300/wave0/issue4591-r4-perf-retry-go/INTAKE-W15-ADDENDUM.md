# W15 — выдать сейчас: terminal intake attempt 1

Все три workflow фактически terminal. Выполни TASK-KANI-4591-R4-FULL-CI-INTAKE-W15.md и INPUTS из **a36150fb0df93b81b9af2884f83b362e75c94b38**. Обязательное дополнение: при возможном параллельном perf retry этот intake остаётся **attempt 1**. Используй sealed ATTEMPT-1-NATIVE.json и явные `/attempts/1` endpoints. Latest-run attempt 2 не подменяет прежнюю попытку.

Полный native состав: 12 jobs, 11 SUCCESS, один perf FAILURE. Причина runner communication/CPU-memory и s2n-quic — COORDINATOR_REPORTED, independent cause UNKNOWN. Сохрани исходные семь деклараций/5 positive/2 expected semantic negatives, suite-vs-named-property ограничения, историю r3, текущую публикацию/источник и provenance. Дополнительных запусков/бенчмарков/компилятора/сырого логирования/архивов нет.

Выход только новый immutable `kani3300/wave0/issue4591-r4-ci-intake/head-b3019ab3f9/`, собственный manifest/HANDOFF/точный commit. Никаких PR-DRAFT/PROPOSED-PR/внешних файлов, source edits, ledger/accounting, push, CI или memory-plan реализации. Root отдельно проверяет READY.
