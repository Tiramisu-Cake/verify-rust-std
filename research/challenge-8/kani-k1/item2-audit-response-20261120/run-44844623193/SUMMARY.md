# q-пилот, кампания 3 (P-2, local RSS cap 9 GiB) — сводка координатора (run 44844623193)

std 0e9b28b293 (как кампания 2), control b716a7f821 (trigger 31450d1720), tool 0aac16ef. RESEARCH_ONLY, proof_credit=NONE.

P-2 `p2_sort13_u8_b01_len17_q_any`: SIGTERM по `rss_cap` на 98,2 с, sampled peak 9,01 GiB (effective cap 9 GiB). Symex 29,6 с, 514 792 шага, slicing убрал 365 780 присваиваний, 32 211 VCC → 4 281 после упрощения, Postprocess Equation 0,58 с; остановка — после постобработки, до первой напечатанной CNF (фаза преобразования SSA/битбластинга).

Вывод: +3 GiB не довели P-2 даже до CNF; память растёт на преобразовании формулы, а не на решателе. Дальше по плану из PILOT-RUN2-ANALYSIS.md — вариант «P-2 на реальных телах swap» (без `stub_verified(swap_if_less)`), cap 6 GiB.
