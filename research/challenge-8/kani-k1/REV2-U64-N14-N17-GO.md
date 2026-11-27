# REV2 u64 N14–N17 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO; пакет назначен планером (`302f507158`). [Ревью R1](REV2-U64-N14-N17-REVIEW.md) · [Задание](REV2-U64-N14-N17-TASK.md) · [Handoff](REV2-U64-N14-N17-HANDOFF.md)

- **Control.** `e51c10547ddd19f1f63ec324cd1ee31fbf0c57c9`, tree `fe9dfbd9a9670cc435190210578d68fa7e363f4e`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_U64_N14_N17_TRIGGER_TREE` → `fe9dfbd9a9670cc435190210578d68fa7e363f4e`.
- **Входы.** Std `53e733666e`, request `6bf1706f…9b5e`, roster `1e76eb9f…055d`, bundle `fbac6f36…5680`, stock Kani `9834c96ce9`.
- **Ожидание.** По handoff: insert-step и сквозной битовый N17 VERIFIED, четыре контроля FAILED с единственным отказом. Лимиты 120 с VT / 4 GiB / 180 с cold на корень. Выход insert-step или N17 за профиль — диагностический результат (R1-2), не повод для повтора без разбора.
