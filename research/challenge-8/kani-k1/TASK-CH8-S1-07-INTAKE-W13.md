# TASK — worker13: intake S1-07 run 43923266772 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Run 43923266772 (твой пакет `kani3300/ch8-s1/s1-07/`, control `9208b373c0` → sibling `b37f6f75c5` на
`uninit-ci/ch8-s1k-i`, тот же tree `b6354b703d`; std `5be85699b8`, tool 0aac). Все 14 jobs success.

1. Скачать artifacts 14 групп в свой каталог; per-row evidence: verdict, rich inventory, location exception (ожидаемо ровно
   2 ID / 18 наблюдений), binary before/after snapshots, native kani-metadata, exits/elapsed/RSS.
2. Сверить с S1-06 (те же verdicts? те же 9986 properties?) и с ожиданиями пакета; любые отличия — явно.
3. Подготовить вход для офлайн-приёмки w11 (что теперь есть из MISSING-FOR-S1-07, что осталось UNKNOWN_NOT_EXPORTED).

Выход: g0 `kani3300/ch8-s1/s1-07/run-43923266772/`: RESULT.md, collected.json, HANDOFF.md. Коммит [skip ci],
author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
