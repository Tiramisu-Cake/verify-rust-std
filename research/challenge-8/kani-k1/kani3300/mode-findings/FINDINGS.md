# MODE-FINDINGS — worker14, 2026-11-13, STATIC / SAVED-ARTIFACTS ONLY

Обозначения: C = `/root/kani-fix-3300-compose1` @ `fef9e0f38c0c645027f20223a562c7008969d9a9`; U = точный `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` через `git show`.
Upstream checkout `/root/kani-upstream-3300` фактически `8a316e627`, 24 экспериментальных коммита поверх U; его HEAD за upstream baseline не принимался и не изменялся.
E = `/root/kani3300-h1-ci/compose-c2-art/tmp.N9PEtF38v1/mode-boundary-results`; исходники ниже относительно C, если не указано U или E.
E exports сообщают clean Kani `197aaa8b367e7cdd804b118a4f050378c7e57e55`; diff с C только `.github/workflows/`, production/fixtures совпадают.
Python сверил JSON и разобрал сохранённые GBF v6 до EOF (symbols + functions), без запуска инструментария; координаты GOTO ниже — индексы инструкций с 0, не runtime trace.
SHA256 GOTO `.out` (не `.symtab.out`), Ordinary / SimpleCheck / Replace: `200414e69ebe57fe1e69889a83c4fd1daa5d4ef55fe8197224e3db77cc8232cb` / `5eacaf8742ca559b7a495030d7834eb6b3f1afe308182b4ffce72ccd4c2849d1` / `d60803cd20e987f096f90db18cb78cbda06810beac787385d499346c9d02fc7a`.

1. **PART1-INDUCED / UNKNOWN (точный crash stack).** `recursive_check` действительно падает в kani-compiler: stack overflow → SIGABRT; E/recursive_check/run.log:12-14, export отсутствует.
   Источник вероятного бесконечного обхода: `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs:439,451,519` (`apply_regular_call_effect` → override body → новый `PointsToAnalysis::run`), без active-instance/SCC guard или межпроцедурного fixed point.
   S3 `58497d98d0` подключает registration trampoline: `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs:95-133`; contract pass заменяет register на `run_contract_fn`: `kani-compiler/src/kani_middle/transform/contracts.rs:343-347`.
   Цикл по коду: recursive_transfer → register → RecursiveCheck closure → check/body closure → recursive_transfer (`tests/json-handler/uninit-contract-mode-boundaries/recursive.rs:24-31`; `library/kani_macros/src/sysroot/contracts/bootstrap.rs:148-160`).
   Points-to обходит обе ветви REENTRY/depth, не исполняя их условия; конечность runtime depth<=1 и `#[kani::recursion]` не ограничивает этот статический обход.
   В U уже есть негардированный рекурсивный анализ (`points_to_analysis.rs:455-459,518-520`), но register анализируется как исходный panic (`bootstrap.rs:69-70`), поэтому именно этот contract cycle там не открывается; S3 его экспонирует.
   Это сильная source diagnosis, не наблюдённый backtrace; иные места compiler crash без нового запуска не исключены. Минимальное прекращение краха — обнаружение цикла с явным Unsupported, не молчаливый cutoff/пустой summary; для поддержки нужен SCC fixed point.

2. **PART1-INDUCED (ложные bool/&bool failures; blocker).** ORDINARY — Assert closure#3, SimpleCheck — closure#2; вложенные ensures — соответственно closure#1 и closure#0, не recursion flag / modifies.
   `bool` — валидный by-value параметр `initialized`; `&bool` — хранимое поле 0 захвата `initialized` в ensures `|result| !initialized || ...` (`tests/json-handler/uninit-contract-mode-boundaries/replace.rs:21-24`).
   Источник checks: DelayedUbPass → `InstrumentationVisitor::visit_place` → `MemoryInitOp::CheckRef` (`kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs:122-130,196-198`), затем `build_get_and_check` (`check_uninit/mod.rs:289-295,431-445` в том же transform/).
   S3 делает generated bodies видимыми анализу; field-insensitive union захватов распространяет targets на bool/ref (`kani-compiler/src/kani_middle/points_to/points_to_analysis.rs:478-501,614-620`; `points_to_graph.rs:100-106`).
   E/replace_ordinary GOTO: passthrough[94-103] берёт &initialized, строит environment, передаёт через force_fn_once/register; Assert[41-50] проверяет *env.0; ensures[17-24] проверяет сам &bool slot, [26-33] — его bool referent.
   В passthrough нет shadow-setter вообще, в Assert есть только setters ZST ContractClauseGuard, в ensures setters нет; incoming bool и by-value копия поля closure не получают initialized shadow. Argument protocol обслуживает только union/MU (`kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:64-84,119-120`).
   False приходит из reset (`library/kani_core/src/mem_init.rs:240-244`), а не из значения initialized=false: оба значения bool и shared reference полностью инициализированы в Rust. Динамического witness/последнего state write в этих exports нет.
   Тот же pattern подтверждён Python для SimpleCheck и Replace. В U есть visitor/coverage-дефект, но нет S3 alias bridge за register: эти конкретные generated-closure checks по данному пути не возникают; A1–A3R/B1I/M1/CLOSURE-ZST не вводят bool predicate.
   Минимальный кандидат (НЕ реализован): при входе/копировании корректно отмечать data bytes обычных scalar/reference parameters и upvar slots, включая копии через trampoline; MU/union payload переносить существующим mask protocol. Не ставить true всему environment/referent и не удалять CheckRef; нужны negative payload controls.

3. **UPSTREAM (layout limitation), PART1-INDUCED (её достижимость здесь).** Unsupported в apply_closure присутствует во всех трёх Replace roots; это не доказательство ошибки пользовательского payload.
   Ensures environment ненулевое: сохранённый symbol type имеет ровно поле 0 `pointer<c_bool>`, width64 (8 bytes), захват &initialized; result — аргумент, не capture. Outer Assert environment содержит &initialized и &value.
   Путь по коду — delayed visitor mutating-place `SetRef` при implicit drop `f` после `f(x)` (`delayed_ub/instrumentation_visitor.rs:189-195`; `library/kani_core/src/lib.rs:693-695`) → `PointeeInfo::from_ty` → Unsupported (`kani-compiler/src/kani_middle/transform/check_uninit/mod.rs:274-283`).
   E/replace_ordinary apply_closure GOTO[9] вызывает ensures, [15-16] содержит Unsupported/assert-false и assume-false после вызова; это отдельный failure от bool checks.
   U `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs:393-400` отвергает любой Closure; C:474-484 разрешает только sized size0 (`0ad35c0a93`). Nonzero layout не был реализован CLOSURE-ZST, S3 лишь приводит сюда анализ.
   Совпадает с границей upvar offsets/masks, но здесь нет captured `out`: захвачен initialized. Handoff `../closure-zst/RESULT-CLOSURE-ZST-PREP.md:19-20,25` сохраняет legal captured PFC/out как release blocker; этот набор эту границу не обходит.

4. **TEST-DESIGN / UNKNOWN (конкретный witness).** Координаторский перечень Replace неполон: E/replace_transfer/observation.json содержит ещё `std::ptr::read::<u8>.safety_check.1` (*const u8) и `.4` (u8), всего 5 failures, не 1.
   GOTO ptr::read[14,27] в обоих случаях вызывает `is_ptr_initialized::<1,u8>`: `.1` — local raw-deref Check (`ptr_uninit/uninit_visitor.rs:796-801`), `.4` — delayed CheckRef фактического byte read; описание *const u8 использует operand type (`check_uninit/mod.rs:431-445`), не означает чтение неинициализированного адреса.
   Replace havocs result перед ensures assumption (`library/kani_macros/src/sysroot/contracts/replace.rs:29-30,114-126`); MaybeUninit::any допускает uninit (`library/kani_core/src/arbitrary.rs:165-170`, также U).
   При initialized=true predicate читает havoc result до assume и может попасть на hole: исходный identity contract законен, но unsafe predicate не тотален на Replace havoc domain. Это ожидаемая дополнительная граница набора; без trace нельзя приписать оба failures конкретному invocation/mask transition или объявить их ложными.

5. **TEST-DESIGN.** `roots.json:20-37,50-67` и README:3-12 разумно требуют PASS как цель для законных ordinary/SimpleCheck executions: input=true даёт new(42), false не читает payload (`replace.rs:17-18,49-76`; recursive.rs:63-89).
   Как уже поддержанные mode-isolation controls они непригодны: nonzero captures смешивают режим с известным layout blocker; bool shadow regression остаётся настоящим blocker, а не поводом ослабить PASS/control.
   Сохранить исходные failures; подготовить отдельный capture-free legal companion и отдельный nonzero-upvar regression, не засчитывать Unsupported за нужный отрицательный результат.
   E/observations.json: Replace=FAILURE(5), Ordinary/SimpleCheck=FAILURE(3/3), covers везде unreachable; RecursiveCheck=COLLECTION_ERROR, остальные два recursive roots=NOT_RUN. `run.py:69-76` накапливает companion errors и останавливает downstream только после collection error.
   Ни mode qualification, ни Part1 acceptance не установлены; точный crash backtrace/новые исправления и их validation остаются NOT_RUN. Cargo/rustc/Kani/CBMC/CI/download/push не выполнялись; только разрешённый git pull --ff-only, чтение и локальный Python.
