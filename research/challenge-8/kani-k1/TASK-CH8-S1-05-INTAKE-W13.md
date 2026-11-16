# TASK — worker13: intake S1-05 run 43864841077 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Run 43864841077 (control `8860d38558`, std `5be85699b8`, tool 0aac; твой пакет g0 `9a798b848f`). Итог jobs:
success — light-model, light-corruption, activation-default, cell; failure — light-controls, activation-override (ожидаемые
негативы?) и **все 8 heavy** (`freeze_copy_u8`, `stable_freeze_u8`, `unstable_freeze_u8`, `freeze_default_noncopy`, n01/n23).
В heavy job `runner.py run` завершился exit 1 без вывода в лог примерно за минуту после setup (пример: freeze_copy_u8-n01,
job лог ~строка 1536) — похоже на ошибку runner/декодера, а не proof verdict. В S1-04 те же heavy строки дали SUCCESS.

1. Скачать artifacts всех 14 групп (gh run download в свой каталог), собрать per-row evidence: verdict, rich inventory
   (полнота descriptions/locations), exits/elapsed/RSS.
2. Найти причину отказа heavy-групп (artifacts, bounded grep логов). Если дефект пакета — минимальное исправление и
   регрессионный тест (без CI).
3. Для успешно собранных групп — передать в офлайн-приёмку (классификатор w11 по ACCEPTANCE-POLICY-BATCH): что уже
   можно принять.
4. g0 `kani3300/ch8-s1/s1-05/run-43864841077/`: RESULT.md, collected.json, HANDOFF.md (+ fix/, если нужен). Коммит [skip ci],
   author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> [<fix control SHA>] или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
