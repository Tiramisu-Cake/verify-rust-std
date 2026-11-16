# TASK — worker11: офлайн-приёмка S1-07 run 43923266772 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: intake w13 `kani3300/ch8-s1/s1-07/run-43923266772/` (RESULT, HANDOFF, collected, binding-metadata, LOCATION-EXCEPTIONS,
COMPARISON-S1-06), твой accept-v2 по S1-06 и MISSING-FOR-S1-07, PLAN-S1-AFTER-06, ACCEPTANCE-POLICY-BATCH.
Решения координатора от 2026-11-16 (location-only исключение для 2 exact ID; семантический success binding) действуют.

1. Применить классификатор к S1-07: binary-after теперь есть во всех 14 группах; native kani-metadata — использовать для
   PFC (selected impl → checked_with → modifies_wrapper → property), success bindings и UNREACHABLE ролей, где хватает.
2. Итог по каждой строке: QUALIFIED или точный оставшийся gate.
3. Для каждого оставшегося gate отдельно: (a) закрывается ли он вообще данными stock Kani 0aac; (b) если нет — какой
   минимальный критерий на stock-данных (file/line/harness/property ID/covers/negatives) даёт ту же защиту от vacuity и
   неверной привязки, и что именно он не покрывает; (c) можно ли закрыть его правкой исходников harness (например,
   уникальные сообщения в `smoke!`/`positive!`) без нового tool. Решение не применять — это предложение координатору.

Выход: g0 `kani3300/ch8-s1/s1-07/run-43923266772/accept/`: ACCEPTANCE.md, ACCEPT.json, replay, **POLICY-OPTIONS.md** (п. 3).
Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
