# TASK — worker11: acceptance v4 — exact contract-wrapper binding (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: accept-v3 (g0 `2f7418a815`): 19 ACCEPTED / 43 PENDING, причина всех 43 — EXACT_CONTRACT_WRAPPER_BINDING_PENDING
(+1 negative frame oracle PENDING). Тот же artifact 14190662926.

1. По source 9fa2f7f977 и Kani 0aac (contract macro expansion: `kani_macros/src/sysroot/contracts/*`, имена
   wrapper/check/replace closures и `kanitool::checked_with`/`inner_check` атрибутов) установить, как PFC harness
   ссылается на check-wrapper целевой функции, и какие имена функций wrapper появляются в per-row stdout
   (`Location: ... in function <name>`) и в export (property IDs `<fn>.<class>.N`, `contract` поле harness).
2. Для каждой из 42 PFC-строк доказать exact binding: target = ожидаемый profile/function (полный путь), checks
   postcondition/assigns/precondition принадлежат именно его wrapper; covers после target.
   Если доказательство требует данных, которых нет в artifact, — указать минимальное изменение runner/export для
   следующего прогона (без CI сейчас).
3. Frame-negative oracle: привязать named assigns failure к wrapper по тому же механизму.
4. Переклассифицировать; g0 `.../accept-v4/`: ACCEPTANCE.md, ACCEPT.json, BINDING.md, HANDOFF.md.
   Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
