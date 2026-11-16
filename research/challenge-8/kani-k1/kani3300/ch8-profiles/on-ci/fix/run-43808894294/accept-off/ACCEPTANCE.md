# PROF-ON-02 — OFF intake worker11

Run `43808894294`, artifact `14204858070`; предыдущий OFF run `43784551069 / accept-v4`.
**63 ACCEPTED / 0 BLOCKED_TOOL / 0 REJECTED / 0 PENDING**: 54 positive, 9 negative.
Это fresh policy admission bounded source-reported evidence; independent proof credit **NONE**, B2/full-domain theorem не установлен. Исторических admissions перенесено **0**.

Source `166a406e2203bae2fc9246ba00c00b944b364445`, tree `460029c0d95fa7ef04eb7da0115f6fa2792c3b0b`; stock Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`; trigger `5710dd67580bb62749a8b25c4c4f685780dfc2c8`.
Request SHA256 `22f9d675279993ad2bf4cd28bf264a601e3671671b85793483c49a22e950d21d`; manifest `a14783b093b32944440bd53c1b734be8ccde54baff053df25fcf959cb7a8cc0a`.

Полные exact bindings, ID/status/function/file/line, clause/cover roles, unsupported links, unreachable reviews, исходные exits/runner states и построчные previous_off_comparison находятся в [ACCEPT.json](ACCEPT.json). Все 63 строки вычислены из новых exports и bounded stdout queries; предыдущий receipt используется только для сравнения.

Проверены pinned source-file hashes, macro/compiler/driver contract chain, полный специализированный target, source attributes, verified stubs, cfg, exact argv, source/tool fingerprints до/после, unwind, enabled checks, complete export↔stdout ID/status inventory. Остались включены memory/overflow/unwinding/undefined-function/reachability checks. OFF не использует ON admissions.

Legacy SOURCE_STAGE_TARGET_MISMATCH перепроверен mature parser без устаревшего terminal-name predicate; все последующие config/mode/unwind gates сохранены, полный predeclared source expression проверен отдельно. INCOMPLETE_CHECK_INVENTORY обработан v2/v3/v4 complete-inventory policy. Исходные статусы не переписаны.

Две свежие конкретизации predicted binding:

- regions_are_disjoint: negate-overflow guard перенесён со строки111 на114. Тело функции побайтно совпадает с прежним pinned source; fresh ID/function/file/line/description связан с тем же defensive geometry guard для u8/u64/[u8;16]. Это 18 occurrences; actual geometry predicate не исключён.
- rejects_always_true: cover.1 — Freeze,229; cover.2 — unstable,220; cover.3 — stable,211. SPEC предсказывал lexical order. Связь установлена по точному literal description, source statement, function и location; required IDs/смысл/oracle не изменены. Covers остаются negative reach witnesses, не post-return.

Все 190 covers SAT (180 positive +10 negative), все 1770 unreachable checks получили явный defensive role, все 209 unsupported records SUCCESS и связаны с assert(false); assume(false) semantics stock Kani. Ни один failure не исключён. У negatives 11 failure properties на 9 строках соответствуют прежним named criteria: обычные — exact assertion/source statement; frame — единственный assigns.1 captured comparisons на helper_contracts.rs:290. Trace pointer→var_9 независимо не установлен; это source-reported class/site binding.

Новый profile_merge4_contract_u8_len4 принят по fresh LtU8/merge4_profile contract symbol, requires/modifies/ensures и post-return cover. Consumer profile_merge_consumer_u8_len4 после leaves связан только с этим leaf: тот же specialized instance, source/tool/config export, OFF lane и текущий run. PFC requires остаются assumptions, PFC ensures — checked assertions; consumer asserts requires и предполагает postconditions принятого leaf. Роли wrappers связаны metadata и pinned macro/compiler chain; closure ordinal сам по себе роли не задаёт. Старый merge_contract_u8_n2_to4 не подставлялся. Оба general merge n2..4 harness сохранены.

С предыдущим OFF receipt: все 62 прежних verdict остались ACCEPTED; добавлен 1 fresh leaf. Covers189→190, unreachable1710→1770, successful unsupported205→209 (все строки, включая negatives). У sort4 bytes16 leaf и его consumer unreachable73→68; новый merge4 leaf добавляет 70 unreachable и 4 successful unsupported. Исторические summary claims не заменяют эти receipt counts.

| Строка | OFF43784551069 → OFF43808894294 | Kani | covers SAT до→после | unreachable до→после | unsupported до→после |
|---|---|---|---|---|---|
| `swap_contract_four_positions_u8` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_four_positions_i32` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_four_positions_u64` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_u8_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_u64_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_drop_u8_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_cell_i32_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_bytes16_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_bytes17_n2` | ACCEPTED → ACCEPTED | SUCCESS | 5→5 | 4→4 | 4→4 |
| `swap_contract_u8_indices_n17` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 4→4 | 4→4 |
| `swap_contract_u64_indices_n17` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 4→4 | 4→4 |
| `swap_contract_u8_n9` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 4→4 | 4→4 |
| `swap_contract_u8_n13` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 4→4 | 4→4 |
| `swap_contract_u64_n9` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 4→4 | 4→4 |
| `insert_tail_contract_u64_start1_tail2_to8` | ACCEPTED → ACCEPTED | SUCCESS | 9→9 | 52→52 | 5→5 |
| `insert_tail_contract_u64_start1_tail9_to12` | ACCEPTED → ACCEPTED | SUCCESS | 6→6 | 44→44 | 5→5 |
| `insert_tail_contract_u64_start1_tail13_to14` | ACCEPTED → ACCEPTED | SUCCESS | 4→4 | 40→40 | 5→5 |
| `insert_tail_contract_u64_start1_tail15_to16` | ACCEPTED → ACCEPTED | SUCCESS | 4→4 | 36→36 | 5→5 |
| `contract_insert_tail_u8_prefix` | ACCEPTED → ACCEPTED | SUCCESS | 4→4 | 34→34 | 5→5 |
| `sort4_contract_u64_n4` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 68→68 | 4→4 |
| `sort4_contract_bytes16_n4` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 73→68 | 4→4 |
| `merge_contract_u64_n2_to4` | ACCEPTED → ACCEPTED | SUCCESS | 6→6 | 70→70 | 4→4 |
| `merge_contract_u8_n2_to4` | ACCEPTED → ACCEPTED | SUCCESS | 6→6 | 70→70 | 4→4 |
| `merge_contract_u64_n5` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 68→68 | 4→4 |
| `merge_contract_u8_n5` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 68→68 | 4→4 |
| `merge_contract_u64_n6` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 66→66 | 4→4 |
| `merge_contract_u8_n6` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 66→66 | 4→4 |
| `merge_contract_u64_n7` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 64→64 | 4→4 |
| `merge_contract_u8_n7` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 64→64 | 4→4 |
| `merge_contract_u64_n8` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 62→62 | 4→4 |
| `merge_contract_u8_n8` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 62→62 | 4→4 |
| `merge_contract_u8_n9` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 60→60 | 4→4 |
| `merge_scratch48_contract_u8_n9` | ACCEPTED → ACCEPTED | SUCCESS | 2→2 | 61→61 | 4→4 |
| `profile_relation_lt_u8` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_lt_i32` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_lt_u64` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_read_u64` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 2→2 | 2→2 |
| `profile_relation_read_b16` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 2→2 | 2→2 |
| `profile_relation_strict_u8` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_strict_u64` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_cell_i32` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_drop_u8` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 2→2 | 2→2 |
| `profile_relation_key_b16` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `profile_relation_key_b17` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 0→0 | 0→0 |
| `stable_cell_n2` | ACCEPTED → ACCEPTED | SUCCESS | 9→9 | 10→10 | 4→4 |
| `unstable_byte_n2` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 32→32 | 4→4 |
| `freeze_noncopy_n2` | ACCEPTED → ACCEPTED | SUCCESS | 7→7 | 19→19 | 4→4 |
| `profile_swap_consumer_u8_backing4` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 4→4 | 4→4 |
| `profile_sort4_consumer_u64` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 68→68 | 4→4 |
| `profile_sort4_consumer_b16` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 73→68 | 4→4 |
| `profile_insert_consumer_u8_backing17` | ACCEPTED → ACCEPTED | SUCCESS | 3→3 | 34→34 | 5→5 |
| `profile_merge4_contract_u8_len4` | NEW → ACCEPTED | SUCCESS | —→1 | —→70 | —→4 |
| `profile_merge_consumer_u8_len4` | ACCEPTED → ACCEPTED | SUCCESS | 1→1 | 71→71 | 4→4 |
| `profile_wrong_f_swap_rejected_u8` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 4→4 | 3→3 |
| `profile_wrong_f_sort4_rejected_u64` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 32→32 | 3→3 |
| `profile_wrong_f_insert_rejected_u8` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 33→33 | 3→3 |
| `profile_wrong_f_merge_rejected_u8` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 34→34 | 3→3 |
| `profile_bad_relation_rejected_u8` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 0→0 | 0→0 |
| `profile_full_value_checker_rejects_payload_change_u8` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 60→60 | 3→3 |
| `rejects_always_true` | ACCEPTED → ACCEPTED | FAILURE | 3→3 | 20→20 | 3→3 |
| `rejects_payload_corruption` | ACCEPTED → ACCEPTED | FAILURE | 1→1 | 18→18 | 3→3 |
| `swap_safety_u8_backing4` | ACCEPTED → ACCEPTED | SUCCESS | 6→6 | 4→4 | 4→4 |
| `rejects_swap_comparator_writing_outside_frame_u8` | ACCEPTED → ACCEPTED | FAILURE | 0→0 | 4→4 | 4→4 |

17 targeted Python tests PASS: legacy/config/identity/unwind/NOT_RUN/partial selection, cover absence, unsupported class, source-site mismatch, exact negative, fresh role translation и consumer leaf/instance/config mismatch. Independent review — [REVIEW.json](REVIEW.json).

Без push/CI/публикаций/ledger/local cargo-rustc-Kani-CBMC. Артефакты read-only; raw logs целиком не читались.
