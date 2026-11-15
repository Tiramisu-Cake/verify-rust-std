# Challenge 8, пункт 2 — v2: путь приёмки и отдельный путь качества

2026-11-16. Черновик после независимого аудита; решения R1–R9/A1–A9 ещё за владельцем.
Это верификация корректности, не security-работа. Без сборок, CI, публикаций и push; Cloud $0.
Связанные документы: [v1](PLAN-CH8-ITEM2-SORTING.md), [пункт1 v2](PLAN-CH8-ITEM1-REMAINING-v2.md),
[общая карта четырёх воркеров](ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md).

## 1. Что меняю по существу

Согласен с основной поправкой аудита: в v1 я сделал generic theorem и функциональную индукцию по
неограниченной длине препятствиями для ближайшей приёмки, а пункт2 излишне привязал к C2/SEL1.
Теперь основной путь: **документированный threshold-domain, primitive/default order, реальные ensures/PFC,
symbolic N, чистый upstream Kani, measured CI cost**. Это самостоятельная работа без ожидания слияния C2.
Safety-only arbitrary-length insertion остаётся дорожкой E пункта1.

Опубликованная опора:
[ответ автора #56 о primitive/default ordering](https://github.com/model-checking/verify-rust-std/issues/56#issuecomment-2611410906),
[текст challenge](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/challenges/0008-smallsort.md),
[архив обсуждений требований/ревью](https://github.com/Tiramisu-Cake/verify-rust-std/blob/d70d85eb021bd7e264f22acab0c371502c2420a0/research/challenge-8/requirements-evidence-2026-10-24/cross_challenge_precedents.md).
Мейнтейнеры требовали sortedness **и** multiset, реальные проверяемые contracts и покрытие до16/32.
Это сильная основа выбранного пути, но не предварительное принятие нашего будущего PR или исключений по UB.
История допускает также boundary-oriented proofs: symbolic N выбираем как ясное полное покрытие, а не утверждаем,
что ровно11 roots или шесть отдельных PFC roots дословно предписаны организаторами.

### R1–R9

| Рекомендация | Моя позиция |
|---|---|
| R1 threshold requires | Согласен: `len≤threshold(T)` плюс реальные scratch/geometry условия. В Rust лучше полностью квалифицировать trait, чтобы не получить неоднозначный Self::small_sort_threshold |
| R2 insertion отдельно | Согласен: arbitrary-length functional insertion не gate пункта2. Для safety E одной геометрии может не хватить: initialized prefix/hole/repair не следуют из того, что u8/u64 допускают любые **инициализированные** биты |
| R3 KeyLess по типу | Согласен с направлением, но прототип rustc вне core/Kani не qualification. `OrdModel: Copy` исключает Cell/non-Copy; Copy нужен Key/snapshot, не обязательно T |
| R4 clean upstream | Согласен. Предлагаю exact upstream `0aac16ef62`, содержащий fix `063204a1`; без C2/SEL1 и extra-UB. Обновление organizer pin — отдельный gate |
| R5 нет ∀T в Kani | Согласен: Kani проверяет instances. Rank-модель и source-parametricity не превращаются в механизированный ∀T. «Только VeriFast» слишком категорично; этот трек у нас закрыт, не возобновляем его |
| R6 три больших замера | Согласен. Consumer с ещё недоказанными semantic summaries — только диагностический cost experiment, не доказательство композиции |
| R7 merge loop contracts | Согласен как ранний эксперимент приоритетного bottleneck. Инвариант требует proof base/step/exit и odd leftover; один offset-parametric шаг не отменяет caller geometry |
| R8 CI ворота | Согласен с численными предлагаемыми gates и заменой только покрытых roots. Это наши проектные ограничения, не опубликованные лимиты комитета |
| R9 S1–S5 | Согласен; владельцев/файлы перераспределить на четыре слота. Короткий N0..3 smoke остаётся частью S1, а не основной целью вместо полноразмерной композиции |

### A1–A9

| Дополнение | Моя позиция |
|---|---|
| A1 u8 первым | Согласен; выигрыш над u64 измерить. u8 не доказывает u64/другие layout автоматически |
| A2 шесть тел | Согласен как наша карта полноты: шесть actual implementations, не только три именных API. Не выдавать это за отдельный дословный ruling о количестве harness'ов |
| A3 11 классов N | Согласен для general+network: 4+7. Fallback отдельно; это не11 roots для любого T и не полное число entry/leaf proofs |
| A4 tail16 | Согласен: network N17 доходит до relative tail16. Отличать relative position от абсолютного offset в backing |
| A5 без panic stub | Согласен для lawful sorting leaves/consumers: доказать недостижимость ord-violation panic. Существующие arbitrary-bool safety proofs имеют другой scope |
| A6 loop/quantifier limits | Важное дополнение, но blanket-формулировки слишком сильны. Проверить exact expression/flags; см. §6. Termination можно оставить отдельным claim |
| A7 сообщение | Объединить с U: подтвердить выбранное прочтение, insertion, типы, CI budget/flags и pin bump. Не повторять как неизвестный уже опубликованный ответ про primitives |
| A8 full leaf domain | Полностью согласен с проверкой domains; PFC сам не доказывает полноту своего harness. Fixed48 не автоматически все allocations/offsets/длины scratch |
| A9 rank,id | Полезно для качества. Нужны IDs range/uniqueness и сохранение rank_by_id; сортировать comparator'ом **только rank**, иначе это просто иной порядок. Нативный перебор не proof |

## 2. Нормативный domain и что именно доказывается

Для каждого actual trait impl: requires `v.len() <= <T as ThisTrait>::small_sort_threshold()`;
для Stable+Freeze дополнительно достаточный, valid/disjoint scratch (N<2 не должен требовать/read лишний scratch).
Сохранять runtime std без изменений: это обоснованная документами verification precondition, не новый runtime abort.
Stable/unstable quicksort callers проверяют этот threshold перед вызовом; их implication включить в coverage map.
Fallback threshold16, general/network32. Helper insertion может иметь более широкий собственный API — это не
расширяет функциональный domain small_sort и не отменяет safety-вопрос пункта1.

Контракт: чистый model order + равенство кратностей полных model-values + frame/длина.
Не вызывать FnMut из ensures и не считать old(&slice) value snapshot. Снимок хранит значения/keys по active N,
не читает unused scratch. У модельных Cell/transparent wrapper key должен представлять весь заявленный logical value.
Позже rank,id использует отдельные key и identity; не подменять full value count одним count ключей при payload.

По T/F ближайший claim — именованные проверенные instances primitive/default order и необходимые route representatives.
Conditional `!modeled || post` допускается только с явной scope-таблицей и proof-root assertion, что modeled=true.
Default modeled=false не является generic theorem. Старый fn-pointer profile address guard не наследуется KeyLess.

## 3. Пины и независимые профили

| Назначение | Source/tool | Flags и смысл |
|---|---|---|
| Исходный #752 | std `872d5a43380752786415bc00d2a12ce0e930cb37`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607` | Baseline опубликованного bounded результата, не новый trait-contract proof |
| Organizer main при проверке | std `25b2b24c82…`; Kani `c5e65fdfc3e15ec32293f2a4c07509aebec033c9` | Тоже без нужного specialization fix |
| **S — пункт2** | std verification branch от#752; **чистый upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`** | Organizer flags, `--no-assert-contracts`, object-bits12; uninit/valid-value OFF. PFC/Replace selected явно |
| **A — пункт1/A1** | Kani SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`, принятый std70ba+test overlay | Uninit ON; actual bodies, прежний W0-A1 scope; не proof S |
| Качество combined-ON | Будущий точный совместимый pin/source | Нужна отдельная квалификация; нельзя сложить по именам roots результаты двух строк выше |

Fix `063204a177272585352b6942ae2b04709fe58b48` входит в выбранный clean upstream и снимает default-fn препятствие
из [#5116](https://github.com/model-checking/kani/issues/5116); generic-method fix
[#4908](https://github.com/model-checking/kani/issues/4908) тоже уже входит.
Пин не выбирать как «любой более новый по дате»: фиксировать exact SHA/ancestry, toolchain/backend и workflow binding.
Отправка bump request не означает adoption. C2 серия U продолжается ради пункта1, но не блокирует S1–S5.

## 4. S1 — механизм на actual impls и статический comparator

Первичный тип u8, `KeyLess` — named ZST FnOnce/FnMut, сравнивающий чистый `key(&self)`.
Model trait должен требовать `Key: Copy + Ord`, а не `T: Copy + Ord`: иначе не покрыты Cell и Freeze non-Copy wrapper.
Начальные projections: u8, Cell<u8>, transparent non-Copy byte-wrapper. Для последних двух не заявлять primitive theorem.
Проверить manual `extern "rust-call"`, core feature gates и Kani tuple/call lowering в одном точном smoke.
Нативный прототип аудитора на другом rustc не подтверждает это. При blocker — минимальный repro и решение P1,
не общий FnPtr compiler project. Проверенный static Profile::cmp остаётся возможным узким fallback-дизайном,
если модель однозначно связывает comparator instance; это отдельное решение, не незаметная подмена F.

Шесть implementation bodies:

| Тело | Начальный instance / маршрут |
|---|---|
| Stable default | Cell<u8>, fallback16 |
| Stable Freeze override | u8, general32 |
| Unstable default | Cell<u8>, fallback16 |
| Unstable Freeze forwarding | u8, forwarding в T3 |
| UnstableFreeze default | non-Copy byte-wrapper, general32; большая default fallback-ветвь отдельно в type coverage |
| UnstableFreeze Copy override | u8, network32 |

На каждом claimed impl actual ensures и проверяющий PFC; не только contract на declaration/wrapper.
S1 smoke N0/1/2/3 доказывает activation/early return/содержательное postcondition, но не full length matrix.
Перенести negatives G3: порча порядка, кратностей, wrong comparator/model guard; immutable snapshot и useful return.
Не добавлять новые runtime trait bounds, исключающие исходные T/F без раскрытия scope.

## 5. S2 — три cost probes и ранний merge pilot

В одном bounded batch на u8/default order, без ord-panic stub:

1. Actual `bidirectional_merge`, len32, отсортированные halves, sorted+full count.
2. Actual sort13 consumer через semantic verified swap summaries, sorted+count.
3. General N32 consumer с semantic summaries всех используемых helpers.

Если для 2/3 leaf ещё не доказан, допустим **отдельный opt-in diagnostic** с явно помеченными assumed summaries.
Такой PASS — только измерение данной формулы, **не formal proof credit** и не строка future accepted inventory.
Нужны satisfiable/nonvacuous controls; inconsistent summary может сделать и время бессодержательным.
Все формальные consumers в S3/S4 позже перепроверяются после qualified leaves на тех же domains.
Safety/frame-only summary не содержит sortedness/permutation и не может заменить semantic leaf.

Замерять real body, model/checker, havoc/summary, driver/backend/aggregate RSS и wall separately по доступным phases.
Сравнение u8/u64 — один адресный paired probe, если нужен для решения; не серия solver sweeps.
N4/G3 — smoke/reference, а не главный deliverable. Исторические 68s/600s и driver OOM
из [#5117](https://github.com/model-checking/kani/issues/5117) — ориентиры разных pins, не прогноз нового head.

Параллельно готовить merge invariant для CAP32. Если монолитный merge32 проходит R8, invariant может стать
оптимизацией; если не проходит — это primary decompose option, не увеличение timeout.

## 6. Merge invariant: что нужно проверить в приложении C аудита

Сохранить геометрию четырёх фронтов, consumed counters, disjoint source/dst, prefix/suffix order,
counts и связи с remaining input. Все indexed comparisons short-circuit-guarded, включая k=0/empty fronts.
Исчерпанный reverse front в actual code использует wrapping_sub и может быть sentinel перед началом;
не кодировать его формулу как безусловный in-bounds add/usize subtraction с underflow.
После paired writes доказать preservation, затем odd leftover и целый output count. Ord-panic должен быть unreachable
из lawful input order/halves, а не отсечён stub. Function frame и callback effects доказываются отдельно.

**Важная тонкость одной query-count реализации:** в C5 endpoint alternatives нужно охранять ненулевым
числом взятых из соответствующей половины элементов. Иначе C1–C5+C6 только для одного probe допускают
нежелательные abstract states. Пример по формулам: len4,h2,k1; i1,j0,i′0,j′1; src=[1,9,2,10];
dst[0]=9, dst[3]=2; probe0. Граничные C3/C4 истинны, оба output bands из одного элемента sorted,
counts для0 равны нулю, а unguarded C5 выбирает src[h+j−1] и src[h−i′] из ещё не взятых частей.
Это **не контрпример идеальному C6 с ∀probe**, а предупреждение о его замене одним fixed probe в Kani.

Два пути: универсальный/полный multiset invariant либо guarded endpoints и самостоятельный order argument,
с query-count лишь для query-count theorem. Для произвольного probe runtime независим от probe;
при композиции один и тот же ghost probe и корректный implication для каждого actual callee, без скрытой смены F.
Оба пути требуют induction/negative controls; нативный перебор аудитора не доказывает invariant на всех abstract states.

Offset-parametric proof снижает число похожих листов, но callers по-прежнему доказывают validity/init/alias/frame.
Sort8 даёт34 same-allocation offset pairs для N16..32; кроме них есть scratch→v и v→stack-scratch.
Один leaf на separate arrays не квалифицирует все эти stubs.

Ограничения:

- [#4585](https://github.com/model-checking/kani/issues/4585): сложные decreases expressions могут вычисляться
  не в нужной точке MIR. Начинать с проверенной простой переменной и false-decrease control.
  [#3168](https://github.com/model-checking/kani/issues/3168) — исторический API контекст, не отдельное доказательство этой ошибки.
- Для пути приёмки достаточно clearly stated partial correctness нормального возврата; termination claim отдельно.
  При конечном CAP сами actual loops bounded; не выдавать invariant без variant за доказательство termination.
- [#5148](https://github.com/model-checking/kani/issues/5148) — symbolic quantifier bound; CAP32 позволяет
  constant-bound/guarded или развёрнутые predicates. Это всё равно требует sound extraction controls.
- Под extra-UB pointer-dereference predicates с safety checks могут отвергаться; это не запрет любого упоминания ptr.
  [#5141](https://github.com/model-checking/kani/issues/5141) напоминает о потере default checks и без extra flags.
  Pure bounded predicates/definedness проверять отдельно. Combined-ON — не этот campaign.
- Loop/contract havoc и shadow-summary совместимость C2 не предполагается автоматически; safety E остаётся отдельным gate.

## 7. S3 — qualified semantic leaves и их полный используемый domain

Порядок: swap→sort9/sort13; insert_tail до **relative16**; sort4→sort8; merge2..32.
Параллелить можно разные модули/доказательства, core annotations интегрирует один владелец.
Вставке внутри finite route достаточно finite proof/summary; functional unbounded induction не required gate.

Для каждого summary: exact T/F, length/offset class, allocation topology, initialized ranges, writable region,
order law, snapshot/probe model. Harness генерирует все claimed inputs под requires; Kani сам это не подтверждает.
У большого requires при маленьком harness либо сужаем **названный qualified domain**/stub guard,
либо расширяем harness/доказываем общий invariant. Не называть универсальным leaf, измеренный лишь в0-offset arrays.
Для Stable arbitrary scratch length отдельно обосновать prefix locality: actual code использует нужный prefix,
но фиксированный backing48 не автоматически доказывает все legal большие allocations/offsets.

Mandatory controls: wrong-precondition, frame violation, input corruption, lost/duplicated full value,
bad/disabled model, misleading weak-summary consumer. Ord-panic без stub и полезный return должны быть проверены.
Не читать uninitialized destination/tail в requires/old snapshot; output typed views только после actual writes.
Contract inventory связывает каждый публикуемый contract/qualified domain с обычным CI root.

## 8. S4 — symbolic N до thresholds и actual entries

| Маршрут | Структурные классы N |
|---|---|
| General | 0..1;2..7;8..15;16..32 |
| Network | 0..1;2..8;9..12;13..17;18..24;25;26..32 |
| Fallback | 0..16 целиком либо0..1 и2..16 |

Один root с arbitrary N под диапазоном проверяет все N этого класса; символические input values независимы.
Показать reachable branch/return и meaningful N edges, не лишь assume, отсекающее дорогие случаи.
11 — general+network classes, не число всех proofs. Шесть impls используют разные маршруты;
при отдельном proof каждого тела получится иной inventory, например около18–20 entry roots при полном разбиении.
Forwarding T2→T3 можно доказать через qualified T3 summary с проверкой caller preconditions, не перепроверять весь алгоритм.

Primary ordinary scope: u8 full threshold-domain; Cell/non-Copy дают default-body coverage в своём domain.
u128, большие/малые Copy/!Copy, oversized fallback, ZST — отдельные boundary/type coverage rows;
объём их включения в ordinary CI решается после P2/R8, не объявляется доказанным от u8.
Snapshots и frames охватывают active sub-slice с symbolic offset там, где это требуется consumer geometry;
оставшийся backing не смешивать с active length. Никаких ord-panic stubs на sorting path.

## 9. S5/R8 — gate стоимости и обновление #752

Предлагаемые owner gates, не выдуманные правила организаторов:

- 600s/root; первая цель — устойчивый запас, а не599s в одной Linux попытке.
- Single-root aggregate driver+backend RSS **≤6GiB**; затем реальный KANI_JOBS=2 на16GiB runner
  с запасом системе, без суммирования несинхронных peaks вместо measured aggregate.
- Суммарный SmallSort VT после замены не выше matched baseline на **том же новом pin**;
  дополнительная абсолютная цель — не превысить опубликованные7802s Ubuntu/10534s macOS без согласования.
  Исторические65.9/70.3% и longest246/340s — контекст, не замер нового suite.
- Обязательно измерить critical shard, полный elapsed и ordinary inventory. Шардирование по количеству
  может сконцентрировать новый набор в одной части; lower total VT не гарантирует fit самого медленного shard.

Таблица замены old root→new theorem должна сохранять type/F/domain/properties/geometry.
U8 proof не поглощает автоматически u64/array-valued proof. Непоглощённую quality-проверку можно перенести opt-in
только явным решением со scope change; обязательные safety/negative controls не удалять ради бюджета.
Каждый claimed multiset/order property остаётся проверен; diagnostic assumed-summary roots не входят в accepted count.

Пара CI arms baseline/new на выбранном upstream pin, Linux/macOS, organizer flags и actual parallelism;
без повторов до удачного результата. UNKNOWN/timeout/ordinary skip — не gate PASS.
Результат S5: direct contracts+PFC, scope/coverage table на страницу, matched cost report, честные Limitations и proposal update#752.
Фактическая приёмка — human review/organizer CI, а не наш P4 receipt.

## 10. Путь качества — отдельно от S1–S5

Не требуется сначала решить ∀T, все comparator effects, stability и extra-UB, чтобы подготовить содержательный пункт2.
Но пункт1 остаётся обязательной отдельной частью overall solution; этот раздел не объявляет его улучшения ненужными.

- **Rank/id:** comparator читает только rank; id — исходный индекс. Нужны N outputs, IDs∈0..N−1,
  сохранение immutable rank_by_id и строгая лексикографическая упорядоченность output по(rank,id).
  Эти условия могут вывести уникальность/перестановку по мощности; одних adjacent comparisons без range/mapping мало.
  Если comparator сам сравнивает(rank,id), это не proof стабильности rank-only алгоритма.
- Stable claim — для соответствующих Stable маршрутов/реальных stable helpers. Unstable fallback insertion
  тоже может быть stable как конкретное тело; название trait не доказательство ни стабильности, ни её отсутствия.
- Нативные5.9млн cases аудитора — полезные tests, не theorem и не оценка SAT стоимости дополнительного id.
- ВсеT: в Kani остаётся finite instance matrix и названный source/parametricity argument, не Kani-checked ∀T.
  Не открываем закрытый VeriFast-трек. Другой универсальный proof — новое отдельное решение владельца.
- Combined-ON: прямые callbacks, unsupported shadow Replace, quantified checks, validity/permissions и model trust
  из пункта1 должны быть квалифицированы на actual combined source/pin; перенос verdict по имени root запрещён.

## 11. P0–P4 и fork-dispatch budget

| Gate | Что должно быть решено/проверено | STOP |
|---|---|---|
| **P0** | Владелец выбирает threshold-domain, KeyLess/projections, чистый exact upstream pin, budgets и одно объединённое organizer message | Не имитировать уже полученное одобрение этой v2; ни source work, ни новые CI из одного этого файла |
| **P1** | Core/Kani smoke: attrs шести bodies, modeled=true на claimed instances, N0..3 и meaningful negatives | Fn ABI/specialization/model activation blocker → repro, без нового общего compiler проекта |
| **P2** | Три больших cost probes + первый merge-invariant результат; выбрать monolithic/invariant и actual summary domain | Budget cap/weak summary/vacuity → one review, не brute-force33N или увеличение timeout |
| **P3** | Qualified leaves, все symbolic classes до thresholds, source/frame/precondition closure, multiset+order, no panic-stub | Любой uncovered length/body/domain, unproved leaf или relevant negative failure |
| **P4** | Cost/shards и replacement map, новая proposal#752/организаторский compatible CI; quality claims отдельно | Нельзя назвать решение принятым до review; no extra-UB не скрывать в общей формулировке |

| Этап | Предлагаемый fork dispatch cap | Ограничение |
|---|---:|---|
| S1 | 1–2 | Один smoke/core build, одна адресная поправка |
| S2 | 1–2 | Три probes одним batch; invariant/paired diagnostic при необходимости |
| S3 | 3–5 | Semantic leaf batches с negatives; не per-N сотни запусков |
| S4 | 1–2 | Symbolic entry/consumer matrix; исправление только по named finding |
| S5 | 2–3 | Matched baseline/new +platforms/shards, reserve только после review |
| **Путь S** | **8–14** | Новый budget proposal владельцу, **не добавлен автоматически к принятому18 пункта1** |

Один dispatch может содержать bounded jobs/matrix; заранее фиксируются root manifest, native exits,
RSS/time/output caps, exact input hashes/selected PFC bodies. Infra-failure расходует попытку; auto-rerun отсутствует.
Локальные Rust/Kani/CBMC builds и native experiments не разрешены; подготовка Git/чтение/Python synthetic tests.
Распределение четырёх работников и сумма budget — в общей карте. Решения и отправка внешнего сообщения — за владельцем.
