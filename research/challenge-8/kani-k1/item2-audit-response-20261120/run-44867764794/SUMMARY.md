# q-пилот, кампания 10 (оставшиеся no-merge длины network) — сводка координатора (run 44867764794)

std 632e4e8d3b (только харнессы), control 6f5009f3be (trigger db700c6c0b), tool 0aac16ef, 12 бит, local cap 10 GiB. До офлайн-qualification — RESEARCH_ONLY.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers |
| --- | --- | ---: | ---: | ---: | --- |
| N00 | SUCCESS | 35 | 2,45 | 0,5 | 0/216, 3/3 |
| N01 (литерал) | SUCCESS | 33 | 2,48 | 0,5 | 0/218, 4/4 |
| N03 | SUCCESS | 55 | 2,39 | 22,2 | 0/796, 6/6 |
| N04 | SUCCESS | 68 | 2,48 | 34,2 | 0/796, 6/6 |
| N05 | SUCCESS | 81 | 2,63 | 46,6 | 0/796, 6/6 |
| N06 | SUCCESS | 95 | 3,16 | 60,8 | 0/796, 6/6 |
| N07 | SUCCESS | 110 | 3,88 | 76,5 | 0/796, 6/6 |
| N10 | SUCCESS | 105 | 4,26 | 72,2 | 0/946, 6/6 |
| N11 | SUCCESS | 123 | 4,76 | 89,1 | 0/946, 6/6 |
| N14 | SUCCESS | 171 | 7,10 | 136,7 | 0/946, 6/6 |
| N15 | SUCCESS | 196 | 7,73 | 161,6 | 0/946, 6/6 |
| N02 corrupt (контроль) | FAILURE ровно `N02_CORRUPT_QPOST` | 44 | 2,40 | 9,9 | 1/638, 3/3 |
| N17 corrupt (контроль) | FAILURE ровно `N17_CORRUPT_QPOST` | 201 | 7,84 | 166,2 | 1/788, 3/3 |

Итог: 13/13 ожидаемо. Вместе с кампанией 9 network no-merge для `u8/KeyLess<u8>` закрыт на всех длинах 0–17 (после qualification).
