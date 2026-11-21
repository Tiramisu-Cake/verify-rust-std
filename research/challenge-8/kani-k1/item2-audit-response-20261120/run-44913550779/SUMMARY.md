# q-пилот, кампания 20 (actual вставки в wide network на OB11) — сводка координатора (run 44913550779)

std bfa60b19cc, control 0b4ba53bc4 (trigger 97f552174e), tool 0aac16ef, 11 бит, cap 6 GiB. Job success, 14:22–15:08Z. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| COMPACT-N20-ACT-INSERT-OB11 (stubs sort9, merge) | SUCCESS | 63 | 2,51 | 29,9 | 0/765, 6/6 | 0,61 млн |
| COMPACT-N20-ACT-INSERT-CORRUPT-OB11 (контроль) | FAILURE — назначенный `COMPACT_N20_ACT_INSERT_CORRUPT_QPOST` | 54 | 2,44 | 20,6 | 1/777, 2/2 | 0,60 млн |
| COMPACT-N25-ACT-INSERT-OB11 (stubs sort9, sort13, merge) | SUCCESS | 76 | 2,97 | 43,2 | 0/862, 6/6 | 0,76 млн |
| COMPACT-N25-ACT-INSERT-CORRUPT-OB11 (контроль) | FAILURE — назначенный `COMPACT_N25_ACT_INSERT_CORRUPT_QPOST` | 59 | 2,55 | 26,3 | 1/874, 2/2 | 0,74 млн |
| MW-S9-R-B13-L12-OB11 (Check sort9, v[13..25]) | SUCCESS | 241 | 4,37 | 200,5 | 0/615, 7/7 | 14,2 млн |
| MW-MERGE-N24-OB11 (Check merge N24) | SUCCESS | 215 | 4,03 | 174,3 | 0/694, 6/6 | 9,4 млн |
| COMPACT-N24-ACT-INSERT-OB11 (stubs sort9, merge) | SUCCESS | 77 | 2,79 | 44,4 | 0/765, 6/6 | 0,79 млн |
| MW-S13-R-B14-L14-OB11 (Check sort13, v[14..28]) | **RSS cap 6 GiB** (во время решения) | 833 | 6,02 | — | — | 25,5 млн |
| MW-MERGE-N27-OB11 (Check merge N27, odd) | SUCCESS | 244 | 4,64 | 202,8 | 0/694, 6/6 | 10,5 млн |
| COMPACT-N27-ACT-INSERT-OB11 (stubs sort13, merge) | SUCCESS | 69 | 2,78 | 37,2 | 0/765, 6/6 | 0,79 млн |

Итог: схема actual вставок работает на всех четырёх длинах — consumers N20/N24/N25/N27 SUCCESS при 2,5–3,0 GiB и 30–44 с VT, контроли N20/N25 упали ровно на назначенных метках. Все новые Check sort9 и merge (N24, N27) — в 6 GiB. N25 закрыт (на 12/13 битах с Replace вставок он упирался в объекты/10 GiB). Единственный корень выше 6 GiB — новый Check sort13 правой половины (14, len14), как и прочие Check sort13 (~7,3 GiB, CNF 25,5 млн совпадает с 17A). Для N20 вся цепочка в 6 GiB: Check sort9 L10/R10 (4,4) и merge N20 (3,4) из кампании 16 на OB11, consumer и control здесь на OB11.
