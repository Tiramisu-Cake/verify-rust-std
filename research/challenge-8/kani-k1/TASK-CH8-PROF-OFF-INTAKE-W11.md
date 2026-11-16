# TASK — worker11: intake PROF-OFF-02 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

PROF-OFF-02 run 43784551069 (control `741b7183b4`, sibling `075750ca90`), artifact id — из
`gh api repos/Tiramisu-Cake/kani/actions/runs/43784551069/artifacts` (скачать zip в scratch вне репозиториев;
анализ из zip; raw job logs не читать).

Координатор (bounded): обе группы COMPLETE. group-00 (53 positive): export summary 53/53 SUCCESS,
checks 19586/21091 success (остальные — unreachable и т. п., проверить), covers 179/179; compile 53 s.
group-01 (9 controls-cfg): 9/9 FAILURE, каждая на своей названной проверке (bad adapter relation ×3,
payload corruption, `Check that *var_9 is assignable`, bad-profile swap/sort4/insert/merge, bad comparator-model relation);
compile 33 s. Phase 1660.8 s, group RSS peak 4 016 648 KiB. Но **все 62 row receipts** = outcome UNKNOWN,
`export.state = SOURCE_STAGE_TARGET_MISMATCH` (например swap_contract_u8_n2), 5 consumers — `matching_leaf_not_accepted`.

1. Найти, почему batch-binding дал SOURCE_STAGE_TARGET_MISMATCH (сравни ожидаемые source/stage/target поля row
   с harnesses[] записями export: file path normalization, target triple, mode/contract, unwind) — дефект runner
   или реальное расхождение.
2. Офлайн-переклассификация из exact export (тот же код классификатора с исправленным binding, без изменения
   oracles), каждая строка: binding доказательства, verdict против oracle, covers, named failures. Явно отделить
   «Kani verdict» от «acceptance». Consumers — после принятия своих leaf.
3. Исправить runner (если дефект), synthetic test на этот случай; общий фикс применим к S1/B/C runners — опиши.
4. g0 `kani3300/ch8-profiles/off-ci-batch/run-43784551069/`: RESULT.md, RECLASSIFY.json, HANDOFF.md.
   Последней строкой `READY <g0>` (+ `<control>` если runner исправлен) или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
