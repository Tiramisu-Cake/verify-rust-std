# C2-S6 — повторная сессия: явный отказ shadow protocol для marker-dispatched hooks

2026-11-15. Worker14, продолжение одной стадии S6. Это верификация корректности, не security-работа.
Координатор предложил bounded production fix; выбран этот путь, а не golden с internal placeholder.
Подготовлено для выдачи координатором; этим файлом выполнение не начинается. Локальные cargo/rustc/Kani/CBMC/Miri/builds
запрещены, preparation Cloud $0. Source push/targeted fork CI — координатор. Gate A3-platform остаётся вне S6.

## 1. Тот же clone; разрешённое dirty состояние сохранить

Работать в **`/root/kani-fix-3300-c2-s6`**, existing `fix/kani-3300-c2-s6`, HEAD
`8d67298c48eb7b2381f806a6353433d1440e3d94`, tree `5fb7dbaa6f79a75ca552be9d4d5c7b535cf38058`.
Это явное исключение к initial dirty-STOP из TASK-KANI3300-C2-S6.md: ожидаются незакоммиченные изменения только в
`docs/src/reference/experimental/contracts.md`, `docs/src/rust-feature-support.md`,
`docs/src/rust-feature-support/intrinsics.md`, `tests/expected/uninit/part1-edges/README.md`.
Перед работой записать status, full diff/patch и hashes этих4 файлов в research INPUTS; сохранить их содержимое/смысл.
Не re-clone/reset/stash/clean/checkout поверх правок. Другой HEAD/неожиданные чужие изменения → STOP без перезаписи.
Остальные положения исходного S6 действуют; supersede только missing-hook prerequisite и разрешённая ниже production delta.

Research input `9c2206bf1f`: `kani3300/c2-s6/REPRO.md`,
`coordinator-observe-43645985416/OBSERVATION.md` и соответствующие исправленные repro/flags.
Void run43645617823 с неверным размещением --keep-temps не использовать как semantic evidence.

## 2. Что наблюдено и что теперь считается контролем

Run43645985416 на exact8d: fn-item-plain SUCCESS0/20; fn-item-shadow-return — ровно1 явный pairing Unsupported
в invoke перед actual FnDef-shim call_once, без early tuple/layout. Это два разных source/instance пути.
Generated `modifies(out)` legal SUCCESS, но hook return — reference, не shadow carrier.
Generated `modifies(*out)` даёт E0277 Pointer bound: compile failure, не protocol-refusal control.
**Прямой** настоящий `kani::internal::untracked_deref::<MU<u16>>` — FAILED1/121 в load_argument с placeholder.
Он Item с `todo!()` body, has_transfer_protocol=true; codegen перехватывает call через UntrackedDerefHook,
MIR callee/return StoreArgument не исполняются, а caller-side LoadArgument ожидает невозможный return0.
Это установленное fail-closed поведение с неправильной классификацией/диагностикой, **не наблюдённый false SUCCESS**.
Прямой internal call принимается вместо недостижимого в legal generated-modifies shadow-return контроля.
Не заявлять, что generated modifies или весь PFC теперь переносит shadow через этот hook.

## 3. Узкая production правка

В shared caller/callee predicate `has_transfer_protocol` сохранить существующее Item/nonforeign/body условие,
но исключить exact marker category, для которой codegen **безусловно заменяет MIR call**.
На этой базе `GotocHooks::hook_applies` сначала использует fn_marker→`try_get_kani_function`→`KaniFunction::Hook`;
этот путь немедленно возвращает registry handler из `fn_hooks()`, не вызывает conditional handler hook_applies.
Использовать существующий MIR-layer `KaniFunction::try_from(instance)` и точный `Hook(_)` match либо маленький общий
helper в kani_middle; не импортировать backend GotocHooks/Rc в MIR pass и не дублировать строковый suffix classifier.

Точная текущая registry category (проверить равенство enum↔fn_hooks в REVIEW):
AnyRawHook, AssertHook, SliceValidityAssumeHook, AssumeHook, CheckHook, CoverHook, ExistsHook, ForallHook,
FloatToIntInRangeHook, InitContractsHook, IsAllocatedHook, PanicHook, PointerObjectHook, PointerOffsetHook,
SafetyCheckHook, SafetyCheckNoAssumeHook, UnsupportedCheckHook, UntrackedDerefHook.
Список в research объясняет границу; implementation по canonical typed category, не второй hardcoded allowlist.

**Не** исключать все fn_marker, все функции с телом todo, все KaniFunction, все KaniModel/KaniIntrinsic.
MIR-body models, contract registration/other markers и обычные bodyful Items остаются прежними eligible paths.
`other_hooks` — отдельная dispatch ветвь: lang/name Panic/RustAlloc/MemCmp, PanicStub и kani_register_loop_contract
имеют другие условия/семантику (loop hook может использовать MIR expression). Не расширять fix на них автоматически;
в HOOK-MAP явно отличить их от18 typed hooks и не заявлять полную классификацию любого backend interception.

Один predicate применяется согласованно в caller classification, callee-entry loads и return stores.
Для shadow-carrying typed hook существующий explicit Unsupported guard должен сработать **до**
Begin/Store/LoadArgument/source deinit, сохраняя operand/pointer checks и B1 flush.
Ожидаемая причина: `Kani does not support shadow transfers without a paired argument/return protocol.`
Для hook без shadow values predicate=false не означает отказ обычного вызова: codegen hook работает как раньше.
Runtime buffer/placeholder formatting/DFCC/hook implementation/alias policy/F5/F6/F7 не менять.
Не реализовывать новое shadow-copy для UntrackedDeref и не подгонять load_argument asserts под перехваченный call.

Write scope: visitor predicate/import и при необходимости маленький shared classifier в kani_middle/kani_functions.rs,
новые bounded expected/classifier tests + сохранённые S6 docs/hygiene. Другой production defect → STOP с отдельным repro.

## 4. Контроли и ожидаемые исходы

| Control | Candidate oracle / отличимость |
|---|---|
| ordinary-hook-return | Исправленный repro из observation, тот же actual UntrackedDerefHook/MU return: ровно1 **явный Unsupported pairing**, FAILED. Не placeholder/assert load_argument, не payload UB, не иной early guard. |
| same-hook scalar companion | Тот же actual hook с initialized non-shadow scalar/reference-shaped return: SUCCESS, useful value/post-call assertion достигнуто; no failed Unsupported/frame/init checks. Не заменить обычной identity function. |
| ordinary marked MIR-body transfer | Проверить, что unrelated marker/model не отключает допустимый actual argument/return protocol; true/false controls сохраняются. Mock hook marker не доказывает actual hook path. |
| fn-item-plain | Exact observed FnDef через generic FnOnce, no shadow: SUCCESS; не fn-pointer coercion/оптимизированный другой путь. |
| fn-item-shadow-return | Exact observed call_once shim: ровно1 existing explicit pairing Unsupported до вызова, без tuple/layout; не blanket отказ всех FnDef. |
| generated modifies(out) | Legal control остаётся SUCCESS; documented hook return — reference, **не** shadow carrier. E0277 modifies(*out) оставить setup/research observation, не semantic negative. |

Перенести необходимые repro в смысловую expected layout; добавить `-Z unstable-options` перед --cbmc-args, Kani flags до
backend args. Сохранить S5 portable matcher: exact failure N, named Failed Checks и function/status/description,
useful own SUCCESS, verdict, ровно selected root; не std/host/nightly/full-inventory pins.
Unit/source classifier audit обязан отличать Hook от Model/Intrinsic/неизвестного marker; не создавать unsafe synthetic Instance.
Existing paired MU argument/return/Copy/Move/known-false witnesses и markers с реальным MIR не должны стать Unsupported.

Differentiating baseline уже наблюдён на8d:1 internal load_argument placeholder. Candidate обязан заменить его на1 явный
pairing Unsupported, а не просто сохранить FAILED. Если source/flags существенно меняются, повторить bounded matched observation
с теми же новыми fixtures; не требовать baseline false SUCCESS, которого здесь не было.
На candidate через bounded MIR/operation review подтвердить отсутствие hooked-call return LoadArgument/snapshots,
а у ordinary paired companion — сохранение protocol. Any new admitted-path regression не bless-ить как новую границу.

## 5. Продолжение S6 и приёмка

Обновить CONTROL-MAP/REPRO disposition: generated-modifies формы — non-carrier/invalid target; actual ordinary hook —
настоящий квалифицированный rejection control. Первоначальный STOP снят только в этой части новыми evidence/исправлением.
Закончить остальные ранее заданные S6 controls (same Copy source×2/hole, padded stride partial extent borrowed/raw,
reuse S2/S3/S4), docs/hygiene и accepted scope A; не пропускать их из-за успешного hook-only targeted test.
Сохранить S5 required local PFC companions в Replace и --harness caller --exact. F11 по-прежнему отдельно optional;
SEL1 source/SmallSort positives не импортировать в C2.

CI-request: fmt/build/clippy; новые targeted controls/classifier tests; ordinary/PFC/quantifier/arbitrary/Uninit
regressions, S2 unit9/S3 resets/S4 unit6+2, remaining upstream JSON и existing bounded Linux Quick.
Фактические reruns с --force-rerun, per-fixture12 bits/normal checks/pins неизменны. Для source hook-predicate fix
особенно проверить ordinary models/generation/contract helpers: не должен возникнуть blanket marker refusal.
**Без Gate A на3 платформах, без полного kani-regression.sh/нового gate workflow в этой стадии.**
Source/predicate delta требует новой targeted qualification; старый S5 CI её не покрывает.

Research `kani3300/c2-s6/hook-fix/`: INPUTS/PRESERVED-DOCS, HOOK-MAP, CONTROL-MAP, REVIEW, CI-REQUEST, RESULT;
основной S6 freeze package дополнить новым source lineage/targeted run после приёмки, original observations не переписывать.
Нейтральный local source commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push.
Freeze по original S6 только после полного S6 control/docs review и targeted qualification этой головы;
при pending CI — FREEZE_PREPARED/QUALIFICATION_PENDING. Gate A3-platform NOT_RUN, отдельный следующий шаг координатора.
Финал после выдачи: `READY <local S6 source sha>`. Не объявлять выпуск/публикацию разрешёнными.
