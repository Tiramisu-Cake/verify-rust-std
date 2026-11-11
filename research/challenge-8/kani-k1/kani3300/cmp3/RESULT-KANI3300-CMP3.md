# RESULT-KANI3300-CMP3 — COMPLETE, diagnostic gate FAIL
Build `ddcd43e2-f48e-4b1f-b688-931250adf78e`; Cloud FAILURE, summary COMPLETE, gate=false, Kani exit1; setup/compilation completed.
Exact head `d1e1a985b2d49dd0d625565e38b11b42d283bbb2`; request SHA256 `2fcfec5e616561e62bdddb894ab3378974a020c03ea6fc1871f668571a90cf7a`.
Patch `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`; observed applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e`; check-tooling KT2 PASS.
Names below share `slice::sort::shared::smallsort::verify::uninit_probe::`; failures A/B quoted verbatim below; omitted counts refer to bounded summary.

|step/root|status|failed/total|covers|Failed Checks|omitted|
|---|---|---|---|---|---|
|1 cmp3_index_range_len|FAILED|2/28|1/1|A ×2|0|
|2 cmp3_polymorphic_sized_len|FAILED|2/142|2/2|A ×2|0|
|3 cmp3_polymorphic_unsized_len|FAILED|2/142|2/2|A ×2|0|
|4 cmp3_manually_drop_unsized_len|SUCCESS|0/92|2/2|—|0|
|5 cmp3_into_iter_len|SUCCESS|0/149|1/1|—|0|
|6 cmp3_into_iter_next|SUCCESS|0/254|3/3|—|0|
|7 small_sort_general_with_scratch_u8_n4 (U8)|SUCCESS|0/550|1/1|—|0|
|8 pincheck_calibration_uninit_read_u8 (U1)|FAILED expected|1/30|3/3|B ×1|0|
|9 pincheck_calibration_init_read_u8 (U2)|SUCCESS|0/31|3/3|—|0|

A: Undefined Behavior: Reading from an uninitialized pointer of type `usize` @ /workspace/src/library/core/src/ops/index_range.rs:57
B: Undefined Behavior: Reading from an uninitialized pointer of type `u8` @ /workspace/src/library/core/src/mem/mod.rs:1283
Первый отказ — шаг1, прямой zero_to(2).len(): адаптер/PolymorphicIter/unsize/IntoIter не нужны для наблюдения отказа в этом пакете.
Шаги2/3 FAIL, 4–6 и U8 SUCCESS; это зависимость наблюдения от контекста, не доказательство причины. Для 2/3 len-vs-Drop instance UNKNOWN; covers только агрегатные.
Семь описаний покрывают все семь aggregate failed checks, summary omissions=0; native omission metadata/property IDs/columns недоступны, их полнота UNKNOWN.
`k1g.sh native`: exit2 `page-summary: no structured native report`; `smallsort-brief`: exit1 HTTP404. Failed Checks доступны только через bounded summary, raw fallback не использован.
Связка transfer/delayed get UNKNOWN: нет конкретного function/MIR-place/type/base+offset, R до/после, points-to и порядка Set/Copy/Get; одинаковый span не связывает объекты.
Следующий шаг — отдельно согласованная ограниченная немутирующая трассировка этих данных для шага1 и проходящего шага4; не добавлять pre-len raw-read/AddressOf или тотальную инициализацию.
Pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain nightly-2026-10-23, standard4/jobs1/3m, controls/uninit on по summary и unchanged-tooling binding; actual argv UNKNOWN.
Расход $0.1215, reserve$0, cap$0.80; единственная попытка исчерпана. Source-reported bounded diagnostic, independent B1/B2 credit NONE; U8 PASS не снимает исходные gates/отдельный GO U4.
Подробности: HARNESS-OUTCOMES.json, POST-BUILD-OBSERVATIONS.json, EVIDENCE-INDEX.json; новых source/tool исправлений и повторов нет. KANI3300 CMP3 ЗАВЕРШЁН.
