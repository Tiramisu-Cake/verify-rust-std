# Challenge 8, пункт 1: оставшиеся обязательства после C2 и SEL1

2026-11-15. План для решения владельца, без выдачи заданий, сборок, CI или публикаций.
Это верификация корректности, не security-работа. Расчёт ресурсов: **fork CI, Cloud $0**.
Оценки ниже — человеко-дни разработки и проверки, без ожидания upstream-review; это не обещание сроков.

## 1. Что считается решением

[Условие Challenge 8](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0008-smallsort.md)
требует отсутствия UB у **семи targets**: трёх trait-реализаций `small_sort`, `swap_if_less`,
`insertion_sort_shift_left`, `sort4_stable`, `has_efficient_in_place_swap`.
Кроме source SAFETY obligations, обязательны dangling/misaligned access, uninitialized reads,
mutation of immutable bytes и producing invalid values. Исключений для последних трёх пунктов в условии нет.
Нынешний честный Limitations объясняет незавершённость, но не отменяет этих требований.

Закрытие A–D также не снимает сквозные ограничения proof: типы/длины, callback frame и panic/unwind.
Kani на этих pins не поддерживает stack unwinding, а SmallSort использует CopyOnDrop/другие guards
для восстановления состояния при панике callback. Abort-only проверка или panic stub не доказывает эту ветвь;
понадобится отдельный проверенный аргумент/инструмент, либо явно согласованный более узкий результат.
Это остаток safety-доказательства, а не требование добавить sorting correctness в нынешний план.

Требование действует для всех допустимых длин, а не только текущих harness-доменов.
`insertion_sort_shift_left` не ограничен нашими N≤20. Пороги диспетчеризации 16/32 сами по себе
не доказывают полноту: нужен проверенный разбор ветвей, действительных preconditions и abort paths.
Для generic `T` конечный набор u8/u64/Cell/tagged types тоже не является автоматически доказательством.
Для unsafe helpers допустимы их реальные safety preconditions; дополнительные ограничения proof-модели
на тип, длину, чистоту callback или initialized scratch нельзя молча выдавать за полное условие.

Достаточное сведение может заменить расширение инструмента, **если само сведение проверяется автоматически**
и связано с исходным Rust target. Одного source review, host replay или closure companion недостаточно.
По [общим правилам](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/general-rules.md)
решение автоматизировано, работает в CI, использует одобренные инструменты и не меняет runtime-логику std.
Новые Kani PR могут быть стеком; итоговая solution для challenge — один PR. Acceptance остаётся за организаторами.

## 2. Точная исходная точка и предел доказательств

- C2: `8e299aa6243bc5f06a29c51e98aafa9564478220`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
  Gate A **43665002636**: полный regression на трёх платформах; это проверка регрессий инструмента.
  Gate B′ **43683557088**: две bounded merge SUCCESS, sort4 — единственная граница select.
- SEL1 поверх этого C2: `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`.
  [Quick 43740679160](kani3300/sel1-c2/quick/ci-43740679160/ACCEPTANCE.md): 29 select controls,
  прежние suites, mutations и mixed-root isolation прошли. Новый Gate A/replay не считать завершёнными по этому Quick.
  Старый SEL1 replay 43611601987 относится к `ec85b782a1`, не квалифицирует новую голову.
- C2 поддерживает выбранные MU/flat storage, raw-copy shadow, typed payload moves, direct MIR-body calls,
  exact masks для квалифицированных immutable allocations и per-harness изоляцию delayed instrumentation.
  SEL1 добавляет один проверяемый fallback `select_unpredictable`. Это существенная основа для A.
- Ни C2, ни SEL1 не добавляет полной validity или immutable-byte модели.
  В прежнем SmallSort replay valid-value был **OFF**. Initialization mask и Rust value validity различны;
  initialization seeding для immutable-константы не запрещает запись в неё.

Основные проверенные source anchors на SEL1:
[feature/support boundary](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/docs/src/rust-feature-support.md#uninitialized-memory),
[contract modes](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/docs/src/reference/experimental/contracts.md#limitations),
[points-to/resolver](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs),
[layout masks](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs),
[transfer instrumentation](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs).
Issue states ниже прочитаны в официальном GitHub; состояние OPEN/CLOSED не заменяет проверку на наших pins.

## 3. A — uninit: довести механизм до реальных маршрутов SmallSort

### A1. Сначала использовать то, что уже реализовано

Цель — actual bodies всех targets с uninit ON, а не ещё один isolated intrinsic microbenchmark.
Инвентарь строить по pinned std, точным roots, MIR/выбранным Check/Original/Replace bodies и actual flags.
Исходные ориентиры: [root/effect map](kani3300/final-gate/REPLAY-ROOT-MAP.md),
[C2 replay](kani3300/c2-gateb/RESULT.md), [SEL1 replay-пакет](kani3300/sel1-c2/replay/ROW-ORACLES.md),
`library/core/src/slice/sort/shared/smallsort/{verify.rs,verify/network.rs,verify/merge.rs}`.

| Маршрут | Первый полезный шаг | Что ещё нужно для пункта 1 |
|---|---|---|
| swap/sort4/реальный merge с direct closure | Закончить SEL1-C2 Gate A + шесть уже заданных replay строк | Расширить domains/types; этот gate не покрывает весь модуль |
| Networks, включая ветвь с merge | Ordinary actual-body roots с closure; сначала один короткий и один проходящий через merge случай | Все reachable branches/length domains, scratch initialization, arbitrary comparator outcomes, соответствие trait dispatch |
| Insertion/insert_tail | Начать с имеющихся len2/3 и tail controls, затем loop invariant initialized prefix/hole | Доказательство произвольного допустимого len/offset, Move/repair/Drop и всех итераций; unwind20 не заменяет индукцию |
| Stable/general | Обе реальные подложки scratch, частично initialized prefix, sort4/sort8→insert→merge | Сквозное сохранение initializedness до каждого typed read и корректность copy-back/guard paths |
| Три small_sort dispatcher | Отдельные Copy+Freeze, Freeze !Copy, !Freeze и размерные ветви, включая большие T | Обоснование полноты specialization/type/length-разбиения, ZST и нетривиальных layout; не только u64 route |
| has_efficient_in_place_swap | Маленькая отдельная проверка size-based predicate и использования результата | Связать типовые/размерные классы с реальной диспетчеризацией; predicate не доказывает безопасность swap |

Начальная матрица: **2–4 дня**. Квалификация нескольких новых bounded roots: ещё **3–7 дней**,
если не найден новый blocker. Это высокая практическая ценность и дешёвый способ выбрать нужные tool patches,
но не оценка стоимости полного all-length/all-T доказательства.
Негативы: hole в реально читаемом source, destination до заполнения, dropped/moved-from slot, untouched tail.
Требовать конкретный отказ операции и reached useful checks; ранний Unsupported/requires не заменяет такой негатив.

### A2. Function-pointer calls: сначала закрытый production profile, затем обобщение

`InitialTargetVisitor::try_resolve_instance` принимает FnDef; FnPtr/vtable остаются границей.
У SEL1 нет общей модели indirect calls. Важный ближайший target — исходный `merge_profile<P>`/`P::CMP`.
Он находится в нашем `verify/merge/profiles.rs`: это verification wrapper над реальным `bidirectional_merge`,
а не отдельная runtime-функция std. Его доказательство полезно, но не заменяет entry-point SmallSort.

Рекомендую первый upstream-кандидат для **полного конечного множества direct function targets**:

1. Проследить источник FnPtr, copies/joins и reachable monomorphizations, включая вызов из contract clauses.
   Доказать полноту target set; неизвестный/foreign/bodyless/unsupported target остаётся явным отказом.
2. Согласовать target set с реальным backend dispatch; shadow args/return должны следовать тому же выбранному callee.
   Сохранить снимки до Move, false bits, typed padding masks, aliases и normal-return-only setters.
3. Начать с одной конкретной `P::CMP`, затем двух различающихся targets и их joins; не считать один const case общей поддержкой.
4. Квалифицировать actual profile, а не closure-копию: legal/hole, payload read, return/out-pointer,
   wrong target, unknown target, caller order, ordinary/PFC companions. Не применять сужающий vtable flag без доказательства полноты.

Оценка: **4–7 стадий, примерно 10–20 дней** для reviewable finite-target проекта с регрессиями,
больше для общего indirect-call analysis. Риск высокий: неполный target set даёт false SUCCESS.
Ценность высокая для имеющихся profile proofs; для произвольного F это лишь первая ступень.

**Вариант сведения.** Проверить, что wrapper с FnPtr и closure companion имеют одинаковые transitions:
тот же comparator body, результаты, side effects, pointer aliases, panic/return behavior и byte-level writes,
при тех же preconditions, типе и геометрии. Связать это с реально переданным `P::CMP` и actual helper.
Address equality comparator guard сам по себе не является доказательством эквивалентности тел.
Замена FnPtr на closure в test-only companion без проверяемого relation даёт только companion evidence.
Сведение можно механизировать для закрытого набора P; произвольные пользовательские FnMut оно не покрывает.
Первый конкретный lemma/pilot — **2–5 дней**; общий theorem существенно дороже. Выбор делать после target-set spike.

### A3. Trait objects, recursion и verified stubs — три отдельных проекта

- **Trait objects:** нужны полные vtable targets и динамические layout/extent для pointee, не просто FnPtr signature.
  Текущий `PointeeLayout::TraitObject` сознательно отказывает. Для заданного конечного набора impl:
  **3–5 стадий, 10–20 дней**, риск полноты/metadata высокий. Приоритет ниже FnPtr: начать лишь если реальный target
  использует этот путь; проверка concrete F не распространяется на все trait-object comparator values.
- **Обычная рекурсия анализа:** F7 устранил меж-harness накопление, CC cycle guard заменяет переполнение стека
  на Unsupported. Для успеха нужен monotone effect/points-to fixed point по SCC, finite lattice и перенос provenance;
  «при повторе return» теряет эффекты и недопустим. **5–15 дней** для ограниченного analysis проекта после дизайна.
  Рекурсия пользовательского comparator — отдельное обязательство относительно его callback contract.
- **Replace/stub_verified и RecursiveCheck:** они не исполняют обычный callee body, так что argument/return pairing
  C2 не доказывает initializedness результата stub. Нужен expressible effect summary: какие байты must-init,
  may-write/deinit, какие false bits сохраняются, затем havoc и применение summary к caller shadow.
  Contract clauses/generated writes и verifier-private state тоже входят в модель.
  Replace сначала, RecursiveCheck с индуктивным контрактом после него; **10–25+ дней**, высокий семантический риск.
  Не bless весь modifies region: это скроет незаписанный output. Не переносить гарантии сортировки в initialization без lemma.

Для первых сквозных ON proofs предпочтительнее исполнять actual bodies и не вводить эти проекты одновременно.
Если unwind перестаёт масштабироваться, без sound summaries/индукции завершить arbitrary-length часть не получится.

### A4. Остальные layout/intrinsic ограничения

Перед расширением общего scope проверить exact issue reproducers и наличие их путей в SmallSort.
В частности, `integer_min/max/cold_path` можно исследовать как узкие модели/fallbacks по образцу SEL1,
с единым reachability/codegen/analysis binding, **2–5 дней** при простом эффекте.
Не обходить отказ общим «intrinsics ничего не меняют». Niche enums, variant-dependent padding, nested MU aggregates,
DST и Drop требуют своих масок/инвариантов; универсальная поддержка — недели, а не один whitelist.

### A5. Карта связанных uninit issues

В столбце «C2/SEL1» различаются исправленный механизм, статическое ожидание и отсутствующий replay.
**Ни один OPEN issue не объявляется закрытым только по нашему green regression.**

| Issue / официальный статус | Отношение C2/SEL1 и оставшаяся работа |
|---|---|
| [#3300](https://github.com/model-checking/kani/issues/3300) OPEN — automatic memory initialization tracker | Существенно продвинута storage/direct-call часть; полный tracker не закрыт: indirect, cycles, layouts, extern/trait-object границы остаются |
| [#3881](https://github.com/model-checking/kani/issues/3881) OPEN — slices delayed-UB regression | Достижимые FnPtr в reported path не становятся поддержанными от F7/SEL1; явный отказ лучше crash, но не proof этого случая |
| [#4850](https://github.com/model-checking/kani/issues/4850) OPEN — transmute 128==64 ICE | Report касается fat pointer/unsized `SUtf16Str`; прямого фикса/контроля нет. Поддержка slices не доказывает исправление unsized struct transmute |
| [#4851](https://github.com/model-checking/kani/issues/4851) OPEN — resolve Arbitrary::any ICE | Autoharness/reachability случай, отдельного replay нет; не включать в обещание C2 |
| [#4852](https://github.com/model-checking/kani/issues/4852) OPEN — delayed unwrap(None) | B1/S3 body filtering/overrides затрагивают смежный механизм; exact reported stubs/alloc путь не квалифицирован. Replace support из этого не следует |
| [#4853](https://github.com/model-checking/kani/issues/4853) CLOSED — trait-object init-state panic | В pin есть явный Unsupported вместо старого unreachable. Официально закрытый crash не означает поддержку trait objects |
| [#4854](https://github.com/model-checking/kani/issues/4854) OPEN — constant MU pointer Unsupported-path ICE | C2 `check_uninit/mod.rs` обрабатывает Unsupported до operand_ty: reported panic mechanism защищён. SUCCESS либо явный отказ exact const repro ещё надо проверить; relocation не входит автоматически в M1 |
| [#5020](https://github.com/model-checking/kani/issues/5020) OPEN — NonNull/Box offset false negative | **Указанный корень исправлен:** `RigidTy::Pat` сохраняет current_offset, commit `5ca51679e3`; `nested-pat-data/padding` проверяют offset8. Добавить exact unwritten pointer-field negative; не объявлять весь Box/layout класс закрытым |
| [#5151](https://github.com/model-checking/kani/issues/5151) OPEN — flat MU array, nontrivial T | Layout refusal для `[MU<D>;2]`, D(u8)+Drop, вероятно снят: C2 распознаёт flat slots и computable mask D. Текущие padded-array controls используют Copy. Нужны exact legal + `drop_in_place` hole; Drop сам по себе не делает mask неподдержанным |
| [#5164](https://github.com/model-checking/kani/issues/5164) OPEN — integer_min/max/cold_path | SEL1 добавляет только select; остальных моделей он не реализует. Приоритет по actual reachable graph |
| [#5165](https://github.com/model-checking/kani/issues/5165) OPEN — niche-encoded enum pointees | `EnumWithNicheEncoding` остаётся layout refusal; соседний enum-offset fix его не снимает |
| [#5166](https://github.com/model-checking/kani/issues/5166) OPEN — trait-object pointees | По-прежнему Unsupported. Отдельно от закрытого panic #4853 и от finite FnPtr dispatch |

Сразу полезный короткий пакет: exact #5020 hole, #4854 crash/explicit refusal, #5151 legal/Drop-hole
на baseline и C2/SEL1; **1–3 дня** подготовки/разбора. Успешный контроль уточнит patch scope,
но только issue-specific результат позволяет просить соответствующее закрытие issue.

## 4. B — valid-value checks: включить проверку на настоящих операциях

### B1. Почему C2 здесь недостаточно

В pinned [check_values.rs](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/kani-compiler/src/kani_middle/transform/check_values.rs)
есть scalar ranges и часть aggregate/niche checks, но `CopyNonOverlapping` выдаёт UnsupportedCheck
с TODO value check. SEL1 этот файл не меняет. Флаг `-Z valid-value-checks` независим от uninit.
В [порядке passes](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/kani-compiler/src/kani_middle/transform/mod.rs)
valid-value идёт перед UninitPass; совместное включение также требует qualification generated instrumentation.

Первый blocking project — [#3762](https://github.com/model-checking/kani/issues/3762):
`copy`/`copy_nonoverlapping` встречаются в SmallSort scratch, moves и CopyOnDrop.
Пилот: один реальный copy site, valid bool/char/enum payload, raw invalid-byte negative,
MU/padding legal companion, затем actual sort4/merge с **обоими flags ON**.

Не добавлять безусловный `is_valid<T>` на каждый raw copy: untyped copy имеет право переносить
неинициализированные/невалидные bytes как bytes, включая padding и MU storage.
Проверять момент производства/использования typed value и корректно переносить или откладывать validity obligation;
для overlapping copy нужна согласованная snapshot/memmove semantics. Иначе вместо gap получим false positives
или исчезновение проверки на последующем typed read.
Дизайн+reproducer **2–4 дня**, узкий upstream-кандидат с контролями **7–15 дней**; полный механизм может оказаться шире.
Ценность для challenge очень высокая: это непосредственный путь через большинство memory-transfer helpers.

### B2. Остальные requested issues: что проверять, а не «закрыть все девять»

Все перечисленные здесь issues сейчас OPEN; C2/SEL1 не вносит их полноценные фиксы.

| Issue | Обязательство и relevance |
|---|---|
| [#2998](https://github.com/model-checking/kani/issues/2998) | Automatic validity invariants tracker; рамка общей цели, не отдельный SmallSort failure |
| [#2541](https://github.com/model-checking/kani/issues/2541) | Producing-invalid-values tracker; часть scalar checks уже есть upstream, полного покрытия нет |
| [#3203](https://github.com/model-checking/kani/issues/3203) | Unsupported validity constructs tracker, включая copies/references/enum representations; не отдельный patch |
| [#3759](https://github.com/model-checking/kani/issues/3759) | Reference/Box validity, metadata/alignment/dangling/pointee obligations. Важно для arbitrary T с refs/Box; ownership либо явные checks |
| [#5021](https://github.com/model-checking/kani/issues/5021) | Invalid bool через const-pointer round-trip/reference transmute не ловится. Нужен production-site check, не только mutable-cast syntax |
| [#5022](https://github.com/model-checking/kani/issues/5022) | Invalid element через slice pointer теряется; traversal dynamic extent вместо zero-count «anything valid» |
| [#5023](https://github.com/model-checking/kani/issues/5023) | Aggregate enum discriminant не проверяется; учитывать representation и фактический active variant |
| [#5156](https://github.com/model-checking/kani/issues/5156) | Дыры между discriminants: scalar min/max range допускает несуществующий tag. Нужна membership, не один диапазон |

Для C2/SEL1 остались разные enum-layout и validity ограничения: чинить discriminant checker не означает
поддержать enum padding в uninit, и наоборот. Узкие #5156/#5023 и #5022 — ориентир **3–7 дней каждый**,
но до заявления о generic T нужен их совместный layout/validity matrix. #3759 шире, его нельзя честно оценить одним днём.
Дефекты false SUCCESS (#5021/22/23/5156) важнее косметических crash fixes, если их construct входит в proof scope.

**Альтернатива B:** механизированный type-preservation theorem: каждый выходной T — исходный valid T целиком,
typed moves соблюдают payload/padding, не читаются holes, не возникает новых discriminants/references,
компаратор сохраняет нужную validity. Текущая tag-permutation assumption этого не доказывает:
она не связывает произвольную byte representation и не покрывает payload mutation.
Конкретный theorem для одного helper — **3–7 дней spike**, generic library-wide — недели и proof composition.
Только review-комментарий «сортировка лишь переставляет T» не выполняет автоматическое UB-требование.

## 5. C — immutable bytes: отсутствующая permission model, а не ещё один flag

Pinned [soundness.md](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/docs/src/soundness.md)
прямо исключает lifetime/alias-rule enforcement и говорит, что immutable mutation обнаруживается лишь через симптомы.
В unstable flags нет действующего Stacked/Tree Borrows pass. Points-to для delayed UB — не borrow checker.
Readonly-static representation/CBMC `CConstant` и `modifies` frame — полезные отдельные механизмы,
но не доказательство отсутствия записи за живым `&T` и не гарантия всех Rust alias rules.

### C1. Ближайший Kani-проект: call-local защита shared-reference bytes

[#5040](https://github.com/model-checking/kani/issues/5040) наиболее близок к нужной части:
отмечать защищённые bytes live `&T` arguments, проверять реальные stores/byte copies/havoc,
снимать call-local защиту в правильный момент и исключать поля `UnsafeCell` по реальному layout.
Нужны nested calls/overlap, slice extent, reborrow, closures/captured aliases и contract-generated writes.
Проверка только адреса allocation или конечного равенства значения пропустит write-then-restore того же байта.

Пилот **3–5 дней**: legal writable destination, запрет alias dst с &u8, write-then-restore negative,
разрешённая Cell/UnsafeCell mutation, nested Freeze/UnsafeCell и callback с внешним mutable state.
Полезный узкий patch — **10–20+ дней**, общий borrow/provenance model — многонедельный/многомесячный проект.
Риск: MIR может не сохранять нужные lifetime boundaries; call-local модель не доказывает более долгие borrow obligations.
Это нельзя назвать закрытием C без доказательства, что все protected lifetimes конкретного SmallSort укладываются в модель.

| Issue / официальный статус OPEN | Значение для плана |
|---|---|
| [#314](https://github.com/model-checking/kani/issues/314) | Object aliasing violations; широкая незакрытая проблема. C2/SEL1 не добавляют такую модель |
| [#3089](https://github.com/model-checking/kani/issues/3089) | Rust-specific UB umbrella, включая aliasing; не один реализуемый SmallSort patch |
| [#3475](https://github.com/model-checking/kani/issues/3475) | Предложение/развитие Stacked Borrows; название не означает наличия working flag на наших pins |
| [#5040](https://github.com/model-checking/kani/issues/5040) | Самый узкий старт: запрещать реальные writes за live shared arguments; пока это не текущая гарантия |
| [#2907](https://github.com/model-checking/kani/issues/2907) | Encapsulated mutability в modifies; необходима корректная UnsafeCell-граница, но frame abstraction не заменяет alias checks |
| [#3672](https://github.com/model-checking/kani/issues/3672) | r_ok/w_ok API; доступность storage/geometry не равна разрешению изменить immutable byte |

### C2. Предпочтительная альтернатива: ownership/separation proof реального кода

Нужен автоматически проверенный invariant: алгоритм владеет writable input/scratch regions;
reborrow компаратору защищает Frozen payload на время вызова; записи sorting body идут после завершения reborrow;
side effects callback разрешены в его собственной footprint и в законных UnsafeCell-полях.
Существующие helper frames перечисляют лишь element/dst memory и честно ограничивают callbacks,
пишущие вне frame. Это надо либо обобщить, либо ограниченный comparator domain оставить как ограниченный результат.
Безмутирующий arbitrary-bool comparator сам по себе не доказывает безопасность всех допустимых FnMut.

Рекомендую отдельный **5-дневный feasibility spike** ownership proof одного реального swap/insert helper
в уже одобренном VeriFast, с теми же source/preconditions и отрицательным alias/write-restore control.
Цель spike — проверить expressibility и связь с Rust, а не объявить theorem по одной удачной верификации.
Если помогает — строить generic element/segment predicates, loop invariants и 7-target coverage; это недели работы.
Если нужна новая frontend semantics или вручную переписанный алгоритм без correspondence theorem — STOP/replan.
Такой трек требует отдельного владельца proof, CI-пакета и решения владельца; не передавать новую разработку
VeriFast maintainer автоматически. Его существующая роль — готовые tool patches и review.

## 6. D — #5104: локализовать, а не записать в решённое посредством SEL1

[#5104](https://github.com/model-checking/kani/issues/5104) OPEN: false counterexample для conditional pointer read
`[u8;1]`, также plain if; сообщён аналогичный raw-byte read через each_mut/map.
Сбой сообщён **без uninit flag**. SEL1 добавляет shadow pairing/points-to для fallback, не новое обычное value lowering.
Не установлены ни false SUCCESS, ни виновный компонент; C-прохождение не исключает CBMC из-за разных GOTO.
Подробности и reproducer: [KANI5104-RECON.md](KANI5104-RECON.md).

Следующая стадия — один bounded диагностический пакет: исходный F7, plain if, scalar-u8 и symbolic-index controls
на одном pin, без смешения solver/model upgrades. Сопоставить MIR → raw symtab → linked/post-instrument GOTO
→ dereference/symex по адресам и байтовым значениям. Отсутствие строки store в compact trace не доказывает потерю store.
Затем менять только компонент, в котором найдено первое расхождение. Host/native replay — control, не proof.
Оценка **2–4 дня** локализации; стоимость исправления до этого неизвестна, при CBMC — отдельный patch+regression.
Узкий workaround допустим только с доказанным correspondence реальному target и отдельной явной границей.

Ценность: высокий приоритет доверия и разблокировка array-payload профилей. В то же время нельзя из одного
false counterexample объявлять все Kani results неверными или обещать, что весь класс исчез после SEL1.
Наличие #5020 и validity false negatives требует controls ещё и на пропущенные failures, не только на ложные отказы.

## 7. Как выбирать между инструментами и сведениями

[Текущий approved list](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/tools.md):
Kani, VeriFast, ESBMC/GOTO-Transcoder, KMIR, Flux, RAPx. Approved не означает, что каждый уже умеет доказать
данный unsafe/generic target или именно эти UB. Не строить новый frontend на предположении о готовой поддержке.

| Подход | Практическая ценность / ограничение |
|---|---|
| Расширять Kani узкими upstream patches | Максимально использует нашу основу и существующий std CI. A2/#3762/validity fixes реалистичны по отдельности; общий alias model и все T гораздо шире |
| VeriFast ownership + validity/initializedness invariants | Наиболее естественный кандидат для C и all-length loop reasoning; нужен пилот на реальном Rust, byte/layout/Drop semantics и связь generic proof с targets |
| KMIR или ESBMC как независимый диагностический replay | Может отделить frontend/backend проблему D. Общий GOTO frontend может наследовать lowering-баг; другой solver сам не добавляет missing UB instrumentation. Для решения A–C нужна отдельная capability qualification |
| Проверяемое сведение FnPtr→closure / validity-preserving permutation | Экономит tool work для закрытого домена. Нужна автоматизация relation и actual-source binding; не расширяет implicit scope до all P/T/N |
| Miri, host replay, C-копия алгоритма | Хорошие controls. Не exhaustive proof для Challenge 8 и не замена разрешённому automated verifier |

Комбинация одобренных инструментов возможна как проект решения, но обязанность должна быть полностью
проверена хотя бы одним корректно связанным proof, либо композиционным theorem.
Два неполных прогона не складываются автоматически в полный UB-check.
Неодобренный инструмент потребует tool application/integration; при медленном review это дополнительный внешний gate.

## 8. Порядок работ и точки решения

### Ближайшая волна: два воркера, ограниченные spikes

1. **Зафиксировать достигнутое:** завершить уже подготовленные SEL1-C2 Gate A/replay на точном freeze,
   не менять C2/SEL1 ради нового roadmap. Это очередь имеющегося задания, не новый массовый CI.
2. **Worker14:** A1 matrix и exact uninit issue controls (#5020/#4854/#5151), затем A2 target-set/design spike
   на исходном `P::CMP`. Между стадиями source/static результат → CI request координатору → приёмка, одна стадия на сессию.
3. **Worker15:** B1 #3762 legality/invalid-byte matrix и схема delayed validity; начать с диагностики, не общего patch.
   Параллельно owner/main оформляет D packet; его исполнителя выбрать после одного из spikes, без третьего пересекающегося writer.
4. **Независимый C feasibility:** сначала краткий design/expressibility audit #5040 против ownership approach;
   если нужен implementation pilot, дать освобождённому воркеру/отдельно назначенному proof-агенту, а не расширять текущую роль молча.

Первый пакет решений можно получить примерно за **5–10 рабочих дней двух исполнителей**;
это диагностические deliverables, не срок завершения Challenge 8.
На развилке сравнить: finite FnPtr support либо механизированный comparator relation;
raw-copy validity instrumentation либо type-preservation proof; #5040 guard либо ownership proof.
Не начинать одновременно все большие проекты из A3/B/C.

### Основная волна после spike review

5. Один владелец A2 patch, другой B1 patch, разные branches; интегратор последовательно сводит общие pipeline/layout хунки.
   Узкие #5156/#5022 fixes брать, когда их validity obligations входят в выбранный generic domain.
6. Прогон actual SmallSort paths с обоими checks и моделью immutable permission/доказательством ownership.
   Нужны initialized/invalid/immutable negative controls и callback frame controls; не только «все прежние tests green».
7. Если bounded execution хватает для следующих helpers — расширять A1. Если упирается в arbitrary len/composition,
   выбрать A3 summaries/SCC либо индуктивный proof в альтернативном инструменте; до выбора не обещать полный пункт 1.
8. Финальный freeze, targeted Quick, полный regression Gate A инструмента на трёх платформах,
   actual std CI/proof matrix на том же combined pin; обновить coverage/Limitations по установленным результатам.
   Перед заявлением полного пункта 1 отдельно принять all-T/all-length, callback-frame и panic/unwind аргументы;
   включение дополнительных UB checks само по себе этих proof obligations не закрывает.

### Обязательные критерии приёмки каждой feature-стадии

- Различающий baseline: defect repro выдаёт false SUCCESS/false failure/Unsupported/crash как заявлено;
  кандидат исправляет именно это. И legal, и intended-negative companions, полезная reachability.
- Raw copy не читает padding как typed data; typed moves не благословляют holes; validity не считается из одного initialized bit.
- FnPtr/vtable target set complete; caller/callee shadow pairing следует actual dispatch; unknown явно отказан.
- C-проверка ловит реальную write, в том числе write-then-restore; UnsafeCell и разрешённый callback state остаются legal.
- Root/file/tool/std/flags/selected-body binding, полный список отказов, exit/signal, unwinding assertions,
  artifact completeness и ограниченные ресурсы; Unsupported/timeout/runner loss — не proof PASS.
- Снижение object bits до12 оставлять там, где квалифицирован профиль; не считать этот ресурсный приём
  доказательством произвольного числа allocations/длин. Нужны соответствующие bounds/guards или абстракция.

## 9. Реалистичный объём, CI и upstream задержки

Реально нашими силами: issue-specific controls, bounded ON coverage, finite FnPtr support spike,
отдельные validity defects, локализация #5104 и узкие исправления с fork CI.
Полная проверка all-T/all-length плюс callbacks/Drop/permissions — **программа на многие недели или месяцы**,
а не ещё несколько вечеров после C2. Особенно велик C: текущая модель Kani его принципиально не покрывает.
Стоимость общего borrow model, trait-object вселенной и полноценных Replace/Recursive summaries пока не подтверждена пилотом.

Fork CI позволяет разрабатывать и квалифицировать точный combined pin без ожидания merge каждого PR;
оно не гарантирует, что организаторы примут этот tool pin как final solution.
Upstream review вести параллельно маленькими связанными PR и exact tests; не смешивать tool project с std runtime changes.
Два маршрута успеха разделены: **fork evidence готово** и **организаторы/maintainers приняли доверенную базу и solution**.

Локальные compilers/verifiers/builds запрещены; подготовка через чтение/Git/Python, запуск CI — координатор.
Для диагностик переиспользовать узкий fork workflow с исходными exits/artifacts; первичный cap — согласованный Quick,
в каждом запросе конкретные roots/time/RSS/output limits и одна попытка, без бесконечного перебора variants.
Полную трёхплатформенную матрицу делать для release freeze/существенной интеграции, не каждого proof-прототипа.
Cloud $0; никакие Builds или новые proof lanes этот план не открывает. Публикации и привязка tool pin — решение владельца.

**Рекомендация:** сначала превратить C2+SEL1 в покрытие реальных SmallSort путей, одновременно снять #3762 и
локализовать #5104; затем finite FnPtr/comparator relation. По C — ранний ownership/#5040 feasibility gate,
поскольку именно он может потребовать другого инструмента. Общие trait objects, рекурсивные contracts и весь
Rust borrow model не брать первым эшелоном. До проверенных сведений и полных domains сохранять статус
«существенный частичный результат», а не «пункт 1 выполнен с тремя оговорками».
