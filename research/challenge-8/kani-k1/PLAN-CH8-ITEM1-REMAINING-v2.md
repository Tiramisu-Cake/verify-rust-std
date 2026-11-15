# Challenge 8, пункт 1 — план v2 после независимого аудита

2026-11-15. Черновик для владельца; заменяет приоритеты v1, а не историю свидетельств.
Это верификация корректности, не security-работа. **Fork CI, Cloud $0; локальные сборки/verifiers запрещены.**
Этот документ не публикует сообщения/PR, не выдаёт задания и не разрешает CI или push.
Основание: [v1](PLAN-CH8-ITEM1-REMAINING.md), аудит g0 `37e33e983f`,
[план пункта 2](PLAN-CH8-ITEM2-SORTING.md), рабочая трактовка требований от 24.10.

## 1. Ответ на F1–F10

| Находка | Моя оценка и изменение |
|---|---|
| **F1** | Согласен: у v1 нет исполнимой unbounded-дорожки с отдельным gate. Добавляю **E** первой технической волной. В плане пункта2 индукция уже разобрана; это одна общая работа, не две независимые реализации |
| **F2** | Согласен с критическим путём upstream→pin→CI организаторов и ограничением WIP. Рекомендую PR-01/02 сейчас, не ждать реакции только на #5172. Категорический запрет любого fork pin из текста правил не следует: исключение возможно лишь после явного принятия, по умолчанию планируем upstream pin |
| **F3** | Согласен: свою реализацию C1 снимаю, включаю RFC/cooperation и C-сейчас. Описание отсутствия alias model **на C2 pin** верно, но выбор нового собственного проекта устарел. Frame/disjointness не объявляю полной temporal/alias моделью |
| **F4** | Согласен: предыдущий опыт VeriFast надо было учесть. Новую разработку этого трека закрываем в данной дорожной карте; новый «пятидневный старт с нуля» снимается, архив сохраняется |
| **F5** | Согласен: статический `Profile::cmp` устраняет искусственную FnPtr-преграду в наших verification wrappers. Общий FnPtr-проект не нужен на ближайшем критическом пути. Нужна переквалификация всех leaf/consumer и карта старых comparator-controls |
| **F6** | Согласен с census и узким fast path, с координацией существующих реализаций. Не согласен, что пустой список validity requirements всегда достаточен или что generic source-check копии заведомо без ложных отказов; конкретные риски ниже |
| **F7** | Согласен: scratch 8/16/18/32 и scale probe прежде общих расширений. Replace может оказаться ближайшим blocker. Предложенный nondet-shadow/ensures — гипотеза для spike, не готовая корректная модель |
| **F8** | Согласен: сначала координация с исполнителем #5104, затем небольшой вклад с struct/tuple controls. Одинаковые size/align/traits дают аргумент покрытия **ветвей**, не доказательство корректности array lowering |
| **F9** | Согласен: нужны решения, STOP, CI-count budget и Limitations trace. 81–173 дня показывают чрезмерный backlog; это сумма вариантов, включая альтернативы, а не обязательная последовательность всех работ. V2 ограничивает первую итерацию |
| **F10** | Согласен: фиксирую владельцев/параллельную upstream-работу через issues, precise pin/RFC status и условность уровней. Чужие PR не перечисляю, чтобы не дублировать их работу/ссылки в заданиях |

### Где аудит требует технических оговорок

1. **Уровни:** трактовка 24.10 E1 делает все четыре UB-класса **М**. E2 переносит лишь невыразимую часть
   в **В с раскрытием**, и только **если комитет примет #733**. B нельзя уже сейчас целиком понизить до К.
2. **C-сейчас:** отсутствие возвращаемых ссылок снимает конкретный returned-reference сценарий из #733,
   но не живые callback/temporary borrows и последующее использование aliases внутри вызова SmallSort.
   Outer `modifies(v)` разрешает писать в v; оно не определяет, в какой момент этого делать нельзя из-за live `&T`.
3. **B-small:** `ty_validity_per_offset(...)=[]` бывает следствием неполного моделирования, а не доказательством
   «любые биты валидны»; текущий array/union fallback и aggregate enum — примеры. `Err`/unknown нельзя пропустить.
4. **Raw copy:** bytes могут быть временно invalid/uninitialized и перезаписаны до typed read. Это законный случай,
   в том числе в исходном #3762. Консервативный producer-check может быть полезен для конкретного SmallSort пути,
   но не является автоматически полной generic реализацией copy/memmove.
5. **Replace/loop havoc:** pinned `can_dereference` вызывает `assert_is_initialized`, а комментарий в API прямо
   запрещает использовать demonic initializedness как обычное assumption. Поэтому «havoc shadow, assume ensures»
   надо обосновать отдельно; нельзя ограничить выбор witness так, чтобы hole перестал наблюдаться.

## 2. М/К/В — восстановленная рабочая классификация

[Трактовка 24.10](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d70d85eb021bd7e264f22acab0c371502c2420a0/research/challenge-8/REQUIREMENTS-INTERPRETATION-2026-10-24.md):
**М** — минимум для подачи по нашей интерпретации; **К** — конкурентное усиление;
**В** — вне выбранной области с явным раскрытием. Это не заменяет ruling организаторов.

| Обязательство | Уровень / условие | Дорожка |
|---|---|---|
| SAFETY/default UB, реальные helpers и trait routes, все соответствующие threshold lengths | М | A1, профили, U |
| insertion_sort_shift_left: любая допустимая длина/offset, включая inner insert_tail | **М**, B4 | **E** |
| Автоматические uninit, invalid value, immutable-byte checks | **М по E1**, пока не принят иной scope | A1/E, B, C-сейчас/U |
| Не выражаемые инструментом части E2 | В **только после принятого #733 ruling**; выразимые остаются М | U, B, C-сейчас |
| Представительные T с покрытием всех наблюдаемых type/size branches | Рабочий М; спорную достаточность уточнить в #734/#56 | A1, D, U |
| Формальный generic T theorem (C5), panic/unwind (D3) | К по трактовке 24.10, явно раскрыть ограничения | Не ближняя волна; U подтверждает scope |
| Общие FnPtr/vtable, SCC-рекурсия, все Replace/Recursive режимы как feature продукта Kani | В для ближайшего проекта, если не требуется actual proof graph | Не начинать; точечный Replace gate ниже |
| VeriFast tool/proof development | Закрыт в этой дорожной карте | Архив, без нового spike |

[#733](https://github.com/model-checking/verify-rust-std/issues/733) и
[#734](https://github.com/model-checking/verify-rust-std/issues/734) OPEN, окончательного ruling не найдено.
Поддержка одним участником обсуждения или отсутствие возражений не являются решением комитета.
Вопрос о длине insertion в [#56](https://github.com/model-checking/verify-rust-std/issues/56) также остаётся без ответа.
До ответа сохраняем E, а не предполагаем разрешение ограничиться N20/N32.

По VeriFast учитывается [бриф 24.10](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d70d85eb021bd7e264f22acab0c371502c2420a0/research/challenge-8/ALTERNATIVE-TOOLS-BRIEF-2026-10-24.md),
а не предполагается новый инструмент с чистого листа: там уже были значительные доработки форка и blockers
`&mut [T]→as_mut_ptr`/panic+CopyOnDrop. Их снятие в этом разборе не установлено; повторный «стартовый spike» не обоснован.

## 3. Текущая база: законченная SEL1-квалификация, не завершённый challenge

- C2 `8e299aa6243bc5f06a29c51e98aafa9564478220`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`.
- SEL1-C2 `14bc57fdb99960240c4944845a3d985c8af4dcf7`, tree `1efb6e4dfa69d346df8e23741d11839b1932403d`.
- Quick **43740679160**, [Gate A 43744142824](kani3300/sel1-c2/gatea/run-43744142824/ACCEPTANCE.md):
  33/33 стадии на трёх платформах, expected +29, остальное без неожиданных изменений.
- [Replay 43751703000](kani3300/sel1-c2/replay/run-43751703000/RESULT.md): обе merge, sort4, swap и raw-legal SUCCESS;
  raw-negative — единственный задуманный uninit-read. Bounded geometries/closures, **valid-value OFF**.
  В v1 эти gates были ещё будущими; теперь повтор только из-за нового source/pin, не ради повторения результата.
- #752 остаётся bounded proposal со своими Limitations; его pin/source и organizer pin не равны SEL1-C2.
  Совпадение названий roots не переносит новые доказательства в старый submitted tree.

## 4. U — upstream, scope и CI организаторов: первый критический путь

Цепочка выпуска: **review архитектуры → принятый стек/согласованные изменения → organizer-compatible pin
→ принятый targeted CI step с нужными flags → успешные PR checks solution**.
Fork evidence необходимо, но само по себе не выполняет gate «проверяется у организаторов».
Правила требуют integrated tool и PR CI; обычный путь — upstream pin.
Письменно согласованное исключение возможно, но не закладывается как уже полученное.

### U1. Подача стека и WIP

Рекомендую заменить ожидание реакции на один #5172 подачей **PR-01 и PR-02 сейчас** как зависимых reviewable PR.
Это изменение рекомендуемого submission trigger из старого INDEX; сам INDEX здесь не переписывается.
Сохраняются parent dependencies/cumulative-diff disclosure и точное описание deferred integration tests.
PR-01 не имеет собственных end-to-end tests этой feature; успешные cumulative tests надо назвать честно.
Не превращать его regression run в доказательство самостоятельного нового поведения.

| Часть | Exact source | Зависит от | Статус на входе / следующий шаг |
|---|---|---|---|
| B1 | `6fe484b300` | upstream `0aac16ef62` | Наш [#5172](https://github.com/model-checking/kani/pull/5172) OPEN, без reviews; не подавать повторно |
| PR-01 analysis | `d82752c8bc` | B1 | Текст/qualification готовы; предложено подать сейчас |
| PR-02 immutable seeds | `932fb8395a` | PR-01 | То же, со всей dependency disclosure |
| PR-03 layout/raw_eq | `5ca51679e3` | PR-02 | Готовый последующий срез; очередь после review/backpressure |
| PR-04 storage/protocol | `345cedfd67` | PR-03 | Крупный архитектурный срез; заранее показать дизайн и cumulative evidence |
| PR-05 closure layout | `96f5d5dc8d` | PR-04 | Следующий зависимый срез |
| PR-06 edges/docs | `3f5242bb15` | PR-05 | Следующий зависимый срез |
| PR-07 isolation | `8e299aa624` | PR-06 | F7, последующий срез |
| SEL1 | `14bc57fdb9` | C2 | Квалифицирован отдельно; PR-текст отдельной стадией |

Прогресс U считать по принятым/поданным частям и разрешённому CI step, не по количеству новых branches.
Предлагаемый WIP: **до публикации PR-01/02 и design note — 0 новых compiler designs**;
затем **не более 1 незавершённой compiler-feature ветки** по конкретному A1/E/B blocker.
Узкий независимый fix можно предложить после U1; изменение shadow/Replace архитектуры ждёт feedback на design note
либо отдельного решения владельца, а не становится разрешённым автоматически после отправки сообщения.
Annotation/test-only/profile работа допускается отдельно при непересечении файлов.
Первое review-окно: #5172 + PR-01/02; не вываливать оставшиеся шесть работ без feedback на архитектуру.
После review/merge проверять actual patch/parent, не переписывать принятые receipts под новый SHA.
Пересечения upstream отслеживать через [#4852](https://github.com/model-checking/kani/issues/4852) и #3300.

### U2. Два приоритетных внешних черновика — публикует владелец

**В #56 либо #752, один основной thread:**

> Before extending the proof, could you clarify (1) whether insertion_sort_shift_left must be checked for
> arbitrary valid length and offset, beyond SmallSort's caller thresholds; (2) whether representative types
> covering every type/size/specialization branch are sufficient, or a generic-T theorem is required; and
> (3) whether a separate CI step for selected SmallSort harnesses with -Z uninit-checks, and later a separately
> qualified -Z valid-value-checks step, would be accepted? Which upstream Kani pin/integration path should it use?

**Design note в [#3300](https://github.com/model-checking/kani/issues/3300):** задача challenge, exact pins,
девять частей/dependencies, один-witness shadow model, storage masks/direct-call protocol,
immutable seeding vs write permission, selected-body analysis/isolation, bounded positive/negative evidence,
стоимость и unsupported boundaries. Отдельные вопросы: приемлема ли архитектура/нарезка;
какой shape init summary допустим для Replace/loop havoc; как согласовать дальнейшие маленькие fixes.
Не заявлять весь #3300 решённым и не начинать новую модель до review существующей.

Дополнительные адресные сообщения — после материала: дизайн малого B-fix в #3762,
вопрос исполнителю #5104 о текущей локализации, feedback/tests к RFC через #5040/#733.
Этот файл не отправляет ни одного из сообщений.

**Gate U:** upstream-совместимый pin, явное принятие step/flags/scope, действительный запуск **CI организаторов**
с полным manifest выбранных proof roots и useful checks. Dispatch форка и optional job, фактически SKIPPED на PR,
этот gate не закрывают. До него результат обозначается «fork evidence / proposal».

## 5. A1 — actual scratch и ранняя проба масштаба

Первый batch с uninit ON: actual general N8, general N16, network N18 и самый тяжёлый выбранный scratch-route N32.
Для начального u64 profile это sort4/sort8 и merge-переходы, а не только insertion без scratch.
Проверить stable flat `[MU<T>;48]`, general `MU<[T;48]>` и network scratch32 в coverage map;
не требовать все варианты в одном дорогом первом запуске. Source/runtime bytes и actual targets остаются реальными.
Comparator — direct body/closure с чтением аргументов и arbitrary bool, без незаконного конструирования slice над holes.

Сначала as-is N32, jobs1, organizer object-bits12/default checks, 600s/root и measured RSS.
Дешёвый OFF companion отличает рост инструмента от базовой стоимости. Зафиксировать также стоимость driver,
а не только CBMC; budget для organizer parallelism должен учитывать совокупную память, не одну успешную строку.
Возврат/covers/полезные reads обязательны; Unsupported до scratch не считается проверкой scratch.

Сохранить короткий пакет exact [#5020](https://github.com/model-checking/kani/issues/5020),
[#4854](https://github.com/model-checking/kani/issues/4854), [#5151](https://github.com/model-checking/kani/issues/5151):
offset-hole, crash/refusal, flat Drop-storage legal/hole. Корень Pat offset исправлен C2; точный repro нужен для scope
и просьбы закрыть issue. Удачный соседний test не даёт автоматически «Resolves».

**STOP A1:** 600s/RSS limit, missing return/checks, unsupported layout/intrinsic/dispatch либо differing bindings.
Результат — названный первый blocker и отдельные verdict/resource данные, не обход checks и не sweep всех N.
Если actual-body N32 не помещается, измерить одну обоснованную декомпозицию. Тогда ближайший проект —
возможно **Replace**, не общий FnPtr. Новый compiler design — только после U/WIP gate.

## 6. E — произвольная длина insertion: spike 3–5 дней

Это safety-дорожка М, общая с induction пункта2. На pin уже есть `-Z loop-contracts`,
а в std есть pointer/slice loop annotations (`str/pattern.rs`, `slice::reverse`); из этого ещё не следует
готовность именно нашего hole/guard loop с uninit. Не переписывать runtime std для подгонки под verifier.

Последовательность:

1. Калибровать base/step/frame/decreases на actual pointer loop, сравнив ON/OFF и отрицательный invariant/frame.
2. Получить **symbolic-length region без константного backing cap и без kani::unwind для целевого цикла**,
   с valid allocation/byte-size/offset preconditions. `[T;32]` + loop invariant не arbitrary-length proof.
3. Outer while: same allocation, tail∈[base+offset,end], valid/readable prefix и остальные входные элементы,
   допустимые writes/frame. Inner head: begin≤sift<tail и gap_guard.dst=sift+1 **в этой program point**;
   tmp владеет вынесенным элементом, hole не читается, предыдущие moved bytes не выдаются за initialized T.
4. Доказать repair и возвращение полностью initialized области. Для ZST отдельный случай:
   указательная дистанция не является счётчиком элементов. Termination — убывающее логическое расстояние.
5. Скомпоновать fallback defaults через доказанную вставку, затем проверить threshold callers/traits.
   Для пункта2 отдельно усилить invariant sorted prefix/permutation; не навешивать эти расходы на первый safety spike.

**STOP E:** не удаётся выразить symbolic storage, dropped/unsupported invariant, неверный frame control,
uninit shadow теряется после havoc, compilation blocker, либо cap. Выдать минимальный reproducer и issue;
не уменьшать len до32 и не называть результат unbounded. Связанные issues/controls —
[план пункта2, §5](PLAN-CH8-ITEM2-SORTING.md#5-kani-loop-contracts-и-quantifiers-возможности-и-риски-на-pin).
Существование invariants в других std-функциях не устанавливает совместимость с MU/hole/Drop.

### Если нужен Replace/loop-havoc fix

Один предварительный design gate: havoc затрагивает shadow разрешённой области, сохраняет outside и фиксированный witness,
а must-init summary следует из реально доказанного callee/invariant. Legal + unwritten-byte + false-bit-preservation
controls обязательны, включая aliases и normal-return-only behavior. Аргументы/return отдельно.
Pinned [mem.rs](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/library/kani_core/src/mem.rs#L73-L79)
использует assertion для initializedness из-за demonic nondeterminism; `ensures(can_dereference(...))`
не считать готовым assume-able init summary. До этой проверки estimate «малый фикс» не принимается.
Эта опция не имеет автоматического разрешения или бюджета сверх spike E.

## 7. Профили — статическая диспетчеризация вместо общего A2

Заменить `Profile::CMP: fn(...)` на `fn cmp(&Elem,&Elem)->bool` и прямую closure `|a,b| P::cmp(a,b)`
в verification wrapper. Wrapper больше не принимает произвольный comparator pointer.
Это изменение **verification-модулей**, не алгоритма SmallSort; новый actual helper call уже использует direct comparator.
Не требуется доказывать старый FnPtr wrapper, от которого мы отказываемся; требуется заново доказать новые wrappers/consumers.
Общий A2/FnPtr, vtable и SCC не начинаем ради искусственного пути профиля.

Карта правок: profiles/identity macro, swap/sort4/merge wrappers, все их callers, covers, forwarding wrappers,
stub_verified consumers и model/comparator relation. Адресный canonical guard больше не подходит.
Старые wrong-F controls сопоставить с новой гарантией API/типов и bad-profile/relation negative;
не удалить их молча и не требовать ровно прежнее число failures без сохранения смысла.
Same T/P/F/geometry между leaf и consumer квалифицировать повторно: тип comparator изменился.

**Приёмка:** не осталось unintended FnPtr/cast coercion в migrated call graph; real bodies исполняются;
leaf/consumer проверены и с ordinary/ON профилями, где это поддержано; probe/full-value checks сохранены;
wrong-model negative, frame и payload corruption обнаружены. Речь о закрытых profiles, не arbitrary FnMut theorem.
**STOP:** скрытый indirect edge, FnDef-shim/layout blocker, weakening property/frame, новая codegen need или CI cap.
Первая оценка **2–4 дня**, но это с полной переквалификацией, не с переносом старых результатов на новое дерево.

## 8. B — census, доказанный no-requirements fast path, ограниченные producer checks

1. Один diagnostic dispatch прежних **235 ordinary roots** с valid-value ON, точным manifest и тем же std/pin.
   Разбить по штатным shards, без autoharness всего std и без новых cfg-on controls.
   Классы: PASS; copy Unsupported; casts; other Unsupported; intended invalid-value failure;
   compile/resource/not-run. Достигнутые default checks и полезные reads сохраняются.
   Обрезанный census — PARTIAL, а не «остальные PASS». Данные по чужому challenge не прогноз SmallSort.
2. Спроектировать минимальный fast path для **доказанно all-bit-valid** pointee: начать с конкретных integer primitives.
   Нельзя принимать `Ok([])` как сертификат для любого T: текущая функция даёт пустой результат и для
   некоторых недостаточно моделируемых array/union/enum cases. Нужны NoConstraints / Constraints / Unknown;
   Unknown/Err остаётся отказом. Не чинить весь validity pass в том же маленьком патче.
3. С координацией в [#3762](https://github.com/model-checking/kani/issues/3762) проверить консервативную
   source-validity модель для **действительно typed-valid initialized copy sites SmallSort**.
   Raw invalid-bytes→overwrite-before-read legal companion обязателен; raw invalid-bytes→typed-read должен падать.
   Отдельно padding, MU, overlapping copy/memmove, обе стороны mutable casts.
4. Добавить bool/char/NonZero families. U8/U64 fast path лишь снимает бессодержательный отказ;
   сам по себе не демонстрирует проверку restrictive validity. Не все casts симметричны:
   MU→T с пустыми source constraints может проходить, обратный T→MU — задевать существующую проверку.

Не начинаем собственные реализации [#5022](https://github.com/model-checking/kani/issues/5022) и
[#5023](https://github.com/model-checking/kani/issues/5023): уже есть внешняя работа, автор kasimte,
координатор/assignee feliperodri. Следим через issues за status/scope; до adoption/qualified replay они не «закрыты».
[#5156](https://github.com/model-checking/kani/issues/5156) и reference/Box validity тоже не объявлять решёнными этой работой.

**STOP B:** неизвестность трактуется как no requirements; legal delayed raw-copy получает ложный отказ;
проверка читает uninitialized bytes до допустимого typed production; пропал intentional invalid-value check;
требуется новая shadow-модель вместо малого fix; выявлено пересечение с активным upstream design.
Тогда — design note/ограниченный исход, не месяцы новой подсистемы по умолчанию.
B остаётся М по E1; перенос части в В возможен лишь после ruling #733.

## 9. C-сейчас — что выражают frames; чужую alias-модель не дублировать

Снять собственную C1-реализацию из v1. [#5040](https://github.com/model-checking/kani/issues/5040)
OPEN, High Priority, взят feliperodri 6 ноября.
[RFC 0016](https://github.com/model-checking/kani/blob/98bf6a427b8f29154f21165c239528f0742723c5/rfc/src/rfcs/0016-aliasing-checks.md)
Under Review: `-Z aliasing-checks`, Tree Borrows monitor/instrumentation, byte-level UnsafeCell,
function/loop contracts. Это новая upstream-дорожка, отсутствующая на C2 pin, а не опция, которую мы забыли включить.
Monitor отдельно ещё не означает готовую instrumentation; есть backend dependencies, inconclusive indirect cases
и PoC resource cost порядка10–20×. Эти cross-challenge цифры не являются измерением SmallSort.

**За 2–3 дня без compiler changes:**

- Инвентарь всех shared spans: merge source, callback inputs, local ManuallyDrop; кто и когда может писать.
  Для каждого edge: real body/stub, frame, disjointness, captured/global effects, после-call uses.
- Использовать уже доказанные modifies + disjoint requires для конкретных write-confinement claims.
  Merge source/dst — хороший имеющийся случай. Frame трёх trait entries добавлять/проверять на pin с fixes #4908/#5116,
  для заявленного callback domain; не объявлять generic FnMut frame решённым одним modifies(is_less).
- Два разных негативных контроля: write-then-restore в **merge source вне dst frame** должен нарушать frame;
  transient write за callback `&T` **внутри разрешённого outer v frame** проверяет недостающую temporal модель.
  Если второй проходит, это documented alias gap, а не разрешённое Rust-поведение и не C PASS.
- Legal disjoint external callback state/UnsafeCell companion; local-temp/ref lifetime и reuse после callback.
  Не запрещать законную interior mutability общим «все bytes readonly».
- Оформить отзыв/tests для RFC по #5040/#733; ранний measurement на готовой upstream ветке — только после отдельного GO,
  с exact source/backend pin. Не обещать, что один draft monitor уже запускает alias checks в наших roots.

**STOP C:** frame не покрывает callback/captures; нужны lifetime/tag checks, которых нет; legal UnsafeCell rejected;
классификация требует недоказанной полноты borrow inventory. Выдать precise proven/gap таблицу, не реализовать Tree Borrows самим.
В Limitations можно уточнить **какие write sets/disjointness реально доказаны**; фразу «all immutable mutations checked»
не писать до соответствующего свидетельства/принятого scope. Ни #733, ни отсутствие returned refs это ещё не разрешают.

## 10. D — сотрудничество по #5104, затем минимальный вклад

[#5104](https://github.com/model-checking/kani/issues/5104) OPEN, High Priority, assignee feliperodri.
Сначала владелец спрашивает о текущем диагнозе/нужном материале. Уже есть [static recon](KANI5104-RECON.md);
не начинать параллельный compiler/backend rewrite и не ждать ответа, простаивая на других независимых задачах.
Если нужен пакет: исходный repro + plain-if/scalar controls, затем struct и tuple с совпадающими size/align/traits.
Сопоставлять actual MIR/GOTO/адрес/value на одном pin; compact trace omission не доказательство отсутствующего store.

Замена array на struct может быть допустимым представителем **ветви** при согласованном type coverage argument.
Это не доказательство самого array case и не исправление #5104. Сохранять исходную Caveat до exact replay/patch.
**STOP D:** нужные данные уже собирает maintainer, нет нового различающего вопроса, cap или нет binding.
Различать source-reported false counterexample и неизвестность false SUCCESS; не объявлять всю модель неправильной.

## 11. Решения владельца, ожидаемые события и ограничения незавершённого

| Решение | Предложение/статус v2 | Триггер пересмотра |
|---|---|---|
| Уровни | Восстановить 24.10, не переносить B/C целиком в К/В до ruling | Ответы #56/#733/#734 и review #752 |
| Диспетчеризация profiles | В v2 выбран рефакторинг по позиции координатора; общий A2 снят | Named FnDef/layout blocker после рефакторинга |
| VeriFast | Новая разработка закрыта, отменить соответствующий spike и в общем плане пунктов1/2; архив сохранить | Только новое явное решение владельца при изменении стратегии |
| PR-01/02 | Предлагается подать сейчас со stack/dependency notice, не ждать реакции только на B1 | Архитектурный feedback/changed parent, policy maintainer о стеке |
| Внешние сообщения | Приоритет два: scope+CI в #56/752 и design note в #3300; публикует владелец | Ответ → обновить scope, WIP и CI gate |
| Новый compiler code | 0 до U1; затем максимум одна feature-ветка из конкретного A1/E/B результата | Review разрешает дизайн либо требует остановить/переделать |
| Replace | Только design/controls после scale/E result; не предрешён готовым решением | Actual timeout либо uninit+havoc blocker |
| B-small | Census и certified primitive fast path; source-check только с legal delayed-copy companion | Дизайн в #3762, пересечение upstream, unexpected false positive |
| RFC early usage | Controls/отзыв сейчас; запуск aliasing ветки отдельно после GO и готовой instrumentation | Upstream availability/backend deps/resource evidence |
| Итоговый tool pin | Upstream-compatible integrated commit + принятый organizer step; fork pin лишь при явном исключении | Фактический organizer pin/CI решение |

Важные внешние статусы: #5040/#5104 — feliperodri; #5022/#5023 — существующая сторонняя реализация,
не наш новый backlog; #4852 — пересекающаяся upstream работа, повторная проверка перед rebase/submission.
Остальные issues v1 — каталог границ, а не автоматический список обязательных наших patches.
Интеграционный конфликт или scope ruling сильнее первоначальной оценки дней/числа задач.

## 12. Limitations #752 → дорожка → условие изменения формулировки

| Нынешняя оговорка | Дорожка | Необходимое свидетельство для снятия/сужения |
|---|---|---|
| Нет uninitialized-memory instrumentation на заявленных routes | U+A1+E+профили | Exact solution/tool pin, actual route matrix ON, useful checks/negatives, arbitrary-length insertion gate, принятый и выполненный organizer CI step |
| Value-validity не поддерживает copies | B+U | Census, certified fast path, restrictive bool/char/etc controls и remaining refusal map; снимать только для реально квалифицированных типов/операций |
| Immutable-byte/aliasing model отсутствует | C-сейчас+U | Checked frame/disjointness claims уточняют текст, но не заменяют temporal model; full removal требует соответствующего alias evidence или явного scope ruling |
| Bounded lengths / representative T/geometry | A1+E+U | Полная threshold matrix с доказанными callers, no-cap/no-unwind insertion theorem; принятое обоснование T branches либо более сильный proof. Полнота one-profile не всеT |
| Arbitrary FnMut footprint не выражен | C-сейчас+профили | Реальные callbacks или sound summaries с точным эффектом; static profile даёт лишь закрытый comparator domain |
| Прямых trait contracts нет | План пункта2+U | Integrated pin с исправленными #4908/#5116, actual selected impl, guard active и substantive ensures; это не автоматически safety/все длины |
| Model caveat #5104 | D | Exact failing class replay на фиксированном pin/patch либо честно согласованный scope; одинаковый size нового T оговорку не снимает |
| Comparator panic/unwind не проверены | К, U scope | Отдельное unwind theorem/accepted limitation; E normal-return loop не снимает эту строку |
| ZST/scratch geometry только выбранная | A1/E/C+U | Отдельная ZST branch/valid-pointer argument и actual backing/offset/frame map; одного u64 scratch proof недостаточно |

Proof receipts, mode/source/flags и именованные failures обязательны. Удаление Limitations — следствие свидетельства
и принятого scope, не самостоятельная редакторская стадия. До ruling по E2 в буквальном требовании остаются все четыре UB.

## 13. Бюджет первой итерации: CI dispatch, не число новых веток

Один «CI-прогон» ниже — один fork dispatch, который может содержать ограниченную matrix;
не считать 235 harnesses за235 dispatch. Верхняя граница включает одну адресную исправительную попытку,
не автоматические retries. Upstream PR-triggered CI и organizer run считаются отдельно от нашего fork envelope.

| Дорожка | Человеко-дни до первого решения | Fork dispatch | Что ограничено |
|---|---:|---:|---|
| U, публикационная подготовка | 1–2 + неизвестное ожидание | 0–1 | Reuse существующих exact-head gates; новый Quick лишь при changed parent/source |
| A1 + exact issue packet | 3–6 | 2–3 | 4 scratch landmarks/scale, небольшой named-control packet, не полный N sweep |
| E | 3–5 | 3–4 | Calibration, actual loops, ON/OFF/negative gates; STOP при named blocker |
| Профили | 2–4 | 2–3 | Targeted new signatures/controls, затем qualified matching consumers |
| B | 2–6 | 2–3 | Один235 census, targeted canaries/малый patch; без generic validity subsystem |
| C-сейчас | 2–3 | 1–2 | Borrow/frame map и ограниченные positive/negative tests; не alias implementation |
| D | 0–4 | 0–2 | Только нужный maintainer contribution после координации |
| **Вся ограниченная итерация** | **13–30 суммарных человеко-дней** | **10–18** | Не срок закрытия challenge; после STOP следующая работа требует решения |

Не добавлять автоматически «ещё столько же» на каждый найденный blocker. Предлагаемый потолок — **18 fork dispatch**
до общего review владельца, внутри — stage caps таблицы. Согласование этого budget ещё не является dispatch-разрешением.
Release requalification/organizer pin update после source changes — отдельная оценка, без обещания длительности upstream.

Профиль: первично Ubuntu/jobs1, exact tool/std/overlay binding, обычные checks, object-bits12 где уже принят,
600s/root. Для census — штатные bounded shards с полным235 manifest; job/aggregate time/output/RSS caps
координатор записывает до запуска по существующему workflow, не поднимает задним числом после OOM.
Записывать raw KiB/bytes и корректные MiB/GiB, driver/backend и concurrent aggregate; сохранять original exit/signal.
Неполный run — PARTIAL/UNKNOWN, не proof. Масштаб с organizer jobs2 проверять отдельно после per-root измерений.
Трёхплатформенный full Gate A уже есть для freeze; повтор — при новом release head, а не для каждой аннотации.

## 14. Очередь двух воркеров и связь с пунктом2

| Волна | Worker14 | Worker15 | Gate / исключение пересечений |
|---|---|---|---|
| 0 | U: готовый stack package/PR-01/02/design-note материалы владельцу | A1 landmarks и scale/issue packet | Source C2/SEL1 freeze не трогать. Публикует/dispatch координатор |
| 1 | Рефакторинг profiles, callers и их comparator controls | E: loop annotations и отдельный loop-control module | W14 владеет verify profiles/callers; W15 — core loop attrs/свой новый модуль. Общий mod-registration — один назначенный writer |
| 2 | B-census/малый compiler fix после U/WIP gate | C-сейчас: borrow/frame map и trait/helper controls | Один compiler writer; core frames после принятия E, не одновременно править тот же smallsort.rs |
| 3 | Review/integration U и нужный B/E blocker — только один | D contribution при запросе/GO либо помощь в CI evidence map | Не открывать FnPtr/trait-object/VeriFast проекты вместо STOP |
| 4 | Solution source/flag integration и coverage map | Organizer-CI package/negative acceptance/resource review | Отдельный принятый organizer gate; matched proof domains и exact combined pin |

На время ожидания U допускается независимая annotation/test-only работа, а не бесконечное разрастание compiler backlog.
G4/пункт2 сохраняется как отдельная functional задача: использовать те же static profiles, entry attrs и E infrastructure,
но sortedness/count composition не подменяет initializedness. После E safety feasibility можно отдельно усилить
invariants до sorted prefix/permutation; стоимость учитывать в плане пункта2, не дублировать здесь.
Если Replace нужен обеим дорожкам, один shared design/patch и общие soundness controls, не две реализации.

**Рекомендация:** принять U→scratch/scale→E и profiles как ближайший путь, B — через census/узкий доказанный gate,
C — через реально проверяемые frames и upstream cooperation. Подать PR-01/02 и design note сейчас после подготовки владельцем,
не ждать молчания на #5172. Снять собственные FnPtr/alias model/VeriFast разработки с критического пути.
При этом не обещать закрыть immutable/validity одной редакцией Limitations или считать существующий flag доказательством.
