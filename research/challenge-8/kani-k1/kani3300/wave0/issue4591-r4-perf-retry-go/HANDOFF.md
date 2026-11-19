# READY: #4591 r4 terminal facts + one perf retry consent

Root согласен на **один perf-only retry**, prospective attempt 2, при неизменных reviewed head/tree/workflow и немедленной проверке единственного failed job. См. GO-REQUEST.md/json. Координатор dispatch/accounting отдельно; root не запускал CI.

Native snapshot attempt 1 сохранён до retry: 12 jobs, 11 SUCCESS, perf FAILURE. W15 может независимо оформить attempt-1 intake по INTAKE-W15-ADDENDUM.md и исходному task a361. Runner-loss причина остаётся сообщением координатора, независимая причина UNKNOWN.

Без source/workflow/PR-текста/ledger правок. Без автоматического второго retry, source fix или CI. Все exact pins и source/workflow hash checks — ROOT-CHECK.json и GO-REQUEST.json.
