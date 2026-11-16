# TASK — worker13: intake S1-04 run 43830757263 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Run 43830757263 (Tiramisu-Cake/kani, control 205b0e98c7, std 5be85699b8, tool 0aac): все 14 jobs завершились
с conclusion failure на шаге «Run grouped S1 batch with per-harness timeout». Длительности 7–19 мин на job,
включая heavy (8–13 мин) — подозрительно мало для тел, которые в S1-03 упирались в 600 s; возможна ошибка
компиляции/runner, а не proof verdict. Validate/build шаги прошли.

1. Скачать artifacts всех 14 jobs (gh run download в свой каталог), собрать collect.py --root ... --out collected.json.
2. Для каждой группы: compile exit/elapsed, per-row: Kani verdict, failed property IDs, timeout/RSS. Отделить
   ошибки runner/компиляции от proof-результатов. Если есть общая причина — найти по bounded head/tail логам.
3. Сводка: что доказано (по oracle пакета S1-04), что NOT_RUN/UNKNOWN и почему; минимальное исправление, если
   причина в пакете (без CI).
4. g0 kani3300/ch8-s1/s1-04/run-43830757263/: RESULT.md, collected.json, HANDOFF. Коммит [skip ci],
   author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать (grep bounded).
