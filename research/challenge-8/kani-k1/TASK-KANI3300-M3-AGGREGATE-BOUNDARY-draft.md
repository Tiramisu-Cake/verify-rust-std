# KANI3300 M3-R2 — aggregate transfer boundary (DRAFT / NOT ISSUED)

2026-11-13. Worker 14, одна будущая стадия. Это верификация корректности, не security-работа.
Сейчас только черновик, вариант (b) предложен владельцу; это не выдача и не разрешение менять source/запускать CI.
После отдельной выдачи: base `aac27ed95364989bc045e5cdc227f2a97448f955`, read-only `/root/kani-fix-3300-m3`;
изолированные clone/branch, Cloud $0, без local cargo/rustc/Kani/CBMC/Miri/builds. CI/push — координатор.
Dirty/wrong base → STOP без reset/stash. Не возвращать удалённые research docs в export.

## Решение и предел утверждений

Вход: research `b79102aa94`, `kani3300/m3-final/STOP-R1.md`, coordinator Quick43488479150.
Tuple-return `(MU<u8>,u8)` не получает paired shadow transfer по существующим predicates. Это source-established gap;
shared transmute property и отсутствие trace не доказывают, какой dynamic conversion вызвал legal FAIL1/200.
Старый legal источник/expectation сохранить в research с SHA; не переименовывать его ложный FAIL в корректный UB.
Новая поддержка recursive aggregate transfer здесь не реализуется. Она требует отдельного design/tests для field offsets,
stride/data/padding, union overlap/enum variants, Move/source lifetime, return normal edge и сохранения source-following false.

## Узкий fail-closed guard

Сохранить существующий `transfers_shadow` и `maybe_uninit_storage`: не заменять их рекурсивным bool,
который направит неподдержанные aggregates в нынешний протокол. Добавить отдельную классификацию:
supported existing carrier / ordinary value без inline shadow slots / unsupported nested shadow carrier.

Nested check идёт по фактическому instantiated by-value layout: tuple/struct/array/enum fields, inline closure captures;
останавливается на refs/raw pointers, не обходит generic arguments вместо реальных fields (`Box<T>` не inline T).
Existing supported top-level carrier прекращает обход; flat MU arrays/slices не становятся aggregate rejection.
Enum inactive variants и zero-sized fields/arrays классифицировать явно и консервативно; не обещать field-sensitive support.
Сохранить existing unsized-size guard. Никакого arbitrary layout unwrap/panic, unsupported nested path должен быть явным.

Guard должен закрывать обе стороны вызова и все направления, а не только failing tuple return:
- entry argument locals и return local0 в visitor `find_all`, до добавления signature LoadArgument;
- actual call operands и destination type в call terminator, до LoadArgument/Begin/Store/source deinit;
- Return path: ни один неподдержанный return не должен пройти мимо entry/call validation.
Проверить actual selected signatures/generated calls/known no-body paths; не полагаться только на нынешний filtered union_args.
Existing deliberate no-transfer exceptions, прежде всего `Forget`, разобрать отдельно и сохранить только обоснованные;
не отвергать их автоматически вместе с обычной передачей и не добавлять новые blanket intrinsic exemptions.
Diagnostic: uninit-checks, argument/return, конкретный aggregate type и причина отсутствия nested-slot transfer.
Он не должен превращаться в payload UB, partial transfer, source-panic fallback или skip checks.

## Fixtures и контроли

1. Поддержанный `handoff` возвращает top-level MU; observed u8 передаёт через обычный scalar out-parameter
   либо сохраняет самостоятельный проверяемый scalar assertion. Сохранить custom-MIR Move(source), saved pointer,
   actual relay return, repair write23 до чтения и проверку returned42; обе исходные смысловые проверки остаются.
   Legal SUCCESS; no-reinit companion — intended moved-from uninit-read, не ранний aggregate Unsupported.
2. Отдельный boundary fixture с исходным legal tuple-return — exact Unsupported aggregate-return;
   tuple/struct аргумент и struct-return companions также exact boundary. Это не proof корректности старого legal root.
3. Nested array-of-struct/tuple и by-value closure capture с MU: classification controls; plain aggregates/scalars,
   references/raw pointers на aggregates и flat MU array/slice/top-level MU остаются прежними supported/known outcomes.
   Не требовать нового support для nested MU-of-flat, Box/realloc, B3 union/ZST или enum layouts.
4. Сохранить existing two-operand/mixed/masks, moved-source/normal-return/false, lawful-modifies/frame/clause,
   восемь strong oracles и CC1–CC4 ordinary/SimpleCheck/cycle controls. Broad new rejection legal contracts → STOP/review,
   не переписывать ожидания массово. Известная upstream неполнота не основание для silent acceptance.

## Владение, handoff, приёмка

Write scope: check_uninit visitor/type classifier и существующая пользовательская scope documentation;
`tests/expected/uninit/part1-composition/move-return-reinit.*` + новые isolated boundary controls.
Worker15 владеет JSON capture/binding; его `uninit-part1-composition/**` не менять здесь.
Runtime/DFCC/points-to/body selection/JSON schema неизменны; выход за bounded guard → STOP с предложением.
Явная ручная проверка Rust типов operands/casts, traversal termination и normal-edge/source-lifetime ordering;
`git diff --check`, bounded source review. Никакого локального compiler/verifier run.
Research `kani3300/m3-aggregate-boundary/`: INPUTS, CLASSIFICATION-MAP, CONTROL-MAP, REVIEW, CI-REQUEST, RESULT.
CI request: targeted supported/boundary pairs и прежние strong controls, затем Quick после JSON binding;
все новые результаты NOT_RUN, heavy cases object-bits12. Новые guard outcomes не legal proof credit.
Source neutral commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push/CI/release-ready claims.
После отдельной выдачи завершить `READY <source sha>`; сейчас **DRAFT / NOT ISSUED**.
