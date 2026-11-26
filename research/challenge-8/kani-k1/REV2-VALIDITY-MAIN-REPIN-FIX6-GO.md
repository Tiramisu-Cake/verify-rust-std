# REV2 валидность · repin FIX6 · GO

**GO** на один диагностический Ubuntu-прогон без повтора в `Tiramisu-Cake/kani`, Item 2, `proof_credit=NONE`.

Решение координатора 2026-11-26 по делегированному праву GO. Планер для темы валидности не используется из-за контент-фильтра его среды. Запуск после сквозного пакета N26–N31 (45876456087): на ветке один прогон за раз. [Ревью R6](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r6--fix6) · [Задание FIX5](REV2-VALIDITY-MAIN-REPIN-FIX5-TASK.md) · [Задание FIX6](REV2-VALIDITY-MAIN-REPIN-FIX6-TASK.md) · [Разбор B](REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS.md)

- **Control.** `1338213af771e2658a3f81a5f720be7765b7eb86`, tree `756dea4a28c9ae012881fe36aa1542d749c78fec`.
- **Trigger.** Новый коммит без `[skip ci]` с этим tree и единственным родителем `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` → `756dea4a28c9ae012881fe36aa1542d749c78fec`.
- **Входы.**
  - Request SHA-256 `ab4550ea…8c62`.
  - Roster `2747be36…81a4`.
  - Overlay `4beda039e6`, bundle `49f0fba0…795e`.
  - Kani `4caf097d84` и Std merge `7f961eda87` не изменились.
- **Цели прогона.**
  - Подтвердить пробами две находки: сравнение `bool` и приведение массива к элементу.
  - Получить фазу B на исправленных fixture.
- **Ожидание.**
  - Фаза 0 PASS.
  - Фаза A: 18/18 плюс 8 probe-слотов. `bool_order_probe` даёт FAILURE (`ASSERTION_FAILURE_PINNED`), control — SUCCESS. `array_elem_cast_nonzero` ON даёт pinned unsupported, остальные — SUCCESS.
  - Фаза B: 13 слотов по гейтам. n18 ON — `MATCH_KNOWN_LIMITATION`.
