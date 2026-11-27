# REV2 general/stable N16 pilot · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; пилот одобрен владельцем 2026-11-27; задание планера `b3614058e7`. [Ревью R1](REV2-GEN-STABLE-N16-PILOT-REVIEW.md) · [Handoff](REV2-GEN-STABLE-N16-PILOT-HANDOFF.md)

- **Control.** `046b1e0f8457390b1e6ffea9dd779a0a4acc053e`, tree `9021966b36dcbbf0a7f36d9065bd0dae580a4e98`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_N16_PILOT_TRIGGER_TREE` → `9021966b36dcbbf0a7f36d9065bd0dae580a4e98`.
- **Входы.** Std `14a5a7322a`, request `c105664a…`, bundle `c11285e3…`, stock Kani `9834c96ce9`.
- **Ожидание.** Шесть слотов VERIFIED (sort8 FULL/BITS, Wide sort4 со стабильностью, Wide fill rel4, две пары merge scratch → v); в пределах 120 с VT / 4 GiB / 180 с cold.
