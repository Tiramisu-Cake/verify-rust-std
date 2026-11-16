# Profiles OFF — acceptance v4

Вход g0 `57ff2242017bf6356f78245d92d871e2534c2c7d`; исходный accept-v3 из
`2f7418a815`, SHA256 `947e1bb9c615d61007fc97ada6a732c098fd69c5d9085268fe5310999b0d4396`.
Run `43784551069`, artifact `14190662926`, ZIP SHA256
`6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9`.
Source `9fa2f7f97760584f38738909625c064006d8a936`; stock Kani
`0aac16ef62da9e9d5645782d458593e5d78143ba`; control
`112fcc9ada67ee2bb8e1712d47983d6717487b78`.

**62 ACCEPTED / 0 PENDING / 0 UNKNOWN**: 53 positive и 9 negative.
Это admission bounded source-reported observations по принятой batch policy.
Independent proof credit **NONE**; B2/full-domain theorem не установлен.
19 принятых v3 строк перенесены без изменения из hash-pinned reviewed receipt;
43 unresolved строки получили exact binding. Старые документы и receipts не менялись.

В задании «42 PFC» означает 42 unresolved positive: фактически manifest содержит
37 positive PFC, 5 Replace-consumers и ещё 1 negative PFC (38 PFC всего).
Все эти 43 строки обработаны; consumers пересчитаны после leaf и дополнительно
проверены на равенство полного специализированного instance.

`contract.contracted_function_name` обозначает вложенный modifies-wrapper,
а check-wrapper — его родительская closure. Pinned macro/compiler/driver chain,
exact raw symbol в metadata и stdout `single_top_level_call`/`no_recursive_call`,
полный decoded target/profile, literal clause и source site связывают их вместе.
Число closure само по себе не используется для определения роли.
PFC requires — assumptions, postconditions — assertions; у Replace наоборот.
Ни отсутствие requires-assertions у PFC, ни assumed post у consumer не объявляется
доказательством их истинности. Полные записи — ACCEPT.json / exact_binding_v4.

Все 168 covers затронутых positive строк сверены с exact stdout ID, SAT status,
function, source site либо macro invocation. Исторические pre-call/callback-only
covers не стали post-target. Есть две уточнённые связи:

- insert_tail: runtime subtraction check занимает assertion.1; postconditions —
  assertion.2/.3, precondition consumer — assertion.2. Binding делается по
  function + source site + clause, а не lexical assertion ordinal.
- merge len2..4: cover.1 относится к длине4, cover.3 — к длине2 (cover.2 — длина3).
  Старое соответствие lexical ordinal в v2/v3 ошибочно; в v4 исправлено по literal
  description + точному macro invocation. Все три остаются post-target.
  Порядок stdout Check не трактуется как порядок выполнения.

Frame oracle принят по заранее заявленному semantic criterion «generated modifies
property for captured comparisons». Единственный failure — exact `.assigns.1`
в comparator closure harness на helper_contracts.rs:276 (`comparisons = ...`).
Эта closure является F в полном target instance; sole enforced contract указывает
на swap_if_less modifies-wrapper с write set только двух элементов.
Это source-reported class/site binding; независимый trace pointer→var_9 не установлен.
Manifest placeholder, historical outcome и descriptions не переписаны, произвольный
FAILURE не принимается. Подробная связь и ограничения — BINDING.md.

20 targeted synthetic tests PASS. Offline replay на pinned ZIP даёт 62/62;
независимое review фиксируется отдельным REVIEW.json после проверки candidate.
Новый runner/export не требуется для текущего policy scope; желаемое компактное
расширение следующего export перечислено в BINDING.md. CI сейчас не запускался.

| Строка | Режим binding | Kani | V4 |
|---|---|---|---|
| `swap_contract_four_positions_u8` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_four_positions_i32` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_four_positions_u64` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u8_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u64_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_drop_u8_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_cell_i32_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_bytes16_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_bytes17_n2` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u8_indices_n17` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u64_indices_n17` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u8_n9` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u8_n13` | PFC | SUCCESS | ACCEPTED |
| `swap_contract_u64_n9` | PFC | SUCCESS | ACCEPTED |
| `insert_tail_contract_u64_start1_tail2_to8` | PFC | SUCCESS | ACCEPTED |
| `insert_tail_contract_u64_start1_tail9_to12` | PFC | SUCCESS | ACCEPTED |
| `insert_tail_contract_u64_start1_tail13_to14` | PFC | SUCCESS | ACCEPTED |
| `insert_tail_contract_u64_start1_tail15_to16` | PFC | SUCCESS | ACCEPTED |
| `contract_insert_tail_u8_prefix` | PFC | SUCCESS | ACCEPTED |
| `sort4_contract_u64_n4` | PFC | SUCCESS | ACCEPTED |
| `sort4_contract_bytes16_n4` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u64_n2_to4` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n2_to4` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u64_n5` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n5` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u64_n6` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n6` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u64_n7` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n7` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u64_n8` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n8` | PFC | SUCCESS | ACCEPTED |
| `merge_contract_u8_n9` | PFC | SUCCESS | ACCEPTED |
| `merge_scratch48_contract_u8_n9` | PFC | SUCCESS | ACCEPTED |
| `profile_relation_lt_u8` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_lt_i32` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_lt_u64` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_read_u64` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_read_b16` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_strict_u8` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_strict_u64` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_cell_i32` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_drop_u8` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_key_b16` | v3 unchanged | SUCCESS | ACCEPTED |
| `profile_relation_key_b17` | v3 unchanged | SUCCESS | ACCEPTED |
| `stable_cell_n2` | PFC | SUCCESS | ACCEPTED |
| `unstable_byte_n2` | PFC | SUCCESS | ACCEPTED |
| `freeze_noncopy_n2` | PFC | SUCCESS | ACCEPTED |
| `profile_swap_consumer_u8_backing4` | Replace | SUCCESS | ACCEPTED |
| `profile_sort4_consumer_u64` | Replace | SUCCESS | ACCEPTED |
| `profile_sort4_consumer_b16` | Replace | SUCCESS | ACCEPTED |
| `profile_insert_consumer_u8_backing17` | Replace | SUCCESS | ACCEPTED |
| `profile_merge_consumer_u8_len4` | Replace | SUCCESS | ACCEPTED |
| `profile_wrong_f_swap_rejected_u8` | v3 unchanged | FAILURE | ACCEPTED |
| `profile_wrong_f_sort4_rejected_u64` | v3 unchanged | FAILURE | ACCEPTED |
| `profile_wrong_f_insert_rejected_u8` | v3 unchanged | FAILURE | ACCEPTED |
| `profile_wrong_f_merge_rejected_u8` | v3 unchanged | FAILURE | ACCEPTED |
| `profile_bad_relation_rejected_u8` | v3 unchanged | FAILURE | ACCEPTED |
| `profile_full_value_checker_rejects_payload_change_u8` | v3 unchanged | FAILURE | ACCEPTED |
| `rejects_always_true` | v3 unchanged | FAILURE | ACCEPTED |
| `rejects_payload_corruption` | v3 unchanged | FAILURE | ACCEPTED |
| `swap_safety_u8_backing4` | PFC | SUCCESS | ACCEPTED |
| `rejects_swap_comparator_writing_outside_frame_u8` | PFC | FAILURE | ACCEPTED |

Push / CI / публикаций / ledger / local cargo-rustc-Kani-CBMC: 0.
