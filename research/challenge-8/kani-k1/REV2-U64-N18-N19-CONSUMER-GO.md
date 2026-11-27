# REV2 u64 N18/N19 consumer · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `1e6caef0f1`. Запуск после прогона N20/N21 (45946532451). [Ревью R1](REV2-U64-N18-N19-CONSUMER-REVIEW.md) · [Handoff](REV2-U64-N18-N19-CONSUMER-HANDOFF.md)

- **Control.** `d15d3c49f57740f89686a90ce17814e3fe54919a`, tree `27ae39f1a845f473cac270ec20ecdfbb47bd7559`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N18_N19_CONSUMER_TRIGGER_TREE` → `27ae39f1a845f473cac270ec20ecdfbb47bd7559`.
- **Входы.** Std `099f0c438c`, request `18dbcbde…`, roster `aeb4cfe5…`, bundle `3dee3db6…`, stock Kani `9834c96ce9`.
- **Ожидание.** Шесть слотов по handoff. Выход сквозных positive за профиль (R1-2) — диагностический результат; допуск длины тогда по составному правилу с локальными copy-back рёбрами.
