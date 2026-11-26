# REV2 валидность · repin FIX4 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-26 по делегированному праву GO. Планер недоступен для этой темы из-за контент-фильтра его среды. Запуск после завершения merge-прогона N26–N31 (45861423438), на ветке строго один прогон за раз. [Ревью R4](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r4--fix4) · [Handoff](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md) · [Прежний GO FIX2](REV2-VALIDITY-MAIN-REPIN-GO.md)

- **Control.** `e2a3e6d48e98693074f51e93369917948f6790bf`, tree `f46e65c42c7ddb45a725569265b8dc7c0fd7a88a`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` сменить на `f46e65c42c7ddb45a725569265b8dc7c0fd7a88a`.
- **Request.** SHA-256 `bdd69de4e0245ad241b22b144a104fdb69256d6c2fb1620d26eda57ccf76a6a2`, roster прежний.
- **Без изменений с FIX2.** Kani `4caf097d84` (main `8c6dba5935` с nightly-2026-11-21), Std merge `7f961eda87`, overlay `bc866f8dfa`, оба bundle.
- **Ожидание.** Фаза 0 PASS. A — 18/18 MATCH. B — 12 слотов по гейтам, отрицательный `vv_stable_char_n09_corrupt` ON — MATCH по правилу пары.
