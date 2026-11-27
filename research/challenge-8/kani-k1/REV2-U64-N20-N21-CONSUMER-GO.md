# REV2 u64 N20/N21 composite consumer · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `f16a69904a`. [Ревью R1](REV2-U64-N20-N21-CONSUMER-REVIEW.md) · [Handoff](REV2-U64-N20-N21-CONSUMER-HANDOFF.md)

- **Control.** `c2bcb3744b88f666e006fe4397f37cc83b21b5ba`, tree `23841cd660808a5a0238e6056aa61a87d72c1d15`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N20_N21_CONSUMER_TRIGGER_TREE` → `23841cd660808a5a0238e6056aa61a87d72c1d15`.
- **Входы.** Std `97b1df7b0a`, request `c15c3f98…`, roster `43480e47…`, bundle `6640b240…`, stock Kani `9834c96ce9`.
- **Ожидание.** Четыре слота по handoff (контроли FAILED с единственным отказом, copy-back VERIFIED) в пределах 120 с VT / 4 GiB / 180 с cold.
