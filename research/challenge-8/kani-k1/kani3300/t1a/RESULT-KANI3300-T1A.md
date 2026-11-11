# RESULT-KANI3300-T1A — воспроизведено, SAME_LIBRARY_CONTRAST
A: build `fd4c3316-efbc-4f33-8506-e22b9f2ff3b3`, head `5d0679cf657683bb9beb754043dda00e48baa24c`; Cloud FAILURE, summary COMPLETE, gate=false, Kani exit1.
B (CMP4-B): build `d137507f-c7de-432a-85dc-62fa03d1adaf`, head `c8967c5a44e8f95b19f31761e55313d8488faea5`; Cloud SUCCESS, COMPLETE, gate=true, Kani exit1.
Library A=B `919cc3e2dc5fb19ea6e7f7be761914b949160a41`; pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; unchanged toolchain recipe nightly-2026-10-23.
CMP2 patch SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`, reported applied tree A=B `d356238999ab436ddc1dd7ffa845b0db214aa53e`; KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` check PASS.
Request SHA256 A `0a5300eb89b52b0e26714b7ce5b749cc66239ef2630dd3e0de5eb2e7fce0156c`, B `e23db232f257a8977e1d90b15260de6295da02898e612c60333fbe19c97abd51`; A argv snapshot = CMP3.
Сверка B пройдена: library/patch/applied tree/pin/toolchain/KT2/recipe; uninit/controls on, inventory off, standard4/jobs1/3m. B используется как source-reported baseline; нового B нет.
Префикс roots: `slice::sort::shared::smallsort::verify::uninit_probe::`; B runtime IndexRange (не выбран в A) SUCCESS 0/26, covers1/1.

|Шаг / root|A status|failed/total|covers|unreachable|Failed Checks|B shared root: status; checks; covers|
|---|---|---|---|---|---|---|
|1 cmp3_index_range_len|FAILED|2/28|1/1|0|F ×2|SUCCESS; 0/20; 1/1|
|2 cmp3_polymorphic_sized_len|FAILED|2/142|2/2|6|F ×2|не выбран в B|
|3 cmp3_polymorphic_unsized_len|FAILED|2/142|2/2|6|F ×2|не выбран в B|
|4 cmp3_manually_drop_unsized_len|SUCCESS|0/92|2/2|0|—|SUCCESS; 0/84; 2/2|
|5 cmp3_into_iter_len|SUCCESS|0/149|1/1|11|—|не выбран в B|
|6 cmp3_into_iter_next|SUCCESS|0/254|3/3|12|—|не выбран в B|
|7 U8 small_sort_general_with_scratch_u8_n4|SUCCESS|0/550|1/1|19|—|не выбран в B|
|8 U1 pincheck_calibration_uninit_read_u8|FAILED expected|1/30|3/3|0|U ×1|FAILED expected; 1/30; 3/3; U ×1|
|9 U2 pincheck_calibration_init_read_u8|SUCCESS|0/31|3/3|0|—|не выбран в B|

F: Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57
U: Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/mem/mod.rs:1283
Класс: шаги1–3 воспроизводят исходный CMP3 отказ; same-library contrast установлен для общего шага1 A FAILED / B SUCCESS. U1/U2 калибровка соответствует ожиданиям; механизм и детерминированная зависимость только от root set не установлены.
Семь описаний исчерпывают aggregate failures; summary omissions=0, страница9/9 next_offset=done. Native property IDs/columns/completeness UNKNOWN; covers после намеренного UB U1 не дают credit; len-vs-Drop instance шагов2/3 UNKNOWN.
Brief exit1 HTTP404; native exit2 `page-summary: no structured native report`. Actual argv/MIR/codegen order UNKNOWN; порядок selectors не устанавливает codegen order. Source-reported bounded diagnostic; independent B1/B2 credit NONE.
Расход A $0.1350 / cap$0.80, reserve$0, попытка1/1; no retry/repair, B не перезапускался. Исходные gates не закрыты, production fix не написан.
Предложение T1b (отдельное задание/review/GO): bounded compile-time unit/stubs/actual root order, cache hit/miss/creator/last-writer и stage/body hashes, target-origin/relevance/MemoryInitOps и малый before/after MIR step1/step4/IndexRange::len; без runtime collector или изменения slicing/trace flags.
Подробности: POST-BUILD-OBSERVATIONS.json, HARNESS-OUTCOMES.json, COMPARISON.json, EVIDENCE-INDEX.json. Одна стадия завершена; стоп.
