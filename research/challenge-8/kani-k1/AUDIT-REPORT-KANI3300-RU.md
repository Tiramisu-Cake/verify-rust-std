# Независимый аудит Kani #3300 для SmallSort

**Дата аудита** — 11 ноября 2026 года  
**Исходный документ** — [AUDIT-BRIEF-KANI3300.md][brief] на `992f8ac7`  
**Решение** — часть 1 доработать и подать отдельным PR, G1 перебазировать после исправления общих инвариантов, для T1b провести один причинный пилот.

## 1. Резюме для принятия решения

Модель одного недетерминированно выбранного байта подходит для проверки переноса состояния при overlap и overwrite. В G1 разделение полного размера хранилища, маски типизированного переноса обычного union и записи отдельного поля согласуется с кодом интерпретатора Rust на исследуемом пине. Для `MaybeUninit<T>` в обеих ветках найдено конкретное расхождение с гарантиями Rust. Типизированный перенос сохраняет shadow байтов padding `T`. Второй блокер касается полноты инструментации на границах вызовов. Отдельный дефект в обработке неразрешённых вызовов может удалить уже собранные проверки. Эти выводы получены из исходников. Выполнение различающих тестов остаётся открытым.

В T1b записи C2 показывают перенос тела `IndexRange::len` между roots до GOTO emission. Из этих записей следует происхождение проверок, но причинная роль caller shadow в двух failures остаётся неизвестной. Прототип `94467a244` подходит для проверки эффекта изоляции. Его готовность к production зависит от результатов пилота, отрицательных контролей и стоимости компиляции.

| Приоритет | Действие | Условие перехода |
| --- | --- | --- |
| P0 | Исправить typed padding `MaybeUninit<T>` и парность аргументов/возвратов | Различающие проверки проходят с ожидаемыми свойствами на точном SHA |
| P0 | Исправить потерю операций на неразрешённых вызовах | Поддерживаемые вызовы сохраняют поведение, неподдерживаемые отклоняются с явной диагностикой |
| P0 | Сверить moved-from случаи с MIR и Miri | Зафиксированы ожидания отдельно для assignment, in-place call и повторной инициализации |
| P0, параллельно | Запустить T1b pilot с тремя roots C2 | Сопоставлены происхождение тела и исходы на shared/fresh transformer |
| P1 | Подать часть 1, затем пересобрать B1 на её новой базе | Объём каждого PR ограничен проверенной семантической дельтой |
| P1 | Повторить SmallSort на реальном scratch | Положительный harness проходит, отрицательный обнаруживает конкретное чтение незаписанного байта |

### Проверенные срезы и метод

| Артефакт | Идентичность |
| --- | --- |
| Часть 1 | [`1cd96e354`][p1-diff] поверх `bf9c58e662` |
| G1 | [`cac044742`][g1-diff] поверх старой упаковки `657c2b245` |
| G1 CI | `8a316e627`, [run `43085855790`][g1-ci] |
| T1b C2 | CMP2 с диагностикой `12b4137c42`, library tree `919cc3e2`, build `0835db8a-7425-4bc9-ad0e-ae83611b3e3d` |
| T1b prototype | [`94467a244`][t-proto] поверх `12b4137c42` |

Аудит включает чтение кода и fixtures, сравнение Git-деревьев, проверку опубликованных CI-статусов и сверку доступных C2 receipts. Новые запуски Kani, Miri, CBMC и Cloud Build для этого аудита не выполнялись. Далее помечены различия между дефектом, видимым в коде, и подтверждённым результатом выполнения.

## 2. P0. Семантика памяти и вызовов

### 2.1. Padding при типизированном переносе `MaybeUninit<T>`

**Статическое расхождение с публичной семантикой Rust.** В части 1 `AssignUnion`, `StoreArgument` и `LoadArgument` для `MaybeUninit` идут через `PointeeInfo::for_storage`, который строит маску `true` на весь extent. `copy_by_id` сохраняет значение отслеживаемого байта при переносе. G1 добавляет маску сохранения для обычного union, однако типизированные операции над `MaybeUninit` по-прежнему получают `for_storage` и маску из `true`. Если исходный padding был инициализирован побайтовой записью, модель гарантирует его сохранение там, где документация `MaybeUninit<T>` гарантирует сохранение только байтов данных `T`. Это риск ложного `SUCCESS` при последующем чтении padding как данных. Такой verdict на новом тесте в аудите не измерялся. [Часть 1][p1-dispatch] · [G1 dispatch][g1-dispatch] · [G1 transfer mask][g1-mask] · [Rust `MaybeUninit`][rust-mu]

**Правка.** Для `copy`/`copy_nonoverlapping` оставить полный extent и перенос всех состояний. Для typed assignment, аргументов и normal returns применять маску данных `T`. Для плоского массива повторять маску по stride слота. Для неподдерживаемого layout выдавать `Unsupported` до применения маски. Маска сохраняет имеющееся состояние разрешённого байта. Она никогда сама не делает этот байт initialized. [Rust `ptr::copy`][rust-copy]

**Критерий приёмки.** На пине Rust выбрать payload с однозначным padding и подтвердить offsets. Явно заполнить физические байты источника, затем сравнить побайтовый copy с типизированным присваиванием и отдельно с bodyful argument/return. Проверить сохранение байтов данных, сохранение padding у raw copy и потерю гарантии у typed transfer. Добавить контроль с исходно незаписанным байтом данных и вариант с плоским массивом. Fixtures с изначально неинициализированным padding проверяют другой инвариант. Снять MIR и сопоставить поведение с Miri для закреплённого nightly.

### 2.2. Обычный union в G1

| Операция | Требуемый shadow-эффект |
| --- | --- |
| Untyped copy | Перенос полного rustc extent, включая padding и tail |
| Typed whole-value assignment, argument, return | Перенос по OR диапазонов данных всех arms. Непокрытые байты назначения сбрасываются |
| Narrow projected store | Обновление записанной проекции по её layout. Внешние байты сохраняют состояние |
| Whole constructor/reset | Новое состояние всего объекта определяется конструируемым arm или операцией reset |
| Чтение pointer value из arm | Проверка байтов самого указателя отдельно от последующего доступа к pointee |

Если padding одного arm входит в data range другого, он остаётся в preserve-mask. При этом исходный `false` должен остаться `false`. Общий tail вне всех data ranges после typed transfer становится uninit. Такой OR соответствует реализации сброса padding в интерпретаторе на пине. Четыре исправленных negative fixtures нацелены на действительно непокрытые байты. Covered-padding positives проверяют сохранение заранее записанного значения. Для усиления матрицы добавить отрицательный контроль с незаписанным байтом **внутри** preserve-mask и положительный контроль, что узкая запись сохраняет данные за пределами проекции. [G1 layout][g1-mask] · [G1 projected writes][g1-narrow] · [Rust interpreter][rust-union] · [G1R6 notes][g1-r6]

### 2.3. Overlap, overwrite, возврат и границы контракта

В `copy_by_id` при совпадении witness с исходным диапазоном есть ветвь, которая переносит ID и offset на соответствующий байт назначения, сохраняя состояние. Ветка со старым состоянием перезаписанного байта назначения нейтрализуется. Это сохраняет нужный контрпример при overlap и overwrite в рамках модели одного witness. При normal return ID и offset фиксируются при живом указателе и используются после возврата как числа. Обращение к завершившемуся stack slot для получения идентичности не требуется. [Witness model][p1-witness]

В DFCC исключение относится к помеченному `MEM_INIT_STATE`. Поля буфера находятся внутри него. Frame-negative проверяет конкретную запись пользователя вне `modifies`. Эта проверка подтверждает сохранение запрета на этом примере. Для более широкой совместимости нужны matched legal PFC с тем же MU roundtrip, отдельный illegal write и отдельное чтение uninit в contract clause. [DFCC][p1-dfcc] · [Frame-negative][p1-frame] · [Clause-negative][p1-clause]

### 2.4. Парность аргументов и возвратов

**Статический пробел.** В части 1 ранний отказ проверяет `!has_body()`, а `StoreArgument` формируется только для nonforeign `InstanceKind::Item`. Bodyful non-`Item` может пройти между этими условиями. Callee entry загружает shadow по типу аргумента. При отсутствии пары fallback выставляет initialized. Fallback оправдан для аргумента, который witness не выбрал в рамках того же вызова. Из одного `active/index` и размера этого установить нельзя. Для normal return с индексом `0` ожидается обязательная запись. Достижимый shim с ложным `SUCCESS` ещё нужно подтвердить на пине. [Visitor][p1-call] · [Store dispatch][p1-store] · [Буфер][p1-buffer]

**Критерий приёмки.** Ввести общий предикат парности caller/callee и ранний отказ при неподдерживаемой форме. Отличать отсутствие выбранного аргумента в текущем вызове от отсутствия самого протокола. Проверять обязательный normal return и исключать оставшееся состояние между вызовами. Проверить несколько shadow-аргументов, вложенные вызовы, повторные вызовы с тем же размером payload и диагностику на bodyless/shim paths. Привязать проверку к MIR и свойству, которое действительно потребляет перенесённое состояние.

### 2.5. Неразрешённые и foreign вызовы

**Подтверждённая потеря операций в коде.** В base ветка `Err` добавляет `Unsupported` в `current_target` и возвращается до записи target. При этом теряются и операции, собранные `super_terminator`, а в пустом entry block возможна потеря ранее поставленных entry loads. G1 сохраняет target только если `touches_shadow` увидел прямой аргумент/результат либо непосредственный pointer/reference к storage. Этот предикат не покрывает erased pointers, wrappers и globals/escaped aliases. Локальный resolver также может вернуть `Ok(Virtual)`, который затем минует обработку `Item`/`Intrinsic`. Delayed-UB instrumentation работает лишь при наличии исходных analysis targets, поэтому зависит от контекста. [Base][base-drop] · [G1 branch][g1-drop] · [Delayed pass][g1-delayed] · [Общая классификация][g1-resolve]

**Решение.** Отдельный upstream patch для сохранения уже собранных операций и общей классификации неподдерживаемых вызовов. Проверить erased pointer, virtual call и контекст без delayed-UB seeds. Если возникает конфликт legacy golden, выбрать один владеющий диагностикой проход и обновить ожидание. Общие исправления следует привязать к воспроизводимому поведению чистой базы.

При `-Z c-ffi` G1 blanket guard охватывает неизвестные foreign calls без аргументов, поэтому учитывает возможность доступа к globals. `__rust_no_alloc_shim_is_unstable_v2` реализован без эффектов. Унаследованное расхождение в `realloc` касается успешного пути. C-модель копирует `min(old_size, new_size)` в новый объект, а shadow этого переноса не моделирует. Для отдельного исправления нужны перенос префикса, uninit нового хвоста и сохранение старого состояния при отказе. В описании G1 разумно указать этот пробел явно. [Foreign guard][g1-ffi] · [C-модель allocator][g1-c]

### 2.6. Moved-from storage

Rust Reference описывает деинициализацию локальной переменной на уровне исходного языка. На уровне MIR обычный `Operand::Move` сейчас не меняет физические байты в Miri и codegen. Для memory-backed аргумента `Call(Move)` есть отдельная in-place семантика с деинициализацией источника в Miri. Поэтому blanket reset по одному признаку `Move` введёт другую ошибку. Удалённые десять fixtures нужно сохранить как материал аудита и пересмотреть по фактическому MIR. [Rust Reference][rust-move] · [MIR на пине][rust-mir-move] · [Решение G1R5][g1-move]

Минимальный контроль различает `Copy`, обычный assignment `Move`, address-taken by-value `Call(Move)` и повторную инициализацию. `forget` проверить отдельно по lowering. Для последующего наблюдения источника подтвердить тот же object ID, живую allocation и причину ошибки. Для подтверждённого in-place случая shadow следует сначала передать, затем корректно деинициализировать источник. До появления модели неподдерживаемую форму следует отклонять, если она достижима в проверяемом коде.

## 3. P0. T1b и причинный эксперимент

### 3.1. Установленный результат C2

В одной invocation фактический порядок `cmp3_into_iter_next → cmp3_manually_drop_unsized_len → cmp3_index_range_len`. Writer72 из первого root меняет тело `IndexRange::len` с fingerprint `8e83681b4d5b4436` на `9bae019701b64b9b` и добавляет два `CheckRef` для `usize`. Consumers130/187 получают тот же symbol и изменённое тело перед GOTO block emission. `into_iter_next` проходит с `0/254` failures, `manually_drop_unsized_len` с `0/92`, direct `index_range_len` падает на `2/28`. Перенос тела подтверждён цепочкой trace records и согласуется с общим transformer на codegen unit. `zero_ops=18` означает отсутствие новых операций при сканировании уже изменённого тела. [C2][t-c2] · [Trace keys][t-keys] · [Upstream cache][t-upstream]

Отсутствие reaching write остаётся гипотезой. Другие варианты включают folding в caller, отсутствие analysis relevance, несовпадение объекта или offset, маску и последующий reset. Чтобы их различить, нужны caller MIR и состояние конкретного witness перед `Get`. [C2][t-c2]

### 3.2. Что изолирует прототип

`94467a244` создаёт временный transformer для ordering и отдельный transformer для каждого root. Изолируются mutable body cache, состояния локальных passes и вспомогательные карты loop contracts. Глобальные passes передаются как clone шаблона. Root-local transformer остаётся живым до синхронного GOTO emission. Поток экспорта получает сформированные данные. По исходникам это достаточный дизайн для пилота. Компиляция и выполнение прототипа остаются непроверенными. [Root setup][t-root] · [Transformer][t-transform] · [Экспорт][t-export]

`last_writer` в диагностике хранится на уровне unit и может остаться от предыдущего root. Для происхождения тела использовать идентичность экземпляра кэша, cache miss/write и нормализованный структурный снимок MIR. 64-битный fingerprint служит сигналом для сопоставления. Если остаётся только старая метка с неполным witness, результат по provenance отмечается `UNKNOWN`. [Критерии пилота][t-accept]

### 3.3. Пилот и интерпретация

Сначала проверить компиляцию. Затем сопоставить shared baseline C2 и fresh prototype на той же library `919cc3e2`, toolchain, flags, stubs и трёх roots в одной invocation. Подтвердить фактический порядок emission. Зафиксировать MIR literal caller, MIR `len` до и после глобальных passes и фактический GOTO. Writer должен сохранить два собственных `CheckRef`, достижимость и `SUCCESS`. Manual root также должен пройти. [Критерии пилота][t-accept] · [Три исходных harnesses][t-probe]

| Наблюдение | Интерпретация и следующее действие |
| --- | --- |
| Direct `len` проходит после исчезновения двух чужих checks, writer сохраняет свои | Изоляция объясняет изменение наблюдавшегося verdict. Инициализацию caller shadow проверять отдельным matched control |
| Direct `len` падает на собственных checks при подтверждённой изоляции | Сопоставить reaching `Set`, reset и `Get` по object ID, offset, выбранному байту, маске и состоянию перед чтением |
| Видно только изменение `last_writer` или fingerprint | Получить структурные снимки и provenance из нужного экземпляра кэша |
| Writer теряет собственные проверки или меняется reachability | Пилот не различает гипотезы. Восстановить сопоставимость запуска |

Если понадобится отделить эффект warmup от эффекта предыдущего root, оставить shared transformer и те же selectors, но поменять только фактический порядок emission, поставив direct перед writer. Символьный `cmp4_index_range_len_runtime` полезен как контроль формы caller MIR при сравнимых co-roots. Перед production нужны свежая пара init/uninit, matched negative в том же call context, IntoIter/compound/padding regressions, multi-harness и loop-contract regressions. Измерить compiler time и peak RSS с `uninit-checks` и без него. Если пересоздание transformer дорого, рассмотреть общий кэш локальных преобразований и root-local изменения глобальных passes с соответствующими auxiliary maps. [Критерии пилота][t-accept] · [Символьный контроль][t-runtime]

Для отдельного upstream PR нужен поддерживаемый пример на чистой базе. Механизм общего кэша есть и в upstream `bf9c58e662`. Текущий verdict относится к экспериментальному CMP2. По брифу остаток старого бюджета `$0.341` меньше требуемого резерва. Отдельный предложенный cap `$0.50` относится к одному пилоту. [Upstream cache][t-upstream] · [Бриф][brief]

## 4. P1. Объём поддержки, CI и упаковка

### 4.1. Границы layout и backend ZST

Часть 1 покрывает прямой `MaybeUninit` и плоское slot storage с поддерживаемыми payload layouts. G1 добавляет прямой union-pointee. Для вложенных и контейнерных unions, enum с различным padding или niche, function-pointer values и вызовов через них, volatile, `typed_swap`, `select_unpredictable`, неподдерживаемых transmutes и bodyless transfers нужны отдельные границы. Допустимый fat pointer как значение следует отличать от проверки unsized pointee. Структурную проверку нужно проводить до ABI/ZST shortcuts. Для неохваченных форм transmute предпочтителен `Unsupported`, если фактическая несовместимость layout не установлена. Отдельно проверить направление `[MaybeUninit<T>; N] → [T; N]` и `raw_eq`, который читает все байты через ссылки. [Структурная проверка G1][g1-layout] · [Rust `array_assume_init`][rust-array] · [Rust `raw_eq`][rust-raw-eq]

В части 1 есть два дополнительных риска. Ветка `RigidTy::Pat` передаёт `0` вместо `current_offset` (G1 уже исправляет), а сравнение padding вариантов вложенного enum строит маски размера enum из абсолютных offsets. Во втором случае различающиеся диапазоны могут обрезаться, и сравнение примет layout за однородный. Выделить исправление смещения `Pat`, проверить вложенный enum на ненулевом offset и до подтверждения не расширять заявления о layout support. [Часть 1 layout][p1-offset] · [Исправление `Pat` в G1][g1-pat]

`d760bad` меняет физическое представление ZST payload внутри padded union wrapper, сохраняя логический тип поля и ширину padding. Для all-ZST union ветка `padding == 0` сохраняет прежнее представление. Перед отдельным backend PR подтвердить abort на чистом base с `uninit-checks` и без него. Добавить проверку индексации `[(); 2]`, ZST с повышенным alignment, offset и all-ZST union. Если abort возникает только через новый G1 lowering, оформить backend-правку отдельным коммитом в B1 с явной зависимостью. [Backend diff][g1-zst] · [G1R6 notes][g1-r6]

### 4.2. Что подтверждено исполнением

| Артефакт | Подтверждено | Открытые вопросы |
| --- | --- | --- |
| P1G | `f046b706 + patch` даёт применённое дерево `10c032ab8`. Семь изменённых production-файлов совпадают с `1cd96e354`. Прошло 15 native selectors, включая три verification `SUCCESS` и 12 диагностических ожиданий | Сквозная идентичность окружения с актуальной базой `bf9c58e662` |
| Part 1 Actions `43027843249` | Exact head `1cd96e354`, три Ubuntu regression jobs и macOS-15-intel прошли | macOS-14 отменён, итог workflow `cancelled` |
| G1 Actions `43085855790` | Три Ubuntu regression jobs, docs, perf, LLBC и benchcomp прошли. Прямой diff двух деревьев `cac044742` и `8a316e627` показывает только frame golden | macOS-15-intel был in progress при сверке, macOS-14 отменён |
| G1 fixtures | Suite `expected` на CI head включает positive golden `65 SUCCESS` и negative golden `62 FAILURE` с заданными свойствами | Compiletest сверяет фрагменты строк. Дополнительные failures внутри negative harness и достижимость отдельных операций требуют отдельной проверки |
| C2 | Сверены SHA-256 17 опубликованных receipts, 17 вложенных stdout и коды выхода. Сохранено 187 из 187 записанных trace records | Трасса остаётся `PARTIAL`, поскольку отдельные лимиты исключили 1829 cache witnesses и 39 external witnesses. Полнота архива и внутренние команды инструментов остаются открытыми |

[P1G][p1-gate] · [Part 1 Actions][p1-ci] · [G1 Actions][g1-ci] · [G1 regression script][g1-reg] · [Compiletest matching][p1-compiletest] · [C2 evidence index][t-evidence].

### 4.3. PFC и последовательность PR

Два 29-строчных fixtures уже изолируют PFC с `modifies` и MU-roundtrip. На проверенном v2 Kani сообщил OOM с `uninit-checks`, а те же тела при выключенной проверке прошли. Пиковый RSS, системное подтверждение OOM и matched результат чистого base отсутствуют. Повторная минимизация вторична. Для заявления о совместимости нужен проходящий legal PFC с тем же roundtrip, ожидаемые frame/clause failures и matched сравнение base/candidate с фиксированным runner и лимитами. Существующее ограничение можно раскрыть в части 1 и вести отдельно. [PFC limitation][p1-pfc]

1. Исправить P0 части 1 и обновить исторический upstream draft по актуальному P1G/Actions. Подать часть 1 с узким заявлением про поддерживаемые прямые и плоские MaybeUninit layouts. Указать PFC и moved-from ограничения, оставшиеся после проверок.
2. По возможности выделить самостоятельные upstream исправления `current_target` и `RigidTy::Pat`. Для allocator, raw intrinsics и общих layout guards вести воспроизводимые отдельные случаи по мере подтверждения.
3. Перебазировать B1 на принятую часть 1. Старый parent `657c2b245` и `1cd96e354` различаются только frame golden, поэтому механическая дельта проста. Новые изменения P0 всё равно требуют повторной проверки. B1 содержит прямой raw union-pointee, narrow store/constructor и typed transfers обычного union с их fixtures. Перенести применимый golden и прогнать итоговый SHA. CI-only историю оставить за пределами upstream PR.
4. T1b и CMP2 вести отдельно. Результат пилота определит, нужен ли отдельный upstream cache fix и какие compound случаи имеет смысл доводить до production.

## 5. Следующий SmallSort replay

**Первый запуск с наибольшей отдачей.** Использовать существующие `small_sort_general_with_scratch_u8_n4` и `small_sort_general_scratch_unwritten_slot_u8_n4`. Положительный harness должен закончить сортировку с достижимым normal return. Отрицательный должен достигнуть чтения `scratch[4]` и дать конкретный uninit failure после проверки записанного `scratch[3]`. Зафиксировать pin Kani, SHA library tree, flags, число проверок, covers и точные свойства. Затем проверить один padded non-`Copy` `Freeze` тип через `StableSmallSortTypeImpl` с длинами по обе стороны переходов `7/8` и `15/16`. Это проводит проверку через scratch, заполнение и merge. [Пара harnesses][small-probes] · [Production scratch path][small-scratch]

**Расширение.** Проверить реальные trait entry points для network и fallback с `Copy + Freeze`, `!Freeze` и ZST. Покрыть граничные длины у соответствующих ветвлений, включая network `8/9`, `12/13` и `17/18`, когда этот путь включён. Для контракта проверять sortedness и permutation, а для stable пути порядок равных элементов. Сохранять требуемые panic и callback paths либо обосновать ограничения контракта. Для более широкой матрицы выделить время после причинного пилота T1b, если нужный путь действительно зависит от `IntoIter`/compound storage.

**Перенос на критерии Challenge 8.** На момент проверки организаторы закрепили Kani `c5e65fdf`. Общий список flags в `run-kani.sh` не содержит `-Z uninit-checks`, поэтому в replay его нужно явно включить и сохранить фактический argv. Для зачёта нужны поддерживаемый pin, все семь safety entry points, сортирующие контракты для трёх `small_sort` implementations и обоснование для произвольной допустимой длины каждого пути. Конечные матрицы типов и длин полезны для регрессий и проверки достижимости ветвей. Доказательство отсутствия invalid values после byte copy остаётся самостоятельной частью работы, связанной с Kani #3762. [Pin][small-pin] · [CI flags][small-flags] · [Challenge 8][small-rules] · [Kani #3762][valid-values]

## Навигация по вопросам брифа

| Вопросы | Раздел отчёта |
| --- | --- |
| 1–3. C2, изоляция transformer и причинный pilot | §3 |
| 4. Extent, preserve-mask и projected writes | §2.1–2.2 |
| 5. Witness, overlap, аргументы, возврат и frame | §2.3–2.4 |
| 6. Move и moved-from fixtures | §2.6 |
| 7–8. Resolver, opaque calls и allocator | §2.5 |
| 9. ZST backend | §4.1 |
| 10. Матрица G1 и padding | §2.2, §4.2 |
| 11. Границы layout/operation support | §4.1 |
| 12–13. Часть 1, PFC и B1 | §4.3 |
| 14. CI и частичная трасса | §3.1–3.2, §4.2 |
| 15. SmallSort replay | §5 |

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/992f8ac7fedd88e117b6a53a16869496a591e387/research/challenge-8/kani-k1/AUDIT-BRIEF-KANI3300.md
[p1-diff]: https://github.com/Tiramisu-Cake/kani/compare/bf9c58e662...1cd96e354ec45346b61c245554a50a8af8cb5ce7
[p1-dispatch]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L218-L240
[p1-witness]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/library/kani_core/src/mem_init.rs#L126-L152
[p1-buffer]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/library/kani_core/src/mem_init.rs#L400-L453
[p1-call]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L480-L520
[p1-store]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L644-L662
[p1-offset]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L299-L375
[p1-dfcc]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L142-L170
[p1-frame]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/tests/expected/uninit/maybe-uninit-contract-frame/main.rs
[p1-clause]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/tests/expected/uninit/maybe-uninit-contract-clause/main.rs
[p1-compiletest]: https://github.com/Tiramisu-Cake/kani/blob/1cd96e354ec45346b61c245554a50a8af8cb5ce7/tools/compiletest/src/runtest.rs#L526-L595
[p1-gate]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c62c126132d7fcc51bda471b22f37fbb8bc9b477/research/challenge-8/kani-k1/kani3300/p1/RESULT-KANI3300-P1G.md
[p1-pfc]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c62c126132d7fcc51bda471b22f37fbb8bc9b477/research/challenge-8/kani-k1/kani3300/u3b/PFC-LIMITATION.md
[p1-ci]: https://github.com/Tiramisu-Cake/kani/actions/runs/43027843249
[base-drop]: https://github.com/Tiramisu-Cake/kani/blob/f046b70644e113be0df9c22c2e6ea44a65a57566/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L263-L271
[g1-diff]: https://github.com/Tiramisu-Cake/kani/compare/657c2b245...cac044742b19d098814d1b76fbe4a8df52d8a824
[g1-dispatch]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L245-L255
[g1-mask]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L230-L244
[g1-narrow]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L432-L442
[g1-drop]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L528-L542
[g1-ffi]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L568-L604
[g1-resolve]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L346-L363
[g1-delayed]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs#L70-L93
[g1-layout]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L261-L302
[g1-pat]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs#L462-L470
[g1-c]: https://github.com/Tiramisu-Cake/kani/blob/cac044742b19d098814d1b76fbe4a8df52d8a824/library/kani/kani_lib.c#L99-L125
[g1-move]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c62c126132d7fcc51bda471b22f37fbb8bc9b477/research/challenge-8/kani-k1/kani3300/g1r5/NOTES.md
[g1-r6]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/c62c126132d7fcc51bda471b22f37fbb8bc9b477/research/challenge-8/kani-k1/kani3300/g1r6/NOTES.md
[g1-zst]: https://github.com/Tiramisu-Cake/kani/commit/d760bad3639ea3a7c4000d41d5462508d5be14ef
[g1-ci]: https://github.com/Tiramisu-Cake/kani/actions/runs/43085855790
[g1-reg]: https://github.com/Tiramisu-Cake/kani/blob/8a316e62704e88d76c54548261abb8b4b3676965/scripts/kani-regression.sh#L49-L100
[rust-mu]: https://doc.rust-lang.org/std/mem/union.MaybeUninit.html#validity
[rust-copy]: https://doc.rust-lang.org/std/ptr/fn.copy.html
[rust-union]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_const_eval/src/interpret/validity.rs#L1178-L1200
[rust-move]: https://doc.rust-lang.org/reference/expressions.html#r-expr.move.deinitialization
[rust-mir-move]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_middle/src/mir/syntax.rs#L1311-L1328
[rust-array]: https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/library/core/src/mem/maybe_uninit.rs#L1045-L1057
[rust-raw-eq]: https://doc.rust-lang.org/core/intrinsics/fn.raw_eq.html#safety
[t-c2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/research/challenge-8/kani-k1/kani3300/t1b-c2/RESULT-KANI3300-T1B-C2.md
[t-keys]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/research/challenge-8/kani-k1/kani3300/t1b-c2/TRACE-KEYS-C2.json
[t-evidence]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/research/challenge-8/kani-k1/kani3300/t1b-c2/EVIDENCE-INDEX-C2.json
[t-accept]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/research/challenge-8/kani-k1/kani3300/t1b-p/ACCEPTANCE.md
[t-proto]: https://github.com/Tiramisu-Cake/kani/commit/94467a24484f1d57315ebbcde7f024dd27576a00
[t-root]: https://github.com/Tiramisu-Cake/kani/blob/94467a24484f1d57315ebbcde7f024dd27576a00/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L491-L544
[t-transform]: https://github.com/Tiramisu-Cake/kani/blob/94467a24484f1d57315ebbcde7f024dd27576a00/kani-compiler/src/kani_middle/transform/mod.rs#L86-L112
[t-export]: https://github.com/Tiramisu-Cake/kani/blob/94467a24484f1d57315ebbcde7f024dd27576a00/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L261-L287
[t-upstream]: https://github.com/model-checking/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L407-L449
[t-probe]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs#L210-L266
[t-runtime]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs#L268-L276
[small-probes]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs#L170-L207
[small-scratch]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/43a95047e96b00b41af30a9c7b1163d61754cce7/library/core/src/slice/sort/shared/smallsort.rs#L207-L294
[small-pin]: https://github.com/model-checking/verify-rust-std/blob/main/tool_config/kani-version.toml
[small-flags]: https://github.com/model-checking/verify-rust-std/blob/main/scripts/run-kani.sh#L76-L87
[small-rules]: https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0008-smallsort.md#L17-L50
[valid-values]: https://github.com/model-checking/kani/issues/3762
