# q-пилот, кампания 21B (N26, N28–N32, actual вставки, OB11) — сводка координатора (run 44919643424)

std e2bd3c6adc, control d62b75ddd9 (trigger 74e03c5955), tool 0aac16ef, 11 бит, cap 6 GiB. Job success, до 17:07Z. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MW-MERGE-N26-OB11 | SUCCESS | 261 | 4,48 | 217,5 | 0/694, 6/6 | 10,2 млн |
| COMPACT-N26-ACT-INSERT-OB11 | SUCCESS | 74 | 2,71 | 39,2 | 0/765, 6/6 | 0,73 млн |
| COMPACT-N26-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N26…_QPOST` | 64 | 2,61 | 29,5 | 1/777, 2/2 | 0,70 млн |
| MW-MERGE-N28-OB11 | SUCCESS | 302 | 4,81 | 257,9 | 0/694, 6/6 | 11,0 млн |
| COMPACT-N28-ACT-INSERT-OB11 | SUCCESS | 81 | 3,04 | 47,1 | 0/765, 6/6 | 0,84 млн |
| COMPACT-N28-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N28…_QPOST` | 66 | 2,43 | 32,2 | 1/777, 2/2 | 0,81 млн |
| MW-MERGE-N29-OB11 (odd) | SUCCESS | 291 | 4,96 | 247,9 | 0/694, 6/6 | 11,3 млн |
| COMPACT-N29-ACT-INSERT-OB11 | SUCCESS | 90 | 3,21 | 53,5 | 0/765, 6/6 | 0,89 млн |
| COMPACT-N29-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N29…_QPOST` | 70 | 2,51 | 34,3 | 1/777, 2/2 | 0,86 млн |
| MW-MERGE-N30-OB11 | SUCCESS | 341 | 5,07 | 297,3 | 0/694, 6/6 | 11,8 млн |
| COMPACT-N30-ACT-INSERT-OB11 | SUCCESS | 94 | 3,40 | 57,9 | 0/765, 6/6 | 0,94 млн |
| COMPACT-N30-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N30…_QPOST` | 74 | 2,50 | 37,4 | 1/777, 2/2 | 0,92 млн |
| MW-MERGE-N31-OB11 (odd) | SUCCESS | 350 | 5,27 | 304,9 | 0/694, 6/6 | 12,1 млн |
| COMPACT-N31-ACT-INSERT-OB11 | SUCCESS | 102 | 3,55 | 66,3 | 0/765, 6/6 | 1,00 млн |
| COMPACT-N31-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N31…_QPOST` | 73 | 2,92 | 37,6 | 1/777, 2/2 | 0,97 млн |
| MW-MERGE-N32-OB11 | **RSS cap 6 GiB** (во время решения) | 500 | 6,01 | — | — | 12,8 млн |
| COMPACT-N32-ACT-INSERT-OB11 | SUCCESS | 107 | 3,73 | 71,0 | 0/765, 6/6 | 1,06 млн |
| COMPACT-N32-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `…N32…_QPOST` | 75 | 3,02 | 39,8 | 1/777, 2/2 | 1,03 млн |

Итог: 17/18 ожидаемых исходов. Consumers N26, N28–N32 SUCCESS при 2,7–3,7 GiB, все шесть контролей упали на назначенных метках, merge N26–N31 SUCCESS в 6 GiB (до 5,27 GiB). Merge N32 остановлен на cap 6 GiB; в кампании 16 тот же Check (cap 10 GiB, OB11) завершился SUCCESS при 6,04 GiB, 482 с. Цепочки N26, N28–N32 ещё ждут правые Check sort13 из 21C (8 GiB).
