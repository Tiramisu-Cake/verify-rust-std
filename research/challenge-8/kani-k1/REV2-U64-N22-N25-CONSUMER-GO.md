# REV2 u64 N22–N25 composite consumer · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `c254479b9a`. [Ревью R1](REV2-U64-N22-N25-CONSUMER-REVIEW.md) · [Handoff](REV2-U64-N22-N25-CONSUMER-HANDOFF.md)

- **Control.** `45501496bc6e9aff5cfc80ba39f6ded22d4c6856`, tree `427855f50583254169533be7a0957237183b9ee5`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N22_N25_CONSUMER_TRIGGER_TREE` → `427855f50583254169533be7a0957237183b9ee5`.
- **Входы.** Std `26ce90b192`, request `f22a8f97…9508`, roster `9255a3c0…`, bundle `32d68dc7…`, stock Kani `9834c96ce9`.
- **Ожидание.** Восемь слотов: четыре контроля FAILED с единственным отказом, четыре copy-back VERIFIED; в пределах 120 с VT / 4 GiB / 180 с cold.
