# q-пилот, кампания 16 (wide merge и провайдер sort13) — сводка координатора (run 44890498157)

std ed184d3f17, control 0578f584b6 (trigger 94e5fba795), tool 0aac16ef, 11 бит, cap 10 GiB. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MW-S9-L10 (Check sort9, len10) | SUCCESS | 243 | 4,38 | 201,3 | 0/615, 7/7 | 14,2 млн |
| MW-S9-R10 | SUCCESS | 244 | 4,37 | 203,7 | 0/615, 7/7 | 14,2 млн |
| MW-INSERT-L (Check insert, base1 rel9–11) | **too many addressed objects (2^11)** | 83 | 3,51 | — | — | — |
| MW-INSERT-R (base11 rel9) | SUCCESS | 103 | 3,30 | 63,7 | 0/762, 8/8 | 5,5 млн |
| MW-MERGE-N20 (Check bidirectional_merge) | SUCCESS | 176 | 3,44 | 134,6 | 0/694, 6/6 | 7,8 млн |
| MW-NETWORK-N20 | **too many addressed objects (2^11)** | 87 | 2,85 | — | — | — |
| **MW-S13-R13 (Check sort13, реальные swap)** | **SUCCESS** | 875 | 7,32 | 833,6 | 0/615, 7/7 | 25,5 млн |
| MW-S9-L12 | SUCCESS | 247 | 4,33 | 204,4 | 0/615, 7/7 | 14,2 млн |
| MW-MERGE-N25 | SUCCESS | 233 | 4,31 | 189,8 | 0/694, 6/6 | 9,7 млн |
| MW-NETWORK-N25 | **too many addressed objects (2^11)** | 118 | 3,89 | — | — | — |
| MW-N25-QPOST-CORRUPT (контроль) | **too many addressed objects (2^11)** | 110 | 3,73 | — | — | — |
| MW-MERGE-N32 | SUCCESS | 482 | 6,04 | 439,5 | 0/734, 8/8 | 12,8 млн |
| MW-N32-NUMERIC-PRE (контроль) | FAILURE — назначенный numeric Pre merge | 36 | 2,51 | 2,5 | 1/624, 3/3 | 0,13 млн |

Итог: впервые доказан провайдер **`Check(sort13_optimal)` на реальных swap** (11 бит, 834 с VT, 7,3 GiB); `bidirectional_merge` доказан на N20, N25 и максимальной N32; `sort9` — на len10/12. Четыре корня упали не на свойствах, а на пределе модели CBMC «too many addressed objects» при 11 object bits — их нужно повторить на 12 битах.
