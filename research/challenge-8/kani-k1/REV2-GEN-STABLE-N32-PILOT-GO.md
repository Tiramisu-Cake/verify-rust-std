# REV2 пилот general Wide и stable u64 на N32 · GO

**GO** на один Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-28; задание планера `e9c072be34`. [Ревью R1–R2](REV2-GEN-STABLE-N32-PILOT-REVIEW.md) · [Handoff](REV2-GEN-STABLE-N32-PILOT-HANDOFF.md)

- **Control.** `79a5ec2fb89f643559e44bdab0f534d6e827ec08`, tree `c1bbb6dbe41ce69c93a65b42fb45655d78da2aac`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_N32_PILOT_TRIGGER_TREE` → `c1bbb6dbe41ce69c93a65b42fb45655d78da2aac`.
- **Входы.** Std `88d05a138c`, request `eddd1856…`, roster `5845e394…`, bindings `623ae996…`, bundle `c806269c…`, relay `c8b4c070…` (не обслуживает ни одного слота), stock Kani `9834c96ce9`.
- **Ожидание.** Семь singleton на stock pipe: правый S8 FULL `u64`, правые fill rel15 `u64` и `Wide`, четыре exact Check `merge_up/down` в геометрии 16+16 — все `VERIFIED/MATCHED`, exit 0, covers достигнуты. Общий итог `GEN_STABLE_N32_PILOT_WITHIN_PROFILE` только при 7/7, полных timely receipts и attestation `COMPLETE`; иначе `GEN_STABLE_N32_PILOT_OPEN` с измерениями успешных слотов. Пределы 120 с VT / 180 с cold / 4 GiB на корень без изменений. Результат — только локальные опоры N32, не строка допуска.
