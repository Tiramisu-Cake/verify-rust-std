# q-пилот, кампания 11 (merge-пакет A) — сводка координатора (run 44872078840)

std 2dc2afe895 (verification-атрибуты и модули; runtime совпадает с базой без cfg_attr), control e18c9d5489 (trigger 4bd023abd7), tool 0aac16ef, 12 бит, local cap 10 GiB. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers |
| --- | --- | ---: | ---: | ---: | --- |
| MA-SWAP-BYTE-Q (PFC swap: q + min/max полных байтов) | SUCCESS | 86 | 1,87 | 36,8 | 0/614, 9/9 |
| MA-INSERT-RIGHT (PFC insert_tail, base 10, rel 9, numeric post) | SUCCESS | 103 | 2,08 | 45,8 | 0/746, 7/7 |
| MA-MERGE-UP (PFC merge_up) | SUCCESS | 61 | 1,85 | 13,0 | 0/433, 14/14 |
| MA-MERGE-DOWN (PFC merge_down) | SUCCESS | 61 | 1,85 | 14,1 | 0/455, 16/16 |
| MA-H9-L1 (probe sort9, base 1) | SUCCESS | 165 | 5,66 | 114,9 | 0/826, 6/6 |
| MA-H9-R10 (probe sort9, base 10) | SUCCESS | 162 | 5,66 | 112,3 | 0/826, 6/6 |
| MA-H10-R10 (probe sort9 + insert, base 10) | SUCCESS | 255 | **9,94** | 204,4 | 0/1164, 7/7 |
| MA-UP-BAD-TIE (контроль: неверная обработка равенства) | FAILURE, 1/429 (назначенный пост — проверить в qualification) | 53 | 1,86 | 5,3 | 1/429, 2/2 |
| MA-H10-CORRUPT-ORDER (контроль) | **rss_cap 10 GiB** на 278 с | 278 | 10,03 | — | — |

Итог: 8 из 9 ожидаемо; все листья merge-пакета A и пробы половин доказаны. Контроль порчи порядка H10 не уложился в 10 GiB. Предупреждение: проба H10 (одна половина N19) уже занимает 9,94 GiB — для полных потребителей N18/N19 профиль памяти — главный риск.
