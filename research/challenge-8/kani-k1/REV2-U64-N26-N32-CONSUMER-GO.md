# REV2 u64 N26–N32 composite consumer · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `b5524a234e`. [Ревью R1](REV2-U64-N26-N32-CONSUMER-REVIEW.md) · [Handoff](REV2-U64-N26-N32-CONSUMER-HANDOFF.md)

- **Control.** `5d58830f278d18a9080c61b4d791f94101e0c4c4`, tree `4e4a20091835954aa9ff6847b11b7a572c9fc277`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N26_N32_CONSUMER_TRIGGER_TREE` → `4e4a20091835954aa9ff6847b11b7a572c9fc277`.
- **Входы.** Std `727137f7ef`, request `146a55a5…`, roster `98a0b977…`, bundle `b7292e6c…`, stock Kani `9834c96ce9`.
- **Ожидание.** Четырнадцать слотов: семь контролей FAILED с единственным отказом, семь copy-back VERIFIED; в пределах 120 с VT / 4 GiB / 180 с cold.
