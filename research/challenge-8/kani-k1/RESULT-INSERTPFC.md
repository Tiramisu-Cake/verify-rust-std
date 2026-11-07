# INSERTPFC — подготовлено; runtime NOT_RUN
Library `a282d08c5afad32ae9abb6205bc417d95152d579`; tree `b2482f4508126b879d1942f9c1c4e0f8bd17cec3`.
База library `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`; diff только verify.rs и verify/helper_contracts.rs.
Статика PASS: прежние 246 корней/замыканий сохранены; новые PFC+exercise совпадают с 44b972435a в разрешённых границах.
Source inventory: ordinary235, cfg-on248; smallsort.rs byte-identical; tooling unchanged; rustfmt PASS; >100/лексика пусто.
GO на dispatch ещё не получен. G1/G2/build identities: NOT_RUN.
Отклонение согласовано координатором 2026-11-07: G1 paid105 вместо100 мин; резерв G1+G2 $2.4165 <= cap $2.50.
| PFC | status | seconds | covers | previous seconds |
| --- | --- | --- | --- | --- |
| insertion_safety_u64_len2 | NOT_RUN | — | — | 81.02985 |
| insertion_safety_u64_len3 | NOT_RUN | — | — | 105.375145 |
| Control (verify::) | status | full failed checks | designated match |
| --- | --- | --- | --- |
| fixed_inputs::reject_mutant_swap_u8_n2 | NOT_RUN | — | — |
| merge::profiles::profile_full_value_checker_rejects_payload_change_u8 | NOT_RUN | — | — |
| merge::profiles::profile_wrong_f_insert_rejected_u8 | NOT_RUN | — | — |
| merge::profiles::profile_wrong_f_merge_rejected_u8 | NOT_RUN | — | — |
| merge::profiles::profile_wrong_f_sort4_rejected_u64 | NOT_RUN | — | — |
| merge::profiles::profile_wrong_f_swap_rejected_u8 | NOT_RUN | — | — |
| tag_permutation::reject_duplicate_network_u8_n9 | NOT_RUN | — | — |
| helper_contracts::rejects_insert_tail_equal_begin_u64 | NOT_RUN | — | — |
| helper_contracts::rejects_merge_overlapping_dst_u64 | NOT_RUN | — | — |
| helper_contracts::rejects_swap_comparator_writing_outside_frame_u8 | NOT_RUN | — | — |
| helper_contracts::rejects_swap_outside_backing_u8 | NOT_RUN | — | — |
| forwarding_contracts::rejects_always_true | NOT_RUN | — | — |
| forwarding_contracts::rejects_payload_corruption | NOT_RUN | — | — |
Cfg-on compiler inventory: NOT_RUN; target248.
Target sorted SHA256 `6d6cd89142e2f8242eb6f1cf6f6b065a11926af2eb16b2939492c59296eb8a61`; runtime equality NOT_RUN.
Warnings: NOT_RUN. Расход $0; текущий резерв $0; плановый максимум $2.4165.
Принятие runtime: NOT_RUN; нового proof credit нет.
