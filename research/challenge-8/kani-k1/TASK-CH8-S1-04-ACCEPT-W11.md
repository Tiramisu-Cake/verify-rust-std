# TASK — worker11: offline acceptance S1-04 по ACCEPTANCE-POLICY-BATCH (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: intake worker13 — kani3300/ch8-s1/s1-04/run-43830757263/RESULT.md, ROWS.json, collected.json (g0 149a94c8fa);
artifacts 14 jobs: /root/ch8-s1-04-intake-w13/run-43830757263/artifacts/ (read-only). Source std 5be85699b8, tool 0aac.
Итог intake: 35 harness выполнены, 27 SUCCESS, 8 FAILURE; in-runner oracle: 6 EXPECTED, 29 UNKNOWN
(23 blanket veto unreachable/unsupported, 3 source binding macro positive!, 2 attachment mutants без oracle, 1 cover message↔ID).

Применить к S1-04 тот же подход, что accept-v2..v4 для Profiles (твои intake.py/binding из
kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/ и on-ci/fix/run-43808894294/accept-off/), по
ACCEPTANCE-POLICY-BATCH.md:
1. unsupported (76, все SUCCESS) — exact property ID ↔ assert(false);assume(false); unreachable (413 checks, 2 covers) —
   роли по source site; mandatory post/frame/relation unreachable — блокер.
2. Source binding через macro: exact export line 29 (`fn $name()`) + invocation anchors 66/67/68 (patch w13
   source-binding-fix.patch — проверить и использовать в офлайн-классификаторе, не в control).
3. Covers: таблица message → property ID по export (description), без сравнения строк с ID.
4. Attachment mutants (activation-default/override, F7/F8): oracle не был объявлен заранее → НЕ засчитывать как
   DETECTED; оставить OBSERVED_UNQUALIFIED с exact IDs; предложить oracle для следующего пакета.
5. Негативы F1–F6 — по заранее объявленным oracles пакета (property ID/description).
g0 kani3300/ch8-s1/s1-04/run-43830757263/accept/: ACCEPTANCE.md, ACCEPT.json, HANDOFF.md. Коммит [skip ci],
author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
