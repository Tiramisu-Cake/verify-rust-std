# q-пилот, кампания 18 (N25 на 13 битах, компактные N20/N25, вставки с литеральным rel, компактный observer sort13) — сводка координатора (run 44907708573)

std a9e7dba799, control 92dbec90b (trigger c8959e6308), tool 0aac16ef, cap 10 GiB. Job success, 13:12–14:01Z. RESEARCH_ONLY до qualification.

| Корень | Биты | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | ---: | --- | ---: | ---: | ---: | --- | ---: |
| MW-NETWORK-N25-OB13 | 13 | **RSS cap 10 GiB** (во время решения) | 326 | 10,03 | — | — | 16,6 млн |
| MW-N25-QPOST-CORRUPT-OB13 (контроль) | 13 | **RSS cap 10 GiB** | 272 | 10,03 | — | — | 15,7 млн |
| COMPACT-N25-OB12 | 12 | **too many addressed objects (2^12)** | 111 | 3,95 | — | — | — |
| COMPACT-N25-CORRUPT-OB12 (контроль) | 12 | **too many addressed objects (2^12)** | 107 | 3,92 | — | — | — |
| COMPACT-N20-OB12 (Replace insert) | 12 | SUCCESS | 203 | 8,34 | 168,4 | 0/1119, 6/6 | 8,9 млн |
| COMPACT-N20-CORRUPT-OB12 (контроль) | 12 | FAILURE — назначенный `COMPACT_N20_CORRUPT_QPOST` (sorting_q_merge.rs:2024) | 189 | 7,24 | 153,3 | 1/1131, 2/2 | 8,8 млн |
| **COMPACT-N20-ACT-INSERT-OB12 (actual inserts)** | 12 | **SUCCESS** | 68 | **2,49** | 33,6 | 0/765, 6/6 | 0,61 млн |
| MW-INSERT-L9-OB11 (Check insert base1/rel9) | 11 | SUCCESS | 106 | 3,38 | 66,0 | 0/766, 8/8 | 5,5 млн |
| MW-INSERT-L10-OB11 | 11 | SUCCESS | 114 | 3,17 | 73,6 | 0/766, 8/8 | 5,8 млн |
| MW-INSERT-L11-OB11 | 11 | SUCCESS | 119 | 3,74 | 76,6 | 0/766, 8/8 | 6,1 млн |
| NM-S13-L17-COMPACT-OB11 (Check sort13, компактный observer) | 11 | SUCCESS | 945 | 7,23 | 902,2 | 0/642, 7/7 | 25,3 млн |

Итог:
- **N20 с actual вставками — 2,49 GiB и 34 с VT** против 8,34 GiB у того же компактного harness с Replace вставок: стоимость N20 давали сводки insert_tail (capture/havoc/post), а не сама сеть. Этот маршрут укладывается в 6 GiB; провайдеры — только Check sort9 (4,4 GiB) и Check merge N20 (3,4 GiB) из кампании 16 на 11 битах. Matched q-post control для этого маршрута ещё нужен (COMPACT-N20-CORRUPT шёл с Replace вставок).
- Левые вставки с литеральным rel9/10/11 на 11 битах — 3,2–3,7 GiB (против 7,12 GiB у сгруппированного символического rel на 12 битах).
- Компактный observer sort13 почти ничего не дал (7,23 против 7,35 GiB): пик определяют actual swaps DFCC.
- N25: на 13 битах упирается в RSS 10 GiB, компактный harness на 12 битах всё ещё превышает 2^12 объектов. Гипотеза для следующего шага — те же actual вставки (у N25 три левые вставки через Replace).
