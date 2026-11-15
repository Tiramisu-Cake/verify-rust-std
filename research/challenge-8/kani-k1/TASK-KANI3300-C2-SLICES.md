# C2-SLICES — нарезка принятого C2 на reviewable upstream-кандидаты

2026-11-15. Worker14 + worker15; одна ограниченная стадия на сессию, переходы принимает координатор.
Это верификация корректности, не security-работа.

Задача — восстановить принятый C2 из логических срезов с production/test/docs ownership, а не изменить модель.
**Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. CI, push/dispatch и публикации — только координатор.**
Cloud $0. Разрешены Git/Python/static review и synthetic tests без verifier. PR-тексты — отдельная будущая стадия,
здесь не писать/обновлять описания PR, не создавать PR/issues, не менять поданный B1 или freeze refs.
Нарезка и её локальные коммиты разрешены после выдачи соответствующей стадии; подготовка workflow не разрешает запуск.

## 1. Единственная база и уже поданный B1

- U: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Поданный B1: `6fe484b30043b3696b5f1ccc4bea0e42891ad012`, parent U,
  fork `fix/kani-uninit-unresolved-call-v3`, upstream kani#5172.
- C2 F: **`ad499e41dd2db9ccd432f89721638a1f3a0bbd44`**, tree
  **`9829702c1aa0ecb73c860fc0ad5451757917d6cb`**; refs `fix/kani-3300-c2-s6`, `freeze/kani-3300-c2`.
- Read-only source `/root/kani-fix-3300-c2-s6`; B1 `/root/kani-fix-b1-upstream`. Ни один не checkout/reset/clean/stash.
- Evidence g0: `kani3300/c2-s6/ci-43656920767/ACCEPTANCE.md`,
  `kani3300/c2-gatea/ACCEPTANCE.md` @9298ff50e1 (43665002636, 33 стадии на трёх платформах),
  `kani3300/c2-gateb/RESULT.md` @cc5c98a59c (43683557088, две merge SUCCESS + sort4 boundary).
  Старые C2-FREEZE/RESULT со статусом PREPARED и head61eb — не актуальная приёмка ad499.

На момент подготовки GitHub API подтвердил: upstream main **ещё U**; #5172 **open, merged=false**, head ровно B1,
base main/U. Это snapshot, не обещание неизменности refs. В стадии0 перепроверить и записать timestamps/полные SHA.
`merge_commit_sha` открытого PR — возможный test-merge, не свидетельство merge и не база нарезки.

**Решение базы: lossless нарезка на U+B1, без rebase.** B1 не повторно squash/cherry-pick в новый первый PR:
сохранить существующий commit как parent последующих срезов; delta первого нового PR считается от B1.
До merge B1 готовить локальный stack и явную карту зависимостей, не выдавать B1 за upstream и не подавать duplicate PR.
Если main/B1 сдвинулись: сохранить эту lossless линию, записать UPSTREAM-DRIFT; перенос на новый pin — отдельная
согласованная стадия с patch-equivalence map и новой квалификацией, без плавающего rebase в середине нарезки.
При merge/squash B1 сверять реальный patch/tree, не только commit ancestry; один лишь сменившийся SHA не означает потери B1.

Обязательные чтения: AGENTS; `PLAN-KANI3300-C2.md`; R4 §14;
`kani3300/c2-s5/{ORACLE-MAP.md,ORACLE-MAP.json,MODE-COVER-MAP.md,DISCOVERY-DELETION-MAP.md,SENSITIVITY-MANIFEST.json}`;
`kani3300/c2-s6/{CONTROL-MAP.md,DOCS-SCOPE-MAP.md}`; authoritative acceptances выше.
Исходные карты описывают структуру оракулов; их исторические NOT_RUN не отменяют последующие принятые runs.

## 2. Рабочие области, владельцы, порядок

Создать отдельные чистые **worktrees** (`git worktree add` от `/root/kani-fix-3300-c2-s6`; диск ~96%, новые полные
clone не делать, target/артефакты не копировать), не использовать существующие dirty paths:
worker14 `/root/kani-fix-3300-c2-slices-w14`; worker15 `/root/kani-fix-3300-c2-slices-w15`.
Research `kani3300/c2-slices/` в g0: worker14 — `source-map/`, `slice-01..06/`, `recompose/`;
worker15 — `oracle-map/`, `reviews/`, `ci/`, `f7/`. Каждый пишет только свою область.

| Стадия / одна сессия | Worker14 | Worker15 | STOP / передача |
|---|---|---|---|
| 0, карта до кода | Фиксирует refs, полный source-hunk/dependency map U→B1→F | Полная test/oracle/docs map, план Quick и F7 extraction | Координатор принимает карту; не начинать сразу все срезы |
| 1, ANALYSIS | Один coherent S3/CC candidate поверх B1 | Read-only review, exact-head CI-only overlay/request | No-regression + units принимает координатор; целевая integration qualification остаётся PENDING до4/5, см. решение ниже |
| 2, IMMUTABLE | M1/E2+F5 поверх принятого1 | Review provenance/masks/тестов, CI request | Нет смешения descriptors и потери false |
| 3, LAYOUT-RAW | A1/A2/layout/raw_eq поверх принятого2 | Review padding/extents/negative oracles, CI request | Прямой u8 mixed/promoted raw_eq; nested offsets/multi-root oracle явно отложены до4 |
| 4, STORAGE | Storage/protocol+F6+hook fix поверх принятого3 | Review pairing/Move/Copy/DFCC/oracles, CI request | Не выпускать paired caller без paired callee/return |
| 5, CLOSURE | Zero-sized/upvar layout поверх принятого4 | Review capture masks/offsets и CI request | Captures не заменяются layout tuple/all-true |
| 6, E1 + остаток docs | Semantic edge tests, завершение Scope A/docs поверх принятого5 | Review полноты oracle map, CI request | Общие production guards уже4; отсутствие новой production delta допустимо, не dump остатка в E1 |
| 7, F7 отдельно | Read-only integration/recompose review | Отдельный F7 commit поверх принятого6, CI request | Final composed tree и controls согласованы с F |
| 8, сверка | Recompose exact-tree/diff receipt | Независимая проверка ownership/CI lineage | Handoff координатору; PR-тексты позже |

### Решение dependency review после стадии0 — вариант C

Входы: worker14 source-map @`bf455494e4`, worker15 oracle-map/Quick plan @`d1dbc70afd`;
`source-map/DEPENDENCIES.md`, `oracle-map/DEPENDENCY-REVIEW.md`. Это static inventory, не новые CI observations.
Приняты следующие уточнения без изменения F и порядка PR:

1. Exact qualification/recognition helpers `immutable_origin_type_supported`, export, `wrapper_inner`,
   `maybe_uninit_storage`, `for_storage` и необходимые imports принадлежат2; typed/deinit/protocol helpers —4.
2. Все projected-raw/address guards принадлежат4. Пятистрочная ordinary-union constant branch V420–424
   (F coordinates, source-map `B1--F:19:009`, part +420/count5) также переходит6→4 вместе с её prerequisites.
   Поэтому `marker-hook-calls/marked-model-{initialized,hole}` назначаются для исполнения на4; будущий CI должен это подтвердить.
3. На3 квалифицируются u8 mixed + promoted raw_eq. `nested-pat-{data,padding}/main`,
   `nested-enum-{same,different}-padding/main`, полный `raw-eq-uninit/main` требуют4 и исполняются там без разрезания fixtures.
   Source ownership offset fixes остаётся3; их integration qualification до4 — PENDING.
4. `marker-hook-calls/generated-modifies-no-shadow` исполняется на5: это captured PFC companion,
   не обязательство получить тот же final fixture на4. Остальные hook controls, включая marked-model пару, —4.

**Для ANALYSIS выбран C: no-regression на1, интеграционные оракулы на4/5.** Не вводить новые non-MU fixtures,
не удалять позднее дополнительные тесты и не сливать/переставлять production slices ради отсутствующего раннего oracle.
Это изменение прежнего условия «обязательный reached positive/negative уже на1», а не утверждение, что ActiveCalls unit
или FunctionContracts без uninit флага проверяет selected contract MIR/обычные entry setters.

На1 обязательны полный присутствующий upstream uninit/delayed-UB набор по manifest, унаследованные B1 controls,
весь kani FunctionContracts и expected/function-contract с их штатными flags/goldens, ActiveCalls units9 и общий Quick.
Не добавлять uninit flags в штатные contract tests. Это **регрессионная и unit-проверка**, не целевая интеграционная квалификация S3/CC.
Для `SLICE.json` головы1 записать `qualification_kind: NO_REGRESSION`, `integration_status: PENDING`,
`integration_heads: [4,5]`, exact tested selectors и deferred obligations со source-hunk/fixture/golden hashes:

- На4: `points-to-cycles/{dag,self-cycle,mutual-cycle,roots-acyclic-first,roots-cycle-first}` и
  `ordinary-slots/{payload,padding}` — actual traversal/cycles/error, сброс cycle state между roots и ordinary entry/pointee distinction.
- На5: `ordinary-slots/positive` целиком, `points-to-cycles/capture-free`, contract-immutable/strong/mode/root fixtures
  по полной oracle map — selected contract bodies, ordinary/PFC paths, scalar/ref entry seeding и captured environments.

До4/5 отсутствие этих final fixtures на1 — разрешённая dependency граница, не пропуск уже имеющегося failing test.
Каждая отложенная обязанность закрывается **явным результатом** на exact cumulative head4/5 с достигнутыми полезными
SUCCESS/задуманными negatives и ссылкой на неизменённые source-hunk parts среза1 (для nested layouts —3).
Одно aggregate CI exit0 или synthetic ActiveCalls PASS не закрывает её. Не называть1 standalone fully qualified;
при закрытии хранить provenance «integration-tested on head4/5», не переписывать историю проверки головы1.
До закрытия обязательств нельзя завершать upstream-submission handoff/PR-text stage как будто каждый срез уже получил
собственную интеграционную квалификацию. В будущих PR-текстах раздельно раскрыть проверенное на1 и integration на4/5.

Вариант C снимает **плановый STOP отсутствия раннего oracle**, но не разрешает реальные ordinary/layout regressions,
false SUCCESS, дополнительные Unsupported или ослабление goldens: при таком наблюдении остаётся STOP.
Worker14/15 сначала согласованно обновляют каждый свою source/oracle/Quick/dependency map и hashes/manifests по этому решению;
исходные stage0 findings не выдавать за ошибочные runtime результаты. Затем координатор выдаёт стадию1 отдельно.

Worker14 — единственный writer production/tests/docs в основной линии стадий1–6.
Worker15 не дописывает эти же файлы параллельно: замечания возвращает worker14; его overlay живёт в другом clone/ref.
F7 карту и static review можно готовить параллельно, production extraction — после передачи immutable head6.
В стадии7 writer — worker15, worker14 только reviewer. Никакого автоматического цикла выдачи всех стадий подряд.

## 3. Карта production-хунков и зависимостей

Префикс **M** ниже: `kani-compiler/src/kani_middle/`; **C**: `kani-compiler/src/codegen_cprover_gotoc/`;
**V**: `M/transform/check_uninit/ptr_uninit/uninit_visitor.rs`; **L**: `M/transform/check_uninit/ty_layout.rs`.
Это исходная карта, её надо уточнить до полного FILE/HUNK-MAP с original blob/диапазоном/символом/hash и владельцем.
**Ни один общий файл целиком не restore-ить из F ради одного среза.**
Исторический S3/CC (contract registration) не путать с C2-S3/F6 (nested reset, срез4 ниже).

| Срез | Production ownership | Зависимости / граница |
|---|---|---|
| B1, уже #5172 | U→6fe: unresolved-call resolution/one walk+flush, points-to no-body guard, соответствующие visitors и baseline fixtures | Не добавлять к B1 поздние entry/return/tuple controls из C2. B1 **не меняет** `mem_init.rs`/`kani_functions.rs`; их поздние хунки не выдавать за поданный B1 |
| 1 ANALYSIS, S3+CC1/2/4 | `M/points_to/{mod.rs,points_to_analysis.rs,points_to_graph.rs}`: selected registration bodies, body/override provenance, call-cycle tracking, receiver/argument paths; `check_uninit/delayed_ub/{mod.rs,initial_target_visitor.rs,instrumentation_visitor.rs}`: согласованная registration traversal и ordinary scalar/ref entry seeding; resolver signature/call sites V по source map | S3 без CC fixes не отдельный кандидат. Сохранить B1 Err/no-body/flush, upstream checked_body/tail-call/atomic fixes. Anonymous immutable arms — срез2, storage entry protocol —4. Ранняя проверка no-regression, integration obligations —4/5 |
| 2 IMMUTABLE, M1/E2+F5 | `M/anonymous_allocations.rs`, `M/mod.rs`; `C/context/immutable_allocations.rs`, context mod/state; `C/codegen/{operand.rs,static_var.rs}`, `C/context/goto_ctx.rs`; prepare/finalize hooks в `C/compiler_interface.rs`; anonymous-origin target/graph/delayed arms; `immutable_origin_type_supported`, export и L::wrapper_inner/maybe_uninit_storage/for_storage с imports | Registry descriptors+alias coalescing+finalize/seal идут вместе. Использовать существующие U reset/private-state markers. Qualification/raw storage helpers имеют одного владельца2 и потребителей4; extended runtime не переносить из4. Не включать F7 scope wrapper из того же codegen_items |
| 3 LAYOUT-RAW, A1/A2 | L: nested Pat offsets, enum local-mask offsets/сравнение masks; V: raw_eq checked byte extent/оба operand и can_skip_intrinsic; согласованные layout/relevance/operation-builder хунки для этих операций | M1 уже присутствует, иначе вернутся ложные raw_eq failures на promoted RHS. Raw byte extent не тождествен typed data mask. Qualification helpers L уже2, typed/deinit/protocol helpers —4, closure arms —5 |
| 4 STORAGE/protocol+F6 | V: storage recognition consumers/typed assignment/transmute, raw vs typed copy, paired direct Item argument/return0, live-source snapshots, Copy/Move/deinit, nested resets, has_transfer_protocol Hook exclusion, все projected-raw/address guards и ordinary-union constant branch V420–424; `ptr_uninit/mod.rs`; `check_uninit/{mod.rs,relevant_instruction.rs}`: MemoryInitOp/builders/signatures, общий constant_init_mask/SetStorage; L: for_typed_storage/for_deinit/argument_size; ранние unsized guards и argument_size unit; `M/kani_functions.rs`: BeginArgumentTransfer и marker classifier tests; `library/kani_core/src/mem_init.rs`: runtime masks/copy/buffer/private state/normal-edge protocol | Wrapper/raw qualification helpers уже2, не копируются. Caller/callee/runtime/signature changes атомарны, вместе с false/full overwrite/F6. Hook exclusion ровно `KaniFunction::Hook`, не все markers. Никакого R7/R8 runtime/SEL1. Общие маски, guards и последняя ordinary-union ветка не оставляются до E1 |
| 5 CLOSURE | L::data_bytes_for_ty: sized zero-byte Closure и monomorphized upvar layout с реальными offsets; согласованные imports/internal type context | Отдельно от wrapper/storage layout. Протокол и relevant-body paths уже есть; captured ordinary/PFC paths получают верные masks, не blanket admission union/UnsafeCell |
| 6 E1 | Отдельная semantic edge qualification: final edge tests/docs, включая ordinary-union constants, projected raw fields и unsized boundaries | После stage0 решения вся соответствующая production delta уже4, включая V420–424. Нулевой production остаток допустим; не придумывать новый fix, не дублировать guard/operation и не вносить aggregate Unsupported |
| 7 F7, отдельный PR | `M/transform/delayed_cache.rs`; scoped API/RAII и unit tests в `M/transform/mod.rs`; delayed writer `replace_delayed_body`; cprover и `codegen_aeneas_llbc/compiler_interface.rs` scope вокруг каждого model codegen | Восстанавливать только delayed mutations на всех выходах, не убирать regular/stub transforms. Сохранить immutable prepare/finalize из2. Срез не содержит SEL1 и не сохраняет T1b allowlist |

### Правила для хунков на стыке

- Один helper/type/import/guard имеет одного владельца и полный список consumers в SEAMS.md; зависимые commits
  используют ancestor, не копируют helper и не приносят всё соседнее изменение. Public/internal API менять вместе с call sites.
- Общий safety guard/data-mask primitive переносится в самый ранний срез, где он нужен для корректного поведения;
  это отражается как prerequisite в карте, а не скрытое расширение scope. Нейтральный import — с первым consumer.
- E1 const masks / SetStorage / unsized guards и storage helpers сильно пересекаются: общий production хунк и его
  базовый контроль принадлежат4, E1-specific дополнительные tests —6. Нельзя оставлять заведомо небезопасный intermediate до E1 ради названия PR.
- F7 API ещё отсутствует в1–6: не добавлять фиктивный no-op `replace_delayed_body`/RAII. При необходимости использовать
  исходную pre-F7 writer форму из `ad324418cd` для intermediate, зафиксировав точную замену в7. Это не разрешение
  возвращать JSON allowlist или выдавать intermediate за structurally isolated. Если separable extraction не получается — STOP.
- Риск порядка: S3/CC открывает layout captured closures, который U считает Unsupported. Если coherent1 без5 даёт
  новую ordinary contract regression, её **не скрывать** исключением теста/новым golden. STOP с минимальным prerequisite
  и предложением координатору (перенос нужного closure хунка/объединение); самостоятельно не менять принятый PR порядок.
- Никаких scaffolding stubs, мёртвых future APIs, TODO implementations или temporary weakened checks ради compile.
  Нет новых fixes/рефакторинга. Перенос существенной семантики между срезами требует review dependency map до реализации.

## 4. Карта тестов и docs

Все пути далее под `tests/expected/uninit/`, если не указано иное. `.rs` + соответствующий `.expected` — единая пара.
Тесты привязывать к **первой голове, имеющей все prerequisites**; это не право пропускать baseline regression.
Для каждого теста записать owner slice, earliest runnable head, linked source hunks, полезные assertions и exact negative.

| Срез / группа | Что переносить / чего не потерять |
|---|---|
| B1 dependency | Точные тесты из B1 `unresolved-calls/**`. Поздние `item-return-*`, `tuple-maybe-uninit-*` и правки entry fixtures требуют отдельной attribution к1/4, не изменения #5172 |
| 1 ANALYSIS | На1 — baseline/B1 uninit+delayed-UB, полные штатные FunctionContracts и active_call_tests9: NO_REGRESSION, не MIR integration credit. Owner1 integration fixtures `points-to-cycles/{dag,self-cycle,mutual-cycle,roots-acyclic-first,roots-cycle-first}` и `ordinary-slots/{payload,padding}` исполняются на4; `ordinary-slots/positive` и capture-free/contract paths —5. Эти обязательства остаются в SLICE.json до закрытия |
| 2 IMMUTABLE | `immutable-masks/**`, `immutable-descriptor-coalescing/**`, `promoted-allocations/**`; unit immutable_allocations9; `part1-edges/immutable-{static,subrange,relocation}-*`; `mixed-promoted-allocations`/`contract-immutable-masks` распределить с учётом3/4/5, не ждать SUCCESS от неподдержанного raw_eq/closure |
| 3 LAYOUT-RAW | На3 — u8 raw/eq mixed + promoted raw_eq и доступные immutable source controls. Owner3 `raw-eq-uninit/main`, `nested-pat-{data,padding}/main`, `nested-enum-{same,different}-padding/main` исполняются целыми fixtures на4: они требуют MU storage. До4 nested offset qualification PENDING, не считать её покрытой u8 raw_eq |
| 4 STORAGE | Все `maybe-uninit-*` storage/argument/return/pairing/Copy/Move/reset/transmute/typed-padding/data controls; `nested-aggregate-reset/**`; `copy-source-arguments/**`, `padded-slice-extents/**`, все `marker-hook-calls` **кроме generated-modifies-no-shadow**; marked-model пара теперь4 благодаря V420–424. marker_category unit1, argument_size unit; отложенные owner1/3 fixtures по строкам выше. `part1-composition/**`, strong contract/transfer cases — при наличии closure prerequisites5 |
| 5 CLOSURE | `closure-zst/**`, `closure-upvars/**`; `ordinary-slots/positive`, `points-to-cycles/capture-free`, `marker-hook-calls/generated-modifies-no-shadow`; delayed contract+transfer controls с closure layout: `contract-immutable-masks/**`, `transfer-qualification/**`, `private-transfer-frame/**`, `maybe-uninit-contract-{clause,frame}`, все7 `contract-modes` и все7 `root-composition` fixtures. Закрыть соответствующие owner1/4 obligations. Сохранить CC4 recursive ordinary/check Unsupported vs simple-check legal; accepted cycle boundary — не новый release blocker |
| 6 E1 | `part1-edges/{union-constant,union-variable,raw-field,dst-by-reference,dst-by-value}-*`, README; дополнительные unsized edge controls используют production guard/unit из4; оставшиеся composition/semantic edge fixtures из полной карты |
| 7 F7 | delayed_cache6/delayed_scope2 и исходные структурные regression tests из C2-S4; mapping mixed-vs-isolated и обоих порядков из `c2-s4/ci-1/` как baseline/review inputs; portable tests без старого T1b allowance |

**Проверка полного покрытия:** список U→F содержит больше shared cases, чем эта групповая таблица.
Worker15 строит ORACLE-MAP по каждому изменённому test path, в том числе удалению/изменению baseline fixtures;
каждый path и каждый прежний semantic oracle имеет owner, зависимости и конечный disposition. Unassigned → STOP.
S5 JSON suites вообще не вводить в новые branches: их нет в U, переносить только конечные expected-тесты из F.
Не трогать остальные upstream JSON/schema/#5154. Не переносить historical JSON→expected cleanup как отдельный PR без тестов.

Сохранить 8 strong oracle cases, 7 mode fixtures и 7 composition roots по S5 карте; полный список/привязки важнее этих чисел.
P2 два read checks одного чтения + outer ensures N3, postcondition-hole N3; Replace caller N2; frame/clause — свои exact failure sets.
Не принимать extra Unsupported/protocol/frame отказ вместо задуманного read/ensures. Сохранить useful SUCCESS assertions,
lawful modifies и normal-return/abort distinction. Local proof_for_contract companion в двух Replace файлах обязателен;
`--harness <caller> --exact` выбирает только caller, companion presence не означает его выполнение.
Никаких cover-summary подстановок вместо `** N of`, host/nightly/std inventories или broad substring goldens.
Promoted-only controls ранее проходили baseline: различающие M1 — D0 legal/immutable/mixed, не любой promoted test.
Nested reset F6 оба controls должны отличать baseline false SUCCESS от intended failure; hook baseline placeholder → pairing Unsupported.
Known tuple-return false positive/unsupported union fields не превращать в обещание nested aggregate support.

Docs распределить по реализованной возможности: immutable qualification/alias limits→2; raw_eq row
`docs/src/rust-feature-support/intrinsics.md`→3; storage shapes/typed/raw/moves/pairing/hook and F6 boundaries→4;
closure mask limits→5; остаток общей Scope A, contract limitations/cycle/Replace/Recursive и edge README→6.
`docs/src/rust-feature-support.md` и `docs/src/reference/experimental/contracts.md` — общие файлы, hunk ownership обязателен.
Не вставлять полное обещание Scope A до реализации; финальные файлы восстановить **точно как F**.
Никаких research URLs/run IDs/CI receipts/process docs в export, PR-текстов или новых unsupported обещаний.

## 5. Проверка каждого head — fork Quick координатором

Каждый source head и отдельный F7 получает CI-only overlay с exact parent/source SHA/tree, hashes и без изменений
compiler/runtime/tests/docs. Stock workflows удаляются только из CI overlay; frozen source/срезы их сохраняют.
Использовать принятую uninit-ci recipe (пример CI `0998b98867`, run43656920767), не переносить устаревшие JSON artifact paths.
`ubuntu-24.04`, fmt → build-dev → clippy workspace/tests `-D warnings` → targeted units/suites.
Около7 min — наблюдавшийся порядок длительности, не обещание; job cap120 min, per-test2400 s, без auto retries.
Сохранить accepted recipe `RUST_TEST_THREADS=2`, штатные checks/solver, существующие per-fixture12-bit flags;
не ставить глобальный object-bits, не выключать contract/assert/UB checks ради успеха.

Общий набор на **каждом** cumulative head:

- kani: Uninit, Quantifiers, TailCall;
- expected: весь присутствующий `uninit`, quantifier-capture, arbitrary;
- ui: quantifier-safety-checks, explicit-tail-calls;
- script-based-pre: mem-init-reinstrumentation, autoharness_explicit_tail_call;
- json-handler: весь штатный suite; никаких трёх старых Part1 JSON suites;
- relevant unit tests: active_call_tests9 начиная с1, immutable_allocations при2, argument_size при первом guard, marker_category при4,
  delayed_cache/delayed_scope при7; фильтр с 0 tests — **не** успешная проверка заявленного unit.

Дополнительно:1 — полный штатный kani `FunctionContracts` и expected `function-contract` (существующие fixme
остаются fixme), все существующие upstream uninit/delayed-UB selectors по manifest + ActiveCalls9;
не ограничиваться прежним списком12 expected smoke. Original flags/goldens, без добавления uninit флага;
это no-regression, не обещание выполнения нового contract MIR/entry path. Расширенный набор может занять дольше≈7 min,
не урезать его ради прежней оценки. На2 — masks/aliases/source qualification9;
на3 — оба raw_eq operands/extent в u8 mixed/promoted; на4 — отложенные Pat/enum/raw-eq-uninit и owner1 traversal/entry cases,
paired/false/Move/Copy/padding/F6/hook включая marked-model; на5 — весь closure/capture, generated-modifies и P1/P2/frame/clause,
закрытие оставшихся owner1 integration obligations;
6 — все E1/composition границы;7 — structural isolation units и то же cumulative Quick.
На head с полным strong-oracle набором квалифицировать S5 sensitivity mutations4/4 через --force-rerun;
не считать compile failure, timeout или ранний Unsupported обнаружением нужной мутации.
Ранее подтверждённые distinguishing baselines переиспользовать по exact unchanged fixtures/semantics;
не повторять каждый baseline без новой причины, но новый/изменённый отрицательный контроль обязан быть различающим.

CI request содержит selectors/ожидаемые counts конкретного slice и исходные argv/exits/term reasons, artifacts с always,
source before/after identities. Накопленные counts растут вместе с тестами: не требовать245 expected/76 compiler units
от раннего head и не трактовать меньший набор как полное покрытие F. Ни один уже присутствующий test не фильтруется
из-за неудачи; нет новых ignores/fixme или ослабления goldens. Недостающая prerequisite feature → STOP/dependency review.
Fork Quick здесь — регрессия/targeted qualification, **не Gate A на три платформы** и не новое all-SmallSort proof credit.

## 6. Exact-tree recomposition и перенос на будущий upstream

Источник истины — полный diff U→F, включая B1, все final tests/docs и F7. Сверить:

1. B1 сохранён как dependency, P1..P6 имеют нужных parents; F7 — отдельный reviewed commit.
2. На финальном recomposed head после применения F7 `git rev-parse HEAD^{tree}` должен равняться
   **`9829702c1aa0ecb73c860fc0ad5451757917d6cb`**, `git diff --exit-code F HEAD` пустой,
   совпадают file modes/submodules/dependency pins, source clean. Commit SHAs/авторы могут отличаться, tree — нет.
3. До применения F7 на head6 разрешены только **точно перечисленные F7 residual hunks**, не произвольные файлы:
   один `compiler_interface.rs` содержит и immutable, и F7. После F7 этот residual обязан исчезнуть.
4. SEL1/B3/CBMC/resource experiments/CI overlays/research не входят в F и не могут попасть в composition.
5. Каждый hunk U→F учтён ровно один раз в конечной композиции; временные pre-F7 adaptations явно отменены7.

При U/B1 неизменных «объяснённый diff» не автоматическая приёмка: непустой diff → STOP с exact file/hunk/hash/reason.
Исключение требует решения координатора; production/test/oracle/dependency отличия требуют новой квалификации,
семантические или platform изменения — повтор affected gates. Даже docs-only отличие не называть same tree.
При точном tree match Gate A/replay F остаются свидетельствами именно итогового дерева; intermediate PR heads
квалифицированы своими Quick, не наследуют автоматически full Gate A/replay.
Для actual upstream подачи после merge B1/new main — отдельный port/revalidation plan, не тихий rebase под старыми receipts.

## 7. Handoff и STOP

Для каждого принятого среза: `SLICE.json` (source/base/tree/parents, dependents, changed hunks/tests/docs, borrowed prerequisite),
source patch, `SOURCE-MAP`/`ORACLE-MAP` updates, `REVIEW.md`, `CI-REQUEST.md`, затем coordinator acceptance с exact run/head.
SLICE.json различает no-regression/unit results и integration qualification на другом cumulative head;
для1 (и nested layout части3) обязательны pending obligations/heads, затем exact closure receipts, без заднего числа.
Общий пакет: `INPUTS`, `FILE-HUNK-MAP`, `SEAMS`, `DEPENDENCIES`, `UPSTREAM-DRIFT` при необходимости,
`RECOMPOSE.json`/остаточный diff и `VALIDATION-SUMMARY` с NOT_RUN отдельно от принятых результатов.
Карта должна позволять reviewer проверить каждый срез без чтения исторического mega-commit ba0e5cfedf.
Локальные source commits нейтральные, одна reviewable feature на commit, fix+её tests/docs вместе;
автор Tiramisu-Cake <igkharin@gmail.com> через `git -c`; существующие frozen/B1 refs не двигать.

STOP: чужое dirty состояние; потерянный B1 pending check; новая false SUCCESS/ordinary regression; меняющаяся semantics;
неучтённый shared hunk; неразрешимая dependency принятого порядка; неполный oracle map; mismatch final tree;
потребность в local build/push/CI, не разрешённых этой подготовительной сессии. Вернуть конкретное препятствие и минимальный вариант.
Финал каждой сессии: `READY <local slice/overlay sha>` либо `STOP <reason>`, пути к map/request и явно не пройденные checks.
После принятой нарезки — отдельное задание PR-текстов/stack publication; это задание их не разрешает.
