# KANI3300 T1b-C — RESULT
Build5fee5ac5-ad04-4edf-b73a-6c35cc448561: Cloud FAILURE; summary REQUEST_INVALID; Kani build/verify NOT_RUN, Kani exit=null/gate=false.
Head b5f8737c1248627c519d599cc2c7bf4f63d7a496; request SHA25661cc4a3fec6e16ef688e6835fab60e96a759bca57070726d1295d557b7910379 — MATCH.
Отказ prepare до компиляции: `REQUEST_INVALID: patch diffstat exceeds bounded report size`; summary прямо сообщает `request rejected before Kani ran` / `build skipped`.
Ошибка моего пакета C: combined patch включил99 исторических test-файлов, отсутствовавших в deployment-патче A3; всего114 путей против14 у A3.
Static Git metadata: diffstat C6990B >4096B, deployment A3 959B; guard tools/kani_k1.py:335–337. Preflight проверил применение/tree, но пропустил этот report bound.
Новый diagnostic commit12b4137c42 не компилировался в C; прежний fork CI success — сообщение координатора, не результат этого Cloud Build. Actual applied-tree/compiler identity UNKNOWN.

| Root suffix uninit_probe:: | C | A3 | A3 failed/total; covers |
|---|---|---|---|
| cmp3_into_iter_next | NOT_RUN | SUCCESS | 0/254; 3/3 |
| cmp3_index_range_len | NOT_RUN | FAILED | 2/28; 1/1 |
| cmp3_manually_drop_unsized_len | NOT_RUN | SUCCESS | 0/92; 2/2 |
| pincheck_calibration_uninit_read_u8 | NOT_RUN | FAILED (expected) | 1/30; 3/3 |
| pincheck_calibration_init_read_u8 | NOT_RUN | SUCCESS | 0/31; 3/3 |

NOT_RUN установлен явным отказом до Kani, не отсутствием строк: bounded rows total=0, controls/calibration verdicts и counts C не получены.
Trace не произведён; state/complete/omitted UNKNOWN, не COMPLETE/omitted0. trace-field state exit2: `outer Kani build identity missing`; guard не обходился.
cmp3_index_range_len → IndexRange::len: presence/goto_body_consumed hash/last_writer/root UNKNOWN; отношение к писателю cmp3_into_iter_next UNKNOWN.
cmp3_manually_drop_unsized_len → IndexRange::len: presence/goto_body_consumed hash/last_writer/root UNKNOWN; отношение к писателю cmp3_into_iter_next UNKNOWN.
Сам cmp3_into_iter_next в C NOT_RUN; нового writer/hash нет. A3 writer299/hash9bae019701b64b9b остаётся историческим наблюдением, не переносится на C.
Published request/pin/library/tooling bindings проверены; runtime argv/env/actual applied tree/MemoryInitOps и конкретный object/offset/R не установлены.
Стоимость k1g rounded pool ledger: C$0.0270 (2min×$0.0135; start19:43:23.317369Z → finish19:44:32.445230Z), terminal reserve$0; initial reserve$0.4725.
A+A2+A3+C=$0.3510 из cap$0.80; остаток$0.4490 не разрешает новый Build. Одна попытка, repair/retry/B не выполнялись.
Brief exit1 HTTP404; использованы разрешённые bounded K1 summary/trace-field и coordinator metadata/ledger. Archive/inventory integrity и independent B1/B2 credit не установлены.
C-OBSERVATIONS.json / EVIDENCE-INDEX-C.json / STATIC-DIFFSTAT-C.json сохраняют exact identities, receipts, UNKNOWN и статическую причину упаковки.
Стоп: одна разрешённая попытка завершена setup-отказом; причинность исходного uninit и root-specific cache reuse не закрыты; proof credit NONE.
