# Независимый аудит Kani #3300 Part 1, раунд 4

**Дата:** 14 ноября 2026 года. Бриф: [`AUDIT-BRIEF-KANI3300-PART1-R4.md` @ `a3911294df`][brief]. Экспорт: C1b [`3f2c12f46e`][c1b], tree `e629978d8f0746bddf896d58a156bad2c59f14ce` (совпадает с брифом, проверено по git).

**Вердикт.**

1. Границу варианта A принять: SEL1 и поддержку вызова компаратора в Part 1 не включать. При этом C1b — исследовательская заморозка, а не пакет, готовый к подаче. Подачу блокируют не две границы SmallSort, а тестовая обвязка, которая ожидаемо не пройдёт на трёх из пяти платформ upstream CI, отсутствие gate вне Linux x86_64 и отставание от upstream (F2–F4).
2. До выбора между A и B есть шаг без изменения инструмента (F1). Путь merge не использует `select_unpredictable`, а raw-строки того же Gate B показывают, что fn-item компаратор под uninit ON проходит. Повтор двух merge-строк на неизменном C1 с компаратором-замыканием может дать первую положительную ON-строку SmallSort на scratch `[MaybeUninit<u64>; 48]` — в рамках A.
3. Если Gate B′ снимет вопрос о компараторе, вариант B сводится к одному изменению: `select_unpredictable` через его fallback body (F8). Это отдельный PR, новая заморозка и оба gate заново.

Семантическая дельта после R3 (9 файлов компилятора, +691/−111) по чтению согласована с заявленным доменом. Новых путей необоснованной инициализации shadow я не нашёл. Runtime `mem_init.rs` после R3 не менялся.

| Утверждение | Статус |
|---|---|
| SHA, tree и состав C1 и C1b; размеры diff; pins; overlays обоих gate | Подтверждено по git |
| Python-проверки обвязки: 24, 42 + 11 и 19 тестов | Воспроизведено на экспорте C1b |
| Счётчики Gate A по наборам равны инвентарю дерева C1b | Подтверждено подсчётом; сам PASS — со слов координатора |
| Результаты run 43521643425 и 43533328479 | Не сверены: Actions форка Kani в этой сессии недоступен |
| Merge-путь SmallSort не вызывает `select_unpredictable`; fn-item компаратор проходит в raw-строках | Установлено по исходникам snapshot и по таблице run4 |
| JSON-привязки содержат host triple и дату toolchain; на трёх платформах upstream CI нормализованный путь другой | Установлено исполнением нормализатора C1b |
| База отстаёт от upstream main на 13 коммитов; два из них меняют файлы Part 1 | Установлено по git |
| Конфликт дескрипторов immutable-реестра обрывает компиляцию корректной программы | По чтению кода; не исполнено |
| Пропуск чтения у вложенных агрегатов достижим только при пополевой сборке значения | По чтению кода; не исполнено |

## 1. Что проверено и границы

Прочитано по точным ревизиям:

- production-дельта `4f64cc617c..3f2c12f46e` целиком;
- на C1b и на base: `mem_init.rs`, `check_uninit/*`, `points_to_analysis.rs`, `immutable_allocations.rs`, `anonymous_allocations.rs`, `contract.rs`, цикл codegen в `compiler_interface.rs`;
- обвязка трёх JSON-наборов и overlays обоих gate;
- research-пакеты `final-gate`, `m3-final`, `mode-findings`, `marker-modes`, дизайн SEL0, прежние отчёты аудитора;
- snapshot std `70ba5befc6`: SmallSort, harness'ы replay, `hint.rs`, `ops/function.rs`;
- upstream Kani main `0aac16ef62`.

Исполнено: Python-самотесты трёх наборов из экспорта C1b и их же нормализатор на синтетических путях. Kani, CBMC, cargo и CI не запускались.

Чего нет:

- Сверки Gate A и Gate B по первичным данным. Страницы и API Actions форка Kani в этой сессии недоступны: запрос доступа остался без ответа. Оба результата в отчёте — со слов координатора.
- Receipt Gate A и stdout строк run4: в репозитории их нет.
- Исполнения гипотез F5 и F6: они выведены чтением кода и снабжены минимальными воспроизведениями.

## 2. Сверка брифа с первичными источниками

| Утверждение брифа | Результат |
|---|---|
| C1 `1658f4cadf`, tree `bfb5eb9db1`; C1b `3f2c12f46e`, tree `e629978d8f`; C1b — прямой потомок C1 | Совпадает |
| `base..C1b`: 331 файл, +21 422/−406; пять строк разбивки по подсистемам | Совпадает |
| C1→C1b: 10 файлов, +278/−107, только `tests/json-handler` | Совпадает |
| nightly-2026-10-23, CBMC 6.11.0, Kissat 4.0.1 | Совпадает |
| Overlay Gate A `7ff2292142` | Прямой потомок C1b; меняет только workflows и `scripts/kani3300-gate`; binding указывает C1b, шесть subtree-хэшей равны хэшам C1b |
| Overlay Gate B `ac49cf8f62` | Пять CI-коммитов над C1; меняет только workflows и `scripts/kani3300-replay` |
| Std snapshot `70ba5befc6`, library tree `6ea9d3425f` | Совпадает |
| Под `tests/` только добавления; handoff-docs и CI-overlays в экспорте нет | Совпадает; оговорка в F10 |
| 24/24 и 53/53 Python-теста | Воспроизведено: 24; 42 + 11; в mode-наборе ещё 19 |
| 8 strong cases, 6 mode roots, 7 composition roots, BINDING_PENDING = 0; manifest 8 238 строк | Совпадает; размер 441 279 байт |
| `cycle_root`: 384 = 337 SUCCESS + 46 UNREACHABLE + 1 FAILURE | Совпадает с `roots.json` |
| Подгонка STEP1 при 12 битах: 3 228 220 переменных, 7 981 631 клауза | Арифметика сходится |
| Gate A: kani 647, expected 686, ui 168, std-checks 5, cargo-kani 72, script-based-pre 99, json-handler 11 | Все семь чисел равны инвентарю дерева C1b; PASS не сверен; «29 стадий» — см. F3 |
| Таблица строк Gate B | Не сверена; координаты согласуются со snapshot: `smallsort.rs:751`, `hint.rs:871`, `function.rs:166` |
| `unwrap_or_default()` в marker lookup сохранён | Совпадает; `contract.rs` относительно base не менялся |
| Публичные docs описывают Replace/RecursiveCheck, циклы и вложенные агрегаты | Совпадает; замечание в F9 |

Два уточнения к этой таблице.

- **Счётчики Gate A.** В дереве C1b 670 файлов `tests/kani/**/*.rs`, из них 23 с `fixme` или `ignore` в имени: остаётся 647. В `tests/expected` 694 теста с expected-файлом, 8 таких же исключений: остаётся 686. Остальные пять чисел равны числу expected-файлов и `config.yml` в соответствующих каталогах. Относительно base добавилось ровно 139 expected-тестов и 3 JSON-набора. Это не подтверждает PASS, но показывает, что сообщённые числа относятся к полному прогону именно этого дерева.
- **Г1 из R3.** Коэффициенты подгонки `774·2^b` и `1926·2^b` равны ровно 6 × 129 и 6 × 321 — стоимости одного чтения срезанной таблицы из §2.1 [отчёта R3][r3]. Гипотеза подтверждена с шестью такими чтениями, а не только «поддержана».

## 3. Находки

P0 меняет решение о пути; P1 блокирует заявление о готовности; P2 — исправить либо вынести отдельно; P3 — замечание.

| # | Sev | Находка |
|---|---|---|
| F1 | P0 | Merge-путь не требует SEL1; fn-item компаратор под ON проходит в raw-строках. Развилка поставлена на неполных данных |
| F2 | P1 | JSON-привязки содержат host triple и дату toolchain |
| F3 | P1 | Gate A — одна платформа и только сводка; «29 стадий» не сходится со схемой receipt |
| F4 | P1 | База отстала от upstream; два upstream-коммита меняют файлы Part 1 |
| F5 | P2 | Конфликт дескрипторов immutable-реестра завершается `fatal` |
| F6 | P2 | Вложенные агрегаты: граница унаследована; пропуск чтения требует пополевой сборки и закрывается дёшево |
| F7 | P2 | T1b — накопление по порядку codegen; allowlist без нужды двусторонний |
| F8 | P2 | SEL1: владельцем переноса должно быть fallback body |
| F9 | P3 | Общие ограничения uninit-checks записаны только в `contracts.md` |
| F10 | P3 | В экспорте остались внутренние ID прогонов и лексика процесса |
| F11 | P3 | Для marker lookup достаточно простого инварианта |

### F1. Развилка поставлена на неполных данных

- **Merge не использует select.** В snapshot `hint::select_unpredictable` вызывается только в `swap_if_less` ([строки 479–480][s-swap]) и в `sort4_stable` ([768–776][s-sort4]). `merge_up`, `merge_down` и `bidirectional_merge` ([808–984][s-merge]) его не вызывают. Строки `merge-raw-pfc-on` и `merge-profile-pfc-on` заблокированы только вызовом компаратора. Бриф (§10.3) говорит о двух зависимостях для всего набора строк; для merge-строк нужна одна.
- **Fn-item компаратор под ON проходит.** У `raw-legal-on` один отказ — select на `hint.rs:871`. До первого select в `sort4_stable` стоят четыре вызова `is_less` (строки 751, 752, 766, 767), а raw-harness передаёт `&mut read_less_u64`, то есть fn item ([overlay][replay-patch]). Unsupported — это `assert(false)` с последующим `assume(false)`. Будь он на пути компаратора, select стал бы недостижим и не дал бы FAILURE. Значит, вызов fn-item компаратора через `<F as FnMut>::call_mut` в режиме Original поддержан.
- **PFC-строки той же формы падают.** `sort4_safety_u64` передаёт `&mut arbitrary_less::<u64>` ([строка 199][s-h-sort4]), `merge_safety_u64_len8_scratch48_src32_dst0` — `&mut tail_less_u64` ([строка 117][s-h-merge]). Отказ записан на `function.rs:166`: это объявление `FnMut::call_mut`, то есть span сгенерированного компилятором shim'а ([источник][s-fnmut]). По коду C1b callee внутри такого shim'а с receiver-типом FnDef разрешается: [`resolve_call`][k-resolve] смотрит только на тип. Причину расхождения raw и PFC по исходникам я не установил. Дословного текста свойства для этих двух строк в пакете нет: в [RESULT][gateb] в кавычках приведён только текст `merge-profile`.
- **`merge-profile` — настоящий fn pointer.** `Profile::CMP` имеет тип `fn(&Elem, &Elem) -> bool` ([profiles.rs:28][s-profile]). Это граница upstream, она есть уже на base.

Что из этого следует.

1. Формулировка «fn-item comparator через `FnMut::call_mut` не поддержан» в общем виде неверна. Граница у́же и пока не названа.
2. Шаг без запусков: достать из сохранённого stdout дословные описания свойств на `function.rs:166` для `sort4-pfc-on` и `merge-raw-pfc-on`.
3. Gate B′ на неизменном C1: те же merge-строки с компаратором-замыканием, например `&mut |a: &u64, b: &u64| tail_less_u64(a, b)`. Вызов замыкания разрешается в его собственное тело, shim не участвует. Меняется только test-only overlay; Gate A остаётся в силе. Исход — либо SUCCESS `bidirectional_merge` под ON на scratch48 с неинициализированным префиксом, либо следующий названный блокер. Оба исхода нужны для решения.
4. В C1b нет контроля «Fn-trait вызов fn item»: в `unresolved-calls` есть только вариант с fn pointer ([тест][k-fnptr-test]). Его надо добавить при любом исходе.

### F2. JSON-привязки содержат host triple и дату toolchain

[Нормализатор][k-checker] заменяет путь rustup на `rust-toolchain:<имя каталога toolchain>/library/…`. Имя каталога включает канал, дату и host triple. В привязках это 86 строк вида `rust-toolchain:nightly-2026-10-23-x86_64-unknown-linux-gnu/…`: 10 в `oracles.json` и 76 в `roots.json`. Они сравниваются точно: как поле `file` отказов, как `location` в `required_regular` и в полных инвентарях.

Upstream запускает `kani-regression.sh`, а с ним и `json-handler`, на пяти платформах ([матрица][k-ci]; на upstream main после [#5138][u5138] вместо macos-14 стоит macos-15). У трёх из них другой triple: `aarch64-unknown-linux-gnu`, `aarch64-apple-darwin`, `x86_64-apple-darwin`. Я исполнил нормализатор C1b на путях всех четырёх triple: с привязкой совпал только `x86_64-unknown-linux-gnu`. Наборы `uninit-contract-oracles` и `uninit-part1-composition` на этих трёх платформах ожидаемо упадут. Это предсказание по исполнению нормализатора, не результат CI.

Вторая сторона того же дефекта: дата. Любая смена nightly меняет все 86 строк, даже если std не изменился. К этому добавляются закреплённые строки std (`core/src/ptr/mod.rs:1754:9`, `core/src/mem/mod.rs:1279:14`). В upstream main прецедента нет: ни один тест в `tests/expected` и `tests/json-handler` не закрепляет путь toolchain или строку `library/core/src`. Gate A этого не показал, потому что шёл на одной платформе и одном toolchain.

### F3. Gate A: одна платформа и только сводка

- Схема receipt overlay'я требует 33 стадии в заданном порядке ([`STAGES`][k-receipt]): 4 предварительные, 8 unit-пакетов, 2 служебные, 15 наборов, 4 завершающие. Статус `COMPLETE_EXIT_ZERO_REQUIRES_REVIEW` возможен только при всех 33. Число 29 из брифа с ней не сходится; оно получается, если не считать четыре предварительные стадии. Вероятнее всего, это ошибка подсчёта в сообщении. Закрывается приложением `receipt.json` к research-пакету.
- Счётчики наборов сходятся с деревом (§2). Это сильная косвенная согласованность, но не замена receipt.
- Прогонов на ubuntu-24.04-arm и macOS нет. Для F2 различающими будут именно они.
- Gate B относится к C1. Перенос на C1b обоснован: C1→C1b меняет только `tests/json-handler`.

### F4. База отстала от upstream

Base `bf9c58e662` — предок upstream main `0aac16ef62`; отставание 13 коммитов. Pins не менялись. Два коммита меняют файлы Part 1.

- [#5115][u5115] меняет ветвь `AtomicStore` в `uninit_visitor.rs`: после записи ставится setter, check остаётся только для non-volatile. В C1b `AtomicStore` по-прежнему стоит в группе «только check». При переносе нужно взять семантику upstream.
- [#5152][u5152] заменяет `instance.body()` на `checked_body` в points-to, delayed-UB и `transform/mod.rs`. Part 1 правит те же строки: выбор override-тела и `resolve_call`. Новые запросы тела тоже должны пойти через `checked_body`.

Кроме того, [#5093][u5093] закрывает находку F9 из R3 (вызовы `saturating_*` в clause-depth helpers).

После переноса production-дерево меняется. По правилу самого брифа (§10.3) receipts обоих gate на него не распространяются.

### F5. Конфликт дескрипторов immutable-реестра завершается `fatal`

Kani кэширует константные allocation по содержимому ([`alloc_map`][k-allocmap]): два разных `AllocId` с одинаковыми байтами получают один символ. Реестр квалифицирует каждый `AllocId` отдельно. Признак frozen ставится, только если на него есть типизированная ссылка на весь объект из top-level константы ([`frozen_origin`][k-anon]). Allocation, на который ссылаются изнутри другого allocation, origin не получает. Если на один символ пришли квалифицированный и неквалифицированный ключ, [`register`][k-immut-reg] возвращает ошибку, а `finalize_immutable_allocations` вызывает [`dcx().fatal`][k-immut-fatal].

Минимальное воспроизведение (не исполнялось):

```rust
static T: [&u8; 1] = [&5];

#[kani::proof]
fn check() {
    let direct: &u8 = &5; // promoted: ссылка на весь объект, ключ квалифицирован
    let nested: &u8 = T[0]; // те же байты через relocation внутри static
    assert_eq!(*direct, *nested);
}
```

Ожидание по коду: с `-Z uninit-checks` компиляция завершается ошибкой «conflicting immutable descriptors»; на base программа компилируется. Это отказ на корректной программе, причём для всего harness'а, а не Unsupported на одном пути. Тестов на смешанную квалификацию одного символа нет: `mixed-promoted-allocations` смешивает stack и promoted операнды, а не ключи.

Исправление не требует новой модели. У ключей одного символа содержимое одинаково, включая `Mutability::Not`, поэтому маска одна и та же. Достаточно считать символ квалифицированным, если квалифицирован хотя бы один ключ. Более осторожный вариант — не сеять такой символ: это false FAIL, но без обрыва компиляции. Для именованных static'ов объединение уже сделано (`static_source`).

### F6. Вложенные by-value агрегаты

1. **Граница не введена Part 1.** На base shadow переносится только для аргументов, чей тип сам является union ([base][k-base-args]), а присваивание значения с union-полем уже отвергается ([base][k-base-assign]). C1b сохраняет оба свойства ([`transfers_shadow`][k-visitor-shadow], [guard][k-visitor-assign]).
2. **По коду, в обычном Rust такое значение не возникает без Unsupported.** Литерал tuple, struct или enum, замыкание с захватом по значению, `transmute`, `ptr::read`, `assume_init` — всё это присваивания целого значения, и guard их останавливает. Обойти его можно только пополевой записью (`RET.0 = …; RET.1 = …`). Known-FP тест получает её через `custom_mir` ([тест][k-knownfp]).
3. **За guard'ом по коду есть два пути к пропуску чтения.**
   - Destination вызова с вложенным слотом не получает ни `LoadArgument`, ни сброса ([код][k-visitor-call]); `StorageDead` и `StorageLive` shadow не трогают ([код][k-visitor-storage]). Если тот же объект раньше держал инициализированный слот, состояние остаётся true.
   - `Call(Move)` сбрасывает источник только для shadow-типов ([код][k-visitor-move]). У вложенного агрегата слот источника остаётся true и читается через сохранённый указатель.
4. **Оба пути закрываются без новых Unsupported.** Для by-value операнда или destination, чей тип даёт `UnionAsField`, ставить полный сброс extent: destination — после возврата, Move-источник — после снимков. Операция `SetRef { value: false }` уже есть и маски типа не требует ([`for_deinit`][k-mod-layout]). Программы, остановленные guard'ом из п. 2, изменения не заметят, существующие goldens не меняются. Пути из п. 3 превратятся в false FAIL, как у known-FP.

До правки нужны два negative-контроля в форме known-FP теста: повторный возврат в тот же destination и чтение moved-from слота. Каждый обязан не дать SUCCESS. После правки формулировку docs «may … miss uninitialized reads» можно сузить до «may produce false positives».

### F7. T1b: накопление по порядку codegen

`codegen_items` вызывается отдельно для каждого harness'а, но с общим на unit `BodyTransformation` ([цикл][k-units]). `DelayedUbPass` берёт тело из кэша, дописывает инструментацию и кладёт обратно ([запись][k-delayed]). Следующий harness того же unit'а получает тела с инструментацией предыдущих. Порядок задаёт компилятор (`order_harnesses::<MostReachableItems>` при наличии export-потоков, иначе порядок unit'а), а не порядок селекторов. Механизм есть на base.

- Сохранённые данные capture с этим механизмом согласуются ([r3][t1b], [r4][t1b-r4]). В обоих порядках селекторов расходятся одни и те же три корня. В `std::ptr::read::<u8>` добавлено 3, 6 и 9 проверок. Это ровно по три на каждый предшествующий harness, если порядок шёл по убыванию размера: `ordinary_ensures_legal` (точное совпадение в обоих порядках), затем `unrelated_legal_after_cycle`, `immutable_legal`, `immutable_hole_negative`. Иначе говоря, каждый следующий harness получает ещё одну копию delayed-проверок общего тела.
- Инвентарь корня в совместном прогоне поэтому — надмножество изолированного: в сохранённом аудите удалённых строк 0, добавленных 18. Allowlist же разрешает и пропажу ([`compare_root`][k-compare]). Пропажа проверки этим механизмом не объясняется; её следует отвергать.
- Каждая добавленная операция обоснована локально: setter стоит после настоящей записи, check — перед настоящим чтением. Поэтому накопление может дать зависящий от порядка false FAIL, но не видно, как оно даст пропуск. Это довод, а не доказательство.
- Исправление небольшое и годится для upstream: запоминать тела, изменённые delayed-pass'ом, и восстанавливать их в кэше после codegen harness'а. Тогда модель harness'а не зависит от соседей, а allowlist, `ORDER_UNCONTROLLED` и требование AB/BA снимаются.

### F8. SEL1: владельцем переноса должно быть fallback body

Codegen и reachability компилируют intrinsic с необязательным fallback body как обычный вызов этого тела ([statement.rs][k-fallback], [reachability.rs][k-reach]). Поэтому OFF-строки проходят. Локальный visitor отвергает любой intrinsic без модели ([ветвь][k-visitor-intr]), а points-to для него рёбер не добавляет ([ветвь][k-pt-intr]). Обе ветви — upstream.

Wrapper `core::hint::select_unpredictable` вызывает intrinsic трижды: дважды над `*mut T` и один раз над `MaybeUninit<T>` ([hint.rs:871, 872, 885][s-hint]). Поддержка только указательной формы U7 не открывает; это отмечено и в [SEL0][sel0].

Минимальная корректная форма — тот вариант SEL0, где у переноса один владелец. Для этого intrinsic, и только при том же предикате, что в codegen, uninit-passes идут по fallback body как по обычной функции. Указательная форма тогда не требует модели: points-to объединит оба arm'а на `Return`. Форма над `MaybeUninit<T>` получает точный перенос выбранного arm'а существующим парным протоколом. Правки нужны в четырёх местах: `has_transfer_protocol`, условие загрузки аргументов на входе callee ([строка 73][k-visitor-entry]), ветвь intrinsic в points-to и в локальном visitor'е. Общего допуска «все intrinsic с телом» вводить не следует.

### F9–F11

- **F9.** Ограничения по вложенным агрегатам и по циклам анализа относятся к `-Z uninit-checks` вообще, но записаны только в разделе контрактов ([contracts.md][k-docs]). Раздел «Uninitialized memory» ([rust-feature-support.md][k-docs-uninit]) не тронут. Строка `raw_eq` «Cannot detect uninitialized memory» ([intrinsics.md][k-docs-raweq]) после Part 1 устареет.
- **F10.** README композиции в экспорте содержит ID прогонов и формулировки вида «the coordinator supplies…», «CI status is `NOT_RUN`» ([README][k-readme]); `roots.json` — `binding_evidence` с именами внутренних артефактов. Для upstream это надо убрать.
- **F11.** Reset вызывается в начале каждого harness'а при включённом pass'е ([код][k-reset]) и пишет в `MEM_INIT_STATE`. При `-Z uninit-checks` символ состояния достижим всегда; его отсутствие — нарушение инварианта сборки библиотеки, а не «случай без записи». Сам C1b уже опирается на это: `finalize_immutable_allocations` обрывает компиляцию, если символ не единственен. В [marker lookup][k-contract] достаточно такой же явной ошибки; анализ эффектов из [REQUIRED-STATE][reqstate] для неё не нужен. Строка — upstream, в Part 1 её можно не трогать.

## 4. Ответы на вопросы брифа

### 1. Можно ли выпускать A; честная формулировка

Как границу — да. Формулировка scope для PR и docs:

> Extends the experimental `-Z uninit-checks` instrumentation to `MaybeUninit` storage: a single slot, `[MaybeUninit<T>; N]`, `[MaybeUninit<T>]`, and a `MaybeUninit<[T; N]>` payload, for element types whose data mask Kani can compute. Initialization state is tracked through raw copies, typed moves (payload bytes only), and direct calls to functions with MIR bodies (arguments and return value). Whole immutable promoted constants and named statics start with their exact byte masks.
>
> Not supported — reported as unsupported or documented: intrinsics without an initialization model, including `select_unpredictable` (and therefore `core::hint::select_unpredictable` and its callers); calls through function pointers and trait objects; shadow transfer under `stub_verified` and `kani::recursion`; by-value aggregates with nested `MaybeUninit` or union fields; call cycles in the delayed-UB analysis.
>
> This change does not make `core::slice::sort::shared::smallsort` verifiable with `-Z uninit-checks`.

Формулировка готовности: «Linux x86_64: полный regression на C1b, по сводке координатора. Другие платформы не запускались. SmallSort с проверками ON: положительных строк нет; negative находит намеренное чтение; шесть OFF-строк проходят». Слова «ready» и «verified» к SmallSort не применять.

### 2. Достаточны ли названные границы; является ли positive ON блокером

Для инструментального PR — не блокер. Блокер он для двух утверждений: «Part 1 позволяет проверять scratch SmallSort» и ссылки на Part 1 в части Challenge 8 про чтение неинициализированной памяти.

Профиль организаторов не включает `-Z uninit-checks` ([run-kani.sh][runkani]), хотя список UB Challenge 8 такое чтение содержит ([текст][ch8]). ON-свидетельство по SmallSort в любом случае будет дополнительным, а не проверяемым CI организаторов. Привязывать подачу Part 1 к варианту B поэтому незачем.

Границы названы не до конца: см. F1 о компараторе.

### 3. Минимальная последовательность для B

1. Без изменения инструмента: дословные диагностики PFC-строк и Gate B′ (F1).
2. SEL1 по F8. Контроли:
   - контрпример из SEL0: select двух указателей, cast к типу с padding, запись, чтение исходного объекта при обоих значениях условия — FAIL;
   - форма над `MaybeUninit<T>`: legal и hole для каждого arm'а; невыбранный arm не получает true; оба Move-источника сброшены;
   - wrapper целиком для `u8` и `*const u64`;
   - raw-строки sort4 из Gate B.
3. Компаратор — только после п. 1. Fn pointer остаётся границей upstream; harness'ам передавать замыкание или fn item. Снимать Unsupported с indirect-вызова без разрешения его целей нельзя: это вернёт потерю проверок, закрытую B1.

После п. 2 — новая заморозка, Gate A и Gate B заново.

### 4. Мешают ли выпуску возможные пропуски чтения у вложенных агрегатов

Не мешают: граница унаследована, Part 1 её не расширяет (F6). Но публичная фраза «may miss uninitialized reads» в PR к верификатору вызовет вопрос, и ответ лучше иметь заранее: два контроля и сброс из F6.

Проверяемая граница допущенного домена — предикат над типом. By-value перенос допущен для top-level union и для `maybe_uninit_storage`, если `for_typed_storage` вычисляет маску. Любой другой тип с union-полем не допущен: присваивание целого значения отвергается, а перенос через вызов после правки F6 сбрасывает shadow. Проверяется матрицей «форма типа × способ появления значения»; ни одна hole-клетка не должна давать SUCCESS. Hole-половины 17 селекторов из отменённой стадии R2 для этого подходят.

### 5. Приемлем ли откат широкого guard'а и known-FP тест

Откат приемлем. Guard дублировал унаследованную проверку присваивания и менял диагностику существующих тестов; по описанию в [задании R3][m3r3task] новые boundary-тесты ловили именно существующий «union as a field».

Known-FP тест приемлем как фиксация поведения, с двумя оговорками. Оба его корня падают одним и тем же сообщением, поэтому сам он не показывает, что hole пойман по нужной причине; это делает только top-level близнец. И он не покрывает пути из F6 п. 3.

Узкий механизм вместо guard'а — сброс из F6 п. 4.

### 6. Достаточны ли A3 и A1; каких контрпримеров не хватает

Для плоского домена — достаточны, по чтению. Runtime после R3 не менялся, выводы R3 остаются в силе. Не хватает контролей:

- вызов, который backend заменяет hook'ом, с shadow-аргументом или возвратом: ожидается отказ протокола, а не SUCCESS (пункт R3);
- один источник в двух аргументах для `Copy`-слота, с hole;
- Fn-trait вызов fn item без shadow-значений (F1) и с ними: shim не имеет протокола, ожидается Unsupported;
- stride с padding внутри `T` при частичном extent: срез `[MaybeUninit<T>]` по ссылке и по raw-указателю;
- два контроля из F6.

### 7. Корректны ли M1 и E2 в whole-object домене

По чтению — корректны. Seed ставит true только байту, который в allocation равен `Some`, а allocation неизменяем, без relocations и Freeze. Такой байт инициализирован на всём исполнении, поэтому seed не может скрыть чтение. Именованные static'и проверяются по тем же условиям и дополнительно по типу и атрибутам символа.

Замечание одно, и оно про доступность, а не про soundness: F5.

Ограничения subrange и relocation — это false FAIL, то есть fail-closed. Их место — раздел «Uninitialized memory» в docs (F9), одной строкой каждое, со ссылкой на тест, который фиксирует ожидаемый отказ.

### 8. Достаточен ли CC1; не расширяет ли он границу на обычные контракты

Достаточен. Корень с циклом получает Unsupported на входе; частичный граф наружу не выходит; остальные корни продолжают работу.

Относительно base это улучшение в двух классах. Для обычной рекурсии base, по коду, уходит в бесконечный обход: в его `apply_regular_call_effect` нет guard'а ([base][k-base-pt]). Для `#[kani::recursion]` base не падал только потому, что не заходил в тела контрактных замыканий. Теперь анализ их видит и честно отказывает. Для нерекурсивных функций с контрактами цикла в сгенерированной структуре нет; новых отказов там я не вижу.

Добавить один контроль: рекурсия через явный `drop_in_place` рекурсивного типа. Это реальный источник циклов в коде с `Vec` и деревьями, а в `points-to-cycles` его нет. Текст о циклах перенести в общий раздел docs (F9).

### 9. Что из R3 обязательно до подачи

Обязательно:

- gate на ubuntu-24.04-arm и macOS после исправления F2;
- перенос на upstream main и повтор gate (F4);
- решение по T1b: правка из F7 либо односторонний allowlist и снятие слов об изоляции;
- контроли: Fn-trait вызов fn item (F1), смешанная квалификация (F5), два контроля F6.

Не обязательно: marker lookup (F11). Требование «два фактических порядка codegen» заменяется правкой F7; без неё оно остаётся.

### 10. Приемлем ли узкий T1b allowlist

Как временное ослабление regression-оракула — да. Он ограничен функцией, классом свойства, статусом и шаблоном ID; существующие ID менять нельзя. Нужна одна правка: сделать его односторонним (F7). Как свидетельство изоляции он непригоден, и в экспорте его лучше не оставлять: правка F7 делает его ненужным.

### 11. Что нужно, чтобы считать mixed-root свидетельством изоляции

Сейчас это наблюдение за регрессией. Свидетельством изоляции его делает одно из двух.

- Структурное: после правки F7 модель harness'а не зависит от соседей по построению; тогда достаточно одного теста «изолированный инвентарь равен совместному» без allowlist.
- Эмпирическое, без правки: записанный фактический порядок codegen (его знает `order_harnesses`), оба порядка, и сравнение GOTO-тел общих функций из сохранённых артефактов — совместное тело содержит все instrumentation-вызовы изолированного. Разбор GBF у команды уже есть (его использует [FINDINGS][findings]).

### 12. Как уменьшить JSON-обвязку

Большую часть гарантий дают обычные expected-файлы с одним harness'ом на файл.

- Строка `** N of` из сводки фиксирует точное число отказов и не зависит от общего числа проверок. Достигнутый Unsupported или frame-отказ меняет N. Прецедент есть: существующие expected-файлы так закрепляют сводку cover. В таком файле не должно быть `kani::cover`, иначе подстрока совпадёт и со сводкой cover.
- По одной строке `Failed Checks: <описание>` на ожидаемый отказ.
- Блоки `<id>\ - Status: SUCCESS\ - Description: …` для полезных утверждений из самого теста. SUCCESS здесь означает и достижимость: недостижимое утверждение получает UNREACHABLE.
- Итоговый вердикт.

Теряется привязка к строкам std, полный инвентарь и сверка JSON с regular. Первое и второе — как раз источник F2. Сравнение mixed-root после F7 не нужно. Остаётся несколько десятков строк вместо 12,8 тысячи. Если полные инвентари нужны команде как внутренний инструмент, их место — форк, а не upstream PR.

### 13. Нормализации путей в C1b

Чрезмерных не нашёл: префикс checkout снимается только на границе пути, суффикс `library/…`, строки и колонки сохраняются. Недостаточны две: в идентичности оставлены host triple и дата toolchain (F2). Gate A их устойчивость не проверяет: это одна раскладка checkout на одной платформе.

### 14. Нарезка на upstream PR

1. **B1** — сохранение инструментации при неразрешённом callee. Уже готовится отдельно; идёт первым, остальные от него зависят.
2. **Анализ контрактных тел**: S3, CC1, CC2, CC4 одним PR. По отдельности S3 даёт переполнение стека на RecursiveCheck и ложные отказы на `bool` и `&bool`. MU-семантики здесь нет.
3. **Маски immutable**: M1 и E2 с исправлением F5. Самодостаточно, около 650 строк.
4. **Layout и `raw_eq`**: A1, A2, полный extent `raw_eq`. Не раньше п. 3, иначе вернётся ложный FAIL на promoted-операндах.
5. **Storage и протокол**: runtime, snapshot, pairing, return0, Move, typed masks. Ядро Part 1; зависит от п. 1 и п. 4. Сюда же сброс из F6.
6. **Layout замыканий**: CLOSURE-ZST и CC3.
7. **E1**: константные union-аргументы, проекции raw-записи, отказ на unsized.

Тесты идут со своим PR в виде expected-файлов. Правка F7 и SEL1 — отдельные PR.

### 15. Какие подтверждения нужны для решения

- `receipt.json` Gate A и число стадий из него (F3).
- По каждой ON-строке Gate B: дословные описания упавших свойств, effective argv, хэши бинарников. Сейчас этого нет в репозитории.
- Результат Gate B′ (F1).
- Gate A на трёх платформах после переноса на upstream main.

Для выбора границы A этого не требуется: он следует из ответа 2 и из того, что SEL1 отделим (F8). Требуется это для заявления о готовности пакета.

## 5. Порядок действий

1. Без запусков: дословные диагностики run4; `receipt.json` в research-пакет.
2. Gate B′: две merge-строки и sort4 с компаратором-замыканием на неизменном C1.
3. Заморозка C2 без новой семантики: перенос на upstream main (F4), обвязка (F2, вопрос 12), F5, F6, F7, docs (F9), гигиена экспорта (F10), недостающие контроли.
4. Gate A на C2: Linux x86_64, ubuntu-24.04-arm, macOS.
5. Нарезка по вопросу 14 и подача, начиная с B1.
6. SEL1 отдельным PR; затем Gate B в исходной постановке.

Решения владельца:

- принять границу A и формулировку scope из ответа 1;
- разрешить Gate B′: до трёх строк, инструмент не меняется;
- разрешить C2 и gate на трёх платформах;
- судьба JSON-обвязки: сократить до expected-файлов либо оставить в форке.

## 6. Поправки к брифу

- §9.1: «29 стадий» — в схеме receipt их 33 (F3).
- §9.2 и §10: «fn-item comparator через `FnMut::call_mut`» как названная граница. Raw-строки показывают, что такой вызов под ON проходит; граница у́же и требует дословной диагностики (F1).
- §10.3: «вероятно понадобятся обе зависимости». Уточнение: для merge-строк select не нужен (F1).
- §2 и §8: ограничение вложенных агрегатов подано как свойство Part 1. Оно унаследовано от upstream вместе с guard'ом на присваивание (F6).
- §3 и §8, T1b: «общий cache». Точнее — накопление delayed-инструментации по порядку codegen внутри unit'а; отсюда следует односторонность расхождений (F7).
- §7, строка об экспорте: «выполнено». README композиции и `roots.json` содержат внутренние ID и лексику процесса (F10).
- §6.1: «сильная ресурсная поддержка». Коэффициенты подгонки равны целому числу чтений из R3 точно (§2).

Новые CI, compiler patches, бриф и существующие goldens в этом аудите не менялись. В репозиторий добавлен только этот отчёт.

[brief]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/AUDIT-BRIEF-KANI3300-PART1-R4.md
[r3]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-PART1-R3-RU.md
[c1b]: https://github.com/Tiramisu-Cake/kani/tree/3f2c12f46e9e32899e8d84e89c65cb6483ba685a
[gateb]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/final-gate/gateb-run4/RESULT.md
[replay-patch]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/final-gate/replay-test-only.patch
[t1b]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/m3-final/r3-capture-t1b/RESULT.md
[t1b-r4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/m3-final/r4-cycle-binding-worker14/CAPTURE-AUDIT.json
[reqstate]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/marker-modes/REQUIRED-STATE.md
[findings]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/kani3300/mode-findings/FINDINGS.md
[m3r3task]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/research/challenge-8/kani-k1/TASK-KANI3300-M3-R3.md
[sel0]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/898fdb62943394e227c7f9b67deb313779be1d7d/research/challenge-8/kani-k1/kani3300/sel0/DESIGN-SELECT.md
[runkani]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/scripts/run-kani.sh#L87
[ch8]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/a3911294df78ef82877c226d8b6993e55d653523/doc/src/challenges/0008-smallsort.md#L41-L49
[s-swap]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort.rs#L454-L486
[s-sort4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort.rs#L737-L782
[s-merge]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort.rs#L808-L984
[s-hint]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/hint.rs#L838-L887
[s-fnmut]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/ops/function.rs#L163-L167
[s-h-sort4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs#L191-L199
[s-h-merge]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts_wide.rs#L102-L118
[s-profile]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L25-L28
[k-resolve]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L521-L546
[k-pt-intr]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L467-L469
[k-visitor-shadow]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L131-L133
[k-visitor-entry]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L64-L105
[k-visitor-assign]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L450-L459
[k-visitor-storage]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L471-L480
[k-visitor-call]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L550-L558
[k-visitor-intr]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L689-L693
[k-visitor-move]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L744-L756
[k-mod-layout]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/mod.rs#L255-L294
[k-delayed]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs#L168-L214
[k-reset]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs#L60-L64
[k-immut-reg]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs#L58-L80
[k-immut-fatal]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs#L228-L253
[k-anon]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/anonymous_allocations.rs#L53-L73
[k-allocmap]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/operand.rs#L565-L591
[k-units]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs#L409-L462
[k-contract]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L146-L171
[k-fallback]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L922-L939
[k-reach]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/kani-compiler/src/kani_middle/reachability.rs#L279-L289
[k-checker]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/tests/json-handler/uninit-contract-oracles/checker.py#L45-L59
[k-compare]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/tests/json-handler/uninit-part1-composition/compare.py#L157-L197
[k-readme]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/tests/json-handler/uninit-part1-composition/README.md#L28-L99
[k-ci]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/.github/workflows/kani.yml#L17-L34
[k-docs]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/docs/src/reference/experimental/contracts.md#L73-L90
[k-docs-uninit]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/docs/src/rust-feature-support.md#L175-L180
[k-docs-raweq]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/docs/src/rust-feature-support/intrinsics.md#L197
[k-fnptr-test]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/tests/expected/uninit/unresolved-calls/fn-trait-pointer-plain.rs
[k-knownfp]: https://github.com/Tiramisu-Cake/kani/blob/3f2c12f46e9e32899e8d84e89c65cb6483ba685a/tests/expected/uninit/part1-composition/move-return-reinit.rs
[k-receipt]: https://github.com/Tiramisu-Cake/kani/blob/7ff22921421730320fee3f3300da711888807ab3/scripts/kani3300-gate/receipt.py#L15-L18
[k-base-args]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L58-L75
[k-base-assign]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs#L117-L131
[k-base-pt]: https://github.com/Tiramisu-Cake/kani/blob/bf9c58e662fd65c64381ef2ac97a6397ffc0693a/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs#L447-L530
[u5093]: https://github.com/model-checking/kani/pull/5093
[u5115]: https://github.com/model-checking/kani/pull/5115
[u5138]: https://github.com/model-checking/kani/pull/5138
[u5152]: https://github.com/model-checking/kani/pull/5152
