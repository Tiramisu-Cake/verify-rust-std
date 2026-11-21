# q-пилот, кампания 17B (сети N13–N17 через сводку sort13, лимит 6 GiB) — сводка координатора (run 44896876797)

std 3fff6aa0db, control 628a03ef3d (trigger 8992b29e86), tool 0aac16ef, 12 бит, cap 6 GiB. Job success, 10:59–12:47Z (ожидание в concurrency-группе за 17A). RESEARCH_ONLY до qualification.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| NM-INSERT-P3-OB12 (insert_tail, base1 rel1–16, любое q) | SUCCESS | 451 | 5,62 | 410,6 | 0/623, 24/24 | 23,0 млн |
| NM-NETWORK-N13 | SUCCESS | 49 | 2,46 | 16,0 | 0/811, 6/6 | 0,34 млн |
| NM-NETWORK-N14 | SUCCESS | 62 | 2,49 | 29,7 | 0/995, 6/6 | 0,93 млн |
| NM-NETWORK-N15 | SUCCESS | 76 | 2,56 | 42,7 | 0/995, 6/6 | 1,59 млн |
| NM-NETWORK-N16 | SUCCESS | 98 | 3,41 | 64,8 | 0/995, 6/6 | 2,30 млн |
| NM-NETWORK-N17 | SUCCESS | 127 | 4,03 | 93,3 | 0/995, 6/6 | 3,07 млн |
| NM-N13-QPOST-CORRUPT (контроль) | FAILURE — назначенный `NM_N13_CORRUPT_QPOST` (sorting_q_merge.rs:1800) | 39 | 2,59 | 5,7 | 1/699, 2/2 | 0,19 млн |
| NM-N17-QPOST-CORRUPT (контроль) | FAILURE — назначенный `NM_N17_CORRUPT_QPOST` (sorting_q_merge.rs:1833) | 88 | 3,53 | 54,2 | 1/888, 2/2 | 2,77 млн |

Итог: потребители N13–N17 через сводку sort13 укладываются в 6 GiB с большим запасом (2,5–4,0 GiB, 16–93 с VT) — вместо 7–9 GiB у прежних plain-потребителей кампаний 7–10. P-3 на 12 битах тоже в лимите (5,62 GiB). Оба контроля упали ровно на своих назначенных метках. Узкое место по памяти теперь только провайдер sort13 (7,35 GiB, кампания 17A).
