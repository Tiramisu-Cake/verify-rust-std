# INSERTPFC — PASS

Library `a282d08c5afad32ae9abb6205bc417d95152d579`; tree `b2482f4508126b879d1942f9c1c4e0f8bd17cec3`.
База library `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`; diff только verify.rs и verify/helper_contracts.rs.
Статика PASS: прежние 246 корней/замыканий сохранены; новые PFC+exercise совпадают с 44b972435a в разрешённых границах.
Source inventory: ordinary 235, cfg-on 248; smallsort.rs byte-identical; tooling unchanged; rustfmt PASS; >100/лексика пусто.
G1 `4da67e0b-a086-459c-8287-f3ae365566dc` / source `db5d23de550329235552a2691e69378c148c3f42`: SUCCESS, COMPLETE, gate true, Kani exit 1.
Отклонение согласовано координатором 2026-11-07: G1 paid 105 вместо 100 мин; плановый резерв G1+G2 $2.4165 <= cap $2.50.

| PFC | status | seconds | failed/total; covers | previous seconds |
| --- | --- | --- | --- | --- |
| insertion_safety_u64_len2 | SUCCESS | 55.339634 | 0/164; 6/6 | 81.02985 |
| insertion_safety_u64_len3 | SUCCESS | 63.423126 | 0/164; 6/6 | 105.375145 |

| Control (verify::) | status | full failed checks (exactly 1) | designated match |
| --- | --- | --- | --- |
| fixed_inputs::reject_mutant_swap_u8_n2 | FAILED | `assertion failed: v[0] <= v[1]` @ smallsort/verify/fixed_inputs.rs:25 | yes |
| merge::profiles::profile_full_value_checker_rejects_payload_change_u8 | FAILED | `full-value checker detects payload corruption` @ smallsort/verify/merge/profiles.rs:347 | yes |
| merge::profiles::profile_wrong_f_insert_rejected_u8 | FAILED | `profile_canonical_comparator::<P>(cmp)` @ smallsort/verify/merge/profiles.rs:273 | yes |
| merge::profiles::profile_wrong_f_merge_rejected_u8 | FAILED | `profile_canonical_comparator::<P>(cmp)` @ smallsort/verify/merge/profiles.rs:311 | yes |
| merge::profiles::profile_wrong_f_sort4_rejected_u64 | FAILED | `profile_canonical_comparator::<P>(cmp)` @ smallsort/verify/merge/profiles.rs:237 | yes |
| merge::profiles::profile_wrong_f_swap_rejected_u8 | FAILED | `profile_canonical_comparator::<P>(cmp)` @ smallsort/verify/merge/profiles.rs:212 | yes |
| tag_permutation::reject_duplicate_network_u8_n9 | FAILED | `every input tag occurs exactly once` @ smallsort/verify/tag_permutation.rs:55 | yes |
| helper_contracts::rejects_insert_tail_equal_begin_u64 | FAILED | `begin < tail && insert_tail_contract_len(begin, tail) > 1 && crate::ub_checks::can_dereference(ptr::slice_from_raw_parts(begin, insert_tail_contract_len(begin, tail),)) && crate::ub_checks::can_write(ptr::slice_from_raw_parts_mut(begin, insert_tail_contract_len(begin, tail),))` @ smallsort.rs:588 | yes |
| helper_contracts::rejects_merge_overlapping_dst_u64 | FAILED | `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` @ smallsort.rs:859 | yes |
| helper_contracts::rejects_swap_comparator_writing_outside_frame_u8 | FAILED | `Check that *var_9 is assignable` @ smallsort/verify/helper_contracts.rs:276 | yes |
| helper_contracts::rejects_swap_outside_backing_u8 | FAILED | `crate::ub_checks::can_dereference(v_base.wrapping_add(b_pos)) && crate::ub_checks::can_write(v_base.wrapping_add(b_pos))` @ smallsort.rs:409 | yes |
| forwarding_contracts::rejects_always_true | FAILED | `canonical comparator required` @ smallsort/verify/forwarding_contracts.rs:60 | yes |
| forwarding_contracts::rejects_payload_corruption | FAILED | `full-value checker rejects payload corruption` @ smallsort/verify/forwarding_contracts.rs:270 | yes |

У двух requires Kani указывает начало атрибута (588/409), packet — выражение (589/410); полный текст совпадает; ожидания сохранены.
G2 `8de198b9-953d-4b19-9eb2-76f90e5a14a4` / source `78d7112ea367dd9a23e588367f2b436876778c0e`: SUCCESS, COMPLETE, gate true, Kani exit 0; тот же library tree.
Cfg-on compiler inventory: 248 уникальных имён, exact match; sorted SHA256 `6d6cd89142e2f8242eb6f1cf6f6b065a11926af2eb16b2939492c59296eb8a61`.
Warnings: целевые bounded scans G1/G2 пусты. Расход: G1 $0.1485 + G2 $0.5940 = $0.7425 из $2.50; резерв $0; 2/2 сборки.
Четыре unreachable non-cover checks на каждом PFC сохранены отдельно; доказаны только указанные u64/len2/len3 домены.
Подробные identities, полный состав failed checks и страницы inventory: insertpfc/{g1,g2}-evidence/verification-report.json.
INSERTPFC ЗАВЕРШЁН.
