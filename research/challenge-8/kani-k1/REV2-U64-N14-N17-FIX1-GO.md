# REV2 u64 N14–N17 FIX1 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `5f7e0e78d7`. [Ревью R2](REV2-U64-N14-N17-REVIEW.md#r2--fix1) · [Handoff FIX1](REV2-U64-N14-N17-FIX1-HANDOFF.md)

- **Control.** `087843c161d70ec36f6533ba8dd39742bae922c4`, tree `b4bf21f6578d30d40f66fd296af4258b6b0bc390`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N14_N17_FIX1_TRIGGER_TREE` → `b4bf21f6578d30d40f66fd296af4258b6b0bc390`.
- **Входы.** Std `fe8444d175`, request `a70f7208…8f8a`, roster `a6eb6158…648f`, bundle `b3752a87…f504`, stock Kani `9834c96ce9`.
- **Ожидание.** `U64-INSERT-REL16/13/14/15` — VERIFIED, в пределах 120 с VT / 4 GiB / 180 с cold. Вместе с пятью слотами 45926757103 это закрывает N14–N17.
