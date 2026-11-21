# q-пилот, кампания 14b (sort9 provider, повтор) — сводка координатора (run 44883003487)

std ad2c458a67, control c01bf94117 (trigger 9b45aa16e3), tool 0aac16ef, 12 бит, cap 10 GiB.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MD-SORT9-L1 (Check sort9, Replace swap, base1 len9) | rss_cap 10 GiB | 90 | 10,02 | — | — | — |
| MD-SORT9-R9 (base10 len9) | rss_cap 10 GiB | 88 | 10,04 | — | — | — |
| MD-SORT9-R10 (base10 len10) | rss_cap 10 GiB | 87 | 10,05 | — | — | — |
| MD-NETWORK-N18 (Replace sort9 ×2 + merge) | **SUCCESS** | 69 | 2,49 | 34,3 | 0/857, 6/6 | 0,74 млн |
| MD-NETWORK-N19 (Replace sort9 ×2 + insert + merge) | **SUCCESS** | 108 | 4,10 | 72,6 | 0/1210, 6/6 | 1,51 млн |
| MD-N19-QPOST-CORRUPT (контроль) | FAILURE ровно `MD_N19_CORRUPT_QPOST` | 84 | 3,00 | 49,4 | 1/1105, 2/2 | 1,24 млн |

Итог: потребители N18/N19 со сводкой sort9 — дёшевы и доказаны (условно на провайдере sort9). Провайдер `Check(sort9_optimal)` с 25 Replace swap упёрся в 10 GiB до CNF — та же картина, что у Check sort13 (DFCC). Следующий шаг: провайдер sort9 на 11 object bits (у sort13 11 бит сняли проблему памяти) в двух вариантах — реальные swap и Replace swap; потребители повторить на 11 битах для согласованного профиля.
