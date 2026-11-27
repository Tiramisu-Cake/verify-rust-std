# REV2 u64 N13 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; направление выбрано с планером (его рекомендация и задание `dde94ee726`), владелец делегировал выбор. Запуск после прогона валидности FIX7 (45916547252): на ветке один прогон за раз. [Ревью R1/R2](REV2-U64-N13-REVIEW.md) · [Задание](REV2-U64-N13-TASK.md) · [Handoff FIX1](REV2-U64-N13-HANDOFF.md#fix1)

- **Control.** `ed62c6a5c94bc2b676d2b9cdb698fcbc7dc3ad79`, tree `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N13_TRIGGER_TREE` → `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b`.
- **Входы.** Std `4d6dd50995`, request `2200182a…baeb`, roster `7aae46a6…`, bundle `1e3fff44…b3da`, stock Kani `9834c96ce9`.
- **Ожидание.** `U64-N13-SWAP` и `U64-N13-S13-BITS` — VERIFIED, exit 0; `U64-N13-S13-CORRUPT` — FAILED, exit 1, единственный отказ `REV2_U64_N13_S13_SORTED_POPCOUNT`. Каждый корень ≤120 с VT, ≤4 GiB, cold ≤180 с.
