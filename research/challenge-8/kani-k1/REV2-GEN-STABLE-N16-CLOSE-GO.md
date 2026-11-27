# REV2 general/stable N16 closure · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-28 по делегированному праву GO; задание планера `fa8731df9e`. [Ревью R1/R2](REV2-GEN-STABLE-N16-CLOSE-REVIEW.md) · [Handoff](REV2-GEN-STABLE-N16-CLOSE-HANDOFF.md#fix1)

- **Control.** `ad7e2ba127919b463a395819c94a30225b844b90`, tree `8fff1fc16152df0c6febf8bac6729199a12407be`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_N16_CLOSE_TRIGGER_TREE` → `8fff1fc16152df0c6febf8bac6729199a12407be`.
- **Входы.** Std `e8e8af6d3b`, request `c3049756…`, bundle `8668301c…`, stock Kani `9834c96ce9`.
- **Ожидание.** Семь слотов: пять VERIFIED (левые S8 u64 и S4 Wide, Wide fill rel5/6/7), два контроля FAILED с единственным отказом (u64 кратность, Wide `STABLE_EQUAL_KEYS`); в пределах 120 с VT / 4 GiB / 180 с cold.
