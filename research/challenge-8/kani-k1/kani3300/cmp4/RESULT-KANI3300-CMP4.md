# RESULT-KANI3300-CMP4 — COMPLETE, диагностика
Clean build `a7061950-0ce5-4776-8d65-fdd686526dd1`, head `9730eb7286d50bfd956b1180b1211927595283aa`: Cloud FAILURE, summary COMPLETE, gate FAIL.
CMP2 build `d137507f-c7de-432a-85dc-62fa03d1adaf`, head `c8967c5a44e8f95b19f31761e55313d8488faea5`: Cloud SUCCESS, summary COMPLETE, gate PASS; Kani exit1 в обоих.
Одинаковые library/roots/flags: f046b70644e113be0df9c22c2e6ea44a65a57566, nightly-2026-10-23, uninit/controls on, inventory off, standard4/jobs1/3m; KT2 check-tooling PASS.
Clean без kani_patch; CMP2 patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, reported applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`.

| Root suffix uninit_probe:: | Clean: status; failed/total; covers; Failed Checks | CMP2: status; failed/total; covers; Failed Checks |
|---|---|---|
| cmp3_index_range_len | SUCCESS; 0/20; 1/1; — | SUCCESS; 0/20; 1/1; — |
| cmp4_index_range_len_runtime | SUCCESS; 0/26; 1/1; — | SUCCESS; 0/26; 1/1; — |
| cmp3_manually_drop_unsized_len | FAILED; 1/27; 0/2; A | SUCCESS; 0/84; 2/2; — |
| pincheck_calibration_uninit_read_u8 | FAILED; 1/31; 3/3; B | FAILED expected; 1/30; 3/3; C |

A: Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<usize>; 2] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<usize> as a field. @ /workspace/src/library/core/src/array/iter/iter_inner.rs:48
B: Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/mem/mod.rs:1283
C: Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/mem/mod.rs:1283
Три описания покрывают все aggregate failed checks; bounded summary omissions=0, native completeness/property IDs/columns UNKNOWN. Clean unreachable: ManuallyDrop1, U1 3; CMP2 0.
Классификация по п.5 планера: НЕРАЗРЕШЕНО — исходный CMP3 отказ IndexRange не воспроизведён; обе direct-проверки SUCCESS на clean и CMP2. Ни pre-existing отказ, ни регрессия этим пакетом не установлены.
Const vs runtime: literal2 и any_where n<=4 проходят одинаково; const fn допускает const evaluation, но фактический Rvalue::Use(Constant), отличие MIR и причина UNKNOWN.
Clean ManuallyDrop — unsupported, U1 — incompatible layouts, а не expected uninit; CMP2 U1 чувствителен к uninit. Covers после намеренного UB не дают credit; gate PASS не закрывает KANI3300.
KT2/native: exit2 no structured native report; Brief: exit1 HTTP404 в обеих сборках. Actual argv/causal transfer binding UNKNOWN; raw fallback не использован.
Следующий шаг: отдельно разрешённая bounded немутирующая трассировка original CMP3 nine-root vs CMP4 four-root (MIR/place/instance, relevance/points-to, object+offset, R и Set/Copy/Get); узкий constant-assign fix только после подтверждения пропущенной записи, не сейчас.
Расход clean$0.1215 + CMP2$0.1080 = $0.2295 / cap$1.20; reserve$0; обе попытки использованы, повторов/исправлений нет. Source-reported bounded diagnostics; independent B1/B2 credit NONE.
Подробности: CLEAN-/CMP2-OBSERVATIONS.json, CLEAN-/CMP2-EVIDENCE-INDEX.json, COMPARISON.json. KANI3300 CMP4 ЗАВЕРШЁН; одна стадия, стоп.
