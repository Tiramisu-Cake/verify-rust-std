# Независимый аудит Kani B1 и B3

12 ноября 2026 года

| Кандидат | Решение |
|---|---|
| **B1 `d5f072f2b`** | **Доработать перед upstream review.** Локальное исправление потери проверок корректно для `Call` и подтверждено на фиксированном коде. Политика разрешения вызовов расходится между local visitor, initial-target visitor и points-to. Тестовый FnPtr shim получает диагностическое имя bodyless, хотя pinned rustc умеет построить его MIR. Допуск MIR-backed shim шире доказанной парности аргументов. Рекомендую оставить в первом PR сохранение операций и согласованную диагностику неизвестных вызовов, а перенос union shadow через shim отложить до отдельной проверки ABI. |
| **B3 `6db3c4dab`** | **Готов к отдельному upstream review после правки описания.** Матчированный прогон на чистой базе показал четыре abort CBMC, после единственного backend-изменения семь harness прошли. Перенос теста в основной набор подтверждён Linux CI на финальном head. Полный workflow отменён. Отдельная паника `-Z uninit-checks` существовала на базе и остаётся задачей для triage. |

[Исходный бриф][brief] · [B1 diff][b1diff] · [B3 diff][b3diff] · [Tracking issue #3300][issue]

## Ревизии и доказательства

База обеих веток — `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`, тот же SHA вернул upstream `main` при проверке. B1 меняет четыре production-файла и добавляет 20 Rust fixtures с 20 expected-файлами, +767/−26. B3 меняет один production-файл и добавляет два тестовых файла, +184/−2. Локальный `git diff --check` от базы прошёл для обеих веток. Сверены исходники, доступные raw logs и metadata завершённых jobs. Новые прогоны Kani, CBMC и CI не запускались. [Upstream base][base] · [B1 diff][b1diff] · [B3 diff][b3diff]

| Источник | Что подтверждено |
|---|---|
| B1 focused `43110714635` | Checkout `0e83acc6823d25949f7d303e70a69441d2cfb138` отличается от `d5f072f2b` только workflow-файлами. Format/build/Clippy прошли. По наборам 22/0, 83/0 (2 ignored), 14/0, 1/0. Все 20 новых селекторов прошли свои goldens. Отдельные exact-head format/Clippy и cargo-deny jobs также прошли. [Лог][b1quick] · [Diff CI head][b1cihead] · [Format/Clippy][b1format] · [Audit][b1deny] |
| B1 full `43112332778` | На `d5f072f2b` прошли Ubuntu 22.04, 24.04 и 24.04 ARM64, macOS 15 Intel, perf, LLBC, docs и benchcomp. macOS 14 отменён до выполнения шагов. Итог workflow — cancelled. Причину отмены по проверенным записям установить нельзя. [Workflow][b1full] |
| B3 matched `43115481098` → `43115485052` | Base fixture в `dc590936c`, затем тот же fixture в `9dddcb113` с единственной правкой `typ.rs`. CI-обёртки `f304106019f8…` и `9ce21fcdf530…` меняют workflow. С default checks на базе три harness прошли, четыре завершились статусом 134 в CBMC 6.11.0, `simplify_utils.cpp:345`, `bits2expr`, условие `el_size_opt.has_value() && *el_size_opt > 0`. С исправлением default selector прошёл неизменённый golden с семью успешными harness. Оба quick workflow в целом красные из-за отдельного flag-on селектора на исправленном дереве и обоих селекторов на базе. [Лог базы][b3baseci] · [Лог исправления][b3fixci] · [Изменение между тестируемыми деревьями][b3production] |
| B3 full `43117729467` | На `6db3c4dab` прошли те же три Linux regression jobs и perf, LLBC, docs, benchcomp. Три Linux jobs прогнали весь `expected` suite (548 passed, 13 ignored) с финальным расположением теста. На macOS 14 шаги отсутствуют, macOS 15 Intel дошёл до setup, итог шага regression отсутствует. Workflow cancelled. Отдельные format/Clippy и cargo-deny workflows на том же SHA прошли. [Workflow][b3full] · [Linux job][b3linux] · [Скрипт регрессий][regress] · [Format/Clippy][b3format] · [Audit][b3deny] |

## B1 — ответы на вопросы 1–6

### 1. Сохранение операций и их порядок

В `Call` один `super_terminator` собирает operand operations. При `Err` `break 'call` ведёт к общему `self.targets.push`, поэтому target сохраняется один раз. Если entry block не содержит statements, `LoadArgument` уже добавлен в этот target до обхода операндов. `Unsupported` добавляется после них. Инструментатор сохраняет порядок операций `Before` при разбиении блока, поэтому порядок на этом ребре — load → operand check → unsupported check → исходный call. Положительный и частичный union entry controls дают наблюдаемый признак, что operand check и Unsupported дошли до верификатора. [Подготовка entry][b1entry] · [Call и эпилог][b1call] · [Эпилог][b1flush] · [Вставка блоков][b1insert] · [Entry fixtures][b1fixtures]

Есть унаследованный отдельный ранний выход из `visit_statement` при `UnionAsField`. Он добавляет Unsupported и возвращается до `push` и продвижения statement index. Если это последняя statement, terminator сбрасывает pending target. Если затем есть обычная statement, она может опубликовать target со старым index. Это дефект того же класса за пределами `Call`. В PR ограничить claim сохранением call-terminator target либо включить отдельное исправление с самостоятельным тестом. [Ранний выход Assign][b1assign] · [Продвижение index и сброс][b1stmtflush]

### 2. Классификация вызовов и ABI shim

Локальный visitor теперь явно различает FnPtr/ошибку резолюции, Virtual, LLVM intrinsic и bodyless Shim. Но initial-target visitor вызывает `Instance::resolve(...).unwrap()` на исходном MIR ещё до проверки, пуст ли список targets. Reachability также повторно разрешает FnDef через `unwrap()` до global passes, даже если локальная инструментированная копия получила барьер. Поэтому обещание диагностировать ошибку резолюции относится только к local visitor. [Reachability][b1reach] · [Порядок фаз][b1phase] Для seeded roots points-to использует собственный классификатор, пропускающий любой успешно разрешённый non-Virtual FnDef в дальнейший dispatch. Nonforeign bodyless instance при попадании в regular-call ветку встречает `body().unwrap()`. У test shim этот unwrap не воспроизведён. Более того, на pinned rustc `!has_body()` и `body().is_none()` дают разные ответы для generated shim. Фактическую доступность тела следует согласовать между проходами. [Rust public Instance API][rustmono] · [Rust bridge][rustbridge] Локальная runtime-диагностика сама по себе не защищает более ранний глобальный анализ. Для LLVM intrinsic уже есть отдельная ранняя Unsupported ветка backend, поэтому новый local guard не является первым таким барьером. [Initial targets][b1seedresolve] · [Порядок глобального прохода][b1global] · [Points-to dispatch и resolution][b1points] · [Body unwrap][b1body] · [Backend LLVM guard][llvm]

Наличие MIR позволяет инструментировать тело, но не доказывает парность union shadow. Caller фильтрует исходные operands по top-level union и использует индекс `idx+1`. Callee ищет union среди своих формальных locals. Backend для `RustCall` разворачивает последний tuple, а некоторые вызовы перехватывает hook. Если конкретный shim получает union в развёрнутой позиции, одного `has_body` недостаточно, чтобы сопоставить store и load. Унаследованный `load_argument` благословляет destination при отсутствии соответствующего slot, предполагая существование другой ветви, которая переносит witness. Для новых форм ABI это предположение надо доказать или отклонить форму. Также `StoreArgument` требует place, поэтому retained constant union operand остаётся отдельной проверкой для расширенной области. [Caller][b1shimcode] · [Callee][b1entry] · [RustCall и hooks][b1abi] · [Argument buffer][b1buffer] · [Ожидаемая форма операнда][paniccodeb1]

### 3. Владение диагностикой

Для обычного FnPtr/Virtual, видимого local visitor и достижимого в итоговом MIR, перенос guard в один проход устраняет зависимость от delayed-UB targets. Это подтверждают пары plain/seeded для прямого указателя, обёртки, erasure, escaped global и trait object. Глобальный анализ по-прежнему опускает неизвестные эффекты, рассчитывая, что исполнение остановится на Unsupported. При расхождении классификации, compile-time отказе или вызове, который не проходит локальное инструментирование в нужной форме, такой аргумент не применим. Согласовать политику трёх мест: initial collector берёт только успешно распознанные intrinsic seeds, points-to не заходит в заведомо неподдерживаемое тело, а local visitor ставит один барьер на исходном call. Проверить, что достигнутые проверки операндов располагаются до барьера. [Удаление delayed guard][b1guard] · [Points-to контракт][b1pointsstart] · [Plain/seeded fixtures][b1fixtures]

### 4. Был ли на базе измеренный false SUCCESS

По имеющимся записям такой результат для точного `entry-partial` не установлен. Источник доказывает потерю `LoadArgument`, operand check и локального Unsupported для данного target. При seeded варианте база может всё равно поставить delayed guard, а на любом варианте возможен другой достигнутый отказ. Сохранить одинаковый source, pinned toolchain, edition, flags, выбранный harness и компиляторное lowering на `bf9c58e66` и финальном B1 export. Для plain и seeded снять свойства по harness и `RUSTFLAGS=--emit=mir`. Различить отсутствие property, property SUCCESS, property FAILURE и отказ до запуска CBMC. Claim о false SUCCESS допустим только при измеренном успешном результате базы на достигнутом частично инициализированном пути. Исправление потери target можно описывать уже по коду и фиксированным контролям. [Base visitor][b1basecall] · [Partial fixture][b1partial] · [Initialized companion][b1init] · [Как снять MIR][mirdump]

### 5. Что проверяет shim fixture

В B1R raw log `43108072253` у обеих версий свойство `indirect.unsupported_construct.1` с причиной bodyless Shim падает на строке `std::ops::Fn::call(&f, (42,))`. В сгенерированном `Fn::call` отдельное свойство function-pointer имеет SUCCESS. Внешняя unsupported-проверка сопровождается `assume(false)`, поэтому SUCCESS внутреннего свойства не подтверждает достигнутую проверку. В финальном B1R2 эти goldens проходят. B1R raw log показывает также отдельные delayed read properties внутри `seed`. Финальный успешный job не печатает per-harness properties и сам по себе не доказывает, что каждый plain root имел пустой набор initial targets. Точный rustc из quick log — `7189d39d9ce936881b8132c6addeaf3e295cd455`. Его resolver для `Fn::call` на `FnPtr` выбирает generated `ShimKind::FnPtr`. `Instance::has_body()` спрашивает доступность MIR определения, тогда как `Instance::body()` использует `instance_has_body`, допускающий генерацию MIR для shim. Лог в сочетании с исходниками указывает на внешний отказ по definition-level predicate. Он не доказывает фактическое отсутствие MIR. До исправления точный комментарий — `Expect the bodyless-shim diagnostic at this Fn::call site.` После исправления обновить golden по реальной точке отказа. [Pinned resolver][rustresolve] · [Rust public Instance API][rustmono] · [Rust bridge][rustbridge] [Сырой лог B1R][b1oldquick] · [Комментарий shim][b1shimtest] · [Golden][b1shimgold]

Для сохранения новой поддержки нужен отдельный положительный bodyful-shim контроль с доказанной резолюцией, парными store/load и наблюдаемым shadow outcome. Практичный набор — initialized positive и partial negative с nontrivial ABI, с seed и без него. Начать с `Fn::call` на function item без приведения к fn pointer как кандидата на положительный generated-shim контроль, а текущий FnPtr пример после исправления должен проверять внутреннюю indirect boundary. Снять internal instance kind, `has_body`, MIR locals/operands и backend ABI. Для LLVM intrinsic, если ветка остаётся частью публичного claim, полезен target-gated fixture на фактическом пути до локального guard. Если такой путь отклоняется на более раннем этапе, так и описать. [Локальный dispatch][b1shimcode] · [Backend LLVM guard][llvm]

### 6. Достаточность B1-матрицы

Двадцать fixtures достаточны для показанных представлений indirect call и для различения pending operand и statement-free entry. Они не доказывают общее покрытие всех ошибок резолюции и shim. Сохранить plain/seeded для FnPtr, Virtual, pending operand, entry initialized/partial и shim с уточнённой диагностикой. Erased/wrapped/global пары можно сокращать только после подтверждения одинаковой существенной формы MIR и поведения alias analysis. Число fixtures само по себе не проблема. Для отрицательных тестов сохранить named outcomes и проверить per-harness свойства там, где substring golden способен принять лишнюю диагностику или отсутствие другого свойства. [Набор fixtures][b1fixtures] · [Правила matcher][goldens] · [Лог финального gate][b1quick]

## B3 — ответы на вопросы 7–11

### 7. Layout, логическая типизация и ABI

В CBMC 6.11.0 `bits2expr` рекурсивно восстанавливает поля структуры. Array-ветка требует положительной ширины **элемента**, а у пустой структуры нет полей для рекурсии. Это согласуется с abort на `[(); 2]` и его исчезновением после замены payload. [CBMC 6.11.0][cbmcbits]

В `codegen_union` ширина union и каждого arm берётся из rustc layout. Для положительного padding сохраняется тот же padding-компонент. Только physical payload с GOTO width 0 заменяется пустым unit-struct, также ширины 0. `DatatypeComponent::unionfield` по-прежнему получает исходный логический тип и отдельный padded type. Lookup типа поля и projections используют логический тип, а ширина UnionField и сериализация определения компонента используют physical type. Это подтверждает локальное сохранение ширины и формы логических projection/index. При нулевом padding, включая all-ZST union, старый путь сохранён. [Хунк B3][b3typ] · [Unit type][b3unit] · [UnionField и ширина][b3component] · [Сериализация Irep][b3serialize] · [Place projections][b3place]

Rust ABI не меняется на уровне type/layout входа. Backend lowering всё равно надо проверять на реальном by-value вызове, если PR заявляет ABI coverage. Приведённые тесты проверяют typed copies, логические операции и один offset содержащей структуры. Они не устанавливают прохождение noinline call/return или проверку alignment у escaping field reference. В aligned fixture `[u8; 8]` уже даёт весь размер, а `align_of` проверяет Rust layout. Для более сильного контроля подойдёт union с меньшим byte arm, где итоговую ширину округляет aligned ZST, плюс проверка поля через реально используемый адрес. [Aligned и offset fixtures][b3aligned] · [Call ABI][b3abi]

### 8. Достаточность семи тестов

Да для воспроизведённой default-check поломки. Четыре соответствующих harness различают прежний abort и починенный backend. Три контрольных случая уже проходили на базе: aligned unit-like ZST, all-ZST union и in-bounds indexing. Индекс nondeterministic, но ограничен `index < 2`. Операции с `size_of_val` над sized ZST и присваивание нулевому lvalue слабее, чем наблюдаемый адрес или проверка выхода за границу. Backend явно пропускает zero-size assignments. Описывать этот harness как контроль типизации и in-bounds projection, без claim о физических записях. [Семь harness][b3tests] · [Пропуск ZST assignments][b3zstassign] · [Базовый лог][b3baseci]

`[u64; 0]` или другой zero-length non-ZST array, дополнительно выровненный arm и noinline identity являются точечными усилениями при расширении claim. Нынешний узкий PR может идти на review с существующим дифференциальным набором и явными границами. Если требуется демонстрировать сохранение выравнивания ZST arm, дать escaping reference и наблюдаемое свойство о его адресе. [Контроли layout][b3aligned]

### 9. Что именно читают post-copy assertions

В byte-array cases `write_bytes` записывает весь extent, а массив байтов покрывает его целиком. В padded cases после копирования читаются только `byte` и `word`, которые имеют допустимые и инициализированные значения. В `PaddedUnionRust` Rust layout имеет внешний union, его `Padded` payload объявлен `repr(C)`. Rust Reference допускает ненулевое смещение поля в repr(Rust) union. Эти assertions используют доступ через типизированное поле после записи полного extent. [Rust Reference][rustunion] Формулировку «padded Rust-layout payload» следует заменить на «padded C-layout payload in C- and Rust-layout unions». ZST assertions не читают payload bytes. Равенство padding bytes тесты не требуют. Именно эти fixtures дают наблюдаемый base/fix контраст при default checks. [Byte и padded fixtures][b3copies] · [Baseline][b3baseci] · [Backend fix run][b3fixci]

### 10. Issue перед PR

Рекомендую сразу отдельный узкий PR с точным воспроизводившимся fixture и ссылками на matched логи. Точного ticket для padded-union typed copy в проверенном upstream поиске не нашёл. Открытый [#5085][issue5085] сообщает тот же CBMC invariant на `static`/`const` с nested zero-width arrays без union. Указать `Related to #5085` как другую ветку lowering с общей сигнатурой. Если владелец предпочитает issue first, в нём достаточно приложить точный base SHA, harness, default flags и abort 134. Flag-on panic связать отдельно с [#4854][issue4854], без closing keyword для обоих issues. [Upstream contribution guide][contributing] · [Наблюдавшийся fixture][b3oldfixture]

### 11. Отдельный panic в `MemoryInitOp::operand_ty`

На обоих matched деревьях flag-on selector падает до CBMC, в `relevant_instruction.rs:136:73`. Match отвергает `Operand::Constant` и `Operand::RuntimeChecks` через `unreachable!` при подготовке address-based operation. Из локальных producers `StoreArgument` — основной кандидат, поскольку принимает call operand напрямую, тогда как другие операции в этой ветке строят `Copy(place)`. Точное значение операнда и вид `MemoryInitOp` из backtrace не следуют. Сохранённый семисценарный input воспроизводился. Сокращённый пример из PANIC-NOTE пока имеет статус NOT_RUN. `#4854` даёт ту же функцию и тип отказа на другом входе, поэтому сначала сопоставить exact MIR и вид операции, а затем дополнить существующий issue или открыть отдельный, если механизмы различаются. [Panic branch][paniccode] · [Сохранённый input][b3flagfixture] · [PANIC-NOTE][panicnote] · [Логи base/fix][b3baseci] · [Лог fix][b3fixci] · [#4854][issue4854]

Для отдельного патча снять per-harness исходный и инструментированный MIR на тех же SHA, выбрать минимальный воспроизводящий harness и зафиксировать `MemoryInitOp`, тип, const allocation/байты и provenance. Если constant operand можно корректно материализовать с его init state, поддержать эту форму и проверить positive/negative. Если семантики для формы нет, выдать точный Unsupported до попытки взять адрес. Для backend-only B3 это унаследованная граница. Наблюдавшийся флаговый вход должен остаться в triage, а в B3 PR нужно явно оставить default-check scope. [Flag-off diff][b3diff] · [Как снять MIR][mirdump]

## 12. Вычитка двух PR drafts

### B1

| Место | Правка |
|---|---|
| Описание и пример | Источник подтверждает потерю target. Представить custom-MIR пример как regression fixture и приводить measured base verdict только после matched-run. |
| Changes | Сузить обещание об ошибке резолюции до local visitor либо синхронизировать с global passes. Убрать общее обещание union shadow для MIR-backed shim до проверки ABI. |
| Shim diagnostic | Исправить комментарий в fixture. По pinned rustc и логу срабатывает внешний guard по item-level predicate. Переформулировать диагноз после выбора корректной политики body availability. |
| Testing | Привести focused результаты на том же source/test tree, full status cancelled и macOS 14 без test steps. Убрать причинное объяснение отмены без отдельной ссылки. |

Предлагаемый заголовок — `Preserve memory initialization checks at unresolved calls`.

> Visit call operands once and append the unsupported-call diagnostic before publishing the same terminator target. This retains operand checks and any union argument loads attached to a statement-free entry block. Emit the function-pointer and virtual-call diagnostics in the local pass, including when delayed-UB analysis has no targets.

После исправления описать точную политику резолюции и shim, которую реализует финальный экспорт. Сохранить `Refs #3300` и лицензионное подтверждение. [B1 draft][b1draft] · [Tracking issue][issue]

### B3

| Место | Правка |
|---|---|
| Reproducer | Короткий пример в черновике опускает ZST projection из реально исполненного harness. Сослаться на точный fixture и его лог, а короткий вариант обозначить illustrative, если он остаётся. |
| Scope | Указать physical empty-unit payload и сохранённый logical arm type. Заменить формулировку про «Rust-layout payload» и ограничить indexing claim. |
| Testing | Заменить «full CI for that placement remains pending» на точный head `6db3c4dab`, три завершённых Linux regression jobs и cancelled overall. Обе macOS jobs без завершённого regression результата. Отдельно указать matched seven-harness исход на `9dddcb113`. |
| Related issues | `Related to #5085` для аналогичного backend invariant. Указать `#4854` как triage аналогичной compiler panic при опциональном uninit-checks. |
| Signoff | Сохранить AI disclosure и добавить стандартное предложение из шаблона ниже. |

Предлагаемый заголовок — `Avoid CBMC aborts when copying padded unions with zero-sized fields`.

> Typed copies of padded unions with zero-sized array fields can abort CBMC under the default checks. Use the existing empty-unit representation for the physical payload inside the padded wrapper and retain the original logical field type. In matched tests, four harnesses aborted on the base and all seven passed with the backend change. A separate compiler panic under `-Z uninit-checks` reproduced on both tested trees.
>
> By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

[B3 draft][b3draft] · [Upstream PR template][prtemplate]

## 13. Структура коммитов

- **B1.** Один самостоятельный commit с retention/classification fix и финальными тестами. Два логических коммита production/tests приемлемы, если удобнее для review. Расширение shadow transfer через shim отделить, если для него нужны отдельная ABI модель и новые controls. При этом сохранить нужную обработку ordinary shim без shadow и не возвращать blanket rejection всех shim: ранний B1 показывал регрессии drop glue. Сохранить только final expected files. [Commit proposal][b1commits] · [Ранний B1 log][b1early]
- **B3.** Один fix-plus-tests commit с конечным расположением в general expected suite. Два коммита тоже возможны, если первый демонстрирует исходный regression с неизменённым fixture. CI-only workflow не входит в оба экспорта. При перепаковке сверить tree ID и diff. Исторические runs ссылать на их реальные SHA, даже если дерево итогового squash совпадает. [B3 production][b3production] · [Relocation][b3relocation]

## 14. Что осталось перед review

**B1.** Исправить или убрать из текущего scope новые шим-решения, основанные на definition-level `has_body()`. Согласовать local classification с initial-target collection и points-to, чтобы неподдерживаемая форма не могла попасть в неподходящий body unwrap. Добавить точный positive для достижимого generated shim или явно сохранить узкую политику без новой передачи union shadow через shim. Проверить plain и seeded на финальном экспорте с наблюдаемыми operand properties и подтверждённой активацией delayed UB там, где требуется. Сопоставимый base запуск нужен для measured false-success claim. После изменения кода обновить targeted и штатный gate на точном tree. Отменённый macOS 14 job указать по факту. [B1 full][b1full] · [B1 focused][b1quick]

**B3.** Исправить draft, приложить matched логи и точный fixture, добавить signoff и связать #5085/#4854 по scope. Linux CI на final head и изолированный default-check differential достаточны для начала review узкого backend fix. macOS остаётся открытой платформенной проверкой перед утверждением о полной матрице. Отдельный flag-on ICE не блокирует review backend fix при указанной границе. [B3 full][b3full] · [Base log][b3baseci] · [Fix log][b3fixci]

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/0161edb6cc252a449b22da052cd3c67e80718b72/research/challenge-8/kani-k1/AUDIT-BRIEF-KANI-B1-B3.md
[base]: https://github.com/model-checking/kani/commit/bf9c58e662fd65c64381ef2ac97a6397ffc0693a
[issue]: https://github.com/model-checking/kani/issues/3300
[issue5085]: https://github.com/model-checking/kani/issues/5085
[issue4854]: https://github.com/model-checking/kani/issues/4854
[b1diff]: https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662fd65c64381ef2ac97a6397ffc0693a...d5f072f2bcf61a04d84bb0e8b54115f3011252fc
[b3diff]: https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662fd65c64381ef2ac97a6397ffc0693a...6db3c4dabd4a368314eb8e2b71d21d1eee721593
[b1quick]: https://github.com/Tiramisu-Cake/kani/actions/runs/43110714635/job/130825677396
[b1cihead]: https://github.com/Tiramisu-Cake/kani/compare/d5f072f2bcf61a04d84bb0e8b54115f3011252fc...0e83acc6823d25949f7d303e70a69441d2cfb138
[b1full]: https://github.com/Tiramisu-Cake/kani/actions/runs/43112332778
[b1format]: https://github.com/Tiramisu-Cake/kani/actions/runs/43112332487
[b1deny]: https://github.com/Tiramisu-Cake/kani/actions/runs/43112332869
[b1oldquick]: https://github.com/Tiramisu-Cake/kani/actions/runs/43108072253/job/130816518284
[b1early]: https://github.com/Tiramisu-Cake/kani/actions/runs/43104793815/job/130805183991
[b3baseci]: https://github.com/Tiramisu-Cake/kani/actions/runs/43115481098/job/130842240466
[b3fixci]: https://github.com/Tiramisu-Cake/kani/actions/runs/43115485052/job/130842254653
[b3full]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467
[b3linux]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467/job/130849943009
[b3format]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117729474
[b3deny]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117729608
[regress]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/scripts/kani-regression.sh#L49-L100
[b3production]: https://github.com/Tiramisu-Cake/kani/compare/dc590936c56556ecfb20fc714da06fcb13e884db...9dddcb1134f8a55ee3a4451df9513941ca3c8fc3
[b3relocation]: https://github.com/Tiramisu-Cake/kani/commit/6db3c4dabd4a368314eb8e2b71d21d1eee721593
[b1entry]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L39-L77
[b1call]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L249-L274
[b1flush]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L454-L465
[b1insert]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/body.rs#L268-L323
[b1fixtures]: https://github.com/Tiramisu-Cake/kani/tree/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls
[b1assign]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L113-L130
[b1stmtflush]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L236-L259
[b1seedresolve]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs#L105-L135
[b1global]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs#L70-L114
[b1points]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L308-L384
[b1pointsstart]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L194-L203
[b1body]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L448-L461
[b1reach]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/reachability.rs#L421-L439
[b1phase]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L92-L124
[b1abi]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L945-L1009
[llvm]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L904-L920
[b1shimcode]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L358-L419
[b1buffer]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/library/kani_core/src/mem_init.rs#L371-L409
[paniccodeb1]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs#L122-L140
[b1guard]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs#L94-L110
[b1basecall]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L260-L277
[b1partial]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs#L19-L32
[b1init]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/entry-initialized-plain.rs
[b1shimtest]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/shim-plain.rs#L12-L20
[b1shimgold]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tests/expected/uninit/unresolved-calls/shim-plain.expected
[rustmono]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_public/src/mir/mono.rs#L50-L70
[rustbridge]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_public_bridge/src/context/impls.rs#L77-L103
[rustresolve]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_ty_utils/src/instance.rs#L321-L348
[mirdump]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/docs/src/rustc-hacks.md#L239-L249
[goldens]: https://github.com/Tiramisu-Cake/kani/blob/d5f072f2bcf61a04d84bb0e8b54115f3011252fc/tools/compiletest/src/runtest.rs#L564-L597
[b3typ]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs#L1286-L1334
[b3unit]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs#L556-L559
[b3component]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/cprover_bindings/src/goto_program/typ.rs#L120-L164
[b3serialize]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/cprover_bindings/src/irep/to_irep.rs#L133-L153
[b3place]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/place.rs#L508-L541
[b3aligned]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/main.rs#L104-L140
[b3abi]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L945-L972
[b3tests]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/main.rs
[b3zstassign]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L306-L309
[b3copies]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/tests/expected/zst-union-arm/main.rs#L56-L102
[b3oldfixture]: https://github.com/Tiramisu-Cake/kani/blob/dc590936c56556ecfb20fc714da06fcb13e884db/tests/expected/uninit/zst-union-arm-no-checks/main.rs#L56-L67
[b3flagfixture]: https://github.com/Tiramisu-Cake/kani/blob/dc590936c56556ecfb20fc714da06fcb13e884db/tests/expected/uninit/zst-union-arm-uninit-checks/main.rs
[paniccode]: https://github.com/Tiramisu-Cake/kani/blob/6db3c4dabd4a368314eb8e2b71d21d1eee721593/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs#L122-L140
[panicnote]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/PANIC-NOTE.md
[b1draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/PR-DRAFT.md
[b3draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b3r/PR-DRAFT.md
[b1commits]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/950fe1f288c4c56e961a7c40bf240a826bd36cbc/research/challenge-8/kani-k1/kani3300/b1pr/COMMITS.md
[contributing]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/CONTRIBUTING.md#L23-L37
[prtemplate]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/.github/PULL_REQUEST_TEMPLATE.md#L9-L11
[cbmcbits]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/util/simplify_utils.cpp#L262-L359
[rustunion]: https://doc.rust-lang.org/reference/items/unions.html#reading-and-writing-union-fields
