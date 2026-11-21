# q-пилот, кампания 22 (compact merge32 observer, OB11) — сводка координатора (run 44930211919)

std 54123e752d (cfg `kani_smallsort_q_compact_merge32`), control 6518a69cbe (trigger 2961f5e228), tool 0aac16ef, 11 бит, cap 6 GiB. Job success, 17:28Z–19:17Z (в очереди за 21C). RESEARCH_ONLY до admission.

| Корень | Итог | Child, с | RSS, GiB | VT, с | Failed / covers | CNF |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| MW-MERGE-N32-OBSERVER-EQUIV | SUCCESS | 44 | 1,86 | 7,6 | 0/182, 3/3 | 0,16 млн |
| MW-MERGE-N32-COMPACT-OB11 | SUCCESS | 525 | 5,07 | 478,7 | 0/759, 8/8 | 12,6 млн |

Итог: 2/2 SUCCESS. Compact merge N32 Check укладывается в 6 GiB (5,07 GiB против 6,01 GiB cap-stop в 21B и 6,04 GiB SUCCESS при 10 GiB в кампании 16). Equivalence root подтверждает, что observer `Below` совпадает со старой маской на всех 32 позициях. Для допуска N32 нужна сверка: Check слияния идёт под compact cfg, consumer `COMPACT-N32-ACT-INSERT-OB11` (21B) — на std e2bd3c6adc без него.
