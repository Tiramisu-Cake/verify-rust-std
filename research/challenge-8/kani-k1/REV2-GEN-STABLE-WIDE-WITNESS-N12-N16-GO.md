# REV2 Wide N12 / N16 witness · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-28; задание планера `44538d9436`. [Ревью R1–R3](REV2-GEN-STABLE-WIDE-WITNESS-N12-N16-REVIEW.md) · [Handoff](REV2-GEN-STABLE-WIDE-WITNESS-N12-N16-HANDOFF.md)

- **Control.** `588fc98143a3321d58d58407c916da621b70cccb`, tree `664f75885c8aafa7b4df8d82e9c8b7e0eb102593`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_WIDE_WITNESS_N12_N16_TRIGGER_TREE` → `664f75885c8aafa7b4df8d82e9c8b7e0eb102593`.
- **Входы.** Std `b465318cc9`, request `1247e9e6…`, roster `7f4ae44e…`, bindings `8df3d8ed…`, bundle `45dfe97f…`, relay `c8b4c070…`, stock Kani `9834c96ce9`.
- **Ожидание.** N12: один слот FAILED с единственным отказом `GEN_N12_WIDE_STABLE_EQUAL_KEYS` на `:1493:9`, covers 3/3, в пределах 120 с VT / 4 GiB / 180 с cold. N16: тот же FIX2-корень с relay stdout; MATCHED только при delivery `COMPLETE`; при RSS_LIMIT — census по PID и CNF из spill. Лимиты не меняются. Диагностика: допуск N16 Wide меняется только отдельным решением по результату.
