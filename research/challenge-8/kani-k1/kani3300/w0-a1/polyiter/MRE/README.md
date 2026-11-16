# Single-file MRE — static, NOT_RUN

`main.rs` использует только `core` и атрибуты Kani; нет `std`, `IntoIter`,
test-only std overlay, stubs, assumes, transmute или compiler patch.
Четыре независимых selectors: negative/initialized companion для struct и
той же пары с внешним `ManuallyDrop`. `usize`, два слота и обычные metadata
приближены к A1. `repr(C)` упрощает последующий аудит offsets; runtime std
не требует именно этого представления.

Constructor с `inline(never)` создаёт struct aggregate и возвращает его по
значению; таким образом проверяются также direct-call argument/return seams.
Negative оставляет slot 1 пустым, объявляет его живым и реально читает `usize`
через raw pointer. Companion меняет только состояние slot 1 на `9`.
Проверки `start/end` не позволяют потерять обычные поля при переносе shadow.
`ManuallyDrop` подавляет Drop, но не делает пустой слот инициализированным.

| Harness | upstream `0aac16ef62` ON, прогноз | SEL1 `14bc57fdb9` ON, прогноз | Цель будущего исправления |
|---|---|---|---|
| `struct_uninitialized_negative` | FAILURE / unsupported nested union; возможен более ранний flat-array layout refusal | FAILURE / unsupported `PolymorphicIter` aggregate | FAILURE / uninitialized `*const usize` read |
| `struct_initialized_companion` | FAILURE / unsupported, несмотря на корректные данные | FAILURE / unsupported `PolymorphicIter` aggregate | SUCCESS |
| `manually_drop_uninitialized_negative` | FAILURE / unsupported | FAILURE / unsupported; struct уже достаточен для отказа | FAILURE / uninitialized read |
| `manually_drop_initialized_companion` | FAILURE / unsupported | FAILURE / unsupported; возможны дополнительные wrapper diagnostics | SUCCESS |

Это ожидаемые классы исходов по source, не результаты исполнения. Номера,
количество и точная очередность properties заранее не утверждаются.
Negative нарушает documented unsafe precondition constructor ещё до read;
указанный read — ожидаемый UB witness, не обещание точного места failure.
У wrapper-пары сейчас нельзя требовать исключительно `ManuallyDrop`-ошибку:
конструкция внутреннего struct тоже достигается. Отдельная идентификация
wrapper seam возможна после поддержки внутреннего struct.

При отдельно разрешённой будущей квалификации: edition 2021, `-Z uninit-checks`,
каждый selector отдельно на двух точных pins, сохранить compiler/toolchain/target
и bounded export/receipt. Не применять `should_panic`: unsupported и intended UB
должны различаться. Нужен failed uninit safety check для negative и отсутствие
failed/unsupported checks у companion. Одной пары недостаточно для допуска
расширенного compiler protocol: дополнительные controls перечислены в ANALYSIS.

Компиляция, Kani и CBMC в этой стадии не запускались; fixture требует будущей
проверки синтаксиса/достижимости и исполнения в разрешённой среде.
