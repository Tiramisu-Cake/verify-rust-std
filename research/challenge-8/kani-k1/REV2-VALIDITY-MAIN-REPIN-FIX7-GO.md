# REV2 валидность · repin FIX7 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-27 по делегированному праву GO. Планер для темы валидности не используется из-за контент-фильтра его среды. [Ревью R7](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r7--fix7) · [Задание FIX7](REV2-VALIDITY-MAIN-REPIN-FIX7-TASK.md)

- **Control.** `008d4e16a7cda26e26502d253f497d9299b96fbb`, tree `3181cc4a239a6fc83e80c89e0f3490f79ebe5990`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` → `3181cc4a239a6fc83e80c89e0f3490f79ebe5990`.
- **Входы.** Request `949ed18f…d986`, roster `2747be36…81a4`, overlay `30545a3ce3`, bundle `6e37fa5c…b71d`. Kani `4caf097d84`, Std merge `7f961eda87`, workflow не изменились.
- **Цель.** Фаза B в лимитах: положительные `vv_stable_char_n09` и `vv_network_nonzero_n10` как validity-only корни на прежних маршрутах.
- **Ожидание.** Фаза 0 PASS; A 18/18 и пробы 8/8 как в 45886041869; B 13 слотов по гейтам, n18 ON — `MATCH_KNOWN_LIMITATION`, n10 ON — допуск `:423:28` со статусом SUCCESS.
- **Разбор.** TIMEOUT `vv_sort8_char_n08` (R7-1) — ресурсный, не результат по валидности. Для `vv_stable_char_n09` ON отдельно проверить `read_binding=OBSERVED` (R7-3).
