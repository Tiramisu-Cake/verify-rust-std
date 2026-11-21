# q-пилот, кампания 21C (правые Check sort13, OB11, cap 8 GiB) — сводка координатора (run 44923999242)

std e2bd3c6adc, control 5eef2b4861 (trigger 86bd362993), tool 0aac16ef, 11 бит, cap 8 GiB по решению владельца для всех sort13 ([OWNER-DECISION-SORT13-8GIB.md](../OWNER-DECISION-SORT13-8GIB.md)). Job success, 16:20Z–19:01Z. RESEARCH_ONLY до admission.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MW-S13-R-B14-L13-OB11 | SUCCESS | 947 | 7,28 | 882,9 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B14-L14-OB11 | SUCCESS | 930 | 7,30 | 881,3 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B15-L14-OB11 | SUCCESS | 941 | 7,28 | 888,7 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B15-L15-OB11 | SUCCESS | 938 | 7,28 | 889,6 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B16-L15-OB11 | SUCCESS | 858 | 7,28 | 810,0 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B16-L16-OB11 | SUCCESS | 870 | 7,29 | 820,6 | 0/615, 7/7 | 25,5 млн |
| MW-S13-R-B17-L16-OB11 | SUCCESS | 958 | 7,29 | 913,8 | 0/615, 7/7 | 25,5 млн |

Итог: 7/7 SUCCESS, все unwinding-assertions и свойства SUCCESS, covers 7/7 SATISFIED, RSS 7,28–7,30 GiB (в пределах 8 GiB lane), child ≤958 с при лимите 1100 с. Это закрывает правые Check sort13, которых ждали цепочки N26–N31 (вместе с consumers и controls из 21A/21B).
