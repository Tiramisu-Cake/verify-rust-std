# q-пилот, кампания 12b (merge-пакет B, повтор) — сводка координатора (run 44876372471)

std 8ae4029765, control 38ef437cb8 (trigger 794e116a2f), tool 0aac16ef, 12 бит, cap 10 GiB. RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF дизъюнктов |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MB-MERGE-N18 (Check `bidirectional_merge`, actual up/down) | SUCCESS | 234 | 4,49 | 193,0 | 0/692, 6/6 | 12,96 млн |
| MB-MERGE-N19 | SUCCESS | 240 | 4,70 | 197,8 | 0/692, 6/6 | 13,55 млн |
| MB-PRE-NUMERIC-N18 (контроль numeric Pre) | FAILURE ровно `merge_halves_numeric` (caller Pre) | 35 | 2,46 | 1,8 | 1/638, 3/3 | 0,08 млн |
| MB-H10-CORRUPT-LITERAL (контроль) | FAILURE ровно `MB_H10_LITERAL_CORRUPT_NUMERIC_ORDER` | 150 | 8,22 | 116,3 | 1/1061, 2/2 | 3,64 млн |

Итог: 4/4 ожидаемо. Провайдер `bidirectional_merge` для N18/N19 доказан Check-ом (несмотря на DFCC, в 4,7 GiB); числовое предусловие merge действительно требуется (контроль). Следующий шаг — пакет C: реальная сеть N18/N19 с Replace swap (байтовая сводка), insert_tail и bidirectional_merge.
