# Независимый аудит Kani #3300 Part 1: PFC, shadow transfer и расход памяти

**Дата:** 12 ноября 2026 года. **Вердикт:** полный заявленный PFC-scope пока не готов к подаче как проверенная функциональность; M3 и полный regression gate остаются открытыми.

Аудит относится к [брифу v2 на `cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf`][brief]. Основной семантический кандидат — `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`; R7/R8 рассматриваются как последующие эксперименты, а не как принятые исправления. В этом отчёте **нет нового solver PASS, готового production patch или разрешения считать M3 завершённым**.

**Рекомендация:** прекратить перебор представлений buffer до получения ограниченного профиля реально кодируемых выражений. Сначала исправить сохранение результатов диагностического CI, затем локализовать расход на точном post-DFCC → SSA → Boolean conversion пути. Сохранять текущие snapshot/protocol obligations при первой локальной оптимизации. Если этот короткий диагностический этап не даёт проверяемого исправления, выбрать явное ограничение поддержки PFC для затронутого класса — только после проверки реального SmallSort call graph. Обещать заранее, что такое ограничение сохраняет всю практическую цель Part 1, нельзя.

## 1. Что проверено и чего этот аудит не устанавливает

Прочитаны исходники модели и compiler instrumentation на закреплённых ревизиях, исследовательские manifests/patches/карты стадий, первичный код CBMC 6.11.0 и существующие журналы GitHub Actions. Независимо сопоставлены несколько source → CI checkout, одинаковость P1 и `mem_init.rs` в ключевом сравнении, фактические counters, ограничения вывода и единицы RSS. Локальные Kani/CBMC/rustc/cargo в окружении отсутствуют; новые сборки, solver runs и dispatch CI не выполнялись. Это статический аудит с повторной проверкой существующих свидетельств, а не воспроизведение вычислений на новой машине.

Для шести проверенных пар source → CI — R1, V02, R5-01, R6-02b, R7 B1, R8 — compare показывает два дополнительных CI-коммита, меняющих workflows и `m2a-cases`, без изменений compiler/runtime. P1 во всех шести исполненных деревьях имеет один blob `04d119ac043aeda0bc701555c5514d1ddf7097b2`. Это укрепляет связь измерений с исходниками, но не делает разные модели семантически эквивалентными.

Отдельно подтверждён restricted Quick [43257528539][quick]: checkout `fc3bccbfff9ae13505e231827e9aa8a377f5f2fc`, format/build/Clippy успешны; unit 5/0, kani 22/0, expected 135/0 с двумя ignored, ui 14/0, script 1/0. В [diff к `4f64`][quickdiff] **удалены из CI-дерева** `.rs` и `.expected` для `legal-pair` и `postcondition-hole`. Таким образом, этот успех действительно ограниченный. Он подтверждает результаты включённых selectors, включая ordinary-singleton и обе ensures-hole проверки; он не подтверждает исключённую тяжёлую PFC-пару, M3 или полноту всех property bindings.

## 2. Исправления и дополнения к ресурсным данным

### 2.1. Есть ошибка единиц RSS

В нескольких строках брифа величины подписаны GiB, хотя численно похожи на KiB, делённые на миллион. Для Linux `ps rss` и приведённых `/usr/bin/time -v` записей здесь используется KiB; перевод в GiB — деление на **1 048 576**. Ниже watchdog sample отделён от максимума, зарегистрированного до принудительного завершения.

| Прогон | Фактически сохранённые данные | Корректное прочтение |
|---|---|---|
| [R1, P1][run-r1] | watchdog 6 787 128 KiB; maxrss 6 789 236 KiB; 11,45 с | watchdog ≈6,473 GiB; выполнение убито |
| [R1 + skip, P1][run-r1skip] | watchdog 6 710 968 KiB; maxrss 6 717 020 KiB; 9,73 с | watchdog ≈6,400 GiB; выполнение убито |
| [R7 B1, P1][run-r7] | watchdog 7 241 492 KiB; maxrss 7 247 504 KiB; 9,52 с | 6,906 / 6,912 GiB, а не >7,24 GiB |
| [R8, P1][run-r8] | watchdog 8 067 896 KiB; maxrss 8 313 556 KiB; 9,10 с | 7,694 / 7,928 GiB |
| [R8, P2][run-r8] | watchdog 9 059 164 KiB; maxrss 9 065 144 KiB; 9,34 с | 8,639 / 8,645 GiB |
| [R6-02b, P1][run-r6b] | завершился с frame failures; maxrss 1 949 040 KiB; 49,83 с | 1,859 GiB; завершённый неуспешный semantic run |
| [Исторический upstream, P1][run-uhistory] | maxrss 1 405 024 KiB; 46,14 с | 1,340 GiB; относится именно к 43244395728 |

Порог watchdog равен 6 291 456 KiB = 6 GiB; период опроса — две секунды. Overshoot объясняет превышение порога, но его величина **не ранжирует окончательную стоимость вариантов**. Maxrss остановленного процесса — максимум наблюдённого префикса, не peak завершённого proof. Ошибка единиц не отменяет ресурсный блокер; её следует исправить, чтобы последующие сравнения были воспроизводимыми.

### 2.2. Рост 17M → 51M подтверждается, причина OOM этим не изолирована

| Вариант, P1 | Steps | VCC до → после упрощения | Первая напечатанная CNF | Convert SSA |
|---|---:|---:|---:|---:|
| [Upstream inventory][run-u] | 4 908 | 222 → 66 | 284 883 vars / 17 072 414 clauses | 2,96431 с |
| [V02][run-v02] | 11 396 | 536 → 191 | 844 029 / 51 222 776 | 8,46104 с |
| [R5-01][run-r5] | 11 639 | 476 → 182 | 846 480 / 51 218 835 | 8,50030 с |
| [R6-02b][run-r6b] | 9 340 | 381 → 115 | 829 958 / 51 173 785 | 9,48409 с |

Upstream `bf9c58e662` и V02 `48d10f9ff2` имеют **один и тот же blob `library/kani_core/src/mem_init.rs`: `37b9da8d674afb814f5024a20b77350ad5f82fd8`**. Следовательно, compiler delta R1 при данном upstream runtime достаточна для наблюдаемого роста завершённой формулы. Приписывать именно этот рост изменениям runtime `copy/bless` неправильно.

Одновременно R6-02b завершает кодирование примерно 51M clauses при 1,859 GiB. Поэтому само число «51M» не объясняет, почему другие варианты превышают watchdog-порог. Важны промежуточные структуры, retained expressions, cache, распределение clause sizes и этап, на котором память потребляется. У killed-вариантов нет завершённого CNF counter: нельзя подставлять туда размер из другой строки.

### 2.3. Диагностический CI теряет именно нужные доказательства

В [исследованном workflow][probe-workflow] полный вывод записывается в `sv.txt`, но наружу выводится только `grep ... | head -30`. На V02/R5-01 это расходует лимит на начальные counters и повторные solver-сообщения: причины отказа, время и RSS отсутствуют. В четырёх проверенных runs — 43253856019, 43258921276, 43268005490, 43296031667 — API artifacts вернул пустой список. Отсутствующие подробности нельзя восстановить выводом из соседнего run.

Этот workflow использует `shell: bash {0}`, сохраняет exit code в переменную и затем печатает его. Диагностический step может быть зелёным после Kani failure или kill. Это допустимо для сборщика наблюдений, если результат явно обозначен как diagnostic; использовать его зелёный статус как readiness gate нельзя. Это замечание **не относится автоматически** к restricted Quick: там другой shell script аккумулирует `rc` и завершает job ошибкой при падении suite.

Минимальное изменение следующего диагностического задания: сохранять отдельные ограниченные журналы для каждого input/root, полный список failed properties, raw KiB и signal/exit, фактический backend argv и hashes модели/бинарников; выгружать их и после отказа. Начальные phase counters и финальный outcome печатать независимо. У каждого ограничения размера должна быть отметка `truncated`; отсутствие строки — `UNKNOWN`, а не успех. Вместо общего `pkill -9 cbmc` привязать watchdog к конкретному process group либо явно сохранить условие строго последовательного единственного CBMC.

## 3. Ответ 1: какие причинные выводы допустимы

| Наблюдение | Поддерживаемый вывод | Чего оно не доказывает |
|---|---|---|
| R1 уже превышает лимит | Onset присутствует на границе upstream → R1; A3/M1 не необходимы для воспроизведения | Конкретный виновный hunk, один дорогой term или отсутствие дальнейших взаимодействий |
| U/V02 с идентичным runtime | Compiler delta меняет достигнутый объём кодирования и даёт указанный рост CNF | Эквивалентность обязательств; причинность OOM именно через рост clauses |
| V02 близок R5-01 | Нет оснований объявлять R1 `copy/bless` единственной причиной 17M → 51M | Что `copy/bless` никогда не участвует в дорогом взаимодействии |
| R6-02 заканчивается на Enum Unsupported | Сравнение отрезано раньше нужной работы | Ресурсное исправление |
| R6-02b доходит до solver с frameFAIL | Полезный дешёвый диагностический контраст после bootstrap skip | Корректный PFC, сохранённый A3 snapshot, точное соответствие `*var_N` приватному полю |
| R1+skip остаётся тяжёлым | Само исключение initializer недостаточно | Что вся самоинструментация и все helper interactions исключены |
| R7 split не помог | Проверенная конкретная декомпозиция не устранила блокер | Невозможность любого private-state решения |
| R8 имеет больше steps/VCC и тоже убит | Этот многокомпонентный carrier-кандидат не прошёл ресурсный gate | Невозможность pointer carrier вообще; точный итоговый peak или размер формулы |

Дешёвый upstream не является положительным performance baseline для корректной полной поддержки. Исторический run содержит не только frameFAIL, но и Unsupported raw pointers/unions, unreachable load, layout assertion и subtraction overflow. Для нового inventory-run нельзя автоматически переносить весь этот список: его semantic tail обрезан. У failed-verification различия obligations могут сохраняться и после достижения solver; важно проверять путь, а не только факт его запуска.

## 4. Ответ 2: предлагаемый путь решения

Я не рекомендую сейчас ещё одну замену чисел указателями, возврат старого runtime или переписывание всей модели в byte masks. Эти варианты меняют слишком много свойств одновременно относительно отсутствующего профиля.

Предлагаю три последовательных результата работы:

1. **Диагностический пакет одного различающего сравнения.** R1+skip против R6-02b уже образуют полезную пару после одинакового bootstrap exclusion. На ней получить attribution дорогой работы, одновременно записав первую точку расхождения CFG/обязательств: frame/Unsupported guards, достижимость Load и ensures. Дешевизна после потерянного или заблокированного пути не становится целевым performance baseline. Эта пара локализует область различия, не один representation term. Upstream/V02 использовать как дополнительное сравнение для установленного роста compiler-side encoding, а не смешивать с первым. Полные новые solver runs всех исторических стадий не нужны.
2. **Одна локальная оптимизация на текущей семантике.** Перенести найденное изменение на `4f64`-derived кандидат, сохранив pre-Move snapshot, A3 pairing, mandatory return0, data/padding masks, M1 и S3. Проверить как ресурс, так и исходный semantic gate. Успех на R1 не переносится автоматически на `4f64`.
3. **Решение о поставляемом scope.** Если attribution не даёт практически проверяемой локальной коррекции, фиксировать явную fail-closed границу либо выделять отдельный более крупный backend проект. Не продолжать неограниченную цепочку R9/R10 с новым представлением и теми же неполными логами.

Если профиль укажет на DFCC bookkeeping приватного состояния, предпочтительное архитектурное направление — **явная классификация compiler-owned auxiliary writes**. Она должна исключать доказанно синтетические записи в конкретные private cells из пользовательского frame accounting, сохраняя их исполнение и все пользовательские проверки. Это может оказаться более точным решением, чем добавление общего mutable aggregate в обычный assigns/havoc механизм. Но это **проектное предложение**, не установленный источник расхода или готовая оптимизация.

У такой классификации нужны строгие правила: compiler-owned origin и unforgeable identity; точный target/range; отсутствие разрешения на pointee; отсутствие blanket exemption для любых записей внутри helper; сохранение checks в contract clauses; отдельная политика Check/Replace/recursion. В частности, разрешение изменять auxiliary state при проверке тела не задаёт корректную shadow-семантику contract replacement. Произвольный havoc shadow metadata в stub может разрушить связь с пользовательскими байтами. Если нельзя доказать эту границу, такое изменение нельзя принимать ради уменьшения RSS.

Ghost args/return или caller-owned metadata — осмысленная долгосрочная альтернатива, если глобальное состояние окажется устойчивым источником цены. Она переносит обязательства в ABI/call transformation: нужно согласовать каждый caller/callee, contract wrapper, trait/shim/foreign/indirect boundary, nested/recursive activation и abnormal return. Экономия памяти заранее не установлена: metadata может снова материализоваться через captures и DFCC. Для первого локального исправления этот объём неоправданно велик.

## 5. Ответ 3: допустимая граница поддержки и размещение guard

**По имеющимся данным нельзя доказать единственную минимальную границу, которая сохраняет весь SmallSort scratch.** P1/P2 покрывают два входа, а constructors, wrappers и helpers могут создавать transfer даже при обычной внешней сигнатуре. Утверждение «PFC не нужен для scratch» требует replay конкретного call graph и целей проверки.

Ближайшая технически обоснованная кандидатная граница:

> При включённых uninit checks отклонять затронутые shadow-transfer paths в выбранном PFC Check/RecursiveCheck proof context; сохранять independently qualified ordinary/Assert/storage paths. Replace/stub и неизвестные call forms квалифицировать отдельно.

Это правило нужно строить по **операциям после выбора contract mode и релевантных compiler transformations**, а не по одному наличию `MaybeUninit` в исходной сигнатуре и не по сочетанию двух глобальных `-Z` флагов. Список должен включать callee entry loads, caller Begin/Store, return-only Store0/Load0, transfers в reachable clauses/helpers/generated bodies. Неразрешённое ребро не считать доказательством отсутствия transfer. Существующая B1 диагностика должна сохраняться.

В [visitor][visitor] решение принимается локально, `CheckUninitVisitor::new(tcx, instance)` не получает весь selected PFC context. В [contracts.rs][contracts] SimpleCheck/RecursiveCheck, Replace, Assert и Original выбираются отдельно. Поэтому узкий context-sensitive guard — реальная compiler change, а не однострочный тест атрибута на локальной функции. Общий cache тела не должен переносить PFC guard в ordinary harness или обратно; нужны multi-harness проверки в обоих фактических порядках обработки.

Два возможных варианта реализации:

- **Консервативный admission check на harness.** После определения reachable transfer effects, до дорогой DFCC/Boolean обработки, выдавать явный Unsupported для всего затронутого PFC harness. Проще гарантировать отсутствие дорогого непокрытого пути; шире динамически необходимой границы. Это честное ограничение, не «минимально доказанный scope».
- **Guard на пути до первого непокрытого эффекта.** Переиспользовать существующий Unsupported: [создание check][unsupported] и [фактический lowering][unsupported-lowering] дают assert с последующим assume(false). Поставить guard до Begin/Store/Move-reset; return-only путь защищать до Store0. Сохранить проверки операндов, корректно завершить накопление диагностик без повторения B1-пропуска; непокрытые transfer effects до guard не выполнять. Не заменять guard одним assume(false), отключением pass или выставлением initialized=true. Отдельно измерить, что guard действительно избегает дорогой обработки: поздний runtime guard не гарантирует дешёвый DFCC prefix.

Для принятия scope cut нужны пары: ordinary и PFC одного тела; PFC без transfer; transfer только в ensures/requires/helper; return-only без MU-аргументов; generic/recursive modes; Replace; mixed harness orders; unreachable/dead-path policy; source ordinary type со скрытым generated transfer. Плюс реальные scratch constructors, flat array/slice, helper calls и возвраты. Если guard блокирует необходимый SmallSort proof, результатом будет **более узкая Part 1**, а не выполнение исходной практической цели.

P1 legal и P2 hole в исключённой области тогда должны давать именно Unsupported. Это не P1 SUCCESS и не P2 установленная uninit FAILURE. Нельзя просто переписать старые goldens и назвать полный набор пройденным: scope decision, новые boundary tests и сохранённые исходные repro фиксируются отдельно.

## 6. Ответ 4: snapshot, carrier и private-frame обязательства

В текущем [mem_init.rs][meminit] уже находятся `has_witness`, captured `value`, `relative_offset` и A3 protocol fields. Это не R1 representation с абсолютным saved object ID. [Visitor][visitor] сначала сохраняет **все** аргументы, затем сбрасывает Move sources; original indices остаются `idx+1`. Store0 стоит перед Return, Load0 — после normal call return. Эта source-level структура поддерживает необходимое направление переноса; она не заменяет проверку emitted MIR/GOTO и результатов.

| Обязательство | Что требуется сохранить и проверить |
|---|---|
| Pre-Move snapshot | Сохранить witness match и boolean до любого deinit источника; не перечитывать старый shadow при входе callee |
| False ≠ no witness | Выбранный неинициализированный байт остаётся достижимым false-сценарием; отсутствие witness не кодируется как captured true |
| Demonic selection | У каждого потенциального bad byte должен существовать путь отбора и продолжения witness; не требуется false на каждой optimistic branch |
| Pairing | Signature, число только shadow-аргументов, original argument index, порядок, полнота stores/loads, запрет stale buffer и двойного consume |
| Return0 | Обязательный отдельный snapshot; consumption только на normal return и в живой destination; abort/unwind не исполняет normal load |
| Typed transfer | Маска data/padding соответствует фактическому типу и extent; ZST/zero extent не порождает недопустимый index или dereference; допустимые metadata queries сами по себе не запрещены |
| Nested calls/recursion | Входной протокол полностью consumed до user body; return protocol не пересекается со старым pending transfer |
| Source death | Carrier переносит сохранённые metadata, не читает payload/dead shadow. Pointer representation дополнительно требует backend lifetime/bit-preservation доказательства |
| Frame soundness | Законные private writes проходят, реальный пользовательский out-of-frame write по-прежнему падает на своём assigns property |

R8 сохраняет snapshot/protocol и заменяет numeric relative offset парой `saved_base`/`saved_byte` с round-trip guards. Поэтому это не проверка «одного простого pointer вместо usize». Его 13 private targets должны обозначать **ячейки полей buffer**. Для pointer field target — адрес этой ячейки и её размер, не адрес сохранённого пользовательского объекта. `object_whole(saved_pointer)` или dereference pointee для разрешения private writes было бы расширением user write set.

Необходимая карта для принятия любого private-state решения:

`marker/StaticDef → monomorphized symbol → assigns lambda/member lvalue → actual target object/offset/extent → enclosing Check/DFCC scope → actual synthetic write/guard → retained SSA step → property outcome`.

Для pointer fields отдельно записать адрес cell и значение pointer, чтобы эти две сущности нельзя было спутать. В [текущем contract.rs][contract-code] неудачный поиск marked symbol заканчивается `unwrap_or_default()`; исходный marker сам по себе не доказывает, что exemption попал в emitted contract. Если shadow writes достигнуты, а private target не найден, это должен быть явный audit failure/diagnostic, а не молчаливая предпосылка отчёта.

Использовать существующие [R7-C controls][controls7] и [R8-C controls][controls8], включая matched legal/hole на ненулевом offset, source Move/death, clause negative, lawful modifies и user-frame negative. FrameFAIL с анонимным `*var_N` без derivation не считается подтверждением нужной границы. Source-only PASS и количество algebra sanity cases не дают solver credit.

## 7. Ответ 5: ограниченная диагностика encoding

### 7.1. Что первичный код CBMC позволяет различить

В [CBMC 6.11 `bv_pointers.cpp`][cbmc-pointers] `pointer_object` и `pointer_offset` преобразуют pointer operand, затем извлекают соответствующие биты и расширяют результат. Самого перечисления всех объектов в этих двух ветках нет. `object_size` — отдельный postponed механизм; стоимость operand conversion и последующего обработки ограничений нужно учитывать отдельно.

Есть более конкретные проверяемые гипотезы:

| Механизм | Свидетельство из исходников | Минимальное измерение |
|---|---|---|
| Symbolic byte extraction | [Код][cbmc-extract] при неконстантном/некорректном offset может подняться от member/index до root object; затем символическая ветка перебирает bytes operand и bits результата | Actual root owner, bytes(root), result bits, offset constant/symbolic, число уникальных conversions |
| Symbolic byte update | [Код][cbmc-update] строит обновления по байтам объекта и ширине записываемого значения | Root width, update width, multiplicity, время/память промежуточных bitvectors |
| Symbolic finite-array read/update | [Index][cbmc-index] и [with][cbmc-with] могут развернуть конечный массив по элементам | Actual N, element width, constant/symbolic index, выбранный flatten/UF путь |
| Array/pointer postprocessing | [Arrays][cbmc-arrays] добавляет ограничения отдельно; `finish_eager_conversion` обрабатывает также postponed pointer operations | Число array classes/indices и postponed terms; время/RSS/vars/clauses до и после каждой фазы |
| Много повторной инструментализации | [Converter cache][cbmc-cache] означает, что число occurrences и число новых кодирований различаются | Unique DAG nodes, cache hits/misses, origin каждого нового conversion |
| DFCC private write checks | [DFCC][cbmc-dfcc] строит check по `&lhs` и `sizeof(lhs)` с class `assigns` | Какому объекту/extent соответствует actual lhs и какое выражение осталось после SSA/slicing |

Эти оценки описывают структуру циклов кодировщика, а не точное количество SAT clauses: simplification и cache могут изменить результат. Ни один из перечисленных механизмов пока не установлен причиной рассматриваемого OOM. Scalar `MaybeUninit<u8>` не доказывает, что все helper layouts, closure captures, write-set arrays и backing views имеют размер один.

### 7.2. Нужны три небольших набора данных

**A. Карта до solver.** Получить actual pre-DFCC и post-DFCC модели именно выполнявшейся команды, их hashes и backend argv. Выбрать transfer helpers, init/reset, generated PFC/Assert bodies, private assigns и actual writes. Для каждого monomorphized `Layout<N>` записать N, associated type/callsite, byte size и solver bit width. Не использовать найденный произвольным `find ... | head -1` файл как доказательство идентичности solver input.

**B. Сводка после slicing.** После `postprocess_equation`/slice посчитать all/ignored/retained SSA steps; распределение operators и widths, symbolic offsets/indices, top-30 roots по width и multiplicity. Считать unique DAG nodes отдельно от occurrences. Фильтрации `step.ignore` недостаточно для полного профиля: учитывать все категории, реально передаваемые `convert_without_assertions`, включая guards, assumptions и auxiliary expressions. Привязать их к исходному PC/function и DFCC owner.

**C. Один ограниченный conversion profile, если B недостаточно.** В [SSA conversion phases][cbmc-equation] и converter cache-miss path писать короткие `enter/exit` записи: SSA id, expr kind, operand/result widths, origin, Δtime/ΔRSS/Δvars/Δclauses. Отдельно инструментировать byte/index/update и array/pointer postprocessing. Запись `enter` должна быть сброшена в журнал **до** выделения большого bitvector и до вызова дорогого helper: иначе kill оставляет только последний дешёвый завершённый term. Для вложенных операций нужны ограниченный стек и раздельные inclusive/exclusive deltas.

Для каждого snapshot достаточно, например, 200 строк и top-30 terms. Но ограничение вывода не ограничивает стоимость обхода: нужны memoization, node/time budget и явный `incomplete`. Не сериализовать целиком expression лишь ради его fingerprint. Diagnostic binary не меняет expressions/assumptions/obligations; его RSS с overhead не смешивается с production measurements.

Приёмочный результат диагностики — хотя бы одна конкретная цепочка:

`source/helper → GOTO write/guard → retained SSA term → converter path + widths + измеренная доминирующая стоимость`.

Если найден огромный root при доступе к маленькой cell, оптимизировать соответствующее представление доступа. Если dominates multiplicity — сокращать повторную работу с сохранением semantics. Если dominates postponed phase — исследовать именно её. Это различающие решения; увеличение VCC само по себе между ними не выбирает.

### 7.3. Какие штатные средства использовать осторожно

Параметры ниже относятся к CBMC 6.11.0, а не к произвольному набору аргументов Kani. Команду брать из фактического backend invocation и применять к точному сохранённому GOTO, сохраняя solver, property set, target/object-bits и slicing.

| Средство | Применение и предел |
|---|---|
| `--show-symbol-table`, `--show-goto-functions`, `--list-goto-functions` | Инвентаризация; CBMC preprocessing snapshot не заменяет отдельные точки до/после Kani DFCC |
| `--export-symex-ready-goto FILE` | Сохранить результат preprocessing и выйти; exit 0 не verification PASS |
| `--program-only`, `--show-vcc`, `--show-byte-ops` | Symex-only diagnostic paths; не дают обычного SAT proof outcome |
| `--show-byte-ops --json-ui` | [Реализация][cbmc-show] не фильтрует `step.ignore` и может печатать полный expression/irep; raw count нельзя называть retained converter workload |
| `--write-solver-stats-to FILE` | Есть source/SSA→SAT attribution, но [collector][cbmc-hardness] хранит clause indices и sets variable IDs; на OOM-входе способен заметно добавить память. Сначала дешёвый control или собственная bounded версия |
| `--show-array-constraints` | Полный вывод constraints, а не небольшой histogram; не первый шаг |
| `--arrays-uf-always` / `--arrays-uf-never` | Диагностическое A/B после установления array hotspot; это ещё не принятый Kani fix |
| `--property ID`, `--slice-formula` | Помогают локализовать, но меняют retained задачу; их дешёвый результат не заменяет all-properties gate |
| `--dimacs` | Не обходит Boolean conversion и расход памяти до записи CNF |

Поддержка solver statistics зависит от выбранного backend; она не универсальна. `--full-slice` не включать в acceptance gate: [сам CBMC предупреждает об experimental/possible-unsound поведении][cbmc-cli]. Полные DIMACS/VCC dumps не нужны до описанных bounded данных.

## 8. Ответ 6: минимальные gates перед подачей

| Gate | Полная поддержка PFC | При принятом scope cut |
|---|---|---|
| Identity/build | Exact source/tree, test composition, actual CI root, backend/toolchain versions; fmt/build/Clippy | То же |
| P1/P2 | P1 SUCCESS; P2 intended payload-read uninit FAILURE в ensures; legal/frame/protocol/carrier checks без лишних failures | Обе исходные repro сохранены; ожидаемый явный Unsupported по новой границе, без претензии на доказанную PFC-семантику |
| Transfer protocol | Move/Copy, captured false, gaps/repeated types/original indices, nested calls, mandatory return0, normal/abort, padding, zero/nonzero offsets | Те же проверки во всех оставленных supported paths; отдельные boundary tests для исключённых |
| DFCC | Lawful user writes SUCCESS; user outside-frame и clause violations на нужных properties; private cells разрешены точно | Все оставленные contract modes квалифицированы; исключение PFC не закрывает Replace автоматически |
| Resource | Один и тот же semantic model, фиксированные flags/solver/slicing; завершённый P1/P2 с RSS/wall/phase; без watchdog и timeout | Guard достигается и завершает диагностику до ресурсного взрыва; supported controls не деградируют |
| M1/S3/M3 | Immutable masks, Some(0)/None, оба raw_eq operands, promoted/stack mixed origins, copy-hole, overwrite/reset/reinit, source-following false; M3 composition | То же для сохранённой области, с явно перечисленными scope differences |
| Regression | Полный Quick с возвращёнными тяжёлыми selectors; unit/kani/expected/ui/reinstrumentation; необходимые full regression suites | Полный состав проверок сохранён либо явно переклассифицирован как Unsupported; никакого скрытого удаления selectors |
| Practical goal | Replay точного SmallSort scratch call graph и целевых proof roots | Доказать, что guard их не блокирует, либо явно сократить обещание Part 1 |

Минимальная ресурсная приёмка должна быть количественной до запуска. Разумный **предлагаемый бюджет** для этих скалярных P1/P2 на прежнем 16-GB runner: завершение каждого в пределах 300 с и ниже прежнего 6-GiB watchdog, с рабочим запасом на build/runner. Это инженерный gate, не доказательство эффективности на всех inputs. После первого принятого результата провести один повтор для устойчивости измерения; более строгий бюджет выбрать по полученному корректному baseline. Overshoot остановленного run не подходит вместо завершённого RSS.

Для negative test нужен полный failed-property inventory: правильный intended failure и отсутствие посторонних private-frame/Unsupported/protocol/invalid-value failures на lawful prefix. Общий `VERIFICATION FAILED` недостаточен. Expected failure suite PASS означает соответствие oracle, а не SUCCESS верифицируемой программы. Для legal SUCCESS дополнительно подтвердить достижение нужных transfer/read sites; пустой или преждевременно обрезанный путь не считается доказательством.

M3 из [текущего задания][m3] включает композицию разных механизмов, а не только повторение P1/P2. Restricted Quick её не заменяет. Existing mixed fixtures, unit5 и multi-harness isolation нужно составить с **финальным** export и проверить на нём. Результаты старых SHA, подготовленные tests-only пакеты и source review не переносятся на него автоматически.

## 9. Конкретный следующий handoff

Предлагаю одно ограниченное задание **на диагностическое свидетельство, без смены memory model**:

1. Исправить сохранение bounded logs/outcome и raw units; закрепить exact source/CI/tool/input identities.
2. На R1+skip и R6-02b снять actual pre/post-DFCC symbol/target map, retained SSA summary и capped converter profile; не требовать сначала SAT completion. Отдельно записать semantic differences этого диагностического сравнения.
3. Вернуть top offenders с source/DFCC owner, widths, counts, фазой и memory deltas; если конкретного offender нет, так и написать, не выбирать новую buffer architecture по RSS.
4. Только по этому результату сформировать одну локальную оптимизацию на текущем кандидате либо точный proposal scope cut с проверкой scratch graph. До принятия semantic/resource/regression gates — NO-GO для полного PFC claim.

Новые CI, compiler patches, исходный бриф и существующие goldens в рамках настоящего аудита не изменялись. В репозиторий добавлен только этот отчёт.

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf/research/challenge-8/kani-k1/AUDIT-BRIEF-KANI3300-PFC-RESOURCE.md
[quick]: https://github.com/Tiramisu-Cake/kani/actions/runs/43257528539/job/131319694917
[quickdiff]: https://github.com/Tiramisu-Cake/kani/compare/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c...fc3bccbfff9ae13505e231827e9aa8a377f5f2fc
[run-r1]: https://github.com/Tiramisu-Cake/kani/actions/runs/43252928887/job/131303384165
[run-r1skip]: https://github.com/Tiramisu-Cake/kani/actions/runs/43276317655/job/131385538330
[run-r7]: https://github.com/Tiramisu-Cake/kani/actions/runs/43283068930/job/131409187267
[run-r8]: https://github.com/Tiramisu-Cake/kani/actions/runs/43296031667/job/131454481523
[run-r6b]: https://github.com/Tiramisu-Cake/kani/actions/runs/43276309576/job/131385510579
[run-uhistory]: https://github.com/Tiramisu-Cake/kani/actions/runs/43244395728/job/131273042649
[run-u]: https://github.com/Tiramisu-Cake/kani/actions/runs/43253856019/job/131306698461
[run-v02]: https://github.com/Tiramisu-Cake/kani/actions/runs/43258921276/job/131324595645
[run-r5]: https://github.com/Tiramisu-Cake/kani/actions/runs/43268005490/job/131356676409
[probe-workflow]: https://github.com/Tiramisu-Cake/kani/blob/b3e6acad8632deb84540ecf4847a1e49e0441798/.github/workflows/uninit-quick.yml
[meminit]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/library/kani_core/src/mem_init.rs#L424-L570
[visitor]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
[contracts]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/contracts.rs#L566-L586
[unsupported]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/kani_middle/transform/body.rs#L512-L518
[unsupported-lowering]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs#L202-L241
[contract-code]: https://github.com/Tiramisu-Cake/kani/blob/4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L142-L171
[controls7]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf/research/challenge-8/kani-k1/kani3300/m2br7c/CONTROL-MAP.md
[controls8]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf/research/challenge-8/kani-k1/kani3300/m2br8c/CONTROL-MAP.md
[m3]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf/research/challenge-8/kani-k1/TASK-KANI3300-M3.md
[cbmc-pointers]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/bv_pointers.cpp#L675-L715
[cbmc-extract]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv_byte_extract.cpp#L63-L173
[cbmc-update]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv_byte_update.cpp#L79-L102
[cbmc-index]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv_index.cpp#L201-L273
[cbmc-with]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv_with.cpp#L109-L174
[cbmc-arrays]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/arrays.cpp#L290
[cbmc-cache]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/boolbv.cpp#L40-L80
[cbmc-dfcc]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-instrument/contracts/dynamic-frames/dfcc_instrument.cpp#L684-L760
[cbmc-equation]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_target_equation.cpp#L330
[cbmc-show]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/show_program.cpp#L154-L245
[cbmc-hardness]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/solver_hardness.cpp#L90-L155
[cbmc-cli]: https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/cbmc/cbmc_parse_options.cpp
