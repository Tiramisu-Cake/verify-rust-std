# KANI3300 C2-S4 — восстановление delayed-MIR между harness'ами (R4 F7)

2026-11-14. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом работа не начинается. После выдачи — isolated clone
`/root/kani-fix-3300-c2-s4`, ветка `fix/kani-3300-c2-s4`. Existing destination/dirty или wrong base → STOP без reset/stash.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. Preparation Cloud $0; fork CI, push/dispatch и review — координатор.
Существующие source/PR ветки и SEL1 worker15 не менять; S5/F8 этой стадией не начинать.

## 1. Принятые входы

- Exact base **`ad324418cdc66b18e9b71f76a412be6ccea20c7e`**, tree `b7e9e8ffa7212c1c41299c32ebd0b72fd9951a68`,
  read-only `/root/kani-fix-3300-c2-s3`, fork `fix/kani-3300-c2-s3`.
- Research `bbe38c563a`: `kani3300/c2-s3/{RESULT.md,ci-2/CI-RESULT.md}`. S3 принят: baseline bf8170b28 + controls-v2,
  run43614612145 — два false SUCCESS; candidate5ca3cbf2e9, run43614615441 — два intended single failures/reinit PASS,
  fmt/build/clippy PASS. ad324418cd — последующий docs-only commit; полный Quick на нём отдельно не заявлен.
- Прочитать PLAN-KANI3300-C2.md S4, аудит R4 F7/ответы10–11, `kani3300/m3-final/r3-capture-t1b/RESULT.md`,
  `r4-cycle-binding-worker14/RESULT.md`, `kani3300/c2-s1/DRIFT.md`, актуальный source наad.
- SEL1 вне C2: replay43611601987 наec85b782a1 дал sort4/swap SUCCESS и clean intended raw negative;
  `kani3300/sel1/replay-43611601987/RESULT.md`. Не импортировать эту production ветку или её proof credit в S4.

## 2. Механизм и результат S4

Один `BodyTransformation` на codegen unit сохраняет regular/stub transforms и prewarm от order_harnesses.
`DelayedUbPass::transform` берёт такое тело, добавляет root-specific instrumentation и пишет его в общий cache;
следующий harness получает уже дополненное тело. Исторические mixed inventories показывали добавления3/6/9 checks,
не пропажу. Это исходный механизм F7, а не изменение значения initializedness, разрешающее потерять required checks.

Результат: delayed-mutated cache entries живут **только до окончания codegen текущего harness**. Перед следующим
harness cache содержит прежние regular transformed bodies/metadata, без cumulative delayed operations и root Unsupported.
Это структурная граница изоляции; она не должна зависеть от порядка CLI selectors или совпадения старого golden.

## 3. Узкий snapshot/restore lifecycle

Primary paths: `kani-compiler/src/kani_middle/transform/mod.rs` (BodyTransformation/TransformationResult),
`kani_middle/transform/check_uninit/delayed_ub/mod.rs` (обе формы cache mutation),
`codegen_cprover_gotoc/compiler_interface.rs` (codegen_items и per-harness loop).

1. Узкий journal по exact Instance хранит **первый pre-delayed TransformationResult** данного scope: Body и исходный
   modified flag. Повторная delayed запись в тот же Instance не заменяет original промежуточной версией.
2. Все delayed cache writes проходят через этот механизм: ordinary instrumentation replacement **и** insertion
   Unsupported для failed analysis root. Иначе cycle/error root может загрязнить следующий legal root.
3. Snapshot делается после обычных transformations для конкретного тела, не как raw rustc/source-body backup.
   Сохранить prewarm, stubs/contract overrides/provenance, B1/checked_body, F5/F6, local Uninit/validity instrumentation.
   Newly computed regular cache entries остаются; genuinely absent до delayed replacement entry восстанавливается как absent,
   если такой случай допускает API. Не откатывать generated_loop_modifies/loop_modifies_bindings, принадлежащие regular passes.
4. Delayed версии должны оставаться видимыми **всему текущему** second reachability, codegen, contract/model emission.
   Restore — после их потребления, перед любым использованием transformer следующим harness. Проверить async export:
   queued artifact writer не должен позднее читать восстановленное MIR вместо уже materialized текущей модели.
5. Lifecycle покрывает normal completion, root Unsupported и любой recoverable early-exit. Scoped guard/structured API
   предпочтительнее ручных несогласованных clear calls. Не ловить panic ради продолжения с dirty cache;
   при unwind, если compiler продолжает использовать объект, restore обязан сработать. Process abort не выдавать за проверенный cleanup.
6. Все call sites codegen_items и Unit/PubFns paths проверить явно. Uninit-OFF/пустой journal не меняет семантику;
   начало нового harness не принимает незакрытый journal. Не clone/clear всего cache на каждый harness,
   не fresh transformer, не изменение codegen ordering, unit configurations или general global-pass архитектуры.

Изменения только lifecycle/API/этим pass'ом мутируемых entries и bounded tests/tooling. Runtime, protocol/masks,
immutable policy, SCC/points-to semantics, solver/check flags и std algorithms неизменны. Новый широкий refactor → STOP/review.

## 4. Обязательный различающий baseline: accumulation есть → его нет

Default baseline — **ad324418cd + те же test-only sources/observer**, candidate — S4 поверхad с идентичными inputs/flags.
bf8170b28 можно использовать как дополнительный исходный reference, но не подменять им согласованный baseline;
сравнение bf↔ad само по себе не является тестом F7, поскольку ни одна из этих голов его ещё не исправляет.

Переиспользовать existing `uninit-part1-composition/mixed.rs` либо его минимальную source-preserving extraction:
несколько roots одного unit с shared monomorphized callee (`std::ptr::read::<u8>`/минимальный общий helper),
legal immutable/ordinary, actual hole negative, cycle и unrelated legal companion. Не удалить реальные target reads.
На каждом tool отдельно запустить isolated roots и mixed selection в fresh processes с jobs1; selections с обратным
CLI order оставить regression coverage. Сначала проверить реальные unit membership/shared callee и observed ordering,
где доступен bounded receipt; source/CLI AB/BA не объявлять actual producer AB/BA.

Сравнивать **новые isolated↔mixed inventories одной версии tool**, не их равенство старым сериализованным C1b bindings.
Координаторский capture может использовать существующий `--collect-unbound --keep-output`, который собирает11 invocations
и возвращает2; это диагностический UNBOUND_CAPTURE, не PASS. Допустим меньший фиксированный manifest, если он различающий.
Сохранить effective argv/source/tool identities и full per-root checks/failures/Unsupported; normalized checkout prefix
может отличаться, но не status/описание/class/смысл source location. Порядковый Check N не identity: сравнивать multiset.

| Lane | Обязательный наблюдаемый результат |
|---|---|
| Baseline | Хотя бы один shared root имеет дополнительные delayed checks/operations относительно собственного isolated; actual retained delta и source mapping видны, не просто ожидаются по старому R4 |
| Candidate | У каждого выбранного root isolated и mixed inventories совпадают точно, включая количество checks, statuses, full failures/Unsupported/useful checks; нет накопления и потерянных checks |

Baseline с точным совпадением NONDISCRIMINATING: worker ищет другую форму/общий callee/настоящий shared unit,
а не объявляет отсутствие накопления исправлением. Нет достигнутой delayed instrumentation, разные units/flags,
ранний unrelated guard, неполный capture/timeout — тоже не воспроизведение. Координатор запускает bounded revised request.
Искомая baseline ошибка — inventory accumulation; legal root может SUCCESS в обоих lanes. Не требовать ложного UB FAIL
для подтверждения F7 и не ослаблять кандидат до совпадения verdict/failure-only при разном числе SUCCESS checks.

## 5. Unit controls и политика T1b

Unit tests journal: first snapshot survives two replacements, exact original body/modified flag восстановлены,
untouched/warmed/new regular entries сохранены, failed-root insertion снят, повторные harness scopes не накапливают journal,
empty/no-op scope и supported cleanup path работают. Не выдумывать tcx/Instance через unsafe для синтетического теста;
если нужен compiler-backed test, включить его в CI-request с точной наблюдаемой state assertion.

**Критерий кандидата — без allowlist.** Предпочтительно убрать acceptance exemption из существующего composition comparator
и обновить его bounded Python tests: пропажа/добавление любого check и изменение existing metadata/status отвергаются.
Диагностические delta reports сохраняются. Если для legacy baseline временно оставлен T1b classification, он может
объяснять только **добавления** known shared checks, никогда removals; на candidate comparison этот allowance отключён.
Не оставлять старую двустороннюю acceptance policy. Новую большую JSON framework/новые golden inventories не строить.
После structural review достаточно order-independent lifecycle + exact regression; отсутствие trace actual AB/BA
не выдавать за observed order, а различать с устранённой зависимостью модели по построению.

## 6. Composition debt, CI и handoff

S4 **должен убрать накопление**: исторические extra shared checks перестают быть допустимым расхождением.
Но обычный composition JSON может оставаться FAIL до S5: старые C1b bindings содержат другой path/location map,
а #5093 добавил2 реальных SUCCESS overflow assertions даже в isolated ordinary_ensures_legal (S1 DRIFT227→229).
Эти2 assertions сохраняются; их нельзя удалять или записывать в T1b allowance ради PASS. Не auto-bless roots.json,
не переписывать serialized inventories и не удалять suite этой стадией. Частичное улучшение состава drift зафиксировать отдельно.

Приёмка S4: различающий baseline и strict candidate isolation, unit/lifecycle controls, fmt/build/clippy и остальные
targeted expected/kani/ui/script/contract/mode suites. Known stale-binding composition FAIL не блокирует эту приёмку,
но **нарушение нового strict isolated↔mixed критерия блокирует**, даже при прежнем общем FAIL. Новый lost check/status/payload
regression не покрывается S5 waiver. Common Quick status/exits сообщать честно, без all-PASS при diagnostic FAIL.
Сохранить S2 immutable19/unit9 и S3 two negatives/reinit; per-fixture12-bit/default solver/checks/pins неизменны.
После native/lifecycle controls CI-request может включить existing Quick; полный3-platform Gate A — после S5/S6/freeze.

До CI: explicit Rust types/borrows/cache ownership review, first-write/restore ordering/async read audit, `git diff --check`.
Research `kani3300/c2-s4/`: INPUTS, MUTATION/LIFECYCLE-MAP, CONTROL-MANIFEST, BASELINE-CANDIDATE,
ISOLATION-DIFFS, REVIEW, CI-REQUEST, RESULT с отдельными structural/observed-order/JSON-debt статусами.
Все новые execution результаты NOT_RUN до координатора; old T1b capture не заменяет новый baseline.
Source neutral local commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push. Финал после выдачи:
`READY <local S4 source sha>`. Не переносить SEL1, не начинать S5 и не объявлять C2/весь SmallSort verified.
