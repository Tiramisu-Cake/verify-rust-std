# Challenge 8, пункт 2: контракты сортировки и общая дорожная карта

2026-11-15. План для владельца; не выдача стадий и не разрешение новых запусков.
Это верификация корректности, не security-работа. Только fork CI, **Cloud $0**.
Локальные compilers/verifiers/builds не запускались; CI, push и публикаций нет.
Оценки — человеко-дни разработки/проверки без времени upstream-review; сначала нужны ограниченные pilots.

## 1. Требование и содержательная спецификация

[Challenge 8](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/0008-smallsort.md)
требует контрактов непосредственно для трёх entry points:
`StableSmallSortTypeImpl::small_sort`, `UnstableSmallSortTypeImpl::small_sort`,
`UnstableSmallSortFreezeTypeImpl::small_sort`, показывающих сортировку всех допустимых slices/lengths.
Контракты loop/callee названы возможным способом доказательства. Один N2 wrapper, обычный harness assertion
или набор примеров без привязки к контракту entry point не выполняет всю эту формулировку.

Предлагаемая нормальная-return спецификация:

1. Длина и допустимая внешняя память сохранены.
2. Выход упорядочен по **фиксированному чистому отношению R** на логических значениях.
3. Выход — перестановка полных входных значений с сохранением кратностей.
   Один sortedness допускает замену всех элементов нулями; set equality пропускает потерю дубликатов.
4. Для stable entry отдельно определить сохранение исходного порядка равных по R элементов.
   В тексте challenge stability не выделена отдельной формулой; её нельзя приписывать нынешним результатам.

Для sortedness нужны условия на comparator: как минимум согласованность ответов со strict weak order,
включая транзитивность эквивалентности несравнимых значений. При этих законах отсутствие соседней инверсии
даёт глобальную упорядоченность; для произвольного нетранзитивного отношения это неверно.
Независимый nondet bool на каждом вызове полезен для safety/permutation, но не заменяет lawful comparator.
Проверку actual comparator относительно R нужно связать с precondition/профилем, не просто assume в harness.

Не вызывать effectful `FnMut` снова из ensures: он может изменить captured state/Cell, вернуть другой ответ,
паниковать или изменить наблюдаемый ключ. Спецификация читает чистую модель/snapshot;
разрешённые side effects callback учитываются отдельно. Нынешний «не пишет вне element/dst frame» — ограниченный домен,
а не описание всех допустимых FnMut. Условие неизменности R/модели надо сформулировать явно.

`old(&slice)` не обязательно снимок элементов: скопированная ссылка продолжает смотреть в ту же память.
Нужен проверенный immutable value snapshot либо ghost sequence/count перед вызовом.
Snapshot читает только initialized input, никогда uninitialized scratch или tail.
Полный результат challenge также требует [пункт 1](PLAN-CH8-ITEM1-REMAINING.md): функциональная формула
на модели с исключёнными UB не превращается в полное корректное Rust-доказательство.

## 2. Что сейчас действительно есть

Официальный [PR #752](https://github.com/model-checking/verify-rust-std/pull/752) OPEN, ready-for-review;
head **`872d5a43380752786415bc00d2a12ce0e930cb37`**, current base `25b2b24c82a960734a2bab082784747b9b785177`.
Его SmallSort файлы совпадают с исследованными здесь g0 файлами; остальные library файлы и Kani pin могут отличаться.
235 SUCCESSFUL/OS и времена ниже — опубликованная сводка PR/его fork CI, не новый прогон этого плана.

| Нынешний результат #752 | Точный предел и чего он не даёт |
|---|---|
| General/stable, u8/u64 N0..9 | Ordinary oracles: порядок и full-value probe count. Это не general trait contract для всех T/N |
| Fallback, u8/u64 N0..6 | То же для конечного набора длин; insertion для произвольного len не доказана |
| Networks: u8 N0..7, N9..13; u64 N0..7, N9 | Sortedness на перечисленных длинах; count только N<9. **Это не непрерывная полная permutation-матрица 0..13** |
| Tag-перестановка N9/N13 с arbitrary answers | Фиксированные distinct tags; перенос на payload — source-level аргумент, не generic refinement theorem |
| Три N2 forwarding contracts | Реальные trait calls: Stable<Cell<u8>>, Unstable<u8>, Freeze<NonCopyU8>; closed comparators, key order и full-byte count |
| Реальные helper safety contracts | requires/modifies и matching bounded consumers; сами по себе не дают semantic sortedness/permutation summary для произвольного caller |
| Profile helper ensures | Закрытые T/F, regions/offsets/backings; не контракт на произвольный FnMut/весь модуль |

Исходники на exact PR head:
[forwarding_contracts.rs](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs),
[profiles](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs),
[module map/limitations](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify.rs).
Замечание Copilot о N2/N9/N6/N13 по существу верно; максимальная длина ещё скрывает разницу свойств и дырки матрицы.
Tie stability отдельно не доказана. Снятие ограничений Kani не расширяет эти domains задним числом.

### Research G3 уже сильнее опубликованного PR, но тоже bounded

[RESULT-TRAITPFC-G3](https://github.com/Tiramisu-Cake/verify-rust-std/blob/70ba5befc617627073738e26cb1466bd4fb76e41/research/challenge-8/kani-k1/RESULT-TRAITPFC-G3.md)
сообщает bounded PASS на Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, repaired std head `2f1c45e519…`:
прямые контракты выбранных **не-default** реализаций трёх traits, u64/U64Cmp, N2/N3;
matching leaf/consumer и negatives. Семь новых ordinary roots имеют ΣVT **596.71 s**.
Первый build был COMPILE_ERROR и не является proof evidence. Новый fork replay этого результата ещё нужен.

В G3 `SortModel<T,F>` имеет default `enabled=false`, а u64/U64Cmp instance включает лишь N2/N3.
Ensure имеет форму **`!old(enabled(...)) || postcondition(...)`**, snapshot — `[u64;3]`.
Это честный conditional contract, но вне enabled домена он ничего не утверждает о сортировке.
Нельзя назвать его generic-контрактом из-за generic Rust-сигнатуры.
При расширении нужны одновременно activation, корректный snapshot/checker и substantive checks;
root PASS при выключенном guard — не достижение. Fn-item/closure — другая F-мономорфизация, не U64Cmp.

## 3. Прямые trait-контракты: фиксы уже merged, adoption пина отдельно

| Где используется Kani | Exact pin | #5135 / #5153 |
|---|---|---|
| Опубликованный #752 | `cd355b0bccd32300713bc2ce4f765dafa1510607` | Оба отсутствуют |
| verify-rust-std main `25b2b24c82…` на момент проверки | `c5e65fdfc3e15ec32293f2a4c07509aebec033c9` | Оба отсутствуют |
| Локальная research/G3 линия | `f046b70644e113be0df9c22c2e6ea44a65a57566` | #5135 есть, #5153 нет |
| C2 `8e299aa624…`, SEL1 `14bc57fdb9…` | Точные fork heads из плана пункта 1 | Оба fix-коммита входят в ancestry |

- [#4908](https://github.com/model-checking/kani/issues/4908) CLOSED;
  [#5135](https://github.com/model-checking/kani/pull/5135) merged **2026-11-09**,
  merge `f046b70644e113be0df9c22c2e6ea44a65a57566`: разрешение method-level generic arguments,
  lifetime/type/const arguments для contract target, proof_for_contract/stub_verified на trait methods.
  Ограничение trait-level const generics этим не снимается; у наших трёх traits таких параметров нет.
- [#5116](https://github.com/model-checking/kani/issues/5116) CLOSED;
  [#5153](https://github.com/model-checking/kani/pull/5153) merged **2026-11-13**,
  merge `063204a177272585352b6942ae2b04709fe58b48`: сохраняет specialization `default fn`
  при обработке contract attributes, в том числе нескольких stacked attributes.

Следовательно, ждать ещё одного синтаксического фикса для этих двух препятствий не требуется.
В C2/SEL1 можно готовить pilots прямых контрактов, включая default implementations.
Проверить все actual selected implementations: default и override имеют свои тела;
контракт на одном из них не автоматически проверяет все три entry names и все специализации.

**Когда попадут в organizer pin:** подтверждённого срока нет. Merged Kani PR не обновляет
`verify-rust-std/tool_config/kani-version.toml` автоматически в нашей solution голове.
Нужны согласованный upstream pin-update либо принятый организаторами точный fork pin, std/tool compatibility
и повтор соответствующего CI. Для research это уже можно сделать на C2/SEL1, не изменяя поданный #752 молча.
Цена pin/trait fixture bridge — **1–3 дня**, при новом codegen/layout blocker STOP с отдельным reproducer.
Синтаксис становится возможен; lawful-order model, frames, lengths и proof resources эти фиксы не доказывают.

## 4. Ось длины: два разных способа завершения

### 4.1. Конечные general/network маршруты

Для фиксированного T/F и **доказанного** N≤threshold можно закрыть каждое N∈0..=threshold,
либо один symbolic-N harness с backing capacity threshold и bounds/unwinding assertions.
Это полноценное покрытие длины **внутри этого домена**, не лишь sampling значений элементов.
Отдельные N легче сопоставлять и ограничивать по ресурсам; один symbolic N может дешевле/дороже — измерить один вариант.
Нужен CI manifest всех длин, selected trait implementation, backings и проверяемых свойств без пропусков.

Но ограниченность надо доказать, а не взять из комментария:

- Реальные stable/unstable quicksort callers проверяют `len <= T::small_sort_threshold()` перед вызовом.
  Проверить этот implication и выбранную специализацию для того же T/F.
- Network body сам aborts при len>32; это не доказательство, что он сортирует произвольную большую длину.
- General body с caller-provided достаточным scratch не обязан ограничиваться 32 самим условием capacity.
  G3/T1 `requires` допускает N>32 при scratch≥N+16. Поэтому theorem 0..32 не покрывает весь записанный contract domain.
- Нужно либо явно контрактовать штатный threshold-domain и доказать callers, согласовав это с «arbitrary valid length»,
  либо доказать более широкий callee domain. Не сужать старый requires только ради зелёного proof без раскрытия scope.
- Generic fallback и `insertion_sort_shift_left` не становятся bounded только потому, что один caller обычно даёт N≤16.
  Для их произвольной допустимой длины нужен следующий раздел.

Если действительный admissible domain trait entry — именно `len≤threshold(T)`, то полная конечная проверка
закрывает его length-ось для данного профиля, при автоматическом доказательстве caller bound.
Если требуется весь более широкий domain записанного callee contract, этого мало; трактовку надо явно
сопоставить с challenge до заявления о полноте. Для одного пункта2 необязательно доказывать helper вне всех
достижимых caller domains. Но пункт1 **прямо называет** insertion_sort_shift_left с произвольной допустимой длиной:
совместный план всё равно требует unbounded safety proof; разумно переиспользовать его induction и для sorting.

Точки смены маршрута: general при N8/N16 вводит sort4/sort8; network N9/N13 — сети,
N18 — merge двух частей; N25/N26 меняют использование sort13 в половинах.
Проверять также длины с непустой вставкой **после** presorted prefix, чётные/нечётные halves и реальные scratch offsets.
Representative boundaries — хороший этап диагностики, но не замена полной конечной матрицы.

### 4.2. Fallback/insertion: индукция по длине и по позиции вставки

Нужны contracts на insert_tail и insertion_sort_shift_left, а затем forwarding contracts defaults:

- На входе внешней вставки prefix `[0..offset]` упорядочен; active slice valid, значения и модель сохранены.
- Внешний invariant: prefix до текущего tail отсортирован, вся active region — перестановка исходной,
  untouched suffix/frame сохранён, pointer/index внутри allocation. Progress: оставшееся число элементов.
- Внутренняя вставка: временно вынесенный элемент + hole + сдвинутый сегмент составляют исходную последовательность,
  обе нужные части упорядочены и связаны с inserted key; после repair hole закрыт.
  Progress — убывающее логическое расстояние sift→begin. Не трактовать hole как живой T в invariant.
- Helper postcondition расширяет sorted prefix на один, сохраняет полные кратности/frame;
  внешний шаг использует этот доказанный summary, а не unwind всей вложенной вставки.
- Для ZST pointer distance/advance не работает как мера позиции: отдельный случай и инвариант логических индексов.

Loop contract уменьшает число исполняемых итераций, но не обобщает backing allocation или Rust monomorphization.
Harness с `[T;32]` остаётся таким даже при loop invariant. Нужна модель произвольной допустимой длины/region
либо автоматически проверяемый параметрический theorem и перенос на реальные callers.
Инвариант без корректной decreases-меры даёт partial correctness, не доказательство завершения.

Оценка: feasibility **3–5 дней** на одном actual loop и простом профиле;
обе вставки с полным functional invariant и composition — **10–20+ дней**, если хватает quantifiers/frames.
При невозможности expressible/sound dynamic-length invariant переходить к альтернативному proof,
а не называть увеличение unwind с20 до32 решением arbitrary-length.

## 5. Kani loop contracts и quantifiers: возможности и риски на pin

Флаги `-Z loop-contracts`/`-Z quantifiers` уже есть; наличие флага не значит, что наш invariant проверен.
Pinned [loop docs](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/docs/src/reference/experimental/loop-contracts.md)
описывают `loop_invariant`, optional `loop_modifies`, `loop_decreases`:
base/step, включение writes во frame, использование invariant после выхода и termination measure.
В actual insertion while/insert_tail loop есть annotation sites; сейчас функциональных loop annotations там нет.

[Quantifier docs](https://github.com/Tiramisu-Cake/kani/blob/14bc57fdb99960240c4944845a3d985c8af4dcf7/docs/src/reference/experimental/quantifiers.md):
variables usize, SAT backend требует constant bounds; глубокие expression/call trees и indexing дороги.
Bounds `(0, i)`/`(0, len)` в inductive state символические. Unsupported/dropped quantifier должен быть FAILED,
а не принятым theorem. Упоминание Z3 в docs не заменяет проверку, что exact driver/backend поддерживает нужный путь.

| Дополнительный issue / текущий статус | Влияние на план |
|---|---|
| [#5148](https://github.com/model-checking/kani/issues/5148) OPEN | SAT отклоняет symbolic-bound forall; рекомендованный Z3 отсутствовал в PATH. Это отдельная packaging/preflight проблема, не доказательство невозможности SMT-проверки |
| [#5141](https://github.com/model-checking/kani/issues/5141) OPEN | Quantifier extraction может терять default checks; нужны отдельные invalid-index/unsafe-read controls в quantified predicate, не только assertion результата |
| [#5147](https://github.com/model-checking/kani/issues/5147) OPEN | Captured-variable writes могут отсутствовать в inferred loop-modifies; frame проверять различающим control, не доверять inference автоматически |
| [#5053](https://github.com/model-checking/kani/issues/5053) OPEN | Missing explicit loop-modifies write может приниматься при MIR opt2; сопоставить реальную optimization setting и write-outside-frame negative |
| [#4893](https://github.com/model-checking/kani/issues/4893), [#4907](https://github.com/model-checking/kani/issues/4907) OPEN | Attach-site/iterator loop ограничения; не объявлять блокером explicit while, но general for-loop путь проверять отдельно |
| [#4908/#5135](https://github.com/model-checking/kani/issues/4908), [#5116/#5153](https://github.com/model-checking/kani/issues/5116) CLOSED/merged | Снимают указанные trait/method syntax-resolution blockers, не доказывают generic comparator или loop invariant |
| [#5117](https://github.com/model-checking/kani/issues/5117) OPEN | Driver memory на composition; отдельный предел от SAT/CBMC сложности |

Первый loop pilot должен иметь legal base/step/exit и **различающие** отрицательные варианты:
сломанный invariant, запись вне frame, ложный forall, сбой нужного bounds/UB check, неубывающая measure.
Если негатив неожиданно SUCCESS — feature нельзя использовать как trusted proof foundation в этом construct.
Для fixed-N этапа разумнее простые bounded checkers/unrolling, чем преждевременно зависеть от symbolic quantifiers.
Переход на SMT/новую модель — отдельный калибровочный шаг с сохранением обязательных checks.
Для fixed CAP можно попробовать `forall j∈[0,CAP): j<i ⇒ property(j)` вместо symbolic upper bound;
это остаётся bounded theorem и тоже требует soundness controls extraction.
Отдельный дешёвый fork pilot с зафиксированным Z3 и preflight должен отделить packaging #5148 от настоящих
ограничений encoding/SMT. Успех простого copy-prefix не означает успех raw-pointer insertion с permutation.

## 6. Обобщение по T и компаратору

### 6.1. Закрытый comparator/model domain — достижимый первый результат

Сохранять один именованный профиль T/F, чистую модель полного значения и R, checked matching callback.
u64/U64Cmp удобен для продолжения G3/G4; новый function-item/closure профиль нужен отдельной квалификацией.
На реальном fn-pointer пути uninit упирается в A2 плана пункта 1: closure companion не доказывает исходный P::CMP.
Получив до32 для выбранного профиля, написать именно этот theorem, а не «все возможные slices» без осей T/F.

### 6.2. Представительные типы требуют параметрического refinement theorem

Маршруты зависят от Copy/Freeze, размеров (efficient swap≤8, sort8≤16, stack budgets), ZST и layout.
Одни u8/u64 не покрывают default !Freeze, Freeze !Copy, oversized fallback, Drop и внутреннюю mutability.
Сами результаты для Cell/Drop тоже не являются proof всех типов соответствующего Rust trait-класса.

Потенциальный theorem:

1. Для фиксированного исходного slice ввести ghost identities элементов и независимые order ranks.
   Любой strict weak order на конечном множестве можно представить рангами его классов эквивалентности.
2. Проверить, что actual code переносит целые значения/identities, принимает те же comparator answers
   и зависит от payload только через проверенные comparisons и type/size predicates.
3. Доказать сохранение correspondence каждого actual move/copy и abstract transition; UB/permissions/validity
   берутся из проверенных обязательств пункта 1, а не из заявления «Rust generic значит параметричен».
4. Тогда abstract permutation и sorted ranks переносятся на original full values; для stability добавить original indices.

Rank и identity должны быть независимы. Модель `u8 >> 1` даёт лишь два полных byte-values на один key;
она не представляет произвольное число различных payload с одинаковым key.
Distinct fixed tags не покрывают duplicate values/ties. Нужны оба класса controls.
Generic callback может менять внешнее состояние; lawful stable R и footprint надо связать с actual FnMut,
не требовать без объяснения абсолютной чистоты всех пользовательских callbacks.

Feasibility такого lifting **5–10 дней**, полноценный checked generic theorem — недели, исход не гарантирован.
Условный SortModel с default false полезен для постепенного покрытия, но не заменяет этот шаг.
Нельзя добавить model trait bounds, исключающие T/F, и затем объявить проверку исходного безусловного generic API.

### 6.3. Альтернативный инструмент

В [approved tools](https://github.com/model-checking/verify-rust-std/blob/main/doc/src/tools.md) есть VeriFast,
Kani, KMIR, ESBMC/GOTO-Transcoder, Flux, RAPx; approval не равен готовой поддержке этого unsafe Rust target.
Наиболее полезный общий spike с пунктом 1 — VeriFast ownership/sequence proof реального insertion helper:
initialized segment + hole invariant, sorted ghost list, permutation, frame и termination.
Он потенциально одновременно закрывает all-length ось и immutable/ownership obligation.

Цена пилота **5 дней**; успешный пилот ещё не доказывает generic traits/specialization/compiler correspondence.
Ручная копия алгоритма на другом языке без проверяемого relation не solution.
KMIR/ESBMC полезны для независимой диагностики/конкретных сравнений, но другой solver не приносит
сам по себе отсутствующие UB модели и arbitrary-length theorem. Новый неодобренный инструмент требует application.
Отдельного proof-владельца назначает владелец; существующий VeriFast maintainer не получает новую миссию автоматически.

## 7. G4: встроить уже принятый порядок, не начинать массовый 0..32

Источник — `scratchpad/plan/PLANNER-TRAITPFC-G4-FRAMING-ANSWER.md`; ниже план воспроизведён по смыслу,
чтобы roadmap не зависел от наличия scratchpad. G4 — предложение; исполненного G4 результата в исследованных материалах нет.

| Стадия | Работа и приёмка | Что закрывает / цена |
|---|---|---|
| G4-0, pin/model bridge | Проверить прямые attrs на actual selected impl; перенести G3 как opt-in, calibrated domain/guard, без runtime changes | Доступность механизма на точном combined pin; **1–3 дня** |
| G4-1 | T1 N0/N1 и один содержательный N4; extend enabled/snapshot/checker согласованно, real bodies, no stubs; return/frame/permutation и негативы | Early return и новая длина general, где обе половины расширяются insertion и merge; **2–4 дня** |
| G4-2 | Semantic leaf contracts реальных insert_tail и bidirectional_merge для exact малого general domain; затем consumer с verified summaries | Первая **замкнутая** композиция, а не просто новый PASS; **5–10 дней** с устранением найденного blocker |
| G4-3 | sort4, затем sort8 с отдельным temp scratch, затем реальная верхняя general ветвь | Переиспользуемые summaries sortedness + full permutation + frame, **3–7 дней/новый уровень**, по измерению |
| G4-4 | sort9/sort13 summaries, insertion after prefix, network merge N18 и смена halves N25/N26 | Закрытие алгоритмических ветвей; это труднее одного swap safety-summary, **5–15+ дней** на содержательный блок |
| G4-5 | Явная матрица всех N0..32 выбранного профиля, затем forwarding T2→T3 и другие специализации | Полнота конечной length-оси, если доказаны bounds/callers; не generic/all-length theorem fallback |
| G4-L | Отдельно calibrated loop induction для unbounded insertion/fallback | Обязательная оставшаяся ось длины; не ждать окончания всех32, feasibility делать рано |

Нынешний snapshot `[u64;3]` не годится для N0/N1/N4 без правки; для N0 checker не должен читать vals[0].
Не расширять сразу до snapshot32: first N4 измеряет стоимость модели и actual body отдельно.
T1 N4 не включает sort4/sort8 и потому подходит как первый содержательный composition case.

На G4-2 leaf обязателен раньше consumer. Совпадают T, **точный F**, instance/body, regions, offsets,
backing, initialized ranges, scratch и callback write frame. Показать actual selected Check/Replace,
не делать вывод об activation по наличию атрибута. Swap safety requires/modifies не заменяет permutation summary.
Post merge: обе отсортированные половины → полностью инициализированный отсортированный выход и сумма кратностей;
insert_tail: prefix+tail → extended sorted prefix и сохранение всей active multiset.

Полная композиция требует доказанного отношения кратностей. На real execution независимый arbitrary probe
доказывает все значения при фиксированном probe и отсутствии его влияния на runtime.
Но stub с postcondition только для одного probe ограничивает один count в данном symbolic state.
Нужны корректные quantifier/ghost-state правила на всех уровнях и общий fixed probe, либо полная snapshot/count
спецификация. Не менять F на struct с полем probe и переносить результат на U64Cmp без equivalence proof.

Пункт 1 здесь существенен: C2/SEL1 пока не квалифицируют shadow transfer Replace/RecursiveCheck.
G4 функциональную композицию с uninit OFF можно исследовать как отдельный ограниченный результат,
но нельзя считать её автоматически сквозным ON proof. Для него нужны actual bodies, sound init summaries
из плана пункта 1 или другой доказанный composition theorem. Нельзя благословить весь modifies region как initialized.
Loop-contract havoc/summary также надо квалифицировать с uninit/valid-value checks: функциональный invariant
сам не устанавливает правильную shadow mask и не разрешает исчезнуть hole-negative после абстрагирования тела.

## 8. Стоимость, #5117 и перенос G4 на fork CI

| Наблюдение | Как использовать |
|---|---|
| POSTS8: sortedness≈68s, probe count TIMEOUT600s | Числа сообщены владельцем и в G4 framing; exact executed report/pin в просмотренных curated файлах не найден. Это исторический ориентир, не измерение нового G4 |
| U64-N13: leaf≈180s, composed TIMEOUT600s | Отдельный старый pin/profile; показывает, что summary consumer не гарантированно дешевле leaf |
| G3: семь roots ΣVT596.71s | Уже заметная прибавка до N4. Не переводить автоматически в нынешний PR budget по одному Linux результату |
| #5117 no-cover N10 diagnostic | 347.04s, CBMC peak2.29GiB, driver peak11.92GiB; исходный nine-cover root убит около15.03GiB driver. No-cover diagnostic не даёт proof credit исходной задаче |

Последняя строка — из [#5117](https://github.com/model-checking/kani/issues/5117), linked
[RESULT-COVERCOST](https://github.com/Tiramisu-Cake/verify-rust-std/blob/8177d26b7fae1b77374003c3e6180fe9c3959544/research/challenge-8/kani-k1/RESULT-COVERCOST.md),
Kani `9461e07af7…`/nightly-2026-10-12, old Cloud profile, uninit OFF.
Причина driver growth не установлена как факт; streaming/parser fix сначала требует bounded profile,
не обещания «уберём covers — OOM исчезнет». Измерять driver, CBMC и одновременный aggregate RSS отдельно.

Что менять при дорогом proof:

- Разделить цену actual body, postcondition/model и composition havoc; сохранить общий исходный theorem.
- Сначала tight frame и небольшой leaf; избегать ненужного havoc всей scratch48 и повторных snapshots.
- O(N²) полные counts — честный первый finite-N model, но не бесплатное решение всех32;
  arbitrary probe/ghost permutation/sequence lemma требуют корректного composition аргумента.
- Обязательные useful assertions/covers не удалять ради PASS. Diagnostic no-cover отдельно и без переноса proof credit.
- #5117 memory-патч — отдельный инструментальный кандидат после профиля, ориентир **3–7 дней диагностики/узкого исправления**,
  с неопределённостью; смена runner не устраняет алгоритмический рост и не делает challenge CI приемлемым.

### Fork CI вместо прежнего Cloud Build

Перенос технически реален: std/Kani source и proofs не привязаны к GCB. Старые долларовые envelopes G4
не являются новым разрешением: Cloud остаётся $0. Нужны новый execution package и квалификация на целевом runner.

1. Exact std target + verification-only G3/G4 overlay, exact combined Kani/toolchain/deps, source/tree и flags binding.
   Не смешивать #752 cd355, research f046 и C2/SEL1 результаты как один pin.
2. Использовать проверенную K1/SEL1 replay обвязку как образец, не копировать исторический workflow вслепую:
   отдельный control/export, fork guard, только узкий CI overlay, штатные workflows не запускать случайно.
   Push/dispatch — координатор; без PR/issue/publication от воркера.
3. Первый opt-in batch: один Ubuntu runner, jobs1, ≤6 exact proof rows, 600s/root,
   job envelope≤90min с setup/upload reserve. Watchdog учитывает всю process group и доступную RAM;
   отдельный RSS/exit/signal для driver/backend, bounded logs/artifacts, UNKNOWN при loss/truncation.
4. Сохранить ordinary/PFC/stub selection, отрицательные и activation controls; исходный exit verifier отличается
   от compiletest/runner outcome. TIMEOUT/Unsupported/failed precondition не принимается как semantic proof.
5. После полного дешёвого leaf+consumer повторить на Linux/macOS, измерить critical shard и штатный parallelism,
   суммарный VT/peak. В обычный PR CI включать только прошедший полный theorem; дорогие варианты остаются opt-in.

Профиль object-bits12 уже принят для соответствующих proof fixtures; не отключать проверки и не менять slicing/solver
молча. Меньше object bits не доказывает произвольное число allocations/длин; держать bounds/guards из плана пункта 1.
В опубликованном #752 SmallSort уже занимает 65.9%/70.3% manual VT Ubuntu/macOS (PR summary);
даже хороший новый proof требует replacement/removal только доказанно дублирующего старого root либо согласования CI budget.
Большую полный Gate A матрицу инструмента делать на release freeze, а не на каждой N4 аннотации.

## 9. Общая дорожная карта пунктов 1 и 2: два воркера

План пункта 1 не заменяется новым перечнем sorting experiments. Общие зависимости:
FnPtr/comparator binding помогает и actual ON profile, и G4; initialized scratch/ownership и semantic summaries
нужны обоим пунктам; #5104 влияет на доверие lifting; loop induction нужен all-length safety и sorting.
Результаты по двум пунктам вести раздельно и соединять только на совпадающих domains/source/pins.

| Волна / точка решения | Worker14 | Worker15 | Результат и STOP |
|---|---|---|---|
| 0: уже намеченная основа пункта1 | A1 actual ON route matrix + exact uninit controls; static trait/pin bridge | B1 #3762 validity spike; затем подготовка D/#5104 пакета отдельной сессией | Завершить SEL1 gates координатором. Не запускать 33 длины или новую крупную tool feature |
| 1: короткое окно feasibility пункта2 | G4-0/1, затем один closed-general design/пилот по запасу | Loop/quantifier/frame/decreases controls; оценить ownership альтернативу | Timebox примерно неделя двух исполнителей. Решить Kani induction vs alternative и цену G4-2; это не срок решения challenge |
| 2: общие tool blockers | Finite FnPtr/A2 с source binding для P::CMP/U64Cmp; отдельные commits | #3762/нужные validity fixes; приоритет false-success controls | После этого actual combined ON proof, либо явно раздельные functional/off и safety/on результаты; не объединять credit по именам |
| 3: доказательства и расширение | G4-2→sort4/sort8→network summaries/конечная матрица; один proof-этап за сессию | Inductive insertion/fallback + ownership/permission theorem либо выбранные loop fixes | Helper specs и core attrs имеют одного владельца; стыки source/frames интегрировать последовательно |
| 4: полнота и подготовка solution | Direct contracts всех impls, caller bounds, T/F refinement, proof coverage map | Negative controls, all-length/UB correspondence, CI cost и final gate preparation | Final pin/std freeze, organizer-compatible CI, owner review; не объявлять full completion при enabled=false/unsupported ветвях |

На волне1 явно предлагаем короткое новое окно перед долгими implementation projects из плана пункта1:
цель — не потратить недели на Kani расширения, если C/all-length generic proof всё равно требует другого инструмента.
Если владелец приоритизирует немедленное UB coverage, окно G4 откладывается, но функциональные сроки сдвигаются честно.
Не вести A2, #3762, loop framework, весь borrow model и новые сети одновременно двумя исполнителями.

### Точки принятия решения

- **P1, pin/contract:** оба фикса включены, прямой target/impl выбран, enabled доказан true на заявленной области,
  substantive postcondition не vacuous. Иначе отдельный reproducer, не новая обёртка под видом trait theorem.
- **P2, G4:** actual N4 и полный matched leaf+consumer прошли со frame/permutation/return/negative controls;
  есть измерение стоимости, а не только PASS leaf. При timeout менять декомпозицию после разбора.
- **P3, induction:** base/step/exit/decreases и sound quantifier/frame controls проходят на выбранном pin;
  есть arbitrary-length region representation. Если нет — закончить узкий tool patch или выбрать альтернативу.
- **P4, genericity:** проверен перенос source→model для всех заявленных T/F и type-route classes;
  finite profile не превращён в generic обещание посредством default Model.
- **P5, complete solution:** direct contracts трёх entries, полная length/domain матрица или индукция,
  multiset/order (и явно оговорённая stability), все UB из пункта1, callback/panic/unwind scope и CI совместимы.
  Частичный результат можно подавать честно, но Limitations не заменяет missing success criteria.

## 10. Рекомендация и реалистичный масштаб

Самый ценный ближайший прирост — **G4 N0/N1+N4 и одна действительно замкнутая композиция**,
при прямых trait contracts на новом квалифицированном pin. Это поднимает форму и содержание над N2 wrappers,
не обещая преждевременно all-T/all-length. Одновременно нужен небольшой loop/quantifier pilot: без него
массовый рост конечных длин может закончиться ещё одной дорогой ограниченной матрицей.

Конечное 0..32 выбранного профиля принципиально достижимо при хороших summaries; сегодня стоимость не установлена.
Unbounded insertion/fallback, generic comparator/representation и immutable/UB proof — существенно более крупные работы.
Первые pilots — дни; несколько helper/composition ступеней — недели; полное решение обоих пунктов —
многонедельная/многомесячная программа с внешними решениями по инструменту и принятию pin, не очередной CI-прогон.
Slow upstream review обходится parallel fork qualification, а не объявлением непроверенного fork принятой trusted base.
Начинать с повторного 600s brute-force всех32, увеличения timeout или удаления дорогого count я не рекомендую.
