# KANI3300 T1b-A3 PRE-BUILD
Task fb88f46b39467382ba73870091e8758a79116fdf; Runtime Codex, одна стадия; Cloud $0, Build/dispatch/phase/reserve NOT_RUN.
Research /root/verify-rust-std-kani3300-t0, experiment/kani-k1-kani3300t0-20261111; активные inputs/ledgers и пакет B не менялись.
Kani /root/kani-fix-3300-t1, diag/kani-3300-t1, clean989f72351c2b5c5f3b5117315fc84f502e66d904; diagnostic delta не меняется/не пушится.
Pin f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; library tree919cc3e2dc5fb19ea6e7f7be761914b949160a41.
CMP2 b1f0105c0390fb55081e3d186fa286d23867b585, production patch SHA25646ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4.
Combined patch ../t1b-r/kani-combined.patch SHA2560e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298; applied tree53927d9bc0ccbff8183aa91ffb6c29d1c8a74465.
Tooling candidate 3de1e033af05252426c39d5f557b229dcc14f118; tree15c846e82de442c23fef3950c86d54aa02b92398; KT2+extension+исправленный validator+A3; file hashes TOOLING-FILES.json.
Tooling delta SHA2567918fe9705e9337d8f6dae23d74f5e8d8e99dd8135ee6774102eb502ab0e06d6; baseline/candidate/packet/spec identities BINDING.json, REVIEW-IDENTITIES.json и REVIEW-FIX-IDENTITIES.json.
Recipe SHA25673b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81; runner/verdict parser/upload behavior unchanged.
A3 request SHA2565b82ada544e8eced4e72a10e4e22c8b71eef892bde4aed34f9309d74e9a414bd; kind diagnostic/slug kani3300/stage kani3300-t1b/owner k1-merge.
Choice (b): все 9 roots A2 и expectations сохранены, включая cmp3_index_range_len, calibration pair, SUCCESS cmp3_manually_drop_unsized_len.
Меньше roots может убрать контекстный отказ/cache writer; поэтому урезается payload, а compiler context остаётся сопоставимым A2.
A2 seen4477 — агрегат отвергнутого summary, не исходные footer counts; sidecar254669B близок к producer256000B на invocation.
trace.rs::matches — literal substring: убраны широкие PolymorphicIter, kani_cmp3:: и IndexRange::zero_to.
Оставлены cmp3_index_range_len, cmp3_manually_drop_unsized_len, kani_cmp3::manually_drop_unsized_len, IndexRange::len, pincheck_calibration_.
Это шаг1/шаг4 + actual len + calibration pair; root filter сохраняет activation/function_presence, в т.ч. явное отсутствие len при inlining.
Unit/root/stub/codegen order, analysis_targets и до16 внешних origin/cache witnesses остаются по producer без новых transformations.
Producer caps прежние:512 rows (510 payload), record2048B, invocation256000B (<256KiB), run<=1MiB; полнота ключевых записей до прогона UNKNOWN.
Timeout2m→1m разрешён A3:60/31s(A2)=1.94×;60/34s(T1a)=1.76×. Timeout не считается PASS; overhead30min сохранён.
Остаток cap$0.80=$0.5975; (9×1+30)×$0.0135=$0.5265; после резерва$0.0710. Это draft расчёт, не live reserve.
Recipe standard4/jobs1, uninit+controls on/inventory off; argv kani-A3.args; validated expected runner argv/env EFFECTIVE-INVOCATION.json.
RUSTFLAGS=--cfg kani_smallsort_controls; TRACE_DIR=/workspace/src/k1-out/trace; FILTER как выше; TRACE_ID=request SHA256; TRACE_STAGE=kani3300-t1b.
INVALID сохраняет bounded UNVALIDATED footer в summary.json до validator; validation.footers/errors доступны trace-field, payload закрыт.
Diagnostic/service15/15 и legacy native15/15 PASS; static packet/diff checks PASS; independent Luna HIGH PASS после P2 fix; TESTS.json/REVIEW-TOOLING.md.
Следующий шаг только после GO: coordinator перепроверяет exact published SHA/request/identities/live slots/budget/deadline и штатный preflight.
Если trace обрезан/не воспроизведён отказ/изменены checks — стоп с UNKNOWN; автоматического B/retry нет. Proof/runtime causality credit NONE.
