# INTEGCHECK — PASS

Library `85ced7f8a8bcdf6b4ffe2e29a65d1d940ff10737`, tree `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8` = RENAMEMODS; G1/G2 и итоговое дерево идентичны.
G1 `15e40390-276a-446c-852c-a4a4e979ca38`, source `d1515761df4b630bd9f51812f9f0e6f8b75ab92d`; G2 `d32340b9-f056-4d53-8d91-a9562f00f08b`, source `da620e719217707c9f8bde005abb57f8519dcabf`.
Обе Cloud SUCCESS, COMPLETE, gate=true; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, exit G1=1 (контроли), G2=0; source/request/pool/tooling PASS. Только bounded интеграция выбранных строк; полной proof-матрицы233, universal T/F, uninit/value-validity и panic-unwinding claims нет. Имена от verify::; verify/* — внутри smallsort/, smallsort.rs — соседний runtime-файл.

| Контроль | Status; failed/total | Все упавшие проверки @ место | Назначенная |
| --- | --- | --- | --- |
| `fixed_inputs::reject_mutant_swap_u8_n2` | FAILED; 1/80 | `assertion failed: v[0] <= v[1]` @ `verify/fixed_inputs.rs:25` | да |
| `merge::profiles::profile_full_value_checker_rejects_payload_change_u8` | FAILED; 1/378 | `full-value checker detects payload corruption` @ `verify/merge/profiles.rs:347` | да |
| `merge::profiles::profile_wrong_f_insert_rejected_u8` | FAILED; 1/605 | `profile_canonical_comparator::<P>(cmp)` @ `verify/merge/profiles.rs:273` | да |
| `merge::profiles::profile_wrong_f_merge_rejected_u8` | FAILED; 1/594 | `profile_canonical_comparator::<P>(cmp)` @ `verify/merge/profiles.rs:311` | да |
| `merge::profiles::profile_wrong_f_sort4_rejected_u64` | FAILED; 1/552 | `profile_canonical_comparator::<P>(cmp)` @ `verify/merge/profiles.rs:237` | да |
| `merge::profiles::profile_wrong_f_swap_rejected_u8` | FAILED; 1/247 | `profile_canonical_comparator::<P>(cmp)` @ `verify/merge/profiles.rs:212` | да |
| `tag_permutation::reject_duplicate_network_u8_n9` | FAILED; 1/559 | `every input tag occurs exactly once` @ `verify/tag_permutation.rs:55` | да |
| `helper_contracts::rejects_insert_tail_equal_begin_u64` | FAILED; 1/205 | `begin < tail && insert_tail_contract_len(begin, tail) > 1 && crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(begin,insert_tail_contract_len(begin, tail),)) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(begin,insert_tail_contract_len(begin, tail),))` @ `smallsort.rs:588` | да* |
| `helper_contracts::rejects_merge_overlapping_dst_u64` | FAILED; 1/235 | `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` @ `smallsort.rs:859` | да |
| `helper_contracts::rejects_swap_comparator_writing_outside_frame_u8` | FAILED; 1/205 | `Check that *var_9 is assignable` @ `verify/helper_contracts.rs:250` | да |
| `helper_contracts::rejects_swap_outside_backing_u8` | FAILED; 1/137 | `crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) && crate::ub_checks::can_write(v_base.wrapping_add(b_pos))` @ `smallsort.rs:409` | да* |
| `forwarding_contracts::rejects_always_true` | FAILED; 1/588 | `canonical comparator required` @ `verify/forwarding_contracts.rs:60` | да |
| `forwarding_contracts::rejects_payload_corruption` | FAILED; 1/345 | `full-value checker rejects payload corruption` @ `verify/forwarding_contracts.rs:270` | да |

* Kani указывает начало того же requires: smallsort.rs:588/409 вместо первой строки условия589/410 в пакете; полный текст условий совпал с неизменённым исходником. Ожидания не переписаны.

| Строка пары | Status | Время, с | Covers | Прежнее с |
| --- | --- | ---: | ---: | ---: |
| `helper_contracts::swap_safety_u8_backing9` | SUCCESS | 17.797321 | 6/6 | 17.355093 |
| `helper_contracts::unstable_network_safety_u8_n9_stubbed` | SUCCESS | 7.1729608 | 1/1 | 11.660206 |
| `helper_contracts::swap_safety_u8_backing13` | SUCCESS | 17.776968 | 6/6 | 17.583559 |
| `helper_contracts::unstable_network_safety_u8_n13_stubbed` | SUCCESS | 13.853836 | 1/1 | 13.978799 |
| `helper_contracts_wide::swap_safety_u8_backing32` | SUCCESS | 33.460003 | 9/9 | 31.575 |
| `helper_contracts_wide::unstable_network_safety_u8_n32_stubbed` | SUCCESS | 122.2593 | 5/5 | 104.319084 |
| `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | SUCCESS | 94.190506 | 5/5 | 86.45552 |
| `helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | SUCCESS | 7.248298 | 4/4 | 8.113433 |

Пары: 8 SUCCESS, 0 failed checks, covers37/37, unreachable covers0; Σ313.7591928с. N9/N13 consumer1/1: по одному прежнему reachable cover, два unreachable callback covers исключены существующим stub.
Cfg-on compiler inventory: ровно246=233 ordinary+13 controls, missing/extra/duplicates0; sorted SHA256 `3e03f6051cb8d0ab71d1a40f73c58234acbc7964315529ac9c603c49f9d222eb` = expected; четыре bound-страницы сверены полностью.
Предупреждения: G1/G2 targeted smallsort/verify/smallsort.rs scan — no match; новых релевантных предупреждений не обнаружено.
Расход G1 $0.2025 + G2 $0.5940 = **$0.7965/$2.75**, reserve0; builds2/2, retries0, repairs0. T0/deadlines сохранены.
Evidence: [G1 report](integcheck/g1-evidence/verification-report.json), [G2 report](integcheck/g2-evidence/verification-report.json), [ledger](integcheck/RUN-LEDGER.json).
