# q-пилот, кампания 21A (N21–N23 и контроли N24/N27, actual вставки, OB11) — сводка координатора (run 44919576152)

std e2bd3c6adc, control 2fa3734008 (trigger 2ffd91183e), tool 0aac16ef, 11 бит, cap 6 GiB. Job success, до 16:11Z. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MW-S9-L-B01-L11-OB11 (Check sort9, v[1..12]) | SUCCESS | 241 | 4,37 | 199,1 | 0/615, 7/7 | 14,2 млн |
| MW-S9-R-B11-L11-OB11 (v[11..22]) | SUCCESS | 237 | 4,36 | 197,5 | 0/615, 7/7 | 14,2 млн |
| MW-S9-R-B12-L11-OB11 (v[12..23]) | SUCCESS | 241 | 4,36 | 201,0 | 0/615, 7/7 | 14,2 млн |
| MW-S9-R-B12-L12-OB11 (v[12..24]) | SUCCESS | 246 | 4,36 | 204,2 | 0/615, 7/7 | 14,2 млн |
| MW-MERGE-N21-OB11 (odd) | SUCCESS | 183 | 3,65 | 138,5 | 0/694, 6/6 | 8,1 млн |
| MW-MERGE-N22-OB11 | SUCCESS | 195 | 3,71 | 151,4 | 0/694, 6/6 | 8,6 млн |
| MW-MERGE-N23-OB11 (odd) | SUCCESS | 192 | 4,02 | 150,6 | 0/694, 6/6 | 8,9 млн |
| COMPACT-N21-ACT-INSERT-OB11 | SUCCESS | 73 | 2,50 | 37,6 | 0/765, 6/6 | 0,66 млн |
| COMPACT-N21-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `COMPACT_N21_ACT_INSERT_CORRUPT_QPOST` | 61 | 2,62 | 25,4 | 1/777, 2/2 | 0,64 млн |
| COMPACT-N22-ACT-INSERT-OB11 | SUCCESS | 76 | 2,53 | 40,6 | 0/765, 6/6 | 0,70 млн |
| COMPACT-N22-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `COMPACT_N22_ACT_INSERT_CORRUPT_QPOST` | 62 | 2,51 | 26,9 | 1/777, 2/2 | 0,68 млн |
| COMPACT-N23-ACT-INSERT-OB11 | SUCCESS | 79 | 2,66 | 43,8 | 0/765, 6/6 | 0,75 млн |
| COMPACT-N23-ACT-INSERT-CORRUPT-OB11 | FAILURE — назначенный `COMPACT_N23_ACT_INSERT_CORRUPT_QPOST` | 64 | 2,43 | 28,1 | 1/777, 2/2 | 0,73 млн |
| COMPACT-N24-ACT-INSERT-CORRUPT-OB11 (контроль к N24 из 20) | FAILURE — назначенный `COMPACT_N24_ACT_INSERT_CORRUPT_QPOST` | 63 | 2,48 | 28,9 | 1/777, 2/2 | 0,77 млн |
| COMPACT-N27-ACT-INSERT-CORRUPT-OB11 (контроль к N27 из 20) | FAILURE — назначенный `COMPACT_N27_ACT_INSERT_CORRUPT_QPOST` | 66 | 2,46 | 31,1 | 1/777, 2/2 | 0,76 млн |

Итог: 15/15 ожидаемых исходов, все корни в 6 GiB (максимум 4,37 GiB). N21–N23 имеют полные цепочки (левый sort9 len10 для N21 — MW-S9-L10 из 16), N24 получил свой контроль. Контроль N27 есть; его цепочка ждёт правый Check sort13 (14,14) из 21C.
