# KANI3300 M2-B/R7 — separate private transfer snapshot, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия дизайн+реализация/review, **Cloud $0**.
Fork CI запускает только координатор. Это верификация корректности, не security-работа.
Worker15 владеет source/integration; worker14 параллельно делает test-only TASK-KANI3300-M2BR7-CONTROLS.md.

## Вход, accepted base и смысл результата R6b

Base **4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**, tree **af28e22ec446b254cfa3a28b2882eafa58d5a458**,
read-only `/root/kani-fix-3300-m2b-seed`. Это полная M1/M2/S3 цепочка, **не** CI-only filtered tree fc3bccbfff.
Читать m2br6b @**13eb2c6310**, m2bs3, M0 contract/M1 SOURCE-BINDINGS и текущие mem_init/contract/finalizer.
По координатору P1 R6-02b405c1f0592/run43276309576:132props,9340steps,381→115VCC,
829958vars/51173785clauses,50s/peak1.95GB, solver FAILED на assignable *var_17/*var_9.
R1+same-skip56cbc5c4a4/run43276317655:131props,8672steps,473→96VCC,>6.71GiB за9.7s,killed.
Observed boundary связан с buffer representation/private membership; это не доказательство конкретного DFCC operator/width
и не semantic PASS указательного варианта. Старые R4 private scalar split и R6 pointer runtime не cherry-pick как fix.

**Важная разница base:** текущий A3 уже хранит source-following snapshot `has_witness/value/relative_offset`, а не R1
saved_object_id/saved_offset. Snapshot снимается пока source жив, до Call(Move)/return. U pointer Option с последующим
copy_init_state_single(saved_source,...) теряет этот lifetime/false-state контракт. R7 сохраняет действующий протокол.

## Scope и два reviewable source commits

Создать **/root/kani-fix-3300-m2br7**, ветку **fix/kani-3300-private-transfer-state** от exact base.
Existing/dirty destination/другой pin → STOP без reset/stash. Старые source clones/release/B3/diagnostic branches не менять.

1. **B0 — base + bootstrap fix:** перенести только exact-identity initializer addition в shared SKIPPED_ITEMS из R6b,
   адаптировав к текущему mod.rs (BeginArgumentTransfer и все новые entries сохраняются). Не переносить R1 file целиком.
   Runtime/fixtures от4f64 unchanged. Отдельный SHA/tree — matched current-chain control, а не старый R1 контроль.
2. **B1 — B0 + separate snapshot:** source sites `library/kani_core/src/mem_init.rs`,
   `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs`; тесты отдельно от14. Никакой ABI/relevance/layout/DFCC
   backend/alias/Move/cache rewrite. Сначала DESIGN.md с field-state mapping, затем code и bounded review.

B1 — узкий correctness-preserving candidate; его меньшая стоимость пока **не установлена**. Если B0 сам закрывает
P1/P2/frame/resource gates, координатор выбирает минимальный B0, не сохраняет ненужную representation переделку ради плана.
Если B1 остаётся heavy, STOP с actual DFCC size/use finding, без автоматического unsafe pointer fallback/нового bisect.

## Дизайн B1: вынести текущий snapshot, не откатывать A3

- MEM_INIT_STATE сохраняет исходный **KaniMemoryInitializationState** marker и только tracked_object_id/offset/value.
  Вынести все12 argument_buffer fields (9usize/3bool) в один отдельный mutable private static с собственным record.
  Возможное имя ARGUMENT_BUFFER, marker **KaniMemoryInitializationArgumentBuffer** (R4-A pattern уже source/build-audited).
  Constructors/initial values, masks/types и reset behavior отобразить один-к-одному. Не добавлять pointer field без нужды.
- Begin/store/load bodies после field-access renaming должны сохранять алгоритм: signature/count/written/remaining/order,
  selected index и usize::MAX sentinel, mandatory return0, demonic argument competition (включая none), layout validation,
  has_witness **отдельно** от value=false и relative-offset snapshot. Не менять helpers/model signatures/caller indices.
- Store читает live source object/offset/value **до Move/reset**; load использует только сохранённый snapshot и live destination.
  Source-following branch переносит actual false через `buffer_value && layout[relative_offset]`; no-witness не означает
  witness true. Никакого reread source после возврата/Move, stale-pointer copy, default true/missing-protocol fallback.
- Initializer по-прежнему nondet-выбирает main witness, value=false, затем инвалидирует buffer active/selected/has_witness
  точно как base. Не заменять partial reset whole-record zeroing: inactive payload/sequence fields не менять сверх base.
  Matched loads/depletion clears/order и panic=abort/normal continuation сохраняются. Bootstrap skip только private initializer.
- M1 finalizer продолжает находить **ровно один main marker** и те же3 typed fields; reset-completion seed остаётся после
  всего reset, до first user effect. Новый buffer — named mutable state, не immutable-origin allocation. Finalizer/registry
  менять source не требуется; сохранить его hashes. Не добавлять buffer в immutable seeds и не reseed на refs/calls.

### DFCC: две private identities, buffer fields вместо whole-buffer target

В codegen_modifies_contract разрешать main state **и** transfer snapshot по двум distinct exact markers,
через actual StaticDef→Instance::mangled_name→emitted symbol. Main target оставить прежним. Для transfer snapshot
сформировать Lambda::as_contract_for по **отдельным scalar field lvalues**, покрывающим все12 mutable protocol/snapshot
полей; не добавлять ещё и whole-buffer lambda. Это один выбранный candidate, не очередь whole/fieldwise variants.
В DESIGN проверить полный write footprint: в Begin/store/load/reset нет whole-record writes в проверяемом contract body;
constructor выполняется как static initialization. Появившийся whole-aggregate/byte/padding write или неразрешимая field
coverage — STOP для уточнения дизайна, не blanket whole-object exemption. Цель — проверить encoding без aggregate target,
а не заявить, что именно такой target уже доказан причиной OOM. R4 whole-private scalar split оставался heavy на старом R1.
Сохранить kani/core fallback, unique marker/object identities. No name wildcard/user-memory target и no duplicate main marker.
При нужной uninit/PFC instrumentation оба emitted objects и все нужные scalar targets обязательны; lookup failure не прятать.
No-uninit/нерелевантные models не должны получать blanket compile failure — проверить source admission/target availability.
Pattern code R4-A75090c498 можно использовать **как identity-lookup reference**, не wholesale patch: current buffer имеет12
fields, а число assigns lambdas теперь не2. Проверять identities и полный набор field expressions отдельно от числа lambdas.
Не менять public modifies, clause routing, frame checks или включать user referents в private set.

До READY: MODEL-MAP со всеми old→new fields/initial/reset/read/write operations, constructor closure и fn_marker/signature
audit; token-normalized Begin/store/load algorithms отличаются только field accesses. Любое другое изменение требует
конкретного invariants rationale/review; broad model premise → STOP с proposal.

## Разделение с worker14 и состав final candidate

Worker14 владеет только новым test path и r7c/; существующие fixtures/goldens и source не редактирует.
Получить его exact reviewed test-only SHA/diff/hash. Импортировать **только new test delta**, не его production base поверх B0/B1.
Если пакет ещё не готов, record exact composition request без ожидания/пересоздания чужих tests. Один source owner15.
В base уже есть legal-pair/postcondition-hole: они остаются в tree. Никаких CI-only удалений/ignore/смягчения goldens.

## Gate G1 → G2, все запуски координатора

**G1:** build/fmt/clippy, затем unchanged P1 на B0 и B1 с одинаковым test delta/flags/tools; один root/process,
existing timeout300s/watchdog>6GiB. P1 SHA256 fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b.
Build error → NOT_RUN solver; ранний Unsupported/frame/path loss не resource improvement. По каждому: actual reset→seed→
transfer→ensures path, both private symbols, main+buffer-field assigns/actual write scopes, steps/VCC/conversion/vars/clauses/RSS/exit.
Memory/time goal — steady completion внутри existing cap, а не обещанные2GB; отсутствие cutoff без правильных checks не gate.

Если source candidate проходит P1, на нём P2 (existing postcondition-hole, source hash
61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759), lawful-modifies positive и existing frame-negative,
requires-clause negative, selected true/false/nested/repeated argument-return controls. P1 all intended checks SUCCESS;
P2 только intended ensures payload u8 read FAILURE, other legal/frame/protocol checks PASS; user out-of-frame write всё ещё
frameFAIL у outside assignment, private state не даёт extra assignableFAIL. Expected negative verdict не равен extra failure.
Source-bound property location/object/target важнее var_N. Actual IDs меняются только после observed binding, не заранее.

**G2 после G1:** полный existing Uninit Quick на final source+tests, unit immutable_allocations5, kani Uninit,
expected **с обоими тяжёлыми legal-pair/postcondition-hole**, ui и mem-init-reinstrumentation. CI-only workflow commit может
менять workflow, но не удалять/ignore fixtures. Полный platform/full-suite gate и actual SmallSort replay позже отдельным handoff.
Source/full test tree/actual flags/CI wrapper identities отдельно. Restricted baseline Quick43257528539 исключал2 selectors,
поэтому его135/0 не full G2 и не новый head PASS. Ничего не запускать/не ждать CI в этой сессии.

## Review, результаты и STOP

TYPE-AUDIT каждого Rust delta: exact API/field types, comparison/arithmetic operands, usize/u64/u128 casts/bounds,
references/unsafe/static_mut, iterator/lambda Vec typing, constructor completeness. B3 E0308/E0277: rustfmt/Luna не compiler.
Pinned rustfmt TASK-M1, hash/source/Python/diff checks разрешены; local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Один bounded Luna High review actual invariant/frame/field delta и input-independent trust boundary; fixes тому же reviewer,
без nested delegation. Worker14 review tests не заменяет model review. Новые outcomes NOT_RUN до fork CI.
g0 **kani3300/m2br7/**: INPUTS.json, DESIGN.md, MODEL-MAP.md, TYPE-AUDIT.md, SOURCE-MANIFEST.json, TEST-MANIFEST.json,
REVIEW.md, CI-REQUEST.md, RESULT-KANI3300-M2BR7.md (≤25 строк, B0/B1/control/composition/gates раздельно).
Neutral local Kani commits, author/committer Tiramisu-Cake <igkharin@gmail.com>, без [skip ci], Kani **не push**.
Research [skip ci], тот же author/committer, stage только m2br7/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, raw logs/archives/credentials, PR/issue/комментариев/сторонних PR links.
После reviewed source/composition package STOP. M3 активируется лишь после accepted G1/G2, не READY.
Последняя строка: `READY <sha локального R7 B1 source-кандидата>`.
