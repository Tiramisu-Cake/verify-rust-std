# C-02 — пакет, NOT_RUN

Std `597e54c5cb503955f9483edc6acc9d4752d57713`, control `59b5c663e3a2a0fb79bc565cdda20342e51ac7bd`, input g0 `d535d987b4`.
Точные identities/flags/caps — `CI-REQUEST.json`; actual runner request — `EXECUTION-REQUEST.json`.
Только две exact selectors: `c_merge_source_write_restore`, `c_merge_source_read_only`
из `slice::sort::shared::smallsort::verify::c_controls`, PFC real `bidirectional_merge`, unwind17.
Один batch, jobs1,600s/root,900s compile,2100s group cap. Workflow caps112m/150m не расширены.

Это последний подготовленный C-02 пакет, не расходование CI credit. Dispatch не разрешён этой стадией.
Оба std attrs8→17; assertions, writes и checks сохранены. Original N1 matcher не расширен под ptr/mod.rs.
PFC source spelling/import/file/line/unwind проверяются до принятия результатов; label/generated-wrapper
binding остаётся отдельным требованием. Ожидаемые oracle: N1 только квалифицированный frame FAIL;
legal companion SUCCESS. Unwind/другие failures не засчитывать. Строгие inventory/cover gates сохранены:
C-02 может дать UNKNOWN, credit заранее не обещан.

Выбор двух строк: остальные6 уже имеют source-reported SUCCESS, их повторение не отвечает unwind blocker.
Сохранение всех8 с прежними attrs потребовало бы3 compile-группы/cap7500s; пара —1/cap2100s.
No local compiler, push, CI, publication or ledger operation.
