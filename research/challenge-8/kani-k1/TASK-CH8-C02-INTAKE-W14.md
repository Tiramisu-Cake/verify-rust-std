# TASK — worker14: intake C-02 и итог C (короткая стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

C-02 run 43790257718 (sibling `b97c4d6cf6`, control `59b5c663e3`, std `597e54c5cb`); zip в scratch, raw logs не читать.
Координатор: group-01 COMPLETE — `c_merge_source_write_restore` FAILURE 279/1 ровно `Check that *dst is assignable`
(covers 4/4); `c_merge_source_read_only` SUCCESS 279/0 (covers 3/4 — один не satisfied).
Политика: [ACCEPTANCE-POLICY-BATCH.md](ACCEPTANCE-POLICY-BATCH.md).

1. Классифицировать обе строки; разобрать неудовлетворённый cover (обязателен ли он по oracle; если да — UNKNOWN).
2. Итоговая таблица C (C-01 + C-02, все 8 controls): что доказано (frame N1 пойман, legal companions), что gap (N2),
   что PENDING. Обновить LIMITATIONS-DRAFT (английский, без публикации) строго по фактам.
3. g0 `kani3300/ch8-c-ctl/run-43790257718/` RESULT.md + `kani3300/ch8-c-ctl/C-SUMMARY.md`. C budget исчерпан.
   Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
