# q-пилот, кампания 13 (merge-пакет C: actual network N18/N19) — сводка координатора (run 44878875303)

std b7cea7f60a, control 65a35d901f (trigger a5610bfa0f), tool 0aac16ef, 12 бит, local cap 10 GiB.

| Корень | Итог | Child, с | RSS, GiB | Первая CNF (дизъюнкты) |
| --- | --- | ---: | ---: | ---: |
| MC-NETWORK-N18 | rss_cap 10 GiB | 312 | 10,03 | 7,70 млн |
| MC-NETWORK-N19 | rss_cap 10 GiB | 431 | 10,02 | 9,24 млн |
| MC-N19-QPOST-CORRUPT (контроль) | rss_cap 10 GiB | 356 | 10,02 | 8,69 млн |

Итог: формулы построены (7,7–9,2 млн дизъюнктов), все три корня упёрлись в 10 GiB на стадии решения. Нужен разбор: поднять cap до предела runner (~12 GiB) или уменьшить потребителя (например, сводка `sort9_optimal` как провайдер, чтобы потребитель N18/N19 видел 2 Replace sort9 + merge вместо 50 Replace swap).
