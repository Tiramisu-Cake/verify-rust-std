# q-пилот, кампания 8 (N17 plain, local cap 10 GiB) — сводка координатора (run 44858566553)

std 1b82e2a9a7, control f839997417 (trigger 82d9f85bc7), tool 0aac16ef, 12 бит. RESEARCH_ONLY, proof_credit=NONE.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Свойства / covers |
| --- | --- | ---: | ---: | ---: | --- |
| N17-PLAIN-STUB-SWAP-INSERT (реальная `small_sort_network` N17; реальные sort13 и insertion loop; Replace `swap_if_less` (P-1) и `insert_tail` (P-3)) | **SUCCESS** | 280,1 | 9,04 | 244,1 | 0 of 946 failed (11 unreachable); 6 of 6 covers |
| N17-PLAIN-QPOST-CORRUPT (контроль) | **FAILURE ровно `N17_CORRUPT_QPOST`** | 200,6 | 7,84 | 164,9 | 1 of 788 failed |

Итог пилота (исследовательский): прежний BLOCKER N17 снят пороговой композицией на реальном коде — провайдеры P-1 (`swap_if_less`, кампании 1–2) и P-3 (`insert_tail`, кампания 2) доказаны PFC, потребитель N17 доказан plain-корнем без Check `sort13_optimal`; контроль ловит порчу результата. Отдельно: q-лемма sort13 (Q13, кампания 7, 80 с). Ресурсы: N17 требует ~9 GiB sampled RSS при 12 object bits — выше прежнего профиля 6 GiB.
