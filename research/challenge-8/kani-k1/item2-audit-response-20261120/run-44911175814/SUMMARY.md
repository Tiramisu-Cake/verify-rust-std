# q-пилот, кампания 19 (matched OB11 повторы для N13–N19) — сводка координатора (run 44911175814)

std 3fff6aa0db (как 17A/17B), control 400b54a57c (trigger e2800a1137), tool 0aac16ef, 11 бит, cap 6 GiB. Job success, 13:54–14:30Z. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MB-MERGE-N18-OB11 (Check merge N18) | SUCCESS | 161 | 3,15 | 116,9 | 0/692, 6/6 | 7,0 млн |
| MB-MERGE-N19-OB11 (Check merge N19) | SUCCESS | 159 | 3,29 | 115,0 | 0/692, 6/6 | 7,3 млн |
| MA-INSERT-RIGHT-OB11 (Check insert base10/rel9) | SUCCESS | 105 | 3,12 | 65,6 | 0/747, 7/7 | 5,5 млн |
| NM-INSERT-P3-OB11 (Check q-only insert base1/rel1–16) | SUCCESS | 374 | 4,31 | 333,1 | 0/623, 24/24 | 13,2 млн |
| NM-NETWORK-N17-OB11 | SUCCESS | 134 | 4,43 | 98,7 | 0/995, 6/6 | 3,07 млн |
| NM-N17-QPOST-CORRUPT-OB11 (контроль) | FAILURE — назначенный `NM_N17_CORRUPT_QPOST` | 93 | 3,38 | 58,1 | 1/888, 2/2 | 2,77 млн |
| NM-NETWORK-N13-OB11 | SUCCESS | 55 | 2,59 | 18,6 | 0/811, 6/6 | 0,34 млн |
| NM-N13-QPOST-CORRUPT-OB11 (контроль) | FAILURE — назначенный `NM_N13_CORRUPT_QPOST` | 41 | 2,50 | 6,5 | 1/699, 2/2 | 0,19 млн |
| NM-NETWORK-N14-OB11 | SUCCESS | 69 | 2,47 | 34,1 | 0/995, 6/6 | 0,93 млн |
| NM-NETWORK-N15-OB11 | SUCCESS | 82 | 2,69 | 47,9 | 0/995, 6/6 | 1,59 млн |
| NM-NETWORK-N16-OB11 | SUCCESS | 104 | 3,37 | 68,5 | 0/995, 6/6 | 2,30 млн |

Итог: все 11 корней завершились в 6 GiB (максимум 4,43 GiB), обе endpoint-контроли упали ровно на назначенных метках. Цепочки N13–N19 теперь целиком на 11 битах: провайдеры sort9 (15) и sort13 (17A) уже были OB11, а Check merge N18/N19, правый insert и P-3 повторены на OB11 здесь. Смешанных OB-рёбер в этих цепочках не осталось. Единственный корень выше 6 GiB во всём пути N13–N17 — Check sort13 (7,35 GiB, 17A); N18/N19 укладываются в 6 GiB целиком.
