# KANI3300 T1b-C2 — RESULT
Build0835db8a-7425-4bc9-ad0e-ae83611b3e3d: Cloud FAILURE; Kani build SUCCESS247s; verify COMPLETE, exit1/gate=false; setup/compile/timeout отказа нет.
Head7b097ac2552fc9d2e5a4df43a6e5be3f7f6c0fdb; request SHA256bb97062288c84b38ae25961ada87aaad28858e23023e69fb4677fa22830fdcaa — MATCH.
Pin f046b70644e113be0df9c22c2e6ea44a65a57566; diagnostic12b4137c42 unchanged; production CMP2/library919cc3e2, patch/tooling/expected argv+env identities MATCH.
Applied deployment tree4b08f55cae739d02d495c05eb23249a62a5a9e50; patch SHA256f38fe31c3c95724098d79f569faeba0b0602464cb0cb06c8983bbfebcf88c930;15paths/no historical tests.

| Root suffix uninit_probe:: | C2 | A3 | Failed/total; covers C2=A3 |
|---|---|---|---|
| cmp3_into_iter_next | SUCCESS | SUCCESS | 0/254; 3/3 |
| cmp3_index_range_len | FAILED | FAILED | 2/28; 1/1 |
| cmp3_manually_drop_unsized_len | SUCCESS | SUCCESS | 0/92; 2/2 |

Все3 verdict/check/cover counts совпали с A3; failing root сохраняет2 uninit usize checks в library/core/src/ops/index_range.rs:57.
Trace PARTIAL, complete=false, seen187/emitted187/omitted0, errors=[]; отсутствует потеря payload records, но полнота witnesses не установлена.
Причина PARTIAL: external_cache_witness_cap1829 и external_witness_cap39; это иные единицы, чем omitted records0, не суммируются с ним.
Sidecar110763B (<256000B), SHA25665eae919bf4318e74b4e3b71f34030e3581518135feeb7e933af6cbf0017eab8; archive/inventory integrity не установлена.
Все seq ниже — invocation8610:0/unit0, stub_count0; actual codegen order: cmp3_into_iter_next → cmp3_manually_drop_unsized_len → cmp3_index_range_len.
Warmup actual IndexRange::len: miss22/hash8e83681b4d5b4436(23), zero_ops8(24); subsequent warmup index/manual hits30/36.
Writer72: DelayedUbPass в root cmp3_into_iter_next меняет actual len на hash9bae019701b64b9b/dump1685B; CheckRef для ((*_1).1/.0:usize) выбраны68/70; его GOTO consumer76 имеет этот hash/last_writer.
cmp3_index_range_len: presence181 present; goto_body_consumed187 IndexRange::len hash9bae019701b64b9b; last_writer=DelayedUbPass, root=cmp3_into_iter_next, stage=codegen/unit0, writer hash9bae019701b64b9b.
cmp3_manually_drop_unsized_len: presence126 present; goto_body_consumed130 IndexRange::len hash9bae019701b64b9b; last_writer=DelayedUbPass, root=cmp3_into_iter_next, stage=codegen/unit0, writer hash9bae019701b64b9b.
Оба consumer относятся к тому же mangled symbol, что writer72; phase=before_goto_blocks, dump_ok=true; связь с writer cmp3_into_iter_next наблюдается до actual GOTO block emission, не только при analysis lookup.
Собственные delayed scans actual len в manual/index дают nonzero_ops0/zero_ops18(111/180), однако writer72 остаётся last_writer в обоих GOTO consumers.
Это source-reported compile-time цепочка переноса контекстно изменённого cached body к failing и passing roots; различие verdicts не объяснено одной лишь общностью hash.
Hash — std-default-hasher-64, не криптографическое/proof identity; concrete runtime object/offset/R, причинность uninit и независимый B1/B2 credit UNKNOWN/NONE.
Calibration pair исключена по решению координатора; checks/expectations сохранены, нового calibration verdict нет. Production repair и дополнительные controls не запускались.
10 bounded records-страниц прочитаны вручную по returned next_start до null; page complete=true не означает trace complete. TRACE-KEYS-C2.json / EVIDENCE-INDEX-C2.json сохраняют identities/receipts/coverage.
Brief exit1 HTTP404; использованы разрешённые bounded K1 summary/trace-field без raw logs/archives и без обхода identity guard.
Стоимость rounded pool ledger: C2$0.1080 (8min×$0.0135); terminal reserve$0, initial reserve$0.4455; A+A2+A3+C+C2=$0.4590 из cap$0.80; остаток$0.3410 не разрешает Build.
RESULT-CHECK-C2.json PASS: identities, все3 сравнения с A3, page-chain/seq1–187, writer→consumers и стоимость; Kani clean/unchanged, локальные compiler/verifier NOT_RUN.
Стоп: одна разрешённая попытка и её отчёт завершены; повторов/repair/нового Build нет. Runtime causality и общее доказательство корректности Kani не установлены; proof credit NONE.
