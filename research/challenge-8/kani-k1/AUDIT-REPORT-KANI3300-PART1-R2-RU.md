# Независимый аудит Kani #3300, Part 1, раунд 2

12 ноября 2026 года

**Вердикт для `a0a2386001`: доработать перед отправкой upstream.** A1 исправляет перенос padding на проверенных формах. A2 исправляет композицию смещений для проверенных layout. A3 добавляет проверки парности к протоколу передачи состояния и устраняет часть проблем первого раунда. У кандидата остаются воспроизведённый ложный отказ в обычном сравнении массивов и статически подтверждённая потеря проверки при неразрешённом вызове. Полный откат `raw_eq` восстановит прежнюю политику самого intrinsic, но оставит непроверяемый путь через новые операции над flat-слотами. [Бриф R2][brief] · [Кандидат][candidate] · [Upstream #3300][issue] · [Последний быстрый прогон][quick]

## Ревизии и проверенные результаты

| Объект | Установлено |
|---|---|
| Исходный бриф | `verify-rust-std@c04750eea087c28929d96cd95cd4b9e775d56021`. Связанные исследовательские материалы в брифе закреплены на `6491a749c2`. [Бриф][brief] |
| Upstream, первый раунд и R2 | База `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`, первый раунд `1cd96e354ec45346b61c245554a50a8af8cb5ce7`, R2 `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`. Между первым раундом и R2 16 коммитов. От базы до R2 71 файл, +2951/−248. Локальный `git diff --check` от базы и от первого раунда прошёл. [Полный diff][upstreamdiff] · [Diff раунда][rounddiff] · [Первый аудит][r1] |
| Финальный быстрый CI | Job `130853314408` прогнал `3b90da205860ebd579c4ae418c9d20ef66b5bd9a`. Его родитель — кандидат, diff меняет только `.github/workflows/`. Форматирование, сборка и Clippy прошли. По четырём наборам 22/0, 93/1 (2 ignored), 14/0, 1/0, где значения означают прошедшие и упавшие селекторы. Итог job — failure. Последний script PASS имеет ограниченную силу: скрипт проверяет текст вывода, без проверки exit status Kani. [Лог][quick] · [Workflow и выборки][quickworkflow] · [Diff workflow][cihead] · [Скрипт][weakscript] |
| A1 | `43105165870` — 85/0 (2 ignored) в основном uninit-наборе. `43105207965` — 81/4 (2 ignored) на `1cd96e354` с теми же семью новыми fixture. Во всех четырёх ожидаемо негативных случаях старый код вывел `VERIFICATION:- SUCCESSFUL`. Файлы тестов между A1 и компаратором совпадают. [A1][a1run] · [Дифференциальный прогон][a1old] |
| A2 / A2R / A2R2 | Blanket Unsupported дал четыре упавших селектора, включая три существующих и новый raw_eq-селектор. A2R и A2R2 дали по 90/1 (2 ignored) после изменения набора. В A3R прошли goldens для reverse-array, raw_eq, call-move, call-pairing и unsupported-pairing. [A2][a2run] · [A2R][a2rrun] · [A2R2][a2r2run] · [A3R][quick] |
| Miri | Проверены журналы трёх указанных прогонов, включая отдельные запуски с обычным Stacked Borrows и с `-Zmiri-disable-stacked-borrows`. Они относятся к конкретным probe и к pinned nightly. [Первый прогон][miri1] · [Уточнение][miri2] · [Move/Copy, записи и повторная инициализация][miri3] |

Статический аудит выполнен по точному checkout. Числа и свойства CI сверены с журналами GitHub Actions. Локального повторного запуска Kani/CBMC/Miri не было. Полную матрицу для R2 и текущую возможность запуска Actions на форке подтвердить по этим журналам нельзя. Отчёт не присваивает более поздним деревьям результаты старых сборок.

## Блокирующие находки

### 1. `raw_eq` ломает обычное сравнение массивов и откат расширяет область риска

В `43118703581` упал один селектор `maybe-uninit-initialized`. Это **два harness с одним и тем же упавшим свойством** `SpecArrayEq::spec_eq.safety_check.2` в каждом. `.1` успешен в обоих. Имена harness — `array_value_as_used_by_merge_output` и `partial_copy_preserves_written_byte`. Оба harness сравнивают результат assume_init с литералом массива. По порядку вставки проверок вероятный источник — правый операнд. Привязка к конкретному runtime-объекту требует MIR/GOTO. Формулировку брифа о двух отдельных источниках сбоя, временном массиве и promoted-константе, следует оставить рабочей гипотезой. [Лог A3R][quick] · [Fixture, включая оба harness][initialized]

Кандидат добавляет проверку полного диапазона обоих операндов. Для `&T` visitor строит `CheckAs<[u8; size_of::<T>()]>`, а `mk_cast` для reference-place берёт `AddressOf(*place)`. Backend сводит ненулевой случай к `memcmp` на весь размер. Исходники подтверждают направление вычисления адреса. Для direct constant reference остаётся отдельный путь приведения. Помимо `raw_eq`, `CheckAs` применяется при transmute raw pointer → reference, и здесь сырой указатель по-прежнему идёт прежней веткой `mk_cast`. [Visitor][rawcode] · [Построение операнда][cast] · [Второй потребитель][castother] · [Backend][rawbackend]

Upstream `bf9c58e66` и первый раунд `1cd96e354` пропускают retained `raw_eq`. Но upstream проверяет layout при bytewise copy типизированным указателем на `[MaybeUninit<T>; N]` и приходит к вложенному union, для которого выставляет Unsupported. R2 допускает эту операцию через `for_storage`. Поэтому откат делает достижимым новый путь к unchecked byte read. Достаточно скопировать flat-массив слотов с unwritten byte через такой указатель, затем сравнить область retained `raw_eq`. Это вывод из исходников, для его фиксации в PR нужен дифференциальный прогон. Простая инициализация массива хуже подходит для сравнения, поскольку upstream visitor может потерять отложенный Unsupported, если после соответствующего `Assign` блок сразу заканчивается. [Upstream Copy и skip list][basecopy] · [Upstream layout][baselayout] · [Upstream Assign][baseassign] · [R2 выбор storage layout][dispatch] · [R1 skip list][r1skip]

**Решение.** Для объёма из брифа полное покрытие `raw_eq` можно вынести в отдельный патч, если в Part 1 есть узкая, проверяемая граница для вновь допускаемых путей и согласована остаточная совместимость обычного сравнения. Сам по себе (a) такого условия не выполняет. Если реализуемой границы пока нет, оставить блокер или сузить экспорт до независимо проверенного поднабора. Blanket Unsupported (c) даёт ложный отказ на обычном array equality. Проверку по одному типу ссылки (b) нельзя считать доказательством происхождения байтов. [Опции из брифа][brief] · [Лог blanket Unsupported][a2run]

### 2. B1: при неразрешённом вызове локальный проход теряет собственную проверку

`visit_terminator` сначала обходит операнды. В ветке `Err` он обходит их повторно, кладёт `Unsupported` в `current_target` и выходит раньше общего `self.targets.push`. Вместе с диагностикой исчезают проверки операндов, а в entry block без statements также могут исчезнуть запланированные `LoadArgument`. Delayed UB ставит свой guard, когда активен, но сам проход пропускает инструментирование при пустом наборе initial targets. Удаление raw_eq seeds при откате дополнительно меняет случаи, в которых этот резервный guard появляется. [Ранний выход][b1loss] · [Общий push][termpush] · [Entry loads][entry] · [Delayed guard][delayedguard] · [Условие запуска][delayed]

Нужен B1 или эквивалентный локальный фикс до upstream review. Провести единый обход операндов, сохранить накопленные операции ровно один раз, определить порядок диагностики относительно чтений и согласовать классификацию shim между анализом и инструментированием. Отдельный B1 вырос из upstream, прошёл отдельный быстрый прогон и содержит собственную политику MIR-backed shim. [Лог отдельного B1][b1run] При переносе сохранить симметрию A3 для caller/callee. Проверки нужны с пустыми и непустыми delayed seeds, с неразрешённым вызовом как первым terminator и с уже собранным чтением операнда. Для негативов проверять нужное свойство, чтобы один Unsupported не скрывал потерю другого. [B1 production, resolver/flush][b1commit] · [B1 shim policy][b1shim] · [B1 tip][b1tip]

## Ответы на вопросы брифа

### 1. Можно ли вернуть (a)

Как временная политика intrinsic — только после согласования с maintainer, с описанием конкретного пробела и matched-прогоном. Для текущего широкого экспорта — нет без защиты вновь достижимых путей из §1. Разделять нужно три сравнения: upstream, R1 и R2 с откатом. R1 уже расширял support domain, поэтому его успех не означает parity с upstream. Для доказательства потери покрытия сравнить с R2 без отката, где свойство для unwritten byte действительно достигается. [Upstream skip][baseskip] · [R1 skip][r1skip] · [R2 checks][rawcode]

### 2. Что именно вызывает ложные отказы

Подтверждены failure `.2` в обоих harness и переход diagnostic `*const [u8;4]` → `[u8;4]` после A2R2 без устранения отказа. Анонимное promoted allocation — конкретный пробел в анализе: initial-target visitor признаёт только `GlobalAlloc::Static` для констант, points-to constant paths учитывают named statics, а `MemLoc` не хранит анонимный allocation ID. Delayed visitor ставит `SetRef` по найденным mutating places. Временный результат обычного вызова может получить setter через relevance. Из одного лога неизвестно, был ли он найден и исполнен. Зависимость от порядка harness пока гипотеза. [Логи A2R/A2R2][a2rrun] · [Initial targets][targets] · [Points-to для констант][ptconst] · [MemLoc][memloc] · [Delayed setters][delayedsets]

На одном и том же export снять `RUSTFLAGS=--emit=mir` и points-to graph. Сопоставить обе исходные ссылки со всеми вставленными `CheckAs` в точном MIR `SpecArrayEq::spec_eq`, включая lowering сравнений и allocation ID для констант. Для каждого check записать исходный operand, runtime `object_id/offset/extent`, выбранный witness, значение и последний setter/transfer по этому байту. Для call destination проследить нормальное ребро возврата и запись в destination, затем адрес, который реально получает equality. Для promotion сверить `AllocId`, диапазон и маску `Option<u8>` в referent allocation. Затем сравнить points-to/relevance и вставленные вызовы при одиночных harness и при совместном запуске в обоих порядках. Так различаются адресная ошибка, пропущенная запись, ошибка отбора и эффект кэша. [Как снять MIR][mirdump] · [Обход и cache update][delayed] · [Состояние witness][witness]

### 3. Что сделало бы (b) обоснованным

Для каждой ссылки нужны конечное множество возможных объектов и корректные смещения, доказательство покрытия полного диапазона и определённые правила переноса состояния на всех достигающих путях. Для mutable storage это охват всех релевантных записей, reset/deinit, raw copy, typed transfer и overwrite, с алиасами и повторным использованием памяти. Для immutable allocation допустимо отдельно доказать init mask по фактическим байтам. Полезно различать доказанную инициализацию всего диапазона, полностью моделируемый диапазон с требуемой проверкой и неизвестное происхождение. Последнее при заявленном покрытии требует Unsupported или отдельной реализованной семантики. Тип `&[u8; N]`, alias graph на уровне объекта или отсутствие hits сами по себе такого доказательства не дают. [Текущий points-to graph][memloc] · [Текущий check][rawcode]

### 4. Какие setters и transfers допустимы

Для нового обычного return temporary установить data mask только на normal-return edge после доказанной типизированной инициализации соответствующим callee/моделью. Если тип переносит shadow, использовать фактическую передачу, включая false data. Для обычного T учитывать padding и текущие границы supported layout. Сеттер должен относиться к тому же destination и диапазону, который затем наблюдает check. Для immutable promotion брать маску из referent allocation с учётом смещения и длины, включая `None`. Применять только к доказанно неизменяемому объекту. Подстановка полного true по типу ссылки или по одному успешному сравнению способна скрыть unwritten bytes.

Текущий witness стартует с false для выбранной пары object/offset и пропускает другие байты. Практичное направление — доказать полноту инструментирования до доступа или отдельно моделировать provenance/доступность shadow, сохранив неинициализированный байт как самостоятельный случай. Неизвестное происхождение не должно делать положительный результат проверки. Для новых setters проверить, что они не сбрасывают корректно перенесённые false и не меняют порядок обновлений. [Инициализация модели][witnessstart] · [get/set][witness] · [Реальные байты константы][constmask]

### 5. Достаточность raw_eq-контролей

Текущий fixture хорошо покрывает локальные и переданные по ссылке обычные массивы, полностью записанные слоты, отдельные holes слева и справа и padding. Трёхбайтный массив и 12-байтный padded payload выбраны с учётом InstSimplify. Scalar и ZST source controls полезны для lowering. Для retained-intrinsic coverage нужен сам вызов в MIR. ZST по backend возвращает true, диапазон пуст. Прямые и прокинутые через функцию promoted references, динамический выбор между promoted и локальным объектом и alias/offset через raw copy следует проверять отдельно. Существующий `maybe-uninit-initialized` сохранить, добавив минимальный изолированный positive. Проверять точное свойство у каждого negative. Compiletest сопоставляет подстроки и может повторно использовать один diagnostic match для нескольких строк expected, если они не сгруппированы. Для такого golden проверять per-harness JSON properties или запускать harness по одному. [RawEq fixture][rawtests] · [Backend][rawbackend] · [Compiletest][goldens]

Минимальный matched набор на upstream, R1, текущем R2 и финальном варианте: оба существующих legal array-equality harness, явный legal retained raw_eq, оба существующих negative с отдельной фиксацией свойств и один flat-slot raw-copy кейс из §1. Для последнего сохранить MIR, в котором копирование остаётся над массивом слотов, и отдельно подтвердить достижимость raw_eq. Если выбран scope guard, его ожидаемый исход для нового пути — точный Unsupported до сравнения. Если выбран полный model — нужный byte-read failure. Пустой диапазон и fully initialized storage должны проходить в рамках заявленной поддержки. [Семантика raw_eq][rustraweq] · [Семантика bytewise copy][rustcopy]

### 6. Закрывает ли A1 padding P0

Да, для показанных форм. `for_typed_storage` строит D(T), а массив повторяет маску по stride rustc. `SetStorage` пересекает её с init mask константы. Typed copy и аргумент/return применяют preserve mask, сохраняя false у исходного data byte, а raw copy применяет all-true mask и переносит фактическое состояние выбранного source byte. Это соответствует различию между typed transfer и bytewise copy. Пара прогонов A1 с идентичными тестами подтверждает именно исходный P0 для assignment/argument/return и слота массива. Для более широкого claim нужны проекции, разные alignment/stride, поддержанные формы constant/aggregate/repeat и отдельные ZST controls. [Layout][layout] · [Constant mask][constantset] · [Typed/raw copy][typedraw] · [Witness transfer][copyid] · [A1][a1run] · [Старый кандидат][a1old] · [Rust MaybeUninit][rustmu]

### 7. Закрывает ли A2 Pat и enum offsets

`Pat` передаёт `current_offset`. Enum с несколькими вариантами сравнивает data masks в локальных координатах, затем единожды сдвигает согласованный payload. Тег уже расположен по внешнему offset. Array recursion добавляет stride к offset элемента. Это согласованная композиция для поддержанных layouts. Niche encoding и различающиеся masks остаются вне модели. Рекомендую добавить nested array с ненулевым индексом и ненулевым offset поля внутри второго элемента, чтобы за один тест проверить оба сдвига. Reverse `[MaybeUninit<T>; N] → [T; N]` имеет явный guard. Финальный лог подтверждает его диагностический текст для initialized и partial fixture, то есть проверенная форма пережила simplification. Другие lowering того же исходного Rust следует оценивать по фактическому MIR. [Array layout][arrayoffset] · [Enum][enumoffset] · [Pat][patoffset] · [Reverse guard][reverse] · [Golden][reversegold] · [Лог][quick]

### 8. Достаточен ли A3-протокол

На обычном nonforeign bodyful `InstanceKind::Item` caller и callee используют один predicate. При входе сверяются signature, количество записей и порядок индексов. Store/Load используют исходный номер параметра, в том числе при gaps с обычными параметрами. Layout size проверяется для выбранного аргумента, return0 выбирается обязательно. Все snapshots выполняются до сброса источников. Все entry loads потребляют буфер до входа в тело. При корректно инструментированном caller/callee демонический выбор каждого аргумента обеспечивает отдельную ветвь, на которой false source state достигает соответствующего destination. Установка D(T) на ветвях без переноса допустима только при наличии ветвей с переносом каждого исходного witness и одинаковых парах. Сам буфер не гарантирует инструментирование на всех входах. B1 даёт конкретный пример потери entry load; DFCC, stubs и специальные roots требуют проверить на фактическом lowered MIR. Текущие mixed, nested, repeated и return0 fixtures дают полезные конечные контроли. Predicate не проверяет backend hook interception: например, generic UntrackedDerefHook может материализовать return в backend вместо выполнения MIR callee. Достижимость такого shadow return на legal PFC проверить отдельно, прежде чем распространять pairing claim на rewritten calls. [Вход][entry] · [Caller][caller] · [Predicate][paired] · [Модель][protocol] · [Pairing fixture][pairtest] · [Backend hook dispatch][hookdispatch] · [UntrackedDerefHook][hook]

Проверить также два статических края. `transfers_shadow` распознаёт slice, тогда как Store/Load используют `T: Sized` и размер одного элемента, игнорируя slice metadata. Backend поддерживает отдельные by-value DST-вызовы с `unsized_fn_params`, поэтому граница должна быть явной. Поддержку slices заявлять по pointer/reference, а by-value DST отклонять до построения Store/Load, пока нет динамического extent model. Для sized ZST оставить pairing счётчиков, проверить на noinline by-value ABI, где helpers сейчас получают pointer object/offset даже при нулевом размере. Материализация constant `StoreArgument` покрывает MaybeUninit. Для обычного union `operand_ty` ожидает place и для constant доходит до `unreachable!`. В отдельном B3 quick log зафиксирован ICE в этом `operand_ty`. На R2 тот же путь подтверждён статически, отдельного воспроизведения нет. Нужен тест с сохранённым constant operand либо ранний Unsupported. [B3 quick log][b3quick] Обычный union с разными field masks использует full-extent preserve mask. Один return0 fixture подтверждает pairing для своей формы и не обосновывает универсальную семантику padding arbitrary union. [Shadow predicate][shadow] · [By-value DST fixture][dstfixture] · [Constant argument][constarg] · [Operand invariant][argoperand] · [Union transfer mask][unionmask] · [Модель][protocol]

### 9. Совпадает ли Call(Move) с Miri и Kani

Код выполняет snapshot всех shadow-аргументов, затем сбрасывает полный extent каждого `Move(place)` непосредственно перед вызовом. Call через временную копию, обычные assignment/field Move, Copy и Forget не подпадают под этот reset исходного объекта. Логи pinned Miri подтверждают разницу на контролируемых probes. При default Stacked Borrows старый alias может стать недействительным уже по aliasing. С отключённым SB in-place Move остаётся uninitialized после вызова, в том числе если callee пишет в свою by-value копию. Copy с записью callee оставляет исходное значение. Повторная инициализация старого места подтверждена для initializedness при отключённом SB. Эти данные не подтверждают законность чтения по старому alias при обычном SB. [Очередность операций][caller] · [Miri probes][miri3]

`UnwindUnreachable` согласован с panic=abort и позволил fixture собраться. Подтверждена работоспособность точного fixture. Отрицательные goldens сами по себе не исключают независимых ошибок. Проверить actual Kani MIR, normal edge, projected Move и реинициализацию в вызывающем коде. Запись в формальный параметр и запись через alias исходного места — разные операции. Два snapshot перед clear предотвращают потерю состояния от порядка сброса, но не моделируют alias protector Miri или запрет перекрытия Move/return place. Поддержку aliasing заявлять только для форм, которым соответствует отдельное доказательство или точный контроль. [Custom MIR][movetest] · [Miri log][miri3] · [Insertion ordering][insertion]

### 10. Intrinsic scope и `integer_max`

`Forget` обрабатывается первым как потребление без чтения payload, затем guard перехватывает unmodeled by-value shadow args/returns до skip list. `black_box` с таким значением попадёт в Unsupported. Модели raw copy, byte fill и compare принимают указатели и сохраняют свои ветки. `VolatileLoad/Store` и подобные операции с by-value shadow на входе или выходе ограничены этим guard. Слово «copies» в PR следует привязать к реально моделируемым операциям. `argument_count.max(1)` удалён из протокола, текущий model задаёт счётчики напрямую. Это снимает конкретную зависимость от `integer_max`. До ремонта A2R2+A3 имел 64/30 (2 ignored), включая `integer_max` Unsupported и MIR validator ICE. После ремонта 93/1 на том же наборе. Восстановились 29 селекторов, новых провалов нет. [Лог до A3R][a3before] Весь граф достижимых private helpers и результаты на иных backend/layout из этого не следуют. Delayed points-to анализирует исходные тела и может попасть в собственный unimplemented для неизвестного intrinsic до того, как локальный guard подействует в verification. Seeds от raw_eq также могут впервые включить этот проход для unit с рекурсивным вызовом. Буфер A3 не даёт рекурсивной поддержки points-to. [Points-to intrinsic dispatch][ptintrinsic] · [Рекурсивный обход][ptrecursion] · [Intrinsic dispatch][intrinsic] · [A3R fix][a3rfix] · [Model][protocol] · [Лог][quick]

### 11. Что из B1, B3, B4 должно войти в Part 1

- **B1 требуется в эквивалентной по эффекту форме** для обещанного fail-closed поведения. При интеграции учесть, что A2R initial-target visitor имеет собственный `Instance::resolve(...).unwrap()`. Неуспешная резолюция на этапе seed collection может безопасно означать отсутствие intrinsic target, если диагностику гарантированно выставляет основной проход. Отдельно проверить seeded bodyless shim: global points-to может анализировать исходный call раньше verification и вызывает `body().unwrap()` для regular call. Для MIR-backed shim проверить argument-only и return-only: существующий FnOnce fixture содержит оба направления и один guard может скрыть отсутствие второго. [Points-to regular call][ptbody] · [FnOnce fixture][shimtest] [B1 diff][b1diff] · [Initial-target resolver][seedresolver]
- **B3 нужен для claim о padded ordinary unions с zero-sized arms.** Код B3 изменяет backend-представление нулевого arm, которому требуется внешний padding. Из исходников нет основания считать его общей зависимостью canonical direct `MaybeUninit<T>`, у которого пустой arm — unit, а для полностью ZST слота внешнего padding нет. Проверить MU ZST copy/reset и by-value argument/return. У отдельной B3-ветки общий full-run отменён, а quick run сохраняет отдельный failure с uninit checks. Если экспорт включает эту область, после интеграции B3 нужны свои проверки. [B3 full run][b3run] [B3 production][b3commit] · [B3 fixtures][b3tip]
- **B4/realloc и foreign effects.** Для `__rust_realloc` текущий visitor не переносит initialized prefix и не обновляет shadow при изменении extent. Resolved non-shadow foreign call может пройти без эффекта на pointee, хотя имеет указатель. Для области flat stack scratch эти пути можно отдельно исключить. Для claim о heap/foreign operations, влияющих на отслеживаемые байты, нужен model или достижимый Unsupported. Аналогично не расширять claim до G1/compound storage. [Ветки allocation/foreign][foreign] · [Границы брифа][brief]

### 12. Какой gate нужен

| Проверка | Критерий |
|---|---|
| Обычный и opt-in regression | Прогнать полный штатный `scripts/kani-regression.sh` и соответствующие workflow jobs для точного export SHA. Зафиксировать regression targets и окружение. Быстрый gate полезен перед полной матрицей. [Upstream CI][fullci] |
| Положительный PFC | Legal roundtrip без контрактов, с legal `modifies` и с теми же options на base/export. Проверять успешную верификацию и достижимость полезной проверки. [Draft PFC evidence][draft] |
| Frame и clause | Пользовательская запись за `modifies` должна падать на frame property. Отдельно подтвердить reached uninit failure в clause, legal control и отсутствие ложного frame violation от private shadow state. Старые goldens оставить. Backend разрешает изменения маркированного private static в DFCC, что само по себе не проверяет достижимость и правильность instrumented property. [DFCC implementation][dfcc] · [Frame fixture][frame] · [Clause fixture][clause] |
| Multi-harness | Сравнить одиночный запуск с совместными, в обоих порядках, проверять одинаковый исход/порядок свойств для shared monomorphization. Один `BodyTransformation` используется для нескольких harness в unit, а delayed pass пишет инструментированное тело обратно в cache. Это подтверждает механизм зависимости от порядка. Вклад в текущий отказ ещё предстоит установить. [Общий transformer][cache] · [Cache update][delayed] |
| Layout и цели | Покрыть поддержанные fixed/nested masks, projected offsets, ZST, flat slices, overwrite/overlap, положительные и отрицательные transfer, B1 и raw_eq. Отдельно проверить прямое присваивание через `(*ptr).field`: local setter распознаёт конечную проекцию Deref, а существующий positive использует `addr_of_mut!(field).write(...)`, другую форму MIR. Использовать поддержанные штатной матрицей архитектуры, как минимум Linux x86_64 и AArch64, включая фактический target layout и pinned compiler. [Upstream matrix][fullci] · [Local setter][fieldsetter] · [Fixture][initialized] |
| SmallSort | Запустить отдельно точный legal и negative SmallSort scratch case перед claim о применимости. Хранить сценарий, версию toolchain, тип/длину и свойства. [Бриф][brief] |

Таймаут и Kani-reported OOM классифицировать как ресурсный результат. Для сравнения зафиксировать base/export SHA, solver, flags, bounds, reachable property, лимиты времени/памяти, exit reason и, если доступен, фактический peak RSS. Успех base при повторяемом OOM у export показывает регрессию ресурса, даже если свойство не вычислено. Для утверждения об отсутствии семантического изменения нужен прошедший matched legal control, плюс нужный reached failure в отрицательном контроле. Старые GCB-результаты с несовпадающими деревьями такой базы не дают. [История PFC в черновике][draft]

### 13. Что нужно для ready-for-review

1. Выбрать и зафиксировать policy raw_eq, устранить legal regression и выполнить matched набор. Закрыть локальную потерю операций B1 с регрессиями plain и seeded. Сузить область, где требуется поддержка DST, foreign/realloc и ZST ordinary unions, до той, которую можно явно защитить.
2. Пересобрать review branch от проверенного upstream base, содержащий только нужные source/test commits. У текущего исходного кандидата 17 commits поверх проверенной базы, и сам candidate diff не содержит CI workflow. CI-only коммит для upstream не нужен. Повторить проверку merge-base и diff после исправлений, приложить полный SHA, tree и goldens. [Upstream compare][upstreamexternal] · [CI-only diff][cihead]
3. Провести targeted и full gate. Приложить точные run IDs, ожидаемые reached properties, известные resource limits и явные unsupported границы. Отдельные патчи разумны для полноценного raw_eq/anonymous allocations, B3 при MU-only scope, B4 realloc, G1 compound layouts и общей стратегии shared-cache. Cache issue становится блокером этого экспорта, если одинаковый harness меняет исход из-за порядка в заявленной области. [Бриф][brief] · [Shared cache][cache]

## Вычитка черновика upstream PR

Найден [UPSTREAM-PR-DRAFT.md][draft]. Он описывает прежний v2 и локальный export `c39cc1121c…`, который отмечен как unpushed. Ветки и diff R2 подтверждают другое дерево. Разделы о 15 fixtures, шести goldens и GCB builds относятся к прежней упаковке. Перед отправкой таблицу заменить результатами на фактическом export, а исторические PFC прогоны использовать только для обоснования известных ограничений. [Результат упаковки v2][oldexport] · [Полный diff R2][upstreamdiff]

| Место черновика | Правка |
|---|---|
| Строки 3–11, описание | Назвать exact supported forms, различить bytewise copy и typed transfer. Явно указать направление flat-array conversion и поддерживаемые формы aggregates/repeats. Заменить «with a MIR body» на «ordinary nonforeign MIR items» для by-value shadow. |
| Строки 13–16, argument buffer | Описать snapshot witness offset/value при живом источнике, typed mask при восстановлении и обязательный return0. Вместо общей фразы о DFCC указать точные legal/frame/clause outcomes финального export. |
| Строки 18–19, exclusions | Указать reverse array conversion, unsupported layouts, by-value DST, compound slots и arbitrary-union pointees. Описать indirect/foreign/shim границы по финальному guard и перечислить актуальную policy raw_eq. Сохранить `Refs #3300`, поскольку tracking issue шире этого патча. |
| Строки 21–49, validation | Текущий быстрый прогон — воспроизведённый failure. Полные результаты и scope limit перенести из финальных прогонов, старые GCB ID убрать из основного блока. Указывать counts по suite, reached properties у отрицательных harness и exact export SHA. |
| Строки 51–53, attribution | Сверить описание AI assistance с фактическим вкладом и сохранить dual-license signoff. |

Предлагаемый заголовок после устранения блокеров

> Track initialization of supported MaybeUninit storage under -Z uninit-checks

Предлагаемый вводный блок после сверки scope финального экспорта

> Refs #3300
>
> Extend `-Z uninit-checks` to direct `MaybeUninit<T>` storage and flat arrays and slices of slots with supported layouts. Preserve initialization state through supported raw pointer operations and bytewise copies. Check the payload’s data bytes when converting a slot to `T` or `ManuallyDrop<T>`. Supported typed transfers preserve the initialization state of payload data bytes and clear padding in the shadow state.
>
> For ordinary nonforeign MIR items, pair shadow-carrying arguments and normal returns with their transfers. Snapshot the selected byte’s relative offset and initialization state while the source is live, then apply that state at the destination under its typed mask. Return slot zero is mandatory.

Следом добавить финальную policy raw_eq и конкретные исключения, затем результаты exact export и существующий signoff. Черновик в репозитории оставлен как запись прежнего v2. Эти правки приведены для будущего PR. [Черновик][draft] · [Tracking issue][issue]

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c04750eea087c28929d96cd95cd4b9e775d56021/research/challenge-8/kani-k1/AUDIT-BRIEF-KANI3300-PART1-R2.md
[candidate]: https://github.com/Tiramisu-Cake/kani/commit/a0a2386001a15fecfe2facc2f6cd87f3dee13b60
[issue]: https://github.com/model-checking/kani/issues/3300
[quick]: https://github.com/Tiramisu-Cake/kani/actions/runs/43118703581/job/130853314408
[upstreamdiff]: https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662fd65c64381ef2ac97a6397ffc0693a...a0a2386001a15fecfe2facc2f6cd87f3dee13b60
[upstreamexternal]: https://github.com/model-checking/kani/compare/bf9c58e662fd65c64381ef2ac97a6397ffc0693a...Tiramisu-Cake:a0a2386001a15fecfe2facc2f6cd87f3dee13b60
[rounddiff]: https://github.com/Tiramisu-Cake/kani/compare/1cd96e354ec45346b61c245554a50a8af8cb5ce7...a0a2386001a15fecfe2facc2f6cd87f3dee13b60
[r1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/dff05db0c85ebaad823bf54edf28e9c5ddb49291/research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md
[cihead]: https://github.com/Tiramisu-Cake/kani/compare/a0a2386001a15fecfe2facc2f6cd87f3dee13b60...3b90da205860ebd579c4ae418c9d20ef66b5bd9a
[quickworkflow]: https://github.com/Tiramisu-Cake/kani/blob/3b90da205860ebd579c4ae418c9d20ef66b5bd9a/.github/workflows/uninit-quick.yml#L30-L50
[weakscript]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/script-based-pre/mem-init-reinstrumentation/mem-init-reinstrumentation.sh#L5-L19
[a1run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43105165870/job/130806488354
[a1old]: https://github.com/Tiramisu-Cake/kani/actions/runs/43105207965/job/130806630990
[a2run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43107071880/job/130813061296
[a2rrun]: https://github.com/Tiramisu-Cake/kani/actions/runs/43111242922
[a2r2run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117585146
[miri1]: https://github.com/Tiramisu-Cake/kani/actions/runs/43109689395
[miri2]: https://github.com/Tiramisu-Cake/kani/actions/runs/43109978880
[miri3]: https://github.com/Tiramisu-Cake/kani/actions/runs/43111757334/job/130829301804
[initialized]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-initialized/main.rs#L38-L85
[rawcode]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L563-L594
[cast]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs#L317-L348
[castother]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L929-L940
[rawbackend]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs#L1309-L1330
[basecopy]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L103-L111
[baselayout]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L396-L404
[baseassign]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L113-L130
[dispatch]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L244-L284
[baseskip]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L624-L631
[r1skip]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L925-L935
[b1loss]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L479-L502
[termpush]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L764-L786
[entry]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L47-L92
[delayedguard]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs#L98-L119
[delayed]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs#L70-L146
[b1commit]: https://github.com/Tiramisu-Cake/kani/commit/751603f96fde4e7d2b9462331380f6204ffe9ce4
[b1shim]: https://github.com/Tiramisu-Cake/kani/commit/500eae8aa28b373fd9a6ff7827257002a039fa5a
[b1tip]: https://github.com/Tiramisu-Cake/kani/commit/d5f072f2bcf61a04d84bb0e8b54115f3011252fc
[b1diff]: https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662fd65c64381ef2ac97a6397ffc0693a...d5f072f2bcf61a04d84bb0e8b54115f3011252fc
[b1run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43110714635/job/130825677396
[targets]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs#L44-L59
[ptconst]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L399-L444
[memloc]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/points_to/points_to_graph.rs#L19-L30
[delayedsets]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs#L168-L209
[witness]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs#L77-L121
[witnessstart]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs#L237-L248
[constmask]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs#L307-L314
[rawtests]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/raw-eq-uninit/main.rs
[goldens]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tools/compiletest/src/runtest.rs#L564-L597
[rustraweq]: https://doc.rust-lang.org/nightly/core/intrinsics/fn.raw_eq.html#safety
[rustcopy]: https://doc.rust-lang.org/std/ptr/fn.copy_nonoverlapping.html
[rustmu]: https://doc.rust-lang.org/std/mem/union.MaybeUninit.html#validity
[mirdump]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/docs/src/rustc-hacks.md#L239-L249
[layout]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L142-L181
[constantset]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L475-L485
[typedraw]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs#L377-L423
[copyid]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs#L152-L185
[arrayoffset]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L272-L292
[enumoffset]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L321-L393
[patoffset]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L413-L419
[reverse]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L889-L908
[reversegold]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-array-reverse-unsupported/expected
[caller]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L693-L724
[paired]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L1147-L1151
[protocol]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/library/kani_core/src/mem_init.rs#L425-L548
[pairtest]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-pairing/main.rs
[shadow]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L119-L121
[dstfixture]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/kani/UnsizedFnParams/unsized_by_value_args.rs#L4-L40
[constarg]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L189-L217
[argoperand]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs#L148-L159
[unionmask]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L837-L843
[hookdispatch]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L971-L981
[hook]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs#L744-L787
[movetest]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-move/main.rs
[insertion]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/body.rs#L268-L323
[intrinsic]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L530-L665
[a3rfix]: https://github.com/Tiramisu-Cake/kani/commit/c57314d4c
[a3before]: https://github.com/Tiramisu-Cake/kani/actions/runs/43116356531/job/130845269142
[ptintrinsic]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L288-L306
[ptrecursion]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L503-L530
[seedresolver]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs#L134-L140
[b3commit]: https://github.com/Tiramisu-Cake/kani/commit/9dddcb1134f8a55ee3a4451df9513941ca3c8fc3
[b3tip]: https://github.com/Tiramisu-Cake/kani/commit/6db3c4dabd4a368314eb8e2b71d21d1eee721593
[b3run]: https://github.com/Tiramisu-Cake/kani/actions/runs/43117729467
[foreign]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L667-L692
[fullci]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/.github/workflows/kani.yml#L16-L34
[draft]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c04750eea087c28929d96cd95cd4b9e775d56021/research/challenge-8/kani-k1/kani3300/p1/UPSTREAM-PR-DRAFT.md
[oldexport]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c04750eea087c28929d96cd95cd4b9e775d56021/research/challenge-8/kani-k1/kani3300/p1/RESULT-KANI3300-P1.md
[frame]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-contract-frame/main.rs
[clause]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-contract-clause/main.rs
[dfcc]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L142-L170
[cache]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L405-L448
[fieldsetter]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L325-L350

[b3quick]: https://github.com/Tiramisu-Cake/kani/actions/runs/43115485052/job/130842254653
[ptbody]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L448-L460
[shimtest]: https://github.com/Tiramisu-Cake/kani/blob/a0a2386001a15fecfe2facc2f6cd87f3dee13b60/tests/expected/uninit/maybe-uninit-call-pairing-unsupported/main.rs#L16-L32
