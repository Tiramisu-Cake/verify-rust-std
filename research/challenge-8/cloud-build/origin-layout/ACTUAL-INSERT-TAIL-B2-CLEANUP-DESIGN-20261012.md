# B2: точная очистка actual `insert_tail<u64, F>`

**Статус: дизайн до семантической реализации; NOT_RUN/NOT_PROVED.** Прочитана
редакция WORK-POLICY `6e1a8e59c56669abe5e6ec2013478e45ed2cc267`.
Этот документ не принимает профиль и не разрешает dispatch сверх текущей
сессии. B1 fresh qualification должна завершиться раньше B2. Источник —
SmallSort SHA-256 `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
полный `insert_tail` 536–571 SHA-256
`9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29`.
Первый actual consumer — `insertion_sort_shift_left` 596, второй —
`small_sort_general_with_scratch` 274. Трёхъячеечный `u64` — только
диагностический домен; generic `T`, ZST и полный caller остаются OPEN.

## Исходный граф и минимальная семантическая граница

В сохранённом прежнем MIR первый `FnMut` у строки 541 имеет
`UnwindAction::Continue`: guard ещё не создан. Поздний `FnMut` у 566 идёт в
cleanup `bb20`, где реальный `Drop(gap_guard)` ведёт к `bb21 UnwindResume`;
нормальные выходы цикла идут к отдельному `Drop` и `StorageDead`. Эти номера
исторические: B2 обязан повторно связать их с точными raw/decode MIR и proof
AST своего Build. Уход из позднего вызова прямо в `ReturnStmt(unwinding)`
пропускает runtime Drop и недопустим.

Exporter уже сериализует все четыре `UnwindAction` варианта для `Call` и
`Drop` (`vf_mir_exporter/src/lib.rs`, `encode_unwind_action` 3052–3064 и
терминаторы 2949–2982). **Первый вариант не требует exporter patch**:
проверить его фактические decoded Call/Drop blocks, source spans, normal и
cleanup successors. Новое экспортируемое поле допустимо обсуждать лишь после
конкретного отказа этой admission; оно не создаёт прав памяти.

Существующий callback protocol в `vf_mir_translator.ml` 2875–2907,
5441–5630, 6494–6508 допускает ровно один generic-`T` двухисточниковый
`FnMut::call_mut` с `Continue` и единым synthetic unwind epilogue. Поэтому
простое расширение числа вызовов или замена типа на `u64` недостаточны.
Нужны два раздельных span/CFG-bound descriptors на неизменённых runtime
вызовах. Первый возвращает оба займы и текущий `F` на normal, false return
и direct unwind до создания guard. Второй относится только к late Call с
проверенным `Cleanup` successor: на обоих исходах закрывает **его** два
`ref_initialized` fractions, завершает соответствующий lifetime и оба
`borrow_end`, возвращает текущие held/sift/F ресурсы, затем на panic
продолжает исходный `Goto` в cleanup guard Drop. Проверка связывает типы,
источники, доли и tokens с реальными `&tmp`, `&*sift`, `F` и MIR Call;
неподходящий/повторный marker, неверная область lifetime или другой
successor отказывает до proof. Она не принимает произвольные ghost commands
и не превращает `Cleanup` в `Continue`.

После actual `Drop` нужен **второй момент восстановления**, отличный от
callback loans. Существующий qualified selected Drop lowering (translator
3140–3217) создаёт receiver через `create_ref_mut` из полных полей и padding
локального guard, вызывает checked generated glue/selected method, затем
исполняет `close_points_to(receiver)`, `end_ref_mut(receiver)` и
`open_points_to(&gap_guard)` на обоих исходах. Только после возвращённого
CURRENT effect и линейного receiver-end можно закончить `held_ref`, объединить
дополнительную долю физического `tmp: ManuallyDrop<u64>`, вернуть единственного
held owner в **текущий** gap и собрать три принадлежащие caller ячейки.
Одинаковые явно проверяемые ghost recovery commands нужны перед normal
`StorageDead` и перед cleanup `UnwindResume`; отсутствие runtime statement
между cleanup Drop и Resume требует узкой проверенной вставки в обе ветви
selected Drop lowering. Она не вправе подменять `Drop` summary или изобретать
receiver/FBC/origin/end premise.

## Ресурсный переход, который должен доказать сам caller

На входе actual callee: полный инициализированный `begin[..3]` и ровно один
`<u64>.own` на каждый текущий элемент, canonical
`*is_less |-> f &*& <F>.own(t,f)`, thread/type/frame. Wrapper получает
ячейки из собственного `[10,20,5]`; `F` — его настоящий входной `&mut F`,
а не подготовленное состояние guard. На normal/unwind выходе требуется
полный текущий массив, все три owner, текущий `F` и frame без незакрытых
tmp/guard/ref/receiver/tokens. Safety не обещает прежние значения при
произвольном допустимом comparator.

После первого true `tail.read` переносит единственный owner `5` в `tmp`,
оставляя логический gap в индексе 2; guard получает actual `src=&*tmp`,
`dst=tail`, `len=1`. Реальный copy 557 пишет sift `20` в gap; owner `20`
переносится в заполненный индекс 2, а исходный sift сохраняет физические
байты как не владеющая копия. `points_to` определяется через `points_to_`
(`prelude_core.rsspec` 231), поэтому прежнее инициализированное хранилище
sift может представлять writable logical gap без уничтожения байтов и без
второго owner. Обновление поля `gap_guard.dst=sift` на 558 обязано заново
связать guard-own с gap индекса 1, сохранив источник tmp, его текущий owner,
поля/padding и отдельный frame индексов 0 и 2. Текущая allocation-span
геометрия должна доказать непересечение stack tmp и **нового** gap; численное
равенство адресов и свежий owner не принимаются. Если поздний callback
паникует, сначала восстанавливаются его genuine shared loans, затем actual
cleanup Drop копирует текущий held в индекс 1. На normal second-false тоже
закрывается индекс 1; second-true делает ещё один shift и закрывает индекс 0.
`CopyOnDrop.own` из `insertion-onecell/prepare.py` 30–38 требует ровно
source quarter, current held owner и writable destination gap; B1 не
устанавливает новый `dst` автоматически.

## Точный refiner gate

`refinement_checker.ml` 2565–2608 сейчас сравнивает `Call`/`Drop` только по
normal successor (`TODO` для обоих unwind paths). Для этого профиля сравнить
число и значения Call args, paired normal-target shape, затем оригинальный и
verified `UnwindAction` variant; `Cleanup` рекурсивно сопоставляет обе cleanup
ветви из pre-call environment без несуществующего результата callback.
`Drop` рекурсивно сопоставляет normal и cleanup successors из среды **после**
потребления того же local. `Continue`, `Terminate`, `Unreachable` должны
совпадать точно; другой constructor/target — отказ. Существующий loop
visited-state protocol защищает рекурсию. Admission ограничить точным
`insert_tail<u64,F>` source/profile/CFG и selected guard identity; прочие
функции сохраняют прежнюю обработку до отдельного review. Изменение refiner
проверяет соответствие runtime графа, а отдельно проверяемая proof-AST
admission должна удостоверить расположение ghost cleanup перед настоящим
Drop и после него. Даже строгий refiner сам не доказывает ownership.

Нужные fail-closed controls: late Call `Cleanup→Continue` и redirect к чужому
cleanup; отсутствие/redirect cleanup guard Drop; missing/wrong/duplicate
callback fraction или borrow token на его точном закрытии; отсутствующий
updated `dst` или held owner на selected Drop precondition; повторный
receiver-end, второй held owner, ложный полный unwind post и реальный dead
code. Положительный gate проверяет first panic, early false, оба normal
loop exits и late panic с полными posts, return/free/leak/dead, exact
source/ghost strip, original/verified exporter+decode, proof AST и официальный
refinement. У каждого negative заранее фиксируются stage/predicate/location;
setup/frontend/unrelated/helper refusal остаётся INCONCLUSIVE.

## Первый причинный шаг и стоимость

Текущий `actual-insert-tail-b2.py` сохраняет полный target contract и
запускается только после B1. Его первая предсказанная граница —
`tail.sub(1)` на source 540: из ресурса трёх ячеек может потребоваться
проверенный interior `pointer_within_limits`; следующий target — genuine
loans первого comparator 541. Это прогноз по прежнему generic опыту, не
новый результат. До raw причинного Build **не писать** late cleanup patch
наугад. Один такой Build определит, где исходный источник/спецификация
действительно остановились; затем проверить, остаётся ли окно/бюджет для
узкого semantic-card+patch+regression шага. Исторические v6/v8 cold/warm
сборки стоят примерно 300–450 Cloud seconds каждая; B2 с полным новым
тело/cleanup может стоить больше, поэтому резервировать порядка 450–900
seconds за причинный Build и как минимум отдельный сопоставимый Build
для любого tool delta — **оценка, не новый бюджет и не право на dispatch**.
Основной риск времени — уже известные pointer/loan/loop proof обязательства
до late edge; основной риск доверия — переставить cleanup так, что реальный
guard Drop будет пропущен. Если первый Build не достигает late Call, статус
late semantics остаётся NOT_RUN, а полезное следующее действие выбирается по
его первой подтверждённой причине.


Предварительный proof-only вариант для подтверждённого отказа `tail.sub(1)`:
существующие `array_split::<u64>`/`array_join::<u64>` и `array_inv`
(`prelude_core.rsspec` 270–284) позволяют раскрыть interior cell bounds из
собственного полного `begin[..3]`. Разбить массив на три одиночные области,
получить bounds для `begin+1`/`begin+2`, затем объединить тот же полный
physical array до callback; логические `foreach(..., own)` ресурсы остаются
единственными. Это вариант для проверки после конкретного causal log, не
выполненная extraction/proof и не новая pointer/origin premise. Его цена —
новый exact proof SHA/roundtrip/Cloud Build на том же frozen profile; он
может лишь продвинуть к genuine callback loan frontier, не закрыть late
cleanup или общий Call/Drop refiner TODO.
