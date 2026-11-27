# REV2 u64 N20/N21 providers · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `2efbad5a82`. [Ревью R1](REV2-U64-N20-N21-REVIEW.md) · [Handoff](REV2-U64-N20-N21-HANDOFF.md)

- **Control.** `c4da71875efe80ebcfe78094afe6889a902d2da5`, tree `0d0857a039e5ffa263414952de49b716e3371c25`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N20_N21_TRIGGER_TREE` → `0d0857a039e5ffa263414952de49b716e3371c25`.
- **Входы.** Std `b09c6f22bf`, request `48f143cc…6a6c`, roster `efe92715…`, bundle `02e9cbbd…`, stock Kani `9834c96ce9`.
- **Ожидание.** Восемь корней по handoff VERIFIED в пределах 120 с VT / 4 GiB / 180 с cold. Выход PAIR за профиль — диагностический результат, дальше разбиение up/down или фиксированный k.
