# После Г1: ресурс принят условно, следующий gate — layout замыкания

2026-11-13. Вход: g0 `7d695258f530eebfc7ec5c2365b011535c7a973e`, `kani3300/h1-step0/`,
`kani3300/h1-step1/{RESULT-H1-STEP1,SEMANTIC-FINDING,FIT,CASES}`; production Kani
`4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`, upstream `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
Это верификация корректности, не security-работа. Только source/curated-report review и TASK-черновик;
новые CI/сборки, чтение raw artifacts и выдача воркерам не выполнялись.

## 1. Оценка анализа worker15

Согласен с разделением resource SUPPORTED / semantic BLOCKED. Fit воспроизводится по опубликованным числам:
`V=774*N+57916`, `C=1926*N+92735`, N=2^b. Четыре точки P1 и три P2 дают нулевые остатки;
у b14 завершилась первая conversion, но не verification. F12 уменьшает V на82%, C на19.7%.
Это сильное подтверждение slicing/array-encoding механизма, а не доказательство всей причинной цепочки.
Решение D=S=6,Cret=0 условно относительно модели стоимости; STEP0 измерял proxy на R1, не converter reads на4f64.
Взятый из task run/source binding не равен независимой привязке binary к сборке: недостающий r3 build receipt
нужно приложить из уже существующей coordinator evidence, а не считать constant source fields такой привязкой.

Новый предел: formula/resource измерены для программы, которая обрывается на Unsupported после callback.
После исправления появится полезный хвост contract assertion;13s/1.8GiB нельзя обещать исправленному P1 или крупным тестам.
Не повторять всю матрицу: policy b12 принята, следующий probe — семантический на новой exact голове.
UF/no-slice остаются диагностическими плечами, не выбранным профилем выпуска; b16 CNF — extrapolated, не measured.

Отказ `RigidTy::Closure` в data-mask computation и отрезанный возврат bool из apply_closure установлены source/receipts.
Одинаковая explicit Unsupported ветвь есть на upstream; это не доказывает, что исходный P1 исполнялся там тем же путём.
Worker15 правильно маркирует S3→receiver alias→SetRef как конкретную гипотезу: точного MIR operation/graph edge пока нет.
`ptr::read` failures относятся к initialization pointee; описание `*const u8` не означает uninitialized pointer value.

## 2. Рекомендуемая минимальная правка

Первой отдельной стадией — **closure-specific empty mask**, только если rustc layout подтверждает `is_sized()` и size0.
Это включает capture-free closure P1 и замыкания с исключительно нулевыми по размеру захватами.
Нулевая ширина означает отсутствие data bytes, а не разрешение читать чей-либо payload.
В `mem_init.rs` get/set уже имеют `LAYOUT_SIZE==0` early return: get=true, set=no-op; другой witness не bless-ится.
Сохранить S3, points-to, оба слоя checks, frame, transfer protocol и ограничения для всех nonzero closures/других типов.
Не добавлять общий «любой size0 → supported» shortcut: менять только `RigidTy::Closure`.

Поддержка nonzero окружения как struct — правильное потенциальное продолжение, но отдельная стадия:
monomorphized upvar types + реальные rustc field offsets/order + рекурсивные data masks, включая padding.
`codegen/typ.rs:827–833` уже использует internal-rustc `args.as_closure().upvar_tys()`; это ориентир,
а не обещание такого же API у rustc_public GenericArgs в ty_layout. Bridge/TCX нужно спроектировать явно.
MU/union **по значению** в захвате — вложенный union: нельзя объявлять все bytes data, терять false или обходить UnionAsField.
Захват `&MU`/raw pointer — pointer bytes и отдельно tracked pointee; разрешение первого не инициализирует второй.
Если legal captured PFC упирается в этот предел, положительный gate для него не закрыт: следующий layout task/решение scope,
а не маскировка Unsupported или общий тезис «PFC+uninit теперь работает».

В points-to tuple сейчас добавляет successors и local1, уже связанной с receiver. Уточнить spread→locals2..arg_count
можно после проверки closure ABI/shims; это самостоятельное precision изменение. Blanket skip receiver/SetRef опасен
для настоящих captures и не заменяет нужный layout. Не смешивать оба исправления в одном различающем опыте.

## 3. Новый oracle P2

Логическая обязанность одна: первый запрещённый payload read в ensures должен быть отвергнут после lawful return.
На текущем инструментаторе ей соответствуют **два сохранённых свойства**: local Check и delayed CheckRef.
Это допустимая избыточная диагностика, не две пользовательские ошибки и не повод убирать слой защиты в этом патче.
Приёмка: полный source/callsite-bound набор этих failures, ни одного постороннего FAIL/Unsupported/frame/protocol failure;
оба ожидаемых обязательства сохранены. Не «любой FAIL», не лишь `>=1` и не жёсткий generated номер без binding.
Если число/вид checks меняется, нужен объяснённый MIR mapping и отдельный review, иначе STOP.
P1: все необходимые проверки SUCCESS, полезный внешний ensures assertion достигнут и успешен.
P2: callback дошёл до запрещённого read/check; внешний assertion может быть UNREACHABLE после отклонения плохого пути.
Именно для P1 такой UNREACHABLE блокирует qualification. Исторические ORACLES/results не переписывать задним числом.

## 4. Новый порядок вместо следующих пунктов R3 §13

1. Ресурсный пакет завершён; принять b12 для тяжёлых uninit/PFC tests. Не менять global default, b16 support не заявлять.
2. Выполнить после отдельной выдачи closure-ZST stage; coordinator targeted CI: неизменные P1/P2 при b12 + zero/nonzero boundary controls.
   Новый P1 должен завершиться полезным SUCCESS; отсутствие Unsupported без этого недостаточно. Старое разрешение≤10 исчерпано.
3. Затем вернуть legal-pair/postcondition-hole с b12 и R7-C lawful-modifies + matched frame/clause negatives.
   Lawful-modifies captures `out`: он может потребовать nonzero-upvar layout; при таком отказе отдельный capture-layout stage до M3.
4. Параллельно готовить conditional diagnostic для missing private marker вместо `unwrap_or_default()`,
   и принятую явную строку + regression controls: Replace/RecursiveCheck с shadow transfer **не заявляются**.
   Это не общий blanket Unsupported и не перевод clause asserts в assumes; actual unsupported/failure path должен быть зафиксирован.
5. Затем semantic edges R3§10, M3 на собранном exact export, multi-harness в обоих порядках;
   маски/false/Move/reinit/offset/alias/immutable admission и negative inventories остаются отдельными gates.
6. Полный неизменённый regression/platform gate на финальной голове; убрать внутренние handoff docs/CI overlays из export.
7. SmallSort read-only call inventory → capacity/semantic qualification выбранного b12 профиля → actual replay.
   Не переносить tiny P1 performance или proof credit на SmallSort. Standalone B1 и прочие согласованные upstream треки отдельно.

G-SC, R9/carriers, CBMC convert_index и Kani-вариант2 остаются отложенными по решению владельца.
Черновик: `TASK-KANI3300-CLOSURE-ZST-draft.md`; **NOT ISSUED**, исполнения/нового CI этим документом не разрешаем.
