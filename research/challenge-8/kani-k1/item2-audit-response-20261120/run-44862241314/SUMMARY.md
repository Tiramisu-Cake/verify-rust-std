# q-пилот, кампания 9 (qualification-пакет + no-merge сетка) — сводка координатора (run 44862241314)

std d968b9a8c3 (runtime без изменений), control baad011375 (trigger d872e81f2f), tool 0aac16ef, 12 бит, local cap 10 GiB. RESEARCH_ONLY до офлайн-qualification по QUALIFICATION-CHECKLIST.md.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers |
| --- | --- | ---: | ---: | ---: | --- |
| P-1 swap PFC | SUCCESS | 70 | 1,86 | 36,5 | 0/363, 10/10 |
| P-3 insert_tail PFC | SUCCESS | 452 | 5,45 | 412,7 | 0/623, 24/24 |
| N17 plain | SUCCESS | 268 | 9,04 | 235,2 | 0/946, 6/6 |
| N17 corrupt (контроль) | FAILURE ровно `N17_CORRUPT_QPOST` | 187 | 8,43 | 154,3 | 1/788, 3/3 |
| P-5a false-OR q any (контроль) | FAILURE (назначенная `swap_false_or_post`) | 42 | 1,83 | 9,9 | 1/344, 4/4 |
| P-5b false-OR q=0 (контроль) | SUCCESS (ожидаемо; отвергается правилом домена q) | 41 | 1,84 | 9,0 | 0/344, 3/4 |
| N01 plain | **timeout 300 с** | 301 | 2,65 | — | — |
| N02 plain | SUCCESS | 43 | 2,47 | 10,4 | 0/796, 6/6 |
| N08 plain | SUCCESS | 124 | 4,52 | 91,8 | 0/796, 6/6 |
| N09 plain | SUCCESS | 74 | 2,54 | 41,2 | 0/805, 6/6 |
| N12 plain | SUCCESS | 141 | 5,67 | 107,0 | 0/946, 6/6 |
| N13 plain | SUCCESS | 113 | 4,52 | 80,2 | 0/805, 6/6 |
| N16 plain | SUCCESS | 214 | 8,36 | 180,5 | 0/946, 6/6 |
| N02 corrupt (контроль) | FAILURE ровно `N02_CORRUPT_QPOST` | 42 | 2,45 | 8,9 | 1/638, 3/3 |
| N13 corrupt (контроль) | FAILURE ровно `N13_CORRUPT_QPOST` | 86 | 3,82 | 53,6 | 1/647, 3/3 |

Итог: все ожидаемые исходы, кроме N01 (символьный выбор длины 0/1 не уложился в 300 с; ранний возврат — тривиальный путь, разбить на отдельные литеральные N0 и N1). Network no-merge покрыт на N2, 8, 9, 12, 13, 16, 17; остаются N0, N1 и промежуточные 3–7, 10, 11, 14, 15.
