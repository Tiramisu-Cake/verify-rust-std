# KANI3300 T1b-A3 — RESULT
Build35308c57-41d6-4057-943d-c55eb28642ad: Cloud FAILURE; Kani build SUCCESS245s; verify COMPLETE, exit1/gate=false; setup/compile/timeout отказа нет.
Head f2990957c8199fea4600b6123ebaeb0a917df775; request SHA2565b82ada544e8eced4e72a10e4e22c8b71eef892bde4aed34f9309d74e9a414bd — MATCH.
Kani989f72351c неизменён; library919cc3e2dc5fb19ea6e7f7be761914b949160a41/applied53927d9bc0ccbff8183aa91ffb6c29d1c8a74465; pin/patch/argv/env/tooling identities MATCH (EVIDENCE-INDEX.json).

| Root suffix uninit_probe:: | A3 = A2 verdict | Failed/total checks | Covers |
|---|---|---|---|
| cmp3_index_range_len | FAILED | 2/28 | 1/1 |
| cmp3_polymorphic_sized_len | FAILED | 2/142 | 2/2 |
| cmp3_polymorphic_unsized_len | FAILED | 2/142 | 2/2 |
| cmp3_manually_drop_unsized_len | SUCCESS | 0/92 | 2/2 |
| cmp3_into_iter_len | SUCCESS | 0/149 | 1/1 |
| cmp3_into_iter_next | SUCCESS | 0/254 | 3/3 |
| small_sort_general_with_scratch_u8_n4 | SUCCESS | 0/550 | 1/1 |
| pincheck_calibration_uninit_read_u8 | FAILED (expected) | 1/30 | 3/3 |
| pincheck_calibration_init_read_u8 | SUCCESS | 0/31 | 3/3 |

Все9 verdict/check/cover counts совпали с A2; прежние2 uninit usize checks index_range.rs:57 и calibration uninit u8 mem/mod.rs:1283 сохранены.
Trace OVERSIZED, complete=false, seen929/emitted374/omitted555; validator errors=[]; sidecar254788B при producer cap256000B.
Footer сохранён в summary: stateOVERSIZED/seen929/emitted374/omitted555/bytes_before_footer253931; отдельная footer observation имеет статус UNVALIDATED, согласована с принятым coverage.
Footer omission_counts: oversized_records555, external_cache_witness_cap6951, external_witness_cap189, mir_excerpt_bytes208884, mir_selected_lines248; это разные единицы, не суммируются.
Sidecar SHA256d6046f88c19e54f9efdaf329648c6cdcc5da36045bd8bbb7be3caf910fbb46e4; footer-line SHA2563caa730cb9c5a703c84b2199791c327fda0b00e620fb0870bf3d03412a606eac.
Ключевые записи получены только trace-field; seq ниже в invocation8611:0, unit1; страницы/receipts/SHA256 — evidence/35308c57/, выборка TRACE-KEYS.json.
Warmup cmp3_index_range_len: root miss_creator96, writer117 local_pass_5, zero_ops103–116; actual IndexRange::len miss_creator120, zero_ops127–134, hash8e83681b4d5b4436 (121/135/136).
Warmup cmp3_manually_drop_unsized_len: root miss_creator178/writer195 local_pass_5/zero_ops185–194; actual IndexRange::len hit241, тот же hash8e83681b4d5b4436 (242).
Его adapter miss_creator198/writer238 local_pass_5; выбраны LoadArgument/StoreArgument/AssignUnion/CheckRef (209–228), есть zero_ops205–208/223–224/229–237; это selection, не runtime execution.
Calibration init/uninit warmup: root miss_creator138/244, writers165/266 local_pass_5; выбраны LoadArgument147/265 и StoreArgument150/254, прочие показанные инструкции zero_ops; hashes после local_pass_5: 6bb412e844e8405b/673a2a5c007ac4e8 (167/268).
Наблюдаемый unit1 writer actual len: DelayedUbPass299 в codegen cmp3_into_iter_next; до280 hash8e83681b4d5b4436 → после298 hash9bae019701b64b9b, CheckRef290/293 для ((*_1).1/.0:usize).
Relevance282/284 выбирает обе проверки с witness Stack(cmp3_into_iter_next,_3); 281/283/285–287 — skip_no_common_ancestor/skip_not_target. Затем hit307/hash9bae…308 в cmp3_into_iter_len.
Это наблюдаемая compile-time цепочка reuse; её runtime-причинность в failing root не установлена. Unit0 scratch имеет отдельный cache; его writer88 не приписывается unit1.
В сохранённых374 records нет codegen-контекста четырёх ключевых roots и нет function_presence; actual len виден в warmup index/manual, но per-root codegen presence/last writer/MemoryInitOps UNKNOWN, не NOT_RUN/не доказанное inlining.
27 страниц прочитаны вручную по next_start до null; page complete=true не означает trace complete. Из-за555 omissions полного сравнения шага1/4 и calibration codegen нет.
Brief exit1 HTTP404; используются явно разрешённые bounded K1 summary/trace-field. Archive/index integrity и independent B1/B2 proof credit не установлены; raw fallback не применялся.
Стоимость k1g.sh rounded pool ledger: A3$0.1215, terminal reserve$0.0000 (initial$0.5265); A+A2+A3$0.3240 из cap$0.80; остаток$0.4760 не разрешает Build.
Одна попытка; повторов/B/source/tooling repair нет. RESULT-CHECK.json PASS: receipts/identity/page-chain/coverage и все9 сравнений; Kani clean, локальный compiler/verifier NOT_RUN.
Стоп: исходные failures воспроизведены, bounded trace доступен, но обрезан; недостающие555 записей, concrete object/offset/R и полная причинность UNKNOWN; proof credit NONE.
