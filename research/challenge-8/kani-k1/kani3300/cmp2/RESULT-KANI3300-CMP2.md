# RESULT-KANI3300-CMP2 — PRE-BUILD, native NOT_RUN
Причина (статически): `delayed_ub/instrumentation_visitor.rs:42` не моделировал typed write ordinary formal parameter на входе; дальнейшие delayed reads видят fresh false shadow. Конкретная привязка failing-instance к points-to graph пока UNKNOWN.
Путь: PolymorphicIter::drop → alive.clone() → partial_drop(IndexRange) → SliceIndex::get_unchecked_mut(IndexRange) → IndexRange::len; aggregate/move/ManuallyDrop/DST вынесены в отдельные минимальные repro.
Фикс: `instrumentation_visitor.rs:54–80` — typed mask только для ordinary sized parameter с delayed get; unions/contains_storage исключены, pointee не затрагивается, P=false; entry ops сохраняются при пустом BB.
Padding: два чтения сделаны прямым `*const u8` dereference; все5 собственных failures и прежние u8/Pad/u32/C<Pad> golden-требования сохранены, incidental pointer failure не считается достаточным.
CMP2−CMP1: production1file +42/−13; total11files +193/−15. R/S/P descriptor, transfer, argument buffer, ghost state, SKIPPED_ITEMS, pin/toolchain/KT2 byte-equal CMP1.
Full `b1f0105c0390fb55081e3d186fa286d23867b585`, tree `45511935c1ce911ea6c85eee5f6850095cbf966e`.
Build subset tree `e6870add67f2b1602f60ef3a623cf08139831265`, patch SHA256 `17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`.
Request `kani3300-cmp2-20261111-01`, SHA256 `27cdfcdf089af8dc025a90ec98e3e189701758ba4fe64f1d77ccd1dfc42421c5`; 20selectors/77roots; all18 CMP1 selectors retained.
|Группа|Ожидание|Сейчас|
|---|---|---|
|CMP1 offset0,1 + remaining positives|SUCCESS|NOT_RUN|
|CMP1 all35 negatives incl offset6 + empty/overwrite/call/projection/layout|own intended failure per harness|NOT_RUN|
|5 new minimal positives (≤20lines each)|SUCCESS|NOT_RUN|
|3 new caller/callee poison/pointee negatives|own Pad/u32 failures|NOT_RUN|
Статические checks: exact-pin apply/tree, full/subset production+fixture equality, all18 old goldens and35 negative expectations, KT2 equality, validate20 — PASS. Rustfmt unavailable in current runtime; compile/native not run.
Независимое Luna HIGH review: static GO for coordinator PRE-BUILD consideration; `c678c133a6d2d65cf60c88a8d0f8f85a3cbd2a8af0188ef462618eb421dcfac4`. No direct empty-entry/nested-pointer fixture; runtime confirmation OPEN.
Расход CMP2 $0; reserve $0; proposed40min×$0.0135=$0.540, cap$0.60. Ни dispatch, ни новая phase/ledger не зарегистрированы.
Core U8/U9 (+U1/U2,U6): NOT_RUN; готовность только после native acceptance и отдельного replay GO/budget. B1/B2 credit NONE; U3/PFC-OOM OPEN.
Следующий шаг: GO координатора на exact published research SHA, одна native попытка, затем bounded evidence; repair только с новым GO. До GO стоп.
