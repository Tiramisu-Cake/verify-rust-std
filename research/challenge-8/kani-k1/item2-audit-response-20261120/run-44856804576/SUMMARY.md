# q-пилот, кампания 7 (plain-композиция) — сводка координатора (run 44856804576)

std 1b82e2a9a7, control bc7fb06c39 (trigger cd6c5d7372), tool 0aac16ef, 12 бит, cap 6 GiB. RESEARCH_ONLY, proof_credit=NONE.

| Корень | Итог | Child, с | RSS, GiB | VT, с | CNF |
| --- | --- | ---: | ---: | ---: | --- |
| Q13-PLAIN-STUB-SWAP (реальный sort13, Replace swap, plain) | **SUCCESS**, 0 of 745 failed (8 unreachable) | 112,5 | 4,85 | 79,6 | 1,54 млн / 2,97 млн |
| N17-PLAIN-STUB-SWAP-INSERT (реальная сеть N17, Replace swap + insert_tail) | rss_cap 6 GiB | 254,6 | 6,02 | — | 2,72 млн / 6,98 млн; 6 SAT-вызовов (55,8 с), последний UNSATISFIABLE за 32 с, затем cap |
| N17-PLAIN-QPOST-CORRUPT (контроль) | rss_cap 6 GiB | 179,9 | 6,03 | — | 2,57 млн / 6,60 млн |

Вывод: без Check sort13 формула в 8–9 раз меньше; q-свойство sort13 по реальному телу доказано за 80 с (лемма, не PFC). N17 дошёл до решателя и упёрся в память на стадии решения — следующий шаг: те же два корня N17 с local cap 10 GiB (outer 12 GiB, runner ~14 GiB).
