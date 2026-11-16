# TASK — планер: S1 после S1-06 — кратчайший путь к принятию (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Факты (g0 `kani3300/ch8-s1/s1-06/run-43889560779/`: RESULT.md, POLICY-QUESTION.md, accept/ACCEPTANCE.md, ACCEPT.json):
- 35/35 harness завершены: 27 SUCCESS (все 16 heavy), 8 FAILURE = ровно предобъявленные негативы. 9986/9986 properties.
- 113/113 required covers SATISFIED; 13/127 required success messages привязаны, 114 PENDING.
- 18 записей без file/line: 2 ID, class `unreachable`, status SUCCESS, `lib.rs:0:0` (stock MIR Unreachable guard).
  **Решение координатора: вариант 2 POLICY-QUESTION принят** (узкое location-only исключение для этих exact записей,
  всё остальное fail-closed, исключение фиксируется в receipt).
- Прочие gates: нет after snapshot в 10 группах (runner остановился на completeness); роль 413 checks + 2 covers со
  status UNREACHABLE; 22 PFC — binding target/contract-wrapper; 114 success-message bindings.
- S1-04/05/06 — три прогона с одинаковыми verdicts и 0 qualified. Бюджет item 2: 6 из 14.

Нужно: план до qualified acceptance с минимумом прогонов. Для каждого gate — офлайн ли он закрывается (классификатор w11
по уже собранным artifacts) или требует прогона; что из этого реально защищает от vacuity/неверной привязки, а что
избыточно и может быть снято решением координатора (с обоснованием). Какие правки runner (после S1-06: не останавливаться
до записи after snapshot) войдут в S1-07, и сколько прогонов нужно.

Выход: g0 `kani3300/ch8-s1/PLAN-S1-AFTER-06.md` (≤1 страница), коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>.
Последней строкой READY <g0> или STOP <причина>. Без push/CI/публикаций/ledger.
