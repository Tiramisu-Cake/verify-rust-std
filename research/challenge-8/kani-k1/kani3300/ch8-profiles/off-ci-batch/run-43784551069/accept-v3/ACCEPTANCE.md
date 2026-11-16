# Profiles OFF — acceptance v3

Вход g0 `28a11b9b7af6d76c951df6518323af4a72b84919`; run `43784551069`,
artifact `14190662926`, ZIP SHA256 `6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9`.

**19 ACCEPTED / 43 PENDING / 0 UNKNOWN** по принятой batch policy.
Positive: 11 ACCEPTED / 42 PENDING; negative: 8 ACCEPTED / 1 PENDING.
Это admission ограниченных source-reported наблюдений; independent proof credit
NONE, B2/full-domain proof не установлен. V2 и все historical receipts неизменны.

62/62 stdout связаны с exact harness через per-row receipt, marker и receipt-разбиение
pinned runner. Обе execution-записи имеют stdout/stderr/output_truncated=false,
timed_out=false, signal=null, без termination_reason. Размеры 9849..368726 bytes
совпадают с compilation.row_output_bytes и строго ниже row cap 1048576.
Compilation receipt побайтно хешируется и структурно совпадает с execution.compilation;
marker order не содержит дублей и совпадает с составом группы. Bounded compile logs
не используются как evidence полноты per-row stdout и не читаются этой стадией.

Парсер проверяет единственный exact marker, RESULTS/SUMMARY/terminal verdict,
полный последовательный список Check N, уникальность всех ID, exact failure,
unreachable и cover IDs/statuses, число SUCCESS и n_properties.
Усечение, ошибочный/частичный блок, дубль или несовпадение дают UNKNOWN всей строке,
включая строки без unreachable. Regular descriptions читаются как literal text:
кавычки и переносы внутри них не интерпретируются как JSON escapes.

1710/1710 unreachable occurrences сопоставлены по exact ID и статусу UNREACHABLE;
каждая запись ACCEPT.json содержит description, file/line/column, function,
номер Check/строки stdout, rule, target/wrapper relation и причину допустимости.
Явные reviewed семейства — ROLE-RULES.json и UNREACHABLE-ROLES.md.
Правила не освобождают helper целиком: допустимы только заданные source sites,
описания арифметических guards и классы property. Unmapped assertion → UNKNOWN;
required post/frame/relation/section → BLOCK/PENDING.
UNREACHABLE означает недостижимость property, а не только невозможность ошибки;
эта стадия не делает вывод о выполнении всего helper по его имени или месту.
Достижение required target/wrapper sections проверяется прежними cover/binding gates.

Остаются 43 exact generated-wrapper bindings PENDING. У одной из этих строк также
независимый predeclared frame oracle PENDING. Все пять consumers вычислены после
leaf и сохраняют MATCHING_LEAF_NOT_ACCEPTED. Эти gates по stdout не закрывались.
Все 62 historical snapshots и прежний ACCEPT.json воспроизведены точно перед v3.
205 unsupported occurrences сохраняют прежние exact assert(false) links;
все required covers и negative oracles остаются под v2 policy.

| Строка | Kani | V3 policy | Оставшиеся причины |
|---|---|---|---|
| `swap_contract_four_positions_u8` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_four_positions_i32` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_four_positions_u64` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u8_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u64_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_drop_u8_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_cell_i32_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_bytes16_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_bytes17_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u8_indices_n17` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u64_indices_n17` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u8_n9` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u8_n13` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `swap_contract_u64_n9` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `insert_tail_contract_u64_start1_tail2_to8` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `insert_tail_contract_u64_start1_tail9_to12` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `insert_tail_contract_u64_start1_tail13_to14` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `insert_tail_contract_u64_start1_tail15_to16` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `contract_insert_tail_u8_prefix` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `sort4_contract_u64_n4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `sort4_contract_bytes16_n4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u64_n2_to4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n2_to4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u64_n5` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n5` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u64_n6` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n6` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u64_n7` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n7` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u64_n8` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n8` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_contract_u8_n9` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `merge_scratch48_contract_u8_n9` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `profile_relation_lt_u8` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_lt_i32` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_lt_u64` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_read_u64` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_read_b16` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_strict_u8` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_strict_u64` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_cell_i32` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_drop_u8` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_key_b16` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `profile_relation_key_b17` | SUCCESS | ACCEPTED | Все применимые gates пройдены |
| `stable_cell_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `unstable_byte_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `freeze_noncopy_n2` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `profile_swap_consumer_u8_backing4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING, MATCHING_LEAF_NOT_ACCEPTED |
| `profile_sort4_consumer_u64` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING, MATCHING_LEAF_NOT_ACCEPTED |
| `profile_sort4_consumer_b16` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING, MATCHING_LEAF_NOT_ACCEPTED |
| `profile_insert_consumer_u8_backing17` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING, MATCHING_LEAF_NOT_ACCEPTED |
| `profile_merge_consumer_u8_len4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING, MATCHING_LEAF_NOT_ACCEPTED |
| `profile_wrong_f_swap_rejected_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_wrong_f_sort4_rejected_u64` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_wrong_f_insert_rejected_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_wrong_f_merge_rejected_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_bad_relation_rejected_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `profile_full_value_checker_rejects_payload_change_u8` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `rejects_always_true` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `rejects_payload_corruption` | FAILURE | ACCEPTED | Все применимые gates пройдены |
| `swap_safety_u8_backing4` | SUCCESS | PENDING | EXACT_CONTRACT_WRAPPER_BINDING_PENDING |
| `rejects_swap_comparator_writing_outside_frame_u8` | FAILURE | PENDING | PREDECLARED_FRAME_ORACLE_BINDING_PENDING, EXACT_CONTRACT_WRAPPER_BINDING_PENDING |

25 новых synthetic tests и 31 прежний policy test PASS. Проверены flags/caps,
missing/null/wrong-type, foreign/duplicate marker, partial block, exact IDs/statuses,
multiline/raw quotes, required-role BLOCK, неизвестная роль, сохранение wrapper и
consumer gates. Независимое Luna HIGH review фиксируется в REVIEW.json после
проверки exact candidate и повторного offline replay. Это только Python/Git/ZIP
analysis, без compiler/verifier execution.

Push / CI / публикаций / ledger writes / local cargo-rustc-Kani-CBMC: 0.
