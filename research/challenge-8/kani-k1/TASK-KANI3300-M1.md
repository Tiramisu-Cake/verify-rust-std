# KANI3300 M1 — immutable-mask seeding для anonymous/promoted allocations, worker 14

**Выдано координатором 2026-11-12. M0 принят с уточнением export boundary ниже.** Runtime **Codex**, одна стадия,
**Cloud $0**. Реализация/тесты/статическое review; CI запускает только координатор. Это верификация корректности, не security-работа.

## Вход, ветка и выбранная модель

Прочитать `kani3300/m0/{MODEL-CONTRACT.md,IMPLEMENTATION-PLAN.md,CONTROL-MAP.json,REVIEW.md}` @ **`742c77fa03`**,
`kani3300/d0a/{RESULT.md,NOTES.md}` @ `ff5cabbfca` и `TASK-KANI3300-C1T.md`.
Чистый base **`6134e42dd1c65dc980336e7d9455aba02d423edf`** в `/root/kani-fix-3300-p1b1` — read-only.
Создать отдельный clone **`/root/kani-fix-3300-m1`**, ветку **`fix/kani-3300-immutable-mask`** от base;
при существующем destination/другом состоянии STOP без reset/stash. B1I-A production/fixtures сохраняются.
Не подменять base диагностическими a0a2386001/5eec235e3, не переносить D0 serde/runner/hooks/workflows.

Выбран M0-A: source-bound Some/None mask immutable referent → canonical emitted symbol → seed **после завершённого
witness/buffer reset, до user effects**. Никакого per-reference reseed, runtime bitmap, global true или raw_eq rollback.
Flat `[MU<T>;N]` / `[MU<T>]` остаются в scope. Левый temporary уже имеет правильный normal-edge setter — его не чинить.

**Уточнение lifetime:** registry принадлежит **одному GotocCtx/экспортируемой GOTO model**, не общему compiler CodegenUnit.
Каждый harness получает собственные GotocCtx/alloc_map/symbol table, хотя BodyTransformation общий. Finalize после всех
producer codegen/contract/quantifier post-passes данного model, до metadata snapshots, split и async export. Если нужно,
переставить snapshots после finalize; не менять порядок harness/cache lifetime. Уже отправленный symbol table не патчить.
Это конкретизация placement M0, не cross-harness registry и не разрешение переделать экспортный pipeline.

## Реализация

1. Frontend origins/descriptor: Anonymous MemLoc и side table по M0; constant operands и deref successors сохраняют
   referent identity, offsets/extent и все alternatives через casts/helpers/joins. Seeds обоих raw_eq operands;
   whole-object relevance не выдавать за точный byte offset. Mutable destination instrumentation/ранее собранные edges не терять.
2. Decode carrier provenance/addend отдельно от referent mask. Qualified M1 admission — fixed, relocation-free anonymous/
   promoted referent с actual Mutability::Not, независимым freeze/no-UnsafeCell обоснованием и byte-exact emission.
   Pointer carrier может содержать relocation: проверить pointer width/endianness, initialized addend range и target.
   Type `&T`, const flag и hardcoded has_interior_mutabity=false недостаточны; origin evidence не терять при erasure.
3. Снять mask `is_some(referent.bytes[i])` **до** unwrap_or(0); Some(0) true, None false. Это не D(T), carrier mask или
   маска физических GOTO zero bytes. Записать source→emitted layout: размер/offset каждого byte; zero extent не индексировать.
4. При alloc_map insertion **и hit** связать requested allocation key с реально возвращённым symbol. Canonical descriptor
   включает mask/extent/mutability/freeze/relocations/layout; compatible aliases дают один seed на symbol.
   Conflicting descriptors — точный diagnostic/STOP emission; не OR/intersection/перезапись и не доверие одному hash/Allocation equality.
5. Собрать registry текущего GotocCtx и seal после всех materializing passes. По существующему KaniFunction marker найти
   InitializeMemoryInitializationStateModel и private state marker. Патчить каждое normal completion reset definition:
   исходные nondet object/offset, false и buffer resets сохраняются; затем matching nonempty immutable object получает
   точный mask[relative_offset]. Использовать live emitted address и runtime pointer_object/offset, не AllocId как object number;
   проверенные bounds/no-overflow, unmatched/out-of-bounds witness не меняется. L=0 — без seed mask indexing/object query.
6. Seed действует только в начальной фазе каждого reset epoch; повторные refs/calls/copies не переинициализируют state.
   Source-following false должен дойти до mutable destination при copy/argument/return; новые optimistic branches не добавлять.
   Static materialization/closure registry должны предшествовать первому user effect/read. Late symbol, missing reset site,
   неправильный private-state/DFCC scope или незамкнутый symbol/range bridge — STOP, не fallback true.
7. Named statics/foreign/allocator/heap policy, ordinary Item protocol, D(T), Move/reset и normal/unwind edges не расширять.
   Неeligible allocations не получают immutable seed; не вводить blanket compile rejection всех vtables/статик/констант,
   которые не участвуют в новом admitted tracked path. Для watched unsupported origin/range/relocated referent — достижимый
   pre-effect Unsupported либо явный release blocker, не silent skip и не ложное обещание покрытия.
8. Scope production — необходимые points-to/initial-target/relevance/descriptor, operand codegen/registry/finalizer sites M0.
   Existing marker/state доступен через symbol table; public runtime ABI/новые dependencies не нужны. Marker добавлять только
   при доказанной невозможности связать существующий; более широкая модель/ABI/runner/contract rewrite → STOP с обоснованием.

## Тесты и разделение владения

- Шесть promoted direct/helper legal/left-hole/right-hole selectors готовит **15 по C1-T** в отдельной ветке от того же base.
  Не редактировать его files параллельно. Перед final M1 package импортировать точный test-only commit без source changes
  (проверить diff/path/hash), либо передать координатору точный composition request, если commit ещё не готов; не дублировать fixtures.
  Эти semantic goldens остаются одинаковыми на baseline/M1: legal SUCCESS, hole — intended operand uninit FAILURE.
- Сохранить два existing D0 legal и raw-eq left/right/padding, typed/data/false, Item-return, mutable reset/overwrite controls.
  Дополнительные различающие M1 controls в собственном path: Some(0) против None; equal descriptor reuse против conflict;
  anonymous hole→raw copy→mutable destination negative; mutable/unqualified object не seeded; zero extent/no index.
  Предпочесть existing controls и небольшие настоящие input/registry unit tests; не создавать framework и не тестировать
  только «сгенерировали нужную строку». Synthetic registry conflict не выдавать за достижимый Rust-source repro.
- Нужны exact target/source/Some-None mask/symbol/reset-completion bindings. Для собственного CI request достаточно
  существующего Quick и при необходимости --emit=mir/targeted properties; **новый diagnostic runner не строить**.
  Initial goldens не содержат выдуманных property IDs. Все runtime/model outcomes остаются NOT_RUN до CI координатора.
  При hole общей FAILURE недостаточно: binding intended operand/read и законного другого operand отдельно в CI acceptance.

## Review, результаты и STOP

Статика: git diff --check, pinned API/source audit imports/unused/-D warnings, разрешённая rustfmt-обёртка
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`.
Один bounded независимый Luna High review semantic candidate + tests/invariants; delta тому же reviewer, без вложенной
делегации. Конкретные soundness findings устранить до READY. Code/test commits нейтральные, без [skip ci], author/committer
`Tiramisu-Cake <igkharin@gmail.com>` через git -c. **Kani не пушить**, source clones/D0/C1-L/B1/B3 не менять.

В g0 `research/challenge-8/kani-k1/kani3300/m1/`: `NOTES.md` (≤40 строк), `SOURCE-BINDINGS.md`, `TEST-MANIFEST.json`,
`REVIEW.md`, `CI-REQUEST.md`, `RESULT-KANI3300-M1.md` (≤20 строк). Full base/candidate/tree, production/tests/dependencies
и exact C1-T composition SHA отдельно. Локальные проверки не называть compilation/verification PASS.
Request координатору: baseline+C1-T и M1+те же tests, два D0 legal, distinguishing controls, затем existing Uninit Quick;
проверить reset→seed→first-effect placement и exact named outcomes. Full gate и M2/M3 позже, не включать их исполнение сюда.
Если source/mask/layout/freeze/epoch bridge не установлен, вернуть PREPARED/BLOCKER с точным gap, а не complete model.

Research commit [skip ci], тот же author/committer, stage только kani3300/m1/, push g0 без force; чужой c1l/c1t/staged
diff не включать. Concurrent/non-fast-forward — handoff без reset/stash/force.
Локальные cargo/rustc/Kani/CBMC/Miri/сборки, Actions/Cloud dispatch/workflow edits, raw logs/archives/credentials,
PR/issue/комментарии и сторонние PR links запрещены. Python/статические schema/hash проверки допустимы.
После reviewed candidate STOP до CI координатора. Последняя строка: `READY <sha локального M1 Kani-кандидата>`.
