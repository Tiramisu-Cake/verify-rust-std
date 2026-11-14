# KANI3300 C2 — принятый план после аудита R4

2026-11-14. Это верификация корректности, не security-работа. Только план/задания; исполнения этим файлом нет.
Владелец принял все4 решения R4 §5: scope A по ответу1, Gate B′, C2+полный Gate A на3 платформах,
сокращение наших JSON suites до expected-файлов. Не возвращаться к выбору A/B и не включать SEL1 в Part1 молча.

## Фиксированные входы и исправления учёта

- R4: `AUDIT-REPORT-KANI3300-PART1-R4-RU.md` @`f8c3266934`.
- Новые evidence @`5b44e9e9be`: gateb-run4/DIAGNOSTICS.md и gatea-c1b/{receipt,runtime-identities}.json.
  Receipt содержит **33** стадии, все EXIT_ZERO, script_exit0, problems[], статус COMPLETE_EXIT_ZERO_REQUIRES_REVIEW.
  Число29 было ошибкой прежней сводки; historical brief не переписывать, в новых status использовать33.
- C1b `3f2c12f46e9e32899e8d84e89c65cb6483ba685a`, tree `e629978d8f0746bddf896d58a156bad2c59f14ce`.
- Зафиксированный upstream U `0aac16ef62da9e9d5645782d458593e5d78143ba`, на13 коммитов позже старойbf9c58e662.
- Актуальный B1 dependency `6fe484b30043b3696b5f1ccc4bea0e42891ad012` поверх U, read-only `/root/kani-fix-b1-upstream`;
  по хронологии B1 подан отдельно как kani#5172. Его ветку/PR не менять; не выдавать этот commit за уже merged upstream.
  Новое upstream main/B1 после выдачи требует явного обновления input pin, не плавающий rebase во время стадий.

## Порядок, владельцы и зависимости

Одна стадия на сессию. Worker14 владеет C2 production integration. Worker15 сначала Gate B′ на C1,
затем отдельный SEL1 branch параллельно дальнейшим стадиям C2. Исходники — раздельные клоны, общие refs не двигать.

| Стадия | Содержание | Вход / критерий передачи |
|---|---|---|
| B′, worker15 | TASK-KANI3300-GATEB-PRIME.md:≤3 ON строки, closure comparators, tool C1 неизменен | До SEL1; результат каждой строки, не blanket PASS |
| C2-S1, worker14 | Перенос accepted C1b delta на U+B1; сохранить #5115/#5152/#5093, без F5–F8 ремонта | Параллельно B′; exact port SHA/tree, conflict/semantic map и targeted CI request |
| C2-S2 | F5 immutable descriptor coalescing + controls | Принятый S1, bounded fix без новой admission модели |
| C2-S3 | F6 conservative reset nested aggregate destination/Move source +2 negatives | Принятый S2; никаких новых blanket Unsupported/recursive transfer support |
| C2-S4 | F7 restore delayed-mutated bodies после каждого harness, не accumulated shared cache | Принятый S3; structural isolation, exact singleton/shared checks; allowlist больше не нужен |
| C2-S5 | Заменить только3 Part1 JSON suites portable expected-файлами | После S4, чтобы не переносить T1b allowance; сохранить semantic-oracle map |
| C2-S6 | Missing controls, docs/scope и экспортная гигиена; freeze C2 | Всё выше интегрировано/reviewed, отсутствие внутренних IDs/overlays, targeted qualification |
| C2-GATE | Полный scripts/kani-regression.sh на3 платформах одной final head | Linux ubuntu-24.04, ubuntu-24.04-arm, macos-15; exact hosts/pins в receipts |
| Upstream package | Нарезка reviewable PR по R4 ответ14, начиная с B1 | После gate; публикации только владелец |

Для S2–S6 нужны отдельные задания/выдачи после accepted handoff предыдущей стадии, не автоматический бесконечный task.
Gate B′ и S1 не зависят друг от друга. SEL1 не выдаётся **до завершения и review Gate B′**; его база — принятый C2-S1,
не ожидание всего C2 freeze. Так SEL1 может идти параллельно S2–S6 в отдельном clone, сохраняя A как выпускной scope C2.
Shared semantic areas (visitor/points-to) явно передаются между владельцами; ни одна линия не cherry-pick'ит незавершённую другую.
При интеграции SEL1 на готовый C2 потребуется отдельный reviewed port и новые gates, не перенос receipts S1.

## Договор каждой стадии

**S1/F4.** Parent U+B1, перенос остальных C1b changes с conflict map. AtomicStore получает upstream setter после store
и сохранённый check только nonvolatile; source-body access через checked_body, включая override selection.
Ни bodyless/tail-call panic, ни потеря B1 pending checks не должны вернуться. Новые upstream JSON tests/#5154 и validator сохранить.
S1 не чинит F5–F7 и не меняет payload/runtime semantics ради прохождения старого inventory.

**S2/F5.** Один emitted immutable symbol может иметь несколько AllocId keys с разной origin qualification.
Сверить фактические bytes/mask/extent/mutability/relocations; при совпадающем immutable объекте объединить qualification
как «достаточен один корректный qualifying key», не устраивать fatal из-за одного неqualifying alias.
Не смешивать разные masks/extent/symbol identities и не делать unqualified mutable/relocated объект initialized.
Контроли: minimal direct &5 + relocation alias из R4, reversed origin discovery, Some(0)/None, genuine inconsistent descriptors.

**S3/F6.** Для transfer-boundary type с UnionAsField полный destination extent сбрасывается false на normal return,
а actual Move-источник — после необходимых snapshots и до утраты его живого адреса. Copy source не сбрасывать.
Переиспользовать for_deinit/SetRef(false), не data mask, не bless. Existing whole-value assignment Unsupported сохраняется.
Контроли через пополевой/custom-MIR construction: reuse initialized destination→hole return и moved-from nested slot read.
Оба не должны дать SUCCESS; supported top-level legal/reinit/false и ordinary scalar/ref pathways остаются прежними.
Docs «may miss reads» сужать только после двух reached negatives и review полноты обоих путей, не по одному false-positive тесту.

**S4/F7.** Снять accumulation ровно delayed-pass mutations: до обработки harness сохранить нужные pre-delayed bodies,
после codegen вернуть их в transformer cache на всех выходах. Сохранить regular/stub-pass transforms и override provenance.
Не подменять это произвольным cache.clear/fresh-transformer refactor без проверки reachability/prewarm и mode configs.
Mixed unit использует тот же общий callee, cycle/legal companions, source order/selector permutations; root model должен
быть независимым по построению. Expected per-root properties isolation/shared равны, исчезновение checks не допускается.
Пока S4 не принят, любой временный внутренний T1b oracle может разрешать только добавление checks, не их потерю.
В экспорт C2 такой allowlist/ORDER_UNCONTROLLED acceptance не переносить; complete inventories можно оставить в research.

**S5/F2.** Из export удалить только `uninit-contract-oracles`, `uninit-contract-mode-boundaries`,
`uninit-part1-composition` и перенести нужные Rust inputs/expected. Остальные upstream json-handler/schema/validator не трогать.
Один harness на expected-file. Сохранять exact N failures через summary `** N of`, intended descriptions/Failed Checks,
useful own assertions со статусом SUCCESS и итоговый verdict; negative файл не содержит cover-summary, неоднозначной с этим N.
Не закреплять host triple, дату toolchain, строки std и полный inventory. P2 два instrumentation checks одного read — не две UB.
Сохранить8 strong semantic cases, legal mode companions и точный cycle boundary; лишний Unsupported/frame failure не совпадает с oracle.
Source inputs/goldens обновляются по смыслу/review, не как любой новый snapshot FAILED. Full JSON comparison остаётся внутренним research,
его потеря — сознательное изменение тестовой формы, не новая претензия на доказанную isolation.

**S6/F9/F10 и недостающие контроли.** General uninit limits — в rust-feature-support, контрактные — в contracts;
обновить raw_eq stale «cannot detect» строку с точной квалификацией. Включить принятую ниже scope формулировку R4.
Убрать run IDs, coordinator/process/binding_evidence лексику, research URLs, handoff docs и CI overlays из export.
Контроли R4 ответ6: backend-hook call с shadow argument/return (protocol failure), один Copy-source в2 args с hole,
Fn-trait fn-item без shadow и с shadow (отдельно layout/protocol/indirect), padded stride partial extent по ссылке/raw slice,
плюс S2/S3/S4 pairs. Fn-item plain не объявлять заранее Unsupported: run4 различает layout FnDef в PFC и реальный fn-pointer.
F11 marker invariant можно оформить отдельно; он не требует старого effect-framework и не является зависимостью C2 по R4.

## Scope, freeze и финальные gates

Scope A для PR/docs — принятый текст R4 ответа1:

> Extends the experimental `-Z uninit-checks` instrumentation to `MaybeUninit` storage: a single slot, `[MaybeUninit<T>; N]`, `[MaybeUninit<T>]`, and a `MaybeUninit<[T; N]>` payload, for element types whose data mask Kani can compute. Initialization state is tracked through raw copies, typed moves (payload bytes only), and direct calls to functions with MIR bodies (arguments and return value). Whole immutable promoted constants and named statics start with their exact byte masks.
>
> Not supported — reported as unsupported or documented: intrinsics without an initialization model, including `select_unpredictable` (and therefore `core::hint::select_unpredictable` and its callers); calls through function pointers and trait objects; shadow transfer under `stub_verified` and `kani::recursion`; by-value aggregates with nested `MaybeUninit` or union fields; call cycles in the delayed-UB analysis.
>
> This change does not make `core::slice::sort::shared::smallsort` verifiable with `-Z uninit-checks`.

Успешный B′ merge не превращает её в утверждение о всём SmallSort или production fn-pointer profile.
S2–S4 исправляют дефекты в принятом домене/границе, не добавляют SEL1/indirect calls/полную compound модель.

Freeze после всех source/test/docs changes. Full Gate A запускает координатор на одном exact export SHA/tree на3 named runners,
со штатными deps/pins, всеми suites и trailing stages; не только Uninit Quick и не старые29 stages. Схему33 сверить с actual script.
Не ставить глобально object-bits12/skip checks; heavy fixtures используют собственный12-bit флаг. Без удаления selectors/новых ignores.
Сохранить per-platform receipts/exits/counts, host/tool/dependency identities, failures и NOT_RUN после infrastructure stop.
Неподдержанная платформа/нет runner — NOT_RUN, не silent подмена другим host. Старый gate C1b не квалифицирует новый C2.
Любой source delta после freeze требует новой qualification затронутых controls и final gate на окончательной голове.
Изменённое upstream main также не протаскивать под уже принятые receipts.

Нарезка после gate: B1 → coherent S3/CC analysis → M1/E2+F5 → layout/raw_eq → storage/protocol+F6 → closure layout → E1;
F7 и SEL1 отдельными reviewable commits/PR по R4. С учётом реальных dependencies не подавать промежуточный S3 без его CC fixes.
Если cherry-pick slices меняет дерево или депы — не утверждать, что каждый промежуточный PR уже прошёл gate C2 без своей проверки.
После SEL1 — отдельный candidate, Gate A и SmallSort replay заново; fn-pointer scope не снимается, closure companions помечаются честно.
Во всех будущих PR: `*Disclosure: this change and description were prepared with the help of AI assistants.*`
Публикаций этот план не разрешает. Новые результаты NOT_RUN; текущая стадия — подготовка четырёх файлов без commit/push/CI.
