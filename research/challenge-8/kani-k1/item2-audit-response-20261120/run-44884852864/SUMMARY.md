# q-пилот, кампания 15 (провайдер sort9 на 11 object bits) — сводка координатора (run 44884852864)

std c5dc2a415e, control 29e75d9887 (trigger e8d4c482cd), tool 0aac16ef, 11 бит для всех корней, cap 10 GiB.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MD-SORT9-L1-OB11 (Check sort9, Replace swap) | rss_cap 10 GiB | 479 | 10,0 | — | — | 19,7 млн |
| MD-SORT9-R9-OB11 | rss_cap 10 GiB | 469 | 10,0 | — | — | 19,7 млн |
| MD-SORT9-R10-OB11 | rss_cap 10 GiB | 489 | 10,0 | — | — | 19,7 млн |
| MD-SORT9-L1-ACT-OB11 (Check sort9, реальные swap) | **SUCCESS** | 212 | 4,33 | 167,8 | 0/607, 7/7 | 14,2 млн |
| MD-SORT9-R9-ACT-OB11 | **SUCCESS** | 213 | 4,29 | 162,0 | 0/607, 7/7 | 14,2 млн |
| MD-SORT9-R10-ACT-OB11 | **SUCCESS** | 212 | 4,29 | 163,9 | 0/607, 7/7 | 14,2 млн |
| MD-NETWORK-N18-OB11 (Replace sort9 ×2 + merge) | **SUCCESS** | 67 | 2,46 | 33,4 | 0/857, 6/6 | 0,74 млн |
| MD-NETWORK-N19-OB11 (Replace sort9 ×2 + insert + merge) | **SUCCESS** | 99 | 4,10 | 64,8 | 0/1210, 6/6 | 1,51 млн |
| MD-N19-QPOST-CORRUPT-OB11 (контроль) | FAILURE ровно `MD_N19_CORRUPT_QPOST` | 83 | 3,15 | 48,4 | 1/1105, 2/2 | 1,24 млн |

Итог: провайдер `Check(sort9_optimal)` доказан на **реальных swap** при 11 битах во всех трёх геометриях N18/N19 (Replace-swap вариант упирается в память и при 11 битах). Вместе с провайдерами правой вставки и `bidirectional_merge` (кампании 11, 12b; 12 бит) N18 и N19 замкнуты на реальной сети. Для qualification: согласование профиля object bits (11 у sort9/потребителей, 12 у insert/merge-провайдеров).
