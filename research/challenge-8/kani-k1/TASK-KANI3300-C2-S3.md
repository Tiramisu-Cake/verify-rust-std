# KANI3300 C2-S3 — conservative reset для nested aggregate call boundaries (R4 F6)

2026-11-14. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим документом работа не начинается. После выдачи — isolated clone
`/root/kani-fix-3300-c2-s3`, ветка `fix/kani-3300-c2-s3`. Existing destination/dirty или wrong base → STOP без reset/stash.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. Preparation Cloud $0; fork CI, push/dispatch и review — координатор.
Не писать в existing clones/PR ветки или SEL1 worker15; S4/S5/F8 этой стадией не начинать.

## 1. Вход и статус свидетельств

- Exact base **`bf8170b28afb682f8dd55a94199caa247736d8fa`**, tree `9ff24911693123853c88cca21a0baf764b63b2bf`,
  read-only `/root/kani-fix-3300-c2-s2`, fork `fix/kani-3300-c2-s2`.
- Прочитать PLAN-KANI3300-C2.md S3, аудит R4 F6/ответы4–6, existing known-FP и top-level Move-return fixtures.
- S2 принят: `kani3300/c2-s2/format-coalescing-followup/CI-RESULT.md` @`60c7f2660f`.
  Baseline69 run43606850975 воспроизвёл conflicting descriptors двумя controls, первые4 оказались NONDISCRIMINATING.
  Candidate run43606854394: fmt/build/clippy PASS, immutable_allocations unit9/0, immutable expected19/0.
  Это targeted S2 acceptance, не новый полный C2 gate.
- F6 остаётся source-established hypothesis до различающих прогонов этой стадии. Known tuple false positive не доказывает
  ни stale-true miss, ни его устранение. Не повторить ошибку S2 с недифференцирующими контролями.

## 2. Два пути F6 и точная граница исправления

Existing whole-value assignment guard отвергает UnionAsField; general nested transfer не реализуется.
Пополевая/custom-MIR сборка может обойти этот guard, после чего:
1. Nested call destination переиспользует объект с прежним initialized=true, но не получает LoadArgument/reset.
2. Actual Call(Move) nested aggregate не входит в union_args, поэтому сохранённый pointer читает stale-true source slot.

Закрыть оба пути существующим **SetRef(false) по полному sized storage extent**, без новых blanket Unsupported,
без пополевого protocol/маски сохраняемого значения и без объявления nested aggregates поддержанными.
Классификация: не existing `transfers_shadow(ty)` carrier и именно existing layout error `UnionAsField`;
не «любой layout error» и не новый рекурсивный поиск MU по всем generic arguments/refs.
Поддержанные top-level MU/union и flat MU arrays/slices остаются в прежнем paired protocol.
Для неизвестного/unsized extent сохранить корректную unsupported-size границу, не использовать размер0/unwrap как fallback.

## 3. Hooks и порядок операций

Primary source: `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`, visit_terminator Call.
Использовать existing `PointeeInfo::from_ty` classification и `MemoryInitOp::SetRef { value:false }`:
`check_uninit/mod.rs` уже выбирает для него `PointeeInfo::for_deinit`, то есть full mask включая padding/storage.

- **Destination:** reset на `InsertPosition::After` этого Call — только normal continuation edge после возврата,
  не до Call, не на unwind/abort, не глобально при StorageLive/StorageDead. Сбросить точный destination place/extent,
  не всю соседнюю allocation и не pointees его pointer fields. Не затирать после reset последующие реальные writes/reinit.
- **Move source:** просмотреть actual by-value args, включая nested типы вне нынешнего union_args;
  все необходимые StoreArgument snapshots снимаются **до любого** source reset, затем actual Move places reset Before Call.
  Это должно работать и когда нет ни одного supported union_arg. Copy args, func operand и обычные scalar/ref/pointer значения
  не получают этот nested reset. Сохранённый адрес берётся пока source storage живо.
- Caller/source/destination alias и projected place требуют проверки порядка. Прежние Begin/Store/Load, return0,
  normal-edge protocol, B1 pending checks и resolver/checked_body/cycle diagnostics сохраняются.
- Existing intrinsic/no-effect исключения (в частности Forget) и early Unsupported paths не обобщать и не менять молча.
  Составить coverage table: direct bodyful calls, intrinsic/hook/bodyless/indirect refusal и какие из них уже fail-closed;
  если остаётся необработанный F6 path — STOP с точным случаем, не сужать docs по неполному исправлению.

Write scope: visitor и только необходимый локальный type/reset helper, новые `tests/expected/uninit/nested-aggregate-reset/**`,
узкая правка `docs/src/reference/experimental/contracts.md`. Runtime, immutable F5, DFCC, body cache F7 и SEL1 неизменны.
Новый broad guard, изменение Slot/MaybeUninit typed masks или общей alias policy → STOP за пределами стадии.

## 4. Обязательные различающие контроли

Два отдельных expected-file, один harness на файл. Сначала подготовить **test-only** пакет над exact bf8170b28;
не смешивать production repair с baseline и не запускать baseline на другом ancestor/последнем HEAD.

| Negative | Какой путь должен реально сохраниться | Baseline bf8170b28 + новые tests | Candidate + те же tests |
|---|---|---|---|
| repeated-return-same-destination | Один и тот же runtime destination сначала держит initialized nested slot, затем Call пишет туда aggregate с незаписанным slot; целевой payload read после второго возврата | **Ложный VERIFICATION SUCCESSFUL**; compiletest с ожидаемым FAILURE падает и подтверждает bug | FAILURE на intended uninitialized read |
| moved-from-nested-slot | Saved pointer к nested slot до фактического MIR Operand::Move в Call; чтение именно старого source storage после вызова | **Ложный VERIFICATION SUCCESSFUL**; expected-negative selector не совпадает с oracle | FAILURE на intended moved-from payload read |

Сборка aggregate — по полям/custom-MIR как в known-FP, без целого aggregate assignment, который заранее Unsupported.
Для destination нельзя подставить новый temporary вместо повторного использования того же place; для Move нельзя читать
callee copy/return temporary вместо source. Storage source остаётся выделенным: ранний StorageDead/dangling failure не цель.
Установить в actual consumed MIR: нужный Call destination, действительный Move (не Copy), field offset/extent,
source/destination object identity и retained target read. Не позволить оптимизатору удалить read или свернуть проверку.

**Оба baseline root обязаны дать именно false SUCCESS.** Baseline FAIL из-за настоящего read/Unsupported/другого guard,
compile error, nondiscriminating lowering или UNKNOWN не закрывает F6: worker ищет другую форму в этой стадии,
передаёт координатору исправленный bounded test-only request. Candidate FAIL при baseline FAIL не является исправлением.
Если форму не удалось воспроизвести в отведённом координатором лимите — STOP/UNREPRODUCED, не выдавать docs narrowing за доказанное.

Sources/goldens/flags между baseline и candidate byte-identical. Оракул target-negative зафиксировать по операции:
полное ожидаемое число и описания payload failures, без иных Unsupported/frame/validity failures; local/delayed duplicates
одного read обозначать явно по source binding, не принимать любую комбинацию FAILED. Host/std lines/full inventory не pin-ить.
Сохранить existing top-level legal/reinit/false/Copy/MU argument-return и immutable controls; добавить узкий reinit companion,
если он нужен для проверки, что reset не уничтожает subsequent write. Known tuple legal остаётся known false positive,
не detection-of-UB credit; возможный drift его false-failure count документировать/review, не auto-bless весь expected набор.

## 5. Docs и CI-приёмка

После source coverage review и **двух различающих baseline/candidate pairs** разрешено заменить текущую фразу
«not guaranteed to fail closed ... may ... miss uninitialized reads» описанием conservative reset на этих call boundaries
и возможных false positives. Сохранить отсутствие nested transfer support, whole-value Unsupported, known tuple-return example
и совет top-level slot. Не писать blanket claim о поддержке/полной soundness всех aggregates или исправлении всего #3300.
Если покрыт только один путь, tests не различают модели или новый source path не разобран — narrowing не готово к приёмке.

До CI: INPUTS/tree/patch hashes, explicit Rust type/borrow/extent review, normal-edge/before-snapshot audit, `git diff --check`.
CI-request координатору: отдельно baseline test-only two negatives и candidate с теми же controls; затем fmt/build/clippy,
targeted expected, existing Move-return/call-pairing/normal-abort/ordinary/PFC/closure/cycle и прочие suites принятого Quick.
Per-fixture12-bit flags/normal checks сохраняются. Targeted S3 proof acceptance — reached intended reads, не просто substring FAIL.
Любой supported legal regression, lost check, новый unqualified seed/bless или extra unrelated negative failure → STOP.

Composition JSON до S5 — **известный FAIL, не блокирующий S3 приёмку сам по себе**; исходный S1 drift описан в DRIFT.md.
Не менять roots.json/checker/allowlist, не удалить suite и не назвать красный общий Quick all-PASS. Приёмка — targeted controls
и остальные обязательные suites; composition outcome/exit и S5 debt записываются отдельно. Новый payload/status/lost-check drift,
не покрытый известным объяснением, требует review; waiver не распространяется на любую новую ошибку composition.

## 6. Handoff

Research `kani3300/c2-s3/`: INPUTS, RESET/COVERAGE-MAP, CONTROL-MANIFEST, BASELINE-CANDIDATE, REVIEW, CI-REQUEST, RESULT.
Показать две фактические baseline false-success/candidate intended-failure пары, identity/extent/order binding, docs disposition
и полный список NOT_RUN/UNKNOWN. До CI не заявлять воспроизведение или устранение F6.
Source neutral local commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push. Existing base/pins/B1/S2 неизменны.
После отдельной выдачи завершить `READY <local S3 source sha>`; координатор принимает stage и отдельно выдаёт S4.
