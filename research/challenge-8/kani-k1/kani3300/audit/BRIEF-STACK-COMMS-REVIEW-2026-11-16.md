# Аудитору: внешние тексты подачи стека Kani (#3300) и вопрос организаторам — тон, порядок, «нейрослоп»

2026-11-16. Только чтение: ничего не запускать и не публиковать. Все тексты приведены ниже
дословно, так что отчёт самодостаточен. Исходные файлы (ветка `experiment/kani-k1-kani3300g0-20261111`):
[PR-тексты](https://github.com/Tiramisu-Cake/verify-rust-std/tree/experiment/kani-k1-kani3300g0-20261111/research/challenge-8/kani-k1/kani3300/c2-slices/pr-texts), [design note и сообщение #56](https://github.com/Tiramisu-Cake/verify-rust-std/tree/experiment/kani-k1-kani3300g0-20261111/research/challenge-8/kani-k1/kani3300/w0-u),
[Limitations #752](https://github.com/Tiramisu-Cake/verify-rust-std/blob/experiment/kani-k1-kani3300g0-20261111/research/challenge-8/kani-k1/kani3300/ch8-c-now/LIMITATIONS-DRAFT.md).

## Зачем

В ближайшие дни от аккаунта владельца (Tiramisu-Cake) уйдёт несколько текстов двум разным аудиториям:
мейнтейнерам Kani и организаторам/комитету verify-rust-std. Внешних взаимодействий стало много, и мы не хотим,
чтобы они выглядели как поток сгенерированного текста. Нужен взгляд со стороны на три вещи:

1. **Порядок и темп.** Что публиковать, в какой последовательности и когда.
2. **Тексты.** Убрать нейрослоп, внутренний жаргон и лишние оговорки, но сохранить честность.
3. **Сообщение организаторам** в свете конкурирующего PR #762, который вы уже смотрите.

## Контекст в двух абзацах

**Challenge 8 (SmallSort).** Наша заявка — [verify-rust-std#752](https://github.com/model-checking/verify-rust-std/pull/752).
В ней ограниченные (bounded) доказательства в Kani; комментариев и ревью пока нет. Следующий шаг по качеству —
доказать безопасность работы с неинициализированной scratch-памятью (`MaybeUninit`) через `-Z uninit-checks`. Kani
этого почти не умеет; трекер в upstream — [kani#3300](https://github.com/model-checking/kani/issues/3300). Мы
сделали в форке стек из семи PR в Kani, который это закрывает для нужных нам форм. Стек стоит поверх нашего уже
открытого [kani#5172](https://github.com/model-checking/kani/pull/5172): он открыт 14.11, ревью требуется, комментариев
ноль. Kani main с базы стека (`0aac16ef62`) не сдвинулся.

**Решение владельца, принятое утром.** Сейчас подаём только PR-01 и PR-02 как stacked PR, плюс design note в
#3300. PR-03…07 подаём позже, по одному, после пересборки поверх нового PR-02. Организаторам пишем одно
сообщение в [#56](https://github.com/model-checking/verify-rust-std/issues/56) (трекер Challenge 8), а не в #752.

## Что уже опубликовано от владельца в Kani (для сверки голоса)

- [#5172](https://github.com/model-checking/kani/pull/5172) — PR, основа стека (открыт, без ревью).
- Issues: [#5104](https://github.com/model-checking/kani/issues/5104), [#5116](https://github.com/model-checking/kani/issues/5116)
  (закрыт исправлением), [#5117](https://github.com/model-checking/kani/issues/5117), [#5072](https://github.com/model-checking/kani/issues/5072).
- Сегодня: [#5179](https://github.com/model-checking/kani/issues/5179) (loop contracts × uninit),
  [#5181](https://github.com/model-checking/kani/issues/5181) (slice `modifies` havoc × uninit) и
  [комментарий в #3762](https://github.com/model-checking/kani/issues/3762#issuecomment-6911595935). Ответов пока нет.
- Важно: мейнтейнер Kani (feliperodri) сам открыл [#5151](https://github.com/model-checking/kani/issues/5151) —
  «arrays of `MaybeUninit<T>` with non-trivial `T` are unsupported». Это ровно наша область. В черновиках на #5151
  сейчас нет ни одной ссылки.

AI-политика: в `CONTRIBUTING.md` Kani про AI ничего нет. Мы всё равно ставим строку раскрытия в каждый текст
(формулировки — в конце каждого текста ниже), без Co-Authored-By. В rust-lang мы не пишем.

## Порядок подачи, который я предложил владельцу

1. **PR-01** «Analyze selected contract bodies and detect active call cycles». Зависит от #5172, поэтому его diff
   против `main` включает коммиты #5172.
2. **PR-02** «Track initialization masks for whole immutable allocations». Идёт сразу за PR-01; в текст
   подставляется номер PR-01.
3. **Design note** — комментарий в kani#3300 со ссылками на оба PR. PR-03…07 в нём обозначены как следующие шаги.
4. **Сообщение организаторам** в verify-rust-std#56 — отдельно и последним. Предлагаю держать его до вашего
   разбора #762 (подробнее ниже).

Отдельно в очереди на вычитку лежит черновик раздела Limitations для #752 (текст E ниже).

## Что меня самого беспокоит (координатор)

Это гипотезы, не выводы. Подтвердите или опровергните.

1. **Объём и темп.** За три дня от нового контрибьютора: #5172 без ревью, два issue, комментарий, теперь ещё два
   stacked PR и длинный design note, а в перспективе ещё пять PR. Для мейнтейнеров это может выглядеть как
   AI-поток. Альтернатива — классический порядок: сначала design note в #3300 (со ссылкой на #5151), PR только
   после реакции. Либо PR-01/02 открыть как Draft.
2. **Разделы Testing перегружены.** Там SHA, номера fork-прогонов и оговорки вроде «These are fork qualification
   results, not organizer integration evidence» и «This is regression/unit evidence only». Различие «fork vs
   organizer» — наша внутренняя кухня, мейнтейнерам Kani оно ничего не говорит. К тому же их CI сам прогонит
   открытый PR.
3. **PR-02, третий абзац Testing.** Мы честно пишем, что убрали падающий fixture и финальную голову не
   перезапускали. Звучит странно. Варианты:
   - убрать абзац и положиться на upstream CI на самом PR;
   - перезапустить fork CI на финальной голове `05da1a7a8c` (один прогон, нужен GO владельца);
   - оставить коротко, одной фразой.
4. **Design note сжат до телеграфа.** Его ужимали до ≤8 KB, и местами он нечитаем: «Six cache/two scope units and
   11 invocations/18 mixed-versus-isolated comparisons…», «unwind34/34/16/8», «object-bits12». Блок с SmallSort-replay мейнтейнерам, вероятно,
   не нужен. Мне кажется, его надо переписать человеческой прозой: проблема → модель → как режем на PR →
   ограничения → вопросы. Доказательства оставить ссылками на PR.
5. **Сообщение организаторам.**
   - Первый абзац — одна длинная интерпретация.
   - Вопрос 4 смешивает практическую просьбу (bump pin Kani) с объяснением про toolchain.
   - Концовка «This requests adoption; neither the bump nor a separate safety step is reported as adopted» звучит
     как оговорка юриста.
   - Отдельно — #762. Там заявлено решение VeriFast для всех длин. В условии: «for all possible slices with
     arbitrary valid length». Мы же просим подтвердить, что интерпретации «каждая валидная длина вызова (≤16 / ≤32)»
     достаточно. Не выглядит ли это сейчас как попытка сузить условие под себя?
6. **Limitations для #752 (текст E)** в нынешнем виде публиковать нельзя. Он написан внутренним языком: N0..3,
   NOT_RUN, «proof credit», «qualified contract instances». Нужен ли такой раздел вообще и в каком виде?

## Вопросы к вам

1. **Порядок и темп.**
   - Ваш порядок для PR-01, PR-02, design note и сообщения #56.
   - Design note до PR или после?
   - Draft или ready-for-review?
   - Ждать ли первой реакции на #5172 перед тем, как ставить на него ещё два PR?
2. **По каждому тексту A–E.**
   - Маркеры нейрослопа и внутреннего жаргона, с конкретными замены «было → стало».
   - Что выкинуть.
   - Целевая длина.
3. **Testing в PR.** Сколько fork-доказательств уместно цитировать в upstream PR Kani? Что делать с абзацем PR-02
   про убранный fixture (см. п. 3 выше)?
4. **Design note.** Нужна ли новая структура? Уместен ли он вообще как комментарий в #3300, а не как отдельный
   issue или discussion? Как сослаться на #5151 и на уже опубликованные #5179 / #5181 / #3762?
5. **Сообщение #56.**
   - Публиковать сейчас или после разбора #762?
   - Одно сообщение или разделить (scope отдельно, pin отдельно)?
   - Как сформулировать вопрос о длинах, чтобы он не читался как попытка сузить условие?
6. **Limitations #752.** Публиковать ли и в каком виде (полный текст «было → стало», если да).
7. **Общий голос.** Согласуются ли новые тексты с уже опубликованными (#5172, #5179, #5181, комментарий #3762)?
   Есть ли в опубликованном что-то, что стоит поправить или дополнить?

Позиция владельца по тону (из прошлых аудитов): честно, но умеренно продающе. Сильные стороны — первыми,
ограничения — спокойно и кратко, без самоуничижения и без жирных дисклеймеров. Конкурентов не упоминать. Каждое
утверждение должно подтверждаться кодом или прогоном. Ссылки на наши внутренние research-доки во внешних текстах
недопустимы.

**Результат:** файл `STACK-COMMS-REVIEW-2026-11-16.md` рядом с этим брифом (каталог `research/challenge-8/kani-k1/kani3300/audit/` той же ветки).
- Пишите по-русски, формулировки для внешних текстов — по-английски.
- В конце — полные предлагаемые тексты A–D (и E, если считаете, что его стоит публиковать).
- В чат: 5–10 строк сводки и строка `REVIEW READY <путь>`.

Ниже, в приложениях, тексты дословно. Строка `Title:` — предлагаемый заголовок PR, в тело она не входит.

---

## Текст A — PR-01 (kani)

Голова `d82752c8bc`, родитель — голова #5172.

````text
Title: Analyze selected contract bodies and detect active call cycles

Refs #3300

Depends on #5172, which is still open. This branch is based on #5172; until that PR merges, its changes are included in this branch's diff against `main`.

With `-Z uninit-checks`, delayed analysis must use the MIR bodies selected for contract registration and discarded closures, and report call cycles without using an incomplete points-to graph. This change also initializes ordinary scalar and reference argument slots before tracked reads, without initializing their referents.

### Change

- Track the active call chain from each analysis entry point, report cycles with short diagnostics, and stop that analysis after an error instead of using an incomplete points-to graph.
- Record which registration or discarded-closure body was selected. Keep the existing call resolution, visit each call's operands once, and retain the checks collected for that call.
- Initialize ordinary scalar and reference argument slots without initializing their referents or union storage.

### Testing

This PR has no new end-to-end tests for this analysis feature on its own: those tests need the later `MaybeUninit` storage/transfer and closure-layout slices. On exact source head `d82752c8bc878398e672bffaa631ca6a28430acc` (parent `6fe484b30043b3696b5f1ccc4bea0e42891ad012`), formatting, build, Clippy, 9 ActiveCalls unit tests and 302 regression tests passed; 9 existing tests remained ignored ([run 43696666260](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260), ubuntu-24.04). This is regression/unit evidence only.

Deferred integration tests passed on cumulative head 4, `345cedfd67df679e326474385308349d609fc43d` ([run 43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495): cycles and ordinary argument slots), and cumulative head 5, `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` ([run 43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377): closure/contract cases). They did not run on this PR's head and do not establish standalone PR-01 behavior. These are fork qualification results, not organizer integration evidence.

### Limitations

This does not fully resolve #3300. Delayed analysis cycles remain unsupported; function pointers, trait objects, `stub_verified`, and `kani::recursion` do not gain shadow-transfer support. This change does not add general `MaybeUninit`, indirect-call, or recursion support.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## Текст B — PR-02 (kani)

Голова `05da1a7a8c`. Фраза «the prerequisite selected-contract-body analysis PR» будет заменена номером PR-01.

````text
Title: Track initialization masks for whole immutable allocations

Refs #3300

Depends on #5172 and the prerequisite selected-contract-body analysis PR. This branch includes their changes until they merge.

With `-Z uninit-checks`, compiler-produced immutable allocations need their initial byte state represented in the shadow model. Otherwise, a legal comparison with an initialized constant can report an uninitialized read. This change records exact masks for supported whole immutable allocations and combines compatible aliases of the same emitted storage. It also recognizes generated automatic harnesses as analysis entry points, resetting the shadow state before applying immutable allocation masks.

### Change

- Record anonymous allocation origins and bind them to emitted immutable symbols.
- Combine compatible aliases only when their extent, layout and mask agree, keeping initialized zero bytes distinct from holes; reject incompatible descriptors.
- Set the shadow bytes from those exact masks after the state is reset, leaving uninitialized bytes uninitialized and skipping empty-mask queries.
- Reset uninitialized-memory state at automatic harness entry, including harnesses with generated arguments and function contracts.
- Document which whole allocations can be handled this way and where checks remain conservative.

### Testing

On the original source head `932fb8395a58f8c86c0d702ba2cae835823b2962`, 9 registry unit tests and 308 regression tests passed, including six descriptor-coalescing tests; 9 existing tests remained ignored ([run 43701587141](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141)). This run used selected Linux test suites on ubuntu-24.04.

Qualification of the entry-reset fix reported formatting, build and Clippy success, 66 compiler unit tests passed, 56 expected uninitialized-memory tests passed (2 ignored), and 134 function-contract tests passed (4 ignored) ([run 43783429976](https://github.com/Tiramisu-Cake/kani/actions/runs/43783429976)). All six retained entry-reset regressions passed: a seeded return, a seeded function with an argument, a seeded function with a contract, an entry without a seed, a read of explicitly initialized padding, and checks disabled. On the original head, the three seeded cases failed with `immutable masks: reset is absent from this model`; the case without a seed completed as expected.

The same run reported 54 passed and 1 failed across the selected `script-based-pre` autoharness tests. The failure was an additional padding-read fixture: it expected an uninitialized-read failure, but verification succeeded with exit 0. That fixture is omitted from this candidate; uninitialized-read detection remains covered by the existing uninitialized-memory suite. The retained 24 fixture files and compiler diff are byte-identical to the tested source, including file modes. This final candidate was not rerun after removing the failing fixture; the complete suite is not claimed to have passed on it. These runs are fork qualification, not organizer integration evidence.

### Limitations

These initial masks apply only to whole immutable allocations with no relocations, a supported `Freeze` origin type and a computable layout. They describe initialization metadata only and grant no permission to write memory or access an allocation. Mutable allocations, allocations with relocations, subrange origins that do not meet these checks, and conflicting origins are not marked initialized by this step. This does not resolve all of #3300 or add general `MaybeUninit`, indirect-call, or recursion support.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## Текст C — design note, комментарий в kani#3300

Строки до `---` (заголовок «RFC draft…» и строка «Owner-only…») служебные, в комментарий не идут. Каким будет заголовок комментария, решим после вашей правки.

````text
# RFC draft: initialization tracking for MaybeUninit storage and selected MIR bodies

Owner-only [#3300](https://github.com/model-checking/kani/issues/3300) draft, 2026-11-16; not upstream acceptance.

---

## Problem

SmallSort needs `-Z uninit-checks` to preserve scratch holes across calls and analyze selected contract/closure bodies.

## Goals and non-goals

Support `MaybeUninit<T>`, flat arrays/slices of it and `MaybeUninit<[T; N]>` with computable layouts. No new alias/provenance model or #3300 completion, permissions, general validity, all-T/N, panic/unwind or sorting proof is claimed.

## Source decomposition and dependencies

Base: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` plus existing [#5172](https://github.com/model-checking/kani/pull/5172), `6fe484b30043b3696b5f1ccc4bea0e42891ad012` (unresolved-call checks).

| Slice | Scope | Source head |
|---|---|---|
| PR-01 | Selected bodies, cycles, entry slots | `d82752c8bc878398e672bffaa631ca6a28430acc` |
| PR-02 | Immutable masks, automatic-harness entry reset | `05da1a7a8ce7921d3f685d9595eab797870ca629` |
| PR-03 | Nested layouts/raw equality | `5ca51679e3f433718807a2e44add0d5abac128e7` (historical) |
| PR-04 | Storage/direct-call transfers | `345cedfd67df679e326474385308349d609fc43d` (historical) |
| PR-05 | Closure capture masks | `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` (historical) |
| PR-06 | Fixtures/documentation | `3f5242bb1539fb88196d7e503b722f0905f2b46c` (historical) |
| PR-07 | Delayed-body restoration | `8e299aa6243bc5f06a29c51e98aafa9564478220` (historical) |

PR-02 adds one reset-fix commit to `932fb8395a58f8c86c0d702ba2cae835823b2962`. PR-03–07 await rebuilding/revalidation over it; listed heads are historical. Review/merge order: #5172 → PR-01 → … → PR-07; stacked diffs include unmerged parents.

Separate `select_unpredictable` Rust-fallback source `14bc57fdb99960240c4944845a3d985c8af4dcf7` has historical PR-07 as parent; its results do not qualify the seven slices or revised PR-02.

## Proposed architecture and actual behavior

### One witness, distinct masks

The model tracks one nondeterministic object/byte witness. Initialization masks distinguish holes from initialized zeros; layout masks select payload, excluding padding. Typed transfers initialize payload; raw copies preserve full byte state, deinitialization clears the full extent, and `raw_eq` checks padding. Copy snapshots precede Move deinitialization. Layout never establishes initialization.

### Direct calls and selected bodies

Ordinary non-foreign MIR calls, excluding Kani hooks, pair signature/argument-index/return-slot transfers on normal returns. Reject unsized storage before partial transfer; retain supported conservative resets on unpaired paths.

Selected contract/discarded-closure analysis retains provenance, root-local snapshots, fallible resolution and operand checks. Cycles abort the root and discard incomplete graphs. Ordinary sized scalar/reference entry slots, not pointees/unions, are initialized. Closure masks use actual capture layouts, including empty zero-byte masks.

### Immutable origins and permissions

Seeding requires whole emitted storage, offset zero, matching extent, no relocations, supported `Freeze` origin and exact mask. Aliases require matching storage/layout/mask; conflicts are rejected. Reset precedes seeding, including automatic argument/contract harnesses; false bits survive, empty masks need no query. Other origins gain no initialization or permission.

### Delayed mutation and per-root isolation

A journal restores delayed replacements on model exit/failure, apart from regular/stub changes/provenance. Both backends guard reachability/global passes/codegen. Six cache/two scope units and 11 invocations/18 mixed-versus-isolated comparisons support tested restoration, not universal isolation or semantic equivalence.

## Alternatives and open design choices

All-true masks erase holes; all-false seeds reject constants. This retains one witness rather than per-allocation shadow memory. Indirect/recursive/Replace/loop-havoc summaries need further rules and controls.

## Evaluation and evidence

Fork runs use source-specific CI overlays; no organizer integration or independent proof credit.

PR-01 [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43696666260): build/format/Clippy, 9 cycle units, 302 regressions/9 ignores; new end-to-end analysis tests deferred. Original PR-02 [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43701587141): 9 registry units, 308 regressions/9 ignores, six descriptor cases.

Reset-fix [run 43783429976](https://github.com/Tiramisu-Cake/kani/actions/runs/43783429976), tested source `f7e89f1942fa6f671f20ec45fde98d9d736dc122`: build/format/Clippy, 66 compiler units, 56 uninit and 134 contract tests passed (2/4 ignored). Six retained reset cases passed; three seeded cases failed on old PR-02 with missing reset. Autoharness: 54 passed/1 failed (padding-read fixture unexpectedly verified). That fixture was removed; compiler/retained fixtures are byte/mode-identical. Final head was not rerun; no complete-suite pass is claimed.

Deferred analysis/layout/storage: historical PR-04 ([43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495)); closure/contracts: PR-05 ([43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377)); restoration/LLBC/regressions: PR-07 ([43723531871](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871)).

Historical seven-slice [run](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636): 33 stages per Linux x86/Arm and macOS platform. Bounded sort4 stopped at `select_unpredictable`, return unreachable.

Separate fallback [regressions](https://github.com/Tiramisu-Cake/kani/actions/runs/43744142824) 33 stages/platform; rounded time 41/40/76 minutes, RSS unknown. Bounded [replay](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000) used std `70ba5befc617627073738e26cb1466bd4fb76e41` plus test overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726`, uninit ON/value checks OFF, object-bits12, controls ON, `--no-assert-contracts`. Merge u64 len8/scratch48/src32/dst0, merge-closure u8 N9/scratch48, sort4 u64 and swap u64/backing4 reached return/all covers (unwind34/34/16/8). Raw sort4 passed initialized; source[1] hole retained exactly the intended uninitialized-u64-read failure, exit1/return covers (unwind16). Replay timing/RSS unknown; no sorting theorem.

## Independent sorting contracts and integration

Stock-upstream sorting uses primitive/default ordering, uninit/value OFF, checked trait methods, thresholds16/32 and proposed symbolic lengths/six-body coverage. [#752](https://github.com/model-checking/verify-rust-std/pull/752) remains separate; its older std head needs upstream toolchain updates before using `0aac`. Arbitrary-bool closure safety and functional results require compatible sources/targets/comparators/modes/flags before combination.

## Limitations

Unsupported here: struct-held arrays of `MaybeUninit` (`PolymorphicIter`), `array_assume_init` transmute; other boundaries: nested by-value union aggregates, function-pointer/vtable calls, Replace/recursion shadow transfers, delayed cycles and unmodeled intrinsics. Loop-havoc/shadow remains open; see [#5179](https://github.com/model-checking/kani/issues/5179), [#5181](https://github.com/model-checking/kani/issues/5181) and the separate [valid-value copy limitation](https://github.com/model-checking/kani/issues/3762#issuecomment-6911595935). #5104, general validity and organizer time/RSS fit remain open.

## Questions for maintainers

1. Is this model and review decomposition acceptable?
2. Which body/origin/isolation controls are missing?
3. What Replace/recursion or loop-havoc shadow summary could preserve every hole witness?
4. How should fixes/integration accompany stock-upstream sorting?

*Disclosure: this note was prepared with the help of AI assistants.*
````

## Текст D — сообщение организаторам, verify-rust-std#56

Строки до `---` служебные.

````text
# Combined scope and integration question

Destination: [verify-rust-std #56](https://github.com/model-checking/verify-rust-std/issues/56). Owner-only draft; post once here, not also in #752.

---

Following the [answer on primitive types and default ordering](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906) and the [challenge requirements](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/challenges/0008-smallsort.md), we read item 2 as checking actual trait-method contracts for sortedness and multiset preservation over every valid caller length: fallback up to 16, general/network up to 32, using primitive values with their usual ordering. Our proposed coverage strategy uses symbolic lengths and accounts for all six implementation bodies, including specialization and forwarding routes. Those are our coverage choices, not a claim that a particular harness count was prescribed. Please correct this interpretation if needed.

Could you clarify the remaining scope and integration points together?

1. Does item 1 additionally require insertion-helper safety for valid lengths and offsets beyond all SmallSort caller thresholds?
2. Would checked primitive instances plus `Cell<u8>` and a non-Copy wrapper as route representatives, with six-body accounting, meet the intended type coverage? Which additional instances would be required?
3. Which total time, worst-shard time, peak RSS and concurrency budget should we target? May selected harnesses run in a separate `-Z uninit-checks` safety step? Item 2's proposed sorting work has uninit/value checks OFF; that proposed safety step is separate, and any later `-Z valid-value-checks` step would need its own qualification.
4. Upstream `main` currently pins Kani `c5e65fdfc3e15ec32293f2a4c07509aebec033c9` ([configuration at the checked revision](https://github.com/model-checking/verify-rust-std/blob/6079edcda31accaf396b883f3f38e2581d0710d7/tool_config/kani-version.toml)). Could it be bumped to **clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`**, which contains the [#4908](https://github.com/model-checking/kani/issues/4908) and [#5116](https://github.com/model-checking/kani/issues/5116) fixes, independently of the pending [initialization series](https://github.com/model-checking/kani/issues/3300)? The current [#752](https://github.com/model-checking/verify-rust-std/pull/752) head `872d5a43380752786415bc00d2a12ce0e930cb37` still uses nightly-2026-10-22 and predates merged [#745](https://github.com/model-checking/verify-rust-std/pull/745), which updates to nightly-2026-10-23. A pin-only change there fails to build with `0aac`; merging upstream `main` is required first. What adoption route should we follow? This requests adoption; neither the bump nor a separate safety step is reported as adopted.

*Disclosure: this message was prepared with the help of AI assistants.*
````

## Текст E — черновик Limitations для #752 (verify-rust-std)

Кандидат в публикацию — только цитата ниже. Остальное в исходном файле — внутренние заметки.

````text
The bounded helper contract proofs check the following write sets on the named
element, comparator, length, and allocation domains: the two selected elements
for swap_if_less, the inclusive begin..tail range for insert_tail, the input
slice for insertion_sort_shift_left, and the destination ranges for sort4_stable
and bidirectional_merge. The latter two contracts require readable sources,
writable destinations, and disjoint source/destination spans. Within these
qualified contract instances, source memory is outside the destination write
set. Verified-summary consumers are restricted to their matching proved domains;
a safety-only merge summary does not guarantee destination initialization.

These write-set and disjointness results do not provide a temporal aliasing or
immutable-byte permission model. In particular, a write within an allowed outer
input or scratch frame may still violate a live shared reference passed to a
comparator. Local ManuallyDrop values, gap guards, subsequent reuse of storage,
and unwind behavior require separate reasoning; the current results do not
establish complete borrow coverage. Dedicated transient write-then-restore
controls have now been run separately on the experimental pins described below;
those observations do not add proof credit to this submitted production pin.

The helper write sets do not describe arbitrary FnMut effects through captured
references, raw pointers, or global state. Their contract proofs use the specified
read-only comparator instances. Legal callbacks that update disjoint external
state or permitted UnsafeCell storage require an explicit additional footprint;
they are not ruled out by Rust. Listing the closure object alone does not specify
the transitive footprint of its captures. Existing mutating Cell route checks
cover selected interior-mutability cases, not general aliasing enforcement.

On this submitted tool pin, the three generic SmallSort trait entry families
have no direct contracts. Concrete N2 forwarding-wrapper proofs execute real
trait entries but do not establish generic trait contracts. A separate S1 source
candidate at std 75a4d1ea6eb60c63c27c1b18e662740d93bafb08 adds contracts to all
six implementation bodies on upstream Kani 0aac16ef62da9e9d5645782d458593e5d78143ba,
which includes the fixes associated with #4908 and #5116. Its planned N0..3
mechanism proofs are NOT_RUN; its frames are scoped to the named KeyLess ZST
comparator instances. It supplies no new proof credit for this submission.
````

---

# Приложение: черновики PR-03…07 (будут подаваться позже, по одному)

Для оценки общего стиля серии. Головы исторические: после пересборки поверх нового PR-02 тексты обновятся. `#<PR-NN>` — плейсхолдеры номеров.

## PR-03

````text
Title: Check raw equality byte extents and preserve nested layout offsets

Refs #3300

Depends on #5172, `#<PR-01>`, and `#<PR-02>`. This branch is based on `#<PR-02>`; until these PRs merge, their changes are included in this branch's diff against `main`.

With `-Z uninit-checks`, `raw_eq` needs checks for the full byte extent of both reference operands, including padding. Layout-mask calculation must also preserve offsets through `Pat` and enum fields so data and padding are attributed to the correct bytes.

### Change

- Check the full extent of both `raw_eq` reference operands, including padding, using the existing byte-read checks.
- Correct nested `Pat` and enum layout offset composition.
- Update the intrinsic support documentation and add an empty-extent regression test.

### Testing

On commit `5ca51679e3f433718807a2e44add0d5abac128e7`, 309 regression tests passed and 9 existing tests remained ignored ([run 43706759714](https://github.com/Tiramisu-Cake/kani/actions/runs/43706759714)). This commit was checked for regressions, not end-to-end behavior of nonempty raw equality or nested layouts. Those tests need the `MaybeUninit` storage work in `#<PR-04>` and passed on that later commit ([run 43710024495](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495)).

### Limitations

Padding read by `raw_eq` must itself be initialized. The preceding PR's whole-allocation limits still apply when setting the initial state of immutable allocations. This does not resolve #3300 or add general nested `MaybeUninit` aggregate, indirect-call, or recursive shadow-transfer support.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## PR-04

````text
Title: Track MaybeUninit storage across copies and direct calls

Refs #3300

Depends on `#<PR-03>` and, through it, #5172. Until those changes merge, the diff against `main` includes the earlier commits in the series.

`MaybeUninit` storage can contain initialized payload bytes and uninitialized padding. The experimental `-Z uninit-checks` model needs to preserve that distinction through copies, moves, and supported direct calls. Marker-dispatched backend hooks bypass the MIR return store and previously reached an internal assertion; they now produce a diagnostic that explains this transfer is unsupported.

### Change

- Pair snapshots of live caller storage with loads at callee entry, then transfer state separately on normal return. This preserves known-uninitialized bytes across Copy and Move.
- Preserve raw byte state through raw copies. Typed transfers preserve payload bytes using the actual slot stride and discard padding state.
- Conservatively reset nested by-value aggregate destinations and Move sources; Copy sources remain intact. This may cause false positives and does not transfer fields recursively.
- Add storage and padding tests, checks that caller and callee operations are paired, tests for nested resets, and checks that supported models still work while unsupported hook transfers are rejected.

### Testing

[Fork CI on `345cedfd67`](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495) passed formatting, build, Clippy, and selected Linux regression suites: 404 passed, 9 pre-existing ignores, plus 20 units. Tests cover paired transfers of initialized and uninitialized data, Copy/Move, padding, nested resets, and hook rejection. They also exercise cycle, ordinary argument-slot, and raw-equality/layout cases from `#<PR-01>`/`#<PR-03>` that needed this storage support. Captured contract and generated-modifies tests passed later in [run 43715788377](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377), not on this commit.

### Limitations

Support covers a `MaybeUninit<T>` slot, `[MaybeUninit<T>; N]`, `[MaybeUninit<T>]`, and `MaybeUninit<[T; N]>` when masks can be computed. State transfer under `stub_verified` or `kani::recursion`, indirect calls, nested by-value union/`MaybeUninit` aggregates, analysis cycles, and unmodeled intrinsics remain limitations. In particular, `select_unpredictable` still blocks verification of the whole SmallSort module.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## PR-05

````text
Title: Analyze closure captures using their concrete layout

Refs #3300

Depends on `#<PR-04>` and, through it, #5172. Until those changes merge, this branch includes the earlier commits in the series. The source tested here is `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`.

Legitimate closure capture and contract cases were stopping because the analysis did not have a supported layout. It needs each closure's concrete environment layout to locate its upvars and padding, including when the environment has zero size, so these cases can proceed through layout checking.

### Change

- Read monomorphized upvar types and offsets from the closure's concrete compiler layout, preserving padding and initialized payload boundaries.
- Handle zero-sized closure environments and add 47 test cases for closure layout and the remaining end-to-end checks, including captured-field contract and generated `modifies` cases.
- Add the remaining end-to-end tests for analysis and storage while keeping conservative resets at unsupported nested aggregate boundaries.

### Testing

[Fork CI on `96f5d5dc8d`](https://github.com/Tiramisu-Cake/kani/actions/runs/43715788377) passed formatting, development build, Clippy, and selected Linux regression suites: 451 passed and 9 pre-existing ignores. Four deliberately changed versions of tests were run; the test runner detected three. The fourth completed and produced the expected mismatch, confirmed by manual review after local-variable renumbering confused the runner's name check. The runner did not detect it automatically. These are not the complete three-platform checks.

### Limitations

Closure support uses compiler-reported sized layouts and the existing computable payload masks; unsupported union/`UnsafeCell` capture layouts remain unsupported. State transfer under `stub_verified` or `kani::recursion`, indirect calls, nested by-value union/`MaybeUninit` aggregates, analysis cycles, and unmodeled intrinsics remain limitations. `select_unpredictable` still blocks verification of the whole SmallSort module.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## PR-06

````text
Title: Cover remaining initialization edges and document support boundaries

Refs #3300

Depends on `#<PR-05>` and, through it, #5172. Until those changes merge, this branch includes the earlier commits in the series. The source tested here is `3f5242bb1539fb88196d7e503b722f0905f2b46c`.

The remaining supported cases need regression tests, and the documentation must explain the model's conservative boundaries.

### Change

- Add 11 test cases for edge conditions: union constants, raw projected-field neighbors and padding, by-reference DST cases, and by-value unsized transfers explicitly rejected as unsupported.
- Complete the contract and Rust feature-support documentation updates.
- Make no production-code changes; this change only adds tests and documentation.

### Testing

[Fork CI on `3f5242bb15`](https://github.com/Tiramisu-Cake/kani/actions/runs/43720042056) passed formatting, development build, Clippy, and selected Linux regression suites: 462 passed and 9 pre-existing ignores. The expected-output checks caught all four deliberate changes to the tests. The three-platform results cover the complete series including `#<PR-07>`, not this commit.

### Limitations

Supported cases remain `MaybeUninit<T>` slots, flat `[MaybeUninit<T>; N]` and `[MaybeUninit<T>]` storage, `MaybeUninit<[T; N]>`, computable masks, and supported direct MIR calls. State transfer under `stub_verified` or `kani::recursion`, indirect calls, nested by-value union/`MaybeUninit` aggregates, analysis cycles, and unmodeled intrinsics remain unsupported or are handled conservatively as documented. `select_unpredictable` still blocks verification of the whole SmallSort module.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

## PR-07

````text
Title: Keep delayed MIR instrumentation local to each model

Refs #3300

Depends on `#<PR-06>` and, through it, #5172. Until those changes merge, the diff against `main` includes the earlier commits in the series.

Delayed uninitialized-memory analysis rewrites cached MIR bodies. When another harness reuses one of those bodies, it can inherit checks inserted for the previous harness. As a result, the generated checks can depend on which harness was compiled first.

### Change

- Record bodies changed by the delayed pass and restore their previous cached state when the model's code-generation scope ends, including on error exits.
- Keep ordinary and stub transformations intact; restore only changes made by the delayed pass.
- Apply this scope at both CPROVER and LLBC code-generation boundaries.

### Testing

[Fork CI on `8e299aa624`](https://github.com/Tiramisu-Cake/kani/actions/runs/43723531871) passed formatting, build, Clippy, the LLBC build, compiler units, and selected regression suites. Six cache tests and two scope tests passed. Eleven completed compiler invocations produced 18 comparisons: the harnesses had exactly the same checks when compiled together as when compiled separately, including the expected read failures and cycle diagnostics. The expected-output checks caught all four deliberate changes to the tests.

The final tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb` is identical to the source tested at `ad499e41dd`: the full `scripts/kani-regression.sh` [passed on ubuntu-24.04, ubuntu-24.04-arm and macos-15](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636). On that same tree, SmallSort tests at the selected sizes with closure comparators [passed two merge cases](https://github.com/Tiramisu-Cake/kani/actions/runs/43683557088) and reported only the expected `select_unpredictable` failure in sort4. These runs tested the final tree, not the earlier commits in the series.

### Limitations

This keeps instrumentation local; it does not expand the initialization model. Indirect calls, nested by-value union/`MaybeUninit` aggregates, state transfer under `stub_verified` or `kani::recursion`, analysis call cycles, and unmodeled intrinsics remain limitations. The SmallSort test run does not establish support for the whole SmallSort module.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````
