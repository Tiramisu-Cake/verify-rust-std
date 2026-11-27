# REV2 u64 N26–N32 providers · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; задание планера `bd6bf381a6`. [Ревью R1/R2](REV2-U64-N26-N32-PROVIDERS-REVIEW.md) · [Handoff](REV2-U64-N26-N32-PROVIDERS-HANDOFF.md)

- **Control.** `f50d86dffac4c1265797189511feaec8bba9d09b`, tree `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N26_N32_PROVIDERS_TRIGGER_TREE` → `dcccfc903bb1953d2184282c5fc1da5067e6f6bb`.
- **Входы.** Std `72bb79d26d`, request `3d97d789…9043`, roster `5b12d12a…`, bundle `d9b30842…`, stock Kani `9834c96ce9`.
- **Ожидание.** Восемнадцать корней по handoff VERIFIED в пределах 120 с VT / 4 GiB / 180 с cold; job до 140 мин.
