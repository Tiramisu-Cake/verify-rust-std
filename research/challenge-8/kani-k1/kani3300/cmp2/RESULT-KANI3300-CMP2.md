# RESULT-KANI3300-CMP2 — native17PASS/3ERROR, acceptance FAIL
Build `a13d3781-287d-4229-88d6-6b3dd1a74879`, exact head `6f50f1fbc4a95ca21444ee9ac6f101034081cd43`; Cloud FAILURE/TOOL_ERROR, gate=false; tool-build PASS (Kani236s, compiletest16s).
Full `b1f0105c0390fb55081e3d186fa286d23867b585`; build tree `e6870add67f2b1602f60ef3a623cf08139831265`; patch `17db5a0db394c5c5db8f7182fb61866df656747b17e160ead4034e03a14dbc0a`.
Request `kani3300-cmp2-20261111-01` SHA256 `27cdfcdf089af8dc025a90ec98e3e189701758ba4fe64f1d77ccd1dfc42421c5`; pin/toolchain/KT2/pool/input identities PASS.
Причина исходного blocker НЕ установлена: гипотеза о formal-parameter shadow в `delayed_ub/instrumentation_visitor.rs:42` не закрыла отказ; exact failing-instance/points-to binding UNKNOWN.
Проверенный кандидат: typed mask ordinary formal при delayed get (`:54–80`), без S/pointee blessing, P=false; cursor сохраняет entry ops. CMP2−CMP1 production1file+42/−13, total11files+193/−15; R/S/P/ghost/buffer unchanged.

|offset/группа|native result|bounded observation|
|---|---|---|
|0 IntoIter|ERROR|прежние IndexRange::len usize safety_check.1/.2 @ops/index_range.rs:52:51/:52:61;24failed-check lines,9omitted|
|1 grouped-positive|ERROR|тот же IndexRange::len;16failed-check lines,3omitted|
|6 padding-negative|ERROR|required u8 diagnostic absent в own stdout/stderr;29failed-check lines,15omitted; echoes содержат *const u8 @main.rs:78,92 и Pad/u32/C<Pad>|
|2–5,7–17:15 прочих CMP1 selectors|PASS|source-reported expected-mode results, не независимый proof|
|18:5 новых minimal positive repro|PASS|--require-success и golden5SUCCESS/0failures; baseline sensitivity NOT_RUN|
|19:3 новых parameter negatives|PASS|golden3named failures; own per-root Failed Checks не сохранены|

All35 прежних negative expectations/goldens сохранены:30отказов по PASS/golden,5padding outcomesUNKNOWN; новые3отказа по golden. Full own per-root causes всех38negative UNKNOWN; подтверждённого unexpected SUCCESS нет.
Переход от ptr::read к прямому byte dereference не исправил padding diagnostic. Ни исходный blocker, ни padding acceptance не закрыты; не ослаблять u8-golden ради PASS.
Расход по k1g budget $0.1620/reserve$0/cap$0.60; одна разрешённая попытка исчерпана, repair/retry только с новым GO.
Compiler rustfmt: координатор PASS (--edition2024 + clone rustfmt.toml); rustfmt новых тестов отложен до upstream-упаковки, только стиль, в эту сборку не вносился.
Независимое Luna HIGH review было static GO; оно не заменяет проваленный native gate. Локальных cargo/rustc/Kani/CBMC и raw evidence reads не было.
Core U8/U9 (+U1/U2,U6) NOT_RUN/не готов к replay; verification credit NONE, U3/PFC-OOM OPEN.
Подробности: POST-BUILD-OBSERVATIONS.json, HARNESS-OUTCOMES.json и EVIDENCE-INDEX.json; PRE-BUILD/STATIC-CHECKS/PACKET-CONTENTS — исторические snapshots approved head.
KANI3300 CMP2 ЗАВЕРШЁН — handoff с acceptance FAIL; следующая локализация/repair требует нового задания/GO, затем стоп.
