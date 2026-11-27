# REV2 u64 N18/N19 providers · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `e758ec3155`. Запуск после прогона N14–N17 FIX1 (45933888115): на ветке один прогон за раз. [Ревью R1/R2](REV2-U64-N18-N19-REVIEW.md) · [Handoff](REV2-U64-N18-N19-HANDOFF.md)

- **Control.** `44aa6a2273588502083e47e204730dd67e0fba51`, tree `74f90d62acda5157906272454ec9d6c4bb9819db`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N18_N19_TRIGGER_TREE` → `74f90d62acda5157906272454ec9d6c4bb9819db`.
- **Входы.** Std `c8eefae4c8`, request `b4316967…3caf`, roster `2110ee32…`, bundle `320e2eee…674d`, stock Kani `9834c96ce9`.
- **Ожидание.** Семь корней по handoff VERIFIED в пределах 120 с VT / 4 GiB / 180 с cold. Выход `PAIR-STEP` за профиль — диагностический результат (R1-2), дальше разбиение up/down.
