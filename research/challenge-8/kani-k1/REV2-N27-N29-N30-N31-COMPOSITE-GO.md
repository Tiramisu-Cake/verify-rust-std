# REV2 copy-back/frame N27/N29/N30/N31 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`, после завершения `45886041869`. Порядок слотов N31, N27, N29, N30. Ожидание — четыре `VERIFIED`/`MATCHED` при 4 GiB group RSS, 120 с VT и 180 с cold wall на корень. [Ревью R1](REV2-N27-N29-N30-N31-COMPOSITE-REVIEW.md) · [Handoff](REV2-N27-N29-N30-N31-COMPOSITE-HANDOFF.md)

- Std `ee9eccad17d08988300e5b9e9e18d821889cdc92`, tree `b242e0d68a9666e2f6c965656cb9b27c6475df4a`.
- Control `17d0184168945306f80352c70993c215bef40c92`. Локальный review-trigger `f922daa92ae449a9929950958d020411314126c1` подтверждает тот же tree.
- Trigger tree `16daa4eabbb186bd4822fbe79a3d56dfb74d89a7`, единственный parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1. Actions variable `CH8_REV2_N26_N31_COPY_BACK_TRIGGER_TREE=16daa4eabbb186bd4822fbe79a3d56dfb74d89a7`.
- SHA-256 request `68289a93e8e1b3ec3617d53fb5f6eb7fbaa9714381d9d8699872731c4e89d249`, roster `6206fc1d9f76cc8e84129c1aecb99e36ab8b38ddd41d7f9152a9a0591a82ecbd`, bundle `2f3cc01614f61dd7fd7d4dcff9d17f324cd6a9ba405ff696601649247e94099e`, source bindings `f43a446614cbc20a889b75bd2916ff14c7e559480138ae67935fa79065ff5acb`.

В будущей строке допуска (R1.1) сквозное нативное свидетельство ограничено четырьмя конкретными контрольными масками. Положительные корни с `RSS_LIMIT` остаются без вердикта. Полный байтовый домен требует составного графа и успешных проверок copy-back/frame. Для R1.3 перечислить места `smallsort.rs:362/425/722/885/918/1034`, чьи достижимые вызовы могут входить в grouped copy ID на фактическом маршруте. В новом корне группа привязывается к единственному `copy_nonoverlapping` на `rev2_n26_n31_copy_back.rs:46:14`. `ptr::write` и `ptr::read` в fixture к этой группе не относятся.
