# Независимый адресный review F1

Один built-in reviewer `f1_independent_review`, GPT-6 Luna/high. Read-only review pinned repair и его checks; reviewer не правил files и не запускал compiler/extraction/refiner/verifier/Cloud или новые tests. Основной агент сохраняет ответственность за итоговый пакет.

**GO.** Diff от exact runner420188dd состоит из одного admission hunk (13 добавленных/4 удалённых строк). Перед dict проверяются direct outer SwitchExpr, отсутствие default, ровно два допустимых clause, уникальные returning/unwinding и точные binders; missing/duplicate/extra/unknown/malformed arms не проходят. Literal False(location) сохранён. Candidate SHA `cb30a0a65e130b4bb38b99f609b3dcf929661185c3fbb9f6da6b845a0fb46d25`, base `3e3e1b917a7cc301fee16074a80f7470a98ebcc4d4eb04b61781e54cbcc28a51`, parser unchanged `a5f28d5feb9c3e07d2bb5ee6b19a29dc45ea782d5f51a1630f993124f20bd995` сверены.

Old reproduction независимо прочитан: old classifier принимает duplicate returning/unwinding через настоящий entrypoint. Fixed output сохраняет saved valid и отклоняет mutants; contracts в каждой мутации остаются равными. Восемь False/location cases переиспользованы. Tests читают собственные serialized files штатным parser, а не подменяют его результат.

Replay содержит все семь случаев; source/caller/glue admissions и scoped logs повторно проверены, positive fragment PASS сохранён, шесть raw INCONCLUSIVE и отсутствие fresh/v8 credit явно записаны. Saved MIR/body/canonical proof результаты переиспользуются, не исполняются.

Первое замечание reviewer: `cloud_failure_preserved=True` было присвоено без проверки source record. Основной агент исправил только reporting: обязательный `--build-record`, summary SHA проверяется по старому INPUTS.json, сверяются IDs/run_exit1/failure_class run-failed/acceptedfalse/API status FAILURE, source hashes входят в receipt. Reviewer адресно проверил исправление и заполненный повторный REPLAY.json: **GO, замечание закрыто**; все семь cases, шесть raw INCONCLUSIVE сохраняются. Classifier hunk при этом не менялся.

Итоговый GO относится к F1 classifier repair/tests/replay. Это не принятие tool/profile, B1/B2/O23, не receiver/end/retirement qualification и не actual insert_tail proof. Пакет не применён к активному merge runner.
