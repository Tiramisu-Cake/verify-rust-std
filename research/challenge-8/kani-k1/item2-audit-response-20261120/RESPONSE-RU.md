# Ответ на внешний аудит статуса пункта 2

Задание: `TASK.md` на `ee47c841c01c275ead16c0b15382782b6550d516`.
Анализ выполнен 2026-11-21 для среза отчёта 2026-11-20. Статус: **READ ONLY / PLAN ONLY**.

Основные фактические поправки принимаем. Пороговые контракты заслуживают первого пилота перед
продолжением матрицы длин. Однако ускорение в Kani, экспоненциальная сложность именно нашей
формулы и точная причина незавершённого запроса N13/N17 пока не установлены. Пилот проверяет
новую функциональную декомпозицию, а не закрывает пункт 2, UB или общий theorem по T.

Прочитаны только очищенный аудит, исходники и committed summaries; скрипты `experiment/`
изучались как текст. Compiler, Kani, CBMC, SAT-решатели, скрипты аудитора и CI не запускались;
raw CI logs/archives не читались и не скачивались. Прошлый запрещённый аудит не открывался.
Отчёт и исторические admission/ledger не изменены. Поправка координатора об ответе автора
на ревью от 2026-11-16 принята как вход задания; §0.7/§6.3 аудита из разбора исключены.

## 1. Сверка фактов

Источники ниже читались через `git show COMMIT:PATH`. Это повторная сверка содержимого Git,
а не независимое исполнение verifier и не новое proof credit. Сокращения путей:

- `K1` = `research/challenge-8/kani-k1/` в этом репозитории;
- `S` = `library/core/src/slice/sort/shared/smallsort.rs`;
- `V` = `library/core/src/slice/sort/shared/smallsort/verify/`;
- `G` = `ee47c841c01c275ead16c0b15382782b6550d516`;
- `STD` = `7b31b060b90ce286e94547993f6a698c549bc5fa`;
- `KANI` = `0aac16ef62da9e9d5645782d458593e5d78143ba`, локальный Git
  `/root/kani-upstream-ch8-s1` (репозиторий `Tiramisu-Cake/kani`).

| Утверждение аудита | Первичный источник | Итог сверки |
| --- | --- | --- |
| По умолчанию CaDiCaL, в S4 нет `#[kani::solver]` | `KANI:kani-driver/src/call_cbmc.rs`, `DEFAULT_SOLVER`, `resolved_solver`; `STD:V/sorting_s4_partition.rs`, `sorting_s4_network_partition.rs`, `sorting_s4_network_r2.rs`, `sorting_s4_full_lengths_next.rs`; `d10b721e5f:K1/kani3300/ch8-s4/network-r2-impl/RESOURCE.json` | Подтверждается. Приоритет CLI solver выше harness attribute и default: отсутствие атрибута само по себе недостаточно. В зафиксированном argv override отсутствует; наблюдения backend также называют CaDiCaL. Наличие Kissat в dependencies не означает его использование. |
| N13/N17: symex 3,62/5,70 с, SSA 0,53/0,67 с | `8bf99aa314310e4a3d5b86b8d0f112ddff2886ab:K1/kani3300/ch8-s4/run-44577116178/COST-INTERPRETATION.json`, `censored_cases[].bounded_backend_observations` | Подтверждается: 3,62284/5,69742 и 0,528227/0,669993 с. Первая напечатанная формула: 455495/761349 и 608369/1005707 variables/clauses. Далее были небольшие приращения. |
| Шесть/пять SAT-ответов, последний текст `Running propositional reduction` | Тот же источник: `SATISFIABLE_messages_printed`, `last_retained_line`, `cover_warning`, `unattributed_cost` | Подтверждается как частичное текстовое наблюдение. Завершённые solver calls N13: 0,0532742–3,02797 с; N17: 0,0961858–7,63886 с. Их нельзя связать с конкретными covers/roles без native IDs. Последняя строка не доказывает состояние процесса в момент timeout. |
| «Оставшиеся ~566 с — SAT, блокер не лимит» | Тот же источник: `difference_scope`, `native_verification_time_s`, `diagnostics_complete` | Лишь гипотеза. Child 600,071/600,152 с, compile-marker upper 33,869/32,884 с; разности 566,202/567,268 с не являются exclusive solver time. Ранние напечатанные стадии быстрые; незавершённый reduction/solve и вклад oracle/body ещё не разделены. Нет completed VT, итогового native inventory и доказанной причины. |
| S2 `post` — `sorting_model::post` | `STD:V/sorting_s2_span.rs`, active `Span::post`; `STD:V/sorting_model.rs`, `active_post` | Подтверждается: порядок плюс кратности каждого входного значения при равных длинах. Комментарий «не осталось места для нового значения» действительно есть. Swap использовал отдельный точный перенос пары, не тот же span post. |
| Merge-pilot не исполнялся в Kani | `G:K1/kani3300/ch8-s2/merge-pilot/HANDOFF.md`, `INVARIANT.md`, раздел M; `G:K1/kani3300/ch8-s2/run-44375519132/VERDICTS.md` | Подтверждается по committed status: offline invariant для всех 256 байтов, Kani/compiler/CI NOT_RUN, credit NONE. В S2 был actual `merge32_real`, но не invariant-root. Непроверенный пилот нельзя считать опровергнутым. |
| PLAN v2 требовал декомпозицию после неудачных больших probes | `G:K1/PLAN-CH8-ITEM2-SORTING-v2.md`, §5 и P2 в §11 | Подтверждается текст: при неудаче merge32 primary decompose option; P2 STOP — budget/weak summary/vacuity, «не brute-force33N или увеличение timeout». Это owner-gated черновик, не доказательство действовавшего безусловного разрешения/запрета. |
| После S2 пошли по длинам | `G:K1/kani3300/ch8-s2/run-44375519132/VERDICTS.md`; `5300938600:K1/item2-status-report-20261120/REPORT-CH8-ITEM2-STATUS-RU.md`, §3.1–3.2; admissions в следующей строке | Нужна хронологическая оговорка: сначала S3 actual leaves, затем bridge, fallback partitions, network partitions, literal calls и N8/N9/N13/N17. Это дало bounded результаты и поправило encoding, но не завершило invariant/semantic-summary ветвь P2. Отчёт должен явно объяснить расхождение с основной стратегией v2. |
| Network 7/33, fallback 5/17, general 0 | `8896f60ae9e0ea1c706c6b8693d00e2500190676:K1/kani3300/ch8-s4/admission-s4p2-r2-network/ADMISSION.md`; `65e78d6bafca12a0f07894fe57897e46bc042b4e:K1/kani3300/ch8-s4/admission-s4p3-network/ADMISSION.md`; `9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9:K1/kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md`; `457641417707e7d254e6074bfd1f02c794fde04e:K1/kani3300/ch8-s4/completion-and-752-plan/CLOSURE-MAP.md` | Подтверждается для новой S4 route-линии: network u8 {0,1,2,3,4,8,9}; fallback Cell {0,1,2,3,4}; general не имеет нового полного route admission. Включены пустые длины. Это не доля всех T/F/геометрий и не отмена S1 entry smoke N0..3 или старых bounded harnesses. |
| N01 33,4 с против N2 3,1 с | `7c66fb85b99f77801ff10e99ccc5d37761ba5442:K1/kani3300/ch8-s4/run-44548842328/COST-INTERPRETATION.json`; `STD:V/sorting_s4_network_r2.rs` | Подтверждается: native VT 33,427759135/3,061223584 с, child 72,998/41,716 с. В N01 literal calls выбраны bool, но post/frame используют n∈{0,1}. Цена symbolic post/frame/branch encoding правдоподобна; причинность не измерена, нужен paired diagnostic. |
| 26 запусков, 15 остановились на инфраструктуре | `26db9b630682cfae8670392ea9236d701f45b481:K1/CH8-DISPATCH-LEDGER.md`; отчёт `5300938600`, §5.1 | Подтверждены 26 различных run IDs из этого списка: 18 учтённых и 8 charge0 (включая попытку с нулём jobs). Число15 получается как семь ранних S1 без финальной квалификации + восемь charge0. «На инфраструктуре» — широкая оценка: S1-03 также имел native timeouts, другие S1 — завершённые native rows. Нельзя утверждать, что все15 не дошли до proof или имели исключительно инфраструктурную причину. Это не новый пересчёт ledger. |

Сверка CaDiCaL по default и по отсутствию harness override не заменяет tool/request binding;
здесь её дополняют закреплённая конфигурация и уже опубликованные bounded observations.
Статусы N13/N17 остаются **UNKNOWN/BLOCKER, не FAILURE свойства и не SUCCESS covers**.

Для воспроизводимости арифметики15: семь ранних S1 — 43775527125, 43777127361, 43784240498,
43830757263, 43864841077, 43889560779, 43923266772; восемь charge0 — 43827636574,
43829165289, 44264952389, 44284869572, 44302170220, 44310254730, 44328364855, 44405927807.
Остальные11 учтённых IDs — два composite origins и девять S2–S4 из таблицы §5.1 отчёта.
Это ограниченный список попыток, а не утверждение об отсутствии любых иных workflow events.

Фраза аудита «три замера S2 не прошли» требует различать NOT_RUN и timeout. В r4-r2 первым
исполнялся `general32_weak`, достиг group RSS cap; остальные10 roots не исполнялись.
В r5 `merge32_real` и `sort13_assumed` остались UNKNOWN, а general32 pair был
DEFERRED_NOT_SELECTED. `swap_pfc` имел native SUCCESS, но qualification NOT_GRANTED;
завершённые negatives не совпали с ожидаемыми roles. Это не три одинаковых solver-timeout.
Источник r4-r2 — ledger выше, r5 — `G:K1/kani3300/ch8-s2/run-44375519132/VERDICTS.md`.
Последующие S3/S4 имели отдельные review/GO; наличие таких разрешений не означает прохождение P2.

## 2. Техническая оценка пороговой формы

### 2.1. Логика сведения

Для фиксированного байтового порядка положим `gq(x) = (value(x) >= q)` и
`Q(X,Y,q) := len(X)=len(Y) && ∀k<len(Y): gq(Y[k]) = at_least(len(X)-k, gq(X))`.
Тогда для выхода, не зависящего от q, `∀q:u8 Q(X,Y,q)` эквивалентно тому, что Y —
отсортированная перестановка X. Действительно, индикаторы Y обязаны идти 0…01…1, а число
единиц равно входному для каждого порога. Из хвостовых частот восстанавливаются кратности:
`count(value=v) = count(value>=v) - count(value>=v+1)`, с нулём для порога 256.
Это математическое обоснование, не результат нового verifier-run.

Отдельная форма `∀q count(X,q)==count(Y,q)` тоже корректна для сохранения мультимножества
при равных длинах; порядок она не устанавливает. Аудитор обоснованно различает её и пороговую
форму: для compare/exchange порог даёт детерминированные AND/OR. Нужны доказанные локальные
отношения и подходящая спецификация потребителя; одна замена `==q` на `>=q` ускорения не гарантирует.
Унарный `at_least` можно задать bounded булевым DP, как `thr` в `experiment/gen2.py`:
это отсутствие двоичного счётчика, но не отсутствие вычисления количества или стоимости SAT.

Формулы swap/insert из §3.2 аудита верны для полного байта и чистого `<`. Вставке достаточно
q-монотонности префикса для q-поста, хотя весь префикс может быть численно не отсортирован.
Merge-формула требует явных границ `0<=i<=len(L)`, `0<=j<=len(R)`, `i+j=k` и
short-circuit перед обращением к исчерпанному фронту. Условия `i=len(L)`/`j=len(R)` —
логические sentinels, не разрешение читать one-past. Для нечётной длины отдельно нужен leftover.
При q-монотонности половин RHS равен условию `k>=zeros(L)+zeros(R)`: допустимые i,j
существуют ровно тогда, когда их сумма не меньше суммы длин нулевых префиксов. Это объясняет
спецификацию, но для actual-body no-panic proof дополнительно нужны numeric-sorted halves
и связь всех четырёх курсоров, а не только пороговая алгебра.

Это сведение относится к трём точным `Project`-реализациям из `STD:V/sorting_model.rs`;
в них байт — всё логическое значение. Оно не доказывает сохранение payload/id у произвольного
типа с одинаковыми ключами, стабильность или корректность произвольного `FnMut`.
Отдельная мета-теорема о 0-1-сетях не нужна, **если** каждый lifted-контракт доказан на
реальном байтовом теле для произвольного q. Для обобщения на T аргумент всё равно нужен.

### 2.2. Ghost q и граница доверия

Предпочтителен verification-only q в `KeyLess<T>`, с сохранением имени T/F и неизменёнными
`call_once`/`call_mut`. На текущем пине это stateless tuple struct с `PhantomData`; добавить
поле технически возможно, но оно меняет verification layout компаратора. Нельзя считать старые
PFC автоматически доказательством новой модели. Обязательны следующие условия:

1. Каждый положительный PFC/consumer создаёт q через самостоятельный `kani::any::<u8>()`.
   Нет сужения алфавита, фиксированного q, `any_where`, фильтра по q, зависимости входного
   массива от q или assumptions о результате. Поле не меняется между вызовами.
2. Runtime сравнения и алгоритм не читают q и не ветвятся по нему; читают его только specs.
   Проверить весь путь конструктора/callback, а не только одну строку `call_mut`.
3. Допустимое именованное requires «prefix q-monotone» означает
   `∀q,X: Pre(X,q) => Post(X,q)` и может ограничивать пары X/q в PFC. Это не скрытый
   фильтр q: потребитель обязан вывести тот же Pre для своего свободного q. Требование
   «никаких assume через производные q» нельзя буквально распространить на такой явный Pre;
   запрещено дополнительное ограничение q сверх опубликованного условного контракта.
4. Capture — owned pre-state, включающий порог, длину и нужные исходные значения/индикаторы.
   `old(threshold(is_less))` разумен; дополнительно frame/ensures сохраняет q. Нельзя молча
   брать в post новый q после havoc F. `modifies` не включает весь компаратор ради удобства.
5. Все `enabled<T,F>` guards точны. Неактивная generic specialization не читает storage/F.
   Положительный root утверждает activation и имеет meaningful covers, включая q=0, q=255,
   порог, разделяющий входные значения, повторения и отсутствие значения q.
6. Таблица provider→consumer фиксирует source/tool/cfg, T/F, Pre, геометрию, frame и **домен q**.
   Регистрация PFC не равна его успешному исполнению. В исходниках KANI есть проверка наличия
   PFC (`tests/ui/stub-verified-without-contract/stub_verified_no_harness.*`), но она не
   устанавливает, что harness охватил все входы или был успешно проверен. Наш S2 прямо имел
   `*_registration_only` без qualification (`STD:V/sorting_s2_batch.rs`).

Verification-only static q хуже: добавляет global state/alias/havoc obligations, скрывает связь между
вызовами и создаёт новую границу доверия. Для первого пилота не нужен.

### 2.3. Выразимость на KANI: вероятна, компиляция не установлена

Пин имеет `requires`, `ensures`, `modifies`, `proof_for_contract`, `stub_verified`, snapshots
через `old` и specialization. Свидетельства синтаксиса: `docs/src/reference/experimental/contracts.md`,
`tests/kani/FunctionContracts/specialization_default_old.rs`,
`tests/expected/function-contract/modifies_fat_pointer/u8slice.rs`; наш `STD:S` уже использует
`old(snapshot(...))` с generic guards. Этого достаточно для проекта атрибутов,
но недостаточно объявлять компилируемым новый `old(threshold(&mut F))` и raw-pointer tuple post.

| Место | Предлагаемое аддитивное описание | Что надо проверить |
| --- | --- | --- |
| `sorting_model.rs` и новый q-model | cfg-поле q, явный `with_q`, guarded generic facade `threshold/capture/qpost`; bounded DP без solver quantifiers | Borrow/lifetime у old, отсутствие чтения неинициализированного, сохранение activation всех T/F; старый `new()` не превращается в случайный q. |
| `swap_if_less` | q AND/OR ensures, прежние safety requires и modifies двух элементов | a=b, оба порядка индексов, exact footprint, неизменность q; обычное тело без stub. |
| `sort13_optimal`, затем `sort9_optimal` | requires минимальной длины; modifies только prefix13/9; q-order-stat ensures этого префикса, frame всего хвоста | Функция сортирует **первые** 13/9 элементов, не весь переданный slice. N17 передаёт region длиной 17. Без prefix/frame контракт неверен или неприменим. |
| `insert_tail` | прежняя геометрия/read/write; отдельный q-prefix Pre и piecewise q-post; modifies `[begin,tail]` | Новая q-ветка не должна одновременно требовать старый numeric-sorted Pre и старый полный count post. Это разные экспериментальные спецификации одного actual body. |
| `sort4_stable`, `sort8_stable` | q-post src→dst, safety/init/disjoint и точный dst/scratch frame | Snapshot читает только src, не unwritten dst/scratch. Same-allocation и separate allocation — разные qualified domains. |
| `merge_up`, `merge_down` | q результата AND/OR; точные возвращённые указатели и выбор ветви по сравнению исходных значений; dst-only modifies | Post одного бита не задаёт курсоры. `merge_down` использует `wrapping_sub` для source; sentinel перед началом не разыменовывается. Структура return tuple и raw pointers требует native калибровки. |
| `bidirectional_merge` | bounded q-merge post плюс source/dst frame; отдельная order/panic-связь | Forward/reverse cursors, обе половины, leftover, panic и выходная init-state не выводятся из одного порогового отношения. |

«Чисто аддитивно» означает сохранение runtime bodies, generic signatures, CFG и старых
обязательств. Потребуются новые verification modules/guards/атрибуты, а не только несколько
ensures поверх S2. Сохранение старого S2 count post в той же q-кампании вернёт старую тяжёлую
формулу. В отдельном opt-in cfg старые S2/S4 режимы должны сохранить прежнюю семантику,
а q-режим — эквивалентные safety clauses и новую функциональную спецификацию.
Изменение cfg guards требует проверки, что нет конфигурации с потерянным safety requires.
Это проект будущего diff, не внесённое изменение и не разрешение ослабить прежний admission.

`stub_verified`-композиция применима только после реальных provider proofs в том же домене.
Она переносит утверждённые ensures, а не весь исполненный callee. Нельзя одновременно
подменять доказываемую функцию собственным summary, считать diagnostic assumptions леммами
или переносить bounded provider на другие allocations/длины по одному имени функции.

### 2.4. Ограничения и спорные выводы аудита

- **E-01 конкретнее, чем «pointer invariants не работают».** В
  `G:K1/kani3300/ch8-e/e01/RESULT.md`, §Q/OFF, истинный isolated pointer/exists witness
  ломался даже без loop contracts; были ignored existentials и ERROR. Математический
  инвариант не опровергнут. Scalar SUCCESS имел warning с nondeterministic substitution
  у init-helper: это не готовый надёжный обход. Нельзя механически вставить `kani::exists`
  из формулы merge. Для bounded пилота — явные конечные циклы/DP с unwind, без quantifiers
  и без `-Z loop-contracts`, чтобы PFC не переводил циклы в автоматический contract mode.
- **E-02 сохраняется.** `G:K1/kani3300/ch8-e/e02/run-43792979809/RESULT.md`:
  primitive write при loop-contracts+uninit ON давал sole assigns failure
  `Check that self->value is assignable` на KANI и SEL1; OFF/no-write/no-loop отличались.
  Функциональный OFF пилот не является исправлением ON. Отдельный ON-план
  `8347878066:K1/kani3300/ch8-s4/init-on-feasibility-plan/PLAN.md` также сохраняет
  union/layout, copy extent/downward offsets, AddressOf, capture/havoc/init-mask blockers.
- **SAT-модель — полезная гипотеза о кодировании.** В `experiment/gen2.py` локальные
  отношения добавляются `assert_true` как assumptions CNF. В `gen5.py` так же внедряется
  инвариант; генератор ограничен чётным n. Отдельные случайные проверки лемм — tests,
  не индуктивные proofs. Модель не содержит реальных pointers, guards, memory instrumentation,
  panic checks и стоимости Rust contracts/havoc. Её времена и ранжирование остаются
  source-reported модельными наблюдениями; здесь они не воспроизводились.
- **Причина S2 и асимптотика.** Счётная сводка может быть существенно тяжелее тела:
  потребитель восстанавливает глобальные факты из слабой локальной информации. Это сильная
  мотивация изменить summary. Но аргумент про pigeonhole и несколько конечных точек не
  устанавливает нижнюю экспоненциальную оценку для конкретной CBMC-формулы с CaDiCaL,
  не доказывает, что никакой cap не поможет, и не объясняет все S2 setup/RSS stops.
- **Panic — отдельное обязательство.** У lawful `<` отсутствие comparator panic не закрывает
  `panic_on_ord_violation` в merge. После q-only stubs значения внутри одного порогового
  класса произвольны; numeric sortedness половин из одного q не следует. Поэтому будущему
  merge-consumer нужны отдельно доказанные numeric order ensures/связи курсоров либо
  самостоятельный actual-body order/panic proof. Q-монотонные, численно неотсортированные
  половины не дают права заявить no-panic. Нельзя выключить panic checks или поставить
  panic-stub ради q-PASS. N17 вообще возвращается до merge и этого канала не проверяет.
- **UB и T не поглощаются.** Нужны actual-body корни без verified stubs и без тяжёлого
  функционального oracle, с требуемой UB instrumentation и её negative controls. OFF
  safety не становится uninit/validity/permissions proof. Равенство внешних значений не
  исключает запись с восстановлением и не доказывает init-mask. Для validity нужны типы
  с запрещёнными битовыми значениями, для layout — padding/ZST/размерные/Copy/Freeze классы;
  произвольные F, interior mutation, Drop/unwind — свои домены. Классификация представителей
  и source parametricity argument должны быть названы; новая матрица u8 не есть ∀T.

## 3. Пилот P-1…P-5 — только план

### 3.1. Файлы и профиль будущего кандидата

База actual std — STD, tool — KANI. Будущий diff ограничить `S`, соседним `verify.rs`,
`V/sorting_model.rs` и новыми `V/sorting_q_model.rs`, `V/sorting_q_pilot.rs`,
`V/sorting_q_controls.rs`. Предлагаемый изолированный cfg — `kani_smallsort_q_pilot`
(контроли дополнительно `kani_smallsort_q_controls`); это новые имена, сейчас они не реализованы.
Не включать автоматически S2 assumed/count attrs; эквивалентные safety clauses сохраняются.
В implementation package добавить manifest `provider → exact consumer call/domain`,
ожидаемые roles/covers/negative-property labels и минимальную конфигурацию runner.

Профиль: u8/KeyLess<u8>, initialized V34, unrestricted full-byte inputs, q:any,
unwind36, exact singleton selection, jobs1, object-bits12, child600 **включая compile**,
local RSS≤6GiB. Включить необходимые function-contracts/mem-predicates/stubbing/export-json;
убрать из **нового** профиля автоматическое loop contracting и quantifiers. Старый профиль
не редактируется. OFF uninit/validity сохраняется явно в названии результата. Действие
`--no-assert-contracts` на explicit PFC и callee requires должно быть подтверждено inventories:
PFC ensures, frame и caller preconditions обязательны, независимо от имени CLI-флага.

Под «точным корнем» ниже понимается имя в будущем модуле:
`slice::sort::shared::smallsort::verify::sorting_q_pilot::<name>`;
для P-5 — тот же префикс с `sorting_q_controls`. Имена ещё не зарегистрированы.

| Шаг / exact name | Атрибуты и домен | Обязательный сигнал |
| --- | --- | --- |
| P-1 `p1_swap_u8_v34_q_any` | `proof_for_contract(swap_if_less)`, без stubs. Как S3 swap: base0..20, a,b0..12 в V34, включая a=b; q:any. Q AND/OR и полный outside-value frame, сохранение q. | Все PFC/safety/unwind/frame roles SUCCESS; covers обоих направлений, равенства, useful return, разделяющего порога. Старый S3 admission не заменяет этот provider. |
| P-2 `p2_sort13_u8_b01_len17_q_any` | `proof_for_contract(sort13_optimal)` + `stub_verified(swap_if_less)`. Actual вызов `&mut v[1..18]`; контракт q-sort первых 13, хвост `[14..18]` и остальные значения V34 сохраняются. P-1 покрывает base1 и все 45 пар. | PFC prefix q-post, tail/frame, caller requires и unwind SUCCESS, activation/return/corner covers. Это проверяет provider ровно для P-4, не общий slice/len theorem. |
| P-3 `p3_insert_u8_b01_rel1_16_q_any` | `proof_for_contract(insert_tail)`, без stubs; begin=1, relative tail:any∈1..16, V34; только q-монотонный prefix Pre, без numeric sorted Pre. Включает худший tail16 и необходимые P-4 tails13..16. | Q-shift post и frame SUCCESS; каждый tail1..16 имеет reachable cover, есть early return/full sift и q-монотонный, численно неотсортированный prefix. Если symbolic tail не помещается, результат UNKNOWN; не сужать молча до16. |
| P-4 `p4_network_u8_b01_n17_q_any` | `proof`, `stub_verified(sort13_optimal)`, `stub_verified(insert_tail)`; actual `small_sort_network(&mut v[1..18], &mut f)`. Сам `insertion_sort_shift_left` остаётся real body; вставки tails13..16, q один и тот же. | Q-order-stat post всего N17, outside-value frame, q frame, callee Pre, safety/unwind и useful return SUCCESS; meaningful mixed-threshold/duplicate/extreme covers. В consumer нет старого full-count oracle. |
| P-5a `p5_swap_false_or_q_any` | Изолированный control-cfg mutant q-ensures swap: левый AND заменён OR, q:any, actual body и геометрия P-1. Не ordinary stub. | Designated PFC q-ensures FAILURE на разных индикаторах; compile/unsupported/timeout или любой произвольный failure не годится. Mutant не провайдер P-2. |
| P-5b `p5_swap_false_or_q_fixed0` | Тот же false-OR mutant, но намеренно q=0 в PFC; единственное отличие от P-5a. | Ожидаем Kani SUCCESS: все u8≥0, неверная универсальная лемма здесь истинна. **Наш provider gate обязан REJECT** fixed-q qualification. Это демонстрирует неполноту PFC-domain, а не ожидаемый отказ Kani. |
| P-5c `p5_network_n17_qpost_corrupt` | Consumer с правильными P-1/2/3 summaries; после real network один элемент меняется через harness-only порчу с 0 на255. Свидетель `[0;17]`, свободный q включает q=1. | Designated consumer q-post FAILURE с feasible mutation/useful-path cover. Новый output value теряет мультимножество; причина не в лживом provider. |

Порядок доверия: P-1 → P-2; P-3 независимо; P-2+P-3 → P-4/P-5c.
В одном CI могут быть выполнены все roots, но consumer помечается diagnostic до проверки
provider results. Если P-1/2/3 не приняты на точных доменах, быстрый P-4 не даёт credit.
P-5a/b — отдельная control-конфигурация, не контракт положительных корней. Одного cfg,
смешивающего верный и неверный provider, быть не должно.
Кроме native исполнения P-5b нужна отдельная проверка qualification: в тестовый provider
manifest подать его успешный результат с явно указанным `q_domain={0}` и проверить отказ
универсальному consumer с причиной `Q_DOMAIN_NOT_UNIVERSAL`. Затем проверить, что корректный
P-1 с `q_domain=all_u8` не отвергается по этой причине. Это проект проверки gate с source/domain
review, а не восьмой native proof invocation. Один Kani SUCCESS фиксированного q этот gate не тестирует.

Существенные уточнения к исходным «пяти корням»: tail16 сам по себе не покрывает tails13–15;
PFC sort13 на len13 не покрывает вызов со slice len17; P-5 содержит несколько независимых
проверок. Нужны **четыре положительных + три контрольных invocation = семь**, а не пять.
Необходимые проверки q-эквивалентности на малом N и matched old/new oracle, real-body N13
без функционального поста (впоследствии ON), wrong-precondition/weak-summary/frame/lost-value
контроли и N13/N32 расширение — следующие отдельные gates. Этот пилот не заменяет полную
приёмочную матрицу и не заявляется как её новый admission.

### 3.2. Критерии и стоимость

До исполнения: static review охвата q/геометрии, definedness captures, runtime diff и cfg
матрицы; отдельное независимое review точного implementation candidate. Нужен native check
регистрации/компиляции, а не обещание компилируемости из этого текста. Runner error-path checks
повторяются для изменённого runner; прежний неизменённый runner не требует переписывать сотни
тестов только ради другого списка roots.

Положительный **исследовательский** результат: все четыре positives завершены с полными
native inventories, нужные covers достижимы, три controls различены как выше; P-2 и P-4
каждый child≤300 с (предлагаемая цель запаса, не правило организаторов), RSS в captured cap.
Это переносимость идеи на Kani в точном OFF-домене. Результат 300..600 с — ограниченный fit
без целевого запаса; дальнейшая архитектура требует решения. Timeout P-2 или P-4, незамкнутый
provider domain, unexpected panic, failed Pre/frame/unwind, ignored quantifier, nondeterministic
helper warning, unsupported или неполный export — пилот неуспешен/неопределён по соответствующей
оси. Compile failure проверяет выразимость, а не опровергает математическую q-редукцию.

При P-2/4 cutoff без нового различающего изменения остановить расширение N-матрицы и пересмотреть
кодирование/local summaries. Не повышать cap и не повторять тот же пакет до случайного PASS.
При успехе следующая стадия — малый matched oracle-equivalence контроль, отдельный order/panic
и actual-body UB-пилот, затем другие длины/типы/merge; исторический N13/N17 BLOCKER не переписывается.

Стоимость **первой попытки по плану**: одна новая авторизованная кампания, семь exact native
invocations, худший суммарный child envelope `7×600=4200 с`, плюс setup/discovery/review/upload
и reserve, которые надо отдельно поместить в окно/лимиты существующего coordinator.
Если discovery — отдельный процесс, он учитывается отдельно от этих семи proof invocations.
Это оценка, не резервирование бюджета и не GO. Нельзя обещать «один запуск подтвердит или
опровергнет всё»: compiler/setup stop может оставить вопрос открытым. Отдельный подготовительный
native campaign увеличит число запусков; это требует явного нового решения, автоматических retries нет.
Повтор на другом SAT solver или запуск CNF аудитора в эти семь не входит и здесь не разрешён.

## 4. Правки отчёта по §5 аудита

Ниже предлагаемый текст; исходный `REPORT-CH8-ITEM2-STATUS-RU.md` не правился.

| Пункт | Решение | Предлагаемая правка |
| --- | --- | --- |
| 1. Резюме, UB и пункт 2 | Согласны | «Пункт 2 требует контрактов сортировки трёх входных методов на заявленном допустимом домене. Первый список Success Criteria отдельно требует отсутствия UB у семи функций; это наша линия пункта 1. Обе части общего Challenge 8 остаются незакрытыми». |
| 2. Решатель в §4.1 | Согласны | «В S-линии на Kani 0aac16ef используется встроенный в CBMC CaDiCaL; CLI/harness override не задан. Kissat объявлен зависимостью tool, но не является решателем этих запусков». В словаре тоже заменить связку Kani/CBMC/Kissat на фактическую. |
| 3. Backend и O(N) | Согласны с числами; уточняем причинность | «N13/N17 имеют напечатанные symex 3,623/5,697 с и SSA 0,528/0,670 с; формулы около455/608 тыс. переменных. Несколько SAT-вызовов закончились быстро. Следующий запрос не завершён; точное время reduction/solve и вклад тела/поста неизвестны. Главная гипотеза — стоимость глобального oracle и его композиции; O(N) вместо O(N²) характеризует исходную проверку, не обещает меньший SAT time». |
| 4. Merge-pilot и STOP | Согласны добавить; не объявляем нарушение неизвестного owner decision | «PLAN v2 §5/P2 ставил декомпозицию главным продолжением при неудаче больших probes. Offline full-multiset merge invariant подготовлен, но в Kani не запускался. После S2 выполнены S3 actual leaves и S4 bounded/literal partitions; они дали частичные результаты, но не заменили отсутствующий decomposition gate. Переход к полной матрице длин пока не обоснован. Требуется решение о приоритетном q-пилоте». |
| 5. Покрытие | Согласны | «Новая S4 route-линия: network u8 — 7 из33 длин {0–4,8,9}; fallback Cell<u8> — 5 из17 {0–4}; general — 0 новых полных route admissions из33. Отдельный S1 проверил actual entry bodies на N0..3. Доли не выражают покрытие всех типов/компараторов/геометрий». |
| 6. N01 | Согласны, с меткой гипотезы | «N01 VT33,428 с против N2 VT3,061 с при literal runtime calls. Post/frame всё ещё зависят от bool-выбранной n. Возможный источник разницы — symbolic-length oracle/frame или branch encoding; matched diagnostic отдельно нужен до планирования symbolic N». |
| 7. Шаг3 плана | Согласны | «Сначала квалифицировать локальную пороговую композицию на P-1…P-5. До её успеха новые монолитные длины не планировать. После пилота оценить отдельные order/panic/UB gates и только затем bounded length/type матрицу с измеренной стоимостью». Сохранить UNKNOWN для её будущей стоимости, но назвать разрешающий gate и STOP. |
| 8. Словарь | Согласны как редакционную правку | Оставить около20 терминов: bounded/domain, pin, PFC, actual/Original, summary/provider, q, model activation, frame, init-state, OFF/ON, role, cover, U, metadata exception, intake, admission, source-reported, UNKNOWN/BLOCKER, child/native VT и PLAN ONLY. Общеинженерные SHA/JSON/CI и форматные детали вынести из основного чтения в приложение. |

Дополнительно к §5.1: «В рассмотренном списке26 попыток:18 учтённых и8 charge0.
Семь ранних S1 и восемь charge0 дают15 попыток без итоговой квалификации соответствующей
кампании; причины смешанные, включая инфраструктуру, encoding и native timeouts.
Это не15 запусков без native activity. Количество попыток не равно расходу бюджета
или числу доказанных обязательств».
Резюме следующего шага также заменить на q-композицию, чтобы оно совпадало с новым §7.

## 5. Процесс: две дорожки с общей границей достоверности

Идея отделить разведку от приёмки разумна. Минимальный исследовательский результат всё равно
должен быть воспроизводимым: source/tool/request/flags/solver, exact root/domain, exit/status,
compile/native/child timing, memory scope, timeout/missing/partial markers и нужные negative controls.
Иначе нельзя даже сравнить формулировки. Исследовательский PASS означает только наблюдение;
для promotion нужны qualification провайдеров, полный native inventory, binding/review и admission.

Что можно предложить владельцу:

- Один простой **версионированный** explorer-профиль на существующем coordinator, с малыми
  exact-root пакетами и manifest вместо отдельного набора prose-файлов для каждой попытки.
  Общие поля автоматически выводить из одного record. Не менять owner/slot/budget/phase controls.
- При неизменённом runner использовать уже пройденный preflight/service-test baseline;
  тестировать delta и обязательные error paths при изменении runner. Число389 само по себе
  не признак избыточности: без разбора тестов удаление не обосновано. Synthetic tests не
  доказывают sorting и не заменяют различающие semantic controls.
- Для исследования цены не проводить поштучный admission/U-emitter анализ, пока нет кандидата
  на приёмку; сохранять unknown/U/native data, не превращать их в PASS. Одинаковый `0:0` SUCCESS
  действительно не является скрытым failed status, но произвольный fingerprint/wildcard не
  доказывает происхождение и полноту inventory. Старые exact exceptions остаются прежними.
- Не убирать timeout, isolation, cleanup и identity checks: их потеря делает timing и attribution
  сомнительными. Нужность более тяжёлых protected snapshots/supervisor можно пересмотреть для
  изолированной разведки только с явно меньшим assurance и новым утверждённым профилем.
- Local CNF на синтетической модели может быть дешёвым предварительным фильтром, но запрет
  текущего TASK прямо включает запуск скриптов аудитора. Интерпретация аудитора не является
  разрешением владельца. Нужны отдельные границы среды/ресурсов и проверка доверия к решателю;
  даже UNSAT такого эксперимента не даёт Kani/std proof credit.

Фактическое сокращение процесса сейчас не применяется. Существующие полномочия и runner gates
действуют до решения владельца. Разведочный профиль не заменяет Cloud/GitHub lane-ограничения,
не открывает phase/окно и не разрешает внешние сообщения. Приёмка не сводится к «кандидатам
для публикации»: любой используемый как proof provider должен пройти свою qualification.

Предложенное source coverage полезно как диагностика маршрутного покрытия, но union строк не
доказывает достижимость каждой property instance и все релевантные states. Нельзя автоматически
заменить им U-обоснования или obligation/domain inventory в приёмочной дорожке.

## 6. Решения владельцу

1. Приоритизировать q-композицию P-1…P-5 и остановить расширение монолитной N-матрицы до её gate?
2. Разрешить следующей стадии реализацию отдельного q-cfg/ghost-поля и review с сохранением
   старых profiles/admissions, без общего T/UB credit?
3. Выдать для native пилота конкретные owner/lane/phase, окно и бюджет одной кампании с семью
   invocations и предложенной целью child≤300 с для P-2/P-4, либо выбрать другой критерий запаса?
4. Нужен ли до него отдельный разрешённый CNF-пилот аудитора на CaDiCaL; где его выполнять,
   с какими caps и учётом запусков? Текущая стадия его не выполняла.
5. Утвердить облегчённую исследовательскую дорожку и точный перечень отложенных admission checks,
   сохранив identity/resource/negative-control gates и запрет promotion без полной qualification?
6. Принять предложенные восемь правок текста и порядок дальнейших отдельных каналов:
   q-функциональность → numeric order/panic → actual-body UB/ON → расширение T/длин и интеграция?

Следующий исполнитель получает план, а не GO. Текущая стадия завершена анализом;
новые proofs, native observations, allocations, budget charges и independent B1/B2 credit: **NONE**.
