# REV2 u64 N22–N25 providers · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `eba522d19e`. Запуск после прогона N20/N21 consumer (45962149067). [Ревью R1](REV2-U64-N22-N25-PROVIDERS-REVIEW.md) · [Handoff](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md)

- **Control.** `9e95965f30f40a4dea9532bd04330b0d68537769`, tree `6b9a8245426143527186a7095e8fbf5623578527`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N22_N25_PROVIDERS_TRIGGER_TREE` → `6b9a8245426143527186a7095e8fbf5623578527`.
- **Входы.** Std `a1335f8e11`, request `3bd9e509…c17f`, roster `732a0e57…`, bundle `d4e71162…`, stock Kani `9834c96ce9`.
- **Ожидание.** Тринадцать корней по handoff VERIFIED в пределах 120 с VT / 4 GiB / 180 с cold. Выход PAIR за профиль — диагностический результат; откат — разделение up/down (R1-1).
