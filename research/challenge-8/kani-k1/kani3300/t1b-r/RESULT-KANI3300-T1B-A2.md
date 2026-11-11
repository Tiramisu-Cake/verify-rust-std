# KANI3300 T1b-R A2 — RESULT
Build `cbf4045a-cf4b-4ac7-8495-dfafcf57f6fb`: Cloud FAILURE, Kani build SUCCESS (252s), verify выполнен, Kani exit1, gate=false.
Head `bddfa044cbb4e884f9140b51c0cc0b9dfc464e58`; request SHA256 `73903bb3f80c34492d575d40d74a4552e4e2d9a55149e578fe05dde01d55035e` — MATCH.
Kani pin f046b70644e113be0df9c22c2e6ea44a65a57566; patch SHA256 0e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298 — MATCH.
Actual applied tree53927d9bc0ccbff8183aa91ffb6c29d1c8a74465 совпал с A2; диагностический commit989f72351c2b5c5f3b5117315fc84f502e66d904.
Класс: PROOF_EXECUTED_ORIGINAL_FAILURE_REPRODUCED_TRACE_INVALID; setup/compile отказа и timeout нет.

| Root suffix (префикс uninit_probe::) | Verdict | Failed/total checks | Covers |
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

Все9 verdict/check-count/cover-count совпали с T1a; индексный и оба polymorphic roots повторили по2 uninit usize checks в core/src/ops/index_range.rs:57.
Calibration pair ожидаемо FAIL/SUCCESS; negative check: uninitialized u8, core/src/mem/mod.rs:1283. Covers после UB не дают proof credit.
diagnostic_trace state=INVALID по штатному reader guard; complete=UNKNOWN, omitted=UNKNOWN, key records=UNKNOWN.
`trace-field state/complete/omitted 0 1` и `records 0 20` вернули exit2: `diagnostic trace state INVALID; pages withheld`.
Ключевые записи cmp3_index_range_len и обоих calibration roots получить нельзя; причина INVALID и полнота producer UNKNOWN, identity guard не обходился.
Brief exit1 HTTP404; bounded summary/rows и точные trace-field ошибки сохранены в evidence/cbf4045a/ с SHA256 в A2-EVIDENCE-INDEX.json.
Verify wall113.45s; longest root31.046s <120s; source-reported данные, не independent B1/B2 proof acceptance.
Стоимость coordinator ledger: A2 **$0.1215**, terminal reserve **$0.0000** (initial$0.648); A+A2 **$0.2025** из cap$0.80, остаток$0.5975 не разрешает новый Build.
Одна A2 попытка использована; повторов, B и source/tooling изменений нет; исходные failures сохранены.
Concrete object/offset/R, runtime-причинность и механизм KANI3300 остаются UNKNOWN; independent proof credit NONE.
Стоп: отчёт опубликован; B/новая диагностика/reader repair/Build требуют отдельного задания/GO.
