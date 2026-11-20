# Challenge 8, пункт 2: сортировки — отчёт для внешнего аудита

## Краткое резюме

Пункт 2 требует контрактов сортировки трёх входных методов на заявленном допустимом домене. Первый список Success Criteria отдельно требует доказать отсутствие UB у семи функций. Эту задачу ведёт линия пункта 1. Обе части Challenge 8 остаются открытыми. Нужны автоматические проверки принятым инструментом с сохранением логики стандартной библиотеки. [факт: N1, N2, CLOSE]

В #752 опубликованы проверки ограниченных наборов типов и длин. Позднее отдельно приняты проверки реальных помощников на точных областях входов. Для новой сетевой сортировки байтов приняты длины 0–4, 8 и 9; для резервной сортировки `Cell<u8>` — 0–4. Проверяются порядок, кратности значений и неизменность внешних значений. Результаты ограничены выбранными типами, компаратором, размещением памяти и нормальным возвратом; в #752 они ещё не интегрированы. [факт: P0, S3Q, S32Q, BQ, FQ, NQ, P3Q, UPD]

Нет общего доказательства для всех типов и длин, чтения неинициализированной памяти, допустимости значений, прав записи и восстановления при панике. Проверки длин 13 и 17 остановлены лимитом времени, результаты неизвестны. Открыты покрытие, контракты вызывающих методов, доверие модели и принятие нового инструмента организаторами. [факт: P3Q, P3C, CLOSE, ON, UPD]

Владелец выбрал пороговый пилот P-1…P-5 как следующий шаг. Четыре положительных корня и три контроля проверят композицию контрактов для произвольного `q`. Расширение монолитной матрицы длин приостановлено до результата пилота. Затем предстоит оценить обязательства по порядку, панике и UB и спланировать матрицу длин и типов. [NEXT, ON]

## Краткий словарь

- **Challenge 8 / item2 / item1** — задача SmallSort; пункт 2 касается сортировок, пункт 1 — отдельной линии безопасности памяти.
- **SmallSort / std / core** — малые сортировки стандартной библиотеки Rust и базовая библиотека, где они реализованы.
- **#752 / pin / snapshot** — опубликованный запрос на включение изменений, закреплённая версия исходников или инструмента и зафиксированный снимок источников.
- **Факт / оценка / гипотеза** — содержание источника, плановое суждение и ещё не проверенное предположение.
- **Source-reported / author-reported / independent** — сведения, обоснованные по исходникам, заявленные автором или установленные независимой проверкой.
- **Bounded / domain / geometry** — ограниченный результат, точная область входов и размещение памяти.
- **T/F / N / u8** — тип элемента, компаратор, длина среза и полный домен байтовых значений.
- **Entry / helper / actual body** — входной метод, вспомогательная функция и её реальное тело.
- **Contract / requires / modifies / post** — контракт, предусловие, разрешённые изменения и постусловие.
- **PFC / `proof_for_contract`** — проверка контракта реального тела; её успех сам по себе не доказывает предусловия будущего caller.
- **Provider / consumer / `stub_verified`** — доказанный контракт-поставщик, его потребитель и проверенная подстановка.
- **Caller entailment / bridge** — обоснование того, что вызывающий код обеспечивает предусловия, и связующее доказательство между этапами.
- **Activation / vacuous** — включение модели и пустой успех при неактивном условии.
- **Oracle / assert / assume / nondeterministic q** — проверка свойства, утверждение, ограничение входа и свободный порог; в плане q охватывает весь u8 и не фильтруется.
- **Sortedness / full-value count / frame** — порядок, сохранение кратности каждого значения и неизменность значений вне активной области.
- **Q / admission / qualified bounded result** — отдельное решение о принятии точного ограниченного случая; оно не переносится на другие домены.
- **Role / cover / negative control** — обязательное проверяемое свойство, свидетельство достижимости и специально сконструированная проверка отказа.
- **UNKNOWN / BLOCKER / NOT_RUN** — неизвестный результат, препятствие и корень, который не запускался; ни один не означает отрицательный результат свойства.
- **OFF / ON / UB** — профиль с выключенными или включёнными проверками памяти и неопределённое поведение.
- **PLAN ONLY / GO / ledger** — план без запуска, отдельное разрешение на запуск и журнал учёта.

Обозначения времени, памяти и инвентаря собраны в приложении А перед §10.

Срез на 2026-11-20. Автор — planner/root. Дополнение от 2026-11-21 учитывает решения владельца и повтор SAT-модели. [NEXT, CAD]
**Пункт 2 не закрыт.** Есть опубликованный bounded baseline и новые принятые bounded cases;
нет полной функциональной и UB-верификации всех требуемых входов и длин. [факт: N1, CLOSE, P3Q]

**Как читать ссылки.** Код источника в квадратных скобках раскрывается в приложении в repository/path/полный commit.
Снимок GitHub #752 и реестр проверенных Git-объектов закреплены в `SOURCE-SNAPSHOT.json`
коммита `2a0becc18c7580c6d39f5d20a02c0cea37dbf924` (далее `[SNAP]`).
`[факт]` означает проверенное содержимое такого источника, включая его границы уверенности;
это не новое независимое исполнение Kani. `[оценка]` и `[гипотеза]` не являются proof credit.
Для этого отчёта не запускались compiler/Kani/CBMC/CI и не скачивались архивы evidence. [факт: SNAP]

## 1. Цель, буквальные критерии и наши рабочие границы

[факт] Официальный текст требует отсутствия UB для семи именованных функций: [N1]

| Группа | Требуемые цели |
| --- | --- |
| Trait entries | `StableSmallSortTypeImpl::small_sort`, `UnstableSmallSortTypeImpl::small_sort`, `UnstableSmallSortFreezeTypeImpl::small_sort` |
| Helpers | `swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, `has_efficient_in_place_swap` |

[факт] Для трёх trait entries отдельно нужны контракты, показывающие, что они сортируют.
Ключевая формулировка: «for all possible slices with arbitrary valid length».
Кроме исходных `SAFETY`-условий перечислены dangling/misaligned accesses, uninitialized reads,
immutable writes и invalid values. Автоматизация, принятый tool и успешные PR checks обязательны;
runtime-логику std менять нельзя. [N1, N2]

| Ось | Наш рабочий смысл | Что ещё должно быть обосновано |
| --- | --- | --- |
| Длина | Для entry-маршрутов рассматриваем fallback до 16, general/network до 32 | Это выбор стратегии через фактический threshold/caller domain, а не замена буквального требования; нужна полнота редукции. [факт: CLOSE] |
| Произвольная длина helper | `insertion_sort_shift_left` имеет собственные valid length/offset условия | Прогон при фиксированных длинах не является индукцией или доказательством любого valid offset. [факт: CLOSE] |
| Элементы | Новая функциональная линия: `u8`, `Cell<u8>`, `NonCopyByte` | Представители закрывают выбранные T/F, а не все Rust-типы, layout и ownership. [факт: MODEL, S1A] |
| Компаратор | Закрытый чистый `KeyLess<T>`: сравнение полного logical byte через `<` | Произвольный `FnMut`, внешние записи и паника требуют иных safety-premises/доказательств. [факт: MODEL, CLOSE] |
| Сортировка | Неубывание: нет соседней пары `next < previous`; сохраняем полные кратности значений | Порядок только по key и count только ключей недостаточны; tie stability — отдельная характеристика. [факт: MODEL, P0] |
| Форма результата | Нужны проверенные контракты реальных entry-методов, с activation и caller entailment | Оракул прямого helper-harness и контракт N2 wrapper не равны контракту всех entry-входов. [факт: CLOSE] |
| «No UB» | Четыре класса из challenge плюс применимые `SAFETY`-premises | Stock-OFF proofs не устанавливают uninit/validity/immutable-write гарантии. [факт: N1, ON, CLOSE] |

[оценка] Для заявления «пункт выполнен» требуется согласовать достаточный scope с критериями,
а не только получить зелёные leaf-прогоны. Примитивы/пороговые домены — явные рабочие выборы;
этот отчёт не выдаёт их за новое решение приёмочной комиссии. [CLOSE]

## 2. Что опубликовано в нашем verify-rust-std#752

[факт] #752 открыт; head `872d5a43380752786415bc00d2a12ce0e930cb37`,
ветка `submission/ch8-smallsort`, base `25b2b24c82a960734a2bab082784747b9b785177`.
Это текущие connected metadata, замороженные в `[SNAP]`; далее содержимое PR body обозначено `[P0]`.

| В опубликованном baseline | Домен / ограничение | Уровень сведений |
| --- | --- | --- |
| 235 обычных harness +13 opt-in негативов | Негативы за `cfg(kani_smallsort_controls)`, обычный CI этот cfg не включает | Заявленные в PR состав и исторические результаты; здесь native discovery не повторялся. [факт: P0] |
| General/stable sorting | `u8/u64`, N0..9, key-order и full-value count | Не general 0..32 contract theorem. [факт: P0] |
| Fallback sorting | N0..6 | Не полный fallback 0..16. [факт: P0] |
| Network | Sortedness до N13 в перечисленных случаях; count ниже N9, отдельные tag proofs N9/N13 | Не full-value permutation для всех длин до 32. [факт: P0] |
| Safety matrix | Представительные длины до 32; scalar/array/Cell/Drop/ZST и разные size branches | Не generic/all-length/все UB-классы. [факт: P0] |
| Реальные helper contracts | 16 `proof_for_contract` и 4 `stub_verified` consumer на заявленных T/F/allocations | Прежде всего safety `requires/modifies`; не универсальные sorting summaries. [факт: P0] |
| Sorting contracts | Proof-owned profiles и 3 N2 forwarding wrappers | Не полное доказательство контрактов самих trait methods. [факт: P0, CLOSE] |

[факт] Safety baseline включает u8/u64, массивы `[u8;16/17/85/86]`, Drop type, ZST `()` и Cell;
размерные классы 1/8/16/17/85/86 выбирают разные ветви. Вставка проверялась по offsets для u64 N1..20;
это не означает sorting correctness для каждого такого T/N. [P0]

[факт] В опубликованном #752 отдельно сохранена оговорка о доверии модели массивов на organizer pin cd355b0b: автор сообщает о failing array-select reproducer. Она относится к `network::swap_contract_bytes16_n2`, `network::swap_contract_bytes17_n2`, `merge::sort4_contract_bytes16_n4` и `merge::sort4_arbitrary_comparator_bytes16_n4`. Это ограничение четырёх исторических array-valued fixtures, не новый counterexample сортировки и не автоматически перенесённый verdict для новой u8-линии. [P0]

[факт] В PR заявлены исторические fork CI run 42363378063 и 235 SUCCESS на каждой ОС,
978/978 satisfied covers; суммы SmallSort verification time 7802 с Ubuntu и 10534 с macOS,
максимум отдельного proof 246/340 с. Это исторические author-reported результаты на своём pin,
не измерение новой experimental matrix. 71 ordinary harness отсекает `panic_on_ord_violation`
через `assume(false)` stub; comparator panic/unwind recovery не проверены. [P0]

[факт] Три pin нельзя смешивать:
`#752/tool_config/kani-version.toml` — `cd355b0bccd32300713bc2ce4f765dafa1510607`;
текущая upstream-база — `c5e65fdfc3e15ec32293f2a4c07509aebec033c9`;
новая S-линия — `0aac16ef62da9e9d5645782d458593e5d78143ba`. [P1, P2, TOOL]
[факт] S1–S4P3 admission, новые source modules и их CI receipts ещё не интегрированы в #752.
Опубликованная голова не менялась из-за этих решений; простое сходство имён не переносит evidence. [SNAP, UPD]

## 3. Что сделано после #752: S1–S4P3

### 3.1. Краткая история этапов

[факт] S1 закрыл механизм model activation/entry registration на tiny domains:
35/35 composite rows, шесть выбранных implementation bodies, N0..3 smoke,
22 source-reported PFC chains, восемь негативов. Это composite двух origin-run,
а не один полностью успешный workflow. Финальное admission — раздел S1 в ledger;
историческое PENDING в candidate не переписывалось. [S1A, S1R, L]

[факт] S2 был cost/encoding probe, не принятой композицией sort13/general 32:
несколько compile/contract-registration ошибок, RSS cutoff на `general32_weak` в r4-r2,
child 600 timeouts на `merge32_real` и `sort13_assumed` в r5. Пара general32 в r5 не была
выбрана. Assumed summaries остались без qualification. [L, S2R5]

[факт] PLAN v2 §5/P2 предлагал перейти к декомпозиции после неудачи больших замеров.
Инвариант merge для всех 256 значений подготовили офлайн. Его Kani-проверка осталась
`NOT_RUN`. После S2 по отдельным GO проверили S3 actual leaves, bridge, fallback/network
partitions и буквальные вызовы вплоть до N8/N9/N13/N17. Они дали ограниченные результаты
при открытом P2. Владелец теперь остановил расширение монолитной матрицы до q-пилота.
[PLANV2, MERGEPILOT, L, S3Q, BQ, FQ, NQ, P3Q, NEXT]

[факт] S3-1-r2 дал actual-body PFC swap/sort4/merge8 на точных геометриях;
S3-2 уточнил same-allocation merge и отдельно сохранил partial-init diagnostics.
Bridge добавил фиксированный insert_tail и реальный sort9; затем S4 разбивал более широкие
fallback/network цели, сохраняя весь full-byte домен, а не уменьшая алфавит. [S3Q, S32Q, BQ, FQ, NP]

[факт] S4P2-r2 заменил symbolic-length call sites на literal slices; N01 — bool-выбор
между двумя literal calls. Actual `small_sort_network` не подменён другим алгоритмом.
Unwind 36, полный backing/frame, assertions и feasible covers сохранены.
Все четыре positives завершились вместо прежних child 600 cutoffs. [NP, NPK, NR, NC]

[факт] S4P3 проверил N8/N9/N13/N17. N8/N9 приняты; N13/N17 — BLOCKER,
неполные native inventories. Review APPROVE последним двум означает согласие
с классификацией BLOCKER, а не одобрение отсутствующего положительного доказательства. [P3I, P3R, P3Q]

### 3.2. Функция × свойства × домен × статус

Обозначения: `O` — actual Original body; `C` — actual-body `proof_for_contract`;
`S/C/F` — sortedness, full-value count, outside-value frame; `Q` — exact bounded
SOURCE_REPORTED admission. `V34/base1` — initialized backing 34 с активным подсрезом от 1.
Домены разных строк не объединяются автоматически в provider или entry theorem. [CLOSE, NPK]

| Цель и mode | Свойства | Точный принятый домен | Статус / evidence |
| --- | --- | --- | --- |
| Entry smoke, C | Activation, post/frame и PFC-связи | Выбранные три T/F пары, шесть bodies, N0..3; свои fixtures | S1 composite Q; runs 44095954742+44128268928; admission L, candidate S1A/review S1R |
| `swap_if_less`, C | Пара значений/order/count/frame, exported safety | u8/KeyLess, V34, base0..20, indices 0..12, включая совпадения | Q; run 44416629057; S3Q |
| `sort4_stable`, C, separate | S/C/F, exported safety | Два backing 6, active[1, 5), full u8 | Q; run 44416629057; S3Q |
| `sort4_stable`, C, same allocation | S/C/F | Backing 48, два disjoint four-element ranges, starts 0..44 | Q с exact metadata exception; run 44416629057; S3Q/S3L |
| `bidirectional_merge`, C, separate | S/C/F | Два backing 10, active[1, 9), два sorted halves 4+4 | Q; run 44416629057; S3Q |
| `bidirectional_merge`, C, MU48 | S/C/known-value frame | src[32, 40), dst[0, 8), known values[8, 48), sorted 4+4 | Один Q; run 44439462279; destination initially outside known set; init-state theorem НЕ дан; S32Q |
| `insert_tail`, C | Sorted prefix/count/frame | V34/base1, relative-tail 1, span 2, u8/KeyLess | Один Q, не все 16 геометрий; run 44460583125; BQ |
| `sort9_optimal`, O | S/C/F | Actual 25-swap body, V34/base1, len 9, u8/KeyLess | Q; run 44460583125; BQ |
| Fallback `Cell<u8>`, O | Logical S/C/F/canary | V34/base1, N0..2 и N3..4, pure KeyLess | Два Q, finite union 0..4; run 44481580554; [FQ, FR] |
| Network `u8`, O | S/C/F/canary | V34/base1, N2,N3,N4 и N01 с обеими длинами | Четыре Q, finite union 0..4; run 44548842328; NQ/NR |
| Network `u8`, O | S/C/F/canary | V34/base1, exact N8 и N9 | Два Q; run 44577116178; только множество{8, 9}; P3Q/P3R |
| Network N13/N17, O | Те же заявленные оракулы | Полный u8, literal lengths, те же V34/base1 | BLOCKER: child 600; свойства/roles/covers UNKNOWN, не 0; P3I/P3C |
| Partial MU merge rows | Наблюдаемые functional checks | Две отдельно pinned partial геометрии | DIAGNOSTIC_ONLY_INITIALIZATION_OPEN, не Q; S32Q |

[факт] Покрытие новых приёмок S4 по длинам маршрута: network `u8` — 7 из 33
`{0,1,2,3,4,8,9}`, fallback `Cell<u8>` — 5 из 17 `{0,1,2,3,4}`, general — 0 из 33.
Отдельный S1 smoke проверял actual entry bodies на N0..3. Доли относятся к заявленным
типам, компараторам и геометриям. [NQ, P3Q, FQ, CLOSE, S1R]

[факт] Для принятых новых leaf недостаточно сказать «реальная функция»: сохранены mode,
компаратор, preconditions, backing/base/alias/init, source/tool/request и все native статусы.
Swap/sort4/merge PFC предполагают свои `requires`; их успех не доказывает,
что произвольный будущий caller эти `requires` обеспечивает. [S3Q, S32Q, CLOSE]

[факт] На source S4P3 N8 проходит insertion tails 1..7; N9 — sort9 и insertion с пустым suffix;
N13 — sort13; N17 — sort13 плюс tails 13..16. Условие `no_merge = len < 18`
возвращает из helper до `bidirectional_merge`. General и network 18..32 — иные пути. [STD, P3R]
[факт] Ни одна новая строка сама по себе не закрывает произвольный comparator panic,
unwind/Drop recovery, ownership/permission, generic T/F или контракт всех trait entries. [CLOSE, P3Q]

## 4. Как устроены доказательства и приёмка

### 4.1. Модель, предусловия и доверенные части

[факт] `sorting_model.rs` проектирует u8/Cell/NonCopyByte в полный logical u8;
Snapshot владеет pre-state, не хранит ссылку на изменяемый slice. `KeyLess<T>` — именованный
статический компаратор, без function-pointer identity test. Неактивные T/F дают
`enabled=false`; обязательная ACTIVE-роль исключает vacuous model-post. [MODEL, NR]

[факт] Post сначала проверяет длину и порядок, затем для каждого входного значения
считает его кратность до/после. Это полный multiset, включая duplicates, а не checksum
или перестановка только заранее различных tags. Цикл count вложенный, source complexity O(N²).
Full backing и отдельный arbitrary outside canary проверяют неизменность внешних значений. [MODEL, HARNESS]

[факт] Доверяем Rust/Kani frontend и инструментированию, CBMC/backend, intrinsic models,
прочтению exported inventory и нашей логической модели. Для stock Kani 0aac16ef
объявлены nightly-2026-10-23, CBMC 6.11.0 и зависимость Kissat 4.0.1. S-линия использовала
встроенный в CBMC CaDiCaL по умолчанию. CLI и harness не переопределяли этот выбор.
Основание для вывода — исходники, закреплённая конфигурация и сообщения backend.
[TOOL, DEP, SOLVER, NI, P3C]

[факт] В новых network-r2/S4P3 positives нет `stub`, `stub_verified` или assumed summary edges.
PFC leaves используют контрактную семантику Check на указанном target; старые #752 и S2 имеют
иные профили/stubs. Нельзя переносить утверждение «без summaries» на всю историю проекта. [NR, P3R, P0, L]

### 4.2. Негативы и невакуозность

[факт] Повторяемые controls: испорченный checker order; испорченный full count;
`sort13_weak` с фиксированным descending13 и слабым seam; Cell count corruption
`[0,1]→[0,0]`, сохраняющая order. Нужен designated FAILURE, а не любой exit1.
Последний control имеет отдельную SUCCESS activation-роль. [S3Q, FQ, P3PK]

[факт] Positive roles: active concrete model, sorted/full-value count, whole outside frame,
arbitrary canary. Feasible covers требуют длину, unsorted input, duplicates, nonconstant output,
descending witness и useful return. У N01 невозможные pair/descending covers не объявлены;
остаются обе длины и return: 3 SAT вместо 6. Это exact-domain design, не waiver UNSAT. [NR, P3R, HARNESS]
[оценка] SAT covers подтверждают существование путей, но не заменяют универсальный assert;
успешный негатив различает конкретную ошибку, а не доказывает полноту оракула. [NR, CLOSE]

### 4.3. UNREACHABLE, guards и SOURCE_REPORTED

[факт] Strict collector сохраняет ZERO_U/REJECT_ALL и disabled proposal. Поэтому даже после
успешного native proof имеются strict 0/8, `s3_expected_match=False`, SELECTED_PARTIAL и workflow FAILURE.
Отдельное admission не превращает исходный workflow в SUCCESS. [NQ, P3Q]

[факт] Каждый U проверяют по exact property instance и source-local path/definedness argument.
Обязательная роль не может быть U. Сохраняются все unsupported guards, включая SUCCESS,
extra failures, locations, covers и неполные inventories. Сходный suffix недостаточен. [NR, P3R]
[факт] В network-r2 retained 67 U across all roots, включая 16 merge U; модель/builtin locations
получили 13 отдельных metadata arguments. В S4P3 observed subtotal 655 properties относится
к шести complete inventories; два timeout inventories неизвестны. [NI, P3I]

[факт] `QUALIFIED_BOUNDED_SOURCE_REPORTED` означает:
**QUALIFIED** — exact case принят отдельным решением после intake/review;
**BOUNDED** — только перечисленные T/F/длины/геометрия/normal-return scope;
**SOURCE_REPORTED** — связь property/role/target и исключение U обоснованы на source/producer уровне.
Это не независимое установление AST/MIR/emitter correctness и не credit B1/B2;
последние — внутренние категории assurance в наших пакетах, не термины критериев challenge. [S3Q, NQ, P3Q]
[оценка] Надёжность этого слоя и достаточность source-local U аргументов — важный предмет аудита,
а не факт, который можно дополнительно доказать тем же Python-collector. [ZERO, CLOSE]

### 4.4. `lib.rs:0:0`: точечное решение, не общее правило

[факт] Здесь надо различать status `UNREACHABLE` и system check class `unreachable`,
имеющий status `SUCCESS`, но present-null file/line и display `lib.rs:0:0`.
Во втором случае принималась exact metadata запись, а координаты не придумывались. [S3L, S32Q, FQ]

| Решение S3/S4 | Число exact SUCCESS metadata cases | Что принято сверх metadata |
| --- | ---: | --- |
| S3 sort4same | 1 | Exact bounded sort4 case после последующего полного admission. [S3L, S3Q] |
| S3-2 merge | 3 | Только allinit функциональный case; две partial строки диагностические. [S32Q] |
| S4P1 fallback | 2 | Два Cell-блока N0..2 и N3..4. [FQ] |

[факт, арифметика] В этих трёх S3/S4 решениях шесть metadata cases, из них четыре относятся
к qualified positives. Исследование общего emitter рассматривало пять: 3 merge+2 fallback;
sort4 был дополнительным reference. Эти разные множества нельзя называть одним «пять исключений». [ZERO, S3L]
[факт] Статический кандидат — MIR Unreachable→assert-assume(false); actual per-invocation
emitter/site/span binding UNKNOWN. Поэтому нет wildcard-правила по `0:0`, suffix или class.
В bridge/network-r2/S4P3 нового missing-location exception не потребовалось. [ZERO, BQ, NR, P3Q]

### 4.5. Исполнимый пакет и независимые проверки

[факт] Последовательность: frozen std source → source/control exact-package review →
root final synthetic Validate → отдельный GO → публикация source → no-skip same-tree
**sibling** control-trigger с тем же parent → fork `.github/workflows/ch8-s2.yml` →
один разрешённый compact member `group-evidence.json.gz` → intake → independent review → admission.
Tree equality не заменяет проверку source/tool/request/workflow/export/invocation identities. [NPK, NI, P3I]

[факт] Supervisor проверяет защищённые snapshots/канонические пути, PID ownership,
reap/cleanup, local continuation против GLOBAL_STOP, atomic durable portable prefix.
Неполный proof не превращается в COMPLETE из-за успешного upload. Штатные timeout и
snapshot drift имеют разные классификации. Это инфраструктурные гарантии, не теорема о sorting. [NI1, NI, P3I]

[факт] Часть lifecycle diagnostics ограничена preview; пропущенные события остаются UNKNOWN. Проверенные completion/shutdown/protected observations не означают полный trace всех событий. [NI]

[факт] S-линия: `--exact`, jobs 1, `--no-assert-contracts`, `--harness-timeout 600s`,
object-bits 12; `function-contracts`, `mem-predicates`, `float-lib`, `c-ffi`,
`loop-contracts`, `quantifiers`, `stubbing`, export-json; explicit sorting/control cfg.
`uninit-checks` и `valid-value-checks` OFF. Имя cfg `s2_assumed` само по себе
не означает enabled summary в новых Original positives. [RES, NPK, NR]
[факт] Набор базовых unstable-флагов и `--no-assert-contracts` согласован с organiser runner
на голове #752; experimental exact-singleton упаковка не является неизменённым PR workflow. [P3, NPK]
[факт] S4P3 positives unwind 36; первые controls 34, Cell control 36. Уменьшить общий unwind
до N+1 нельзя: outside-frame loop проходит 34 элемента. Native unwind sufficiency и
результат для новой кодировки нужно устанавливать заново, не угадывать по длине. [HARNESS, NP, RES]

## 5. Ресурсы и цена уже выполненной работы

### 5.1. Запуски из coordinator ledger

[факт] Срез ledger `26db9b6306…`: item2 used 18; это tracking, не предел.
Подготовка, compile failures и accounting трактуются согласно append-only решениям координатора;
здесь они не пересчитываются. Учётная единица — не число roots и не число закрытых теорем. [L]

| Этап | Учётные run IDs, attempt 1 | Технический итог |
| --- | --- | --- |
| S1, первые три | 43775527125; 43777127361; 43784240498 | Toolchain compile, expensive list, затем partial groups/timeouts. [L] |
| S1, следующие четыре | 43830757263; 43864841077; 43889560779; 43923266772 | Native rows появились, но terse/rich decoder/location/binary-finalization мешали квалификации. [L] |
| S1 composite origins | 44095954742; 44128268928 | Exact original+Cell retry; итог 35/35 composite. [L, S1R] |
| S2 | 44336681406; 44375519132 | Group RSS cutoff, затем singleton timeouts/protected-snapshot stop; не full sorting proof. [L] |
| S3-1-r2 / S3-2-r1 | 44416629057; 44439462279 | Actual leaves и diagnostics, частичные кампании. [S3Q, S32Q] |
| Bridge / S4P1 | 44460583125; 44481580554 | Insert/sort9 и Cell fallback; широкие network цели не завершены. [BQ, FQ] |
| S4P2 / r2 / S4P3 | 44505531344; 44548842328; 44577116178 | Четыре timeout → четыре bounded successes; затем N8/N9 successes, N13/N17 timeout. [NI1, NQ, P3Q] |

[факт] В рассмотренном списке 26 попыток, из них 18 учтённых и 8 charge0. Семь ранних
S1 и восемь charge0 дают 15 попыток без итоговой квалификации кампании. Среди причин
были инфраструктура, кодирование и native timeouts. Часть S1 дала native результаты.
Учёт попыток, расход ресурсов и число закрытых обязательств измеряются отдельно. [L]

[факт] Отдельно ledger сохраняет неучтённые в 18 попытки, а не скрывает их:
43827636574 (workflow schema), 43829165289 (shallow Validate), 44264952389/44284869572/
44302170220/44310254730 (compile/contract closure), 44328364855 (Validate timeout),
44405927807 (controller BEFORE snapshot stop). Они не дали положительных proof results. [L]

### 5.2. Per-family время и sampled память

Все числа ниже — [факт] из COST receipts; округление VT до 0.001 с, GiB=KiB/1048576.
`VT` — exported native verification time, `child` включает compilation и supervision interval;
запас=600−child только у завершившихся cases. RSS — sampled PGID, не kernel/cgroup peak. [SNAP]

| Семейство / case | VT, с | Child, с | RSS, GiB | Запас до 600 с / outcome | Источник |
| --- | ---: | ---: | ---: | --- | --- |
| Swap geometry | 27.297 | 62.995 | 1.843 | 537.005 с | S3I |
| Sort4 separate / same | 78.983 /212.238 | 120.782 /254.769 | 2.447 /2.192 | 479.218 /345.231 с | S3I |
| Merge8 separate | 150.964 | 191.767 | 2.453 | 408.233 с | S3I |
| Merge8 same MU48 allinit | 197.389 | 236.409 | 2.691 | 363.591 с; init-state OPEN | S32I |
| Insert_tail fixed-base p1 | 51.863 | 94.058 | 2.073 | 505.942 с | BI |
| Actual sort9 len 9 | 223.202 | 260.338 | 2.468 | 339.662 с | BI |
| Cell fallback N0..2 /N3..4 | 140.742 /144.622 | 189.050 /193.600 | 2.866 /2.668 | 410.950 /406.400 с | FI |
| Network-r2 N2 /N3 /N4 | 3.061 /3.846 /4.692 | 41.716 /43.751 /44.183 | 2.491 /2.428 /2.109 | 558.284 /556.249 /555.817 с | NC |
| Network-r2 N01 | 33.428 | 72.998 | 2.163 | 527.002 с | NC |
| Network N8 /N9 | 109.308 /207.138 | 143.320 /242.435 | 2.509 /2.470 | 456.680 /357.565 с | P3C |
| Network N13 /N17 | UNKNOWN | 600.071 /600.152 | 2.447 /2.521 | Child wall cutoff, не RSS/compile | P3C |

[факт] Старые insert_tail rel16 / variable-tail в S3 имели RSS cutoffs:
112.349 с и 6.034 GiB; 131.465/126.130 с и 6.067/6.037 GiB. У broad fallback/network bridge,
S4P1 network и всех четырёх symbolic S4P2 — wall 600 cutoffs, при памяти ниже local 6 GiB.
Это разные причины; «все упали по памяти» неверно. [S3I, S32I, BI, FI, NI1, SNAP]

[факт] Campaign wall: S3-1-r2 1454.136 с; S3-2-r1 1068.751 с; bridge 1672.393 с;
S4P1 1779.707 с; S4P2 2535.875 с; network-r2 359.381 с; S4P3 1722.953 с.
Network-r2 setup 531.185 с и whole job 898 с — другие scopes, не 359 с S5. [S3I, S32I, BI, FI, NI1, NC, P3C, S5T]
[факт] N01 занял 33,428 с native VT, N2 — 3,061 с. В N01 bool выбирает между двумя
буквальными вызовами, а post/frame зависят от `n∈{0,1}`. [гипотеза] Разницу может
объяснять кодирование этой длины в post/frame или в ветвлении. Вклад каждого фактора
остаётся предметом отдельного сопоставимого замера. [NC, N01]
[факт] Исторический S1 Cell retry отличался: native stable 617.990 с, unstable 485.290 с,
лимит 1200 с. Его нельзя присоединить к утверждению «всё уже укладывается в 600». [L, S5T]

[факт] Текущий envelope: child 600 включает compile-subcap 180; slot 720; controller 180+
cleanup 240 внутри campaign 6900; outer 7500/step 7560/phase 8100; setup 1800; job 180 мин.
Local 6 GiB, outer owned 12 GiB, reserve 2 GiB, Ceff=min(6, 12,A−2); stdout 16 MiB,
stderr 1 MiB, export 8 MiB, artifact 256 MiB. Полный peak и exclusive solver time UNKNOWN. [RES, S5T]

## 6. Блокеры, ошибки и риски

### 6.1. N13/N17: установленное и неизвестное

[факт] Оба ребёнка достигли whole-child 600, compile-marker upper bound 33.869/32.884 с;
полного native resource/results export нет. Сигнал остановки и cleanup сохранены.
Нельзя вычислять solver time как 600−compile или объявлять нулевые U/FAIL/covers. [P3C]
[факт] Наблюдаемые фазы symex заняли 3,623/5,697 с, преобразование SSA — 0,528/0,670 с.
Первые формулы содержали 455 495/608 369 переменных и 761 349/1 005 707 дизъюнктов.
Зафиксированы шесть и пять завершённых SAT-вызовов соответственно. Последней сохранена
строка `Running propositional reduction`. Итоговый статус запроса, время незавершённой
фазы и вклад тела и оракула остаются неизвестны. N13/N17 идут по маршруту перед merge. [P3C]

[гипотеза] Основной кандидат на дорогую проверку — глобальный счётный оракул и его
композиция. Замена O(N²) на O(N) описывает рост объёма работы исходной проверки.
Стоимость SAT предстоит измерить отдельно. [MODEL, P3C]

[наблюдение координатора, SAT-модель] CaDiCaL 1.7.3 решил пороговые формулы с добавленными
леммами за 0,06 с на N9, 0,45 с на N13 и 0,69 с на N17. Счётные формулы с текущим
оракулом и с одним свободным `q` достигли предела 300 с на N9 и N13. На вставке N5–N7
один `q` оказался в 3–4 раза быстрее текущего оракула, в отличие от результата на
решателе аудитора. Эти времена получены на модели значений с леммами в качестве
допущений. Проверка лемм на телах std и время Kani остаются открытыми. [Результаты повтора](../item2-audit-response-20261120/SAT-CADICAL-RESULTS.md)

[план] В каждом положительном корне `q: u8` выбирается свободно до вызова и сохраняется
на всём пути через компаратор. Само сравнение читает только значения. Пилот связывает
проверенные области листовых контрактов с потребителем и сохраняет точные корни,
safety, frame, unwind и три контроля. Сначала получаем исследовательский результат
для этой декомпозиции. Покрытие порядка и паники за её пределами, UB и типы проходят
свои проверки. [NEXT, CLOSE, ON]

### 6.2. Partial MaybeUninit и остальные UB-классы

[факт] Stock-OFF `is_initialized` не является доказательством initializedness.
Partial-init feasibility plan не исполнялся и остаётся BLOCKED/CONDITIONAL: MU/union layouts,
copy extent/count0/downward address arithmetic, raw AddressOf blessing, exact init-mask frame,
contract capture/typed reads и отдельный ON classifier требуют проверки. [ON]
[факт] Известные значения `[8,48)` и правильно отсортированный dst в MU48 не доказывают,
что все реально читаемые bytes были initialized или что остальные holes остались holes. [S32Q, ON]
[оценка] Нужна новая совместимая ON-линия после item1 fixes: реальный uninit-read +/- control,
copy0/copy-many/downward/overlap controls, затем helpers и scratch caller. Нельзя вручную
«благословить» маску, игнорировать unsupported или импортировать OFF admission в ON. [ON]
[факт] Value-validity и immutable-write/permission остаются самостоятельными пробелами
даже после будущего uninit PASS. Frame равенства значений не исключает forbidden write-restore. [N1, CLOSE]

### 6.3. Что могло съесть время или доказать не то

| Проблема / наблюдение [факт] | Вывод для продолжения [оценка] |
| --- | --- |
| Несколько запусков ушли на несовместимость toolchain, `kani list`, malformed workflow, shallow checkout и contract closure failures; один compile diagnostic потерян bounded preview. [L] | Setup/preflight и полный ограниченный diagnostic нужны до дорогой матрицы; нельзя чинить гипотезу без сохранённого первичного сообщения. |
| Review нашёл selected_roots=8 при 7 rows; writer и local/upload reader принимали неверные types/counts. [RCOUNT] | Integrity bug не sorting counterexample, но ослаблял полноту receipts. Обязателен count из validated inventory и failclosed обоих путей. |
| Review нашёл неполную powerset cfg-матрицу и пропущенный terminal-schema gate. [RGATE] | Число host PASS само по себе не доказывает полноту prebuild/profile gates. |
| Текстовый snapshot-path false positive остановил S3 до полезного proof; S2 interrupted compile дал GLOBAL_STOP. [L] | Различать настоящий drift и надёжно проверенную recovery; не убирать gate ради продолжения. |
| Все маленькие symbolic network roots упёрлись в 600; concrete-call equivalent завершился в прежних caps. [NI1, N01, NP, NC] | Успех encoding существенен, но четыре censored значения не доказывали N-independent стоимость и не локализовали compiler/MIR причину. |
| Final synthetic Validate: 366 tests/685.015 с, затем 389/701.366 с на host; это не native proof. [NG, P3G] | Обвязка сама стала дорогим объектом сопровождения. Сдерживать дублирование gates/framework, не удаляя meaningful error-path проверки. |
| Новый u8/KeyLess helper PASS беднее старых u64/tied-key/Drop/ZST/mutating-F/contract-consumer roots. [P0, S5] | Дешёвые листья нельзя использовать как повод удалить несопоставимые старые гарантии. |
| Exact metadata/U admission требует source interpretation; независимое frontend/emitter binding не установлено. [ZERO, NR, P3R] | Самый рискованный trust seam вынести аудитору явно, а не скрывать за словом QUALIFIED. |

[факт] Планы не закрывают отсутствующие general 0..32, fallback 5..16, network gaps между
принятыми {0..4, 8, 9}, threshold/type/geometry lifting и реальные entry/caller contracts. [CLOSE, P3Q]
[факт] Старый organizer pin блокирует перенос нужной contract/tool поддержки в официальный CI;
наличие fixes в ином main не равно принятию нового pin и совместимой ON-линии. [P1, P2, UPD, ON]

## 7. План завершения: порядок, gates, стоимость

Все следующие строки — [оценка], не assignment, reservation или GO. Root-оценки зафиксированы
в `[SNAP]`; планы S5/closure остаются PLAN ONLY. Каждый native этап требует своего exact-package
review, GO и учёта координатором; обещания fit или полного срока сейчас нет. [S5, UPD]

| Порядок | Конкретный следующий результат | Dependency / успех | Стоимость и время, предварительно |
| --- | --- | --- | --- |
| 1 | Пороговый q-композиционный пилот P-1…P-5: четыре положительных и три контрольных invocation | Exact u8/q domains, providers P-1/P-2/P-3 перед consumer P-4/P-5c; designated controls; полный inventory, роли/covers/safety/unwind; прежние child/RSS caps | Одна исследовательская кампания из семи exact invocations после реализации, review и GO. Время Kani остаётся UNKNOWN. [NEXT] |
| 2 | По результату gate — отдельная оценка order/panic/UB, затем решение о bounded length/type matrix | Не переносить q-PASS на UB, merge panic, произвольные T/F или отсутствующие caller contracts; без gate новые монолитные длины не планировать | Срок и число запусков UNKNOWN; каждый запуск требует exact-package review, GO и строки ledger. [CLOSE, ON, SNAP] |
| 3 | После пилота спланировать остальные классы длин fallback/general/network | Переход разрешает результат декомпозиции и оценка отдельных order/panic/UB обязательств. Классы включают gaps 5..7/10..12/14..16, 18..32 и merge/copyback | Объём запусков определить по замерам пилота и новым доменам. [NEXT, CLOSE, S5] |
| Параллельно | Item1-compatible ON feasibility и controls | Исправить/обойти только обоснованно MU/copy/address blockers; separate flags/schema; затем реальные helper/caller paths | Отдельная дорожка, стоимость OFF не предсказывает ON; deadline UNKNOWN. [ON] |
| 4 | Полные entry PFC и helper→caller applicability | Шесть implementation bodies, scratch/threshold, реальное post/frame; без assumed-provider cycle | Зависит от 3 и tool adoption; safety classes оценивать отдельно. [CLOSE, UPD] |
| 5 | S5 replacement/integration candidate | Old→new domain/property map; native cfg discovery; старое сохраняется без доказанной замены | Предыдущий core-план: 23 positives, 43 invocations в 5 hypothetical campaigns; retained/provider lanes дополнительно. [S5, S5T] |
| 6 | Matched organizer CI и #752 update | Новый принятый pin, тот же final source, полный retained inventory, обе ОС/critical shard/RSS | Сквозной срок пока дни–недели, не обещание; после S4 blocker нужен новый прогноз. [S5T, UPD, SNAP] |

[факт] S5-plan требует не роста total SmallSort native VT относительно matched baseline,
измерения actual critical shard и concurrency (исторически KANI_JOBS=2), setup/build/compile/job wall.
600 с — отдельный harness/child budget, не требование завершить весь CI за 600 с.
Предложенные пять core-campaigns — арифметика, не полная S5 matrix и не уже выданные попытки. [S5T]

[оценка] Критерий «готово»: покрыт согласованный literal scope N1 по всем целям,
контракты реальных entries проверены, caller/preconditions/модели/UB-premises закрыты либо
есть применимое явное решение комиссии; полный integrated inventory проходит принятую CI-конфигурацию,
старые обязательства не потеряны, все ограничения отражены в #752. Ни одного из этих gates
не заменяют новое имя профиля, selected campaign PASS или суммирование bounded admissions. [CLOSE, UPD]

## 8. Вопросы внешнему аудитору

1. Достаточна ли threshold/caller редукция фразы arbitrary valid length, и где её нужно формализовать? [N1, CLOSE]
2. Какая representative-type стратегия допустима, а какие layout/Drop/Cell/ZST классы нельзя свести к u8? [P0, CLOSE]
3. Достаточна ли наша source-level проверка PFC registration/target при отсутствии независимого MIR binding? [S1R, CLOSE]
4. Какие U-аргументы сомнительны: branch exclusions, generated failure edges, definedness без actual-site причины? [NR, P3R]
5. Приемлемы ли exact SUCCESS `0:0` cases, и какой минимальный emitter fingerprint нужен вместо wildcard? [S3L, ZERO]
6. Где у oracle-independent q возможна скрытая зависимость/assumption; сохраняется ли полный multiset и невакуозность? [MODEL]
7. Как отделить цену sort13 от quadratic post и compiler expansion без ослабления свойств и cap escalation? [P3C, MODEL]
8. Что дешевле для full lengths: direct bodies, per-length proofs, loop contracts или qualified summaries с caller DAG? [CLOSE]
9. Какую минимальную ON-последовательность выбрать для MU/copy/address без ручного init blessing? [ON]
10. Как не спутать value frame, initializedness, validity и permission, особенно при write-restore/CopyOnDrop? [ON, CLOSE]
11. Какие старые roots действительно subsumed новой матрицей, а какие должны остаться даже ценой CI? [S5]
12. Какие части нашей runner/review-инфраструктуры избыточны, а какие нужны для достоверности конечного утверждения? [RCOUNT, RGATE, S5T]

## 9. Приложение: источники и воспроизводимость

`P0` — connected PR body/metadata в `[SNAP].pr752`; это зафиксированные слова автора,
не новая проверка исторических 235 verdicts. `[SNAP]` содержит hashes 47 Git-source records
и 56 cost rows, включая негативы; эти числа не являются числом theorem/proof credit.
Таблицы ресурсов округлены; точные поля и происхождение находятся в snapshot и исходных COST.

Для проверки: `git show COMMIT:PATH`; repository+commit+path важнее локального checkout.
Если объект отсутствует в клоне g0, источник и точный SHA указаны в snapshot: std и Kani
имеют разные репозитории. Читать исходные committed отчёты/receipts; acquisition/native scripts
повторно не запускать. Этот отчёт не требует raw logs, full archives или нового CI. [SNAP, NI, P3I]

Префикс путей `kani3300/` ниже: `research/challenge-8/kani-k1/`.

| ID | Репозиторий / путь | Commit | Содержание |
| --- | --- | --- | --- |
| N1 | g0/std: `doc/src/challenges/0008-smallsort.md` | `25b2b24c82a960734a2bab082784747b9b785177` | Официальная формулировка Challenge 8 |
| N2 | g0/std: `doc/src/general-rules.md` | `25b2b24c82a960734a2bab082784747b9b785177` | Общие правила приёмки |
| P1 | g0/std: `tool_config/kani-version.toml` | `872d5a43380752786415bc00d2a12ce0e930cb37` | Pin опубликованного #752 |
| P2 | g0/std: `tool_config/kani-version.toml` | `25b2b24c82a960734a2bab082784747b9b785177` | Pin текущей upstream-базы |
| P3 | g0/std: `scripts/run-kani.sh` | `872d5a43380752786415bc00d2a12ce0e930cb37` | Организаторский runner на голове #752 |
| L | g0/std: `research/challenge-8/kani-k1/CH8-DISPATCH-LEDGER.md` | `26db9b630682cfae8670392ea9236d701f45b481` | Ledger: item2 used 18; учётные решения и S1 admission |
| S1A | g0/std: `kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/accept/ACCEPTANCE.md` | `3c40a15d37890c8b5ef7ba49308e81279a494b05` | S1 composite candidate; финальное решение в L |
| S1R | g0/std: `kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/review/REVIEW.md` | `c4e619d9668eeea860bda1de1790665357a6e399` | Независимое S1 composite review |
| S3Q | g0/std: `kani3300/ch8-s3/admission-r2-qualified/ACCEPTANCE.md` | `b4879b203e42e265f38ce1b44fe767aa78bb43fc` | Четыре actual-body leaf и три контроля |
| S3I | g0/std: `kani3300/ch8-s3/run-44416629057-r1/COST.json` | `31c1dbfc7ca2df34b28bb5eb7ee81bc207ee5642` | S3-1-r2 per-root стоимость |
| S3L | g0/std: `kani3300/ch8-s3/admission-r2-location/ADMISSION.md` | `f74025e493a627962842e8f7bc6a2766d33dd300` | Один exact sort4same missing-location case |
| S32Q | g0/std: `kani3300/ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.md` | `ff193cc35690a5daabaa849d412c58d9f286d893` | Один merge case и три metadata exceptions |
| S32I | g0/std: `kani3300/ch8-s3/run-44439462279/COST.json` | `5d9439a7641c929838bf075c6aa6533a353ee92d` | S3-2-r1 стоимость и RSS cutoffs |
| BQ | g0/std: `kani3300/ch8-s3-s4/admission-bridge-1-r1/ADMISSION.md` | `39606c431ba266a5dbab2163d0e5175428d38aec` | Bridge insert_tail и actual sort9 |
| BI | g0/std: `kani3300/ch8-s3-s4/run-44460583125/COST.json` | `97eaff96cd28267e36af69fe98077dd08737eea6` | Bridge per-root стоимость |
| FQ | g0/std: `kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md` | `9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9` | Два Cell fallback блока |
| FI | g0/std: `kani3300/ch8-s4/run-44481580554/COST.json` | `842984040e87b8b8594653634b72df7d800ca198` | S4P1 стоимость |
| FR | g0/std: `kani3300/ch8-s4/run-44481580554-review-w14/HANDOFF.md` | `3c7bd65cf0bb758cb82dc56ef71a8b8e23efd5c0` | Независимое S4P1 intake/location review |
| NP | g0/std: `kani3300/ch8-s4/network-r2-offline-plan/HANDOFF.md` | `cdedf547df37aec4c442727a902a784f4d1b5155` | Concrete-call план и сохранение unwind 36 |
| NI1 | g0/std: `kani3300/ch8-s4/run-44505531344/COST.json` | `00efb1f5440627362af5c470ad434b89c5e27cca` | Четыре исходных network timeout |
| N01 | g0/std: `kani3300/ch8-s4/run-44505531344/N01-COST-PATH.md` | `00efb1f5440627362af5c470ad434b89c5e27cca` | N01 source/native cost-path uncertainty |
| NQ | g0/std: `kani3300/ch8-s4/admission-s4p2-r2-network/ADMISSION.md` | `8896f60ae9e0ea1c706c6b8693d00e2500190676` | Четыре network-r2 bounded admissions |
| NI | g0/std: `kani3300/ch8-s4/run-44548842328/HANDOFF.md` | `7c66fb85b99f77801ff10e99ccc5d37761ba5442` | Network-r2 intake с per-instance addendum |
| NC | g0/std: `kani3300/ch8-s4/run-44548842328/COST-INTERPRETATION.json` | `7c66fb85b99f77801ff10e99ccc5d37761ba5442` | Network-r2 complete cost projections |
| NR | g0/std: `kani3300/ch8-s4/run-44548842328-review/HANDOFF.md` | `2d872340cdea8c5ff39fbf2cc181af823dcb36a6` | Независимое review четырёх кандидатов |
| NPK | g0/std: `kani3300/ch8-s4/network-r2-impl/HANDOFF.md` | `d10b721e5f9423a0de2602893045c31985e3fbf8` | Реализация с literal-call slices |
| RES | g0/std: `kani3300/ch8-s4/network-r2-impl/RESOURCE.json` | `d10b721e5f9423a0de2602893045c31985e3fbf8` | Флаги, caps, отдельные timing scopes |
| NG | g0/std: `kani3300/ch8-s4/network-r2-go/FINAL-VALIDATE-RESULT.json` | `fef8170d868c64bfa61e6de5eee3450943354ec7` | Root final synthetic Validate, не proof |
| P3Q | g0/std: `kani3300/ch8-s4/admission-s4p3-network/ADMISSION.md` | `65e78d6bafca12a0f07894fe57897e46bc042b4e` | Admission exact N8/N9; N13/N17 BLOCKER |
| P3I | g0/std: `kani3300/ch8-s4/run-44577116178/HANDOFF.md` | `8bf99aa314310e4a3d5b86b8d0f112ddff2886ab` | S4P3 intake: шесть полных inventories |
| P3C | g0/std: `kani3300/ch8-s4/run-44577116178/COST-INTERPRETATION.json` | `8bf99aa314310e4a3d5b86b8d0f112ddff2886ab` | N8/N9 cost и N13/N17 censoring |
| P3R | g0/std: `kani3300/ch8-s4/run-44577116178-review/HANDOFF.md` | `ec49aa6408fdb2bce6f1e15511162aa8664ea0ae` | Review N8/N9 и BLOCKER classifications |
| P3PK | g0/std: `kani3300/ch8-s4/s4-next-impl/HANDOFF.md` | `f485968493d3512f3e719825ef4490866808d120` | S4P3 package, actual source/control identities |
| P3G | g0/std: `kani3300/ch8-s4/s4-next-go/FINAL-VALIDATE-RESULT.json` | `7d7e814de5cf137784ca13dc4957cd63a6e612a3` | Root final 389 Validate receipt |
| ON | g0/std: `kani3300/ch8-s4/init-on-feasibility-plan/PLAN.md` | `83478780666d36ae3c59ebab95d1fdebdaa9cea4` | MU/copy/address/init-mask блокеры |
| S5 | g0/std: `kani3300/ch8-s5/integration-budget-plan/PLAN.md` | `cf0b8f4e9f58eba06099bfb1e813fe416587c0c1` | Legacy-to-new domain/coverage map; 23-positive core proposal |
| S5T | g0/std: `kani3300/ch8-s5/integration-budget-plan/TIME-BUDGET.md` | `cf0b8f4e9f58eba06099bfb1e813fe416587c0c1` | S5 caps/shard/aggregate timing gates |
| CLOSE | g0/std: `kani3300/ch8-s4/completion-and-752-plan/CLOSURE-MAP.md` | `457641417707e7d254e6074bfd1f02c794fde04e` | Полная карта критериев и provider gaps |
| UPD | g0/std: `kani3300/ch8-s4/completion-and-752-plan/UPDATE-752-PLAN.md` | `457641417707e7d254e6074bfd1f02c794fde04e` | Порядок интеграции и обновления #752 |
| ZERO | g0/std: `kani3300/ch8-s4/system-zero-location-feasibility/HANDOFF.md` | `551f11b7a42ca90fbc0cc094fab0e242d32b8cf0` | Общий emitter UNKNOWN, правило не активировано |
| RCOUNT | g0/std: `kani3300/ch8-s3-s4/bridge-1-review/REPORT.md` | `4bd906e8fe1e2dc78afef74d32db8b9e14c2db7e` | Review нашёл неверный selected_roots writer/reader invariant |
| RGATE | g0/std: `kani3300/ch8-s4/s4p-1-review/REVIEW.md` | `4856a87f39d2606adbbed747d3cae9a73fb80d52` | Review нашёл неполную cfg-матрицу и schema gate |
| STD | g0/std: `library/core/src/slice/sort/shared/smallsort.rs` | `7b31b060b90ce286e94547993f6a698c549bc5fa` | Точный actual runtime SmallSort, network 13/17 до merge |
| MODEL | g0/std: `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs` | `7b31b060b90ce286e94547993f6a698c549bc5fa` | Полный logical-byte model, count O(N²) |
| HARNESS | g0/std: `library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs` | `7b31b060b90ce286e94547993f6a698c549bc5fa` | Четыре concrete-call roots, V34/base1/unwind 36 |
| TOOL | Kani: `rust-toolchain.toml` | `0aac16ef62da9e9d5645782d458593e5d78143ba` | Stock tool nightly declaration |
| DEP | Kani: `kani-dependencies` | `0aac16ef62da9e9d5645782d458593e5d78143ba` | Декларируемые CBMC 6.11.0 и Kissat 4.0.1 |
| PLANV2 | g0/std: `research/challenge-8/kani-k1/PLAN-CH8-ITEM2-SORTING-v2.md` | `ee47c841c01c275ead16c0b15382782b6550d516` | Декомпозиционная ветвь §5 и P2 |
| MERGEPILOT | g0/std: `kani3300/ch8-s2/merge-pilot/HANDOFF.md` и `INVARIANT.md` | `c8e4ab764d58bd8b684b660d92c62374530623d4` | Offline invariant, Kani NOT_RUN |
| S2R5 | g0/std: `kani3300/ch8-s2/run-44375519132/VERDICTS.md` | `ee47c841c01c275ead16c0b15382782b6550d516` | Статусы двух cutoffs, general32 DEFERRED_NOT_SELECTED |
| SOLVER | Kani: `kani-driver/src/call_cbmc.rs` | `0aac16ef62da9e9d5645782d458593e5d78143ba` | CaDiCaL и порядок CLI/harness/default при выборе решателя |
| NEXT | g0/std: `research/challenge-8/kani-k1/item2-audit-response-20261120/NEXT-STAGE.md` | `543d32cccc81c9ff71752642caeb11a6ade74733` | Решения владельца о q-пилоте и исследовательской дорожке |
| CAD | g0/std: `research/challenge-8/kani-k1/item2-audit-response-20261120/SAT-CADICAL-RESULTS.md` | `dea64fcdad63832975dd1cc0409ce7e8665eeca9` | Результаты координатора на SAT-модели |


## Приложение А. Обозначения инвентаря и измерений

- **U / metadata exception** — статус UNREACHABLE и отдельно рассмотренное исключение для конкретной записи с неполной координатой.
- **VT / child / compile marker** — нативное время проверки, время дочернего процесса с компиляцией и верхняя граница до наблюдения начального экспорта.
- **RSS / sampled PGID / headroom** — резидентная память, её выборочная сумма для группы процессов и доступный запас относительно лимита.
- **Intake / native inventory / source binding** — разбор сохранённых результатов, список проверок инструмента и привязка записи к точному входу и месту в исходнике.
- **Same-tree sibling / exact package** — коммит запуска с тем же деревом и родителем и прошедший ревью пакет с закреплёнными версиями.
- **Init-state / value frame** — состояние инициализации и сохранение известных значений за пределами записи.

## 10. Дополнение координатора

**Как была организована работа.** Пункт 2 вели планер (отдельная сессия Codex) и четыре воркера Codex; координатор (Claude) распределял стадии, проверял результаты и вёл учёт запусков. Каждая стадия — отдельная сессия агента с заданием (TASK) и отчётом (HANDOFF) в репозитории. Перед каждым запуском CI — независимое ревью другим агентом, затем GO и строка в журнале запусков (`research/challenge-8/kani-k1/CH8-DISPATCH-LEDGER.md`). Агенты работали в «чистой комнате»: им не давались чужие решения этого челленджа. Публикации (PR, комментарии) — только по команде владельца.

**Последовательность разрешений.** 2026-11-15 — план пункта 2 и S1 в рамках выделенного владельцем бюджета. 2026-11-18 — владелец добавил +3 запуска на S2-r5…S5 (с одним резервом) и передал решения о GO для CI координатору вместе с планером. 2026-11-19 — бюджеты стали учётными, а не ограничивающими: каждый запуск по-прежнему требует ревью, GO и строки в журнале.

**Сроки и учёт.** Первый запуск — 2026-11-15 23:34 UTC (43775527125), последний — 2026-11-19 17:26 UTC (44577116178): около четырёх дней активной работы, параллельно с исправлениями в Kani (пункт 1, 49 запусков). По пункту 2 учтено 18 запусков. Ещё 8 записаны с нулевым списанием по заранее принятому правилу: запуск упал до первого доказательства (ошибка компиляции, схема, валидация, остановка контроллера). Нулевое списание не означает, что запуск ничего не стоил: каждый перезапуск проходил отдельное ревью и GO.

**Что пошло не так организационно.**
- Большая доля усилий ушла на обвязку, а не на доказательства. Из 9 запусков S1 первые семь остановились на инфраструктуре (схема вывода, декодер, привязка к исходникам, финализация), и только два дали проверенный результат. Восемь незачтённых запусков — тоже инфраструктура. Строгие проверки целостности оправданы для внешнего аудита, но синтетические тесты обвязки покрывали меньше, чем настоящий запуск, и часть ошибок всплыла только в CI.
- S2 был пробным замером стоимости на крупных размерах (general 32, merge 32, sort13). Он показал пределы памяти и времени, но положительных доказательств не дал. С S3 работа идёт от малых N вверх.
- Были ложные срабатывания наших собственных проверок (путь snapshot в S3, неверный счётчик selected_roots) — каждое стоило запуска и цикла ревью.
- Блокер N13/N17 (таймаут child600) обнаружен только в S4P3. Оценку стоимости оракула O(N²) стоило сделать до планирования длин выше 9.
- Пункт 2 делил агентов с пунктом 1 (исправления Kani upstream); после 2026-11-19 новых запусков по сортировкам не было.

**Что изменим.** Новые проверки обвязки — с синтетическими тестами на те случаи, где уже были сбои. Размеры наращивать от малых N, с оценкой стоимости до запуска. Для N13/N17 — сначала гипотеза оракула с одним `q: u8` (раздел 6.1) на малом пилоте. Независимую сверку отчётов (как эта: 120 групп утверждений, 118 подтверждены, два дефекта исправлены) делать перед каждой передачей наружу.
