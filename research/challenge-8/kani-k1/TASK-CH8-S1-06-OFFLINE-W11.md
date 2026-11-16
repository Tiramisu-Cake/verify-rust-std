# TASK — worker11: офлайн-приёмка S1-06 по плану PLAN-S1-AFTER-06 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: `kani3300/ch8-s1/PLAN-S1-AFTER-06.md` (план планера), S1-06 intake w13 `kani3300/ch8-s1/s1-06/run-43889560779/`
(RESULT, collected.json, missing-sites.json, STOCK-ROLE.json, accept/ACCEPT.json), ACCEPTANCE-POLICY-BATCH.md, твой классификатор.

Решения координатора (2026-11-16):
- Вариант 2 POLICY-QUESTION принят: location-only исключение для exact 2 ID `...small_sort_general_with_scratch::<…>.unreachable.1`
  (class unreachable, status SUCCESS, display `lib.rs:0:0`), фиксируется в новом receipt; всё остальное fail-closed.
- Literal-уникальность сообщения заменяется семантическим binding (macro-instance/callsite/harness → exact SUCCESS property).

Сделать офлайн по уже собранным artifacts (строки плана): (1) 413 checks + 2 covers со status UNREACHABLE → роль/target/
wrapper; mandatory post/frame/relation или требуемый участок недостижим — blocker; (2) 22 PFC bindings до wrapper/post/
modifies sites; (3) 114 success bindings семантически; (4) остальные gates плана. Исторические receipts не переписывать.

Выход: g0 `kani3300/ch8-s1/s1-06/run-43889560779/accept-v2/`: ACCEPTANCE.md, ACCEPT.json, replay; и **MISSING-FOR-S1-07.md** —
точный перечень полей/metadata, которых нет в artifacts и которые должен сохранить S1-07 (для w13). Коммит [skip ci],
author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
