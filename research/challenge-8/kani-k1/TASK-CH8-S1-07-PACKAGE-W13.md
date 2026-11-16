# TASK — worker13: пакет S1-07 — runner finalization (одна стадия, без dispatch)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: `kani3300/ch8-s1/PLAN-S1-AFTER-06.md` (раздел «S1-07 runner»), твой S1-06 intake, control `b25dd39a46`.
Std/tool/domain/checks/группы — без изменений (35 roots / 14 groups).

1. After fingerprint: защищённая finalization после остановки child, до rich validation — также при timeout/error/partial
   export; fixed required binaries хешировать независимо от export. Сохранять original exit/exception, отдельные snapshot
   errors, rich records, source/variant cleanup; missing/drift → UNKNOWN.
2. Location-exception (решение координатора: exact 2 ID `small_sort_general_with_scratch::<…>.unreachable.1`, class
   unreachable, SUCCESS, display `lib.rs:0:0`) согласовать в decoder/collector/receipt; admission остаётся за офлайн w11.
3. Когда w11 закончит `accept-v2/MISSING-FOR-S1-07.md` — добавить сохранение перечисленных metadata (если появится до
   конца твоей стадии; иначе оставить точку расширения и отметить в HANDOFF).
4. Тесты: synthetic success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-stage-target-mismatch/snapshot-error;
   прежние preflight/YAML/shallow регрессии.

Выход: g0 `kani3300/ch8-s1/s1-07/`: control-кандидат (новый commit, локально, без push), CI-REQUEST.json/md, VALIDATION.json,
HANDOFF.md. Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> <control SHA> или STOP.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
