# REV2 Wide N12 / N14 merge Checks и контроль N14 · GO

**GO** на один Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-28; задание планера `17cd85afc2`. [Ревью R1](REV2-GEN-STABLE-WIDE-N12-N14-REVIEW.md) · [Handoff](REV2-GEN-STABLE-WIDE-N12-N14-HANDOFF.md)

- **Control.** `bfc6f20a86ad00f59b7b97fea2ab35371e7a57de`, tree `e10399474aacb1f9377be57e79e2ba7e54ef3c99`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_WIDE_N12_N14_TRIGGER_TREE` → `e10399474aacb1f9377be57e79e2ba7e54ef3c99`.
- **Входы.** Std `93d0c4a18d`, request `bfa5a790…`, roster `2cb3104a…`, bindings `caca8508…`, bundle `8c7a8b2d…`, relay `c8b4c070…`, stock Kani `9834c96ce9`.
- **Ожидание.** Четыре exact Check `merge_up/down` (N12, N14) — SUCCESS, covers достигнуты; контроль N14 — FAILED/MATCHED с единственным отказом `GEN_N14_WIDE_STABLE_EQUAL_KEYS` на `:1939:9`, MATCHED только при delivery `COMPLETE`. Пределы 120 с VT / 180 с cold / 4 GiB на корень без изменений. Результат N12 не зависит от исхода N14.
