# REV2 закрытие general Wide и stable u64 на N32 · GO

**GO** на один Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`. Решение координатора 2026-11-28; задание планера `dfb51e90a8` с решением координатора `83d9fbff5f`. [Ревью R1](REV2-GEN-STABLE-N32-CLOSURE-REVIEW.md) · [Handoff](REV2-GEN-STABLE-N32-CLOSURE-HANDOFF.md)

- **Control.** `33a2aa9bfe67aaa16b64ed905774efe646d02c3b`, tree `b5f8cea6e633b9b439488637b12ad9d542397e94`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_GEN_STABLE_N32_CLOSURE_TRIGGER_TREE` → `b5f8cea6e633b9b439488637b12ad9d542397e94`.
- **Входы.** Std `650d8aa728`, request `f756bcbf…`, roster `e09400ca…`, bindings `14499e80…`, bundle `52874345…`, relay `c8b4c070…` (только слот контроля Wide), stock Kani `9834c96ce9`.
- **Ожидание.** Левый S8 stable `u64` — `VERIFIED/MATCHED`; контроль u64 N32 (scratch D48) — `FAILED/MATCHED` с единственным отказом MULTIPLICITY. Контроль Wide N32 через relay — замер: по экстраполяции ревью почти наверняка OPEN по cold, VT или RSS; MATCHED засчитывается только при delivery `COMPLETE`. Пределы 120 с VT / 180 с cold / 4 GiB на корень без изменений. Итог u64 не зависит от исхода Wide.
