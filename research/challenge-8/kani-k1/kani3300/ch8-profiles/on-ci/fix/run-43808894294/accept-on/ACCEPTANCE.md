# PROF-ON-02 — worker15 intake

61 ACCEPTED / 2 BLOCKED_TOOL / 0 REJECTED / 0 PENDING; все 63 строки классифицированы заново.
53 positive admissions и 8 negative admissions. Исторические admissions не перенесены.
Assurance: `BOUNDED_SOURCE_REPORTED_POLICY_ADMISSION; NOT_INDEPENDENT_PROOF`; proof credit `NONE`, B2 не установлен.

## Exact inputs

- g0 task package: `7d1ae3dd048e50b245817fadbcdfb4244153669c`; source `166a406e2203bae2fc9246ba00c00b944b364445` (tree `460029c0d95fa7ef04eb7da0115f6fa2792c3b0b`).
- ON tool `14bc57fdb99960240c4944845a3d985c8af4dcf7`; control trigger `5710dd67580bb62749a8b25c4c4f685780dfc2c8`.
- Run `43808894294`, artifact ID `14203740678`, directory `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/prof02/on`.
- Request SHA256 `b3714a13cff56c278fc3cac9fdc8df9efc8428e63bd48496076327001556711b`; previous ON ACCEPT SHA256 `7a5b260ccc5a187bae6ccb3362dfb6bb89ad300d84de9f0b2bb8cfdc0f8b5b2d`.
- Directory→artifact ID связь передана coordinator; независимой archive attestation нет.
- Runner inputs сохранены в `runner-input/`, побайтно сверены с выполненным trigger. На VPS исполнялись только static parser/classifier functions.
- Источник, binding adapter/spec, manifest, runner/request, tool source chain и compiler features/checks/config проверены по exact identities; SHA256 перечислены в ACCEPT.json.

| Group | Export SHA256 | cfg |
|---|---|---|
| group-00 | `260ccaeb37e331a6c82de16aa10bc6a858ee55d2f6ca36f0c039cb21b705a301` | `[]` |
| group-01 | `e5203e8532e95ce482897106f80da9df523ff0d8dc1e9480191b480d74918e8a` | `['kani_smallsort_controls']` |

## Admission gates

Использованы ON intake accept-v4, прежние v2 completeness/policy и v3 role gates; fresh `fix/binding_v02.py` проверяет новые source sites, full target/profile/wrapper, pre/post/assigns, covers и frame oracle. Сохранены все unsupported, failures, unreachable и emitted covers. Regular stdout прочитан только bounded `rg`: ID/status inventory, exact selected IDs с контекстом ≤12 строк, terminal markers с sentinel; полные raw logs не читались.

61 admissions имеют BOUND binding, пустые unknown/pending причины. Accepted positive имеет Kani SUCCESS; accepted negative — только predeclared named failures. Group exit 1 сохранён в original_receipt и не заменяет row verdict. Все 63 exact harnesses присутствуют; 54 legacy INCOMPLETE_CHECK_INVENTORY и 9 VALIDATED_OBSERVATION переоценены политикой.

Fresh source translation единственного изменившего координаты defensive rule: regions_are_disjoint negate guard, merge.rs old111→new114; строка побайтно неизменна. Никаких blanket helper/uninit exemptions. 1782 defensive +583 instrumentation defensive +2 postcondition +1 frame +20 UNKNOWN unreachable записей сохранены; required/UNKNOWN остаются blockers в двух tool-blocked строках.

Всего 183 SAT covers и 7 unreachable covers; из SAT 180 в admissions и 3 в tool-blocked negative. 389 SUCCESS unsupported и 2 FAILURE unsupported сохранены, включая exact ID/class/site/description и pinned assert(false)→assume(false) generator semantics. SAT не устанавливает полную domain/branch coverage или независимость assumptions.

`profile_merge4_contract_u8_len4` — свежий accepted leaf:
`core::slice::sort::shared::smallsort::verify::merge::profiles::merge4_profile::<core::slice::sort::shared::smallsort::verify::merge::profiles::LtU8>`.
Его checked/modifies wrapper: `{closure#3}::{closure#2}`. Consumer len4 использует replacement `{closure#2}`, зависит только от этого нового leaf; exact instance и source/tool/tree/config/features/cfg tuple совпадают. Старый merge_contract_u8_n2_to4 не подставлялся.

Frame negative заново связан с `rejects_swap_comparator_writing_outside_frame_u8::{closure#0}.assigns.1`, helper_contracts.rs:290:9, `Check that *var_9 is assignable`; sole failure. Критерий остаётся captured counter write вне двух swap targets. Независимая pointer trace к var_9 не установлена; credit NONE.

## Два tool blockers

- `freeze_noncopy_n2`: единственный failure — PolymorphicIter memory-initialization unsupported. 7 required covers UNREACHABLE, 2 postconditions и frame недостижимы, 14 UNKNOWN roles; binding PENDING сохраняет exact observations. Это не успешная проверка контракта.
- `rejects_always_true`: тот же unsupported плюс собственные assertion.4/.6 failures; assertion.2 UNREACHABLE. 6 UNKNOWN roles сохранены. Negative не принимается целиком. Предсказанный lexical cover ordinal не совпал с emitted match-arm order (.1 Freeze@229, .2 unstable@220, .3 stable@211); `FRESH_BINDING:COVER_SOURCE_LINE_MISMATCH` остаётся вторичным unresolved gate, фактические exact records сохранены.

## Построчное сравнение с ON run 43798838603

49 ACCEPTED→ACCEPTED; 11 BLOCKED_TOOL→ACCEPTED; 2 BLOCKED_TOOL→BLOCKED_TOOL; новый merge4 leaf ACCEPTED. В ACCEPT.json для каждой строки сохранены предыдущий/нынешний failure inventory, cover buckets, target, added/removed unreachable IDs; старые данные используются только для сравнения.

| Row | Previous ON | Current | Binding | Failures | Covers SAT/total |
|---|---|---|---|---:|---:|
| `swap_contract_four_positions_u8` | ACCEPTED | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_four_positions_i32` | ACCEPTED | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_four_positions_u64` | ACCEPTED | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_u8_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_u64_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_drop_u8_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_cell_i32_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_bytes16_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_bytes17_n2` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 5/5 |
| `swap_contract_u8_indices_n17` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `swap_contract_u64_indices_n17` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `swap_contract_u8_n9` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `swap_contract_u8_n13` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `swap_contract_u64_n9` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `insert_tail_contract_u64_start1_tail2_to8` | ACCEPTED | ACCEPTED | BOUND | 0 | 9/9 |
| `insert_tail_contract_u64_start1_tail9_to12` | ACCEPTED | ACCEPTED | BOUND | 0 | 6/6 |
| `insert_tail_contract_u64_start1_tail13_to14` | ACCEPTED | ACCEPTED | BOUND | 0 | 4/4 |
| `insert_tail_contract_u64_start1_tail15_to16` | ACCEPTED | ACCEPTED | BOUND | 0 | 4/4 |
| `contract_insert_tail_u8_prefix` | ACCEPTED | ACCEPTED | BOUND | 0 | 4/4 |
| `sort4_contract_u64_n4` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `sort4_contract_bytes16_n4` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u64_n2_to4` | ACCEPTED | ACCEPTED | BOUND | 0 | 6/6 |
| `merge_contract_u8_n2_to4` | ACCEPTED | ACCEPTED | BOUND | 0 | 6/6 |
| `merge_contract_u64_n5` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u8_n5` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u64_n6` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u8_n6` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u64_n7` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u8_n7` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u64_n8` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u8_n8` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_contract_u8_n9` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `merge_scratch48_contract_u8_n9` | ACCEPTED | ACCEPTED | BOUND | 0 | 2/2 |
| `profile_relation_lt_u8` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_lt_i32` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_lt_u64` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_read_u64` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_read_b16` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_strict_u8` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_strict_u64` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_cell_i32` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_drop_u8` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_key_b16` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_relation_key_b17` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `stable_cell_n2` | ACCEPTED | ACCEPTED | BOUND | 0 | 9/9 |
| `unstable_byte_n2` | ACCEPTED | ACCEPTED | BOUND | 0 | 7/7 |
| `freeze_noncopy_n2` | BLOCKED_TOOL | BLOCKED_TOOL | PENDING | 1 | 0/7 |
| `profile_swap_consumer_u8_backing4` | ACCEPTED | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_sort4_consumer_u64` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_sort4_consumer_b16` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_insert_consumer_u8_backing17` | ACCEPTED | ACCEPTED | BOUND | 0 | 3/3 |
| `profile_merge4_contract_u8_len4` | NEW_ROW | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_merge_consumer_u8_len4` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 1/1 |
| `profile_wrong_f_swap_rejected_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `profile_wrong_f_sort4_rejected_u64` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `profile_wrong_f_insert_rejected_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `profile_wrong_f_merge_rejected_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `profile_bad_relation_rejected_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `profile_full_value_checker_rejects_payload_change_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `rejects_always_true` | BLOCKED_TOOL | BLOCKED_TOOL | PENDING | 3 | 3/3 |
| `rejects_payload_corruption` | ACCEPTED | ACCEPTED | BOUND | 1 | 1/1 |
| `swap_safety_u8_backing4` | BLOCKED_TOOL | ACCEPTED | BOUND | 0 | 6/6 |
| `rejects_swap_comparator_writing_outside_frame_u8` | ACCEPTED | ACCEPTED | BOUND | 1 | 0/0 |

## Validation и границы

Fresh offline replay: 63/63; 16 synthetic tests PASS (включая wrong full target, failed postcondition, missing/non-SAT cover, source/oracle drift exact negative source/function/site и duplicate terminal markers). Independent Luna HIGH static audit: marker-count finding исправлен, delta проверена, открытых findings нет. См. REVIEW.md и VALIDATION.json.

Только одна назначенная intake-стадия. Без push, CI/dispatch, публикаций, ledger и локальных cargo/rustc/Kani/CBMC. OFF lane и исторические receipts/ledgers не изменялись.
