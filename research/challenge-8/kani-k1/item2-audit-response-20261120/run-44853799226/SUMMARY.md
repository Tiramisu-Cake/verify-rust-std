# q-пилот, кампания 6 (A/B --refine-arrays) — сводка координатора (run 44853799226)

std c8b703918a, control 87c9919ffa (trigger e0ad63e26c), tool 0aac16ef, cap 6 GiB. RESEARCH_ONLY, proof_credit=NONE.

| Корень | Итог | Child, с | RSS, GiB | Первая CNF |
| --- | --- | ---: | ---: | --- |
| P17-STATS (база, 12 бит) | timeout 180 с | 180,1 | 3,96 | 845 551 / 18 770 582 |
| P17-REFINE (12 бит, --refine-arrays) | timeout 180 с | 180,2 | 3,95 | 845 548 / 18 770 583 (refinement loop) |
| P-2b-OB11-REFINE (45 actual, 11 бит) | timeout 600 с | 600,2 | 5,44 | 1 537 303 / 25 398 620 (refinement loop) |
| P-2-OB11-REFINE (45 Replace, 11 бит) | rss_cap 6 GiB | 81,9 | 6,0 | — |

Вывод: `--refine-arrays` не меняет размер формулы и не даёт результата; гипотеза «стоимость — ограничения теории массивов» опровергнута. 11 бит не спасают P-2 с 45 Replace под Check.
