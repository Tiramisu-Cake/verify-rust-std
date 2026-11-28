# REV2 Wide N10 stability witness · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-28; задание планера `e8d06aefc3`. [Ревью R1](REV2-GEN-STABLE-N10-WIDE-WITNESS-REVIEW.md) · [Handoff](REV2-GEN-STABLE-N10-WIDE-WITNESS-HANDOFF.md)

- **Control.** `e54fde9f4c9c8e24085c6953f25c0d036c586a30`, tree `6d353bd8a1e1f587dc772a7a2958edc55ee78d9e`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_N10_WIDE_WITNESS_TRIGGER_TREE` → `6d353bd8a1e1f587dc772a7a2958edc55ee78d9e`.
- **Входы.** Std `bec3b6ee80`, request `da2a7c14…`, bundle `ea580502…`, stock Kani `9834c96ce9`.
- **Ожидание.** Один слот FAILED с единственным отказом `STABLE_EQUAL_KEYS` на `:1407:9`; в пределах 120 с VT / 4 GiB / 180 с cold. Диагностика: допуск N16 Wide не меняет.
