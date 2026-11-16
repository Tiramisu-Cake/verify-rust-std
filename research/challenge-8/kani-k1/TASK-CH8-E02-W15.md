# TASK — worker15: пакет E-02 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Основание: твой E-01 intake (g0 `4596de81f5`, `kani3300/ch8-e/e01/`), раздел «Следующее отдельное задание».
Координатор разрешает один дешёвый dispatch E-02 (bucket E, item 1; single-file, без std):
1. E-S: исправить namespace (`kani::arbitrary::...`), symbolic-length storage без constant CAP — positive + false control.
2. Primitive H: positive / no-write / OFF варианты для разграничения «shadow assigns в loop frame» (ON SEL1) от
   прочих причин; MRE из ISSUE-DRAFT как отдельная строка с точным ожидаемым сообщением.
3. Те же pins (upstream 0aac + SEL1), тот же control-шаблон `ch8-e-control` (проверенный в E-01), `--repo`/пути как в
   E-01, static path preflight (как в Profiles fix1). Synthetic tests, review.
4. g0 `kani3300/ch8-e/e02/`: CI-REQUEST, REVIEW, HANDOFF. Последней строкой `READY <control> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; новую shadow/havoc модель не делать.
